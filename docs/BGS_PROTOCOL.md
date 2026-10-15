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
| 20505 | four u64[] | 0x77a000 calls 0x57bba0, which feeds content override lists and balances initialization counters through 0x1719a20/0x1719a60. List 0 fills the content provider's Hero (type 0x75) set, list 1 issues per-GUID resource requests (0x171ace0, priority 2), list 2 fills the map (0x9f) set; list 3 stays in the handler (see "Hero preload list" below) |
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

### Instance datagram format (2026-10-13, private runs udpcap2..udpreply6)

Verified offline against every captured packet of two independent runs (each
regenerated byte-for-byte from our own locally generated 20600 inputs):

| offset | size | field |
|---|---|---|
| 0 | 12 | AES-GCM tag, truncated to 12 bytes |
| 12 | 4 | u32 LE `(version << 4) \| type`; client connect = version 2, type 0 |
| 16 | 4 | u32 LE send sequence (peer +0xa4), also the nonce counter |
| 20 | 4 | u32 LE next received sequence (peer +0xa8; received sequence +1) |
| 24 | 8 | u64 LE peer +0x140 (received-sequence bitmap; initially 0) |
| 32 | 1 | flags (1 on connect) |
| 33 | 1 | magic `0xad` |
| 34 | n | payload (empty for the connect packet) |

Client-to-server packets are AES-256-GCM with key = the referral's first
32-byte input (+0xae), nonce = eight zero bytes then u32 LE sequence, the
22-byte header (offsets 12..33) as AAD and the payload as plaintext. Header
builder 0x003f96d0; a second sender is 0x00402b6a. Codec factory 0x003fbc60
selects by type: 2 plain (copy, zero tag), 0 HMAC-MD5, 1/3 AEAD codec
(vft 0x025f5bd0, the one live in a mid-send dump), 5 BCrypt AES-GCM. Seal ABI:
payload, length, AAD (packet+0xc, 0x16 bytes), nonce sequence, output, tag
(packet+0) and tag length 12. The send codec is peer **+0x10**, keyed by +0xae;
the receive codec is peer **+0x18**, keyed by +0xce. These directions are
verified by the constructor, sender/receiver call sites and the later private
read-only key reconstruction; the original opposite slot labels were incorrect.

The client retransmits the connect packet every ~257 ms, 39 times (~10 s),
then abandons the attempt. In `udpreply6` a private responder answered each
packet with a sealed version-2 header (key +0xce, zero-prefix nonce, ack = the
client sequence, bitmap 0, flags 1, empty payload), cycling types 1..15.
The bridge delivered all 39 replies; the client's packets did not change
(type 0, ack 0, bitmap 0). The later reconstruction confirms that +0xce and
the zero nonce prefix were correct. All 39 captured client packets and 39
responder replies authenticate independently using those locally generated
inputs. This offline result does not prove the native receive path accepted them.

### Read-only instance key reconstruction (2026-10-13)

Following the user's requested disassembly, the private reconstruction of
0x003fa810 recovers the five-qword nonce-prefix/key block in both live AEAD
codec objects from the mid-send dump. Both match our generated referral inputs
exactly; the nonce prefix is zero. The paired encoder 0x003fa380 and eight
arithmetic inverse operations pass 4144 bidirectional checks; re-encoding both
decoded objects reproduces their original 40-byte scrambled blocks exactly.
The timestamp-derived/object-address/call-site-dependent storage is local
representation scrambling; it is not evidence of an additional session-key KDF.
No client memory is changed, and no native table bytes, key bytes or decoder
implementation are published. Reports contain comparisons and counts only.

Decode caller 0x003fb2e0 constructs nonce prefix || u32 LE packet sequence,
32-byte key and passes AAD length 22 / tag length 12 to the original GCM open.
Incoming dispatcher 0x004027f0 checks length >=34 and looks up the packet's
upper header bits as the peer/version key; 0x00402bdc invokes codec +0x10 on
the receive object stored at peer +0x18. Accepted packets enter peer +0x188
and are processed by 0x00401500 -> 0x003f94f0.

In native peer state 1, 0x003f95c4 requires `(flags & 3) == 3` before advancing
to state 3 and producing an event. The earlier flags=1 replies fail this check
even with a valid tag. State 3 has further flag/sequence checks. These are
protocol transitions, not flags to patch in client memory. Sequence updater
0x003f9fc0 shifts/sets peer +0x140 as a receipt bitmap and advances +0xa8 to
received sequence +1; treating +0x140 as a connection id was incorrect.

### Native handshake progress with flags 3 (2026-10-13, udpflags7)

A bounded private responder sent version-2/type-0, flags-3, empty-payload
replies using our generated +0xce key and zero nonce prefix. Direct Computer
Use input selected Training -> Practice Range; the original UI changed to
**ENTERING GAME**. After the first reply, the client changed from type-0/
flags-1/sequence-0 to flags-2/sequence-2 with next-sequence 1 and a nonzero
receipt bitmap. It then sent type-1 packets with 13-byte and larger payloads.
This demonstrates native receive/handshake progress beyond connect retries;
it does not establish a completed application session or a loaded map.

The bridge independently counted **161 outbound / 100 inbound** datagrams.
All 161 client packets and 100 private replies authenticate and regenerate
exactly using the independent public `tools/instance_datagram.py` codec.
Observed nonempty plaintext sizes are 13, 33, 43, 63, 73, 93, 103 and 123 bytes.
They do not match the complete known lobby bootstrap offer or its three-byte
framing. The reliable payload/message format still needs tracing. The old
private responder's `tag_ok` field only checked empty packets; false for a
nonempty packet is not an authentication failure.

The responder was limited to 100 replies and 180 seconds; it returned no
application payloads. At bounded client shutdown the dump reports world
WAITING/no pending request, zero queue records and no referral job. No rendered
map or controllable hero was observed. Original executable hash/signature and
both saved ACLs match; owned processes and diagnostic listeners are gone.

The public codec supports the observed AES-256-GCM envelope with caller-supplied
local keys, a 12-byte front tag, 22-byte AAD and eight-byte nonce prefix plus
sequence. Its 4096-byte cap follows our diagnostic bridge limit. It authenticates
before returning fields/plaintext and rejects malformed bounds or unsupported
version/magic. It does not implement peer state, replay handling, reliability
or game messages. Fixtures use author-written bytes only; all captures, input
keys, dumps and the private key-storage reconstruction remain outside Git.

### Receipt tracking and application-body frontier (2026-10-13, udpack8)

