# Build and verification

Latest verification (2026-10-14): native targets build and **22/22 CTest targets
pass**. The metadata target now has eight synthetic fixtures, including separate
active/staged contexts, default-context readiness, initialization completion/error
lifetime and malformed identities/reference/count bounds. Reinspection of saved
udpmeta26/27/28/29 confirms the reader against original objects. These checks do
not establish map rendering or gameplay; no new game launch occurred.
The new preloader target has four synthetic fixtures covering bounded native
identities/arrays, resource-type classification, submission versus completion
and omitted identifiers/addresses. Its reader also reproduces empty engine
preload queues in saved udpapp11/21/udpmeta26/29.

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

## 2026-10-13: receipt windows and compact body primitives

Native targets rebuilt and **18/18 CTest targets pass**. Eight envelope/window
fixtures now include explicitly expected receipt bitmap values for gaps,
duplicates, signed-distance bounds, 64-bit window resets and wrap rejection.
Four bitstream fixtures use written expected bytes at 18/24/32-bit selector
boundaries, exhaust every shorter bit limit, cross unaligned/64-bit boundaries,
check padding/nonminimal input and reject type/size/value errors without
partially writing a compact value. No native input is used by CI fixtures.

Private native udpack8 verification: **224 client packets / 224 replies** open
and reseal exactly, and every reply matches next-sequence/receipt bitmap.
Counts by plaintext size: 0=75,13=4,33=145. This compares combined receipt and
normal-flag corrections; no application body reply is sent. Observer 180 seconds
started before client 150 seconds, and ended earlier. Bridge 225 out/224 in;
the extra outbound packet is not in the observer capture. UI ENTERING GAME,
later Training; final world WAITING/no request. Map/hero remain unverified.

Public compact-field primitives separately reproduce all 138/149 nonempty
type-1 bodies' first field from udpflags7/udpack8. This is a prefix comparison,
not complete message decoding. Native disassembly/captures/keys remain ignored.
Final cleanup checks original hash/Valid signature, exact saved ACLs and zero
owned native processes or diagnostic listeners. 8540434 Windows CI passed.

## 2026-10-14: join records and resource-load diagnostics

Build succeeds and **20/20 CTest targets pass**. Five reliable-record fixtures
now include written 21600 name/boolean/blob bytes followed by another record,
ignored upper boolean bits, truncation, invalid strings/blobs/padding and the
existing record/body bounds. Four new resource-state fixtures distinguish
catalogue presence from an absent/in-progress/completed load, traverse hash
collisions and reject corrupt counts, chains, memory and image profiles.

Private saved-run validation: all **1003** nonempty application bodies across
udpapp10/11/21 authenticate and re-encode exactly: 184/373/446 respectively,
including one 21600 join per run. All records total 3 joins, 974 21610s and
26 21627s. The native boolean byte's ignored upper nibble is preserved.

The earlier compact-prefix comparison did not identify the client-to-server
field correctly: its body starts with the reliable-module block, not the
server-to-client compact frame field. Complete reliable-body validation
supersedes that interpretation; the LSB-first compact primitive remains valid.

`retail_login_state.py --world-resource-state` rechecks saved udpapp10/11/21
dumps without writing client memory or invoking native code. The latter two
contain pending requests whose headers are in the catalogue but absent from
the load cache (raw state 0). udpapp21's optional mode resource has the same
result; udpapp10 has no request. Private arithmetic interpretation validates
the independent resource hash against the original routine. No new interactive
game run or rendered-map claim accompanies this source checkpoint.

## Metadata registration/retry checkpoint — 2026-10-14

Native targets build and **21/21 CTest targets pass**. Five new synthetic
fixtures cover registration versus content/context state, bounded/empty
samples, malformed owners/arrays/entries/flags, identifier/address omission,
and an independently written 108-byte 20318 message. All message truncations,
trailing bytes and incorrect fixed-array sizes are rejected. No captured
payload or proprietary bytes are used as fixtures.

The public read-only `--metadata-state` reader rechecks owned udpmeta22/24/25/26
dumps: one default-identifier entry, format 1, flags 0xa0, ten completed
acquisition attempts, no content and no current context. The entry's +0x80 is
a retry deadline and +0x88 a counter; earlier private pointer/marker names are
superseded. In udpmeta26 six completed kind-14 requests were additionally
sampled through live original service references; each failed with 3/2/-3.
The native error formatter classifies -3 as "failed to open", not a specific
Windows error. Own-directory creation and own-package-only modify access did
not make acquisition succeed. The original client still waits for an unrequested
map header. The latest owned-process/listener/profile cleanup and exact scoped
ACL restoration checks pass; the original signed executable remains unchanged.

