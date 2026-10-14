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

    def context(self, offset, pointer=0x50001000, ready=0, default=True):
        self.integer(self.service + offset, pointer)
        self.put(pointer, bytes(0xa0))
        self.integer(pointer, self.image_base + metadata.CONTEXT_VFT)
        self.integer(pointer + 8, 1, 4)
        self.integer(pointer + 0x10, 1, 4)
        if not default:
            self.put(pointer + 0x14, b'private context identifier'.ljust(32, b'!'))
        self.integer(pointer + 0x98, ready, 1)
        return pointer

    def initialization(self, completed=0, succeeded=0):
        control = 0x50002000
        pointer = control + 16
        self.integer(self.service + 0x118, pointer)
        self.integer(self.service + 0x120, control)
        self.put(control, struct.pack('<Qii', self.image_base + metadata.INITIALIZATION_CONTROL_VFT, 1, 1))
        self.put(pointer, bytes(0x148))
        self.integer(pointer, self.image_base + metadata.INITIALIZATION_VFT)
        self.integer(pointer + 0x10, 13, 1)
        self.integer(pointer + 0x130, completed, 1)
        self.integer(pointer + 0x11, succeeded, 1)
        self.put(pointer + 0x18, bytes([3, 2]))
        self.put(pointer + 0x20, struct.pack('<q', -1))
        return pointer, control


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
        dump.context(0x1a0)
        report = self.inspect(dump)
        self.assertTrue(report['current_context_present'])
        self.assertTrue(report['entries'][0]['retry_deadline_set'])
        self.assertFalse(report['entries'][0]['acquisition_failed'])
        self.assertEqual(report['entries'][0]['completed_acquisition_attempts'], 7)
        dump.integer(dump.entry + 0x78, 0x60, 4)
        self.assertTrue(self.inspect(dump)['entries'][0]['acquisition_in_flight'])
        dump.integer(dump.entry + 0x78, 0x21, 4)
        self.assertTrue(self.inspect(dump)['entries'][0]['content_present'])

    def test_active_default_survives_empty_staged_slot(self):
        dump = SavedMemory(0)
        dump.context(0x198)
        report = self.inspect(dump)
        self.assertFalse(report['current_context_present'])
        self.assertEqual(report['staged_context'], dict(present=False))
        self.assertEqual(report['active_context'], dict(present=True, kind=1,
                         identifier_is_default=True, ready=False, record_count=0))
        # The default processing branch completes without setting +0x98.
        # Preserve the observed readiness flag rather than inferring failure.
        dump.context(0x1a0, pointer=0x50003000, ready=1, default=False)
        report = self.inspect(dump)
        self.assertTrue(report['staged_context']['ready'])
        self.assertFalse(report['staged_context']['identifier_is_default'])
        dump.integer(dump.service + 0x1a0, 0)
        self.assertTrue(self.inspect(dump)['active_context']['present'])

    def test_initialization_completion_and_error_lifetime(self):
        dump = SavedMemory(0)
        pointer, _ = dump.initialization(succeeded=255)
        self.assertEqual(self.inspect(dump)['initialization_request'],
                         dict(present=True, completed=False))
        dump.integer(pointer + 0x130, 1, 1)
        with self.assertRaises(ValueError): self.inspect(dump)
        dump.integer(pointer + 0x11, 0, 1)
        self.assertEqual(self.inspect(dump)['initialization_request'],
                         dict(present=True, completed=True, succeeded=False,
                              error=dict(status=3, tag=2, code=-1)))
        dump.integer(pointer + 0x11, 1, 1)
        self.assertEqual(self.inspect(dump)['initialization_request'],
                         dict(present=True, completed=True, succeeded=True))

    def test_context_and_initialization_reject_invalid_memory(self):
        for offset, value, size in ((0, 1, 8), (8, 0, 4),
                                  (8, metadata.MAX_REFERENCES + 1, 4),
                                  (0x98, 2, 1), (0x90, metadata.MAX_ENTRIES + 1, 4),
                                  (0x90, 0xffffffff, 4), (0x90, 1, 4)):
            dump = SavedMemory(0); pointer = dump.context(0x198)
            dump.integer(pointer + offset, value, size)
            with self.assertRaises(ValueError): self.inspect(dump)
        for value in (1, 0x90000000):
            dump = SavedMemory(0); dump.integer(dump.service + 0x198, value)
            with self.assertRaises(ValueError): self.inspect(dump)
        for field, offset, value, size in (('control', 0, 1, 8), ('control', 8, 0, 4),
                                         ('control', 12, 0, 4), ('request', 0, 1, 8),
                                         ('request', 0x10, 14, 1), ('request', 0x130, 2, 1)):
            dump = SavedMemory(0); pointer, control = dump.initialization()
            dump.integer((control if field == 'control' else pointer) + offset, value, size)
            with self.assertRaises(ValueError): self.inspect(dump)
        for offset, value in ((0x118, 0), (0x118, 1), (0x120, 0), (0x120, 1)):
            dump = SavedMemory(0); dump.initialization()
            dump.integer(dump.service + offset, value)
            with self.assertRaises(ValueError): self.inspect(dump)

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
        dump.context(0x198, default=False)
        dump.initialization(completed=1)
        report = self.inspect(dump)
        self.assertFalse(report['entries'][0]['identifier_is_default'])
        text = json.dumps(report)
        for forbidden in ('private fixture', 'private context', str(dump.entry),
                          str(0x50001000), str(0x50002000), 'digest', 'pointer', 'payload'):
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
