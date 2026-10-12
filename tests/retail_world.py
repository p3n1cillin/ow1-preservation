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
        struct.pack_into('<Q', cls.image, 0x26188c8 + 8, BASE + 0x81dc30)
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
        for at in [0xb4b5cd, world.WORLD_VTABLE + 6 * 8, 0xb4d8e4, 0x26188c8 + 8]:
            saved = self.image[at]; self.image[at] ^= 1
            try:
                with self.assertRaises(ValueError): world.verify_image(self.image, BASE)
            finally: self.image[at] = saved
        with self.assertRaises(ValueError): world.verify_image(b'', BASE)

    def test_object_owner_and_request_rejection(self):
        for offset, value in [(0, 0), (8, 0), (0x10, 0), (0x20, 0x0800000000000165)]:
            memory = self.fixture(); struct.pack_into('<Q', memory.data[OBJECT], offset, value)
            with self.assertRaises(ValueError): world.world_state(memory, OBJECT, self.image, BASE)
        memory = self.fixture(); memory.data[OBJECT][0x18] = 11
        with self.assertRaises(ValueError): world.world_state(memory, OBJECT, self.image, BASE)
        memory = self.fixture(); memory.data[OWNER] = bytes(8)
        with self.assertRaises(ValueError): world.world_state(memory, OBJECT, self.image, BASE)
        memory = self.fixture(); memory.data[OBJECT] = memory.data[OBJECT][:16]
        with self.assertRaises(ValueError): world.world_state(memory, OBJECT, self.image, BASE)

    def test_descriptor_is_pointer(self):
        memory = self.fixture(); descriptor = 0x22000000
        struct.pack_into('<Q', memory.data[OBJECT], 0x20, descriptor)
        memory.data[descriptor] = bytearray(0x150)
        struct.pack_into('<I', memory.data[descriptor], 0, 0x688)
        report = world.world_state(memory, OBJECT, self.image, BASE)
        self.assertFalse(report['idle_without_request'])
        self.assertEqual(report['request_descriptor_first_u32'], 0x688)
        self.assertFalse(report['request_loading_context_nonzero'])
        memory.data[descriptor][0x18] = 1
        report = world.world_state(memory, OBJECT, self.image, BASE)
        self.assertTrue(report['request_loading_context_nonzero'])
        memory.data[OBJECT][0x18] = 10
        self.assertEqual(world.world_state(memory, OBJECT, self.image, BASE)['state'], 10)
        memory.data[descriptor] = memory.data[descriptor][:4]
        with self.assertRaises(ValueError): world.world_state(memory, OBJECT, self.image, BASE)

    def test_unrelated_executable_rejected_before_dump(self):
        with tempfile.TemporaryDirectory(prefix='ow1-world-test-') as folder:
            executable = Path(folder) / 'synthetic.exe'; executable.write_bytes(bytes(64))
            with self.assertRaises(ValueError): world.inspect(executable, Path(folder) / 'absent.dmp')

    def test_callback_metadata_distinguishes_unqueried_and_available(self):
        address = 0x24000000; blob = bytearray(256)
        blob[60:64] = b'FRP1'; blob[128:136] = bytes.fromhex('0107020007011b00')
        struct.pack_into('<III', blob, 160, 256, 1000, 128)
        blob[56] = 255
        memory = Memory({address: blob}); captured = {'request_descriptor_pointer': '0'}
        self.assertIsNone(world.callback_metadata(memory, address, captured)['native_practice_header_available'])
        self.assertIsNone(world.callback_metadata(memory, address, captured)['native_practice_header_load_state_raw'])
        self.assertFalse(world.callback_metadata(memory, address, captured)['native_header_resource_request_attempted'])
        self.assertIsNone(world.callback_metadata(memory, address, captured)['native_update_observation'])
        self.assertIsNone(world.callback_metadata(memory, address, captured)['native_loading_context'])
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
        blob[74:79] = bytes((3, 4, 4, 1, 1))
        struct.pack_into('<3I', blob, 80, 1, 4, 0)
        observation = world.callback_metadata(memory, address, captured)['native_update_observation']
        self.assertEqual(observation['highest_returned_state'], 4)
        self.assertEqual(observation['calls_entered_from_loading_states'], {'2': 1, '3': 4, '4': 0})
        captured['request_descriptor_pointer'] = '0'
        rejected = world.callback_metadata(memory, address, captured)
        self.assertTrue(rejected['native_request_submitted'])
        self.assertFalse(rejected['request_matches_world'])
        captured['request_descriptor_pointer'] = '25000000'
        for offset, value in [(60, 0), (128, 0), (161, 0), (56, 2), (58, 2), (72, 2), (96, 2)]:
            saved = blob[offset]; blob[offset] = value
            try:
                with self.assertRaises(ValueError): world.callback_metadata(memory, address, captured)
            finally: blob[offset] = saved
        for offset, value in [(74, 11), (75, 11), (76, 11), (77, 2), (78, 3), (83, 1)]:
            saved = blob[offset]; blob[offset] = value
            try:
                with self.assertRaises(ValueError): world.callback_metadata(memory, address, captured)
            finally: blob[offset] = saved

    def test_native_loading_context_verifies_identity_and_reads_readiness(self):
        address = 0x24000000; context_pointer = 0x28000000; blob = bytearray(256)
        blob[60:64] = b'FRP1'; blob[128:136] = bytes.fromhex('0107020007011b00')
        struct.pack_into('<III', blob, 160, 256, 1500, 128)
        blob[56] = 255; blob[192:196] = bytes((1, 1, 1, 1))
        struct.pack_into('<Q', blob, 176, context_pointer)
        context = bytearray(0xa0)
        struct.pack_into('<QI', context, 0, BASE + 0x2611290, 2)
        struct.pack_into('<I', context, 0x10, 2)
        memory = Memory({address: blob, context_pointer: context}); captured = {'request_descriptor_pointer': '0'}
        result = world.callback_metadata(memory, address, captured, BASE)['native_loading_context']
        self.assertTrue(result['identity_verified']); self.assertTrue(result['activation_result'])
        self.assertFalse(result['native_reports_ready'])
        context[0x98] = 1
        self.assertTrue(world.callback_metadata(memory, address, captured, BASE)['native_loading_context']['native_reports_ready'])
        with self.assertRaises(ValueError): world.callback_metadata(memory, address, captured)
        for offset, value in [(0, 0), (8, 0), (0x10, 3)]:
            saved = context[offset]; context[offset] = value
            try:
                with self.assertRaises(ValueError): world.callback_metadata(memory, address, captured, BASE)
            finally: context[offset] = saved
        for offset, value in [(192, 2), (193, 2), (194, 2), (195, 0)]:
            saved = blob[offset]; blob[offset] = value
            try:
                with self.assertRaises(ValueError): world.callback_metadata(memory, address, captured, BASE)
            finally: blob[offset] = saved
        struct.pack_into('<Q', blob, 176, 0); blob[193:196] = bytes(3)
        result = world.callback_metadata(memory, address, captured)['native_loading_context']
        self.assertFalse(result['identity_verified']); self.assertIsNone(result['activation_result'])
        self.assertIsNone(result['native_reports_ready'])

    def test_native_context_service_requires_unique_owner_and_bounds(self):
        root, array, manager, context = 0x29000000, 0x2a000000, 0x2b000000, 0x2c000000
        image = self.image.copy(); struct.pack_into('<Q', image, 0x2f586e0, root)
        struct.pack_into('<Q', image, 0x2ee4bd0, 0)
        slots = bytearray(256 * 8); struct.pack_into('<Q', slots, 126 * 8, manager)
        blob = bytearray(0x1a8)
        struct.pack_into('<2Q', blob, 0, BASE + 0x2611278, root ^ 0xf3b530a5300e4c1a)
        struct.pack_into('<Q', blob, 0x1a0, context); struct.pack_into('<I', blob, 0xe8, 2)
        memory = Memory({root + 0x140: struct.pack('<Q', array ^ 0x4e3494c633194824), array: slots, manager: blob})
        report = world.loading_context_service(memory, image, BASE, context)
        self.assertTrue(report['current_context_matches']); self.assertEqual(report['cached_metadata_entries'], 0)
        self.assertEqual(report['registered_context_change_subscribers'], 2)
        for offset, format, value in [(0, '<Q', 0), (8, '<Q', 0), (0x1a0, '<Q', 0), (0x158, '<Q', 4097), (0xe8, '<I', 4097)]:
            saved = blob[:]; struct.pack_into(format, blob, offset, value)
            try:
                with self.assertRaises(ValueError): world.loading_context_service(memory, image, BASE, context)
            finally: blob[:] = saved
        other = 0x2d000000; memory.data[other] = blob[:]; struct.pack_into('<Q', slots, 127 * 8, other)
        with self.assertRaises(ValueError): world.loading_context_service(memory, image, BASE, context)

    def test_retained_sdk_request_separates_submission_completion_and_data(self):
        address, control_pointer = 0x24000000, 0x2e000000
        action_pointer = control_pointer + 16; blob = bytearray(256)
        blob[60:64] = b'FRP1'; blob[128:136] = bytes.fromhex('0107020007011b00')
        struct.pack_into('<III', blob, 160, 256, 1800, 128)
        blob[56] = 255; blob[200:203] = bytes((1, 1, 1))
        struct.pack_into('<2Q', blob, 240, control_pointer, action_pointer)
        control = bytearray(struct.pack('<QII', BASE + 0x2656740, 1, 1))
        action = bytearray(0x148); struct.pack_into('<Q', action, 0, BASE + 0x26188c8); action[0x10] = 13
        memory = Memory({address: blob, control_pointer: control, action_pointer: action})
        captured = {'request_descriptor_pointer': '0'}
        result = world.callback_metadata(memory, address, captured, BASE)['retained_sdk_metadata_request']
        self.assertTrue(result['submission_accepted']); self.assertFalse(result['completed'])
        self.assertIsNone(result['response_data_present']); self.assertIsNone(result['error_code_raw'])
        action[0x130] = 1
        action[0x18:0x1a] = bytes((3, 2)); struct.pack_into('<q', action, 0x20, -1)
        result = world.callback_metadata(memory, address, captured, BASE)['retained_sdk_metadata_request']
        self.assertTrue(result['completed']); self.assertFalse(result['result_succeeded'])
        self.assertIsNone(result['response_data_present']); self.assertIsNone(result['response_entry_count'])
        self.assertEqual((result['error_status_raw'], result['error_tag_raw'], result['error_code_raw']), (3, 2, -1))
        action[0x11] = 1; struct.pack_into('<I', action, 0x140, 51)
        result = world.callback_metadata(memory, address, captured, BASE)['retained_sdk_metadata_request']
        self.assertTrue(result['result_succeeded']); self.assertFalse(result['response_data_present'])
        self.assertEqual(result['response_entry_count'], 51); self.assertIsNone(result['error_code_raw'])
        struct.pack_into('<Q', action, 0x138, 0x30000000)
        result = world.callback_metadata(memory, address, captured, BASE)['retained_sdk_metadata_request']
        self.assertTrue(result['response_data_present']); self.assertIsNone(result['error_tag_raw'])
        action[0x130] = 0
        result = world.callback_metadata(memory, address, captured, BASE)['retained_sdk_metadata_request']
        self.assertIsNone(result['result_succeeded']); self.assertIsNone(result['response_entry_count'])
        for buffer, offset, value in [(control, 0, 0), (control, 8, 0), (action, 0, 0), (action, 0x10, 12),
                                     (action, 0x11, 2), (action, 0x130, 2), (action, 0x131, 2), (blob, 200, 0), (blob, 201, 2)]:
            saved = buffer[offset]; buffer[offset] = value
            try:
                with self.assertRaises(ValueError): world.callback_metadata(memory, address, captured, BASE)
            finally: buffer[offset] = saved


if __name__ == '__main__': unittest.main()
