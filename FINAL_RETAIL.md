# Final OW1 supplied-client baseline — 2026-10-12

The user supplied `Overwatch1.74.0.0.104319.7z` from their Downloads folder.
The requested final client is now acquired locally. Its original executable
starts under network isolation and survives a bounded 60-second observation.
The user confirmed the interactive client displays its title or login screen
on 2026-10-12; this is user-observed UI evidence.
No final-retail map, controllable hero, private login or multiplayer session is
verified. Acquisition does not make the beta or disc hooks compatible.

## Identity and extraction

| Item | Verified result |
|---|---|
| Archive size | 27,710,552,582 bytes |
| Archive SHA256 | `53a353a3ee220bb88f4b30d9ced4f248b2d0417152c6cbdba2f319e3d7c7634f` |
| Listing | 692 entries: 672 files / 20 directories; no traversal, absolute paths, ADS, links or duplicate paths accepted |
| Extraction | 7-Zip 25.01, all entries extracted, integrity result `Everything is Ok`; 28,516,918,608 uncompressed bytes |
| Executable | `_retail_/Overwatch.exe`, 52,045,144 bytes, x64, valid Blizzard Entertainment signature |
| Executable SHA256 | `ef67d348ecca066ce1698683fd0fd810075357164b345d83ed9296d676e0ebe2` |
| Declared version / BuildConfig | `1.74.0.0.104319` / `786a31729ba1c684a5c80fbaf7cb92b8` |
| Config verification | Config MD5 equals its key; `build-name = prometheus-1_74_0_0-104319` |
| CASC executable | `RetailClient/Overwatch.exe`, MD5 `96e49aa240e70bf0c2eda9fe552c252a`; identical to the extracted EXE |

The config's `prometheus` name is Blizzard's internal build label. It does not
refer to this project's DLL. Windows' four-part fixed file version is
`1.74.0.38783`: its 16-bit private field holds `104319 mod 65536`. The full build
identity comes from the supplied build/config metadata, corroborated by the
final manifest build number. Empty version strings are retained in inspection.

The extracted installation is outside Git at
`%LOCALAPPDATA%\OW1-preservation-build\clients\1.74.0.0.104319-original\Overwatch`.
Its `.build.info` and `data/casc` are in the installation parent of `_retail_`.
The original archive is unchanged. Native startup may write caches/settings to
the extracted installation; the archive remains the pristine backup.

## Offline storage and manifest evidence

CascLib `38a34665624b8775bb875274b36191b21c38d97b` read the 20,119-byte ROOT and
all three selected CMFs offline; their original content MD5s were verified.
ROOT has 134 named entries. The new source-built .NET 8 metadata probe links
TACTLib's exact 104319 provider at
`388f8dd6a7e67a72904bab9b5bffaa163ecbe59c` (MIT).

| Manifest role | Bytes / original MD5 | Decoded logical assets | Direct local-index matches |
|---|---|---:|---:|
| Base | 13,665,280 / `473a98cea8209538af13cb0e487f54e4` | 471,024 | 195,904 |
| English text | 1,296,096 / `ff4eb4e109f18bf03adb052618b0a00a` | 44,691 | 137 |
| English speech | 696,544 / `864624c8f08865aae68beaa9a5a16307` | 24,017 | 24,008 |

The local enumeration yielded 1,019,717 files and 461,032 distinct locally
available content keys. A logical asset without a direct content-key match is
**not established missing**: many resources are stored inside bundles.

A bounded bundle sample read and hash-verified 41 bundles, then hash-verified
130 of the base manifest's 132 map-header payloads inside those bundles. One
sampled bundle returned CascLib error 6002 (`ERROR_FILE_ENCRYPTED`), indicating
an unavailable decryption key; that is not proof of absent physical data.
The remaining bundles and two map headers were not resolved by this sample.
Map-header verification does not prove map geometry, every dependency or
gameplay. This is not a complete asset audit.

## Native startup

Two isolated runs survived their 60-second deadline. The helper ended both
owned jobs and returned a diagnostic nonzero exit; this is process-survival
evidence, not a successful game/session result. The executable was not patched,
the beta DLL was not injected, and no disc offsets were read. The real
AppContainer TCP probe returned WSAEACCES (10013). Scoped ACL restoration and
the original executable's valid signature were checked after the first run.

