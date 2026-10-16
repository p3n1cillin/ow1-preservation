# Agent handoff (Claude ↔ Codex)

Last updated 2026-10-16 by Codex (after runs 294/295; HUD message delivery verified, root display unresolved). Whoever stops
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
  dumps deleted, D: copies removed). Current keep set: livemode18-295 (authored Practice wrapper and four client children, PID2488, hero comp47 0x276c4c06640, controller comp47 0x276c4c07860), livemode18-294 (hero fallback HUD widgets created, PID30008, hero comp47 0x15f57aa6640, controller comp47 0x15f57aa7860), livemode18-292-e2 (Recall mirror stage3 active, PID21500, hero comp47 0x1f031996640), livemode18-283-e1 (0.25 s after a first E press; Recall prediction already rolled back, PID 22460, hero comp47 0x13a4b356640), livemode18-272-shift (Shift held, button lists), livemode18-275 (native Blink + Recall states), livemode18-264 (mode-18 HUD routing), livemode18-257 (mode-18 pre-pick emulation base), livehudowner254 (ownership/message audit), liveheroc90-252 (HUD ownership
  comparison baseline),
  livehudtrig233 (0x0bcf with HUD node running),
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
native Tracer Blink with collision and server-tracked charges → 13 static training bots →
H in the spawn room reopens hero select, **repeatedly**: run 218 went Tracer → Soldier
(rifle, fires) → McCree (revolver, two volleys, revolver kept). Hero Gallery lists all
heroes (run 198).

Recall, HUD, authored bot movement and complete combat/roster behavior remain
unresolved. Historical teleport recipes are not the best baseline.

## Recall prediction mechanics (Claude, 2026-10-16, runs 299-304) - read first

- **Live sampler:** `.local/claude-scratch/session/recall-addrs-300.py <dump> <pid>`
  (resolve hero instance-1 node/queue/clock addresses from a dump of the
  running client) + `livesample-300.py <pid> <secs> <out.jsonl> label=addr:size ..`
  (ReadProcessMemory at ~30 kHz, logs changes). Logs `.local/runs/30x-sample.jsonl`.
- **40-tick reconcile:** 0xa0b200 (called from 0xa093e0) takes the client tick
  (0x979210 -> 0x7fc490 -> vt+0x10) minus 0x28; once the oldest predicted entry
  is older, it sets instance bit 10 (inner vt+0xd8 0x97b060), restores
  (0xa0f5d0) and replays (0xa0ab00). Live 301/302/304: E is predicted (states
  17/3/9/15/23 on, queue fills) and exactly 0.64 s later all drop.
- **CmFD is in client ticks:** the interpreter stores it at manager +0x900 and
  uses the current tick when 0; the hero graph-create frame has no CmFD, so
  +0x900 starts at the client tick. Our hero frames sent 4000+seq (future).
  New `--hero-cmfd-ticks` (driver `-HeroCmfdTicks`): CmFD = max(prev+1, last
  command seq + 8) per hero frame change. Live 302: spawn/pistols fine, CmFD
  1669; Ability +0x270 now resets to 0 after the reconcile (before: stuck 3).
- **Rewind state 0 must start locally:** its enter handler 0x8ed090 (vt+0x280)
  returns immediately when edx == 2 (server restore); its normal path sets
  +0x238 (end time = now + config*1000 ms) and the history index +0x270 that the
  update 0x8ee160 requires (+0x270 == -1 skips movement). So server-entered
  state 0 (runs 299/303: active 1.3 s with correct start time) never moves.
- Live 303 (cmfd ticks + mirror + phase B): mirror and phase B apply; state 0/1
  run server-entered; no movement; client exit 0x1 ~0.45 s after mirror-off.
  Live 304 (cmfd ticks + mirror phase A only, 3 s): states still drop at
  +0.64 s despite the server frame listing them active; mirror-off did not
  crash. State 3's update is vt+0x60 (0x8e5a90): re-queues state 3/31/11
  records; state 3's runtime def +0xf8 = var 0x018b cv (+0xf0 null; the slot
  0x90 listener reads +0xf0, so it is not the end path). What really ends state 3
  (likely the wind-up anim via DataFlowMapping 10) is not established.
- New responder options (all opt-in, not in the best recipe): `--recall-var`
  (instance UVGu var write mid-mirror), `--hero-pulse`, `--recall-phase2` token T.
- **Load-in race fixed:** run 300 lost hero select because graph creates (33 s)
  went out only 1 s after the controller create (32 s); best recipe now
  31/32/34/36 and controller full frames wait for 60 graph-create sends.

## Session 297-298 (Claude, 2026-10-16) - read first

- **Live testing blocked:** runs 297/298 hit the Windows lock screen (ow-ui
  "CopyFromScreen ... handle is invalid", u0 screenshot shows the lock screen).
  No hero pick happened; both cleanups passed. Re-run when the desktop is unlocked.
