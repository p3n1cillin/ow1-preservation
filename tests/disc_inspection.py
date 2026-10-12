import hashlib
import importlib.util
from pathlib import Path
import struct
import unittest
import zlib

spec = importlib.util.spec_from_file_location("disc_inspection", Path(__file__).resolve().parents[1] / "scripts/Inspect-Disc.py")
disc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(disc)


class DiscInspection(unittest.TestCase):
    def test_unchunked_plain_and_compressed(self):
        self.assertEqual(disc.decode_blte(b'BLTE\0\0\0\0Nmetadata'), b'metadata')
        blob = b'BLTE\0\0\0\0Z' + zlib.compress(b'metadata' * 100)
        self.assertEqual(disc.decode_blte(blob), b'metadata' * 100)
        with self.assertRaises(ValueError):
            disc.decode_blte(blob, limit=10)

    def test_chunk_checksum_and_bounds(self):
        chunk = b'Nmetadata'
        header = b'BLTE\0\0\0\x24\x0f\0\0\x01'
        blob = header + struct.pack('>II', len(chunk), 8) + hashlib.md5(chunk).digest() + chunk
        self.assertEqual(disc.decode_blte(blob), b'metadata')
        with self.assertRaises(ValueError):
            disc.decode_blte(blob[:-1] + b'x')
        with self.assertRaises(ValueError):
            disc.decode_blte(blob[:-1])
        with self.assertRaises(ValueError):
            disc.decode_blte(blob + b'extra')

    def test_unsupported_encrypted_chunk(self):
        with self.assertRaises(ValueError):
            disc.decode_blte(b'BLTE\0\0\0\0Eencrypted')

    def test_install_manifest_bounds(self):
        content = bytes.fromhex('00112233445566778899aabbccddeeff')
        blob = b'IN\x01\x10\0\0\0\0\0\x01Overwatch.exe\0' + content + struct.pack('>I',123)
        self.assertEqual(disc.install_entries(blob), [{'name':'Overwatch.exe', 'content_md5':content.hex(), 'bytes':123}])
        with self.assertRaises(ValueError):
            disc.install_entries(blob[:-1])
        with self.assertRaises(ValueError):
            disc.install_entries(blob + b'extra')


if __name__ == '__main__':
    unittest.main()
