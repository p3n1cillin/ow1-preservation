# Agent handoff (Claude ↔ Codex)

Last updated 2026-10-16 by Codex (Nearby Players discovery after party-first runs; latest checkpoint below). Whoever stops
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

Later Claude runs supersede this early summary: full Tracer HUD including portrait,
Soldier first-pick HUD, Pulse Bomb throw, and two clients seeing each other are
verified (372-374 and pair-e3-367; details at the end of this file). Hero re-pick
regressed in 375. Authored bot movement and complete combat/roster behavior remain
unresolved. Historical teleport recipes are not the best baseline.

## Latest continuation: Nearby Players discovery (Codex, 2026-10-16)

- **Run `pair-social-381` removes the seeded group suggestion.** Message
  **20815**, schema 446200228, +0x78 array of embedded player records, creates
  the native Nearby Players tab. Mercy sees Tracer there, right-click / Invite
  to Group sends real 22102, Tracer's Yes sends real 22110, then both get the
  two-member roster. Mercy alone starts Training / Practice; both enter, pick
  Tracer, and spawn with full HUD/weapons. Follower Blink consumes 3 -> 2 charges.
  Both alive at shared bound, one own-port referral each (1119 / 1129), both
  responder sessions bound, no bind refusals or stderr, all 12 cleanup fields true.
  Proof: `.local/runs/pair-social-381-{nearby,group,leader-range,follower-range}.png`.
- **`pair-social-382` repeats from fresh clients with 20815 supplied at login.**
  Nearby Players is already populated when Mercy opens Social. Native Invite /
  Yes / roster / leader-only queue again brings both to first-person Tracer
  with HUD. Follower Blink moves to the doorway (3 -> 2); leader volley and
  volley-end events logged. Both alive at shared bound, one own-port referral
  each, both bound, no bind refusals, empty probe/UDP stderr, all 12 cleanup
  fields true. Proof: `pair-social-382-{nearby-invite,leader-range,
  follower-range,follower-blink}.png`. No new dumps or native changes.
- Private `.local/re/social_probe.py`, opt-in `OW1_SOCIAL_EXPERIMENT` pointing
  to the SAME manifest as `OW1_PARTY_EXPERIMENT`, installs after the party probe.
  Write `{"mid":20815,"version":1}` to `<manifest-prefix>-social-control.json`.
  Each client gets the other configured account once. No `suggest` control is
  needed: use Social / Nearby Players / right-click account / Invite to Group,
  Yes in the follower, then only the leader selects Practice. The party probe's
  22102 routing no longer requires `party_suggested`.
- `pair-social-380` failed before launching clients: the full RE descriptor set
  exceeded the codec's 64-message bound. Fixed by selecting 41 messages into
  `.local/runs/social380-runtime-schemas.json`, preserving the public bound.
  The later 381 run used this subset successfully. Full 126-message extraction
  remains `.local/runs/social380-schemas.json`; do not load it as one codec file.
- Public `protocol/nearby-players-104319.json` contains only the verified 20815
  numeric layout. Other candidates 20809 / 20810 / 20816 were NOT sent in 381;
  do not assign them friend/recent semantics. Friends still spins; Recent
  Players was empty. Requests observed around menus: 22207 and 58400; no
  evidence yet that the empty 22210-22213 requests load those lists.
- Shared private RE helpers: `.local/codex-scratch/social380-{schemas,meta,xrefs}.py`.
  Numeric descriptors / metadata only; retained dump 295 and local emu image
  are unchanged. No new dumps. `.local/codex-scratch/test_social382.py` extends
  the party regression with nearby identity and no-suggestion checks; all five
  checks pass. All 28 public `tests/bnet_probe.py` tests pass, including the new
  nearby identity, empty-list, truncation, catalogue and existing-player-layout
  checks. `git diff --check` passes. Native build/27 CTest results from the prior
  checkpoint remain the latest native validation; no native sources changed.
- **Next:** automatic presence/removal and party leave/re-invite lifecycle,
  then peer movement/pose/weapon replication and shared bot/combat state.
  The nearby list is a configured two-account fixture, not live presence.
  Peer still floats in a fixed pose; hero re-pick regression from 375 remains.
  Do not claim full multiplayer or completion of the master goal.

## Prior continuation: party before Practice (Codex, 2026-10-16)

The owner explicitly wants joining the other account's party BEFORE starting
Practice. Claude's E2/E3 runs entered Practice separately on each client; they
do not verify invitations, party joining, or leader-driven group entry.

- Rebuilt Codex's native tree with `scripts/Build.ps1 -SkipDependencies` after
  the launcher pair changes: full build and all 27 CTest targets pass.
