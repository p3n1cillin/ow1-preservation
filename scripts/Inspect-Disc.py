"""Read-only inspection of ISO9660 media and the observed Blizzard DD v1 index.

Does not execute the installer, write game files, or contact services. Disc index
interpretation is experimental; bounds and BLTE checksums are checked before use.
"""
import argparse
import hashlib
import json
import struct
import zlib
from datetime import datetime, timezone


def decode_blte(blob, limit=128 * 1024 * 1024):
    if blob[:4] != b"BLTE":
        return blob
    if len(blob) < 8:
        raise ValueError("Truncated BLTE")
    header_size = int.from_bytes(blob[4:8], "big")

    def chunk_decode(chunk):
        if chunk[:1] == b"N":
            result = chunk[1:]
        elif chunk[:1] == b"Z":
            decoder = zlib.decompressobj()
            result = decoder.decompress(chunk[1:], limit + 1)
            if not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:
                raise ValueError("Incomplete, trailing or excessive compressed data")
        else:
            raise ValueError("Unsupported BLTE chunk mode")
        if len(result) > limit:
            raise ValueError("Decoded size limit")
        return result

    if not header_size:
        return chunk_decode(blob[8:])
    if len(blob) < 12 or blob[8] != 15:
        raise ValueError("Unsupported BLTE chunk table")
    count = int.from_bytes(blob[9:12], "big")
    if header_size != 12 + count * 24 or header_size > len(blob):
        raise ValueError("Invalid BLTE header size")
    offset = header_size
    result = bytearray()
    for index in range(count):
        entry = blob[12 + index * 24:36 + index * 24]
        compressed, decoded = struct.unpack(">II", entry[:8])
        if decoded > limit - len(result) or compressed > len(blob) - offset:
            raise ValueError("BLTE bounds")
        chunk = blob[offset:offset + compressed]
        offset += compressed
        if hashlib.md5(chunk).digest() != entry[8:]:
            raise ValueError("BLTE checksum mismatch")
        data = chunk_decode(chunk)
        if len(data) != decoded:
            raise ValueError("BLTE decoded size mismatch")
        result.extend(data)
    if offset != len(blob):
        raise ValueError("Trailing BLTE bytes")
    return bytes(result)


