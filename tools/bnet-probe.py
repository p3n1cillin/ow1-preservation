"""Observing TLS server for the bgs login connection (private-server research).

Completes a TLS handshake using our own local cert, then logs the Battle.net
RPC framing the client sends: a 2-byte big-endian header length, a protobuf
Header, then a body of the Header's declared size. It decodes only the generic
protobuf wire structure (varints / length-delimited fields) so we can learn the
service hash, method id and token the retail client uses. It sends nothing back,
so it cannot complete a login; it exists to observe what to implement next.

Run it on the host loopback port that the launcher's container bridge forwards
to (default 21119 <- container 1119). Pair with Start-PrivateClient.ps1.
"""
import argparse
import datetime
import socket
import ssl
import base64, hashlib, struct
import threading
import time

MAX_HEADER = 65535
MAX_BODY = 1024 * 1024


def read_exact(conn, size):
    data = bytearray()
    while len(data) < size:
        chunk = conn.recv(size - len(data))
        if not chunk:
            raise EOFError(f"peer closed with {size - len(data)} bytes missing")
        data.extend(chunk)
    return bytes(data)


def read_varint(buf, pos):
    shift = result = 0
    while pos < len(buf) and shift < 70:
        b = buf[pos]; pos += 1
        if shift == 63 and b > 1:
            raise ValueError("varint exceeds uint64")
        result |= (b & 0x7F) << shift
        if not (b & 0x80):
            return result, pos
        shift += 7
    raise ValueError("truncated varint")


def decode_header(buf):
    """Decode the bgs Header protobuf into {field_number: value} (generic)."""
    if not 0 < len(buf) <= MAX_HEADER:
        raise ValueError("header size out of bounds")
    fields, pos = {}, 0
    while pos < len(buf):
        tag, pos = read_varint(buf, pos)
        fnum, wire = tag >> 3, tag & 7
        if not 0 < fnum <= 0x1fffffff:
            raise ValueError("protobuf field number out of bounds")
        if wire == 0:
            val, pos = read_varint(buf, pos)
        elif wire == 2:
            ln, pos = read_varint(buf, pos)
            if ln > len(buf) - pos: raise ValueError("truncated length-delimited field")
            val = buf[pos:pos + ln]; pos += ln
        elif wire == 5:
            if len(buf) - pos < 4: raise ValueError("truncated fixed32")
            val = struct.unpack_from("<I", buf, pos)[0]; pos += 4
        elif wire == 1:
            if len(buf) - pos < 8: raise ValueError("truncated fixed64")
            val = struct.unpack_from("<Q", buf, pos)[0]; pos += 8
        else:
            raise ValueError(f"unsupported wire type {wire}")
        fields.setdefault(fnum, []).append(val)
    return fields


def read_ws_message(conn):
    """Return one reassembled client data message (unmasked), or None on close."""
    parts = []
    while True:
        b0, b1 = read_exact(conn, 2)
        op, ln = b0 & 0x0F, b1 & 0x7F
        if ln == 126: ln = struct.unpack(">H", read_exact(conn, 2))[0]
        elif ln == 127: ln = struct.unpack(">Q", read_exact(conn, 8))[0]
        if ln > MAX_BODY + 65536: raise ValueError("oversized WebSocket frame")
        mask = read_exact(conn, 4) if b1 & 0x80 else b"\x00\x00\x00\x00"
        data = bytes(c ^ mask[i % 4] for i, c in enumerate(read_exact(conn, ln)))
        if op == 8: return None
        if op in (9, 10): continue
        parts.append(data)
        if b0 & 0x80: return b"".join(parts)


def read_frame(conn):
    hlen = struct.unpack(">H", read_exact(conn, 2))[0]
    fields = decode_header(read_exact(conn, hlen))
    sizes = fields.get(5, [0])
    if len(sizes) != 1 or not isinstance(sizes[0], int) or not 0 <= sizes[0] <= MAX_BODY:
        raise ValueError("invalid or oversized body length")
    # Observe framing only. Account/token/body bytes are never written to logs.
    read_exact(conn, sizes[0])
    return hlen, fields, sizes[0]


