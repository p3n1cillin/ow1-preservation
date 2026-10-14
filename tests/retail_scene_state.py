"""Synthetic completion gates and reversible pointer encoding; no client data."""
import json
import struct
import sys
from pathlib import Path
import unittest
from unittest import mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import retail_scene_state as scene
import retail_login_state as login


class SavedMemory:
    image_base=0x10000000
    manager=0x50000000
    def __init__(self):self.memory={}
    def put(self,address,value):self.memory.update({address+i:v for i,v in enumerate(value)})
    def integer(self,address,value,size=8):self.put(address,value.to_bytes(size,'little'))
    def read(self,address,size):
        if any(address+i not in self.memory for i in range(size)):return b''
        return bytes(self.memory[address+i] for i in range(size))
    def find_all(self,needle):return [self.manager] if self.read(self.manager,8)==needle else []


class SceneTests(unittest.TestCase):
    def fixture(self):
        d=SavedMemory();b=d.image_base;pid=1234
        d.put(b+0xb4d8e4,struct.pack('<8I',0xb4ccca,0xb4ccd4,0xb4cce7,0xb4ccf1,0xb4ccfb,0xb4cd05,0xb4cd20,0xb4cd0f))
        d.put(b+0xb4d910,bytes.fromhex('4863420885c07e20'))
        d.put(b+scene.SCENE_READY,bytes.fromhex('0fb681a0000000c3'))
        d.put(d.manager,bytes(0xa0));d.integer(d.manager,b+login.WORLD_VFT)
        d.integer(d.manager+0x10,b+scene.SECONDARY_VFT);d.integer(d.manager+0x18,6,1)
        owner,obj=0x60000000,0x70000000
        d.integer(b+0x2ee48a1,0);d.integer(d.manager+8,owner^0x4dfd564467c27b96)
        d.integer(owner,b+scene.OWNER_VFT)
        seed=0x0a75eb31b884f74c^pid^0xb668aee222e8c2a6
        key=(~0xeef881967912c76c^((pid*0x4997511ddd173d59)&scene.MASK))&scene.MASK
        d.integer(b+0x2ee46d0+(key>>52),0);d.integer(b+0x2ee46d0+(key&0xfff),0)
        low=obj;rawlow=low^(seed&0xffffffff)
        rawhigh=((2*low)^(0x2e213dd2-low)^(seed>>32)^(-rawlow)^rawlow)&0xffffffff
        d.integer(owner+0x1d0,(rawhigh<<32)|rawlow)
        d.integer(obj,b+scene.SCENE_VFT);d.integer(b+scene.SCENE_VFT+0x140,b+scene.SCENE_READY)
        d.integer(obj+0xa0,0,1)
        d.integer(obj-0x70,0);d.integer(obj+0x38,0)
        return d,pid,obj

    def report(self,d,pid):
        with mock.patch.object(scene,'inspect'):return scene.loading_gates(d,pid)['managers'][0]

    def test_resource_completion_is_not_scene_readiness(self):
        d,pid,obj=self.fixture();row=self.report(d,pid)
        self.assertTrue(all(g['native_complete'] for g in row['resource_groups']))
        self.assertFalse(row['scene_ready']);self.assertFalse(row['loading_complete'])
        self.assertFalse(row['active_scene_present']);self.assertFalse(row['pending_scene_present'])
        self.assertNotIn('0x',json.dumps(row))
        d.integer(obj+0xa0,1,1);self.assertTrue(self.report(d,pid)['loading_complete'])
        d.integer(d.manager+0x18,7,1)
        self.assertEqual(self.report(d,pid)['state'],'WORLD LOADED')
        d.integer(d.manager+0x18,8,1)
        self.assertEqual(self.report(d,pid)['state'],'WORLD REPLICATING')
        for state in (9,10):
            d.integer(d.manager+0x18,state,1)
            self.assertEqual(self.report(d,pid)['state'],login.WORLD_STATES[state])
            self.assertTrue(self.report(d,pid)['loading_complete'])
        d.integer(d.manager+0x50,0x71000000);d.integer(d.manager+0x58,1,4)
        d.integer(0x71000000,0x72000000);d.integer(0x720000ac,1,1)
        self.assertFalse(self.report(d,pid)['loading_complete'])
        for value,complete in ((2,True),(3,True),(255,False)):
            d.integer(0x720000ac,value,1)
            self.assertEqual(self.report(d,pid)['loading_complete'],complete)

    def test_rejects_wrong_pid_profile_flags_and_arrays(self):
        mutations=[lambda d,o:d.integer(o+0xa0,2,1),
                   lambda d,o:d.integer(d.manager+0x58,4097,4),
                   lambda d,o:d.integer(d.manager+0x58,0xffffffff,4),
                   lambda d,o:d.integer(d.manager+0x58,1,4),
                   lambda d,o:d.integer(d.image_base+scene.SCENE_READY,0,1),
                   lambda d,o:d.integer(o+0x38,3),
                   lambda d,o:d.integer(d.image_base+0xb4d8e4,0,4)]
        for mutate in mutations:
            d,pid,obj=self.fixture();mutate(d,obj)
            with self.assertRaises(ValueError):self.report(d,pid)
        d,pid,obj=self.fixture()
        with self.assertRaises(ValueError):scene.loading_gates(d,pid) # incomplete original profile
        with self.assertRaises(ValueError):self.report(d,pid+1)
        with self.assertRaises(ValueError):scene.loading_gates(d,False)

    def pending_fixture(self):
        d,pid,obj=self.fixture();b=d.image_base
        expected=bytes.fromhex('488b815804000048ba2b2c1efcd260d5e4')
        for offset in (0x1b53d80,0x1b53d30):d.put(b+offset,expected)
        d.integer(obj+0x38,0x74000000);d.integer(0x74000000,0x75000000)
        d.integer(0x75000000,b+scene.SCENE_OBJECT_VFT)
        d.integer(0x75000478,123,4)
        d.integer(0x75000458,0x76000000^0xe4d560d2fc1e2c2b)
        d.integer(0x760001a8,1,4);d.integer(0x760001b0,0x77000000)
        d.integer(0x77000018,0x7a000002);d.integer(0x7700003c,0,4)
        d.integer(0x7a000000,0);d.integer(0x7a000008,2,4)
        d.integer(0x77000008,0x78000000);d.integer(0x77000010,0x79000000)
        d.integer(0x780000ac,3,1);d.integer(0x790000ac,3,1)
        return d,pid,obj

    def test_scene_state_must_advance_after_resources_complete(self):
        d,pid,obj=self.pending_fixture();row=self.report(d,pid)
        self.assertTrue(row['pending_scene_present']);self.assertEqual(row['pending_scene']['raw_state'],1)
        self.assertFalse(row['pending_scene']['native_ready_condition'])
        self.assertEqual(row['pending_scene']['update_count'],123)
        self.assertEqual(row['pending_scene']['typed_asset'],dict(reference_valid=True,object_present=False,native_status=2))
        d.integer(0x760001a8,5,4)
        row=self.report(d,pid);self.assertTrue(row['pending_scene']['native_ready_condition'])
        self.assertFalse(row['scene_ready']);self.assertFalse(row['loading_complete'])
        d.integer(0x790000ac,1,1)
        self.assertFalse(self.report(d,pid)['pending_scene']['native_ready_condition'])

    def test_typed_asset_status_does_not_replace_scene_readiness(self):
        d,pid,obj=self.pending_fixture()
        for flags,status in ((2,2),(0x10002,4),(0x18002,3),(3,0)):
            d.integer(0x7a000008,flags,4)
            self.assertEqual(self.report(d,pid)['pending_scene']['typed_asset']['native_status'],status)
        d.integer(0x7a000008,0x10002,4);d.integer(0x7a000000,0x7b000000)
        row=self.report(d,pid);self.assertTrue(row['pending_scene']['typed_asset']['object_present'])
        self.assertFalse(row['loading_complete'])

    def test_scene_progress_rejects_identity_state_and_truncated_data(self):
        mutations=[lambda d:d.integer(0x75000000,0),lambda d:d.integer(0x760001a8,33,4),
                   lambda d:d.integer(0x77000008,1),lambda d:d.integer(d.image_base+0x1b53d30,0,1)]
        for mutation in mutations:
            d,pid,obj=self.pending_fixture();mutation(d)
            with self.assertRaises(ValueError):self.report(d,pid)
        d,pid,obj=self.pending_fixture();del d.memory[0x790000ac]
        with self.assertRaises(ValueError):self.report(d,pid)


if __name__=='__main__':unittest.main()