The original receive updater 0x003f9fc0 accepts forward sequences, shifts its
64-bit bitmap by `received_sequence - next_sequence + 1`, sets bit zero and
advances next-sequence to received-sequence +1. A gap of at least 64 clears
the old bitmap. Older packets are rejected rather than inserted into missing
bits. At the sender, a queued sequence is acknowledged by bitmap bit
`next_sequence - 1 - queued_sequence`. These receipts cover datagrams, not
completion of the reliable messages carried inside them.

`tools/instance_datagram.py` now includes an independent `ReceiptWindow` for
authenticated bounded peers. It rejects sequence wrap; start a new session
with fresh keys instead of reusing an AES-GCM nonce. Our earlier private replies
echoed the received sequence and sent bitmap 0, which did not match this updater.

Native `udpack8` uses next-sequence/bitmap receipts, flags 3 on the connect reply
and flags 2 thereafter, with empty type-0 bodies. All **224 client packets and
224 replies** authenticate and regenerate exactly; all replies match the
receipt-window calculation. Client plaintext sizes are 0 (75 packets), 13 (4)
and 33 (145); no 43..123-byte bodies occur in the captured interval. This combined
acknowledgement/flag correction changes the traffic compared with udpflags7;
the run does not isolate which individual field caused the change.

Fresh Computer Use verifies menu -> Training -> Practice Range -> ENTERING GAME
and later a return to Training, with no map. The observer's 180-second lifetime
started before the client's 150-second run and ended before client shutdown;
this is not a stability test. The bridge counts 225 outbound/224 inbound, one
more outbound than the observer captured. Final world WAITING/no request,
zero queues/no referral job. Original hash/signature and both ACLs match;
owned processes and listeners are gone. No application payload reply was sent.

Read-only inspection identifies the active instance transport (vtable 0x2616458)
with seven modules. Authenticated event 4 reaches its original receive callback
0x007ce110 via vtable+0xb0. The callback reads an LSB-first bitstream, a compact
u32, six module prefixes, a seven-bit message count, encoded message identifiers
and per-module handlers. The reliable-channel module has its own conditional
block; complete framing and application-message semantics remain unresolved.
The separate 0x00e3af00 session callback expects a different fixed 32-byte control
body and is not the active callback identified in the mid-send dump.

`tools/instance_bits.py` implements only the independently written bounded bit
reader/writer and compact u32 primitive traced at 0x00db0e60: selector 1 +18 value
bits, selector 0/1 +24 bits, or selector 0/0 +32 bits, all least-significant bit
first. Written fixtures cover exact bytes, selector boundaries, truncation,
unaligned/64-bit crossings, padding and bounds. Private validation reproduces
the first compact field exactly in all 138 udpflags7 and 149 udpack8 nonempty
type-1 bodies. All use 19 bits; later bodies include both absent and present
conditional module blocks. This is prefix validation, not complete packet or
game-message decoding. Captured plaintext remains private.

`protocol/queue-104319.json` holds all 34 queue-message layouts as numeric
metadata only, compactly serialized within the existing size/field budget.
The opt-in empty-notification control requires the selected schema and decodes
complete observed Training requests before replying. 23332's native handler
0x006ce750 sets component-38 +0x10f9; its lifetime/meaning is unverified. The
read-only `--queue-state` diagnostic emits that marker, four record counts and
a referral-job-presence boolean. It exports no native bytes or session inputs.

### Reliable records and the game-server welcome (2026-10-13, udpapp9..udpapp20)

**Client-to-server bodies** start directly with the reliable module block: a
present bit, a 4-bit primary record count and a 4-bit secondary count, then
byte-aligned records `u32 sequence | u8 channel | u8 message delta | fields`,
then the remaining module bits (observed as one zero byte). Record sequences
are one counter across channels, starting at 0. `tools/instance_reliable.py`
round-trips every captured client body exactly (138 udpflags7, 149 udpack8)
for the two observed channel-1 messages, 21610 (i32 counter + u64[] times,
every 250 ms) and 21627 (one float, 15.0 every ~10 s).

**Server-to-client bodies** (receive callback 0x007ce110, type 1): compact u32
server frame, then module prefixes 0..5 (module vtable +0x30), then a 7-bit
entity count with per-entity identifiers and module presence bits.

| Module | Prefix reader | Prefix layout |
|---|---|---|
| 0 reliable | 0x00c6a480 | present bit; 4-bit primary, 4-bit secondary counts; byte-aligned records as above. Primary records are delivered in sequence order (older dropped, newer buffered); secondary records are delivered unsequenced |
| 1, 2 | 0x00d34a80 | none |
| 3 | 0x007c0630 | compact u32 (acknowledged frame), 4 flag bits, time-present bit (+16 bits) |
| 4 | 0x00787e70 | one bit; 1 is the normal path |
| 5 | 0x007e3ff0 | outside hot reload: one bit-terminated list of 8+8-bit items (a single 0 bit when empty). The 16-bit item is read only when the hot-reload flag is set |

The instance connection carries 11 reliable channels (channel vtable +0x28 =
first message id, +0x30 = last):

| Channel | Schema | Messages |
|---|---|---|
| 0 | 0xc77f6403 | 20300-20323 (game server) |
| 1 | 0xa7fbbd0c | 21600-21634 (common) |
| 2 | 0x8f89e0df | 25000-25019 |
| 3 | 0x82a2f991 | 27500-27502 |
| 4 | 0x9f0a9f88 | 25800-25810 |
| 5 | 0xa9385a52 | 30700-30777 |
| 6 | 0x398e145e | 42900-42907 |
| 7 | 0x741ec7b2 | 42800-42803 |
| 8 | 0x716ad5d9 | 22300-22308 |
| 9 | 0x145ce2da | 25700-25708 |
| 10 | 0xcf043764 | 42700-42701 |

The 20300 dispatcher is 0x007d2000. **20300 is the game-server welcome**: its
handler 0x007d9400 rejects a record whose +0x500 differs from the client's
simulation quanta (16000) or whose +0x519 hot-reload flag differs (false),
then builds a world request (first field = message +0x4a8, then two settings
u64s, the 32-byte array at +0x4b4, the settings record and the u64[] at +0x520)
and calls 0x00b97f40. On success it submits through 0x00b4b1c0 and 0x00b4b430,
the same sequence the client's local-world path 0x008359a0 uses.

Private bounded runs, UI driven by window capture plus coordinate clicks:

