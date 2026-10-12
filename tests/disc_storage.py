"""Synthetic CASC index framing and published lookup3 known-answer checks."""
import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('storage', Path(__file__).resolve().parents[1] / 'scripts/Rebuild-DiscStorage.py')
storage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(storage)


class StorageTests(unittest.TestCase):
    def test_jenkins_known_answers(self):
        # Bob Jenkins lookup3, default seeds; covers empty input and final mixing.
        self.assertEqual(storage.lookup3(b'')[0], 0xdeadbeef)
        self.assertEqual(storage.lookup3(b'a')[0], 0x58d68708)
        self.assertEqual(storage.lookup3(b'abc')[0], 0x0e397631)

    def test_index_framing_and_location(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / '0300000001.idx'
            entries = [b'\x30' * 9 + ((2 << 30) | 17).to_bytes(5, 'big') + struct.pack('<I', 60),
                       b'\x10' * 9 + (42).to_bytes(5, 'big') + struct.pack('<I', 35)]
            storage.write_index(path, 3, entries)
            data = path.read_bytes()
            self.assertEqual(struct.unpack_from('<I', data)[0], 16)
            self.assertEqual(struct.unpack_from('<H6B', data, 8), (7, 3, 0, 4, 5, 9, 30))
            self.assertEqual(data[16:24], bytes.fromhex('0000000040000000'))
            self.assertEqual(len(data), 0xa0000)
            self.assertEqual(data[24:32], bytes(8))
            self.assertEqual(struct.unpack_from('<I', data, 32)[0], 36)
            self.assertEqual(data[40:49], b'\x10' * 9)
            self.assertEqual(int.from_bytes(data[67:72], 'big'), (2 << 30) | 17)
            self.assertEqual(struct.unpack_from('<I', data, 72)[0], 60)

    def test_archive_integrity_regression_vectors(self):
        # Envelope format independently confirmed by the native 27578 reader.
        common = '0f0e0d0c0b0a09080706050403020100990000000000bc7caab9'
        for offset, checksum in [(0, 'c9a917c7'), (17, 'd016b481'),
                                 (1073741794, '04eaa0fd')]:
            self.assertEqual(storage.archive_header(bytes(range(16)), 123, offset).hex(), common + checksum)
        with self.assertRaises(ValueError): storage.archive_header(bytes(15), 123, 0)
        with self.assertRaises(ValueError): storage.archive_header(bytes(16), 0xffffffff, 0)

    def test_native_required_build_columns(self):
        text = storage.build_info('aa' * 16, 'bb' * 16, ('cc' * 16, 'dd' * 16, 851, 852))
        header, row = [line.split('|') for line in text.splitlines()]
        values = dict(zip(header, row))
        required = {'Branch', 'Active', 'Build Key', 'CDN Key', 'Install Key',
                    'IM Size', 'CDN Path', 'CDN Hosts', 'Tags', 'Armadillo', 'Last Activated'}
        self.assertTrue(required.issubset({key.split('!')[0] for key in header}))
        self.assertEqual(len(header), len(row))
        self.assertEqual(values['IM Size!DEC:4'], '851')
        self.assertEqual(values['Install Key!HEX:16'], 'dd' * 16)


if __name__ == '__main__':
    unittest.main()
