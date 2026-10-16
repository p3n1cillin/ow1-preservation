"""Loopback bgs observer/prototype server for private-server research.

Completes a TLS handshake using our own local cert, then logs the Battle.net
RPC framing the client sends: a 2-byte big-endian header length, a protobuf
Header, then a body of the Header's declared size. It decodes only the generic
protobuf wire structure (varints / length-delimited fields) so we can learn the
service hash, method id and token the retail client uses. WebSocket negotiation
is supported. --serve additionally grants a local account and answers referral
and lobby proofs. An explicit own key can issue a credential for the client's
guarded -TrustLobbyKey diagnostic. Gateway application replies and main-menu
access remain unimplemented/unverified.

Run it on the host loopback port that the launcher's container bridge forwards
to (default 21119 <- container 1119). Pair with Start-PrivateClient.ps1.
"""
import argparse
import datetime
import socket
import ssl
import base64, hashlib, hmac, struct
import os
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
REFERRAL_KEY_BYTES = 64           # k0..k3 must each be a 64-byte blob (handler rva 0x00e2f6c0)


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


def enc_attribute(name, variant_field, value):
    """bgs.protocol.v2.Attribute{name=1, value=Variant=2}. Variant field numbers:
    4 string, 5 blob, 6 uint (the client's variant type tag equals the field)."""
    if variant_field == 6:
        variant = enc_v(6, value)
    else:
        variant = enc_b(variant_field, value.encode() if isinstance(value, str) else value)
    return enc_b(1, name.encode()) + enc_b(2, variant)


def attribute_strings(request):
    """name -> string value for a ProcessTaskRequest's string attributes."""
    out = {}
    for raw in request.get(1, []):
        try:
            attr = decode_header(raw)
            variant = decode_header(attr.get(2, [b""])[0] or b"")
        except (ValueError, TypeError):
            continue
        name, value = attr.get(1, [b""])[0], variant.get(4, [None])[0]
        if isinstance(name, bytes) and isinstance(value, bytes):
            out[name.decode("utf-8", "replace")] = value.decode("utf-8", "replace")
    return out


# Referral sessions handed to the client: cid -> (k0, k1, k2, k3). The lobby
# connection names its cid in the first handshake message.
REFERRALS = {}
_GW_PROBE_INDEX = 0  # cycles candidate responder replies across lobby retries
REFERRALS_LOCK = threading.Lock()


def build_referral_info(host):
    """ProcessTaskResponse answering the Balancer/Referral task with ReferralInfo.
    The client's ReferralInfo handler (rva 0x00e2f6c0, reached from the
    response_type dispatch at rva 0x00e2a880) requires all six result attributes:
    k0..k3 = 64-byte blobs, cid = uint, hostv4 = string. Missing or mistyped
    attributes set the referral to its failure state (4). The keys are random
    per session; we own both ends, so no Blizzard key material is involved."""
    keys = tuple(os.urandom(REFERRAL_KEY_BYTES) for _ in range(4))
    with REFERRALS_LOCK:
        connection_id = len(REFERRALS) + 1
        REFERRALS[connection_id] = keys
    result = [enc_attribute("response_type", 4, "ReferralInfo")]
    for name, key in zip(("k0", "k1", "k2", "k3"), keys):
        result.append(enc_attribute(name, 5, key))
    result.append(enc_attribute("cid", 6, connection_id))
    result.append(enc_attribute("hostv4", 4, host))
    return b"".join(enc_b(1, attr) for attr in result), connection_id


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


def handle(conn, addr, log, serve=False, battle_tag="Preservation#1001", no_grant=False,
           referral_host=None, account_id=1001):
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
                    result = build_logon_result(battle_tag, account_id)
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
                    task = attribute_strings(request)
                    if (referral_host and task.get("service_type") == "Balancer"
                            and task.get("request_type") == "Referral"):
                        resp, cid = build_referral_info(referral_host)
                        ws_send(conn, frame([enc_v(1, RESPONSE_SERVICE), enc_v(3, token)], resp))
                        emit(f"{now()}   -> ReferralInfo sent (hostv4={referral_host!r}, cid={cid}, "
                             f"k0..k3 random, {len(resp)} B); observing client's next move")
                        conn.settimeout(60)
                        continue
                    # Empty ProcessTaskResponse (no result attributes); the client
                    # retries with backoff, which shows what result it requires.
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


