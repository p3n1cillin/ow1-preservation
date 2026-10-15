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
- Historical Claude runs used `.local/re/ow-ui.ps1` for screenshots/input.
  Codex must follow its Computer Use skill for Windows automation; do not mix
  PowerShell UI code into those turns or reuse historical coordinates.
- **FIRST PENDING WORLD REQUEST (udpapp11):** 20300 +0x4a8 = Practice Range
  header GUID 0x0790000000000688 becomes the world request's first field; both
  world managers then hold a pending request (previously none). State stays
  WAITING; UI ENTERING GAME. udpapp12 added 21610 pong echoes: no change.
  Dumps retail-private-udpapp10/11/12.dmp beside the client. Next: find what
  advances WAITING+pending (server frames/module-3 time, snapshots, hotfix).
- udpapp13 (type-1 frame on every reply), udpapp14 (empty local Hotfix dir),
  udpapp15 (settings +0x128 = same GUID): all still WAITING + pending, referral
  job present. 20301 = settings update (installer 0x587e10). A second join flow
  exists: queue session start 0x828580 -> 0x8357a0 -> local-world builder
  0x8359a0.
- udpapp16/17 (black-box): 20301/20302/20322 follow-ups, module-3 time and
  welcome +0x78/+0x4b0/+0x518 changed nothing (WAITING + pending). Untried:
  entity snapshots/module-5 lists, settings-record contents, queue join flow.
  Dumps now land as retail-private.dmp; rename to the run name afterwards.
- udpapp19/20: OW1_QUEUE_FIRST=23311|23332 (private probe_record_inputs.py)
  sends an empty queue notification before 20600. 23332 accepted (marker),
  still WAITING + pending. Queue pending-game path = tournament (spectator-
  like session), not Practice Range. Remaining black-box levers are blind
  (entity snapshots, settings record); next needs a decision from the user.
- udpapp21 (settings sweep, user-chosen): game-mode GUIDs are type 0xC5
  (0x0230...); low parts = public decimal mode ids, Practice Range = 0x5a.
  Welcome +0x130 = 0x023000000000005a with map in +0x4a8/+0x128: still
  WAITING + pending, same client messages. Next settings levers: +0x138,
  32-byte +0x4b4, u64[] +0x520 (no basis yet). Notes in
  .local/re/instance-welcome-frontier.md.

## WAITING resource gate continuation (Codex, 2026-10-14)

- Followed aligned branch targets through opaque padding: world tick
  0xb4b5f0 -> switch at 0xb4cca8 -> WAITING handler 0xb52b20.
- Handler normalizes the request's low u32 to map-header type 0x9F; checks
  catalogue availability with 0x171b800; polls load status with 0x171c0b0.
  Status <2 returns; status 3 calls 0xb523f0 and enters state 3 (ABANDONING
  SCENES). Other statuses >=2 take the error path. No native gate patched.
- Read-only reinspection of udpapp11/21: both pending managers' Practice
  headers exist in the catalogue but have no load-cache object (status 0).
  Resource cache has 28 other entries. udpapp21's optional mode resource also
  exists without a load-cache object. udpapp10 has no pending request.
- Public `retail_login_state.py --world-resource-state` reproduces these
  booleans/counts/statuses. Private arithmetic interpretation confirms its
  independent CRC lookup against the native hash routine; no table/key bytes
  are exported. Reports: .local/runs/udpapp{10,11}-resource-gates.json and
  udpapp21-public-resource-check.json. Private trace: world-waiting-22*.txt.
- Added observed common-channel 21600 layout and ignored boolean padding to
  the independent codec. 1003 complete bodies across udpapp10/11/21 open and
  re-encode exactly: 3 joins, 974 21610s, 26 21627s. No captures published.
- Build and all 20 CTest targets pass (5 reliable fixtures, 4 resource-state
  fixtures). Stopped the stale owned udpapp9 BGS process after checking its
  command line. No new interactive game run occurred in this continuation.
- Next: identify the normal client/server path that requests and retains the
  map-header resource. Existing standalone PracticeResources proves native
  resource request 0x171e8e0 can load it; invoking that adapter is a diagnostic,
  not completion of the original application negotiation.

## Latest native metadata checkpoint — 2026-10-14, udpmeta26

- Work stays in this project. Use the existing original client explicitly from
  Claude's package cache for bounded live launches; Computer Use capture/input
  work from that path. Do not use `sky.launch_app` for the game or infer the
  desktop is locked. The last run's window disappears at its bounded exit.
- 20318/channel 0/schema 0xc77f6403 -> handler 0x7d8010 -> registrar 0x684310.
  Checked field +0x98 is format **1**, not client build 104319. Public numeric
  profile: protocol/instance-metadata-104319.json. Remaining descriptor fields
  and valid content payload are unresolved; the empty diagnostic is not content.
- Original registrar adds one entry in udpmeta22/24/25/26. Saved final flags
  0xa0, ten completed acquisition attempts, content absent, current context
  absent. Empty identifier matches resident default 0x321ff30; constructor
  0x684610 skips metadata lookup for that default. Association with the world
  request is not proved by accepting this record.
- CORRECTION to older private reports: entry +0x80 is a retry deadline, NOT an
  action pointer; +0x88 is a completed-attempt counter, NOT a state marker.
  Consumer 0x67fd70/0x68018b increments it on kind-14 completion and schedules
  retry at +0x80 or sets failure bit 0x80 at the configured limit. Flags:
  1 content present, 0x40 acquisition in flight, 0x80 acquisition failed.
- Run 22 shows HF-503. Owned empty-directory initialization in 24 and scoped
  own-package modify grants in 25/26 fail to resolve the final result. Do not
  ship or describe these as a working fix. `GetAppContainerFolderPath` can
  already return the AC directory: never append a second AC blindly. Aborted
  23 created nothing and its cleanup passed.
- Kind-14 request ctor 0x81c270, vft 0x26188d8, worker 0x81dfc0. Opens a native
  Hotfix temporary file through 0x1858f30 with flags 0x321 before transfer.
  Read-only live observer captured SIX completed requests still held by the
  original metadata service queue in 26: all status/tag/code **3/2/-3**.
  Native formatter 0x185e3a0 labels -3 "failed to open"; underlying Windows
  error not established. Do not conflate this with kind-13 enumeration 3/2/-1.
- Public `retail_login_state.py --metadata-state` validates native identities
  and exports only flags/counts/retry/context booleans. Corrected saved reports:
  .local/runs/udpmeta{22,24,25}-metadata-corrected.json and
  udpmeta26-final-state.json. Private live evidence: udpmeta26-live-sdk-errors.jsonl.
- Final 26: WAITING/pending, header and optional mode in catalogue but no load
  cache object/raw state 0, 29 other loads. No map/hero success. All owned runs,
  servers and observer have ended; exact baseline scoped ACLs/hash/signature
  checks pass. Do not run builds/isolation tests while the game is alive.
- New five-fixture metadata target brings CTest to 21/21; native build passes.
  041c327 public CI passed. Next: original file-provider open failure (including
  path/mount/actual error), valid descriptor/content/context association and
  original map-header preload. No readiness/verifier/transport code patches.

## Latest saved-dump correction — 2026-10-14

- Private runs udpmeta27/28/29 predate this continuation but were newer than the
  prior public notes. Storage probe 27 verifies direct owned-folder writes while
  ancestor attribute checks return Win32 5. Alias run 28 passes own-token access
  probes and samples four live kind-14 errors 9/2/6 instead of 3/2/-3. Retries
  still exhaust; no working Hotfix fix or content descriptor is established.
- Native 0x68362f..0x68370a processes staged slot +0x1a0 and promotes it into
  ACTIVE +0x198 on completion. The earlier previous/current names were misleading.
  0x6825de..0x68262d returns completion 2 for the default identifier without
  setting +0x98. Active default readiness false is not a processing-failure verdict.
  0x6855a0 installs a new staged context, checking both slots for matching ids.
- Public metadata_state now reports active_context/staged_context and bounded,
  identity-checked kind-13 initialization completion/errors. Legacy
  current_context_present is retained as STAGED presence only. Original default
  context is active (kind 1, zero records, ready false) in saved 26/28/29.
  Run 27's snapshot has neither slot and initialization_terminal_flag 0.
- Corrected reports: .local/runs/udpmeta{26,27,28,29}-context-corrected.json.
  Private aligned traces: context-default-path-30.txt, context-selection-30.txt,
  context-promote-aligned-30.txt. Candidate scans are not validated call paths.
- Native build and 21/21 CTest targets pass; metadata fixtures increased 5 -> 8.
  No native game launched this continuation. Existing run cleanup records pass.
  The live maps remain unverified: 29 still WAITING/pending, catalogue-present
  header/mode but no load-cache objects. Next trace normal map-header preload;
  do not infer that sending the empty 20318 is necessary for a default context.

## Engine preloader queue continuation — 2026-10-14

- Extended the API search beyond default wrapper 0x171e8e0 to its structured
  callee 0x171cca0. Native 0x67b250 builds options through 0x679fa0 and calls
  that callee: descriptor +8 resource, +0 condition key, +0x20 priority.
  Retained +0x44 is set after submission and cleared by 0x67b160 withdrawal;
  it is not a load-completion flag.
- Engine slot 39/vft 0x2610910/owner xor 0xf3b530a5300e4c1a has configured
  64-byte descriptors at +0x2678/count +0x2680 and retained 72-byte descriptors
  at +0x58/count +0x60. Public --preload-state validates that engine identity,
  bounded signed counts/arrays and submission flags; exports aggregate counts
  only. It does not claim that every world uses this one queue.
- Saved udpapp11/21/udpmeta26/29 have both engine queues empty. Private prototype
  agrees with the public reader. Reports:
  .local/runs/{udpapp11,udpapp21,udpmeta26,udpmeta29}-preloader-state.json.
  Empty final queues do not establish their earlier transient activity.
- 0x677190 adds/merges configured descriptors; 0x67a7e0 consumes them. Producer
  0x6775d0..0x679de0 reads entity/resource descriptors and calls 0x677190/0x677350;
  0x67be50 also adds a separate source list. The route from private assignment
  to a Practice header descriptor remains open. Main-root queue identity is
  verified; its exact relationship to the individual world owners is not.
- Earlier getter 0x1b53d00 "190GUID" meant member offset +0x190, not GUID type.
  Its initializer 0x1b51540 checks resource type 2 before 0x1b40d20 requests it;
  that is not a proven map-header preload path. World submission 0xb4b1c0 only
  copies the request. 0xb4b430 calls 0xb52630 then sets +0x41; the aligned ordinary
  0xb52630 scene traversal does not call a resource loader.
- Native build and 22/22 CTest targets pass, with four new synthetic preload
  fixtures. No new native launch. Next: trace descriptor producer inputs and
  conditional eligibility, then observe queues through a bounded live Practice
  attempt before deciding which original application message/entity data is missing.

