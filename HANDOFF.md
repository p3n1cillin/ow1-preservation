# Agent handoff (Claude ↔ Codex)

Last updated 2026-10-15 by Claude (after run 251; previous update by Codex after run 213). Whoever stops
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
  Each is ~4 GB. **Keep only reference dumps** (user request, 2026-10-15; 151 old
  dumps deleted, D: copies removed). Current keep set: liveheroc90-250 (0x0c90-on-hero failure, next to diagnose), livehudtrig233 (0x0bcf with HUD node running),
  liveuiroot226 (0x041a on the controller), livehud222 (HUD baseline), liverepick218 (full working recipe),
  livemccree200 (Codex emulation baseline), livebuttons144 (command/reload
  emulation), plus `dumps\instance-sending5.dmp`. Delete each new run's dump after
  analysing it unless you add it to this list.
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

## Latest HUD status (Claude, runs 235-251) — read first

- **Responder bug that invalidated runs 240-246:** loop variables named `_part`
  shadowed the `_part` encoder function, so `statescript_full_payload` crashed
  with "TypeError: 'str' object is not callable". Renamed to `_ccs/_hls/_cgv/_hev`.
  After any client "abort", check `.local/runs/<run>-udp.err` first.
- **Hero HUD chain:**
  - Tracer graph 0x4b state 3 (runner #68) runs 0x01cf (hero HUD) on the hero.
  - 0x01cf: #5 waits for 0x0717, then #41/#49 switches, then #101 waits for 0x1291
    (params 0a4...08fb/08fa = vars 272e/d42a), then stack #149, then presenters
    #155/#159. Stack #84 sets 0x0406.
  - Runtime node index = position in the graph's m_nodes:
    #5=97, #41=1, #49=66, #101=178, #149=179, #155=181, #159=62, #84=126.
  - 0x1291 is sent only by 0x20e4 #187 (client-only STU_38EE1100). Its target #193
    is STU_1D719351, which has no broadcast flag, so it is probably the own entity.
  - 0x20e4 is client-spawned from 0x0c90. So 0x0c90 (and therefore 0x20e4) very
    likely has to run on the HERO, next to 0x01cf.
- **Run 251** (run-247 recipe + new `--server-game-message 1:0240000000001291
  --server-game-message-delay 8`; driver `-ServerGameMessageDelay`):
  - On the dump, 0x01cf #101 is running and waiting, and #84 is running.
    Server-sent 21616 does nothing: the client has NO handler for the 21600 family
    (client->server only; server->client channels are 20300/25000/27500/25800/42900).
  - The statescript message-section mode 1 calls node vtable +0x38. For
    GameMessageEntry states that is 0x1ce5640 = `ret 0`, so it cannot fire #101.
  - Pistols render, no HUD. Its dump was deleted after analysis.
- **Run 250** (`-PickSubgraph '11:0x01cf:6:7;12:0x0c90:0:0' -HeroLateStates '12:0'`):
  - Hero frames broke: pistols vanished, and the dump has hero instances 1-10 only.
  - Emulating the exact sent frame (with and without state 12:0 and the 0x03ac GUID
    global) on dump 239 aligns perfectly (432/441/490/499 bits). So the failure is
    not frame encoding as seen from dump 239's state.
  - **Next:** emulate the same frame on dump 250 itself (the hero's real state at
    that time; PID in liveheroc90-250.log; hero comp47 via `session/comp_addr.py
    <dump> <pid> 80000305 47`).
  - Also check whether StateHero (0x0c90 state 0) on a hero entity resets
    component 47.
- Run 249 (0x0c90 late on the controller) reached #187, but 0x1291 did not reach
  the hero. Its dump was deleted.
- Still open: Blink (the server dead-reckoned teleport drifts into geometry and the
  engine pushes the hero up), Tracer projectile origin (no weapon child entities
  or hardpoints), hero-select 3D preview, Hero Gallery cosmetics.

## Not working yet (open frontier)

1. **HUD** (health/ammo/abilities/crosshair). New chain found (Claude, runs 219-222):
   - The UI manager sets HUD_Root property 6720 from UI-entity var 0x2206
     (0xafd420) and property 6729 from var 0x34f5 (0xafd4a0, default true).
   - Only UI root graph 0x041c writes 0x2206: StateStack state 9 (0x2206 = true)
     under GameMessageEntry state 8, which waits for game message
     0x02400000000006dd. On the dump that entry is running and waiting (instance
     65478, node 19).
   - 0x06dd appears in no code and in no record (466,358 records scanned), so the
     server supplies it.
   - Candidate relay: graph 0x1289 state 9 (STU_38EE1100 client send state, remote
     sync) sends the message held in its sync var 0x3803 (slot 1) to the local UI
     target STU_1D719351.
   - Sending 0x06dd as a server 21616 to the controller or hero does nothing (run
     220).
   - Creating 0x1289 on the controller (`--controller-subgraph 2:0x1289:0:0`,
     `--pick-controller-guid-vars 2:s1=02400000000006dd`, `--pick-controller-states
     2:9`) makes the whole controller frame fail (emulator: interpreter returns 0
     after 3 bits). 0x1289 is not resident even with `-PreloadGraph` (runs 221/222);
     those runs lose hero select.
   - Graph 0x1289 is map-specific. Its only reference is per-map package
     0x0dd0000b0000079f; 0x0dd0 records are per-map packages indexed by map id, and
     Practice 0x688 has no 000b package. It is not how Practice raises the HUD.
   - Of the 36 send nodes whose message comes from a variable, only graphs 0x05ad (a
     server-side gameplay flow) and 0x2fca are resident. 0x2fca is a client
     STU_38EE1100 sender whose message is an array lookup `var c125[var 967c]` (comm
     or emote wheel?); its literal entries are 0x17ab, 0x17ac and 0x15d4.
   - Emulator control: creating resident graph 0x0cb6 in the same controller frame
     parses (114/114); 0x1289 fails only because it isn't loaded.
   - Next:
     - Decide which Practice-resident path sends a variable UI message, or trace the
       client's handling of server statescript "remote messages" (RMFr/TrID,
       0xa0cca0) to UI targets.
     - Check whether any native path forwards entity game messages to the UI entity.
   - Exhausted so far (runs 219-222 plus offline):
     - 0x06dd is absent everywhere checked: 466k raw records (including the
       Practice map packages), 4,885 decoded mode/ruleset/map/definition/UI records,
       all 1,586 graphs (only receiver 0x041c), code immediates and .rdata as a
       64-bit or 32-bit value.
     - Native "send to UI" API: build message 0x1ba7970, set GUID 0x1ba7e20, deliver
       via root vtable +0x110, then +0x18. All 50 call sites use fixed GUIDs, script
       node vtables (0x2622280.., 0x2792fb0..) or unrelated data (43301 = clock
       sync).
     - Exactly one UI manager (vtable 0x26552a8) exists and is root-owned. It
       creates the UI entity in slot 15 (0xb0aee0) with its own owner, so no
       world-owned UI context exists.
     - The UI entity is in no world entity table, so 21616 cannot address it.
     - UI flag updater 0xafd550 on dump 222: 0x08e3=1, 0x0a0d=1, 0x0522=0, 0x1df3=0
       (the last two are used only by front-end graph 0x0151).
   - More negatives (runs 223 plus emulation):
     - Map 0x79f is Rialto (Archives PvE event), so 0x1289 is event-mission UI.
     - No pair of 64-bit code immediates XOR/ADD/SUB to 0x06dd (77,721 movabs
       scanned).
     - Channel-0 handlers 20303..20322 send no UI messages directly.
     - Client UI listeners are global: the root message router dispatches by GUID,
       so any client-side send of 0x06dd would reach 0x041c.
     - Resident client sender graph 0x2fca (#16, message = var 0x25c1[var 0x7c95])
       creates fine on the controller (emulator 115/115). Setting those instance
       vars, or its sync slots s0/s1, crashes in the native value reader (undeclared
       instance vars or wrong slots). Run 223 exits 0x1 at the pick.
     - Responder opt-ins added: `--pick-controller-vars 'inst:key=g<hex>|i<n>|L<hex,..>|b0/1'`
       (GUID lists = kind 15/6 arrays) and `--pick-controller-guid-vars`. GRAPH_COUNTS
       now includes 0x2fca/0x1289.
   - Game-server reliable channels (client receive side):
     | Channel | Family (schema) | Dispatcher | What it carries |
     |---|---|---|---|
     | 2 | 25000 (8f89e0df) | 0x7d1dc0 | 19 handlers 0x6c2xxx..0x6c4xxx; 25003/4/5/7 raise UI messages, all fixed GUIDs (0x8cb, 0xf72, 0xf76, 0xf7b, 0xf7c) |
     | 3 | 27500 (82a2f991) | 0x7d2400 | 0xb12cd0/0xb12d60: three entity ids + u64s (+ floats/bool in 27501) appended to world+0x138 via 0xb11070 = combat events (use later for damage numbers/kill feed) |
     | 4 | 25800 (9f0a9f88) | 0x7d22a0 | 0xaeb2e0..0xaebd80: stats ("Stat: %s", "Shots Fired", time played) |
     | 6 | 42900 | 0x7d1c70 | 7 table entries, no direct calls |
     - 30700 (78 msgs), 22300, 25700, 42800 and 42700: only encoder/decoder
       switches found (0x4b..0x4f range). Their client handlers are registered some
       other way; not yet examined.
     - 30700's id switch is 0x4c1b00 (77 cases, table 0x4c231c). Every case calls a
       per-message decoder (0x4bb240..0x4bd890), so the handlers sit behind a
       further dispatch layer. Next: follow one decoded 30700 message to its
       consumer (0x4be180 is the matching send/encode switch).
   - Session 224-227 (Claude):
     - Full demangled scan of all 467,972 records (every field hash, plus raw, plus
       bits 32-47 wildcarded): the only reference to 0x06dd is receiver 0x041c.
       Live dump 222 memory holds it once (heap listener), never in the image .data.
       Tools: `.local/claude-scratch/session/demangled-ref-scan-224.py`,
       `demangled-wild-scan-224.py`, `dump-qword-scan-224.py`.
     - Server->client handled channels are only 20300, 25000, 27500, 25800 and 42900
       (registrar 0x7d5100). 21600, 30700, 42800, 22300, 25700 and 42700 register
       codecs with NO client handler (client->server only). Field layouts for all
       families: `.local/runs/instance-families-224.json` (`family-schemas-224.py`).
     - Generic client relay graph 0x1d9e (on message var 0x3b4e, send var 0x3023;
       both remote-sync schema vars) exists, but only in other maps' packages
       (definition 04000000000030b8, packages 0dd0000b00000afe/0b56). Preloading
       that definition does nothing (run 224: typed cache absent), so the controller
       frame that creates it fails and hero select is lost. Same gate as 0x1289.
       Resident graphs with variable messages: only 0x05ad (server-side send) and
       0x2fca (local instance-var array, not server-settable).
     - UI root 0x041a created on the controller (`--controller-subgraph
       2:0x041a:0:0`, GRAPH_COUNTS (16,33), state types in graph-state-types.json):
       hero select/spawn still work, but none of its nodes run, because its entries
       are not client-only (run 225). Activating state 25 (0x120b runner, state data
       0:1,3:4,0:1) makes the runner node run but spawns no child (run 226). Creating
       0x120b as its child (3:0x120b:2:38) plus state 15 (HUD_Root STU_501733D7)
       makes the client exit 1 on that frame (run 227). Don't relocate UI graphs.
     - UI manager slot 6 (0xafb740) creates HUD_Root (layer 0502, 0a88..01c3) at
       startup, so HUD_Root exists; visibility is property 6720 = UI var 0x2206.
     - New private responder option `--controller-guid-vars` (driver
       `-ControllerGuidVars`): GUID instance vars from the first controller frame.
   - Session 228-234 (Claude): **FRAME ALIGNMENT FIX.** 0x288b state 35 is a
     StateStack; the native StDt reader (0x1b96460) reads 2 state-data bits (+0x238
     is-top, +0x239 is-under) after its entry, but the recipe sent none. Every
     controller frame since hero select was 2 bits short; harmless only while all
     following bits were zero. Any later instance with active states (0x041a, 0x120b,
     0x0bcf) was misparsed, which explains run 227's crash. The baseline recipe now
     has `StateData='288b:35=0:1,0:1;...'`; emulation aligns exactly (116/116).
     - HUD_Root binding names (layer 0502 strings): `ShowDistortion` (prop 6720 = UI
       var 0x2206, message 0x06dd) and `ShowHeroHud` (6729 = 0x34f5, default true).
       So 0x06dd is the distortion effect, NOT the HUD gate. Drop that lead.
     - HUD_Root is displayed only by node type STU_501733D7 (mode switch 0x9c2380:
       mode 4 -> 0x9cf9b0 shows HUD_Root; node waits in mode 0 until its load input
       plug STU_2561471D fires, handler vt+0x198 0x9c2490 -> 0x9cad70 job +0x1c0).
       Only two graphs contain it: 0x120b (UI root 0x041a branch, gated by special
       client flags/selected-entity term that is false for the root-owned UI entity)
       and 0x0bcf.
     - 0x0bcf is the HIGHLIGHT/REPLAY viewer graph (resident; 128 sync vars, 86
       states). Creating it on the controller (`--controller-subgraph 2:0x0bcf:0:0`)
       and activating StateStack state 1 with is-top (`bcf:1=1:1,0:1`) shows HUD_Root
       (the orange network-warning icon appears top-left, run 231). State 3 = its
       HUD_Root node (enters, mode 0, no load). States 22/25 start "LOADING
       HIGHLIGHT" (run 234). Not the live-play HUD path.
     - The StDt mask covers all `m_states` (graph data +0x60 list); entries of a
       newly created instance are not read in its creation frame.
     - New: public probe `--lobby-preload-stack-item` (raw 0x0d60; these are IDs, no
       records exist), private responder `--pick-controller-messages 'inst:node:width'`
       (one-shot mode-0 entry triggers, driver -PickControllerMessages), GRAPH_COUNTS
       for 0x0bcf/0x041a/0x1d9e.
     - User-reported bugs (run 229 play): Blink can launch the hero into the air
       (server-side teleport to an estimated position), and Tracer's tracers start
       at her stomach (no weapon child entity/muzzle hardpoint, so effects use the
       hero origin).
   - Remaining hypotheses: the server delivers UI messages through a channel not
     yet decoded (e.g. statescript frame remote-message section RMFr/TrID on an
     entity whose client graph relays to UI), or a native path with an obfuscated
     GUID constant.
   - The older 0x041a state-20 analysis below is now secondary.
   - Old analysis, 0x041a state 20 terms: AECBBA41 (UI entity is root-owned), 0x09ba
     (0x0bce: front-end/menu paths), special-client flags, replay string, constant
     false.
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
$base=@{Name='liveNAME';MapRoot=$true;NativeHeaderControl=$true;PlaceableCreate=$true;SelectedEntity=$true;SelectedEntityValue=3221225473;SelectedEntityDelay=30;DefinitionCreate=$true;DefinitionGuid=@('040000000000000e','04000000000003cf','04000000000014d2','04000000000014d2','04000000000014d2');SelectDefinitionIndex=0;SelectDefinition=$true;HeroList=$heroes;PreloadDefinition=@('0400000000000017','0400000000000018','04000000000004bf','040000000000130d');ControllerActor=@(0,1);ServerTime=$true;CreateSends=150;Statescript=@('0','0x288b');StatescriptDelay=60;CreateFlags=@('0:0x30','1:0x80');LateDefinition=@(0,50);HeroHealth='1:200';ControllerComp74='2=0,6=1';ControllerStates='1:35';ControllerStatesDelay=63;ControllerVars='g:7acb=1,0986=1';HeroSelectServer=$true;HeroOnPick=1;CloseHeroSelect=@(1,36);PickGraphs='.local/runs/hero-graphs-125.json';HeroConfigs='.local/runs/hero-configs-180.json';PickWeaponList='1';PickVars='g:001f=i1;10:s29=i1,s53=i40,s6=i40,s5=i1';PickStates='9:39,43;10:0,1,30,31';StateData='288b:35=0:1,0:1;16:8=0:1,0:1,0:8,0:1,0:1,0:6;16:9=1:1,0:1,10:4,1:6,0:3,0:1;16:18=0:1,0:1';FireVolley='10:8';ReloadStates='10:9,18,26';ReloadTime=1.4;Ammo='10:53:40:1';FireHold=36;DefinitionSkin=@('2:0x0a50000000001afd','3:0x0a50000000001aff','4:0x0a50000000001b00');Bot=@('2:53.0:2.0:22.8:200','3:56.0:2.0:22.8:200','4:59.0:2.0:22.8:200');Blink=7.5;Recall=3.0;RunFor=300}
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