- **Recall two-phase server timeline (ready, untested live):** state 3
  (54feb21c, container of 9/10/11/23) ends only via its var-change listener
  (0x8e5f50 slot 0x90 -> 0xc880c0 finish) when instance var 0x018b is true.
  0x018b is referenced only by state 3 (not synced, no writer in any decoded
  graph), so the server must drive 3 -> 0. Emulating that finish
  (`session/recall-phase2-296.py`, from Codex's serializer) starts rewind 0 plus
  1/2/31. Native writers give data: Stacks 15/28/33/35 = `1,0`; 1/2/22/37 = one 0
  bit; 17/31/36 = none. **State 0 data = 80 bits:** its reflected object
  (vt+0x168 = 0xd44bf0 -> node+0x1c0, descriptor image+0x3168080, one s64 field
  +0x78, hash 0007bf47) is read as 8 raw bytes from the current bit position
  (0x1b71930 writeback keeps the sub-byte offset; the 193 -> 257 jump is real),
  then the class's u16 (node+0x970). Phase-B frame with `0:64,0:16` decodes
  725/725 and starts nodes 1/2/3. The s64 is the client statescript clock when
  state 0 began (emulated: owner+0x1e0). That clock is the hero's command tick:
  dump 283-e1 owner+0x1d0 = 2398 vs E at command seq 2341 ~0.9 s earlier;
  ms = tick*16 (+15). Responder token `T` in phase-2 data = (E command seq +
  delay/16 ms)*16; recipe `.local/runs/run-livemode18-299.ps1` uses
  `1a/0=T/64,0/16`.
  New responder option `--recall-phase2 'DELAY:ON:OFF:G/S=d/w,..'` (driver
  `-RecallPhase2`). **Live 299 result:** phase A (cmd seq 2270), phase B at
  +0.4 s (start time T = 36720) both accepted (81 client datagrams after
  phase B), but **no rewind/movement** during ~1.3 s of server-entered state 0.
  The client exited 0x1 on the mirror-off frame (0 datagrams after it); the
  same off frame decodes 600/600 offline, so the exit is semantic (exiting the
  server-entered rewind), not alignment. Conclusion: like Blink, server-driven
  ability states do not move the hero; Recall needs the client's own
  prediction to survive. Do not ship the mirror; the best recipe has none.
  Open question remains why the live client drops its predicted Recall
  states within 0.25 s with no server frame (283-e1).
- **HUD gate var 0x2af6:** 0x01cf presenters #155 (runtime 181, layer 05a7) and
  #235 are gated by `NOT var 0x2af6`. On 294, 0x2af6 = true in hero 0x01cf
  instance 11 and controller 0x20e4 instance 4. Its only writer is client-only
  Stack #311 (state 109, node 155; 0x20e4 #399), under GameMessageEntry #5
  plug m_452862E6 (0x0717 received; #5's normal branches are active too).
  0x2af6 is not synced in either graph. A server pulse that exits state 109
  (new `--hero-pulse 'DELAY:inst:graph:state:data:HOLD'`, driver `-HeroPulse`)
  exits node 155 in emulation (556/554 bits), but 0x2af6 stays true afterwards,
  so the exit alone does not clear it. Semantics of Stack out-var / the presenter
  condition (show vs hide) still to settle.
- Map tag markers (empty tag components, positions from 294): 15 x [1,110],
  18 x [1,111], 10 x [1,38]; the [1,38] set lies at y ~6.5 on a loop
  (42,-0.5)...(46,-28)...(62,-37)...(95,-12)...(79,10.5), possibly a patrol
  track. Unconfirmed.
- **Pistol/muzzle:** replicated component states found via vtable decode
  0x5d6b20 (`session/compstate-297.py <dump> <pid> <entity> <types>`): comp 26
  = u64 (filter bits, flags 2), 69 = u64, 90 = one field, 136 = {s32, entity,
  entity, s32, s32} (hashes 373dbf32/2ec62fac/c7927090/a2141aef/e2894f84; on the
  hero all zero, last -1). Components 1/3/4/82 have no replicated state. Comp
  136 is the only candidate parent/attachment link so far (added by create-flag
  0x80 builder). Create records have only placeable/definition kinds; no
  pending child rows after the hero create.

## UI root 0x041a is the observer/tournament path, not the play HUD (Claude, 2026-10-16) - read first

- Native evaluation on reference 295 (`.local/claude-scratch/session/uiroot-terms-296.py
  <dump> <pid> <UI comp47> 65535 46,52,53`, env `MODE=1`): switch node 46 and
  node 52 are false, node 53 true. **Set the instance owner mode first:** state
  entry copies node def+0x74 into inner+0x4c0 (here 1), and inner vt+0x240
  (0x979280) switches on it. With the dump's leftover mode 0 the selected
  entity resolves to nothing. With mode 1 it resolves to controller 0x80000304.
- Node 46 = AECBBA41(selected) OR global 0x09ba OR (F94506DB AND B4F19440) OR
  CEFF290A OR E95A9C77; all five false. AECBBA41 (0xcec6c0) reads component 44,
  then component 25 via 0xc1ecd0: comp25+0x58 bit 28 set AND team (0xb8af40,
  bits 23-27 -> 0..4, else -1) == -1. The local-session builder 0x829430
  sets 0x10040001 | (0x800000 << team). Our controller/hero comp25+0x58 = 0
  (filter bits are never sent). Setters: 0xb8af90 (comp26 state+0x78 or
  comp25+0x58) from 0xb21790/0x6c9f40, and 0xb8bdf0 (OR) from 0x7e37e0.
- **Node 52 = B36E804B = config byte image+0x2e39138** (evaluator 0x91af30).
  Registration sets 0; only the `tank_ShowMode` preset 0x1807e20 and the
  `tank_TournamentMode` preset 0x1807f10 (config keys checked in 0x17e3d70 via
  0x1839600) set it to 1. Node 46's false branch (#25) is empty. So the
  0x041a -> 0x120b HUD_Root branch is for show/tournament observers. **Do not
  chase 0x041a/0x120b for the player HUD.** The play HUD has to come from the
  hero/controller presenters (0x01cf, 0x20e4) and the startup-registered
  HUD_Root (UI manager +0x58, created and added in 0xafb740 -> 0x1dc9c10).
- Filter bits still matter elsewhere: Recall's gate 0xc1d860 reads comp25+0x58
  bit 10, and hostility/teams depend on them. Their network path (module 2 /
  0xb22900 / 0xb21790) is still not decoded.
- Widget census (`session/widgets-296.py <dump>`, vft I+2644a08; reports
  `.local/runs/widgets-257.txt` / `widgets-294.txt`): all UI widgets use context
  id 0x1800 (index 3, table global image+0x2ebaaf8). Top-level widgets (HUD_Root
  0502, hero select 008c, hero HUD 059d/05a7/05d0) share one top-level array.
  The HUD widgets in 294 have +0x90 = 0 (attached by deferred command
  0x1c635d0 -> 0x1c648a0, vt 0x27c9e50). HUD_Root has no children
  (+0xa0 count 0); the HUD widgets are top-level, not under HUD_Root.
- Visible vs hidden hero-select widget (257 vs 294, `qdump.py`): +0x60/+0x64 is
  -1/0 while shown and 0x21/1 while hidden. The 294 HUD widgets have -1, so they
  are nominally shown but draw nothing; next suspect is their data binding
  (local player/hero context), not attachment. I+27f7fc0 references are not a
  visibility marker (the hidden hero select still has them).
- Presenter vs widget wiring (294/257): `m_45017CEA` is the presenter's
  published widget-handle variable, not its parent. Type-7 handle =
  {state index, instance id}: controller 0x20e4 instance 4 has 0x2ad4 =
  0x900040004 (state 9) and 0x2e27 = 0xa00040004 (state 10); hero globals hold
  0x23000b0004 / 0x28000b0004 (0x01cf instance 11). Hero select's handle var is
  0x07b2 (unset). Startup layers by serial: 1 = 0273, 2 = GameLayer 029b,
  3 = HUD_Root 0502, 4 = MenuLayer 029c, 5 = 0503, 6 = DialogLayer 0514,
  8 = System_Clock 0513. All have show state -1. Visible hero-select presenter
  node vs HUD presenter nodes differ at +0xf0 (1 vs 0), +0x240 (1 vs 0x20/0x23),
  +0x250/+0x258 (one-entry array vs empty); meanings not established.
  0x01cf presenters 155/235 are gated by `NOT var 0x2af6`.
- **Muzzle origin (Tracer shoots from the stomach):** graph 0x16 CosmeticEntity
  states 0/1 (runtime nodes 1/2, vt 0x2630450) look up child pistol entities
  by identifier 0x1b9b/0x1b9c on hardpoints 0x0a/0x0b and publish them in
  synced vars s49 = 0x0031 / s50 = 0x0032. Volley #230 fires from hardpoint
  0x06 of those entities. On 294 both nodes hold -1 at +0x1d0/+0x1d8 and
  0x31/0x32 do not exist. Tracer's definition 0400...0001 lists
  `m_childEntityData`: 0x0169 at hardpoint 0x11 and two 0x0017 pistols at 0x0b/0x0a
  with identifiers 0x1b9c/0x1b9b. **No child entities are created** (the only
  class-6 entities with components [1,3,4,82] are map objects far from the
  hero). The visible pistols come from another path. The create record has
  no parent field (0x78dab0: flag 1 type/skin, 2 movement snapshot, 4 scale,
  8 transform). Next: find how child entities are instantiated or replicated
  (runtime STUEntityDefinition descriptor image+0x3090590, size 0x50, array
  field at +0x38 is the child list candidate), then sync s49/s50.
- Mask-getter ids (`session/maskid-296.py`): 0xbcacb0 = comp 25, 0x5d4520 = 26,
  0xbd59a0 = 44, 0xbd5ef0 = 50, 0xbc9610 = 57. Module-2 sections (0xb40130,
  0xb24600, 0xb22900) work on component 50, which our controller and hero
  lack. 0xb21790 (comp 26, calls 0xb8af90) is called from 0xae43f0; it looks
  like local game-mode spawn logic.

## Codex continuation, runs 294/295 (2026-10-16) - read first

- **Correction to the earlier HUD diagnosis: message 1291 and its parameters
  do reach the hero.** On reference 264 the native evaluator reads valid type 7
  widget handles for both parameters. Existing raw STU labels are byte strings:
  `272e` = numeric variable 0x2e27, `d42a` =0x2ad4, `ed73` =0x73ed. Looking up
  numeric 0x272e/0xd42a/0xed73 queried different variables. Correct numeric IDs
  work with `ssvars.py`; this is not evidence of a separate hidden UI store.
- Authored listener 178 (0x1cf object 101) selects between two owner branches.
  While sender 15 (0x20e4 state 13) exists, Stack 180 sets owner 0x73ed to the
  selected controller; hero Stack 179/presenters 181/62 are inactive by design.
  When the sender disappears, Stack 179 selects the hero and its presenters run.
  Thus inactive hero presenters alone do not establish failed delivery.
- Offline `.local/codex-scratch/hud294-sender-off264.py` sends a normal full
  controller frame ending state 13. Native decoding consumes 170/170 bits, calls
  the sender exit, then the hero listener switches branches and begins 181/62.
  `hud294-params264.py`, `hud294-stack264.py`, `hud294-outputs264.py` and reports
  under `.local/runs/hud294-*` preserve the read-only/causal comparisons.
- Live 294 adds `RetriggerExtraStates='4:-13'` to the best recipe, plus the known
  sender data. Sender 13 ends; hero 179/181/62 become active and real widgets
  exist at 181/62. Controller widgets also remain. **HUD is still invisible.**
  UI root graph 0x041a node 46 condition is false and no 0x120b child is present in
  the UI component. This moves the next investigation to root display and
  attachment, not missing 1291 delivery. All seven cleanup checks pass; UDP
  stderr is empty. Keep 294 as the fallback-widget reference.
- Private emulator `ssfull2.py` now loads mode18-255 metadata as well as 180.
  Previously its default omitted 13c1/20e4 state types: a supposed sender exit
  could instead decode as data and leave the sender running, even with equal
  total bit counts. `SS_HERO_CONFIG=hero-configs-mode18-295.json` can add a
  further recipe's metadata. `hud294-encoder-check.py` verifies the one-bit
  exit and active+compact-u16 entry; `hud295-encoder-check.py` verifies override
  loading. Check state types and actual exit/enter events as well as alignment.
- Live 295 tests the authored Practice wrapper: controller 13c1 state 43 runs
  graph 288a, created as instance 5 under 3:43, runner data names 5. Private recipe
  `run-livemode18-295.ps1` / config `hero-configs-mode18-295.json`. Native
  creation replay 218/218; live wrapper client nodes start graphs 2951/2931/
  2939/28fe. Hero selection and Tracer first person remain. HUD stays absent,
  including after opening/closing Escape menu and an Alt+Z keypress pair.
  Root 041a condition remains false. All seven cleanup checks pass, UDP stderr
  empty. Keep 295 as the authored-wrapper reference. No best-recipe promotion.
- `hud294-live-audit.py` / `hud295-live-audit.py` and matching text reports
  resolve the UI component through root router vt+0x10 without a dump scan.
  Reference 294 UI comp47=0x15e681e7620, root041a instance0x15e491dc550;
  reference 295 UI comp47=0x2758e017620, root041a instance0x2764fc8cd70.
- Next: inspect actual HUD root loading/display and widget attachment using
  these working ownership branches. Preserve the baseline 6:3 parent and do
  not repeat parameter-delivery experiments as an unresolved gate. Read the
  older HUD notes carefully: message 06dd/variable 2206 controls distortion,
  **not HUD visibility**; online client mode 6 is correct. Recall stage 3->0 and
  the full Practice Range completion requirements remain unresolved. No native
  source changes or fresh CTest result this turn.

## Codex continuation, run 293 (2026-10-16)

- Corrected the best private recipe's hero HUD parent to
  `PickSubgraph='11:0x01cf:6:3'`. Graph 0x4b object 68 has state index 3 and
  runtime node 7; PSIn carries the state index. Runner StateData still names
  child 11. No other recipe behavior changed.
- Offline helper `.local/codex-scratch/hud293-parent-replay.py` creates a
  comparison child 12 under 6:3 on reference 292-e2. Native header consumes
  519/519 bits; interpreter consumes 474/474. Old child 11 records parent
  state 7; new child 12 records 3 at instance+0x2c. This is decoding/metadata
  evidence, not proof of UI rendering.
- Bounded live 293 reaches hero select and Tracer floor spawn. Native Blink
  reaches the doorway; firing records one shot in frames 5/6 and manual reload
  frame 7. HUD remains absent. UDP stderr empty; all seven cleanup checks true.
- Read-only `.local/codex-scratch/hud293-audit.py` writes
  `.local/runs/hud293-native-audit.txt`: hero HUD parent is 6, state 3;
  controller 20e4 parent 3, state 42. Controller widgets 11/12/16 exist. Hero
  listeners 97/178 are active and listener 178 finds sender 15; Stack 179 and
  presenters 181/62 remain inactive with no widgets. Correcting parentage alone
  therefore does not resolve the HUD. The 293 dump was deleted after analysis;
  264 remains the message-routing reference.
- Offline `hud293-tick264.py`: three instance ticks and direct update-list
  calls produce no listener callbacks on reference 264; both update lists are
  empty in that snapshot. This does not prove the live scheduler is broken.
  `hud293-listener-begin264.py` is a negative diagnostic: calling native begin
  and refreshing lookup does not activate the presenters. Do not interpret
  dump-time f0=0 alone as proof a listener never fired; it is transient, and
  registration itself increments the 1b1 generation counter.
- Next: trace actual sender parameter delivery / event scheduling into hero
  listener 178 and its Stack 179 output. Preserve parent 6:3. Recall's stage3 to
  rewind0 handoff remains a separate open task described below. Full Practice
  Range completion requirements remain in `docs/PRACTICE_RANGE_PLAN.md`.

## Codex continuation, run 292 (2026-10-16) - read first

- The best baseline remains `.local/runs/run-livemode18-best.ps1`. Run292 is
  experimental Recall mirroring; it is not a working Recall recipe.
- Added a private encoder guard in `_stdt_entry`: an active StateStack with
  fewer than two supplied data bits raises a clear error before the malformed
  frame is emitted. Regression helper `.local/codex-scratch/recall292-guard.py`
  rejects missing payloads on all four Recall Stacks 15/28/33/35 and accepts
  valid data and inactive one-bit entries. No arbitrary payload defaults added.
- Native writer audit after a fresh emulated E press: those four Stacks carry
  bits `1,0`, not the `0,0` used by experiment289. Predicted states36/37 were
  also omitted there; sender37 needs its zero compact-u16 bit. Correcting these
  gives a full native replay at 643/643 bits, preserving predicted active nodes.
  Helpers `recall292-serialize.py`, `recall292-stable.py`, `recall292-replay.py`
  and corresponding text reports are in `.local/codex-scratch` / `.local/runs`.
  The raw writer outputs are node payloads, not a replacement for the complete
  wire envelope (Ability still has its verified leading data fields).
- Fixed private emulator `ssfull2.py` to supply STATEDATA through the responder's
  normal STATE_DATA path, retaining payloads for inactive two-bit entries as
  well as active ones; this also makes the Stack guard apply to native replays.
- Live292: floor spawn, native Blink to the doorway, firing and manual reload
  work. Two E presses are accepted (mirror frames5/6 and7/8), but neither
  visibly rewinds. UDP stderr empty; all seven cleanup/integrity checks pass.
  The camera turns toward the ceiling on automated mouse-click firing; that
  is the known input artifact, not evidence of a movement/Recall teleport.
- Mid-press reference `retail-private-livemode18-292-e2.dmp`: PID21500,
  hero comp47 0x1f031996640, Recall instance 0x1ef2341edf0. Capture triggered
  on the second mirror-on event, with a 0.2 s delay. Its stage3/node4 runs;
  rewind0/node1 does not. Ability node24 flag+270 is0 and the deferred queue
  is empty. Nodes12/13/23/27/59/69/72/73/74/60 are active. Thus corrected
  Stack values keep the first stage present but do not hand off to rewind.
- Next: trace the authored transition that ends state3 and begins state0, or
  implement and verify the complete server timeline. Graph state3 has its
  onEnd connected to rewind0. Its subgraph contains states9/10/11/23; state0's
  subgraph includes2/12/27/1/26/5/7/14/18/34. Do not declare Recall fixed from
  active stage3 or frame alignment alone. Rewind's reader0x8eeef0 consumes a
  u16 and converts it into a duration-like field at node+0x970; its meaning
  and a useful value still need verification, rather than assuming zero works.
- Validation: Python compilation, guard regression, native643/643 replay,
  four public `tests/instance_bits.py` tests, and the bounded live session.
  No native sources changed this turn; the previous25/25 CTest result is not
  presented as a fresh run. Full Practice Range goal remains active/incomplete.

## Load-in, spawn and Recall prediction (Claude, 2026-10-16, runs 281-289) — read first

- **Faster load-in (runs 282/283, now in `.local/runs/run-livemode18-best.ps1`):**
  the user saw a long wait at a "random place" (default world camera after the
  loading screen), a jump to another place (the controller), then hero select.
  - Old timeline: diagnostic selection 30 s, controller selection 45 s, controller
    create 50 s, graphs 60 s, hero select 63 s.
  - New timeline (run 291, now the best recipe): 30 / 31 / 32 / 33 / 34 s. The
    driver has a new `-SelectDefinitionDelay` (was hard-coded to 45). Hero select
    now follows the loading screen after about one screenshot (~2.5 s) of the
    controller view.
- **Spawn height:** `-PickSpawn 48.71,2.05,37.77`. The old default y = 6.31 dropped
  Tracer about 4 m from near the spawn-room ceiling. The responder now starts the
  spawn snapshots after the second hero create (`PICK['sent'] >= 2`, 12 snapshots)
  instead of after all 40. `-SpawnAt 1,48.71,2.05,37.77,180` puts the same point
  in the hero's create transform, so its first frame is already in the spawn
  room (before: a dark corner elsewhere). Run 291 dump: the settled position
  (comp1 +0x440) is (48.70, 1.96, 37.45), so y = 2.05 is on the floor. About 1 s
  of camera motion (pitch/yaw sweep under the ceiling pipes) still follows the
  pick. It looks like a camera transition rather than a fall, but the user has
  not confirmed it yet. Run 290 was the known early instance failure (9
  datagrams, exit 1).
- **Recall (graph 0x1a) is client-predicted and gets rolled back:**
  - Emulated E press (`session/abil-flow-281.py`): press handler 0xc847c0 queues
    a deferred record (state 16 = 1). Gate 0xc85560 -> 0xca8d20 qualifies the
    press (buffered press record +0x280, window from def+0x148). It then calls
    0xc96d40 and 0xc99460, which sets node+0x270 |= 1 and fires the Ability's
    output plug (0x1b73fa0). The links queue deferred begin records on the
    instance (+0xc8 list; 0x1b92990 only if instance vt+0x138 says local).
    0x1b921f0 processes them by time (dispatch 0x1b91690 by record type +0x22).
  - Emulated result: states 3, 9, 10, 15, 17, 23, 28, 33, 35, 36, 37 turn on
    (state 11/31 briefly). Vars change: 0x009a = 1.0f (s26), 0x0021 = true
    (global), 0x02bb = true (s59). State 0 (41b3fc2b, the rewind) starts only
    when state 3 (54feb21c, with sub-states 9/10/11/23) ends.
  - Live (dumps 281-e, 283-e1): 0.25 s after the first E press, none of these
    states run, the record queue is empty and the Ability stays flagged
    node+0x270 = 3. Later presses then take the ca87e0 path and do nothing.
    The server sent no hero frame bump on E. So the client itself rolls back
    the prediction (reconcile against the last server statescript state). Same
    mechanism as the old double blink (charges mismatch -> replay).
  - Experimental `--recall-mirror 'MASK:INST:STATES:SECONDS:G/S=d/w,..;..:SC/KEY=VAL|..:DELAY'`
    (driver `-RecallMirror`): one hero frame bump on E with the predicted
    states, data and vars, and one bump back after SECONDS. New float value kind
    `('float', x)`: kind 5 (u4 -> float) or kind 8 (raw f32).
    - Runs 284-288: client exit 1 immediately. Cause (exact replay of the sent
      payload, `full-payload-*.json`, on the run-288 pre-mirror dump):
      the four Stacks 15/28/33/35 had no STATE_DATA in the responder, so the
      frame misaligned and hit the fatal path 0xf661e4. **Every entered Stack
      needs `0/1,0/1` data.** The responder does not check this; add a guard.
    - Run 289 (data fixed): no crash, Ability flag resets, but still no rewind.
      Server-entered states appear to be treated as server-driven, so state 3
      never hands over to state 0 on the client.
  - Next: make the server frame match the prediction exactly, so the client
    does not roll back (find the reconcile/compare code, inner vt 0xd8/0xe0
    0x97b060/0x97b100 set instance bit 10 during resimulation), or drive the
    full timeline (3 -> 0 with its sub-states) from the server.
  - Emulator additions: `ssfull2.py` env `PRESS=inst:node:button` (emulate a
    fresh press + record processing first), `POSTTICK=inst:n` (tick the
    instance afterwards), `PAYJSON=file` (replay an exact sent payload), float
    and bool INSTVARS (`f`, `b`). `session/recall-full-283.sh` wraps it for
    dump 283-e1. The responder writes `full-payload-*.json` for the two hero
    full frames after a mirror press (DUMP_FULL).
- Tools this session: `session/abil-flow-281.py` (press -> gate -> records ->
  timed ticks; prints active states and var diffs), `recall-state-281.py`,
  `hdr-scan-281.py` (client body module headers: only module 3 commands,
  module 0 reliable; no upstream statescript on E), `instvar-281.py`,
  `instvt138-281.py`, `recall-statemap-281.txt` (0x1a state -> node index).

## NATIVE BLINK WORKS (Claude, 2026-10-16, runs 272-275)

- **Best current recipe:** `.local/runs/run-livemode18-best.ps1`. It combines
  run 271's bots without the fake patrol, the calibrated Tracer, mode 0x18,
  native Blink and Recall states, and no server Blink/Recall teleports.
- **Tracer Blink is client-predicted with collision**, like the original. Two
  inputs were missing:
  1. Graph 0x24 state 0 (LogicalButton) must be active, with 4 data bits:
     `PickExtraStates '...;2:0'`, StateData `24:0=0:4`.
  2. Its press flow (Wait state 20, then condition #27) requires
     `var 0x000b > 0` (charges; Ability state 38 sync var, slot s11), var
     0x2562 (slot s34), NOT global 0x003e, and config #318 (global 0x0021
     priority). Fix: `PickExtraVars '2:s11=i3,s34=i1'`.
  - Run 274 shows correct dashes, stopping at walls, landing on the floor.
    The user confirmed Blink is good.
  - Charges are server-tracked (run 277): `--blink-charges-var 2:11:3:3.0`
    (driver `-BlinkChargesVar`): -1 per Shift press edge, +1 every 3 s, max 3.
    The hero frame advances only when the count changes. A fixed s11 = 3 made
    the client's prediction disagree with the server and roll back/replay
    (the user saw double blinks). Live: 3 blinks, the 4th only after a
    recharge, then none, then one again after waiting.
- **How the client handles input:**
  - Pressed logical buttons are listed per entity at comp47+0xd0+0x440
    (count +0x448). Shift = 35, E = 36; dump 272 shows [35, 114] on BOTH the
    hero and the controller.
  - LogicalButton node: vt 0x2637e20; update 0x1b9d280; press handler
    0x1b9f160; links via 0x1b73fa0 -> 0x1b74220.
  - Local activation gate: instance vt+0xc0 = 0x99af30. It allows when
    +0x318 bit 10 is clear and bit 19 is set, refuses if target def+0x7b,
    and otherwise uses def+0x7a.
- **The run-160 crash is explained:** LogicalButton data was missing. That
  STOP at 0xf661e4 is the generic "missing/garbled state data" signature.
- **Server-driven Blink states do NOT move the hero** (run 273: states
  25/11/2/3/6/7 entered, no motion), so movement needs client prediction.
  Data forms (emulator-verified): Anim 11 = `0:1,0:3,0:1`; states 2/3/7
  (types 3bc72de1/75d1c308) = `0:1`; PhysicsExplosion 25 and BlinkEffect 6 =
  none; ChaseVar 4/5 irregular.
- **Recall (graph 0x1a) is not working yet:**
  - Run 276: server-activating states 17 and 3 on E (`ButtonStates
    0x10:1:17,3:0.9`) enters them but does not rewind. The movement must be
    client-predicted.
  - The E press calls 0x1b714e0, which queues a state REQUEST (instance,
    state 16, value 1) on instance+0xc8 for the server (type-1 object via
    owner vt+0x98, queued by 0x1b92990), instead of activating locally.
    Likely the server must answer with Ability data: flag A=1, f32 +0x80,
    optional f32 +0x84, and a compact frame offset -> +0x78 activation
    time (reader 0xc84ac0).
  - Only caller of the Ability's vt+0x1d8 (0x8eb450) is 0x8eb424, in slot
    0x1b8 (0x8eb3e0). It runs when node+0x2e0 > 0 after gate 0xc85560
    (instance vt+0x140, +0x318 bit 19, 0xcb00f0, 0x1ba3490/0x1ba4060, 0xc1d860).
  - Run 278: new `--ability-press GRAPH:STATE:MASK:SECONDS:DATA` (driver
    `-AbilityPress`) swaps in "activated" Ability data on E:
    `1a:16=0:8,0:1,1:1,0:32,0:1,0:1,0:8` (emulator 461/461; the presence bit
    must be 0). Accepted, but no rewind; the pistols may twitch. Recall is
    still open. The best recipe has no Recall teleport (the old one threw the
    hero into the sky).
  - Run 279: live dump with E held (`retail-private-livemode18-279-e.dmp`,
    PID 8308, hero comp47 0x20f3f676640).
    - Pressed list = [36, 110]. Ability node 24 is running; its inline press
      record (+0x290: button 36, pressed) has been consumed (count +0x288 = 0).
    - States 17 (node 27), 3 (node 4) and 0 (node 1) are NOT running.
    - All Recall/Blink state defs have +0x78..+0x7b = [1,0,0,0], so the local
      activation gate is not the blocker.
  - Readiness check 0xca8d20 (`session/abil-ready-279.py`, emulated on that
    dump with the press record restored):
    - def+0x150 button is empty; it then uses def+0x158 = 36 with a hold time
      from def+0x148, and press qualification via 0xc9e6f0.
    - It sets the start flag only if the press qualifies ([rbp+0x67]) AND at
      least one condition at 0xca9308 is set: [rbp+0x6f], r12b, r15b, r14b =
      entity check 0xc1cc30, and sil/bl/al = 0x1b95e10 checks on
      def+0x1c0/0x1c8/0x1d0/0x1d8 objects from 0x8f6b40.
    - Live/emulated all are 0, so it only marks node+0x270 |= 4 ("ready").
    - Next: decode those condition configs (graph 0x1a #40 bool fields and
      m_3B7BED2E STU_A1AAB8C4) and whether a server sync var must be set.
  - Gate 0xc85560 on the E-held dump (`session/abil-cd-280.py`): the cooldown
    value is 0 (ready), 0x1ba4060 = 0, and the entity check 0xc1d860 returns 0.
    - 0xc1d860 uses mask function 0xbcacb0 = COMPONENT 25. Components 25/26
      are the team/filter components (see the comp-26 notes and the AECBBA41
      filter-bit gate).
    - So Recall's predicted start most likely depends on the hero's
      team/filter state, the same unresolved problem as hostility and hit
      feedback. Next: decode component 25's layout (its state at comp+0x18 is
      not plain like comp 26's; `comp-vt-266.py` fails on it) and what
      0xc1d860 tests.
  - 0xc1cc30 (the r14b condition in 0xca8d20) is an anti-tamper
    return-address check, not gameplay.
  - 0x1b95e10 is the ability priority-stack check (instance mgr +0x98 ->
    0x1ba3940; compares priority f32 +0x24).
  - It is driven by Ability state 16 (button 36 = E), which sits under
    Switch 22 (false branch) under Stack 29. Data forms: 29 = `0:1,0:1`,
    22 = `0:1`, 16 = `0:8,0:1,0:1` (reader 0xc84ac0); var 0x2562 = s34. They
    are in the best recipe.
  - The Ability is running, and emulating an E press passes the block check
    and calls activation 0x1b714e0. Live, nothing rewinds.
  - Activation sequence: Ability -> state 17 -> state 3 (54feb21c, no data)
    -> state 0 (41b3fc2b, 16-bit reader 0x8eeef0, but combined emulation
    over-reads 4 bits).
  - Next: compare the Ability's predicted-activation path (slot 0x1d8,
    0x8eb450) with Blink's LogicalButton path.
- Bot patrol (`--bot-patrol`) is only a movement-replication test (a sine
  wave with no collision). The user saw it clip through walls. Real bots need
  authored paths/AI; patrol is removed from the best recipe.
- Session helpers (`.local/claude-scratch/session/`): btnlist-272.py,
  btn-eval-272.py, press-emu-273.py, instvt-273.py, abil-btn-275.py,
  abil-press-275.py, graph-flow-272.py, graph-back-272.py. Dumps:
  livemode18-272-shift (Shift held) and 273-blink are reference dumps.
- Responder: (0,-8) state-data token = byte alignment (unused; the Ability
  data turned out to be 8+1+1 bits).

## Mode 0x18 HUD runs 256-264 (Claude, 2026-10-15) — read first

- **PSIn is a parent STATE index, not a runtime node index.**
  - Server-creating 0x20e4 under (0x13c1, 101) kills the client (exit 1, no
    dump) within one packet: runs 256/258/259/260/261.
  - Top-level (262) or parent (3, 42) (263/264) works. 101 is past 0x13c1's
    49 states.
  - The hero recipes' `11:0x01cf:6:7` therefore name 0x4b state 7, not runner
    state 3 (node 7). This is untested; try `6:3`.
- Run 257 never picked a hero (no UI driving); 258 = 256 plus 13c1:42 data.
- 0x03ac is now also set when 0x13c1/0x20e4 are controller graphs
  (USE_STATE_HERO). This is harmless; it was not the crash cause.
- **Working mode-0x18 recipe:**
  - `.local/runs/run-livemode18-264.ps1`: GameMode 18, PreloadGraph 13c1+20e4,
    `CloseControllerSubgraph '3:0x13c1:0:0;4:0x20e4:3:42'`,
    `CloseControllerStates '3:42'`, StateData `13c1:42=0:1,4:4,0:1`.
  - Hero select, pick, pistols and firing all work. No HUD.
  - The fatal emulator check: dump 257 with
    `.local/claude-scratch/session/hud258-mode18-replay257.py` (all variants
    decode cleanly; the crash was runtime).
- **0x1291 routing (native, dump 264, private session scripts *-264/265.py):**
  - Graph gates (evaluated natively, `eval-cv-264.py`):
    - 0x01cf #49 = `STU_1FF67CA6 == self`, where 1FF67CA6 = the local possessed
      body (the hero) in every context.
    - 0x20e4 #159 = `selected == self`.
    - So 0x01cf belongs on the hero and 0x20e4 on the controller. Both gates are
      true live (the 20e4 presenters run).
  - Game-message store = per-world system (sender vt+0x1c0 -> 0xa00b10, store
    vt 0x2657ed8): 64 buckets x 0x1d0, entries 0x70 keyed
    {entity, mode, message index}.
    - Sender 0xd4c3e0: a STU_1D719351 target writes entity = invalid (0)
      (`sender-emu-264.py`: pushes {0, mode 2, 4753}).
    - node+0xc0 = def byte +0x7a = client-only; client-only senders take only
      the mode-2/8 branch.
  - Listener 0xd4bd40/0xd514b0: subscribes under BOTH its own entity and 0
    (0xd4f5a0 -> 0xd9b2b0). Lookup 0xd9ad40 tries the own key, then key 0.
    - Hero #101 (node 178) finds #187's record (+0x250 = sender node,
      +0x238 = 0x80000304), but takes the non-fire path.
    - Firing requires node+0xf0 != 0 && +0x1b1 == +0x1b2. +0xf0 is set by begin
      routine 0x1b72ad0 and cleared by 0x1b750c8/0x1ba7230, a per-frame
      transient. Every node in the dumps has +0xf0 = 0, including 0x01cf #5,
      which therefore also never "fired": #41/#49/#101 are #5's subgraph,
      running while #5 waits.
    - Next: emulate a full instance tick (who calls 0xd514b0/0xd51fc0 while
      +0xf0 is set), or find the server-side counterpart that marks the
      GameMessageEntry as received.
