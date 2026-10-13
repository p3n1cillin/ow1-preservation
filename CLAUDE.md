# OW1 preservation continuation

Continue the existing implementation; do not restart or replace working systems.
Work in the project directory `Y:\repos\WIP\OW1` (the UNC path is equivalent),
as requested by the user. New private research/run artifacts belong in ignored
`.local/` here. Reuse the existing original client, keys and native build cache
as inputs; do not create a separate source checkout or scratch workspace.
Public AGPL-3.0 fork: https://github.com/p3n1cillin/ow1-preservation.
Upstream: https://github.com/saturn-xvi/prometheus. Active branch is `main`, which
includes `codex/public-preservation` and Claude's continuation. Historical
`preservation-foundation` is a parallel private development reference; do not
merge or publish its history without checking what it contains.

## Active client and local files

Target **1.74.0.0.104319**, supplied as
`C:\Users\lukem\Downloads\Overwatch1.74.0.0.104319.7z`.
The 1.0 ISO is gone and is not required for current development.
Original executable SHA256:
`ef67d348ecca066ce1698683fd0fd810075357164b345d83ed9296d676e0ebe2`.
The extracted client, outputs, captures and generated reports are available under
`%LOCALAPPDATA%\OW1-preservation-build`; check before extracting again. They may
resolve through Codex's package-local filesystem virtualization. Keep original
client/archive unchanged on disk and proprietary bytes outside Git. Never
publish credentials, keys, generated certificates, dumps or client assets.
Research checkouts in `Y:\repos\WIP\OW1-research` include unlicensed projects:
reference only; do not import their code or bundled credentials.

## Commands

```powershell
.\scripts\Build.ps1 -SkipDependencies
ctest --test-dir "$env:LOCALAPPDATA\OW1-preservation-build\relay" -C Release --output-on-failure
.\scripts\Start-RetailClient.ps1 -Mode PracticeMetadata
.\scripts\Start-PrivateClient.ps1 -RunForSeconds 90
```

Omit `-SkipDependencies` for a first build. Build.ps1 uses VS 2022/v143 or
VS 2026/v145 and preserves an existing CMake generator. Private diagnostics need
`tools/bnet-probe.py` with our own local certificate/key and host port 21119.
The client sees container loopback port 1119 through a named-pipe bridge.
No Internet/LAN capabilities are granted. Bounded runs stop owned jobs, save
a local dump and restore scoped ACLs. Wait for launcher exit before checking
restoration or rebuilding its executable.
Private launcher logs now default to project `.local/runs`; `-LogRoot` can
select another directory. BuildRoot still selects the existing native executable.

## Real frontier, 2026-10-13

- Final 1.74.0.0.104319 client reaches real TLS 1.2, WebSocket RPC, local
  'Pro' account login and Balancer referral. Use mapped-loopback cert CN/SAN
  `::ffff:127.0.0.1`, CA import and native socket CA setter; keep BNetServer IPv4.
  Earlier handshake-only/error-1016 descriptions are historical, superseded.
- Own-key lobby credential now passes the ORIGINAL native RSA/address/HMAC
  checks. `-TrustLobbyKey <public.modulus>` installs exactly one guarded heap
  RSA-2048/e=65537 modulus per launch; original allocation/ownership remain.
  Requires bounded loopback `-TrustCaCertificate -ObserveTls -TrustSocketCa`.
- Lobby server sends a **Panama-LE encrypted 292-byte packet**, comprising
  credential[256], two 128-bit identifiers, one uint32. Client receive key is
  HMAC(k2,CR|SR), send key HMAC(k3,SR|CR); key also serves as IV. Native transport
  at RVA 1909547 waits for 0x124 bytes. Sending only 256 raw bytes times out.
- Positive runs 2/3 reach native handshake state 6 / connection phase 6 and
  send 13 encrypted bytes. These decode to a 3-byte BE length plus a 10-byte
  body starting with 1: the bootstrap negotiation offer `01 00 | u32 1 |
  0x11d82194` (entry byte, message id - base, u32 hash vector).
