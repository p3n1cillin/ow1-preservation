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
import struct
import threading


def read_varint(buf, pos):
    shift = result = 0
    while pos < len(buf):
        b = buf[pos]; pos += 1
        result |= (b & 0x7F) << shift
        if not (b & 0x80):
            return result, pos
        shift += 7
    raise ValueError("truncated varint")


def decode_header(buf):
    """Decode the bgs Header protobuf into {field_number: value} (generic)."""
    fields, pos = {}, 0
    while pos < len(buf):
        tag, pos = read_varint(buf, pos)
        fnum, wire = tag >> 3, tag & 7
        if wire == 0:
            val, pos = read_varint(buf, pos)
        elif wire == 2:
            ln, pos = read_varint(buf, pos)
            val = buf[pos:pos + ln]; pos += ln
        elif wire == 5:
            val = struct.unpack_from("<I", buf, pos)[0]; pos += 4
        elif wire == 1:
            val = struct.unpack_from("<Q", buf, pos)[0]; pos += 8
        else:
            raise ValueError(f"unsupported wire type {wire}")
        fields.setdefault(fnum, []).append(val)
    return fields


def handle(conn, addr, log):
    stamp = datetime.datetime.now().isoformat(timespec="seconds")

    def emit(line):
        print(line, flush=True); log.write(line + "\n"); log.flush()

    emit(f"{stamp} bgs TLS connection established from {addr}")
    try:
        conn.settimeout(20)
        data = b""
        while len(data) < 2:
            chunk = conn.recv(4096)
            if not chunk:
                emit(f"{stamp} peer closed before a full frame ({len(data)} bytes)"); return
            data += chunk
        hlen = struct.unpack_from(">H", data, 0)[0]
        while len(data) < 2 + hlen:
            data += conn.recv(4096)
        header = data[2:2 + hlen]
        try:
            fields = decode_header(header)
            desc = ", ".join(f"f{k}={v}" for k, v in sorted(fields.items()))
            emit(f"{stamp} Header ({hlen} B): {desc}")
            # Field 1 is the service hash on export-service requests; field 2 is
            # the method id; field 5 is the body size. These are what the real
            # login service must dispatch on.
        except ValueError as e:
            emit(f"{stamp} Header ({hlen} B) raw {header.hex()} ({e})")
        emit(f"{stamp} first frame bytes: {data[:2 + hlen + 16].hex()}")
    except (ssl.SSLError, OSError, ValueError) as e:
        emit(f"{stamp} connection error: {e}")
    finally:
        conn.close()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--port", type=int, default=21119)
    ap.add_argument("--cert", required=True, help="server certificate (chain) PEM")
    ap.add_argument("--key", required=True, help="server private key PEM")
    ap.add_argument("--log", default="bnet-probe.log")
    args = ap.parse_args()

    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(args.cert, args.key)
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
            try:
                tls = ctx.wrap_socket(raw, server_side=True)
            except ssl.SSLError as e:
                line = f"{datetime.datetime.now().isoformat(timespec='seconds')} TLS handshake FAILED from {addr}: {e}"
                print(line, flush=True); log.write(line + "\n"); log.flush()
                raw.close(); continue
            threading.Thread(target=handle, args=(tls, addr, log), daemon=True).start()


if __name__ == "__main__":
    main()
