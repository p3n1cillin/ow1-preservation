# Development log

## 2026-10-12 — Native TLS socket and connection-job observation

- Added bounded `-ObserveTls` / `--observe-tls` with original instruction,
  socket/wrapper/transport/callback, handle-map and shared-control guards.
  Retains one original connection-job reference until bounded process exit;
  reports original state/error without rewriting verdicts or readiness.
- Own-CA run captures socket 1->2, job 1/0->2/1016. No-CA/no-patch control
  captures socket 1->3, job 1/0->2/1016. Both complete real TLS 1.2 and close
  before an RPC header. Original callback tracing proves state 2 means result
  zero and state 3 means chain-result 2; CA import fixes that lower chain check.
- Traced the distinct 17,289-byte CA input and its original setter/secondary
  verifier. No setter or original pin verdict has been changed. Exact meaning
  and underlying cause of the higher-level 1016/0x3F8 failure remain unverified.
- Two debugger-attachment experiments ended C0000005 before capturing a verdict.
  Preserved experimental source locally and removed that option from the shipped
  code. Switched to guarded native-state sampling; no attachment-cause claim.
- A 30-second delayed server test closed before any server bytes; classified as
  a timeout baseline, not a certificate-validation result. Final comparisons
  use a 15-second delay. Private launches continue to skip the cutscene.
- Final native build and all 13 CTest targets pass. Saved client-folder and
  launcher-file ACLs match exactly after owned runs; original executable hash
  and Valid signature are unchanged. Diagnostic observers are stopped.

## 2026-10-12 — Cutscene skipping, native CA import and TLS 1.2

- Private launches automatically apply the existing guarded native ShowIntro
  dismissal. No user window input is required for these test runs.
- Traced exact original TLS object/context/SSL/store identities and APIs. Verify
  modes are already zero; transport +10 is the role. Added an opt-in bounded,
  exact-loopback public-CA import through original PEM/store/free functions.
  It retains the context, preserves original suspend counts and registers an
  author callback unwind table. Original verifier code, TLS role/mode fields,
  host trust and original client files are unchanged by this path.
- Initial guards stopped before CA import on an incorrect parser prefix and
  changing thread inventory. Corrected the exact instruction guard and bounded
  thread stabilization; already-suspended threads keep their original counts.
  Final native callbacks report parsed/inserted/unwind 1/1/1; measured completion
  at 2,891 ms precedes a 30-second-delayed server certificate.
- Added observer `--tls-max` / `--handshake-delay` and negotiated-version logs.
  TLS 1.2 completes with our own server, then the client closes before the first
  RPC header bytes. A no-CA/no-patch control repeats this result. CA import is
  therefore not credited as the cause of handshake completion. Default TLS
  negotiation's native failure remains unverified.
- Traced a mapped-loopback certificate-CN case; neither a matching own CN nor a
  bracketed mapped BNetServer produces RPC. Removed the experimental address
  allowance from the shipped CA guard. Post-handshake verdict/state tracing is
  the next frontier; no original authentication or gameplay is claimed.
- Rebuilt native targets and passed all 13 CTest targets, including restricted
  CA CLI safeguards and five synthetic observer framing cases. Local dumps,
  generated certificates/keys and client bytes remain outside Git.
- Completed owned runs restore the saved client-folder/launcher-file ACLs
  exactly. Original client hash is unchanged and its signature remains Valid.

## 2026-10-11 — User-supplied ISO inspection

- Inspected the supplied 5.18 GB ISO using read-only archive listing, then an experimental ISO9660/DD-v1 reader. No mounting, installer execution, game launch or patching.
- Verified the disc index hash against `disc.id`; scanned all 64,883 archive record headers. Skipped 64,826 encrypted first chunks; decoded supported metadata and executable records only. Parsed the 14-entry install manifest.
- Recovered signed x64 `Overwatch.exe` to an external local cache. Size/content MD5 match the install manifest. SHA256 `8d33644f844b81e830c12749371c80a83d26f81b186265897ca5d67f6e7e665d`; numeric PE version is `1.0.1.27578` despite empty version strings. Confirmed numeric version with pefile and .NET independently.
- Extended executable inspection to include numeric fixed version; added bounded BLTE/install parsing and synthetic regression checks. This client is an additional static-analysis candidate, not compatible with the existing beta hooks and not the final retail target. Full offline installation, encrypted assets and runtime behavior remain unverified.
- Rebuilt the standalone targets and reran CTest: 4/4 passed, including the new disc-inspection checks and existing socket/PE tests. No proprietary payload was staged in Git.

## 2026-10-10 — Preservation foundation

- Inspected the empty Windows/network-share workspace and the complete project directive. No repository-specific agent instructions were found. Cloned Prometheus recursively at `ad1fea7e6c04c9959c7115cb8ecd9c79c93c1ccb`; created branch `preservation-foundation`.
- Inspected Prometheus game initialization, STU/entity/movement/serialization, debug tools, network callbacks and fixed-offset patcher. Evaluated mandatory Login-Server and OW1-Emulator sources plus OWLib, Plasmawatch lobby/launcher, issues/PRs and sampled forks. Rejected unsupported assumptions of runtime/version compatibility.
- Established a local build cache because Windows denied executing tools from the mapped share. Used the pinned vcpkg checkout `11bbc873e00e9e58d4e9dffb30b7a5493a030e0b` and manifest baseline `c5ff0f76a2212d49e92f02b510cc7509e7e119ef`. Initial vcpkg bootstrap/download attempts on the share were unsuccessful; the local executable/dependency installation succeeded.
- Built the upstream Release/x64 DLL and .NET 8 patcher. Recorded existing warnings and kept launch/map/hero behavior unverified because no client files were present.
- Implemented a reusable validated BSON demo protocol, pure relay core and standalone listener. Added connection-owned IDs, state ordering, latest-hero cache, late-join snapshots, disconnect cleanup, room/input/rate/queue limits and JSON diagnostics. This is a movement relay, not match authority.
- Added regression tests and a dedicated-process integration harness with two-way movement values, reconnect, 12 real sockets and rejected malformed/excess participants. Fixed a test readiness callback and Windows bcrypt link dependency discovered by compilation/testing.
- Started the client WebSocket worker; synchronized identity/hero/connection state; added bounded receive queue and disconnect controls; shared the embedded relay core; fixed stale entity removal, controller hero ID and missing log argument; guarded absent resources/components. Skip uninitialized movement and movement before a selected hero. Client changes compiled successfully but were not exercised in-game.
- Added read-only PE/version/hash/signature inspection and synthetic malformed-file checks. No original client was patched, loaded or executed.
- At the user's request, cloned BlizzGet in an external research folder, inspected its NGDP implementation and compiled a headless probe. Found archived final build metadata `1.74.0.0.104319` / config `786a31729ba1c684a5c80fbaf7cb92b8`. Final config lookup returned 403; tested alternatives returned 404. Current and older PTR control configs returned 200. No game data or substitute build was downloaded.
- Added a reproducible probe build using external BlizzGet source; compiled/reran the committed probe and reproduced the 403. External source redistribution permissions are not established, so no linked binary/source was vendored.
- Added `Build.ps1`, CI build/test configuration and required research/status/architecture/license documents. Resolved a Windows network ownership issue by reading a detached vcpkg worktree's revision without changing Git's global trust settings. Full build workflow passed locally; CTest 3/3 passed. CI configuration has not run remotely.
- Remaining blocker: compatible authorized game files and verified byte/profile checks. Next acceptance target: original beta launch, one hero/map and visible two-client movement; retail adaptation and synchronized combat/objectives remain future work.

## 2026-10-11 — User request: get the supplied disc running

- Recovered and hash-checked all 14 install files to local cache. Rebuilt five encoded CASC segments/16 indices with all 64,883 disc records and verified their EKeys. Generated clearly labeled inferred configuration; encrypted payloads remain unchanged.
- Built external CascLib `38a34665624b8775bb875274b36191b21c38d97b` and verified ROOT, executable and English application/speech manifests by original content MD5. The native game still cannot initialize its resources; this reader check does not establish playable content.
- Built a bounded offline diagnostic launcher. Real zero-capability AppContainer probe denies TCP with WSAEACCES; DACLs restored/profile removed afterward. Added exact SHA256/instruction guards for an opt-in in-memory WMI fallback. Original executable remains unchanged and signed.
- Isolated unmodified startup crashes at RVA 0x415EBB after WMI services are denied. Workaround reaches an original Overwatch Mgr 13 resource-error dialog. Full local memory diagnostics identified missing `cache/casc/shmem.lock`; creating the cache fixes that particular error, but not resource-manager initialization. No original menus/maps/heroes/gameplay verified. Beta DLL was not injected.
- Root CMake now includes launcher and safeguards tests. CTest 6/6 passed, including published Jenkins answers/index framing, real network isolation, DACL restoration and unknown-build refusal. See DISC_RUNTIME.md for reproduction and limitations.

## 2026-10-11 — Native disc title-screen startup

- Captured native diagnostics identified required build-table columns and missing archive-envelope integrity fields. Corrected metadata, index byte order/allocation and seeded Jenkins/offset checksums; encrypted BLTE payloads remain unchanged.
- Both the repaired installation and a fresh ISO reconstruction rendered the original animated title/login screen with network denied. CascLib named-file verification passed after native startup; fresh captured diagnostics contain the expected no-server downloader failure. Login, maps, controllable heroes and private gameplay remain unverified.
- Added bounded dump inspection, format/bounds regression tests and `--run-offline`, which keeps the original window open until user exit with the same AppContainer isolation and scoped cleanup. The executable on disk retains its verified SHA256.
- MSVC Release build and seven CTest targets pass; proprietary assets, dumps and logs stay outside Git.

## 2026-10-11 — Disc package graphs and native world-loaded milestone

- Added a read-only old APM/package inspector and synthetic bounds/gzip/hash tests. Base Hanamura (5 packages / 8,257 entries), Practice (6 / 11,270), global 29 (1,270 / 178,957) and Hanamura localized (8 packages) checks passed. Global localized checks found 10,293 unavailable entries; this client is not complete. Entries include duplicates.
- Traced global pack readiness, optional speech rows, native loader work and resource dependencies. Confirmed absent global-29 English bundle and loose voice catalogue encoded records against the ISO index and encoding manifest. CDN probes returned no copy; no invented asset was written.
- Added fingerprinted bounded disc probes: omit optional speech, preload common/map packages on the native game thread, explicitly request the missing voice catalogue through the native API. Native failure completes the unresolved dependency and permits world state 5 / the correct Hanamura GUID. Restoring the original map callback after submission is now automatic.
- Visually observed Hanamura geometry behind the original loading overlay. The restored-callback probe survived five minutes at state 5 without a new crash report; no controllable hero, collision, combat, authenticated session or actual multiplayer was verified. One earlier run with a retained callback crashed at a call to zero; causation remains unresolved.
- Added a separate native world-stage callback experiment based on upstream beta behavior. The disc raises assertion 3980(92)/3981/"2" before a playable transition. This diagnostic is not a successful game/session implementation; its post-startup deadline is one minute. No assertion or loader-ready flag was bypassed.
- Rechecked the user-supplied NGDP archive and OWLib/TACTLib source. The exact final, 1.23 and disc config hashes returned 403/404 on tested paths, including ConfigPath; the source-built BlizzGet prerequisite probe again returned 403 for final OW1. No new client acquired. Current TACTLib's old-version rejection prevents direct use for this disc.
- MSVC source build and eight CTest targets pass. Game files, local crash reports, screenshots returned by the UI tool, dumps and logs remain outside Git. The next native work is to identify required callback/session/controller initialization before advancing out of world-loaded state.
- Subsequent exception-context inspection identifies the stage assertion's requested resource as Hanamura STU `0x04000000000001fa`; its native object is unavailable after the missing voice-catalogue dependency fails. Next work is optional voice-reference handling that preserves the map definition, or obtaining the original missing catalogue, before session/controller activation. Other locale manifests/package metadata did not yield an available alternative through the reconstructed storage.

## 2026-10-12 — Missing catalogue audit and author-written schema prototype

- Added a repeatable read-only audit of original EN/ISO/package data. Verified all 1,787 EN content-key pages / 191,194 mappings and the 64,883-entry original disc index. The 46,208-byte catalogue has one declared EKey, absent from the index.
- Searched 5,034 English base/speech package rows, parsing 3,988 hash-verified metadata files; 47 metadata files remained unreadable. Only the missing loose record matched. No exact available duplicate was found; unreadable/external copies remain unknown.
- Eighteen HTTPS CDN asset attempts returned no copy; certificate validation was retained. No matching hash-named file was found among 190 checked local cache files. These checks do not establish universal unavailability.
- Derived the disc immutable-STU v3 VoiceSet schema from owned readable resources and authored a 96-byte empty candidate with no original mappings/audio. Unregistered-callback parsing/creation attempts crashed; exact failure sites were not captured. Added guarded Windows unwind registration; the subsequent native parser constructed the expected root and empty list successfully.
- Added the separate `--catalogue-schema-probe`: verifies schema/instructions/object identity and original missing descriptor, then stops the isolated job. The candidate is not installed, no loader flags are fabricated and native map/gameplay integration remains unresolved. A successful schema probe is not a successful resource replacement or game session.
- Source build and nine CTest targets pass, including new EN corruption/bounds checks and unknown-build rejection for the schema probe. Game files/payload samples/dumps/logs remain outside Git.

## 2026-10-12 — Native silent catalogue import

- Traced native memory import, work attachment/cancellation, STU ownership/destruction and descriptor completion. Added guarded `--catalogue-import-probe` with a client-allocated aligned 96-byte author-written buffer, native request/descriptor guards and callback unwind metadata. Completion/failure flags remain native.
- Repeatedly observed a published catalogue object under the original GUID with flags `0xb1301`, size 96 and expected root vtable; the completed captured descriptor has no loader work. The helper verifies that the object is the exact newly allocated buffer's root. Original voice definitions/audio remain absent.
- Initial one-minute runs, including an active-window check using computer-use, remain at world state 4 / loaded-map zero. Common package 79 has 1,070 queued work entries among 1,115 handles in one capture; target map/global STU descriptor GUIDs were not found in its bounded heap scan. No playable map/hero or stage advancement is claimed.
- Independently read the queued common bundle CKey `6320cb843838297c27d1674a8d70420b` through offline CascLib: all 2,688,272 bytes match its MD5. Its native loading delay is not proof of missing data. Extended import-mode observation to the normal five-minute map window.
- MSVC source build and nine CTest targets pass, including unknown-build rejection for the new mode. Diagnostic payloads/dumps/logs remain outside Git.
- The extended five-minute native import run also stayed at state 4 / loaded-map zero. Its diagnostic deadline is a map-load failure, not a successful session. Original executable SHA256/signature and scoped ACL restoration were checked after ending the owned job. Next native work is the pending common-package task/reader queue; do not advance stages while map-definition availability remains unverified.

## 2026-10-12 — Supplied final retail client

- Inspected the supplied 104319 archive paths, recorded SHA256, and fully extracted all 672 files / 20 directories outside Git with 7-Zip integrity success. Verified signed x64 EXE, exact archived BuildConfig MD5/build-name, and CASC-versus-disk executable identity.
- Added parent `_retail_` storage/metadata inspection and a guarded final startup fingerprint. Two unmodified network-isolated launches survived 60 seconds; scoped cleanup completed. Both native captures log offline DNS errors and the same `.build.info` path-normalization warning, even with root working directory. Final visual inspection failed twice with Windows access denial; no final title screen or gameplay is claimed.
- Added .NET 8 metadata-only probe using the pinned external MIT TACTLib 104319 provider; no provider source/assets vendored. Original base and English text/speech CMFs hash-verified and decoded to 471,024 / 44,691 / 24,017 logical records. Bounds, wrong-build/hash, existing-output and decoded-entry rejection tests pass.
- Added reproducible offline retail storage inspection. Enumerated 461,032 local CKeys; direct-match absence is explicitly not a missing-file claim because resources are bundled. Verified 41 bundles and 130 map-header payloads. One sampled encrypted bundle's key was unavailable; full asset completeness remains unknown.
- Added an interactive unmodified retail launch mode/script and synthetic bundle-table bounds tests. MSVC build and 10 CTest targets pass. Updated acquisition, compatibility, feature, roadmap, license and testing records. Final resource/service/session/controller adaptation is the current priority; single-player and actual multiplayer remain unverified.
- Saved the preceding disc experiment: explicit native global/map-definition requests returned failure flags `0x3b301` / null objects despite the published silent catalogue. The disc job was ended when the user paused for their final download. This does not establish an available or recreated map definition.

- Started the interactive unmodified final client with the source-built helper: owned launcher PID 2768 / client PID 13096. Network denial verified before launch; the helper remains alive until client exit. UI outcome still requires observation because automation is denied access.

## 2026-10-12 — User-confirmed final UI and map references