- Dumps: livemode18-264 is the new reference for this path (hero comp47
  0x2343c521b80, controller 0x2343c522da0, PID 18040). 257 (pre-pick mode-18
  emulation base) is kept. 263 is deleted after analysis.

- **Native Blink attempt (run 265):**
  - The run-160 crash cause: LogicalButton state data is missing. Tracer
    graph 0x24 state 0 (LogicalButton 0xb480a974) needs 4 data bits.
    Without them the native decoder stops at 0xf661e4, exactly the run-160
    signature. With `StateData 24:0=0:4` the frame aligns (387/387).
    BlinkEffect (state 6) enters cleanly (382/382).
  - Live 265 (`PickExtraStates '6:3;2:0'`, server Blink off): the client
    survives and node 1 (the LogicalButton) is running. Shift still does
    nothing: no transition and no message to the server.
  - Abilities therefore need the hero's instances to be client-predicted, or
    server-driven Ability state 38 plus synced vars 0x9a/0xb0 on states 3/7
    (STU_75D1C308, likely a teleport over duration), still with the server
    computing the destination.
  - The old "prediction gate" byte image+0x2f7f840 has NO writer: it is a
    dev-only check in 0x64d990, not the gameplay gate.
  - Instance +0x318 bit 8 (0x100) is NOT a prediction flag. 0x1b92c30 sets
    it after queuing a type-7 request (rcx+0x10 vt+0x98).
  - Instance creation (0xa0adc0) has more optional parts than the responder
    encodes: PIID/PSIn, then 'SPUI' plus a list of {entity (0xdb0f70),
    SrcI u16, SrcS u16}. Their meaning (source/predicting entity?) is
    untested.
  - Tracer child entities (0x17 x2, 0x169) do not exist in the world
    (`entity-ids-265.py`: only 0x80000300..308 plus map entities). The
    client never self-instantiates them.