## 2026-10-14: live preload comparisons and Hero Gallery

Five bounded 150-second original-client runs completed with passing cleanup
checks (owned launcher/responders ended, exact saved ACLs restored, original
hash and Valid signature retained). Three Practice runs compare baseline header
assignment, an additional header/mode resource list, and map-root assignment.
All visibly reach ENTERING GAME and end with pending WAITING requests, absent
header/mode cache objects and 28 other resource-cache entries. The map-root run
provides only about 20 seconds after selection. Corrected private native-request
checks verify both resource-list entries in both requests and the map-root
assignment in the third run; the earlier wrong-array reports are superseded.

Approximately 100-ms read-only observations have 1365/1330/1295 successful
samples respectively and zero rejected samples. Engine configured/retained
queues stay empty in the observed snapshots. This does not exclude activity
between samples or an alternate queue. Default contexts activate in Practice
without 20318. Two gallery controls have 1306/1390 successful samples and zero
rejections; their final world manager has no pending request or active context.
The gallery remains visibly empty, including after every rarity/category/
ownership option is enabled in the second control. No rendered hero or map
is verified.

The public world-resource reader now exports extra_resource_count from native
request +0xf8/count +0x100 and validates signed count bounds, alignment and
complete array reads. Saved public reports agree with the corrected private
reader (counts 0/2/0). Six synthetic resource fixtures include delivery versus
load state and malformed/truncated arrays. **All 22 CTest targets pass** after
the live clients exit; native launcher isolation and datagram bridge checks pass.

## 2026-10-14: native header control inside the private session

Native targets build and **22/22 CTest targets pass**. Eight resource diagnostic
fixtures now also cover aggregate cache states, duplicate object references,
count mismatches, cycles/shared nodes, unreadable objects and traversal budgets.
Launcher isolation checks reject the new control without its bounded own-key
UDP session and reject duplicate flags before any client starts.

`--preload-practice-header` is an opt-in launcher control used alongside
`--retail-private`, the own CA/modulus options and bounded loopback forwards.
It waits for the original pending Practice header/mode request and calls the
original resource loader once at its default priority. This is deliberately a
diagnostic preload, not evidence that the original server negotiation is solved.
It changes no world state/readiness value and runs no extra world updates.

Two 150-second live controls return successful scheduling, unwind registration,
native API call and resource reference. Their read-only cache observers have
1308/1325 valid samples and zero rejected samples; header and mode reach raw
state 3. Both final dumps have WORLD LOADING/pending managers, default active
contexts and 29 cache objects all at raw state 3. The map-root cache object is
still absent. A world observer in the repeat records WAITING -> ABANDONING
SCENES -> WORLD LOADING with 1269 valid samples; it follows the one manager
discovered before selection. The other is verified in the final dump.

Direct Computer Use in the repeat shows the original Practice Range loading
screen with map art, name and changing tip/spinner. It stays there: no hero
selection, rendered gameplay scene or movement/combat is verified. A fresh
map-root-only comparison remains WAITING, with 1309 valid samples and zero
rejections. All three live cleanup audits pass: exact saved ACL restoration,
original hash/Valid signature and owned launcher/server/UDP termination.

## 2026-10-14: WORLD LOADING scene gates

Native build and **23/23 CTest targets pass**. The new scene diagnostic checks
the corrected state-6 dispatch, original completion getter, world/scene identities,
signed array bounds and raw resource states. It decodes the scene pointer using
the original PID associated with the saved dump. Reports contain aggregate
counts and booleans only. Synthetic cases cover completed resources without
scene readiness, an incomplete resource, native signed-state comparisons,
wrong PID, malformed profile/boolean/arrays and absence of pointer text.

For a saved owned-client dump, supply the PID from that run's private log:

```powershell
python tools/retail_login_state.py --dump $savedDump --scene-state --client-pid $savedClientPid
```