Native logs from both runs include offline CDN DNS failures and
`PathOps: .. is the leading path component: /../.build.info`. Using the
installation root as the working directory did not resolve this warning.
Its effect on initialization is not established. Windows window inspection
failed with `GetCursorPos ... Access is denied (0x80070005)` in two attempts;
automation could not verify the final screen. The user subsequently reported
"Title or login screen" for the still-running interactive client, confirming
startup to the original interface. This does not verify login or gameplay.

`--retail-offline` keeps the same unmodified fingerprinted client open until
user exit. This provides startup inspection only. A separate retail resource,
session/controller and service adapter remains required for gameplay.

## Reproduction

Keep game files, generated metadata and diagnostics outside Git. From the
repository root, with the source build and external CascLib already available:

```powershell
$buildRoot = Join-Path $env:LOCALAPPDATA 'OW1-preservation-build'
$client = Join-Path $buildRoot 'clients\1.74.0.0.104319-original\Overwatch'
.\scripts\Inspect-Client.ps1 -Path "$client\_retail_\Overwatch.exe"
dotnet build research-tools/final-manifest-probe -c Release `
  -p:TACTLIB_SOURCE_DIR=C:/path/to/pinned/TACTLib `
  "-p:BaseIntermediateOutputPath=$buildRoot\final-manifest-probe-obj\" `
  -o "$buildRoot\final-manifest-probe"
python tests/final_manifest.py "$buildRoot\final-manifest-probe\final-manifest-probe.dll"
python scripts/Inspect-RetailStorage.py $client `
  --casclib "$buildRoot\casclib\Release\CascLib.dll" `
  --manifest-probe "$buildRoot\final-manifest-probe\final-manifest-probe.dll" `
  --output "$buildRoot\new-retail-audit"
& "$buildRoot\relay\tools\offline-launch\Release\ow1-offline-launch.exe" `
  "$client\_retail_\Overwatch.exe" --retail-snapshot
.\scripts\Start-RetailClient.ps1 -ClientFolder $client -BuildRoot $buildRoot
```

Use a new audit output directory; existing output is refused. Preserve the
original CMF filename for provider derivation. The probe validates source MD5,
build/count/table bounds and decoded ordering before creating metadata output;
it does not print derived keys. `--retail-snapshot` writes a local full-memory
`_retail_/startup-wait.dmp` at its deadline, then ends the owned process.
Interactive startup logs go to `retail-interactive*.log` in the build root.
Close the game normally so the owning helper can restore permissions.

Local evidence includes `final-retail-extraction.log`,
`final-retail-client-inspection.json`, `final-retail-root-native-logs.txt` and
`final-retail-repeatable-audit/report.json`. No proprietary payload, dump or
generated manifest was added to source control. Source tests pass 11/11;
separate manifest-probe synthetic tests also pass. Linux/Wine remain untested.

## Map-header interpretation — 2026-10-12

The new bounded STU V2 reader parses root field bags and dynamic strings using
OWLib/TankLib's documented serialized format. It derives resource references
using the header CRC64 and field hash, with independent checksum/byte-swap
vectors and malformed table/field/string checks. This does not specify native
object layouts or fixed retail hook offsets.

All 130 previously hash-verified map headers parse as root type `02514b6a`.
Each has a readable internal name and a map reference matching the original
base manifest. Names include regular Hanamura, its winter variant, Gibraltar
and the Practice Range; lobby/event variants are also present. The 130 count
is a header/variant count, not 130 distinct playable maps.

| Selected map | Header GUID | Map-root GUID | Original map-root MD5 |
|---|---|---|---|
| Hanamura PvP | `0790000000000165` | `0800000000000165` | `2193ea608bd0fbf9546cf25d91e7e8e3` |
| Practice Range | `0790000000000688` | `0800000000000688` | `32fd86999325f7adbe7c85fd104122b9` |

Both selected 912-byte map-root payloads were found inside separate bundles
and hash-verified. Their payload format is unparsed and is not STU V2. The
bounded search attempted 135 bundles / 43,653,532 advertised bytes before both
were found; six other bundles returned unavailable-key error 6002. Their
contents were not required to resolve these two selected payloads. Neither
these reads nor title-screen startup establishes complete map dependencies,
native world/entity initialization, hero availability or collision.

```powershell
python scripts/Inspect-RetailMaps.py $client `
  --casclib "$buildRoot\casclib\Release\CascLib.dll" `
  --audit "$buildRoot\final-retail-repeatable-audit" `
  --map-guid 0800000000000165 --map-guid 0800000000000688
```

