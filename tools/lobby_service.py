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
    def __init__(self, hashes, messages, battle_tag='Preservation#1001', initial_data=None):
        self.hashes, self.messages = hashes, messages
        self.name = battle_tag.encode('utf-8')
        if not self.name or len(self.name)>128 or b'\0' in self.name:
            raise ValueError('local battle tag length/NUL')
        self.hello_entry=hashes.index(HELLO_SCHEMA)+1
        self.welcome_entry=hashes.index(WELCOME_SCHEMA)+1
        if len(hashes)>255: raise ValueError('unsupported extended protocol entries')
        self.sent=False
        if initial_data not in (None,'keys','keys-hotfix','keys-hotfix-player'):
            raise ValueError('unsupported initial-data experiment')
        self.initial_data=initial_data
        self.updates_sent=False
        self.initial_ids={None:(),'keys':(20504,),'keys-hotfix':(20504,20505),
                          'keys-hotfix-player':(20504,20505,20502)}[initial_data]
        for mid in self.initial_ids:
            if (WELCOME_SCHEMA,mid) not in messages:raise ValueError('initial-data schema missing')

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
        self.identity=identity
        return bytes((self.welcome_entry,0))+body

    def initial_notifications(self):
        """Server has no additional content keys or hotfix overrides to supply.

        20504's native handler imports entries, then initializes its key-list
        context. 20505 hands four override lists to the content-update receiver.
        Optional 20502 supplies our local player-record experiment.
        These optional packets run those original handlers, not heap writes.
        """
        if not self.sent or self.updates_sent or self.initial_data is None:return ()
        packets=[]
        for mid in self.initial_ids:
            # 20502 runs the native player-record initialization handler.
            # The two identities are the same local experiments as 20500;
            # unverified counters/flags stay zero and the name is our own tag.
            values={0x78:{0:self.identity,0x10:{0:1001,8:1<<56},0x40:self.name}} if mid==20502 else {}
            body=encode(self.messages[WELCOME_SCHEMA,mid],values)
            packets.append((mid,bytes((self.welcome_entry,mid-20500))+body))
        self.updates_sent=True
        return tuple(packets)
