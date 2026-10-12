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
