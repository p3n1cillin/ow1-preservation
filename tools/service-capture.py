"""Loopback protocol capture for private-service research.

Listens on 127.0.0.1 ports and records what a connecting client sends first:
for TLS, the ClientHello version, SNI and ALPN; otherwise a bounded hex prefix.
It never answers with protocol data, so it cannot complete a login. Use it
behind the launcher's container bridge to learn which endpoint and transport
a client uses before implementing a service.
"""
import argparse
import asyncio
import datetime
import struct


def parse_client_hello(data: bytes) -> dict:
    """Return the fields of a TLS ClientHello record, or raise ValueError."""
    if len(data) < 5 or data[0] != 0x16:
        raise ValueError("not a TLS handshake record")
    record_len = struct.unpack(">H", data[3:5])[0]
    body = data[5:5 + record_len]
    if len(body) < 4 or body[0] != 0x01:
        raise ValueError("not a ClientHello")
    pos = 4
    legacy_version = body[pos:pos + 2].hex(); pos += 2 + 32
    session_len = body[pos]; pos += 1 + session_len
    suites_len = struct.unpack(">H", body[pos:pos + 2])[0]; pos += 2 + suites_len
    comp_len = body[pos]; pos += 1 + comp_len
    result = {"record_version": data[1:3].hex(), "legacy_version": legacy_version,
              "cipher_suites": suites_len // 2, "sni": None, "alpn": [], "versions": []}
    if pos + 2 > len(body):
        return result
    ext_end = pos + 2 + struct.unpack(">H", body[pos:pos + 2])[0]; pos += 2
    while pos + 4 <= min(ext_end, len(body)):
        ext_type, ext_len = struct.unpack(">HH", body[pos:pos + 4]); pos += 4
        ext = body[pos:pos + ext_len]; pos += ext_len
        if ext_type == 0 and len(ext) >= 5:
            name_len = struct.unpack(">H", ext[3:5])[0]
            result["sni"] = ext[5:5 + name_len].decode("ascii", "replace")
        elif ext_type == 16 and len(ext) >= 2:
            p = 2
            while p < len(ext):
                n = ext[p]; result["alpn"].append(ext[p + 1:p + 1 + n].decode("ascii", "replace")); p += 1 + n
        elif ext_type == 43 and ext:
            result["versions"] = [ext[i:i + 2].hex() for i in range(1, 1 + ext[0], 2)]
    return result


async def handle(reader, writer, port, log):
    peer = writer.get_extra_info("peername")
    try:
        data = await asyncio.wait_for(reader.read(16384), timeout=15)
    except asyncio.TimeoutError:
        data = b""
    stamp = datetime.datetime.now().isoformat(timespec="seconds")
    try:
        summary = f"TLS {parse_client_hello(data)}"
    except (ValueError, IndexError, struct.error):
        summary = f"raw {len(data)} bytes: {data[:96].hex()}"
    line = f"{stamp} port {port} from {peer}: {summary}"
    print(line, flush=True)
    log.write(line + "\n"); log.flush()
    writer.close()


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ports", nargs="+", type=int)
    parser.add_argument("--log", default="service-capture.log")
    args = parser.parse_args()
    with open(args.log, "a", encoding="utf-8") as log:
        servers = [await asyncio.start_server(lambda r, w, p=p: handle(r, w, p, log), "127.0.0.1", p) for p in args.ports]
        print("listening on 127.0.0.1:" + ",".join(map(str, args.ports)), flush=True)
        await asyncio.gather(*(s.serve_forever() for s in servers))


if __name__ == "__main__":
    asyncio.run(main())