- A default-valued 20300 (quanta/hot-reload set) is accepted; the client
  immediately sends a new reliable 21600 on channel 1 (local name, zeros,
  empty blob) and creates no world request.
- With +0x4a8 = the Practice Range header GUID `0790000000000688`, both world
  managers hold a **pending world request** whose first field is that GUID,
  the first world request observed in this project. State remains WAITING;
  the UI stays on ENTERING GAME. No map is rendered.
- Echoing each 21610 with two server times appended, sending a type-1 frame on
  every reply, or pre-creating an empty local `104319\Hotfix` directory does
  not change that result.
- Also setting the settings record's map field (+0x128) to the same GUID
  (udpapp15) leaves both managers WAITING with the request pending.
- Further sequenced channel-0 records after the client join (a 20301
  settings update with the same map, a 20302 with player id 1, a 20322 i64),
  module-3 server time, and non-zero welcome +0x78/+0x4b0/+0x518 values
  (udpapp16/udpapp17) produce no new client messages and no state change.
- Answering the Training request with an empty 23311 or 23332 queue
  notification immediately before the 20600 referral (udpapp19/udpapp20):
  23332 is accepted (its native marker is set), but queue records stay empty
  and both managers stay WAITING with the request pending.
- Resource GUIDs follow the public TankLib convention (type = bit-reversed
  12-bit field + 1): map headers are type 0x9F, game modes type 0xC5, whose
  low parts match the public decimal game-mode ids (Practice Range = 90).
  Putting the Practice Range game mode in settings +0x130 next to the map
  (udpapp21) also leaves both managers WAITING with the request pending.

The settings-record installer 0x00587e10 is also called by the 20301 handler
(message +0x78), so 20301 is a settings update with the same 1,064-byte record.
The client has a second, queue-driven join flow: the local-world builder
0x008359a0 is reached from 0x008357a0 beside the queue session-start function
0x00828580, building its request from the session descriptor instead of a
20300 welcome. That consumer logs tournament pending games and its session
class looks spectator-like, so the instance-referral flow remains the one the
Practice Range demonstrably uses.

The referral job is created only by 20600 (0x00775cd0) and consumed only on the
instance-teardown path 0x007cdb60; its presence at shutdown means the instance
connection was still up. The manager step function 0x00b52190 remains partially
traced; the WAITING branch of world tick 0x00b4b5f0 is traced below. Field meanings of
the 1,064-byte 20300 settings record are unknown. Captured bodies, generated
inputs and dumps remain private.

### WAITING resource gate and client join (2026-10-14)

Following aligned branch targets through the opaque padding reaches the world
tick's state dispatch at 0x00b4cca8. WAITING calls 0x00b52b20. The handler
constructs a type-0x9F map-header GUID from the request's low u32, checks its
catalogue entry with 0x0171b800, and polls 0x0171c0b0. A raw load state below 2
returns without advancing; state 3 calls 0x00b523f0, entering world state 3
(ABANDONING SCENES). Other states >=2 take its error path.

Read-only reinspection of udpapp11/21 finds the requested Practice header in
the resource catalogue, but no corresponding load-cache object, so the query
returns 0. Each dump has 28 other load-cache entries. The optional mode resource
in udpapp21 is also in the catalogue without a load-cache object. udpapp10 has
no pending request. These are saved-run observations, not new live launches.
The next prerequisite is the original path that initiates/retains the header
load; header existence, additional server frames and guessed settings do not
establish that prerequisite. The earlier standalone native-resource experiment
in FINAL_RETAIL.md independently demonstrates header loading through the
original API, but is separate from server application negotiation.

`retail_login_state.py --world-resource-state` now reports these checks with
bounded lookups and profile validation. It exports only booleans, counts and
raw state values; GUIDs, native hash tables, pointers and resource bytes stay
inside the reader.

Common-channel message 21600 (base delta 0) is the client join seen after 20300.
Its observed layout is a NUL-terminated name, u32, four packed booleans, float32,
u32 and length-prefixed blob. Semantic meanings beyond the join response remain
unverified. The boolean byte's upper four bits are ignored by the native reader;
the independent codec preserves them as `Record.boolean_padding`. With this
layout, all 1003 complete authenticated client bodies in udpapp10/11/21 roundtrip
exactly, including the previously undecoded 21600 records. The public profile
supports only 21600/21610/21627 on primary channel 1; it is not a complete game
protocol or a server-to-client encoder.

### Instance content metadata 20318 — 2026-10-14

Channel 0/schema 0xc77f6403 message 20318 routes through dispatch 0x7d2000
and handler 0x7d8010 to the original metadata registration routine 0x684310.
The checked uint32 at message +0x98 must equal **1**, the resident format
constant; it is not the client build number. `instance-metadata-104319.json`
contains only its numeric layout: a fixed 32-byte identifier at +0x78 and a
76-byte nested record at +0x98 (two uint32s, one int32, two fixed 32-byte
arrays). The serialized field body is 108 bytes. Further field semantics,
including valid content digests and sizes, are unresolved.

An empty diagnostic descriptor sent through the authenticated transport is
registered in native runs udpmeta22/24/25/26. The final cache contains one
entry with flags 0xa0, no content-present bit, and ten completed acquisition
attempts. There is no current content context. The default empty identifier
matches the resident default at 0x321ff30; constructor 0x684610 bypasses the
metadata lookup for that default. Registration of this record therefore does
not prove association with the pending world request.

Entry +0x78 contains flags (1: content present, 0x40: acquisition in flight,
0x80: acquisition failed). **+0x80 is a retry deadline; +0x88 is a completed
attempt counter**, not an action pointer or state enum. Consumer 0x67fd70
submits kind-14 requests via 0x67e120/0x81c270, increments the counter on
completion, sets bit 1 on success, and schedules another attempt or sets the
failure bit at the configured limit. The live 7-to-final-10 change in udpmeta25
was retries, not progress past the failure.

Kind 14's vtable is 0x26188d8 and worker method is 0x81dfc0. The worker opens
a local temporary file with flags 0x321 via 0x1858f30 before transferring
content. Its file-open error path returns status/tag 3/2 and the filesystem
code. In udpmeta26, a read-only observer validated six completed requests
still referenced by the original service queue: each reports 3/2/-3. Native
error formatter 0x185e3a0 labels -3 "failed to open". This generic code does
not establish the underlying Windows error. Empty-directory initialization
and an own-package-only modify grant both failed to resolve it.

