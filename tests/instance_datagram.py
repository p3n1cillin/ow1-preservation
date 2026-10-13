"""Author-written keys/packets only; no client captures or private inputs."""
from pathlib import Path
import struct
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from instance_datagram import Header, MAX_PACKET, OVERHEAD, ReceiptWindow, open_packet, seal


class InstanceDatagramTests(unittest.TestCase):
    key=bytes(range(32))

    def test_known_envelope_layout_and_independent_cipher(self):
        header=Header(0,0,flags=1)
        # Written positional header: version2/type0, seq0, next0, bitmap0, flags1.
        aad=bytes.fromhex('200000000000000000000000000000000000000001ad')
        c=Cipher(algorithms.AES(self.key),modes.GCM(bytes(12))).encryptor()
        c.authenticate_additional_data(aad);self.assertEqual(c.finalize(),b'')
        packet=seal(self.key,header)
        self.assertEqual(packet,c.tag[:12]+aad)
        self.assertEqual(open_packet(self.key,packet),(header,b''))

    def test_payload_direction_and_prefix(self):
        header=Header(1,0xffffffff,19,0x8000000000000001,3)
        for payload in (b'',b'author fixture\0payload',bytes(MAX_PACKET-OVERHEAD)):
            for prefix in (bytes(8),b'fixture1'):
                packet=seal(self.key,header,payload,nonce_prefix=prefix)
                self.assertEqual(open_packet(self.key,packet,nonce_prefix=prefix),(header,payload))
                with self.assertRaises(InvalidTag):open_packet(bytes(reversed(self.key)),packet,nonce_prefix=prefix)
                with self.assertRaises(InvalidTag):open_packet(self.key,packet,nonce_prefix=b'wrong123')

    def test_every_byte_is_authenticated(self):
        packet=seal(self.key,Header(1,5,8,15,3),b'own synthetic body')
        for i in range(len(packet)):
            altered=bytearray(packet);altered[i]^=1
            with self.assertRaises(InvalidTag):open_packet(self.key,bytes(altered))

    def test_truncation_and_size_bounds(self):
        packet=seal(self.key,Header(1,2),b'own body')
        for size in range(len(packet)):
            with self.assertRaises((ValueError,InvalidTag)):open_packet(self.key,packet[:size])
        with self.assertRaises(ValueError):seal(self.key,Header(0,0),bytes(MAX_PACKET-OVERHEAD+1))
        with self.assertRaises(ValueError):open_packet(self.key,bytes(MAX_PACKET+1))
        with self.assertRaises(ValueError):open_packet(self.key,bytearray(packet))

    def test_header_and_key_guards(self):
        for header in (Header(True,0),Header(16,0),Header(0,-1),Header(0,2**32),
                       Header(0,0,next_sequence=2**32),Header(0,0,receipt_bitmap=2**64),Header(0,0,flags=256)):
            with self.assertRaises(ValueError):seal(self.key,header)
        for key in (b'',bytes(31),bytes(33),bytearray(self.key)):
            with self.assertRaises(ValueError):seal(key,Header(0,0))
        with self.assertRaises(ValueError):seal(self.key,Header(0,0),nonce_prefix=b'bad')

    def test_authenticated_unsupported_envelope(self):
        for word,magic in ((0x30,0xad),(0x20,0)):
            aad=struct.pack('<IIIQBB',word,0,0,0,0,magic)
            c=Cipher(algorithms.AES(self.key),modes.GCM(bytes(12))).encryptor()
            c.authenticate_additional_data(aad);c.finalize()
            with self.assertRaisesRegex(ValueError,'unsupported'):open_packet(self.key,c.tag[:12]+aad)

    def test_receipts_gaps_and_duplicates(self):
        window = ReceiptWindow()
        # Receipts 0, 2, 3: bitmap bits mark sequence 3, 2, gap at 1, then 0.
        for sequence, expected in ((0, (1, 1)), (2, (3, 5)), (3, (4, 11))):
            self.assertTrue(window.record(sequence))
            self.assertEqual((window.next_sequence, window.bitmap), expected)
        for sequence in (0, 1, 2, 3, 0x80000004):
            self.assertFalse(window.record(sequence))
            self.assertEqual((window.next_sequence, window.bitmap), (4, 11))
        for sequence in (-1, True, 0xffffffff, 2**32):
            with self.assertRaises(ValueError): window.record(sequence)

    def test_receipt_window_boundary(self):
        window = ReceiptWindow()
        window.record(0)
        window.record(63)
        self.assertEqual((window.next_sequence, window.bitmap), (64, (1 << 63) | 1))
        window.record(127)
        self.assertEqual((window.next_sequence, window.bitmap), (128, 1))
        # Receipt bitmap bit index = next_sequence - 1 - acknowledged sequence.
        packet = seal(self.key, Header(0, 1, window.next_sequence, window.bitmap, 2))
        header, payload = open_packet(self.key, packet)
        self.assertEqual((header.next_sequence, header.receipt_bitmap, payload), (128, 1, b''))


if __name__=='__main__':unittest.main()
