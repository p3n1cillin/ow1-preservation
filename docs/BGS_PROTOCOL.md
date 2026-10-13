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
Which flag-2 message the client expects in reply is not yet identified. No
menu, map or gameplay is established.
