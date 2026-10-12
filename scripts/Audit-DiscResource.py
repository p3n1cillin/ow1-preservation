"""Read-only audit of a disc resource: EN mappings, ISO index and package copies.

Uses the original hash-checked 27578 encoding manifest and offline CascLib.
An absent indexed EKey proves the declared encoded file is absent from this
disc's index, not that no copy exists elsewhere or in unreadable package data.
No network calls, asset extraction, replacement or storage modifications.
Encoding layout reference: CascLib 38a3466 CascStructs.h (MIT).
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import struct


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(filename))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


stage = module('stage', 'Prepare-DiscClient.py')
packages = module('packages', 'Inspect-DiscPackages.py')
ENCODING_EKEY = '7fc41bc4b5c2ab58c16dc2dad5c3cdb9'
ENCODING_CKEY = 'a964b91b8c2413c6f7284b904e841d29'


def encoding_mapping(data, wanted):
    if len(wanted) != 16 or len(data) < 22 or data[:5] != b'EN\x01\x10\x10' or data[17]:
        raise ValueError('Requires EN v1 / 16-byte keys')
    page_size = int.from_bytes(data[5:7], 'big') * 1024
    page_count = int.from_bytes(data[9:13], 'big')
    specs_size = int.from_bytes(data[18:22], 'big')
    table = 22 + specs_size
    start = table + page_count * 32
    if not 1024 <= page_size <= 65536 or not 0 < page_count <= 65536:
        raise ValueError('Encoding page limits')
    if start + page_count * page_size > len(data):
        raise ValueError('Encoding table bounds')
    matches = []
    entries = 0
    for number in range(page_count):
        head = data[table + number * 32:table + (number + 1) * 32]
        page = data[start + number * page_size:start + (number + 1) * page_size]
        if hashlib.md5(page).digest() != head[16:]:
            raise ValueError('Encoding page checksum mismatch')
        cursor = 0
        first = True
        while cursor < len(page):
            if cursor + 2 > len(page):
                raise ValueError('Truncated encoding entry')
            count = int.from_bytes(page[cursor:cursor + 2], 'little')
            if not count:
                if any(page[cursor:]): raise ValueError('Nonzero encoding page padding')
                break
            end = cursor + 22 + count * 16
            if end > len(page): raise ValueError('Encoding entry bounds')
            key = page[cursor + 6:cursor + 22]
            if first and key != head[:16]: raise ValueError('Encoding first key mismatch')
            first = False
            if key == wanted:
                matches.append({'bytes':int.from_bytes(page[cursor + 2:cursor + 6], 'big'),
                                'encoded_keys':[page[p:p + 16].hex() for p in range(cursor + 22, end, 16)]})
            cursor = end
            entries += 1
    if len(matches) > 1: raise ValueError('Duplicate content-key mapping')
    return {'pages_hash_verified':page_count, 'entries_checked':entries,
            'mapping':matches[0] if matches else None}


def asset_available(storage, package, record):
    guid, size, flags, offset, key = record
    try:
        if flags & 0x40000000:
            blob = storage.read(package['content_key'], True)
            packages.checked_hash(blob, package['content_key'])
            if len(blob) != package['content_bytes'] or offset + size > len(blob):
                raise ValueError('Bundled asset bounds')
            asset = blob[offset:offset + size]
        else:
            asset = storage.read(key, True)
        packages.checked_hash(asset, key)
        if len(asset) != size: raise ValueError('Asset size mismatch')
        return {'verified_available':True}
    except (OSError, ValueError) as error:
        return {'verified_available':False, 'error':str(error)}


def audit(iso, folder, dll, guid, key):
    disc = stage.disc_module.Disc(iso)
    try:
        records = list(stage.records(disc))
        indexed = {entry[0] for entry in records}
        _, offset, size = next(row for row in records if row[0] == ENCODING_EKEY)
        blob = disc.read(offset, size)
        header_size = int.from_bytes(blob[4:8], 'big')
        if hashlib.md5(blob[:header_size] if header_size else blob).hexdigest() != ENCODING_EKEY:
            raise ValueError('Encoding encoded-key mismatch')
        encoding = stage.disc_module.decode_blte(blob)
        if hashlib.md5(encoding).hexdigest() != ENCODING_CKEY:
            raise ValueError('Encoding content-key mismatch')
        mapping = encoding_mapping(encoding, key)
        mapped = mapping['mapping']
        present = [value for value in mapped['encoded_keys'] if value in indexed] if mapped else []
    finally:
        disc.stream.close()
    storage = packages.Storage(folder, dll)
    try:
        rows = {}
        manifests = [
            (b'Manifest/Win_SPWin_RDEV_LenUS_EExt.apm', '1c03e74827ec7e42781f83bb8a1c5683'),
            (b'Manifest/Win_SPWin_speech_RDEV_LenUS_EExt.apm', '9f8caf03d04d9c85292cf420bd3c341e')]
        for name, expected in manifests:
            blob = storage.read(name)
            packages.checked_hash(blob, bytes.fromhex(expected))
            parsed = packages.apm_packages(blob)
            if rows.keys() & parsed.keys(): raise ValueError('Overlapping package identities')
            rows.update(parsed)
        grouped = {}
        for identity, row in rows.items(): grouped.setdefault(row['key'], []).append(identity)
        matches, failures = [], []
        checked = 0
        for metadata_key, identities in grouped.items():
            try:
                blob = storage.read(metadata_key, True)
                packages.checked_hash(blob, metadata_key)
                package = packages.package_records(blob)
            except (OSError, ValueError, EOFError) as error:
                failures.append({'metadata_key':metadata_key.hex(), 'packages':[hex(p) for p in identities], 'error':str(error)})
                continue
            checked += 1
            for record in package['records']:
                resource, size, flags, offset, content_key = record
                if resource != guid and content_key != key: continue
                matches.append({'packages':[hex(p) for p in identities], 'guid':hex(resource),
                                'content_key':content_key.hex(), 'bytes':size, 'flags':hex(flags),
                                'offset':offset, 'exact_content_key':content_key == key,
                                **asset_available(storage, package, record)})
        return {'build':'1.0.1.27578', 'offline':True, 'target_guid':hex(guid), 'target_content_key':key.hex(),
                'iso_index_records':len(records), 'encoding':mapping,
                'encoded_keys_present_in_iso_index':present,
                'declared_encoded_file_absent_from_iso_index':bool(mapped) and not present,
                'declared_package_rows':len(rows), 'distinct_metadata_keys':len(grouped),
                'package_metadata_hash_verified_and_parsed':checked,
                'unreadable_package_metadata':failures, 'matching_records':matches,
                'available_exact_package_copy_found':any(m['exact_content_key'] and m['verified_available'] for m in matches),
                'scope':'Indexed encoded files and readable English base/speech packages only; unreadable metadata and external copies remain unknown.'}
    finally:
        storage.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('iso'); parser.add_argument('folder'); parser.add_argument('--casclib', required=True)
    parser.add_argument('--guid', type=lambda value:int(value, 16), default=0x07a000000000001d)
    parser.add_argument('--content-key', default='80c124710acc8a1aacb282d895631909')
    args = parser.parse_args()
    print(json.dumps(audit(args.iso, args.folder, args.casclib, args.guid, bytes.fromhex(args.content_key)), indent=2))
