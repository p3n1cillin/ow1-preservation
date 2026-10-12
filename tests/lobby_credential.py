"""Own-key credential fixtures; no client bytes or keys are bundled."""
import importlib.util
import hmac
from pathlib import Path
import struct
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('credential', Path(__file__).resolve().parents[1] / 'tools/lobby_credential.py')
credential = importlib.util.module_from_spec(spec)
spec.loader.exec_module(credential)
stream_spec = importlib.util.spec_from_file_location('stream', Path(__file__).resolve().parents[1] / 'tools/panama_stream.py')
stream = importlib.util.module_from_spec(stream_spec)
stream_spec.loader.exec_module(stream)


class CredentialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from cryptography.hazmat.primitives.asymmetric import rsa
        cls.key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        cls.numbers = cls.key.private_numbers()

    def test_wire_matches_native_public_op_and_integrity(self):
        integrity = bytes(range(64))  # author fixture, not native material
        wire = credential.build_credential(self.numbers, integrity)
        self.assertEqual(len(wire), 256)
        public = self.numbers.public_numbers
        plain = pow(int.from_bytes(wire, 'little'), public.e, public.n).to_bytes(256, 'little')
        self.assertEqual(plain[:7], b'\x02\x7f\0\0\x01' + struct.pack('<H', 1119))
        self.assertEqual(plain[7:19], bytes(12))
        self.assertEqual(plain[176:208], hmac.digest(integrity, plain[:176] + plain[208:], 'sha256'))
        # Wrong wire byte order must not accidentally produce a valid block.
        other = pow(int.from_bytes(wire, 'big'), public.e, public.n).to_bytes(256, 'little')
        self.assertNotEqual(other, plain)
        tampered = bytearray(plain); tampered[25] ^= 1
        self.assertNotEqual(tampered[176:208], hmac.digest(integrity, tampered[:176] + tampered[208:], 'sha256'))

    def test_inputs_reject_wrong_key_and_nonloopback(self):
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import rsa, ec
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'key.pem'
            for key in (ec.generate_private_key(ec.SECP256R1()),
                        rsa.generate_private_key(public_exponent=65537, key_size=1024),
                        rsa.generate_private_key(public_exponent=3, key_size=2048)):
                path.write_bytes(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
                with self.assertRaises(ValueError): credential.load_key(path)
        for key in (b'', bytes(63), bytes(65)):
            with self.assertRaises(ValueError): credential.build_credential(self.numbers, key)
        for host, port in (('192.168.0.1', 1119), ('127.0.0.1', 0), ('127.0.0.1', 65536)):
            with self.assertRaises(ValueError): credential.address_block(host, port)

    def test_panama_public_reference_vector_and_fragmentation(self):
        # Crypto++ Panama-LE cipher vector (public-domain reference).
        key = bytes(range(32))
        expected = bytes.fromhex('F07F5FF2CCD01A0A7D44ACD6D239C2AF0DA1FF35275BAF5DFA6E09411B79D8B9')
        cipher = stream.Panama(key, key)
        self.assertEqual(cipher.apply(key), expected)
        fragmented = stream.Panama(key, key)
        self.assertEqual(b''.join(fragmented.apply(bytes([v])) for v in key), expected)
        self.assertEqual(stream.Panama(key, key).apply(expected), key)


if __name__ == '__main__': unittest.main()