- The user reports "Title or login screen" in response to the interactive startup question. Recorded this as user-observed evidence; automation still cannot inspect the window. Original final executable remains running under the owned offline helper. Login and gameplay remain unverified.
- Inspected external OWLib's STU V2 field-bag/string/resource-reference readers and TACTLib's bundle lookup. Added a bounded metadata-only STU reader and final map-header inspector, with no native offsets or exported payloads. Parsed all 130 audited headers; all names and map references resolve in the base manifest.
- Independently hash-verified Hanamura PvP and Practice Range map-root payloads (912 bytes each) inside separate bundles. These map roots are not STU V2 and remain unparsed; no map definition, world/entity initialization or full dependency completeness is claimed. Six other sampled bundles lacked keys; both selected roots were resolved.
- Added synthetic malformed STU table/instance/field/string tests plus an independently evaluated CRC64 vector. Corrected the hand-written byte-swap test expectation after its first run failed; the original parser decoded all real references correctly. All 11 CTest targets then passed. Proprietary data/metadata reports remain outside Git.
- Next priority: locate final native world/resource and session/controller entry points with verified instruction/profile evidence before requesting a map. The beta and disc profiles remain separate; there is still no final playable hero or actual multiplayer.


## 2026-10-12 - Native retail request and repeatable diagnostics

- Added a read-only dump inspector for the fingerprinted final world, its decoded owner, native state table and request descriptor. A descriptor pointer is distinguished from a resource GUID. Added malformed profile/object/owner/descriptor and author-written diagnostic metadata checks.
- Directly observed the original 104319 title/login screen through computer-use. Later input returned Windows access denial despite the unlocked desktop. Added guarded process-local ShowIntro handling to make map diagnostics independent of intro keys; original files remain unchanged.
- APC/worker/callback-table experiments did not publish a request. The primary-thread delay-return transport now registers unwind metadata, executes the native map API and restores the captured context. The native allocator publishes its own Practice descriptor with index 0x688; original world dispatch remains intact.
- Added non-reentrant original-stack loading experiments. The final captured loading run returned 218 native handlers and reports the Practice header available in the native resource index. A separate full-world-update run returned 221 calls without a new crash. Both remain at idle state 2; no map, hero or private session is verified.
- Recorded earlier scratch-stack single-step termination and a separate debugger startup access violation without treating either as a successful session or assigning an unproven internal cause.
- Added repeatable PracticeRequest/PracticeLoad launch-script modes. Full CMake Release build and 12/12 CTest targets pass. Original executable SHA256 is unchanged and its Authenticode signature remains valid. All owned diagnostic jobs ended; game files, dumps and generated metadata stay outside Git.
- Next native work is request/session/entity-admin initialization required by the idle handler, followed by actual map loading and controller/session integration. Native header recognition is verified; missing header data is not an evidenced explanation for the idle state.

- The user has removed the old 1.0 ISO. Active development remains exclusively on supplied final retail 104319; old tools/notes are historical and synthetic disc tests do not require the ISO.

## 2026-10-12 - Public source and native header loading

- Created the public AGPL-3.0 repository at https://github.com/p3n1cillin/ow1-preservation. Retained public upstream history and published a source snapshot using the GitHub noreply identity. Existing local development history remains on preservation-foundation; game files, dumps and private external research were excluded.
- The first remote CI run exposed legacy ACL control changes. Reproduced them in an owned temporary fixture, captured file ACLs before parent grants, restored parents before children, and preserved the exact original control flags. Added protected/inherited legacy fixtures. The subsequent public Windows CI completed dependency installation, DLL/patcher/relay builds and all 12 tests.
- Distinguished native header existence from load state. A query-only run returned 214 handlers at world state 2 with raw header load state 0. A once-only native resource request returns a client-owned entry, changes raw header state to 3 and advances native world state 2 to 3.
- The first resource/loading-handler run returned 216 calls and survived two minutes at state 3. The full original-world-update version returned 214 calls and survived two minutes, with loading state 3 and observed retries through state 2. Loading completion, rendering, hero control and private sessions remain unverified.
- Added the bounded PracticeResources mode and guarded raw resource-state/request-entry diagnostics, including explicit unqueried results. The full local CTest suite passes 12/12. A captured game window was black; activation still returned Access denied despite the unlocked desktop. No new input or authentication was attempted.
- All owned test jobs ended. Next work is native loading/session prerequisites beyond the loaded Practice header. The original executable remains unchanged.
- The later full-update dump captures 215 returned calls versus 214 in the final log snapshot, with the callback inactive. Added guarded read-only reporting of the native loading gate counter (captured 0) and opaque request-context presence (absent). The context's native format and session relationship remain unresolved; its bytes are never reported. Corrected the inspector's known-state bound to include native terminal unload state 10, guarded by its original instruction, and retained unknown-state rejection.

## 2026-10-12 - Native state-4 tracing and context activation

- Immediate before/after measurements catch native 3-to-4 transitions missed by half-second host sampling. The single-update dump captures 222 returned updates, highest returned state 4. The title-loop observation subsequently returns to state 3; its intervening behavior remains unresolved.
- Added a maximum of two native updates per callback, with the second conditional on returned state 4. Without context activation the state-4 update clears/rejects the map request. The diagnostic now stops extra updates on native request removal and checks the 2-to-4 state bound inside the callback.
- The all-zero descriptor identifier matches the resident native default. Followed the original type-2 context constructor/reference transfer/activation sequence without altering a ready flag or supplying resource/metadata payloads. Activation succeeds; the request survives two minutes and the dump captures 433 returned updates, including 216 from state 4.
- Added bounded read-only native context/service verification: vtables, type, retained reference, decoded component owner and unique 256-slot search. The service owns the current context and has two notification subscribers, but its metadata cache is empty and native readiness remains zero. Notification dispatch, rather than an assumed background worker, is the verified API behavior.
- Added PracticeContext and malformed observation/context/service tests. Renamed the descriptor predicate to request_loading_context_nonzero because zero is a native default, not proof of an absent context. Full local CTest suite passes 12/12. Gameplay and private sessions remain unimplemented; next work is native metadata registration/processing and its service/session schema.

## 2026-10-12 - Original metadata handlers and SDK completion

- Added PracticeMetadata: verified context-service discovery followed by the original metadata initialization/processing handlers. The captured run returns 432 calls to each handler and 433 world updates, but does not populate the cache or finish map loading.
- Retained an independent native kind-13 metadata request through the original aligned allocation/control-block/constructor/submission sequence. The internal client kind is not a network opcode. Original submission consumes a second reference; the retained reference preserves the result for read-only inspection. No reply, payload or completion flag is supplied by this project.
- Native async submission is accepted with gate value 1. The request completes with result flag 0, queue-reset marker 0 and a null response-data pointer. The context remains unready, its cache is empty and the service's native initialization terminal flag is 1. Next work is the actual metadata provider/session path; submission/completion is not private-backend or gameplay success.
- Added native SDK identity/reference/flag/empty-data/error-result checks. Corrected the async gate RVA during local research before publication by evaluating the original RIP-relative operand. Full CTest suite passes 12/12 and the world-profile target now exercises nine synthetic cases. The game archive/executable remain unchanged and all owned test jobs ended.

## 2026-10-12 — Retail login architecture reverse-engineered (static, from title-screen dump)

Analyzed the unpacked in-memory image recovered from `_retail_/startup-wait.dmp`
(the on-disk EXE is packed; the dump holds the decrypted image at base
`0x7ff794400000`). Read-only static analysis with capstone/pefile; no client
bytes were modified and nothing proprietary was committed.

**Two independent TLS stacks:**
- **bgs RPC** (the `*.actual.battle.net:1119` login connection the client makes
  FIRST): statically-linked **OpenSSL** (`3rdparty\cross_ssl\src\openssl\openssl_impl.cpp`,
  "OpenSSL Solution Initialized", `SSL_CTX_new`, `ssl_ctx_make_profiles`). Trust is
  driven by a **ServerInfo** structure, not a user CA store.
- **web-auth HTTPS**: **libcurl 7.52.1 + schannel** (Windows cert store). This leg
  CAN be satisfied by trusting our own CA in the Windows user Root store (the
  Plasmawatch README's documented step); it needs no patch.

**ServerInfo / cert pinning (the bgs blocker).** The title-screen heap held the
signed bundle `{"Created":1612222344,"Certificates":[25],"PublicKeys":[25],
"SigningCertificates":[10],"RootCAPublicKeys":[10]}` followed by a 256-byte
RSA-2048 signature. Pinned URIs: `us/eu/kr/cn.actual.battle.net`, `*.bgs.battle.net`,
`*.dev.battle.net`, `*.integration.blizzard.com`, test/loc variants. `PublicKeys`
entries carry `ShaHashPublicKeyInfo` (SHA-256 of the server SPKI). The bundle
loader (image `0x7ff79656aa24`) deserializes keys `PublicKeys` /
`ShaHashPublicKeyInfo` / `SigningCertificates` / `RootCAPublicKeys`; the signature
is checked against a trust anchor not present in the file, so the bundle is not
forgeable and we will not attempt to forge it.

**bgs TLS profile config keys** (parsed into a hash-map dispatch at `0x796292c43`):
`Options, VerifyMode, Certificate, PrivateKey, ServerInfoFile, ChainCA{Path,File},
VerifyCA{Path,File}, RequestCAFile, ClientCA{File,Path}, DHParameters, …`. These
describe how a profile is built but, for the client→server leg, trust resolves
through the signed ServerInfo rather than a locally settable CA file.

**Empirical gate.** Prior session presented a valid CA-signed cert with
`IP:127.0.0.1` SAN on the host loopback; the client sent its ClientHello
(293 bytes, TLS 1.3, no SNI) and closed after receiving ServerHello+cert — i.e.
it rejected our cert at the bgs leg. This is consistent with ServerInfo-pinned
trust that our CA cannot satisfy.

**Conclusion / plan.** A no-patch path exists only for the web-auth leg (trust our
CA). The bgs leg requires a minimal in-memory patch of the client's own TLS
verification result (same WriteProcessMemory technique the launcher and
`retail_world_probe.h` already use; the Plasmawatch OverLauncher does the
equivalent for the beta client). Remaining ladder after trust is established:
reimplement a private bnet login RPC (TLS + length-prefixed protobuf header:
service hash / method id / token) to answer Logon → web_auth_url → token →
reach the main menu; maps/heroes/matchmaking/6v6 remain long-horizon research.
Tooling note: capstone/pefile/numpy were installed only into the session
scratchpad, not the repo.

### bgs TLS verify patch point located (candidate)

Static RE of the decrypted image mapped the `cross_ssl` post-handshake
verification. Three independent gates exist: X509 chain/CA verify
(`ssl_cert_chain_bundle_verification_failed`), public-key pinning
(`ssl_public_key_pinning_check_failed` reporter at image `0x7ff79657b9e0`),
and CN/SAN hostname match (predicate `0x7ff796770c80`, consumed by the
hostname verifier that logs `common_name=` / "Could not validate common name").

The post-handshake **verdict aggregator** is `0x7ff79676f140` (RVA `0x236f140`):
it returns `ebx`, where **0 = accept**, 2 or 1 = reject (set on sub-check
failure). It is invoked immediately after the "Finished SSL Handshake" log in
the handshake state machine, and its result propagates to the connection code.

**Primary candidate patch** (RUNTIME / in-memory only; the on-disk exe is
packed, so apply after decryption via WriteProcessMemory as the launcher
already does):
- RVA `0x236f1e6`, bytes `8B C3` (`mov eax, ebx`) → `31 C0` (`xor eax, eax`):
  forces the aggregator to return 0 (accept) regardless of sub-check results.

Fallbacks if the aggregator is not the sole gate (pin/chain run inside the
OpenSSL verify callback during the handshake): neutralize each predicate —
hostname `0x7ff796770c80`, pin path `0x7ff79657b9e0`, chain-verify (xref
`0x7ff79657c359`). All RVAs are relative to image base `0x7ff794400000`.

NOT YET TESTED against a live handshake. Patching our own client's cert
verification to trust our own loopback server is the established private-server
technique (cf. Plasmawatch OverLauncher for the beta); we are not forging
Blizzard's ServerInfo signature. Next: apply the patch in the launcher, present
our cert on the bridged bgs port, run the client, and confirm the handshake
completes and a bgs RPC arrives.

### Empirical bgs TLS test — in-handshake rejection, external patch insufficient

Built an end-to-end test harness: `--retail-private` now runs a background
in-memory patch thread (`retail_tls_patch.h`, opt-out `OW1_SKIP_TLS_PATCH`),
`tools/bnet-probe.py` is an observing OpenSSL TLS server (our own 127.0.0.1
cert) that logs the client's first bgs RPC frame, and `Start-PrivateClient.ps1`
bridges container 1119 -> host 21119. Full build + 12/12 CTest pass; the
launcher restores folder ACLs on client exit (verified clean).

Two client runs (patched launcher). Each time the client, as the TLS *client*,
sent only its ClientHello (293 B), received our ServerHello+Certificate
(~1303 B), then closed before its own Finished — the probe logs
`UNEXPECTED_EOF_WHILE_READING`. So the certificate is rejected **inside** the
handshake by the client's OpenSSL cert-verify callbacks (chain + public-key
pinning), not by the post-handshake hostname/verdict path.

First patch attempt targeted the post-handshake verdict aggregator
(`0x236f1e6`); the launcher reported it "did not decrypt within timeout" —
correct, because that code only runs after a completed handshake. Retargeted to
the two in-handshake verify-callback returns (chain `0x217c3a9`, pin
`0x217bb53`, both `mov eax,ebx` 8B C3 -> `xor eax,eax` 31 C0). Second run: BOTH
required sites also "did not decrypt within timeout", although the handshake ran
twice. The bytes at those `.text` RVAs in the *live* process do not match the
title-screen dump.

**Conclusion:** the retail client protects/decrypts code on demand, so these
verify functions are not stably decrypted in-place at their dump RVAs; external
`WriteProcessMemory` polling cannot reliably patch them (the earlier WMI-site
patch at `0x415eae` worked only because that site is stably decrypted). The
right mechanism is an **in-process hook via an injected DLL** — fitting, since
this repo is a Prometheus (injected-DLL) fork. From inside the process the
verify code is decrypted and executing, so a hook on the OpenSSL verify
callback / `X509_verify_cert` result, or forcing `SSL_VERIFY_NONE` at SSL_CTX
setup, is reachable. The static RVAs and verify-function map above remain valid
inputs for that DLL. Deferred pending direction: injected-DLL hook is a larger,
dual-use-sensitive step and gates everything after it (login service, menu,
maps, 6v6).

### Hard wall: client blocks external code patching (Arbitrary Code Guard)

Instrumented the patch thread and ran repeatedly. New facts:
- The verify code DOES decrypt and become resident in place at its `.text`
  RVAs (lazily, after the client initializes further — generally after its
  first early bgs attempts). The diagnostic confirms the live bytes at
  `0x217bb53` (pin-verify) and `0x236f1e6` (post-handshake-verdict) exactly
  match the expected instruction signatures, on committed `PAGE_EXECUTE_READ`
  pages, uniquely at the site (the chain-verify idiom `8b c3 eb 02 33 c0` also
  appears as many unrelated copies, so it is not a reliable scan signature).
- So decryption was never the blocker. The blocker is the WRITE:
  `VirtualProtectEx(..., PAGE_EXECUTE_READWRITE, ...)` fails with
  **Win32 error 87 (ERROR_INVALID_PARAMETER)** on those resident pages. On a
  committed execute-read page with a full-access process handle, that is the
  behavior of **Arbitrary Code Guard** (ProcessDynamicCodePolicy /
  ProhibitDynamicCode) or an equivalent anti-tamper mitigation: the kernel
  refuses to make existing executable pages writable. External in-memory code
  patching of the final client is therefore blocked by design.

Implications for the bgs login patch:
- A simple external WriteProcessMemory patch (what works for the beta client,
  and for the one retail WMI site in earlier notes) cannot neutralize the
  retail client's TLS verify.
- Execution-triggered patching avoids changing page protection:
  (a) hardware breakpoints (Dr0-3 via SetThreadContext) at the verify-return
      site, caught by a debugger loop in the launcher, adjusting RAX to the
      success value — but the signed client may have anti-debug (a prior
      "debugger startup access violation" was noted);
  (b) an injected DLL using HWBP + a vectored exception handler across all
      client threads (DLL image load is permitted under ACG; dynamic code is
      not) — larger, and still an anti-tamper-sensitive effort.
- The harness, address map and diagnostics remain valid inputs for either.

`retail_tls_patch.h` now polls for the whole session and logs the exact failure
reason; it is retained as documented infrastructure even though the write is
currently blocked. No disk bytes were ever modified; the launcher restored
folder ACLs cleanly after every run.

## 2026-10-12 — Branch consolidation onto main

Consolidated all active work onto `main`. Fast-forwarded `main`
`ad1fea7 -> 0bcc551` (the `claude/continuation` tip: full private-bgs TLS
harness + ACG diagnosis). `codex/public-preservation` was a strict ancestor of
that line, so it is fully included. `preservation-foundation` was **not**
merged: it is a 3.5 h-older parallel line with zero files absent from the
consolidated tree, and merging it would only re-delete the TLS harness; left in
place as a reference branch. Auto-stash (`stash@{0}`, a CLAUDE.md deletion from
a branch switch) left untouched. `git diff main claude/continuation` is empty —
no work lost.

The ACG diagnosis in the preceding entries was provisional and is superseded
by the measured policy result below. The private TLS handshake remains blocked.

## 2026-10-12 — Codex resumes Claude's continuation

- Inspected the consolidated `main` and preserved Claude's loopback bridge,
  TLS observer and VS 2026 support. The original local captures/build tree are
  present; corrected stale CLAUDE.md statements about absent evidence/branches.
