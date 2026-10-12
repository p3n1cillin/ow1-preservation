"""Panama-LE compatibility for the local legacy lobby transport.

Independent Python formulation of the Panama state/buffer operations described
by Wei Dai's public-domain Crypto++ reference:
https://github.com/weidai11/cryptopp/blob/master/panama.cpp
This legacy cipher is used solely to interoperate with the owned client.
"""
import struct


MASK = 0xffffffff


def rotate(value, count):
    value &= MASK
    return ((value << count) | (value >> ((32-count) % 32))) & MASK


class Panama:
    def __init__(self, key, iv=None):
        if len(key) != 32 or (iv is not None and len(iv) != 32):
            raise ValueError('Panama requires 32-byte key and IV')
        self.state = [0]*17
        self.buffer = [[0]*8 for _ in range(32)]
        self.position = 0
        self.pending = b''
        self.step(struct.unpack('<8I', key))
        self.step(struct.unpack('<8I', iv if iv is not None else bytes(32)))
        for _ in range(32):
            self.step()

    def step(self, push=None):
        a = self.state
        output = struct.pack('<8I', *a[9:17])
        b4 = self.buffer[(self.position-4) % 32][:]
        b16 = self.buffer[(self.position+16) % 32][:]
        self.position = (self.position+1) % 32
        b0 = self.buffer[self.position]
        b25 = self.buffer[(self.position-25) % 32]
        incoming = push if push is not None else a[1:9]
        for i in range(8):
            old = b0[i]
            b0[i] ^= incoming[i]
            b25[(i+6) % 8] ^= old
        c = [0]*17
        for i in range(17):
            target = (5*i) % 17
            c[target] = rotate(a[i] ^ (a[(i+1) % 17] | ~a[(i+2) % 17]), target*(target+1)//2 % 32)
        injections = [1] + list(push if push is not None else b4) + b16
        self.state = [(c[i] ^ c[(i+1) % 17] ^ c[(i+4) % 17] ^ injections[i]) & MASK for i in range(17)]
        return output

    def apply(self, data):
        output = bytearray()
        for value in data:
            if not self.pending:
                self.pending = self.step()
            output.append(value ^ self.pending[0])
            self.pending = self.pending[1:]
        return bytes(output)
