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

## Native metadata processing and retained request — 2026-10-12

`PracticeMetadata` activates the same native default context, discovers its
verified service, and invokes the original metadata initialization/processing
handlers on the owned primary thread. The request fields, metadata records,
world states and native readiness flags are not filled by this adapter.

```powershell
.\scripts\Start-RetailClient.ps1 -Mode PracticeMetadata
```

A separate retained request follows the native aligned allocation,
shared-control-block and request-constructor sequence. The original async
submission API consumes a second reference; the diagnostic retains one so the
native completion result remains inspectable. Its internal kind is 13, as in
the original metadata initializer. **This is an internal client identifier,
not a demonstrated network message opcode.** The adapter supplies no reply or
completion flag and does not consume or export response payloads.

The two-minute captured run establishes:

- The async submission gate is 1, including immediately before the retained
  request's submission. The native submission API returns true.
- The retained request's completion flag becomes true, with result flag 0 and
  queue-reset marker 0. The original report interpreted the result union
  incorrectly; the correction below supersedes its empty-data/error claims.
- Both native metadata handlers return 432 times in the dump. The world update
  returns 433 times and still returns at state 4 in immediate observations.
- The context remains current, its readiness stays zero, and the metadata cache
  stays empty. The service's initialization terminal flag is 1 and its pending
  metadata action has been cleared.

The initial report suggested a metadata provider/session failure. The corrected
native trace below instead identifies a local Hotfix-directory operation. It
does not demonstrate a private-backend reply, a working login, an original
wire protocol, or a completed map. No socket capability was granted and no
production credentials were entered. SDK submission/completion alone is not
metadata or gameplay success.

The read-only inspector validates the retained native control/object identities,
reference counts and internal kind. It distinguishes unsubmitted, incomplete,
empty-data and error-code results. Only flags, counters, identities and data
presence are reported; response/identifier bytes stay local.

Local evidence: `final-retail-practice-metadata-service.json`,
`final-retail-practice-sdk-metadata.json`, `retail-PracticeMetadata.log` and
`retail-map-metadata-probe.dmp` outside Git. The pre-retention comparison is
`retail-PracticeMetadata-service-baseline.log` /
`retail-map-metadata-service-baseline.dmp`.

## Continuation: structured result and private TLS diagnosis

Read-only tracing of the original async worker, kind-13 virtual method and
native consumer establishes that **result flag 1 means success; flag 0 means
structured error**. The completed captured request reports status 3, tag 2
and signed code -1 from offsets +18, +19 and +20. Data presence and entry count
at +138/+140 are reported only on success; error code +140 was a decoder bug.
New instruction/vtable guards and synthetic malformed-flag tests protect this
interpretation. Re-reading the existing dump reproduces the structured error.
The second tag is reported numerically; its enum meaning is unverified.

The kind-13 method enumerates the native local `104319/Hotfix` directory
through a filesystem provider. Its successful consumer marks existing cache
entries rather than populating the cache. This is not a backend-response or
authentication operation. Missing/empty Hotfix state and the empty context
cache still need separate investigation; no cache records or readiness flags
have been supplied by this project.

Claude's loopback bridge and observing TLS server were tested in a new
90-second owned run. The final client makes two TLS attempts: each sends
293 bytes and receives 1,295 bytes, then closes before completing the handshake.
No decrypted RPC, login or menu is verified. Candidate code-page writes still
fail with Win32 87. The pages are committed execute-read **MEM_MAPPED** pages,
with execute-read allocation protection. Dynamic-code policy was queried at
startup and again after failures: both return flags 0. This does **not** support
the prior ACG diagnosis; the mapping's protection constraints remain unresolved.
[Windows policy field meanings](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-process_mitigation_dynamic_code_policy).

The launcher now supports a bounded private diagnostic:

```powershell
.\scripts\Start-PrivateClient.ps1 -RunForSeconds 90
```

Pair it with `tools/bnet-probe.py` using your own loopback certificate/key outside
Git. The bridge preserves Internet/LAN isolation; only configured host loopback
ports are reachable. The TLS patch worker stops and joins before process-handle
cleanup. The run saves `retail-private.dmp` locally and restores the original
ACLs; exact restoration was checked after the completed run. Dump writing adds
time after the configured client wait. The TLS observer bounds framing, exits
on EOF/timeout and omits body/length-delimited field contents from logs.