- Traced native worker result copying, the kind-13 virtual operation and its
  consumer. Corrected a prior Codex decoder error: flag 1 is success, flag 0
  structured error. Real captured status/tag/code are 3/2/-1 at +18/+19/+20;
  +138/+140 hold success data/count, not an error code. The operation enumerates
  the local Hotfix directory through a filesystem provider. Its success loop
  marks existing cache entries, rather than registering new records. This does
  not demonstrate any backend reply or authentication prerequisite.
- Added native instruction/vtable guards and malformed flag/result coverage;
  re-read the existing native dump with the corrected decoder. Context readiness
  remains zero and cache count zero. No native response or ready flag fabricated.
- Added `--run-for` / `-RunForSeconds` private diagnostics and stop-aware TLS
  worker teardown before process-handle closure. Duration rejection and final
  executable fingerprint checks run in the isolation regression target.
  Host bridge listeners now cancel pending pipe connections and join before
  their owner is destroyed; the self-test exercises idle-listener teardown.
- Queried dynamic-code policy at startup and again after write failures: flags
  0 on both queries. ACG is therefore not established by Win32 87. TLS candidate
  pages are committed execute-read MEM_MAPPED pages with execute-read allocation
  protection. Exact full-page searches in the dump find no alternate copies;
  short repeated signatures are no proof of relocated verify functions.
- A new 90-second native run reaches our own loopback TLS observer twice.
  Each direction records 293 client bytes / 1,295 server bytes; the peer closes
  before handshake completion. No RPC or private login succeeded. The run ends
  all owned game/bridge jobs and restores exact folder/file ACLs. Original exe
  remains unchanged; no trust store or production credentials were used.
- Hardened the observing server's fragmented/truncated input handling, protobuf
  bounds, maximum body length and handshake timeout. Removed raw body/string
  contents from logs; new framing tests verify omission and malformed input.
  Generic header fields are not presented as verified final-retail dispatch.
- Reproduced a Build.ps1 generator regression when VS 2026 was chosen for the
  existing VS 2022 cache. Build.ps1 now reuses the cached generator and selects
  its matching installed toolchain. Full local build then passes, including
  relay, launcher, beta DLL, patcher and all 13 CTest targets.
- Updated persistent status, roadmap and handoff records. Private TLS acceptance
  and native Hotfix/cache initialization remain unresolved; final map/hero/login
  and original authoritative multiplayer are not verified.

## 2026-10-12 — original socket CA setter (`-TrustSocketCa`)

- Added opt-in `--trust-socket-ca` (requires `--trust-ca` and `--observe-tls`).
  A guarded primary-thread callback calls the original socket setter vft +70 /
  RVA 216cd30 with one 40-byte native string record, then reads the original
  peer-name getter 21e2fa0. No verifier code, verdict or client file is changed.