- **New research on main** (from branch claude/blissful-bohr-qodvyf):
  `reports/Overwatch 1 complete game reference.md` plus
  `research_notes/Overwatch 1 complete game reference/`. Hero numbers, Practice
  bot/health-pack data, and a priority roadmap. Torrent hash redacted.
- **Tracer calibration from the report (run 268):** FireHold=40 (20 shots x 2)
  and ReloadTime=1.0. Live, 40 rounds drain in 1 s, auto-reload runs and
  firing resumes. Recipe: `.local/runs/run-livemode18-268.ps1` (= 264 plus
  calibration). The 0.686 s ammo-restore point is not modelled yet.
- **Component 26 (filter bits) cannot be sent in a create:**
  - The state type is 0x30dabc0, one u64 at state+0x78 (comp+0x90), hash
    82ce0230, field flags 0x2. Component 44's replicated fields have flags 0.
  - Runs 266/267 (`--filter-bits` / `-FilterBits`, sorted component lists)
    crash the client at the first bot create carrying it. Do not use.
  - All live entities have filter bits 0.
  - The client's local-session builder 0x829430 sets 0x10040001 (+team bit)
    itself.
  - Comp-26 mask functions 0x5d4520/0xbd5b90 are used by 0xb22900, called
    from module-2 readers 0xb3e8ed/0xb41bac. Module 2 (the per-entity section
    we send empty) is the likely replication path for team/filter bits; trace
    next.
  - Responder now sorts each create's component list by type (harmless).