`retail_login_state.py --metadata-state` exposes only bounded counts, flags,
retry information and context-presence booleans. SDK kind 13 remains local
directory enumeration; it must not be confused with kind 14 acquisition.
No proprietary descriptor payload, packet, identifier, digest or key is public.

### Server entity section and map placeables (2026-10-14, livecreate51..55)

After the module prefixes, the server body carries a 7-bit entity count. Each
entity starts with an identifier (0x00db0f70: 2 class bits giving top bits
`1gg`, then a varint index — 0 + 8 bits, 1 0 + 16 bits, 1 1 + 32 bits; index 0
is the invalid sentinel). A **terminating** module chain follows: bit 1 means
module *k* has per-entity data, bit 0 ends the entity. Empty per-entity forms:
module 0 none; module 1 one 0 bit (0x00a16ad0); module 2 two 0 bits
(0x00b3a490: two optional sections); module 3 one 0 bit (0x007c2e60).
Module 4 (the replication module, 0x00787f20 -> 0x0078bbc0) carries a 2-bit
operation (1 create, 2 update, 3 destroy) and, unless destroy, a 14-bit payload
length plus payload. Records are batched per packet and processed by the
world update (0x0078dd60 -> 0x0078e300): create 0x0078c360, update 0x0078e5d0,
destroy 0x0078e4e0.

A create may name a **map placeable** (presence bit, u32 placeable id, an
optional-extra bit) instead of an entity definition; its body then continues
as an update (8-bit component count; an extra 32-bit check only during hot
reload). Placeable-spawned entities must use identifier class `0b100`.

When a world reaches WORLD REPLICATING, producer 0x00787f50 walks the scene
and records every placeable whose descriptor contains component type 0x5e or
0x3a as *pending*; only a create naming that placeable removes it. Practice
Range has four. The world update processes the queued records only once the
selected-entity gate (20302) resolves; with all pending rows cleared it sets
the completion marker and the world advances through GAME MODE LOADING to
**WORLD_RUNNING**.

Private bounded runs livecreate54/55 sent minimal placeable creates (no
components) for the four Practice placeables plus the earlier diagnostic
20302 selection of an existing local entity. Both reached WORLD_RUNNING with
four class-`0b100` entities present. The UI stayed on the Practice loading
screen; no hero selection, player entity, rendered gameplay or input is
established. The empty component lists and the diagnostic selection are
experiments, not a reconstruction of the original server's replicated state.
Earlier livecreate51..53 failed only because of two framing errors (an extra
module-5 bit and a one-bit module-2 form), found from the client's own
per-module consumed-bit counters at connection +0xa0.

`tools/instance_entities.py` now implements this minimal, non-hot-reload
placeable section using the independent bit primitives. Its caller supplies
the stream after the module prefixes, at the seven-bit entity count. It supports
only the observed empty modules and 42-bit placeable create payload; unsupported
forms and truncated input are rejected. Four synthetic fixtures cover explicit
bit vectors, all identifier widths, unaligned sections, bounds and corruption.
Private capture verification re-encodes 2079 sections exactly across runs55,
58,59 and60, including 1481 placeable creates. No captured payload is embedded.

The private responder now uses this codec. Livecodec59 and livecamera60 render
Practice geometry and the in-game Escape menu after WORLD_RUNNING. A playable
player/hero remains unverified. The non-placeable definition-create path and
its component state are distinct from these minimal placeable records.

### Minimal definition create (2026-10-14, livedefcreate64/livedefselect65)

The non-placeable branch of native create 0x0078c360 reads a type-3 resource
index through 0x00db11c0, followed by the transform flags in 0x0078dab0. The
verified neutral form is: placeable bit 0, two zero selector bits, a 32-bit
resource index, zero 8-bit transform flags, zero 8-bit network component count.
Its payload is 51 bits, using the same class-0b100 identifier and module chain
as the placeable codec. Other resource-index forms, transform flags, component
state, updates and destroy records remain unsupported by the reusable codec.

A hash-verified final-retail definition already ready in the native fallback
typed cache constructs a new entity, including component 44 and callback pairs
25/26 and 84/85. A later sequenced 20302 selects it. Its component-44 actor ID
remains invalid, so this is entity creation/selection, not a controllable hero.
All 1332 captured sections from the two runs re-encode exactly, including 160
definition creates. The public placeable-only wrappers still reject definitions.

### Hero preload list and hero definition create (2026-10-14, liveherodef68..70, liveherolist71)

Creating a hero's gameplay entity definition (Soldier: 76, type-3 index 0x3cf,
from the offline hero-record mapping) with the same minimal codec runs the
original create path, but the client cannot construct it unless the definition
is already resident. The create lookup 0x0078cf3a -> 0x017d3360 -> 0x0173ba30
only *looks up* the typed cache; it never starts a load. Without a preload:

- the client's replication completion check 0x0078dd60 fails, and 0x0078b059
  calls the abort routine 0x00b64af0 with the label "Mirroring mismatch."
  (decoded label getter 0x00787350). The formatted "Missing entity definition"
  message in the mid-run dump names the hero definition itself;
- 0x00b64af0 sends lobby 21801 (empty, sender 0x007731a0, vtable 0x02604ac0)
  and 21802 (bool, sender 0x00773940, vtable 0x02604ae0) in pairs, notifies the
  Battle.net session object (0x00e25980), so its keepalives stop, and the client
  eventually leaves: instance packets with header flag 4, BNet TCP closed, and the
  UI returns to Training. 21801/21802 need no reply for this diagnosis.

A census of the native fallback typed cache in a mid-run dump finds 129 resident
type-3 definitions, including the controller definition used earlier, but none of the
56 hero gameplay definitions. 20505 list 0 is the original input: the handler
passes it to 0x0057bba0, which resets the provider's hero/map/mode sets, inserts
catalogue-present GUIDs into the Hero (0x75) set through 0x0057c700 and the map
(0x9f) set from list 2. The opt-in probe flag `--lobby-hero-list <hex>` (type-0x75
hero-record GUIDs only, at most 64, requires 20505 initial data) puts
hero records into list 0. With Soldier: 76's hero record:

- 21801/21802 are never sent; Battle.net keepalives continue; there are no
  instance flag-4 packets, and the world stays WORLD_RUNNING with the hero
  entity selected until the bounded end (sampler: 17607 samples, 0 rejected);
- the final dump has 150 resident type-3 definitions, including the hero's,
  and the hero entity has 28 native components (component 44 not among them);