- Clean run (single listener; an earlier run was contaminated by a stale probe
  on 21119 serving a different CA's certificate and showed socket 1->3):
  setter guard/result 1/1, CA input 17,289 -> 650 bytes and byte-equal to our
  public CA. Socket 1->2 (chain success), TLS 1.2 established, job ends 2/1016,
  peer closes before the 2-byte RPC header length. No RPC was captured.
- The original expected peer name is `::ffff:127.0.0.1`. Our certificate has
  CN `ow1-preservation.test` and SAN IP 127.0.0.1/localhost. A hostname/pin
  mismatch after chain success is a **hypothesis only**; 1016 is still undecoded.

## 2026-10-12 — mapped-loopback certificate: first real RPC captured

- Server certificate (ours, signed by our local CA, outside Git) with
  CN `::ffff:127.0.0.1` and SAN IP `::ffff:127.0.0.1`, IP 127.0.0.1,
  DNS `::ffff:127.0.0.1`, DNS localhost. Run: `-TrustCaCertificate <ca> -ObserveTls
  -TrustSocketCa`, probe `--tls-max 1.2`, single listener on 21119.
- Native socket 1->2. The client then sends an HTTP WebSocket upgrade:
  `GET / HTTP/1.1`, `Sec-WebSocket-Protocol: v1.rpc.battle.net`. The client sends
  no raw bgs frame first; the earlier "N bytes missing" errors were the probe
  reading `GE` as a header length.
- `tools/bnet-probe.py` now accepts the upgrade (logs request line, header names
  and the protocol value only) and decodes the first WebSocket binary message:
  bgs header 11 B: service_id 0, method_id 1, token 0, service hash
  1698982289 (0x65446991), 72-byte message (body omitted). That hash matches the
  public bgs `ConnectionService`, method 1 = `Connect`. The decoding is from the
  observed bytes; no response was sent, so the client tears down (job 3).
- Not yet run: certificate-variant isolation (which SAN/CN entry is required)
  and the `-TrustSocketCa`-off control. No login, session or gameplay is verified.
- Control (same mapped-loopback certificate, `-TrustCaCertificate -ObserveTls`,
  **without** `-TrustSocketCa`): socket 1->2, job 2/1016, client closes before
  any bytes; no WebSocket upgrade or RPC. Both the mapped peer-name certificate
  and the original socket CA input are therefore required for the first RPC.

## 2026-10-12 — RPC sequence to the login step (`--serve`)

- `tools/bnet-probe.py --serve` answers ConnectionService.Connect (response =
  Header{service_id=0xFE, token=echo} + minimal ConnectResponse) and keeps
  observing. The client accepts a token-matched response (even a 14 B one) and
  advances. ConnectRequest body carries no credentials.
- Next RPC is **AuthenticationServer.Logon** (hash 0x0DECFC01, method 1). The
  LogonRequest structure (string/bytes VALUES redacted, never logged):
  f1 str(3)=program, f2 str(3)=platform, f3 str(4)=locale, f5 str(3)=version,
  f6 varint=build 346134399, f10 varint=1 (flag), **f15 str(0)=empty**.
- The empty credential field indicates the **web-auth flow**: Logon expects the
  server to drive a browser login (our launcher/web page), not SRP-in-RPC. This
  matches the two-TLS-stack model in [[retail-login-architecture]] (web leg =
  libcurl+schannel, satisfiable via our CA in the Windows root store).
- Confirmed login entry sequence: TLS (mapped cert + socket CA) -> WebSocket
  v1.rpc.battle.net -> Connect -> Logon(web-auth). No login completed yet; the
  Logon responder and the web-auth endpoint are the next implementation step.

## 2026-10-12 — full bgs login schema extracted; login grant attempted

- The client embeds its protobuf descriptors. Extracted the authoritative schema
  to docs/BGS_PROTOCOL.md: ConnectionService/AuthenticationService/Authentication
  Listener method ids, and ConnectRequest/LogonRequest/LogonResult/EntityId fields.
- Service hash = FNV-1a 32 of the legacy bnet.protocol.* name (verified:
  AuthenticationServer -> 0x0DECFC01 matches the wire). Listener =
  AuthenticationClient -> 0x71240E35. Method ids from (method_options).id:
  Logon=1 (byte 08 01, matches wire), OnLogonComplete=5 (byte 08 05).
- ConnectRequest.use_bindless_rpc=true (the observed f3=1): services are addressed
  purely by hash, no id binding. ConnectRequest field 5 is client_sdk_info, not a
  bind. Our minimal ConnectResponse is accepted and the client advances to Logon.
- `--serve` now: acks Logon (empty NoData) and calls AuthenticationClient.
  OnLogonComplete(LogonResult{error_code=0, battle_tag, EntityId account ids}).
  The Logon ack alone is accepted (client waits); adding OnLogonComplete makes the
  client cleanly close (native job error 0, not a TLS/connection failure). Routing
  params (hash 0x71240E35, method 5) are byte-verified correct, so the client is
  rejecting the LogonResult CONTENT. Next: real EntityId high-word type bits and/or
  session_key; iterate LogonResult until the client stays connected and proceeds.

## 2026-10-12 — OnLogonComplete content is parse-clean but flow-rejected

- LogonResult now uses EntityId type tags (account high=1<<56, game=2<<56) and a
  session_key; all fields are wire-type-correct against docs/BGS_PROTOCOL.md.
  Client still cleanly closes right after OnLogonComplete (native job error 0).
- Since routing (hash 0x71240E35, method 5) and encoding are both verified, the
  client is rejecting on LOGIN-FLOW LOGIC, not parse/route. The client ships an
  embedded CEF browser (`_retail_/BlizzardBrowser`) and sent Logon with empty
  cached_web_credentials — it expects the web-auth session to occur, and treats
  an unsolicited OnLogonComplete(success) as invalid.
- Next (needs client-code analysis, not more blind runs): read the Authentication
  Client/login state machine in the image to find the exact post-Logon sequence
  the client requires (e.g. a server-pushed web-auth URL + VerifyWebCredentials,
  or a prerequisite OnServerStateChange), then implement that sequence.

## 2026-10-12 — client waits for server-driven login completion

- `--no-grant` (ack Logon, no OnLogonComplete, 40s observe): after the Logon ack
  the client stays connected and, ~21s later, sends ConnectionService.KeepAlive
  (method 5, empty) and keeps waiting. It does NOT open CEF or start web-auth on
  its own. So the server is expected to drive login completion.
- Sending OnLogonComplete causes an immediate close (vs. surviving 21s+ without).
  Routing (hash/method) and LogonResult encoding are verified, so the client
  actively rejects the completion's VALUES or a missing prerequisite callback.
- Resolving this by guessing is exhausted; next is reading the AuthenticationClient
  method-5 handler in the client image. Added tools/offline-launch/re/mdump.py to
  read VAs out of the minidump for disassembly.

## 2026-10-12 — located the client's OnLogonComplete handler

- Added tools/offline-launch/re/mdump.py (minidump VA reader + numpy xref +
  capstone disasm; run with PYTHONPATH=<scratch>/pylibs, no -I so capstone loads).
- Client exports its services in a registration table at rva 0x00e369xx:
  call site encodes rdx=(hash<<32)|(0x80000000|method). Confirms the listener is
  AuthenticationClient 0x71240e35 (our hash is correct), with method 5 =
  OnLogonComplete. Also confirms bindless dispatch by hash.
- OnLogonComplete handler = rva 0x00e2ebe0 (reached via thunk 0x00e2f310).
  It parses LogonResult, requires [rbp+0x48]==0, iterates game_account_id, and
  branches on a result field == 0x35 (53) into a path that XOR-decrypts embedded
  data (web-auth related). The token value is irrelevant (high-token test still
  closed). Reject/parse-fail paths of the sibling method return quietly; the
  immediate close on our grant comes from this handler's own logic.
- Next: finish reversing 0x00e2ebe0 to determine the exact LogonResult the accept
  path needs (and what [rbp+0x48] / the 0x35 branch require) vs. the disconnect.

## 2026-10-12 — OnLogonComplete(error_code=0) is accepted by the handler

- Finished reversing the handler at rva 0x00e2ebe0. Flow for our grant:
  parse LogonResult (ok) -> status gate [arg+0x48]==0 (ok; we send no status) ->
  store account_id into auth object [r14+0x60] and battle_tag into [r14+0xd0] ->
  error_code switch. The switch is error telemetry only; every case (incl. the
  error_code==0 branch at 0x00e2f11a, report id 0x10069) ends at the quiet tail
  0x00e2f2e1 (destruct + ret). No branch in this handler disconnects.
- Conclusion: the client ACCEPTS OnLogonComplete(error_code=0) and records our
  account/battletag. The post-grant close is therefore DOWNSTREAM of the handler
  (the client's logged-in flow proceeding and then failing/finishing), not a
  rejection of the grant. Routing, encoding, and acceptance are all confirmed.
- Next: trace what the client does after the handler returns (the logged-in
  phase) to see which further backend step it needs before the main menu, and
  whether it keeps or drops the bgs connection.

## 2026-10-12 — CORRECTION + real login: game account must carry program 'Pro'

- **Correction to the previous entry:** the error_code switch is NOT telemetry-only.
  Every case, including the error_code==0 branch (0x00e2f11a, id 0x10069), calls
  0x7ff7952360a0, which moves the auth object to state 1 (via 0x7ff795236630) and
  fires the logon-failure virtuals (+0xd0/+0xd8). That was a rejection.
- The real success path is 0x00e2ed93 (sets auth state 0x18, then 0x7ff795227150).
  It is taken only when a LogonResult.game_account_id decodes through helper
  rva 0x02152e10 as: type (high>>56) == 2, region byte ((high>>32)&0xff) != 0,
  program (low 32 bits of high) == 'Pro' 0x0050726f (global rva 0x0267838c), and
  low != 0. Our game account used high = 2<<56 only, so it failed.
- With high = (2<<56)|(1<<32)|0x0050726f the client accepts the login, keeps the
  connection, and enters the logged-in phase: it repeatedly calls
  **GameUtilities.ProcessTask** (service hash 0x5dbb51c2 =
  FNV-1a("bnet.protocol.game_utilities.v2.client.GameUtilities"), method 1) with
  attributes service_type, request_type, version=3, build=104319, cluster,
  platform_available, payload(empty), plus ConnectionService.KeepAlive. It
  retries with backoff when given an empty ProcessTaskResponse, so the next step
  is producing the result attributes it expects. Schema added to BGS_PROTOCOL.md.
- retail_ca_probe: per-pass TLS-context search deadline 15s -> 60s; under host load
  a single scan exceeded 15s and aborted the run ("CA session search deadline").

## 2026-10-12 — post-login ProcessTask is the Balancer referral

- Short ProcessTask string values (request parameters only) are now logged:
  service_type='Balancer', request_type='Referral', version=3, build=104319,
  cluster='Pro', platform_available='pc_1', payload=empty blob. This is the
  load-balancer referral: the client asks where its game-service gateway is.
- The client's referral attribute table (heap copy of its string pool) lists the
  response vocabulary: response_type in {ReferralInfo, ReferralQueue,
  ReferralUpdate, ReferralError}, plus payload, callback_delay,
  approx_queue_position, error_code, debug_error_message, psplus_product_code.
  Request-side extras: online_id, psn_account_id, xid, platform_env, method_name.
- An empty ProcessTaskResponse makes the client retry with backoff. Next: decode
  the ReferralInfo payload format from the client's handler and return a referral
  to our own gateway.

## 2026-10-12 — ReferralInfo accepted; lobby handshake served up to the signed credential

- Decoded the Balancer referral response. Dispatcher rva 0x00e2a880 reads result
  attribute `response_type` and routes ReferralError -> 0x00e2ff20, ReferralInfo
  -> 0x00e2f6c0, ReferralQueued -> 0x00e30090; anything else = referral state 4
  (failure). ReferralInfo requires all six attributes (names are XOR-obfuscated
  inline strings in the handler): `k0`,`k1`,`k2`,`k3` = 64-byte blobs, `cid` =
  uint, `hostv4` = string. Variant type tags equal the proto field numbers
  (4 string, 5 blob, 6 uint). Success = state 5 + the requester's callback.
- `tools/bnet-probe.py` now answers the referral with random per-session keys and
  `hostv4=127.0.0.1:1119` (the only bridged endpoint). The client accepts it and
  immediately opens a **plaintext TCP connection** to hostv4 that starts with
  `HELLO PRO CLIENT\0` (17 B). With no reply it retried the referral (run 4).
- Reversed the lobby pipe handshake (handler rva 0x00e38fe0, state at pipe+0x80;
  referral copied to pipe+0x88: k0 +0x88, k1 +0xc8, k2 +0x108, k3 +0x148, cid
  +0x1a8). Raw little-endian messages, one per send, no framing:
  1. C `HELLO PRO CLIENT\0` / S `HELLO PRO SERVER\0`
  2. C `cid u64 | client_random[32]` / S `challenge[32] | difficulty u8 | server_random[32]`
  3. C `nonce u64 | HMAC-SHA256(k0, CR|SR)` / S `HMAC-SHA256(k1, SR|CR)`
  The nonce is a proof of work (rva 0x00e38990): SHA-1(challenge | nonce) must
  have >= difficulty low-order zero bits (difficulty <= 160). Session keys are
  HMAC-SHA256(k2, CR|SR) and HMAC-SHA256(k3, SR|CR) (rva 0x00e39890).
- Run 6 (live): the probe served stages 1-3. It verified the client's
  HMAC(k0) proof as valid (confirming the key/cid/random mapping), sent HMAC(k1),
  and the client stayed connected silently for 60 s, then closed and requested a
  new referral. Bridge byte counts match exactly: 97 B up (17+40+40), 114 B down
  (17+65+32).
- **Hard gate (state 4):** the client next expects a 256-byte block that it
  raises to e=65537 mod a 2048-bit modulus **embedded in the client** (key built
  at rva 0x00e386a0 from rva 0x026779d0; RSA op rva 0x024d3510). The result must
  carry the 19-byte server address (checked against the peer address/port) and,
  at +0xb0, an HMAC-SHA256 under a client-embedded key (rva 0x01908fe0). This is a
  Blizzard-signed server credential. We do not have that private key and will not
  forge it. An unmodified client therefore cannot complete the lobby handshake
  against any third-party server. Moving past it means having the owned
  diagnostic process trust OUR key instead (e.g. replace the modulus in the
  heap key object at pipe+0x28 with our own public key, analogous to
  `-TrustSocketCa`), which is a scope decision for the project owner.
- Run hygiene: the launcher's primary-thread scheduler now undoes its own suspend
  and retries when the client already holds the thread suspended (two runs saw 36
  client-suspended threads and aborted the socket-CA install); the socket-CA install
  window is 15 s. The probe binds with SO_EXCLUSIVEADDRUSE, so a stale probe makes
  a new one fail instead of silently sharing port 21119 (this contaminated run 3).
  Always stop the previous probe before a run.
- Not verified: main menu, lobby session, map, heroes or matchmaking.

## 2026-10-12 — lobby credential decoded; key-trust swap approved, keypair generated

- User approved making the owned diagnostic client trust OUR RSA key for the
  lobby credential (not forging Blizzard's), analogous to -TrustSocketCa.
- Credential verifier fully reversed (rva 0x01908fe0). The 256-byte RSA-recovered
  plaintext block layout: [0x00..0x13) 19 B server address struct (parsed by
  0x0041a940, a type-tagged address reader); [0x13..0xAF) 156 B + [0xAF] 1 B
  payload; [0xB0..0xD0) 32 B HMAC-SHA256 tag (the compared value, memcmp 0x184f590);
  [0xD0..0xFF) 47 B + [0xFF] 1 B payload. HMAC covers everything except the tag,
  keyed by a 64-byte client-embedded constant at rva 0x0278cf30 (value captured
  in scratch; it is integrity, NOT the authenticity gate).
- The authenticity gate is RSA: client reads a 256-byte wire ciphertext, computes
  C^e mod N (public op rva 0x024d3510) to recover the block. Embedded public key:
  modulus 256 B at rva 0x026779d0, exponent 3 B at rva 0x026779c4 = 010001.
  **Both modulus and exponent are LITTLE-ENDIAN** byte arrays (bignum loader
  0x024d32d0 builds the integer LSB-first: modulus as big-endian is even/2044-bit,
  as little-endian it is a proper odd 2048-bit modulus). The key object is built
  per pipe by ctor 0x024d34c0 from those static bytes into a heap bignum; the
  pipe holds the key object pointer at pipe+0x28.
- Generated our own RSA-2048 keypair at
  %LOCALAPPDATA%\OW1-preservation-build\private-tls\lobby_key.pem (+ lobby_pub.pem).
  Private key stays there, never committed.
- Plan (next session): (A) probe builds the credential — fill the block, place the
  HMAC tag with the embedded key, sign C = block^d mod N_ours, send 256 bytes
  little-endian; validate offline with a harness that plays the client's exact
  C^e-mod-N + field/HMAC checks. (B) launcher opt-in (e.g. -TrustLobbyKey) swaps
  the client's trusted modulus with ours. Prefer the heap key-object mutation
  (pipe+0x28) over a static .rdata write (.rdata is likely mapped execute-read;
  image-page writes previously failed Win32 87). Our key must be 2048-bit, e=65537
  to match the existing bignum layout.
- Iterate the block's unknown payload/address fields via the client's own failure
  report codes (0x300xx emitted at each check), as with earlier stages.

## 2026-10-13 — own-key lobby credential accepted; next application packet captured

- Continued from Claude's commit 485f280 and its generated own RSA key. Added
  `-TrustLobbyKey <public.modulus>` / `--trust-lobby-key`: exactly 256 LE public
  modulus bytes, odd and 2048-bit. Requires existing bounded loopback CA/socket
  diagnostics, which already require the exact final executable fingerprint.
- Validated key-object vft 26569c8, owning pipe vft 2616130 and original function
  guards. Native modulus is 74 28-bit limbs (allocation 75); exponent is 65537.
  Under a balanced owned-process pause, compare the original heap limbs to the
  original image modulus, write our limbs and read them back. Allocation,
  ownership and verifiers are preserved. A failed installation rolls back.
  This first version installs one pipe key per launch; retry integration is pending.
- Own private key stays outside Git. `tools/lobby_credential.py` validates the
  operator's RSA-2048/e=65537 key, exports only the public modulus and extracts
  the client-local 64-byte integrity input from an exact guarded dump call-site.
  No native key/constant bytes or client image are bundled in source.
- Native transport correction: it waits for **292 decrypted bytes**, not 256.
  After HMAC(k1), receive encryption is already active. Cipher is Panama-LE;
  client receive key HMAC(k2,CR|SR), send key HMAC(k3,SR|CR), key also used as IV.
  Independent Python implementation passes the public Crypto++ cipher vector.
  The packet is RSA credential[256] + two 128-bit identifiers + uint32 metadata.
  Current suffix is local server assignments (1,1),(cid,1),0; semantic decoding
  remains pending. Signing and plaintext/tag layout pass an own-key roundtrip.
- Native positive runs 2 and 3: CA and socket setter pass; our heap key is
  installed at handshake state 4. Our encrypted credential makes the client
  advance to **handshake state 6 / connection phase 6** through its original
  RSA/integrity/address checks. Bridge lobby counts: 110 B client -> host,
  406 B host -> client. The extra 13 client bytes decrypt to a 3-byte BE length
  plus a **10-byte body starting with byte 1**.
- Run 1 (256 raw bytes) timed out at the receive gate. Run 2's initial observer
  closed after one read; run 3 keeps the gateway connection open and the CLIENT
  closes about ten seconds after sending its first application packet. Required
  response/schema remains unverified. No main menu, map, hero or game session.
- Original-key native control: same server credential/cipher, no key install.
  Client closes immediately upon each credential, sends only the original 97 B
  handshake data, and retries referral. No post-credential application packet.
  This supports that original verification is active and the own key is needed.
- Local logs: retail-private-own-lobby-key1/2/3, original-lobby-key-control;
  server logs under private-mapped-ca. Named dumps are preserved outside Git.
  Key, integrity files and modulus files are ignored. Never publish scratch.
- Next: decode the 10-byte gateway packet and required reply. Research call chain:
  lobby success vft+a8 -> 7beff0 -> e3e160 -> 56b330 -> 563410 -> 55ff60 ->
  562810 (connection negotiation emitter) -> 560d90; message constructors
  56cb90/56cc50 and initial parser paths 560040/561890 are useful candidates.
  These references are interface research, not a verified reply implementation.

Validation checkpoint: all native targets build and 14/14 CTest targets pass.
Client executable hash/signature and both saved ACLs remain unchanged. Owned
clients/launchers/observers are stopped. Do not infer gameplay from this result.

## 2026-10-13 — gateway negotiation scaffold + reply-parser reversed

- Preserved the gateway negotiation layer codex left uncommitted when its session
  was cut off (tools/gateway_protocol.py, tools/gateway_catalogue.py,
  protocol/gateway-104319.json, probe + test wiring). It parses the client's
  bootstrap offer, loads the exported interface catalogue, frames packets
  (3-byte BE length) and replies. All 9 probe unit tests pass; no native change,
  so the 14/14 CTest checkpoint is unaffected. Catalogue JSON holds only protocol
  hashes/id-ranges/flags/group numbers (no code, keys or assets), like
  docs/BGS_PROTOCOL.md.
- The client's first post-credential packet is a bootstrap OFFER (10 B over the
  Panama stream): `channel=1, version=0, count=u32=1, schema_hash=u32=0x11d82194`
  (group-0 bootstrap protocol; gateway-104319.json record 0, ids 1..5, flags 3).
- **Reversed the client's reply parser (the open question).** Incoming gateway
  messages are dispatched by the negotiation state machine at rva 0x00560040
  (ctx state at +0x18). In state 2 it calls 0x00561180 (adopts the sender
  ProcessId at msg+0x78) then 0x00561890, which iterates the message's record
  vector at msg+0x88 (count at +8) and calls per-record handler 0x00561730 for
  each 0x40-byte record. 561730 reads the record's schema hash (record+0) and
  looks it up in the client's local catalogue via 0x00569a70; an unknown hash
  takes the reject path 0x005615f0. Only after 561890 succeeds does the client
  emit its response (0x00562810) and advance state 2->4; a later message drives
  3->5 (final ack via 0x0056ccc0 + 0x00562600).
- **Therefore the required state-2 reply is the server's own catalogue OFFER**
  (sender identity + the protocol hash list the client can resolve), NOT a 2-byte
  `01 02` ack. This is consistent with the observation that codex's positive runs
  2/3 — which already sent `01 02` — still had the CLIENT close ~10 s after its
  offer. `gateway_protocol.offer_response` returning `01 02` is thus an
  unverified hypothesis that the reversed parser contradicts.
- Next (needs a live own-key run): send a version-matched catalogue offer back
  (channel 1, the client's offered schema hash(es), wire form = channel,version,
  count,hashes — records are expanded locally from the catalogue by 561730).
  Use the client advancing to negotiation state 4 then 5 (and not closing) as the
  success signal; iterate the `version` byte (0 vs the role the native mode-2
  responder expects) and whether an identity prefix is required. Still unverified:
  main menu, gateway session, map, heroes, matchmaking.

## 2026-10-13 — own-key gateway run with catalogue-offer reply; state model corrected

- Reconstructed the key inputs codex had only in a virtualized FS: regenerated
  lobby-public.modulus and the 64-byte lobby-integrity.credential-key from
  private-tls/lobby_key.pem via tools/lobby_credential.py (RSA roundtrip passes),
  and rebuilt the launcher so the committed `-TrustLobbyKey` is in the binary.
- Added a selectable state reply: `gateway_protocol.catalogue_offer` mirrors the
  client's offered hash list back (channel,version 0,count,hashes), and
  `bnet-probe.py --gateway-reply {offer,ack}` (default offer). All 9 unit tests pass.
- **State model corrected (important).** The lobby negotiation initiator (rva
  0x0055ff60) sets state by peer role at ctx+0x1c: the CLIENT is mode 1
  (initiating), so after emitting its offer (0x00562810 -> message ctor 0x0056cb90)
  it goes to state **3**, not 2. In state 3 the receive handler 0x00560040 parses
  the server's incoming message (0x00561890 over the record vector at msg+0x88),
  and on success sends the client's FINAL message (ctor 0x0056ccc0) and advances
  to state **5** (negotiated). State 2 is the mode-2 responder path.
- Live own-key run (retail-gw1): CA + socket setter + heap key install all pass;
  own credential accepted; client reaches handshake state 6 / connection phase 6
  and sends its 10-byte offer. Our catalogue-offer reply (the client's own 10
  bytes echoed) did NOT advance it: the client closed the lobby immediately
  ("peer closed"), then sent bgs KeepAlives and re-requested a referral (~60 s
  backoff). The earlier `01 02` ack failed the same way. So neither reply is
  structurally accepted.
- Conclusion: the blocker is the reply's exact WIRE serialization / message type,
  not the negotiation semantics. The mode-1 client in state 3 likely requires the
  responder's distinct "response" message (ctor 0x0056cc50, vtable rva 0x02609cd8;
  it zeroes +0x78/+0x80/+0x88), NOT an echoed offer (ctor 0x0056cb90, vtable
  0x02609cf8). The three bootstrap message types' vtables are adjacent
  (0x02609cf8 offer, 0x02609cd8 response, and the final type). Their visible vtable
  slots (0x0056d040/0x0056d190/0x0056d210) are clone/factory methods; the actual
  field serialization is a visitor framework invoked by the transport (0x00560d90
  send path) — reversing that framework is the next concrete RE target.
- Next: (1) capture the exact decrypted 10-byte offer with `--lobby-packet-capture`
  to pin the on-wire record encoding empirically; (2) reverse the serialize/
  deserialize visitor to build the responder "response" message (opcode/type 2)
  correctly; (3) rerun and use the client advancing to negotiation state 5 (and
  not retrying the referral) as the success signal. Still unverified: main menu,
  gateway session, map, heroes, matchmaking.

## 2026-10-13 — gateway receive pipeline fully mapped; framing confirmed correct

- Added a candidate-cycling reply mode (`--gateway-reply probe`): each referral
  retry is a fresh lobby connection, so the probe sends one candidate responder
  message per connection and logs the client's reaction. Captured the exact
  decrypted offer with `--lobby-packet-capture`: `01 00 | 01 00 00 00 | 94 21 d8 11`
  = u16-LE message id 1, uint32 count 1, schema hash 0x11d82194 (confirms codex's
  parse). The message id is a u16 (native reads a word, rva 0x00565260).
- Live runs: tried replying with id-1 echo, the 2-byte ack, and id-2 variants
  (with/without a 16-byte identity, with/without the hash list). EVERY reply makes
  the client close immediately; sending nothing makes it wait ~10 s. That timing
  difference shows the problem is the reply bytes, not the absence of a reply.
- **Mapped the full receive pipeline** (resolves where replies must go):
  - recv dispatcher rva 0x01908cf0 branches on the handshake-complete flag
    peer+0x1053. Pre-handshake -> the fixed-stage state machine (rva 0x019094a0,
    state at peer+0x104c) that consumes exactly hello, 65 B (challenge+difficulty+
    server_random), 32 B (HMAC k1 proof), then 292 B (credential); state 5
    (rva 0x01909330) then frees the handshake buffer, sets peer+0x1053=1 and goes
    inert. Post-handshake -> decrypt (Panama, ctx+0x1040) then the gateway reader.
  - gateway reader rva 0x0041a100: reads **3-byte big-endian length + body**
    frames (so the probe's framing is correct) and hands each body to the message
    dispatcher rva 0x0041db50 -> 0x0041cd60.
  - the dispatcher requires peer state peer+0x20 == 6 (matches the observed
    connection phase 6) and parses the body with field readers 0x02378cf0 /
    0x02378d40 (varint/length-delimited style).
- Conclusion: TLS, login, referral, lobby handshake, own-key credential, Panama
  cipher (both directions) and the 3-byte gateway framing are all correct and
  confirmed. The remaining blocker is purely the message BODY format that
  0x0041cd60 accepts. Both the record-vector reply model (560040/561890) and the
  simple id/ack models are ruled out by live runs.
- Next RE target: reverse 0x0041cd60 (and its field readers 0x02378cf0/0x02378d40)
  to get the exact body schema of the responder's first negotiation message, then
  emit it via `--gateway-reply probe` candidates and watch for the client leaving
  phase 6 (not retrying the referral). Key inputs, cipher and framing are all in
  place for that run. Still unverified: main menu, gateway session, map, heroes,
  matchmaking.

## 2026-10-13 — gateway message dispatch mapped (reply is id 2); body encoding is the wall

- Found the gateway message dispatcher: rva 0x0055e980 reads the message id as a
  u16 (via 0x00565260) and routes by id to per-type handlers:
  id 1 -> 0x005601e0, id 2 -> 0x00560040 (the negotiation state machine analysed
  earlier), id 3 -> 0x00560370, id 4 -> 0x0055e9e3.
- Confirmed why echoing the client's id-1 offer fails: handler 0x005601e0 requires
  the peer to be a mode-2 responder ([peer+0x1c]==2) in state 2. The client is a
  mode-1 initiator, so it rejects any received id-1 and closes. The reply the
  mode-1 client expects in state 3 is an id-2 message (-> 0x00560040 state-3 path:
  adopt sender via 0x00561180, parse records via 0x00561890, send the client's
  final id-3 and advance to state 5). id 3 handler 0x00560370 accepts state 3/4.
- id-2 message struct (field table rva 0x02cf0180): a {seq, src} header at object
  offset 0x78 (sub-type rva 0x02cefb60, two 8-byte fields literally named "seq"
  and "src") followed by a record vector at 0x88. id-1 has no such header (just a
  record vector at 0x78/0x80), which matches the captured 10-byte offer
  (u16 id, u32 count, u32 schema hash; vectors are fixed-width, untagged).
- Live-tested six id-2 body encodings over the Panama gateway stream: id+records,
  id alone, id+count0, id+16-byte-zero-header+records, id+{1,0}-header+records,
  and the id-1 echo / 2-byte ack / mirror from before. EVERY one makes the client
  close immediately (vs ~10 s wait with no reply). So transport, framing (3-byte
  BE length), cipher and the id-2 routing are all correct; the exact id-2 body
  WIRE ENCODING is the only remaining unknown.
- Wall: that encoding is produced by a generic reflection (de)serializer that
  walks the per-message field tables (0x02cf0180 etc.); it takes the descriptor as
  an argument and is heavily obfuscated, so it is not resolvable by the static
  xref method used so far, and debugger attachment crashes the client.
- Recommended next approach (not yet done): extend the existing bounded owned-
  process observer (retail_tls_observer / lobby key installer style - safe
  ReadProcessMemory, no debugger) to dump a correctly-serialized id-2 message that
  the client itself builds (ctor 0x0056cb90, which populates +0x78/+0x88), or to
  single-shot the generic serializer, and read the exact wire bytes. That gives
  ground truth for the id-2 body without guessing. Still unverified: main menu,
  gateway session, map, heroes, matchmaking.

## 2026-10-13 — id-2 gateway message schema fully decoded; wire framing still unresolved

- Enumerated all four bootstrap message descriptors (schema 0x11d82194):
  id1 field table 0x02cf0120, id2 0x02cf0180, id3 0x02cf0030, id4 0x02cf0080.
  Confirmed id-1 (the client's offer) = u16 id + a type-6 vector (u32 count +
  u32 schema hashes), matching the captured 10-byte offer exactly.
- Decoded the id-2 message (the reply the mode-1 client wants in state 3):
  field 0 = a {seq:u64, src:u64} header (nested type 0x02cefb60, fields literally
  named "seq"/"src") at object offset 0x78; field 1 = a repeated record at 0x88
  whose element (field table 0x02cf0380) has named fields m_protocolCRC (u32),
  m_messageBase (u32), m_messageMax (u32), m_protocolFlags (u32),
  m_untrustedServer (bool, type 7), m_protocolName (string, type 12). The
  bootstrap record values are {0x11d82194, 1, 5, 3, false, ""} (gateway-104319.json).
- Reversed the primitive serializer rva 0x00561e90: primitives are written RAW,
  fixed-width, inline — no field tags, no length prefixes (type bits
  0x10/0x20/0x40/0x80/0x100 -> 1/2/4/8/16 bytes). So id-1's inline encoding
  generalises to id-2's primitives.
- Built and live-tested the full decoded id-2 body in many framings: inline
  header + records with u32/u16/u8/omitted string-length prefixes, and
  length-prefixed (u32) nested header and/or records, with and without the
  header. EVERY variant still makes the client close immediately (it then retries
  the referral); no candidate advanced it past connection phase 6.
- So: message id (2), the record field set, and primitive encoding are known and
  correct, but the exact framing of the nested {seq,src} header, the record
  vector, the bool and the type-12 string (and possibly required seq/src values)
  is not captured by inline or simple u32 length-prefix forms. The generic
  field-walker + string/vector/nested routines are a separate obfuscated layer
  (primitive writer 0x00561e90, record populate 0x00561ac0, write path 0x00560d90)
  that resists the static xref method, and debugger attach crashes the client.
- Documented the decoded schema in docs/BGS_PROTOCOL.md. Recommended path
  (unchanged, now better scoped): a bounded owned-process observer that invokes
  the client's own id-2 serializer (ctor 0x0056cb90 + the field walker) and dumps
  the resulting wire bytes for ground truth, rather than guessing the framing.
  Still unverified: gateway session, main menu, map, heroes, matchmaking.

## 2026-10-13 — gateway serializer framework investigated; wire framing unresolved

- Traced the message serialize path from 0x00560d90: it calls the message's
  vt+0x28 (0x005651f0) then a generic walker 0x00568690, which iterates the field
  table (stride 0x30, terminator type 0x11) and per field calls 0x00568050
  (single) / 0x00568150 (repeated) -> leaf 0x00568250, bracketed by 0x003f4e40 /
  0x003f5200 / 0x003f5620.
- Determined 0x003f4e40/0x003f5200/0x003f5620 are **trace-scope markers**, not wire
  writers: they push/pop a scope stack at obj+0x1e0 and call a formatter 0x003f5480
  with format strings. Likewise 0x00568250's type dispatch (jump table at
  0x00568630, type <= 0x10) passes each field's **name pointer** (e.g.
  "m_protocolCRC") to per-type encoders 0x00566xxx. Passing field names means this
  whole 0x00568690 path is a **named/trace serializer** (message logging/dump),
  distinct from the compact wire form (the captured id-1 offer has no field names).
