# Disc adapter investigation — 2026-10-11

> Historical experiment. Current development targets final OW1 1.74.0.0.104319. The old ISO is no longer available and is not a current project dependency.

The experimental 27578 profile has rendered Hanamura geometry behind the original loading overlay and reached native world state 5 with the correct loaded-map GUID. It has not spawned a controllable player or completed the gameplay/session transition. It operates inside the same network-denied AppContainer as the verified title-screen launch. Missing speech is explicitly omitted in these diagnostics; this is not a faithful complete-audio preservation.

`tools/offline-launch/disc_profile.h` records the executable fingerprint and observed world-system RVAs. `--map-probe` waits 20 seconds, checks the world initializer's instruction bytes, entity-admin vtable, bounded system list, unique world ownership, idle state and empty map fields. It writes only the Hanamura request, then monitors the world state for five minutes. The bounded diagnostic captures `map-probe.dmp` and ends its job at the deadline. It does not initialize an account or authenticated session.

| Disc location | Observed layout |
|---|---|
| Entity-admin pointer | RVA `0x15011e0` |
| Entity-admin vtable | RVA `0x12f54c8` |
| World-system vtable | RVA `0x12f4b18` |
| World initializer | RVA `0x962fc0`; writes state 2 |
| System array | Entity-admin offset `0xd8`; pointer/count/capacity |
| World ownership | World offset `0x08` |
| State / wanted map / loaded map | World offsets `0x10` / `0x18` / `0x20` |

These are separate from beta offsets and apply only to the allowlisted fingerprint. The basic probe remains in state 4 with loaded-map ID zero. Its initial logs report an empty downloader server list and request-handler creation failures. The primary experimental staging folder uses `127.0.0.1` in its CDN-host field, with a local backup of the previous `.build.info`; this removed those handler diagnostics. The fresh storage writer still emits an empty server list, and the AppContainer still denies all network access. This metadata experiment has not been promoted into the storage writer.

## Native loading experiments

| Mode | Additional behavior / observed result |
|---|---|
| `--map-probe` | Writes the native world request; stalls in state 4 |
| `--map-probe-no-speech` | Validates all 729 speech APM rows, then omits this optional table in memory. Global packages 29/66 complete; direct map dependencies still wait |
| `--map-probe-preload` | Calls native package loader `0xc13b70` for common package 79 and the requested map on the existing game thread. Resolves most pending assets; both packages still wait on the missing voice catalogue |
| `--map-probe-voice-request` | Also requests `0x07a000000000001d` through native `0x647450`. Native logs report missing manifest data and dependency failure; descriptor flags become `0x3b301`, not a fabricated success. World advances to state 5 / Hanamura GUID; geometry is visible beneath the loading overlay |
| `--map-probe-stages` | Separate experiment dispatching disc-native `0x964500` state-change callbacks in states 5/6, analogous to upstream beta behavior. It hits a native assertion before a playable transition; this mode is bounded to one minute after startup |
| `--catalogue-schema-probe` | Validates an author-written 96-byte empty catalogue through the native STU parser, checks the constructed root/empty list and stops. It does not install a replacement or demonstrate gameplay |
| `--catalogue-import-probe` | Imports a client-allocated author-written empty catalogue into the existing native descriptor, verifies the published object, then observes map loading for five minutes. This supplies no voice mappings or audio and does not claim gameplay success |

Preloading preserves volatile integer registers, flags, XMM0–5 and aligned Win64 call/shadow space, then tail-jumps to the original loader. A marker lets the helper restore the original map vtable slot once requests are submitted. The stage experiment similarly restores the world tick slot after reaching state 7. Callbacks remain allocated until the child ends, avoiding reclamation while a thread could still execute them. No remote thread, beta DLL, on-disk executable patch, rewrite of original asset bytes or forced loader-ready flag is used. The explicitly selected catalogue-import probe substitutes an author-written object in memory as described below.

The first voice-request run, before automatic callback restoration was added, reached state 5 then crashed: a call to zero from RVA `0xa384ea`. The cause is unresolved; the dependency error alone does not establish causation. A subsequent run with callback restoration visibly rendered partial Hanamura geometry. This does not establish collision, hero input, audio or match rules.

The native state-5 tick waits on world byte `0x65`, observed unset, through `0x961f80`. Native `0x964500` dispatches registered callbacks and advances 5→6 / 6→7. The upstream beta extension explicitly calls its equivalent at those stages. Disc replication/session semantics remain unverified.