class Disc:
    def __init__(self, path):
        self.stream = open(path, "rb")
        self.stream.seek(0, 2)
        self.size = self.stream.tell()
        self.files = {}
        volume = self.read(16 * 2048, 2048)
        if volume[:7] != b"\x01CD001\x01":
            raise ValueError("Requires ISO9660 primary volume descriptor")
        if int.from_bytes(volume[128:130], "little") != 2048:
            raise ValueError("Unsupported ISO block size")
        self.label = volume[40:72].decode("ascii").rstrip()
        self.walk(*self.record(volume[156:190])[:2], depth=0)

    def read(self, offset, size):
        if offset < 0 or size < 0 or offset + size > self.size:
            raise ValueError("ISO bounds")
        self.stream.seek(offset)
        result = self.stream.read(size)
        if len(result) != size:
            raise ValueError("Truncated ISO")
        return result

    @staticmethod
    def record(record):
        if len(record) < 34 or 33 + record[32] > len(record):
            raise ValueError("ISO directory record bounds")
        return (int.from_bytes(record[2:6], "little") * 2048,
                int.from_bytes(record[10:14], "little"), record[25],
                record[33:33 + record[32]].decode("ascii").split(";")[0])

    def walk(self, offset, size, prefix="", depth=0):
        if depth > 8 or size > 16 * 1024 * 1024:
            raise ValueError("Directory limit")
        data = self.read(offset, size)
        cursor = 0
        while cursor < len(data):
            length = data[cursor]
            if not length:
                cursor = (cursor // 2048 + 1) * 2048
                continue
            entry = self.record(data[cursor:cursor + length])
            cursor += length
            if entry[3] in ("\x00", "\x01"):
                continue
            name = prefix + entry[3]
            self.files[name.lower()] = entry
            if entry[2] & 2:
                self.walk(entry[0], entry[1], name + "/", depth + 1)

    def file(self, name, limit=16 * 1024 * 1024):
        offset, size, flags, _ = self.files[name.lower()]
        if flags & 2 or size > limit:
            raise ValueError("File extraction limit")
        return self.read(offset, size)

    def inspect(self, max_records):
        index = self.file("data/0000")
        if index[:4] != b"DD\x01\x10" or len(index) < 40:
            raise ValueError("Unsupported experimental DD index")
        count = int.from_bytes(index[4:8], "big")
        if index[8:10] != b"\x01\x03" or len(index) != 40 + count * 24:
            raise ValueError("Unsupported DD groups or size")
        report = {"volume": self.label, "iso_bytes": self.size,
                  "files": {name: entry[1] for name, entry in self.files.items()},
                  "disc_configuration": self.file("disc.id").decode("ascii"),
                  "index_md5": hashlib.md5(index).hexdigest(), "index_entries": count,
                  "scanned_records": 0, "interesting_payloads": [], "unsupported_payloads": 0,
                  "first_chunk_modes": {}, "skipped_large_payloads": 0}
        covered = 40
        for group in range(3):
            number, offset, length = struct.unpack(">HII", index[10 + group * 10:20 + group * 10])
            if offset != covered or length % 24 or offset + length > len(index):
                raise ValueError("DD group bounds")
            covered += length
            archive = "data/" + format(number, "04x")
            base, archive_size, _, _ = self.files[archive]
            for item in range(min(max_records, length // 24)):
                entry = index[offset + item * 24:offset + (item + 1) * 24]
                position, size = struct.unpack(">II", entry[16:])
                if position + size > archive_size:
                    raise ValueError("DD archive range")
                report["scanned_records"] += 1
                header = self.read(base + position, min(size, 12))
                if header[:4] == b"BLTE" and len(header) >= 8:
                    blte_header_size = int.from_bytes(header[4:8], "big")
                    mode_offset = blte_header_size if blte_header_size else 8
                    if mode_offset >= size:
                        raise ValueError("BLTE first chunk offset")
                    mode = self.read(base + position + mode_offset, 1).decode("ascii", errors="replace")
                    modes = report["first_chunk_modes"]
                    modes[mode] = modes.get(mode, 0) + 1
                    if mode not in ("N", "Z"):
                        report["unsupported_payloads"] += 1
                        continue
                if size > 64 * 1024 * 1024:
                    report["skipped_large_payloads"] += 1
                    continue
                try:
                    payload = decode_blte(self.read(base + position, size))
                except ValueError:
                    report["unsupported_payloads"] += 1
                    continue
                kind = None
                if payload[:2] in (b"MZ", b"IN", b"EN"):
                    kind = payload[:2].decode("ascii")
                elif b"build-name" in payload[:4096] or payload.startswith(b"#"):
                    kind = "config"
                if kind:
                    details = {"archive": archive, "offset": position,
                               "encoded_key": entry[:16].hex(), "decoded_bytes": len(payload), "kind": kind}
                    if kind == "config":
                        details["description"] = payload.splitlines()[0].decode("ascii", errors="replace")
                    if kind == "IN":
                        details["install_entries"] = install_entries(payload)
                    if kind == "MZ":
                        details["sha256"] = hashlib.sha256(payload).hexdigest()
                        try:
                            import pefile
                            pe = pefile.PE(data=payload, fast_load=False)
                            details["machine"] = hex(pe.FILE_HEADER.Machine)
                            details["pe_timestamp_utc"] = datetime.fromtimestamp(pe.FILE_HEADER.TimeDateStamp, timezone.utc).isoformat()
                            fixed = getattr(pe, "VS_FIXEDFILEINFO", [])
                            if fixed:
                                version = fixed[0]
                                details["fixed_file_version"] = '.'.join(str(value) for value in (
                                    version.FileVersionMS >> 16, version.FileVersionMS & 65535,
                                    version.FileVersionLS >> 16, version.FileVersionLS & 65535))
                            details["versions"] = {}
                            for group_info in getattr(pe, "FileInfo", []):
                                for info in group_info:
                                    for table in getattr(info, "StringTable", []):
                                        for key, value in table.entries.items():
                                            details["versions"][key.decode("utf8", errors="replace")] = value.decode("utf8", errors="replace")
                            pe.close()
                        except ImportError:
                            details["versions"] = "Install pefile for optional PE version inspection"
                    report["interesting_payloads"].append(details)
        if covered != len(index):
            raise ValueError("Uncovered DD records")
        download = decode_blte(self.file("data/0001"))
        report["download_manifest_magic"] = download[:3].hex()
        report["download_manifest_bytes"] = len(download)
        return report


def install_entries(data):
    if len(data) < 10 or data[:4] != b"IN\x01\x10":
        raise ValueError("Unsupported install manifest")
    tags, count = struct.unpack(">HI", data[4:10])
    if count > 100000:
        raise ValueError("Install entry limit")
    offset = 10
    mask_size = (count + 7) // 8

    def name():
        nonlocal offset
        end = data.find(b'\x00', offset)
        if end == -1 or end - offset > 4096:
            raise ValueError("Install name bounds")
        result = data[offset:end].decode("utf8")
        offset = end + 1
        return result

    for _ in range(tags):
        name()
        offset += 2 + mask_size
        if offset > len(data):
            raise ValueError("Install tag bounds")
    entries = []
    for _ in range(count):
        filename = name()
        if offset + 20 > len(data):
            raise ValueError("Install entry bounds")
        entries.append({"name": filename, "content_md5": data[offset:offset + 16].hex(),
                        "bytes": int.from_bytes(data[offset + 16:offset + 20], "big")})
        offset += 20
    if offset != len(data):
        raise ValueError("Trailing install manifest bytes")
    return entries


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("iso")
    parser.add_argument("--max-records", type=int, default=100, help="Records scanned per archive (default 100)")
    args = parser.parse_args()
    if args.max_records < 0:
        parser.error("max-records must be nonnegative")
    disc = Disc(args.iso)
    try:
        print(json.dumps(disc.inspect(args.max_records), indent=2))
    finally:
        disc.stream.close()