- The real wire primitive writer is 0x00561e90 (raw, fixed-width, no names/tags),
  but the wire-side field walker that drives it for a full message was not cleanly
  isolated: the send path interleaves the trace walker and the wire writer, and
  the framework is obfuscated enough that the exact nested/vector/string wire
  framing could not be pinned by static reading. Debugger attach crashes the client.
- Net: the id-2 message schema and primitive encoding are known; the per-field
  wire framing (header/count/string) is still not确定. Pure static RE and black-box
  probing are exhausted for this.
- Refined recommended approach: capture a **genuine** id-2 from the client by
  flipping it to a mode-2 responder. The gateway negotiation context holds the
  role at ctx+0x1c (==1 initiator; id-1 handler 0x005601e0 requires ==2). Using
  the lobby-key installer's find + bounded guarded-write pattern
  (retail_lobby_key.h), locate the negotiation context after the credential and
  set ctx+0x1c=2 before it emits (0x0055ff60); then send it our known id-1 offer
  and record the id-2 message it serializes and sends on the wire. That yields the
  exact bytes without guessing or in-process code injection. Still unverified:
  gateway session, main menu, map, heroes, matchmaking.

## 2026-10-13 — mode-flip capture assessed as unreliable; id-2 encoding unresolved

- Specified the gateway context fully: created/initialised by 0x00560560 (called
  from 0x00563ca5 inside the receive setup 0x00563410), which hardcodes the role
  ctx+0x1c=1 (initiator), sets ctx+0x84=mode flag, ctx+0x88/0x8c, and builds the
  first message via 0x00561d60. The context is registered into the gateway peer
  object and is locatable by signature (ctx+0x1c in {1,2}, ctx+0x8c=0x1000000,
  ctx+0x88 in {0x18800,0x1000000}, message object at ctx+0x78) with the
  lobby-key installer's scan pattern.
- However the mode-flip capture (set ctx+0x1c=2 so the client acts as a responder
  and serialises a real id-2 we can record) is **not reliable** with polling-only
  instrumentation: 0x00560560 (role set) and the emit path 0x0055ff60 (which reads
  ctx+0x1c and sends the offer, advancing to state 3) run back-to-back in the same
  call chain, so there is no observable window to interpose the write. Flipping the
  role afterwards does not help because the id-1 handler 0x005601e0 also requires
  state==2, so a late flip would have to overwrite the live state machine
  (ctx+0x18) as well — invasive and crash-prone, and debugger/HWBP single-stepping
  of the serialiser crashes the client (established earlier).
- Bounded ReadProcessMemory polling and guarded heap writes did not capture
  the exact id-2 wire framing; the serialiser is obfuscated and interleaves a
  named trace serialiser (0x00568690) with the compact wire writer (0x00561e90),
  and neither the wire field-walker nor the string/nested framing could be pinned.
- Everything up to this point stands and is reproducible: TLS, login, Balancer
  referral, lobby handshake, own-key credential, Panama cipher both directions,
  the 3-byte gateway framing, the full message dispatch map and the complete id-2
  message schema (docs/BGS_PROTOCOL.md). The remaining unknown is one message's
  byte framing. No gateway session, main menu, map, hero or matchmaking is
  verified; none should be claimed.

## 2026-10-13 — gateway codec reversed; bootstrap negotiation completes live

- Re-read the send path from 0x00560fb6: it writes the protocol entry byte
  (entry[0], bootstrap = 1), an optional per-entry header (0x00561e90; empty for
  bootstrap), then 0x00568690 in mode 1 writes ONE byte = message id - the
  protocol's m_messageBase and calls the compact binary walker 0x005652b0. The
  "named/trace" walk is only mode 2. So the captured offer `01 00 | 01000000 |
  9421d811` is entry 1, id 1, u32 count, u32 hash; it was never a u16 id.
- Compact encoding (writer 0x005652b0, reader 0x005670e0 via decoder
  0x00567de0 from receive path 0x00561ff0): no tags or length prefixes, nested
  structs inline, vectors as u32 count + elements, type 0 bit-packed bool,
  types 6/7 u32 (m_untrustedServer is 4 bytes), type 8 u64, type 12/13
  NUL-terminated strings. Receive framing (0x0041a100) confirmed as 3-byte BE
  length from the reader itself.
- The handlers depend on ctx+0x84 bit 0 (a caller argument to init 0x00560560):
  id 2 (0x00560040) disconnects when it is clear; id 3 (0x00560370) is accepted
  in state 3 when it is clear and moves to negotiated state 5. Per-state timers
  (0x00560b50 / 0x005609c0): states 1-4 expire into shutdown (the old ~10 s
  close); state 5 expiry sends an id-4 heartbeat.
- Live runs (own key, CA + socket CA, bounded): decoded id 2 (`01 01` + seq/src +
  one bootstrap record, 43 B; `--gateway-reply id2`) still closes immediately,
  as the bit-0 check predicts. Empty id 3 `01 02` (`--gateway-reply ack`, now the
  default) negotiates: the client sends `01 03` heartbeats every 5 s, the probe
  echoes them, and lobby #2 stays open 112 s (22 heartbeats) until the bounded
  run ends. Earlier notes that `01 02` "failed the same way" were wrong.
- New frontier: ~60 s after negotiation, with lobby #2 still up, the client
  asks for another Balancer referral and opens lobby #3 (also negotiates; the
  own key was accepted again). The upper lobby layer is waiting for something
  after the negotiated event (0x00562600 event 0). Probe now logs each gateway
  packet's entry byte and message delta only. Unit tests: 10 pass.
- Still unverified: application lobby session, main menu, map, heroes,
  matchmaking.

## 2026-10-13 — lobby service protocols negotiated (peer group 13); first application messages decoded

- The offered protocol list comes from the gateway peer id's group
  (0x00561ac0 -> channel query by `(id >> 40) & 0xffff`); 0x00563410 adopts the
  server id from the credential suffix before the offer. With group 0 only the
  bootstrap protocol is offered, which is why the client re-requested a
  referral ~60 s later.
- Live run with `--lobby-peer-group 13`: 350-byte offer of all 86 group-13
  hashes (exact catalogue match), `00 02` accepted, heartbeats every 5 s, and the
  client immediately sent protocol 0x3c7e3468 messages 21800 (218 B) and 21809
  (3 B) on entry 25. No re-referral during the 112 s run.
- Decoded 21800 against the client's own field table (all 216 body bytes
  consumed), confirming the compact codec end to end: a client hello carrying
  the granted game account id, locale/platform, build, product string and
  empty optional records. Captures stay local under private-tls/mapped/cap13.
- Flag-2/10 group-13 protocols have client receive dispatchers
  (0x007a8120-0x007ab630); flag-1 ones are client-to-server. The reply to
  21800 is therefore some flag-2 message, not yet identified in that session.
- Probe: the `ack` reply accepts bootstrap-only or the exact group catalogue
  and logs the offered count; per-connection packet bound raised to 1024.
- Still unverified in that session: lobby login result, main menu, map, heroes,
  matchmaking.

## 2026-10-13 — initial identity reply advances the original UI

- Continued Claude's current `main` in the requested project directory. New
  private RE/run files live in ignored `.local/`; original client/build/key
  caches are reused, with no new checkout. Added `-LogRoot` and project-default
  private launch logs.
- Mapped native dispatcher 0x7a9860: 20500 -> 0x774710 -> 0x6261e0. The last
  helper copies identity/string fields into the login context and raises event
  13. Exported numeric schemas only for 20500/21800/21809. No image bytes,
  captured account payloads, keys or assets are included in source.
- Added bounded compact decoding/encoding. All 216 bytes of a private native
  21800 body decode and re-encode exactly. Public fixtures cover known bytes,
  bool alignment, strings, arrays, truncation, schema bounds and recursive/
  ambiguous descriptor rejection.
- Opt-in `--lobby-login-schema` answers the exact granted local account/build
  once with message 20500 (sorted entry 83, delta 0). Uses local identities and
  battle tag; unknown flags/counters stay zero. Original client state, verifiers
  and readiness bits are untouched.
- Native `lobby-identity3`: TLS/credential/group-13 negotiation succeed, the
  81-byte reply is sent, and direct window capture shows **ENTERING GAME…**.
  Heartbeats continue until the 120-second owned run ends; no further application
  request or main menu appears. Two earlier runs fail at TLS timing and do not
  exercise the new reply.
- All 14 CTest targets pass; the probe target contains 14 fixtures. Original
  EXE SHA256/signature and client-folder/launcher ACLs match the saved baseline.
  Next: initial account/configuration/menu gate. 20801's traced handler only
  prints account data; sending that message is not an established solution.
- Negotiation-only comparison also reaches hello/heartbeats without 20500, but
  its game window closed before capture. A repeat fails at TLS startup. Those
  runs do not establish a visual before/after control; the positive screen is
  directly observed. Owned processes/listener end and both ACLs are restored.

## 2026-10-13 — key/hotfix/player notifications; new service requests

- Continued in the requested project directory; private RE, captures and run
  logs stay under ignored `.local/`. Previous public commit 0ffa8a6 passed CI.
- Traced 20504 -> 0x77a560: key entries import through 0x17253f0, then context
  slot 10/+0x40 initializes. Traced 20505 -> 0x77a000 -> 0x57bba0: content-list
  override notifications balance native initialization counters. Added their
  numeric schemas and opt-in empty lists for our server with no added keys or
  hotfix overrides; no native verdict/readiness writes.
- Traced 20502 -> 0x7752a0: player-record consumers at 0x619c90/0x619770 and
  slot 22/+0x88 update marker. Added a local record with our same experimental
  identities, own tag and zero unknown counters. Other field meanings remain
  unverified.
- Native runs initial-keys1 / initial-hotfix1 / initial-player1 each survive
  their 180-second diagnostic with continuing gateway heartbeats. Key-context
  flag changes 0 -> 1. Player run additionally sends 60002 and repeating 42600;
  two-byte request bodies map to entries 29/80 and the published catalogues.
  Related server handlers show migration and tournament data, without a proven
  request/reply pairing or menu dependency. No speculative response is sent.
- Window captures are black, not a visible main menu. Added a guarded,
  read-only boolean dump inspector. Player marker is false in the completed
  player dump; it is not a persistent receipt flag. All 14 CTest targets and
  15 probe/codec/state fixtures pass. Original EXE hash/signature and both saved
  ACLs are unchanged after the three runs. Initial loading/menu gate remains.
- Repeated the player path as initial-focused1; same follow-up requests. Windows
  rejected `@oai/sky` activation with GetCursorPos/Access denied 0x80070005.
  Refresh/retry found no window after bounded exit. No successful foreground
  check or functional menu is claimed from black screenshot captures.

## 2026-10-13 — server-to-client protocol roles mapped; 60002/42600 identified

- Continued from codex's initial-data runs. Built (scratch, outside Git) a
  decoder for the client's XOR-obfuscated strings (4,270 decoded) and a map of
  every flag-2 receive dispatcher to its handlers and their log strings.
- 20501 is `LobbySystem_C::LobbyConnectHelloErrorHandler` (localized error and
  connection state 3/4/5): an error notice, not a success reply.
- The client's 60002 (0x49963fa6) is an account-migration query; its reply
  family 59900 is log-only (migration servers/queue status). 42600 (0xeb45ad29)
  is a tournament status poll (~12 s); 42401 logs eSports match data. Neither is
  evidenced as the menu gate, so no reply is sent for them.
- Other families: 20800 player profile/settings, 24300/24900 unlocks,
  26400/60900 currencies, 28000 achievements, 39800 weekly arcade,
  40900/51800/53000 custom games/replays (docs/BGS_PROTOCOL.md table).
- Candidate gate for later checking: hotfix state machine (~0x00b4cd70, 15 s
  re-poll, "hotfix timeout" after a configurable 81 s in state 4). Not verified.
- No live run in this step; main menu remains unverified.

## 2026-10-13 — world-state manager located; ENTERING GAME has no world request

- Found the client's world/game state machine: manager ctor 0x00b4a5b0
  (vtable 0x02655d88), state byte +0x18, pending request +0x20, tick with
  per-state handlers (~0x00b4cca8). Its own name table (0x00b4f760): 0 SHUTDOWN,
  1 SHUTTING DOWN, 2 WAITING, 3 ABANDONING SCENES, 4 HOTFIXING, 5 GLOBAL LOADING,
  6 WORLD LOADING, 7 WORLD LOADED, 8 WORLD REPLICATING, 9 GAME MODE LOADING,
  10 WORLD_RUNNING. The 81 s "hotfix timeout" belongs to state 4.
- World requests enter through 0x00b4b1c0 (allocates a 0x150-byte request).
  Callers: 0x0082c3e0 (game-server join; fetches hotfix data first and fails
  with "Hotfix unavailable"), 0x008359a0 (local world via on-demand component
  slot 79) and 0x00b97f40 (reached from the 20300 game-server dispatcher, with
  "Server/Client hot reloading mismatch"/"quanta mismatch" checks).
- Native run world1 (full codex sequence: group 13, 20500, empty 20504/20505,
  20502): same requests 60002/42600 as before. Dump: the manager is **WAITING
  with no pending world request**; the hello-only dump is also WAITING. So the
  client has not asked to load any world (menu scene included) and the hotfix
  timeout is not involved. The gate is the front-end logic that issues the first
  world request.
- `tools/retail_login_state.py --world-state` reports the state name and a
  pending-request boolean only. 16 probe fixtures; all 14 CTest targets pass.

## 2026-10-13 — default account preferences (20802) experiment

- Added opt-in `--lobby-initial-data keys-hotfix-player-settings`: after
  codex's 20504/20505/20502 it sends 20802 (profile protocol 0x1a9879a4, entry
  9, delta 2) with every list empty and every flag/byte at zero. Exported its
  numeric descriptor into protocol/lobby-login-104319.json (no payloads). The
  handler 0x7793a0 applies the preference blocks (+0x108/+0x10d); it is not
  log-only. Fixture checks the 52-byte packet independently (16 probe tests).
- Native run settings2 (150 s): accepted, heartbeats continue. New client
  behaviour: message 58400 (protocol 0x692c511b, entry 37; one {u64,u64,u32}
  record, 26 B) every ~30 s after the preferences arrive, plus the existing
  60002 and 42600 polls. No reply sent for 58400.
- Dump: world-state manager still WAITING with no pending world request, so
  preferences alone do not start the menu world. An earlier attempt reused a
  stale probe (port guard refused the new one); that run is discarded.

## 2026-10-13 — MAIN MENU REACHED on the private server

- Desktop screenshots were masked (lock screen), which explains earlier "black"
  captures. Added scripts/Capture-ClientWindow.ps1: renders the owned client's
  window via PrintWindow into a local PNG (keep captures out of Git).
