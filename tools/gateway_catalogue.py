"""Export bounded interface metadata from an owned final-client dump.

Output contains protocol hashes, id ranges, flags and group numbers only.
No executable bytes, keys, game assets or account data are exported.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import struct


def extract(dump, peer):
    image = dump.image_base
    def unpack(address, fmt):
        data = dump.read(address, struct.calcsize(fmt))
        if len(data) != struct.calcsize(fmt):
            raise ValueError('incomplete gateway catalogue memory')
        return struct.unpack(fmt, data)
    if unpack(peer, '<Q')[0] != image + 0x2609988 or unpack(peer+8, '<Q')[0] != image + 0x26099c0:
        raise ValueError('original gateway peer identities differ')
    if unpack(peer+0x1c, '<I')[0] != 1:
        raise ValueError('expected an initiating gateway peer')
    context = unpack(peer+0x98, '<Q')[0]
    if not context or context % 8:
        raise ValueError('invalid gateway protocol context')
    table, count, capacity = unpack(context+0x80, '<QQQ')
    capacity &= 0x7fffffffffffffff
    if not table or not 0 < count <= 256 or not count <= capacity <= 512:
        raise ValueError('gateway catalogue bounds')
    rows, seen = [], set()
    for index in range(count):
        schema, first, end, flags, group = unpack(table+index*64, '<IIIII')
        if not schema or not 0 < first < end <= 65536 or group > 65535 or (group,schema) in seen:
            raise ValueError('gateway catalogue record bounds/duplicates')
        seen.add((group,schema))
        rows.append(dict(schema_hash=schema, first_id=first, end_id=end, flags=flags, group=group))
    if rows[0] != dict(schema_hash=0x11d82194, first_id=1, end_id=5, flags=3, group=0):
        raise ValueError('gateway bootstrap profile differs')
    return {'build':104319, 'protocols':rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dump', required=True)
    parser.add_argument('--peer-va', type=lambda value:int(value,0), required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('local_dump', Path(__file__).parent/'offline-launch/re/mdump.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    dump = module.Dump(args.dump)
    try:
        result = extract(dump, args.peer_va)
    finally:
        dump.f.close()
    with open(args.out, 'x', encoding='utf-8') as output:
        json.dump(result, output, indent=2); output.write('\n')
    print(f"Exported {len(result['protocols'])} interface metadata records.")


if __name__ == '__main__': main()
