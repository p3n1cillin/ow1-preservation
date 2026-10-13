"""Experimental plain 20600 referral for an owned loopback instance.

The native handler creates a slot-120 referral job with this profile. That is
not evidence of a game connection or map load. Remaining field semantics and
the instance transport handshake still need verification. No production inputs
or native memory writes are used; every session input is generated locally.
"""
import secrets


INSTANCE_SCHEMA = 0x074dad18


def signed_chars(value, width):
    if len(value)>width:raise ValueError('instance fixed string size')
    return [byte if byte<128 else byte-256 for byte in value.ljust(width,b'\0')]


def local_referral():
    """Numeric fields for the demonstrated plain, mapped-loopback profile.

    Outer +0x78 false skips the native conditional payload transform. Host
    +0x2e and port +0x2c are traced by the original '%s:%d' formatter/parser.
    The instance id, +0x10, token and two byte vectors are server-local inputs.
    +0x28=2 matches the tested job-creation profile; its meaning is unverified.
    """
    record={0:{0:1,8:1},0x10:secrets.randbelow(2**31-1)+1,0x28:2,0x2c:1119,
            0x2e:signed_chars(b'127.0.0.1',64),
            0x6e:signed_chars(secrets.token_hex(16).encode('ascii'),64),
            0xae:list(secrets.token_bytes(32)),0xce:list(secrets.token_bytes(32))}
    return {0x78:False,0x80:record}