- Runs screen5/6/7 (same server configuration, desktop locked) showed
  "CONNECTING…" then "SORRY, WE WERE UNABLE TO LOG YOU IN. TIME OUT
  COMMUNICATING WITH BATTLE.NET SERVICES", although the protocol completed in
  the background. With --handshake-delay 0 the CA-trust step is too late and
  TLS is dropped.
- Run screen8 (desktop unlocked; probe: group 13, login schema,
  `--lobby-initial-data keys-hotfix-player-settings`, --handshake-delay 25):
  3 s after the initial data the original client shows the **main menu** (PLAY,
  TRAINING greyed, HERO GALLERY, LOOT BOX, OVERWATCH LEAGUE, HIGHLIGHTS, SOCIAL,
  CAREER PROFILE, OPTIONS, PATCH NOTES, EXIT GAME, chat prompt, party/friends
  buttons), then the first-run **TUTORIAL** prompt. The static backdrop has no
  3D hero scene, consistent with the world-state manager having no world request.
- Not yet established: which of the initial messages is strictly required for
  the menu (screen8 is the only visible-desktop run so far), why the locked-desktop
  runs timed out, and anything beyond the menu (tutorial/practice/map loading,
  heroes, matchmaking). Nothing was clicked.

## 2026-10-13 — local accounts and launcher; second main-menu run (Mercy#1002)

- Correction: the "TIME OUT COMMUNICATING WITH BATTLE.NET SERVICES" captures from
  runs screen5/6/7 came from a leftover test client (started 13:23:30) whose
  server had already stopped; the capture helper picked the first window. Bounded
  runs end the diagnostic window but leave the game process running, so the next
  launch (single-instance game) exits early and the old window shows the timeout
  once its server goes away. The screen8 main-menu capture is correctly
  attributed (process started 13:47:41, 2560x1080). The capture helper now picks
  the newest client window or a given process id.
- Added tools/accounts.py: our own local accounts (not Battle.net) in
  `.local/accounts.json`: name, battle tag `Name#<id>`, account id from 1001
  (never reused), optional password stored only as salted PBKDF2-SHA256.
- The account id now reaches every identity we serve: OnLogonComplete
  EntityIds (`--account-id`), the 20500 identity reply, its local identities
  and the 20502 player record; the lobby only answers a hello carrying the
  granted account. Previously 1001 was hard-coded.
- Added tools/ow1_launcher.py (`configure`, `create`, `list`, `delete`, `play`):
  `play` checks the password, refuses while an earlier test client or run is
  active, starts the private server for that account, launches the bounded
  client, and keeps serving until the game closes.
- Live: `play Mercy` -> login as Mercy#1002, 20500 for account 1002 accepted,
  main menu + tutorial prompt captured. 18 probe tests pass.

## 2026-10-13 — interactive main menu; menu requests 22206/22207

- Added scripts/Click-ClientWindow.ps1: posts a left click to the owned client's
  window at window coordinates (pairs with Capture-ClientWindow.ps1).
- Launcher sessions as Mercy#1002: 3 of 4 reached the main menu. One run stayed
  on CONNECTING… and then showed the Battle.net timeout although its server log
  matches a successful run line for line, so the variance is client-side and
  still unexplained. In that run, LOGIN retried without sending any new RPC and
  timed out again; EXIT TO DESKTOP closed the client cleanly.
- In a successful run, NO THANKS dismissed the tutorial prompt; the interactive
  menu showed the original tip "Play the tutorial at any time from the Training
  menu". CAREER PROFILE opens its page (background, ESCAPE/BACK) but with no
  content.
- New client requests on protocol 0x75d32ae2 (entry 41): 22207 (i8 + i32, 7 B)
  twice around the menu interaction and 22206 (two {seq,src} identities + i32,
  38 B) when Career Profile opened, presumably the profile request. No replies
  are sent yet; this is the next protocol frontier for the menu.

## 2026-10-13 — login reliability: 27/27 controlled sessions reach the menu

- Built an unattended trial harness (local scratch): launcher `play`, window
  capture every 5 s, classify menu / tutorial / connecting / error, close the
  client, repeat. Results: plain baseline 8/8, window minimize+restore right
  after the lobby data 4/4, larger plain batch 15/15. Every session reached the
  menu or first-run tutorial prompt 1-7 s after the initial data.
- The earlier stuck-on-CONNECTING session could not be reproduced. Its server
  exchange and launcher diagnostics are identical to successful runs; the only
  unique factor is that the computer-use tool activated the game window, hid
  other windows and drew its overlay a few seconds after the lobby data, while
  the client was switching to the menu. Treated as external interference; not
  proven (reproducing it would need that tool again).
- Reproduced and fixed a real launcher race: a new session started while the
  previous client or server was still exiting quits at once (single-instance
  game, `Client exited: 0x1`) or refused on the busy port. `play` now waits up
  to 60 s for the previous client/launcher and 30 s for the port, and retries
  the client once if it exits before reaching TLS. Verified: force-closing a
  session and immediately starting another reaches the menu.
- Probe/launcher gain `--lobby-initial-delay` / `--initial-delay` (default 0) to
  defer the initial data; not needed for reliability (baseline is 0).
  19 probe tests pass.

## 2026-10-13 — Career Profile answered (22206 -> 20807)

- 22206 (protocol 0x75d32ae2, sent by 0x00773f00 from UI code) is "view a
  player's profile": {target player id, related id, i32}; it records the target
  in component slot 50 (+0x68). The only server-to-client handler that fills
  that component is 20807 (profile protocol 0x1a9879a4, handler 0x00779280):
  {player id, compressed flag, inline profile record (0x188 B), blob}. With the
  flag false the inline record goes to 0x00ba48a0, keyed by record +0x100; the
  display name comes from the 20502 player record.
- Codec gains blob fields (kind 15: u32 length + bytes, native writer 0x005668e0)
  and f32/f64 (kinds 10/11); the schema exporter accepts kind 15. Exported the
  numeric 22206 and 20807 descriptors (no payloads).
- lobby_service answers 22206 after login with a 20807 carrying only the
  requested id (outer and record +0x100), flag false and every list, counter,
  string and blob empty: no stats or progress are invented.
- Live (play Mercy): after the request the original Career Profile shows
  OVERVIEW / STATISTICS / ACHIEVEMENTS / PLAYER ICON, the default player icon,
  "MERCY", "0 / 0" and "CAREER PROFILE IS EMPTY" — the correct state for a new
  account. 21 probe tests pass.

## 2026-10-13 — party of one unlocks Quick Play, Game Browser and Training

- With no party state the client locked Quick Play and Game Browser ("ONLY
  AVAILABLE TO THE GROUP LEADER") and greyed out TRAINING. Zeroing the third
  20500 identity did not change this (ruled out).
- Party state is 20700 (protocol 0x2411de56, handler 0x008529a0 -> component
  slot 20, record copied at +0x18 by 0x00e1f0d0; party id at record +0x60).
  The client's own party printer (0x008511b2: "BattleTag, ID, Status, Leader")
  gives the member layout: player block (+0x40 battle tag), status +0xe0
  (5 = Member; 0x00e1ef80 counts statuses 5-7) and Leader flag +0xe2.
- New initial-data option `full` (now the launcher default) adds a party of one:
  our player as the only member, status Member, Leader true, party id = the
  game account; every other field empty. Exported the numeric 20700 layout.
- Codec fix: omitted fixed-size arrays now encode as zero items (a fixed u64[2]
  in 20700 previously raised "compact array size/type" and dropped the lobby).
- Live (play Mercy): Quick Play and Game Browser unlocked, a MERCY party card
  appears, TRAINING is enabled and opens TUTORIAL / PRACTICE RANGE / PRACTICE
  VS. AI. The party card shows "-75% XP / 0 MATCHES REMAINING" (likely a
  zeroed penalty field; not yet investigated).
- Clicking PRACTICE RANGE sends 24000 (8 B) on protocol 0xa6e53896
  (24000-24028, client-to-server game queue); the screen waits. Answering it is
  the matchmaking / game-server track. 22 probe tests pass.

## 2026-10-13 — game-queue requests decoded (Training)

- 24000 (protocol 0xa6e53896, client game queue; built by 0x004cf1e0, sent from
  the queue routine 0x006ceab0 in the module that also holds the 23300-family
  handlers) is {i8 mode, string, i32}. Live: Practice Range sends
  {mode 2, "", 4} and the client shows "ENTERING PRACTICE RANGE" (spinner +
  BACK) while it waits; Tutorial sends {mode 3, "", 4}; Practice vs. AI first
  opens an Easy/Medium/Hard picker without a request.
- The server now logs decoded fields of known client requests it does not
  answer yet (`lobby request (not answered): ...`). Exported the 24000 layout;
  the schema loader bounds grow to 256 KiB / 4096 fields for the larger
  party/profile layouts.
- Reply side: server-to-client family 23300 (0x21286b49, 34 messages) has
  several repeated groups of 6-7 message layouts (likely one per queue/game
  type) plus large records (23304, 23320). Which message advances "entering"
  to joining a game is not yet identified.

## 2026-10-13 — path from queue reply to game-server session (static map)

- 23300 family (server-to-client queue, dispatcher 0x007a8ad0): ten standalone
  messages (23300-23303, 23310, 23311, 23318, 23319, 23332, 23333) and four
  parallel groups of six forwarded to queue sub-objects at +0x10 (23304-23309),
  +0x38 (23312-23317), +0x60 (23320-23325) and +0x88 (23326-23331); each group
  has the same shapes (large record, two bool messages, two-i32 message, big
  multi-struct record, string message). 23318 only formats a localized notice.
  No handler calls the game join directly.
- Game-server session: a session class (vtable 0x02677cd8, ctor 0x00e3bcb0)
  whose Connect (0x00e3d9b0) parses host:port from the object (+0x48) and opens
  a gateway connection (0x0056b430 -> 0x00563a50), logging "Connecting to %s";
  related logs "Session loaded.", "Received header.", "Pause set to %s".
  Created by 0x00e3ca60 ("Failed to open/start %s"), called from 0x00828580,
  whose callers include the queue module's pending-game consumer
  (~0x006d30d4, "Consuming pending tournament game %s", obfuscated).
- Expected end-to-end path for Practice Range: 24000 -> queue reply stores a
  pending game (address + credentials) -> 0x00828580 starts the session ->
  second gateway connection to our "game server" -> game-server welcome
  (20300 family, handler reaching RequestWorld 0x00b4b1c0) -> map load.
  Not yet identified: which queue message carries the pending game and its
  fields; the game-server gateway handshake and peer group.

## 2026-10-13 — plain instance-referral job after Practice Range

- Continued from the current main-menu/Training commits and preserved the
  unfinished queue-reply experiment. Exported all 34 numeric queue layouts
  (3086 fields, compact JSON within existing 256 KiB/4096-field bounds); schema
  message-count limit is now 64. No payloads or native code are exported.
- Queue controls now require explicit layouts/protocol registration, decode the
  whole 24000 request, reject malformed bodies and restrict experiments to the
  observed Training shapes. Default local-account play behavior is unchanged.
- Traced 20600's dispatcher -> 0x775cd0 -> 0xe3e940 -> 0xe1e6f0. Its outer bool
  false selects a plain record; host/port go through the original formatter and
  parser. Added an explicit loopback-only instance-referral profile with locally
  generated session inputs. Unverified field meanings stay documented.
- Live private prototype (referral-plain3) and public code (instance-public1):
  Computer Use screenshots/input show the main menu and Training, then
  ENTERING PRACTICE RANGE; request 24000 is answered with 20600 (242 B). A
  guarded read-only check immediately observes a slot-120 referral job. Later
  snapshots show no job: the native consumer can copy and clear it. This is
  handler/job acceptance, not a verified complete matchmaking sequence.
- No additional TCP connection observed; final public dump has zero queue
  records, world WAITING and no pending world request. Game transport, map load
  and controllable hero remain unresolved. A default-menu 3D backdrop is also
  still absent. Added queue/job count and boolean diagnostics without exporting
  identities, session inputs or proprietary bytes.
- Two intervening launches failed before application traffic in guarded TLS
  setup; neither tested the referral reply. The 1090-byte mapped CA / 15-second
  TLS delay succeeded in the subsequent bounded runs. The initial seed0 scratch
  had mismatched transform signaling and is not counted as a rejection control.
- All 14 CTest targets pass (24 probe fixtures), including every exported queue
  layout's empty-body roundtrip, malformed Training requests, experiment scope,
  fixed endpoint/session-input generation and read-only diagnostic guards.

## 2026-10-13 — original-client UDP instance traffic reaches private observer

- Corrected a referral field interpretation: nested +0x6e is parsed as
  IPv4:port by ConnectToInstance, not a token. Both address forms now target
  our own loopback endpoint. Traced the original transport selector to its
  datagram path without overriding native state or verification.
- Added explicit bounded UDP forwarding through the existing restricted pipe
  alongside TCP. Fixed loopback destination, one source port, 4096-byte bound,
  packet boundary preservation and shutdown; no network capabilities granted.
- Native instance-udp1 reaches menu/Training via Computer Use and answers
  Practice request 24000 with corrected 20600. Observer receives 39 packets of
  34 bytes; bridge independently reports outbound 39/inbound 0. No replies sent.
  The entering overlay clears back to Training after the attempt; final world
  WAITING/no request. Handshake reply, authenticated instance, map and hero
  remain pending. The older expected second-TCP-session path is a hypothesis,
  superseded for this observed instance attempt by actual UDP evidence.
- Added a receive-only size/count observer and native boundary/source/size/frame
  regression tests. All 16 CTest targets pass, including isolation and ACL tests.
  Original client hash/signature and baseline ACLs unchanged; owned processes
  and diagnostic listeners stopped. No client bytes or local secrets published.

## 2026-10-13 — instance datagram format and authentication identified

- Rebuilt the native launcher (the cached binary predated `--udp-forward`).
  UDP diagnostics are limited to 180-second runs. A lost first run showed
  "time out communicating with Battle.net" after I brought the game window to
  the front during login; the desktop was unlocked. Leave the window alone
  until the menu.
- Private hex capture (ignored `.local/`) of the original client's 34-byte
  instance packets, plus a wrapper that records the probe's locally generated
  20600 inputs. Offline: AES-256-GCM, key = referral +0xae, nonce = 8 zero
  bytes || u32 LE sequence, 22-byte plaintext header as AAD, tag truncated to
  12 bytes at the front. Header fields come from builder 0x003f96d0; see
  BGS_PROTOCOL.md "Instance datagram format". All packets regenerate exactly.
- A mid-send full dump of our own client (outside Git) shows two live AEAD
  codec objects (vft 0x025f5bd0) at peer +0x10/+0x18. Peer +0x20 is the
  127.0.0.1:1119 endpoint; +0xa4 is the sequence.
- First reply experiment (`udpreply6`): 39 sealed version-2 replies with key
  +0xce, types 1..15, were delivered by the bridge but changed nothing.
  The server-direction expectations are still unknown. No handshake, map or
  hero is claimed. All 16 CTest targets pass; owned clients and listeners
  were stopped.

## 2026-10-13 — scrambled key reconstruction and native instance handshake progress

- Continued the user's requested disassembly in the project directory,
  preserving Claude's unfinished notes. Aligned branch targets and chained
  unwind fragments recover the local five-qword nonce-prefix/key representation.
  Both objects match our generated referral inputs; both nonce prefixes are zero.
  Private inverse checks pass 4144 cases; two 40-byte blocks re-encode exactly.
  Corrected peer roles: +0x10 send/+0xae, +0x18 receive/+0xce. No decoder,
  native bytes or keys are published.
- Traced authenticated receive -> pending packet list -> handshake processing.
  State 1 requires `(flags & 3) == 3`; previous flags-1 replies cannot advance.
  +0x140 is a received-sequence bitmap; +0xa8 is received sequence +1.
  The original transitions remain enabled and unmodified.
- Native udpflags7 uses own-key type-0/flags-3 replies. Direct Computer Use shows
  ENTERING GAME after Practice Range. The client acknowledges replies and sends
  nonempty type-1 payloads. Bridge totals 161 outbound/100 inbound; every packet
  authenticates and regenerates with the new independent public envelope codec.
  Payload sizes 13..123 do not match the complete lobby bootstrap/framing.
- Responder bounded to 180 seconds/max 100 replies, no application payload replies.
  Final world WAITING/no request, zero queues and no referral job. Map, hero and
  a complete instance application session remain unresolved. Cleanup verifies
  original hash/signature, both baseline ACLs and no owned processes/listeners.
- Rebuilt native targets and all 17 CTest targets pass. Six new author-written
  codec fixtures cover layout, payloads, all-byte authentication, wrong key/nonce,
  truncation/bounds and authenticated unsupported headers. Private captures,
  dumps and key reconstruction stay outside Git. Next is reliable-message framing.

## 2026-10-13 — native receipts and bitstream callback identified

- Traced forward-only receipt semantics and added an independent bounded
  ReceiptWindow. Bit0 acknowledges next-sequence-1; sequence wrap is rejected
  in diagnostics to prevent nonce reuse. Added gap/duplicate/window-bound tests.
- Native udpack8 sends next-sequence/receipt bitmap, connect flags 3 and later
  flags 2. All 224 captured client packets/224 replies authenticate and match
  receipt semantics. Payload sizes settle at 13/33 bytes in the captured interval,
  compared with 13..123 previously. Multiple header fields changed together;
  this is not a single-field causal control or complete application session.
- Computer Use sees ENTERING GAME and later Training. Observer 180-second bound
  ends before client 150-second bound; bridge 225 out/224 in. Final world WAITING,
  no request/map/hero. Client hash/signature and saved ACLs match; cleanup complete.
- Active transport has seven modules; event 4 reaches0x7ce110. It reads LSB-first
  compact integers and module prefixes before a seven-bit message count. Added
  independent bit primitives with written bytes, selector/truncation/bit-bound
  tests. All 138/149 nonempty native bodies' first compact fields regenerate
  exactly; reliable blocks/message contents are not yet fully decoded.
- Rebuilt native targets; all 18 CTest targets pass (8 envelope/window fixtures,
  4 bitstream fixtures). Previous 8540434 CI passed. Public changes contain own
  code and semantic notes only; native code, captures and generated keys private.

## 2026-10-13 — reliable records, game-server welcome, first world request

- Verified Codex's public client reliable-record codec (21610/21627 on common
  channel 1): exact roundtrip of all 138/149 captured bodies; all 19 CTest
  targets pass.
