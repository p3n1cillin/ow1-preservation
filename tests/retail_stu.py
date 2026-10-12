"""Synthetic serialized STU bounds and independent CRC/reference vectors."""
from pathlib import Path
import struct
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from retail_stu import StructuredData, asset_reference, header_checksum


def fixture():
    blob = bytearray(116)
    struct.pack_into('<9i', blob, 0, 1, 36, 0, 52, 1, 52, 24, 76, 100)
    struct.pack_into('<IIii', blob, 36, 0x02514b6a, 0, -1, 16)
    struct.pack_into('<ii', blob, 52, 2, 60)
    struct.pack_into('<IiIi', blob, 60, 0x4e87690f, 8, 0x506fa8d8, 4)
    struct.pack_into('<iIq', blob, 76, 3, 0, 16)
    blob[92:95] = b'map'
    struct.pack_into('<iQi', blob, 100, 0, 0, 0)
    return blob


class StructuredDataTests(unittest.TestCase):
    def test_checksum_and_reference_vectors(self):
        # Checksum obtained independently from OWLib's published lookup table.
        self.assertEqual(header_checksum(b'123456789'), 0x163926eb3b472635)
        # Input little-endian bytes 08 07 06 05 04 03 02 01 become
        # 05 01 02 08 03 04 06 07 under the documented disjoint swaps.
        self.assertEqual(asset_reference(0x0102030405060708, 0, 0), 0x0706040308020105)
        self.assertEqual(asset_reference(0, 0xffffffffffffffff, 0x12345678), 0)

    def test_root_fields_and_string(self):
        root = StructuredData(fixture()).map_header()
        self.assertEqual(root['internal_name'], 'map')
        self.assertEqual(root['map_guid'], '0000000000000000')
        self.assertEqual(root['root_fields'], 2)
        self.assertIsNone(root['base_map_guid'])

    def test_tables_and_instance_bounds(self):
        for offset, value in [(0, -1), (0, 50001), (4, 35), (4, 1000),
                              (24, -1), (28, 0), (32, 117), (48, 1000),
                              (56, 114), (64, -1), (100, 1)]:
            blob = fixture(); struct.pack_into('<i', blob, offset, value)
            with self.subTest(offset=offset, value=value), self.assertRaises(ValueError): StructuredData(blob)
        for blob in (b'', fixture()[:35], fixture()[:-1], b'STUD' + bytes(112)):
            with self.assertRaises(ValueError): StructuredData(blob)
        blob = fixture(); blob[68:72] = blob[60:64]
        with self.assertRaises(ValueError): StructuredData(blob)

    def test_variable_field_and_string_bounds(self):
        blob = fixture(); struct.pack_into('<i', blob, 64, 0); struct.pack_into('<i', blob, 104, -1)
        with self.assertRaises(ValueError): StructuredData(blob)
        for offset, kind, value in [(112, '<i', 24), (76, '<i', -1), (76, '<i', 4097), (84, '<q', 23)]:
            blob = fixture(); struct.pack_into(kind, blob, offset, value)
            with self.subTest(offset=offset, value=value), self.assertRaises(ValueError): StructuredData(blob).map_header()


if __name__ == '__main__': unittest.main()