## Live Practice and Hero Gallery continuation — 2026-10-14

- Original signed client launched in five new bounded 150-second runs:
  livepreload32 baseline header assignment, 33 plus header/mode resource list,
  34 with map-root assignment, and livegallery35/36 gallery controls. Practice
  reaches ENTERING GAME in all three; no map or controllable hero is rendered.
  Run 34 selected Practice late, leaving only about 20 seconds afterward.
- Native request-copy 0x590d50 and welcome consumer 0x7d9990..0x7d99be locate
  the extra resource array at request +0xf8/count +0x100, not +0x68/+0x70.
  Private corrected *-world-inputs-v2.json verifies both list entries in both
  run-33 requests and the root GUID in both run-34 requests. Earlier private
  world-inputs.json reports used the wrong array and are superseded.
- Public --world-resource-state now reports validated extra_resource_count
  (0/2/0 in 32/33/34), with signed count cap 4096, aligned nonempty arrays and
  complete reads; no GUIDs exported. Delivery does not establish submission/load.
- Read-only approximately 100-ms live samples: 32=1365, 33=1330, 34=1295,
  35=1306, 36=1390, all with zero rejected samples. Configured/retained engine queues
  remain empty, header/mode cache absent. This does not exclude sub-sample
  activity or alternate world-owned queues. Final Practice snapshots contain
  active default contexts with zero records, no 20318 and 28 other cache entries.
- Gallery 35/36 is visually empty; 36 enables every rarity/category/ownership
  checkbox and still has no hero cards/model. Both have no pending world request
  or active metadata context. Do not infer a general filesystem/GPU failure from
  this UI result. Next investigate gallery roster initialization and the normal
  Practice header-load trigger before inventing more assignment fields.
- Cleanup records preserve original hash/Valid signature and exact saved ACLs;
  all owned bounded launcher/server/UDP processes exit. Private run artifacts
  remain ignored and original client assets untouched.
- All 22 CTest targets pass after live exit, including native launcher isolation;
  resource-state fixtures increase from four to six. No commit/push this continuation.

## Private-session native header control — 2026-10-14

- New bounded runs: liveroot37 repeats the map-root assignment with earlier
  selection (1309 live samples, zero rejected), still WAITING/no header load.
  liveheader38/39 use the baseline header/mode welcome plus an explicit native
  preload CONTROL. This is diagnostic loading, not a solved protocol trigger.
- New launcher --preload-practice-header is opt-in, requires bounded own-key
  TCP/UDP loopback diagnostics, waits for exact guarded pending Practice
  header/mode, then schedules a ONE-SHOT original 0x171e8e0(priority 4) call on
  the verified original primary-thread delay return. Registered unwind, original
  stack, full NtContinue restore. It does not submit/tick worlds or change native
  readiness/state values. Returned reference survives only until owned job exit.
- Both controls return scheduled/unwind/native API/reference true. Header and
  mode reach cache raw state 3. Final dumps: both managers WORLD LOADING (6),
  pending requests, active default context (zero records/ready false), 29 cache
  entries all raw state 3; map-root remains catalogue-present/cache-absent.
- Direct UI in 39 shows Practice Range LOADING SCREEN with its map art/name/tip.
  No hero selection, actual scene rendering or playable hero is established.
  Read-only observer starts before Practice: existing manager transitions
  WAITING(no request) -> WAITING(pending) -> ABANDONING SCENES -> WORLD LOADING;
  1269 samples, zero rejected. It tracks only the manager discovered at startup;
  second manager is confirmed by final dump. Control 38 world observer starts
  late: 44 samples in WORLD LOADING. Cache observers: 38=1308, 39=1325, zero rejected.
- New --resource-cache-state exports aggregate counts only, capped traversal,
  exact profile, unique objects and raw state counts; rejects changing/corrupt
  counts/chains/objects. Saved 33/36 have 28 objects all raw state 3: some assets
  do load normally. Private *-cache-states.json agrees with public reader.
- Correct world-owner decoding is ONE xor using 0x2ee48a1/0x4dfd564467c27b96;
  it is NOT the fixed engine owner mask. Both world owners differ from main root
  and have no slot-39 service in 33/36. Earlier world_owned_preload_queues.py
  double-decoded the owner and is superseded by world-preload-owner-check.py.
- WORLD LOADED (7) switch -> 0xb54370; aligned 0xb543f2 calls 0xb4ffd0 content
  gates, requires manager +0x41 and owner virtual +0xc8 (0x587170: owner+0x2a8),
  compares target request and checks target manager state >=7. Final 38/39 have
  one submitted/owner-flag true, other false. Do not patch these flags.
  0xb4ffd0 checks matching active/staged identifiers, staged absence and provider
  readiness for types 0x75/0x77 via 0x57b9f0, then extra-resource availability.
  Precise stopping branch and downstream world/scene dispatch remain to trace.
- Native build and all 22 CTest targets pass. Resource fixtures now eight;
  launcher isolation rejects incomplete/duplicate control flags. All three owned
  runs restored exact ACLs/hash/Valid signature; helpers/listeners ended. No push.

## WORLD LOADING completion gates — 2026-10-14

- Correction: actual dispatch table index state-2 maps WORLD LOADING (6) to
  0xb4ccfb -> 0xb54a80. The previous 0xb54370 trace is WORLD LOADED (7),
  downstream of the current stall, not its immediate gate.
- Ordinary 0xb55bbf path calls world-owner getter 0x5855f0, checks resource
  arrays at world +0x50/+0x60/+0x88 via 0xb4d910 (signed object+0xac >=2),
  then scene virtual +0x140. Getter decodes owner+0x1d0 using original PID
  (GS:[0x40]), stack-only seed routine 0xb7c60 and table 0x2ee46d0.
  Scene secondary vft=0x2655fc8; method 0xb59220 returns scene+0xa0 boolean.
- Public --scene-state --client-pid <PID associated with dump> reproduces
  both saved controls 38/39: each of two managers has resource groups 4/2/0,
  six objects raw3, all native-complete, but scene_ready=false. Active/pending
  scene handles (scene-0x70/+0x38) are absent. No native field is changed.
- Native scene update at 0xb5b78e sets primary+0x128 (secondary+0xa0) only
  when pending or active scene exists, 0x1b53d80 returns 5 and predicate
  0x1b40cf0 succeeds on 0x1b53d30 result. Scene request method 0xb59680
  resets readiness and calls 0xb5cfe0; next trace is why construction is absent
  or returns null. Do not assume deserialization failure from missing handles.
- Loaded Practice header +0x50 is type2/index1672, already cache raw3 but
  absent from loaded-asset lookup. Null global 0x32213e8 uses native fallback
  0x3225890, FNV1a32 over eight little-endian GUID bytes; earlier private
  lookup that rejected null root was incomplete. This does not prove no blob.
- livescene40 was bounded150s, native handshake reached6, 1020 resource and
  1013 world samples, zero rejects. Captured window black; activation failed
  GetCursorPos Access denied (0x80070005), including fresh selection recovery.
  No Practice input, pending request or header-control call: this is not a
  new loading-screen reproduction. Startup manager stayed WAITING/no request.
  All cleanup checks pass. No game/owned responders remain.
- Native build and all 23 CTest targets pass, including new scene fixtures.
  Read-only public reports omit pointers/PIDs/GUIDs/native bytes. No commit/push.

## Live typed-map comparison — 2026-10-14

- UI works after user's desktop/input fix. Two bounded original-client runs:
  livescene41 baseline header assignment/control and livevariant42 exact typed
  map reference/control. Both directly show original Practice loading screen,
  with no hero selection, geometry rendering or playable hero verified.
- Header asset +0x50 names 0x0800010000000688, not earlier unflagged root
  0x0800000000000688. The 0x10000000000 variant bit is material. Both native
  pending requests in 42 contain the exact header reference and Practice mode.
- Opt-in header control now accepts only the earlier exact Practice header or
  that exact typed Practice map plus exact mode. It still requests the header
  once, changes no native completion flags, and is confined to bounded own-key
  loopback sessions. Default launcher behavior unchanged.
- Baseline 41: live WAITING -> GLOBAL LOADING -> WORLD LOADING, three groups
  4/2/0 complete, scene_ready false. Final dump has two managers and absent
  active/pending scene handles. World observer follows startup manager only;
  1265 valid/0 rejected; resource observer 1349/0. A later WAITING/no-request
  sample occurs near the bounded run's end; do not claim its cause.
- Variant 42: both managers have pending scene handles, active absent,
  ready false; groups still 4/2/0 all raw3. Both pending scene objects have
  vft0x27abc08 and decoded controller state1, not required5. Completion data
  exists and its two resource objects are raw3. Scene construction progressed,
  but scene state advancement remains missing. No root-level gameplay claim.
- Extended public --scene-state with conditional active/pending scene progress,
  exact object/getter identities, bounded raw state and signed resource statuses.
  Reproduces private snapshot; no native addresses/IDs/payload bytes exported.
  State getter 0x1b53d80 and data getter 0x1b53d30 decode object+0x458 xor
  0xe4d560d2fc1e2c2b; controller+0x1a8 state, +0x1b0 completion data. Native
  predicate 0x1b40cf0 requires both data+8/+0x10 resources with signed state>=2.
- First 42 world discovery exceeded10sec, failed without observations. Retried
  with bounded20sec/4GiB discovery; found both managers after WORLD LOADING.
  Second observer554 valid/2 rejected (not a complete transition history),
  resource observer946/0. Both native controls return scheduling/unwind/API/ref
  true. All cleanup ACL/hash/signature/owned-process checks pass.
- Native build and all 23 CTest targets pass. Four synthetic scene
  fixtures now cover resource completion versus controller state and readiness,
  plus malformed scene identities/state/pointers/unreadable data. No commit/push.

## Canonical map reaches WORLD REPLICATING — 2026-10-14

- State1 trace: scene update 0x1b57ff0 increments object+0x478 and calls
  0x1b5f230 before controller state5. Its state1 path calls 0x1b412d0;
  load-progress0 calls 0x1b416a0, which waits for data+0x18 typed asset handle.
  Native constructor 0x1b40dee..0x1b40e12 requests two raw resources via
  0x171e8e0 and a separate typed handle via 0x173b8f0 ->0x1740bd0.
- Saved variant42 has3757 scene ticks in each object, load_progress0, valid
  typed handle but no asset object, native handle status2. Completion resources
  raw3 do not establish typed-asset completion. Type2 maps to descriptor group15;
  it exists. 0x1736fc0 is merely a reference increment, not queue insertion.
- Native 0x173b910 status: invalid0; valid unfinished2; finished+failed3;
  finished without failure4. Finished is control+8 bit16; failure bit15.
  Never interpret typed status3 as raw resource status3.