- the window shows a large armored boot model at the default camera position,
  consistent with the hero model's scale. No hero HUD, first-person view or
  controllable movement is established. Component 44 is still on the controller
  entity, and its actor target remains invalid.

### Component state in creates: controller actor link (2026-10-14, livecontrol72/73)

The create payload's trailing u8 is the component count of the update body
0x0078e5d0. Each entry is a u8 runtime component type; the client locates that
component through the entity's component mask and calls its slot-0x18 method
with network visitor 0x0078b870 (vtable 0x02615c10). The visitor:

1. byte-aligns, relative to the start of the server **body** (each frame's body is
   copied into the record and entity items store absolute bit offsets, 0x0078bbc0);
2. reads a u8 mask length and that many mask bytes;
3. walks the component state's reflected fields (0x01bdfdd0/0x01be0130). The filter
   0x00788510 takes one presence bit per field (LSB first) from the mask;
4. reads each present field's value from the main stream: raw little-endian bytes
   (8 bits per read, 0x01be0300), or special forms for strings, 128-bit values and
   compact-flagged u64 fields.

Type kinds are CRC32 values of lower-cased type names (for example `teentityid`),
initialized lazily; a 4-byte kind table is resolved by 0x01be1c90.

Component 44's state (type descriptor 0x030d8f80, size 0x88, located at component
+0x58) has three `teEntityID` fields at state +0x78/+0x7c/+0x80 (reflection hashes
0x1ab5e773, 0x4d1ffc51, 0xb1ca772f). The native actor getter reads +0x7c (component
+0xd4). The client's own local-game path 0x0082a5e0 sets all three to one entity.
The public codec's `DefinitionCreate(..., controlled_actor=ID)` does the same:
count 1, type 44, padding, mask length 1, mask 0x07, then three equal 4-byte IDs.

Live runs: run livecontrol72 creates the controller definition with Soldier: 76's
entity as its controlled actor, preloads the hero (20505) and selects the
controller. The final dump reports a valid actor target that resolves to the hero
entity, WORLD_RUNNING and no abort. Livecontrol73 adds the optional module-3 time
field. Its receiver 0x007c7800 resolves the selected component-44 actor
(0x00da69d0) and records its ID at module +0x64. That controlled-actor marker
is valid for the submitted world. The default fixed view remains on screen; no
first-person camera, HUD or input control is verified. All captured sections from
runs 71/72/73 re-encode exactly with the public codec at their body offsets,
including 66 actor creates in each of runs 72 and 73.

### Statescript frame body: variables, state data and full snapshots (2026-10-14, runs 87-90)

Emulator traces of the client's own frame interpreter 0x00a0e3c0 on saved dumps,
then live runs:

- Module-1 sync header: `SFSF` base frame, `SFDt` delta, one part-present bit, then
  `Size` (`SFDt` form 8/16/32 bits) which counts **bits** of the blob.
- Blob header 0x009b4160: one bit, then a *full snapshot* bit (record +0x4c); a full
  snapshot adds a bit (+0x4d), `CmFD` (absolute frame stamp, must exceed manager
  +0x900) and, when the base frame is non-zero, `LBSS` (bits to skip if already
  applied).
- Instance list 0x00a0e1d0: `Inst` instance-ID delta (0 ends). Per ID: bit **1 =
  destroy** (0x00a0f440), bit 0 then a create-data bit: 1 = create (graph etc.),
  0 = update of the existing instance (no data).
- Body 0x00a0f080: global variables (bit, then `UVGu` identifiers ORed into type
  0x1C identifier GUIDs), then per listed instance: `IVDt` bitmask over the graph's
  sync variables and the same `UVGu` list (0x00a0ca20), then `StDt` bitmask
  (0x00a0c620) over the graph's remote-sync nodes, or over **all states** in a
  full snapshot. A set state entry is `has-data` bit + `active` bit; activation
  calls the state's begin 0x01b70790.
- Bitmask 0x00d530e0: n <= 8 bits raw; otherwise a byte-presence mask
  (ceil(n/8) bits) followed by each present 8-bit chunk.
- Variable value 0x00a0d2c0: 4-bit kind (bool, sized ints/floats, vectors, entity
  ID `IDVd`, handles); kind 15 + 3-bit subkind 0 is a 64-bit value in four u16
  words, then `StEC` state-event count.
- Remote messages 0x00a0cca0 (`RMFr`/`RMSz`/`TrID`) address remote-sync nodes;
  the GameMessageEntry state's handler (0x01ce5640) ignores them.

Graph STU content (reference-only OWLib type names) shows Practice graph 0x0c90's
state 0 is a `STUStatescriptStateHero` reading sync variable 0x03ac. Live run
livehero89 sends a full snapshot that sets 0x03ac/0x30df to Soldier: 76's hero
GUID and activates state 0; the dump shows that state running. Its client class
is a generic state (no hero-specific client logic). Run liveherogr90 also creates
the hero definition's nine statescript graphs (0x33, 0x4b, 0x43, 0x251, 0x255,
0x257, 0x259, 0x91b, 0x8b6) on the hero entity; all nine instances exist.

### Local control: create ownership flag and the 20302 selection (2026-10-14, liveowned93)

The client's module-3 command writer 0x007cc060 and first-person reader
0x007c7900 take their entity from the world owner's per-component list for type
59 (0x00699530; type byte from 0x00be0ad0). No definition maps a serialized
component to 59. The create path 0x0078c360 reads the create-flags byte
(0x0078dab0, record +0x60). Bit 0x10 builds the entity with builder vtable
0x02615ae8. Its 0x0064ee90 adds components 59 and 63 when builder +0x2098 is set
and adds 74 when bit 0x20 is present. The create path sets +0x2098 from
0x00586060, which compares the entity ID with world-owner +0x298, the current
20302 selection.

Recipe used in run liveowned93: the diagnostic 20302 selection (0xc0000001)
drains the create queue; the selection then moves to the controller ID; only
after that is the controller created, with flag 0x10 and its component-44 actor
link to Soldier: 76. Result: the original client enters first person (hero
hand visible), mouse-look rotates the view, and the client sends a continuous
stream of new instance packets. The public codec accepts
`DefinitionCreate(..., create_flags=0x10|0x20)`; other flag bits carry data and
are rejected. Health and authoritative movement are not replicated yet (red
damage vignette), and no server-side simulation exists. Entity-ID class 0b101
(0xA...) tested in run livepred91 does not add component 59.

### Hero select and the picked-hero spawn (2026-10-15, runs 110-120)

