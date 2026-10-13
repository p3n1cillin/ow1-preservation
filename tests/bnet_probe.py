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
                probe.serve_lobby(conn, ('127.0.0.1',1), 1, log, credential=credential)
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
