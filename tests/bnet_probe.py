"""Framing fixtures only; no original client login or service replies."""
import importlib.util
import io
from pathlib import Path
import struct
import unittest
from unittest import mock
import sys
import json
import tempfile
import subprocess

spec = importlib.util.spec_from_file_location('probe', Path(__file__).resolve().parents[1] / 'tools/bnet-probe.py')
probe = importlib.util.module_from_spec(spec); spec.loader.exec_module(probe)
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))


class Fragmented:
    def __init__(self, data): self.data = bytearray(data); self.closed = False; self.sent = bytearray()
    def recv(self, size):
        chunk = bytes(self.data[:min(size, 1)]); del self.data[:len(chunk)]; return chunk
    def settimeout(self, _): pass
    def version(self): return 'TLSv1.2'
    def close(self): self.closed = True
    def sendall(self, data): self.sent.extend(data)


class ProbeTests(unittest.TestCase):
    def test_nearby_players_notification_preserves_identity(self):
        from gateway_codec import load_messages, encode, decode
        from lobby_service import PROFILE_SCHEMA, WELCOME_SCHEMA, GAME_ACCOUNT_HIGH
        root = Path(__file__).resolve().parents[1]
        messages = load_messages(root/'protocol/nearby-players-104319.json')
        self.assertEqual(set(messages), {(PROFILE_SCHEMA,20815)})
        catalogue = json.loads((root/'protocol/gateway-104319.json').read_text())['protocols']
        self.assertTrue(any(p['schema_hash'] == PROFILE_SCHEMA and p['first_id'] <= 20815 < p['end_id']
                            for p in catalogue))
        fields = messages[PROFILE_SCHEMA,20815]
        existing = load_messages(root/'protocol/lobby-login-104319.json')
        self.assertEqual(fields[0]['fields'], existing[WELCOME_SCHEMA,20502][0]['fields'])
        player = {0:{0:1001,8:GAME_ACCOUNT_HIGH}, 0x10:{0:1001,8:1<<56}, 0x40:b'Tracer#1001'}
        wire = encode(fields, {0x78:[player]})
        decoded = decode(fields, wire)
        self.assertEqual(len(decoded[0x78]), 1)
        for offset, value in player.items():
            self.assertEqual(decoded[0x78][0][offset], value)
        self.assertEqual(decode(fields, encode(fields, {0x78:[]})), {0x78:[]})
        with self.assertRaises(ValueError): decode(fields, wire[:-1])

    def test_party_message_identity_wire_and_catalogue(self):
        from gateway_codec import load_messages, encode, decode
        root = Path(__file__).resolve().parents[1]
        messages = load_messages(root/'protocol/party-104319.json')
        catalogue = json.loads((root/'protocol/gateway-104319.json').read_text())['protocols']
        for (schema, mid), fields in messages.items():
            self.assertTrue(any(p['schema_hash'] == schema and p['first_id'] <= mid < p['end_id']
                                for p in catalogue))
        identity = {0:123, 8:456}
        # The original Invite and merge-accept actions each send exactly two u64s.
        for mid in (22102,22110):
            fields = messages[3003079262,mid]
            wire = encode(fields, {0x78:identity})
            self.assertEqual(wire, struct.pack('<QQ',123,456))
            self.assertEqual(decode(fields, wire), {0x78:identity})
            with self.assertRaises(ValueError): decode(fields, wire[:-1])
        existing = load_messages(root/'protocol/lobby-login-104319.json')
        self.assertEqual(messages[605150806,20700], existing[605150806,20700])

    def test_read_only_login_state_guards_and_secret_omission(self):
        import retail_login_state as state
        class SparseDump:
            image_base=0x10000000
            def __init__(self):
                self.memory={}
                self.put(self.image_base,b'MZ')
                self.put(self.image_base+0x3c,struct.pack('<I',0x80))
                header=bytearray(84);header[:4]=b'PE\0\0'
                struct.pack_into('<H',header,4,0x200)
                struct.pack_into('<I',header,8,state.TIMESTAMP)
                struct.pack_into('<H',header,24,0x20b)
                struct.pack_into('<I',header,80,state.IMAGE_SIZE)
                self.put(self.image_base+0x80,header)
                root,table,login,keys=0x20000000,0x20001000,0x20002000,0x20004000
                self.put(self.image_base+state.ROOT_RVA,struct.pack('<Q',root))
                self.put(self.image_base+state.COOKIE_RVA,bytes(8))
                self.put(root,struct.pack('<Q',self.image_base+state.ROOT_VFT))
                self.put(root+0x140,struct.pack('<Q',state.TABLE_MASK^table))
                self.put(table+9*8,struct.pack('<QQ',login,keys))
                self.put(table+22*8,struct.pack('<Q',0x20006000))
                self.put(login,struct.pack('<Q',self.image_base+state.LOGIN_VFT))
                self.put(keys,struct.pack('<Q',self.image_base+state.KEYS_VFT))
                self.put(login+0xe0,b'SECRET_ACCOUNT!!')
                self.put(keys+0x40,b'\1')
                self.put(0x20006000,struct.pack('<Q',self.image_base+state.PLAYER_VFT))
                self.put(0x20006088,b'\0')
            def put(self,address,value):
                for index,byte in enumerate(value):self.memory[address+index]=byte
            def read(self,address,size):
                if any(address+i not in self.memory for i in range(size)):return b''
                return bytes(self.memory[address+i] for i in range(size))
        dump=SparseDump()
        result=state.inspect(dump)
        self.assertEqual(result,dict(build=104319,identity_installed=True,key_notification_received=True,player_update_marker=False))
        self.assertNotIn('SECRET',json.dumps(result))
        # Queue diagnostics retain only counts/booleans, even if a native job
        # pointer is present. They never dereference or export session inputs.
        queue,instance,service=0x20008000,0x2000a000,0x2000c000
        dump.put(0x20001000+38*8,struct.pack('<Q',queue))
        dump.put(0x20001000+120*8,struct.pack('<Q',instance))
        dump.put(0x20000000+0x220,struct.pack('<Q',service))
        for pointer,vft in ((queue,state.QUEUE_VFT),(instance,state.INSTANCE_VFT),(service,state.QUEUE_SERVICE_VFT)):
            dump.put(pointer,struct.pack('<Q',dump.image_base+vft))
        for offset,count in zip((0x10,0x38,0x60,0x88),(1,0,0,2)):
            dump.put(service+offset+0x10,struct.pack('<i',count))
        dump.put(queue+0x10f9,b'\1')
        dump.put(instance+0x20,struct.pack('<Q',0x30000000))
        self.assertEqual(state.queue_states(dump),dict(record_counts=[1,0,0,2],
                         reply_23332_marker=True,instance_referral_job_present=True))
        self.assertNotIn('SECRET',json.dumps(state.queue_states(dump)))
        dump.put(service+0x20,struct.pack('<i',-1))
        with self.assertRaises(ValueError):state.queue_states(dump)
        dump.put(service+0x20,struct.pack('<i',1025))
        with self.assertRaises(ValueError):state.queue_states(dump)
        dump.put(service+0x20,struct.pack('<i',1))
        dump.put(queue+0x10f9,b'\2')
        with self.assertRaises(ValueError):state.queue_states(dump)
        dump.put(0x20004040,b'\0')
        self.assertFalse(state.inspect(dump)['key_notification_received'])
        for address,value in ((0x20004040,b'\2'),(0x20006088,b'\2'),(0x20002000,bytes(8)),
                              (dump.image_base+0x80+8,bytes(4)),(dump.image_base+state.ROOT_RVA,bytes(8))):
            broken=SparseDump();broken.put(address,value)
            with self.assertRaises(ValueError):state.inspect(broken)

    def test_training_queue_experiment_scope_and_layouts(self):
        from gateway_codec import load_messages,encode,decode
        from gateway_protocol import load_catalogue
        from lobby_service import InitialLobby,QUEUE_SCHEMA,QUEUE_REPLY_SCHEMA
        root=Path(__file__).resolve().parents[1]
        messages=load_messages(root/'protocol/lobby-login-104319.json')
        replies=load_messages(root/'protocol/queue-104319.json')
        self.assertEqual(len(replies),34)
        for (schema,mid),fields in replies.items():
            self.assertEqual(schema,QUEUE_REPLY_SCHEMA)
            self.assertTrue(23300<=mid<23334)
            wire=encode(fields,{})
            self.assertEqual(encode(fields,decode(fields,wire)),wire)
        messages.update(replies)
        hashes=load_catalogue(root/'protocol/gateway-104319.json',13)
        entry=hashes.index(QUEUE_SCHEMA)+1
        request=bytes((entry,0))+bytes.fromhex('020004000000')
        service=InitialLobby(hashes,messages,queue_reply=23332)
        self.assertIsNone(service.answer(request))  # before native hello
        service.sent=True
        self.assertEqual(service.answer(request),(23332,bytes((hashes.index(QUEUE_REPLY_SCHEMA)+1,32))))
        # Optional experiment only; the normal launcher still waits for a
        # demonstrated game assignment instead of inventing a queue result.
        normal=InitialLobby(hashes,messages);normal.sent=True
        self.assertIsNone(normal.answer(request))
        for body in (b'',bytes.fromhex('02000400'),bytes.fromhex('02000400000000')):
            with self.assertRaises(ValueError):service.answer(bytes((entry,0))+body)
        for mode,name,value in ((1,b'',4),(2,b'nontraining',4),(2,b'',5)):
            self.assertIsNone(service.answer(bytes((entry,0))+encode(messages[QUEUE_SCHEMA,24000],{0x78:mode,0x80:name,0xa8:value})))
        for reply in (True,23299,23334):
            with self.assertRaises(ValueError):InitialLobby(hashes,messages,queue_reply=reply)
        with self.assertRaises(ValueError):InitialLobby(tuple(h for h in hashes if h!=QUEUE_REPLY_SCHEMA),messages,queue_reply=23332)
        with self.assertRaises(ValueError):InitialLobby(hashes,{k:v for k,v in messages.items() if k!=(QUEUE_SCHEMA,24000)},queue_reply=23332)

    def test_plain_instance_referral_is_explicit_and_loopback_only(self):
        from gateway_codec import load_messages,decode
        from gateway_protocol import load_catalogue
        from lobby_service import InitialLobby,QUEUE_SCHEMA
        from instance_referral import INSTANCE_SCHEMA,local_referral,signed_chars
        root=Path(__file__).resolve().parents[1]
        messages=load_messages(root/'protocol/lobby-login-104319.json')
        messages.update(load_messages(root/'protocol/instance-104319.json'))
        hashes=load_catalogue(root/'protocol/gateway-104319.json',13)
        service=InitialLobby(hashes,messages,instance_referral=True)
        request=bytes((hashes.index(QUEUE_SCHEMA)+1,0))+bytes.fromhex('020004000000')
        self.assertIsNone(service.answer(request))
        service.sent=True
        mid,packet=service.answer(request)
        self.assertEqual((mid,packet[:2],len(packet)),(20600,bytes((hashes.index(INSTANCE_SCHEMA)+1,0)),242))
        values=decode(messages[INSTANCE_SCHEMA,20600],packet[2:])
        self.assertFalse(values[0x78])
        record=values[0x80]
        self.assertEqual(record[0],{0:1,8:1})
        self.assertEqual(record[0x2c],1119)
        host=bytes(v&255 for v in record[0x2e])
        self.assertEqual(host,b'127.0.0.1'+bytes(55))
        self.assertEqual((len(record[0xae]),len(record[0xce])),(32,32))
        self.assertTrue(1<=record[0x10]<2**31)
        # 0x007ccbf6 parses this string as IPv4:port. A random token leaves
        # the zero-initialized connection address unusable.
        endpoint=bytes(v&255 for v in record[0x6e])
        self.assertEqual(endpoint,b'127.0.0.1:1119'+bytes(50))
        fresh=local_referral()[0x80]
        self.assertEqual(fresh[0x6e],record[0x6e])
        self.assertNotEqual((fresh[0xae],fresh[0xce]),(record[0xae],record[0xce]))
        self.assertEqual(signed_chars(b'\xff',2),[-1,0])
        with self.assertRaises(ValueError):signed_chars(bytes(65),64)
        for broken in (b'',request[2:-1],request[2:]+b'x'):
            with self.assertRaises(ValueError):service.answer(request[:2]+broken)
        with self.assertRaises(ValueError):InitialLobby(hashes,messages,instance_referral=1)
        with self.assertRaises(ValueError):InitialLobby(hashes,messages,instance_referral=True,queue_reply=23332)
        with self.assertRaises(ValueError):InitialLobby(hashes,{k:v for k,v in messages.items() if k!=(INSTANCE_SCHEMA,20600)},instance_referral=True)
        self.assertIsNone(InitialLobby(hashes,messages).answer(request))
        # Pair mode: the second client is referred to its own container port 1129.
        pair=local_referral(1129)[0x80]
        self.assertEqual(pair[0x2c],1129)
        self.assertEqual(bytes(v&255 for v in pair[0x6e]),b'127.0.0.1:1129'+bytes(50))
        self.assertNotEqual((pair[0xae],pair[0xce]),(fresh[0xae],fresh[0xce]))
        third=local_referral(1139)[0x80]
        self.assertEqual((third[0x2c],bytes(v&255 for v in third[0x6e])),(1139,b'127.0.0.1:1139'+bytes(50)))
        for bad in (1130,1149,0,21129,True,'1129',None):
            with self.assertRaises(ValueError):local_referral(bad)
            with self.assertRaises(ValueError):InitialLobby(hashes,messages,instance_referral=True,instance_port=bad)
        second=InitialLobby(hashes,messages,instance_referral=True,instance_port=1129);second.sent=True
        mid,packet=second.answer(request)
        record=decode(messages[INSTANCE_SCHEMA,20600],packet[2:])[0x80]
        self.assertEqual((mid,record[0x2c]),(20600,1129))
        self.assertEqual(bytes(v&255 for v in record[0x6e]),b'127.0.0.1:1129'+bytes(50))

    def test_resource_list_type_allowlist(self):
        from lobby_service import RESOURCE_LIST_HIGHS,STACK_ITEM_GUID_HIGH
        self.assertIn(STACK_ITEM_GUID_HIGH,RESOURCE_LIST_HIGHS)
        self.assertEqual(STACK_ITEM_GUID_HIGH,0x0d60)
        self.assertNotIn(0x02e0,RESOURCE_LIST_HIGHS)
        probe=Path(__file__).resolve().parents[1]/'tools'/'bnet-probe.py'
        for bad in ('0580000000001d9e','0d60000000000000'):
            r=subprocess.run([sys.executable,str(probe),'--lobby-initial-data','full','--lobby-preload-stack-item',bad],capture_output=True,text=True)
            self.assertNotEqual(r.returncode,0)

    def test_own_key_referral_allowlist(self):
        self.assertEqual(probe.own_key_referral_port('127.0.0.1:1119',21119),1119)
        self.assertEqual(probe.own_key_referral_port('127.0.0.1:1119',21129),1119)
        self.assertEqual(probe.own_key_referral_port('127.0.0.1:1129',21129),1129)
        self.assertEqual(probe.own_key_referral_port('127.0.0.1:1139',21139),1139)
        for host,port in (('127.0.0.1:1129',21119),('127.0.0.1:1130',21129),('127.0.0.2:1119',21119),
                          ('example.invalid:1119',21119),('',21119),('127.0.0.1:1129 ',21129),
                          ('127.0.0.1:1139',21129),('127.0.0.1:1139',21119),('127.0.0.1:1149',21149)):
            self.assertIsNone(probe.own_key_referral_port(host,port))
        script=Path(__file__).resolve().parents[1]/'tools'/'bnet-probe.py'
        base=[sys.executable,str(script),'--cert','missing.pem','--key','missing.key','--serve',
              '--lobby-private-key','missing-own.pem','--lobby-integrity-key','missing.bin']
        for extra in (['--referral-host','127.0.0.1:1129'],['--port','21119','--referral-host','127.0.0.1:1129'],
                      ['--port','21129','--referral-host','127.0.0.1:1139'],['--port','21149','--referral-host','127.0.0.1:1149']):
            r=subprocess.run(base+extra,capture_output=True,text=True)
            self.assertNotEqual(r.returncode,0)
            self.assertIn('exact loopback referral',r.stderr)
        # The allowed pair referral passes the guard and fails only on the absent key input.
        r=subprocess.run(base+['--port','21129','--referral-host','127.0.0.1:1129'],capture_output=True,text=True)
        self.assertNotEqual(r.returncode,0)
        self.assertNotIn('exact loopback referral',r.stderr)

    def test_local_account_store(self):
        import tempfile
        from accounts import AccountStore
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'accounts.json'
            store=AccountStore(path)
            tracer=store.create('Tracer','blink')
            mercy=store.create('Mercy')
            self.assertEqual((tracer['account_id'],tracer['battle_tag']),(1001,'Tracer#1001'))
            self.assertEqual(mercy['account_id'],1002)
            self.assertNotIn('blink',path.read_text())
            store=AccountStore(path)
            self.assertEqual(store.verify('tracer','blink')['account_id'],1001)
            self.assertEqual(store.verify('Mercy',None)['account_id'],1002)
            with self.assertRaises(ValueError):store.verify('Tracer','wrong')
            with self.assertRaises(ValueError):store.create('TRACER')
            for bad in ('ab','1abc','Way2LongNameHere','Bad#Name'):
                with self.assertRaises(ValueError):store.create(bad)
            store.delete('Mercy')
            self.assertEqual(AccountStore(path).create('Genji')['account_id'],1003)

    def test_profile_request_gets_minimal_profile(self):
        from gateway_codec import load_messages,decode,encode
        from gateway_protocol import load_catalogue
        from lobby_service import InitialLobby,HELLO_SCHEMA,PROFILE_SCHEMA,SOCIAL_SCHEMA,GAME_ACCOUNT_HIGH
        root=Path(__file__).resolve().parents[1]
        hashes=load_catalogue(root/'protocol/gateway-104319.json',13)
        messages=load_messages(root/'protocol/lobby-login-104319.json')
        target={0:1002,8:1<<56}
        request=bytes((hashes.index(SOCIAL_SCHEMA)+1,6))+encode(messages[SOCIAL_SCHEMA,22206],{0x78:target,0x98:7})
        service=InitialLobby(hashes,messages,'Mercy#1002',None,1002)
        self.assertIsNone(service.answer(request))  # not before login
        service.receive(bytes((hashes.index(HELLO_SCHEMA)+1,0))+encode(messages[HELLO_SCHEMA,21800],
                        {0xb8:{0:{0:1002,8:GAME_ACCOUNT_HIGH}},0x1bc:104319}))
        mid,reply=service.answer(request)
        self.assertEqual((mid,reply[:2]),(20807,bytes((hashes.index(PROFILE_SCHEMA)+1,7))))
        profile=decode(messages[PROFILE_SCHEMA,20807],reply[2:])
        self.assertEqual((profile[0x78],profile[0x88],profile[0x90][0x100]),(target,False,target))
        self.assertEqual(profile[0x218],b'')
        self.assertIsNone(service.answer(b'\x01\x03'))
        empty=bytes((hashes.index(SOCIAL_SCHEMA)+1,6))+encode(messages[SOCIAL_SCHEMA,22206],{})
        with self.assertRaises(ValueError):service.answer(empty)

    def test_compact_blob_and_float_fields(self):
        from gateway_codec import encode,decode
        fields=[{'kind':15,'offset':0,'width':40,'count':0},{'kind':11,'offset':40,'width':8,'count':0}]
        body=encode(fields,{0:b'abc',40:1.5})
        self.assertEqual(body,struct.pack('<I',3)+b'abc'+struct.pack('<d',1.5))
        self.assertEqual(decode(fields,body),{0:b'abc',40:1.5})
        with self.assertRaises(ValueError):decode(fields,struct.pack('<I',99)+b'abc'+bytes(8))
        with self.assertRaises(ValueError):encode(fields,{40:1})
        fixed=[{'kind':8,'offset':0,'width':8,'count':2}]
        self.assertEqual(encode(fixed,{}),bytes(16))
        with self.assertRaises(ValueError):encode(fixed,{0:[1]})

    def test_party_of_one_marks_player_leader(self):
        from gateway_codec import load_messages,decode,encode
        from gateway_protocol import load_catalogue
        from lobby_service import InitialLobby,HELLO_SCHEMA,PARTY_SCHEMA,GAME_ACCOUNT_HIGH
        root=Path(__file__).resolve().parents[1]
        hashes=load_catalogue(root/'protocol/gateway-104319.json',13)
        messages=load_messages(root/'protocol/lobby-login-104319.json')
        service=InitialLobby(hashes,messages,'Mercy#1002','full',1002)
        identity={0:1002,8:GAME_ACCOUNT_HIGH}
        service.receive(bytes((hashes.index(HELLO_SCHEMA)+1,0))+encode(messages[HELLO_SCHEMA,21800],
                        {0xb8:{0:identity},0x1bc:104319}))
        sent=dict(service.initial_notifications())
        self.assertEqual(list(sent),[20504,20505,20502,20802,20700])
        packet=sent[20700]
        self.assertEqual(packet[:2],bytes((hashes.index(PARTY_SCHEMA)+1,0)))
        party=decode(messages[PARTY_SCHEMA,20700],packet[2:])[0x78]
        self.assertEqual(party[0x60],identity)
        [member]=party[0x00]
        self.assertEqual((member[0x00][0x00],member[0x00][0x40],member[0xe0],member[0xe2]),
                         (identity,b'Mercy#1002',5,True))

    def test_launcher_detects_start_conflicts(self):
        import tempfile
        import ow1_launcher as launcher
        with tempfile.TemporaryDirectory() as folder:
            log=Path(folder)/'run.log'
            log.write_text('Native CA probe: original instruction profile verified.\nClient exited: 0x1\n')
            self.assertTrue(launcher.early_exit(log))
            log.write_text('TLS observer: native_job_state=1\nClient exited: 0x0\n')
            self.assertFalse(launcher.early_exit(log))
            self.assertFalse(launcher.early_exit(Path(folder)/'missing.log'))
        calls=iter([False,False,True])
        with mock.patch.object(launcher.time,'sleep'):
            self.assertTrue(launcher.wait_until(lambda:next(calls),10))
            self.assertFalse(launcher.wait_until(lambda:False,0))

    def test_account_identity_reaches_login_and_lobby(self):
        from gateway_codec import load_messages,decode,encode
        from gateway_protocol import load_catalogue
        from lobby_service import InitialLobby,HELLO_SCHEMA,WELCOME_SCHEMA,GAME_ACCOUNT_HIGH
        root=Path(__file__).resolve().parents[1]
        hashes=load_catalogue(root/'protocol/gateway-104319.json',13)
        messages=load_messages(root/'protocol/lobby-login-104319.json')
        entry=hashes.index(HELLO_SCHEMA)+1
        def hello(account):
            return bytes((entry,0))+encode(messages[HELLO_SCHEMA,21800],{0xb8:{0:{0:account,8:GAME_ACCOUNT_HIGH}},0x1bc:104319})
        service=InitialLobby(hashes,messages,'Mercy#1002',None,1002)
        with self.assertRaises(ValueError):service.receive(hello(1001))
        values=decode(messages[WELCOME_SCHEMA,20500],service.receive(hello(1002))[2:])
        self.assertEqual(values[0x78][0],1002)
        self.assertEqual(values[0x88][0],1002)
        self.assertEqual(values[0xa8],b'Mercy#1002')
        with self.assertRaises(ValueError):InitialLobby(hashes,messages,'X#0',None,0)
        result=probe.build_logon_result('Mercy#1002',1002)
        self.assertIn(b'Mercy#1002',result)
        self.assertEqual(result.count(struct.pack('<Q',1002)),2)

    def test_world_state_report_names_only(self):
        import retail_login_state as state
        base=0x10000000
        manager=bytearray(0x28)
        manager[:8]=struct.pack('<Q',base+state.WORLD_VFT)
        manager[0x18]=2
        unknown=bytearray(manager); unknown[0x18]=11
        class FakeDump:
            image_base=base
            def __init__(self, objects): self.objects=objects
            def find_all(self, needle):
                return [a for a,b in self.objects.items() if b.startswith(needle)]
            def read(self, address, size): return bytes(self.objects[address][:size])
        report=state.world_states(FakeDump({0x30000000:manager, base+0x100:manager}))
        self.assertEqual(report,[{'state':'WAITING','world_request_pending':False}])
        manager[0x20:0x28]=struct.pack('<Q',0x40000000)
        self.assertTrue(state.world_states(FakeDump({0x30000000:manager}))[0]['world_request_pending'])
        with self.assertRaises(ValueError):
            state.world_states(FakeDump({0x30000000:unknown}))

    def test_compact_known_bytes_and_bounds(self):
        from gateway_codec import decode,encode
        fields=[dict(kind=0,offset=i,width=1,count=0) for i in range(3)]
        fields += [dict(kind=7,offset=4,width=4,count=0),dict(kind=12,offset=8,width=40,count=0),
                   dict(kind=8,offset=48,width=8,count=2)]
        wire=b'\x05\x78\x56\x34\x12fixture\0'+struct.pack('<QQ',3,4)
        values={0:True,1:False,2:True,4:0x12345678,8:b'fixture',48:[3,4]}
        self.assertEqual(decode(fields,wire),values)
        self.assertEqual(encode(fields,values),wire)
        for size in range(len(wire)):
            with self.assertRaises(ValueError):decode(fields,wire[:size])
        with self.assertRaises(ValueError):decode(fields,wire+b'x')
        for bad in ({**values,0:1},{**values,8:b'embedded\0NUL'},{**values,48:[3]},
                    {**values,4:-1},{**values,99:0}):
            with self.assertRaises(ValueError):encode(fields,bad)
        array=[dict(kind=2,offset=0,width=1,count=-1)]
        for packet in (struct.pack('<I',1025),struct.pack('<I',10)+b'x'):
            with self.assertRaises(ValueError):decode(array,packet)

    def test_initial_lobby_reply_is_scoped_to_own_hello(self):
        from gateway_codec import load_messages,decode,encode
        from gateway_protocol import load_catalogue
        from lobby_service import InitialLobby,HELLO_SCHEMA,WELCOME_SCHEMA,GAME_ACCOUNT_HIGH
        root=Path(__file__).resolve().parents[1]
        hashes=load_catalogue(root/'protocol/gateway-104319.json',13)
        messages=load_messages(root/'protocol/lobby-login-104319.json')
        identity={0:1001,8:GAME_ACCOUNT_HIGH}
        hello={0xb8:{0:identity},0x1bc:104319}
        entry=hashes.index(HELLO_SCHEMA)+1
        packet=bytes((entry,0))+encode(messages[HELLO_SCHEMA,21800],hello)
        service=InitialLobby(hashes,messages,'Fixture#1001')
        self.assertIsNone(service.receive(b'\0\x03'))
        reply=service.receive(packet)
        self.assertEqual(reply[:2],bytes((hashes.index(WELCOME_SCHEMA)+1,0)))
        values=decode(messages[WELCOME_SCHEMA,20500],reply[2:])
        self.assertEqual(values[0x78],identity)
        self.assertEqual(values[0xa8],b'Fixture#1001')
        self.assertFalse(values[0x148])
        with self.assertRaises(ValueError):service.receive(packet)
        for value in (103000,0):
            hello[0x1bc]=value
            wrong=bytes((entry,0))+encode(messages[HELLO_SCHEMA,21800],hello)
            with self.assertRaises(ValueError):InitialLobby(hashes,messages).receive(wrong)
        with self.assertRaises(ValueError):InitialLobby(hashes,messages).receive(packet[:-1])
        for option,expected in (('keys',((20504,bytes((83,4))+bytes(8)),)),
                                ('keys-hotfix',((20504,bytes((83,4))+bytes(8)),(20505,bytes((83,5))+bytes(16))))):
            service=InitialLobby(hashes,messages,initial_data=option)
            self.assertEqual(service.initial_notifications(),())
            hello[0x1bc]=104319
            service.receive(bytes((entry,0))+encode(messages[HELLO_SCHEMA,21800],hello))
            self.assertEqual(service.initial_notifications(),expected)
            self.assertEqual(service.initial_notifications(),())
        with self.assertRaises(ValueError):InitialLobby(hashes,messages,initial_data='all')
        with self.assertRaises(ValueError):InitialLobby(hashes,{(HELLO_SCHEMA,21800):messages[HELLO_SCHEMA,21800]},initial_data='keys')
        service=InitialLobby(hashes,messages,initial_data='keys-hotfix-player')
        service.receive(bytes((entry,0))+encode(messages[HELLO_SCHEMA,21800],hello))
        notifications=service.initial_notifications()
        self.assertEqual([mid for mid,_ in notifications],[20504,20505,20502])
        mid,packet=notifications[-1]
        # Independent positional wire fixture: two ids, three u64 counters,
        # two u32 counters and the own tag, all on message delta 2.
        expected=bytes((83,2))+struct.pack('<QQQQQQQII',1001,GAME_ACCOUNT_HIGH,1001,1<<56,0,0,0,0,0)+b'Preservation#1001\0'
        self.assertEqual(packet,expected)
        self.assertEqual(decode(messages[WELCOME_SCHEMA,mid],packet[2:])[0x78][0],identity)
        from lobby_service import PROFILE_SCHEMA
        service=InitialLobby(hashes,messages,initial_data='keys-hotfix-player-settings')
        service.receive(bytes((entry,0))+encode(messages[HELLO_SCHEMA,21800],hello))
        notifications=service.initial_notifications()
        self.assertEqual([mid for mid,_ in notifications],[20504,20505,20502,20802])
        # Default preferences on the profile protocol entry, delta 2: six empty
        # vectors (24 B), bit-packed flag groups and bytes (15 B + 6 B), then an
        # empty trailing vector after its flushed flag byte (5 B).
        self.assertEqual(notifications[-1][1],bytes((hashes.index(PROFILE_SCHEMA)+1,2))+bytes(50))
        # Opt-in 20505 list 0 (native Hero-set input): count then u64 GUIDs,
        # followed by the three remaining empty lists.
        heroes=(0x02e000000000006e,0x02e0000000000002)
        service=InitialLobby(hashes,messages,initial_data='keys-hotfix',hero_list=heroes)
        service.receive(bytes((entry,0))+encode(messages[HELLO_SCHEMA,21800],hello))
        hotfix=dict(service.initial_notifications())[20505]
        self.assertEqual(hotfix,bytes((83,5))+struct.pack('<IQQ',2,*heroes)+bytes(12))
        self.assertEqual(InitialLobby(hashes,messages,initial_data='keys-hotfix').hero_list,())
        for bad in ((0x040000000000000e,),(0x02e0000000000000,),(0x02e000000000006e,)*2,
                    tuple(0x02e0000000000001+i for i in range(65)),('0x02e000000000006e',)):
            with self.assertRaises(ValueError):InitialLobby(hashes,messages,initial_data='keys-hotfix',hero_list=bad)
        with self.assertRaises(ValueError):InitialLobby(hashes,messages,initial_data='keys',hero_list=heroes)
        # Opt-in 20505 list 1 (statescript graph resource requests).
        graphs=(0x0580000000000c8e,)
        service=InitialLobby(hashes,messages,initial_data='keys-hotfix',resource_list=graphs)
        service.receive(bytes((entry,0))+encode(messages[HELLO_SCHEMA,21800],hello))
        hotfix=dict(service.initial_notifications())[20505]
        self.assertEqual(hotfix,bytes((83,5))+struct.pack('<IIQ',0,1,*graphs)+bytes(8))
        for bad in ((0x02e000000000006e,),(0x0580000000000000,),graphs*2,(0x0400000000000000,)):
            with self.assertRaises(ValueError):InitialLobby(hashes,messages,initial_data='keys-hotfix',resource_list=bad)
        # Entity definitions (type 3) share list 1 with graphs.
        mixed=(0x0580000000000c8e,0x04000000000004bf)
        service=InitialLobby(hashes,messages,initial_data='keys-hotfix',resource_list=mixed)
        service.receive(bytes((entry,0))+encode(messages[HELLO_SCHEMA,21800],hello))
        hotfix=dict(service.initial_notifications())[20505]
        self.assertEqual(hotfix,bytes((83,5))+struct.pack('<IIQQ',0,2,*mixed)+bytes(8))
        # Opt-in 20505 list 2: map-header GUIDs only (the original map preload input).
        header=0x0790000000000688
        service=InitialLobby(hashes,messages,initial_data='keys-hotfix',map_headers=(header,))
        service.receive(bytes((entry,0))+encode(messages[HELLO_SCHEMA,21800],hello))
        self.assertEqual(dict(service.initial_notifications())[20505],bytes((83,5))+struct.pack('<IIIQI',0,0,1,header,0))
        for bad in ((0x0800000000000688,),(0x0580000000000c8e,),(0x0790000000000000,),(header,header),('0790000000000688',)):
            with self.assertRaises(ValueError):InitialLobby(hashes,messages,initial_data='keys-hotfix',map_headers=bad)
        with self.assertRaises(ValueError):InitialLobby(hashes,messages,initial_data='keys',map_headers=(header,))
        # Opt-in 24900 unlock state: one zero-keyed group of 24-byte records.
        from lobby_service import UNLOCK_SCHEMA
        unlock_messages=dict(messages);unlock_messages.update(load_messages(root/'protocol/unlocks-104319.json'))
        skins=(0x0250000000000876,0x02500000000001fb)
        service=InitialLobby(hashes,unlock_messages,initial_data='keys',unlocks=skins)
        service.receive(bytes((entry,0))+encode(messages[HELLO_SCHEMA,21800],hello))
        mid,packet=service.initial_notifications()[-1]
        self.assertEqual(mid,24900)
        record=lambda g:struct.pack('<QQiHBB',g,0,0,0,0,0)
        self.assertEqual(packet,bytes((hashes.index(UNLOCK_SCHEMA)+1,0))+struct.pack('<iII',0,0,1,)
                         +struct.pack('<I',2)+record(skins[0])+record(skins[1])+struct.pack('<QI',0,0))
        for bad in ((0x02e000000000006e,),skins*2,(0x0250000000000000,),(0x0a5000000000170f,)):
            with self.assertRaises(ValueError):InitialLobby(hashes,unlock_messages,initial_data='keys',unlocks=bad)
        with self.assertRaises(ValueError):InitialLobby(hashes,messages,initial_data='keys',unlocks=skins)
        with self.assertRaises(ValueError):InitialLobby(hashes,unlock_messages,unlocks=skins)

    def test_message_descriptor_export_rejects_ambiguity_and_cycles(self):
        from gateway_catalogue import extract_message
        class SparseDump:
            image_base=0x10000000
            def __init__(self):
                self.area=bytearray(0x80000)
                struct.pack_into('<Q',self.area,16,self.image_base+0x2c81000)
                struct.pack_into('<IH',self.area,24,123,100)
                struct.pack_into('<QIIIiQQQ',self.area,0x1000,0,7,120,4,0,0,0,0)
                struct.pack_into('<QIIIiQQQ',self.area,0x1030,0,17,0,0,0,0,0,0)
            def read(self,address,size):
                start=address-self.image_base-0x2c80000
                return bytes(self.area[start:start+size]) if start>=0 else b''
        dump=SparseDump()
        result=extract_message(dump,123,100)
        self.assertEqual(result['fields'],[dict(kind=7,offset=120,width=4,count=0)])
        struct.pack_into('<QIIIiQQQ',dump.area,0x1000,0,14,120,16,0,dump.image_base+0x2c81000,0,0)
        with self.assertRaises(ValueError):extract_message(dump,123,100)
        dump=SparseDump()
        struct.pack_into('<Q',dump.area,0x2010,dump.image_base+0x2c81000)
        struct.pack_into('<IH',dump.area,0x2018,123,100)
        with self.assertRaises(ValueError):extract_message(dump,123,100)
        with self.assertRaises(ValueError):extract_message(dump,123,101)

    def test_message_schema_loader_bounds(self):
        from gateway_codec import load_messages
        field=dict(kind=7,offset=0,width=4,count=0)
        message=dict(schema_hash=123,message_id=100,fields=[field])
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'schema.json'
            for document in ([],{'build':1,'messages':[message]},
                             {'build':104319,'messages':[message,message]},
                             {'build':104319,'messages':[{**message,'fields':[field,field]}]},
                             {'build':104319,'messages':[{**message,'fields':[{**field,'kind':True}]}]},
                             {'build':104319,'messages':[{**message,'fields':[{**field,'count':1025}]}]}):
                path.write_text(json.dumps(document))
                with self.assertRaises(ValueError):load_messages(path)

    def test_fragmentation_and_secret_omission(self):
        header = b'\x08\x00\x10\x01\x28\x06\x6a\x06SECRET'
        frame = struct.pack('>H', len(header)) + header + b'SECRET'
        hlen, fields, count = probe.read_frame(Fragmented(frame))
        self.assertEqual((hlen, fields[2], count), (len(header), [1], 6))
        conn, log = Fragmented(frame), io.StringIO()
        probe.handle(conn, ('127.0.0.1', 1), log)
        self.assertTrue(conn.closed); self.assertNotIn('SECRET', log.getvalue())
        self.assertIn('body bytes=6', log.getvalue())
        self.assertIn('version=TLSv1.2', log.getvalue())

    def test_tls_peer_close_is_not_an_rpc(self):
        conn, log = Fragmented(b''), io.StringIO()
        probe.handle(conn, ('127.0.0.1', 1), log)
        self.assertTrue(conn.closed)
        self.assertIn('peer closed with 2 bytes missing', log.getvalue())
        self.assertNotIn('Header (', log.getvalue())

    def test_truncated_frames_stop(self):
        for data in (b'', b'\0', b'\0\x04\x08', b'\0\x02\x28\x05X'):
            with self.assertRaises(EOFError): probe.read_frame(Fragmented(data))

    def test_malformed_headers(self):
        for data in (b'', b'\0\0', b'\x08\x80', b'\x08' + b'\xff' * 10,
                     b'\x0a\x03x', b'\x0dX', b'\x09X', b'\x0b'):
            with self.assertRaises(ValueError): probe.decode_header(data)

    def test_body_bounds_and_duplicate_lengths(self):
        for header in (b'\x28\x01\x28\x01', b'\x2a\x01x', b'\x28\xff\xff\xff\x7f'):
            with self.assertRaises(ValueError):
                probe.read_frame(Fragmented(struct.pack('>H', len(header)) + header))
        self.assertEqual(probe.read_frame(Fragmented(b'\0\x02\x08\0'))[2], 0)

    def test_own_lobby_transport_fragmentation(self):
        from panama_stream import Panama
        import gateway_protocol as gateway
        keys = tuple(bytes([i])*64 for i in range(1,5))
        cid = 123
        client_random, server_random = bytes([5])*32, bytes([6])*32
        challenge = bytes([7])*32
        probe.REFERRALS[cid] = keys
        try:
            inbound_key = probe.lobby_hmac(keys[3], server_random, client_random)
            offer = b'\x01\x00' + struct.pack('<II',1,gateway.BOOTSTRAP_HASH)
            payload = b'\x02SECRET123'  # author follow-on fixture; omitted from logs
            framed = gateway.frame(offer) + gateway.frame(gateway.READY) + gateway.frame(gateway.HEARTBEAT) + gateway.frame(payload)
            client = (probe.LOBBY_CLIENT_HELLO + struct.pack('<Q',cid) + client_random
                      + struct.pack('<Q',1) + probe.lobby_hmac(keys[0], client_random, server_random)
                      + Panama(inbound_key,inbound_key).apply(framed))
            conn, log = Fragmented(client), io.StringIO()
            credential = bytes([9])*256
            with mock.patch.object(probe.os, 'urandom', side_effect=[challenge,server_random]), mock.patch.object(probe.time, 'sleep'):
                probe.serve_lobby(conn, ('127.0.0.1',1), 1, log, credential=credential, gateway_reply='ack')
            self.assertTrue(conn.closed)
            self.assertIn('client_proof_valid=True', log.getvalue())
            self.assertIn('body_bytes=10 first_byte=2', log.getvalue())
            self.assertIn('gateway negotiation acknowledgement received', log.getvalue())
            self.assertNotIn('SECRET', log.getvalue())
            self.assertEqual(len(conn.sent), 17+65+32+292+5+5)
            outbound_key = probe.lobby_hmac(keys[2], client_random, server_random)
            packet = Panama(outbound_key,outbound_key).apply(conn.sent[17+65+32:])
            self.assertEqual(packet[:256], credential)
            self.assertEqual(packet[256:292], struct.pack('<QQQQI',1,1,cid,1,0))
            self.assertEqual(packet[292:], gateway.frame(gateway.READY) + gateway.frame(gateway.HEARTBEAT))
            self.assertIn('gateway heartbeat exchanged', log.getvalue())
        finally:
            probe.REFERRALS.pop(cid,None)

    def test_lobby_frame_bounds_and_truncation(self):
        for prefix in (b'\0\0\0', b'\xff\xff\xff'):
            with self.assertRaises(ValueError): probe.read_lobby_frame(Fragmented(prefix))
        for packet in (b'\0\0', b'\0\0\x02x'):
            with self.assertRaises(EOFError): probe.read_lobby_frame(Fragmented(packet))

    def test_gateway_offer_validation(self):
        import gateway_protocol as gateway
        offer = b'\x01\x00' + struct.pack('<II',1,gateway.BOOTSTRAP_HASH)
        self.assertEqual(gateway.offer_response(offer), b'\x01\x02')
        for packet in (b'', b'\x01\x02', b'\x01\x00'+struct.pack('<I',0), offer+b'x',
                       b'\x01\x00'+struct.pack('<III',2,gateway.BOOTSTRAP_HASH,gateway.BOOTSTRAP_HASH),
                       b'\x01\x00'+struct.pack('<II',257,gateway.BOOTSTRAP_HASH)):
            with self.assertRaises(ValueError): gateway.parse_offer(packet)
        with self.assertRaises(ValueError): gateway.offer_response(b'\x01\x00'+struct.pack('<II',1,123))
        # The catalogue-offer reply mirrors the offered hash list back (what the
        # native state-2 parser consumes), not a 2-byte ack.
        self.assertEqual(gateway.catalogue_offer(offer), offer)
        self.assertEqual(gateway.catalogue_offer(b'\x01\x00'+struct.pack('<II',1,123),(123,)),
                         b'\x01\x00'+struct.pack('<II',1,123))
        with self.assertRaises(ValueError): gateway.catalogue_offer(b'\x01\x00'+struct.pack('<II',1,123))

    def test_gateway_negotiation_reply(self):
        import gateway_protocol as gateway
        offer = b'\x01\x00' + struct.pack('<II',1,gateway.BOOTSTRAP_HASH)
        reply = gateway.negotiation_reply(offer, 0x1122, 0x33)
        self.assertEqual(reply, b'\x01\x01' + struct.pack('<QQI', 0x1122, 0x33, 1)
                         + struct.pack('<IIIII', gateway.BOOTSTRAP_HASH, 1, 5, 3, 0) + b'\x00')
        self.assertEqual(len(reply), 2 + 20 + 21)
        with self.assertRaises(ValueError):
            gateway.negotiation_reply(b'\x01\x00'+struct.pack('<II',1,123), 0, 0)
        with self.assertRaises(ValueError):
            gateway.negotiation_reply(offer, 0, 0, ((gateway.BOOTSTRAP_HASH,1,5,7,0,b''),))

    def test_gateway_catalogue_bounds(self):
        import gateway_protocol as gateway
        catalogue = {'build':104319, 'protocols':[dict(schema_hash=123,first_id=100,end_id=102,flags=2,group=13)]}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'catalogue.json'
            path.write_text(json.dumps(catalogue))
            self.assertEqual(gateway.load_catalogue(path,13),(123,))
            self.assertEqual(gateway.offer_response(b'\x01\x00'+struct.pack('<II',1,123),(123,)),gateway.READY)
            self.assertEqual(gateway.offer_response(b'\x00\x00'+struct.pack('<II',1,123),(123,)),b'\x00\x02')
            self.assertEqual(gateway.heartbeat_response(b'\x00\x03',0),b'\x00\x03')
            self.assertIsNone(gateway.heartbeat_response(b'\x01\x03',0))
            for broken in ({**catalogue,'build':1}, {**catalogue,'protocols':catalogue['protocols']*2},
                           {'build':104319,'protocols':[dict(schema_hash=True,first_id=100,end_id=102,flags=2,group=13)]}):
                path.write_text(json.dumps(broken))
                with self.assertRaises(ValueError): gateway.load_catalogue(path,13)
            path.write_bytes(bytes(65537))
            with self.assertRaises(ValueError): gateway.load_catalogue(path,13)


if __name__ == '__main__': unittest.main()
