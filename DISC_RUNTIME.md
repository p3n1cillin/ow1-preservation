# Disc runtime investigation — 2026-10-11

> Historical experiment. Current development targets final OW1 1.74.0.0.104319. The old ISO is no longer available and is not a current project dependency.

**The supplied client renders the original Overwatch title/login screen offline.** A separate speech-omitting experimental profile reaches native world-loaded state 5 and renders partial Hanamura geometry beneath the loading overlay; see [DISC_ADAPTER.md](DISC_ADAPTER.md). A controllable hero, completed gameplay session, successful login or private match has not been demonstrated. Title startup was reproduced from a fresh ISO reconstruction.

## Recovered installation and independent checks

The original ISO and all proprietary artifacts remain outside Git. The local installation candidate is `%LOCALAPPDATA%\OW1-preservation-build\clients\1.0.1.27578`. All 14 install-manifest files were recovered, with their decoded size/content MD5 checked against the original manifest. The executable retains its original SHA256 and Blizzard signature.

`Rebuild-DiscStorage.py` copies all 64,883 encoded disc records into five CASC segments and 16 indices under `Data/casc`. It verifies each encoded key, preserves encrypted bytes, and writes an **inferred** build configuration and `.build.info`; these are not the missing original CDN configuration. The writer also prepares `cache/casc`, required by the client. This is an experimental installation candidate, not a claim that all game assets or startup requirements are satisfied.

Independently built [CascLib](https://github.com/ladislav-zezula/CascLib/tree/38a34665624b8775bb875274b36191b21c38d97b) opened the reconstructed storage and returned these files with MD5 matching the original ROOT manifest:

| File | Bytes | Original content MD5 |
|---|---:|---|
| `PtrClient/Overwatch.exe` | 23,996,904 | `34c00f0646b42e09f5fc50880f048cd1` |
| English RDEV application manifest | 312,324 | `1c03e74827ec7e42781f83bb8a1c5683` |
| English RDEV speech manifest | 54,852 | `9f8caf03d04d9c85292cf420bd3c341e` |

These independent reads validate storage framing and selected named files. The subsequent native title-screen launch validates startup resource loading; complete map/hero asset availability remains unverified.

## Startup evidence

The diagnostic launcher creates a temporary [Windows AppContainer](https://learn.microsoft.com/en-us/windows/win32/secauthz/appcontainer-isolation) with no network capabilities. Its child probe verifies `TokenIsAppContainer=1` and a TCP connection is rejected with `WSAEACCES=10013` before the game starts. The job closes on timeout/error and kills its children. Folder/executable DACLs are saved and restored; the profile is deleted afterward. Only the staging folder gets temporary write access for the game's cache. No firewall, WMI, account or system trust settings were changed.

An unmodified isolated launch crashes with access violation `0xC0000005` at game RVA `0x415EBB`. The decrypted instructions dereference a null `IWbemServices` pointer after WMI `ConnectServer` fails. A separate probe reproduced WMI access denied (`0x80070005`) inside AppContainer; DXGI and hardware/WARP D3D11 device creation succeeded there.

The opt-in `--wmi-workaround` checks executable SHA256 and expected instructions before applying an in-memory return from that hardware-query function. It does not alter the file on disk, inject the beta DLL, redirect authentication or provide a game adapter. It is an experimental diagnostic workaround; no gameplay compatibility is established. Timing matters because the executable decrypts code on demand. A default launch applies no patch.

The first reconstructed installation stopped at `Error: Mgr 13 failed to start. Could not locate resources.` Captured timestamped native logs narrowed this down to missing required `.build.info` columns, then `Failed to validate reconstruction header. Bytes read: 30`. The writer now includes `IM Size`, `Armadillo` and `Last Activated`, uses the install encoded key, writes the index archive-limit field in big endian, pads indices and adds the archive envelope's seeded Jenkins hash and offset-dependent checksum. The checksum format is documented in [CascLib's reader](https://github.com/ladislav-zezula/CascLib/blob/38a34665624b8775bb875274b36191b21c38d97b/src/CascReadFile.cpp); the matching constants and validation were also observed in this client's captured code. Encoded BLTE payloads stay unchanged.

After these fixes both the repaired candidate and a completely fresh `1.0.1.27578-native-check` staging folder rendered the original animated title screen. The fresh capture contained no resource-header failure; it contained the expected downloader `no servers` message. CascLib verification still passed after native startup. No beta DLL was injected or account credentials entered.

A diagnostic 60-second run captures local memory and terminates the job; timeout returns failure because it cannot determine gameplay success. `--run-offline` instead keeps the verified client open until the user exits it, with the same network isolation, WMI workaround, job cleanup and scoped permissions. The original client detects a debugger and exits early, so ordinary external debugging did not reproduce the same startup path. Memory/log artifacts must stay outside Git.

## Reproduction

For the subsequent guarded map-loading probe and independent Hanamura/Practice asset checks, see [DISC_ADAPTER.md](DISC_ADAPTER.md).

Use Python 3, Windows x64 and the source-built launcher. Run from the source directory, with a **new empty destination** for preparation:

```powershell
$buildRoot = Join-Path $env:LOCALAPPDATA 'OW1-preservation-build'
$client = Join-Path $buildRoot 'clients\1.0.1.27578'
$iso = Join-Path $env:USERPROFILE 'Downloads\Overwatch 1.0.iso'
python scripts/Prepare-DiscClient.py $iso $client
python scripts/Rebuild-DiscStorage.py $iso $client
cmake -S tools/offline-launch -B "$buildRoot\offline-launch" -A x64
cmake --build "$buildRoot\offline-launch" --config Release --parallel 4
& "$buildRoot\offline-launch\Release\ow1-offline-launch.exe" "$client\Overwatch.exe" --wmi-workaround
# Keep the offline title window open instead of running a bounded diagnostic:
& "$buildRoot\offline-launch\Release\ow1-offline-launch.exe" "$client\Overwatch.exe" --run-offline
```

For the default local installation, `scripts/Start-DiscClient.ps1` starts the root-built helper in the background and leaves the original title window open. It accepts `-ClientFolder` and `-BuildRoot`; logs go to the local build directory. Close the game to end the session and restore temporary folder permissions.

The normal root build includes the launcher at `<BuildRoot>/relay/tools/offline-launch/Release`. `--self-test` performs only the network-isolation probe. `--graphics-test` checks the isolated WMI/graphics behavior. Neither requires game assets. `--snapshot` and `--debug` are diagnostic modes; RVA-specific snapshot assumptions apply only to this build.

Build CascLib externally at the pinned revision, retain its license, then perform read-only verification:

```powershell
python scripts/Verify-DiscStorage.py $client --casclib "$buildRoot\casclib\Release\CascLib.dll"
```

The storage writer refuses an existing `Data` or `.build.info`; it is not an updater. Reconstruct into a fresh staging folder to apply the corrected format. A failed preparation can leave partial diagnostic files for inspection. `Inspect-StartupDump.py <startup-wait.dmp> --logs` prints captured timestamped native diagnostics and accepts `--find <term>` for module strings, without exporting or executing image bytes. Do not feed this build to the fixed-offset beta patcher. The next milestone is a separate fingerprinted client adapter and local authentication/session handling. Private gameplay remains unimplemented.
