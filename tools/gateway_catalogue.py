"""Export bounded interface metadata from an owned final-client dump.

Output contains protocol hashes, id ranges, flags, groups and optional numeric
message field descriptors only.
No executable bytes, keys, game assets or account data are exported.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import struct


def extract_message(dump, schema_hash, message_id):
    """Read numeric field descriptors for a selected registered message only."""
    image = dump.image_base
    if type(schema_hash) is not int or type(message_id) is not int or not 0<schema_hash<=0xffffffff or not 0<message_id<65536:
        raise ValueError('message identity bounds')
    area = dump.read(image+0x2c80000, 0x80000)
    needle = struct.pack('<IH', schema_hash, message_id)
    matches = []
    start = 0
    while (index := area.find(needle, start)) >= 0:
        if index >= 24:
            pointer = struct.unpack_from('<Q', area, index-8)[0]
            if image+0x2c80000 <= pointer < image+0x2f00000:
                matches.append(pointer)
        start = index+1
    if len(matches) != 1:
        raise ValueError('message metadata is absent or ambiguous')
    remaining = [1024]
    def fields(table, ancestors=()):
        if table in ancestors or len(ancestors) >= 8:
            raise ValueError('recursive/deep message field table')
        result = []
        for index in range(128):
            raw = dump.read(table+index*48, 48)
            if len(raw) != 48:
                raise ValueError('incomplete message field table')
            _, kind, offset, width, count, child, _, _ = struct.unpack('<QIIIiQQQ', raw)
            if kind == 17:
                return result
            remaining[0] -= 1
            if remaining[0] < 0 or kind not in range(16) or count < -1 or count > 1024 or offset > 65536 or not 0<width<=65536:
                raise ValueError('unsupported message descriptor/bounds')
            record = dict(kind=kind, offset=offset, width=width, count=count)
            if kind == 14:
                if not image+0x2c80000 <= child < image+0x2f00000:
                    raise ValueError('nested field table outside descriptor region')
                record['fields'] = fields(child, ancestors+(table,))
            result.append(record)
        raise ValueError('unterminated message field table')
    return dict(schema_hash=schema_hash, message_id=message_id, fields=fields(matches[0]))


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
    parser.add_argument('--message', action='append', default=[], help='optional schema-hash:message-id numeric descriptors')
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('local_dump', Path(__file__).parent/'offline-launch/re/mdump.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    dump = module.Dump(args.dump)
    try:
        result = extract(dump, args.peer_va)
        if args.message:
            result['messages'] = []
            for value in args.message:
                schema, message = (int(part,0) for part in value.split(':'))
                if not any(row['schema_hash']==schema and row['first_id']<=message<row['end_id'] for row in result['protocols']):
                    raise ValueError('message outside registered protocol range')
                result['messages'].append(extract_message(dump, schema, message))
    finally:
        dump.f.close()
    with open(args.out, 'x', encoding='utf-8') as output:
        json.dump(result, output, indent=2); output.write('\n')
    print(f"Exported {len(result['protocols'])} interface metadata records.")


if __name__ == '__main__': main()
