"""Bounded read-only STU V2 root-field metadata inspection.

Format reference: MIT OWLib/TankLib, df522f0ceea8748dcb51463ceb990234ceb45c9a:
teStructuredData*, STUInstance and teStructuredDataAssetRef. No source vendored.
Full upstream notice: docs/licenses/OWLib.txt.
This reads serialized field bags; it does not define native object layouts.
"""
import struct


def header_checksum(header):
    """OWLib CRC64 header convention: reflected Jones, seed all ones."""
    crc = 0
    for byte in header:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ (0x95ac9329ac4bc9b5 if crc & 1 else 0)
    return crc ^ 0xffffffffffffffff


def asset_reference(encoded, checksum, field_hash):
    if not encoded: return 0
    value = encoded ^ checksum ^ (field_hash | (field_hash << 32))
    data = bytearray(value.to_bytes(8, 'little'))
    for a, b in ((0, 3), (7, 1), (2, 6), (4, 5)):
        data[a], data[b] = data[b], data[a]
    return int.from_bytes(data, 'little')


class StructuredData:
    def __init__(self, blob):
        if len(blob) < 36 or len(blob) > 32 * 1024 * 1024 or blob[:4] == b'STUD':
            raise ValueError('Requires bounded STU V2 input')
        self.blob = blob
        self.checksum = header_checksum(blob[:36])

        def bag(at, width):
            count, offset = struct.unpack_from('<ii', blob, at)
            if count < 0 or count > 50000 or (count and offset < 36):
                raise ValueError('STU bag count/offset')
            if count and offset + count * width > len(blob): raise ValueError('STU bag bounds')
            return count, offset

        count, offset = bag(0, 16)
        self.instances = [struct.unpack_from('<IIii', blob, offset + n * 16) for n in range(count)]
        inline_count, inline_offset = bag(8, 8)
        for n in range(inline_count):
            _, size = struct.unpack_from('<Ii', blob, inline_offset + n * 8)
            if size < 0 or size > 1000000: raise ValueError('STU inline count')
        count, offset = bag(16, 8)
        self.bags = []
        for n in range(count):
            fields, field_offset = bag(offset + n * 8, 8)
            parsed = [struct.unpack_from('<Ii', blob, field_offset + f * 8) for f in range(fields)]
            if any(size < 0 for _, size in parsed) or len({h for h, _ in parsed}) != fields:
                raise ValueError('Invalid or duplicate STU fields')
            self.bags.append(parsed)
        dyn_size, dyn_offset, data_offset = struct.unpack_from('<iii', blob, 24)
        if dyn_size < 0 or (dyn_size and (dyn_offset < 36 or dyn_offset + dyn_size > len(blob))):
            raise ValueError('STU dynamic-data bounds')
        if data_offset < 36 or data_offset > len(blob): raise ValueError('STU data offset')
        if any(size < 4 for _, _, _, size in self.instances) or sum(i[3] for i in self.instances) > len(blob) - data_offset:
            raise ValueError('STU instance-data bounds')
        self.dynamic = blob[dyn_offset:dyn_offset + dyn_size] if dyn_size else b''
        self.fields = {}
        if not self.instances: return
        limit = data_offset + self.instances[0][3]
        bag_index = struct.unpack_from('<i', blob, data_offset)[0]
        if bag_index == -1: return
        if not 0 <= bag_index < len(self.bags): raise ValueError('STU root field-bag index')
        cursor = data_offset + 4
        for field_hash, size in self.bags[bag_index]:
            if size == 0:
                if cursor + 4 > limit: raise ValueError('STU variable-size prefix bounds')
                size = struct.unpack_from('<i', blob, cursor)[0]; cursor += 4
            if size < 0 or cursor + size > limit: raise ValueError('STU root field bounds')
            self.fields[field_hash] = blob[cursor:cursor + size]
            cursor += size

    def reference(self, field_hash):
        data = self.fields.get(field_hash)
        if data is None: return None
        if len(data) != 8: raise ValueError('STU reference size differs')
        return asset_reference(struct.unpack('<Q', data)[0], self.checksum, field_hash)

    def string(self, field_hash):
        data = self.fields.get(field_hash)
        if data is None: return None
        if len(data) != 4: raise ValueError('STU string offset size differs')
        offset = struct.unpack('<i', data)[0]
        if offset == -1: return None
        if offset < 0 or offset + 4 > len(self.dynamic): raise ValueError('STU string header bounds')
        count = struct.unpack_from('<i', self.dynamic, offset)[0]
        if count == 0: return ''
        if count < 0 or count > 4096 or offset + 16 > len(self.dynamic): raise ValueError('STU string size bounds')
        text_offset = struct.unpack_from('<q', self.dynamic, offset + 8)[0]
        if text_offset < 0 or text_offset + count > len(self.dynamic): raise ValueError('STU string data bounds')
        return self.dynamic[text_offset:text_offset + count].decode('utf8')

    def map_header(self):
        if not self.instances or self.instances[0][0] != 0x02514b6a:
            raise ValueError('Root is not the known map-header type')
        return {'root_type': '02514b6a', 'instances': len(self.instances), 'root_fields': len(self.fields),
                'internal_name': self.string(0x506fa8d8),
                **{name: None if (value := self.reference(h)) is None else f'{value:016x}'
                   for name, h in [('map_guid', 0x4e87690f), ('base_map_guid', 0x38f33424),
                                   ('display_name_guid', 0x5db91ce2)]}}