Graph `0x058000000000288b` (instance 4 on the controller in our runs) contains both the
client-only hero-select UI logic and the server half that answers it. Our responder
emulates that server half; nothing below patches the client.

- **Identifiers.** `STUConfigVarDynamic` is 0x18 bytes: u16 identifier at +0x10, u8
  `m_60DB8F99` at +0x12. Text dumps that print the identifier as raw bytes show it
  byte-swapped (`4208` is variable 0x0842). With the flag set, lookup 0x1ba56e0 uses the
  entity-global table `[[table+8]+0x1f0]`; without it, the instance's own table. The
  graph's 32-entry `m_syncVars` list (runtime entries 0x18 bytes, GUID `0x0d80…|id` at +8)
  contains the flagged hero-select variables.
- **Writing variables.** The body's global section (0xa0c440) is one present bit, then
  `UVGu` identifiers (SFDt 8/16/32) each followed by a value, ending with identifier 0;
  values are stored with instance id 0, which is where flagged variables live. The
  per-instance IVDt mask (0xa0ca20) writes instance-scope values. A value (0xa0d2c0) is a
  4-bit kind and payload (0xd57de0), then a `StEC` state-event count (unary 0xd53400;
  zero is one 0 bit). Kind 0 is `Bool` (one bit); kind 9 is a GUID (0xd57a20 type 4,
  `ResV`: present bit, high u16, SFDt low part); kind 15 has subkinds (0 = raw u64 as four
  u16 words, 1 = u32, 2 = string, 3 = null, 4-7 = arrays).
- **Expressions.** Retail opcodes differ from the beta's numbering. Jump targets give:
  0 end, `2 n` AND-jump and `3 n` OR-jump (relative to the opcode), `8 k` dynamic variable,
  `14 k` config variable, 30 NOT.