- New livecanonical43 keeps header preload but uses unflagged canonical map
  0x0800000000000688 in both welcome fields. Exact pending map/mode verified
  in both final requests. Opt-in guard accepts header, canonical map and
  referenced variant, all exact Practice assignments plus exact mode.
- Canonical run directly reaches Practice loading screen, internally advances
  WORLD LOADING ->WORLD LOADED. Final dump: first manager7 WORLD LOADED,
  second8 WORLD REPLICATING. Both scene_ready=true, active present/pending
  absent, controller5, load_progress4, typed object present/status4, update_count
  4750, groups4/2/0 all raw3. Public inspector now covers world states6/7/8.
- This isolates the variant as a blocker: canonical map completes typed load;
  the header's referenced variant stalls. Prior header-only versus variant
  comparison did not independently isolate map type and variant flag.
  Original normal header initiation is still unresolved; diagnostic preload
  remains opt-in. No native readiness/state writes or extra ticks introduced.
- Live world observer follows startup manager only: 1043 valid/0 rejected,
  captures asset completion/progress0->2->4 and scene state1->2 before world7.
  It misses state5 between samples and does not observe the submitted manager's
  transition to8; final dump verifies it. Resource observer1286/1 rejected.
  A late second observer starts as the client exits and produces no snapshots.
- UI remains loading screen: no hero selection, rendered gameplay geometry,
  movement or combat verified. Next frontier is replication initialization.
  Failed main-root provider getter prototype is not evidence of a provider
  blocker; the actual submitted manager already passed WORLD LOADED.
- Native build and all23 CTest targets pass (five scene fixtures). Exact ACL,
  original hash/signature and owned helper/listener cleanup pass. No commit/push.

## Selected entity and pending replication — 2026-10-14

- Completed liveselect44, livegeneration46 and livedelay47. A failed responder
  startup livegeneration45 never launches the client and also passes cleanup.
  All new runs retain canonical Practice map/mode and explicit header preload.
  All owned runs are ended; original hash/signature and exact saved ACLs pass.
- Normal 20302: dispatcher 0x7d2000, table 0x7d2244 index2=0x7d2079 calls
  0x7d6c10. Handler passes record+0x78 to 0x5881c0, which writes owner+0x298
  as u32. Schema is signed i32: convert packed high-bit ID to signed equivalent
  at encoding, without changing its bits. +0x7c false/+0x80 zero unchanged.
- Client update 0x788900 (vtable pointer ref 0x2615848): 0x789330 decodes owner
  via [client+8] XOR image[0x2ee48a1] XOR 0x4dfd564467c27b96. Getter 0x582340
  returns owner+0x298; validity rejects image[0x3241288] and low29 bits all ones.
- Exact entity lookup 0x78abe1..0x78acb5: table=owner+0x18 XOR
  (0x042b51ef9b84a901+2*ror64(image[0x2ee53a8],4)), all modulo64. Bucket at
  table+(selected&0xfff)*16, array+0/count+8, rows16 bytes keyu32+0/objectptr+8.
  Full ID match is required; matching low29 index with a different generation
  does not resolve. Private saved entity generation is6/index1; this is a
  diagnostic selection of an existing entity, not a demonstrated player spawn.
- Baseline43 both owners selected unset. 44 submitted owner selected1 valid,
  bucketcount1 but no exact record/object match; same index/different generation.
  46 sends matching packed ID; selected valid, exact record and object present.
  47 sends same ID after30sec from first welcome with the same resolution.
  All final submitted worlds remain8, startup7. All active scenes ready/state5,
  typed status4, groups4/2/0 raw3. Scene ticks44=3008,46=4872,47=4804.
- New public tools/retail_replication_state.py via --replication-state exports
  only statuses/counts/booleans. Exact root/getter/dispatch/owner/slot guards,
  bounded one-bucket reads, duplicate selected key rejection, truncated reads,
  changing selected/table/context/queue rejection. Five synthetic tests pass;
  native build and all24 CTest targets pass, final extension targeted CTest pass.
- Native 0x641250 uses normal owner+0x140 context table decode with TABLE_MASK
  minus image[COOKIE_RVA]; 0x5fd5a0 returns slot79. Slot vft0x2610cf0, +0x18
  points to plain replication job (first qword is NOT a vtable). Job+8 is the
  context used by update. Job+0x18 queued record count, +0x128 pending count,
  +0x148 completion marker. Baseline43/44 pending4 markerfalse; 46 pending4
  markertrue; 47 pending4 markerfalse. Do not label +0x148 a separate busy flag.
- Completion path at 0x78ab81 also requires staged metadata false and
  0x78dd60 error result0. It tests job+0x148 false, entityobject non-null and
  pending count0 (calls 0x78efd0 to drain if nonzero), then 0xb4a810 and writes
  completion markertrue. 0xb4a810 calls owner0x1836820 then tailjumps0xb523f0.
  Forward dispatch state8->0xb52517 sets9 at0xb52548. 0xb52190 is backward/
  teardown, not the replication trigger. Never invoke these callbacks or write
  readiness/state/queue flags directly as a fix.
- Next trace: 0x78efd0 drain, aligned continuation0x78f022..0x78f242. Pending
  array context+0x118 (=job+0x120), count context+0x120 (=job+0x128), rows24:
  +8 dependency GUID array, +0x10 signed count. Saved47 four entries have
  dependency count0; handler at0x78f0e8 skips those, leaving them in queue.
  Nonzero dependency lists compare against world+0xe0 virtual getter, owner
  0xd9d640 result, and typed asset from returned object+0xb8, then remove via
  0x787620. Meaning/producer of zero-dependency entries remains unresolved.
- Ignored helpers: .local/re/world-replication-state.py, updated private
  udp_welcome_reply.py (--selected-entity u32, signed conversion, followup delay)
  and run-live-preload.ps1 (-SelectedEntity -SelectedEntityValue -SelectedEntityDelay).
  Follow-ups now send after welcome repeats stop, so delayed delivery works.
  .local/re/watch-live-world.py includes replication gates/context counts and
  states6/7/8 scene snapshots; late second observers discover submitted owner.