- **BOTS MOVE (run 269):** module-3 movement items need an increasing frame
  in movement field 2. See docs/BGS_PROTOCOL.md "Remote movement frames".
  - Responder `--snapshot-frames` (driver `-SnapshotFrames`) writes the reply
    server frame. It was emulator-verified with 0xc5f680: 174 bits, decoded
    frame exact.
  - `--bot-patrol 'IDX:x|z:AMP:PERIOD'` (driver `-BotPatrol`) streams one
    framed item per reply, and hit tests follow the moving position.
  - Recipe: `.local/runs/run-livemode18-269.ps1`; bots 2/3 visibly swing.
  - Untested: whether framed hero teleports (Blink) behave differently, and
    bot facing/animation.

- **Tracer muzzle origin (runs 269/270):**
  - The volley (0x16 state 8, #230) muzzles are two {hardpoint 0dc0000000000006,
    entity handle} pairs. The handles are 0x16 remote-sync vars 0x0031 (slot
    s49) and 0x0032 (slot s50).
  - CosmeticEntity states 0/1 (def 0x0400000000000017, hand hardpoints
    0x0a/0x0b) name those same vars (m_1DEF59FA).
  - On dump 264 both vars are UNSET (ammo 0x35 = 40 reads fine), so the volley
    has no muzzle entity and shots start at the hero body.
  - Run 270: server-created 0x17 x2 (definition indices 5/6) plus
    `--pick-extra-vars '10:s49=e5,s50=e6'` (new option; `e<idx>` = entity
    value; driver `-PickExtraVars`). The vars now hold 0x80000309/0x8000030a,
    but the entities sit unattached at the origin (identity transform,
    components 1,3,4,22,25,26,40,97), and the tracer still starts low.
  - Next: find how a child entity is attached to the hero's hardpoint
    (components 3/4/40 or a create field), or how the client-side cosmetic
    entity's handle is meant to reach vars 0x31/0x32.
  - Attachment negatives: components 3 and 4 (present on the hero, the
    pistols and attached map props) have no state visitor (slot 0x18 =
    0x1ce5640), so they are not replicated as component state. Module-4 op 0
    is "none". The create format has no known parent field.
  - Tool: `.local/claude-scratch/session/instvar-269.py` (reads instance vars
    via 0xbe8b60(comp47, instance id, var GUID)).