Output is metadata only. The local report is
`final-retail-map-metadata.json`; payloads are read in memory and not exported.
The optional map-root search accepts up to eight exact manifest IDs and stops
at 256 bundles / 512 MiB advertised bytes. Tests and real metadata reads passed;
no native game-stage manipulation was attempted for this milestone.

## Native Practice request — 2026-10-12

The separate 104319 world probe now executes the native request API. It copies
the resident 0x150-byte default request, repairs its inline-vector pointers and
sets only the map index to `0x688`. The client allocates its own descriptor,
publishes it at world offset `+0x20`, and preserves the original world/owner
identities and dispatch. This field is a **descriptor pointer**, not a GUID.

The read-only dump inspector checks the original executable hash, captured
module size/timestamp, instructions, vtables, state table and decoded owner.
It independently confirms the native descriptor's first u32 is 1672 (`0x688`).
Optional `FRP1` records identify this project's callback diagnostics; absent
records or an unqueried header result are reported explicitly, not as failure.

Submission executes at the owned primary thread's verified native delay-return
instruction and restores the captured context with `NtContinue`. Loading
experiments use verified free space on that thread's original stack and refuse
callback reentry. Windows unwind registration succeeds. The request allocation
is distinct from the probe's input buffer. No loader-ready or world-state value
is written by the probe.

The guarded `ShowIntro` option is cleared only in each owned map-diagnostic
process after its native initializer. This makes testing independent of intro
keystrokes. Normal interactive startup retains the original option. The archive
and executable on disk are unchanged.

Results:

- The original final title/login interface was inspected directly with the
  computer-use tool; its visible build is `1.74.0.0 - 104319` and its isolated
  login attempt times out. No credentials were entered. Later input failed with
  `GetCursorPos ... Access is denied (0x80070005)` despite the user's unlocked
  desktop; this is an automation limitation, not evidence of a game failure.
- Submission-only observation publishes the native Practice descriptor and
  survives its two-minute diagnostic window at state 2.
- The loading-handler run returned 218 calls in its captured metadata and
  reports the exact Practice header `0790000000000688` available in the native
  resource index. This is stronger than the earlier external CASC read, but
  does not establish every dependency or a loaded world.
- The full original-world-update run on the original stack returned 221 calls
  and also survived its two-minute window at state 2. Neither run reached state
  3 (global loading), state 5 (world loaded), a controllable hero or a session.
- Earlier scratch-stack full-update execution ended with `0x80000004`; the
  original-stack transport subsequently survived. A debugger experiment instead
  failed before map submission at RVA `0x2101790` / `0xc0000005`. These failures
  are recorded separately; their exact internal causes are not established.

The next experiment below distinguishes resource existence from loading.
Private login and actual match replication remain unimplemented.

```powershell
.\scripts\Start-RetailClient.ps1 -Mode PracticeRequest
# Separate loading experiment; let the preceding owned job finish first:
.\scripts\Start-RetailClient.ps1 -Mode PracticeLoad
```

Both diagnostic modes wait for native world creation, have bounded observation
windows, save local full-memory dumps and end their owned jobs. A deadline
returns a diagnostic nonzero exit; it is not game/session success. Keep the
resulting logs/dumps outside Git. Reinspect one with:

```powershell
$buildRoot = Join-Path $env:LOCALAPPDATA 'OW1-preservation-build'
$exe = Join-Path $buildRoot 'clients\1.74.0.0.104319-original\Overwatch\_retail_\Overwatch.exe'
python scripts/Inspect-RetailWorld.py $exe `
  (Join-Path (Split-Path $exe) 'retail-map-loader-probe.dmp')