Both prior loading-screen controls reproduce two managers, resource groups
4/2/0 with six raw-state-3 objects, scene_ready=false, active_scene_present=false
and pending_scene_present=false. The missing scene initialization is distinct
from resource completion. WORLD LOADED gates traced earlier are downstream.

New run livescene40 authenticated through native handshake state 6, but its
capture stayed black and window activation returned GetCursorPos Access denied
(0x80070005). Fresh window selection did not restore a usable view. No Practice
input was issued and the armed control was not invoked. The startup manager
stayed WAITING without a request; observers recorded 1020/1013 valid samples,
zero rejects. This run does not reproduce or advance map loading. The 150-second
launcher exited and all cleanup checks passed, including original hash/signature
and exact saved ACLs. Further live UI testing requires working Windows input.

## 2026-10-14: working live UI and typed-map scene construction

UI capture/input recovered and two bounded Practice selections completed.
Baseline livescene41 uses the existing header welcome and one native preload;
it reaches the original loading screen, with complete groups 4/2/0 and no scene
handles in either final manager. The live world observer follows the startup
manager through WAITING -> GLOBAL LOADING -> WORLD LOADING (1265 valid samples,
zero rejected); the resource observer records 1349/0. A late WAITING/no-request
sample near run end has no established cause.

livevariant42 assigns the exact typed map reference from header +0x50 in both
welcome map fields. The guarded header control now permits that exact Practice
map/mode pairing as well as the original header/mode pairing. Both controls
return successful native scheduling, unwind registration, API call and reference.
The second run constructs pending scene objects in both managers; active scene
handles remain absent and readiness false. All three groups are complete and
the two deeper scene completion resources are raw3, but both scene controllers
end at raw state 1 instead of the readiness setter's required 5. The original
loading screen persists; no geometry, hero selection or control is verified.

The initial world discovery in 42 exceeded its 10-second limit and produced no
samples. A 20-second/4-GiB bounded retry observes both managers after loading begins,
with 554 valid/2 rejected samples. This is not a complete transition trace.
Resource observation has 946 valid/0 rejected. Public saved-dump scene reports
agree with the private read-only checks, and native request comparisons confirm
the exact map reference/mode in both pending requests. Both cleanup audits pass.

Native build and all **23/23 CTest targets pass**. The scene diagnostic includes guarded conditional scene
controller progress, exact object/getter identities and bounded signed resource
states. Four synthetic fixtures cover resource completion before state advancement,
state 5 without the scene readiness flag, incomplete resources, malformed native
identity/state/pointers, wrong PID/profile and truncated data. The diagnostic
still exports only statuses/counts/booleans; private material remains ignored.

## 2026-10-14: canonical map and typed asset completion

Native build and **23/23 CTest targets pass**. Five scene fixtures now cover
separate typed-reference validity, pending/success/failure statuses, update count,
loaded/replicating snapshots and scene readiness. No client payloads embedded.

Saved variant42 has 3757 updates per scene object but a valid typed asset handle
with no object and native status 2. The state-1 handler waits for this handle;
raw-resource status 3 does not establish typed completion. Native typed status
3 denotes finished with failure, while status 4 denotes finished without that
failure flag. The report preserves these distinct status fields.

livecanonical43 supplies the canonical Practice map in both welcome map fields,
keeping the same one-shot original header preload. Input checks confirm both
pending requests and the Practice mode. Direct UI reaches the Practice loading
screen. The startup-manager observer captures resource completion, load progress
0 -> 2 -> 4 and scene state 1 -> 2, followed by WORLD LOADED (1043 valid samples,
zero rejected). Intermediate state 5 is not sampled. The second manager is
created later and is confirmed only in the final dump, at WORLD REPLICATING.

Both final managers have active scenes, pending handles absent, readiness true,
scene state 5, typed object present/status 4 and 4750 updates. Both raw-resource
groups remain 4/2/0, complete. The public snapshot reproduces these values.
The resource observer has 1286 valid/1 rejected sample. A late second world
observer starts during process exit and yields no valid snapshots.

The loading screen persists; no hero selection, actual geometry rendering,
movement or combat is verified. The next boundary is replication initialization.
The experiment still uses explicit diagnostic header loading. It does not solve
normal header initiation or change the default launcher behavior. Cleanup passes:
owned processes/listeners ended, exact saved ACLs restored, original hash and
Valid signature retained.

## 2026-10-14: selected entity and pending replication