- **Range populated from map data (run 271):**
  - The Practice map has exactly 15 entities with components [1, 110] (ids
    0xc0000004..0xc000020c): the training-bot spawn markers.
  - `.local/claude-scratch/session/comp-positions-271.py <dump> <pid> 110`
    lists them with comp-1 positions (+0x90). Floors are y -4/-2/2/5/11; the
    y=-2 floor matches the public health-pack coordinates.
  - `.local/runs/run-livemode18-271.ps1` spawns 13 bots (0x14d2, three skins)
    at 13 markers. Definitions are capped at 16, so 2 markers are unused.
    Three bots patrol via framed snapshots.
  - Live: bots stand across the range (upper deck, far target area, behind the
    passage). This is the new baseline recipe (calibrated Tracer, mode 0x18,
    snapshot frames).

- **Health packs (open):**
  - At the 4 public pack coordinates the map has bare markers with component 1
    only (0xc0000042, 0xc0000045, 0xc0000050, 0xc0000129). Next to each is a
    class-0 entity with [1, 5] (probably the pad).
  - The pickup entity/definition is unknown: no graph has the 75/250 heal
    constants together (0x0e95 is UI), and OWLib has no pack type name.
  - Tool: `.local/claude-scratch/session/near-271.py <dump> <pid> x,y,z ...`.