```

Local evidence: `final-retail-practice-request.json`,
`final-retail-practice-loader.json`, `retail-map-loader-availability.log`,
`retail-map-context-tick-native-stack.log` and
`final-retail-loader-native-logs.txt` under the external build root.

## Native header loading — 2026-10-12

The idle handler's existence query is separate from its load-state query.
With just the map descriptor, native header existence is true but the raw
load-state byte remains `0`. A captured two-minute run returned 214 loading
callbacks without progressing beyond world state 2.

A separate experiment requests `0790000000000688` once through the native
resource API at its native default priority 4. That API returns a nonzero
client-owned resource entry. The raw header load state changes to `3` and
the idle handler advances the world to state `3`. No resource payload,
readiness flag, loader counter or world state is supplied by the probe.
The native resource reference remains alive until this owned job ends.

The initial loading-handler experiment returned 216 callbacks and survived
two minutes at state 3. The subsequent full original-world-update experiment
logged 214 returned updates (215 in the later dump) and also survived two
minutes. It reaches state 3 but
can return to state 2 and retry. Further loading completion is unverified.
A directly captured game window was black; activation still failed with
`GetCursorPos ... Access is denied (0x80070005)` despite the unlocked desktop.
No rendered map, hero or session is claimed.

`PracticeResources` now uses the full original world update on the verified
original thread stack. It stops this project's extra updates if the native
world advances beyond loading states 2–4; later session/replication integration
needs separate verification. The existing `PracticeLoad` mode remains the
earlier loading-handler experiment without the resource request.

```powershell
.\scripts\Start-RetailClient.ps1 -Mode PracticeResources
```

The deadline saves `retail-map-resource-probe.dmp` outside Git and ends the
owned job. `Inspect-RetailWorld.py` reports resource existence, the raw load
state (or explicitly unqueried), whether this experiment submitted a native
resource request, and its returned entry pointer. These measurements establish
the header-loading prerequisite, not complete map dependency readiness.

The guarded read-only loading report also records the native state-3 gate
counter and whether the descriptor's opaque 32-byte loading context is present.
The captured counter is `0` and that context is all zero. Later native loading
examines this context, but its format and required session relationship remain
unverified. The report exposes presence only, never its bytes. Next work is
the native loading/session setup beyond the header, rather than assuming all
dependencies are ready or filling unknown context fields with fabricated data.

Local evidence: `final-retail-practice-load-state.json`,
`final-retail-practice-resource-handlers.json`,
`final-retail-practice-resource-request.json` and the corresponding
`retail-PracticeLoad.log` / `retail-PracticeResources*.log` files.
The additional loading report is `final-retail-practice-loading-context.json`.

## Immediate state tracing and native context activation — 2026-10-12

The earlier half-second host observations miss a short state transition.
Measurements immediately before/after each original update show **3 → 4**;
by the next host observation the world is back at 3. The single-update dump
captures 222 returned calls, including 221 entered from state 3, with highest
returned state 4. This establishes a native transition, not a completed map.

The resource experiment now permits at most two updates per callback. The
second is conditional on the first returning in state 4. Without an active
context, that state-4 update rejects and clears the native map request. The
probe now stops extra updates when the native request is cleared and refuses
to call the update outside loading states 2–4, including a check inside the
callback. No original loading gate or state is overwritten.

The descriptor's 32-byte all-zero identifier matches a resident native default;
zero bytes alone do **not** prove that the identifier is invalid. A separate
`PracticeContext` experiment follows the original caller's native sequence:
construct a type-2 context from that default identifier, retain a reference,
and pass another reference to the consuming activation API. The native API
publishes the object and dispatches its context-change notifications. The
adapter does not register fabricated metadata, fill an original resource
payload, set readiness, or advance a world-state field.

```powershell
.\scripts\Start-RetailClient.ps1 -Mode PracticeContext
```

The native constructor's object identity and type are guarded. Activation
returns true. A two-minute run logged 431 returned updates; the later dump
captures 433, including 216 entered from state 4, with the callback inactive
and the native Practice request retained. Each immediate state-4 update
returns at state 4. Host observations still see state 3 between callbacks;
the reason for that intervening change remains unverified.

The guarded read-only report verifies the native context service through its
vtable, decoded owner and a bounded 256-slot component search. It records:

- The constructed context is the service's current context; it has not become
  the previous context.
- Two native context-change subscribers are registered.
- The native metadata cache has zero entries, and the context's readiness
  flag remains zero. The native lookup used by context processing cannot find
  a metadata entry in that empty cache.

The next prerequisite is native content-metadata registration and processing.
Its source, schema and service/session relationship still need verification;
the existing archive's map-header availability does not supply this cache.
There is no evidence yet of state 5, a rendered final world, a hero or a private
match. The report now names the descriptor byte predicate
`request_loading_context_nonzero` to avoid implying that a zero native default
identifier is an absent object. Identifier and metadata payload bytes are not
returned by the report.

Local evidence: `final-retail-practice-update-trace-single.json`,
`final-retail-practice-update-burst.json`,
`final-retail-practice-context-service.json` and the corresponding
`retail-PracticeResources-update-*.log` / `retail-PracticeContext.log` files.
The context diagnostic saves `retail-map-loading-context-probe.dmp` outside Git.