- Mapped the server-to-client body layout (frame, six module prefixes, entity
  count) and the instance's 11 reliable channels. Channel 0 is the 20300
  game-server family; 20300's handler checks quanta 16000 / hot-reload false and
  issues a world request from message +0x4a8.
- Private runs udpapp10..14: default 20300 accepted (client sends 21600 join);
  +0x4a8 = Practice Range header GUID yields the first pending world request in
  both world managers. Still WAITING / ENTERING GAME; pongs, continuous frames
  and an empty local Hotfix directory changed nothing. No map, hero or gameplay.
- UI driven by private window capture + coordinate clicks; Computer Use was
  masked for the bounded client and its open_application started a stray
  unbounded client (killed after ~20 s). Each run: client exited, listeners
  stopped, original EXE hash unchanged.

## 2026-10-14 — pending world requests wait for a resource load

- Continued from Claude's latest project files and saved udpapp10/11/21 runs.
  Followed aligned opaque-branch targets in the original world tick to its
  WAITING handler. This handler checks resource availability, then polls the
  map-header load state: <2 waits, 3 advances to ABANDONING SCENES, other >=2
  statuses take an error path. A pending request alone does not initiate a load.
- New independent read-only resource diagnostic reproduces catalogue presence
  versus load-cache presence/status. udpapp11/21 have valid pending Practice
  requests and catalogue entries, but no header load-cache object (status 0).
  Both dumps have 28 other resource-cache entries. udpapp21's optional mode
  resource is likewise available but unrequested. udpapp10 has no pending world.
  Private arithmetic interpretation independently checks the resource hash;
  native tables, pointers and payloads remain private.
- Added observed 21600 client-join numeric schema and boolean-padding handling.
  All 1003 authenticated nonempty client bodies from those three welcome runs
  decode/re-encode exactly, including 3 joins, 974 21610s and 26 21627s.
- Native targets build and all 20 CTest targets pass. New synthetic fixtures
  check resource absence versus load states 0..3, hash collisions, malformed
  chains/counts/memory, profile validation and report omissions. No new native
  game launch or map/hero success is claimed. Next: original header preloading
  path during private application negotiation, before further settings sweeps.

## 2026-10-14 — metadata accepted; acquisition exhausts retries

- Continued in the project directory. Native udpmeta24/25/26 runs were bounded
  to 150 seconds with loopback-only TCP/UDP bridges. Explicit reuse of Claude's
  original client cache made Computer Use capture/input work. Drove the tutorial
  dismissal, Training and Practice ourselves. The map did not load.
- Traced 20318 to original handler 0x7d8010 and registration 0x684310. The gate
  at +0x98 is format 1, not client build 104319. Published numeric fields only,
  with written-message fixtures and a bounded read-only metadata reader.
- Empty diagnostic registration creates one entry. Saved udpmeta22/24/25/26
  all end with flags 0xa0, ten acquisition attempts and no current context.
  Creating the owned Hotfix directory, then granting only its own package SID
  modify access, did not fix this. No speculative storage option was shipped.
- Native tracing corrected private field interpretations: +0x80 is a retry
  deadline and +0x88 counts completed acquisitions. The apparent intermediate
  marker 7 was seven attempts, not processing success. Kind-14 acquisition is
  separate from kind-13 local enumeration. Six live-referenced completed
  requests in udpmeta26 all return 3/2/-3; native -3 means "failed to open".
  The underlying file-provider error and valid content descriptor remain open.
- Final udpmeta26 still has pending WAITING world requests and no header/mode
  load-cache object (raw state 0), despite catalogue entries and 29 other loads.
  Exact scoped ACLs were restored, owned processes/listeners/profile removed,
  and original EXE hash/signature retained. Native targets build; 21/21 CTest
  targets pass. Earlier checkpoint 041c327 also passed public Windows CI.

## 2026-10-14 — active content context recovered from saved runs

- Recovered the newer private 27/28/29 artifacts. Direct owned Hotfix writes
  succeed despite denied ancestor attribute checks; the private alias experiment
  changes four observed kind-14 failures to 9/2/6 but does not produce content.
- Original update tracing corrects the diagnostic slot names: +0x1a0 is staged,
  +0x198 active. The default identifier completes processing without setting
  its content-ready flag. Saved 26/28/29 contain an active default kind-1 context
  with zero records. Earlier staged-slot absence did not prove no active context.
- Extended the independent read-only metadata reader with bounded active/staged
  context identities and retained initialization request completion/error state.
  Kept current_context_present as the legacy staged-presence alias. No native
  addresses, identifiers, descriptors or memory bytes are exported.
- Eight synthetic metadata fixtures cover promotion observations, uninitialized
  error omission and malformed native identities/references/counts. Native build
  and all 21 CTest targets pass. No new native game run; Practice remains
  WAITING with an unrequested header in the latest saved dump.

## 2026-10-14 — structured resource requests and engine preload queues

- Extended the native search to the structured resource API behind the default
  wrapper. Traced its engine descriptor builder, configured/retained arrays and
  submission/withdrawal marker. Corrected the earlier +0x190 getter notation:
  the map initializer checks resource type 2, not the WAITING map-header type.
- Added --preload-state with exact engine identity, signed count/array bounds,
  aggregate map-header/submission counts and no exported GUIDs or native bytes.
  Public and private readers agree: saved udpapp11/21/udpmeta26/29 have empty
  configured/retained engine queues. This is not evidence of no earlier activity
  or proof of the missing private-server message.
- Native targets build and all 22 CTest targets pass. Four new author-written
  fixtures cover header/other-resource and submitted/unsubmitted cases,
  malformed memory/profile bounds and report omissions. No new native client
  run; map rendering and hero control remain unresolved.

## 2026-10-14 — live Practice assignment comparisons and gallery control

- Ran the original signed client through three bounded Practice attempts and
  two Hero Gallery controls. Header assignment, extra header/mode resources and
  map-root assignment all remain on ENTERING GAME. The root comparison has only
  about 20 seconds after selection; no stronger duration claim is supported.
- Confirmed the extra resource list in both native pending world requests,
  correcting a private prototype's settings-array offset. The public read-only
  world diagnostic now validates/counts that array. Received resources are not
  evidence that the native loader submitted them.
- Approximately 100-ms live observations show empty engine preload queues and
  no header cache entry, consistent with final dumps. Practice activates a
  default context without 20318. Gallery remains empty after all visible filters
  are enabled, leaving roster initialization and hero rendering unverified.
- Original executable/hash/signature and scoped ACLs are preserved. Generated
  credentials, captures, dumps and experiments remain in ignored private storage.
- All 22 CTest targets pass after live exit, including six resource-state fixtures
  and native launcher isolation. No playable-map milestone is advanced.

## 2026-10-14 — private-session preload reaches Practice loading screen

- Added an explicit bounded native header control after an exact original
  Practice request. One original-loader call, retained native reference,
  registered unwind and complete primary-thread context restore; no world-state
  or readiness writes and no extra ticks. Default launcher behavior is unchanged.
- Two live controls reach header/mode raw load state 3 and both managers WORLD
  LOADING. The repeat visibly shows the Practice Range loading screen and stays
  there. No gameplay scene, hero selection or controllable hero is established.
- Added aggregate read-only resource-cache states. Earlier Practice/gallery
  snapshots contain 28 completed objects; the controls end with 29 completed
  objects but no map-root cache entry. Ordinary header initiation and downstream
  world/scene initialization remain unresolved.
- Repeated the map-root-only assignment with earlier selection: still WAITING.
  Native build, eight resource fixtures and all 22 CTest targets pass. Live
  cleanup preserves original hash/signature and exact saved scoped ACLs.

## 2026-10-14 — corrected loading dispatch and scene readiness

- Corrected a native-trace stage error: WORLD LOADING (6) dispatches to a
  different handler from WORLD LOADED (7), which the earlier notes followed.
- Added guarded read-only scene-state reporting with the saved client PID as
  an operand of the original owner getter. Both existing loading-screen dumps
  show all three resource groups complete, scene readiness false, and absent
  active/pending scene handles. No pointers, PIDs, identifiers or bytes exported.
- Traced the original readiness setter to scene state 5 plus its completion
  predicate. Scene construction is the next investigation; missing handles
  alone do not establish why construction failed or was not invoked.
- A new bounded live attempt authenticated but Windows activation failed with
  Access denied and a black capture. No Practice selection/control was performed.
  Read-only observers had 1020/1013 valid samples and zero rejects; all owned
  process, original hash/signature and exact ACL cleanup checks pass.
- Native build and all 23 CTest targets pass, including new synthetic scene
  readiness, signed resource-state, wrong-PID/profile and malformed-array checks.

## 2026-10-14 — live scene construction with the typed Practice map

- Recovered working game input and completed two bounded Practice selections.
  Baseline header assignment reproduces complete resources with no scene object.
  Both runs visibly remain on the original Practice loading screen.
- The loaded header references a typed map variant different from the earlier
  unflagged root. Supplying that exact reference in the experimental welcome
  constructs pending scene objects in both managers. Extended the existing
  opt-in header control's exact Practice identity guard for this comparison.
- Both scene controllers remain at raw state 1, while the readiness setter
  requires state 5. Their two completion resources are already raw state 3.
  Added guarded aggregate scene-progress reporting and synthetic fixtures.
- All original image/signature and exact scoped ACL cleanup checks pass.
  Geometry, hero selection and gameplay remain unverified. The normal header
  trigger and subsequent scene-state transition remain open.

## 2026-10-14 — canonical map completes scene loading

- Traced the state-1 stall to a valid typed asset reference that remains pending
  without an asset object. The scene is ticking; completed raw-resource reads
  alone do not complete the typed asset.
- Compared the canonical Practice map with the referenced variant under the
  same opt-in header preload. The canonical assignment completes the typed
  asset and scene loading. The final original-client dump has WORLD LOADED and
  WORLD REPLICATING managers, both with active, ready scenes and state-5 controllers.
- Extended read-only diagnostics with typed status, load progress and update
  count, including loaded/replicating snapshots. The native control remains
  restricted to exact Practice assignments in bounded own-key loopback sessions.
- The UI still shows the loading screen. Replication initialization and gameplay
  remain unverified; ordinary header initiation remains unresolved.
- Native build and all 23 CTest targets pass. Original hash/signature, exact ACLs
  and owned process/listener cleanup checks pass.

## 2026-10-14 — selected entity validity and generation

- Traced the original world update's selected-entity gate and the normal 20302
  notification setter. Baseline canonical43 has unset IDs in both world owners.
- Run select44 assigns index 1, clearing the validity gate, but the full ID does
  not match the existing native entity's generation. Run generation46 supplies
  the matching packed ID and resolves a native entity object. Both remain at
  WORLD REPLICATING; this is not a replicated player or gameplay milestone.
- Added bounded read-only `--replication-state` reporting for validity, bucket
  count, record/object presence and generation mismatch. Exact profile/getter
  guards, truncated data, malformed pointers/counts and changing selection are
  covered by five synthetic fixtures. Reports omit IDs, pointers and payloads.
- Delaying the valid notification by 30 seconds also leaves four pending entries
  and WORLD REPLICATING, with the completion marker false instead of true.
  Late observers miss notification delivery, so this does not prove why the
  marker differs. Extended the guarded snapshot to these queue counts/marker.
- Native build and all 24 CTest targets pass. Completed run cleanup retains
  original hash/signature and exact scoped ACLs, and ends owned helpers.

## 2026-10-14 — map placeables replicate; world reaches WORLD_RUNNING

- Traced the four zero-dependency pending replication rows: they are map
  placeables with networked components (types 0x5e/0x3a), removed only by an
  entity create naming the placeable. Decoded the server entity section,
  module-4 create/update framing and the placeable create path.
- Extended the private responder with opt-in minimal placeable creates. Two
  framing errors (module-5 prefix, module-2 empty form) were found from the
  client's per-module consumed-bit counters and fixed.
- Bounded runs livecreate54/55: after the 20302 selection resolves, the client
  processes the queued creates, clears all pending rows and advances the
  submitted world to GAME MODE LOADING and WORLD_RUNNING, with four class-0b100
  entities. A new read-only ~10 ms sampler recorded the transition. The UI
  stays on the Practice loading screen; no player entity or gameplay is shown.
- Claude's launcher binary predated `--preload-practice-header`; rebuilt with
  Build.ps1 -SkipDependencies, all 24 CTest targets pass. Every run's cleanup
  (owned processes/listeners, exact ACLs, original hash and signature) passed.

## 2026-10-14 — verified placeable codec and visible Practice geometry

- Resumed Claude's map-placeable work. Saved run55 and liveverify58 confirm
  WORLD_RUNNING with no queued/pending records and completion marker set.
- Added a bounded independent placeable entity-section codec and four synthetic
  fixtures for exact framing, identifier widths, alignment, truncation, unsupported
  module forms and bounds. Across runs55/58/59/60, all 2079 captured sections
  re-encode exactly, including 1481 create records.
- Migrated the private responder to the reusable codec. Livecodec59 visibly
  renders Practice geometry after loading. Livecamera60 reproduces that view;
  Escape opens/closes the in-game menu. No hero HUD or weapon is present; short
  W, mouse-drag and H checks establish no movement, camera control or hero picker.
- Extended the existing guarded scene snapshot to game-mode-loading/running
  states, without equating the native state with playable gameplay.
- Native build and all 25 CTest targets pass. Normal header initiation and
  local-player/hero replication remain unresolved. All live cleanup audits pass;
  raw captures remain private.

## 2026-10-14 — first-person prerequisite and timing-field control

- Traced the first-person timing reader to a selected-entity lookup followed by
  component 44. The current diagnostic selected entity lacks that component;
  resolving its entity-table entry does not establish a controlled actor.
- Extended the guarded read-only replication snapshot with native-ID agreement
  and component-presence booleans. Six synthetic fixtures cover absent/present
  components, identity mismatch, truncated memory, changed masks and profiles.
- Bounded livetime62 enables the existing optional 16-bit timing field. Practice
  geometry visibly renders again, without a hero HUD or weapon. The client stores
  49.085 seconds in the traced native field, while both controlled-actor markers
  remain invalid. This verifies receipt and scaling, not full clock synchronization.
- The new and prior livecamera60 snapshots both report the missing component.
  Run62 reaches WORLD_RUNNING with no queued/pending records, ready scenes and
  complete resource groups. All 433 captured entity sections re-encode exactly,
  including 366 create records. All 25 CTest targets and cleanup checks pass.
  Hero creation, selection, movement and combat remain unresolved.

## 2026-10-14 — definition entity created and selected

- A full 4096-bucket census of both run62 worlds finds 1019/1020 matching native
  entity IDs and no component-44 candidate. Component 44's native actor getter
  reads a separate entity ID, so an existing map object cannot fill that role.
