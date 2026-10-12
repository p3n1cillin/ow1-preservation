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
