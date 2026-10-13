# OW1 1.74.0.0.104319 bgs RPC protocol reference

Derived interface description (service hashes, method ids, message field numbers)
for the Battle.net "bgs" RPC the retail client speaks, so our independent
preservation server can answer it. Extracted from the protobuf reflection
descriptors embedded in the client (startup-wait.dmp), the same way open-source
bgs server projects document the protocol. This file is an interface spec only:
no client code, assets, keys, or credentials. Do not add proprietary bytes here.

Transport: TLS 1.2 -> WebSocket (`Sec-WebSocket-Protocol: v1.rpc.battle.net`).
Each WebSocket binary message = `[u16-BE header length][Header][body]`.
Header fields observed on the wire: f1 service_id (0 under bindless RPC),
f2 method_id, f3 token, f11 service_hash (fixed32). Responses use service_id
0xFE and echo the request token. Services are addressed by hash (the client
sets `use_bindless_rpc=true` in ConnectRequest, so there is no id binding).

Method-id note: ids below come from the `(method_options).id` option. The ones
exercised so far (Connect=1, Logon=1, OnLogonComplete=5) are byte-verified; a few
others may be approximate where the option parse was ambiguous.

```proto
# OW1 1.74.0.0.104319 bgs protocol schema, extracted from the client's embedded
# descriptors (startup-wait.dmp). Service hashes are FNV-1a 32 of the legacy
# bnet.protocol.* names. Method ids are the (method_options).id option (field 90000).

// ConnectionService: hash 0x65446991  (bnet.protocol.connection.ConnectionService)
// AuthenticationService: hash 0x0decfc01  (bnet.protocol.authentication.AuthenticationServer)
// AuthenticationListener: hash 0x71240e35  (bnet.protocol.authentication.AuthenticationClient)

service ConnectionService {  // hash = FNV-1a of bnet.protocol legacy name
  rpc Connect = 1; // ConnectRequest -> ConnectResponse
  rpc Bind = 1; // BindRequest -> BindResponse
  rpc Echo = 3; // EchoRequest -> EchoResponse
  rpc ForceDisconnect = 4; // DisconnectNotification -> NO_RESPONSE
  rpc KeepAlive = 5; // NoData -> NO_RESPONSE
  rpc Encrypt = 1; // EncryptRequest -> NoData
  rpc RequestDisconnect = 7; // DisconnectRequest -> NO_RESPONSE
}

service AuthenticationService {  // hash = FNV-1a of bnet.protocol legacy name
  rpc Logon = 1; // LogonRequest -> NoData
  rpc VerifyWebCredentials = 7; // VerifyWebCredentialsRequest -> NoData
  rpc GenerateWebCredentials = 8; // GenerateWebCredentialsRequest -> GenerateWebCredentialsResponse
}

service AuthenticationListener {  // hash = FNV-1a of bnet.protocol legacy name
  rpc OnServerStateChange = 4; // ServerStateChangeRequest -> NO_RESPONSE
  rpc OnLogonComplete = 5; // LogonResult -> NO_RESPONSE
  rpc OnLogonUpdate = 10; // LogonUpdateRequest -> NO_RESPONSE
  rpc OnVersionInfoUpdated = 11; // VersionInfoNotification -> NO_RESPONSE
  rpc OnLogonQueueUpdate = 12; // LogonQueueUpdateRequest -> NO_RESPONSE
  rpc OnLogonQueueEnd = 13; // NoData -> NO_RESPONSE
}

message ConnectRequest {
  optional message .bgs.protocol.ProcessId client_id = 1;
  optional message .bgs.protocol.connection.v1.BindRequest bind_request = 2;
  optional bool use_bindless_rpc = 3;
  optional enum .bgs.protocol.connection.v1.MeteringLevel metering_level = 4;
  optional message .bgs.protocol.connection.v1.ClientSdkVersionInfo client_sdk_info = 5;
}

message ConnectResponse {
  required message .bgs.protocol.ProcessId server_id = 1;
  optional message .bgs.protocol.ProcessId client_id = 2;
  optional uint32 bind_result = 3;
  optional message .bgs.protocol.connection.v1.BindResponse bind_response = 4;
  optional message .bgs.protocol.connection.v1.ConnectionMeteringContentHandles content_handle_array = 5;
  optional uint64 server_time = 6;
  optional bool use_bindless_rpc = 7;
  optional message .bgs.protocol.connection.v1.ConnectionMeteringContentHandles binary_content_handle_array = 8;
  optional string ciid = 9;
}

message BindRequest {
  repeated fixed32 deprecated_imported_service_hash = 1;
  repeated message .bgs.protocol.connection.v1.BoundService deprecated_exported_service = 2;
  repeated message .bgs.protocol.connection.v1.BoundService exported_service = 3;
  repeated message .bgs.protocol.connection.v1.BoundService imported_service = 4;
}

message BoundService {
  required fixed32 hash = 1;
  required uint32 id = 2;
}

message ProcessId {
  required uint32 label = 1;
  required uint32 epoch = 2;
}

message ClientSdkVersionInfo {
  optional string sdk_name = 1;
  optional message .bgs.protocol.SemanticVersion sdk_version = 2;
  optional message .bgs.protocol.SemanticVersion protocol_version = 3;
}

message LogonRequest {
  optional string program = 1;
  optional string platform = 2;
  optional string locale = 3;
  optional string email = 4;
  optional string version = 5;
  optional int32 application_version = 6;
  optional bool public_computer = 7;
  optional bool allow_logon_queue_notifications = 10;
  optional bytes cached_web_credentials = 12;
  optional string user_agent = 14;
  optional string device_id = 15;
  optional string phone_number = 16;
}

message LogonResult {
  required uint32 error_code = 1;
  optional message .bgs.protocol.EntityId account_id = 2;
  repeated message .bgs.protocol.EntityId game_account_id = 3;
  optional string email = 4;
  repeated uint32 available_region = 5;
  optional uint32 connected_region = 6;
  optional string battle_tag = 7;
  optional string geoip_country = 8;
  optional bytes session_key = 9;
  optional bool restricted_mode = 10;
  optional string client_id = 11;
}

message EntityId {
  required fixed64 high = 1;
  required fixed64 low = 2;
}

message VerifyWebCredentialsRequest {
  optional bytes web_credentials = 1;
}

message LogonUpdateRequest {
  required uint32 error_code = 1;
}

message ServerStateChangeRequest {
  required uint32 state = 1;
  required uint64 event_time = 2;
}

```