- `pair-party-376`: both original clients reach menus (Mercy#1002 / Tracer#1001).
  Friends remains loading, Groups has no active channels, chat does not open in
  the initial menu state. Both alive at bound, no instance referrals, all 12
  cleanup/integrity audit fields true. This was a party-menu diagnostic.
- `pair-party-377`: **20701 is a group suggestion, not an incoming invitation**.
  Native banner says "Mercy suggests Tracer to the group?" with Invite / Don't
  Invite. Clicking Invite sends **22102** (schema decimal 3003079262 from
  the catalogue), +0x78 = target game account identity.
  Both clients closed normally with Alt+F4 after this evidence (exit 0), all 12
  cleanup audit fields true. No party joined and no instance referral.
- Private `.local/re/party_probe.py`, opt-in via `OW1_PARTY_EXPERIMENT=<manifest>`
  in `.local/re/probe_record_inputs.py`: run-scoped signalling for the two owned
  accounts. Current experiment sends the suggestion to the LEADER, routes its
  real 22102 to an incoming 20703 candidate for the other account, records all
  native 221xx requests, and only joins after a real request selected by control.
  Follower referral forwarding is prepared; NOT yet verified live at this checkpoint.
  Ordinary recipes are unaffected when the environment variable is unset.
- `.local/codex-scratch/party376-schemas.py` exports numeric party/social field
  descriptors from retained dump 295 to `.local/runs/party376-schemas.json`.
  No proprietary bytes exported. Offline initial-notification check passes:
  first list 20504/20505/20502/20802/20700, second empty (no repeated login data).
- **Party-first Practice verified in 378:** 20703 displays a group merge request;
  clicking Yes sends **22110** naming Mercy's identity. After the two-member
  20700 roster, Tracer says "You have joined a group!", Training is disabled on
  the follower, and Mercy remains leader. Mercy alone starts Practice; the
  wrapper forwards the accepted Training queue request to the follower's own
  session. Both receive their own referral, pick Tracer, spawn with HUD/weapons,
  and the follower sees the leader's proxy. Leader fire/stop logged. Both alive
  at bound, no stderr, all 12 cleanup fields true. The 378 incoming request was
  a server fixture (leader's suggestion expired behind Tutorial).
- **Native Invite -> Accept -> party -> Practice repeated in 379:** after both
  tutorials are dismissed, write `{"suggest":1}` to `pair-party-379-control.json`.
  Mercy clicks the seeded suggestion's Invite: real 22102 targets Tracer; this
  generates 20703 in Tracer's client. Tracer clicks Yes: real 22110 targets Mercy;
  backend automatically sends 20700 to both. Mercy alone starts Practice, follower
  automatically enters. Both pick Tracer and spawn with portrait/name/health,
  crosshair, ult, ability and ammo HUD. Follower Blink moves to the doorway and
  HUD charges drop from 3 to 2. Screenshots `pair-party-379-{tracer-group,
  leader-range,follower-range}.png`. Both alive at the shared bound, exactly one
  own-port instance referral each, both bound, no bind refusals, empty probe/UDP
  stderr, all 12 cleanup/integrity audit fields true. No dumps requested/retained.
- Private fixture is still opt-in and bounded; Friends/player discovery remains
  missing, so a server-seeded suggestion supplies the selectable candidate.
  20703 is a merge request, not a claim that all invitation variants work.
  Bots still per session; proxies float, lack locomotion/weapon animation and
  PvP damage. Run 375 hero-repick regression also remains. Next prioritize normal
  local-player discovery / durable party lifecycle, then proxy movement state,
  shared combat and the hero-change regression; do not revisit the old HUD root theory.
- `.local/codex-scratch/test_party379.py`: offline checks pass for initial data
  sent once, configured-target-only Invite, matching-leader-only acceptance,
  exactly one party leader, and one follower referral on its own port. Public
  `protocol/party-104319.json` contains five numeric descriptors only; all 27
  `tests/bnet_probe.py` tests pass, including catalogue/identity-wire consistency.
  Public behavior/scope documentation: `docs/PARTY_PROTOCOL.md`.

## Master goal + session 327-329 notes (Claude, 2026-10-16) - read first

- The owner set a master goal (docs/MASTER_GOAL.md): complete OW1 with 6v6.
  Priority 1 = hero HUD ownership/routing. Work autonomously; keep this file
  current.
- Run 327 (best + 294 hero-ownership switch + controller 0x0bcf instance 5
  with state 1): 0x0bcf exists, only its stack node 2 runs; no HUD_Root
  content and no warning icon (run 231 not reproduced). Only 0x0bcf/0x120b
  contain STU_501733D7 among all 1586 graphs (full rescan). 0x9cf9b0 creates
  a render target (replay/highlight viewer), not a general HUD_Root show.
- 0x0cc9 Stack sets ShowHeroHud (UI var 0x34f5) false only while active.
- HUD presenter bindings (private .local/runs/hud-binding-vars-327.txt):
  presenter m_EC32138E = {screen 0a88.., binding list id->expression over
  vars}; m_45216F79 = two UX ids. Hero 0x01cf instance 11 in 294: 0x2af6 = 1
  (main presenters #155/#235 gated on NOT 0x2af6), 0x7c20/21/22 = 1,
  0x2ad4/0x2e27 handles present, 0x73ed = hero.
- Runs 328/329: server 21616 game message 0x0717 to hero/controller is
  delivered without effect (0x2af6 stays 1; 0x0717 had already been received
  per the earlier #5/m_452862E6 analysis). Creating 0x0cb6 on the hero (329,
  emulation 471/471 aligned) makes the client drop the hero's 0x01cf/0x0cb6
  instances and the pistols: do not put 0x0cb6 on the hero.
- 0x0717 senders: 0x0cb6 (client, target mode 1), 0x0cbb (Practice tree,
  server-side, target 0) and 10 others; server game messages need a network
  carrier (background investigation; notes go to
  .local/re/server-game-message-path.md).
- Client send path: send node vt 0x263ac80 -> 0xa06fc0 -> 0xbe9cb0 (entity
  comp47 vt+0x60) -> per-manager dispatcher 0x1b8d150 (16 callers).
- Module roles (vtables): slot 0x30 = frame-prefix reader (m0 0xc6a480, m3
  0x7c0630, m4 0x787e70, m5 0x7e37c0; m1/m2 none), slot 0x38 = per-entity
  reader (m1 0xa13b90, m2 0xb3a490, m3 0x7c06a0, m4 0x787f20), m2 slots
  0x60/0x68 = 0xb3b0d0/0xb3b1f0 (tick). Module-2 per-entity records
  (0xb40130 -> 0xd81f80) look like combat events (entity ids, two vec3,
  u16s, entity list); applied by the m2 tick via 0xb40d40 -> 0xb22900.
- Movement decode: state position = qwords +0x70/+0x78 XOR a rolling key
  (+0x80, stepped BEFORE each word by one of 8 constants chosen by key&7).
  numpy scanner `.local/claude-scratch/session/scan-movestates-329.py <dump>
  x y z tol` finds every encoded state (authoritative history, rewind/recorder
  nodes, three states in controller comp59 at +0x70/+0x3f0/+0x770). No
  state holds the hero's current predicted position.
- Server placeables 0x80000300..303 (comp1 +0x90): (28.02,6.31,3.73),
  (50.44,2.06,23.02), (54.57,1.0,42.15) = the claimed team-0 spawn point (comp
  58), (34.24,1.99,22.97); they are not health packs. Run 330 spawned the hero
  at (54.565,1.05,42.148): she fell under the map to y -18.8, so the placeable
  height is not a standing position; keep PickSpawn (48.71,2.05,37.77).
- **Feed-based hit registration (run 331, best recipe now includes it):**
  driver `-HeroPosFeed <json>` starts `.local/re/hero_pos_feed.py auto 80000305
  <json> 60` itself (waits for the owned client, read-only, exits with it);
  the responder's TRACK position then comes from the client instead of dead
  reckoning. Live: aimed hold-fire killed bot 6 (53 hits) with the server using
  the true position (49.25,2.0,23.08). Echo stays off.
- **Statescript game-message bus (static, .local/re/server-game-message-path.md):**
  no network record carries a game-message GUID. Messages are posted by
  send-state nodes (vt 0x263ac80, begin -> 0xd4c3e0 -> registry 0xd9a770; the
  registry hangs off root 0x2f586e0 via 0xa00b10, 64 buckets keyed by entity^msg)
  whenever such a state begins, including when the server activates it via
  StDt. Listeners (GameMessageEntry, vt 0x263b408, begin 0xd4bd40, poll
  0xd514b0) pick a mode at node+0x248; client-only listeners in instances with
  vt+0x148 true listen in mode 2 and only match REMOTE posts (sender def+0x110
  set in such an instance). So to deliver message X to entity E the server
  activates a sender state whose authored config yields X/E. 0x1b8d150 is a
  variable-write dispatcher, not a message path. Message section 0xa0cca0 has
  no GUID field.
- HUD listeners: 0x01cf waits for 0x0717 (#5), 0x1291 (#101), 0x1509/0x1504/
  0x150a (#105/#109/#113) and others; 0x20e4 for 0x0c9c, 0x0717, 0x1509/04/0a.
  Graph senders found: 0x1291 = 0x20e4 #187 (state 13, client-only), 0x0c9c =
  0x0233 #1044 (client-only); no graph sends 0x1504/0x1509/0x150a (native
  posters; message GUIDs are obfuscated in code).
- Pistol child definition 0400000000000017: contact set, EE0FB992, model
  0d00000000000413 (third-person pistol), own children 0x2d33/0x3024; child
  0x0169 = one effect component. Class-0 entities in 294 are static map
  objects; no child of the hero exists. Creation path still unknown.

## Statescript server ack / reset bit (Claude, 2026-10-16, runs 307-309) - read first

- **Frame header 0x9b4160:** reserved bit, CmFD-present bit (+0x4c), then a
  **reset bit (+0x4d)**. Our responder always sent 0. 0xa0e3c0: if +0x4d (or a
  delta frame while history exists) it undoes predictions (0xa0f5d0), applies the
  frame, then 0xa0a780 drops the whole history list (mgr+0x90) and replays only
  local inputs (mgr+0xc8, 0x48-byte items, tick +8) newer than CmFD (+0x900).
  Without it, 0xa0b200 rolls back every prediction 40 ticks after the oldest
  history entry (it replays only from now-40), which is why Recall states
  always dropped at +0.64 s (307 confirms: tick rewound to the E tick at drop).
- New responder `--hero-reset never|always|after-close` (driver `-HeroReset`):
  hero full frames set the reset bit. **Live 308** (after-close, margin 0, mirror
  2.0 s): E predicted, mirror frame acks it (CmFD = E tick), history cleared and
  states 3/9/15/17/23 stay active the full 2 s until mirror-off. Prediction
  survives; Recall now needs the 3 -> 0 transition.
- Instance var `1/18b=b1` at +0.25 s (308) does not end state 3 (not the trigger).
- Emulation (283-e1, PROBEADDRS=8ed090): a server frame entering state 0 calls
  enter with **edx=1** (normal path, not the edx==2 early return).
- **Rewind (state 0, 41b3fc2b) dependency chain, runs 309-313:**
  - Enter 0x8ed090: end time +0x238 = start + duration(def+0xf0 = var 0x00d7,
    SetVar #31 = 0.9 s) then overwritten by the state-data s64 (our T token is the
    END time: use `T+900`); start +0x978; recorder node via 0xca2660 = def+0x108
    state-ref var 0x72a3 (written by recorder STU_CF950CB5 = **state 4, node 5**);
    history index +0x270 = 0xc90880(recorder, look-back def+0xe8 = var 0x1bd5 =
    3, SetVar #23); success sets node bit 9 (0x1b72e30 dl=1, per-tick update).
  - 309: no state 4 -> +0x270 = -1. 310b (`PickExtraStates 1:...,4`, no data
    bits, emulation-aligned 554/554): +0x270 = 0, update registered, no move.
    311b/312: `T+1250`/`T+900` and mirror vars `1/s21=i3|1/s23=f0.9`
    (674/674 aligned): still no move; client exits on mirror-off (as 299).
  - Update 0x8ee160 (vt 0x2620e18 slot 0x80): progress = (+0x248 clock -
    start)/(end-start); eased curve 0x8fb1d0 (range -0.285..1.285); then
    0xc909e0 needs two recorder samples around the cursor (+0x260) -> null.
  - **Recorder never samples:** ring at node+0x1c0 (0x480-byte entries,
    cap +0x1c8 = 101, write +0x1d0, count +0x1d4) has 1 entry. Record fn
    0xc94a00 (vt slot 0x70, called each tick by 0x1b925f0 from instance tick
    0x1b927c0 via list inst+0x238) samples only when the hero comp28 movement
    time (0xbe71d0 -> 0xc5be90: comp28 inner ring +0x400 cap/+0x410 idx/
    +0x414 count, 16-byte {f64 time, u32 seq}) >= next time +0x1d8 (+0.1 s).
  - **comp28 ring holds only the 12 spawn-snapshot states** (t 53.44..53.79,
    seq 3340..3362 step 2) in dump 313-r: it is appended by authoritative
    movement (0xc5b640 from module-3 apply 0x64a970, 0x803420 via 0x7fdf10,
    0x805970 = slot 0x48 of interface vt 0x260fdb0 at +0x14f0 of the
    controller's component 59 (comp vt 0x260fd10), and module-2 0xb25480).
    Local prediction alone does not extend it, so Recall needs either streamed
    server movement states for the controlled hero or the comp59 path that
    feeds 0x805970. Next: trace who calls interface slot 0x48 (0x805970).
- **Movement snapshot sequence:** module-3 reader 0x7ca130 uses state +8
  (snapshot field 2) as the ring seq; 0 -> current server tick [rdi+0x108];
  ring time = 0xbb7100(seq) = seq x 16 ms; apply 0x64a970 -> 0xc5b640 skips
  states whose seq <= the newest ring seq. Client prediction 0x8013d0 also calls
  the simulator 0xdaa6c0 but never appends to the ring.
- **User decision (2026-10-16): the local private server may read the client's
  own predicted position.** `.local/re/hero_pos_feed.py <pid> <entity> <json>`
  (ReadProcessMemory, live Ctx world scan, hero comp1 +0x440 f32 xyz, 60 Hz,
  re-resolves if entity +0xb0 changes). Responder `--hero-pos-feed` (driver
  `-HeroPosFeed`): server TRACK position/history from the feed instead of dead
  reckoning. `--hero-pos-echo` (run 314) echoes it as position-only snapshots:
  the hero sinks/drifts (other snapshot fields reset), ends inside geometry at
  y~30. Do not use echo.
- **Server Recall rewind (runs 315-317):** `--recall 3 --recall-rewind 0.9
  --recall-step-hz 30` (driver `-Recall -RecallRewind -RecallStepHz`): on E the
  responder plays the last 3 s of fed positions in reverse as teleport
  snapshots, plus the mirror states for visuals. 315 crashed (emit bug, fixed).
  316: path rewinds correctly (z 22.75 -> 37.4 in ~0.9 s) but points at floor
  height sink below the floor and the end lands at y 13.3; 317 lifts every
  point by TeleportDy 0.3: points then rise and the end still lands at 13.3.
  318 adds snapshot field 3 (0xc61b60, state +0xc: changed, raw-bit 0, u32 =
  monotonic teleport generation `TELE_GEN`, emulator-verified 207/207 bits):
  no change. 319 (6 Hz steps), 320 (single final teleport): still 13.3.
- **Snapshot teleports are swept, not hard (run 321 calibration,
  `-SpawnSequence` at fixed times, feed-logged):** the client moves the hero
  from its predicted position to the snapshot position over ~0.3-1 s with
  collision, rising over obstacles. Open ground -> lands near target;
  outdoors -> spawn room (48.7,2.3,37.44) peaked 12.4 then fell to the floor
  (ok); inside the room -> (48.71,2.05,37.77) climbs onto the roof at y 13.3;
  a target in geometry ends at the fallback (52.4,30.2,14.1). This also
  explains the old 'spawn on top of the spawn room then fall' report. 322
  (mirror ends before the final teleport) still lands on the roof.
- **Generation makes teleports snap (runs 323-326, `-TeleportGen`,
  `-SpawnSeqSends`, SpawnSequence targets `here` / `here+dx,dy,dz` from the
  feed):** with field 3 = new generation the x/z jump is instant (no sweep).
  Interpolation ring +0xe040 (0x30-byte {pos, time, gen}; 0xc5bd30/0xc5b820)
  only interpolates between equal generations. But ~0.3-1.2 s after a ground
  landing the client launches the hero straight up to a fixed hover height
  y ~30.7 at any x/z (open field 70,-1.7,10 included; 'here' at the spawn exit
  too). Teleports while hovering drop correctly. While the same state is
  re-sent continuously (150 sends) the hero sits ~3.6 m BELOW the target, then
  pops up and launches once the stream stops. So our snapshot's non-position
  fields (left at the default prior 0x2f82d30: stance/height +0x34/+0x38 feed
  the computed +0x2c/+0x30 = -2.5, etc.) disagree with the client's predicted
  state. Next: obtain a genuine predicted state for comparison (the decoded
  +0x420 history holds only our spawn states; heap scans around comp59 and
  the simulator holder found none) and send matching fields.
  Next: find the native hard-teleport path (0xc5b640 equal/greater gen copies
  the state into the predicted entry at comp28 inner +0x420 + idx*0x370;
  field 1 = state +4 bit gates 0x7ca130 velocity derivation) by emulating
  0x7ca130 + prediction on a dump instead of more live runs.
- Tools: `session/rewind-update-313.py` (gate probes + timed updates),
  `recorder-313.py`, `recorder-tick-313.py` (instance tick trace),
  `tick-lists-313.py`, `movering-313.py`, `nodevt-313.py`,
  `recall-sample-show.py`; emu.py has an optional `e.tracelog` list.
  Responder: `--hero-reset`, `T+N` token. Dump kept: livemode18-313-r
  (PID 16660, mid-rewind).

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
  Live 305 regression with it: Blink, firing (tracer+impact) and reload all
  work, so it is now in the best recipe (`HeroCmfdTicks=$true`).
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

## HUD transparency cause + teleport frame-domain test (Claude, 2026-10-16, run 332)

- **HUD widgets are created and visible but fully transparent.** Background agent
  (static + dump 294/257 emulation; `.local/re/hud-presenter-visibility.md`):
  visibility = widget property key 0xffffffffffffffff (map at widget+0x40) is 1 for
  HUD_Hero_Common 059d and HUD_Tracer 00f3. Their STUConfigVarColor properties
  2eab/2eac/2ead/4498/4499 hold RGBA ff ff ff 00 (alpha 0). Chain on hero 0x01cf
  (client-only stacks): #76 var 0x4769 = team(self) (comp25+0x58 bits 23..27,
  getter 0xb8af40) = -1; #80 global 0x45c2 = session team-colour GUID T+0x2c8[team]
  (0x641b70) = null; #84 global 0x0406 = colour record lookup (0x923170 against
  0x0460000000000105) -> no match -> 0x00ffffff. Emulation with 0x45c2 patched to
  0x0b3000000000001a yields opaque colours. Two missing inputs: (1) team filter bits
  on hero/controller (0x10040001 | 0x800000<<team, as local builder 0x829430);
  (2) session team-colour table (context slot 0x4e, getter 0x641d50, vft 0x2611ad8)
  empty. Online layer 1 is filled by queue component (vft 0x2610c68) methods 3/4
  0x5fa9a0/0x5f9bb0 from lists of 0x48-byte {GUID +0x10, team +0x18}; 0xb87060
  (team, guid) is another writer (callers 0xa2cc48/0xa2cc87). Corrections: presenter
  +0x240 = registration index; +0x248/+0x250 child list; +0xf0 transient flag;
  widget +0x60/+0x64 property-map free list. Second agent traces the online sources
  (`.local/re/team-sources-332.md` when done).
- New private responder option `--component-update 'IDX:EL:TYPE:U64[:SENDS]'`
  (driver `-ComponentUpdate`): module-4 op-2 one-field u64 component update.
  Run 333 tests comp26 = 0x10840001 (team 0) as an UPDATE (creates with comp26
  crashed in 266/267).
- **Teleport launch is not the frame domain.** `--snapshot-frame-source cmd|cmdlast`
  (driver `-SnapshotFrameSource`) puts the newest command (+1) into movement field 2.
  Run 332 (relative floor teleports `here+4,0,0`, gen, 4 sends): x/z snap, then y
  rises 3.5 -> 13.3 within 0.3 s, same as with server frames. Snapshot apply
  0x7ca130: template frame must match history ([rax+0x58]); new frame must exceed
  newest ring seq (0x7947e0 +8) else skipped; time = frame*16 ms (0xbb7100) or
  server tick when 0; velocity = dpos/dt only when gen (+0xc) unchanged, else the
  zero constant 0x3241710. So the launch is not injected velocity; likely
  depenetration/ground state from fields we leave at default. Create flag bit 1
  (0x78dab0 -> 0xc5f680 with prior 0x2f82d30) carries an initial movement state in
  the create descriptor (+0x1b0); untested.
- hero_pos_feed.py: OpenProcess now includes SYNCHRONIZE (old feeders never exited);
  writes `<out>.hist.jsonl` at 10 Hz. `.local/re/ui-pick-tracer.ps1 -Prefix <runs path>`
  automates menu -> Practice -> Tracer + CONTINUE + periodic screenshots.
- Run 333 invalid: responder crashed at emit() serializing bytes (fixed: emit uses a
  bytes->hex default). Run 333b: comp26 = 0x10840001 sent as op-2 updates to the
  controller (EL 80) and hero (EL 95). Client survives, but the final dump shows
  comp26 +0x90 = 0 and comp25+0x58 = 0 on both (team -1): the update is silently
  ignored (field flag 0x2 likely excludes it from replicated updates). Team bits
  need another path. Helper `.local/claude-scratch/session/team-bits-333.py
  <dump> <pid> <ids>`.
- **Teleport "launch" = placement ~10 m ABOVE the target, then settling on the first
  surface below** (runs 334/335c, relative teleports with dy 1.0/2.0/0.5 and gen):
  target y 3.0 -> 13.2 (spawn-room roof), 15.3 -> 30.6 (rock top), 31.0 -> 30.7.
  The very first pick spawn shows it too: hero appears at y 12.0 and falls through
  to the floor (1.75) in 1.3 s. Same with frame source server (334) and cmdlast
  (335c, native reconcile path), so it is not the frame domain. Ring append
  0xc5b640: local-predicted entities (+0xec68) send frames <= newest predicted to
  reconcile 0xc5c3e0 (0xc5c330 finds newest stored state with seq <= frame and
  0x64a530 overwrites it, then updates interpolation ring +0xe040); newer frames
  append; older frames return 2; same frame with lower gen returns 3. Next: find
  where the predicted sim re-places itself on a gen change (likely a safe-location
  trace starting ~10 m up); 0xc5a140's 10.0 vector is unrelated grid code.
  Runs 335/335b were early-instance failures (exit 1 after 5-6 datagrams).
- **Team bits + team colours (agent, `.local/re/team-sources-332.md`, emulated):**
  comp26's u64 field has flag 0x2 -> reader 0x3f0c20: one presence-mask byte then
  only non-zero LE bytes (team 0 = `0d 01 84 10`). Raw 8-byte values misdecode
  (runs 266/267 crash, 333b no-op). Responder now encodes comp26 with
  flagged_u64() in `--component-update` and `--filter-bits`. Team-colour GUIDs come
  from lobby 23310 (+0x138 list of 0x48-byte {GUID +0x10, team u8 +0x18}, teams 0/1)
  -> 0x6ce7f0 -> queue slot 4 0x5f9bb0 -> layer 1; layer 1 is used only when the
  world job byte +0x6e8 is set, written from welcome +0x518 (`--w518`). Private probe
  wrapper: env OW1_TEAM_COLORS="g0,g1" fills 23310 sent via OW1_QUEUE_FIRST; driver
  `-QueueFirst 23310 -TeamColors 0b300000000000f6,0b300000000000f7 -W518`.
  Run 336 tests the full combination.
- **Run 336 (team bits + team colours, PID 31988, dump retained as HUD reference
  `retail-private-livemode18-336.dmp`):** 23310 with f6/f7 accepted (165 B) before
  the referral; welcome +0x518 = 1; comp26 0x10840001 updates (flagged encoding)
  at EL 80/95. Dump: controller and hero comp26 = comp25+0x58 = 0x10840001, team 0.
  HUD_Hero_Common 059d and HUD_Tracer 00f3 are visible (vis 1) with OPAQUE colours
  2eab/2eac/4499 = 27aae1ff (friendly blue), 2ead ffffffff, 4498 000000ff
  (`.local/runs/widget-colors-336.txt`). Gameplay unaffected. **Screen still shows no
  HUD**, so the transparent tint was one defect, not the only one. Next: why visible,
  opaque top-level HUD widgets do not draw (attachment/render list, child element
  bindings, global HUD-hidden state).
- **Run 337: comp26 in CREATES works with the flagged encoding** (`-FilterBits
  '0:0x10840001;1:0x10840001;2..14:0x11040001'`): final dump controller/hero team 0,
  bots 0x80000306/07/10 team 1; no crash (supersedes the 266/267 "cannot be sent in a
  create" note, which was an encoding bug). Best recipe
  `.local/runs/run-livemode18-best.ps1` now includes FilterBits (players team 0,
  bots team 1), W518, QueueFirst 23310 and TeamColors f6/f7 (backup .bak337).
  HUD still not drawn; third agent investigating `.local/re/hud-render-336.md`.
- **TELEPORT LAUNCH SOLVED (run 340): it was the spawn-room barrier ejecting a hero
  with no team.** Run 339 (targets 10 m BELOW, no team) snapped to the target and was
  pushed up to the first free surface (y ~1.0): depenetration. Run 340 = run 334's
  teleports (gen, server frames, 4 sends, `here+3,1.0,0` / `here+0,2.0,-3` /
  `here-3,0.5,0`) plus team bits (FilterBits players 0x10840001, bots 0x11040001,
  W518, 23310 colours): all three land exactly at the target (3.02, 3.96, 2.43) and
  fall ~1 m to the floor (1.76-2.0). Earlier "+10 m launches" (runs 326-335) and the
  first-spawn y 12 were team-less heroes inside the spawn room's enemy barrier.
  Generation teleports are now usable for Recall/respawn/Blink when the hero has a team.
- **RECALL WORKS (run 341, best recipe + team bits + server Recall:** `Recall=3.0
  RecallCooldown=3.0 RecallRewind=0.9 RecallStepHz=0 TeleportGen TeleportSends=4
  TeleportDy=0.3` + run-326 RecallMirror; recipe `.local/runs/run-livemode18-341.ps1`,
  UI `.local/re/ui-pick-recall.ps1`). Feed trajectory: hero walks (48.69,1.96,37.41)
  -> (49.30,2.03,19.99); E at 19:44:42.74; at 43.71 the hero is at (49.33,3.39,26.87)
  = its feed position at 39.78 (3 s earlier) and settles to the floor; second recall
  likewise (to 16.49). No launch now that the hero has a team. The native Recall
  screen effect is not visible in the screenshots (mirror states only).
- **HUD hidden by OUR 0x0717 (agent, `.local/re/hud-render-336.md`):** UI side hosts
  HUD_Root 0502 under GameLayer 029b; HUD_Root hosts 05a7/05d0/00f3/0571; 05a7 hosts
  059d (corrects "top-level" note). UI manager 0xafb990 shows HUD_Root from
  0xa7f5e0 = UI global var 0x0734; graph 0x0cc9 node 6 (client-only, on game message
  0x0240000000000717) stacks 0x0734=false at priority 20 over 028c's true. 0x20e4
  #399 and hero 0x01cf set 0x2af6 on 0x0717 (hides 05a7/05d0). Dump 144 (pre-0x0717)
  has HUD_Root visible. 0x0717 came from `RetriggerControllerState='2:3:4'`
  (0x0cb6 state 3 = client-only send 0x0717). 0x0717 is the game's HIDE-HUD message.
  Run 342 = best recipe without the retrigger.
- **Run 342 (best recipe without RetriggerControllerState; PID 8416, dump
  `retail-private-livemode18-342.dmp` retained as the newest HUD reference):** no
  0x0717 sent. Dump: UI var 0x0734 = 1, HUD_Root gate 0xa7f5e0 = 1, HUD_Root 0502 vis
  1, 05a7 vis 1, 05d0/059d/00f3 vis 1 with opaque team-0 colours
  (`.local/runs/widget-colors-342.txt`). The cyan world chevron returns. **Screen
  still shows no HUD.** Best recipe now drops the retrigger. The agent continues on
  `.local/re/hud-render-342.md`.
- **Run 343 (best recipe, bot 2 moved to (48.71,2.0,29.0) straight ahead of the
  spawn view, team 1; `.local/re/ui-pick-shoot.ps1` fires without turning):** 8
  bursts -> server hits 53/106/159 -> bot_killed x3, bot_respawned x2. Screenshots
  show the bot, Tracer tracers and impact sparks on its body; on death the entity is
  destroyed and vanishes instantly (no death animation) and later shots hit the wall.
  No enemy health bar/outline visible (no HUD yet). Death presentation should use
  the bot's authored death state instead of an immediate destroy (todo).
- Run 344 (`--bot-death-hold 2.5`, driver `-BotDeathHold`: replicate health 0, keep
  the entity 2.5 s, then destroy): bot stays standing at 0 HP, no native death
  presentation. Bot def 04000000000014d2: STUHealthComponent m_73AEA60D
  [STU_9EA55F3D {05c0..0015, 0da0..000d}], graphs 0x33 (StatescriptStateHealthPool,
  ModifyHealth), 0xbe2, 0xa5b, 0x2206 (dumps `.local/re/graph-*-344.txt`). Agent
  decoding module-2 combat events -> `.local/re/module2-combat-344.md`.
- **Out-of-bounds respawn (run 345):** private responder `--respawn-below Y
  --respawn-delay S` (driver `-RespawnBelow/-RespawnDelay`): when the fed hero y drops
  below Y, generation-teleport to `--pick-spawn` after S s. Run 345 teleported the
  hero to (74,-1.5,9) with Y=-1.0: out_of_bounds at 20:09:35.7, back at the spawn
  (48.68,3.35,37.45 -> floor) at 20:09:37.9. A stale feed sample re-triggered once;
  a 2 s grace period now follows each respawn. Best recipe uses Y=-15 (an
  approximation; the original kill-volume rule/death sequence is not implemented).
  Responder log rows now carry `ts` (for diagnosing early instance failures: the
  failing client sends the same 21627/21600/21610 as good runs, then exits 1).
- **THE HUD DRAWS (agent, `.local/re/hud-render-342.md`):** the cyan chevrons ~80 px
  under the crosshair are HUD_Tracer's BlinkCharges control (not a world marker):
  present in every non-0x0717 run (pixel count 1950 vs 0). UI-node chain
  059d->05a7->HUD_Root->GameLayer->root all IsVisible 1. Remaining hero HUD content
  presenters are under server-driven BooleanSwitch false branches we never send:
  ammo inst10/0x16 switch 2(true)+29(false) -> presenter 31 (slot 68d4); Blink icon
  inst1/0x1a switch 21 -> 32 (5fdb); Recall icon inst2/0x24 switch 21 -> 32; ultimate
  inst3/0x34 switch 10 -> 13 (6869); health card inst11/0x01cf 15->66->139 -> client
  switch 79 (sync slot 15 = var 0x070f > 0) -> 37 (2d11); crosshair inst9/0x15
  11->23->42 -> client 28/26 -> 38 (reticle screen 02bc). Recipe bug: apply_hero_config
  replaced pick_states (recipe's 10:30,31 dropped); hero pick-state parsing now MERGES
  per-instance lists. Run 348 adds `PickExtraStates
  '6:3;2:0,21,32;1:29,22,16,21,32;10:2,29,31;3:10,13;11:15,66,139;9:11,23,42'`,
  StateData `16:2=1:1;16:29=0:1;1a:21=0:1;24:21=0:1;34:10=0:1;1cf:15=0:1;15:11=0:1;
  15:23=0:1,0:1`, PickExtraVars `11:s15=f200`.
- Key -> command bit (run 346, responder `buttons` events): Q 0x20, V 0x800, F 0x4,
  Ctrl 0x80, Space 0x40, Shift 0x8, E 0x10, R 0x400, fire 0x1 (C none). Tracer
  ultimate = graph 0x34 node #38 STUStatescriptStateAbility, logical button 0x25,
  condition (0x0156 op35 0x0152) && 0x1db5; 0x0152 copied by graph 0x4b; 0x34 resets
  0x0156 (float). Logical buttons: 0x23 Shift (0x24 Blink), 0x24 E (0x1a Recall),
  0x25 Q, 0x1f (graph 0x43, likely melee). Run 347 (0x0156=f99999) never pressed Q
  (key-list bug, fixed: `ui-pick-keys.ps1 -Keys 'Q,V'`).
- **ORIGINAL HERO HUD LIVE (run 348, recipe `.local/runs/run-livemode18-348.ps1`):**
  health card (bottom left), ultimate meter with Q prompt (centre, shown ready),
  Blink (LSHIFT, 3 charges) and Recall (E) icons, ammo 40/40 with the pulse-pistol
  icon. Live checks (`livemode18-348-hudstrip.png`): firing drains 40 -> 21, Shift
  Blink spends a charge 3 -> 2, R reload restores 40. Remaining: health reads 0/200
  (current value binding not fed; hero health pools are statescript graph 0x33
  instance 4 / STUStatescriptStateHealthPool) and no crosshair (inst9/0x15 client
  switches 28/26). The run-348 additions belong in the best recipe.
- Run 349 (ult charge 0x0156=f99999, Q/V presses): client sends Q 0x20 / V 0x800 but
  predicts nothing; meter unchanged. Run 350 (`ButtonStates '0x20:3:9:1.5'` = server
  activates 0x34 Ability state 9 on Q): client exits 1 immediately. Do NOT force
  Ability states (same failure class as the BlinkEffect attempt in run 160).
- **Combat agent (`.local/re/module2-combat-344.md`):** module 2 = projectile
  replication (section A volley/projectile-spawn records, emulator bit-exact 169/172
  bits; section B projectile physics); keep `1,0,0`. Combat feedback = reliable
  channel 2 family 25000 (dispatcher 0x7d1dc0; schema
  `.local/re/instance-combat-families-344.json`): 25001 hit confirm {target s32,
  amount s32, flags u8, frame offset s32} -> controller comp59 hit ring +0x12d0,
  counters, world notification 7; 25000 combat log (0x450-byte event on hero health
  component list +0x4c0; arrays +0xa8 >=3 and +0xd8 >=2 items). No native death
  record; health 0 alone never starts death (ragdoll code 0x1b18330 <- 0x1ae8203 is
  the next lead). **Health component bug fixed:** mask must be [1] (pool 0, 20 bytes);
  the old 9-bit mask over-read 9 pools (320/248 bits). Run 351 checks the HUD health.
- Run 351 (health mask fixed): health card still reads 0/200 (8 white segments full)
  -> the card's current value is not component 51 pool 0; HUD agent tracing
  (`.local/re/hud-render-348.md`).
- **Hit confirms work natively (run 352):** private responder `--hit-confirm-every N`
  (driver `-HitConfirmEvery`) queues a reliable channel-2 record 25001
  (`pack('<iiBi', target, amount, 0, 0)`) every N server-registered bot hits. With
  N=5: 31 sent, bot killed/respawned twice, client alive; final dump: controller
  0x80000304 comp59 hit ring (+0x12d0; cap 32, idx 25, count 26) filled. No visible
  hit marker yet (crosshair presenter not active). Best recipe gets HitConfirmEvery=5.
- Run 353 (`--bot-death-fields`: on kill, component 51 pool 0 = 0 HP plus fields
  48-52 = u32 0, u32 0, killer = hero id, u8 1, u8 1; held 3 s before destroy): bot
  stays standing, no death presentation, client fine. The ragdoll chain 0x1b18330 <-
  0x1ae7790 <- 0x1b0e280 <- scene/model code has no network trigger found. Death
  presentation remains open (likely server statescript states of the bot graphs).
- **Health number and ultimate meter fixed (run 355; agent `.local/re/hud-render-348.md`):**
  the card's CurrentHP is a statescript expression over hero globals 0x01de, 0x8398
  (must stay false), 0x06c9 current, 0x06c4 max; the ultimate meter = charge 0x0156 /
  cost 0x0152 (unset = "ready at 0%"). PickExtraVars `g:06c4=f200,06c9=f200,0152=f1000,
  0156=f350` -> card shows 200/200, meter 35% (Q not ready). Crosshair presenter
  (inst9/0x15 state 38) is gated on 0x0ebc, written only by StateStack 23 with is-top 1:
  StateData changed `15:23=0:1,0:1` -> `15:23=1:1,0:1`; still no visible crosshair in
  355 (checking the dump). General rule: StateStacks whose value matters need is-top 1.
- **Ultimate charge from hits (run 356):** private responder `--ult-charge
  'COST:START:PER_HIT'` (driver `-UltCharge`) injects hero globals 0x0152 (cost) /
  0x0156 (charge) and raises the charge per server-registered bot hit (snapshot at
  most every 0.25 s). With '1000:0:4' the meter climbs 0 -> 21 -> 36 -> 42 -> 63%
  while shooting the bot (`livemode18-356-ult.png`). Cost/rate are approximations,
  not the original charge rules; Q at 100% (server-side Pulse Bomb) is not
  implemented. Best recipe now uses UltCharge '1000:0:4'.
- **Two concurrent clients (design `.local/re/two-client-design-353.md`, static):**
  no single-instance check in the client (583 resolved IAT slots traced). Likely
  blocker: TACT/CASC shared-memory named mutex `Global\<storage path>` (name at
  offset 8 of each `shmem` file; 0x3347f0 CreateMutexW x2 then OpenMutexW) - a
  second client in a different AppContainer profile gets error 5 and exits 1
  (matches the DEVLOG 2026-10-13 second-launch 0x1). Proposed: launcher pre-creates
  both exact-named mutexes granting owner/SYSTEM/both client SIDs (Low label) for
  the run; pair mode with per-client profiles, bridges (1119/1129), jobs, one ACL
  capture/restore; second bnet probe on 21129; multi-player responder refactor.
  First step E0: launcher self-test of mutex behaviour across two profiles (no game).
  Never run two launcher processes concurrently (ACL save/restore interference).
- **Run 357 (UltCharge '1000:1000:4' = meter full, Q):** the client now PREDICTS the
  ultimate: pistols holstered (empty hands), hero HUD replaced (health/ammo/ability
  widgets gone) and a red prohibited marker at the meter position (`livemode18-357-k-Q.png`).
  Setting the cost 0x0152 was the missing condition (349 had it unset). The prediction
  is never confirmed by the server. End-of-run dump: instance 3 (0x34) has no running
  nodes (prediction long over). Run 358 dumps 0.3 s after Q to read the predicted
  states for a server mirror (as done for Recall).
- Responder `--extra-for-def GUID` (driver `-ExtraForDef`): PickExtraStates/PickExtraVars
  (hero-instance-numbered HUD states, Blink/Recall vars) now apply only to that picked
  definition; best recipe uses Tracer 0400000000000001 so hero changes (Soldier etc.)
  do not receive Tracer's instance numbers. Per-hero HUD presenter states still need
  deriving for the other heroes.
- **Muzzle origin cause (agent, `.local/re/child-entities-354.md`, emulated on 348):**
  the client creates ALL m_childEntityData children locally (0x17d3480 -> 0x1830a50)
  when their definitions are preloaded (keep -PreloadDefinition 0400000000000017);
  the server must NOT create them; comp136 is unrelated. Tracer's volley muzzles read
  hardpoint 0dc0000000000006 from the entity named by weapon-instance vars 0x0031 /
  0x0032, which hold CosmeticEntity NODE HANDLES {u16 1, u16 inst, u16 state, u16 0}
  resolved through comp47+0x11b0 (0x9a0c90 -> 0x9a0db0). Unset -> viewmodel root /
  hero origin = the bottom-centre tracers. Responder now has value kind 14 handles
  (`_handleval`, PickVars `h<inst>.<state>`): Tracer `10:s49=h10.1,s50=h10.0`
  (27 bits incl. kind nibble and StEC bit). Run 361 tests it (waits for the E0 build).
- **E0 two-client mutex self-test (agent; `.local/re/two-client-e0-360.md`; public
  `tests/offline_mutex.ps1`, CTest `offline-launch-mutex-namespace`, launcher
  `--self-test-mutex` / `--mutex-probe`):** inside an AppContainer `Global\` resolves
  to the package's own AppContainerNamedObjects directory. Different profiles get
  SEPARATE mutexes (no error 5; client descriptor create fails 1314, default create
  succeeds); same-profile processes share one; a host-precreated mutex is invisible
  to containers. So the CASC mutex does NOT explain the old second-client exit 1 and
  host pre-creation is useless. Recommended pair design: both clients in ONE shared
  AppContainer profile (shares the lock like a normal machine). E1 (second client to
  the menu) is the deciding test. Build + all 26 CTest targets passed.
- **MUZZLE ORIGIN FIXED (run 361):** sending weapon-instance sync slots 49/50 (vars
  0x0031/0x0032) as CosmeticEntity node handles `10:s49=h10.1,s50=h10.0` makes Tracer's
  volley originate at both pulse-pistol muzzles (blue muzzle flashes at the barrels,
  `livemode18-361-grid.png`); 3 bot kills, client stable. Promoted to the best recipe.
  Other heroes: set each CosmeticEntity state's output var to {1, weapon inst, state, 0}.
- **CROSSHAIR + HERO NAME LIVE (run 367; agent sections 5-6 of `hud-render-348.md`):**
  hero global `g:0ebc=b1` shows Tracer's reticle (the stack is-top bit alone does not set
  it); controller component 75 field 0 = picked hero GUID (`-ComponentUpdate
  '0:80:75:0x02e0000000000003'`, flagged u64 like comp26; responder now flags 26 and 75)
  makes the card show "TRACER". Portrait hexagon still empty: also needs hero 0x01cf
  instance var 0x3457, pushed by client stack state 67 (sent `11:...,138,67` and
  `1cf:67=1:1,0:1`; not yet effective). Promoted to the best recipe (backup .bak367).
- Muzzle handles generalized: generator `hero-weapon-config-180.py` now emits
  `cosmetic_handles` {slot: CosmeticEntity state} per hero (Tracer {49:1, 50:0}
  matches); merged into `.local/runs/hero-configs-mode18-362.json`; apply_hero_config adds
  `s<slot>=h<weapon inst>.<state>`. Best recipe uses mode18-362 (hand-set Tracer vars removed).
- **Soldier FIRST pick exits the client (runs 363-366)** ~0.7 s after the first hero full
  frame, with or without muzzle handles (364 control), with PickSubgraph gated to Tracer
  (365; responder EXTRA_OK) and without UltCharge (366). Cause not yet found; next: dump
  0.1 s after hero_cmfd and replay the frame in ssfull2.py.
- **Pair mode for two concurrent clients (agent; `.local/re/two-client-pair-362.md`):**
  launcher `--retail-private-pair` (public wrapper `scripts/Start-PrivatePair.ps1`,
  CTest `offline-launch-pair-guards`, 27/27 pass): one shared AppContainer profile,
  one ACL capture/restore, per-client job/bridge (container 1119 / 1129)/observers/
  dump, `--run-for` shared bound, `--client-delay`, strict guards. bnet-probe accepts
  own-key referral 127.0.0.1:1129 only with --port 21129 (credential carries the port).
  Private driver `.local/re/run-live-pair.ps1 -Name pair-e1-363 -RunFor 300
  -ClientDelay 60` (accounts Mercy#1002 / Tracer#1001); ow-ui.ps1 `-ProcessId`.
  Whether the client honours a non-1119 --BNetServer port is unverified (E1 shows it).
- Portrait (agent section 7): server-activated stacks never push their own value
  (0x1b95ff0 modes 1/2 skip push/var write), so 0x3457 needs the authored path:
  deliver game message 0x02400000000009cc to the hero via sender graph 0x0b6c state 7
  (create 0x0b6c on the hero, then activate 12:7 with `b6c:7=0:1`); hero states
  `11:15,66,138,139` without 67.
- **E1 PASSED (run pair-e1-363): two original clients at the main menu simultaneously**,
  Mercy#1002 (c0, container 1119 -> probe 21119) and Tracer#1001 (c1, container 1129
  -> probe 21129, referral 127.0.0.1:1129), one shared AppContainer profile, both
  alive at the 300 s bound (`Pair summary: c0=alive-at-bound c1=alive-at-bound`).
  The client honours the --BNetServer port. Screenshot `pair-e1-363-both.png`. Cleanup:
  probes/launcher/clients gone, listeners gone, profile deleted, both ACLs exact,
  original hash + Valid signature. Driver fix: `run-live-pair.ps1` must not wrap
  ConvertFrom-Json in @() (PS 5.1 makes the array one element; first attempt failed at
  probe startup with missing --cert/--key, clean). Next E2: both into one instance
  session (instance_referral port parameter, multi-client responder).
- Run 369 (portrait attempt: hero PickSubgraph `12:0x0b6c:0:0`, GRAPH_COUNTS 0xb6c=(4,35),
  0xb6c state types added to graph-state-types.json, HeroLateStates `12:7` +
  StateData `b6c:7=0:1`, hero states `11:15,66,138,139`): client stable; the card now
  shows a level badge "6 | TRACER" but the portrait hexagon is still empty. Dump 369
  sent to the HUD agent. Responder: BlinkChargesVar now also gated by EXTRA_OK
  (Tracer instance 2 = Blink graph; for Soldier instance 2 is 0x4b).
- **Tracer ultimate plan (agent, `.local/re/ult-mirror-359.md`, emulated on 358-q):**
  the 0x34 Ability (state 9, node 31) sits in the FALSE branch of BooleanSwitch 11
  (global 0x1880), reached from server Entry #1 -> SetVars 0x18e0/0x1cdd/0x00d7 ->
  Stack 12 -> switch 11; our server never entered 12/11/9, so 358 had no prediction
  (357's stuck holster unexplained, no dump). Ability state data = 10 bits
  (`0:8,0:1,1:1,0:32,0:1,0:1,0:8` per emulator) - run 350 crashed for lack of it.
  States: 0 WeaponVolley throws projectile 0400000000000045 (graph 0x0c1b, explosion
  on message 0x02400000000005d4), 1 Anim, 2 Wait .15, 3 CosmeticEntity bomb-in-hand
  04000000000000ea, 5 Wait .2 + 14 Stack (0x034a), end action #128 clears 0x0021.
  Step 1 recipe: PickExtraStates `3:9,10,11,12,13`; StateData `34:12=1:1,0:1;34:11=0:1;
  34:9=0:8,0:1,0:1;34:0=0:1,0:1,0:8,0:1,0:1,0:6;34:14=1:1,0:1`; PickExtraVars
  `3:s32=i15,s29=f30,s23=f0.5`; UltCharge full. Steps 2/3 (AbilityPress mirror;
  `patch_ultmirror-359.py` adds --ult-use-button/--mirror-needs-ult and fixes state 0
  never being sendable inactive) are prepared, not applied. Bomb stick/explosion = design.
- **Soldier first pick fixed (run 370b):** the crash was Tracer's BlinkChargesVar
  ('2:11:3:3.0') written into Soldier's instance 2 (graph 0x4b); now gated by
  EXTRA_OK. Soldier: pulse rifle, 8 volleys, 3 bot kills, tracer leaves the rifle muzzle
  (generated cosmetic handle s50=h11.11 works). No hero HUD for non-Tracer heroes yet
  (red marker at the meter position); per-hero HUD presenter states/vars still to derive.
  Run 370 was invalid (probe crashed: E2 agent changed tools/lobby_service.py
  local_referral(port); private probe_record_inputs.py wrapper now passes *args).
- Run 371 (ult step 1, Q dump `retail-private-livemode18-371-q.dmp` PID 34048): client
  stable; the ult meter shows a large glowing Pulse Bomb icon; no throw/holster/
  projectile visible. Dump with the ult agent. Separate agent deriving per-hero HUD
  configs (`.local/runs/hero-hud-configs-372.json`, patch script, notes
  `.local/re/hero-hud-372.md`).
- **HERO PORTRAIT LIVE (run 372; agent section 8 of hud-render-348.md):** hero sync var
  0x070f (01cf slot 15) IS the portrait texture (card property 070f bound to it);
  sending `11:s15=g0c0000000000128e` (Tracer's portrait texture, = hero-select property
  4447 / hero record m_8203BFE1 entry 0d80..40c9) shows Tracer's face beside the
  health bar (`livemode18-372-full.png`), with name, health, crosshair, ult, abilities,
  ammo. Earlier 6dff/0x3457/0x0b6c work only feeds the role icon. Best recipe updated.
  Other heroes: send their record's m_8203BFE1 0d80..40c9 texture (key assumed same).
- Ult (run 371 dump, agent section 8): Ability state 9 ran and consumed the Q press;
  no projectile; likely rolled back because our frames keep idle Ability data and
  0x0156=1000. Next: apply `patch_ultmirror-359.py`, then AbilityPress
  '34:9:0x20:0.6:0:8,0:1,1:1,0:32,0:1,0:1,0:8', UltUseButton 0x20, dumps/shots
  at 0.1-1.0 s after Q.
- **E2 groundwork (agent, `.local/re/two-client-e2-364.md`; nothing launched):** public
  `local_referral(port)` / `InitialLobby(instance_port=)` allow-list {1119,1129}; bnet-probe
  refers the instance to the same port as its allow-listed own-key lobby referral (1129 only
  with --port 21129); `tests/bnet_probe.py` 26 pass. New private multi-client responder
  `.local/re/udp_pair_reply.py`: one session per client = an exec of the UNEDITED
  udp_welcome_reply.py with socket/time/argparse shims (all per-client state separate),
  dispatcher binds each host-bridge source port by that client's own +0xae key, index bases
  c0 0x300 / c1 0x340 (heroes 0x80000305 / 0x80000345), opt-in `--proxy-heroes` creates the
  other player's picked hero (flags 0x41 + skin, comp26/51) and streams its position.
  Offline: 8 tests + concurrent replay of runs 368/369 (all reply headers identical; 369
  bodies identical except the elapsed-ms field). Driver `.local/re/run-live-pair-game.ps1
  -Name pair-e2-365 -UI [-ProxyHeroes]` (`-DryRun` composes only; reuses run-live-preload.ps1's
  own argument blocks), UI `.local/re/ui-pair-game.ps1`. E2/E3 live behaviour unverified.
- **TRACER ULTIMATE (PULSE BOMB) WORKS (run 373):** applied `patch_ultmirror-359.py`
  (--ult-use-button, --mirror-needs-ult, OFF0 so state 0 can be sent inactive); recipe =
  371 + `AbilityPress=@('34:9:0x20:0.6:0:8,0:1,1:1,0:32,0:1,0:1,0:8')`,
  `UltUseButton='0x20'`. Q at full meter: meter -> 0, pistols holster, throw animation,
  pistols return, the bomb flies out (blue orb) (`livemode18-373-grid.png`). The
  client predicts the chain; the server confirms the Ability for 0.6 s. Promoted to the
  best recipe (meter charges from hits; backup .bak373). Bomb stick/explosion damage on
  bots is server design only (projectile 0400000000000045, graph 0x0c1b, message 0x05d4).
- **E2 PASSED (pair-e2-366): two original clients in ONE instance session at once.**
  `.local/re/run-live-pair-game.ps1 -Name pair-e2-366 -UI -PairDump none` with the new
  multi-client responder `.local/re/udp_pair_reply.py` (per-client sessions: own
  referral keys, source port binding, sequences, statescript frames; ids 0x300/0x340):
  c0 (Mercy, 1119) and c1 (Tracer#1001, 1129) both bound, hero select, picked Tracer,
  full HUD (portrait/name/health/crosshair/ult/abilities/ammo) in both
  (`pair-e2-366-both.png`). First attempt pair-e2-365: c0's menu clicks came before its
  menu existed (two simultaneous logins); `ui-pair-game.ps1` now retries menu clicks
  until the client's `bound` event (up to 3). No proxies yet (players do not see each
  other); E3 = `-ProxyHeroes`.
- Per-hero HUD (agent, `.local/re/hero-hud-372.md`): `.local/runs/hero-hud-configs-372.json`
  for all 32 playable heroes (portrait textures, comp75 hero GUIDs, HUD 0x01cf
  subgraph under 0x4b state 3, presenter chains); patch
  `.local/claude-scratch/session/patch_hero_hud-372.py` (+ driver) adds
  `--hero-hud-configs`. Tracer verified by native decoder; others encoder-only.
- **E3: the two players SEE EACH OTHER (pair-e3-367, `-ProxyHeroes`):** both bound,
  both picked Tracer; each client got the other's hero as a proxy (same entity id as in
  its owner's world, skin 0a5000000000170f, team bits, health), moved by module-3
  snapshots from the owner's tracked position. Screenshots (`pair-e3-367-both.png`):
  c0 sees c1's Tracer, c1 sees c0's Tracer. Defects: proxies float above the floor in a
  fixed pose (no locomotion animation, no yaw), no weapon visuals, no PvP hits, bots per
  session. Next: proxy height/animation (movement-state fields: velocity/grounded/yaw),
  then shooting each other.
- Per-hero HUD patch applied to the responder/driver (backups .bak372); best recipe has
  `HeroHudConfigs='.local/runs/hero-hud-configs-372.json'` (live check pending).
- **Per-hero HUD live for Soldier: 76 (run 374):** hero_hud entry applied (states
  `2:3;5:17,31;6:7,16;7:15,32;10:11,23,42;11:0,9,40,67,69,70;12:15,66,139,138,67`,
  subgraph `12:0x01cf:2:3`, comp75 0x02e000000000006e): portrait, "SOLDIER: 76", 200/200,
  crosshair, ult meter (charges from hits), Sprint/Biotic Field/Helix icons, rifle and
  ammo (`livemode18-374-full.png`); 3 bot kills. Ammo max is still the generic 40
  (Soldier 25): per-hero magazine sizes still needed in the ammo option.
- **REGRESSION (run 375): in-game hero change Tracer -> Soldier with per-hero HUD fails**:
  hero_hud for Soldier applied on re-pick (hero_repick logged), but Soldier spawns with
  no weapon, no HUD, red marker (`livemode18-375-grid.png`). First-pick Soldier works
  (374). Suspect: re-pick resets (HERO_SNAP seq/sub-graph instance numbering) vs the
  new HUD subgraph (12:0x01cf) or merged Tracer instance states. Next session: fix the
  re-pick path, then resume: proxy height/pose/yaw (E2 agent was stopped mid-task;
  its note `.local/re/two-client-e2-364.md`), per-hero ammo/reload params (agent
  stopped; target file `.local/runs/hero-weapon-params-375.json`), Pulse Bomb
  explosion, bot death presentation, early instance failure.
- Session end 2026-10-16: usage limit reached; agents stopped. Best recipe
  `.local/runs/run-livemode18-best.ps1` (Tracer HUD incl. portrait/crosshair/name,
  muzzle, Pulse Bomb, Recall via run-341 options, per-hero HUD configs).

## 2026-10-17 (Claude) - party flow already done by Codex; remote player fixed to the floor

- User asked for party -> leader starts Practice. Codex had already verified it overnight
  (docs/PARTY_PROTOCOL.md: Nearby Players 20815 -> native Invite 22102 -> merge 20703 ->
  Yes 22110 -> 2-member roster; leader alone starts Practice, both referred to their own
  endpoints; pair-social-381/382). My redundant static-party edits were reverted.
- **Remote player height fixed:** dump pair-e3-385 (c1 dumped 10 s after the proxy was
  placed; `dump_on_log_regex.py` now takes `<owned-pids.json> c0|c1`): proxy render
  comp1+0x440 = (48.73, 2.93, 38.13) for snapshot (48.71, 2.00, 37.77): remote heroes
  draw ~0.93 m above the snapshot y. `udp_pair_reply.py --proxy-dy` (default -0.93,
  backup .bak386). pair-e3-386: from c1 the remote Tracer stands on the floor and runs
  (stride animation) when c0 walks (`pair-e3-386-move.png`, `-m1-zoom.png`).
  Remaining: no pistols on the proxy (needs the remote hero's weapon/cosmetic statescript
  states), yaw not replicated, no PvP, separate bots per session. Helper
  `.local/claude-scratch/session/entpos-384.py` (comp1 +0x90/+0x440 by entity).
- **Hero change fixed (run 387):** the re-pick kept the first hero's HeroCmfdTicks tick
  (cmfd_seq/cmfd_tick survived because HERO_SNAP seq resets to the same 0), so the new
  hero's frames carried a stale CmFD (run 375: one hero_cmfd event; Soldier without
  weapon/HUD). Re-pick now also pops cmfd_seq/cmfd_tick; 387 logs a fresh hero_cmfd
  (2311) and Tracer -> H -> Soldier spawns with rifle, portrait, "SOLDIER: 76", health,
  crosshair, ult, abilities, ammo (`livemode18-387-grid.png`).
- **Proxy facing + weapons (agent, offline, `.local/re/two-client-e2-364.md` section 7):**
  udp_pair_reply.py now replicates the owner's command yaw as movement field 13 (s16 euler yaw,
  emulator-verified: +y rotation, forward=(sin,0,cos); default on, `--proxy-yaw-offset`,
  `--proxy-pitch` opt-in) and, with `--proxy-weapons` (driver `-ProxyWeapons`), creates weapon
  manager 0x15 + weapon script 0x16 on the proxy (instances 1/2) with states 39,43 / cosmetic and
  mirrors the owner's volley/reload states; all frames aligned on dump pair-e3-385-c1-proxy
  (`.local/re/ssproxy-390.py`). Live rendering effects unverified. Backups *.bak390.
- **Pulse Bomb run 392** (patches patch_pulsebomb-359 + patch_mirrorreset-359 applied;
  recipe `.local/runs/run-livemode18-392.ps1`: AbilityPress removed; RecallMirror for Q
  with reset frame (`MirrorReset`), RecallPhase2, MirrorNeedsUlt, UltUseButton,
  `PulseBomb='350:2:4:0.2:1.0:15:30:5'`, UltResend, `0021=b0`): events in order
  pulse_bomb (point 48.71,1.93,32.46, fuse 1.33 s) -> recall_mirror_on -> ult_used ->
  mirror_reset_frame (CmFD 1821) -> recall_phase2 -> recall_mirror_off ->
  pulse_bomb_detonated (bot 2 at 2.53 m: 70 dmg). Throw animation plays, the meter
  now STAYS at 0% (reset stops the 0.64 s rollback; 388/389/390 restored 1000). No bomb
  or explosion visible yet (client-predicted projectile absent; server projectile path
  = definition 0x45 entity + module-2 sections A/B still to do). Run 389's 'orb' was the
  HUD ult-ready burst, not an explosion.
- Proxy weapons/yaw (pair-e3-391, `-ProxyWeapons`): statescript create (0x15/0x16) and
  full frames sent, client stable, but no pistols on the remote Tracer and facing did not
  visibly change; the 'running stride' is probably just the static default pose.
  c1 dump `retail-private-pair-e3-391-c1-weap.dmp` with the pair agent.
- Per-hero weapon params patch applied (`--hero-weapon-params`,
  `.local/runs/hero-weapon-params-375.json`; Soldier 30 rounds / 1.5 s reload; Tracer
  unchanged 40/1.0); best recipe uses it (not yet live-checked for non-Tracer heroes).
- **Proxy dump 391 + fix (agent, offline, `.local/re/two-client-e2-364.md` section 8):** proxy
  statescript instances/cosmetic states run and its two 3P pistol children exist and resolve,
  but sit near the feet (not attached), pose is static and the model ignores the (correctly
  replicated) yaw. The proxy lacked comps 69/86/122/136, which bots have natively and the local
  hero gets from create flag 0x80. Responder now creates proxies with flags 0xC1
  (`--proxy-create-flags`, default 0x80) and sends movement field 19 velocity (state +0x90,
  emulator-verified). Next live: `run-live-pair-game.ps1 -Name pair-e3-393 -UI -ProxyHeroes -ProxyWeapons`.
- **Pulse Bomb investigation (runs 388-400; agent `.local/re/ult-mirror-359.md` §9-11):**
  the client's volley fire (0xae6df0 -> job 0xae88a0) queues a projectile REQUEST in world
  context slot 44 (+0x20 list; key hero<<32|inst<<19|node<<8|shot = 0x8000030500180001,
  definition 0x0400000000000045) whose projectile-entity list stays EMPTY; module-2 update
  0xb3b1f0 -> 0xb3e490 only simulates linked server entities. So no bomb ever renders
  until the server creates a 0x45 entity and links it via a module-2 section A record.
  Runs 389/398 screen bursts: no bomb in any frame ('orb' = HUD ult-ready burst); 398
  shows a double throw. Patches applied: pulsebomb (server arc/stick/fuse/damage,
  25001 confirms), mirrorreset (reset frame at Q -> meter stays 0, run 392),
  pulsebomb2 (stick to bot body), bombentity (+bombentity2 ordering fix:
  `-BombEntity IDX` creates/destroys a 0x45 entity; 399/400: client survives, model not
  rendered, bot killed by 350 server damage). Dumps for the section A link design:
  retail-private-livemode18-{394-u040,395-u100,396-A,400-bomb}.dmp.
- Soldier weapon params live (run 393): HUD 30/30, auto reload, 3 kills.
- **Dump 401 (agent, `.local/re/two-client-e2-364.md` section 9):** proxy now has the own hero's
  component set; movement state carries yaw/velocity and comp4 follows, but comp1 (world transform)
  is frozen at the create pose and the mover/comp86 never run for it (zeros, like bots). The own
  hero is a controller's comp44 actor; the proxy is nobody's. New `--proxy-controller` (driver
  `-ProxyController`) creates the other player's controller (its id, def 0e, flags 0x30, comp44 =
  proxy hero, comp74 team 0) before the hero; bit-identical to the live controller encoder.
  Next live: `run-live-pair-game.ps1 -Name pair-e3-403 -UI -ProxyHeroes -ProxyWeapons -ProxyController`.
- **Remote player (pair-e3-401/403):** create flag 0x80 + velocity (401) gives the proxy
  the same component set as the own hero (incl. 69/86/122/136) and its movement state
  follows the owner (yaw, velocity), but its comp1 world transform stays at the create
  pose and its mover (comp31/86) never runs -> static pose, no turn, pistols near the
  feet (agent). 403 adds `-ProxyController` (other player's controller 040000000000000e
  with comp44 actor = proxy hero, flags 0x30): created, client stable, visuals unchanged.
  Walk dumps: retail-private-pair-e3-{401,403}-c1-walk.dmp. Next: trace what drives a
  non-local hero's world transform (compare with bots, which move correctly).
- **Dump 403 (agent, two-client-e2-364.md section 10):** proxy controller exists and comp44
  resolves, but proxy comp1 (hero model transform) stays at its create pose and is not linked in
  the transform graph (own hero comp1 +0x2b8/+0x4c0../+0x850 set, proxy null); comp4/comp24 follow
  the movement (this is how bots render: their comp1 is stale). The native writer for a non-local
  hero's comp1 was not found. New per-viewer experiments: `--proxy-remote-bit-viewers`,
  `--proxy-transform-viewers` (driver `-ProxyRemoteBitViewers 0 -ProxyTransformViewers 1`).
- pair-e3-405 (`-ProxyTransformViewers 1` create transform for c1's proxy,
  `-ProxyRemoteBitViewers 0` snapshot slot-1 remote bit for c0's proxy): stable; c1's
  view unchanged (static pose); c0's view inconclusive (proxy displaced after the owner
  strafed). Dumps retail-private-pair-e3-405-{c0,c1}.dmp with the pair agent; next is
  the native scene/animation registration that links a hero's comp1 (+0x2b8/+0x4c0/+0x850).
- **Proxy test motion (agent, two-client-e2-364.md section 12):** `--proxy-test-motion
  VIEWER:circle|strafe|still[:radius,speed,dx,dz,yaw=spin|path|s16,spin,form=remotebit|velocity,fire]`
  (driver `-ProxyTestMotion '1:circle:fire=1;0:strafe:dz=2.5,form=velocity'`) moves a viewer's
  proxy on a deterministic path, no owner input needed. Proxy code errors no longer stop a session.
- **REMOTE PLAYER ANIMATES (pair-e3-410):** server-side `--proxy-test-motion`
  ('1:circle:radius=1.5,speed=3,fire=1;0:strafe:dz=2.5,form=velocity,yaw=path') with the
  movement-state slot-1 "remote bit" (+4 = 1, positions q/256, client derives velocity):
  from c1 the remote Tracer follows the circle, turns, plays running animation and holds
  a pulse pistol (`pair-e3-410-grid.png`, `-m4-zoom.png`). So the remote-bit form selects
  the client's remote-character render path (comp1 is irrelevant for remote heroes).
  Next: real owner motion with `-ProxyRemoteBitViewers 0,1` (407 was invalid: ow-ui
  keyboard focus failed; ow-ui.ps1 now Alt-taps + verifies foreground, backup .bak407).
- Bomb link (408/409): section A record links the 0x45 entity (comp50 +0x40 key, +0x76=1,
  pending list consumed) but aimed +z (backwards into Tracer); patch_bomblink2-359 uses
  the command aim. Double throw at ~1.2 s may be the 1.2 s UltResend.
- **PULSE BOMB EXPLODES ON SCREEN (run 411):** patch_bomblink2 (section A record aimed
  with the command yaw/pitch) + run-408 recipe without UltResend
  (`.local/runs/run-livemode18-411.ps1`): the linked server 0x45 entity flies forward and
  the client's projectile system plays the blue explosion at ~0.79 s and smoke at ~1.0 s
  at bot 2 (`livemode18-411-burst.png`); server detonation (350 dmg) kills the bot at
  1.24 s. Open: visual detonation precedes the server damage by ~0.45 s (align fuse with
  the client's impact/fuse), and the throw animation still plays twice without
  UltResend (second volley from the phase-2 timeline?).
- **Proxy facing/pistols (agent, two-client-e2-364.md section 13):** audit of pair-e3-412 shows
  the owner's yaw reaches every proxy snapshot (field 13, +4 form); the 44-deg stationary look
  did not visibly turn the body. Proxy weapon script now activates the cosmetic BooleanSwitch
  (Tracer 0x16 state 2) like the local hero (aligned on dump 385). Remote bit is now default.
  Decisive next test: `-ProxyTestMotion '1:still:yaw=spin'` (stationary spin, idle pistols).
- **pair-e3-414 (still spin):** `-ProxyTestMotion '1:still:yaw=spin'`: from c1 the stationary
  remote Tracer turns in place and holds both pistols (idle pose). Body yaw from snapshot field
  13 renders; the 412 non-turn was the small (44 deg) look. Next: real owner 180 deg look (415).
- **Pulse Bomb promoted (run 416, best recipe):** patch_mirrorreset2-359 (reset ack frame's CmFD
  never goes backwards) + MirrorOnRelease + PulseBombAt 0.8 + BombEntityAuto/BombLink 3 are now in
  `.local/runs/run-livemode18-best.ps1` (backup .bak414). Verified 416 (`livemode18-416-burst.png`):
  ult-ready -> Q -> ONE throw -> blue explosion on bot 2 with server 350 dmg kill at the same time
  -> meter 0% and stays 0% (late frame), bot respawns. No rollback, no double throw.
- **pair-e3-415 (real owner turn):** default remote bit, no test motion; ui-pair-game.ps1 now also
  fires c0 (`-FireC0 1`, 1.2 s mousehold after its shots 2 and 4). c0 turns ~180 deg toward c1:
  c1 sees the remote Tracer FACING it with both pistols raised (`pair-e3-415-grid.png`,
  `-c1-zoom.png`); c0 likewise sees c1's front. c0 ammo 40 -> 31. Remote muzzle flashes were
  not caught in the 6 s screenshots. All 12 cleanup checks pass.
- **SERVER-AUTHORITATIVE PvP DAMAGE (pair-pvp-417):** private `udp_pair_reply.py --pvp-dps N`
  (driver `-PvpDps`; patch_pvp-417.py, backup .bak417) ray-tests each player's active volley
  (command yaw/pitch from the session's newest command, eye = feed +1.5 m) against the other
  player's proxy as the shooter sees it (last proxy snapshot - dy, body center +1.0 m, r 0.5,
  half-height 1.0), subtracts dps*dt from the victim's server health, queues 25001 hit
  confirms on the shooter (target = proxy entity), and gives the victim its health through
  hero global 0x06c9 (responder hook `HERO_SNAP['hp']`, udp_welcome_reply.py .bak417) plus its
  own hero comp51 and the proxy's comp51 in the other client. Kill -> 3 s -> respawn teleport.
  417 (dps 100, c0 turns 180 deg and fires at c1 2.15 m behind): 89 hits / 6 confirms, c1's
  OWN HUD drops to 58 with the NATIVE low-health red vignette (`pair-pvp-417-grid.png`,
  `-c1-health.png`). The card read 58/59: `health_component(v)` writes v into BOTH pool floats
  (current and max); pair layer now sends `pvp_health(hp, max)`. No kill (2nd burst missed).
  All 12 cleanup checks pass.
- **First player kill (pair-pvp-418, dps 200):** c0 kills c1 in ~1.0 s (75 hits, 11 confirms),
  c1 respawns 3 s later (`pvp_kill` / `pvp_respawn`). c0's 2nd burst had 1 round left (fire_hold
  40 drained 39) -> reload, no hits. c1's card froze at 163/165: dump
  (`.local/claude-scratch/session/pvp-health-418.py <dump> <pid> 80000345`) shows hero comp51
  pool 0 = current +0xdc 164.3 / max +0xe0 200 (so pool floats are current, max) while all hero
  statescript frames applied (cf 19, CmFD 2301 = last sent, queue 0). Cause: the pair wrapper
  drops the plan when the base body carries creates, but combat() had already marked the own
  hp as sent. Fixed: own-hp sends commit only in commit(), plus a 1 s refresh. c1 screenshots
  started after the respawn, so no death view; ui-pair-game.ps1 now fires c0 after its shots
  4 and 7 and shoots c1 four times right after each burst (`-c1-k<shot>-<n>.png`).
- **pair-pvp-419 (own-hp commit fix, dps 200):** kill + respawn; victim view right after the kill
  shows the card **"-1/0"** with empty segments, then **200/200** after the respawn; after a
  5-round burst it reads 171/172 (`pair-pvp-419-c1-health.png`). Per hud-render-348.md the big
  number is CurrentHP(0x06c9, 0x06c4; non-integer -> -1) and "/N" is Health.TotalAmount from
  comp51; "/N" followed the FIRST pool float every time (165, 172, 0), so the pool order is
  (max, current) and `pvp_health` now packs (1, max, hp, ...). No native death presentation
  (view/weapons unchanged at 0 HP). 12/12 cleanup checks. c0's 2nd burst had 5 rounds (no reload
  between bursts); ui-pair-game.ps1 now presses R after each c0 burst.
- **NATIVE PLAYER DEATH (pair-pvp-420):** `--pvp-dead-flag` (driver `-PvpDeadFlag`) sets the
  victim's hero GLOBAL **0x01de = true** at the server kill (hero full snapshot via the new
  responder hook `HERO_SNAP['gvars']`, udp_welcome_reply.py) and clears it at the respawn; with
  the pool order fixed to (max, current). c0 killed c1 twice (129 hits, 19 confirms, 2 kills,
  2 respawns). Victim view (`pair-pvp-420-kills.png`, `-death-zoom.png`, `-c1-health.png`):
  card **0/200** with grey segments and red vignette, **pistols removed, camera detaches from
  first person** (own head visible, then a low view) = original death presentation; after the
  3 s respawn the card refills to 200/200 and the pistols return with the equip animation.
  Second kill identical. So 0x01de is the hero dead flag (hud-render-348: forces CurrentHP 0).
  Not yet: killer's view of the proxy dying, kill feed, death recap/killcam, respawn timer UI.
  12/12 cleanup checks, empty UDP stderr. Dumps deleted.
- **Killer view of the death (pair-pvp-421):** with `-PvpDeadFlag` the pair layer also mirrors the
  owner's dead flag (global 0x01de) into the proxy's full statescript frame (proxy svars[0]).
  c0's view of c1's proxy (`pair-pvp-421-c0-proxy.png`): pistols aimed before the kill; while dead
  the proxy's PISTOLS VANISH and the hands drop; after the respawn the pistols return. No body
  collapse/ragdoll/kill feed. `-PvpCombatLog` sent 19 victim 25000 records (98 B each, gateway
  codec + instance-combat-families-344.json) without errors; no distinct damage-direction arc
  visible in the screenshots. 2 kills / 2 respawns, 12/12 cleanup, empty UDP stderr.
  ui-pair-game.ps1: alternating c0/c1 kill shots; new `-UiFireC1` (driver) makes c1 fire back
  after its shot 6.
- **MUTUAL PvP (pair-pvp-423; 422 = intermittent c1 startup exit 0x1 before login, cleanup ok):**
  `-UiFireC1` makes c1 return fire. 189 hits, 28 confirms, 3 kills (c0->c1 x2, c1->c0 x1), 3
  respawns. `pair-pvp-423-return.png`: c0 killed by c1 -> c0's own view 0/200, red vignette,
  pistols removed; c1's view of c0's proxy drops its pistols; c0 respawns 3 s later at 200/200
  with pistols. Both directions of server-authoritative damage/death/respawn verified on two
  real clients. 12/12 cleanup, empty UDP stderr. Kill-feed trace (25011..25013) running.
- **Channel-2 25011/25012/25013 (agent, offline, `.local/re/killfeed-25011-422.md`):** 25011
  (0x6c3940) is NOT the kill feed. It stores ONE "killed by" record in global-root slot 12
  (vt 0x2611310). The Kill_Cam_Overlay presenter (0xace460) and the killcam replay follow target
  read it: +0x78 killcam entity, +0x7c killer controller (== local -> attacker hidden),
  +0x80 AttackerName, +0xb0 killer hero GUID (AttackerHero), +0xd8 kind (5 hides).
  VERIFIED-EMU on dump 416 (`session/kf-emu-422.py`). The overlay is probably shown only in
  killcam mode, so 25011 alone probably stores data invisibly. 25012 (0x6c3fe0) / 25013
  (0x6c29c0) = slot 13 highlight/POTG records plus cosmetic preloads; do not send them for kills.
  The kill-feed source is still unidentified (not channel-2 UI messages, not HUD statescript
  entries); next candidates are 25010 (0x7a5740) and the channel-3 world+0x138 consumers.
- **Map GUIDs in lobby 20505 lists CRASH the client (runs 424..424f, single client, mode 18):**
  experiment to replace the native header-preload control with the original lobby inputs. 424/424b
  (list 2 map set = header 0790..0688 + map 0800..0688, list 1 = header) and 424d (list 2 only):
  client exits 0x1 after 4 instance datagrams; 424c (list 1 header only): exits 0x1 right after
  the lobby reaches phase 6. Controls: 424e (best recipe, native control) and 424f (best recipe
  WITHOUT native control, no lists) stay alive to the bound. So map/map-header GUIDs must not be
  sent in 20505 lists 1/2 in this form; the public probe options were reverted (never committed)
  and the private driver restored (.bak424). Native header control remains the only map loader;
  other maps/modes still need the original header-load trigger. All 7 cleanup checks pass x6.
- **Original map-header trigger (agent 425, offline; `.local/re/map-header-trigger-425.md`):** headers
  are preloaded at LOGIN from lobby 20505's THIRD array (offset 168, "list 2"): 0x77a000 -> 0x57bba0 ->
  0x57c700(type 0x9F, provider+0x98 set) -> 0x171a9b0 -> 0x171cca0, priority 4; completion 0x57ce60 ->
  0x57c2d0 -> 0x57ca70 -> 0x57c540 (state 3, 0x7f0970 registers header) -> 0x57cba0 requests the header's
  game modes (|0x10000000000). VERIFIED-EMU on dump 416 (`session/map-header-emu-425.py`,
  `.local/runs/map-header-emu-425.txt`; provider vft 0x260bbe0, `session/provider-sets-425.py`).
  No queue/20600/20300 code requests a 0x9F header. 424c explained: a header in list 1 completes into
  0x57c5e0 with no 0x9F-set entry -> NULL at 0x57c54a (emulated). 424/b/d put the type-2 MAP 0x0800..0688
  in the header set (entry stuck at state 1, header/mode sets never ready); their post-welcome exit is
  unexplained. Untested original form: list 2 = [0x0790000000000688] ONLY, no native control.
- **THREE REAL CLIENTS IN ONE SESSION (pair-trio-426; 425 = c2 TLS CA setter timed out under
  load with a 20 s stagger, other two fine):** launcher pair mode now takes 2 or 3 clients
  (container 1119/1129/1139, client n starts n x delay; public main.cpp, Start-PrivatePair.ps1,
  bnet-probe 1139/21139 referral, instance_referral 1139, tests; build + 27/27 CTest).
  Private: udp_pair_reply.py `--clients 3` (base 0x380), run-live-pair-game.ps1 `-Clients 3
  -AccountC Reaper -C2Spawn` (patch_trio-425.py; new local account Reaper#1003), ui-pair-game.ps1
  drives c2. 426 (`-ClientDelay 45`): all three bound (1119/1129/1139), all six proxy creates
  (each client sees the other two Tracers), c0 kills c1, all alive at the bound, 13/13 audit.
  c0 saw c1's proxy float near the ceiling while dead: the feed follows the death camera
  (c1 y up to 3.41). Fixed: proxies freeze at the death position (`dead_pos`) until respawn.
  RAM: 31 GB machine; three clients fit, 12 local clients will not (6v6 needs multi-machine
  networking, which requires granting network capabilities: ask the user first).
- **ORIGINAL MAP PRELOAD WORKS (livemode18-427):** agent trace (`.local/re/map-header-trigger-425.md`):
  20505 list 2 (+0xa8) is the content provider's map-HEADER set; 0x57c700 requests each header
  (priority 4) and the mode list follows. Public `--lobby-map-header 0790...` (header GUIDs only;
  driver `-MapHeader`). 427 = best recipe WITHOUT NativeHeaderControl + list 2 = [0790..0688]:
  no exit, hero select shows the Practice panorama (previously absent), Tracer spawns with full
  HUD/pistols, 13087 datagrams, 7/7 audit. The 424 crashes came from the type-2 map in list 2
  and the header in list 1 (null deref at 0x57c54a, emulated). Best recipe now uses MapHeader
  instead of NativeHeaderControl (backup .bak427). Other maps: send their 0790 headers.
- **Integrated 3-client run (pair-trio-428):** best recipe with the ORIGINAL map preload (no native
  control), 3 clients 45 s apart, mutual fire, dead flag, frozen dead proxies. All three bound
  (1119/1129/1139), 240 proxy + 240 proxy-controller creates, 125 hits, kills c0->c1 and c1->c0,
  2 respawns, all alive at bound, 13/13 audit (`pair-trio-428-kills.png`): the dead proxy now
  stays on the floor with its pistols removed (no ceiling float); the third player is visible
  in c0's view. Dumps deleted. Map catalogue/placeables/spawns agent running (other maps).
- **Teams (pair-team-429, private `--pvp-teams` / driver `-PvpTeams`, patch_teams-429.py):** session i plays
  on team i%2: odd sessions get team-1 filter bits (0x11040001) for controller/hero and comp74 field 2 = 1
  via per-session args; proxies carry their owner's team bits (comp26) and proxy controllers comp74 team;
  same-team hits are ignored. 3 clients bound, kills c0->c1 and c1->c0 (cross-team), 13/13 audit, all alive.
  NOT yet checked visually: whether enemies now render with enemy (red) outlines/health bars
  (`pair-team-429-views.png` crops c0/c1/c2 views). Next: verify team visuals, then other maps from the
  map catalogue agent (`.local/re/map-catalogue-426.md` / `.local/runs/map-catalogue-426.json` if it finished).
- **SECOND MAP: Temple of Anubis (anubis430..432, single client, Skirmish 0x0230000000000010):** map
  catalogue `.local/runs/map-catalogue-426.json` (agent, 132 headers / 25 modes; headers carry name,
  canonical map, modes, pending placeables). Recipe `.local/runs/run-anubis432.ps1`: MapHeader
  079000000000005b, MapCanonical 080000000000005b (new driver params `-MapCanonical`, `-PlaceableIds`;
  responder placeable cap 8 -> 64; single-driver feed id follows the placeable count). Pending keys
  read live from a no-placeable run (431 dump retail-private-anubis431-pending.dmp,
  replication-pending-keys-55.py): 29 zero-dependency keys = the catalogue keys exactly (Practice's
  catalogue keys were 5 low; use live keys). 430b with keys+5 aborted to Training after ~4.5 s of
  commands; 432 with the true keys: original "DEFEND - TEMPLE OF ANUBIS" hero select, Tracer spawns
  in the Anubis spawn room (14.04,0.9,-28.94; spawns.py clusters (14,0.8,-30), (-13,4.3,139),
  (-68,2.5,19)) with HUD/pistols. The Practice close step leaves the hero-select overlay/CHANGE HERO
  visible (Practice-specific controller graphs 13c1/20e4); Skirmish mode graph 0d76 not driven yet.
- **PRACTICE VS AI v0 (ai-practice-433/434):** "Practice vs. AI" is not a mode (catalogue): vs-AI uses
  normal modes with server-side bots. New private `udp_pair_reply.py --ai-bots 'x,y,z;..'`
  (patch_ai-431.py; driver `-AiBots -AiDps -AiAccuracy -AiRange -AiStrafe`, `-Clients 1` now uses
  the launcher's single-client mode): each AI is a virtual session (AiSession, team 1, Tracer +
  controller, entity base 0x3c0+0x10k) only in World.sessions; existing proxy code creates its hero,
  controller and pistols in every client; ai_tick strafes it around its spawn, aims at the nearest live
  enemy player, fires bursts (weapon 10:8 mirrored) and deals dps x accuracy; players kill it through
  the PvP hit test (dead flag, frozen body, 3 s respawn). 433: two AI Tracers render in front of the
  player, aim, strafe, fire; the player's HUD drops and the native death view plays (15 AI kills).
  434 (accuracy 0.15, bot ahead): player kills an AI (86 hits) and it respawns; BUT the player's hero
  had NO HUD/pistols (red no-entry) from the start: damage bumped the hero snapshot sequence before the
  hero's first full frames had created its HUD/weapon subgraphs. Fix (ai-435): AI targeting and PvP
  damage wait for the victim's counts['pick_full'] >= 40, HUD-hp sequence bumps for >= 20.
- **ai-practice-435 (setup gate):** same matchup as 434 with the ai-435 gate: the player's HUD and pistols
  persist the whole match (`ai-practice-435-grid.png`: health 70/12/193/133/98/33/death/158), two enemy
  AI Tracers aim, strafe and fire, 7 AI kills / 6 player respawns, the player kills an AI (63 hits),
  13/13 audit. Practice-vs-AI v0 works on Practice Range. Next: AI on Anubis (spawn clusters above),
  AI navigation (no navmesh: bots strafe around spawn points and do not path), more heroes for AI,
  the Skirmish/vs-AI mode flow (lobby "Practice vs. AI" card: client queue request shape unknown).
- **Interactive session bound 4 h (public):** launcher private UDP/CA/TLS and pair bounds raised 300 s ->
  14400 s at the user's request (cleanup still at the bound or when the client exits); tests updated;
  responder/pair responder/drivers accept up to 14400. Build + 27/27 CTest.
- **AI heroes per bot (439b):** `-AiBots 'x,y,z@DEF:RECORD;..'` + `-AiPreload` (weapon children): Soldier
  (03cf/006e), 0022/0002 and 0141/0005 render as different heroes with their own skins on Anubis; AI
  weapon instance/volley from the hero configs. Anubis floor feed y ~1.75: AI y and the recipe's pick
  spawn must use it (run-anubis438.ps1); the pair driver now counts the recipe's placeables for hero ids.
  Player HUD/pistols missing in 434/436/438 but present in 433/435/437/439b: unresolved, server counters
  identical; not caused by AI timing alone (gate kept).
- **User exploration session (user-explore-440, user clicked through every menu; watcher
  `.local/re/watch-lobby-calls.py <probe.log>` maps entry/delta to message ids):** 24000 Training
  (Tutorial and Practice Range, mode field differs) -> answered (only one instance per session: a second
  entry hangs); **44100/44102 = matchmaking queue join/leave for Quick Play role queue, Competitive and
  Practice vs. AI** (queue type/difficulty inside the 32-byte struct + 3 u32; layout
  protocol/vs-ai-queue-104319.json); 26500 = Shop request; 38201 = settings blobs (x9 at once); 22200 sent
  when leaving Options; 22206 profile -> answered 20807 (Career Profile); 39200/39201 periodic
  stats-like uploads; 21801 leave game; 44100/44102 unanswered (search spins). No request at all for
  Arcade (empty: server push missing), Loot Box (0 boxes), Patch Notes (web content, no Internet),
  Options, Statistics, Achievements, Player Icon browsing, Social (Friends = Battle.net service),
  Highlights, role toggles. New opt-in public `--lobby-vs-ai-schema protocol/vs-ai-queue-104319.json
  --lobby-vs-ai-referral` (needs instance referral; driver `-VsAi`) answers 44100 with the local 20600
  referral (test added). Agent tracing the Arcade push + full queue reply sequence (arcade-queue-440.md).
- **Practice vs. AI end to end (vsai-441):** `-VsAi` + Anubis recipe + 3 AI heroes: the original
  Training -> Practice vs. AI -> EASY sends 44100; the probe answers 23310 + 20600; original loading
  screen "VERSUS AI / EASY / TEMPLE OF ANUBIS", hero select "DEFEND / VERSUS AI EASY" with the full
  roster, Soldier: 76 spawns with HUD/rifle facing AI Hanzo/Soldier/Reaper. Firing is blocked until
  Escape dismisses the pre-match hero-select overlay (no "assemble your team" countdown yet); then the
  player killed the AI Soldier (4.1 m). Captured 44100 (vs AI Easy): first u64 = 0x0630000000000070
  (queue/game-type record), u32s 0xf38640 / 0xf47266. Public probe: lobby loop bound 1024 -> 200000
  packets (long sessions), opt-in `--lobby-capture-message ID` (driver `-CaptureMessages`).
- **Research (user request):** OW1 vs AI: humans vs AI 6v6, Easy/Medium/Hard, bot roster (2018)
  Roadhog, Zarya, Ana, Lucio, Zenyatta, McCree, Reaper, Soldier: 76, Mei (no Tracer/Hanzo); standard
  maps with objectives. Driver `-AiTeam roadhog,zarya,.. -AiSpawns` builds the bots + preloads.
  Other projects: MIT-licensed Boi-027/overwatch-1.74-lobby-server (same build; lobby, queue cards,
  matchmaking, 30-s assemble countdown, loot boxes; no weapons/HUD) cloned read-only to
  Y:\repos\WIP\OW1-research\boi027-ow174 (reuse requires MIT attribution; do not copy its client-
  derived data/). Plasmawatch (beta 0.8), OW1 Emulator Workshop mode (OW2 workshop). Agents running:
  OW1 reference (ow1-reference-2019.md), Assault/Anubis flow (assault-anubis-flow.md), navigation
  (navigation-data.md), MIT lobby map (boi027-lobby-map.md), Arcade/queue (arcade-queue-440.md).
- **boi027/ow174 comparison (agent, read-only, `.local/re/boi027-lobby-map.md`):** MIT project for the same
  build (relay DLL instead of native crypto). Maps their lobby/game-server messages to ours with file:line
  refs. Top adoptable: 20813 leave policy {0,20,0.3,0.2} (likely removes "-75% XP / 0 MATCHES REMAINING";
  matches aq440 leaver trace), 44201 queue-joined + 44202 reason 1 before 20600 (QUEUE 0xB4F8BC62), Arcade
  push 39802 (QP card 0x06300000000000ED at +0x78+0x18; vs-AI cards 0x0630000000000070..72), 24300 account
  record + 24900 +0x80 hero records (gallery 0/0), retail 20505 list 1 = 2457 skin themes (0x0a50; our
  validator refuses them), 55500 features (chat), 27100 friends, 35500 empty data centers, 20704 invite popup.
  Game side: game-mode entity def 0x04000000000016B2 + comp114 mode GUID, countdown var 0x0517 (1303) via
  H=0 full frame ("Assemble your team"), team-list graph 0x288D under 288A state 1, 20304 {0,F} send home,
  CmFD-only owner acks. Caution: they call comp74 field 2 "slot" (ours: team). Do not copy their data/
  files, descriptors.pb, handshake BLOB_KEY or the 36600 template (production endpoints); MIT attribution
  required for any adapted code.
- **Arcade list / queue / leaver indicator (agent 440, offline; `.local/re/arcade-queue-440.md`):**
  - **Arcade list = 39802** (schema 0x00A8654E). Handler 0xba84b0 fills root slot 74; 0xba8ad0
    resolves menu cards through catalogue 0x046000000000010b. VERIFIED-EMU: entries DM 0x0630..3b,
    TDM 0x0630..34 and Elim 0x0630..1e resolve to the DM/TDM/Elimination cards. Entry +0 is the
    0x0630 game type; the +0x18 single entry is Quick Play (REF 0x0630..ED); the +0xD0 list is
    Competitive.
  - **Queue (STATIC + MIT reference boi027-ow174):** 44100 key = {card GUID,0,0,0 | flags |
    platform 0xF38640 | pool 0xF48644}. The server replies 44201 {key echoed verbatim} (queued),
    then 44202 {key, reason 1} (popped), then 20600. 44203-44207 are ignored by the client.
  - **Leaver indicator:** "-75% XP / 0 MATCHES" shows because 20813 was never sent (leave rate 0/0 =
    NaN). Sending 20813 {mask 0, window 20, 0.3, 0.2} hides it (VERIFIED-EMU).
  - **Shop:** 26500 is answered with 26400 (result +0x9C = 0).
  - Descriptors: `.local/runs/arcade-queue-440.json`. Card names: `.local/runs/arcade-cards-440.json`.
- **Retail queue sequence + leaver fix live (vsai-443):** public lobby_service/bnet-probe (values from
  the MIT Boi-027 project, layouts exported from the client via private .local/re/msgdesc-json.py):
  `--lobby-vs-ai-referral` now answers 44100 with 44201 (queue entry echoing the 48-byte key) and
  sends follow-ups 44202 {key, reason 1 popped} + 20600 at once (new InitialLobby.followups());
  `--lobby-leaver-thresholds` sends 20813 {0, 20, 0.3, 0.2} after 20802 (agent emulation: no 20813 ->
  NaN leave rate -> "-75% XP / 0 MATCHES REMAINING"). Live: label gone; Training -> Practice vs. AI ->
  Easy loads Temple of Anubis via 44201/44202/20600; six AI from the OW1 bot roster (`-AiTeam
  roadhog,zarya,mccree,soldier,ana,lucio`) render with weapons and fight. Loading screen no longer
  says "VERSUS AI EASY" (that label came from the still-open queue entry; retail would supply the game
  type via the game server). 28 probe tests, 27/27 CTest. Descriptors: vs-ai-queue (+44201/44202),
  lobby-login (+20813).
- **OW1 reference (agent, .local/re/ow1-reference-2019.md):** build 1.74 = final 2022 client. vs AI:
  6 humans vs 6 AI, Easy/Medium/Hard = 25/50/100% AI damage, AI roster (12): Roadhog, Zarya, Bastion,
  McCree, Mei, Reaper, Soldier: 76, Sombra, Torbjorn, Ana, Lucio, Zenyatta; random Assault/Control/
  Escort/Hybrid map; bots named after heroes. Assemble 30 s, setup 45 s, respawn 10 s, Assault 4:00
  (+3:00 after A). Leaver: last-20-games leave rate, -75% XP. Arcade/queue (agent, arcade-queue-440.md):
  39802 card list (game-type GUIDs 0x0630..., 151 cards in .local/runs/arcade-cards-440.json), 26400
  shop reply. MIT map (boi027-lobby-map.md): 24300/24900 collection, 27100 friends, 35500 group finder,
  55500 features, assemble countdown via game-mode entity 0x04000000000016B2 comp 114 + var 0x0517.
- **AI NAVIGATION DATA EXISTS IN THE CLIENT (offline agent, 2026-10-17; `.local/re/navigation-data.md`):**
  map chunk **0x12** (`0dd00012_<map>`, all 132 maps) has two 'DUTS' reflection documents. Doc 1, root
  `5ae64839`, is an **AI tactical volume set**: AABB tree plus volumes, each with a floor point, s32
  neighbour list and a walkable-voxel mask (1 x 1.4 x 1 m, bit = z + Sz*(x + Sx*y), fitted 116/116 and 60/63).
  Neighbours are symmetric and every pair is voxel-adjacent. Doc 0 (`3bc32a6e`, block-keyed blobs,
  probably the compressed surface/flight graph) is not decoded. Reader `.local/re/nav/navdata.py`;
  builder `.local/re/nav/nav-graph.py` writes `.local/runs/nav-graph-5b.json` (Anubis: 117 nodes, main
  component 85, 113 portal edges; objectives A/B with capture boxes; paths attacker_spawn->A 125 m,
  ->B 206 m, A->B, forward/defender spawns) and `nav-graph-688.json` (Practice: 67 nodes, spawn->landmark
  paths). Node y = floor rounded up to 0.35 m, so feed y is about node y + 0.8. Not used live yet.
- **Assault/Anubis match-flow analysis (agent, offline, `.local/re/assault-anubis-flow.md`):** mode graph
  0f4a runs on a server-created **game-mode entity = definition 04000000000016b2** (only definition with
  serialized STU_F00E5A06 = runtime component 114). Config var A3DEF368 ("game-mode entity", read by 288b
  MATCH TIME = `A3DEF368.v0517`, 0c90, 0d73, 0e8e) resolves natively (0xcdd340 -> 0xd0a0a0, type getter
  0xbcb240 = 0x72) to the first world entity with component 114; emulated on dump 416 it returns 0 -> our
  "MATCH TIME 0.0". Phase var v003b: 0 waiting / 1 assemble (30 s, later 25) / 2 setup (45 s, first point
  only) / 3 round (+240 s A, +180 s B) / 4 round end (11.6 s) / 5 match end (R13 S20 msg 0695 winner).
  Phase messages 0700/0692/0701/0694/0695 drive 1feb (client-run objective HUD), 288b (S32 chain ->
  S35/S36 opens hero select; 0701 -> "SETUP:"), 0c90, 0cbb; client-only S79 sends 071d ATTACK/DEFEND.
  Anubis A idx698/B idx723 (def 1c22, 0e8e+0f4c), doors 0d32, spawn rooms by tag 0x341/0x3cc/0x310;
  anubis431 census: no map entity has comp 47 client-side. Replication plan + new responder options
  (mode entity/graph/states/vars) in the doc; state tables `.local/runs/assault-graph-state-types.json`.

## 2026-10-17 (Claude) - AI navigation live, vs-AI tactics, reply cap, game-mode entity (runs 445-448)

- **AI navigation works live (ainav-445):** six roster AIs walk the client-derived nav graph
  (`-AiNav .local/runs/nav-graph-5b.json -AiGoal capture_point_A`) from the attacker spawn to point A
  (18 waypoints) and fight. Problems seen: all six stopped within 0.4 m of each other, and the damage was
  far above Easy.
- **Tactics patch (`.local/re/patch_aitactics-446.py`, `patch_aispread-447.py`, private responder):**
  `--ai-difficulty easy|medium|hard` = 0.25/0.5/1.0 damage (OW1 vs-AI rule). Per-hero base DPS table
  `AI_BASE_DPS` (approximate published OW1 primary-fire values, public reference, NOT client data) when
  `--ai-dps 0` (new default), x accuracy x range falloff. Each bot gets its own nav cell around the goal
  (`--ai-spread 6`), departures 1.5 s apart (`--ai-stagger`), hold range +0/+3/+6 m, and a lateral slot
  while holding (`--ai-lateral 2`) clamped to walkable voxel columns (`NavGraph.walkable/clamp`).
  Driver: `-AiDifficulty/-AiSpread/-AiStagger`. **aispread-447b verified:** bots spread across the A
  courtyard; player kills Lucio/Roadhog, both respawn and route back (6 player kills, 19 AI kills).
  447 = known TLS CA-setter startup failure (retried as 447b).
- **Reply cap fixed:** run 446 dropped back to the vs-AI menu after ~13 min because
  `udp_welcome_reply.py` stopped at 20000 replies (`reply_bound`). Bound is now `1 << 31` (u32 GCM nonce
  sequence; never wraps/reuses). 447b passed 21810 replies still live.
- **Game-mode entity (modehost-448, `.local/re/patch_modehost-448.py`):** new responder options
  `--mode-host IDX --mode-graphs 0xf4a --mode-delay S --mode-graph-types FILE --mode-timeline JSON`
  (driver `-ModeHost/-ModeGraphs/-ModeDelay/-ModeGraphTypes/-ModeTimeline`): creates the mode graph on the
  game-mode entity, then one full-snapshot frame per timeline phase (base 2+phase; states active earlier
  are sent inactive; vars per scope; per-phase state_data; sub-graph creates). NOT yet emulated/encoded
  with real phase states. Recipe `.local/runs/run-assault448.ps1` = 445 recipe + mode `0230000000000014`
  (Assault) + definition `04000000000016b2` at index 14 (replaces the last unused 14d2; its skin/filter
  entries removed) + preload 16b2 and graphs 0f4a/0cbb/1feb/0c35/1b47/0c8f + `mode-timeline-448.json`
  (one empty phase). Pair-responder definition bound = 15 entries in this recipe.
- **assault-448 result (single client, vs AI Easy, Soldier):** with only the 16b2 entity + 0f4a instance,
  the client's own mode logic runs: hero-select header becomes **ATTACK** (client S79: team == v2a2b,
  default 0) and the top-centre mode HUD appears in hero select and in game (**"0.0 | UNSPECIFIED"**,
  objective name var unset). Cleanup 12/12. **Dump kept:**
  `%LOCALAPPDATA%\OW1-preservation-build\clients\1.74.0.0.104319-original\Overwatch\_retail_\retail-private-assault-448-c0.dmp`
  (client PID 11620; mode entity = definition index 14, entity index = create base + 29 placeables + 14).
- **Next:** on dump 448, find the mode entity's comp47 manager and run
  `.local/claude-scratch/emu/ssfull2.py` (needs an `SS_HERO_CONFIG` wrapper `{"graphs": <assault types>}`)
  for the phase frames in assault-anubis-flow.md section 6 (always-on S52/S58/S12+0cbb/S178; g:2a2b=1,
  2a2c=0, 1ddb name, 0517 clock; phase 1 S43/S7/S10/S8/S9). Settle the ChaseVar/Wait/GME/team/string
  value forms there before any live phase test. Then the timeline: assemble 30 s -> setup 45 s -> round.