def observe_raw(raw, addr, number, log):
    """Log the size and a short prefix of a non-TLS follow-on connection's first
    bytes (protocol identification only), then close it."""
    try:
        raw.settimeout(20)
        data = raw.recv(4096)
        line = (f"{now()} connection #{number} from {addr}: first read {len(data)} B, "
                f"prefix {data[:16].hex()}")
    except OSError as e:
        line = f"{now()} connection #{number} from {addr}: read error {e}"
    finally:
        raw.close()
    print(line, flush=True); log.write(line + "\n"); log.flush()


LOBBY_CLIENT_HELLO = b"HELLO PRO CLIENT\0"
LOBBY_SERVER_HELLO = b"HELLO PRO SERVER\0"


def lobby_hmac(key, *parts):
    return hmac.new(key, b"".join(parts), hashlib.sha256).digest()


class DecryptedConnection:
    def __init__(self, raw, cipher):
        self.raw, self.cipher = raw, cipher

    def recv(self, size):
        return self.cipher.apply(self.raw.recv(size))


def read_lobby_frame(conn):
    length = int.from_bytes(read_exact(conn, 3), 'big')
    if not 0 < length <= MAX_BODY:
        raise ValueError('invalid or oversized lobby packet')
    return read_exact(conn, length)


def serve_lobby(raw, addr, number, log, difficulty=0, credential=None, credential_delay=0, packet_capture=None,
                peer_group=0, gateway_hashes=None, capture_count=1, gateway_reply='ack', lobby_service=None,
                initial_delay=0):
    """Lobby (game-service gateway) handshake at the referral hostv4, as the
    client's handler (rva 0x00e38fe0, state at pipe+0x80) expects it. Messages
    are raw little-endian bytes, one per TCP send, with no framing:
      C: "HELLO PRO CLIENT\0"            S: "HELLO PRO SERVER\0"
      C: cid u64 | client_random[32]      S: challenge[32] | difficulty u8 | server_random[32]
      C: nonce u64 | HMAC(k0, CR|SR)      S: HMAC(k1, SR|CR)
    nonce is the client's proof of work (rva 0x00e38990): SHA-1(challenge|nonce)
    must have >= difficulty low zero bits. Session keys are then
    HMAC(k2, CR|SR) and HMAC(k3, SR|CR) (rva 0x00e39890). The client next
    expects an encrypted 292-byte packet including an RSA credential. With an
    explicit own key configured, issue our own credential for a diagnostic
    client running -TrustLobbyKey; otherwise stop at that gate. Original
    verifier code and results remain enabled."""
    def emit(line):
        line = f"{now()} lobby #{number}: {line}"
        print(line, flush=True); log.write(line + "\n"); log.flush()

    try:
        raw.settimeout(20)
        hello = read_exact(raw, len(LOBBY_CLIENT_HELLO))
        if hello != LOBBY_CLIENT_HELLO:
            emit(f"unexpected greeting ({len(hello)} B, prefix {hello[:16].hex()})"); return
        raw.sendall(LOBBY_SERVER_HELLO)
        emit("client hello received; server hello sent")
        m1 = read_exact(raw, 40)
        if len(m1) != 40:
            emit(f"stage 1: expected 40 B (cid|client_random), got {len(m1)} B"); return
        cid = struct.unpack_from("<Q", m1)[0]
        client_random = m1[8:]
        with REFERRALS_LOCK:
            keys = REFERRALS.get(cid)
        if keys is None:
            emit(f"stage 1: unknown cid {cid}"); return
        challenge, server_random = os.urandom(32), os.urandom(32)
        raw.sendall(challenge + bytes([difficulty]) + server_random)
        emit(f"stage 1: cid={cid} matches a referral; challenge sent (difficulty={difficulty})")
        m3 = read_exact(raw, 40)
        if len(m3) != 40:
            emit(f"stage 2: expected 40 B (nonce|proof), got {len(m3)} B"); return
        nonce = struct.unpack_from("<Q", m3)[0]
        work = hashlib.sha1(challenge + m3[:8]).digest()
        zeros = 0
        for byte in work:
            if byte == 0: zeros += 8; continue
            while not byte & 1: zeros += 1; byte >>= 1
            break
        proof_ok = hmac.compare_digest(m3[8:], lobby_hmac(keys[0], client_random, server_random))
        emit(f"stage 2: nonce={nonce} work_zero_bits={zeros} client_proof_valid={proof_ok}")
        if not proof_ok or zeros < difficulty:
            return
        raw.sendall(lobby_hmac(keys[1], server_random, client_random))
        emit("stage 2: server proof sent; client now expects the signed server credential")
        if credential is not None:
            # Allow the guarded owned-process key installer to find the pipe.
            # This is scheduling time for the experiment, not a protocol delay.
            time.sleep(credential_delay)
            from panama_stream import Panama
            outbound_key = lobby_hmac(keys[2], client_random, server_random)
            inbound_key = lobby_hmac(keys[3], server_random, client_random)
            outbound = Panama(outbound_key, outbound_key)
            inbound = Panama(inbound_key, inbound_key)
            # The original transport requires a 292-byte decrypted packet:
            # credential[256], two 128-bit identifiers, then uint32 metadata.
            # These are our server's local identifiers; their downstream
            # semantics are still being investigated.
            packet = credential + struct.pack('<QQQQI', (peer_group<<40)|1, 1, (peer_group<<40)|cid, 1, 0)
            raw.sendall(outbound.apply(packet))
            emit("own-key credential packet sent (292 B, Panama-LE); native verification remains enabled")
        else:
            emit("no own-key credential configured; observing at credential gate")
        raw.settimeout(60)
        if credential is not None:
            decrypted = DecryptedConnection(raw, inbound)
            from gateway_protocol import offer_response, catalogue_offer, negotiation_reply, frame as gateway_frame, parse_offer, heartbeat_response
            offered = False
            initial_due = float('inf')
            bootstrap_channel = None
            captured = 0
            # Serve the demonstrated hash negotiation, then observe the next
            # application interface. Never invent game/session replies.
            for _ in range(1024):
                payload = read_lobby_frame(decrypted)
                if packet_capture is not None:
                    if len(payload) > 4096:
                        emit('gateway packet capture skipped (over 4096-byte bound)')
                    else:
                        from pathlib import Path
                        target = Path(packet_capture)
                        if capture_count > 1:
                            target = target.with_stem(f'{target.stem}-{captured}')
                        try:
                            with open(target, 'xb') as output:
                                output.write(payload)
                            emit(f"gateway packet {captured+1} captured locally ({len(payload)} B)")
                        except FileExistsError:
                            emit('gateway packet capture already exists; preserving it')
                    captured += 1
                    if captured >= capture_count:
                        packet_capture = None
                emit(f"post-credential packet: body_bytes={len(payload)} first_byte={payload[0]}"
                     + (f" message_delta={payload[1]}" if len(payload) > 1 else "")
                     + " (remaining contents omitted)")
                if not offered:
                    bootstrap_channel = payload[0]
                    if gateway_reply == 'probe':
                        # Each referral retry is a fresh lobby connection, so cycle
                        # one candidate responder reply per connection and let the
                        # client's reaction (advance vs. close) identify the right
                        # message. Candidates follow the captured offer framing
                        # (u16-LE message id, then body); the client offered id 1.
                        global _GW_PROBE_INDEX
                        hashes = parse_offer(payload)
                        hs = struct.pack(f'<{len(hashes)}I', *hashes)
                        count = struct.pack('<I', len(hashes))
                        # id-2 descriptor (rva 0x2cf0180) has a 16-byte identity
                        # field at object offset 0x78 (two u64, sub-type 0x2cefb60)
                        # before the record vector at 0x88. Wire (positional) =
                        # u16 id, identity[16], count u32, hashes. Try identity
                        # variants; id-1 (client's own form) carries no identity.
                        # id-2 message (handler 0x00560040) decoded from the field
                        # tables: u16 id, {seq:u64, src:u64} header (type-8 fields),
                        # then a repeated record (field table 0x02cf0380):
                        # m_protocolCRC u32, m_messageBase u32, m_messageMax u32,
                        # m_protocolFlags u32, m_untrustedServer bool, m_protocolName
                        # string. The bootstrap record (gateway-104319.json) is
                        # {0x11d82194, 1, 5, 3, false, ""}. The only unknowns are
                        # the generic bool/string encodings and whether nested
                        # messages are length-prefixed, so vary just those.
                        # Serializer 0x00561e90 writes primitives raw/inline (no
                        # tags, no length prefix): type 0x10=1B, 0x20=2B, 0x40=4B,
                        # 0x80=8B, 0x100=16B. So id-2 body = u16 id, {seq:u64,
                        # src:u64}, u32 record count, then each record's fields:
                        # CRC/base/max/flags (u32), untrustedServer (bool 1B),
                        # protocolName (string, type 12 - separate routine, prefix
                        # form unconfirmed). Vary only the string prefix.
                        hdr = struct.pack('<QQ', 0, 0)
                        rf = struct.pack('<IIII', 0x11d82194, 1, 5, 3) + b'\x00' + struct.pack('<I', 0)
                        I = struct.pack('<H', 2)
                        lp = lambda b: struct.pack('<I', len(b)) + b
                        candidates = [
                            ("LPhdr count LPrec",  I + lp(hdr) + struct.pack('<I', 1) + lp(rf)),
                            ("inlinehdr count LPrec", I + hdr + struct.pack('<I', 1) + lp(rf)),
                            ("LPhdr count inlinerec", I + lp(hdr) + struct.pack('<I', 1) + rf),
                            ("nohdr count LPrec",  I + struct.pack('<I', 1) + lp(rf)),
                            ("LP wholebody", I + lp(hdr + struct.pack('<I', 1) + lp(rf))),
                        ]
                        label, response = candidates[_GW_PROBE_INDEX % len(candidates)]
                        _GW_PROBE_INDEX += 1
                        emit(f"gateway PROBE candidate [{label}] -> {response.hex()}")
                    elif gateway_reply == 'id2':
                        # Decoded responder reply: id 2 with the server's 128-bit
                        # peer identity as {seq,src} (copied whole into ctx+0x20 by
                        # 0x00561180) and the bootstrap protocol record.
                        response = negotiation_reply(payload, (peer_group<<40)|1, 1)
                        emit(f"gateway id-2 reply sent ({len(response)} B) -> {response.hex()}")
                    else:
                        builder = catalogue_offer if gateway_reply == 'offer' else offer_response
                        hashes = parse_offer(payload)
                        # The client offers the protocols of the peer group in its
                        # gateway peer id (0x00561ac0); accept bootstrap-only or the
                        # exact exported group catalogue, nothing else.
                        catalogue_match = gateway_hashes is not None and hashes == gateway_hashes
                        response = builder(payload, gateway_hashes) if catalogue_match else builder(payload)
                        emit(f"gateway {gateway_reply} reply sent ({len(response)} B); offered "
                             f"{len(hashes)} protocol hash(es), catalogue group match={catalogue_match}"
                             + (f", hashes={[hex(h) for h in hashes]}" if len(hashes) <= 4 else ""))
                    raw.sendall(outbound.apply(gateway_frame(response)))
                    offered = True
                elif payload == bytes((bootstrap_channel,2)):
                    emit('gateway negotiation acknowledgement received (bootstrap version 3)')
                elif (response := heartbeat_response(payload,bootstrap_channel)) is not None:
                    raw.sendall(outbound.apply(gateway_frame(response)))
                    emit('gateway heartbeat exchanged (bootstrap version 4)')
                elif lobby_service is not None and (response := lobby_service.receive(payload)) is not None:
                    raw.sendall(outbound.apply(gateway_frame(response)))
                    emit(f'initial lobby identity reply 20500 sent ({len(response)} B; contents omitted)')
                    initial_due = time.monotonic() + initial_delay
                elif lobby_service is not None and (answer := lobby_service.answer(payload)) is not None:
                    mid,reply = answer
                    raw.sendall(outbound.apply(gateway_frame(reply)))
                    emit(f'lobby request answered with {mid} ({len(reply)} B; contents omitted)')
                elif lobby_service is not None and (summary := lobby_service.describe(payload)) is not None:
                    emit(f'lobby request (not answered): {summary}')
                if (lobby_service is not None and lobby_service.sent and not lobby_service.updates_sent
                        and time.monotonic() >= initial_due):
                    # Optionally deferred: sent on the first client packet (heartbeats
                    # arrive every 5 s) once --lobby-initial-delay has elapsed.
                    for mid,update in lobby_service.initial_notifications():
                        raw.sendall(outbound.apply(gateway_frame(update)))
                        emit(f'initial-data notification {mid} sent ({len(update)} B; contents omitted)')
            return
        data = raw.recv(4096)
        emit(f"after server proof: client sent {len(data)} B" + (" (closed)" if not data else " (contents omitted)"))
    except (OSError, EOFError, ValueError) as e:
        emit(f"connection error: {e}")
    finally:
        raw.close()