Local evidence: `retail-private-mitigation.log`,
`private-tls-probe/bnet-observer.log`, `retail-private.dmp` and
`final-retail-practice-sdk-corrected.json`, all outside Git. A game-window capture
did not establish the current rendered screen; the runtime findings above come
from native/server diagnostics. No final map, hero or private match is verified.

## Continuation: native CA import and completed TLS 1.2

**Latest evidence:** our TLS 1.2 observer completes the original client's
handshake. The client then closes before sending even the two-byte RPC header
length. This is transport progress, not private authentication or gameplay.
The control run disables the legacy TLS patch worker and imports no CA; it also
completes TLS 1.2 and closes without RPC. Thus CA import is not established as
necessary for handshake completion. Default server TLS negotiation still fails
during handshake; its precise native error remains unverified.

All private diagnostic launches now skip the cutscene using the existing
instruction-guarded native ShowIntro option. No window input is required, and
this setting does not establish which screen rendered afterwards.

Static original instruction tracing identifies a native TLS client context
and its certificate store. SSL_CTX and SSL verify-mode fields are already zero;
the transport +10 field is its client/server role, not a verification switch.
The separate bgs chain/hostname/pin verdict path runs under its connection-state
dispatcher. Earlier claims that the candidate patch sites necessarily belonged
to OpenSSL's in-handshake certificate callbacks are superseded.

The new opt-in `-TrustCaCertificate` diagnostic uses only an operator-supplied
public certificate, at most 16 KiB, for the exact loopback BNetServer argument.
It requires a 1..180-second run and one container-port-1119 forward. It verifies
the executable hash and native instruction/object profile, finds one live TLS
context, preserves existing thread suspend counts, stabilizes the owned thread
inventory and retains the context. On the guarded primary transport it calls
the original PEM parser, X509_STORE_add_cert and X509-free functions, then
restores the original thread context. The extra context reference and author
callback allocation remain local until bounded job exit.

Native runs return `parsed=1 inserted=1 unwind_registered=1`; the timed run
completes the callback in 2,891 ms, before a server delayed by 30 seconds sends
its certificate. An independently read local dump also contains the completed
author callback and a live retained context. This does not override original
certificate, hostname or pin verdicts, alter TLS roles/modes, write original
executable pages, or install host certificates. Initial parser-guard, thread
suspension and changing-inventory failures stopped before CA import; the final
thread guard preserves already-suspended threads and bounds stabilization.

Provide your own local CA, server certificate chain and server private key
outside Git, with a loopback SAN/name. Start the observing server in one shell:

```powershell
$localTls = Join-Path $env:LOCALAPPDATA 'OW1-preservation-build\private-ca-probe'
python tools/bnet-probe.py --cert "$localTls\server.pem" --key "$localTls\server-key.pem" --log "$localTls\observer.log" --tls-max 1.2 --handshake-delay 10
```

In another shell, after building:

```powershell
.\scripts\Start-PrivateClient.ps1 -RunForSeconds 60 -TrustCaCertificate "$env:LOCALAPPDATA\OW1-preservation-build\private-ca-probe\root.pem"
```