def handle(conn, addr, log):
    stamp = datetime.datetime.now().isoformat(timespec="seconds")

    def emit(line):
        print(line, flush=True); log.write(line + "\n"); log.flush()

    emit(f"{stamp} bgs TLS connection established from {addr}; version={conn.version()}")
    try:
        conn.settimeout(20)
        first = read_exact(conn, 2)
        if first == b"GE":
            # HTTP (e.g. WebSocket upgrade). Log the request line and header
            # names only; header values may carry cookies or tokens.
            data = first
            while b"\r\n\r\n" not in data and len(data) < 16384:
                chunk = conn.recv(4096)
                if not chunk: break
                data += chunk
            head = data.split(b"\r\n\r\n", 1)[0].decode("latin-1").split("\r\n")
            headers = {h.split(":", 1)[0].strip().lower(): h.split(":", 1)[1].strip() for h in head[1:] if ":" in h}
            proto = headers.get("sec-websocket-protocol", "")
            emit(f"{stamp} HTTP request ({len(data)} B): {head[0]!r}; header names={sorted(headers)}; protocol={proto!r}")
            key = headers.get("sec-websocket-key")
            if headers.get("upgrade", "").lower() != "websocket" or not key:
                return
            accept = base64.b64encode(hashlib.sha1((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest()).decode()
            reply = "HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: " + accept
            if proto: reply += "\r\nSec-WebSocket-Protocol: " + proto.split(",")[0].strip()
            conn.sendall((reply + "\r\n\r\n").encode())
            emit(f"{stamp} WebSocket upgrade accepted")
            payload = read_ws_message(conn)
            if payload is None:
                emit(f"{stamp} WebSocket closed before a data message"); return
            hlen = struct.unpack_from(">H", payload)[0]
            fields = decode_header(payload[2:2 + hlen])
            desc = ", ".join(f"f{k}=" + str([f"bytes({len(v)})" if isinstance(v, bytes) else v for v in values])
                             for k, values in sorted(fields.items()))
            emit(f"{stamp} WS bgs header ({hlen} B): {desc}; message bytes={len(payload)} (body omitted)")
            return
        hlen = struct.unpack(">H", first)[0]
        fields = decode_header(read_exact(conn, hlen))
        sizes = fields.get(5, [0])
        if len(sizes) != 1 or not isinstance(sizes[0], int) or not 0 <= sizes[0] <= MAX_BODY:
            raise ValueError("invalid or oversized body length")
        read_exact(conn, sizes[0]); body_size = sizes[0]
        desc = ", ".join(f"f{k}=" + str([f"bytes({len(v)})" if isinstance(v, bytes) else v for v in values])
                         for k, values in sorted(fields.items()))
        emit(f"{stamp} Header ({hlen} B): {desc}; body bytes={body_size} (omitted)")
        # These are generic field numbers, not verified final-OW1 service
        # dispatch. Field 1 and field 11 must not be conflated as one hash.
    except (ssl.SSLError, OSError, ValueError, EOFError) as e:
        emit(f"{stamp} connection error: {e}")
    finally:
        conn.close()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--port", type=int, default=21119)
    ap.add_argument("--cert", required=True, help="server certificate (chain) PEM")
    ap.add_argument("--key", required=True, help="server private key PEM")
    ap.add_argument("--log", default="bnet-probe.log")
    ap.add_argument("--handshake-delay", type=int, choices=range(0, 61), default=0,
                    help="local diagnostic delay before TLS, in seconds (0..60)")
    ap.add_argument("--tls-max", choices=("1.2", "1.3"),
                    help="limit the observer's TLS version for native compatibility diagnostics")
    args = ap.parse_args()

    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(args.cert, args.key)
    if args.tls_max:
        ctx.maximum_version = {"1.2": ssl.TLSVersion.TLSv1_2, "1.3": ssl.TLSVersion.TLSv1_3}[args.tls_max]
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE  # we do not require a client cert

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", args.port))
    srv.listen(8)
    with open(args.log, "a", encoding="utf-8") as log:
        print(f"bgs observing TLS server on 127.0.0.1:{args.port}", flush=True)
        while True:
            raw, addr = srv.accept()
            raw.settimeout(10)
            if args.handshake_delay: time.sleep(args.handshake_delay)
            try:
                tls = ctx.wrap_socket(raw, server_side=True)
            except (ssl.SSLError, OSError) as e:
                line = f"{datetime.datetime.now().isoformat(timespec='seconds')} TLS handshake FAILED from {addr}: {e}"
                print(line, flush=True); log.write(line + "\n"); log.flush()
                raw.close(); continue
            threading.Thread(target=handle, args=(tls, addr, log), daemon=True).start()


if __name__ == "__main__":
    main()