Native build and **24/24 CTest targets pass**. A new guarded read-only snapshot
separates selected-ID validity, exact entity-table resolution and generation
mismatch from the replication context's queued/pending counts and completion
marker. Five synthetic cases cover unset IDs, generation aliases, missing objects,
pending work despite successful entity resolution, malformed profiles/pointers/
counts, truncated records and changing selection. The final queue extension
passes its targeted CTest rerun. Reports export booleans/counts, without IDs,
pointers, credentials or native payloads.

```powershell
python tools/retail_login_state.py --dump $savedDump --replication-state
```

The original update rejects an unset selected ID, then requires an exact packed
ID match with a non-null entity object. The normal 20302 handler assigns that ID.
The following comparisons retain canonical Practice assignment and the same
one-shot original header preload:

| Run | Submitted world's selected ID | Entity object resolves | Pending count | Completion marker | Final state |
|---|---|---|---|---|---|
| canonical43, saved baseline | Unset | Not tested by native gate | 4 | False | WORLD REPLICATING |
| select44 | Valid index-only ID; generation mismatch | False | 4 | False | WORLD REPLICATING |
| generation46 | Valid full packed ID | True | 4 | True | WORLD REPLICATING |
| delay47 | Same packed ID, sent 30 seconds after first welcome | True | 4 | False | WORLD REPLICATING |

Run generation45 stops before client launch because the private encoder requires
the signed wire representation of the packed ID. The corrected conversion is
used in 46/47; its failed startup cleanup also passes. Each completed new run
sends the same sequenced 20302 notification ten times. The private responder
accepts 230/230 client datagrams in 44, 367/367 in 46 and 355/355 in 47. Each has
one body outside the existing reliable-record decoder; these counts do not
establish a complete entity protocol.

World/resource observers have 688/0 and 739/1 valid/rejected samples in 44;
1071/0 and 1102/0 in 46; 1015/0 and 1064/1 in 47. Startup observers follow only
the first manager. Later bounded observers see both managers in 46 (202/0)
and 47 (335/0), after loading and notification delivery. They do not capture
the submitted world's notification or state transition. The timing comparison
therefore establishes different final completion-marker values, not their cause.

Direct UI captures in 46/47 show the original Practice loading screen throughout
the observed loading period. Final scene reports remain ready, active, state 5,
typed status 4, with complete raw groups 4/2/0. Scene update counts are 3008 in
44, 4872 in 46 and 4804 in 47. The selected entity's existence does not establish
a replicated player. No hero selection, gameplay geometry, movement or combat
is verified. The next investigation is the native pending-entry drain; its four
saved entries each have an empty dependency list, whose significance is unresolved.

All completed cleanup audits pass: owned helpers/listeners terminate, exact
saved scoped ACLs are restored, and original executable hash/Valid signature
remain unchanged. Public diagnostics reproduce the private aggregate checks;
raw captures and experimental responders remain ignored under `.local/`.

## 2026-10-14: WORLD_RUNNING, placeable codec and visible geometry

Resumed Claude's later map-placeable work. The four pending rows are replicated
placeables; minimal entity creates naming them clear the queue. A saved original
run55 snapshot confirms WORLD_RUNNING, queued/pending counts zero, marker true
and selected entity resolving. Independent liveverify58 reproduces this result;
its submitted-world observer captures GAME MODE LOADING -> WORLD_RUNNING in
35 ms, with 12719 valid samples, zero rejects and maximum queued count 133.
The initial observer only sees the startup owner. This run's final scene report
has two active/ready state-5 scenes with typed status 4 and 4706 update ticks.

`tools/instance_entities.py` now provides a bounded reader/writer for the observed
minimal server placeable section. Four synthetic fixtures cover an independently
assembled 95-bit vector, byte and non-byte alignment, 8/16/32-bit index widths,
empty/multiple/max-count sections, every truncation and unsupported forms/types.
The section requires class 0b100, empty earlier modules, both module-2 optional
bits zero, create operation, a 42-bit payload, no extra data/components and the
terminating chain bit. It does not implement hero definitions or a full server.

Private authenticated-capture checks preserve exact entity-section bits:

| Run | Authenticated replies | Type-1 sections re-encoded exactly | Placeable creates |
|---|---:|---:|---:|
| Claude livecreate55 | 545 | 543 | 400 |
| liveverify58 | 428 | 426 | 359 |
| livecodec59 | 390 | 388 | 322 |
| livecamera60 | 724 | 722 | 400 |

