"""Written bit patterns only; no native payload or key fixtures."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from instance_bits import MAX_BODY, Reader, Writer


class InstanceBitsTests(unittest.TestCase):
    def test_written_compact_vectors(self):
        for value, count, encoded in (
            (0, 19, '010000'), (0x3ffff, 19, 'ffff07'),
            (0x40000, 26, '02001000'), (0xffffff, 26, 'feffff03'),
            (0x1000000, 34, '0000000400'), (0xffffffff, 34, 'fcffffff03')):
            wire = bytes.fromhex(encoded)
            writer = Writer()
            writer.compact_u32(value)
            self.assertEqual((writer.finish(), writer.bit_count), (wire, count))
            reader = Reader(wire, bit_count=count)
            self.assertEqual(reader.compact_u32(), value)
            self.assertEqual(reader.position, count)
            # Every shorter bit limit is insufficient, including byte padding.
            for limit in range(count):
                with self.assertRaisesRegex(ValueError, 'truncated'):
                    Reader(wire, bit_count=limit).compact_u32()

    def test_unaligned_fields_and_word_boundary(self):
        writer = Writer()
        writer.write(0x55, 7)
        writer.write(0x1ab, 9)
        self.assertEqual(writer.finish(), bytes.fromhex('d5d5'))
        reader = Reader(writer.finish())
        self.assertEqual((reader.read(7), reader.read(9)), (0x55, 0x1ab))
        reader = Reader(bytes(7) + b'\x80\x01', bit_count=65)
        self.assertEqual((reader.read(32), reader.read(31), reader.read(2)), (0, 0, 3))

    def test_nonminimal_selector_and_padding(self):
        # The native reader accepts a full-width zero; writer chooses 18 bits.
        reader = Reader(bytes(5), bit_count=34)
        self.assertEqual(reader.compact_u32(), 0)
        self.assertEqual(reader.position, 34)
        writer = Writer()
        writer.write(1, 1)
        self.assertEqual(writer.finish(), b'\x01')
        with self.assertRaisesRegex(ValueError, 'truncated'):
            Reader(writer.finish(), bit_count=1).read(2)

    def test_bounds_and_nonmutating_rejected_operations(self):
        for data in (bytearray(), bytes(MAX_BODY + 1)):
            with self.assertRaises(ValueError): Reader(data)
        for limit in (-1, 9, True):
            with self.assertRaises(ValueError): Reader(b'\0', bit_count=limit)
        for value in (-1, 2**32, True):
            writer = Writer()
            with self.assertRaises(ValueError): writer.compact_u32(value)
            self.assertEqual(writer.bit_count, 0)
        reader = Reader(b'\0')
        writer = Writer()
        for width in (-1, 33, True):
            with self.assertRaises(ValueError): reader.read(width)
            with self.assertRaises(ValueError): writer.write(0, width)
        for value, width in ((2, 1), (-1, 1), (True, 1), (1, 0)):
            with self.assertRaises(ValueError): writer.write(value, width)
        self.assertEqual((reader.position, writer.bit_count), (0, 0))
        for _ in range(MAX_BODY): writer.write(0, 8)
        with self.assertRaises(ValueError): writer.write(1, 1)
        self.assertEqual(len(writer.finish()), MAX_BODY)
        writer = Writer()
        for _ in range(MAX_BODY - 1): writer.write(0, 8)
        writer.write(0, 7)
        before = writer.bit_count
        with self.assertRaises(ValueError): writer.compact_u32(0)
        self.assertEqual(writer.bit_count, before)


if __name__ == '__main__': unittest.main()