- GATEWAY NEGOTIATION SOLVED (2026-10-13, retail-ack run): reply `01 02`
  (empty message id 3; `bnet-probe.py --gateway-reply ack`, the default). The
  client (ctx+0x84 bit 0 clear) enters negotiated state 5 and sends `01 03`
  heartbeats every 5 s; the probe echoes them and the lobby stays open until
  the bounded run ends (112 s, 22 heartbeats). id-1 echo and decoded id-2
  replies close immediately (role/bit-0 checks). Wire format and native RVAs:
  docs/BGS_PROTOCOL.md "Gateway negotiation messages".
- Control without our heap key closes immediately upon the same own credential,
  sends no post-handshake packet and retries referral. Original checks stay on.
  Main menu, persistent gateway session, rendered final map, controllable hero,
  authoritative multiplayer and 6v6 are **not verified**.
- Own private key, public modulus, local integrity input, certs and dumps stay
  outside Git. Own key copied from Claude's package cache to this app's local
  `OW1-preservation-build/private-mapped-ca/lobby-key.pem`. Corresponding
  `lobby-public.modulus` and `lobby-integrity.credential-key` are prepared there.
  Never publish the 64-byte client-local integrity constant or proprietary image.
- `tools/lobby_credential.py` prepares local inputs and verifies own RSA roundtrip.
  `tools/panama_stream.py` independently implements Panama-LE and passes the
  public Crypto++ reference vector. Framing tests include one-byte TCP fragments,
  directional cipher mapping and omission of message/session contents.
- Native logs/dumps: retail-private-own-lobby-key1/2/3 and
  retail-private-original-lobby-key-control. Server logs under private-mapped-ca.
  Stop previous probe on 21119 before any run; exclusive socket bind prevents
  accidental sharing. Wait for owned client exit before rebuilding/testing ACLs.
- Private launches automatically disable the guarded ShowIntro option: skip the
  cutscene ourselves. Current computer-use `@oai/sky` window capture works;
  native state does not
  establish a rendered world. No debugger attachment mode is shipped.
- Map track: original Practice header loads, default loading context activates,
  updates return state 4, but readiness/cache remain zero. SDK kind 13 is LOCAL
  Hotfix enumeration, with structured error status/tag/code 3/2/-1 at +18/+19/+20.
  +138/+140 are successful data/count. Never fabricate completion/readiness flags.
- Original final executable hash/signature are unchanged. Candidate mapped-page
  code writes fail Win32 87; ACG is not established (policy flags zero). Don't
  repeat failed hardware-debugger experiments as working diagnosis.

