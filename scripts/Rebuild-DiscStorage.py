"""Experimental, offline CASC layout from the inspected 1.0.1.27578 disc.

Preserves encrypted records unchanged. Generated build configuration is inferred
from disc manifests, not an original Blizzard build configuration. Requires a
staging folder produced by Prepare-DiscClient.py; never overwrites Data.
Index format reference: CascLib 38a3466, CascIndexFiles.cpp/CascStructs.h (MIT).
Jenkins lookup3 algorithm: Bob Jenkins, public domain.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import struct

spec = importlib.util.spec_from_file_location('stage', Path(__file__).with_name('Prepare-DiscClient.py'))
stage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stage)

MASK = 0xffffffff


def rotate(value, bits):
    value &= MASK
    return ((value << bits) | (value >> (32 - bits))) & MASK


def lookup3(data, primary=0, secondary=0):
    a = b = c = (0xdeadbeef + len(data) + primary) & MASK
    c = (c + secondary) & MASK
    cursor = 0
    while len(data) - cursor > 12:
        x, y, z = struct.unpack_from('<III', data, cursor)
        a = (a + x) & MASK; b = (b + y) & MASK; c = (c + z) & MASK
        a = ((a - c) ^ rotate(c, 4)) & MASK; c = (c + b) & MASK
        b = ((b - a) ^ rotate(a, 6)) & MASK; a = (a + c) & MASK
        c = ((c - b) ^ rotate(b, 8)) & MASK; b = (b + a) & MASK
        a = ((a - c) ^ rotate(c, 16)) & MASK; c = (c + b) & MASK
        b = ((b - a) ^ rotate(a, 19)) & MASK; a = (a + c) & MASK
        c = ((c - b) ^ rotate(b, 4)) & MASK; b = (b + a) & MASK
        cursor += 12
    tail = data[cursor:]
    if not tail:
        return c, b
    a = (a + int.from_bytes(tail[:4], 'little')) & MASK
    b = (b + int.from_bytes(tail[4:8], 'little')) & MASK
    c = (c + int.from_bytes(tail[8:12], 'little')) & MASK
    c = ((c ^ b) - rotate(b, 14)) & MASK
    a = ((a ^ c) - rotate(c, 11)) & MASK
    b = ((b ^ a) - rotate(a, 25)) & MASK
    c = ((c ^ b) - rotate(b, 16)) & MASK
    a = ((a ^ c) - rotate(c, 4)) & MASK
    b = ((b ^ a) - rotate(a, 14)) & MASK
    c = ((c ^ b) - rotate(b, 24)) & MASK
    return c, b


def write_index(path, bucket, entries):
    header = struct.pack('<H6B', 7, bucket, 0, 4, 5, 9, 30) + (1 << 30).to_bytes(8, 'big')
    high = low = 0
    entries.sort()
    for entry in entries:
        high, low = lookup3(entry, high, low)
    payload = b''.join(entries)
    data = struct.pack('<II', len(header), lookup3(header)[0]) + header + bytes(8)
    data += struct.pack('<II', len(payload), high) + payload
    if len(data) >= 0xa0000: raise ValueError('Index bucket exceeds fixed allocation')
    path.write_bytes(data + bytes(0xa0000 - len(data)))


# CASC envelope integrity constants documented by CascLib's VerifyHeaderSpan.
OFFSET_MASKS = (0x049396b8, 0x72a82a9b, 0xee626cca, 0x9917754f,
                0x15de40b1, 0xf5a8a9b6, 0x421eac7e, 0xa9d55c9a,
                0x317fd40c, 0x04faf80d, 0x3d6be971, 0x52933cfd,
                0x27f64b7d, 0xc6f5c11b, 0xd5757e3a, 0x6c388745)


def archive_header(key, encoded_size, offset):
    if len(key) != 16 or encoded_size < 0 or encoded_size + 30 > MASK or offset < 0:
        raise ValueError('Archive envelope bounds')
    header = key[::-1] + struct.pack('<I', encoded_size + 30) + bytes(2)
    header += struct.pack('<I', lookup3(header, 0x3d6be971)[0])
    position = (offset + 30) & MASK
    position = struct.pack('<I', position ^ OFFSET_MASKS[position & 15])
    folded = bytearray(4)
    for index, byte in enumerate(header): folded[(offset + index) & 3] ^= byte
    return header + bytes(folded[(offset + index) & 3] ^ position[(offset + index) & 3]
                          for index in range(26, 30))


def build_info(build_key, cdn_key, install):
    fields = [('Branch!STRING:0', 'pro'), ('Active!DEC:1', '1'),
              ('Build Key!HEX:16', build_key), ('CDN Key!HEX:16', cdn_key),
              ('Install Key!HEX:16', install[1]), ('IM Size!DEC:4', str(install[2])),
              ('CDN Path!STRING:0', ''), ('CDN Hosts!STRING:0', ''),
              ('Tags!STRING:0', 'TPWin:SPWin:DevReg:enUS:speech:text:EExt'),
              ('Armadillo!STRING:0', ''), ('Last Activated!STRING:0', ''),
              ('Version!STRING:0', '1.0.1.27578'), ('Product!STRING:0', 'pro')]
    return '|'.join(key for key, _ in fields) + '\n' + '|'.join(value for _, value in fields) + '\n'


def rebuild(iso, destination):
    destination = Path(destination).resolve()
    repo = Path(__file__).resolve().parents[1]
    if destination == repo or repo in destination.parents:
        raise ValueError('Game data must stay outside the source repository')
    executable = destination / 'Overwatch.exe'
    if hashlib.sha256(executable.read_bytes()).hexdigest() != '8d33644f844b81e830c12749371c80a83d26f81b186265897ca5d67f6e7e665d':
        raise ValueError('Requires the verified 1.0.1.27578 executable')
    data_dir = destination / 'Data'
    if data_dir.exists() or (destination / '.build.info').exists():
        raise ValueError('Existing storage/configuration will not be overwritten')
    disc = stage.disc_module.Disc(iso)
    output = None
    try:
        records = list(stage.records(disc))
        metadata_keys = {'root':'0cf46751dc11df8419febdbaf444ca7e',
                         'install':'eed90f42128bdcb38a2b593bd36adac7',
                         'download':'c4544ad8ae012afc37606d422e5929ee',
                         'encoding':'7fc41bc4b5c2ab58c16dc2dad5c3cdb9'}
        metadata = {}
        for kind, key in metadata_keys.items():
            _, offset, size = next(row for row in records if row[0] == key)
            decoded = stage.disc_module.decode_blte(disc.read(offset, size))
            metadata[kind] = (hashlib.md5(decoded).hexdigest(), key, len(decoded), size)
        storage_dir = data_dir / 'casc'
        archive_dir = storage_dir / 'data'
        archive_dir.mkdir(parents=True)
        (destination / 'cache' / 'casc').mkdir(parents=True, exist_ok=True)
        buckets = [[] for _ in range(16)]
        segment = -1
        archive_offset = 1 << 30
        total = 0
        for number, (key, offset, size) in enumerate(records):
            if archive_offset + size + 30 > 1 << 30:
                if output: output.close()
                segment += 1
                output = (archive_dir / f'data.{segment:03d}').open('xb')
                archive_offset = 0
            encoded_key = bytes.fromhex(key)
            head = disc.read(offset, min(size, 12))
            if head[:4] != b'BLTE':
                raise ValueError('Expected BLTE record')
            header_size = int.from_bytes(head[4:8], 'big')
            # EKey is the BLTE header MD5 for chunked files, the full blob MD5 otherwise.
            blob = disc.read(offset, size)
            if hashlib.md5(blob[:header_size] if header_size else blob).digest() != encoded_key:
                raise ValueError('Encoded-key mismatch')
            output.write(archive_header(encoded_key, size, archive_offset))
            output.write(blob)
            prefix = encoded_key[:9]
            folded = 0
            for byte in prefix: folded ^= byte
            bucket = (folded & 15) ^ (folded >> 4)
            entry = prefix + ((segment << 30) | archive_offset).to_bytes(5, 'big') + struct.pack('<I', size + 30)
            buckets[bucket].append(entry)
            archive_offset += size + 30
            total += size + 30
            if number % 10000 == 0: print(f'Copied {number}/{len(records)} encoded records', flush=True)
        output.close(); output = None
        for bucket, entries in enumerate(buckets):
            write_index(archive_dir / f'{bucket:02x}00000001.idx', bucket, entries)
        build_text = '# Inferred offline disc configuration; not original CDN metadata\n'
        build_text += 'build-uid = pro\nbuild-name = 1.0.1.27578\n'
        for kind, (content, key, decoded_size, encoded_size) in metadata.items():
            keys = f'{content} {key}' if kind == 'encoding' else content
            build_text += f'{kind} = {keys}\n{kind}-size = {decoded_size} {encoded_size}\n'
        cdn_text = '# Offline only; no network hosts\narchives =\n'
        def config(text):
            encoded = text.encode('ascii')
            key = hashlib.md5(encoded).hexdigest()
            target = storage_dir / 'config' / key[:2] / key[2:4] / key
            target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(encoded)
            return key
        build_key = config(build_text); cdn_key = config(cdn_text)
        (destination / '.build.info').write_text(build_info(build_key, cdn_key, metadata['install']), encoding='ascii')
        report = {'experimental':True, 'original_build_config':False, 'records':len(records),
                  'encoded_bytes':total, 'segments':segment + 1, 'build_key':build_key,
                  'cdn_key':cdn_key, 'metadata':metadata, 'encrypted_payloads_preserved':True,
                  'resource_loading_verified':False}
        (destination / 'storage-report.json').write_text(json.dumps(report, indent=2), encoding='utf8')
        print(json.dumps(report, indent=2))
    finally:
        if output: output.close()
        disc.stream.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('iso'); parser.add_argument('destination')
    args = parser.parse_args()
    rebuild(args.iso, args.destination)
