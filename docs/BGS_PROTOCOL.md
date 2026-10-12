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
starts with byte 1. Its application schema/required reply remain unverified;
the probe observes it and keeps the connection open until the client closes.
No main menu, map, hero or gameplay is established by this handshake.