## Logged-in phase: GameUtilities (v2)

Service hash 0x5dbb51c2 = FNV-1a of the service-option name
`bnet.protocol.game_utilities.v2.client.GameUtilities`. ProcessTask = 1,
GetAllValuesForAttribute = 2 (byte-verified option ids).

```proto
// file bgs/low/pb/client/api/client/v2/game_utilities_service.proto  package bgs.protocol.game_utilities.v2.client
message ProcessTaskRequest {
  repeated .bgs.protocol.v2.Attribute attribute = 1;
  repeated .bgs.protocol.v2.Attribute payload = 2;
}
message ProcessTaskResponse {
  repeated .bgs.protocol.v2.Attribute result = 1;
}
message GetAllValuesForAttributeRequest {
  optional string attribute_key = 1;
}
message GetAllValuesForAttributeResponse {
  repeated .bgs.protocol.v2.Variant attribute_value = 1;
}
service GameUtilitiesService {  // options 82f92b360a34626e65742e70726f746f636f6c2e67616d655f7574696c69746965732e76322e636c69656e742e47616d655574696c697469657382f92b102a0e67616d655f7574696c69746965738af92b0210018af92b021801
  rpc ProcessTask(.bgs.protocol.game_utilities.v2.client.ProcessTaskRequest) returns (.bgs.protocol.game_utilities.v2.client.ProcessTaskResponse);  // options 82f92b020801
  rpc GetAllValuesForAttribute(.bgs.protocol.game_utilities.v2.client.GetAllValuesForAttributeRequest) returns (.bgs.protocol.game_utilities.v2.client.GetAllValuesForAttributeResponse);  // options 82f92b020802
}

// file bgs/low/pb/client/api/client/v2/attribute_types.proto  package bgs.protocol.v2
message Variant {
  optional bool bool_value = 1;  // oneof type
  optional int64 int_value = 2;  // oneof type
  optional double float_value = 3;  // oneof type
  optional string string_value = 4;  // oneof type
  optional bytes blob_value = 5;  // oneof type
  optional uint64 uint_value = 6;  // oneof type
}
message Attribute {
  optional string name = 1;
  optional .bgs.protocol.v2.Variant value = 2;
}
message AttributeFilter {
  enum Operation { MATCH_NONE=0, MATCH_ANY=1, MATCH_ALL=2, MATCH_ALL_MOST_SPECIFIC=3 }
  optional .bgs.protocol.v2.AttributeFilter.Operation op = 1;
  repeated .bgs.protocol.v2.Attribute attribute = 2;
}

```