Use `--lobby-peer-group 13 --gateway-catalogue protocol/gateway-104319.json`:
the client then offers all 86 lobby protocols, negotiates and sends hello
21800 + 21809 on protocol 0x3c7e3468 (entry 25). Add
`--lobby-login-schema protocol/lobby-login-104319.json` for the live-verified
initial identity reply 20500 (protocol 0xf5ff548a, sorted entry 83). Native
20500 handler 0x774710 calls 0x6261e0 to install identities/strings and raise
event 13; direct window capture in `lobby-identity3` showed **ENTERING GAME…**.
That identity-only connection sent no further application requests before
bounded shutdown. New opt-in `--lobby-initial-data keys-hotfix-player` sends
empty 20504 key lists, empty 20505 hotfix lists and our local 20502 player
record. All three original handlers are traced. The key context's +0x40 changes
0 -> 1; the player experiment then sends 60002 (entry 29/schema 0x49963fa6)
and repeating 42600 (entry 80/schema 0xeb45ad29). Window captures are black,
with a healthy connection; main menu remains unverified. Read-only snapshot:
`python tools/retail_login_state.py --dump <owned-dump>`. It reports booleans
only. The slot-22 +0x88 player marker is transient/meaning not fully established;
it is false in the finished player run. Never label it persistent receipt.
World state (2026-10-13): at ENTERING GAME the world-state manager (vtable
0x02655d88, +0x18 state, names SHUTDOWN..WORLD_RUNNING) is WAITING with no
pending world request; `retail_login_state.py --world-state` reports it. World
requests enter via 0x00b4b1c0 (callers 0x0082c3e0 game-server join,
0x008359a0 local world, 0x00b97f40 from the 20300 game-server dispatcher).
`--lobby-initial-data keys-hotfix-player-settings` adds default 20802 account
preferences: accepted; client then reports 58400 (0x692c511b) every ~30 s;
world state still WAITING/no request (run settings2).
MAIN MENU REACHED (2026-10-13, run screen8, desktop unlocked): full initial
data incl. 20802 -> original main menu + first-run TUTORIAL prompt. Current
Computer Use screenshots/input work through @oai/sky; prefer that plugin.
The "time out communicating with Battle.net" screens came from leftover clients
whose server had stopped. Current bounded diagnostics terminate their owned
client/job, write a private dump and restore scoped ACLs at the end.
Accounts/launcher: `python tools/ow1_launcher.py configure|create|list|play`
(tools/accounts.py, store in .local/); `play Mercy` reached the menu as Mercy#1002.
Reliability (2026-10-13): 27/27 unattended launcher sessions reached the menu.
`play` waits for an exiting client/port and retries an instant client exit
(single-instance game). Don't drive the game window with desktop automation
during login; use the Computer Use plugin after the main menu appears.
Related 59900-family handlers print account-migration data; 42400-family
handlers process tournament data. Exact reply pairing/menu dependency remains
unresolved. Next: trace initial account/configuration/loading/menu gates; do not
blindly send all registered messages. 20801's traced handler only prints account
information. Field meanings beyond observed identities remain experimental.
Public numeric descriptors (20500/20502/20504/20505/21800/21809) contain no payloads. The bounded
codec exactly roundtrips all 216 private hello-body bytes. Fourteen probe
fixtures grew to fifteen, and all 14 CTest targets pass. Gateway codec: send 0x00560d90 ->
0x00568690 -> 0x005652b0; receive 0x00561ff0 -> 0x00567de0 -> 0x005670e0;
per-state timers 0x00560b50/0x005609c0. Do not invent application replies.
A final repeated player run (`initial-focused1`) confirms the same service
requests. `@oai/sky` focus failed with `GetCursorPos ... Access is denied
(0x80070005)`; refreshed selection found no window after bounded exit. The
user already reported the desktop unlocked; do not infer a locked desktop or
claim successful foreground verification. Screenshot-only captures are black.
The 36-byte credential suffix is currently server-local group-13 ids
`((13<<40)|1,1),((13<<40)|cid,1),0`; its other field semantics still need
verification. Do not invent gameplay
from handshake success. Refer to FINAL_RETAIL.md current reproduction checkpoint
and docs/BGS_PROTOCOL.md for the tested protocol boundary.

`server/` is a synthetic BSON movement relay, not final OW1's protocol.
`prometheus/` is the fixed-offset beta DLL, not a retail adapter.
Final probes live in `tools/offline-launch/`; use their exact-build guards.
No Blizzard production credentials/endpoints or third-party private keys.

See `docs/PROJECT_STATUS.md`, `FINAL_RETAIL.md`, `ROADMAP.md`, `RESEARCH.md`,
`COMPATIBILITY.md`, `FEATURE_MATRIX.md`, `TESTING.md` and `DEVLOG.md` for the
existing status/research/matrix/test/log equivalents requested in the handoff.
Distinguish implementation, compilation, synthetic tests and native runtime
evidence. Successful relay tests do not complete original-gameplay milestones.

## Latest Training checkpoint (2026-10-13, instance-public1)

Continue from the current menu/Training implementation, not the historical black
window notes above. `@oai/sky` directly captured the original main menu and drove
No Thanks -> Training -> Practice Range in this run. No focus workaround was
needed. Use the Computer Use plugin for Windows UI when available.

- Public opt-in: `--lobby-instance-referral --lobby-instance-schema
  protocol/instance-104319.json`, with initial-data `full`. It answers only the
  observed Training 24000 shapes (mode 2 or 3, empty name, final integer 4).
- 20600/schema 0x074dad18 -> original handler 0x775cd0. Outer +0x78 false skips
  the conditional transform. Native '%s:%d' uses nested host +0x2e/port +0x2c;
  our endpoint is exactly 127.0.0.1:1119. Local generated session inputs only.
