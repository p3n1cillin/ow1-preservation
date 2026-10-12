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


def now():
    return datetime.datetime.now().isoformat(timespec="seconds")


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


CONNECTION_SERVICE = 0x65446991   # FNV-1a of bnet.protocol.connection.ConnectionService
AUTH_SERVER_SERVICE = 0x0DECFC01  # FNV-1a of bnet.protocol.authentication.AuthenticationServer
AUTH_CLIENT_SERVICE = 0x71240E35  # FNV-1a of bnet.protocol.authentication.AuthenticationClient
GAME_UTILITIES_SERVICE = 0x5DBB51C2  # FNV-1a of bnet.protocol.game_utilities.v2.client.GameUtilities
PROCESS_TASK = 1                     # GameUtilitiesService.ProcessTask


def describe_attribute(raw):
    """bgs.protocol.v2.Attribute {name=1, value=Variant=2}. Names, numeric/bool
    values and short string values (<= 32 B, request parameters such as
    service_type/cluster) are shown; longer strings and blobs only by length."""
    try: attr = decode_header(raw)
    except ValueError: return f"opaque({len(raw)} B)"
    name = attr.get(1, [b"?"])[0]
    name = name.decode("utf-8", "replace") if isinstance(name, bytes) else str(name)
    value = attr.get(2, [b""])[0]
    try: variant = decode_header(value) if isinstance(value, bytes) and value else {}
    except ValueError: return f"{name!r} = opaque"
    kinds = {1: "bool", 2: "int", 3: "float", 4: "string", 5: "blob", 6: "uint"}
    for k, kind in kinds.items():
        if k in variant:
            v = variant[k][0]
            if kind == "string" and isinstance(v, bytes) and len(v) <= 32:
                return f"{name!r} = string {v.decode('utf-8', 'replace')!r}"
            return f"{name!r} = {kind}" + (f"({len(v)} B)" if isinstance(v, bytes) else f" {v}")
    return f"{name!r} = (empty)"
ON_LOGON_COMPLETE = 5             # AuthenticationClient method id (from client descriptors)
PROGRAM_PRO = 0x0050726F          # 'Pro' program fourcc the client requires
REGION = 1                        # nonzero region byte for the game account
RESPONSE_SERVICE = 0xFE           # bgs service_id marking a message as a response


def enc_f64(field, val):
    return enc_varint(field << 3 | 1) + struct.pack("<Q", val)


def enc_fixed32(field, val):
    return enc_varint(field << 3 | 5) + struct.pack("<I", val)


def build_logon_result(battle_tag, account_id):
    """LogonResult for AuthenticationClient.OnLogonComplete. This is our own
    preservation server granting a local session; the battle_tag is the identity
    the player appears as. error_code 0 = success. EntityId = {high, low}."""
    # EntityId.high carries a type tag: account = 1<<56. A game account must be
    # high = (2<<56) | (region<<32) | program fourcc; the client's OnLogonComplete
    # handler (rva 0x00e2ebe0, helper 0x02152e10) only takes its success path when
    # a game account decodes with program == 'Pro' (0x0050726f) and region != 0.
    account_entity = enc_f64(1, 1 << 56) + enc_f64(2, account_id)
    game_entity = enc_f64(1, (2 << 56) | (REGION << 32) | PROGRAM_PRO) + enc_f64(2, account_id)
    body = enc_v(1, 0)                       # error_code = success
    body += enc_b(2, account_entity)         # account_id
    body += enc_b(3, game_entity)            # game_account_id (repeated; one entry)
    body += enc_b(7, battle_tag.encode())    # battle_tag
    body += enc_v(6, REGION)                 # connected_region
    body += enc_v(5, REGION)                 # available_region (repeated; one entry)
    body += enc_b(9, bytes(32))              # session_key placeholder
    return body


