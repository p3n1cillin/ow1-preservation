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