- 0xe3e940 creates a referral job through 0xe1e6f0 in component slot 120
  (vft 0x26775f0, job pointer +0x20). Immediate read-only checks saw the job in
  both referral-plain3 and instance-public1. This proves handler/job acceptance,
  not a complete queue reply sequence, successful connection or gameplay.
- The original consumer 0xe3e700 compares the job's initial integer, copies its
  parameter prefix and clears/frees the job. Later snapshots are false; do not
  label that rejection or persistent completion. The meaning of +0x28=2 and
  remaining referral fields is still experimental.
- `tools/retail_login_state.py --queue-state` guards image/root/context vfts and
  emits counts/booleans only. Native queue component slot 38 is vft 0x2610c68;
  root+0x220 queue-service vft 0x260cd68 owns four record lists.
- All 34 numeric 23300-family layouts are in protocol/queue-104319.json. The
  explicit empty-notification control is `--lobby-queue-schema <that file>
  --lobby-queue-reply <id>`; cannot combine with instance referral. Not enabled
  by the default account launcher. No successful game allocation is invented.
- 180-second public run: UI stays ENTERING PRACTICE RANGE, no extra TCP
  connection, final world WAITING/no request, queue records [0,0,0,0].
  Next trace the queue assignment and instance job consumer/transport. Do not
  assume the game protocol is the BSON relay or the raw lobby protocol.
- Private logs/snapshots/harnesses: project .local/. Dumps retained beside the
  existing client: retail-private-referral-seed0.dmp,
  retail-private-referral-plain2-startup.dmp, retail-private-referral-plain3.dmp,
  retail-private-instance-public1.dmp. First seed0 prototype had a mismatched
  outer transform flag; it is not a valid protocol-rejection control.
  Plain1/plain2 failed before application traffic (TLS context/suspension guard).
  Known 1090-byte mapped CA with TLS delay 15 worked in subsequent runs.
- All 14 CTest targets pass, including 24 probe fixtures. No native code,
  readiness or verification flags were changed for the instance experiment.

## Latest transport checkpoint (2026-10-13, instance-udp1)

This supersedes the instance-public1 transport frontier above. Work stays in
the project directory; all new private RE and run files are in ignored .local/.

- Corrected 20600 nested +0x6e: it is an IPv4:port endpoint, not a token.
  Native job +8 holds this string; callback 0x7daf70 -> 0x7cc690
  (ConnectToInstance) calls parser 0x41ef00 at 0x7ccbf6. Both referral address
  forms now use 127.0.0.1:1119. Keep outer bool false and original verifiers.
- Instance connect: 0x7cc690 -> 0xc68980 -> 0x3fc550 -> 0x3ff920. Selector
  byte RVA 0x2e2f308 is zero in the inspected run, selecting alternate peer
  path 0x40009d -> 0x3f8990. Do not overwrite the selector or force TCP.
- Original bridge was TCP-only. New explicit launcher `--udp-forward
  1119:21120` / Start-PrivateClient.ps1 `-UdpForward 1119:21120` adds a UDP
  bridge through an owner/AppContainer-only named pipe. It requires normal
  TCP 1119:21119, exact BNetServer loopback and a 1..180-second duration.
  One source port per run, <=4096-byte datagrams; no Internet/LAN capability.
- Start receive-only `python tools/instance_probe.py --run-for 180 --log
  .local/runs/<unique>.jsonl` BEFORE the client. It binds host 127.0.0.1:21120
  and logs sizes/counts only. Use the existing full initial-data / opt-in
  instance-referral bnet probe on TCP 21119. Known private-mapped-ca 1090-byte
  root / 15-second handshake delay worked in both new native runs.
- Direct @oai/sky screenshots/input: No Thanks -> Training -> Practice Range
  causes 24000 -> corrected 20600. The observer receives 39 original-client
  datagrams, all 34 bytes. Bridge totals: outbound39/inbound0. The native job
  is present immediately, later absent. The entering overlay eventually clears
  back to Training. Final world WAITING/no pending request, no map or hero.
