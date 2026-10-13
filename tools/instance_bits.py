"""Independent bounded LSB-first primitives for the observed instance body.

The compact u32 selector uses 18, 24 or 32 value bits. These primitives do not
implement module prefixes, message routing, reliable channels or a game session.
"""
MAX_BODY = 4062  # Diagnostic bridge packet bound minus authenticated envelope.


class Reader:
    def __init__(self, data, *, bit_count=None):
        if type(data) is not bytes or len(data) > MAX_BODY:
            raise ValueError('instance bitstream size/type')
        if bit_count is None:
            bit_count = len(data) * 8
        if type(bit_count) is not int or not 0 <= bit_count <= len(data) * 8:
            raise ValueError('instance bitstream length')
        self._bits = int.from_bytes(data, 'little')
        self.bit_count = bit_count
        self.position = 0

    def read(self, width):
        if type(width) is not int or not 0 <= width <= 32:
            raise ValueError('instance bit width')
        if self.position + width > self.bit_count:
            raise ValueError('truncated instance bitstream')
        value = (self._bits >> self.position) & ((1 << width) - 1)
        self.position += width
        return value

    def compact_u32(self):
        if self.read(1):
            return self.read(18)
        if self.read(1):
            return self.read(24)
        return self.read(32)


class Writer:
    def __init__(self):
        self._bits = 0
        self.bit_count = 0

    def write(self, value, width):
        if type(width) is not int or not 0 <= width <= 32:
            raise ValueError('instance bit width')
        if type(value) is not int or not 0 <= value < 1 << width:
            raise ValueError('instance bit value')
        if self.bit_count + width > MAX_BODY * 8:
            raise ValueError('instance bitstream size')
        self._bits |= value << self.bit_count
        self.bit_count += width

    def compact_u32(self, value):
        if type(value) is not int or not 0 <= value <= 0xffffffff:
            raise ValueError('instance compact u32 bound')
        needed = 19 if value < 1 << 18 else 26 if value < 1 << 24 else 34
        if self.bit_count + needed > MAX_BODY * 8:
            raise ValueError('instance bitstream size')
        if value < 1 << 18:
            self.write(1, 1)
            self.write(value, 18)
        elif value < 1 << 24:
            self.write(2, 2)
            self.write(value, 24)
        else:
            self.write(0, 2)
            self.write(value, 32)

    def finish(self):
        return self._bits.to_bytes((self.bit_count + 7) // 8, 'little')
