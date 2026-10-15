# Agent handoff (Claude ↔ Codex)

Last updated 2026-10-15 by Claude (after run 218; previous update by Codex after run 213). Whoever stops
working updates this file. `CLAUDE.md` holds the full research log; this file is
the short "where are we, how do I run it, what next".

## Shared workspace rules (both agents)

- Work only in `Y:\repos\WIP\OW1`. Never leave tools or results only in an agent's
  temp/scratch folder: the other agent cannot see them.
- Public, reviewed code/docs: `tools/`, `tests/`, `protocol/`, `docs/`, root `*.md`.
  Commit and push to `main` (`git push origin main`; "Permission denied" repack
  warnings are harmless).
- Private research (ignored by Git): `.local/`.
  - `.local/re/` — responder, driver, generators, graph dumps, RE notes.
  - `.local/runs/` — per-run logs, screenshots, datagram logs, JSON reports.
  - `.local/claude-scratch/emu/` — Claude's emulator/disassembly toolkit, including
    `image.bin`/`image.base` (decrypted client image; never commit). Run its scripts
    with the working directory set to this folder (they open `image.bin`
    relatively).
  - `.local/claude-scratch/session/` — Claude's dump/patch helpers from the latest
    session (findui.py, inst_list.py, msgnames.py, back2.py, fwd.py, owner.py).
  - Codex: put your equivalents in `.local/codex-scratch/` and list them here.
- Dumps stay beside the original client:
  `C:\Users\lukem\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Local\OW1-preservation-build\clients\1.74.0.0.104319-original\Overwatch\_retail_\retail-private-<run>.dmp`
  (older ones moved to `D:\OW1-preservation-dumps`). Each is ~4 GB; check free space.
- Never publish keys, certificates, dumps, client bytes or captured payloads.
- One bounded run at a time; wait for the launcher's cleanup audit before the next
  run, a build, or CTest.
- Each agent's `%LOCALAPPDATA%` may resolve to a different (virtualized) build tree.
  After the other agent changes native sources (`tools/offline-launch`, relay, etc.),
  run `.\scripts\Build.ps1 -SkipDependencies` yourself before CTest or live runs.
  Example: Codex's 300-second launcher change was missing from Claude's tree until
  rebuilt.
- Check for a running `Overwatch.exe` or responder before starting work: the other
  agent may still have a bounded run in progress.

## Current state (what works in a live run)

Load-in → original SELECT A HERO → pick → spawn in the spawn room in first person →
move/look → fire (Tracer, Soldier: 76, McCree; tracers/impacts, ammo, reload) →
Blink/Recall (server-side teleports) → three training bots that die and respawn →
H in the spawn room reopens hero select, **repeatedly**: run 218 went Tracer → Soldier
(rifle, fires) → McCree (revolver, two volleys, revolver kept). Hero Gallery lists all
heroes (run 198).

## Not working yet (open frontier)

1. **HUD** (health/ammo/abilities/crosshair). UI root graph 0x041a state 20 (node 46)
   must turn true to run 0x120b (creates HUD layers). Its OR terms:
   - AECBBA41(8985E00A): needs a world-owned UI context. The only UI entity (definition
     04000000000001f1) is owned by the global root, so this is false.
   - var 0x09ba: written by graph 0x0bce. That graph is pushed by 0x046b (front-end,
     mode 5/9 only), by 0x17c7 (a key binding) and by 0x1e2f (a toggle). Creating
     0x1e2f client-side did nothing (run 194).
   - F94506DB and B4F19440: special-client global flags.
   - CEFF290A: replay/tournament join string.
   - E95A9C77: constant false.
   Mode 6 is the correct in-game mode; the older "needs mode 5/9" note is wrong.
   Untested ideas:
   - Find what normally pushes 0x0bce or writes 0x09ba in a match.
   - Look for a second, world-owned UI context.