## Continuation through 255 (Codex, 2026-10-15)

Active objective: fully functioning Practice Range. Completion requirements are
in `docs/PRACTICE_RANGE_PLAN.md`; HUD alone is not completion.

Claude's research is now in `reports/Overwatch 1 server emulation research.md`
and `research_notes/Overwatch 1 server emulation research/`, recovered from
origin/claude/blissful-bohr-qodvyf at d8b2998. External claims are hypotheses.
Exact-build asset decoding confirms mode 0x18 references controller 0x13c1;
state 42 (runtime node 101) runs 0x20e4, state 43 runs 0x288a. Counts are
64 sync slots / 49 states for 13c1 and 4 / 26 for 20e4. Do not copy the
external fork's compressed state numbering.

Runs 253/254 discovered another alignment omission: 0x0cb6 state 3 needs a
compact-u16 payload after its active bit. The zero form is one additional bit.
Without it the second native replay consumes 474/460 bits and StateHero never
enters; corrected creation is 492/492, activation 461/461 with StateHero enter,
data and post calls. Reader 0xd4bac0 calls 0x185bb20. The private responder now
defaults this known state's zero form. Repro hud253-replay.py; old/corrected
outputs hud253-replay.txt and hud253-senderbit.txt in .local/runs.

Live 254: pistols and registered firing persist, no HUD, empty UDP stderr,
all seven cleanup checks true. Controller 20e4 widgets are active. Controller
01cf stops at node 66 because selected hero != own controller; hero 01cf
passes that ownership gate and waits at node 178 for 1291, with presenters
inactive. These are complementary ownership gates: 20e4 belongs on controller,
01cf on hero. PID 49200; controller comp47 0x138b9952da0, hero 0x138b9951b80.
Read-only audit: .local/codex-scratch/hud254-audit.py -> hud254-native-audit.txt.
Retain livehudowner254 as a reference; 253 is superseded after analysis.