The restored-callback voice-request run survived its five-minute diagnostic window in state 5 without a new native crash report. The stage experiment instead produced native assertion identifiers `3980(92)` / `3981` / `"2"`, with the crashing stack at game RVAs `0x93ecc6` / `0x93e19c`. The saved exception's R14 points at GUID `0x04000000000001fa`: Hanamura's map-definition resource. Native `0x93f220` finds no loaded object for it, following the missing-voice dependency failure. This explains why map geometry/world state can advance while the next activation step asserts. No assertion was disabled and no readiness flag was fabricated; keep this failed stage experiment out of ordinary startup usage.

## Independent asset checks

`Inspect-DiscPackages.py` reads the old English APM and package versions 1 / 20–27 through independently built [CascLib](https://github.com/ladislav-zezula/CascLib/tree/38a34665624b8775bb875274b36191b21c38d97b), checks bounds, decodes bounded gzip record lists and follows package IDs. Its format definitions were identified from local captures and CascLib's MIT-licensed declarations. The package's dependency tail is an array of **32-bit package IDs**, not a content key. Bundled assets are slices of the package content block. Loose assets have separate content keys. The tool never extracts files or enables online access.

`--verify-assets` checks every asset's size and MD5, including each bundled slice. Hanamura passed across five packages and **8,257 package-record entries**. Practice Range passed across six packages and **11,270 entries**. Counts include records repeated across packages. These results establish local readability and integrity for those graphs, not native rendering or full-client completeness.

Global package 29's base graph passed across 1,270 packages / 178,957 record entries. Adding English localized variants expanded this to 2,507 packages / 282,709 entries and reported **10,293 unavailable entries**; these are not unique-file counts. Hanamura's own localized graph passed across eight packages. Native imported resources reference dependencies beyond these declared graphs, including common package 79.

Two confirmed absent English speech records are the global-29 bundle (CKey `efe5405f73d9ebbd8484c8fb2e8754a7`, EKey `8f7728672c364deba643119a458709bb`) and the loose 46,208-byte voice catalogue `0x07a000000000001d` (CKey `80c124710acc8a1aacb282d895631909`, EKey `8d1a43b1873eb94b531906061c34124b`). The encoding manifest lists their encoded keys, but neither is in the 64,883-record ISO index. Tested public CDN paths returned no copy. No replacement bundle or invented asset was written.

```powershell
$buildRoot = Join-Path $env:LOCALAPPDATA 'OW1-preservation-build'
$client = Join-Path $buildRoot 'clients\1.0.1.27578'
python scripts/Inspect-DiscPackages.py $client --casclib "$buildRoot\casclib\Release\CascLib.dll" --verify-assets
python scripts/Inspect-DiscPackages.py $client --casclib "$buildRoot\casclib\Release\CascLib.dll" --map 08000000000000d4 --verify-assets
& "$buildRoot\relay\tools\offline-launch\Release\ow1-offline-launch.exe" "$client\Overwatch.exe" --map-probe
# Stronger experimental probe; loading overlay and gameplay remain unresolved:
& "$buildRoot\relay\tools\offline-launch\Release\ow1-offline-launch.exe" "$client\Overwatch.exe" --map-probe-voice-request
# Check English text/speech variants as well as base packages:
python scripts/Inspect-DiscPackages.py $client --casclib "$buildRoot\casclib\Release\CascLib.dll" --include-localized --verify-assets
```

Next work: integrate the empty catalogue with the native importer/storage, or trace optional voice-reference handling, so the unavailable original does not invalidate the map-definition object; retain explicit missing-audio status. A complete authorized catalogue would permit the original behavior. Then verify the stage callbacks and initialize a local controller, camera and hero with native resource/component guards. Menu/session handling and authentic multiplayer remain separate work. Do not apply the beta DLL or patcher to this build. Dumps, logs, game files and recovered payload must remain outside Git.

Update: native memory import now publishes the empty catalogue successfully. Next work is the remaining common-package loading queue and verification of the real map-definition object before any world-stage advancement. The missing-original-data status remains explicit.

## Catalogue recovery and replacement investigation — 2026-10-12

`scripts/Audit-DiscResource.py` independently decodes and content-hash checks the original EN manifest, verifies all 1,787 content-key page hashes, parses 191,194 entries and checks every encoding declared for the target CKey against the hash-checked ISO index. The catalogue has one declared EKey and none is indexed. This establishes absence of its declared encoded file in this disc's index.

The same offline audit checks both original English APM hashes and searches all 5,034 declared package rows. Of 4,035 distinct metadata keys, 3,988 are readable, hash-verified and parsed; 47 are unreadable. Its only matching record is the unavailable loose file in English speech package `0x06e0100000000079`. No exact available bundled/loose duplicate was found. This does not prove absence from unreadable metadata, arbitrary unindexed bytes or external backups.

Eighteen HTTPS asset URLs across six hosts and `tpr/odin`, `tpr/ovw`, `tpr/pro` paths returned no payload: mostly 404, one 418 and certificate errors on the Korean host. Certificate validation was retained. A filename-only check of 190 local Steam/Battle.net cache files found no matching CKey/EKey filename; it was not a scan of every current-game archive. The original 46,208 bytes cannot be reconstructed from their hash and size alone.

Other owned disc resources exposed the old VoiceSet root schema. Encoded GUID type `0x7a` maps to native type `0x5f`; these are immutable STU v3 resources, not the modern OWLib format. The new `silent_catalogue.h` contains an author-written empty root, layout and schema identifiers, with no original voice mappings or audio. The client successfully parsed it via guarded RVA `0x447970`, producing root vtable `0x11c0f60` and an empty entry list. The schema probe registers Win64 unwind metadata for its callback through a checked child `RtlAddFunctionTable` export; code and metadata remain allocated until process exit. Earlier unregistered-callback attempts crashed, including a direct creation attempt at `0x647110`; their exact failure sites were not captured and should not be attributed to a closed creation gate.

In the schema-only probe, the original catalogue descriptor retains flags `0x3b301` and object pointer zero; that probe does not register the candidate. Exit zero validates its structure, not game/session success. The separate memory-import milestone below publishes a candidate, but a repeatable map-definition load remains necessary to verify its effect on map loading. Neither probe forces completion flags or changes original CASC contents/executable bytes.

### Native memory import

The separate import probe validates importer RVA `0x64bfd0` and the STU allocator's global/vtable/allocation function (`0x155aef8`, `0x12791b0`, `0x437220`). It checks native request success and descriptor GUID before import, allocates an aligned 96-byte buffer through the client, copies only the author-written candidate and transfers ownership through the native import request. This uses the same allocation family as the native STU destructor. The native attachment routine detaches earlier work; the native completion path publishes the object and updates failure/completion flags. The adapter does not write those flags.

Repeated runs publish the candidate under `0x07a000000000001d`: native descriptor flags `0xb1301`, nonzero root pointer, 96 bytes, and no remaining loader-work pointer in the captured completed descriptor. The helper also checks that the published root is exactly the allocated candidate buffer plus 16 and has the expected vtable. The original files remain unchanged; this is an in-memory silent substitute, not recovered original content.

The initial one-minute runs, including an active-window run, remained at world state 4 with loaded-map ID zero. The common-79 package had 1,070 pending work entries among 1,115 handles in one capture: 1,035 at stage 6, 27 at stage 13, seven at stage 8 and one at stage 10. The target Hanamura/global STU descriptor GUIDs were not found in the bounded heap scan. Its pending bundle CKey `6320cb843838297c27d1674a8d70420b` was independently read offline and hash-verified (2,688,272 bytes), so absence of that bundle is not established. Why native work is waiting remains unresolved; do not infer that the catalogue is the only loading issue or force world readiness from this result.

The extended five-minute run also stayed at world state 4 / loaded-map zero after publishing the candidate. It ended at the diagnostic deadline; this is a failed map-load test despite successful catalogue import. The original executable hash/signature and scoped ACL restoration were checked after cleanup. The separate earlier missing-voice-request probe's state-5/partial-geometry result remains distinct from this new mode.

```powershell
$buildRoot = Join-Path $env:LOCALAPPDATA 'OW1-preservation-build'
$client = Join-Path $buildRoot 'clients\1.0.1.27578'
python scripts/Audit-DiscResource.py (Join-Path $env:USERPROFILE 'Downloads\Overwatch 1.0.iso') $client --casclib "$buildRoot\casclib\Release\CascLib.dll"
& "$buildRoot\relay\tools\offline-launch\Release\ow1-offline-launch.exe" "$client\Overwatch.exe" --catalogue-schema-probe
# Separate native import + bounded map-load observation:
& "$buildRoot\relay\tools\offline-launch\Release\ow1-offline-launch.exe" "$client\Overwatch.exe" --catalogue-import-probe
```

Each diagnostic mode writes its own `<mode-without-leading-dashes>.dmp`, so a failed stage experiment no longer overwrites a map-rendering capture. Diagnostic timeout returns failure and terminates the owned job even when the native world is loaded; the helper does not report gameplay success from a state value alone.
