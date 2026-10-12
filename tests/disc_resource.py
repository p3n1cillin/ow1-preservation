"""Encoding-map corruption must not be reported as a missing game file."""
import hashlib
import importlib.util
from pathlib import Path
import struct
import unittest

spec = importlib.util.spec_from_file_location('audit', Path(__file__).resolve().parents[1] / 'scripts/Audit-DiscResource.py')
reader = importlib.util.module_from_spec(spec); spec.loader.exec_module(reader)


class ResourceAuditTests(unittest.TestCase):
    def fixture(self, count=2):
        entry = struct.pack('<H', count) + (46208).to_bytes(4, 'big') + b'A' * 16 + b'B' * (16 * count)
        page = entry + bytes(1024 - len(entry))
        header = b'EN\x01\x10\x10' + struct.pack('>HHII', 1, 1, 1, 0) + bytes(5)
        return header + b'A' * 16 + hashlib.md5(page).digest() + page

    def test_all_declared_encodings_and_absent_mapping(self):
        result = reader.encoding_mapping(self.fixture(), b'A' * 16)
        self.assertEqual(result['mapping'], {'bytes':46208, 'encoded_keys':['42' * 16, '42' * 16]})
        self.assertEqual(result['pages_hash_verified'], 1)
        self.assertIsNone(reader.encoding_mapping(self.fixture(), b'C' * 16)['mapping'])

    def test_corruption_truncation_and_limits(self):
        blob = self.fixture()
        corrupted = bytearray(blob); corrupted[-1] = 1
        bad_header = bytearray(blob); bad_header[3] = 15
        excessive = bytearray(blob); excessive[9:13] = (65537).to_bytes(4, 'big')
        for data in (b'', blob[:-1], corrupted, bad_header, excessive):
            with self.assertRaises(ValueError): reader.encoding_mapping(data, b'A' * 16)

    def test_bad_entry_with_valid_page_checksum(self):
        blob = bytearray(self.fixture()); blob[54:56] = b'\xff\xff'
        blob[38:54] = hashlib.md5(blob[54:]).digest()
        with self.assertRaises(ValueError): reader.encoding_mapping(blob, b'A' * 16)


if __name__ == '__main__': unittest.main()
