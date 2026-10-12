"""Synthetic dump bounds and captured-log checks; no game data required."""
import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('dump_reader', Path(__file__).resolve().parents[1] / 'scripts/Inspect-StartupDump.py')
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


def fixture():
    data = bytearray(512)
    struct.pack_into('<4sIIIIIQ', data, 0, b'MDMP', 0, 2, 32, 0, 0, 0)
    struct.pack_into('<III', data, 32, 4, 112, 64)
    struct.pack_into('<III', data, 44, 9, 32, 176)
    struct.pack_into('<I', data, 64, 1)
    struct.pack_into('<QIIII', data, 68, 0x100000, 128, 0, 123, 208)
    name = 'Overwatch.exe'.encode('utf-16le')
    struct.pack_into('<I', data, 208, len(name)); data[212:212 + len(name)] = name
    struct.pack_into('<QQQQ', data, 176, 1, 256, 0x100000, 128)
    message = b'CASC: [20261011T13:29:27] {1234} ERR synthetic failure\0'
    data[256:256 + len(message)] = message
    return data


class DumpTests(unittest.TestCase):
    def open(self, data):
        path = Path(self.folder.name) / 'synthetic.dmp'
        path.write_bytes(data)
        return reader.Dump(path)

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)

    def test_captured_image_and_actual_logs(self):
        dump = self.open(fixture())
        self.addCleanup(dump.close)
        self.assertEqual(dump.modules[0]['name'], 'Overwatch.exe')
        self.assertTrue(dump.image(dump.modules[0]).startswith(b'CASC: '))
        self.assertEqual(len(dump.logs()), 1)
        with self.assertRaises(ValueError): dump.memory(0x10007f, 2)
        with self.assertRaises(ValueError): dump.memory(0x100000, -1)

    def test_malformed_directory_and_memory(self):
        for offset, value in [(12, 500), (184, 500), (200, 0xffffffff)]:
            data = fixture(); struct.pack_into('<I', data, offset, value)
            with self.assertRaises(ValueError): self.open(data)
        with self.assertRaises(ValueError): self.open(fixture()[:31])

    def test_dbghelp_unused_directory_padding(self):
        data = fixture()
        data[384:496] = data[64:176]
        struct.pack_into('<I', data, 8, 4)
        struct.pack_into('<III', data, 56, 0, 0, 0)
        struct.pack_into('<I', data, 40, 384)
        struct.pack_into('<III', data, 68, 0, 0, 0)
        dump = self.open(data)
        self.addCleanup(dump.close)
        self.assertEqual(len(dump.modules), 1)


if __name__ == '__main__':
    unittest.main()
