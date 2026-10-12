"""Framing fixtures only; no original client login or service replies."""
import importlib.util
import io
from pathlib import Path
import struct
import unittest

spec = importlib.util.spec_from_file_location('probe', Path(__file__).resolve().parents[1] / 'tools/bnet-probe.py')
probe = importlib.util.module_from_spec(spec); spec.loader.exec_module(probe)


class Fragmented:
    def __init__(self, data): self.data = bytearray(data); self.closed = False
    def recv(self, size):
        chunk = bytes(self.data[:min(size, 1)]); del self.data[:len(chunk)]; return chunk
    def settimeout(self, _): pass
    def close(self): self.closed = True


class ProbeTests(unittest.TestCase):
    def test_fragmentation_and_secret_omission(self):
        header = b'\x08\x00\x10\x01\x28\x06\x6a\x06SECRET'
        frame = struct.pack('>H', len(header)) + header + b'SECRET'
        hlen, fields, count = probe.read_frame(Fragmented(frame))
        self.assertEqual((hlen, fields[2], count), (len(header), [1], 6))
        conn, log = Fragmented(frame), io.StringIO()
        probe.handle(conn, ('127.0.0.1', 1), log)
        self.assertTrue(conn.closed); self.assertNotIn('SECRET', log.getvalue())
        self.assertIn('body bytes=6', log.getvalue())

    def test_truncated_frames_stop(self):
        for data in (b'', b'\0', b'\0\x04\x08', b'\0\x02\x28\x05X'):
            with self.assertRaises(EOFError): probe.read_frame(Fragmented(data))

    def test_malformed_headers(self):
        for data in (b'', b'\0\0', b'\x08\x80', b'\x08' + b'\xff' * 10,
                     b'\x0a\x03x', b'\x0dX', b'\x09X', b'\x0b'):
            with self.assertRaises(ValueError): probe.decode_header(data)

    def test_body_bounds_and_duplicate_lengths(self):
        for header in (b'\x28\x01\x28\x01', b'\x2a\x01x', b'\x28\xff\xff\xff\x7f'):
            with self.assertRaises(ValueError):
                probe.read_frame(Fragmented(struct.pack('>H', len(header)) + header))
        self.assertEqual(probe.read_frame(Fragmented(b'\0\x02\x08\0'))[2], 0)


if __name__ == '__main__': unittest.main()