## Game account EntityId (required by the OnLogonComplete success path)

`high = (2 << 56) | (region << 32) | program` with region a nonzero byte and
program = `0x0050726f` ("Pro"); `low` = nonzero game-account id.

## Balancer referral (GameUtilities.ProcessTask)

Request attributes: `service_type="Balancer"`, `request_type="Referral"`,
`version=3`, `build=104319`, `cluster="Pro"`, `platform_available="pc_1"`,
`payload` (empty blob). Response `result` attributes for success:

| name | Variant field | value |
|---|---|---|
| response_type | 4 string | `ReferralInfo` |
| k0, k1, k2, k3 | 5 blob | exactly 64 bytes each |
| cid | 6 uint | connection id the lobby handshake echoes |
| hostv4 | 4 string | `ip:port` of the lobby gateway |

Other response types: `ReferralQueued` (callback_delay, approx_queue_position,
payload), `ReferralError` (error_code, psplus_product_code). All six ReferralInfo
attributes are required; any missing or mistyped one fails the referral.

## Lobby gateway handshake (TCP to hostv4)

Raw bytes, little-endian, one message per send, no framing. CR/SR = 32-byte
client/server randoms.

| # | direction | bytes |
|---|---|---|
| 1 | C->S | `HELLO PRO CLIENT\0` (17) |
| 2 | S->C | `HELLO PRO SERVER\0` (17) |
| 3 | C->S | cid u64, CR (40) |
| 4 | S->C | challenge[32], difficulty u8, SR (65) |
| 5 | C->S | nonce u64, HMAC-SHA256(k0, CR‖SR) (40) |
| 6 | S->C | HMAC-SHA256(k1, SR‖CR) (32) |
| 7 | S->C | Panama-LE encrypted 292-byte packet: RSA credential[256], two identifiers[16] each, metadata uint32 |

nonce: SHA-1(challenge‖nonce_le64) must have >= difficulty low-order zero bits.
Session keys: HMAC-SHA256(k2, CR‖SR), HMAC-SHA256(k3, SR‖CR). Step 7's
decrypted RSA block holds the 19-byte server address and an HMAC-SHA256 at +0xb0
under a client-local integrity input. The input is extracted locally from an
owned dump, never bundled in source. The original trusted modulus requires the
original signing key. Our diagnostic instead installs our own public modulus
and sends a credential issued with the matching own private key.

## Own-key lobby handshake — native verification, 2026-10-13

The wire credential and RSA integers are little-endian. Heap bignums use 74
28-bit limbs for the 2048-bit modulus. The launcher verifies the original
modulus against the client image before replacing its heap digits; its
allocation, exponent, ownership and original verifiers remain intact.

RSA plaintext: 256 bytes, tag at [176:208], HMAC-SHA256 over [0:176] followed
by [208:256]. Address envelope: type byte 2, IPv4 bytes, port uint16 LE,
then zero padding to 19 bytes. Remaining RSA payload bytes are zero in this
experiment. The 36-byte transport suffix comprises two uint64 pairs and one
uint32. Our server assigns (1,1), (cid,1), 0; their application semantics still
need decoding.

After the HMAC(k1) proof, **encryption is already enabled**. Client receive key
= HMAC(k2, CR‖SR), client send key = HMAC(k3, SR‖CR). Each direction uses
Panama-LE with key also used as the 32-byte IV, two pushes and 32 warm-up pulls.
The server encrypts the entire 292-byte packet. Sending only 256 unencrypted
bytes leaves the original transport waiting for its full packet.

