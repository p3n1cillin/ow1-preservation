"""Synthetic selected-entity gates; no native captures or game assets."""
import json
import struct
import sys
from pathlib import Path
import unittest
from unittest import mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import retail_replication_state as replication
import retail_login_state as login


class Memory:
    image_base = 0x10000000
    world, owner, table, array = 0x50000000, 0x60000000, 0x70000000, 0x71000000
    def __init__(self):self.memory={}
    def put(self,address,data):self.memory.update({address+i:byte for i,byte in enumerate(data)})
    def integer(self,address,value,size=8):self.put(address,value.to_bytes(size,'little'))
    def read(self,address,size):
        if any(address+i not in self.memory for i in range(size)):return b''
        return bytes(self.memory[address+i] for i in range(size))
    def find_all(self,needle):return [self.world] if self.read(self.world,8)==needle else []


class ReplicationTests(unittest.TestCase):
    def fixture(self,selected=1,entries=()):
        d=Memory();b=d.image_base
        for rva,data in replication.PROFILES:d.put(b+rva,data)
        d.integer(b+0x7d224c,0x7d2079,4)
        d.integer(b+0x3241288,0xffffffff,4)
        d.integer(b+0x2ee48a1,0)
        d.integer(b+login.COOKIE_RVA,123)
        # Nonzero cookie tests the native rotate/add/XOR decode.
        cookie=0x123456789abcdef0;d.integer(b+0x2ee53a8,cookie)
        rotated=((cookie>>4)|(cookie<<60)) & replication.MASK
        key=(0x042b51ef9b84a901+2*rotated)&replication.MASK
        d.integer(d.world,b+login.WORLD_VFT)
        d.integer(d.world+8,d.owner^0x4dfd564467c27b96)
        d.integer(d.world+0x10,b+replication.SECONDARY_VFT)
        d.integer(d.world+0x18,8,1);d.integer(d.owner,b+replication.OWNER_VFT)
        d.integer(d.owner+0x298,selected,4);d.integer(d.owner+0x18,d.table^key)
        d.integer(d.owner+0x140,0x74000000^((login.TABLE_MASK-123)&replication.MASK))
        d.integer(0x74000000+79*8,0x75000000)
        d.integer(0x75000000,b+replication.REPLICATION_SLOT_VFT)
        d.integer(0x75000018,0)
        bucket=d.table+(selected&0xfff)*16
        d.integer(bucket,d.array if entries else 0);d.integer(bucket+8,len(entries),4)
        for i,(entity,obj) in enumerate(entries):
            d.put(d.array+i*16,struct.pack('<IIQ',entity,0,obj))
            if obj:
                d.integer(obj+0xb0,entity,4);d.integer(obj+0x88,0)
        return d

    def report(self,d):
        with mock.patch.object(replication,'inspect'):
            return replication.replication_gates(d)['managers'][0]

    def test_unset_id_is_distinct_from_an_empty_bucket(self):
        for selected in (0xffffffff,0x1fffffff,0x7fffffff):
            row=self.report(self.fixture(selected))
            self.assertFalse(row['selected_entity_valid'])
            self.assertNotIn('selected_bucket_count',row)
        row=self.report(self.fixture())
        self.assertTrue(row['selected_entity_valid'])
        self.assertFalse(row['selected_entity_record_present'])
        self.assertFalse(row['generation_mismatch'])

    def test_generation_and_object_resolution(self):
        row=self.report(self.fixture(1,[(0xc0000001,0x72000000)]))
        self.assertTrue(row['generation_mismatch'])
        self.assertTrue(row['same_index_record_present'])
        self.assertFalse(row['selected_entity_record_present'])
        row=self.report(self.fixture(0xc0000001,[(0xc0000001,0x72000000)]))
        self.assertTrue(row['selected_entity_object_present'])
        self.assertTrue(row['selected_entity_native_id_matches'])
        self.assertFalse(row['first_person_owner_component_present'])
        self.assertFalse(row['generation_mismatch'])
        self.assertEqual(row['state'],'WORLD REPLICATING')
        self.assertNotIn('0x',json.dumps(row));self.assertNotIn(str(0xc0000001),json.dumps(row))
        row=self.report(self.fixture(1,[(1,0),(0x1001,0x72000000)]))
        self.assertTrue(row['selected_entity_record_present'])
        self.assertFalse(row['selected_entity_object_present'])

    def test_rejects_profile_identity_counts_and_truncated_records(self):
        mutations=[lambda d:d.integer(d.image_base+0x7d224c,0,4),
                   lambda d:d.integer(d.image_base+0x5881c4,0,1),
                   lambda d:d.integer(d.owner,0),
                   lambda d:d.integer(0x75000000,0),
                   lambda d:d.integer(d.world+0x18,11,1),
                   lambda d:d.integer(d.table+16+8,4097,4),
                   lambda d:d.integer(d.table+16,3),
                   lambda d:d.integer(d.array+8,3),
                   lambda d:d.memory.pop(d.array+15)]
        for mutate in mutations:
            d=self.fixture(1,[(1,0x72000000)]);mutate(d)
            with self.assertRaises(ValueError):self.report(d)
        with self.assertRaises(ValueError):self.report(self.fixture(1,[(1,0),(1,0)]))
        with self.assertRaises(ValueError):replication.replication_gates(self.fixture())
        with self.assertRaises(ValueError):replication.replication_gates(self.fixture(),False)

    def test_first_person_component_is_only_a_prerequisite(self):
        d=self.fixture(1,[(1,0x72000000)])
        d.integer(0x72000088,1 << 44)
        row=self.report(d)
        self.assertTrue(row['first_person_owner_component_present'])
        self.assertEqual(row['state'],'WORLD REPLICATING')
        self.assertNotIn('controlled_actor_present',row)
        for address,size in ((0x720000b0,4),(0x72000088,8)):
            damaged=self.fixture(1,[(1,0x72000000)])
            damaged.memory.pop(address+size-1)
            with self.assertRaisesRegex(ValueError,'incomplete'):self.report(damaged)
        d.integer(0x720000b0,2,4)
        with self.assertRaisesRegex(ValueError,'identity differs'):self.report(d)
        d=self.fixture(1,[(1,0x72000000)])
        d.integer(d.image_base+0xbd59a0,0,1)
        with self.assertRaisesRegex(ValueError,'profile differs'):self.report(d)
        d=self.fixture(1,[(1,0x72000000)]);original=d.read;reads=0
        def changing(address,size):
            nonlocal reads
            if address==0x72000088:
                reads+=1
                if reads==2:return (1 << 44).to_bytes(8,'little')
            return original(address,size)
        d.read=changing
        with self.assertRaisesRegex(ValueError,'object changed'):self.report(d)

    def test_entity_resolution_does_not_complete_pending_replication(self):
        d=self.fixture(1,[(1,0x72000000)])
        d.integer(0x75000018,0x76000000)
        d.integer(0x76000018,0,4);d.integer(0x76000128,4,4);d.integer(0x76000148,0,1)
        row=self.report(d)
        self.assertTrue(row['selected_entity_object_present'])
        self.assertTrue(row['replication_context_present'])
        self.assertEqual(row['pending_count'],4)
        self.assertFalse(row['completion_marker'])
        d.integer(0x76000148,1,1)
        self.assertEqual(self.report(d)['state'],'WORLD REPLICATING')
        self.assertTrue(self.report(d)['completion_marker'])
        for address,value,size in ((0x76000148,2,1),(0x76000128,4097,4),(0x76000018,4097,4)):
            d.integer(0x76000148,0,1);d.integer(0x76000128,4,4);d.integer(0x76000018,0,4)
            d.integer(address,value,size)
            with self.assertRaises(ValueError):self.report(d)

    def test_rejects_a_changing_selection(self):
        d=self.fixture(1,[(1,0x72000000)]);original=d.read;reads=0
        def changing(address,size):
            nonlocal reads
            if address==d.owner+0x298:
                reads+=1
                if reads==2:return (2).to_bytes(4,'little')
            return original(address,size)
        d.read=changing
        with self.assertRaisesRegex(ValueError,'state changed'):self.report(d)


if __name__=='__main__':unittest.main()
