# Overwatch 1 replay, kill cam, POTG, highlights, spectator and client UI flows (for a reimplemented server)

Scope note: notes target the final OW1 client (1.74.0.0.104319) and what a local server must supply. "Fact" bullets are sourced. Bullets under "Inferences" are reasoning, including links to this project's reverse-engineering findings (client mode 7 = replay, highlight/replay viewer graphs, Spectator_Show1PHeroHUD); they are not externally confirmed.

## 1. GDC 2017 "Replay Technology in Overwatch: Kill Cam, Gameplay, and Highlights" (Philip Orwig): content beyond the abstract

### Takeaway
A detailed Chinese write-up of the talk exists (lfzxb.top, mirrored by Tencent GWB/GameRes). It confirms the following. Replay is a special replication receiver on the server. It records 1-per-second full snapshots plus 20 Hz deltas into two ~1 MB/min buffers. The server cuts kill cam "reels" (last snapshot + deltas), compresses them and block-transfers them to the client. The client plays a reel in a second, isolated ECS domain (EntityAdmin) that receives the reel as if it were network data, while the live world keeps running. Consequence for this project: kill cam/POTG/highlights are all server-produced reels of normal state-sync data. A reimplemented server must record and serve them, because the client cannot reconstruct them on its own.

### Cited Findings
- The official session page (abstract only) says the talk covers developing replay alongside the network model, generating and transferring reels within a hard respawn deadline, refactoring the client for an interruptible kill cam, kill cam accuracy problems, and custom scripting for highlights. It also lists replay as a bug-repro tool — [GDC Vault](https://www.gdcvault.com/play/1024053/Replay-Technology-in-Overwatch-Kill); video write-up at [Game Developer](https://www.gamedeveloper.com/design/video-how-blizzard-designed-and-built-i-overwatch-i-s-replay-tech). A GitHub resource list links a YouTube recording — [0xFA11/MultiplayerNetworkingResources #53](https://github.com/0xFA11/MultiplayerNetworkingResources/issues/53). Contemporary tweet confirming the speaker and title — [Carl Chimes on X](https://x.com/carlc27843/status/835241226999758848).
- No official transcript or slide PDF was found. The most detailed text is a Chinese reconstruction of the talk: [lfzxb.top "《守望先锋》回放技术-阵亡镜头、全场最佳和亮眼表现"](https://www.lfzxb.top/ow-gdc-replay/). It is also published at [Tencent GWB](https://gwb.tencent.com/community/detail/115186) and [GameRes](https://www.gameres.com/768220.html), with an index at [lfzxb.top table of contents](https://www.lfzxb.top/ow-gdc-share-table-of-contents/). All points below come from the lfzxb write-up, a third-party transcription/translation; treat exact numbers as "as reported".
- **Goals:** One central system serves kill cam, POTG and Highlights, and also produces replay files for internal debugging. The kill cam shows the seconds before death, usually from the killer's view. The victim's ragdoll is visible, the camera faces the killer, and the killer is outlined through walls — [lfzxb](https://www.lfzxb.top/ow-gdc-replay/).
- **Network models compared:**
  - Deterministic lockstep was rejected. It is fragile with floating point, stalls scale with players (2% per-player stall chance over 5 min gives ~8% for 4 players and ~22% for 12), and joins need a re-simulation from the start.
  - Snapshot interpolation was rejected because of bandwidth.
  - Chosen: **state synchronization**, per-client customized packets of atomic per-object state, prioritized by relevance and measured bandwidth — [lfzxb](https://www.lfzxb.top/ow-gdc-replay/). Tencent's translation also calls OW's model state sync, an improved form of snapshot interpolation — [Tencent GWB](https://gwb.tencent.com/community/detail/115186).
- **Replication architecture (ECS):**
  - Serializing systems are "participants", recipients (clients/spectators) are "receivers", and networked entities are "subjects".
  - Each frame's changed entities go into a frame dirty set, which is merged into each receiver's dirty set. Serialized items are removed from it.
  - The server keeps client-acknowledged state history for delta encoding over custom UDP. Lost packets are re-merged into the dirty set; if the object has changed again, only the newest state is sent.
  - **Late join:** the receiver's dirty set is initialized to the "lifetime dirty set" (every object ever dirtied) — [lfzxb](https://www.lfzxb.top/ow-gdc-replay/).
- **Recording:**
  - Replay uses two special receivers: a "replay snapshot receiver" and a "replay delta receiver".
  - Snapshots mark everything dirty and are taken **once per second**. They can be hundreds to thousands of KB, with no MTU limit.
  - The server simulates at 62.5 Hz (16 ms), but deltas are recorded at **20 Hz**, because full rate would roughly triple memory/bandwidth.
  - There are two contiguous buffers (snapshots, deltas), each with per-frame offset/size, at **~1 MB per minute** each — [lfzxb](https://www.lfzxb.top/ow-gdc-replay/).
- **Reel generation and transfer:**
  - A reel is the last snapshot before the reel start plus the deltas up to the end time. Building it takes two memory copies, then the reel is compressed and metadata is added.
  - The reel is split into MTU-sized fragments and sent by a **BlockTransferSystem** only when bandwidth allows.
  - Replay and network share serialization code. For replay, bandwidth thresholds are set high enough that they are never reached.
  - Replay participants use before/after callbacks instead of ACK/NACK: deltas are ACKed immediately and snapshots NACKed immediately.
  - The team moved from a component-based sync API to entity-based participants, because components starved each other and one entity could be split over several packets — [lfzxb](https://www.lfzxb.top/ow-gdc-replay/).
- **Timing:**
  - The reel must arrive between death and respawn. The respawn time varies with map, mode, overtime and designer settings.
  - The reel starts slightly before death and continues a few seconds after, so the ragdoll is visible.
  - The effective transfer window is **~0.5 s**, which drove general bandwidth reduction.
  - An alternative was considered but not adopted as primary: send pre-death data immediately, then stream deltas. It has worse compression and playback must buffer — [lfzxb](https://www.lfzxb.top/ow-gdc-replay/).
- **Interruptible kill cam = second client world:**
  - The live world must keep receiving data during the cam, because live scripts drive UI, effects and events.
  - Replay therefore runs in a separate ECS domain (EntityAdmin). Live data goes to the live domain and the reel to the replay domain, and both process concurrently. A black fade marks the switch, and a respawn interrupts playback.
  - The refactor removed globals/statics and scoped parameters per domain, taking a few weeks. Four domains were considered; the costs are CPU and scripted transition coordination — [lfzxb](https://www.lfzxb.top/ow-gdc-replay/). Chinese architecture notes describe the same two parallel ECS worlds — [lfzxb architecture/netcode](https://www.lfzxb.top/ow-gdc-gameplay-architecture-and-netcode/); [CSDN GDC2017 notes](https://blog.csdn.net/u014581509/article/details/102579926).
- **Accuracy fixes and special cases:**
  - Turret kills credit the builder even when away or dead. In beta, a dead Torbjörn's turret won POTG, fixed by not awarding POTG to dead heroes.
  - Turret kill cams use a scripted camera attached to the turret's animation bone, chosen from a ring of points so the victim stays in frame.
  - Falls: the camera detaches and follows the ragdoll (Vostokaya ice river). Environmental pushes switch to the pusher's view.
  - Hanzo Dragonstrike uses a third-person camera following the dragon.
  - **Interpolation hints:** per-player interpolation delays are recorded so the replayed crosshair lines up with the shot, since the server acts on attackers' past states.
  - **Fast-forward** to the reel start compensates for the 1 s snapshot granularity.
  - **Server stepping:** expected vs actual durations are recorded for when the server falls 1–2 frames behind.
  - **Message filtering:** game messages are annotated for inclusion in replay/spectator streams, and playback filters out messages not relevant to the current subject. Without this, hit indicators, hit confirms, UI and voice lines were missing — [lfzxb](https://www.lfzxb.top/ow-gdc-replay/).
- **Future work as of 2017:**
  - The 20 Hz delta rate limits aim precision. Player movement is ~half of total bandwidth.
  - Replay files had a single snapshot at the start (forward-only playback). The plan was a snapshot every ~10 s for skipping and scrubbing.
  - Spectating could use a proxy/relay receiving snapshots and deltas, like Source TV.
  - Player-facing replays: one week of replays is about **200 TB** even compressed, and compression is CPU-bound.
  - **Patch compatibility:** serialization depends on asset definitions, and ~22 patches shipped May–Dec 2016. Old replays would need the previous patch's assets from a CDN — [lfzxb](https://www.lfzxb.top/ow-gdc-replay/).
- **Q&A:**
  - Destructibles moved from entities to one bitmap (~200 B full sync, 8 bits per changed range).
  - Replays use **default crosshairs**, because the replay domain lacks the local player's settings.
  - Cosmetic physics (ragdolls, Zenyatta orbs, hair) is client-only — [lfzxb](https://www.lfzxb.top/ow-gdc-replay/).

### Inferences
- The project's observed "client mode 7 = replay", the highlight/replay viewer graph and HUD_Root display are consistent with the second-domain design: a replay/kill cam domain is a separate client world fed buffered server state. The project's "WAITING/ABANDONING/WORLD LOADING..." world-state manager with **two** world managers (startup + submitted) may be the live/replay domain pair. This is unverified.
- The talk's "message filtering for replay/spectator streams" suggests that statescript game messages and UI events carry replay/spectator inclusion flags. Spectator HUD settings (Spectator_Show1PHeroHUD) likely gate first-person HUD presenters inside a replay/spectator domain.
- Because replay data = recorded server→client replication, a reimplemented server could record the same module-4/module-1/module-3 records it already sends. A kill cam could replay those records (snapshot = full creates + full statescript snapshots, then deltas) into the second world, provided the client-side trigger message for kill cam reels is identified. 2017 replay files having one starting snapshot matches "full create + deltas".
- The 2020 player-facing Replay Viewer's forward-only skip/scrub behavior and the patch-reset rule match the 2017 "future work" (periodic snapshots, asset-version dependency).

### Gaps
- No official transcript, slides (media.gdcvault.com PDF) or English notes were found. The free GDC Vault video was not retrievable here; the YouTube recording linked in the GitHub issue was not fetched.
- Kill cam reel wire format (message IDs, compression codec, metadata layout) is not public.
- POTG scoring weights were not described in the write-up beyond the turret and dead-hero rule.

## 2. Play of the Game, Highlights, Replays (2020) and kill cam behaviour

### Takeaway
- **POTG:** one end-of-match highlight, chosen by server-side scoring across four categories (High Score, Sharpshooter, Lifesaver, Shutdown), patented by Blizzard. Weights are not public.
- **Highlights:** "Today's Top 5" are auto-generated, held for 24 h or until a patch. Manual "Request Highlight" captures 12 s, up to 36 stored. Clips are exportable to video via `[MovieExport.1]`.
- **Replays (2019 PTR / 2020 live):** the last 10 matches, kept for the duration of a patch, with shareable 6-character codes valid until the next patch.

### Cited Findings
- **POTG categories:** High Score, Shutdown, Sharpshooter and Lifesaver are the POTG sub-titles; the highest score in any category wins — [Fandom summary via search](https://overwatch.fandom.com/wiki/Play_of_the_Game) (page itself returned HTTP 402).
  - Lifesaver = saving a teammate from imminent death.
  - Sharpshooter = difficult kills, weighing shooter movement speed, distance, headshot and whether the victim was airborne.
  - Shutdown = killing an enemy just as they were about to do something impactful (the game predicts how impactful, e.g. a Lúcio Sound Barrier) — [over.gg reproduction of March 22, 2016 beta patch notes](https://www.over.gg/179/overwatch-beta-patch-for-march-22-2016); [Dot Esports](https://dotesports.com/overwatch/news/how-does-overwatch-decide-play-of-the-game) (403 on fetch; snippet only).
- **Timeline:** the categories were introduced in the **March 22, 2016 beta patch** as a major POTG rework — [over.gg](https://www.over.gg/179/overwatch-beta-patch-for-march-22-2016). A "POTG 2.0" was reported in Nov 2016 — [iTechPost](https://www.itechpost.com/articles/51269/20161108/overwatch-update-play-game-2-0-feature-coming.htm). The Nov 15, 2016 live patch notes contain no POTG change, only highlight-intro fixes — [Blizzard patch notes Nov 2016](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2016/11/).
- **Patent:** Blizzard filed a POTG patent in December 2016 covering the algorithm that scrapes the end-of-game event log — [TheGamer](https://www.thegamer.com/blizzard-overwatch-patent-play-of-the-game/); [TechTimes](https://www.techtimes.com/articles/231273/20180627/blizzard-wants-to-patent-the-overwatch-play-of-the-game-feature-smart-move.htm); [TweakTown](https://www.tweaktown.com/news/62355/blizzard-acquires-patent-overwatch-play-game/index.html).
- **Server-side rules:** dead heroes don't get POTG (fix for a turret POTG while Torbjörn was dead). POTG and Highlights exist so every player can receive shareable clips ("亮眼表现" = Highlights) — [lfzxb](https://www.lfzxb.top/ow-gdc-replay/); [Tencent GWB](https://gwb.tencent.com/community/detail/115186).
- **Highlight intros:** highlight intros are per-hero cosmetics, e.g. Genji "Pumpkin Carving", Mercy "Guardian Angel" and Zarya "Deadlift" fixes in the Nov 2016 notes — [Blizzard Nov 2016](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2016/11/).
- **Highlights, June 2017 overhaul:**
  - Before: auto clips from the last five matches, lost on logout.
  - After: "Today's Top 5" auto-highlights kept 24 h or until the client is patched; manual capture of 12 s via the "Request Highlight" keybind (Options) into "Recently Captured", up to 36 stored; export to video, PC up to 4K60 (Win 8+) — [PC Gamer](https://www.pcgamer.com/au/you-can-now-save-your-overwatch-highlights); [TheSixthAxis](https://www.thesixthaxis.com/2017/06/23/blizzard-testing-overwatch-update-with-better-highlights-fewer-loot-box-duplicates/); [TechRaptor](https://techraptor.net/content/overwatch-is-improving-its-highlights-loot-box-systems).
- **Export settings:** highlight video export path is `Settings_v0.ini` `[MovieExport.1] VideoPath` — [Blizzard Support 118885](https://support.blizzard.com/en/article/118885).
- **Replays, PTR announcement (2019):**
  - Location: Player Profile → Replays tab. Content: your **10 most recent matches**, all modes except Tutorial and Practice Range. Retention: "available for the duration of a patch", reset at each new patch like Highlights.
  - Camera: first-person, third-person, bird's-eye, with or without UI, plus a free camera.
  - Keys: N show/hide controls; WASD planar camera move; Q/E up/down; Space toggles 1st/3rd person; mouse buttons detach to free cam; **F1–F12 spectate players**; 0 snaps to objective; Ctrl+1..9 save bookmarks, 1–9 restore; scroll wheel changes speed; Ctrl+P play/pause; Ctrl+L map overlay (the page also says Ctrl+I).
  - Bindings live under Esc → Options → Controls → **Spectate** — [Blizzard "Introducing Overwatch Replays"](https://overwatch.blizzard.com/en-us/news/23000187); [Gamereactor](https://www.gamereactor.eu/replays-arrive-in-the-overwatch-test-servers/); [PCGamesN](https://www.pcgamesn.com/overwatch/replays).
  - A May 2019 BlizzardWatch article notes even small patches clear replays — [BlizzardWatch](https://blizzardwatch.com/2019/05/24/overwatch-replays-will-let-rewatch-whole-matches-improve-game/).
- **Share Replays (PTR Feb 26, 2020; live Mar 12, 2020):**
  - A replay is shared via an alphanumeric code, typically 6 characters, "valid until the next patch".
  - Pin up to 10 replays to keep them until the next patch.
  - The 10 most recently imported codes are tracked; each entry has a note field.
  - Fixed: replays not recording in immediately-started Custom Games — [PTR Feb 26, 2020](https://eu.forums.blizzard.com/en/overwatch/t/overwatch-ptr-patch-notes-%E2%80%93-february-26-2020/21874); [Retail Mar 12, 2020](https://us.forums.blizzard.com/en/overwatch/t/overwatch-retail-patch-notes-%E2%80%93-march-12-2020/469664).
- **Replay Viewer options (PTR Nov 19, 2020):** a "Custom Spectator Options" menu in the Media Controls. Exact option names:
  - Team 1 Banner, Team 1 Heroes, Team 2 Banner, Team 2 Heroes, Status Messages, Playback Indicators, Game Mode Specific HUD, Kill Feed, Player Names, Player Health Bars, Player Outline Strength.
  - First-Person Health, First-Person Ultimate Meter, First-Person Ability and Weapon Info, First-Person Crosshair, First-Person Hero HUD, First-Person Activity Feed.
  - Objective Capture Sounds, Time Skip Interval Length, FOV Change Per Zoom, FOV Interpolation Rate, Maximum Free Camera FOV.
  - New 0.75x and 1.75x speeds — [PTR Nov 19, 2020](https://eu.forums.blizzard.com/en/overwatch/t/overwatch-ptr-patch-notes-%E2%80%93-november-19-2020/24881).
  - The Jan 14, 2021 PTR adds finer playback speed steps (0.10x–1.00x) — [PTR Jan 14, 2021](https://eu.forums.blizzard.com/en/overwatch/t/overwatch-ptr-patch-notes-%E2%80%93-january-14-2021/25255).
- **Kill cam:**
  - Shows the seconds before death from the killer's perspective, with the killer outlined. It ends on respawn and is streamed as a server reel just before death plus a few seconds after.
  - Special cameras exist for turrets, falls, environmental kills and Dragonstrike — [lfzxb](https://www.lfzxb.top/ow-gdc-replay/).
  - Player discussion of skipping/disabling: [GameFAQs](https://gamefaqs.gamespot.com/boards/182930-overwatch/75259592), [Blizzard forums](https://us.forums.blizzard.com/en/overwatch/t/death-cam-replay/270302).

### Inferences
- "First-Person Hero HUD" is very likely the user-facing label of the internal `Spectator_Show1PHeroHUD` setting found in the client, and "Game Mode Specific HUD" of `Spectator_ShowGameModeHud`. The other First-Person/Team options probably have sibling `Spectator_*` setting names. This implies the hero HUD presenter path consults spectator settings when the viewing context is a spectator/replay domain. For a live player domain, a "1P hero HUD visible" decision may depend on whether the client considers itself the controlled-player context rather than a spectator.
- Replay Viewer replays (10 games, patch-scoped, codes) imply server-side storage of whole-match reels (the 2017 single-snapshot + deltas format). Clients download them by match/code. A preservation server could store recorded server→client streams per match and serve them through the lobby/BNet request that the Player Profile → Replays tab issues. That request is not yet identified.
- Highlights "Today's Top 5" are server-selected reels delivered to the client (lost on logout pre-2017; 24 h/until-patch post-2017), so they are also server-held. "Request Highlight" captures 12 s that the client must request from server buffers. This is consistent with the talk's reel model.

### Gaps
- Exact POTG scoring weights and the "POTG 2.0" (late 2016/2017) changes could not be verified; the Fandom/wiki.gg pages were blocked (402/401) and Dot Esports returned 403.
- Whether highlight/POTG reels are cached locally on disk (and where) was not found.
- The protocol messages for kill cam reel delivery, highlight lists and replay downloads are not documented publicly.

## 3. Spectator/observer mode, observer tools and OWL broadcast tooling

### Takeaway
Custom Games have spectator/observer slots: 6, raised to 12 in Nov 2016. Spectating offers free cam, first- and third-person follow, and later static cameras (2018). The Replay Viewer reuses the same spectator controls ("Spectate" keybind category) and options menu.

### Cited Findings
- **Nov 15, 2016:** Custom Games observer slots increased from **6 to 12**; incorrect health bar colors when spectating Custom Games were fixed — [Blizzard patch notes Nov 2016](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2016/11/).
- **Sept 2017 console update:** adjusted the spectator camera — [mp1st](https://mp1st.com/news/overwatch-console-update-patch-notes-for-ps4-xbox-one) (via search snippet).
- **Sept 2018 PTR:** static camera support in spectator mode, editable team names and pausing in Custom Games — [Icy Veins thread](https://www.icy-veins.com/forums/topic/23538-overwatch-ptr-patch-september-22/) (snippet).
- **Oct 23, 2018 developer update:** a replay/live-spectating test at the Overwatch World Cup, with free cam and first/third-person follow — [TechRaptor](https://techraptor.net/gaming/news/overwatch-developer-update-details-replay-system-new-ptr-patch-out) (snippet; page 403).
- **2020:** third-person observing ultimate sound fix; Workshop "Spectators" renamed "Non-Team Spectators" in Create HUD/In-World Text — [Retail Mar 12, 2020](https://us.forums.blizzard.com/en/overwatch/t/overwatch-retail-patch-notes-%E2%80%93-march-12-2020/469664).
- **Spectate keybinds** (F1–F12 players, 0 objective, bookmarks, free cam) are configured under Options → Controls → Spectate — [Blizzard Replays article](https://overwatch.blizzard.com/en-us/news/23000187).
- **2017 future work:** proposed spectating through a relay/proxy fed by the same snapshots and deltas (Source TV-like) — [lfzxb](https://www.lfzxb.top/ow-gdc-replay/).

### Inferences
- In-game spectators, the Replay Viewer and OWL broadcast observers likely share one client "spectator" controller and HUD layer, with the Nov 2020 options as `Spectator_*` settings. For this project, the existence of `Spectator_Show1PHeroHUD` means the 1P hero HUD has a spectator-gated presentation path separate from the local-player path.
- A spectator receiver on the server is "another receiver" in the replication model (late join = lifetime dirty set). A reimplemented server could support observers by sending the same full-create stream without controller selection (20302).

### Gaps
- No primary source found on the OWL broadcast observer toolset (internal tools, observer HUD), on the exact spectator slot count in final OW1 (12 after 2016 is the last found), or on "Spectator Show" setting names outside this client.

## 4. Client UI flows (menus, match flow, options)

### Takeaway
Little reliable primary documentation was gathered here in the available budget. Facts found:
- Replays live under the Player/Career Profile.
- Highlights are a menu with Today's Top 5 and Recently Captured.
- Options → Controls has a Spectate category and the "Request Highlight" bind.
- Deleting `Settings_v0.ini` resets only video/audio, implying controls/gameplay/social settings are stored server-side (BNet/cloud).

### Cited Findings
- Replays tab in Player Profile — [Blizzard](https://overwatch.blizzard.com/en-us/news/23000187); "Career Profile" wording — [PCInvasion via search](https://pcinvasion.com/?p=192344).
- Highlights UI: Today's Top 5 and Recently Captured (36 max); "Request Highlight" keybind in Options — [PC Gamer](https://www.pcgamer.com/au/you-can-now-save-your-overwatch-highlights).
- Training/Practice Range and Tutorial are excluded from replays — [Blizzard](https://overwatch.blizzard.com/en-us/news/23000187).
- Hero Select screen portraits blur fix (2020) — [Retail Mar 12, 2020](https://us.forums.blizzard.com/en/overwatch/t/overwatch-retail-patch-notes-%E2%80%93-march-12-2020/469664).

### Inferences
- The project's observed flow (No Thanks → Training → Practice Range; SELECT A HERO with CONTINUE; "You must be in a spawn room to change heroes"; Esc menu with Social/Career/Options/LEAVE GAME/Exit) matches the retail menu structure. These items come from the project's own native observation, not external sources.
- From general knowledge, unverified here: the end-of-match sequence was POTG → team/player highlight cards (with voting until endorsements replaced voting in 2018) → endorsements → summary/XP. A server must at least drive POTG reel delivery and match-end state for this.

### Gaps
- Not researched within budget, so needing sourcing: hero-select timers; end-of-match card/endorsement screens; the full Options tree (Video, Sound, Controls per hero, Gameplay, Accessibility, reticle customization); which exact settings are cloud-stored.

## 5. Settings_v0.ini format and cloud-synced settings

### Takeaway
`Documents\Overwatch\Settings\Settings_v0.ini` is an INI with versioned section names (`[Section.N]`) and quoted values. It holds local hardware-dependent settings (render, sound, movie export). Controls (including per-hero settings), gameplay and social settings are not reset by deleting it, so they are evidently account/cloud-stored on Battle.net servers.

### Cited Findings
- Location: `\Documents\Overwatch\Settings\Settings_v0.ini` — [Blizzard Support 118885](https://support.blizzard.com/en/article/118885).
- Format: `[Section.N]` headers with `Key = "value"` lines, e.g. `[Sound.3] MasterVolume = "42.000000"` — [Blizzard EU forums](https://eu.forums.blizzard.com/en/overwatch/t/i-cant-change-any-options/19617) (via search snippet).
- Keys seen:
  - `[MovieExport.1] VideoPath` — [Blizzard Support](https://support.blizzard.com/en/article/118885); `Type` ("1" = WebM) and `UseHardware` — [Lutris installer](https://lutris.net/games/install/10154/view).
  - `[Render.13] WindowMode` — [Lutris](https://lutris.net/games/install/10154/view). `GFXPresetLevel`, `FullScreenWidth`/`FullScreenHeight` — [Blizzard forums](https://eu.forums.blizzard.com/en/overwatch/t/video-settings-not-updating/27517); [Resolution issues](https://eu.forums.blizzard.com/en/overwatch/t/resolution-issues/655).
  - `[Sound.3] PreferXAudio2` — Blizzard forums (search snippet).
  - Some of these posts may concern OW2, which kept the same file.
- Deleting the file resets video and audio, but **not** control, gameplay or social settings — [Blizzard EU forums thread](https://eu.forums.blizzard.com/en/overwatch/t/crashes-performance-issues-read-this/22/10) (via search snippet).

### Inferences
- Per-hero control settings and gameplay/social options arrive from the server. In this project that is likely the lobby initial-data account preferences (20802 "default account preferences", required for the main menu) and possibly 20801.
- A preservation server should persist the client's preference updates per account and return them at login. Otherwise, Options changes (including reticle and per-hero binds) are lost or defaulted.
- Spectator options (`Spectator_*`) and the client "special client" flags may be among the cloud-stored settings.

### Gaps
- No complete key list or section-version table for `Settings_v0.ini` was found, nor a public description of the cloud settings blob format or which message carries it.
