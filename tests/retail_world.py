"""Synthetic final-world profile rejection and pointer/owner bounds."""
import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('world', Path(__file__).resolve().parents[1] / 'scripts/Inspect-RetailWorld.py')
world = importlib.util.module_from_spec(spec); spec.loader.exec_module(world)
BASE = 0x140000000
OBJECT = 0x20000000
OWNER = 0x21000000


class Memory:
    def __init__(self, data): self.data = data
    def memory(self, address, size):
        blob = self.data.get(address, b'')
        if len(blob) < size: raise ValueError('Synthetic memory bounds')
        return blob[:size]


class WorldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image = bytearray(world.IMAGE_BYTES)
        for rva, data in world.GUARDS.items(): cls.image[rva:rva + len(data)] = data
        for slot, function in [(0, 0xb4a860), (5, 0xb4a7d0), (6, 0xb4b5c0), (14, 0xb4b5f0)]:
            struct.pack_into('<Q', cls.image, world.WORLD_VTABLE + slot * 8, BASE + function)
        struct.pack_into('<8I', cls.image, 0xb4d8e4, 0xb4ccca, 0xb4ccd4, 0xb4cce7, 0xb4ccf1,
                         0xb4ccfb, 0xb4cd05, 0xb4cd20, 0xb4cd0f)

    def fixture(self):
        data = bytearray(0x48)
        struct.pack_into('<3Q', data, 0, BASE + world.WORLD_VTABLE,
                         OWNER ^ world.OWNER_XOR_CONSTANT, BASE + world.SECONDARY_VTABLE)
        data[0x18] = 2
        return Memory({OBJECT: data, OWNER: struct.pack('<Q', BASE + world.OWNER_VTABLE)})

    def test_valid_profile_and_idle(self):
        world.verify_image(self.image, BASE)
        report = world.world_state(self.fixture(), OBJECT, self.image, BASE)
        self.assertTrue(report['idle_without_request'])
        self.assertEqual(report['owner'], f'{OWNER:x}')

    def test_instruction_and_table_rejection(self):
        for at in [0xb4b5cd, world.WORLD_VTABLE + 6 * 8, 0xb4d8e4]:
            saved = self.image[at]; self.image[at] ^= 1
            try:
                with self.assertRaises(ValueError): world.verify_image(self.image, BASE)
            finally: self.image[at] = saved
        with self.assertRaises(ValueError): world.verify_image(b'', BASE)

    def test_object_owner_and_request_rejection(self):
        for offset, value in [(0, 0), (8, 0), (0x10, 0), (0x20, 0x0800000000000165)]:
            memory = self.fixture(); struct.pack_into('<Q', memory.data[OBJECT], offset, value)
            with self.assertRaises(ValueError): world.world_state(memory, OBJECT, self.image, BASE)
        memory = self.fixture(); memory.data[OBJECT][0x18] = 10
        with self.assertRaises(ValueError): world.world_state(memory, OBJECT, self.image, BASE)
        memory = self.fixture(); memory.data[OWNER] = bytes(8)
        with self.assertRaises(ValueError): world.world_state(memory, OBJECT, self.image, BASE)
        memory = self.fixture(); memory.data[OBJECT] = memory.data[OBJECT][:16]
        with self.assertRaises(ValueError): world.world_state(memory, OBJECT, self.image, BASE)

    def test_descriptor_is_pointer(self):
        memory = self.fixture(); descriptor = 0x22000000
        struct.pack_into('<Q', memory.data[OBJECT], 0x20, descriptor)
        memory.data[descriptor] = struct.pack('<I', 0x688)
        report = world.world_state(memory, OBJECT, self.image, BASE)
        self.assertFalse(report['idle_without_request'])
        self.assertEqual(report['request_descriptor_first_u32'], 0x688)

    def test_unrelated_executable_rejected_before_dump(self):
        with tempfile.TemporaryDirectory(prefix='ow1-world-test-') as folder:
            executable = Path(folder) / 'synthetic.exe'; executable.write_bytes(bytes(64))
            with self.assertRaises(ValueError): world.inspect(executable, Path(folder) / 'absent.dmp')

    def test_callback_metadata_distinguishes_unqueried_and_available(self):
        address = 0x24000000; blob = bytearray(176)
        blob[60:64] = b'FRP1'; blob[128:136] = bytes.fromhex('0107020007011b00')
        struct.pack_into('<III', blob, 160, 256, 1000, 128)
        blob[56] = 255
        memory = Memory({address: blob}); captured = {'request_descriptor_pointer': '0'}
        self.assertIsNone(world.callback_metadata(memory, address, captured)['native_practice_header_available'])
        self.assertIsNone(world.callback_metadata(memory, address, captured)['native_practice_header_load_state_raw'])
        self.assertFalse(world.callback_metadata(memory, address, captured)['native_header_resource_request_attempted'])
        struct.pack_into('<II', blob, 0, 2, 3); blob[8] = 1
        struct.pack_into('<QI', blob, 16, 0x25000000, 0x688); blob[56] = 1
        captured['request_descriptor_pointer'] = '25000000'
        result = world.callback_metadata(memory, address, captured)
        self.assertTrue(result['native_request_submitted']); self.assertTrue(result['request_matches_world'])
        self.assertTrue(result['native_practice_header_available'])
        blob[58] = 1
        for raw in (0, 1, 2, 3, 255):
            blob[57] = raw
            self.assertEqual(world.callback_metadata(memory, address, captured)['native_practice_header_load_state_raw'], raw)
        blob[72] = 1; struct.pack_into('<Q', blob, 64, 0x26000000)
        result = world.callback_metadata(memory, address, captured)
        self.assertTrue(result['native_header_resource_request_attempted'])
        self.assertEqual(result['native_header_resource_request_entry'], '26000000')
        for offset, value in [(60, 0), (128, 0), (161, 0), (56, 2), (58, 2), (72, 2), (96, 2)]:
            saved = blob[offset]; blob[offset] = value
            try:
                with self.assertRaises(ValueError): world.callback_metadata(memory, address, captured)
            finally: blob[offset] = saved


if __name__ == '__main__': unittest.main()
