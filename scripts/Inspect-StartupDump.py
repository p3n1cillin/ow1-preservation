"""Bounded, read-only inspection of local Windows minidump image memory.

Maps captured module bytes and locates diagnostic strings and native logs.
Never runs the client or writes recovered proprietary image bytes.
"""
import argparse
import bisect
import re
import struct


class Dump:
    def __init__(self, path):
        self.stream = open(path, 'rb')
        try:
            self._parse()
        except Exception:
            self.stream.close()
            raise

    def _parse(self):
        self.stream.seek(0, 2); self.size = self.stream.tell()
        header = self.read(0, 32)
        if header[:4] != b'MDMP': raise ValueError('Not a minidump')
        count, directory = struct.unpack_from('<II', header, 8)
        if count > 128: raise ValueError('Excessive stream count')
        self.directories = {}
        for index in range(count):
            kind, size, offset = struct.unpack('<III', self.read(directory + index * 12, 12))
            if kind == 0: continue  # DbgHelp pads directories with UnusedStream entries.
            if offset + size > self.size: raise ValueError('Stream bounds')
            if kind in self.directories: raise ValueError('Duplicate dump stream')
            self.directories[kind] = (offset, size)
        if 4 not in self.directories or 9 not in self.directories:
            raise ValueError('Requires module and full-memory streams')
        offset, size = self.directories[4]
        count = struct.unpack('<I', self.read(offset, 4))[0]
        if count > 4096 or 4 + count * 108 > size: raise ValueError('Module list bounds')
        self.modules = []
        for index in range(count):
            record = self.read(offset + 4 + index * 108, 108)
            base, image_size, _, timestamp, name_offset = struct.unpack_from('<QIIII', record)
            name_size = struct.unpack('<I', self.read(name_offset, 4))[0]
            if name_size > 65536 or name_size % 2: raise ValueError('Module name bounds')
            name = self.read(name_offset + 4, name_size).decode('utf-16le')
            self.modules.append({'base':base, 'bytes':image_size, 'timestamp':timestamp, 'name':name})
        self.regions = []
        offset, size = self.directories[9]
        count, file_offset = struct.unpack('<QQ', self.read(offset, 16))
        if count > 100000 or 16 + count * 16 > size: raise ValueError('Memory descriptors bounds')
        for index in range(count):
            address, length = struct.unpack('<QQ', self.read(offset + 16 + index * 16, 16))
            if file_offset + length > self.size: raise ValueError('Memory data bounds')
            self.regions.append((address, length, file_offset))
            file_offset += length
        self.regions.sort()
        if any(a + n > b for (a, n, _), (b, _, _) in zip(self.regions, self.regions[1:])):
            raise ValueError('Overlapping memory regions')
        self.starts = [row[0] for row in self.regions]

    def read(self, offset, length):
        if offset < 0 or length < 0 or offset + length > self.size: raise ValueError('Dump file bounds')
        self.stream.seek(offset); data = self.stream.read(length)
        if len(data) != length: raise ValueError('Truncated dump')
        return data

    def memory(self, address, length):
        if length < 0: raise ValueError('Negative memory length')
        index = bisect.bisect_right(self.starts, address) - 1
        if index < 0: raise ValueError('Memory not captured')
        start, size, offset = self.regions[index]
        if address + length > start + size: raise ValueError('Memory range crosses captured region')
        return self.read(offset + address - start, length)

    def image(self, module):
        if module['bytes'] > 64 * 1024 * 1024: raise ValueError('Image size limit')
        data = bytearray(module['bytes'])
        base = module['base']; end = base + len(data)
        for start, size, offset in self.regions:
            low = max(start, base); high = min(start + size, end)
            if low < high: data[low - base:high - base] = self.read(offset + low - start, high - low)
        return bytes(data)

    def close(self):
        self.stream.close()

    def logs(self):
        """Actual timestamped log messages, excluding dormant format strings."""
        pattern = rb'[A-Za-z][A-Za-z0-9/_.-]{0,50}: \[20[0-9]{6}T[0-9:]{6,8}\][^\0\r\n]{0,400}'
        result = set()
        for _, size, offset in self.regions:
            carry = b''
            for cursor in range(0, size, 8 * 1024 * 1024):
                data = carry + self.read(offset + cursor, min(8 * 1024 * 1024, size - cursor))
                result.update(re.findall(pattern, data))
                carry = data[-1024:]
        return sorted(result)


def inspect(path, terms, logs=False):
    if any(not term for term in terms): raise ValueError('Search terms must not be empty')
    dump = Dump(path)
    try:
        module = next((m for m in dump.modules if m['name'].lower().endswith('overwatch.exe')), None)
        if module is None: raise ValueError('Overwatch module not captured')
        print('module', module)
        image = dump.image(module)
        for term in terms:
            for encoding in ('utf8', 'utf-16le'):
                needle = term.encode(encoding)
                cursor = 0
                while (cursor := image.find(needle, cursor)) >= 0:
                    print('string', repr(term), encoding, 'RVA', hex(cursor))
                    cursor += len(needle)
        if logs:
            for entry in dump.logs(): print(entry.decode('ascii', errors='replace'))
    finally:
        dump.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dump'); parser.add_argument('--find', action='append', default=[])
    parser.add_argument('--logs', action='store_true', help='Print captured timestamped game log messages')
    args = parser.parse_args()
    inspect(args.dump, args.find, args.logs)
