"""Written records/strings/blobs only; no original-client fixtures."""
from pathlib import Path
import struct
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from gateway_codec import load_messages
from instance_reliable import Record, decode_client_body, encode_client_body


class InstanceReliableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.messages=load_messages(Path(__file__).resolve().parents[1]/'protocol/instance-common-104319.json')

    def test_written_single_and_multiple_records(self):
        one=bytes.fromhex('0300')+struct.pack('<IBBf',7,1,27,20.0)+b'\0'
        record=Record(7,21627,{0x78:20.0})
        self.assertEqual(decode_client_body(one,self.messages),[record])
        self.assertEqual(encode_client_body([record],self.messages),one)
        clock=Record(9,21610,{0x78:-1,0x80:[100,200]})
        two=bytes.fromhex('0500')+one[2:-1]+struct.pack('<IBBiIQQ',9,1,10,-1,2,100,200)+b'\0'
        self.assertEqual(decode_client_body(two,self.messages),[record,clock])
        self.assertEqual(encode_client_body([record,clock],self.messages),two)

    def test_truncation_and_array_bounds(self):
        packet=encode_client_body([Record(0,21610,{0x78:1,0x80:[2,3]})],self.messages)
        for end in range(len(packet)):
            with self.assertRaises((ValueError,struct.error)):decode_client_body(packet[:end],self.messages)
        bad=bytearray(packet);struct.pack_into('<I',bad,12,0xffffffff)
        with self.assertRaisesRegex(ValueError,'array'):decode_client_body(bytes(bad),self.messages)

    def test_join_record_strings_bits_blob_and_next_record(self):
        values={0x78:b'Fixture',0xa0:7,0xa4:True,0xa5:False,0xa6:True,0xa7:False,
                0xa8:1.25,0xac:9,0xb0:b'a\0b'}
        join=Record(1,21600,values)
        tail=Record(2,21627,{0x78:20.0})
        body=b'\x05\0'+struct.pack('<IBB',1,1,0)+b'Fixture\0'+struct.pack('<IBfII',7,5,1.25,9,3)+b'a\0b'+struct.pack('<IBBf',2,1,27,20.0)+b'\0'
        self.assertEqual(decode_client_body(body,self.messages),[join,tail])
        self.assertEqual(encode_client_body([join,tail],self.messages),body)
        padded=bytearray(body);padded[20]=0xf5
        records=decode_client_body(bytes(padded),self.messages)
        self.assertEqual(records[0],Record(1,21600,values,boolean_padding=15))
        self.assertEqual(encode_client_body(records,self.messages),bytes(padded))
        for padding in (-1,16,True):
            with self.assertRaises(ValueError):encode_client_body([Record(1,21600,values,boolean_padding=padding)],self.messages)
        with self.assertRaises(ValueError):encode_client_body([Record(1,21627,{0x78:1.0},boolean_padding=1)],self.messages)
        for end in range(len(body)):
            with self.assertRaises((ValueError,struct.error)):decode_client_body(body[:end],self.messages)
        bad=bytearray(body);struct.pack_into('<I',bad,29,0xffffffff)
        with self.assertRaisesRegex(ValueError,'blob'):decode_client_body(bytes(bad),self.messages)
        for invalid in ({**values,0x78:b'bad\0name'},{**values,0xa4:1},{**values,0xb0:'text'}):
            with self.assertRaises(ValueError):encode_client_body([Record(1,21600,invalid)],self.messages)

    def test_unsupported_profiles_and_padding(self):
        packet=encode_client_body([Record(0,21627,{0x78:1.0})],self.messages)
        for off,value in ((0,1),(0,2),(0,0x23),(1,1),(6,0),(7,99),(-1,1)):
            bad=bytearray(packet);bad[off]=value
            with self.assertRaises(ValueError):decode_client_body(bytes(bad),self.messages)
        with self.assertRaises(ValueError):decode_client_body(packet[:-1]+b'\0\0',self.messages)
        with self.assertRaises(ValueError):decode_client_body(bytearray(packet),self.messages)
        with self.assertRaises(ValueError):decode_client_body(packet,{})
        padded=bytes.fromhex('03fe')+packet[2:]
        records=decode_client_body(padded,self.messages)
        self.assertEqual(encode_client_body(records,self.messages,padding=127),padded)
        self.assertEqual(encode_client_body(records,self.messages),packet)
        for padding in (-1,128,True):
            with self.assertRaises(ValueError):encode_client_body(records,self.messages,padding=padding)

    def test_record_count_sequence_and_size_limits(self):
        record=Record(0xffffffff,21627,{0x78:0.0})
        body=encode_client_body([record]*15,self.messages)
        self.assertEqual(len(decode_client_body(body,self.messages)),15)
        for records in ([],[record]*16,(record,),[Record(True,21627,{})],
                        [Record(-1,21627,{})],[Record(2**32,21627,{})],[Record(0,21601,{})]):
            with self.assertRaises(ValueError):encode_client_body(records,self.messages)
        huge=Record(0,21610,{0x78:0,0x80:[0]*510})
        with self.assertRaises(ValueError):encode_client_body([huge],self.messages)


if __name__=='__main__':unittest.main()
