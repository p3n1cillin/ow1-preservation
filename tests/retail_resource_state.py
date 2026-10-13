"""Synthetic resource-cache fixtures; no client memory or payloads embedded."""
import json
from pathlib import Path
import struct
import sys
import unittest
from unittest import mock
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import retail_resource_state as resource
import retail_login_state as login


class SavedMemory:
    image_base = 0x10000000
    def __init__(self):
        self.memory = {}
        # Synthetic CRC-64/ECMA reflected table, generated from a public
        # polynomial, rather than copied from any client/dump.
        table = []
        for byte in range(256):
            value = byte
            for _ in range(8):
                value = (value >> 1) ^ (0xc96c5795d7870f42 if value & 1 else 0)
            table.append(value)
        self.put(self.image_base + resource.HASH_TABLE_RVA, struct.pack('<256Q', *table))
        self.catalogue, self.buckets = 0x40000000, 0x40001000
        self.cache_buckets = 0x40002000
        self.integer(self.image_base + resource.CATALOGUE_ROOT_RVA, self.catalogue)
        self.integer(self.catalogue + 0x70, 1, 4)
        self.integer(self.catalogue + 0x74, 1, 4)
        self.integer(self.catalogue + 0x78, self.buckets)
        self.integer(self.buckets, 0)
        self.integer(self.image_base + resource.CACHE_BUCKETS_RVA, 1, 4)
        self.integer(self.image_base + resource.CACHE_COUNT_RVA, 0, 4)
        self.integer(self.image_base + resource.CACHE_TABLE_RVA, self.cache_buckets)
        self.integer(self.cache_buckets, 0)
        self.manager = 0x50000000
        self.put(self.manager, bytes(0x48))
        self.integer(self.manager, self.image_base + login.WORLD_VFT)
        self.integer(self.manager + 0x18, 2, 1)
        self.integer(self.manager + 0x20, 0x50001000)
        self.integer(self.manager + 0x41, 1, 1)
        self.integer(0x50001000, 0x688)
        self.integer(0x50001008, 0)
    def put(self, address, value):
        self.memory.update({address+i:byte for i,byte in enumerate(value)})
    def integer(self, address, value, size=8):
        self.put(address, value.to_bytes(size, 'little'))
    def read(self, address, size):
        if any(address+i not in self.memory for i in range(size)):return b''
        return bytes(self.memory[address+i] for i in range(size))
    def find_all(self, needle):
        return [self.manager] if self.read(self.manager, 8) == needle else []
    def catalogue_node(self, address, guid, next_node=0):
        self.integer(address, next_node)
        self.integer(address+8, 0x60000000)
        self.integer(address+0x18, guid)
    def cache_node(self, address, key, obj, next_node=0):
        self.integer(address, next_node)
        self.integer(address+8, obj)
        self.integer(address+0x10, key)


class ResourceTests(unittest.TestCase):
    def test_catalogue_presence_is_not_a_load(self):
        dump=SavedMemory();reader=resource.ResourceReader(dump)
        guid=resource.MAP_HEADER_TYPE | 0x688
        dump.catalogue_node(0x60001000, guid)
        dump.integer(dump.buckets, 0x60001000)
        self.assertEqual(reader.resource(guid),dict(catalogue_present=True, cache_entry_present=False, raw_load_state=0))
        dump.integer(dump.image_base+resource.CACHE_COUNT_RVA, 1, 4)
        dump.cache_node(0x60002000, reader.hash_guid(guid), 0x60003000)
        dump.integer(dump.cache_buckets, 0x60002000)
        for status in (0, 1, 2, 3):
            dump.integer(0x600030ac, status, 1)
            self.assertEqual(reader.resource(guid),dict(catalogue_present=True, cache_entry_present=True, raw_load_state=status))

    def test_collision_lookup_and_missing_keys(self):
        dump=SavedMemory();reader=resource.ResourceReader(dump)
        guid=resource.MAP_HEADER_TYPE | 0x688
        dump.catalogue_node(0x60001000, guid+1, 0x60001100)
        dump.catalogue_node(0x60001100, guid)
        dump.integer(dump.buckets, 0x60001000)
        self.assertTrue(reader.catalogue_present(guid))
        self.assertFalse(reader.catalogue_present(guid+2))
        dump.cache_node(0x60002000, reader.hash_guid(guid+1), 0, 0x60002100)
        dump.cache_node(0x60002100, reader.hash_guid(guid), 0x60003000)
        dump.integer(dump.cache_buckets, 0x60002000)
        dump.integer(dump.image_base+resource.CACHE_COUNT_RVA, 2, 4)
        dump.integer(0x600030ac, 3, 1)
        self.assertEqual(reader.load_state(guid),dict(cache_entry_present=True, raw_load_state=3))
        self.assertEqual(reader.load_state(guid+2),dict(cache_entry_present=False, raw_load_state=0))

    def test_corrupt_memory_fails_closed(self):
        for address,value,size in ((resource.CACHE_COUNT_RVA,resource.MAX_ENTRIES+1,4),
                                   (resource.CACHE_BUCKETS_RVA,3,4),(resource.HASH_TABLE_RVA,1,8)):
            dump=SavedMemory();dump.integer(dump.image_base+address,value,size)
            with self.assertRaises(ValueError):resource.ResourceReader(dump)
        dump=SavedMemory();reader=resource.ResourceReader(dump)
        dump.integer(dump.buckets,0x60001000)
        dump.catalogue_node(0x60001000,12,0x60001000)
        with self.assertRaises(ValueError):reader.catalogue_present(13)
        dump.integer(dump.buckets,0x60001001)
        with self.assertRaises(ValueError):reader.catalogue_present(13)
        dump.integer(dump.buckets,0x70000000)
        with self.assertRaises(ValueError):reader.catalogue_present(13)
        dump.integer(dump.buckets,0)
        dump.integer(dump.image_base+resource.CACHE_COUNT_RVA,1,4)
        dump.integer(dump.image_base+resource.CACHE_TABLE_RVA,0)
        with self.assertRaises(ValueError):reader.load_state(13)

    def test_world_report_omits_identifiers_and_checks_profile(self):
        dump=SavedMemory()
        with mock.patch.object(login,'inspect',return_value={}) as validate:
            report=resource.world_resource_states(dump)
            validate.assert_called_once_with(dump)
        self.assertEqual(report['managers'][0]['map_header'],dict(catalogue_present=False,cache_entry_present=False,raw_load_state=0))
        text=json.dumps(report)
        for forbidden in ('guid','pointer','hash_table','0x688',str(dump.manager)):
            self.assertNotIn(forbidden,text)
        with self.assertRaises(ValueError):resource.world_resource_states(dump) # incomplete PE/profile
        with mock.patch.object(login,'inspect',return_value={}):
            for flag in (2,255):
                dump.integer(dump.manager+0x41,flag,1)
                with self.assertRaises(ValueError):resource.world_resource_states(dump)
            dump.integer(dump.manager+0x18,11,1)
            with self.assertRaises(ValueError):resource.world_resource_states(dump)
        with self.assertRaises(ValueError):resource.world_resource_states(dump,limit=9)


if __name__ == '__main__':unittest.main()