2. **Hero changes and weapons: fixed (run 218).**
   - Codex (runs 204-213) fixed the state encoding behind McCree's vanishing revolver:
     483 one-bit types, BooleanSwitch = active + branch, inactive two-bit entries keep
     their data.
   - Claude (runs 215-218) fixed the re-pick weapon regression. The replacement hero's
     statescript manager is at frame 2 after its graph-create frame (base 1). The client
     queues any full frame whose base exceeds current+1. HERO_SNAP['seq'] was not reset
     on re-pick, so every frame had base >= 4 and queued forever (dump 215: 13 pending
     records, bases 4..18). The responder now resets the sequence on re-pick.
   - H only works while var 0x6321 is false (0x288b switch #160, state 96, H
     LogicalButton in its false branch). The open handler sets 0x6321 for the re-pick
     UI, so the close step now clears it again. Before this, the second H did nothing.
   - StateStack needs two state-data bits; totals alone can hide missing bits (Codex).
3. **Hero-select 3D hero preview and gallery cosmetics.** The user reports no hero
   model in hero select. The backdrop is the map's fixed placed view, which is
   probably correct.
   - The gallery shows 0/0 cosmetics, no skins and no 3D model.
   - These didn't help: lobby 24900 unlock state with real default unlocks, hero
     progression preload (run 203), preview-entity preload (run 195), UI context var
     0x07b2 (run 196 hid the header).
   - Next: find where the per-hero cosmetic catalogue and the gallery/hero-select model
     come from.
4. Other heroes' abilities, bots placed further into the range, damage numbers.

## How to run the current best recipe

Responder: `.local/re/udp_welcome_reply.py` (private). Driver:
`.local/re/run-live-preload.ps1`. Use the Computer Use skill for UI interaction
(the old `ow-menu.ps1` and `ow-ui.ps1` helpers remain in private research).
The game window is 2560×1080.
- Roster y = 928: Tracer x 1700, Soldier 1485, McCree 1000 (more in `CLAUDE.md`).
- CONTINUE is at (1280, 1011).

```powershell
$heroes=(Get-Content 'Y:\repos\WIP\OW1\.local\runs\hero-guids-111.txt').Trim().Split(',')
$base=@{Name='liveNAME';MapRoot=$true;NativeHeaderControl=$true;PlaceableCreate=$true;SelectedEntity=$true;SelectedEntityValue=3221225473;SelectedEntityDelay=30;DefinitionCreate=$true;DefinitionGuid=@('040000000000000e','04000000000003cf','04000000000014d2','04000000000014d2','04000000000014d2');SelectDefinitionIndex=0;SelectDefinition=$true;HeroList=$heroes;PreloadDefinition=@('0400000000000017','0400000000000018','04000000000004bf','040000000000130d');ControllerActor=@(0,1);ServerTime=$true;CreateSends=150;Statescript=@('0','0x288b');StatescriptDelay=60;CreateFlags=@('0:0x30','1:0x80');LateDefinition=@(0,50);HeroHealth='1:200';ControllerComp74='2=0,6=1';ControllerStates='1:35';ControllerStatesDelay=63;ControllerVars='g:7acb=1,0986=1';HeroSelectServer=$true;HeroOnPick=1;CloseHeroSelect=@(1,36);PickGraphs='.local/runs/hero-graphs-125.json';HeroConfigs='.local/runs/hero-configs-180.json';PickWeaponList='1';PickVars='g:001f=i1;10:s29=i1,s53=i40,s6=i40,s5=i1';PickStates='9:39,43;10:0,1,30,31';StateData='16:8=0:1,0:1,0:8,0:1,0:1,0:6;16:9=1:1,0:1,10:4,1:6,0:3,0:1;16:18=0:1,0:1';FireVolley='10:8';ReloadStates='10:9,18,26';ReloadTime=1.4;Ammo='10:53:40:1';FireHold=36;DefinitionSkin=@('2:0x0a50000000001afd','3:0x0a50000000001aff','4:0x0a50000000001b00');Bot=@('2:53.0:2.0:22.8:200','3:56.0:2.0:22.8:200','4:59.0:2.0:22.8:200');Blink=7.5;Recall=3.0;RunFor=300}
& 'Y:\repos\WIP\OW1\.local\re\run-live-preload.ps1' @base      # run in background
# Use Computer Use to dismiss the tutorial, open Training -> Practice Range,
# then observe the roster before selecting a hero. H reopens hero select.
```

