"""Experimental plain 20600 referral for an owned loopback instance.

The native handler creates a slot-120 referral job with this profile. That is
not evidence of a game connection or map load. Remaining field semantics and
the instance transport handshake still need verification. No production inputs
or native memory writes are used; every session input is generated locally.
"""
import secrets


INSTANCE_SCHEMA = 0x074dad18
# Container loopback UDP ports of the owned launcher's clients: the single
# (or first pair) client 1119 and the pair mode's second client 1129. Each
# client must be referred to its own container bridge; in the shared pair
# AppContainer a second client referred to 1119 would share the first
# client's bridge source port.
INSTANCE_PORTS = (1119, 1129)


def signed_chars(value, width):
    if len(value)>width:raise ValueError('instance fixed string size')
    return [byte if byte<128 else byte-256 for byte in value.ljust(width,b'\0')]


def local_referral(port=1119):
    """Numeric fields for the demonstrated plain, mapped-loopback profile.

    Outer +0x78 false skips the native conditional payload transform. Host
    +0x2e and port +0x2c are traced by the original '%s:%d' formatter/parser.
    The connection callback parses +0x6e as another IPv4:port endpoint, not a
    token. Both address forms target the owned loopback listener. The instance
    id, +0x10 and two byte vectors are server-local inputs.
    +0x28=2 matches the tested job-creation profile; its meaning is unverified.
    PORT selects the client's own container port from INSTANCE_PORTS; the
    keys are fresh per call, so two clients never share an AES-GCM key.
    """
    if type(port) is not int or port not in INSTANCE_PORTS:
        raise ValueError('instance referral port must be an owned container port')
    record={0:{0:1,8:1},0x10:secrets.randbelow(2**31-1)+1,0x28:2,0x2c:port,
            0x2e:signed_chars(b'127.0.0.1',64),
            0x6e:signed_chars(b'127.0.0.1:%d'%port,64),
            0xae:list(secrets.token_bytes(32)),0xce:list(secrets.token_bytes(32))}
    return {0x78:False,0x80:record}
