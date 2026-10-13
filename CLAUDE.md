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
data incl. 20802 -> original main menu + first-run TUTORIAL prompt. View the game
with scripts/Capture-ClientWindow.ps1 (desktop screenshots show the lock screen).
The "time out communicating with Battle.net" screens came from leftover clients
whose server had stopped (bounded runs leave the game running; close it first).
Accounts/launcher: `python tools/ow1_launcher.py configure|create|list|play`
(tools/accounts.py, store in .local/); `play Mercy` reached the menu as Mercy#1002.
Reliability (2026-10-13): 27/27 unattended launcher sessions reached the menu.
`play` waits for an exiting client/port and retries an instant client exit
(single-instance game). Don't drive the game window with desktop automation
during login; use scripts/Capture-ClientWindow.ps1 / Click-ClientWindow.ps1.
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