Notes:
- Runs sometimes hit the intermittent "early instance failure" (the client exits 0x1
  after about 5-11 datagrams). Retry.
- The cleanup audit (hash, signature, ACLs) is printed at the end of each run's output.
- Recent opt-in responder flags:
  - `--volley-ancestors` (experimental; no longer crashes, unnecessary for revolver fix).
  - `--first-frame-globals` (experimental, no effect).
  - `--ui-entity-var`.
  - `--spawn-at` (also available on the driver).
- Recent driver flags: `-Unlocks FILE`, `-PreloadProgression`, `-VolleyAncestors`,
  `-UiEntityVar`.
- Bounded UDP/CA/TLS diagnostics now allow up to 300 seconds. The driver forwards
  RunFor to the responder (previously hardcoded to 180). Build and all 25 CTest
  targets passed, including 180/181/300 acceptance through the fingerprint guard
  and rejection at 301 seconds. Run 210 hit the known early instance failure.
- Runs 206 and 212 reached the roster too late to establish firing results; run
  207 spawned but its click missed the responder deadline. Runs 208/209 were
  rejected by the old 180-second launcher cap before gameplay. Do not count these
  as successful weapon tests.

## Key analysis tools

- Codex private tools: `.local/codex-scratch/stdt-native204.py` executes the native
  one-bit predicate; `.local/codex-scratch/ssfull204.py` tests two full snapshots,
  including inactive WeaponVolley data. Run these with the emulator directory as
  cwd. Repro outputs are `.local/runs/stdt-204-native.json`,
  `ssfull207-inactive-data.txt`, and `ssfull212-baseline.txt`.
- Dump 200 baseline: PID 30652, hero comp47 0x181436c1b80, counters base 8 / cmfd
  4005 (older values are ignored). Runtime node indices, not STU object numbers:
  states 0,1,2,4,11,12,25,27,34 map to nodes 1,2,4,8,30,31,48,50,61.
- Native global-var reader updates listed UVGu entries without clearing all globals.
  `--first-frame-globals` is unnecessary for the revolver fix.
- Dump inspection: `tools/retail_login_state.py --world-state / --scene-state /
  --replication-state ...` (public).
- Statescript instances and vars on a dump (`.local/claude-scratch/emu/`):
  - `ssnodes.py <dump> <pid> <comp47> <inst> <nodes>`
  - `ssvars.py <dump> <pid> <comp47> scope:var,...`
  - `nodedefs.py` (evaluate any node's condition)
  - `uicheck.py` / `uicond3.py` / `cvreads.py` (UI root terms)
  - `ssfull.py` / `ssfull2.py` (emulate a responder full frame and check alignment)
  - The hero's comp47 comes from `.local/claude-scratch/session/inst_list.py <dump>
    <pid> 80000305` (controller: 80000304; run it from the project root). The PID is
    in `.local/runs/<run>.log` (`PID=`).
- Disassembly: `deob2.py <start> <lo> <hi>` (follows opaque branches). For `.pdata`,
  use `prim.py`/`pdata.py`. Image base for absolute pointers is 0x7ff6a1790000.
- Graph text: `.local/re/stu-dump-89.py <GUID> [out]`.
  - `graph-text-scan-175.py out.json TOKEN` scans all 1586 graphs.
  - Back/forward walkers are `session/back2.py` and `session/fwd.py`.
- Raw GUID bits 48-59 are the 12-bit reversal of (type − 1). Examples: 0x0400 = 3
  (entity definition), 0x0580 = 0x1B (graph), 0x02e0 = 0x75 (hero), 0x0250 = 0xA5
  (unlock), 0x0a50 = 0xA6 (skin theme).
