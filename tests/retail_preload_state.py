"""Author-written preloader fixtures; no captured memory or asset identifiers."""
import json
from pathlib import Path
import struct
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import retail_login_state as login
import retail_preload_state as preload


class SavedMemory:
    image_base = 0x10000000

    def __init__(self):
        self.memory = {}
        self.root, self.table, self.service = 0x40000000, 0x40001000, 0x40002000
        self.integer(self.image_base + login.ROOT_RVA, self.root)
        self.integer(self.image_base + login.COOKIE_RVA, 0)
        self.integer(self.root + 0x140, login.TABLE_MASK ^ self.table)
        self.integer(self.table + preload.PRELOADER_SLOT * 8, self.service)
        self.integer(self.service, self.image_base + preload.PRELOADER_VFT)
        self.integer(self.service + 8, self.root ^ preload.OWNER_MASK)
        self.requests(False, [])
        self.requests(True, [])

    def put(self, address, value):
        self.memory.update({address + i: byte for i, byte in enumerate(value)})

    def integer(self, address, value, size=8):
        self.put(address, value.to_bytes(size, 'little'))

    def read(self, address, size):
        if any(address + i not in self.memory for i in range(size)): return b''
        return bytes(self.memory[address + i] for i in range(size))

    def requests(self, retained, records):
        array = 0x50000000 if retained else 0x50001000
        pointer, count, stride = (0x58, 0x60, 72) if retained else (0x2678, 0x2680, 64)
        self.integer(self.service + pointer, array)
        self.integer(self.service + count, len(records), 4)
        for i, (guid, key, submitted) in enumerate(records):
            row = bytearray(stride)
            struct.pack_into('<QQ', row, 0, key, guid)
            if retained: row[0x44] = submitted
            self.put(array + i * stride, row)


class PreloadTests(unittest.TestCase):
    def inspect(self, dump):
        with mock.patch.object(login, 'inspect', return_value={}):
            return preload.preload_state(dump)

    def test_empty_snapshot_is_not_completion(self):
        report = self.inspect(SavedMemory())
        self.assertEqual(report['configured']['request_count'], 0)
        self.assertEqual(report['retained']['submitted_request_count'], 0)
        self.assertNotIn('completed', json.dumps(report))

    def test_header_classification_and_submission_are_separate(self):
        dump = SavedMemory()
        header = preload.MAP_HEADER_TYPE | 42
        other = 0x023000000000007b
        dump.requests(False, [(header, 0, 0), (other, 9, 0)])
        dump.requests(True, [(header, 0, 0), (header + 1, 9, 1), (other, 9, 1)])
        report = self.inspect(dump)
        self.assertEqual(report['configured'], dict(request_count=2,
                         map_header_request_count=1, conditional_request_count=1))
        self.assertEqual(report['retained'], dict(request_count=3,
                         map_header_request_count=2, conditional_request_count=2,
                         submitted_request_count=2, submitted_map_header_request_count=1))
        dump.requests(False, [])
        self.assertEqual(self.inspect(dump)['retained'], report['retained'])

    def test_malformed_identity_counts_arrays_and_flags(self):
        for offset, value, size in ((0, 1, 8), (8, 0, 8),
                                  (0x2680, 0xffffffff, 4), (0x60, preload.MAX_REQUESTS + 1, 4)):
            dump = SavedMemory(); dump.integer(dump.service + offset, value, size)
            with self.assertRaises(ValueError): self.inspect(dump)
        for retained, pointer in ((False, 0x2678), (True, 0x58)):
            for value in (0, 1, 0x90000000):
                dump = SavedMemory(); dump.requests(retained, [(42, 0, 0)])
                dump.integer(dump.service + pointer, value)
                with self.assertRaises(ValueError): self.inspect(dump)
        dump = SavedMemory(); dump.requests(True, [(42, 0, 2)])
        with self.assertRaises(ValueError): self.inspect(dump)
        dump = SavedMemory(); dump.integer(dump.table + preload.PRELOADER_SLOT * 8, 1)
        with self.assertRaises(ValueError): self.inspect(dump)
        with self.assertRaises(ValueError): preload.preload_state(SavedMemory())

    def test_identifiers_and_native_addresses_are_omitted(self):
        dump = SavedMemory()
        guid, key = preload.MAP_HEADER_TYPE | 123, 0x123456789abc
        dump.requests(True, [(guid, key, 1)])
        report = json.dumps(self.inspect(dump))
        for value in (guid, key, dump.root, dump.service, 0x50000000):
            self.assertNotIn(str(value), report)
            self.assertNotIn(hex(value), report)


if __name__ == '__main__': unittest.main()
