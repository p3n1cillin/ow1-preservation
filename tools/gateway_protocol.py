"""Bounded, demonstrated engine gateway negotiation for final OW1 104319.

Bootstrap protocol 0x11d82194 has message ids 1..4 (m_messageBase 1). Each
packet starts with entry 1 for group 0, or entry 0 for group 13, then one byte
(message id - 1), then the body. id 1 is the initiator's uint32 hash vector,
id 2 the newer-mode record reply, id 3 the accepted empty acknowledgement
for the demonstrated mode, and id 4 an empty heartbeat. No game
state or account bytes are bundled.
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
    # Reply with empty message id 3 (delta 2). The 104319 lobby client
    # initiates with ctx+0x84 bit 0 clear, so its id-3 handler 0x00560370
    # accepts id 3 in state 3 and enters negotiated state 5 (live-verified:
    # the client then sends id-4 heartbeats every 5 s). id 2 is only taken
    # when bit 0 is set (0x00560040), and id 1 needs the responder role.
    return bytes((packet[0],2))


def catalogue_offer(packet, allowed=(BOOTSTRAP_HASH,)):
    """Reply to the client's bootstrap offer with the server's own catalogue
    offer carrying the same resolvable protocol hash list. The client's state-2
    receiver (rva 0x00560040 -> 0x00561890 -> per-record 0x00561730) parses an
    incoming record vector and validates each schema hash against its local
    catalogue (0x00569a70). This sends message id 1, which a mode-1
    initiator rejects (0x005601e0 needs the responder role); kept only as a
    diagnostic control. Live result: the client disconnects immediately.
    """
    hashes = parse_offer(packet)
    if hashes != allowed:
        raise ValueError('gateway offer includes an unsupported protocol')
    return bytes((packet[0], 0)) + struct.pack('<I', len(hashes)) + struct.pack(f'<{len(hashes)}I', *hashes)


# Bootstrap protocol record as registered by the client (catalogue group 0):
# m_protocolCRC, m_messageBase, m_messageMax, m_protocolFlags,
# m_untrustedServer, m_protocolName.
BOOTSTRAP_RECORD = (BOOTSTRAP_HASH, 1, 5, 3, 0, b'')


def negotiation_reply(packet, seq, src, records=(BOOTSTRAP_RECORD,)):
    """Responder id-2 message for the client's id-1 offer.

    Wire form reversed from the native binary (mode-1) serializer: send path
    0x00560d90 writes the protocol entry byte, 0x00568690 writes one byte
    (message id - m_messageBase), then 0x005652b0 walks the field table with
    no tags or length prefixes: nested structs inline, repeated fields as a
    uint32 count + elements, type-6/7 as uint32, type-8 as uint64 and type-12
    strings NUL-terminated (0x00567020 writes strlen+1 bytes). id-2 (field
    table 0x02cf0180) is {seq:u64, src:u64} then a record vector (0x02cf0380).
    Only a context with ctx+0x84 bit 0 set accepts id 2; the 104319 lobby
    client does not (it disconnects on this reply; use offer_response).
    """
    hashes = parse_offer(packet)
    if tuple(record[0] for record in records) != hashes:
        raise ValueError('gateway reply records must match the offered protocols')
    body = bytearray((packet[0], 2 - 1))
    body += struct.pack('<QQI', seq, src, len(records))
    for crc, base, maximum, flags, untrusted, name in records:
        if b'\0' in name or flags & 4:
            raise ValueError('gateway record name/flags unsupported (binary mode only)')
        body += struct.pack('<IIIII', crc, base, maximum, flags, untrusted) + name + b'\0'
    return bytes(body)


def heartbeat_response(packet, channel=1):
    heartbeat = bytes((channel,3))
    return heartbeat if packet == heartbeat else None


def frame(packet):
    if not 0 < len(packet) <= 1024*1024:
        raise ValueError('gateway outgoing packet length bounds')
    return len(packet).to_bytes(3, 'big') + packet
