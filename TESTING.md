# Build and verification

Final-retail update 2026-10-12: the supplied `1.74.0.0.104319` archive passed full extraction integrity; original EXE and selected CASC manifests match their hashes. Title/login display is directly observed. Native Practice request ownership and header availability are verified; repeated world/loading calls stay at idle state 2. Gameplay remains unverified. See [FINAL_RETAIL.md](FINAL_RETAIL.md) for reproduction. **CTest 12/12 passed**, plus the separate source-built manifest decoder’s synthetic input/output/bounds checks.

Disc update 2026-10-12: the signed disc client `1.0.1.27578` reaches its native title screen and, in the earlier missing-voice request probe, world-loaded state 5 / partial Hanamura rendering beneath the loading overlay. The new catalogue-import probe publishes an author-written empty catalogue through the native loader, but initial one-minute runs remain at world state 4. No controllable hero or completed gameplay session is verified. **The disc checkpoint passed 9/9 CTest targets** before adding final-retail bundle coverage. Native evidence and limitations are in [DISC_ADAPTER.md](DISC_ADAPTER.md).

## Requirements and quick start

Windows x64; Git; CMake 3.21+; Visual Studio 2022 C++ tools with v143 and Windows SDK 10.0.26100.0; .NET SDK 8.0. No game files are required for source builds or synthetic tests.

```powershell
git submodule update --init external/vcpkg external/imnodes
.\scripts\Build.ps1
$buildRoot = Join-Path $env:LOCALAPPDATA 'OW1-preservation-build'
& "$buildRoot\relay\Release\ow1-relay.exe" --bind 127.0.0.1 --port 6969
```

Stop the foreground relay with Ctrl+C. Embedded hosting uses loopback port 6969 and includes the local host in the 12-slot limit. The client tool window exposes connect, port and disconnect controls. In-game use is pending a verified beta client; do not run the beta patcher/DLL against retail.

The build script creates a detached local vcpkg worktree at the submodule's pinned revision, installs pinned dependencies, builds the relay, runs CTest, then builds the DLL and patcher. This avoids executing tools from a network share. `-BuildRoot C:\ow1-build` selects a separate cache; `-ServerOnly` omits client/patcher; `-SkipDependencies` requires an already populated compatible cache. Switching a server-only dependency installation back to a full client build requires a full dependency stage. A cached worktree at a different revision is rejected; choose a fresh cache instead of overwriting it.

