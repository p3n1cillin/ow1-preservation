"""Independent codec for the observed 104319 instance datagram envelope.

Uses caller-supplied local AES-256 keys. This codec authenticates the envelope;
it does not implement peer state, reliable delivery, game messages or gameplay.
The sender must never reuse a sequence/nonce with the same directional key.
"""
from dataclasses import dataclass
import struct
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

MAX_PACKET = 4096
HEADER = struct.Struct('<IIIQBB')
TAG_SIZE = 12
OVERHEAD = TAG_SIZE + HEADER.size


@dataclass(frozen=True)
class Header:
    packet_type: int
    sequence: int
    next_sequence: int = 0
    receipt_bitmap: int = 0
    flags: int = 0

    def pack(self):
        for name, value, limit in (
            ('type', self.packet_type, 15), ('sequence', self.sequence, 0xffffffff),
            ('next sequence', self.next_sequence, 0xffffffff),
            ('receipt bitmap', self.receipt_bitmap, 0xffffffffffffffff),
            ('flags', self.flags, 255)):
            if type(value) is not int or not 0 <= value <= limit:
                raise ValueError(f'instance {name} bound')
        return HEADER.pack(0x20 | self.packet_type, self.sequence,
                           self.next_sequence, self.receipt_bitmap, self.flags, 0xad)


class ReceiptWindow:
    """Observed forward-only receive window for bounded diagnostic peers.

    Bit zero acknowledges next_sequence-1; older packets are not inserted.
    Sequence wrap is rejected so a diagnostic cannot silently reuse a nonce.
    Call record only after authenticating a packet from the selected peer.
    """

    def __init__(self):
        self.next_sequence = 0
        self.bitmap = 0

    def record(self, sequence):
        if type(sequence) is not int or not 0 <= sequence < 0xffffffff:
            raise ValueError('instance receive sequence bound or wrap')
        gap = sequence - self.next_sequence
        if gap < 0 or gap >= 0x80000000:
            return False
        shift = gap + 1
        self.bitmap = 1 if shift >= 64 else ((self.bitmap << shift) | 1) & 0xffffffffffffffff
        self.next_sequence = sequence + 1
        return True


def _inputs(key, prefix):
    if type(key) is not bytes or len(key) != 32:
        raise ValueError('instance AES-256 key requires 32 bytes')
    if type(prefix) is not bytes or len(prefix) != 8:
        raise ValueError('instance nonce prefix requires 8 bytes')


def seal(key, header, payload=b'', *, nonce_prefix=bytes(8)):
    _inputs(key, nonce_prefix)
    if type(header) is not Header:
        raise ValueError('instance header required')
    if type(payload) is not bytes or len(payload) > MAX_PACKET - OVERHEAD:
        raise ValueError('instance payload bound')
    aad = header.pack()
    cipher = Cipher(algorithms.AES(key), modes.GCM(nonce_prefix + struct.pack('<I', header.sequence))).encryptor()
    cipher.authenticate_additional_data(aad)
    ciphertext = cipher.update(payload) + cipher.finalize()
    return cipher.tag[:TAG_SIZE] + aad + ciphertext


def open_packet(key, packet, *, nonce_prefix=bytes(8)):
    """Authenticate before returning any header fields or plaintext payload.

    InvalidTag from cryptography is preserved on authentication failure.
    Packet sequence is used only to build the nonce until authentication passes.
    """
    _inputs(key, nonce_prefix)
    if type(packet) is not bytes or not OVERHEAD <= len(packet) <= MAX_PACKET:
        raise ValueError('instance packet bound')
    aad = packet[TAG_SIZE:OVERHEAD]
    word, sequence, next_sequence, bitmap, flags, magic = HEADER.unpack(aad)
    cipher = Cipher(algorithms.AES(key), modes.GCM(
        nonce_prefix + struct.pack('<I', sequence), packet[:TAG_SIZE], min_tag_length=TAG_SIZE)).decryptor()
    cipher.authenticate_additional_data(aad)
    payload = cipher.update(packet[OVERHEAD:]) + cipher.finalize()
    if word >> 4 != 2 or magic != 0xad:
        raise ValueError('unsupported instance envelope')
    return Header(word & 15, sequence, next_sequence, bitmap, flags), payload
