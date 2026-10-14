"""Synthetic metadata objects and written messages; no captured client bytes."""
import json
from pathlib import Path
import struct
import sys
import unittest
from unittest import mock
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import retail_login_state as login
import retail_metadata_state as metadata
from gateway_codec import decode, encode, load_messages


class SavedMemory:
    image_base = 0x10000000

    def __init__(self, count=1):
        self.memory = {}
        self.root, self.table, self.service = 0x40000000, 0x40001000, 0x40002000
        self.array, self.entry = 0x40003000, 0x40004000
        self.integer(self.image_base + login.ROOT_RVA, self.root)
        self.integer(self.image_base + login.COOKIE_RVA, 0)
        self.integer(self.root + 0x140, login.TABLE_MASK ^ self.table)
        self.put(self.table, bytes(2048))
        self.integer(self.table + 42 * 8, self.service)
        self.put(self.service, bytes(0x1a8))
        self.integer(self.service, self.image_base + metadata.METADATA_VFT)
        self.integer(self.service + 8, self.root ^ metadata.OWNER_MASK)
        self.integer(self.service + 0x150, self.array)
        self.integer(self.service + 0x158, count)
        self.integer(self.service + 0x169, 1, 1)
        self.put(self.image_base + metadata.DEFAULT_IDENTIFIER_RVA, bytes(32))
        for i in range(count):
            entry = self.entry + 0x100 * i
            self.integer(self.array + i * 8, entry)
            self.put(entry, bytes(0x90))
            self.integer(entry + 0x24, 1, 4)
            self.integer(entry + 0x78, 0xa0, 4)
            self.integer(entry + 0x88, 10, 4)

    def put(self, address, data):
        self.memory.update({address + i: byte for i, byte in enumerate(data)})

    def integer(self, address, value, size=8):
        self.put(address, value.to_bytes(size, 'little'))

    def read(self, address, size):
        if any(address + i not in self.memory for i in range(size)):
            return b''
        return bytes(self.memory[address + i] for i in range(size))


class MetadataTests(unittest.TestCase):
    def inspect(self, dump, limit=8):
        with mock.patch.object(login, 'inspect', return_value={}):
            return metadata.metadata_state(dump, limit)

    def test_registration_processing_and_context_are_separate(self):
        dump = SavedMemory()
        report = self.inspect(dump)
        self.assertEqual(report['cached_metadata_entries'], 1)
        self.assertFalse(report['current_context_present'])
        self.assertFalse(report['pending_initialization_action'])
        self.assertEqual(report['entries'], [dict(identifier_is_default=True, format_field=1,
                          processing_flags=0xa0, content_present=False,
                          acquisition_in_flight=False, acquisition_failed=True,
                          retry_deadline_set=False, completed_acquisition_attempts=10)])
        dump.integer(dump.entry + 0x78, 0x20, 4)
        dump.integer(dump.entry + 0x80, 0x50000000)
        dump.integer(dump.entry + 0x88, 7, 4)
        dump.integer(dump.service + 0x1a0, 0x50001000)
        report = self.inspect(dump)
        self.assertTrue(report['current_context_present'])
        self.assertTrue(report['entries'][0]['retry_deadline_set'])
        self.assertFalse(report['entries'][0]['acquisition_failed'])
        self.assertEqual(report['entries'][0]['completed_acquisition_attempts'], 7)
        dump.integer(dump.entry + 0x78, 0x60, 4)
        self.assertTrue(self.inspect(dump)['entries'][0]['acquisition_in_flight'])
        dump.integer(dump.entry + 0x78, 0x21, 4)
        self.assertTrue(self.inspect(dump)['entries'][0]['content_present'])

    def test_empty_and_bounded_sample(self):
        self.assertEqual(self.inspect(SavedMemory(0))['entries'], [])
        report = self.inspect(SavedMemory(9))
        self.assertEqual(report['sampled_entries'], 8)
        self.assertTrue(report['entries_truncated'])
        self.assertEqual(self.inspect(SavedMemory(3), 2)['sampled_entries'], 2)

    def test_malformed_metadata_fails_closed(self):
        for offset, value, size in ((8, 0, 8), (0x158, metadata.MAX_ENTRIES + 1, 8),
                                    (0x150, 1, 8), (0x169, 2, 1)):
            dump = SavedMemory(); dump.integer(dump.service + offset, value, size)
            with self.assertRaises(ValueError): self.inspect(dump)
        for value in (0, 1, 0x80000000):
            dump = SavedMemory(); dump.integer(dump.array, value)
            with self.assertRaises(ValueError): self.inspect(dump)
        dump = SavedMemory(2); dump.integer(dump.array + 8, dump.entry)
        with self.assertRaises(ValueError): self.inspect(dump)
        dump = SavedMemory(); dump.integer(dump.table + 43 * 8, dump.service)
        with self.assertRaises(ValueError): self.inspect(dump)
        dump = SavedMemory(); dump.integer(dump.table + 42 * 8, 0)
        with self.assertRaises(ValueError): self.inspect(dump)
        for limit in (0, 9, True):
            with self.assertRaises(ValueError): metadata.metadata_state(SavedMemory(), limit)
        with self.assertRaises(ValueError): metadata.metadata_state(SavedMemory())

    def test_identifiers_addresses_and_payloads_do_not_escape(self):
        dump = SavedMemory(); dump.put(dump.entry, b'private fixture identifier'.ljust(32, b'!'))
        report = self.inspect(dump)
        self.assertFalse(report['entries'][0]['identifier_is_default'])
        text = json.dumps(report)
        for forbidden in ('private fixture', str(dump.entry), 'digest', 'pointer', 'payload'):
            self.assertNotIn(forbidden, text)
        # Unrelated/unreadable context slots do not masquerade as metadata.
        dump.integer(dump.table + 8, 1)
        self.assertEqual(self.inspect(dump), report)

    def test_written_20318_schema_and_bounds(self):
        messages = load_messages(Path(__file__).resolve().parents[1] / 'protocol/instance-metadata-104319.json')
        fields = messages[0xc77f6403, 20318]
        values = {0x78: list(range(32)), 0x98: {0: 1, 4: 42, 8: -7,
                  12: [11] * 32, 44: [22] * 32}}
        written = bytes(range(32)) + struct.pack('<IIi', 1, 42, -7) + bytes([11] * 32 + [22] * 32)
        self.assertEqual(len(written), 108)
        self.assertEqual(encode(fields, values), written)
        self.assertEqual(decode(fields, written), values)
        for end in range(len(written)):
            with self.assertRaises(ValueError): decode(fields, written[:end])
        with self.assertRaises(ValueError): decode(fields, written + b'\0')
        with self.assertRaises(ValueError): encode(fields, {0x78: [0] * 31})


if __name__ == '__main__': unittest.main()
