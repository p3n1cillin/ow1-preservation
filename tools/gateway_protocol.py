"""Bounded, demonstrated engine gateway negotiation for final OW1 104319.

Bootstrap message id 1 carries protocol hash 0x11d82194. A one-byte version
delta selects versions 1..4. Version 1 is a little-endian uint32 hash vector;
version 3 acknowledges negotiation. No game state or account bytes are bundled.
"""
import struct
import json

BOOTSTRAP_HASH = 0x11d82194
MAX_HASHES = 256
READY = b'\x01\x02'
HEARTBEAT = b'\x01\x03'


def parse_offer(packet):
    if len(packet) < 6 or packet[0] not in (0,1) or packet[1] != 0:
        raise ValueError('not a gateway bootstrap version-1 offer')
    count = struct.unpack_from('<I', packet, 2)[0]
    if not 0 < count <= MAX_HASHES or len(packet) != 6 + count*4:
        raise ValueError('gateway offer count/length mismatch')
    hashes = struct.unpack_from(f'<{count}I', packet, 6)
    if len(set(hashes)) != count:
        raise ValueError('duplicate gateway protocol hash')
    return hashes


def load_catalogue(path, group):
    with open(path, 'rb') as source:
        data = source.read(65537)
    if len(data) > 65536:
        raise ValueError('gateway catalogue size bound')
    document = json.loads(data)
    if document.get('build') != 104319 or not isinstance(document.get('protocols'), list) or not 0 < len(document['protocols']) <= 256:
        raise ValueError('gateway catalogue build/count')
    result = []
    for item in document['protocols']:
        values = [item.get(key) for key in ('schema_hash','first_id','end_id','flags','group')]
        if any(type(value) is not int for value in values):
            raise ValueError('gateway catalogue numeric field types')
        schema,first,end,flags,namespace = values
        if not 0 < schema <= 0xffffffff or not 0 < first < end <= 65536 or not 0 <= flags <= 0xffffffff or not 0 <= namespace <= 65535:
            raise ValueError('gateway catalogue record bounds')
        if namespace == group:
            result.append(schema)
    if not result or len(set(result)) != len(result):
        raise ValueError('gateway catalogue group missing/duplicated')
    # Native 55f090 sorts the protocol vector by unsigned schema hash.
    return tuple(sorted(result))


def offer_response(packet, allowed=(BOOTSTRAP_HASH,)):
    hashes = parse_offer(packet)
    # Negotiate only this exact registered interface catalogue. Application
    # operations are separate from the catalogue/transport handshake.
    if hashes != allowed:
        raise ValueError('gateway offer includes an unsupported protocol')
    # The initiating mode-1 peer waits in state 3 for version 3. The native
    # mode-2 responder validates this hash list and emits that empty ack;
    # reflecting the version-1 offer back selects the wrong role handler.
    return bytes((packet[0],2))


def heartbeat_response(packet, channel=1):
    heartbeat = bytes((channel,3))
    return heartbeat if packet == heartbeat else None


def frame(packet):
    if not 0 < len(packet) <= 1024*1024:
        raise ValueError('gateway outgoing packet length bounds')
    return len(packet).to_bytes(3, 'big') + packet
