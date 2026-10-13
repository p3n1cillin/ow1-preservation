"""Opt-in initial lobby identity reply for our single local test account.

20500's native handler installs identities and raises event 13. The numeric
schema is verified; downstream meanings of several fields remain unknown.
Unknown flags/counters stay zero. This is a diagnostic, not a game server.
"""
from gateway_codec import decode, encode

HELLO_SCHEMA = 0x3c7e3468
WELCOME_SCHEMA = 0xf5ff548a
GAME_ACCOUNT_HIGH = (2<<56)|(1<<32)|0x0050726f


class InitialLobby:
    def __init__(self, hashes, messages, battle_tag='Preservation#1001'):
        self.hashes, self.messages = hashes, messages
        self.name = battle_tag.encode('utf-8')
        if not self.name or len(self.name)>128 or b'\0' in self.name:
            raise ValueError('local battle tag length/NUL')
        self.hello_entry=hashes.index(HELLO_SCHEMA)+1
        self.welcome_entry=hashes.index(WELCOME_SCHEMA)+1
        if len(hashes)>255: raise ValueError('unsupported extended protocol entries')
        self.sent=False

    def receive(self, packet):
        if packet[:2]!=bytes((self.hello_entry,0)):return None
        if self.sent:raise ValueError('duplicate initial lobby hello')
        hello=decode(self.messages[HELLO_SCHEMA,21800],packet[2:])
        identity=hello[0xb8][0]
        if hello[0x1bc]!=104319 or identity!={0:1001,8:GAME_ACCOUNT_HIGH}:
            raise ValueError('hello differs from the granted local build/account')
        # Identities from the server's own BGS grant. Third identity is an
        # experimental local persistent id; no existing player data is reused.
        values={0x78:identity,0x88:{0:1001,8:1<<56},0x98:{0:[1001,0]},
                0xa8:self.name,0xd0:b'',0xf8:b'',0x120:b''}
        body=encode(self.messages[WELCOME_SCHEMA,20500],values)
        self.sent=True
        return bytes((self.welcome_entry,0))+body
