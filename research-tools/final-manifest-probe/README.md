# Final OW1 manifest probe

Read-only metadata decoder for the supplied 104319 CMFs, with table bounds,
original content MD5, decoded first-entry and GUID ordering checks. No network
calls or asset extraction. It links the exact provider from external
[TACTLib](https://github.com/overtools/TACTLib/tree/388f8dd6a7e67a72904bab9b5bffaa163ecbe59c)
(MIT), without vendoring it. Keep the included license with built outputs.

```powershell
dotnet build research-tools/final-manifest-probe -c Release -p:TACTLIB_SOURCE_DIR=C:/path/to/TACTLib -o C:/ow1-build/final-manifest-probe
dotnet C:/ow1-build/final-manifest-probe/final-manifest-probe.dll C:/owned-data/Win_SPWin_RDEV_EExt.cmf 473a98cea8209538af13cb0e487f54e4 C:/ow1-build/base-assets.tsv
```

The input's original filename is required for the provider's digest. Refuses
existing output. Output is metadata only; game payloads remain outside Git.