# Own-key lobby referrals: the container port of the single (or first pair)
# client on any probe port, as before, and the launcher pair mode's second
# client container port only for its dedicated host port.
OWN_KEY_REFERRALS = {'127.0.0.1:1119': (1119, None), '127.0.0.1:1129': (1129, 21129)}


def own_key_referral_port(referral_host, probe_port):
    """Container port named by an allowed own-key referral, else None."""
    entry = OWN_KEY_REFERRALS.get(referral_host)
    if entry is None or (entry[1] is not None and probe_port != entry[1]):
        return None
    return entry[0]


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
    ap.add_argument("--account-id", type=int, default=1001,
                    help="local account number (EntityId low half) granted with --battle-tag; see tools/accounts.py")
    ap.add_argument("--referral-host", default="127.0.0.1:1119",
                    help="hostv4 returned for the Balancer referral (ReferralInfo); "
                         "'' keeps the empty-response behaviour")
    ap.add_argument("--lobby-private-key", help="operator's own RSA-2048/e=65537 PEM, outside Git")
    ap.add_argument("--lobby-integrity-key", help="local 64-byte client integrity input, outside Git")
    ap.add_argument("--lobby-credential-delay", type=int, choices=range(0,31), default=12,
                    help="bounded scheduling delay for the owned client key installer (0..30 seconds)")
    ap.add_argument("--lobby-packet-capture", help="optional bounded first gateway packet capture outside Git")
    ap.add_argument("--gateway-capture-count", type=int, choices=range(1,5), default=1,
                    help="try capturing the first 1..4 packets; candidates over 4096 bytes are skipped")
    ap.add_argument("--lobby-peer-group", type=int, choices=(0,13), default=0,
                    help="native peer-id protocol group: 0 bootstrap or 13 lobby service interfaces")
    ap.add_argument("--gateway-catalogue", help="104319 interface metadata exported from the owned client")
    ap.add_argument("--lobby-login-schema", help="opt-in experimental 20500 reply using the numeric lobby login schemas")
    ap.add_argument("--lobby-hero-list", action="append", default=[], type=lambda v: int(v,16),
                    help="opt-in hero-record GUID (hex, type 0x75) for 20505 list 0; repeatable, max 64")
    ap.add_argument("--lobby-preload-graph", action="append", default=[], type=lambda v: int(v,16),
                    help="opt-in statescript graph GUID (hex, type 0x1b) for 20505 list 1 resource requests; max 64")
    ap.add_argument("--lobby-preload-definition", action="append", default=[], type=lambda v: int(v,16),
                    help="opt-in entity definition GUID (hex, type 3) added to the same 20505 list 1")
    ap.add_argument("--lobby-preload-progression", action="append", default=[], type=lambda v: int(v,16),
                    help="opt-in hero progression GUID (hex, raw 0x0ea0) added to the same 20505 list 1")
    ap.add_argument("--lobby-preload-stack-item", action="append", default=[], type=lambda v: int(v,16),
                    help="opt-in statescript state-stack item GUID (hex, raw 0x0d60) added to the same 20505 list 1")
    ap.add_argument("--lobby-unlock-schema", help="opt-in numeric 24900 unlock-state schema (protocol/unlocks-104319.json)")
    ap.add_argument("--lobby-unlocks", help="opt-in file of type-0xA5 unlock GUIDs (hex, whitespace/comma separated) sent as one 24900")
    ap.add_argument("--lobby-initial-data", choices=('keys','keys-hotfix','keys-hotfix-player','keys-hotfix-player-settings','full'),
                    help="opt-in empty key/hotfix lists (20504/20505), optionally our local player record (20502) "
                         "and default account preferences (20802); requires login schemas")
    ap.add_argument("--lobby-queue-reply", type=int, choices=range(23300, 23334),
                    help="diagnostic: answer game-queue request 24000 with this empty 23300-family message")
    ap.add_argument("--lobby-queue-schema", help="numeric 23300-family layouts for an explicit queue-reply experiment")
    ap.add_argument("--lobby-instance-referral", action='store_true',
                    help="experimental plain 20600 loopback referral for Training; game transport remains unverified")
    ap.add_argument("--lobby-instance-schema", help="numeric 20600 layout for the instance-referral experiment")
    ap.add_argument("--lobby-initial-delay", type=int, choices=range(0, 31), default=0,
                    help="seconds to wait after the 20500 identity reply before sending the initial data")
    ap.add_argument("--gateway-reply", choices=("offer", "ack", "probe", "id2"), default="ack",
                    help="reply to the client's bootstrap offer: 'ack' sends empty message id 3, "
                         "which the 104319 client accepts (negotiated state, id-4 heartbeats); "
                         "'offer' (id-1 echo), 'id2' (decoded responder record reply, only valid "
                         "for a ctx+0x84 bit-0 peer) and 'probe' are diagnostic controls that the "
                         "client rejects")
    args = ap.parse_args()
    if not 1 <= args.account_id < 2**32:
        ap.error('--account-id must be 1..2^32-1')
    credential = None
    gateway_hashes = None
    login_messages = None
    if args.lobby_initial_data and not args.lobby_login_schema:
        ap.error('initial data requires the initial lobby login reply and numeric schemas')
    if args.lobby_hero_list and (args.lobby_initial_data in (None,'keys') or len(args.lobby_hero_list)>64
            or len(set(args.lobby_hero_list))!=len(args.lobby_hero_list)
            or any(g>>48!=0x02e0 or not g&0xffffffffffff for g in args.lobby_hero_list)):
        ap.error('hero list needs 20505 initial data and up to 64 unique type-0x75 hero GUIDs')
    if args.lobby_preload_graph and (args.lobby_initial_data in (None,'keys') or len(args.lobby_preload_graph)>64
            or len(set(args.lobby_preload_graph))!=len(args.lobby_preload_graph)
            or any(g>>48!=0x0580 or not g&0xffffffffffff for g in args.lobby_preload_graph)):
        ap.error('graph preload needs 20505 initial data and up to 64 unique type-0x1b graph GUIDs')
    if args.lobby_preload_definition and (args.lobby_initial_data in (None,'keys')
            or len(args.lobby_preload_graph)+len(args.lobby_preload_definition)>64
            or len(set(args.lobby_preload_definition))!=len(args.lobby_preload_definition)
            or any(g>>48!=0x0400 or not g&0xffffffffffff for g in args.lobby_preload_definition)):
        ap.error('definition preload needs 20505 initial data and unique type-3 definition GUIDs (64 total)')
    if args.lobby_preload_progression and (args.lobby_initial_data in (None,'keys')
            or len(args.lobby_preload_graph)+len(args.lobby_preload_definition)+len(args.lobby_preload_progression)>64
            or len(set(args.lobby_preload_progression))!=len(args.lobby_preload_progression)
            or any(g>>48!=0x0ea0 or not g&0xffffffffffff for g in args.lobby_preload_progression)):
        ap.error('progression preload needs 20505 initial data and unique hero progression GUIDs (64 total)')
    if args.lobby_preload_stack_item and (args.lobby_initial_data in (None,'keys')
            or len(args.lobby_preload_graph)+len(args.lobby_preload_definition)+len(args.lobby_preload_progression)
               +len(args.lobby_preload_stack_item)>64
            or len(set(args.lobby_preload_stack_item))!=len(args.lobby_preload_stack_item)
            or any(g>>48!=0x0d60 or not g&0xffffffffffff for g in args.lobby_preload_stack_item)):
        ap.error('stack-item preload needs 20505 initial data and unique raw-0x0d60 GUIDs (64 total)')
    if args.lobby_queue_reply is not None and (not args.lobby_login_schema or not args.lobby_queue_schema):
        ap.error('queue-reply experiments require initial login and queue schemas')
    if args.lobby_queue_schema and args.lobby_queue_reply is None:
        ap.error('queue schemas require an explicit queue-reply experiment')
    if args.lobby_instance_referral and (not args.lobby_login_schema or not args.lobby_instance_schema
                                        or args.lobby_queue_reply is not None):
        ap.error('instance experiment requires initial login and instance schemas and no queue-reply experiment')
    if args.lobby_instance_schema and not args.lobby_instance_referral:
        ap.error('instance schemas require an explicit instance-referral experiment')
    if args.lobby_peer_group == 13:
        if not args.gateway_catalogue or not args.lobby_private_key or not args.lobby_integrity_key:
            ap.error('peer group 13 requires own credential inputs and a native interface catalogue')
        from gateway_protocol import load_catalogue
        gateway_hashes = load_catalogue(args.gateway_catalogue, 13)
    unlock_list = []
    if args.lobby_login_schema:
        if args.lobby_peer_group != 13 or args.gateway_reply != 'ack':
            ap.error('initial lobby reply requires peer group 13 and the accepted gateway acknowledgement')
        from gateway_codec import load_messages
        login_messages = load_messages(args.lobby_login_schema)
        if args.lobby_queue_schema:
            queue_messages = load_messages(args.lobby_queue_schema)
            if login_messages.keys() & queue_messages.keys():
                ap.error('queue schemas duplicate initial login schemas')
            login_messages.update(queue_messages)
            from lobby_service import QUEUE_SCHEMA, QUEUE_REPLY_SCHEMA
            if ((QUEUE_SCHEMA,24000) not in login_messages
                    or (QUEUE_REPLY_SCHEMA,args.lobby_queue_reply) not in login_messages
                    or QUEUE_REPLY_SCHEMA not in gateway_hashes):
                ap.error('queue experiment requires its request, selected reply and registered protocol')
        if (0x3c7e3468,21800) not in login_messages or (0xf5ff548a,20500) not in login_messages:
            ap.error('initial lobby reply requires hello and identity reply schemas')
        if args.lobby_instance_schema:
            instance_messages=load_messages(args.lobby_instance_schema)
            if login_messages.keys() & instance_messages.keys():
                ap.error('instance schemas duplicate initial login schemas')
            login_messages.update(instance_messages)
            from instance_referral import INSTANCE_SCHEMA
            from lobby_service import QUEUE_SCHEMA
            if ((INSTANCE_SCHEMA,20600) not in login_messages or (QUEUE_SCHEMA,24000) not in login_messages
                    or INSTANCE_SCHEMA not in gateway_hashes):
                ap.error('instance experiment requires registered request/referral schemas')
        if args.lobby_unlocks:
            if not args.lobby_unlock_schema or not args.lobby_initial_data:
                ap.error('unlock state requires its schema and initial data')
            unlock_messages=load_messages(args.lobby_unlock_schema)
            if login_messages.keys() & unlock_messages.keys():
                ap.error('unlock schema duplicates initial login schemas')
            login_messages.update(unlock_messages)
            unlock_list=[int(v,16) for v in open(args.lobby_unlocks,encoding='utf-8').read().replace(',',' ').split()]
        if args.lobby_initial_data:
            from lobby_service import InitialLobby
            initial_ids={'keys':(20504,),'keys-hotfix':(20504,20505),'keys-hotfix-player':(20504,20505,20502),
                         'keys-hotfix-player-settings':(20504,20505,20502,20802),
                         'full':(20504,20505,20502,20802,20700)}[args.lobby_initial_data]
            if any((InitialLobby.schema_of(mid),mid) not in login_messages for mid in initial_ids):
                ap.error('initial data requires each selected notification schema')
    # The instance referral (20600) names the same owned container port as the
    # allow-listed lobby referral: 1129 only for the pair's dedicated 21129 probe.
    instance_port = 1119
    if args.lobby_private_key or args.lobby_integrity_key:
        referral_port = own_key_referral_port(args.referral_host, args.port)
        if not args.serve or not args.lobby_private_key or not args.lobby_integrity_key or referral_port is None:
            ap.error('own lobby credential requires --serve, both key inputs and the exact loopback referral')
        from lobby_credential import load_key, load_integrity, build_credential
        credential = build_credential(load_key(args.lobby_private_key), load_integrity(args.lobby_integrity_key),
                                      port=referral_port)
        instance_port = referral_port

    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(args.cert, args.key)
    if args.tls_max:
        ctx.maximum_version = {"1.2": ssl.TLSVersion.TLSv1_2, "1.3": ssl.TLSVersion.TLSv1_3}[args.tls_max]
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE  # we do not require a client cert

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # On Windows SO_REUSEADDR lets a second probe bind the same port and steal
    # connections (a stale probe contaminated runs); require exclusive use.
    if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
    else:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", args.port))
    srv.listen(8)
    with open(args.log, "a", encoding="utf-8") as log:
        print(f"bgs observing TLS server on 127.0.0.1:{args.port}", flush=True)
        accepted = 0
        while True:
            raw, addr = srv.accept()
            accepted += 1
            raw.settimeout(10)
            # The CA probe imports our CA shortly after the first connection
            # opens, so only that first handshake is delayed.
            if args.handshake_delay and accepted == 1: time.sleep(args.handshake_delay)
            if accepted > 1:
                # Follow-on connections (e.g. to the referral hostv4) may not be
                # TLS. Peek at the first byte: 0x16 = TLS handshake record.
                try: first = raw.recv(1, socket.MSG_PEEK)
                except OSError as e: first = e
                if first != b"\x16":
                    line = (f"{now()} connection #{accepted} from {addr}: "
                            + (f"no data ({first})" if isinstance(first, OSError)
                               else "closed without data" if first == b""
                               else f"non-TLS first byte 0x{first[0]:02x}"))
                    print(line, flush=True); log.write(line + "\n"); log.flush()
                    if first == b"H" and args.serve:
                        from lobby_service import InitialLobby
                        lobby_service = InitialLobby(gateway_hashes,login_messages,args.battle_tag,args.lobby_initial_data,args.account_id,
                                                     args.lobby_queue_reply,args.lobby_instance_referral,
                                                     args.lobby_hero_list,args.lobby_preload_graph+args.lobby_preload_definition+args.lobby_preload_progression+args.lobby_preload_stack_item,
                                                     unlock_list,instance_port=instance_port) if login_messages is not None else None
                        threading.Thread(target=serve_lobby,
                            args=(raw, addr, accepted, log, 0, credential, args.lobby_credential_delay, args.lobby_packet_capture,
                                  args.lobby_peer_group, gateway_hashes, args.gateway_capture_count,
                                  args.gateway_reply, lobby_service, args.lobby_initial_delay), daemon=True).start()
                    else:
                        threading.Thread(target=observe_raw, args=(raw, addr, accepted, log), daemon=True).start()
                    continue
            try:
                tls = ctx.wrap_socket(raw, server_side=True)
            except (ssl.SSLError, OSError) as e:
                line = f"{datetime.datetime.now().isoformat(timespec='seconds')} TLS handshake FAILED from {addr}: {e}"
                print(line, flush=True); log.write(line + "\n"); log.flush()
                raw.close(); continue
            threading.Thread(target=handle, args=(tls, addr, log, args.serve, args.battle_tag, args.no_grant,
                                                  args.referral_host or None, args.account_id), daemon=True).start()


if __name__ == "__main__":
    main()
