"""Opt-in initial lobby identity reply for our single local test account.

20500's native handler installs identities and raises event 13. The numeric
schema is verified; downstream meanings of several fields remain unknown.
Unknown flags/counters stay zero. This is a diagnostic, not a game server.
"""
from gateway_codec import decode, encode
from instance_referral import INSTANCE_SCHEMA, local_referral

HELLO_SCHEMA = 0x3c7e3468
WELCOME_SCHEMA = 0xf5ff548a
PROFILE_SCHEMA = 0x1a9879a4
PARTY_SCHEMA = 0x2411de56  # 20700 party state (handler 0x008529a0 -> component slot 20)
QUEUE_SCHEMA = 0xa6e53896   # client game-queue requests (24000-24028)
QUEUE_REPLY_SCHEMA = 0x21286b49  # server game-queue messages (23300-23333)
SOCIAL_SCHEMA = 0x75d32ae2  # client requests; 22206 = view a player's profile
GAME_ACCOUNT_HIGH = (2<<56)|(1<<32)|0x0050726f


class InitialLobby:
    def __init__(self, hashes, messages, battle_tag='Preservation#1001', initial_data=None, account_id=1001,
                 queue_reply=None, instance_referral=False):
        self.hashes, self.messages = hashes, messages
        self.name = battle_tag.encode('utf-8')
        if not self.name or len(self.name)>128 or b'\0' in self.name:
            raise ValueError('local battle tag length/NUL')
        if type(account_id) is not int or not 1<=account_id<2**32:raise ValueError('local account id bounds')
        self.account_id=account_id
        if queue_reply is not None:
            if type(queue_reply) is not int or not 23300<=queue_reply<23334:
                raise ValueError('queue reply experiment id bounds')
            if (QUEUE_REPLY_SCHEMA not in hashes or QUEUE_SCHEMA not in hashes
                    or (QUEUE_REPLY_SCHEMA,queue_reply) not in messages or (QUEUE_SCHEMA,24000) not in messages):
                raise ValueError('queue reply experiment needs registered request/reply schemas')
        self.queue_reply=queue_reply
        if type(instance_referral) is not bool:raise ValueError('instance experiment must be boolean')
        if instance_referral and (queue_reply is not None or INSTANCE_SCHEMA not in hashes
                or QUEUE_SCHEMA not in hashes or (INSTANCE_SCHEMA,20600) not in messages
                or (QUEUE_SCHEMA,24000) not in messages):
            raise ValueError('instance experiment requires its registered schemas and no queue-reply experiment')
        self.instance_referral=instance_referral
        self.hello_entry=hashes.index(HELLO_SCHEMA)+1
        self.welcome_entry=hashes.index(WELCOME_SCHEMA)+1
        if len(hashes)>255: raise ValueError('unsupported extended protocol entries')
        self.sent=False
        if initial_data not in (None,'keys','keys-hotfix','keys-hotfix-player','keys-hotfix-player-settings','full'):
            raise ValueError('unsupported initial-data experiment')
        self.initial_data=initial_data
        self.updates_sent=False
        self.initial_ids={None:(),'keys':(20504,),'keys-hotfix':(20504,20505),
                          'keys-hotfix-player':(20504,20505,20502),
                          'keys-hotfix-player-settings':(20504,20505,20502,20802),
                          'full':(20504,20505,20502,20802,20700)}[initial_data]
        for mid in self.initial_ids:
            if (self.schema_of(mid),mid) not in messages:raise ValueError('initial-data schema missing')

    @staticmethod
    def schema_of(mid):
        if 20800<=mid<20826: return PROFILE_SCHEMA
        if 20700<=mid<20713: return PARTY_SCHEMA
        return WELCOME_SCHEMA

    def receive(self, packet):
        if packet[:2]!=bytes((self.hello_entry,0)):return None
        if self.sent:raise ValueError('duplicate initial lobby hello')
        hello=decode(self.messages[HELLO_SCHEMA,21800],packet[2:])
        identity=hello[0xb8][0]
        if hello[0x1bc]!=104319 or identity!={0:self.account_id,8:GAME_ACCOUNT_HIGH}:
            raise ValueError('hello differs from the granted local build/account')
        # Identities from the server's own BGS grant. Third identity is an
        # experimental local persistent id; no existing player data is reused.
        values={0x78:identity,0x88:{0:self.account_id,8:1<<56},0x98:{0:[self.account_id,0]},
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
            # 20802 (account preferences, handler 0x7793a0) is sent with every
            # list empty and every flag/byte at its zero default.
            player={0:self.identity,0x10:{0:self.account_id,8:1<<56},0x40:self.name}
            values={0x78:player} if mid==20502 else {}
            if mid==20700:
                # A party of one: our player as the only member (status 5 =
                # "Member", +0xe2 Leader true; field meanings from the client's
                # own party printer 0x008511b2). Party id = the game account.
                values={0x78:{0x00:[{0x00:player,0xe0:5,0xe2:True}],0x60:self.identity}}
            schema=self.schema_of(mid)
            body=encode(self.messages[schema,mid],values)
            base={PROFILE_SCHEMA:20800,PARTY_SCHEMA:20700}.get(schema,20500)
            packets.append((mid,bytes((self.hashes.index(schema)+1,mid-base))+body))
        self.updates_sent=True
        return tuple(packets)

    def answer(self, packet):
        """Reply to a client request after login, or None if not handled.

        22206 (protocol 0x75d32ae2, built by 0x00773f00) asks for a player's
        profile: {target id, related id, i32}. 20807 (handler 0x00779280) with
        its +0x88 flag false carries an inline profile record that 0x00ba48a0
        files under the record's +0x100 id. We send that id with every list,
        counter and string empty: no stats or progress are invented.
        Training experiments are explicit: either one empty queue-family
        notification or a plain loopback instance referral. Neither supplies
        a working game server or proves a correct matchmaking reply sequence.
        """
        if not self.sent:
            return None
        if ((self.queue_reply is not None or self.instance_referral) and QUEUE_SCHEMA in self.hashes
                and packet[:2] == bytes((self.hashes.index(QUEUE_SCHEMA)+1, 0))):
            # Diagnostic only: select one 23300-family default notification or
            # the demonstrated plain 20600 referral profile. Decode the
            # entire request before replying and restrict this experiment to
            # the observed Training modes; no matchmaking result is invented.
            request = decode(self.messages[QUEUE_SCHEMA,24000],packet[2:])
            if request[0x78] not in (2,3) or request[0x80] or request[0xa8]!=4:
                return None
            if self.instance_referral:
                body=encode(self.messages[INSTANCE_SCHEMA,20600],local_referral())
                return 20600,bytes((self.hashes.index(INSTANCE_SCHEMA)+1,0))+body
            mid = self.queue_reply
            body = encode(self.messages[QUEUE_REPLY_SCHEMA, mid], {})
            return mid, bytes((self.hashes.index(QUEUE_REPLY_SCHEMA)+1, mid-23300))+body
        if SOCIAL_SCHEMA not in self.hashes:
            return None
        if packet[:2] != bytes((self.hashes.index(SOCIAL_SCHEMA)+1, 22206-22200)):
            return None
        if (SOCIAL_SCHEMA,22206) not in self.messages or (PROFILE_SCHEMA,20807) not in self.messages:
            return None
        request = decode(self.messages[SOCIAL_SCHEMA,22206], packet[2:])
        target = request[0x78]
        if not any(target.values()):
            raise ValueError('profile request without a player id')
        body = encode(self.messages[PROFILE_SCHEMA,20807], {0x78:target, 0x88:False, 0x90:{0x100:target}})
        return 20807, bytes((self.hashes.index(PROFILE_SCHEMA)+1, 20807-20800))+body

    # Client request families we decode for the log but do not answer yet.
    OBSERVED = {QUEUE_SCHEMA: 24000}

    def describe(self, packet):
        """Short decoded summary of a known, unanswered client request (or None)."""
        if len(packet) < 2 or not 1 <= packet[0] <= len(self.hashes):
            return None
        schema = self.hashes[packet[0]-1]
        base = self.OBSERVED.get(schema)
        if base is None or (schema, base+packet[1]) not in self.messages:
            return None
        values = decode(self.messages[schema, base+packet[1]], packet[2:])
        shown = {hex(k): (v[:40] if isinstance(v, bytes) else v) for k, v in values.items()}
        return f'{base+packet[1]} {shown}'
