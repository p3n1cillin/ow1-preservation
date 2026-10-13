"""Observed client-to-server reliable record block for build 104319.

Only primary records on common channel 1, messages 21610/21627 and the observed
empty trailing modules are supported. Authenticate the datagram before parsing.
Server-to-client bodies have a different prefix; this is not a server encoder.
"""
from dataclasses import dataclass
import struct
from gateway_codec import Reader, encode
from instance_bits import MAX_BODY

COMMON_SCHEMA = 0xa7fbbd0c
COMMON_CHANNEL = 1
COMMON_BASE = 21600
OBSERVED_MESSAGES = (21610, 21627)


@dataclass(frozen=True)
class Record:
    sequence: int
    message_id: int
    values: dict


def _fields(messages, message_id):
    if type(message_id) is not int or message_id not in OBSERVED_MESSAGES:
        raise ValueError('unsupported instance record message')
    try:
        return messages[COMMON_SCHEMA, message_id]
    except KeyError:
        raise ValueError('instance record schema missing') from None


def decode_client_body(body, messages):
    if type(body) is not bytes or not 3 <= len(body) <= MAX_BODY:
        raise ValueError('instance reliable body size/type')
    word = struct.unpack_from('<H', body)[0]
    count = (word >> 1) & 15
    # Native byte I/O aligns after nine bits; its seven padding bits are ignored.
    if not count or (word & 0x1ff) != (1 | (count << 1)):
        raise ValueError('unsupported instance reliable header')
    if body[-1:] != b'\0':
        raise ValueError('unsupported instance trailing modules')
    reader = Reader(body[2:-1])
    records = []
    for _ in range(count):
        sequence, channel, delta = struct.unpack('<IBB', reader.take(6))
        if channel != COMMON_CHANNEL:
            raise ValueError('unsupported instance reliable channel')
        message_id = COMMON_BASE + delta
        records.append(Record(sequence, message_id, reader.fields(_fields(messages, message_id))))
    if reader.pos != len(reader.data):
        raise ValueError('instance reliable trailing data')
    return records


def encode_client_body(records, messages, *, padding=0):
    if type(records) is not list or not 1 <= len(records) <= 15:
        raise ValueError('instance primary record count')
    if type(padding) is not int or not 0 <= padding <= 127:
        raise ValueError('instance reliable padding bound')
    result = bytearray(struct.pack('<H', 1 | (len(records) << 1) | (padding << 9)))
    for record in records:
        if type(record) is not Record or type(record.sequence) is not int or not 0 <= record.sequence <= 0xffffffff:
            raise ValueError('instance reliable record sequence/type')
        fields = _fields(messages, record.message_id)
        result.extend(struct.pack('<IBB', record.sequence, COMMON_CHANNEL, record.message_id - COMMON_BASE))
        result.extend(encode(fields, record.values))
        if len(result) + 1 > MAX_BODY:
            raise ValueError('instance reliable body bound')
    return bytes(result) + b'\0'