- **Next: trace the native 34-byte datagram handshake and its reply**, using
  original receiver/state transitions and locally generated referral inputs.
  A received packet is not an authenticated game session. Do not assume BSON,
  the lobby raw handshake or a tournament pending-game path is the game protocol.
- New private dumps beside existing client: retail-private-instance-endpoint1.dmp
  and retail-private-instance-udp1.dmp. Private .local/re/instance-*.txt contains
  bounded disassembly/callback analysis; .local/runs/instance-udp1-final.json
  and instance-udp1-cleanup.json record state/cleanup without session bytes.
- All 16 CTest targets pass: 24 bnet fixtures, 2 observer fixtures plus native
  UDP/pipe boundaries/guards/shutdown and isolation tests. Original EXE hash/
  signature and both baseline ACLs match; no owned native processes/listeners.
  Default account launcher is still the existing menu path.

## Latest datagram checkpoint (2026-10-13, udpcap2..udpreply6)

Supersedes the "Next: trace the native 34-byte datagram" line above.
- Instance packets are AES-256-GCM: key = referral +0xae, nonce = 8 zero bytes
  || u32 LE seq, 22-byte header (ver2<<4|type, seq, +0xa8, u64 +0x140, flags,
  0xad) as AAD, 12-byte tag at the front. Verified by exact regeneration.
  Table: docs/BGS_PROTOCOL.md "Instance datagram format".
- Sealed replies (key +0xce, types 1..15, flags1) were delivered and ignored.
  The user's later explicit request to continue key-handling disassembly is
  handled in the checkpoint below; earlier key/nonce guesses are superseded.
- Private helpers in .local/re: run-capture.ps1 (probe+capture/responder+client),
  probe_record_inputs.py, udp_capture.py, udp_aead_reply.py, aead_search.py,
  dump_on_datagram.py, dump_scan.py, stack_scan.py. Run the launcher with
  `-UdpForward` (≤180 s). Leave the game window alone until the menu; then
  click/view through Computer Use with fresh returned screenshot coordinates.
  Do not assume a fixed frame scale or reuse stale window/screenshot handles.

## Key-handling disassembly checkpoint (2026-10-13)

- Continued from Claude's latest files in the project. Existing uncommitted
  datagram notes were preserved. The user explicitly requested the scrambled
  key path. New private disassembly/reconstruction files are in .local/re/.
- Mid-send dump is actually in Claude's package-local input cache:
  C:\Users\lukem\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Local\OW1-preservation-build\dumps\instance-sending5.dmp.
  Reuse read-only; do not copy the client image or create another workspace.
- 0x3fa810 decode / 0x3fa380 encode: recovered aligned jump targets across
  opaque branches; eight arithmetic inverse operations. Linear disassembly
  drifts into junk. Function .pdata fragments can chain: follow UNW_FLAG_CHAININFO
  (private unwind_chain.py), not just the fragment enclosing a call.
- Private decode_instance_key.py reads only the dump, reconstructs both codec
  blocks, compares with OUR udpcap5-generated +0xae/+0xce values and reports
  booleans/counts. Both keys match exactly and both nonce prefixes are zero.
  verify_instance_key_reconstruction.py: 4144 bidirectional primitive checks,
  both 40-byte blocks re-encode exactly, and all 39 client/all 39 server udpreply6
  packets authenticate independently. No key bytes are printed or published.
- Correct codec roles: peer+0x10 SEND/+0xae, peer+0x18 RECEIVE/+0xce.
  Native constructor 0x3f89e0, sender 0x3f96d0 and receive call 0x402bdc agree.
  Earlier Claude slot labels were reversed; server +0xce key hypothesis was right.
- Received authenticated packets: 0x4027f0 -> codec-open -> 0x401880 queues at
  peer+0x188 -> 0x401500 -> 0x3f94f0. Native peer state 1 requires(flags&3)==3
  at 0x3f95c4; flags 1 cannot advance. State 3 checks flag mask 2 plus later ack sequences.
  0x3f9fc0 sets/shifts peer+0x140 as received-sequence BITMAP, not connection id,
  and updates +0xa8 to receivedseq+1. Do not patch any of these fields.