def walk(buf, depth=0):
    """Wire-type-aware recursive outline. fixed32 values are shown as hex (bgs
    service hashes are fixed32). Only used on the bind block, which carries
    service hashes/ids and a ProcessId, never account credentials."""
    pos, parts = 0, []
    try:
        while pos < len(buf):
            tag, pos = read_varint(buf, pos)
            fn, wt = tag >> 3, tag & 7
            if wt == 0:
                v, pos = read_varint(buf, pos); parts.append(f"f{fn}={v}")
            elif wt == 5:
                v = struct.unpack_from("<I", buf, pos)[0]; pos += 4; parts.append(f"f{fn}=x{v:08x}")
            elif wt == 1:
                v = struct.unpack_from("<Q", buf, pos)[0]; pos += 8; parts.append(f"f{fn}=x{v:016x}")
            elif wt == 2:
                ln, pos = read_varint(buf, pos); sub = buf[pos:pos + ln]; pos += ln
                inner = walk(sub, depth + 1) if depth < 4 and sub else ""
                parts.append(f"f{fn}={{{inner}}}" if inner else f"f{fn}=bytes({ln})")
            else:
                break
    except (ValueError, struct.error):
        pass
    return ", ".join(parts)


def sketch(buf):
    """Field-number/type outline of a protobuf body with NO string/bytes values
    shown (only their length), so account identifiers in a LogonRequest are not
    logged. Varints (flags/enums/versions) are shown; they carry no identity."""
    try: fields = decode_header(buf)
    except ValueError: return f"opaque({len(buf)} B)"
    parts = []
    for k, values in sorted(fields.items()):
        shown = [f"str/bytes({len(v)})" if isinstance(v, bytes) else v for v in values]
        parts.append(f"f{k}={shown}")
    return ", ".join(parts)


def enc_varint(n):
    out = bytearray()
    while True:
        b = n & 0x7F; n >>= 7
        out.append(b | (0x80 if n else 0))
        if not n: return bytes(out)


def enc_v(field, n):   return enc_varint(field << 3) + enc_varint(int(n))
def enc_b(field, buf): return enc_varint(field << 3 | 2) + enc_varint(len(buf)) + buf


def frame(header_parts, body):
    """One bgs RPC message: u16-BE header length, Header protobuf, then body."""
    header = b"".join(header_parts)
    return struct.pack(">H", len(header)) + header + body


def ws_send(conn, payload):
    """Send one unmasked binary WebSocket message (server -> client)."""
    n = len(payload)
    out = bytearray([0x82])  # FIN + binary opcode
    if n < 126: out.append(n)
    elif n < 65536: out.append(126); out += struct.pack(">H", n)
    else: out.append(127); out += struct.pack(">Q", n)
    conn.sendall(bytes(out) + payload)


def imported_hashes(bind):
    """ConnectRequest.bind_request.imported_service_hash[] (field 1), whether the
    client sent them packed (one bytes blob) or as repeated fixed32."""
    out = []
    for v in bind.get(1, []):
        if isinstance(v, bytes):
            out += [struct.unpack_from("<I", v, i)[0] for i in range(0, len(v) - 3, 4)]
        else:
            out.append(v)
    return out


def build_connect_response(req_body):
    """ConnectResponse for ConnectionService.Connect, built from the client's
    ConnectRequest. server_id/client_id are ProcessId{label,epoch}; the client's
    imported services are each assigned a sequential server-local id, which it
    then uses as the service_id when calling those services (e.g. Logon).
    Field numbers follow the public bgs connection protocol; refine empirically."""
    request = decode_header(req_body) if req_body else {}
    client_id = request.get(1, [b""])[0]
    client_id = client_id if isinstance(client_id, bytes) else b""
    # bind_request is a sub-message; this client carries it in field 5.
    bind, bind_field = {}, None
    for f in (2, 5):
        if f in request and isinstance(request[f][0], bytes):
            try: bind = decode_header(request[f][0]); bind_field = f; break
            except ValueError: pass
    imports = imported_hashes(bind)
    server_id = enc_v(1, 1) + enc_v(2, int(time.time()))
    bind_response = b"".join(enc_v(1, i) for i in range(len(imports)))
    body = enc_b(1, server_id)
    if client_id: body += enc_b(2, client_id)
    body += enc_v(3, 0)               # bind_result = success
    body += enc_b(4, bind_response)   # BindResponse.imported_service_id[]
    detail = (f"request={describe(request)}; bind(field {bind_field})={describe(bind)}; "
              f"imported_hashes={[hex(h) for h in imports]}")
    return body, imports, detail


def describe(fields):
    return ", ".join(f"f{k}=" + str([f"bytes({len(v)})" if isinstance(v, bytes) else v for v in values])
                     for k, values in sorted(fields.items()))


