"""Synthetic old package layouts, graph input bounds and asset hash checks."""
import gzip
import importlib.util
from pathlib import Path
import struct
import unittest

spec = importlib.util.spec_from_file_location('packages', Path(__file__).resolve().parents[1] / 'scripts/Inspect-DiscPackages.py')
reader = importlib.util.module_from_spec(spec); spec.loader.exec_module(reader)


class PackageTests(unittest.TestCase):
    def test_apm_identity_and_bounds(self):
        data = bytearray(96)
        struct.pack_into('<QIIII', data, 0, 1, 27578, 1, 0, 0x13636d66)
        struct.pack_into('<QQQQQIIQ16s', data, 24, 1, 2, 0, 3, 4, 5, 6, 7, b'A' * 16)
        self.assertEqual(reader.apm_packages(data)[4]['guid'], 2)
        for malformed in [data[:-1], b'', bytes(96)]:
            with self.assertRaises(ValueError): reader.apm_packages(malformed)
        struct.pack_into('<I', data, 12, 10001)
        with self.assertRaises(ValueError): reader.apm_packages(data)

    def fixture(self):
        record = struct.pack('<QIII16s', 123, 3, 0x40000000, 0, b'A' * 16)
        compressed = gzip.compress(record)
        data = bytearray(96 + len(compressed) + 4)
        struct.pack_into('<4Q', data, 0, 96, 96 + len(compressed), 96 + len(compressed), 0)
        struct.pack_into('<IIQI', data, 32, 22, 1, len(compressed), 1)
        struct.pack_into('<Q', data, 64, 3); data[76:92] = b'B' * 16
        data[96:-4] = compressed; struct.pack_into('<I', data, len(data) - 4, 456)
        return data

    def test_records_and_dependency_ids(self):
        parsed = reader.package_records(self.fixture())
        self.assertEqual(parsed['dependencies'], (456,))
        self.assertEqual(parsed['records'][0][:4], (123, 3, 0x40000000, 0))
        self.assertEqual(parsed['content_key'], b'B' * 16)
        for version in (1, *range(20, 28)):
            data = self.fixture(); struct.pack_into('<I', data, 32, version)
            self.assertEqual(reader.package_records(data)['records'], parsed['records'])

    def test_empty_loose_package(self):
        compressed = gzip.compress(b'')
        data = bytearray(96 + len(compressed))
        struct.pack_into('<4Q', data, 0, 96, len(data), len(data), 0)
        struct.pack_into('<IIQI', data, 32, 1, 0, len(compressed), 0)
        data[96:] = compressed
        package = reader.package_records(data)
        self.assertEqual(package['records'], [])
        self.assertEqual(package['content_bytes'], 0)
        self.assertEqual(package['content_key'], bytes(16))

    def test_header_and_decompression_bounds(self):
        for offset, value in [(0, 95), (24, 1), (32, 99), (36, 100001), (48, 4097)]:
            data = self.fixture(); struct.pack_into('<I', data, offset, value)
            with self.assertRaises(ValueError): reader.package_records(data)
        for data in [self.fixture()[:-1], b'', self.fixture()[:95]]:
            with self.assertRaises(ValueError): reader.package_records(data)
        data = self.fixture(); struct.pack_into('<I', data, 36, 0)
        with self.assertRaises(ValueError): reader.package_records(data)

    def test_hash_mismatch(self):
        with self.assertRaises(ValueError): reader.checked_hash(b'asset', b'A' * 16)


if __name__ == '__main__': unittest.main()
