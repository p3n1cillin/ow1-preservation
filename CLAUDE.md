# OW1 preservation continuation

Continue the existing implementation; do not restart or replace working systems.
Public AGPL-3.0 fork: https://github.com/p3n1cillin/ow1-preservation.
Upstream: https://github.com/saturn-xvi/prometheus. Active branch is `main`, which
includes `codex/public-preservation` and Claude's continuation. Historical
`preservation-foundation` is a parallel private development reference; do not
merge or publish its history without checking what it contains.

## Active client and local files

Target **1.74.0.0.104319**, supplied as
`C:\Users\lukem\Downloads\Overwatch1.74.0.0.104319.7z`.
The 1.0 ISO is gone and is not required for current development.
Original executable SHA256:
`ef67d348ecca066ce1698683fd0fd810075357164b345d83ed9296d676e0ebe2`.
The extracted client, outputs, captures and generated reports are available under
`%LOCALAPPDATA%\OW1-preservation-build`; check before extracting again. They may
resolve through Codex's package-local filesystem virtualization. Keep original
client/archive unchanged on disk and proprietary bytes outside Git. Never
publish credentials, keys, generated certificates, dumps or client assets.
Research checkouts in `Y:\repos\WIP\OW1-research` include unlicensed projects:
reference only; do not import their code or bundled credentials.

## Commands

```powershell
.\scripts\Build.ps1 -SkipDependencies
ctest --test-dir "$env:LOCALAPPDATA\OW1-preservation-build\relay" -C Release --output-on-failure
.\scripts\Start-RetailClient.ps1 -Mode PracticeMetadata
.\scripts\Start-PrivateClient.ps1 -RunForSeconds 90
```

Omit `-SkipDependencies` for a first build. Build.ps1 uses VS 2022/v143 or
VS 2026/v145 and preserves an existing CMake generator. Private diagnostics need
`tools/bnet-probe.py` with our own local certificate/key and host port 21119.
The client sees container loopback port 1119 through a named-pipe bridge.
No Internet/LAN capabilities are granted. Bounded runs stop owned jobs, save
a local dump and restore scoped ACLs. Wait for launcher exit before checking
restoration or rebuilding its executable.

## Real frontier, 2026-10-12

- Original final title/login was user-confirmed. Automated capture has been
  unreliable; do not claim a rendered world from a native loading state.
- Practice header loading and native default-context activation work. Immediate
  updates return state 4, but the context stays unready and its cache is empty.
- **SDK result correction:** kind 13 is local Hotfix-directory enumeration.
  Flag 1 = success, 0 = structured error. Captured status/domain/code = 3/2/-1
  at action +18/+19/+20. +138/+140 are successful data/count fields. Earlier
  empty-backend-reply/error-at-+140 claims are superseded.
- The private TLS bridge works at transport level. A fresh bounded run reaches
  our observer twice and closes before handshake completion. No decrypted RPC
  or working private authentication has been captured.
- Candidate TLS writes fail Win32 87 on execute-read MEM_MAPPED pages.
  **ACG is not established:** queried dynamic-code policy flags are 0, including
  after failures. Do not repeat the old diagnosis or assume injection fixes
  the mapping constraints. Generic short pattern matches are not proof of
  relocated functions. No alternate full-page copies were found in the dump.
- The original final executable hash/signature remain unchanged. No final map,
  controllable hero, authoritative match or 6v6 matchmaking is verified.

Next: establish narrowly scoped trust for our own loopback TLS service, capture
the real first RPC, then implement demonstrated login/session interfaces.
Independently trace native Hotfix/cache initialization. Never fabricate
completion/readiness/state flags as gameplay success.

`server/` is a synthetic BSON movement relay, not final OW1's protocol.
`prometheus/` is the fixed-offset beta DLL, not a retail adapter.
Final probes live in `tools/offline-launch/`; use their exact-build guards.
No Blizzard production credentials/endpoints or third-party private keys.

See `docs/PROJECT_STATUS.md`, `FINAL_RETAIL.md`, `ROADMAP.md`, `RESEARCH.md`,
`COMPATIBILITY.md`, `FEATURE_MATRIX.md`, `TESTING.md` and `DEVLOG.md` for the
existing status/research/matrix/test/log equivalents requested in the handoff.
Distinguish implementation, compilation, synthetic tests and native runtime
evidence. Successful relay tests do not complete original-gameplay milestones.