The delay is diagnostic scheduling time, configurable 0..60 seconds; it is not
a protocol requirement. The observer logs the negotiated TLS version and bounds
framing while omitting body/string contents. The TLS 1.2 CA run exchanges 386
client bytes / 2,185 server bytes, completes the handshake, then closes before
RPC. The no-CA/no-patch control produces the same byte counts and outcome.
[Python's TLS version limit API](https://docs.python.org/3/library/ssl.html#ssl.SSLContext.maximum_version).

Original pin-helper tracing finds a special certificate-CN comparison for
`::ffff:127.0.0.1`. A fresh own certificate with that CN still completes TLS 1.2
and closes without RPC. A bracketed mapped-address BNetServer experiment makes
no bridge connection. Neither is a verified solution; the shipped CA probe
continues to require the exact IPv4 loopback argument. The next step is observing
the original post-handshake verdict and connection-state transition, rather
than assuming a specific pin failure or inventing server replies.

Local evidence outside Git: `retail-private-ca-stable.log`,
`retail-private-ca-delay30.log`, `retail-private-ca-tls12.log`,
`retail-private-ca-mapped-cert.log`, `retail-private-tls12-no-ca.log`, corresponding
named dumps, and observing-server logs under `private-ca-probe` /
`private-mapped-ca`. Certificate/key files, dumps and proprietary bytes stay
outside the public source repository. No RPC, private login, rendered final map,
hero or original private match is verified.
After the completed runs, client-folder and launcher-file ACLs match the saved
baseline exactly; the original executable SHA256 is unchanged and its signature
remains Valid. All owned clients and diagnostic observers were stopped.

## Continuation: native socket success and retained connection failure

The new `-ObserveTls` mode finds one original TLS socket, validates its wrapper,
transport and pending callback identities, then locates the corresponding
connection job through the original guarded handle map. It bounds heap searches,
bucket counts, chain traversal and observations. A brief owned-process pause
validates the live job/control identities and retains one original strong
reference until bounded job exit. This deliberately extends diagnostic object
lifetime; it does not change state, error, readiness or verifier results.
Socket sampling ends if its original identities disappear, while the retained
job preserves the subsequent error for observation. No debugger attachment,
callback replacement or original code patch is used by this mode.

Two native TLS 1.2 runs establish the distinction:

| Diagnostic | Native socket | Native connection job | RPC |
|---|---|---|---|
| Own public CA imported | 1 -> 2 | state 1/error 0 -> state 2/error 1016 | No header bytes |
| No CA, no verifier patch | 1 -> 3 | state 1/error 0 -> state 2/error 1016 | No header bytes |

The original callback writes socket state 2 only for result code zero; state 3
requires the original chain-result code 2. Thus the CA import does resolve this
native chain check, even though TLS handshake completion alone did not require
it. Both runs still close with higher-level **1016 (0x3F8)**. The job state's
enum and the precise underlying verdict that produces this error have not been
decoded; do not describe the code as a proven pin failure or working login.

The native socket keeps a separate 17,289-byte CA input. Original tracing shows
its higher-level verifier uses that input, independently of the SSL_CTX store.
An original virtual setter concatenates native certificate string records into
the input; it has not been called by this project. This is the next trust path
to investigate, together with the higher-level connection error handling.

With the TLS 1.2 observer running and a diagnostic delay of 15 seconds:

```powershell
.\scripts\Start-PrivateClient.ps1 -RunForSeconds 60 -TrustCaCertificate "$env:LOCALAPPDATA\OW1-preservation-build\private-ca-probe\root.pem" -ObserveTls
```

Omit `-TrustCaCertificate` for the control. The observation mode itself skips the
legacy verifier patch worker. For an unsigned source script on a UNC share,
invoke it with `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ...`;
this changes only that invocation's execution policy. Cutscenes skip as before.
A 30-second server delay produced a timeout before receiving any server bytes
in an earlier run, so do not treat that capture as certificate-verdict evidence.

Two local hardware-debugger experiments exited C0000005 before any verdict
observation. Existing debug registers were not overwritten. Their source is
saved outside Git; no debugger mode is included in the shipped launcher. The
exit's cause is unverified, and these runs provide no certificate diagnosis.

Local evidence: `retail-private-ca-socket-observe.log` /
`retail-private-ca-socket-observe.dmp`, `retail-private-ca-job-retained.log` /
`retail-private-ca-job-retained.dmp`, `retail-private-no-ca-job-retained.log`,
the timeout baseline and TLS observer logs under `private-ca-probe`, all outside
Git. These checks establish native trust/error behavior, not authentication,
a rendered final world or original private multiplayer.
The final build and all 13 tests pass; the saved client-folder/launcher-file
ACLs are restored exactly, original hash/signature are unchanged, and owned
diagnostic processes/listeners have ended.

## Current reproduction checkpoint — 2026-10-13

Historical handshake-only/error-1016 descriptions above are superseded. Native
local login and referral now work, and the own-key diagnostic lobby completes
its credential handshake. The group-13 gateway negotiates and accepts our
initial identity reply, advancing the original UI to **ENTERING GAME…**.
Main-menu access and gameplay remain unverified.
See docs/BGS_PROTOCOL.md for the observed transport, the verified gateway
negotiation and the current post-negotiation application frontier.

Requires Python `cryptography` for own-key loading/tests (`python -m pip install
cryptography`). Supply your own RSA-2048/e=65537 private PEM outside Git. Export
its modulus and the local client integrity input from an owned final-build dump:

```powershell
$local = Join-Path $env:LOCALAPPDATA 'OW1-preservation-build\private-mapped-ca'
$dump = Join-Path $env:LOCALAPPDATA 'OW1-preservation-build\clients\1.74.0.0.104319-original\Overwatch\_retail_\startup-wait.dmp'
python tools/lobby_credential.py --private-key "$local\lobby-key.pem" --public-modulus-out "$local\lobby-public.modulus" --integrity-dump "$dump" --integrity-out "$local\lobby-integrity.credential-key"
```

Outputs use exclusive creation: reuse existing matching files instead of
rerunning that export over them. Cert CN/SAN must include `::ffff:127.0.0.1`
(the original native expected peer name), while the client argument stays
`--BNetServer=127.0.0.1:1119`. Use your own local CA and leaf chain/private key.
Start exactly one host probe; stop it before starting a replacement:

```powershell
New-Item -ItemType Directory -Force .local\runs | Out-Null
python tools/bnet-probe.py --cert "$local\server.pem" --key "$local\server-key.pem" --log .local\runs\observer.log --tls-max 1.2 --handshake-delay 15 --serve --lobby-private-key "$local\lobby-key.pem" --lobby-integrity-key "$local\lobby-integrity.credential-key" --lobby-peer-group 13 --gateway-catalogue protocol/gateway-104319.json --lobby-login-schema protocol/lobby-login-104319.json
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\Start-PrivateClient.ps1 -RunForSeconds 120 -TrustCaCertificate "$local\root.pem" -ObserveTls -TrustSocketCa -TrustLobbyKey "$local\lobby-public.modulus"
```

Use separate shells for the server and launcher. The server delay gives the
owned key installer time to find the pipe; it is not a protocol requirement.
Expected native evidence: guarded heap key installed at state 4, then
`native_handshake_state=6 native_connection_phase=6`. Expected server evidence:
valid client proof, a 350-byte group-13 offer (`message_delta=0`), the probe's
`00 02` acknowledgement, hello 21800, our 81-byte reply 20500, and heartbeat
`00 03` every 5 s. Direct window capture showed **ENTERING GAME…**, still
waiting until the 120-second diagnostic ended. No further application request
or main menu was observed. Omit `--lobby-login-schema` for the negotiation-only
control. Group 0 is the earlier bootstrap-only experiment which retries referral
after about 60 seconds; group 13 selects the actual lobby-service schemas.
Original RSA/address/integrity checks execute unchanged, and the original
executable on disk is untouched. In the 2026-10-13 runs the retry lobby also
accepted the own-key credential; that is observed, not yet explained.
New run logs default to project `.local/runs`; `-LogRoot` overrides the location.
Continue development and private analysis in this project directory, reusing
the existing extracted original client and local native build/key caches.

Add `--lobby-initial-data keys-hotfix-player` to exercise the new initial-data
checkpoint: empty key/hotfix lists and our local player record. The key context
initializes through its original handler and the client sends requests 60002
and 42600. This is additional native protocol evidence; current game-window
captures are black and the main menu is still unverified. Use `keys` or
`keys-hotfix` to compare fewer notifications, or omit the option for identity
only. See BGS_PROTOCOL.md for packet sizes, traced handlers and evidence limits.

```powershell
python tools/retail_login_state.py --dump "$dump"
```

This read-only diagnostic emits booleans and guards the native context profile.
Its player marker is a current snapshot, not a persistent receipt/completion flag.

## Play with local accounts (launcher) — 2026-10-13

Accounts are our own, stored in `.local/accounts.json` (passwords as salted
PBKDF2 hashes); no Battle.net account is involved. Configure the server
certificate, CA and own lobby-key inputs once, create accounts, then play:

```powershell
python tools/ow1_launcher.py configure --cert <chain.pem> --key <server.key> --ca <ca.crt> `
  --lobby-private-key <lobby-key.pem> --lobby-integrity-key <lobby-integrity.credential-key> `
  --lobby-modulus <lobby-public.modulus>
python tools/ow1_launcher.py create Tracer
python tools/ow1_launcher.py list
python tools/ow1_launcher.py play Tracer
```

`play` starts the private server for that account (battle tag `Name#<id>`,
account id from 1001), launches the bounded client and keeps serving until the
game is closed. Close any earlier test client first: the game runs one
instance. Verified: the original client reaches the main menu and first-run
tutorial prompt as Mercy#1002. Computer Use (`@oai/sky`) also directly captured
and drove the main menu and Training in the later runs. A playable map is
still unverified.

## Experimental Training instance referral — 2026-10-13

To the private probe command above, add:

```powershell
--lobby-initial-data full --lobby-instance-referral --lobby-instance-schema protocol/instance-104319.json
```

Use the normal bounded private launch, dismiss the first-run Tutorial prompt,
then select Training -> Practice Range. The probe answers the observed 24000
request with a 242-byte plain 20600 referral to mapped loopback 127.0.0.1:1119.
All session inputs are generated locally. The original handler creates an
instance-referral job; it does not advance the visible entering screen in the
tested runs. The complete queue/game-assignment sequence and authenticated game
transport remain unverified. The default launcher does not enable this experiment.

The second referral string is also an IPv4:port endpoint; an earlier random
token there was incorrect. For the original client's datagram connection attempt,
start `python tools/instance_probe.py --run-for 180 --log .local/runs/instance.jsonl`
before launching, and add `-UdpForward 1119:21120` to Start-PrivateClient.ps1.
Keep the normal TCP `1119:21119` lobby forward and the bounded launch. Our
receive-only observer saw 39 native 34-byte packets after Practice Range in
`instance-udp1`; it sends no replies. This verifies outbound traffic only.
The UDP diagnostic preserves packet boundaries (<=4096 bytes), accepts one
container-loopback source port and grants no Internet/LAN capability. Its
parameters are optional; normal menu play is unchanged.

Independent queue-notification controls use
`--lobby-queue-schema protocol/queue-104319.json --lobby-queue-reply <23300..23333>`.
Select one notification deliberately; do not cycle through all handlers as if
they were interchangeable successful match replies. These controls accept only
the demonstrated Training request shapes and reject truncated/trailing bodies.
They cannot be combined with the instance-referral experiment.

```powershell
python tools/retail_login_state.py --dump "$dump" --queue-state --world-state
```

The queue snapshot contains counts and booleans only. Job absence in a late
snapshot is not proof that a referral was rejected: the original consumer can
copy and clear it. `instance-public1` ended with no job, zero queue records and
world state WAITING/no pending request. No new game TCP connection, map load or
playable hero is claimed.

## Authenticated instance handshake continuation — 2026-10-13

Read-only disassembly reconstructs both scrambled nonce/key blocks, matches
our generated referral inputs and corrects the send/receive codec roles.
The original state-1 receive transition requires flags 3. A bounded own-key
reply experiment (`udpflags7`) now changes the Practice Range overlay to
**ENTERING GAME**, advances acknowledgement state and produces nonempty type-1
packets. All 161 client packets/100 replies authenticate and regenerate with
`tools/instance_datagram.py`; its public fixtures contain only author-written
inputs. See BGS_PROTOCOL.md for the envelope and observed state checks.

This experiment uses a private responder with 100-reply/180-second bounds and
returns no application payloads. The public receive-only observer described
above still sends no replies. Reliable-message framing and game negotiation
remain unresolved; the final world is WAITING/no request. No rendered map,
controllable hero or completed game session is claimed. New RE/captures/keys
remain in ignored project .local/ and existing input caches.

## Server-welcome resource gate — 2026-10-14

Later private 20300 welcome experiments create pending Practice world requests
and receive a 21600 client join. The client remains WAITING. Read-only tracing
now reaches the real WAITING handler through aligned opaque-branch targets:
it checks resource catalogue availability, then waits for the map-header load
query to return 3 before entering ABANDONING SCENES. Raw state 0 does not advance.

`tools/retail_login_state.py --world-resource-state --dump <private-dump>`
reproduces the saved udpapp11/21 result: catalogue entry present, header load
cache entry absent, raw state 0. Both snapshots have 28 other resource-cache
entries. This is the resource-load cache, separate from the earlier context
metadata cache. The new reader exports only flags/counts/statuses and never
calls a loader or writes native memory.

The native-header experiment above already establishes that a retained native
resource request can satisfy this prerequisite. The remaining work is to find
the original initiation path during server application negotiation. Guessed
settings/server frames have not done so. No new game launch, rendered map or
playable hero is claimed by this saved-dump continuation.

## Native metadata registration and acquisition retries — 2026-10-14

Later bounded interactive runs udpmeta22/24/25/26 reproduce the main menu,
Training and Practice selection through Computer Use, using the existing
original client in Claude's cache. That explicit client path restores working
window capture/input. The completed native runs terminate at their bound;
new private evidence stays in project
`.local/`. The default launcher has not gained a speculative filesystem fix.

The authenticated 20318 record reaches the original metadata registrar. Its
checked format value is 1, not build 104319. A diagnostic empty descriptor
creates one cache entry but no content, and ends after ten acquisition attempts
with flags 0xa0 and no current context. The public numeric profile and read-only
`--metadata-state` reader make this distinction reproducible without publishing
identifiers, digest bytes, native memory or packets.

Run udpmeta22 visibly reports HF-503 (insufficient write permissions). Creating
only the owned Hotfix directory in udpmeta24, then adding an own-package-only
modify grant in udpmeta25/26, does not resolve the final failure. Earlier private
reports called +0x80/+0x88 an action pointer/marker. Aligned native tracing
corrects them to **retry deadline/completed-attempt counter**. The apparent
7-to-10 change was further failed attempts.

The original acquisition requests are kind 14, distinct from the earlier
kind-13 enumeration. A read-only observer in udpmeta26 captures six completed
requests while their original service/control-block references remain live.
Every sample reports error 3/2/-3; the native file-error label is "failed to
open". The kind-14 worker attempts to open a local temporary file before
content transfer. The generic error alone does not identify the underlying
Windows failure, and the descriptor still lacks valid content information.

Final udpmeta26 state remains WAITING with pending requests, catalogue-present
but load-cache-absent header/mode resources (raw state 0), and 29 other cache
entries. No map or playable hero is verified. Cleanup confirms owned processes
and listeners gone, exact captured installation/launcher ACLs restored, the
ephemeral profile removed, and the original EXE hash/signature unchanged.
Next: trace the native file-provider open failure and establish valid metadata
association/content; separately retain the original map-header load path.

## Active versus staged context correction — 2026-10-14

Reinspection of the newer saved udpmeta27/28/29 artifacts narrows the storage
issue: direct writes inside the owned Hotfix folder succeed, while several
ancestor attribute checks return Windows access denied. The private path-alias
experiment passes restricted-token access checks and changes four live-referenced
kind-14 completions in udpmeta28 from the earlier 3/2/-3 to 9/2/6. Acquisition
still exhausts its retries; this does not establish working Hotfix content.
The alias and owned processes were removed and the recorded ACLs restored.

Aligned tracing of the original context update corrects an earlier diagnostic
label. Slot +0x1a0 holds the staged context; completion moves it into active slot
+0x198 and clears the staged slot. The default identifier takes a completion
branch without setting the content-ready flag. Saved udpmeta26/28/29 all have
an active kind-1 default context, zero records and an empty staged slot.
Neither empty staged state nor this default's unset ready flag proves that
context processing is stalled. Earlier "current context absent" descriptions
refer only to the staged slot and must not be used as evidence of no active
context. udpmeta27's snapshot precedes terminal initialization and has neither
slot populated.

The public read-only metadata reader now validates and reports both context
identities, reference bounds, default-identifier equality, readiness and record
counts. It also validates any retained kind-13 initialization request/control
block, reporting success or structured error only after completion. The old
`current_context_present` field remains as a compatibility alias for staged
presence; use `active_context` and `staged_context` for new analysis.

Eight synthetic metadata fixtures pass, and the native build and all 21 CTest
targets pass. This continuation reuses saved dumps; no new native launch or map
success is claimed. The remaining frontier is the original map-header preload
path: udpmeta29 still has a catalogue entry but no header load-cache object.

## Structured resource API and engine preloader — 2026-10-14

The default resource-request wrapper calls a structured API, which also has
direct callers elsewhere in the client. A native engine preloader builds those
requests from configured descriptors and retains submitted descriptors. Its
submission marker is distinct from resource completion. Searching only callers
of the default wrapper misses this path.

The new `--preload-state` diagnostic verifies the exact engine context and
reports bounded aggregate counts without identifiers, pointers or resource
bytes. Saved udpapp11/21/udpmeta26/29 each contain zero configured and retained
entries in this preloader. These are final snapshots; transient earlier queue
activity and the queue's precise relationship to Practice assignment remain
unresolved. No native queue or readiness state is changed.

The previously identified map-loader getter reads member +0x190. Its initializer
checks for resource type 2, rather than the map-header type used by WAITING.
That initializer therefore does not by itself establish the missing header
preload path. The engine descriptor producer and conditional eligibility are
the next investigation target.

Native targets build and **22/22 CTest targets pass**, including four new
synthetic queue fixtures for type classification, submission versus completion,
native identity/count/array bounds and output omissions. This continuation uses
saved dumps and adds no new native launch or gameplay verification.

## Live assignment and gallery checks — 2026-10-14

Five new bounded original-client runs exercise Practice Range and Hero Gallery.
The three Practice comparisons use a map-header assignment, that assignment
plus an extra header/mode list, and a map-root assignment respectively. All
reach ENTERING GAME and end with pending WAITING requests and no header cache
object (raw state 0), despite catalogue presence. The root comparison has only
about 20 seconds after selection. No rendered map or controlled hero is verified.

The welcome's extra resource list is copied into native request +0xf8 with
signed count +0x100. The prior private prototype's +0x68/+0x70 was a separate
settings array. Corrected private checks verify count 2 and both expected
resources in each list-test request. Public --world-resource-state exposes only
the bounded count and rejects malformed/incomplete arrays. This verifies
delivery, not a preload request or completion.

Live read-only sampling around every 100 ms records empty configured/retained
engine queues throughout these observed intervals; shorter transitions and
other world queues remain possible. Practice activates the default metadata
context with zero records without a 20318 message. Hero Gallery remains empty
in both controls, including after selecting all visible filters in the second.
These findings leave both the normal header-load trigger and gallery roster
initialization open. They do not establish a global asset-read or rendering fault.

All 22 CTest targets pass after the clients exit, with six synthetic resource
diagnostic fixtures. Cleanup verifies original hash/signature and exact saved
ACL restoration; private captures and generated session material stay ignored.

## Private-session native preload control — 2026-10-14

The opt-in launcher flag `--preload-practice-header` adds a bounded control to
the existing own-key private-session diagnostic. After validating the original
pending Practice header/mode request and native loader instructions, it calls
that loader once at default priority on the verified original primary thread.
The returned native reference is retained until the owned job ends. No world
request, extra world tick, resource payload, completion or readiness value is
supplied by this control. The default launch path is unchanged.

Both live controls load the header and mode to raw state 3 and advance both
native world managers to WORLD LOADING (6). A repeat visibly reaches the
Practice Range loading screen with its art/name/tip, where it remains. This is
loading-screen progress, not a rendered gameplay scene or controllable hero.
Final cache totals are 29 objects, all raw state 3; the map-root entry remains
absent. The normal protocol path that triggers the header load is unresolved.

The later WORLD LOADED handler checks content-context/provider gates, request
submission, the owner's loading flag, and a target world's request/state.
This was initially mislabeled WORLD LOADING; the actual dispatch for state 6
is a different handler. Those later gates do not identify the current stall.

The new read-only `--resource-cache-state` reports only bounded aggregate counts
and raw statuses. It confirms 28 completed resource objects in the earlier
Practice/gallery controls, so those UI failures do not establish a general
asset-read failure. Native build and all 22 CTest targets pass after live exit.

## WORLD LOADING completion — 2026-10-14

The corrected state-6 handler checks three resource groups and a scene-service
readiness boolean. The read-only `--scene-state --client-pid` diagnostic uses
the PID belonging to the saved dump to reproduce the original pointer getter;
it validates the original profile and identities and exports only counts,
statuses and booleans. Both saved loading-screen controls have groups 4/2/0,
all six resources at raw state 3, but scene readiness is false and both active
and pending scene handles are absent. This narrows the observed failure to
scene initialization beyond resource completion. Its cause remains unresolved.

The original update sets readiness only after a scene object reaches native
state 5 and satisfies its completion predicate. The next investigation is the
scene-construction path. No readiness flag, scene state or client asset is
overwritten. A fresh bounded run authenticated but Windows input access failed
with a black captured window, so it did not exercise Practice selection.
Cleanup passed; native build and all 23 CTest targets pass.

## Typed Practice map assignment — 2026-10-14

With Windows input working, two bounded live selections reproduce the original
Practice loading screen. The baseline again has complete resources and absent
scene handles. The loaded map header's scene reference includes a variant bit
missing from the earlier root assignment. Supplying this exact typed reference
in the experimental welcome, alongside the explicit header preload control,
creates pending scene objects in both world managers.

Those objects remain at native raw state 1; readiness requires state 5 plus
the scene completion predicate. The predicate's two resource objects are already
at raw state 3. The read-only scene diagnostic now reports these distinct gates
with exact getter/object identity checks and bounded aggregate output. Scene
construction has progressed, but scene-state advancement and gameplay remain
unresolved. The opt-in control accepts only the two exact Practice assignments
and the exact Practice mode. It retains the one original header-loader call;
the default launcher path is unchanged. Both live cleanup audits pass.

## Canonical map and replication boundary — 2026-10-14

A further bounded comparison uses the canonical Practice map identifier with
the same explicit header preload. It completes the typed map asset, unlike the
referenced variant. The original state-1 path was waiting for that typed asset;
the earlier raw-resource completion checks described a separate loading layer.
This corrects the earlier assumption that the referenced variant was the right
server assignment.

The final dump has one WORLD LOADED manager and one WORLD REPLICATING manager.
Both have active scene handles, readiness true and scene-controller state 5;
the typed asset object is present with native status 4. The read-only diagnostic
reports these fields separately, without native pointers or identifiers.
The original UI still displays the loading screen: geometry rendering, hero
selection and gameplay remain unverified. Replication initialization is the next
boundary. Normal protocol-driven header loading is still unresolved, and the
default launcher path is unchanged. Native build, all 23 CTest targets and
the live cleanup audit pass.

## Selected-entity replication gates — 2026-10-14

The normal 20302 notification writes the world owner's selected-entity ID.
A bounded comparison clears the native validity gate, but its index-only ID
does not match the existing entity generation. Supplying the matching packed
ID resolves a native entity object. The world still remains WORLD REPLICATING
and the original UI stays on the Practice loading screen. No replicated player,
hero selection or gameplay is verified.

`retail_login_state.py --replication-state` now reports the separate validity,
record and object gates, plus generation mismatch, using only booleans/counts.
It validates the original profile/getters and bounds reads to one bucket per
world owner. Native build and all 24 CTest targets pass; completed live cleanup
audits pass. The experiments retain the opt-in header preload.

A further comparison delays the valid notification by 30 seconds. It still
resolves the entity and stays WORLD REPLICATING, with four pending entries and
completion marker false. The earlier notification run has that marker true;
the observers do not establish why. Queue counts and marker are now reported
separately, without treating any one field as completed replication. The native
pending-entry drain is the next investigation.

## Placeable replication and visible map — 2026-10-14

Claude identified the four pending entries as map placeables whose creates
must arrive from the server. Minimal placeable creates clear those entries and
advance the original client through GAME MODE LOADING to WORLD_RUNNING.
Saved run55 and an independent bounded reproduction confirm this state.

The new reusable entity-section codec reproduces captured sections exactly,
and its migrated private responder reaches the same state. In livecodec59 and
livecamera60 the loading overlay disappears and Practice geometry visibly
renders. Escape opens the in-game menu. There is no hero HUD, weapon or hero
picker; short forward/mouse/hero-selection checks do not establish control.
This is a rendered original map, with player/hero replication still unresolved.

Native build and all 25 CTest targets pass. The protocol experiment continues
to use the opt-in original header preload and a diagnostic existing-entity
selection. The default menu path is unchanged.

The livetime62 timing-field control reproduces visible Practice geometry without
a hero HUD or weapon. The original client stores the timing field, while its
controlled-actor marker remains invalid. The diagnostic selected entity lacks
component 44, required by the traced first-person owner lookup. New guarded
read-only checks distinguish this prerequisite from successful entity resolution;
component presence alone would not prove a controllable hero. All 25 CTest
targets and bounded-run cleanup checks pass. Player/hero initialization and full
clock synchronization remain unresolved.

Further bounded runs create and select a verified definition entity using the
native network-create path and 20302. The engine constructs component 44 and
both post-create callback component pairs. The selected entity therefore passes
the previously missing prerequisite, while its linked actor ID remains invalid.
Practice geometry renders, but no hero HUD or hero picker is observed. Actor
creation and link initialization remain unresolved. The strict reusable codec
now includes the verified minimal definition-create form; all 1332 captured
sections from these two runs re-encode exactly, including 160 definition creates.