- Latest private files: instance-key-*.txt, instance-receive-*.txt,
  instance-authenticated-handshake-dispatch.txt, instance-handshake-flags.txt;
  reports .local/runs/instance-key-decode-peer-continuation.json and
  instance-key-reconstruction-verified.json. Public docs contain semantics only.

## Native flags-3 checkpoint (2026-10-13, udpflags7)

- Private responder: type 0/flags 3, +0xce own key, zero nonce prefix, ack=client
  sequence, bitmap 0, empty body; bounded 180 seconds/max 100 replies. This is a
  handshake experiment, not the final ack/reliability implementation.
- Fresh Computer Use selected No Thanks -> Training -> Practice Range after
  the menu. Original UI showed ENTERING GAME; no map rendered. Client progressed
  to flags 2, advancing next-sequence/receipt bitmap, then nonempty type-1 packets.
- Bridge outbound 161/inbound 100. Independent cryptography validation and public
  tools/instance_datagram.py authenticate/reseal every packet exactly. Nonempty
  body sizes 13/33/43/63/73/93/103/123; neither full lobby bootstrap offer nor
  three-byte lobby framing matches. The private responder's old tag_ok=False
  on nonempty packets is an empty-body-only checker artifact.
- Reports: .local/runs/udpflags7-authenticated-summary.json,
  public-instance-codec-native-validation.json and udpflags7-final-state.json.
  Dump beside existing client: retail-private-udpflags7.dmp. Captures/inputs and
  key reconstruction stay private. Do not print their payloads or key bytes.
- Bounded final world WAITING/no request; queues 0/0/0/0, referral job absent.
  Original EXE SHA256/signature and both baseline ACLs match. Owned native PIDs
  and TCP 21119/UDP 21120 listeners are gone. Stale window handles were discarded;
  no post-shutdown game UI is claimed.
- Rebuilt native targets; all 17 CTest targets pass, including six synthetic
  instance datagram fixtures. No native state/verification/readiness patched.
- Next: trace authenticated type-1 reliable-message framing and application
  negotiation before attempting a game/map reply. Keep native peer transitions
  intact; do not confuse envelope authentication with complete gameplay.

## Receipt/body continuation (2026-10-13, udpack8)

- 8540434 Windows CI passed. Continued in the project; private follow-on trace
  is .local/re/instance-payload-frontier.md and instance-upper-event-*.txt.
- Mid-send dump: active transport vtable 0x2616458, seven modules, verified by
  .local/re/instance_active_transport.py. Interface report in
  .local/runs/instance-active-transport-continuation.json. Event 4 from 0x401740
  ->0x3fc1b0 queue/core+0x3a0 ->0x3fc650 ->0xc68c30 ->vtable+0xb0/0x7ce110.
  Separate 0xe3af00 expects 32-byte control packets; don't assume that path active.
- Original receipt updater 0x3f9fc0 advances to receivedseq+1 and shifts/sets
  its receipt bitmap; old sequences are rejected. bit 0 acknowledges nextseq-1.
  Public ReceiptWindow matches this bounded, no-wrap behavior. Authenticate
  before recording; never start sequence 0 again with the same GCM key/prefix.
- Private .local/re/udp_receipt_reply.py uses public codec/window, fully opens
  payloads, one authenticated source port, metadata-only stdout, 180-second bound.
  Connect reply flags 3; later flags 2. No application payload replies. Own inputs
  generated by probe_record_inputs.py; captures/inputs remain ignored.
- udpack8: bridge 225 out/224 in; capture 224 client/224 server, all exact GCM
  roundtrips/receipts. Payload sizes: 0 bytes (75 packets), 13 (4), 33 (145); no 43..123-byte bodies in this interval.
  This changes ack/bitmap AND normal flags; don't attribute it to one field alone.
  Observer ended before client's 150-second bound; no long-term stability claim.
- Fresh Computer Use: No Thanks -> Training -> Practice Range -> ENTERING GAME,
  later Training. No rendered map. Final world WAITING/no request, queues all 0,
  no referral job. Hash/signature/ACL audit passes; owned processes/listeners gone.
  Dump retained beside client as retail-private-udpack8.dmp. Reports in
  .local/runs/udpack8-verified-receipts.json, udpack8-final-state.json,
  udpack8-cleanup.json. Discard the old owWindow8/owState8 bindings after shutdown.