The Python implementation is checked against the public-domain
[Crypto++ Panama implementation](https://github.com/weidai11/cryptopp/blob/master/panama.cpp)
and [cipher vector](https://github.com/weidai11/cryptopp/blob/master/TestVectors/panama.txt).
The native transport at RVA 1909547 explicitly waits for 0x124 (292) bytes.
The native verifier path at e39066 performs the original RSA operation and
e39080 checks integrity before e391b9 sets handshake state 6. Two real own-key
runs reach state 6/connection phase 6 and transmit a post-handshake packet.
The original-key control sends no such packet and closes upon our credential.

Post-handshake transport is a continuing Panama stream over packets with a
three-byte big-endian length prefix. The first captured body is 10 bytes and
starts with byte 1: the bootstrap negotiation offer, decoded below together
with its verified `01 02` reply. No main menu, map, hero or gameplay is
established by this handshake.

## Gateway negotiation messages (post-credential, decoded and live-verified)

After the secure channel (peer+0x1053=1) the client runs a message-based
negotiation over the Panama stream. Frames are a 3-byte big-endian length then
the body, in both directions (reader rva 0x0041a100). Every body is:

| bytes | meaning | native |
|---|---|---|
| 1 | protocol entry byte (bootstrap = 1); receiver requires `entry < count` and `entry[0] == byte` | send 0x00560fb6 / receive 0x00561ff0 |
| 0+ | per-entry header (flags at entry+8: optional u32, then 1/2/4/8/16-byte routing value); empty for bootstrap | 0x00561e90 / 0x00561c50 |
| 1 | message id − m_messageBase (bootstrap base 1) | 0x00568690 / 0x00567de0 |
| n | fields from the message's field table, compact binary (mode 1) | writer 0x005652b0 / reader 0x005670e0 |

Compact binary field encoding (entry byte +1 = mode 1; mode 2 is a named/trace
form via 0x003f52e0): no tags or length prefixes; nested structs inline;
repeated fields as u32 count + elements (reader bounds count by remaining
bytes); type 0 is a bit-packed bool; types 1-3 = 1 B, 4-5 = 2 B, 6-7 = 4 B
(including `m_untrustedServer`), 8-9 = 8 B; type 12/13 strings NUL-terminated
(writer 0x00567020 emits strlen+1 bytes); type 14 nested (sub-table).

Bootstrap protocol 0x11d82194, message ids 1..4 (dispatcher 0x0055e980):

| id | wire prefix | handler | meaning |
|---|---|---|---|
| 1 | `01 00` | 0x005601e0 | initiator offer: u32 count + u32 schema hashes; handler needs the responder role (ctx+0x1c == 2) |
| 2 | `01 01` | 0x00560040 | responder record reply `{seq:u64, src:u64}` + record vector (table 0x02cf0380: CRC, base, max, flags, untrusted u32, name NUL-terminated); only accepted when ctx+0x84 bit 0 is set |
| 3 | `01 02` | 0x00560370 | empty completion: bit 0 clear → accepted in state 3; bit 0 set → state 4; then state 5 (negotiated) |
| 4 | `01 03` | 0x0055e9e3 | empty heartbeat; receiver records ctx+0x40 = now |

Captured client offer (10 B): `01 00 | 01 00 00 00 | 94 21 d8 11`. Earlier
notes that read `01 00` as a u16 message id were wrong.

Timers (0x00560b50 / expiry 0x005609c0, seconds from a config struct): in
states 1-4 expiry calls shutdown 0x00561350 (the ~10 s close seen with no or
wrong reply); in state 5 expiry sends an id-4 heartbeat and checks the peer's
heartbeat age.

**Live result (2026-10-13, retail-ack run).** The 104319 lobby client is a
mode-1 initiator with ctx+0x84 bit 0 clear, so the correct reply to its offer
is the empty id 3, `01 02`. With that reply the lobby connection stays
negotiated: the client sends `01 03` every 5 s, the probe echoes it, and the
connection stays open until the bounded run ends (lobby #2: 112 s, 22
heartbeats). Replies of id 1 (echo), the decoded id 2 (`01 01` + 41 B) and the
earlier u16-id candidates all close immediately: id 2 hits the bit-0 check in
0x00560040 and id 1 the role check in 0x005601e0.

Still open: about 60 s after negotiation, while the first lobby stays up, the
client asks GameUtilities for another Balancer referral and opens a second
lobby. The upper layer is therefore still waiting for an application-level
message after the negotiation event (0x00562600 event 0). No main menu,
map, hero or gameplay is established.

## Lobby service protocols (peer group 13, live-verified 2026-10-13)

The client chooses which protocols to offer from the **peer group** in the
gateway peer id (`(id >> 40) & 0xffff`, offer builder 0x00561ac0). For the
lobby, 0x00563410 adopts the server peer id carried in the credential suffix
before emitting the offer. With the probe's credential ids built as
`(13 << 40) | n` (`--lobby-peer-group 13 --gateway-catalogue
protocol/gateway-104319.json`):

- the offer is 350 B on entry 0: all 86 group-13 protocol hashes (exact match
  with the exported catalogue, sorted by unsigned hash);
- `00 02` (id 3) completes negotiation; heartbeats `00 03` follow every 5 s;
- the client immediately sends two application messages on **entry 25**
  (entry n = n-th sorted group-13 protocol, 1-based), protocol **0x3c7e3468**
  (ids 21800-21815): message **21800** (218 B) and **21809** (3 B);
- unlike group 0, the client does not request a new referral during a 112 s run.

Direction: every flag-2 (and flag-10) group-13 protocol has a client receive
dispatcher (rva 0x007a8120-0x007ab630, `id - first_id` switch); flag-1
protocols such as 0x3c7e3468 have none, so they are client-to-server and the
server's replies arrive on flag-2 protocols.

Message 21800 schema (field table rva 0x02cbdc20; field names stripped except
seq/src), decoded from a local capture with all 216 body bytes consumed:

| field | type | observed |
|---|---|---|
| +0x078 | string | empty |
| +0x0a0 | {seq,src} | zero |
| +0x0b0 | i32 | 0 |
| +0x0b8 | struct: {seq,src} account id, 4 x u32, u8[] , 5 x string | game account id as granted at login; platform/locale fourCCs; build 104319; 32-byte zero blob; product `Overwatch/1.74.0.0/104319`; OS description; `PC` |
| +0x1b8, +0x1b9 | bool | false |
| +0x1bc | u32 | 104319 |
| +0x1c0 | i32 | 1 |
| +0x1c8, +0x240, +0x298 | three records (u64/u32 ids, bools, strings, string lists) | empty |

21809 carries one string (empty in the capture). The protocol's other messages
(21801-21815) are small: empty, bool, u32, u64+bool, or one/two strings.
The initial identity reply is now identified and live-tested below. No menu,
map or gameplay is established.

## Initial lobby identity reply (20500, live-verified 2026-10-13)

Server-to-client protocol **0xf5ff548a**, first id 20500, flags 2, group 13.
Its sorted catalogue entry is 83 (verify from the catalogue rather than
hardcoding an index). The wire prefix is the entry byte then delta 0; flags 2
add no routing header. Message descriptor 0x02ca6ca0 points to field table
0x02ca69a0. Dispatcher 0x007a9860 maps 20500 to 0x00774710. That handler calls
0x006261e0, which stores identities/strings in the login context and raises
event 13. This identifies the initial connection reply; it does not establish
every field's original semantic name.

| native offset | compact type | our local experiment |
|---|---|---|
| 0x78, 0x88 | two `{u64,u64}` records | game-account and BGS-account ids from our own grant |
| 0x98 | fixed two-u64 record | local persistent-id experiment `(1001,0)` |
| 0xa8, 0xd0, 0xf8, 0x120 | four NUL-terminated strings | own battle tag, then empty strings |
| 0x148..0x14a | three packed bools | false |
| 0x14c, 0x150 | two i32 | zero |
| 0x154..0x156 | three packed bools | false |

`protocol/lobby-login-104319.json` includes numeric schemas for 21800, 21809
and 20500. It contains no captured payloads, executable bytes or account data.
`tools/gateway_codec.py` implements the bounded compact subset used by these
messages: positional integers, adjacent bool bits, NUL strings, fixed/repeated
arrays and nested records. All **216 body bytes** of the private hello decode
and re-encode exactly. The public tests use author-created fixtures only.

Opt in with `--lobby-login-schema protocol/lobby-login-104319.json`, group 13
and the normal `ack` reply. `InitialLobby` validates the build and exact local
account granted by this diagnostic server, answers once and rejects duplicates.
Unknown flags/counters stay zero; neither game state nor client verdicts are
written. Capture files remain ignored/private and bounded to four packets.
Oversized capture candidates are skipped without closing a valid connection.

Native run `lobby-identity3` sent the **81-byte** reply and continued exchanging
heartbeats until owned shutdown. Direct game-window capture showed
**ENTERING GAME…**. No subsequent application request or main menu appeared.
The next frontier is initial account/configuration delivery and the menu gate;
do not blindly send all registered messages. In particular, 20801's traced
handler only prints account information, so its descriptor alone is insufficient
evidence that sending it will satisfy the initial-data gate.

Two preceding attempts did not exercise this reply: one TLS context ended
before CA retention; a 30-second TLS delay exceeded the client's timeout.
The successful run used the established 15-second delay. Native trust checks
and the original client file remained unchanged.

## Initial key, hotfix and player notifications (2026-10-13)

Three further messages share server protocol 0xf5ff548a (entry 83, no extra
routing header). They are optional experiments, selected with
`--lobby-initial-data keys`, `keys-hotfix` or `keys-hotfix-player`; the normal
identity-only path remains available. The login schema contains their numeric
field descriptors, with no original payloads or executable bytes.

| message | compact body | native receive behavior |
|---|---|---|
| 20504 | u64[] and u8[] | 0x77a560 imports 16-byte key entries via 0x17253f0, then sets the key context's +0x40 flag (context-table slot 10) |
| 20505 | four u64[] | 0x77a000 calls 0x57bba0, which feeds content override lists and balances initialization counters through 0x1719a20/0x1719a60 |
| 20502 | nested record: two 128-bit ids, three u64, two u32, NUL string | 0x7752a0 marks context-table slot 22 at +0x88, updates player-record consumers via 0x619c90/0x619770 and additional login fields |

Our server supplies **no additional keys or hotfix overrides**, so 20504 and
20505 carry empty lists (10 and 18 total packet bytes). The optional 20502
uses our same two local identity experiments, own battle tag, and zero counters
(84 packet bytes for the default tag). Remaining field semantics are unverified.
These packets exercise original receive handlers; no client readiness or
verification result is written by the server/tool.

Native comparisons: `initial-keys1` and `initial-hotfix1` keep heartbeating,
with a black game-window capture and no visible menu. The saved key-context flag
changes **0 -> 1** compared with the identity-only run. `initial-player1`
additionally triggers **60002** (entry 29, schema 0x49963fa6) and repeating
**42600** (entry 80, schema 0xeb45ad29); both observed bodies are two bytes,
entry plus delta. Related server handlers cover migration and tournament data,
but precise request/reply pairings and whether they gate the menu are not yet
established. They are observed without invented replies.

`tools/retail_login_state.py --dump <owned-dump>` reads only guarded native
contexts and emits booleans. It checks the demonstrated runtime PE profile,
root/context vtables and pointer bounds. The native runtime's header reports
Machine 0x0200, while the unchanged file reports 0x8664; timestamp 1661534873
and image size 58298368 match. `key_notification_received` is persistent in
these runs. `player_update_marker` is a snapshot of +0x88, not proof that a
player message was never received: it is false in the completed player run
despite the newly observed requests. Neither flag establishes a menu or world.
A repeated player run showed the same requests. Attempting to focus its window
failed with Windows `GetCursorPos ... Access is denied (0x80070005)`; a refreshed
selection after bounded shutdown found no window. Foreground rendering could
not be verified, so black captures alone do not prove the menu's exact state.

## Server-to-client protocol roles (static, 2026-10-13)

Roles below come from the client's own receive dispatchers (rva
0x007a8120-0x007ab630, `id - first_id` switch) and the obfuscated log strings
their handlers decode. They identify what each family carries; they are not
live-verified replies and must not be sent speculatively.

Client-to-server (flag 1) and server-to-client (flag 2) families sit in
adjacent id hundreds (e.g. 59900 f2 / 60000 f1, 42400 f2 / 42500 f1).

| family | handler evidence | role |
|---|---|---|
| 20500 (0xf5ff548a) | 20501 -> 0x7744d0 `LobbySystem_C::LobbyConnectHelloErrorHandler`, "Lobby couldn't create player."; shows a localized error by code, then drives connection states 3/4/5 | 20501 is a **hello error / disconnect** notice; never send it as a success reply. 20506 is ignored (handler returns 0); 20507 logs dynamic-configuration update success/failure |
| 20800 (0x1a9879a4) | 20801 prints ID/Name/Persistent ID/Version/Experience/Level; 20802 "Low Violence" | player profile and account settings |
| 24300, 24900 | "Active Unlocks", "All Unlocks for 0x%016llx" | unlock inventory |
| 26400, 60900 | "Currency", "Virtual currency granted/spent/reversed" | currencies |
| 28000 | ID/Name + "Achievements" | achievements |
| 39800 | weekly wins / first-win rewards | arcade weekly progress |
| 40900, 51800, 53000 | custom-game links, saved matches/replays, instance state | custom games and replays |
| 42400 (0x5f8c3add) | 42401 logs eSports tournament match ("Tourny Name", "Ready To Play") | tournament data; the client's empty **42600** (0xeb45ad29) repeats every ~12 s and is a tournament status poll |
| 59900 (0x2558bd8d) | "# Migration Servers", migration type/state/source, "Queue Status ... Approx Position", "Received add migration response" | account-migration status, log-only; the client's empty **60002** is a migration query |

Neither 60002 nor 42600 is evidenced as the main-menu gate. A separate
candidate is the hotfix state machine at rva ~0x00b4cd70: it re-polls every
15000 ms and, while its state byte (+0x18) is 4, reports "hotfix timeout"
(error 8/6/-5/4 via 0x0060eca0) after an elapsed time compared against a
configurable 81.0 s value. Whether this state is reached in our runs is not yet
checked.

## Training instance-referral frontier (2026-10-13)

24000 is the observed Training request; 20600 (schema 0x074dad18) is a separate
instance connection referral. Answering Training with it is currently an explicit
experiment, not proof of the correct complete queue/game-allocation sequence.
The original 20600 handler is 0x00775cd0 (dispatcher 0x007a99c0). Outer bool at
+0x78 false skips its conditional record transform. Nested +0x2e is the fixed
64-byte host and +0x2c the port used by the original `%s:%d` formatter/parser.
Nested +0x6e is a second 64-byte **IPv4:port string**, not a random token.
The connection callback 0x007daf70 -> 0x007cc690 (ConnectToInstance) passes
the job's +8 string to 0x0041ef00 at 0x007ccbf6. That parser searches for ':',
parses the port and resolves IPv4. Our earlier token hypothesis was incorrect;
both endpoint forms now contain owned loopback 127.0.0.1:1119.

The public probe's profile targets only mapped loopback 127.0.0.1:1119 and uses
locally generated session inputs. `protocol/instance-104319.json` contains the
numeric layout. Handler -> 0x00e3e940 -> 0x00e1e6f0 creates a component-slot-120
(vft 0x026775f0) referral job at +0x20. This was observed immediately after
Practice Range in two bounded live runs. The original 0x00e3e700 consumer checks
an initial integer, copies the parameter prefix and clears/frees the job.
Job absence later does not establish rejection. The remaining field semantics
and queue assignment are unresolved. No extra TCP connection was observed in
the early runs; the final world state was WAITING/no request.

The original instance request path is 0x007cc690 -> 0x00c68980 -> 0x003fc550
-> 0x003ff920. Runtime selector byte 0x02e2f308 is zero in the inspected run;
this selects the alternate datagram peer path at 0x0040009d, rather than the
per-peer TCP socket path. Do not overwrite the selector. The original bridge
was TCP-only. An explicit `--udp-forward 1119:21120` now adds a datagram bridge
using the same owner/AppContainer-restricted pipe and fixed loopback endpoints.
It retains datagram boundaries with a two-byte LE length, caps packets at
4096 bytes and admits one container-loopback source port per diagnostic run.
It requires the existing TCP lobby forward and a 1..180-second run. Internet
and LAN capabilities remain absent. This is a diagnostic, not multiplayer
transport for multiple players.

Native `instance-udp1`: after 24000 -> corrected 20600, the original client
sends **39 datagrams of 34 bytes** through the UDP bridge to the private
receive-only observer. No UDP protocol replies were sent. This verifies outbound
native instance traffic, not a completed handshake or a loaded map. The UI
first shows ENTERING PRACTICE RANGE, then returns to Training after the
unanswered attempt. The final world state is WAITING/no pending request.
`tools/instance_probe.py` reports packet sizes
and counts only; it logs no payload, identifiers, keys or peer source ports.

`protocol/queue-104319.json` holds all 34 queue-message layouts as numeric
metadata only, compactly serialized within the existing size/field budget.
The opt-in empty-notification control requires the selected schema and decodes
complete observed Training requests before replying. 23332's native handler
0x006ce750 sets component-38 +0x10f9; its lifetime/meaning is unverified. The
read-only `--queue-state` diagnostic emits that marker, four record counts and
a referral-job-presence boolean. It exports no native bytes or session inputs.