- **Flow.** H in the spawn room sets global 0x7acb = !0x0986 and sends client game
  message (21616) `0x0240000000001360` with parameter `0x0a400000000005a2` = that value.
  The server stores it in global 0x0986 ("hero select open"; entry #1199). Selecting a
  portrait sends `0x0240000000001361` with parameter `0x0a4000000000005d` = the selected
  hero GUID (local 0x3748) when the hero is available, !0x0842 and 0x0986 hold. The
  server's entry #1227 checks spawn room and availability, then sets global 0x3369 = hero
  and 0x0842 = true. Remote-sync state 36 (#1463) holds 0x0986 true and, through state
  142, opens the hero-select UI without H.
- **Parameter blob.** u32 0, u8 count, then per parameter a GUID byte-presence mask with
  the present bytes, and a value `0c 01 ff <type>` followed by 1 byte (type 1, bool) or
  8 bytes (type 4, GUID).
- **Result (livepickspawn120).** On the pick the responder creates the hero's gameplay
  definition (hero record → gameplay entity map) as the controller's linked actor and
  moves it into the spawn room. The client shows Tracer's first-person arms and offers
  CHANGE HERO. Weapons, abilities, HUD and closing the overlay are not yet verified.

### Statescript state data, sub-graph instances and weapons (2026-10-15, runs 128-138)

- **StDt entries depend on the state type.** `0xf5e960` tests the state's STU type hash.
  For 458 types (including StateStack, CosmeticEntity and the sub-graph runner
  `STU_37D754C8`) an entry is one active bit; other types read has-data then active.
  An entered state may read state data through `0x1b72060`. The sub-graph runner reads
  6 bits: a flag, a 4-bit value (the child instance) and a flag.
- **Every listed instance has blocks.** Creates and updates alike are followed by
  their IVDt and StDt blocks; earlier creates only worked because bits past the end of
  a frame read as zero.
- **Sub-graph instances are created by the server.** The create's option bits (0xa0adc0)
  are: owner entity, a flag, `PIID`/`PSIn` (parent instance and parent state), and `SPUI`
  plus (entity, `SrcI`, `SrcS`) triples. A child created with PIID/PSIn shows in the
  instance table (verified in emulation and live: game-mode state 21's HUD root 0x0cb6).
- **Arrays.** Kind 15 subkind 6 (0xd57430): `ArrC` count, list/map bit, same-type bit,
  elements via 0xd579c0. Integers: kind 1 (4 bits) or kind 4 (32 bits).
- **Weapons.** The weapon script's `STUStatescriptStateCosmeticEntity` states spawn the
  weapon models from their `m_entityDef` (Tracer: 0x0400000000000017), which must be
  resident (lobby preload list). Activating them plus the weapon manager states renders
  Tracer's pistols in first person (livecosmetic131). Firing, ammo and the HUD are not
  yet driven.
- **Messages to state nodes.** The frame's message section (0xa0cca0) delivers remote
  messages to state nodes: `RMFr` frame, `RMSz` size, then per message a 17-bit id,
  `TrID` target instance and a node reference. The HUD graph 0x106b keeps most of its
  17 UX presenters under a game-message state (message 0x0240000000000717).

### Client input and server-driven firing (2026-10-15, runs 144-145)

- **Client commands (module 3).** The encoder is 0xc2ddc0, with fixed-width fields
  written by 0x7cad20. After the header (10 bits, u32, u16, u8, u8 count), the first
  command is written in full: u32 seq, movement, s16, s16, u24 buttons, u8, optional
  extras when button bit 16 is set, then u16.
  - Later commands are deltas against the previous one. The sequence delta is one bit
    (+1) or an unsigned varint (widths 2, 6, then 32). A change bit follows; if set:
    movement, signed deltas (8, 10, then 16 / 5, 8, then 16), button presence + 24 bits,
    and +0x1c presence + 8 bits.
  - Movement (0xc2e2f0) is a changed bit, then a table bit: in table form a 0 bit means
    the zero entry (no movement), otherwise a 1 bit and a 3-bit index - 1 into the
    9-entry direction table of axes 0/±127; without the table bit, per-axis presence
    bits with 8-bit values. (Corrected 2026-10-15: the earlier decoder always read 3
    index bits, which misaligned every later field by two bits.)
  - The module-3 header's u32 is the bit length of the data that follows it; with the
    corrected movement field every captured command block decodes to exactly that
    length and repeated commands decode identically across packets.
  - Buttons: 0x0001 primary fire (held), 0x0008 ability 1 (Shift), 0x0010 ability 2 (E),
    0x0040 jump, 0x0400 reload (R), 0x2000 press edge, 0x4000 release edge. (The older
    0x1000/0x0002/0x0004 values came from the misaligned decode.)
- **State data.** Entered two-bit states carry state data. WeaponVolley (0xd60400) is:
  start time as a sign-magnitude int (0x1b736a0: sign, width selector 0→8 / 10→16 /
  11→32, value); a flag (if set: second int + Part); a flag (if set: Part); then 6 bits.
  Zero values (18 bits) align exactly in emulation.
- **Firing.** On primary fire the private responder sends a new hero full-snapshot frame
  activating Tracer's weapon-script WeaponVolley state (0x16 state 8) with that data,
  then deactivates it about 250 ms later. livefire145: four clicks give four volleys; the
  client shows pistol recoil, tracers and wall impacts. Damage, ammo and the HUD are
  separate and not yet driven.

### Reload, ammo and other per-state data (2026-10-15, runs 152-157)

- **Buttons.** Reload (R) is client command button 0x0400 (see the corrected button map above).
- **More one-bit state types with data.** Entered states read type-specific data after the
  active bit (emulator-verified with the private full-snapshot harness):
  - Stack (594c2d80): two 1-bit flags (0x1b96460).
  - Wait (6540c278): none.
  - Anim (ca60e86e): an optional state reference (0x1b737d0: present bit; if set, the
    instance id as a varint read by 0x1b75190 — selector 0 → 4 bits, 1,0 → 8 bits,
    1,1 → 16 bits — then a state index of the graph's m_statesBitCount width), then a
    3-bit field, then a flag read by 0xcbd370.
  The reference names the state whose entity the animation plays on. With no reference
  nothing visible plays; referencing the weapon graph's CosmeticEntity state (the
  pistols) plays the first-person reload.
- **Reload.** Tracer's weapon script 0x16 reloads through Stack state 18 (var 0x0021),
  Anim state 9 (anim alias 0c80000000000004, speed var 0x0245) and Wait state 26, then
  refills ammo 0x0035 from 0x00c6. On the reload button the private responder activates
  those three states in a new hero full-snapshot frame (Anim data referencing
  instance 10 / CosmeticEntity state 1) and clears them after 1.4 s. livereload157 shows
  the original first-person reload animation (pistols flip, cylinders swap, guns return).
  Volleys are suppressed while reloading; an opt-in ammo sync var (0x0035, sync index
  53) counts down per volley and triggers the same reload at zero.
- **Instance create flag.** The flag bit after the entity bit in an instance create
  (0xa0adc0 → 0xd55d30 → entry +0x3c → instance +0x5d) is copied to entities the
  instance spawns (effects/cosmetics). Setting it on the hero's graphs does not make the
  client predict them.
- **Local prediction.** The statescript inner's vtable slots 0xd8/0xe0 set and clear a
  per-instance 0x400 bit (on instances with bit 0x8) plus execute bytes; dumps always
  show them clear, consistent with a per-frame begin/end bracket. Component 47's slot
  0x68 reports "locally owned" only when the entity's component 60 lists the selected
  entity; no entity in the world has component 60, and no definition or create flag adds
  it. How the original client gets local statescript prediction is still open.
- **Player info.** Component 74's s8 field 2 (component +0xf2) is the team (-1 = none);
  a native config-var evaluator (0xcf2120) returns it. Setting team 0 does not make the
  HUD draw. Create flag 0x80 on a hero with component 31 adds components 86 and 136
  (plus 69/122); create flag 0x20 adds 74; 0x10 selects the ownership builder.
- **HUD diagnosis.** The client itself spawns the HUD subtree under 0x0cb6 (0x2056,
  0x106b, 0x0dea, 0x0ec8, 0x1fc0) with negative (client-side) instance ids; all its UX
  presenters run and create widgets, and every referenced UI resource (0a88…) is loaded,
  but nothing draws. The visible hero-select presenter differs mainly in the root layer
  GUID (09a0…008c versus the HUD's 09a0…0571).
- **Ammo and continuous fire.** With the corrected decoder, primary fire is a held bit, so the
  private responder can keep the WeaponVolley state active while fire is held and drain
  the ammo sync var by time (liveblink160: one sustained volley, 40 rounds drained, then
  the automatic reload). With per-click pulses (liveammo159) five volleys empty a
  40-round magazine at 8 rounds each, the reload plays automatically and firing resumes.
- **Blink (not working).** Activating Tracer's BlinkEffect (0x24 state 6) with its Anim
  (state 11) through a full snapshot makes the client exit (liveblink160); the emulator
  stops at a null variable-type read after the same activation, independent of the
  state data supplied. Blink also needs the hero's movement, which the server does not
  simulate.

### Skinned creates: third-person heroes and training bots render (2026-10-15, runs 161-163)

- **Create flag 0x41.** In the entity-create flags byte (0x78dab0), bit 0x01 means a
  resource reference follows the flags byte; with bit 0x40 that reference is a skin theme
  (resource type 0xa6, GUIDs 0a50…), read by 0xdb1290 as one u32 (bit 31 = flag, low 31
  bits = skin index) followed by one bit (0x787be0). The client maps the skin through a
  world singleton (0xbb0c70 → 0x641af0) and keeps it with the new entity.
- **Visibility.** Non-controlled hero entities created without a skin are positioned (their
  movement snapshots apply) but are never drawn. Created with flag 0x41 and the hero's
  skin they render in third person: a Tracer entity with her first skin theme
  (0a5000000000170f, from the hero record's m_skinThemes) appears in the spawn room
  (liveskin162), and the practice-range training-bot record 02e0000000000170 (definition
  04000000000014d2, skin 0a50000000001afd) renders as the original white/red training
  bot (livebot163).
- **Positions.** Plain positions are readable from component memory in dumps (component
  1 +0x440 render position, component 4 +0x160, component 24 history). The spawn-room
  floor is at y ≈ 2.0; remote entities do not fall, so snapshots must use floor height.

### Entity updates and destroys; a working shoot-to-kill loop (2026-10-15, runs 164-168)

- **Module-4 ops.** The per-entity module-4 field is a 2-bit op (0x78bbc0): 1 create,
  2 update, 3 destroy. Ops 1 and 2 carry a 14-bit length and payload; op 3 has none.
  Queued records are applied by 0x78e300: op 2 looks the entity up and runs the same
  component-state body (0x78e5d0: u8 count, then per component u8 type, byte alignment
  at the absolute body position, u8 mask length, mask, primitive values) that ends a
  create; op 3 calls 0x78e4e0 and removes the entity (livebot165: the bot disappears).
- **Movement calibration (livecal166).** Yaw is the first s16 of a command
  (θ = a·2π/65536, −32768 at the practice spawn), pitch the second (negative = up).
  Forward is (sin θ, 0, cos θ) and right is (−cos θ, 0, sin θ); the second movement axis
  is forward (W = +127) and the first is right (D = +127). One second of W moved the
  hero 5.94 m and one second of D 6.39 m (≈ 6 m/s at 62.5 commands per second), so the
  server can estimate the player's position from the command stream.
- **Shoot-to-kill.** The private responder tracks the player from the spawn with those
  axes, ray-tests each command while the weapon volley is active against each bot's body
  (centered about 2.4 m above its origin), lowers the bot's component-51 health with
  throttled op-2 updates, destroys it at zero and re-creates it (skin, health, position
  snapshots) after 3 s. livekill168: tracers hit the bot, it disappears after 200
  damage (53 server-side hits) and respawns.

### Client-local game messages, HUD layers and server-side movement abilities (2026-10-15, runs 174-177)

- **No generic server→client game-message record.** The 20300-family channel-0 handler
  set has no "game message to entity" record. 20315 (string, u64, selected entity, u32,
  f32) compares a string and then raises one fixed local message; the client handles no
  incoming 21600-family records (the client only sends 21616).
- **Client-local delivery works.** Client-only `StateGameMessageEntry` nodes register a
  local listener; local messages are dispatched through the root object's message
  router (build message, set its GUID with 0x1ba7e20, router = root vtable +0x110,
  dispatch = router vtable +0x18). A client-only "send game message" state
  (STU_38EE1100) is entered by ordinary server state data: creating the client-only HUD
  root graph 0x0cb6 on the controller and activating its state 3 makes the client send
  0x0240000000000717 itself, and the client-spawned 0x106b receives it (both of its
  0x0717-triggered stacks become active; livehudmsg177). This is a general way to
  deliver a message to client graphs when such a send node exists.
- **UI layers are named.** UI layer resources (09a0…, "DUTS" format) carry view names:
  0571 `HUD_Elements_Objectives`, 0502 `HUD_Root`, 059d and 05d0 `HUD_Hero_Common`,
  05a7 `HUD_Hero_Common_Animated`, 00f3 `HUD_Tracer`, 008c `HeroSelection2`. The 0a88…
  resources only declare a presenter's bindable properties (for 0571: container, an
  int, and the bool 07aa that the presenter sets to `!0x2246`).
- **The hero HUD is not 0x106b.** 0x106b presents the objectives panel. Hero HUD
  presenters (`HUD_Tracer` from Tracer's graph 0x3d; `HUD_Hero_Common` from graphs
  0x01cf/0x20e4) were present with widgets in earlier runs but drew nothing.
- **HUD_Root is native.** No statescript graph references `HUD_Root`. It is created by
  a native state class (vtable 0x26337e8; a 15-way mode switch at +0x1d8 calls 0x9cf9b0,
  which creates layers 029b, 029c and 0502). That state is state 15 (STU_501733D7) of the
  UI graph 0x120b. 0x120b is run by the client UI root graph 0x041a (state 25), which
  lives on a separate client-only statescript component (47 local instances). Its
  BooleanSwitch (state 20) is true when any of five native predicates is true:
  AECBBA41 on an entity reference (8985E00A), global var 0x09ba, F94506DB and B4F19440,
  CEFF290A, or E95A9C77. In our sessions this switch stays false, so `HUD_Root` is never
  created. What makes these predicates true in a normal game is the next HUD question.
- **Movement abilities (server side).** The private responder now implements Tracer's
  Blink (ability-1 press: 7.5 m along the movement input, or forward when idle; three
  charges recharging 3 s each) and Recall (ability-2 press: back to the tracked
  position 3 s earlier, 12 s cooldown) as position snapshots (fields 16-18). Blink from
  the spawn moves Tracer to the spawn-room door with the bots visible outside
  (liveblink176). The server has no collision data, so its tracked position can be
  wrong: a teleport into geometry is resolved by the client onto the top of the rock
  mass near (52.5, 30, 14.3). The local hero's component-1 render position is not a
  reliable position probe until the hero has moved.
- **HUD chain to the client-mode byte (runs 178-180, emulated on dumps).** The UI
  statescript entity (definition 04000000000001f1, root graphs 0x041a/041b/041c) is
  owned by the global client root, not by a world, so "local player" predicates that
  resolve through a world owner (AECBBA41 on entity reference 8985E00A) are always false
  for it. The UI manager (vtable 0x26552a8) updates UI-entity globals every frame
  (0xafd550): var 0x04d2 = (client mode byte == 5) and var 0x1c8d = (client mode == 9),
  plus 0x08e3, 0x0522, 0x0a0d and 0x1df3 from other native state. The mode byte is
  behind an encrypted pointer in a client game object (predicates 0x5981f0/0x597ba0/
  0x597240/0x597880/0x597560 test modes 3/5/6/8/9). Our Practice Range join leaves the
  client in mode 6, so UI graph 0x046b's first switch (0x04d2 or 0x1c8d) stays false. That
  graph would otherwise send local message 0x05ce carrying graph 0x0bce; 0x0bce writes
  var 0x09ba, which is the term of the UI root's condition (0x041a state 20) that can
  become true. Only then does 0x041a run 0x120b, whose state 15 is a mode state machine
  (vtable 0x26337e8; step 4 = 0x9cf9b0) that creates the HUD layers and sets HUD_Root's
  bool 0d80…6729 (HUD_Root properties are 6720 and 6729). The UI manager's own HUD_Root
  widget already exists but stays hidden.
- **Things that did not open the HUD.** Activating 0x120b state 15 on the controller
  (run 178): the state enters but its loader stays in mode 0 waiting for a native job
  (set by events of types 0x2def1c0/0x2def1d0). A non-empty 20300 settings string
  (+0x80/0/0/+0x110 and +0x4d8, run 179b): the strings arrive, but predicate CEFF290A reads
  a different session string. Referral 20600 +0x28 = 1 instead of 2 (run 180): the client
  stays in the Training menu, so 2 is required for the Practice Range.
- **Prediction gate.** Statescript prediction (0x64d990) first requires a global byte
  (image +0x2f7f840) that is 0 in our sessions. The earlier "entity component 60" reading
  of the next check is correct (0xbc18d0 tests component bit 60), but the global gate
  comes first. The writer of that byte has not been found.