- Private disassembly: replication-status-details-53.txt, completion-prerequisites-53,
  replication-pending-drain(-aligned)-54.txt; earlier 51/52 files trace selection
  and dispatch. Exclusive public snapshot reports in .local/runs/*-public-
  replication-final.json, plus44/46/47 scene reports. Original PID44=14616,
  46=34228,47=39844; imagebase140699994357760; original dumps in client _retail_
  retail-private-<run>.dmp. All private material stays ignored.
- 44 observers world688/0 resource739/1; 46 world1071/0 resource1102/0 late202/0;
  47 world1015/0 resource1064/1 late335/0. Startup discovery sees first owner
  only. Late observers begin after notification, so marker timing cause is
  unproven. Private responder accepted230/230,367/367,355/355 datagrams; each
  has one body outside public reliable decoder. Ten follow-up repeats each.
- Direct UI46/47 stays original Practice loading screen. No hero selection,
  rendered gameplay geometry, movement or combat. No commit/push this session.

## WORLD_RUNNING via placeable creates (Claude, 2026-10-14, livecreate54/55)

- The 4 zero-dependency pending rows are server-replicated MAP PLACEABLES:
  producer 0x787f50 (scene visitor 0x78b9a0) adds scene records with a
  component of type 0x5e/0x3a, keyed by placeable id (record +0x2c): 0x88,
  0x22e, 0x234, 0x289 in Practice. Only an entity CREATE naming that placeable
  removes a row (0x78c360 -> 0x788480). Drain 0x78efd0 never does.
- Server entity section (0x7ce110): 7-bit count; id 0xdb0f70 (2-bit class ->
  top bits 1gg, varint index 8/16/32); TERMINATING module chain: mod0 none,
  mod1 one 0 bit, mod2 TWO 0 bits (0xb3a490 has two optional sections), mod3
  one 0 bit, mod4 = 2-bit op | 14-bit length | payload. Module-5 PREFIX is ONE
  0 bit outside hot reload (old responder wrote two; harmless only with zero
  entities). Minimal placeable create: 1 | u32 placeable | 0 | 8-bit zero
  component count; entity id class must be 0b100 (we use 0x80000300+).
- Records queue (job+0x18) but are processed only after the 20302 selected
  entity resolves. livecreate54/55: then all creates process, pending 4->0,
  marker set, submitted world GAME MODE LOADING -> WORLD_RUNNING, four
  0x800003xx entities with objects. UI STILL the Practice loading screen; no
  player/hero entity, rendering or input. Selection is still the diagnostic
  existing local entity 0xc0000001; components are empty. Next: what the
  loading screen/local player needs (likely a real player/hero entity create
  via the non-placeable definition path 0xdb11c0/0x78dab0, then 20302 for it).
- Debug lever: connection(+vft 0x2616458)+0xa0 = u32 bits consumed per module
  (prefix + per-entity). It found both framing errors. Private tools:
  .local/re/watch-replication-56.py <pid> <out> <sec> (live ~10 ms sampler),
  replication-pending-keys-55.py, instance-connection-owner-57.py,
  replication-gate-object-57.py (0x594af0 discard gate obj+0x280 must be 0).
  Notes: .local/re/replication-entity-create-55.md.
- Responder: udp_welcome_reply.py --placeable-create ID --create-delay;
  driver run-live-preload.ps1 -PlaceableCreate (use with -MapRoot
  -NativeHeaderControl -SelectedEntity -SelectedEntityValue 3221225473
  -SelectedEntityDelay 45). Claude drives the UI with .local/re/ow-ui.ps1
  (accepts the package-cache client path; menu coords at 2560x1080: No Thanks
  2100,1006; Training 471,326; Practice Range 1279,538 — re-verify by shot).
  Computer Use cannot be approved when the user is away.
- Claude's launcher build was stale; rebuilt (Build.ps1 -SkipDependencies),
  24/24 CTest. All runs' cleanup audits passed. Dumps
  retail-private-livecreate5{0..5}.dmp beside the client; 50..53 are
  superseded failures (50/48/49 never reached Practice). No commit/push.

## Codex continuation: reusable codec and visible geometry — 2026-10-14

- Independently verified saved55 WORLD_RUNNING with public --replication-state,
  then liveverify58 reproduces state8->9->10 and pending4->0 with the same private
  placeable responder. Submitted observer12719 valid/0reject/maxqueued133.
- Added public tools/instance_entities.py: PlaceableCreate(entity_id,placeable_id)
  and read/write_placeable_creates on independent Reader/Writer, at 7-bit entity
  count AFTER server prefixes. Observed non-hot-reload minimal42-bit payload,
  class100/8-16-32bitindex, empty modules0..3 (module2 TWO0bits), terminatingchain.
  Unsupported forms rejected. Four synthetic tests; CMake adds25thtarget.
- Migrated ignored udp_welcome_reply.py server_body to this public codec. Old
  entity_create function remains unused as a private comparison reference.
  .local/re/check-server-entities-58.py authenticates saved replies and parses
  reliable prefixes privately, then re-encodes exact entity-section bits.
  Checks:55=545replies/543sections/400creates;58=428/426/359;59=390/388/322;
  60=724/722/400. Total2079sections,1481creates. No bytes/keys in stdout/public.
- livecodec59 default150sec, selecteddelay45, canonical/header/placeables:
  WORLD_RUNNING, queue0/pending0, marker1. UI DIRECTLY shows actual Practice
  snow/rocks/building/animated sky, with tip/mapname/loading overlay gone.
  Esc attempted as bounded process exited, so no effect established in59.
- livecamera60 bounded180sec, selecteddelay30, same codec/placeables: geometry
  reproduced; Escape opens in-game menu Social/Career/Options/LEAVE GAME/Exit,
  Escape returns to map. Short W press, mouse drag, H produce no visible camera
  translation/rotation or hero selection. No HUD/weapon/controllable hero.
  This supersedes 'geometry unverified' for these runs, NOT playable-game claims.
  Renderer shows one fixed camera near snowy exterior; animated clouds change.
- run-live-preload.ps1 adds private -RunFor30..180(default150), actual launcher
  duration, outerduration+70 deadline. UDP stays180. All 58/59/60 audits pass,
  original hash/Valid signature/exactsavedACLs intact, ownedprocesses ended.
  No game/listeners remain. No commit/push. Do not rerun isolation whilegamealive.
- Public --scene-state now includes world9/10 (tests aswell). Both final scenes
  active/ready/state5, rawgroups4/2/0 complete, typedstatus4; ticks58=4706,
  59=4385,60=7322. Nativebuild+all25CTest passed; CLIhelp adjusted only afterward.
- Live observers58/59/60: submitted12719/0max133,11411/0max128,18605/0max67;
  startup observers miss submittedworld because discoverypreselection. Private
  sampler .local/re/watch-replication-56.py exports selectedIDs to ignoredlogs;
  don't copy these into public docs. See .local/runs/*-public-final.json.
- OriginalPID58=30400,59=30256,60=15924, imagebase140695393271808. Dumps
  _retail_/retail-private-liveverify58/livecodec59/livecamera60.dmp in original
  packagecacheclient folder; savedclientinfoJSONs .local/runs/<name>-client.json.
- Next frontier remains real local-player/hero replication, not pendingplaceables.
  Read-only nonplaceable path notes .local/re/entity-definition-reader-59.md;
  native0x78c8c4 calls0xdb11c0(bs,type3) then0x78dab0 8bittransformflags.
  No definitioncreate sent; resolve actual GUID and components before doingso.
  The hardcoded0x0400000000002299 is AUTOMATION ENTITY, NOT player evidence:
  0x787260 errorlabel 'Automation entity unavailable'. Generic0x7873f0 missing
  definition ->nativeerror0x40131. Private definition-create-*58/59 traces.
- Next concrete native gate: post-create0x787b20 walks callbacks+90/count+98,
  passing entity to function/contextpairs16bytes. Actual primary replication
  module vft0x26157d8; networksecondaryvft0x2615850 is atprimary+0x10 (NOT+40).
  Saved60 two module instances each register0xb8c530 and0xbae5e0, nullcontexts.
  .local/re/post-create-callbacks-60.py confirms identities/countbounds/RVAs;
  post-create-callback-bounds-60.txt traces bodies.0xb8c530 firstcomponent
  maskgetter0xbcacb0. Match requiredcomponentpresence/nativecomponentinitialization
  against selectedlocalentity and realplayer before inventing packet fields.
  Earlierzero-resultcallbackscan assumed wrongbaseoffset; it is superseded.
- Selectedlocalandfourcreatedentities have matching nativeID+0xb0 and nonempty
  componentmasks+0x88..0xa0, despite zero networkcomponentcount. They are plain
  structures; firstqoutsideimage is not invalidvft evidence. Ignoredoverview
  .local/re/created-entity-observations-59.py and liveverify58-entity-observations.
- Native followup20303 dispatchhandler0x7d8870 callsworldcomponent0xbfd760;
  20304handler0x7d6830 eventually calls0xe3e4d0(owner,u8field+78). Meaning not
  established; no20303/04 sent. Traces post-world-records-59/record20303-target-60.
  Never directlyinvoke nativecallback orwriteworldreadiness/state asafix.

- Continuation run62 (livetime62) visibly renders Practice with the existing
  optional module-3 timing field enabled. No hero HUD or weapon is present.
  Native timing field +70 is 49.085 seconds; +64 controlled-actor markers are
  invalid in both module instances. Primary module VFT is 0x26162d8, secondary
  network VFT 0x2616350 at +10. Private first-person-clock-observations-62.py
  verifies saved fields. This establishes receipt/scaling, not clock sync.
- First-person reader 0x7c7800 calls selected-object getter 0x582b10 then
  0xda69d0, whose component getter 0xbd59a0 requires word-0 bit 44 (+88 mask).
  Component method 0xbd4d40 resolves a separate actor whose +b0 ID is saved.
  The current selected diagnostic entity lacks component 44. Public replication
  snapshot now checks native-ID agreement (+b0) and exposes this prerequisite
  as a boolean. Six fixtures cover malformed/changing memory and profiles;
  component presence alone does not prove hero or controlled-actor initialization.
  Both run60 and run62 final snapshots confirm absence. Do not construct a
  guessed component or native actor; trace its definition/initialization next.
- Run61 ended at the menu, so it is not a Practice timing control. Run62 client
  PID 1988, saved client JSON and public-final JSON are under .local/runs; dump
  retail-private-livetime62.dmp stays in the original client's package cache.
  Submitted observer: 1920 valid, zero rejected, maximum queued 63, records
  WORLD_RUNNING before teardown resets. Final snapshot still captures running,
  ready state-5 scenes (ticks 4783), zero queued/pending and completion marker.
  All 433 entity sections re-encode exactly, 366 create records. All 25 CTest
  targets pass, full cleanup audit passes, game and diagnostic listeners ended.
  No native build changes, commits or pushes this continuation. Next unresolved
  step is actual player/hero replication and first-person entity-state decoding.
- Additional read-only traces: post-create callback 0xb8c530 requires components
  25/26; 0xbae5e0 requires 84/85. Their roles are not established. The current
  selected entity lacks 44; map placeables have 25/26 but not 84/85. Private
  post-create-component-61 and secondary-gates-61 record these getter masks.
  20304 -> 0xe3e4d0 dispatches a byte to world-owner context slot 120's callback;
  both saved run60 owners have no slot 120. 20308 -> 0x7d88b0 uses global-root
  context slot 29 plus descriptor/notification paths, not verified hero creation.
  Actual reliable-handler-map-61.json supersedes earlier candidate 0x7d89e0
  (that handler belongs to 20306). No 20304/20308 messages were sent.
  Module-3 per-entity path 0x7c2e60 queues bitstream snapshots under job+150,
  then 12-bit payload length and an entity-ID/offset/length item. 0xbea7f0 is
  bitstream copying, not a decoded first-person header. Do not send guessed
  first-person payloads. The separate post-receive-62/queue-consumers-62 traces
  are candidates, not established queue decoders; vtable span/roles need checking.

## Definition-create checkpoint — 2026-10-14

- Complete entity-table census (.local/re/entity-census-63.py) checks all 4096
  buckets, duplicate/index/count bounds and native IDs. Run62: worlds contain
  1019/1020 entries, all ID matches, zero component-44 candidates. Run64: 1019/1021
  entries, all matches, exactly one candidate in WORLD_RUNNING after definition
  create. This supersedes investigating whether a hidden existing entity has 44.
- The old beta controller resource is only a research lead. Its exact final
  definition is hash-verified offline from bundle data: 272 bytes, root hash
  73bb2f3a, serialized components 445e7678/7a36ae06/dae477d5/fd024f42. See private
  definition-storage-probe-63.json and definition-000e-63.bin. The verified source
  GUID and content hash stay in that private report. Pinned OWLib schema/tree
  and filtered type metadata are ignored owlib-*-63 files. No third-party tool
  binary was installed or run. Native 0xf525e0 maps these to 76/29/73/47; script
  component-type-map-63.py statically traverses compare/branch leaves, reports
  89 mappings and 11 unresolved default cases. Do not equate serialized types
  with runtime components, or assume the beta's offsets/classes apply.
- Cache correction: 0x173ba30 uses primary typed manager at image+0x321f3e8;
  when absent it uses global fallback cache at image+0x3225890. Native 0x1738160
  uses FNV-1a of eight GUID bytes, capacity+58, buckets+48, node GUID+10/next+18.
  0x173baae returns node's object directly. definition-load-state-63.py now reads
  both paths. Run62 has a ready typed definition object (status4), despite no raw
  catalogue/load-cache entry. Earlier *definition-baseline-63/final JSONs omit
  fallback and are incomplete; use *definition-full-lookup* results instead.
- Livedefresource63 is a failed welcome-list control, not a working asset preload:
  -DefinitionResource adds the verified definition to 20300 +520. HOTFIXING and
  loading overlay persist; final metadata default context not ready, current
  context absent, teardown states WAITING/ABANDONING SCENES. It has no fallback
  definition entry at the end. Do not add this list to the working create run.
  PID45976; 3418 observer samples, 3 rejected, max queued83; 522 sections/400
  placeable creates re-encode exactly. Full cleanup audit passes.
- Livedefcreate64: baseline canonical welcome/header/placeables, plus opt-in
  -DefinitionCreate, initial diagnostic selection after30sec, run-for180.
  Non-placeable payload is 51 bits: bit0, resource selectors00+index32 for type3,
  flags0(8), component count0(8). Class100/new unused index, same module chain.
  Native engine constructs components 22/25/26/29/44/45/47/73/76/84/85/90/96/97/137.
  Thus both post-create callback pairs and missing first-person prerequisite
  exist without guessed component bytes or memory writes. Practice geometry
  renders. PID46404; observer2252 valid/0 rejected/max queue66. Capture check
  661 authenticated replies, 659 sections, 400 creates including80 definitions.
- Livedefselect65 adds -SelectDefinition: after45sec, a new reliable sequence
  sends 20302 for the definition entity; initial diagnostic selection is still
  delivered after30sec so create queues can drain. It successfully selects the
  new object, native ID agreement true, component44 true, WORLD_RUNNING with
  queue/pending0 and marker1. Scene ready/state5, ticks6953, groups4/2/0 complete.
  PID26336; observer2852 valid/1 rejected/max67; 675 replies/673 sections/400
  creates including80 definitions. H produces no hero picker/HUD. Subsequent
  W action fails because the bounded process has exited; no movement result.
- Public tools/instance_entities.py now adds DefinitionCreate and strict
  read/write_entity_creates. Neutral type3 GUID index32, flags0, empty components;
  placeable-only wrappers remain strict. Six synthetic fixtures. Both run64/65
  captures re-encode exactly with public and independent private encoders:
  1332 sections, 160 definitions. Private responder migrated to public definition
  writer afterward; byte equivalence is verified, no redundant new run yet.
  Full25CTest pass, original hash/signature/ACL audits pass for63/64/65. No native
  build/source change, commit or push this turn. All owned processes ended.
- New remaining gate: component44 has an invalid actor target at +d4, and cannot
  resolve a controlled actor. Private definition-actor-link-65.py verifies this
  in both64/65, including decoded component's world-owner identity. Decode uses
  the saved PID and native b7c60 key transform; wrong PID must not be accepted.
  Its native da69d0 component mask/popcount and four pointer transforms are
  traced in component44-*63 and component-key-*64. bd4d40 actor getter reads
  +d4 then the world's ordinary entity table. Do not write this ID as a shortcut.
  Next trace actual hero gameplay definition and native replicated state linking
  it to this entity, including CFPS/generic component readers. Actor-link helper
  remains private; add exact instruction/profile guards and synthetic tests if
  promoting it to public diagnostics. This checkpoint establishes creation and
  selection of a definition entity, not hero control or actual combat.

## Hero preload checkpoint (Claude, 2026-10-14, liveherodef67..70, liveherolist71)

- Pushed 2689ae9 (all prior Codex work) before this continuation.
- Hero gameplay definitions: Codex's offline .local/re/hero-storage-probe-66.json
  maps 56 hero records (type 0x75, raw 0x02e0...) to gameplay entity definitions
  (Soldier: 76 0x02e000000000006e -> 0x04000000000003cf).
- Creating that definition WITHOUT preload aborts: create lookup 0x78cf3a ->
  0x17d3360 -> 0x173ba30 is lookup-only; 0x78dd60 error -> 0x78b059 'Mirroring
  mismatch.' -> abort 0xb64af0, which sends lobby 21801 (0x7731a0) + 21802(bool,
  0x773940) pairs, notifies BNet object root+0x1f8 (keepalives stop) and leaves
  (instance header flags 4, UI back to Training). Proof: in-place decoded labels
  (.local/re/label-usage-70.py) + 13 heap 'Missing entity definition:
  04000000000003CF' strings in mid dump retail-private-liveherodef70-mid.dmp.
- Original preload input = lobby 20505 list 0: 0x77a000 -> 0x57bba0 -> 0x57c700
  inserts catalogue-present GUIDs into content provider Hero(0x75) set (+0x88);
  list 2 -> map set; list 1 -> 0x171ace0 requests. Promote 0x6835f0 also refreshes
  sets. New opt-in public `--lobby-hero-list <hex>` (type-0x75 only, <=64, needs
  20505 initial data); driver -HeroList; test fixture added.
- liveherolist71 (PID 38776): no abort, keepalives continue, WORLD_RUNNING with
  hero 0x80000305 selected; definition resident (typed census 150 vs 129); hero
  entity 28 components (no 44); a huge armored BOOT model renders at the default
  camera (hero model at world scale). No HUD/first-person/movement verified.
  Controller (000e) still holds component 44 with invalid actor target (+d4).
- Private: .local/re/hero-definition-frontier-70.md, typed-cache-census-70.py,
  content-provider-70.py (getter 0x594510 decode; provider object not located),
  dump_on_lobby_message.py, definition-actor-link-68.py (entity arg). Responder
  --definition-guid/--select-definition; driver -DefinitionGuid
  -SelectDefinitionIndex -HeroList. Dumps retail-private-liveherodef67/68/69/70
  (+70-mid) and liveherolist71 beside the package-cache client. All audits pass.
- Next: link the controller's component-44 actor (+d4) to the hero entity via
  original replicated state (component network state / update op), or find
  which entity the server should select; then first-person/HUD and input.

## Controller actor link checkpoint (Claude, 2026-10-14, livecontrol72/73)

- Pushed 6e82108 (hero preload). Component state rides in the create payload's
  trailing u8 count: update body 0x78e5d0 -> per entry u8 runtime component type
  -> component slot 0x18 (44: 0x5b5a00) -> visitor 0x78b870 (vft 0x2615c10):
  byte-align at ABSOLUTE body bit offset (0xbea7f0 copies the body; items keep
  offsets), u8 mask length, mask bytes (filter 0x788510, 1 bit/field LSB-first),
  then field values from the main stream (0x1be0300: raw LE bytes; kinds are
  CRC32 of lower-case type names, sizes 0x1be1c90; teentityid=0x0c525b48 -> 4 B).
- Component 44 state: descriptor 0x30d8f80, three teEntityID fields state
  +0x78/+0x7c/+0x80 (component +0xd0/+0xd4/+0xd8; hashes 1ab5e773/4d1ffc51/
  b1ca772f). Local-game path 0x82a5e0 sets all three to one entity.
- Public `DefinitionCreate(entity, guid, controlled_actor=ID)` + known-vector test.
  Private responder --controller-actor C T (driver -ControllerActor 0,1) now uses it.
- livecontrol72 (PID 34860): controller 0x80000304 selected; actor target valid and
  resolves to hero 0x80000305. livecontrol73 (PID 24888, -ServerTime): module-3
  receiver 0x7c7800 sets +0x64 controlled-actor marker VALID (submitted world).
  View still the default fixed camera with the hero boot; no first person/HUD/input.
- Private: check-server-entities-73.py (absolute-offset re-encode; 723/717/717
  exact, 66 actor creates), definition-actor-link-68.py, first-person-clock-
  observations-62.py. Dumps retail-private-livecontrol72/73.dmp. Audits pass.
- Next: what moves the camera to the controlled actor (camera/view component,
  hero transform/state, game-mode spawn flow) and input routing.

## Camera/input controls (Claude, 2026-10-14, liveinput74, livetransform75/76, livepreloadonly77)

- Pushed 90c7439 (actor link). Run 74: look/W/Space/H/Tab after controller select ->
  no visible change, no new client instance messages (no movement commands).
  ow-ui.ps1 now has `hold -Key W|A|S|D|H|Space|Tab|E|Shift -Ms N` and `look -X dx -Y dy`.
- Run 75 (create flag 4: f32 +0x10) and 76 (flag 8: +0 xyz, +0x20 quat, +0x10 xyz)
  do not move/scale the boot; run 77 (preload, no hero create) has no boot -> boot is
  the created hero, positioned by other replicated state. Private responder
  `--transform-triple DEF FLAGS values...` (driver -TransformTriple) is experimental.
- Camera views: descriptors around 0x26134a8 ("First Person View" label 0x698ef0);
  shared predicate 0x699730 reads root slot 5 (vft 0x26112d0) +0x606, a user-setting.
  Local-game 0x82a5e0 links component 74 (+0x68 -> comp44) and uses component 43.
- Hero record (02e000000000006e) root refs: gameplay 03cf, plus type-3 03d0 (322c521a),
  09fc (26d71549), 0dda (8125713e), 1438 (previewEmote); private
  .local/re/record-references-75.py (Codex package manifest/CascLib, read-only).
- Next: module-3 per-entity snapshot format (0x7c2e60, job+0x150, 12-bit length) for
  the controlled hero's movement state; then camera/input. Don't send guessed payloads
  without tracing the native reader first.

## Module-3 hero snapshots (Claude, 2026-10-14, livesnapshot78)

- Tools (private, scratch copies in .local/re): deob2-78.py (opaque-chain collapsing
  disassembler), emu-78.py (x86-64 interpreter over image.bin; SIMD = no-op),
  emusnap-78.py (runs 0xc5f680), emutest-78.py (bit-reader validation).
- Module-3 per-entity item: [1][len:12 incl. itself][payload]. 0x7c7f50 applies
  per frame if selected entity valid (+0x57f310 gate); 0x7ca130: template bit,
  entity lookup, needs comp 28 (0xbe76f0) + comp 43 (0xbd4680); template id via
  delta int 0xc66d00 (widths table 0x2d17d80) else default prior 0x2f82d30;
  movement decode 0xc5f680 -> apply comp28 0x64a970. Minimal payload = 36 zero bits.
- Responder --hero-snapshot DEF --snapshot-delay S (driver -HeroSnapshot 1
  -SnapshotDelay 55 -CreateSends 150). Run 78: accepted, hero geometry moves by
  itself after snapshots begin; no movement commands from client.
- Next: add scalar float support to the interpreter, map the snapshot fields
  (position/orientation), send a sane spawn position; then camera/input.
- Snapshot field map (zero path = 35 one-bit "changed" flags, read order):
  0 0xc619b0 (4 optional bytes), 1 out+4 bit, 2 delta int 0xc66d00 -> out+8,
  3 0xc61b60 -> +0xc, 4 delta16 +0x42 (widths table 0x2d17d60), 5 next field,
  6 0xc61b60 -> +0x14, 7/8 floats +0x18/+0x1c via 0xc66e30->0xc67260 (likely view
  angles), 9 0xc61e50, 10 0xc61b60, 11-12 0xc61c50, 13-15 0xc5ff00 (+0x50),
  16-18 0xc606c0 (+0x70, obfuscated vec3 container; likely position), 19 0xc673d0
  vec3, 20-28 nine sub-decoders 0xc5c720..0xc5caa0, 29-34 tail (0xc670b0, 0xc5fd10,
  0xc61ce0). Float component 0xc67260: changed bit; selectors over widths 8/10/24
  (table 0x2d17d88, sign-extended) else raw s32; value = prev + q/1024 (or /256).
  Next: SIMD scalar support in emu-78.py, decode the +0x70 container, send a spawn
  position, then revisit camera/input.
- Follow-up (Claude, 2026-10-14): emu-78.py now has a scalar/packed SSE subset;
  float component unit tests pass (0xc67260). snapprev-79.py overlays runtime
  default object 0x2f82d30 from the run-78 dump: the default prior position and
  the +0x20 vector are (0,0,0), so minimal snapshots put the hero at the origin.
  Position = 0xc606c0 first (ungated) 0xc673d0 call: three changed bits (16-18),
  q/1024 when out+4 bit is 0; stored XOR-encrypted (rolling key +0x10, 7-entry
  step table). +0x20 vector: gated by bit 19.
- Camera view classes: labels at 0x68c097..0x6ac357 ("First Person View" 0x698f07,
  "First Person Spectate View" 0x698d57, Orbit/Lookat/Spectator...). Heap census
  (vtable-census-79.py) in run 78: one 0x2613450 instance, three 0x26135b0; no
  direct references from root/world context slots (pointers likely encoded).
- Practice mode record 023000000000005a (root 494c33c4, 4 instances) references
  0c000000000280c0 (type 4) and 05800000000013c0 (type 0x1b, likely statescript
  graph). record-references-75.py has a bundle fallback. Hypothesis: HUD/camera/
  hero-select are driven by game-mode statescript state the server must replicate.

## Game-mode/statescript direction (Claude, 2026-10-14)

- record-deep-refs-80.py (brute-force all qword x field-hash references, bundle
  fallback): Practice mode 023000000000005a -> ruleset schemas 0a30..0060/0006/0008
  (0xc6, field e04197af) and statescript graphs (0x1b) 05800000000013c0 (cf63b633),
  0580000000000c8e (76e8c82a), 0580000000000c90 (a2781aa4); no entity definitions.
  Map header 0790..0688 references only its game modes (0230..18, 0230..5a).
- Runtime component 47 = STUStatescriptComponent (serialized fd024f42); on both the
  controller and the hero. vft 0x2611f68; slot 0x18 0xbc19e0 = generic visitor on
  state +0x20, whose reflected type 0x30db340 (hash e458e69e) has ZERO fields, so
  statescript state does not ride component reflection. Component 47 getter
  0xbe9db0 (mask 1<<47); users cluster at 0xa11768..0xa16e82 next to module-1
  per-entity reader 0xa16ad0 -> module 1 is the likely statescript replication.
  Module 2 (0xb3a490 -> 0xb40130/0xb24600) also neighbours component-47 users.
- stu-type-80.py prints runtime type descriptors (+0x28 fields x0x38, +0x90 count,
  +0x98 size, +0xb0 hash, kinds = crc32 lower-case names); component-inspect-80.py
  prints any component's vtable/state (args: dump pid out entity --methods TYPE).
- Next: deobfuscate module-1 reader 0xa16ad0 (and 0xa16e82 etc.), determine the
  per-entity statescript payload (graph instance/variables), and use emu-78.py to
  find a minimal valid form before any live attempt.
- Dump-backed emulation (Claude, 2026-10-14): .local/re/dumpemu-81.py serves unmapped
  reads lazily from a minidump at its real image base (code from image.bin).
  mod1emu-81.py runs module-1 per-entity reader 0xa16ad0 (vtable 0x263c3c8 slot 0x38
  = 0xa13b90 wrapper: rcx=secondary-0x18, rdx=stream, r8=&info+0x2c entity id,
  r9=info[0], 5th=info+0x24) on run-78 world state with: synthetic TEB (gs:[0x40]=PID,
  gs:[0x58] TLS blocks with epoch 0x7fffffff), stub 0xb7c60 (Codex's PID transform),
  bump allocators for 0x18512c0(rcx size) / 0x1854900(rdx size), rep stos/movs, bnd,
  bt*. emu-78.py also tracks a call stack (e.cstack).
- Module-1 framing (all-empty, 38 bits, accepted): presence 1; 0x787be0 bit;
  0xd53000 flag+u16; 0xd531b0 flag+u8; 0x996450 statescript-sync list bit (0=none;
  1 -> 0xd53330 flag+4 bits, then 0x99654f bit ...); 0xd531b0 flag+u8. The reader
  queues the payload (0xa132e0, time +0x1f40); semantic application is deferred.
  Next: emulate the deferred statescript consumer on dump state.
- Statescript sync decoder 0x996450 (FourCC-tagged field readers, edx = tag):
  'SFSF' 0xd53000 (flag+u16) -> obj+0 base frame; 'SFDt' 0xd531b0 (flag+u8) ->
  obj+4 = base+delta; bit -> optional 'Part' 0xd53320 (obj+8 index, else -1) and a
  bit at obj+0xc (likely last part); 'Size' 0xd531b0 -> 0x7c0f00 copies a raw blob
  into obj+0x18 (bit buffer). The queued object (0x58 B, 0xa07ef0) is later consumed
  by the statescript system; blob format is the next layer to decode.
- Statescript replication field tags (FourCC readers 0xd53000/0xd530e0/0xd531b0/
  0xd53290/0xd53320/0xd53400/0xd53510/0xd53620/0xd536e0; call sites enumerated):
  0xa0adc0 PIID/PSIn/SPUI/SrcI/SrcS (instance creation, via 0xa0c510 <- 0xa0e1d0);
  0xa0bab0 TmrU/DelT (timers); UVGu (vars, 0xa0bd50..0xa0c4c0); 0xa0c63e StDt;
  0xa0ca20 IVDt+UVGu; 0xa0cca0 RMFr/RMSz/TrID (remote messages/triggers);
  0xa0d4f0 StEC, 0xa0d545 SpEC/SpBN/SIID/SUDa/SPIn (state events, primary 0xa0d2c0);
  0xa0df50/0xa0e1d0 Inst; 0xa0f126 EIns; 0xd5744a/0xd590d0 ArrC/ArrS/ArrE;
  0xd57aa0..0xd58a53 ResV/HndI/HndS/HndD; 0x9b4160 CmFD/LBSS.
- Statescript consumer chain: 0x97a980 -> 0xa093e0 -> 0xa0e630 -> 0xa0e3c0 (frame
  interpreter: loop 0xa0e050 Inst records + 0xa0ee10 messages/vars; component
  +0x900 frame, +0x733/+0x734 flags, callbacks via [comp+0x50]). Direct path from
  module-1 reader: 0xa08f00 (comp47+0x690 manager, +0x738) -> 0x996450 -> 0xa0a3e0
  (frame-ordered insert). prim-81.py resolves chained .pdata fragments.
- Next: dump-backed emulation of 0xa08f00 + 0xa0e3c0 with synthetic blobs (tagged
  fields above) to learn instance/variable encodings; then decide what game-mode
  state (graphs 0580..13c0/0c8e/0c90) to replicate.
- Statescript live test (livestatescript80, PID 40392; window now 1920x1080:
  No Thanks 1782,1004 / Training 150,324 / Practice 960,540): responder
  --statescript DEF GRAPH (driver -Statescript 0,0x13c0 -StatescriptDelay 60) adds
  module-1 records (update_section in udp_welcome_reply.py). Controller comp47
  manager (+0x690): +0x908 frame 0->2, +0x900 0->354, +0xc4 1878->6118 = applied.
  Hero unchanged. No UI change. Tagged readers: 0xd53000 0/10/11 + 16/24/32 bits,
  0xd531b0 8/16/32, 0xd53320 4/8/16, 0xd53290 zigzag, 0xd53400 unary count.
  Processing rule 0xa0e630: list +0x748/+0x750, needs +0x8d8, cf=+0x908; discard if
  base+delta<=cf, wait if part>=0 or base>cf+1, else apply 0xa0e3c0.
  Next: try graphs 0x0c8e/0x0c90 too, on a game-mode entity if one is needed;
  decode variable (UVGu) and state-event (SpEC) records to drive game phases.
- Runs 81-83: multi-graph statescript on the controller. Per-instance encoding:
  create 0, present 1, u16 graph, 4 absent flags, nested Inst count (0+4 bits);
  then var bit and two message bits. New opt-in probe `--lobby-preload-graph`
  (20505 list 1, type 0x1b; driver -PreloadGraph) makes graphs resident (status 4).
  Run 83 (0x13c0+0x0c8e+0x0c90, fixed encoding): client exits code 1 ~1 s after
  records start (no dump). Bisect graphs before reuse; consider a dump trigger on
  the first statescript send. Graph records: root 7236f6e3; 0x13c0 references
  sub-graphs 0cbb/0bd6/0c8f/255d/0cb6 (field c71ea6bc).
- BLOCKER CLEARED (runs 84-87): 'Inst' in 0xa0e1d0 is an instance-ID delta (0 ends);
  each create = 0, 1, u16 graph, 4 absent flags; instance table at manager+0x58
  (+0x10 entries x0x40, id word +4, graph GUID +0x20, count +0x18). Duplicate IDs
  are rejected by 0xd55d30. livegraphs87 (PID 18468): controller has instances
  1/2/3 = 0x13c0/0x0c8e/0x0c90; a red "prohibited" HUD icon appears (first
  statescript-driven HUD). Graphs are resident without preload. Emulator tools:
  .local/re/ssemu-82.py, ssrun-82.py, ssproc-87.py (runs real processing loop
  0xa0e630 on dumped records; arg/return probes).
- Next: decode variable (UVGu/IVDt/StDt) and state-event (SpEC/SIID) records to
  move the game-mode graphs into hero-select/spawned states; the prohibited icon
  suggests the player is in a restricted (e.g. spawn/pre-game) state.

## First-person control (Claude, 2026-10-14, livehero89..liveowned93)

- Statescript frame body decoded (docs/BGS_PROTOCOL.md "Statescript frame body"):
  Size counts bits; instance bit 1 = destroy, update = 0,0; IVDt/StDt masks
  (0xd530e0 byte-presence form); full snapshot (CmFD > manager +0x900) makes StDt
  cover all states. Private responder --statescript-hero GUID enters 0x0c90 state 0
  (StateHero, generic client class). --statescript2 1,<graphs> creates Soldier's
  nine definition graphs on the hero. Emulator tools: .local/re/sshero-89.py,
  sscreate-89.py, ssactive-89.py (running nodes), ssinst-89.py, view-lists-89.py,
  stu-dump-89.py / graph-trace-89.py / graph-forward-89.py (OWLib names, reference).
- LOCAL CONTROL GATE: command writer 0x7cc060 and first-person reader 0x7c7900
  need a world entity with component 59 (owner+0xa0 per-type lists, 0x699530).
  Create flag 0x10 -> builder vtable 0x2615ae8 -> 0x64ee90 adds 59/63 iff the
  entity ID == world owner+0x298 (20302 selection, 0x586060); flag 0x20 adds 74.
- liveowned93 recipe (driver): ... -SelectDefinition (20302 controller at 45 s,
  after diagnostic 0xc0000001 at 30 s) -CreateFlags '0:0x10' -LateDefinition 0,50
  (controller created only after its selection). Result: FIRST PERSON Soldier view,
  mouse-look, client streams input packets. Public DefinitionCreate(create_flags=).
- Responder reply bound (2000) is now reached early: raise it. Red vignette = no
  health replication. Next: decode client module-3 input commands, reply with
  movement/health state; then weapons/abilities.

## Hero-change UI, teleport and spawn-room frontier (Claude, 2026-10-15, runs 101-108)

- Statescript entries run on the client only when `m_clientOnly`; other entries are
  server-driven (their effects arrive as state sync). Practice tree (13c0/0c8e/0c90 ->
  62 graphs, 16 with UXPresenter): private .local/runs/practice-subgraph-tree-100.json,
  .local/re/subgraph-tree-100.py, graph-bundle-scan-100.py, graph-288b/20e4/288a-100.txt.
- 0c90 state 119 runs container 0x288a whose state 0 runs 0x288b (hero-change UI:
  client-only entry -> BoolSwitch owner==local player -> UXPresenter state 92).
  liveui103: creating 0x288b directly as a controller instance makes H show the
  original "You must be in a spawn room to change heroes". Activating 13c0 state 5 /
  0c90 state 119 via full snapshot (runs 101/102) gave no visible change.
- TELEPORT: create flag 8 transform is ignored for the hero's movement. A module-3
  snapshot with only fields 16-18 changed (position x/y/z: changed 1, selectors 000,
  raw s32 q, value = q/1024; 140-bit movement block, emulator-verified) teleports the
  hero; send a few, then stop (client prediction continues). Responder
  --spawn-snapshot / --spawn-sequence 't:x,y,z;...' (driver -SpawnSnapshot/-SpawnSequence).
- Map entity census (entity-census-63.py + entity-positions-103.py on liveui103):
  component-1 position at comp+0x90 (xyz). Candidates: (1,12)x2 at (26.0,13.5,-18.9)
  rooftop and (90.1,10.6,36.4) doors; (1,6)x5 volumes (size +0x50); (1,110)x15,
  (1,111)x18, (1,38)x10 markers. (48.7,6.3,37.8) is a spawn-room-like interior
  (monitors/benches). All teleports still show the spawn-room message, also with
  welcome +0x78=1 (liveteam108). Spawn-room ownership/team gate is unresolved.
- Graph 0x288b condition types E72F6348/3D5F853C (m_entity) register evaluators at
  0xcfb290/0xcfb1d0 (vtables 0x2663070/0x2663968); E72F's evaluate 0xce4a60 is a
  generic entity-reference evaluator, not the spawn-room test.
- Window can be 2560x1080 (pillarboxed): use .local/re/ow-menu.ps1 -Prefix <runs path>,
  which picks menu coordinates from the reported width. Run 106 was wasted by 1920
  clicks on a 2560 window. Runs 99-108 cleanup audits pass (99 fatal-exited on
  forced weapon states; 100 never launched).
- Next: find the native/statescript "in spawn room" test (team assignment, spawn-room
  volume membership), then hero select -> 21605/21607 -> create chosen hero at spawn.

## HERO SELECT SCREEN REACHED (Claude, 2026-10-15, runs 109-111)

- Spawn-room test in 0x288b = config var E4C6AAB4(self) -> evaluator vtable 0x26643e8,
  evaluate 0xcf1f40 -> component getter 0xd0c210 (mask 0xbcb8e0 = component **74**)
  -> byte comp+0xf6. Component 74 (added with create flag 0x20; builder B) has
  replicated state at comp+0x70 (9 fields: u64 36bb7775, s16, s8, u8, u8, s8,
  **u8 field 6 = +0x86 = spawn-room flag**, u8, u8); component 64/65/75 also appear.
- Private responder --controller-comp74 '6=1' (driver -ControllerComp74) adds comp 74
  state to the controller create (with -CreateFlags '0:0x30'); together with the
  0x288b instance and a teleport into the spawn room (48.71,6.31,37.77), H opens the
  ORIGINAL "SELECT A HERO" screen (livespawnroom110). With all 56 hero records in the
  20505 hero list (liveroster111b) the full 32-hero roster (tank/damage/support) shows.
- Picking Tracer + CONTINUE makes the client send reliable **21616** {struct{u32 entity},
  blob(0x28), u64, i16}: entity = controller 0x80000304, u64 = game message
  0x0240000000001360, i16 4, 23-byte parameter blob. Also 21602/21603 (empty) early.
  Private decoder .local/re/decode-21616-111.py. Next: map the blob to the chosen hero,
  then server-side: create that hero's definition entity at the spawn point, link
  the controller's comp44 actor, give health, and send the hero graphs.
- Driver window size may be 2560 wide: always use .local/re/ow-menu.ps1. Never launch
  a new run until the previous run's launcher has exited (driver refuses).
- 21616 decoded (2026-10-15): it is NOT the hero choice. Graph 0x288b node 21
  (STU_79A131B4, client game-message action; runtime descriptor RVA 0x3175af0) sends
  game message 0x0240000000001360 with ONE param 0x0a400000000005a2 = var cb7a.
  Blob = u32 0 | u8 param count | GUID byte-presence mask (0xc3) + nonzero GUID bytes
  (a2 05 40 0a) | value bytes. Server side of the same graph handles it: entry #1199
  (STUStatescriptEntryGameMessage, node 22, param 05a2 -> var 8609) -> condition #1203
  (var 8609 and E4C6AAB4 spawn room) -> SetVar #1207 / game message 0x13ef. Our
  responder must emulate that server-side graph result (vars/state/messages).
- Likely hero-pick message: node 29 (client-only STU_79A131B4) game message 0x1361 with
  param 0x0a4000000000005d = STUConfigVarHero; NOT sent when Tracer was clicked in 111b.
  Next: find what gates node 29 (its state/inputs in 0x288b) and the hero select UX.
- Runtime reflection descriptors carry OWLib INSTANCE hashes at +0xb0 (SetVar 75001a77
  at RVA 0x31748f0, SendGameMessage bd6f5f83 at 0x3175670, STU_9AE5FC4C fields
  176ed263/37ab13d3 = controller/hero). Beta lower-case CRC names (Prometheus STU.h,
  e.g. UXHeroSelectScreen 0x8F23FA30, SendHeroSelection) are absent from retail.
  None of the 34 retail types with field 37ab13d3 is a direct statescript node type.
- 0x1361 gating chain in 0x288b (all client-only): UX entry #1009 STU_EB19DAFA (id
  0d800000000065d3; sibling #1043 id ...65d0) -> cond #1012 !var 2222 -> cond #1016
  var 2163 (false -> local message 0x1402) -> cond #1020 var 4208 -> SetVar be44=false
  -> node 29 sends 0x1361 {0x0a4000000000005d: STUConfigVarHero}. 4208 is an
  expression over local vars 8d63/4837/6b0c/ac03 (4837 = the STU_9AE5FC4C hero
  availability input). Synced vars (m_syncVars, 32 slots) include 03ac (hero), 0986,
  3369, 7acb, 1c61, 0842, 6321, 01de, 07b2, 09d5, 1cbb, 8017, 8793; the chain's
  locals are not synced. Next: read the live instance's local values at the pick
  (which condition fails) and which synced var feeds 2163/4208.
- What unlocks the hero pick (graph 0x288b, from .local/re/varwriters-112.py and
  graph-trace-89.py <dump> <node> <depth>):
  * var 2163 is written ONLY by StateStack #1459 = state index 35 / remote-sync index 3
    (value true while active; remote-sync var 6321). Server must activate it.
  * var 4208 on the client is written true by #1654 inside StateGameMessageEntry #1649
    = state 71 / remote-sync 5 when game message 0x02400000000006e4 arrives; other
    writers (#1247, #1604, #1897) are server-side.
  * SERVER handler of the pick: entry #1227 STUStatescriptEntryGameMessage for 0x1361
    -> conditions #1231/#1235/#1239 -> SetVar #1243 -> #1247 (4208=true) ... (the
    server's hero-change logic; continue tracing forward from #1227 to see which
    synced vars/states/messages it produces, e.g. hero var 03ac).
  * Responder full-snapshot activation (--controller-states 'inst:states') needs
    GRAPH_COUNTS[0x288b] = (32 sync vars, 146 states); instance 4 = 0x288b in the
    run-110 recipe. Delivering a game message to the client (0x06e4) is not yet
    implemented (statescript message records RMFr/RMSz/TrID, 0xa0cca0).
- Runs 112/113 (2026-10-15): run-111b recipe + -ControllerStates '4:35'
  -ControllerStatesDelay 63 (full snapshot activating 0x288b state 35; responder needs
  GRAPH_COUNTS[0x288b]=(32,146)). 112 is INVALID: responder crashed at the first
  snapshot (module-level --controller-comp74 code rebound global _mask; fixed by
  renaming to _c74mask), the client then timed out back to Training. 113: no crash,
  hero select + Tracer pick work, CONTINUE no longer closes the screen, but the
  client still sends only 21616 0x1360 (same blob), no 0x1361. Next: confirm on the
  dump that state 35 is active / var 2163 true, then the 4208 gate (state 71 + game
  message 0x06e4, or m_60DB8F99 semantics on #1033), and the server's #1227 result.

## PICKED HERO SPAWNS (Claude, 2026-10-15, runs 112-120)

- Graph dumps print u16 var ids BYTE-SWAPPED ("4208" = var 0x0842). m_60DB8F99=1 vars
  are entity-GLOBAL (0x1ba56e0); write them via the body's global UVGu list (0xa0c440).
  Value = kind(4)+payload (0xd57de0) + StEC count 0 (one 0 bit). Bool kind 0 + bit; GUID
  kind 9 (0xd57a20 type 4 'ResV': bit, hi u16, SFDt low). Details: docs/BGS_PROTOCOL.md
  "Hero select and the picked-hero spawn". .local/re/graph-walk-112.py decodes ids and
  expressions (0 end, 2/3 n AND/OR jumps, 8 dyn var, 14 cfg var, 30 NOT).
- H -> client 0x1360 {05a2 = !0x0986}; server sets global 0x0986. Portrait -> 0x1361
  {005d = hero}. Private responder: --hero-select-server (0x1360 toggles global 0x0986,
  bumps full-snapshot frame/CmFD), --hero-on-pick IDX (create that definition only after
  0x1361, GUID from .local/re/hero-storage-probe-66.json, global 0x3369=hero, 0x0842=1,
  then 6 spawn snapshots at --pick-spawn). Driver -HeroSelectServer -HeroOnPick 1.
  Needs -ControllerStates '4:35' (full snapshot path; GRAPH_COUNTS 0x288b=(32,146)).
- livepickspawn120 (PID 27860): H -> roster, Tracer -> 0x1361 -> Tracer gameplay entity
  0x0400000000000001 created -> first-person Tracer arms in the spawn room, overlay shows
  CHANGE HERO. Invalid: 112 (responder _mask shadowing), 116 (JSON tuple keys), 115
  (wrong ids -> client exit 1), 117 (0x6321/0x0842 set -> H no longer opened).
- Next: activate remote-sync state 36 (#1463: 0x0986 true + state 142 -> UI) for hero
  select at load-in; deactivate it / clear 0x0986 after the spawn; then hero graphs
  (weapons/abilities/HUD from the picked definition's component 47) and hero changes.
- LOAD-IN HERO SELECT -> SPAWN -> CONTROL (runs 121-125): activating states 35/36/37/142
  by full snapshot does NOT open the UI (121/122). Writing global 0x7acb=1 and
  0x0986=1 (-ControllerVars 'g:7acb=1,0986=1' at 63 s) opens the original SELECT A HERO
  automatically (123). UX event 65d0 is CONTINUE: portrait then CONTINUE sends 0x1361
  (123 never pressed CONTINUE). liveautoselect125 (PID 29040): auto hero select ->
  Tracer + CONTINUE -> Tracer created/teleported -> -CloseHeroSelect 4 36 clears
  0x0986/0x7acb -> overlay closes; first-person Tracer moves (W) and turns (mouse) out of
  the spawn room. 124 failed at instance startup (client exit 1 after 7 datagrams,
  unrelated; identical config to 123/125). Red no-entry crosshair, no weapon/HUD yet.
  Next: create the picked hero's own graphs (definition component 47 + weapon scripts).
- Picked hero's own graphs (run 126): .local/re/hero-graphs-125.py dumps every hero
  gameplay definition (stu-dump-89.py -> .local/re/defs/) into .local/runs/
  hero-graphs-125.json (54 defs: component 47 graphs, weapon manager 0x15, weapon
  scripts, child entities). Responder --pick-graphs JSON (driver -PickGraphs) creates
  graphs+manager+weapons (<=15) on the picked hero after its spawn. liveherographs126
  (Tracer: 1a,24,34,33,43,4b,3d,8b6,15,16): a world-space cyan chevron marker appears;
  still red no-entry crosshair and no pistols. Child entities (Tracer 0x169, 0x17 x2;
  m_childEntityData hardpoints) are not created yet; weapon states are server-driven
  (forcing them crashed in run 99). Next: child entity creates with parent/hardpoint,
  then the weapon/game-mode state that clears the no-entry crosshair.
- livenomode127: controller graphs only 0x288b (-Statescript 0,0x288b; -ControllerStates
  '1:35'; -CloseHeroSelect 1 36) + full -PickGraphs map: auto hero select/pick/spawn/close
  still work and the red no-entry crosshair is GONE (it comes from the game-mode graphs
  0x13c0/0x0c8e/0x0c90, probably a pre-game weapons-disabled status: 0x13c0 has five
  STU_37D754C8 states with ids in m_F09A03B3). No crosshair/pistols: weapon manager
  0x15 is server-driven (remote-sync states 13..44, sync vars 0x21,0x22,0x2565,0x53c6,
  0x04ca,0x0f0c,0x0f10,0x1e50,0x00f3,0x2536,0x0ebc,0x003d,0x787e,0x001f; entity-global
  0x001d weapon list). Prometheus beta set hero 0x001d=[1] and 0x00FD=1 (0xFD unused in
  retail graphs). Array values = kind 15 subkind 4-7 (0xd57430, ArrC/ArrS/ArrE).

## WEAPONS: StDt per-state form + cosmetic states (Claude, 2026-10-15, runs 128-131)

- StDt entries (0xa0c620) are NOT uniformly (has-data, active): 0xf5e960 checks the
  state's STU type hash; 458 types (StateStack, CosmeticEntity, CD46AF93, BD02E168, ...)
  read ONE active bit, the rest has-data + active. Entered states may read state data
  (0x1b72060; zero bits for the ones tested). Private lists: .local/runs/
  stdt-onebit-types.json, graph-state-types.json; responder _stdt_entry() uses them.
  Earlier 2-bit encodings (113-130) misaligned everything after the first state.
- Emulator check: scratchpad ssfull.py runs a responder-encoded full snapshot through
  0xa0a6e0/0x996450/0xa0e3c0 on a dump (stub destructor 0xf63740) and compares the
  record's consumed bits (rec+0x34) with the blob size (rec+0x30). ssactive-89.py's
  "no running nodes" is unreliable (its loop aborts on the first emulator Stop).
- Hero arrays: kind 15 subkind 6 (0xd57430): ArrC count, list bit 0, same-type bit,
  elements via 0xd579c0 (kind+payload). -PickWeaponList 1 sets hero global 0x001d=[1].
  -PickStates 'inst:s,..' (hero instance order = pick graph order) in a hero full
  snapshot; counts for Tracer graphs added to GRAPH_COUNTS.
- livecosmetic131: preload 0400000000000017/18 (-PreloadDefinition) + PickStates
  '9:39,43;10:0,1,30' (weapon manager 0x15 states 39/43; weapon script 0x16
  CosmeticEntity states 0/1, UXPresenter 30) -> Tracer's PULSE PISTOLS render in first
  person. CORRECTION: the "39" on the right pistol is a fixed marking (present before
  any click), NOT an ammo counter; firing is not demonstrated. livehud132 also activates
  remote-sync UXPresenters 0x1a:32, 0x24:32, 0x34:13, 0x16:30/31: no HUD/crosshair
  appears (they likely need their synced vars, e.g. 0x2ad4/0x73ed/0x001f/0x001c, or
  game-mode HUD context). Run 128 = early instance failure (unrelated).
- HUD frontier (runs 134-138): game mode 0x13c0 state 21 (sub-graph runner STU_37D754C8)
  runs HUD root 0x0cb6 (client-only), which runs 0x106b (17 UX presenters, mostly under a
  GameMessageEntry waiting for 0x0240000000000717), 0x2056, 0x0dea, 0x0ec8, 0x1fc0.
  Responder: --controller-subgraph 'id:graph:piid:psin' (create with parent link in the
  first controller full snapshot) and --state-data 'graph:state=v:w,..' (13c0:21 =
  0:1,3:4,0:1). livehudsub138: instance 3 = 0x0cb6 exists live; no nested 0x106b and no
  HUD yet. 21616 records can follow other records: the responder now walks them all
  (136's pick was the second record). Runs 134 = early instance failure (unrelated).
  Next: deliver 0x0717 via the message section (0xa0cca0) or create 0x106b with PIID 3
  / PSIn 0; then firing (client command buttons, 0xc2ddc0) -> WeaponVolley state 8.
- livehudsub139: also created 0x106b as instance 4 (PIID 3 / PSIn 0, GRAPH_COUNTS
  0x106b=(32,22)): still no HUD. UX presenters likely also need the 0x0717 message
  delivered (message section) and/or the client's in-game UI layer; not established.
- Message section attempt (emulation, run-139 dump): responder _messages()/msgs param
  (group bit, RMFr, RMSz, per message bit, mode bit, 8-bit length, TrID+Part+node).
  Without messages the controller full snapshot aligns (112/112, 0xa0cca0 entered at
  112). With a group appended, the decoder reads a new frame header (CmFD) at 112 and
  fails (ret 0): the full-snapshot tail before 0xa0cca0 is EIns (0xa0b850) then 0x9b40f0
  and a guarded call (0xa0f080 lines 39-99); encode that tail correctly before any live
  message test. Not used live yet (msgs default None keeps the old [EIns 0, msgs 0]).
- Message section fixed in emulation (run-139 dump): full-mode tail = EIns bit,
  continuation bit (0x9b40f0: 1 = another sub-frame), then 0xa0cca0; message length
  counts from its own start (8 or 17 bits). Mode 0 (8-bit) triggers ENTRY nodes
  (0x1b73b90, is-a 0x2eac9f0); mode 1 (17-bit) calls the node's vtable +0x38, which is
  the shared default 0x1ce5640 for GameMessageEntry states and UX presenters.
- Run-139/140 dumps (scratchpad ssnodes.py: 0x1b93000 node objects, +0x40 bit 0 =
  running): HUD root 0x0cb6 and HUD graph 0x106b nodes are RUNNING, including all UX
  presenters under the 0x0717 GameMessageEntry, already in 139. livehudmsg140 also
  sends a server->client 21616 (controller, 0x0240000000000717; --server-game-message):
  accepted without error, no visible change. HUD presenters run but nothing is drawn:
  the remaining gap is the client UI layer / data binding (local player/hero context),
  not statescript activation.
- livehudhero141: component 74 field 0 (u64) = Tracer hero GUID at controller create:
  no HUD. liveherostate143 (142 = early instance failure): controller graphs 0x13c0,
  0x0c90, 0x288b; on pick global 0x03ac = hero and 0x0c90 state 0
  (STUStatescriptStateHero, m_hero = 0x03ac*) activated (--pick-controller-states 2:0):
  no hero HUD, but the red no-entry indicator returns (0x13c0 client state 20 ->
  sub-graph 0x255d; its condition involves the 0x0c90 player state). HUD layer can
  draw; the hero HUD (health/abilities/crosshair) still needs its trigger/data.
- Early instance failures (124/128/134/142): identical first exchange; the client keeps
  resending 33-byte join packets, then exits 1. Intermittent; retry. Cause not found.

## FIRING WORKS (Claude, 2026-10-15, runs 144-145)

- .local/re/commands-144.py decodes client module-3 commands (0xc2ddc0); buttons:
  0x1000 primary fire, 0x800 edge, 0x2 Shift, 0x4 E, 0x10 Space (livebuttons144).
- WeaponVolley (Tracer 0x16 state 8, two-bit type 0xeed6d952) state data = signed int
  (0x1b736a0) + flag[+int+Part] + flag[+Part] + 6 bits; zero form
  '16:8=0:1,0:1,0:8,0:1,0:1,0:6' (--state-data) aligns exactly (emulator; emu.py now
  has idiv/bsf/bsr/prefetch*). Responder --fire-volley 10:8 (driver -FireVolley): fire
  press -> hero full snapshot frame (HERO_SNAP seq) with state 8 active, 250 ms later
  inactive. livefire145 (PID 28532): 4 clicks -> 4 volleys -> recoil, tracers, impacts.
- Next: ammo (0x0035/0x00c6), reload, abilities (Shift/E graphs 0x1a/0x24/0x34),
  practice targets/bots and damage, HUD.
- HUD binding (runs 146/147): 0x106b presenters read entity var 0x2698 (flagged; also
  an instance-scope read). Setting it to the hero entity (kind 13 entity value
  'IDVd' bit + u32; --hud-entity-var 'g:2698;4:2698') stores correctly (dump: global
  0x2698 = 0x80000305 type 0xa) but no HUD draws. Strings only show
  "Spectator_Show1PHeroHUD"/"Spectator_ShowGameModeHud" setting names (index tables).
- Bots (runs 148-150): hero records beyond the 32 playable ones (02e...016b-01f9,
  no weapons) are AI/bot definitions; 0x04000000000014d2 is shared by records
  0x0170-0x0172. Creating it works (entity 0x80000306 WORLD_RUNNING, 25 components incl.
  28/43/47/51) but it is not visible near the spawn: module-3 position snapshots
  (--extra-snapshot, repeatable) and the create transform (-SpawnAt flag 8) do not
  place a non-controlled entity there. Remote-entity position replication still to find.
  Map placeables 0x88/0x22e/0x234/0x289 have components 1,22,25,26,(58),76,94,97 only.
- livedummy151: a second Soldier gameplay entity (index 2) with the same snapshot is
  not visible either, so non-controlled hero-like entities are not drawn in this setup
  at all (not only a bot-definition issue). Likely needs team/filter-bit state
  (Prometheus beta spawner set FilterBits/team) and/or a spawned/visible state; the
  earlier "boot" render was the selected entity. Next for bots: find the filter-bit
  /team component state and remote-entity position replication.
