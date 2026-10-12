# Final OW1 acquisition experiment — 2026-10-10

**Update 2026-10-12: the user supplied the exact final OW1 archive; extraction, fingerprints and offline manifest checks passed. See [FINAL_RETAIL.md](FINAL_RETAIL.md).** The CDN experiment below remains historical evidence.

**Original experiment result: the requested final OW1 client was not downloaded through BlizzGet.** BlizzGet's NGDP retrieval code could access current metadata and some configurations, but the final OW1 build configuration was unavailable at the tested paths. No substitute OW2/beta/PTR client or game content was downloaded.

The primary metadata record is [US/pro/104319/versions at archive commit ae8ae8a](https://github.com/mdX7/ngdp_data/blob/ae8ae8a07c9f27985ed271ecbc0e762dea1a5314/US/pro/104319/versions), dated 2022-09-30, preceding the [October 3 OW1 service shutdown](https://overwatch.blizzard.com/en-gb/news/23852690/).

| Metadata field | Value |
|---|---|
| Version / BuildId | `1.74.0.0.104319` / `104319` |
| Product | `pro` |
| BuildConfig | `786a31729ba1c684a5c80fbaf7cb92b8` |
| CDNConfig | `930762d51b18d263c9a1d3dc2b51af26` |
| ProductConfig | `b57914660da2a68617669c8dae267d9a` |
| Versions sequence | `1321808` |

US/EU/CN/KR metadata agrees in that archived record. It identifies the final target; it is not proof the CDN still serves its files. The archive directory contains version metadata, not the required complete build configuration or game payload.

## Actual attempts

Cloned BlizzGet at `2764ef6a378a1a3e85bf002d946898b417d747d2`. Its GUI project targets an older Win32 compiler and initially fails under v143 due to a missing `<string>` include in `src/frameui/window.h`. An isolated local include repair was made, but the complete GUI was not rebuilt or used. Instead, the original NGDP and WinHTTP source was compiled with a small newly authored x64 command-line probe. That probe uses the original config URL selection and does not download content archives.

The current live `pro` metadata returned `2.25.0.0.154088`, build config `c80f7be2605b7909b2f77200d6c76148`, with no historical builds list in the current CDN configuration. A control lookup of that current config returned HTTP 200. Another older OW1 PTR control config `5feb299b72497fab4eb728473fa95462` returned HTTP 200 and identified `1.64.1.0.86609-PTR`; only its config was fetched. Neither control is the requested final retail version.

Final hash lookup through BlizzGet returned:

```text
ADVERTISED_BUILDS=(none)
BUILD_CONFIG_HTTP_STATUS=403
exit code: 3
```

Additional direct endpoint checks of `/tpr/ovw/config/78/6a/786a31729ba1c684a5c80fbaf7cb92b8`:

| Endpoint | Observed result |
|---|---|
| `https://level3.ssl.blizzard.com` | 403, S3 AccessDenied response |
| `http://level3.blizzard.com` | 403 |
| `https://eu.cdn.blizzard.com` | 404 |
| `https://us.cdn.blizzard.com` | 404 |
| `http://blzddist1-a.akamaihd.net` | 404 |

These results establish failure through the tested paths, not permanent deletion or impossibility of retrieval through every CDN/cache. A 403 was not bypassed. Without this config and the referenced encoding/root/install manifests, BlizzGet cannot reconstruct the requested build. Config availability alone would still not prove every required content blob remains available.

## Reproduce the prerequisite probe

Keep BlizzGet outside this repository. From the repository root in PowerShell:

```powershell
git clone https://github.com/d07RiV/blizzget C:\ow1-research\blizzget
git -C C:\ow1-research\blizzget checkout 2764ef6a378a1a3e85bf002d946898b417d747d2
$probeBuild = Join-Path $env:LOCALAPPDATA 'OW1-preservation-build\blizzget-probe'
cmake -S research-tools/blizzget-probe -B $probeBuild -G 'Visual Studio 17 2022' -A x64 -DBLIZZGET_SOURCE_DIR=C:/ow1-research/blizzget
cmake --build $probeBuild --config Release --parallel 4
& "$probeBuild\Release\blizzget-probe.exe" 786a31729ba1c684a5c80fbaf7cb92b8
```

The checked-in probe contains only newly authored glue; external BlizzGet code is not vendored. The committed probe was separately compiled and rerun against the final hash with the same 403 result. ASCII metadata lookup passed; warnings about pointer truncation in BlizzGet's x64 UTF8 implementation mean this experiment does not validate a complete downloader. Do not distribute the linked probe binary until external code redistribution rights are established.

Next useful input is an authorized complete backup, or evidence of another available public build-config/content source for this exact hash. A backed-up folder's `.build.info`, executable version/SHA256 and CASC files are needed together. Preserve an untouched copy outside this source repository. `scripts/Inspect-Client.ps1` performs read-only executable inspection and does not patch or execute it. Retrieving the final client would begin retail adapter research; the current beta DLL would still not become compatible automatically.

## Archive retry — 2026-10-11

Rechecked the user-supplied [EU/pro archive](https://github.com/mdX7/ngdp_data/tree/master/EU/pro). Its final 104319 metadata agrees with the earlier US record. Build 46510 is `1.23.0.1.46510`, BuildConfig `7f5122113fdd832af624edfdd1603468`; 46510 is the build ID, while this file's actual metadata sequence is 6917. The disc's 27578 metadata identifies original BuildConfig `6bced84bccd049d6dae94aa6b7050a53`; the reconstructed disc configuration remains explicitly inferred.

The archive's `versions` files contain config hashes, not complete build configs or payloads. Its small `blob/game` and `blob/install` entries are metadata, not a client backup. Retried these three exact hashes through HTTPS EU/US/level3 hosts, including both the legacy `tpr/ovw/config` and the advertised `tpr/configs/data` path: level3 returned 403, EU/US returned 404. Re-ran the source-built BlizzGet probe for the final hash: current metadata succeeded, final BuildConfig returned 403 again. No game payload was downloaded. Historical instructions about version availability do not establish CDN availability today.