The private responder was migrated to the public codec before run59. That run
reaches WORLD_RUNNING and directly shows Practice geometry, with the map-name,
tip and loading spinner gone. The process exits at its bound before the first
menu input, so that attempted input has no established effect. A new 180-second
run60 reproduces rendering using a 30-second selection delay. Escape visibly
opens and closes the in-game menu, including Leave Game. A short W press,
mouse drag and H press show no camera displacement or hero picker. There is no
hero HUD or weapon; playable movement, combat and player replication remain
unverified. Animated clouds change while the camera remains fixed.

Submitted-world observers: run59 11411 valid/0 rejected, maximum queued128;
run60 18605/0, maximum queued67. Startup observers follow only the other owner.
Final dumps show WORLD_RUNNING plus WORLD LOADED, active/ready state-5 scenes,
complete raw groups4/2/0 and typed status4. Scene ticks59=4385,60=7322. The
scene snapshot now covers native states9/10 as well as6/7/8, with synthetic
checks; a running enum/readiness alone remains distinct from visible gameplay.

Native build and **25/25 CTest targets pass**. All three new cleanup audits pass:
owned services/launchers/listeners end, exact saved scoped ACLs are restored,
and original executable hash/Valid signature remain intact. The experiments
retain explicit header preload and diagnostic local-entity selection. No raw
captures, keys, native bytes or proprietary assets are embedded in public tests.

The bounded timing-field control livetime62 also visibly renders Practice
geometry, without a hero HUD or weapon. The native timing field is 49.085 seconds;
both controlled-actor markers are invalid. The selected diagnostic entity lacks
component 44, required by the traced first-person owner lookup. The read-only
replication report now exposes native-ID agreement and that prerequisite as
booleans, without IDs, masks or pointers. Component presence would still not prove
a playable actor. Six synthetic fixtures cover these checks. The prior run60
snapshot agrees. Run62 has 433 exactly re-encoded entity sections, including 366
creates; all 25 CTest targets pass after the game exits. Cleanup retains the
original hash/signature and exact saved ACLs. Clock synchronization semantics and
player/hero initialization remain unresolved.

The definition-create continuation independently audits the complete entity
tables: run62 has no component-44 candidate among 1019/1020 entries. A verified
final-retail definition is already ready in the native fallback typed cache.
Its absence from the raw cache therefore does not mean it is unavailable.

The welcome-list control livedefresource63 stays at HOTFIXING and displays the
loading overlay; final metadata readiness is false. Livedefcreate64 instead
keeps the baseline welcome and sends a minimal definition create. The original
engine adds runtime components 44, 25/26 and 84/85. A full census finds exactly
one component-44 candidate among 1021 entries in the running world. Practice
geometry visibly renders. Livedefselect65 successfully selects the new entity
using a later sequenced 20302, but its linked actor ID is invalid. H does not
show a hero picker or HUD. W is attempted after exit and has no established
effect. No hero control, movement or combat is claimed.

The reusable definition codec supports only the neutral type-3 resource-index
form, zero transform flags and empty network component state. Six synthetic
fixtures cover placeables and definitions, mixed sections, alignment, independent
bit vectors, truncation, unsupported flags and bounds. Public/private encoders
agree on all 659/673 captured entity sections in runs64/65, including 80 definition
creates each. The resource-list control separately verifies 522 sections. All
three cleanup audits retain the original hash/signature and scoped ACLs.

Hero preload (liveherodef68..70, liveherolist71): without 20505 hero list,
the selected hero create aborts (decoded labels and the formatted missing-definition
message in a triggered mid-run dump; repeated 21801/21802; flag-4 instance
packets). With `--lobby-hero-list` for the hero record, there is no abort, the
world stays running and the definition is resident (typed-cache census 150 vs
129). The probe test adds an independent 20505 hero-list wire fixture and
rejects non-hero types, duplicates, more than 64 entries and lists without 20505.

Controller actor link (livecontrol72/73): the final dumps report a valid
component-44 actor target that resolves to the hero entity. Run 73 has a valid
module-3 controlled-actor marker. The entity test adds an independent known
vector over 16 body alignments, mixed sections, self/class rejection, truncation
and corrupted mask/field bits. Private re-encoding of captured sections matches
723/717/717 sections exactly at their absolute body offsets.