Outputs and logs are outside Git: `<BuildRoot>\client\prometheus.dll` plus runtime dependencies, `<BuildRoot>\patcher\`, `<BuildRoot>\relay\Release\ow1-relay.exe`, and `*.log`. Keep runtime dependencies with their executables. Debug/Win32 configurations are not validated. The standalone CMake manifest pins the same baseline as the original client; when building both, the script installs the client's superset of dependencies and disables CMake's separate install step.

## Session evidence — 2026-10-10

| Check | Result | Scope |
|---|---|---|
| Unmodified upstream DLL Release/x64 | Pass | MSBuild v143; not loaded into a game |
| Modified DLL Release/x64 | Pass | Relay integration and game-thread changes compile |
| .NET patcher Release | Pass | `net8.0-windows`; no client patched/executed |
| CMake relay Release/x64 | Pass | Source-built standalone process |
| Full `Build.ps1` | Pass | Existing dependency cache reused; initial dependency source builds also passed earlier |
| CTest `protocol-regression` | Pass | Synthetic schema/range checks, golden BSON, identity, late-join/cache/lifecycle and capacity |
| CTest `relay-integration` | Pass | Child dedicated process, two-way meaningful movement data, hero changes, late join, reconnect, 12 sockets, excess admission and malformed sender isolation |
| CTest `client-inspection` | Pass | Synthetic PE reporting and rejection of truncated/out-of-bounds headers |
| BlizzGet NGDP probe build | Pass with warnings | External source, MSVC x64, ASCII metadata/config lookup only |
| BlizzGet final build config lookup | Failed, exit 3 / HTTP 403 | Separate controls returned 200; full client unavailable |
| Disc client isolated startup | Pass within stated scope | Corrected metadata/envelopes reach original title/login screen from a fresh ISO reconstruction; disconnected, no gameplay |
| Disc Hanamura voice-request probe | Pass within stated scope | Native state 5 / correct GUID, visible partial geometry beneath loading overlay, five-minute run without new crash report; speech omitted, no hero |
| Disc native world-stage probe | Failed | Assertion 3980(92)/3981/"2"; initialization requirements unresolved; not a playable transition |
| Disc staging / CASC verification | Pass within stated scope | 14 install files; all encoded records copied/hash-checked; CascLib reads original executable and English APMs |
| Offline launcher safeguards | Pass | Real AppContainer denies network, restores DACLs, rejects unknown patch fingerprints |
| Original gameplay | Blocked | Compatible adapter and local authentication/session handling remain missing |
| Hosted Windows CI | Pass | [Public run](https://github.com/p3n1cillin/ow1-preservation/actions/runs/38258001906): dependency install, source builds and 12 tests; protected/inherited legacy ACL fixtures included |
| Linux backend / Wine client | Untested | Source paths present, no execution evidence |

Last full CTest run: 12/12 passed (2026-10-12), including disc parsing/storage format, EN page integrity/bounds, old package bounds/decompression, bounded dump inspection, final bundle/STU table/field/string bounds, independent CRC/reference vectors, captured retail world/owner and diagnostic metadata bounds, and isolated-launcher safeguards (including final retail fingerprint refusal and correct mode routing). Separately, the native catalogue schema probe constructed the expected author-written empty root; native catalogue import is verified separately, but playable map/session integration remains unverified. Logs are local build artifacts; no benchmark or stability claim is based on this short run. Upstream DLL warnings include pointer truncation in STU, format mismatches, macro token-pasting and missing-return diagnostics. Some were addressed in touched code, but the DLL build is not warning-clean and runtime crashes remain plausible. Debugger reproduction is required before attributing issue #41 to a specific fault.

Run just the suite after a relevant change:

```powershell
$buildRoot = Join-Path $env:LOCALAPPDATA 'OW1-preservation-build'
cmake --build "$buildRoot\relay" --config Release --parallel 4
ctest --test-dir "$buildRoot\relay" -C Release --output-on-failure
```

Integration tests use an ephemeral loopback port, bounded event waits and a child process terminated during cleanup. A short readiness probe precedes participants; capacity assertions occur after its close. Fixtures contain synthetic zeroed movement fields with chosen frame/position values and synthetic hero IDs, not game assets or gameplay simulations. No private certificates or live service credentials are required.

## Next original-client smoke test

Final-retail diagnostics also cover immediate native update-state observations,
rejected/cleared map requests, context constructor/activation results, native
object identity/readiness, and bounded unique context-service discovery. The
synthetic world-profile tests reject malformed observations, context objects,
owners, duplicate services and oversized cache/subscriber counts. A real
two-minute PracticeContext run retained its map request and captured 433 native
updates, with highest returned state 4 and readiness still zero. The separate
no-context run now stops after native rejection, verified after three updates.
Neither result is a gameplay acceptance test; see FINAL_RETAIL.md.

The PracticeMetadata run also verifies original handler execution and a retained
native SDK request. Submission and completion occur, but the corrected result
is a local Hotfix-enumeration error (status 3/tag 2/code -1), and the context
stays unready. Synthetic coverage verifies SDK native identity, reference
lifetime bounds, unqueried/incomplete results, successful result fields,
structured errors and malformed flags. Internal SDK kinds are not wire-format
tests or evidence of private-server communication.

`bnet-probe-framing` tests fragmented input, truncated/malformed protobuf fields,
body-size limits and omitted secret/body bytes. These fixtures do not establish
original-client protocol compatibility. A bounded private-client TLS run reaches
the observing server twice and closes during handshake; native dynamic-code
policy flags are zero despite Win32 87 on the candidate mapped-page writes.
See FINAL_RETAIL.md for the actual run and corrected scope.
The isolation self-test also exercises host bridge teardown with a pending pipe
listener, so bounded cleanup does not leave a detached thread using its owner.

Latest continuation: the rebuilt native targets and **13/13 CTest targets pass**
with the CA option's unknown-build, bounded-lifetime, non-loopback endpoint and
private-key rejection checks. The five observer framing fixtures also verify
that a completed TLS connection followed by immediate EOF is not reported as
an RPC. These are guard/framing tests, not native login tests.

Native CA callbacks return parsed/inserted/unwind results 1/1/1. Real TLS 1.2
handshakes now complete; the peer closes before an RPC header. A no-CA/no-patch
control also completes TLS 1.2, so the handshake improvement is not attributed
to the CA import. Private-launch ShowIntro skipping is recorded by the guarded
native launcher. See the latest FINAL_RETAIL continuation for evidence and
reproduction; final login/gameplay remain unverified.

The latest rebuild and **13/13 CTest targets pass**, including the new observation
CLI safeguards. The native comparison additionally captures socket 1->2 with our CA and
1->3 without it, followed in both cases by retained job error 1016 (0x3F8).
The original callback establishes success versus chain failure. Observation
retains object lifetime only; no state/error/verdict flag is supplied. The CLI
regression rejects unbounded observation, other endpoints and unrelated
executables. Hardware-debugger experiments failed before any verdict and are
not shipped. See the newest FINAL_RETAIL continuation for evidence limits.

Run `scripts/Inspect-Client.ps1 -Path <authorized-client-folder>` before any patching. Check the exact executable/build and signature on an untouched backup, ensure data is complete, and establish the patch profile described in ROADMAP. Then use a debugger and record startup/logging, map load, controllable hero, collision, two-client movement, latest selection on late join, cleanup/reconnect and repeated unload. Record each outcome separately. Until those steps succeed, do not label map/hero/client integration as verified.

## 2026-10-13: own-key credential and encrypted lobby transport

Rebuilt all native targets and **14/14 CTest targets pass**. Added own RSA
roundtrip/address/tag checks, key type/size/exponent rejection, wrong-endian and
tag tampering tests, the public Crypto++ Panama-LE cipher vector and fragmented
stream checks. Seven probe fixtures cover one-byte TCP fragments through lobby
proofs/encrypted credential delivery, directional key mapping, post-handshake
24-bit packet limits/truncation and secret omission. CLI tests reject unscoped,
duplicate, even and wrong-size lobby public modulus inputs. CI installs Python
cryptography for these own-key fixtures; no native client/key is used by CI.

Native evidence is separate: two own-key runs advance the original lobby
handshake 4 -> 6 and connection phase 5 -> 6, then transmit a 10-byte framed
application packet. The control with the original trusted modulus rejects our
same credential and sends no post-handshake packet. Exact original executable
SHA256/signature and saved client-folder/launcher-file ACLs remain unchanged;
owned clients, launchers and observers were stopped. Main menu, rendered final
map, controllable hero and private multiplayer remain unverified. The next
required implementation was the gateway's application negotiation/reply;
the newer checkpoint below supersedes that frontier.

## 2026-10-13: initial lobby identity and entering-game screen

**14/14 CTest targets pass** with 14 probe/codec fixtures. Added known-byte
bool/integer/string/fixed-array encoding, exhaustive truncation of that fixture,
oversized repeated counts, duplicate/invalid schemas, descriptor ambiguity and
recursive-table rejection. The initial reply only accepts build 104319 and the
server's local account and rejects duplicate hellos. No client bytes or account
captures are used by the tests. The native launcher is unchanged; new private
launcher logs default to ignored project `.local/runs` (`-LogRoot` overrides).

Native `lobby-identity3`: normal own-key credential/group-13 negotiation;
21800 body fully decoded/re-encoded (216 bytes), 81-byte reply 20500, continuing
heartbeats and direct UI observation of **ENTERING GAME…**. The run ended at
its 120-second bound. Main menu, rendered map, hero and private match remain
unverified. Two earlier TLS-timing failures never reached the application reply
and are not counted as reply rejection. Original EXE SHA256/signature and both
saved ACLs were checked unchanged after the completed run. Server/client logs,
captures and RE scratch are private in `.local/`; original full dumps remain
with the already-extracted client, outside Git.
The negotiation-only comparison reached hello/heartbeats without the identity
reply, but ended before a window capture. Its repeat failed during TLS startup.
No visual control or additional menu progress is claimed from those runs.

## 2026-10-13: initial key/hotfix/player notifications

All **14 CTest targets pass**, including **15 probe/codec/state fixtures**.
Added independent positional bytes for empty 20504/20505 and local 20502,
one-shot/order checks, unsupported/missing notification schema rejection, and
the read-only native-state inspector's exact-profile/pointer/flag guards and
secret omission. No original image or account payload appears in a fixture.

Three separate 180-second native runs compare keys, keys+hotfix and
keys+hotfix+player. Original key-context +0x40 is unset in identity-only and set
in each new run. The player run starts 60002 and repeating 42600 requests.
Heartbeats remain healthy; window captures are black, so no main menu/world is
claimed. The slot-22 player marker is false in the completed dump and is reported
as a snapshot only. Original EXE hash/signature and both saved ACLs remain
unchanged after these runs; owned processes and listener were stopped.

## 2026-10-13: queue layouts and plain instance-referral experiment

All **14 CTest targets pass**, with **24 probe fixtures**. New checks cover all
34 queue layouts, independent Training request bytes, malformed/trailing request
bodies, required protocol/schema identities, mutually exclusive experiments,
fixed mapped-loopback endpoint and locally generated session inputs. Native-state
fixtures guard queue counts/markers and omit identifiers/session contents.

Live `referral-plain3` and `instance-public1` reproduce main-menu input and
Training -> Practice Range via Computer Use. The original client receives plain
20600 (242 B); an immediate read-only inspection sees a transient native
instance-referral job. The final public dump has no job, zero queue records and
world WAITING/no request; no additional TCP connection or map/hero is verified.
The earlier seed0 prototype is an invalid transform control; plain1/plain2 fail
before application traffic and provide no referral acceptance/rejection evidence.

After the completed runs, the original EXE SHA256 and Authenticode signature
remain unchanged/valid, both saved ACLs match exactly, and no owned game,
launcher or port-21119 listener remains.

## 2026-10-13: corrected instance endpoint and UDP loopback bridge

All **16 CTest targets pass**, including the existing **24 bnet fixtures**,
two receive-only observer fixtures and a native pipe/datagram transport fixture.
The latter verifies bidirectional zero/one/33/4096-byte packet boundaries,
embedded NULs, rejection of a second source port and oversized datagrams,
recovery after rejected traffic, malformed frame rejection, partial pipe reads
and bounded pump shutdown. Launcher guards reject unbounded, wrong-port and
duplicate UDP forwards. Isolation and scoped ACL tests continue to pass.

`instance-endpoint1` corrects the second referral string, which the original
connection callback parses as IPv4:port rather than a token. TCP-only forwarding
still observes no extra connection. Read-only native inspection identifies the
alternate datagram path; no selector/verification/readiness flags are modified.

`instance-udp1` adds the explicit 1119:21120 UDP bridge: after menu/Training input
and 24000 -> 20600, the receive-only observer gets **39 datagrams, each 34 bytes**.
Host bridge totals independently report 39 outbound and zero inbound datagrams.
The client first shows ENTERING PRACTICE RANGE, then returns to Training after
the unanswered attempt. Final dump: zero queue records, no referral job,
world WAITING/no pending request. No authenticated game session or map/hero
is claimed. Private logs/analysis stay in project .local/; dumps remain outside Git.

After bounded shutdown, original EXE SHA256 matches and Authenticode remains
Valid; both saved ACLs match exactly. Owned game/launcher processes and the
TCP/UDP diagnostic listeners are gone. Source-only publication contains no
packet payloads, credentials, keys, client assets or dumps.

## 2026-10-13: key reconstruction and authenticated instance envelope

Rebuilt native targets; **17/17 CTest targets pass**. The new
`instance-datagram-codec` target runs six author-written fixtures covering the
22-byte positional header and independent GCM comparison, empty/nonempty/max
payloads, directional-key and nonce-prefix rejection, mutation of every packet
byte, truncation and size/type bounds, and authenticated unsupported version or
magic. Tests contain no native captures, client bytes or private keys.

```powershell
python tests/instance_datagram.py
```

Separate private evidence: read-only reconstruction passes 4144 inverse checks,
both scrambled blocks re-encode exactly and match our own referral inputs.
The public codec authenticates and regenerates udpreply6's 39 client/39 server
packets and udpflags7's 161 client/100 server packets exactly, including nonempty
payloads. This validation is local and is not a shipped capture fixture.

Native udpflags7's flags-3 replies advance acknowledgements/receipt bitmap and
produce nonempty type-1 traffic; direct window capture shows ENTERING GAME.
The responder caps at 100 replies/180 seconds and supplies no application reply.
The final dump remains WAITING/no pending world request. No map/hero or complete
application session is claimed. After bounded shutdown, exact original EXE hash,
Valid signature and both saved ACLs match; owned processes/listeners are gone.
