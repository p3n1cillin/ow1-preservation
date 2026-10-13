"""Written sequences, numbers and floats only; no original-client fixtures."""
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
                        [Record(-1,21627,{})],[Record(2**32,21627,{})],[Record(0,21600,{})]):
            with self.assertRaises(ValueError):encode_client_body(records,self.messages)
        huge=Record(0,21610,{0x78:0,0x80:[0]*510})
        with self.assertRaises(ValueError):encode_client_body([huge],self.messages)


if __name__=='__main__':unittest.main()