After the codec extension, all **25/25 CTest targets pass**. The private responder
is migrated to the public definition writer after the live runs; exact captured
section equivalence verifies the migration without repeating a live baseline.

## 2026-10-15 — state encoding and longer bounded gameplay diagnostics

Full scripts/Build.ps1 -SkipDependencies completed successfully; all 25/25 CTest
checks pass. UDP/CA/TLS diagnostic bounds now permit 300 seconds. Tests accept
180/181/300 through the unrelated-executable fingerprint guard and reject 301,
while retaining endpoint, certificate and bounded-process requirements.

Offline native emulation on dump 200 tests two complete accepted snapshots. The
old inactive WeaponVolley entry omits 18 bits, consumes 316/312 bits and stops the
cosmetic. The corrected entry consumes 330/330 and leaves intended states active.
The minimal recipe without ancestors also preserves it at 282/282 second-frame
bits. Live run 211 confirms two registered McCree volleys/stops and one reload
with the revolver still visible. The experimental ancestor option can hide the
rifle after switching to Soldier, so it is excluded from the normal recipe.
Run 212 did not establish firing before its deadline. Cleanup audits for completed
runs retain the original executable hash/signature, restore saved ACLs and stop
owned processes. Private captures/dumps/scripts remain in ignored local storage.

## 2026-10-15 — HUD subgraph scheduling regression (run 252)

Rebuilt this agent's native tree with scripts/Build.ps1 -SkipDependencies; full
build succeeds and all 25/25 CTest targets pass (tests.log: 13.26 seconds).
Private responder syntax compilation passes. Offline replay uses run 250's actual
first snapshot and its own dump: original update-only subgraph entries return 0
at 3 bits; corrected creation returns 1 at 656/656 bits and the next activation
returns 1 at 607/607 bits. Both subgraphs exist after the corrected pair.

Live run 252 confirms first-send create flags true, then update flags false and
late activation in the following frame. The dump has all 12 server instances,
plus 0x0c90's client-spawned 0x1a36 and 0x20e4. Tracer's weapons stay visible;
firing and the original reload animation work. HUD remains absent. Native
condition evaluation reproduces selected-controller/hero-owner mismatch in
0x20e4 node 19; its three UX presenters are inactive. All seven cleanup audit
fields are true, original hash/signature retained, exact ACLs restored and owned
processes stopped. UDP error log is empty. Reference dumps 250/252 and private
replay/audit tools remain in shared ignored storage, listed in HANDOFF.md.


## 2026-10-15 continuation: runs 253-255 and Claude research

Controller sender 0x0cb6 state 3 consumes one compact-u16 zero payload bit after
its active bit. Native two-frame replay improves from 474/460 bits (invalid) to
492/492 and 461/461, with StateHero activation decoded. Run 254 preserves pistols
and firing but no HUD. Its native ownership gates require 20e4 on controller and
01cf on hero; hero 01cf still waits for 1291. All seven cleanup checks pass.

Claude's report/notes from branch d8b2998 are included. Original mode18 assets
confirm controller13c1, whose state42/node101 runs20e4 (64 sync slots,49 states).
Run255 cannot test gameplay: the diagnostic preloader admits only mode5a and
never calls the native header loader for18. The guard now explicitly accepts
both Practice modes. Follow-up requires rebuild after cleanup and a mode18 run.
See HANDOFF.md for private audit scripts, recipes and the message-order hypothesis.
The full goal and remaining acceptance requirements are in docs/PRACTICE_RANGE_PLAN.md.


## 2026-10-16 - Recall mirror audit and bounded run292

The private encoder now rejects active StateStack entries without two data bits.
Regression checks cover the four missing Recall Stack payloads that invalidated
runs284-288; valid and inactive forms still encode. Native client writer output
for Stacks15/28/33/35 is1,0, whereas experiment289 sent0,0. Adding omitted
states36/37 and sender37's zero bit gives a643/643-bit native full replay.
The private replay helper now uses the responder's normal STATE_DATA path,
including inactive two-bit payloads.