Ordering hypothesis: GameMessageEntry subgraphs run while waiting. 20e4 starts
presenters and sender 187 under its 0717 listener immediately; the message pulse
separately sets f62a. Thus 1291 may be sent before hero 01cf passes 0717 and
opens its 1291 listener. This is not yet a demonstrated cause. STU_1D719351 is a
target descriptor, not a normal config-var evaluator; exact scope is unproved.

255 is a loader-control negative, not a HUD result. Mode 18 returned to Training
because retail_private_preload.h admitted only mode 5a. The guard now permits
exactly 18 and 5a for the same Practice map identifiers. Rebuild after 255 cleanup.
Prepared next: .local/runs/run-livemode18-256.ps1, mode18/preload13c1+20e4,
create controller13c1 at close, state42 after five seconds, HUD child20e4 after
eight seconds (after 0717). Driver accepts GameMode and LateControllerSubgraph.
Check residency and native alignment on its dump before attributing UI failures.

## Latest HUD status — read first

- **Run 250 scheduling failure reproduced and fixed (Codex, 252):** the close step
  advanced HERO_SNAP seq before the first hero full snapshot. Consequently that
  first snapshot had base 3 and both subgraph create flags false. It updated
  nonexistent instances 11/12, so native decoding returned 0 after only 3 bits.
  This failure happened before StateHero ran; it is not evidence that StateHero
  resets component 47. Subgraph creation now uses the first full-send count, and
  the late-state sequence advances only after that first full frame is emitted.
  On dump 250 itself, corrected creation consumes 656/656 bits and activation
  607/607; both succeed and instances 11 (0x01cf) / 12 (0x0c90) exist.
  Private repro: `.local/codex-scratch/hud252-replay.py legacy|fixed`, cwd emulator
  directory; `.local/runs/hud252-legacy.txt` and `hud252-fixed.txt`.
  Rebuilt in Codex's build tree: full build and 25/25 CTest pass.
- **Live 252:** pistols render, firing/reload work, no HUD. All cleanup checks pass;
  UDP errors empty. Dump PID 1400, hero comp47 0x22bbeda1b80. Instances 11/12
  now exist, StateHero node 0 runs, and 0x0c90 spawns client graphs 0x1a36 and
  0x20e4 (instance 65532). No component-47 reset occurred.
- **New blocker:** 0x20e4 switch #159 (runtime node 19, condition at def+0xe8)
  compares STU_8985E00A = selected controller 0x80000304 with STU_B5A0CAF0 = own
  hero 0x80000305, and evaluates false. Its UX presenters #166/#178/#183
  (nodes 16/11/12) are all inactive with no widgets. The hero 0x01cf presenters
  have widgets, but message parameters/parent handles 272e/d42a are unset.
  Native audit: `.local/codex-scratch/hud252-audit.py` from project root writes
  `.local/runs/hud252-native-audit.txt`.
- **Next:** resolve the intended ownership of 0x20e4 / hero HUD against selected
  controller identity. The hypothesis that 0x0c90 must run on the hero is now
  contradicted by that native equality gate. On-controller run 249 reached sender
  #187 but did not establish delivery to hero HUD; compare routing/parent handles,
  and consider a controller-owned 0x01cf control. Do not repeat the hero-owned
  setup unchanged. Target STU_1D719351 semantics remain unproved; the simple
  config-value evaluator does not apply directly to that target object.

Earlier Claude findings (runs 235-251):

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
  - 0x20e4 is client-spawned from 0x0c90. The earlier hypothesis that it should
    share the hero owner with 0x01cf fails the selected-controller equality in
    run 252; see the new ownership finding above.
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
  - Resolved by the captured-frame replay in run 252 above: create flags were
    false before the subgraphs existed. Correcting scheduling preserves component
    47 and creates all expected instances; ownership is the next blocker.
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
