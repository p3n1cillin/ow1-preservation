# User-supplied installation disc — 2026-10-11

> Historical experiment. Current development targets final OW1 1.74.0.0.104319. The old ISO is no longer available and is not a current project dependency.

The supplied `Overwatch 1.0.iso` contains a recoverable original **x64 `Overwatch.exe` with fixed file version `1.0.1.27578`**. This differs from the beta `0.8.0.24919` adapter and final retail target `1.74.0.0.104319`. Initial inspection did not run either executable. Subsequent isolated game launch and an opt-in in-memory WMI workaround are documented in [DISC_RUNTIME.md](DISC_RUNTIME.md); the installer was never run and the game file on disk was not modified. The ISO remains unchanged and outside Git.

| Evidence | Observed value |
|---|---|
| ISO size | 5,183,471,616 bytes |
| ISO SHA256 | `363334bbf9926d7ae0ada2f70782b9688f55c1f22b9c718e9ad224caf4c5f842` |
| Volume label | `Overwatch 1.0` |
| Disc index MD5 | `4382d23c457d836f51152703112cccaf`, matches `disc.id` |
| Download identifier in `disc.id` | `c4544ad8ae012afc37606d422e5929ee` |
| Game executable size | 23,996,904 bytes |
| Game executable SHA256 | `8d33644f844b81e830c12749371c80a83d26f81b186265897ca5d67f6e7e665d` |
| Game executable content MD5 | `34c00f0646b42e09f5fc50880f048cd1`, matches embedded install manifest |
| Game executable machine | `0x8664` / x64 |
| Fixed file version | `1.0.1.27578` |
| Game PE timestamp | `2016-03-02T23:44:20Z` (timestamp evidence, not proof of release date) |
| Game Authenticode | `Valid`, Blizzard Entertainment, Inc. |
| Outer setup version / architecture | `1.12.1.2563` / x86, valid Blizzard signature |

The game version string fields are empty. The version comes from the numeric `VS_FIXEDFILEINFO` resource, confirmed independently with pefile and .NET `FileVersionInfo` numeric parts. The inspector now reports `FixedFileVersion` so an empty string cannot hide a present version. The setup program has its own version and cannot identify the game build.

## Packed-data inspection

ISO9660 root contains `disc.id`, `Setup.db`, `Launcher.db`, setup executable, icon, autorun instructions and `data/0000`, `0001`, `0101`, `0102`, `0103`. No setup/autorun instructions were followed. Metadata/root timestamps are March 3, 2016.

The observed `DD` version-1 disc index contains 64,883 records in three archive groups. Experimental read-only parsing checks group bounds and offsets against archive lengths. Scanning all record headers found 64,826 with first BLTE chunk mode `E`, 56 with `N`, and one with `Z`. `E` records were skipped, with no decryption attempted. Thus this inspection does not establish that the game asset set can be decoded or the client installed offline.

Supported `N`/`Z` BLTE records were decoded in memory with size/checksum checks. The install manifest has 14 file entries, including `Overwatch.exe`, launcher, voice/video DLLs and error-reporting runtimes. The game executable was located in archive `data/0103` at relative offset `824160091`, encoded key `ea13112c65675af7a7f0a980718836e4`. Its decoded MD5 and size match the install entry. The executable was extracted for fingerprint/signature inspection to a local build-cache folder, outside the source repository. Small disc metadata and the outer installer are also in that inspection cache; none was executed.

## Reproduce the read-only report

Python 3 is required; optional `pefile` provides embedded PE version details (available and used in this session). The scanner does not write payloads or contact services:

```powershell
python scripts/Inspect-Disc.py (Join-Path $env:USERPROFILE 'Downloads\Overwatch 1.0.iso') --max-records 70000
```

`--max-records` applies per archive; the default 100 is a sample and cannot establish all payload types. The scanner supports this observed ISO9660/DD-v1 layout, not arbitrary UDF/ISO images or Blizzard disc formats. It intentionally does not install a client, decrypt assets, or import credentials. BLTE/install-manifest parsing has synthetic regression checks for checksums, malformed/truncated data, size limits and unsupported encrypted chunks.

Local report: `<BuildRoot>\iso-inspection\disc-report.json`. Extracted game: `<BuildRoot>\iso-inspection\Overwatch.exe`, with `<BuildRoot>` defaulting to `%LOCALAPPDATA%\OW1-preservation-build`. The proprietary ISO, executable and decoded manifest remain outside the repository.

## Compatibility decision

This removes the absence of any original executable for static analysis. It does not provide the specific beta client currently supported by Prometheus, nor the final retail client requested earlier. Do not apply the beta patcher or DLL to this executable. An experimental `.build.info`/CASC layout was subsequently constructed and independently checked with CascLib. An isolated launch now renders the original title/login screen after metadata and archive-integrity fixes; no login or gameplay was verified. See [DISC_RUNTIME.md](DISC_RUNTIME.md).

Native startup resource initialization now passes. Next work for this build is a compatible adapter and local authentication/session handling. A separate fingerprinted adapter would be required. Keep this build as an additional candidate; the final `1.74.0.0.104319` target remains unchanged.