- Client receive0x7ce110: compact u32 -> first 6 module prefixes -> seven-bit
  message count -> encoded identifier -> module presence/handler calls.
  Read bits0x78bdb0 is LSB-first; compact u32 reader 0xdb0e60 widths18/24/32.
  Independent tools/instance_bits.py primitive validated against all 138/149
  nonempty type 1 bodies' first compact field (19 bits). Later blocks include
  reliable-module presence; first small sampled prefix report wasn't the full run.
- Modules' numeric vtables (in order):26167c0,263c3c8,260e2b8,2616350,2615850,
  2617c58,2615fe0. Reliable module 0 receiver 0xc6a480 / writer 0xc6ade0;
  module 3 receiver 0x7c0630 / writer 0x7c0930 ->0x7cc060. Body writer loop candidate
  0x7cf479; inspect aligned0x7cf386 across the opaque jump, not junk after0x7cf342.
  Private instance-module-prefixes.txt / instance-bitstream-primitives.txt /
  instance-outgoing-module-writers.txt hold read-only disassembly.
- All18 CTest targets pass:8 envelope/window fixtures and4 bitstream fixtures.
  Next: complete conditional reliable-module framing and the application
  negotiation message before generating an engine-level reply. No readiness,
  transport or verification flags are patched.

## Game-server welcome checkpoint (Claude, 2026-10-13, udpapp9)

- Codex's uncommitted public reliable-record codec (21610/21627) passes: all 19
  CTest targets, exact roundtrip of 138+149 captured client bodies.
- Server->client body (receive 0x7ce110): compact server frame, module prefixes
  0..5, 7-bit entity count. Reliable mod0 = present bit, 4b primary, 4b
  secondary, byte-aligned records; mod1/2 empty; mod3 compact ack frame + 4 flag
  bits + time bit(+16); mod4 bit must be 1; mod5 bit-terminated lists. Codex's
  draft --app-empty body misplaced mod3's time bit; it was never run.
- Instance carries 11 reliable channels; **channel 0 = 20300 family**
  (schema 0xc77f6403). 20300 handler 0x7d9400 directly calls world-request path
  0xb97f40 after checking +0x500 == 16000 (quanta) and +0x519 == false.
- Private: .local/re/instance-welcome-frontier.md, instance-channel0-messages.json,
  udp_welcome_reply.py, run-welcome.ps1. udpapp9 reached login, but Computer Use
  screenshots on both monitors were fully masked, so Practice Range was never
  selected (0 datagrams). Re-run when the game window can be captured/driven.
  Cleanup, listeners and original EXE hash verified.
- udpapp10 (user clicked Practice Range): the client accepted the default 20300
  welcome and immediately sent a new reliable 21600 (channel 1: local name,
  zeros, empty blob) = client join. World stayed WAITING/no request; referral
  job present at shutdown. Next: fill 20300 settings (+0x80) with a real map/mode.
- NEVER call computer-use open_application for Overwatch: it started an unbounded
  second client from the package-cache path (killed after ~20 s). Computer Use
  grants that package path, so the bounded client (real LOCALAPPDATA path) is
  masked; ask the user to click No Thanks -> Training -> Practice Range.
- UI driving: do not use Computer Use for runs. `.local/re/ow-ui.ps1 -Action
  shot|click` captures the owned window via CopyFromScreen and clicks client
  coords (2560x1080: No Thanks 2100,1006; Training 471,325; Practice 1279,538).
- **FIRST PENDING WORLD REQUEST (udpapp11):** 20300 +0x4a8 = Practice Range
  header GUID 0x0790000000000688 becomes the world request's first field; both
  world managers then hold a pending request (previously none). State stays
  WAITING; UI ENTERING GAME. udpapp12 added 21610 pong echoes: no change.
  Dumps retail-private-udpapp10/11/12.dmp beside the client. Next: find what
  advances WAITING+pending (server frames/module-3 time, snapshots, hotfix).