def handle(conn, addr, log, serve=False, battle_tag="Preservation#1001", no_grant=False):
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
            # Observe the RPC sequence. In --serve mode, answer the opening
            # ConnectionService.Connect so the client advances to the next RPC
            # (expected: service bind, then authentication) and we learn it.
            for _ in range(64 if serve else 1):
                payload = read_ws_message(conn)
                if payload is None:
                    emit(f"{now()} WebSocket closed by client"); return
                hlen = struct.unpack_from(">H", payload)[0]
                header = decode_header(payload[2:2 + hlen])
                body = payload[2 + hlen:]
                service = header.get(11, [0])[0]
                method = header.get(2, [None])[0]
                token = header.get(3, [0])[0]
                emit(f"{now()} WS RPC in: {describe(header)}; body bytes={len(body)}"
                     + ("  <ConnectionService.Connect>" if service == CONNECTION_SERVICE and method == 1 else ""))
                if not serve:
                    return
                if service == CONNECTION_SERVICE and method == 1:
                    resp_body, imports, detail = build_connect_response(body)
                    emit(f"{now()}   ConnectRequest: {detail}")
                    emit(f"{now()}   bind walk: {walk(decode_header(body).get(5, [b''])[0])}")
                    ws_send(conn, frame([enc_v(1, RESPONSE_SERVICE), enc_v(3, token)], resp_body))
                    emit(f"{now()}   -> ConnectResponse sent ({len(resp_body)} B, assigned {len(imports)} imported service id(s))")
                elif service == AUTH_SERVER_SERVICE and method == 1:
                    emit(f"{now()}   LogonRequest body: {sketch(body)}  (string/bytes values redacted)")
                    # Acknowledge the Logon RPC (empty NoData response). The real
                    # auth result is expected via a server->client listener call;
                    # observe whether the client waits for that, opens a web login
                    # connection, or sends another RPC.
                    ws_send(conn, frame([enc_v(1, RESPONSE_SERVICE), enc_v(3, token)], b""))
                    emit(f"{now()}   -> Logon acknowledged (empty NoData response)")
                    if no_grant:
                        conn.settimeout(40)
                        emit(f"{now()}   (no-grant mode: observing what the client does next for up to 40s)")
                        continue
                    # Grant the session by calling the client's AuthenticationClient
                    # listener: OnLogonComplete(LogonResult{error_code=0, ...}). The
                    # service is addressed by hash (fixed32, field 11), as the client
                    # does; method 5 = OnLogonComplete.
                    result = build_logon_result(battle_tag, 1001)
                    header = (enc_v(1, 0) + enc_v(2, ON_LOGON_COMPLETE) + enc_v(3, 2)
                              + enc_fixed32(11, AUTH_CLIENT_SERVICE))
                    ws_send(conn, frame([header], result))
                    emit(f"{now()}   -> OnLogonComplete sent (battle_tag={battle_tag!r}, "
                         f"{len(result)} B); observing client's next move")
                    conn.settimeout(45)
                elif service == GAME_UTILITIES_SERVICE and method == PROCESS_TASK:
                    request = decode_header(body) if body else {}
                    for label, key in (("attribute", 1), ("payload", 2)):
                        for raw in request.get(key, []):
                            emit(f"{now()}   ProcessTask {label}: {describe_attribute(raw)}")
                    # Empty ProcessTaskResponse (no result attributes) for now; the
                    # client's reaction tells us what result this task requires.
                    ws_send(conn, frame([enc_v(1, RESPONSE_SERVICE), enc_v(3, token)], b""))
                    emit(f"{now()}   -> empty ProcessTaskResponse sent")
                else:
                    emit(f"{now()}   service {hex(service)} method {method} body: {sketch(body)}")
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
    ap.add_argument("--serve", action="store_true",
                    help="answer ConnectionService.Connect and keep observing the follow-on RPC sequence")
    ap.add_argument("--no-grant", action="store_true", help="ack Logon but do not send OnLogonComplete; observe the client's next move")
    ap.add_argument("--battle-tag", default="Preservation#1001",
                    help="identity granted to the client on login (served to OnLogonComplete)")
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
            threading.Thread(target=handle, args=(tls, addr, log, args.serve, args.battle_tag, args.no_grant), daemon=True).start()


if __name__ == "__main__":
    main()