- Hash-verified a 272-byte definition from the final-retail installation, using
  the old controller resource as a research lead. The serialized root agrees with
  the [pinned OWLib entity-definition schema](https://github.com/overtools/OWLib/blob/df522f0ceea8748dcb51463ceb990234ceb45c9a/TankLib/STU/Types/STUEntityDefinition.cs).
  Its four serialized components map to native types 29/47/73/76. Runtime
  components must be established separately; serialized presence is insufficient.
- Livedefresource63 puts that definition in the experimental welcome list. The
  client remains at HOTFIXING with the loading overlay; metadata is not ready,
  and the final snapshot is tearing down. This does not verify generic resource
  preloading. All 522 entity sections re-encode exactly; cleanup checks pass.
- Corrected the private cache inspection to include the native fallback cache:
  run62 already has the definition's typed object ready (status 4), despite no
  raw catalogue/cache entry. Raw-cache absence is not definition-load failure.
- Livedefcreate64 uses the baseline welcome and a minimal non-placeable create
  with neutral transform flags and no network component state. The original
  engine constructs the new entity, including components 44, 25/26 and 84/85.
  The complete running-world census is now 1021 entities with one component-44
  candidate. Practice geometry still visibly renders.
- Livedefselect65 selects that entity through a later sequenced 20302 message.
  The guarded report confirms native-ID agreement, component 44 present, running
  world and ready scenes. Its component-44 actor target remains invalid. H shows
  no hero picker/HUD; the subsequent W attempt happens after process exit and
  establishes no input result. A controllable hero remains unverified.
- Extended the reusable codec with strict minimal definition creates and two
  new synthetic fixtures; placeable-only APIs remain strict. Across runs64/65,
  all 1332 entity sections re-encode exactly, including 160 definition creates.
  Private actor-link inspection validates the decoded component's world owner.
  All three live cleanup audits pass. Hero creation and actor-link state are the
  next protocol investigation; no native state fields were written for these tests.

- All 25 CTest targets pass after the codec extension and completed live cleanup.

## 2026-10-14 — hero definition preload through 20505

- Liveherodef68/69/70 add a minimal create for Soldier: 76's gameplay entity
  definition (from the offline hero-record mapping) and select it. The world
  runs and geometry renders, then the client leaves: repeated lobby 21801/21802
  pairs, Battle.net keepalives stop, instance header flag 4, and the UI returns
  to Training. Run 65's controller-only create never does this.
- Traced the sends to abort routine 0xb64af0 (21801 then 21802, plus a
  Battle.net session notification). A triggered mid-run dump (run 70) shows the
  decoded labels "Mirroring mismatch." and "Missing entity definition" in use,
  naming the hero definition. The create path only looks up the typed cache;
  129 type-3 definitions are resident, but no hero gameplay definitions.
- 20505 list 0 is the original hero preload input: 0x77a000 -> 0x57bba0 ->
  0x57c700 fills the content provider's Hero (0x75) set. Added opt-in
  `--lobby-hero-list` (type-0x75 only) and an independent wire fixture.
- Liveherolist71 sends Soldier: 76's hero record in that list. No abort,
  keepalives continue, and the world stays WORLD_RUNNING with the hero entity
  selected. The final dump has 150 resident definitions, including the hero's,
  and a 28-component hero entity. The window shows a large armored boot
  model at the camera position. No HUD/first-person/control is claimed. Component
  44's actor link on the controller entity remains the next gate.
- All cleanup audits pass (hash, Valid signature, exact ACLs, owned processes).

## 2026-10-14 — controller actor link through component state

- Traced the create payload's component count into update body 0x78e5d0 and
  network visitor 0x78b870: absolute-body byte alignment, u8 mask length, presence
  mask, then raw field values. Kinds are CRC32 names; component 44's state holds
  three teEntityID fields, and its actor getter uses the second (state +0x7c).
- The client's own local-game path writes all three fields to the same entity.
  Public `DefinitionCreate(controlled_actor=...)` encodes that block. A new
  known-vector test covers all 16 alignments, mixed sections, rejection and
  truncation.
- Livecontrol72: controller created with Soldier: 76 as controlled actor, selected
  through 20302. Final dump: actor target valid and resolving, WORLD_RUNNING, no
  abort. Livecontrol73 adds the module-3 time field. Receiver 0x7c7800 then records
  a valid controlled-actor marker. The view is unchanged (fixed default camera);
  first-person, HUD and input remain unverified.
- Runs 71/72/73 entity sections re-encode exactly with the public codec at their
  body offsets (723/717/717 sections; 66 actor creates in 72 and 73). All cleanup audits pass.

## 2026-10-14 — camera/input controls after the actor link

- Liveinput74 repeats run 73 and sends relative mouse look, W, Space, H and Tab after
  the controller is selected. No visible change (only animated clouds), and the client
  sends no new instance message types (no movement commands).
- Camera-view classes ("First Person View", spectator views) are registered through
  descriptor tables; their shared predicate 0x699730 reads a user-settings flag, not
  gameplay state. The local-game setup 0x82a5e0 also links a component 74 (absent on
  both our entities) back to component 44; updates cannot add missing components.
- Livetransform75/76 create the hero with transform flag bit 2 (three f32 at
  +0x10) or bit 3 (+0 xyz, +0x20 quaternion, +0x10 xyz). The boot model does not move
  or scale. Control livepreloadonly77 (preload, no hero create) shows no boot, so
  the model belongs to the created hero; its rendered position evidently comes from
  other replicated state (likely module-3 per-entity movement snapshots), not the
  create transform. All four cleanup audits pass.

## 2026-10-14 — first server movement snapshots for the hero

- Wrote a flag-simulating deobfuscator (opaque jcc chains collapse when every flag
  assignment reaches one endpoint) and a bounded x86-64 interpreter over the
  static image (validated on bit reader 0x78bdb0).
- Module-3 per-entity items (0x7c2e60): presence bit, 12-bit length counting
  itself, payload queued as {entity, body offset, length}. Applier 0x7c7f50 runs
  when the selected entity is valid; per-entity decoder 0x7ca130 reads a template
  bit, needs components 28 and 43 on the entity, decodes 0xc5f680 and applies it
  to component 28 (movement) through 0x64a970.
- The interpreter runs 0xc5f680 on an all-zero input: 35 bits, every field
  unchanged from the default prior state. A minimal item is presence 1, length
  48, then 36 zero bits; the entity chain ends after module 3.
- Livesnapshot78 sends that item for the hero after the controller link. No abort;
  the boot leaves its old place and hero geometry appears elsewhere on its own
  (before any input). Later look/W frames differ, but the client sends no new
  message types, so input control is not established. Cleanup passes.

## 2026-10-14 — statescript replication applied on the controller

- Runtime component 47 is the statescript component. Module 1 carries per-entity
  statescript sync records: base frame, frame delta, optional part, size in bits,
  then a frame blob. Field readers take FourCC debug tags; enumerating their call
  sites names the command set (instances, timers, variables, messages, state
  events, arrays, resources).
- A dump-backed interpreter (synthetic TEB, seed-transform and allocator stubs)
  runs the client's module-1 reader and the statescript frame interpreter on real
  run-78 state. An empty frame is 10 blob bits; one instance creation adds a create
  bit, a graph-present bit, a 16-bit graph index and four absent optional fields.
- Livestatescript80 sends a record creating Practice graph index 0x13c0 on the
  controller (base frame 1, delta 1). The final dump shows that controller's
  statescript manager advanced to frame 2 with new bookkeeping values; the hero's
  manager is unchanged. No visible HUD/camera change and no new diagnostic labels.
  Run 79 never reached the statescript phase (resolution change cost time). Both
  cleanup audits pass.
- Livegraphs81 creates all three Practice graphs on the controller: the record stays
  pending (frame 0, one queued record). Livegraphs82 adds an opt-in 20505 list-1
  preload (`--lobby-preload-graph`, type-0x1b only); all three graphs become
  resident (status 4) but the record is still pending: the multi-instance blob was
  mis-encoded (each instance carries its own nested `Inst` count).
- Livegraphs83 fixes the encoding: about one second after the records start, the
  client exits with code 1 (fatal-error exit; no dump). Graph 0x13c0 alone (run 80)
  applies cleanly, so one of 0x0c8e/0x0c90, or running them on the controller,
  hits a client fatal path. Offline: graphs have 233/869/1782 STU instances and
  reference sub-graphs; driving them needs graph-content parsing. All cleanup
  audits pass.

## 2026-10-14 — three Practice graphs running; first statescript HUD element

- Bisected: graphs 0x0c8e (livegraph84) and 0x0c90 (livegraph85) each apply alone.
  Livegraphs86 (one graph per sequential frame) leaves frames 2/3 pending.
- Emulating the client's own processing loop on run 86's stuck records shows the
  failure: instance-table add 0xd55d30 rejects a duplicate instance ID (every
  create used ID 1). In 0xa0e1d0 the `Inst` field is an instance-ID **delta**
  (id += delta, 0 ends the list); run 83's zero after the first graph ended the
  list early and the remaining bits misparsed into a fatal exit.
- Livegraphs87 sends Inst=1/graph per instance (IDs 1..3) in one frame: the
  controller's statescript instance table holds 0x13c0, 0x0c8e and 0x0c90, the
  frame applies, the client keeps running, and a red "prohibited" HUD icon appears
  at the bottom centre. This is the first HUD element driven by our game-mode
  statescript. No hero select, first-person camera or input control yet. Cleanup
  audits pass for runs 84-87.

## 2026-10-14 — StateHero, hero graphs and first-person control

- Decoded the statescript frame body with the dump-backed emulator: blob size is
  in bits; instance-list bit 1 destroys an instance (updates are `0,0`); per-instance
  `IVDt` sync-variable masks and `StDt` state masks; full-snapshot header with
  `CmFD`/`LBSS`. Remote messages do not fire GameMessageEntry states.
- livehero89: a full snapshot sets the hero variables and activates Practice graph
  0x0c90 state 0 (`StateHero`); the dump shows it running. liveherogr90 also
  creates the nine statescript graphs listed in Soldier: 76's definition on the
  hero entity.
- Found the local-control gate: movement-command and first-person code need an
  entity with component 59, added only when a create carries flag 0x10 for the
  entity that is *already* the 20302 selection (0x00586060 vs world owner +0x298).
  livepred91 (class-101 IDs) and liveowned92 (create never sent) did not get it.
- liveowned93: diagnostic selection, then selection of the controller ID, then the
  controller create with flag 0x10 and the actor link. The original client shows a
  first-person Soldier: 76 view (hand visible), mouse-look works, and the client
  streams new packets (2354 undecoded bodies; the private responder hit its
  2000-reply bound). No health or server movement replication yet. All cleanup
  audits pass for runs 89-93.

## 2026-10-14 — movement, command acks, health; hero-select investigation

- Client module-3 input: after the empty module-0 header (9 bits), `[1][u32 bit
  length]` then `u16, u8, u8 count, u32 oldest sequence` and delta-coded commands
  (writer 0x00c2ddc0). The server module-3 compact field acknowledges commands
  (0x007cadd0 acks up to value-1); acking the newest drops unacked commands from 32
  to 2-3 per packet (liveack94).
- livenosnap95: without our per-tick "unchanged" hero snapshots the hero walks and
  strafes under client prediction. livehealth96: a health pool in the hero create's
  component-51 state (3x16 pool structs `{u32, f32 value, f32 max, enum, 4 x u8}`;
  first pool 200/200) removes the critical-health vignette.
- Weapons are statescript-driven (component 49 has no replicated state). Creating the
  definition's weapon graphs (0x15, 0x254) works; activating weapon-graph states
  11/68/69/70 in a full snapshot fatal-exits the client (liveherostates99). State 11
  is a CosmeticEntity that spawns definition 0x04000000000004bf; the 20505 list 1
  now also accepts type-3 definitions (`--lobby-preload-definition`) for that test.
- Not yet: load-in hero-select screen and spawning in the spawn room. Prometheus
  (beta build) shows hero selection as a statescript UI action that the client
  reports; retail candidates are instance messages 21605 `{u64,u64,i32}` and 21607
  `{u64,bool,bool}`. The Practice graph tree has 62 graphs, 16 with UI presenters.

## 2026-10-15 — original hero-change UI and teleports

- Creating Practice subgraph 0x288b (reached from 0x0c90 state 119 via container 0x288a)
  as a controller instance activates the original hero-change flow: H shows "You must
  be in a spawn room to change heroes" (liveui103).
- A module-3 movement snapshot carrying only the position fields teleports the hero
  (emulator-verified 140-bit form); runs 105/107/108 move the hero around the base,
  including a spawn-room-like interior. The spawn-room message persists at every
  candidate location and with the welcome's +0x78 byte set to 1, so the remaining gate
  is spawn-room ownership/team or volume membership. Map entities with component 1
  expose positions at component +0x90.

## 2026-10-15 — original hero-select screen

- The spawn-room check reads component 74's replicated state (field 6). Creating the
  controller with ownership flags 0x30 and that field set, then pressing H in the spawn
  room, opens the original "SELECT A HERO" screen; with the full 20505 hero list the
  complete 32-hero roster is offered (livespawnroom110, liveroster111b).
- Picking a hero and pressing CONTINUE sends client message 21616 (a client game
  message from the controller entity, message GUID type 0x024). Runs 109-111 cleanup
  audits pass.
- The CONTINUE press's 21616 is game message 0x1360 (one parameter, var cb7a), which
  graph 0x288b's own server-side entry consumes; the chosen hero is not in it. The
  hero-pick message (0x1361 with a hero parameter) has not been observed yet.

## 2026-10-15 — the picked hero spawns

- The hero-select graph's server half is now emulated by the private responder: the
  "open" request (0x1360) sets the global variable the client checks, the client then
  sends its pick (0x1361 with the hero GUID), and the responder creates that hero's
  gameplay entity as the player's actor in the spawn room. livepickspawn120 shows
  Tracer's first-person arms after choosing Tracer. Variable scopes, value encodings and
  the expression opcodes are in docs/BGS_PROTOCOL.md.
- Load-in now follows the original flow: the server's hero-select variables open SELECT A
  HERO automatically, CONTINUE sends the pick, the chosen hero spawns in the spawn room,
  the overlay closes and the player moves and turns as that hero (liveautoselect125).
  Weapons, abilities and HUD are the next step.

## 2026-10-15 — reload

- Pressing R as Tracer now plays the original first-person reload: the responder turns
  on the weapon script's reload stack, wait and animation states, giving the animation a
  reference to the pistol cosmetic state (without that reference nothing plays). The
  per-state data formats were confirmed in emulation before the live run
  (livereload157). Firing is paused while reloading; an optional ammo counter reloads
  automatically when empty.
- Investigated, not solved: local statescript prediction (Blink/abilities), HUD
  visibility (presenters and widgets exist, UI resources loaded, setting the player's
  team does not show it), and non-controlled entity visibility.

## 2026-10-15 — training bots render

- Found why non-player heroes were invisible: the create needs the skin. The flags byte's
  0x40 bit (with 0x01) carries a skin-theme reference; with it, a Tracer entity and the
  original white/red Practice Range training bot render in third person in the spawn room
  (liveskin162, livebot163). This unblocks practice targets; health, damage and bot
  placement in the range are next.
- Client commands now decode exactly (movement table fix), giving the real button map;
  holding fire keeps the weapon volley running, ammo drains, and the original reload
  animation plays (R or automatically when empty).

## 2026-10-15 — shooting a training bot kills it

- The server now knows where the player is (it integrates the client's movement inputs
  with calibrated axes) and where they aim, so it can tell when Tracer's shots hit a
  bot. Hits lower the bot's health through entity updates; at zero the bot is removed and
  comes back three seconds later (livekill168).

## 2026-10-15 — HUD root cause narrowed; Blink and Recall

- The panel we had been trying to show (0x106b) is the objectives element, not the hero
  HUD. UI layer resources carry readable view names, which let us find the real
  structure: the hero HUD layers hang under a native `HUD_Root` that is only created
  when a client-side UI condition (five native predicates) becomes true. That condition
  stays false in our sessions; finding what satisfies it is the next HUD step.
- Server state data can make the client send a local game message by activating a
  client-only "send message" node. That delivered 0x0717 to the HUD graphs for the
  first time (livehudmsg177).
- Shift now blinks Tracer 7.5 m and E recalls her 3 s back. The server performs these
  as teleports from its estimate of the player's position, so they work in open space.
  Without collision data they can land inside geometry.
- Three skinned training bots stand outside the spawn room on verified floor. Shooting
  kills them and they respawn; the hit test uses the server's position estimate.

## 2026-10-15 — more heroes; HUD gate found

- Weapon setups are now generated from each hero's own graphs instead of being
  hand-written for Tracer. Soldier: 76 can be picked and fires his rifle with tracers;
  McCree spawns with his revolver, but it disappears when firing (his weapon model's
  parent switch is not driven yet).
- The missing hero HUD comes down to a native "client mode" value. The in-game UI only
  starts in modes 5 or 9; our Practice Range join leaves the client in mode 6. Several
  intermediate experiments (driving the in-game UI graph directly, filling settings
  strings, changing the referral kind) did not open it.

## 2026-10-15 — changing hero works

- In the spawn room, H opens hero select. Clicking another hero now switches to that
  hero: run 193 went from Tracer to Soldier: 76, who then fired his rifle.
- The client was already able to do this. It refused because two server variables were
  wrong: the "initial pick" flag stayed set after spawning, and a hero variable that
  only one game-mode graph uses was set. Clearing the first and leaving the second unset
  fixed it.

## 2026-10-15 — revolver state encoding corrected

- Corrected two state-stream errors: several one-bit types were misclassified,
  and stopping a firing state omitted data that the client still reads. The
  resulting bit shift was what turned off McCree's revolver. In run 211 it stays
  visible after two firing cycles and the original reload animation.
- Five-minute bounded diagnostics now leave time for loading and gameplay checks.
  All 25 tests pass. The experimental ancestor flag remains outside the baseline.
- Correction to the earlier HUD note: client mode 6 is normal in-game mode; the
  mode-5/9 menu path does not establish the missing hero HUD. HUD, hero previews,
  gallery cosmetics and complete hero behavior remain open.

## 2026-10-15 — change hero as often as you like

- H in the spawn room now works again after a hero change, and every new hero gets its
  weapon. One session went Tracer → Soldier: 76 → McCree, firing with each, and
  McCree's revolver no longer disappears.
- Two server-side mistakes caused this: the replacement hero's script updates were
  numbered as if it were the old hero, so the game waited for updates that never came,
  and a hero-select flag was never cleared, which disabled the H key.

## 2026-10-15 — HUD setup packet ordering

The failed HUD experiment in run 250 skipped the packet that creates its extra
script graphs. Fixed the private responder to create those graphs before activating
their states. Native emulation of both stages now succeeds against that run's own
saved state. Run 252 keeps Tracer's weapons, firing and reload working, but still
has no HUD. The new saved state exposes an ownership mismatch: the animation
graph expects its owner to equal the selected controller, while we placed it on
the hero. That comparison is false and its presenters never start. Rebuilt
successfully with all 25 tests passing.


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
