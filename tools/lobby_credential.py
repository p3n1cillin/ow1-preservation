"""Own-server credential experiment for final OW1; contains no embedded keys.

This is the client's legacy raw RSA block format, not a general signing API.
Only an operator's RSA-2048/e=65537 private key is accepted. The client-specific
integrity constant is read locally from an owned dump, never included in source.
"""
import argparse
import hmac
import ipaddress
from pathlib import Path
import struct


def load_key(path):
    from cryptography.hazmat.primitives.serialization import load_pem_private_key
    from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
    with open(path, 'rb') as source:
        data = source.read(16385)
    if len(data) > 16384:
        raise ValueError('private key exceeds size bound')
    key = load_pem_private_key(data, password=None)
    if not isinstance(key, RSAPrivateKey) or key.key_size != 2048:
        raise ValueError('credential requires an own RSA-2048 key')
    numbers = key.private_numbers()
    if numbers.public_numbers.e != 65537:
        raise ValueError('credential requires e=65537')
    return numbers


def load_integrity(path):
    with open(path, 'rb') as source:
        data = source.read(65)
    if len(data) != 64:
        raise ValueError('credential integrity key must be 64 bytes')
    return data


def address_block(host, port):
    address = ipaddress.IPv4Address(host)
    if not address.is_loopback or not 0 < port <= 65535:
        raise ValueError('credential experiment requires a loopback peer')
    # Native address reader: type 2, uint32 IPv4, uint16 port. The address
    # region has a fixed 19-byte envelope; unused bytes remain zero.
    return b'\x02' + address.packed + struct.pack('<H', port) + bytes(12)


def build_credential(numbers, integrity_key, host='127.0.0.1', port=1119):
    if len(integrity_key) != 64:
        raise ValueError('credential integrity key must be 64 bytes')
    block = bytearray(256)
    block[:19] = address_block(host, port)
    message = bytes(block[:176] + block[208:])
    block[176:208] = hmac.digest(integrity_key, message, 'sha256')
    n = numbers.public_numbers.n
    value = int.from_bytes(block, 'little')
    if value >= n:
        raise ValueError('credential block exceeds own modulus')
    wire = pow(value, numbers.d, n).to_bytes(256, 'little')
    # Check the actual serialized wire block with the matching public key.
    recovered = pow(int.from_bytes(wire, 'little'), 65537, n).to_bytes(256, 'little')
    if recovered != block:
        raise ValueError('own credential RSA roundtrip failed')
    return wire


def extract_integrity(dump_path):
    import importlib.util
    spec = importlib.util.spec_from_file_location('local_mdump', Path(__file__).parent / 'offline-launch/re/mdump.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    dump = module.Dump(dump_path)
    try:
        # Exact native verifier call-site: key length 64, RIP-relative key.
        site = dump.read(dump.image_base + 0x1909012, 13)
        if site != bytes.fromhex('41b840000000488d15113fe800'):
            raise ValueError('dump does not match final credential verifier')
        data = dump.read(dump.image_base + 0x278cf30, 64)
        if len(data) != 64:
            raise ValueError('dump lacks native credential integrity input')
        return data
    finally:
        dump.f.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--private-key', required=True)
    parser.add_argument('--public-modulus-out', required=True)
    parser.add_argument('--integrity-dump', required=True)
    parser.add_argument('--integrity-out', required=True)
    args = parser.parse_args()
    numbers = load_key(args.private_key)
    integrity = extract_integrity(args.integrity_dump)
    build_credential(numbers, integrity)
    # Exclusive creation prevents accidentally overwriting an existing key.
    with open(args.public_modulus_out, 'xb') as output:
        output.write(numbers.public_numbers.n.to_bytes(256, 'little'))
    with open(args.integrity_out, 'xb') as output:
        output.write(integrity)
    print('Own public modulus exported; local integrity input extracted; RSA roundtrip passed.')


if __name__ == '__main__':
    main()