Run292 preserves floor spawn, native Blink, firing and manual reload. Two
Recall mirror pulses are accepted without crash, but neither rewinds. A dump
captured during the second pulse shows stage3 running and rewind0 inactive,
with Ability flag+270=0 and an empty deferred queue. The next investigation
is the authored stage3-to-stage0 handoff or the complete server timeline.
UDP stderr is empty and all seven cleanup/integrity checks pass. Four public
instance-bit tests and the guard/native replay checks pass. No fresh CTest or
native-build result is claimed; native sources were unchanged.
Private evidence and reference coordinates are listed in HANDOFF.md.

## 2026-10-16 - HUD parent correction and bounded run293

Corrected the private best recipe's hero HUD parent from graph 0x4b runtime
node 7 to authored state 3 (PSIn). Native comparison replay consumes 519/519 header
bits and 474/474 interpreter bits, and records the expected parent state.
Live 293 confirms parent 6/state 3, floor spawn, native Blink, firing and manual
reload, but the HUD remains absent. Controller widgets exist; hero listener 178
finds its sender while Stack 179 and presenters 181/62 stay inactive.

UDP stderr is empty and all seven cleanup/integrity checks pass. The 293 dump
was deleted after read-only analysis; 264 remains the routing reference. Private
helpers/reports are shared under .local/codex-scratch and .local/runs (hud293-*).
Three offline instance ticks on 264 see empty update queues and no callbacks;
this is a snapshot limitation, not evidence of a broken live scheduler.
Dump-time f0=0 alone does not establish whether a listener previously fired.
Next: trace sender parameter delivery and scheduling into listener 178 / Stack 179.
Recall and the full Practice Range requirements remain unresolved. No native
source changed or fresh CTest run was performed for this recipe-only change.
Python compilation and all four public instance-bit tests pass.

## 2026-10-16 - HUD ownership controls, runs 294 and 295

Corrected the earlier message-delivery diagnosis: native evaluation and variable
lookup on reference 264 show both widget-handle parameters present. Raw two-byte
STU labels must be read little-endian: labels 272e/d42a/ed73 name numeric IDs
0x2e27/0x2ad4/0x73ed. Earlier numeric lookups used different keys.

While controller message 1291's sender exists, the authored hero listener selects
controller ownership (Stack 180); removing it selects hero ownership (Stack 179)
and starts the hero presenters. Native sender-exit replay consumes 170/170 bits.
Live 294 confirms actual hero widgets are created, yet no HUD appears. The UI root
condition remains false. Message delivery and widget creation are therefore
verified steps, not the remaining visibility diagnosis.

Live 295 adds the authored Practice wrapper 288a under controller 13c1 state 43.
Its creation replay consumes 218/218 bits and the live client starts four child
graphs. Tracer first person remains; HUD stays absent, including after a native
menu open/close and Alt+Z keypress pair. Both runs have empty UDP stderr and all
seven cleanup/integrity checks pass. Their dumps are retained as distinct
references; shared helpers/reports and coordinates are listed in HANDOFF.md.

Private ssfull2.py now loads the mode18 graph state types and accepts an optional
SS_HERO_CONFIG metadata file. Missing types had made a supposed sender exit read
as state data instead. The focused entry/exit and metadata checks and Python
compilation pass. No native source or public runtime changed; no fresh build or
CTest result is claimed. The best recipe remains the run 293 baseline. Next:
trace root display/attachment while preserving the working ownership branches.

## 2026-10-16 - E0 named-mutex namespace self-test (no game)

New CTest target `offline-launch-mutex-namespace` runs
`ow1-offline-launch <launcher> --self-test-mutex`. It does not use any game
files, and no network capability is granted. The launcher creates its normal
temporary AppContainer profile plus a second one (`.m1`), and each passes the
existing network-isolation child probe. It then re-runs itself in-container as
`--mutex-probe <name> hold|release`. The child reproduces the final client's
MutexLock sequence:

1. `CreateMutexW` with the client's descriptor (Medium label);
2. on failure, `CreateMutexW` with the default descriptor;
3. on error 5, `OpenMutexW(SYNCHRONIZE)`;
4. on error 2, retry, up to 5 attempts.

The child accepts only reserved `Global\OW1-E0-*` names, never storage names.
Three cases are measured: cross-package, same-package, and a launcher-pre-created
mutex whose DACL names the owner, SYSTEM and both package SIDs, with a Low label.
For each object, the test prints whether it already existed and which kernel
directory class holds it. Session numbers and SIDs are not printed. The test
requires the following:

* both profiles are deleted;
* every test object is gone after its handles close;
* the exact launcher/folder ACLs are restored;
* the same-package control actually shares its object;
* a non-test name is refused.

Observed on Windows 11 (10.0.26300):

* Inside an AppContainer, `Global\` resolves to that package's own
  `AppContainerNamedObjects` directory, not to `\BaseNamedObjects`.
* The client's descriptor create fails with 1314, because a Low token cannot
  apply a Medium label. The default-descriptor fallback then succeeds.
* Two different packages each get a **separate** mutex. Neither sees the other's
  object, and no error 5 occurs. Two processes in the same package share one
  mutex.
* The host cannot open a container's object by the same name (error 2). A
  host-pre-created `Global\` mutex is invisible to both containers, so
  pre-creation in the host namespace cannot provide a shared lock.

All 26 CTest targets pass.

## 2026-10-16 - Launcher pair mode for two concurrent clients (no game in tests)

New launcher mode `--retail-private-pair` (public wrapper
`scripts/Start-PrivatePair.ps1`) prepares experiment E1: two original clients
at the main menu at the same time. Following the E0 result, both clients run
in **one shared AppContainer profile** (one package SID), so they share named
objects such as the storage writer lock, as two clients do on a normal
machine. One launcher process owns both clients:

* one ACL capture and grant, and one exact restore after both clients end;
* one network-isolation probe; no capabilities are granted;
* per client, an owned job, a container loopback bridge, TLS/CA/lobby-key
  observer threads and an optional bounded dump
  (`retail-private-pair-c0.dmp` / `-c1.dmp`, never overwritten);
* stdout lines are tagged `[c0]` / `[c1]`, and the PIDs are logged as
  `Offline client[cN] PID=`.

The guards are stricter than in single mode:

* `--run-for` is mandatory and lies in 1..300 seconds. It is one shared bound,
  measured from the first client's start.
* `--client-delay` (0..180 s) must leave at least 30 seconds for the second
  client.
* Container ports are fixed: client 0 uses 1119 and client 1 uses 1129. TCP
  host ports must differ, and no host port may be 1119 or 1129. Optional UDP
  forwards must be given for both clients or for neither, and each must use
  its client's container port. Both may share one host UDP port.
* Client arguments are fixed by the launcher:
  `--BNetServer=127.0.0.1:<that client's container port>`.
* The executable fingerprint is checked before anything else is created.
  The launcher then refuses to start while another launcher or Overwatch
  process exists.

`tools/bnet-probe.py` now accepts the own-key referral `127.0.0.1:1129` only
together with `--port 21129`. The own credential's address block then carries
port 1129. The `127.0.0.1:1119` behaviour is unchanged.

New CTest target `offline-launch-pair-guards` (`tests/offline_pair.ps1`) checks
the accepted shapes, which stop at the fingerprint guard, and each rejection.
It also checks that the ACLs are unchanged. `bnet-probe-framing` gains the
referral allow-list test. All 27 CTest targets pass. No game was launched for
this change, so it is not yet known whether the client honours a non-default
`--BNetServer` port. E1 will show it: client 1's bridge on port 1129 either
receives connections or it does not.
## 2026-10-17 - Launcher pair mode for two or three clients (no game in tests)

`--retail-private-pair` now accepts two or three clients in the one shared
AppContainer profile: container ports are fixed at 1119, 1129 and optionally
1139, and client n starts n x `--client-delay` seconds after client 0 (the last
client still needs 30 seconds of the shared bound). `--pair-dump` adds `all` and
`c2`. All TCP host ports must be pairwise distinct and never a container port;
UDP forwards are given for every client or none. `tools/bnet-probe.py` accepts
the own-key referral `127.0.0.1:1139` only with `--port 21139`, and the instance
referral allowlist adds 1139. `scripts/Start-PrivatePair.ps1` takes two or three
`-HostPorts`. `tests/offline_pair.ps1` covers the accepted three-client shapes and
rejects a fourth client, a wrong third port, a shared host port, a container host
port, missing UDP on the third client and a delay that leaves less than 30 seconds
for the third client; `tests/bnet_probe.py` covers the 1139/21139 referral pair.
Native build and all 27 CTest targets pass. Live: three original clients reached
one Practice session and each saw the other two players (private run 426).
