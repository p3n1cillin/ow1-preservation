# CLAUDE.md — OW1 preservation

Fork of [Prometheus](https://github.com/saturn-xvi/prometheus) (AGPL-3.0). Remotes: `origin` = p3n1cillin/ow1-preservation, `upstream` = saturn-xvi/prometheus.

## Branches
- `main` — upstream Prometheus only (beta 0.8.0.24919 injected DLL + patcher).
- `preservation-foundation` → `codex/public-preservation` — prior Codex work (latest: `bd4092b`).
- `claude/continuation` — current work, branched from `codex/public-preservation`.

## Target client
Final retail **1.74.0.0.104319** (`Overwatch1.74.0.0.104319.7z`, user-supplied, in `%USERPROFILE%\Downloads`).
Exe SHA256 `ef67d348…e0ebe2` (see `tools/offline-launch/retail_profile.h`). Never commit game files, dumps or derived metadata.
Extract with Windows' built-in `tar.exe -xf` (libarchive reads the 7z) into
`%LOCALAPPDATA%\OW1-preservation-build\clients\1.74.0.0.104319-original\`.

## Build / test
```powershell
.\scripts\Build.ps1            # vcpkg deps, relay, CTest, prometheus.dll, patcher
ctest --test-dir "$env:LOCALAPPDATA\OW1-preservation-build\relay" -C Release --output-on-failure
```
Supports VS 2022 (v143) or VS 18/2026 (v145); the script picks generator + toolset. Build root defaults to `%LOCALAPPDATA%\OW1-preservation-build` (outputs, logs, vcpkg worktree, client copy).

## Verified state (2026-10-12, this machine)
- Full build passes on VS 18 / MSVC 14.51; CTest 12/12 (all synthetic; no game files needed).
- The Codex-era build root, dumps and evidence logs were **not present** on this machine; client re-extraction was started. Claims in `FINAL_RETAIL.md` about native loading states are Codex's records, not re-verified here.

## Components
- `server/`, `protocol/legacy_wire.h` — Prometheus beta BSON movement relay (not the original game protocol).
- `tools/offline-launch/` — launches the unmodified retail exe in a network-denied AppContainer; `retail_world_probe.h` holds Codex's native map-loading experiments (fixed RVAs for 104319 only).
- `scripts/`, `tests/` — CASC/STU/manifest inspection tools and their synthetic tests.
- `prometheus/` — upstream beta DLL; fixed beta offsets, **not** retail-compatible.

## Key finding for planning
Codex's retail track tries to load the Practice Range with no server; it stalls because a native metadata request completes with no data. Retail OW1 hosted all maps (including Practice Range) on servers, so map loading likely depends on server-provided state rather than client-side bootstrapping alone. Treat this as an assumption to verify, not a fact.

## Rules
- Distinguish implemented / compiled / tested / runtime-verified. Synthetic relay tests are not gameplay evidence.
- No Blizzard credentials, production endpoints, or third-party private keys/certs (e.g. those in the Plasmawatch login-server checkout).
- Research checkouts live in `Y:\repos\WIP\OW1-research` (several have no license — reference only, never import code).
