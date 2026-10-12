"""Reject unsafe bundle tables before reading any untrusted payload slices."""
import importlib.util
from pathlib import Path
import struct
import unittest

spec = importlib.util.spec_from_file_location('retail', Path(__file__).resolve().parents[1] / 'scripts/Inspect-RetailStorage.py')
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


class BundleTests(unittest.TestCase):
    def test_supported_offset_widths(self):
        for width in (1, 2, 4):
            end = 5 + 2 * (8 + width)
            fixture = struct.pack('<iB', 2, width)
            fixture += struct.pack('<Q', 17) + end.to_bytes(width, 'little')
            fixture += struct.pack('<Q', 23) + (end + 3).to_bytes(width, 'little') + b'abcdef'
            self.assertEqual(reader.bundle_entries(fixture), (end, {17: end, 23: end + 3}))

    def test_table_bounds(self):
        for fixture in (b'', bytes(4), struct.pack('<iB', -1, 1),
                        struct.pack('<iB', 1000001, 1), struct.pack('<iB', 1, 8),
                        struct.pack('<iB', 1, 4) + bytes(11)):
            with self.assertRaises(ValueError): reader.bundle_entries(fixture)

    def test_duplicate_identity_rejected(self):
        fixture = struct.pack('<iB', 2, 1) + struct.pack('<QBQB', 17, 23, 17, 24)
        with self.assertRaises(ValueError): reader.bundle_entries(fixture)


if __name__ == '__main__': unittest.main()
