# Public Overwatch 1 emulator, private-server and revival efforts (survey as of 2026-10-15)

Scope note: public sources only. "Claim" means a project's own statement. "Code evidence" means it was read in public source. Nothing here was run. The sources were read on 2026-10-15. Two kinds of material were left out on purpose. Some upstream repos publish client-embedded keys, certificates or passwords, for example Boi-027's PROJECT_STATE BLOB_KEY, the Plasmawatch `.key`/`.pfx` and its install password, and Boi's `resource_keys_174.json`. This note says those files exist and does not copy them.

How the decimal and hex variable IDs line up: Boi/squeeeezy's 1.74 server writes statescript variable IDs in decimal, and this project writes them in hex. They are the same numbers: 2438 = 0x0986, 31435 = 0x7ACB, 25377 = 0x6321, 8535 = 0x2157, 8419 = 0x20E3, 1303 = 0x0517.

## Q1. Prometheus (saturn-xvi/prometheus): what it did, and which vars and components its spawner set

### Takeaway
Prometheus is a DLL that runs inside the client, against the Overwatch 0.8 beta (build 24919). It is not a server. It reaches the game by writing the client's own entities and statescript variable bags directly. That covers its "hero select", weapons and health. Its own README admits that the parts a server owns are still missing: hero-select flags, weapons that shoot, the tab list, abilities and voice. The spawner's exact recipe can be read in the code. It is the closest public "what a server must set" checklist for a player.

### Cited Findings
- **What the repo is.** "Research and Reverse-Engineering project of Overwatch!" It had about 601 stars, 73 forks and 18 commits on main. The license changed from MIT to AGPL. The target is the beta 0.8.0.24919 build from archive.org. — [GitHub saturn-xvi/prometheus](https://github.com/saturn-xvi/prometheus)
- **Where it was presented.** It was presented as a 37-minute talk at 39C3 (Dec 28/29 2025), "Prometheus: Reverse-Engineering Overwatch". The talk calls the engine "Tank", reusing parts of the cancelled Titan, and describes an ECS plus a "deterministic, graph-based scripting engine". The stated goal is "hosting your own servers and modifying the client". — [media.ccc.de](https://media.ccc.de/v/39c3-prometheus-reverse-engineering-overwatch); [39C3 Fahrplan](https://events.ccc.de/congress/2025/hub/en/event/detail/prometheus-reverse-engineering-overwatch)
- **Branches.** `main` was last updated Jan 18 2026. `artpop2` (May 15 2026) is the active branch: a launcher, dataflow, the mirrorsystem, teScene, MinGW/Nix builds. `stu-editor-ui` dates from Jan 13 2026. — [branches](https://github.com/saturn-xvi/prometheus/branches/all); [artpop2 commits](https://github.com/saturn-xvi/prometheus/commits/artpop2)
- **artpop2 README status.** "load a map, spawn a hero, and look around". There is no multiplayer, and "A lot of hero abilities don't work, including shooting (some) weapons". Documentation moved to owdev.wiki. — [artpop2 tree](https://github.com/saturn-xvi/prometheus/tree/artpop2)
- **README "Broken stuff" list (upstream main).** These are quotes:
  - "Press H to select Hero ... always displayed ... controlled by the server by setting a boolean flag in component" (the sentence is truncated in the original).
  - "Weapons don't shoot: ... Probably a system which needs to be explored first or a statescript var that needs to be set."
  - "Main Menu buttons only send JAM messages to the server".
  - "Some abilities ... depend on the server sending you stuff and acknowledging".
  - "Tutorial does not give you hero selection screen: ... server spawns Tracer for you automatically".
  - "Doors, Capture Points and Payloads get placed at (0,0,0) ... 'load filter' which I bypass (selectiveResLoad_hook)".
  - "Lobby does not show a hero right to the buttons: ... some info is sent via JAM".
  - "No weapons visible: Setting the position and modifying Statescript shortly after spawning sometimes does not work".
  - "DVa is floating around ... Probably because the Mecha isnt spawned".
  - "VoiceLines are handled by the server".
  - "Player tablist doesnt work: Can be force-enabled in a Statescript script."

  — README section 3 in [saturn-xvi/prometheus](https://github.com/saturn-xvi/prometheus). The same text is retained in /home/user/ow1-preservation/README.md, lines 189-208.
- **README internals.**
  - The Game Entity Admin holds "an uint that says 'this is the local entity'. This must reference the controller entity. Systems use Components 2F (local player component) and 20 (model reference component)".
  - The MirrorSystem pre/post component-deserialization callbacks run "When a server sends a component update".
  - "The controller entity has no Statescript Instance. Only the model has one which controls abilities".
  - Component 1 (SceneRendering) is needed for an entity to be shown.
  - "you cannot force-set the position in Component 1"; the MovementStateSystem (components 12/15/16) holds server deltas.

  These component IDs are 0.8 IDs. — [README](https://github.com/saturn-xvi/prometheus)
- **The spawner recipe** (`player_spawner.cpp`, upstream main; code evidence). It uses two entities:
  - **Controller entity:** definition `0x040000000000000E`, with components 2F, 33 and 3F loaded.
  - **Model entity:** Tracer `0x0400000000000001`.

  `modify_ent` then does the following:
  - (a) Sets `GameEntityAdmin.local_entid` to the controller.
  - (b) Sets Component 0x20 ModelReference `aim_entid` (+0x90), `cam_attach_entid` (+0x94) and `movement_attach_entid` (+0x98) to the model.
  - (c) Sets Component 0x1F Backref `backref_entid`/`backref_global_entid` on the model to the controller.
  - (d) Component 0x28 health part[0]: enabled 1, curr 169, max 200, plus two flag bytes.
  - (e) Component 0x2F LocalPlayer: calls a movement-system function (0.8 RVA 0xc27560 on system 36) to make the player movable.
  - (f) **Component 0x3F PlayerInfo**: `hero_select_enabled=1`, `hero_was_selected=1`, `m_slot=3`, `selected_heroid=hero`, `localplayer_heroselected=1`. All of these are MirrorData at +0x98..+0xC3.
  - (g) **Component 0x10 FilterBits**: optional `set_filterbits_spectator()` (field_8C=0x101, field_8E=1, pre_filter_bits=0x400001), `set_team(t)` (clears 0x3C0000 and sets 0x40000<<t), then `filter_bits = 0x800000` and a native `FilterBitsMakeFinal`.
  - (h) Component 0x23 Statescript on the model: loads the hero definition's STUWeaponComponent `m_managerScript`, plus each `m_weapons[].m_script`.
  - (i) Entity var `0x0D800000000000FD` = BYTE 1, and entity array `0x0D8000000000001D` = INT [1]. The code comments that a single entry means "SECONDARY WEAPONS DONT WORK".

  — [player_spawner.cpp](https://github.com/saturn-xvi/prometheus/blob/main/prometheus/player_spawner.cpp); struct offsets in [entity_admin.h](https://github.com/saturn-xvi/prometheus/blob/main/prometheus/entity_admin.h)
- **Per-tick health/HUD variables (code evidence, `PrometheusSystem::OnTick`, main and artpop2).** Every tick, on the local model's statescript entity var bag, it writes:
  - `0x0D800000000006C4` = current health (float, from STUHealthComponent `GetFullCurrentHealth`).
  - `0x0D800000000006C9` = max health (float).
  - artpop2 also writes `0x0D8000000000094C` = BYTE 1. The comment reads: "When this is 1 the statescript component does not add the 'spectator' graph. Assuming 1 == alive?"

  — [artpop2 entity_admin.cpp (raw)](https://raw.githubusercontent.com/saturn-xvi/prometheus/artpop2/Prometheus-Core/entity_admin.cpp)
- **Maintainer on health (issue #4, "HP is always 169").** 169 "is just a placeholder since health is controlled by the server". Statescript health nodes exist, but "server-side node implementations are missing". To find them, look for nodes with `m_serverOnly` or with no implementation class. Health lives in two places, the health component and the statescript component, and the client forces the statescript vars to match STUHealthComponent. — [issue #4](https://github.com/saturn-xvi/prometheus/issues/4)
- **artpop2 weapon fix (code evidence; from PR #22 by Hazno-dev, merged into artpop2 Jan 13 2026).**
  - Scripts are loaded with exec flag 0x8 through `load_statescript_script_bit3` (Statescript vtable +0x60, versus +0x58 for normal loading). Bit 0x2000 is passed as a "bit13" bool, and the owning entity id is passed too.
  - Entity array `0x1D` (the "valid weapon idx dict") is seeded with 0, then extended to [1..n].
  - Each weapon graph instance gets **instance var `0x0D8000000000001C` = its weapon target ID (1..n)**.
  - The model's filter bits get `|= 0x100`.
  - The PR text says this "fixed weapon swapping", "corrected the player valid weapon ID dictionary and the target ID script instance variables". It also added a variable that disables the generic, conditionalized "spectator graph".

  — [artpop2 player_spawner.cpp (raw)](https://raw.githubusercontent.com/saturn-xvi/prometheus/artpop2/Prometheus-Core/player_spawner.cpp); [artpop2 Statescript.h (raw)](https://raw.githubusercontent.com/saturn-xvi/prometheus/artpop2/Prometheus-Core/Statescript.h); [PR #22](https://github.com/saturn-xvi/prometheus/pull/22)
- **Demo hooks (artpop2).** Hooks on the 0.8 `play_game_btn` (0xc87220) and `SendHeroSelection` (0xd774b0). A `heroSelectActive` config-var getter (0xd8ee00) gates the hero "hello" voice line, which Prometheus plays itself through VoiceSystem::PlayVoice. — [artpop2 entity_admin.cpp](https://raw.githubusercontent.com/saturn-xvi/prometheus/artpop2/Prometheus-Core/entity_admin.cpp)
- **Multiplayer in Prometheus.** The "Awful Demo Server" (`state_replicator`/`serialization`) is a BSON-over-WebSocket peer relay: AssignPlayerID, JoinInstance, ChangeHero and PositionUpdate. It is not Blizzard's protocol. — README "Tips & Tricks" and [state_replicator.cpp](https://github.com/saturn-xvi/prometheus/blob/main/prometheus/state_replicator.cpp). Boi-027's analysis agrees: "Prometheus does NOT implement a server ... The gameplay shown in the talk comes from state_replicator, peer-to-peer entity replication between two patched clients." — [PROJECT_STATE.txt §7](https://github.com/Boi-027/Overwatch-1-v1.74-Lobby-Research)
- **Open PR #39 (Sidiusz, Jul 24 2026), "Set real per-hero health for offline play".**
  - Offline, "every hero spawns at 0 HP", because 0.8 stat descriptors stream from the retired NGDP CDN.
  - The PR seeds normal/armour/shield pools only when they are empty, so a real server still wins.
  - D.Va is excluded and the fallback is 200.

  — [PR #39](https://github.com/saturn-xvi/prometheus/pull/39)
- **Issue #35 (Feb 24 2026), Drahsid.** Built a private 0.8 game server with "match entry, hero spawning, basic damage, and movement". Abilities "seem to run on the client but wait on something from the server". Got "Tracer's recall working by hacking around the intended logic". The maintainer pointed to a new wiki and Discord. That server is not public; a follow-up request in Jul 2026 got no answer. — [issue #35](https://github.com/saturn-xvi/prometheus/issues/35)
- **Issue #18, bots.** The maintainer: bot logic is not in the client, and Practice vs. AI depends on Blizzard servers. — [issue #18](https://github.com/saturn-xvi/prometheus/issues/18)
- **owdev.wiki (the Prometheus wiki).**
  - Full 0.8 named-component table (component ID to STU name), for example: 4 Model, 7 Camera, 0x12 MovementState, 0x13 PlayerController, 0x15 CharacterMover, 0x22 FirstPerson, 0x23 Statescript, 0x24 PvPGame, 0x26 Weapon, 0x27 Projectile, 0x28 Health, 0x2E Spawn, 0x37 DerpBotEntity, 0x3A/0x3B AI targeting/weapon, 0x6D AIBot, 0x73 RequiredMirroredPlaceable, 0x80/0x81 CommandSource/Target.
  - Entity-ID prefixes: 0x20000000 'P' (player/synchronized), 0x40000000 'S' (server), **0x60000000 = "Used when a projectile is spawned on the client using a LeaseBlock"**, and 0x80000000 = "Clients can only spawn entities with this prefix".
  - Entities have three resource IDs: STUEntityDefinition, STUSkinTheme (an override) and STUSkinBase.
  - Startup lobby statescript entity 0x4000000000001f1 runs graphs 0x41a (login/music/pause), 0x41b (lobby UI) and **0x41c (loaded only in-game: HeroSelect, Victory, Scoreboard, Spectate, Hero details)**.
  - The 0.8 systems table includes "Combat System 'combat.disableRecticle'", "Camera System", "First Person System" and "Sends messages to toggle spectator functionality".

  — [owdev.wiki Game/ECS](https://owdev.wiki/wiki/index.php/Game/ECS), [Game/Structure](https://owdev.wiki/wiki/index.php/Game/Structure), [Game/ECS/Systems](https://owdev.wiki/wiki/index.php/Game/ECS/Systems) (read via the MediaWiki API)
- **0.8 launch options** (owdev wiki): `--instanceServer`, `--lobbyServer`, `--DefaultHero`, `--startPosition`, `--BNetServer`, `--tank_InstallDataOnly`, `--tank_FeatureFlags`, `--disableTimeout` and others. These are 0.8 options; whether 1.74 keeps each one is not stated. — [owdev.wiki Game/Launch Options](https://owdev.wiki/wiki/index.php/Game/Launch_Options)

### Inferences
- In 0.8, Prometheus's "hero select done" is the PlayerInfo MirrorData (component 0x3F) plus FilterBits. Those are *replicated* (MirrorData) fields. In 1.74 the equivalents are server-replicated components; see Q4 for what the 1.74 server project sends for 26/44/74/75/123.
- The 0x0D8… IDs are statescript-variable asset GUIDs. Their low 16 bits are the u16 variable IDs that this project uses. If the IDs carried over to 1.74, the vars to check in 1.74 graphs are 0x06C4/0x06C9 (health current/max), 0x094C ("alive"/no-spectator-graph), 0x001C (per-weapon-instance target ID) and 0x001D (valid weapon list). This is unverified for 1.74. The project already noted that 0x00FD is unused in retail graphs.
- The README's "tablist can be force-enabled in a Statescript script" and the wiki's "0x41c loaded only in-game: ... Scoreboard" suggest that the scoreboard and hero-select UI hang off the in-game UI graph 0x41c, which a game-join event loads. That matches this project's 0x041c/0x2206 HUD_Root chain.

### Gaps
- PR #22's file diff and the exact "spectator graph" variable it added could not be seen (the "Files changed" tab was not rendered). Only the artpop2 `player_spawner.cpp` and `entity_admin.cpp` were read.
- The 39C3 talk transcript was not available (c3subtitles returned HTTP 500), so its spoken technical claims are not captured.
- No evidence was found that Prometheus ever showed a working hero HUD (ammo/ability icons). Issue #4 implies a health value was visible, but this was not confirmed.
- owdev.wiki has only about 18 pages. The Networking/JAM pages are stubs.

## Q2. Other projects: Plasmawatch, the 1.74 lobby/game-server line, Workshop "emulators" and others

### Takeaway
The most advanced public work on the *same* build, 1.74.0.0.104319, is the Boi-027 → squeeeezy/"Egor Kulikovskiy" → Boi line of Python servers. It claims a working UDP game server with Practice Range and PvP hero select, skins, walking and multi-player body replication. It names the HUD, weapons and abilities as not done, and the original squeeeezy repo is now 404. Plasmawatch, an older Go Battle.net emulator for 0.8/1.65, is archived. "Overwatch 1 Emulator" is an OW2 Workshop mode, not a server.

### Cited Findings
- **Plasmawatch** ("Overwatch 1 Archival Project").
  - `login-server`: a Go Battle.net emulator on TLS port 1119 plus an auth webserver on 6969, with hosts redirects. Archived Mar 6 2025, 36 stars. The repo ships a private key and a pfx with the password in the README; not reproduced here.
  - `OverLauncher`: a C++ 0.8 launcher. Archived, 45 stars.
  - `lobby`: README "wip, soon"; only a README; updated Aug 7 2026.
  - `go-bnet-compiler`.

  — [Plasmawatch org](https://github.com/plasmawatch); [login-server](https://github.com/plasmawatch/login-server); [lobby](https://github.com/plasmawatch/lobby)
- **Plasmawatch's own forum posts** describe "server emulation software for Overwatch 1" with "Beta 0.8 and 1.65" versions. A developer asked for help with "packets that no longer exist on the servers but are required to enter the game fully". These were seen as search snippets only; RaGEZone returned HTTP 403 to direct fetch. — [RaGEZone: OW1 Beta 0.8 & 1.65 Private Server Development](https://forum.ragezone.com/threads/overwatch-1-beta-0-8-1-65-private-server-development-help-needed.1216816/); [RaGEZone: OW1 Beta Server In-Development](https://forum.ragezone.com/threads/overwatch-1-beta-server-in-development-developers-reverse-engineers-needed.1241771/)
- **Boi-027 / Arlecchino, "Overwatch-1-v1.74-Lobby-Research"** (MIT; last commit Sep 25 2026; "ON HIATUS INDEFINITLY").
  - Says that as of Sep 17 2026, "4-5 people have managed to get into the Overwatch 1.74 Main Menu" and that "someone ... is planning to release a full game server".
  - Solved items it lists:
    - The JAM stream cipher (a known-answer test is given). An anonymous follow-up identifies it as PANAMA.
    - The HMAC-SHA256 key schedule (k0..k3 from the Battle.net session; tournament mode zeroes them).
    - The `HELLO PRO CLIENT/SERVER` handshake, with a proof-of-work counter and a difficulty byte.
    - The 292-byte state blob (tournament-mode shortcut only).
    - A first-reply counter gate.
    - msgid 0x0102 as the ack; 0x0103 polls are answered with keepalives.
    - The JamMessageInfo/ItemInfo layouts, validated against Prometheus `JAM.h`.
  - It also documents decrypted real lobby traffic captured on 1.68.
  - Arxan/ACG limits: no `.text` writes (VirtualProtect err 87 on all 11,408 pages, even with early injection), hardware breakpoints detected, SuspendThread trips a watchdog, x64dbg+ScyllaHide defeated. Heap writes and calling game functions do work.

  — [Boi-027/Overwatch-1-v1.74-Lobby-Research](https://github.com/Boi-027/Overwatch-1-v1.74-Lobby-Research) (README and docs/PROJECT_STATE.txt rev 31)
- **Anonymous follow-up (credited by Boi's fork to "Logo2K", AyakaPS), Sep 26 2026.**
  - Channel setup to CONNECTED on both the tournament (`--lobbyServer`) and retail (Battle.net referral k0–k3, cid, hostv4) routes.
  - Login messages 0x5528, 0x5014/0x5016/0x5018/0x5019 (= 20500/20502/20504/20505) give the main menu.
  - Loot-box messages; the channel type-13 trailer requirement.
  - No instance/game protocol.

  — [rentry.co/3bswrgmw](https://rentry.co/3bswrgmw)
- **"overwatch-1.74-lobby-server"** (MIT; the original squeeeezy repo is 404 as of 2026-10-15; readable copies are the forks Boi-027 (last commit Oct 7 2026, with the `game/` WIP) and LizRollin).
  - A Python offline lobby: Battle.net RPC emulator, relay DLL, JAM codec, 707 lobby message layouts in 87 groups, loot boxes, group finder, role queue, friends, career, menu hero, a web dashboard, LAN hosting.
  - The WIP commit "game server, matchmaking and hero select" (Egor Kulikovskiy, Oct 1 2026) claims these work "checked in the game":
    - matchmaking;
    - "The game connects to our UDP game server (port 3730), loads the map and spawns the player";
    - "Hero select in the Practice Range and in the PvP modes, with skins";
    - "Assemble your team" with a 30 s countdown;
    - the team list showing yourself;
    - walking, with "Other players see your body move and change heroes".
  - "Not done yet":
    - "Weapons, abilities and the in-game HUD. The client predicts them but rolls them back without the server's answers, so the server has to run the heroes' statescript graphs itself";
    - "Other players' bodies play a run animation while standing";
    - teammates in the team list;
    - match phases; "damage and health".
  - Credits: "Xref — ... captured Overwatch 2 game traffic and research on the 1.74 game server ... the facts behind the game server, matchmaking and hero select". The code repeatedly cites "ProCore's live tests" in the Practice Range.

  — [Boi-027/overwatch-1.74-lobby-server](https://github.com/Boi-027/overwatch-1.74-lobby-server) (WIP.md, CREDITS.md, ow174/game/*); [LizRollin fork](https://github.com/LizRollin/overwatch-1.74-lobby-server); [squeeeezy original (now 404)](https://github.com/squeeeezy/overwatch-1.74-lobby-server)
- **"Overwatch 1 Emulator"** (Overwatch-1-Emulator/ow1-emulator, mirrored at LeSqueed): OverPy source for an *OW2 Workshop* game mode that recreates OW1 hero kits (BSD-2; about 2,058 commits). It is not a server. — [GitHub](https://github.com/Overwatch-1-Emulator/ow1-emulator); [workshop.codes](https://workshop.codes/PBMYC)
- **AyakaPS.** A Discord community of OW researchers; mods are listed on ayakamods.com, including Prometheus and an "Overwatch Beta v0.8 Launcher" page. — [ayakamods Prometheus](https://ayakamods.com/mods/prometheus.1451/); [ayakamods launcher](https://ayakamods.com/mods/overwatch-beta-v0-8-launcher.1444/); the community is named in [CREDITS.md](https://github.com/Boi-027/overwatch-1.74-lobby-server)
- **Community perception.** A Steam thread (Jan 23) says the 0.8 build has "no servers ... no shooting", only map selection, moving, jumping and character selection. A Blizzard forum thread (Jan 3–4 2026) calls the 0.8 build "explorable but not playable" and names BreakingBread0/Prometheus. — [Steam discussion](https://steamcommunity.com/app/2357570/discussions/0/685243980153186014/); [Blizzard forums](https://us.forums.blizzard.com/en/overwatch/t/beta-version-of-ow1-got-leaked-online/995710)
- **Unverified claim.** An X post (Oct 2026) says "AI hackers" have private servers "for the latest update to Overwatch". It is a single post with no sourcing. — [x.com/hyxkkimxru](https://x.com/hyxkkimxru/status/2108533805091099130)

### Inferences
- "4-5 people" at the 1.74 main menu (Sep 2026) is consistent with this project's own menu result (2026-10-13). The squeeeezy/Egor WIP (Oct 1 2026) appears to be the "someone ... planning to release a full game server" line, and it overlaps this project's frontier: its hero select and spawn work, but its HUD, weapons and abilities do not.
- Because squeeeezy's upstream is gone, the Boi-027 fork may be the only public copy of the game-server WIP. It could disappear.

### Gaps
- "ProCore", "Xref" and their OW2-traffic knowledge base are not public; nothing could be found.
- No YouTube or video metadata could be read; the page returned an empty shell. One video was found, "You Can Play Overwatch 1 RIGHT NOW... (Reverse Engineered!)", but its contents could not be verified. — [YouTube](https://www.youtube.com/watch?v=rR7JAZOnZ4k)
- No public video or evidence of a hero HUD (health, ammo, abilities, crosshair) working on any private 1.74 or 0.8 server was found.
- The Plasmawatch 1.65 work's technical details are unavailable (archived repos, RaGEZone blocked).

## Q3. Public reverse-engineering write-ups of the protocol, anti-cheat and client internals

### Takeaway
The public sources are GDC 2017 talks (Ford's ECS/netcode talk and Reed's networking statescript talk), Prometheus/owdev (0.8 internals), Boi-027 PROJECT_STATE (1.74 lobby/JAM/Arxan), and the Boi fork's code comments (1.74 UDP link, world frames, statescript frames, input commands). Nothing public was found on "Defense Matrix" or Warden for OW.

### Cited Findings
- **GDC 2017, Tim Ford, "'Overwatch' Gameplay Architecture and Netcode".** Covers ECS and determinism. Secondary summaries report 16 ms command frames (7 ms in tournament) and rollback-and-replay of mispredictions. — [GDC Vault](https://gdcvault.com/play/1024001/-Overwatch-Gameplay-Architecture-and); [Edgegap summary (secondary)](https://edgegap.com/blog/game-backend-deep-dive-overwatch-2016-netcode-architecture-rollback). Corroboration: the 1.74 server uses `RETAIL_QUANTA = 16000` µs and `TOURNAMENT_QUANTA = 7000`, and states "20300 must name the client's own value". — [Boi fork match.py](https://github.com/Boi-027/overwatch-1.74-lobby-server)
- **GDC 2017, Dan Reed, "Networking Scripted Weapons and Abilities in 'Overwatch'".** Statescript runs weapon and ability state machines, and its "prediction and replication of script behavior is automated". This is the official explanation of why the client predicts abilities and needs server state. — [GDC Vault](https://gdcvault.com/play/1024041/Networking-Scripted-Weapons-and-Abilities)
- **1.74 game link (Boi fork `link.py`; code comments with their IDA RVAs).**
  - Datagram layout: 12-byte GCM tag, then u32 `connid<<4|kind`, seq, ack, u64 ack_bits, flags (SYN 1 / ACK 2 / FIN 4), 0xAD.
  - AES-256-GCM. The AAD is the 22 header bytes. The nonce is the 8-byte salt from 20600 plus seq. The 20600 first key is client→server and the second key server→client.
  - Kinds: 0 empty, 1 world frame, 15 bulk fragment.
  - "The transport resends nothing". The client sends SYN until SYN|ACK. MAX_DATAGRAM is 0x4F0.

  This matches this project's own decode. — [Boi fork ow174/game/link.py](https://github.com/Boi-027/overwatch-1.74-lobby-server)
- **World frame / entity channel (Boi fork `world.py`).**
  - ch3 is ack + 4 flag bits + ping bit. ch4 is a 1-bit keep. ch5 ends the list.
  - There is a 7-bit entity count; each entity has a per-channel presence bit.
  - Entity op 2 bits (1 create / 2 update / 3 destroy) plus 14-bit length.
  - Create flags: 0x01 skin (+0x40 = skin theme u32 plus a golden-weapon bit), 0x02 movement-state block, 0x04 scale, 0x08 position+quaternion (+scale), 0x10 "player's own entity (the client adds its command components when 20302 named it)", 0x20 adds component 74.
  - Update body: u8 count; per component an index, byte pad, u8 mask length and field mask, then the field values. "id" u64s are sent as byte mask plus non-zero bytes.

  This matches this project's findings. — [Boi fork world.py](https://github.com/Boi-027/overwatch-1.74-lobby-server)
- **Input commands (Boi fork `commands.py`).** "The client never sends its position". Commands carry frame, throttles, s16 yaw/pitch, 24-bit buttons, action and extra. FIRE 0x01, SECONDARY 0x02, JUMP 0x40, CROUCH 0x80. — [Boi fork](https://github.com/Boi-027/overwatch-1.74-lobby-server)
- **Statescript replication (Boi fork `statescript.py`; reader RVAs in their dump).**
  - Chunk = `w_u32 first | w_var span | fragmented bit | w_var size | payload`.
  - Owner frames (H=1) carry CmFD and are skipped unless CmFD is larger than the last one.
  - A full frame "destroys the network instances it does not list and first clears the variables the network set, so every full frame carries everything".
  - "In an owner frame the states are the graph's m_states minus the client-only and server-only ones".
  - "**Instances the server makes never run their own Entry nodes (only client-only ones run), so the server sends what those would have done**".
  - An ack-only owner delta (`owner_ack`) every 0.1 s moves CmFD forward "else it replays old key presses".

  — [Boi fork statescript.py / match.py](https://github.com/Boi-027/overwatch-1.74-lobby-server)
- **Anti-tamper (1.74).** Arxan plus ACG, as detailed in Q2. Code decrypts per block only while executing. A live dump during execution yields clean code. `.pdata` gives exact function bounds. This matches this project's experience (Win32 87 on code writes; chained `.pdata`). — [Boi-027 PROJECT_STATE.txt](https://github.com/Boi-027/Overwatch-1-v1.74-Lobby-Research)
- **STU (0.8).** CRC32 name hashes (test: "teString" → 0xbbca304b) and STUv1 versus v2 differences. — [owdev.wiki STU](https://owdev.wiki/wiki/index.php/Game/Resources_%26_Managers/STU). The OWLib/TACTLib (overtools) data tools are credited by both 1.74 projects. — [Boi fork CREDITS.md](https://github.com/Boi-027/overwatch-1.74-lobby-server)

### Inferences
- Reed's talk combined with the Boi fork's "server-made instances never run their own Entry nodes" gives the general principle behind the open HUD, ability and Blink problems: the client predicts, and the server must replay the *server-side* graph effects as state sync (states, vars, events). Otherwise the client rolls the prediction back.

### Gaps
- There are no public write-ups of Overwatch's anti-cheat ("Defense Matrix") or of Warden-like scanning in OW, and no public description of the instance join/early-failure failure modes.
- The GDC talks' full text is paywalled; only the abstracts and secondary summaries were read.

## Q4. Technical findings mapped to the project's open problems

### Takeaway
The most actionable external leads all come from the 1.74 Boi/squeeeezy game-server code. Seven stand out:

- The Practice Range uses mode **0x0230000000000018** with team-controller graph **0x13C1**. Its SubScript state 42 starts HUD graph **0x20E4** and state 43 starts hero select 0x288A→0x288B.
- A separate **game-mode entity** (definition 0x04000000000016B2, component 114 MECGameMode = mode GUID) is created.
- Filter bits are **0x00040001 | (0x800000<<team)**; 0x10000000 is the spectator bit.
- Health goes in component 51 ("as the HUD bar reads it").
- Possession uses component 44 and component 75; the body carries component 123.
- Remote bodies are moved by per-frame movement records.
- The map data gives the real Practice spawn point.

Prometheus adds the health/alive/weapon-target statescript vars.

### Cited Findings (all are code-comment claims in [Boi-027/overwatch-1.74-lobby-server](https://github.com/Boi-027/overwatch-1.74-lobby-server) unless marked otherwise)

- **HUD (health, ammo, abilities, crosshair)**
  - "Each team of a game mode names its controller graph. The Practice Range's is 13C1: its SubScript states start the HUD (state 42 -> graph 20E4) and hero select (state 43 -> 288A, whose state 0 -> 288B). The PvP modes use 0C90, whose state 119 starts 288A; its HUD graph is client-only, so the client makes that one itself." — `heroselect.py`
  - `statescript.py` defines `CONTROLLER = Graph(0x13C1, 43 owner states, 12 sync vars)`, `HUD = Graph(0x20E4, 1, 0)` ("13C1's weapon and ability HUD (0C90 starts its own)"), `HERO_SELECT_HOST = Graph(0x288A, 6, 0)`, `HERO_SELECT = Graph(0x288B, 30, 4)` and `TEAM_ENTRY = Graph(0x288D, 0, 0)`.
  - The Practice owner frame puts 13C1 as instance 1 on the **player (controller) entity**, with presence bit 5 (v8419 = 0x20E3, "m_allowHeroSelect") = true and owner state bits 25 (HeroSelect), 37 (SubScript → 288A) and **36 (SubScript → 20E4 as instance 4, parent (1, state 42))**.
  - `tools/extract_game_graphs.py` labels 0x13C0 "Practice Range mode" (a mode graph, not the controller). It labels 0x0F4A/0x0EC2 "PvP mode" and 0x0C8E "PvP mode body".
  - `content.py`: "Practice Range (0688.002 with 0018.0C5)". The map data lists both 0x0230000000000018 and 0x023000000000005A as Practice Range modes, with the same four placeables 0x88/0x22E/0x234/0x289.
  - The controller graph per team comes from the mode's `m_teams[].m_170AA4B8`. — `tools/extract_game_queues.py`
  - Status per WIP.md: the HUD is **still not working** for them either. They attribute this to the server not running the hero statescript graphs.
  - Prometheus (0.8): `0x06C4`/`0x06C9` current/max health floats and `0x094C`=1 ("alive", no spectator graph) on the hero's entity var bag every tick. — [artpop2 entity_admin.cpp](https://raw.githubusercontent.com/saturn-xvi/prometheus/artpop2/Prometheus-Core/entity_admin.cpp)
  - Spectator bit: "0x10000000 is the spectator bit (GetEntityIsSpectator) ... ProCore's player with it got the spectator's HUD panel". — `match.py`
- **Team and filter bits**
  - "Component 26, the filter bits: 0x800000 << team picks the team's physics proxy (team 0 or 1). The client's own session builder gives its player 0x10040001 | that bit, but 0x10000000 is the spectator bit ... bodies with only it had no collision and no enemy outline. So the player gets 0x00040001 | the team bit, a body only the team bit." — `match.py`
  - The component field maps (`world.py`):
    - 26 = MFilterBitsComponentData ["id"].
    - 74 = MECGameModeParticipant [id portrait frame, s16, s8 slot, u8, u8, s8, u8 "can select a hero", u8, u8]. The player create sets slot = player index and fields 6 and 7 = 1.
    - 20300/20301 game struct `+0xC0` teams: `{+0x18: [{+0x0: entity}], +0x60: team, +0x61: team}`.
  - Prometheus 0.8 for comparison: `set_team` sets 0x40000<<team inside mask 0x3C0000, plus filter 0x800000; artpop2 adds `|=0x100` on the hero model. — [entity_admin.h](https://github.com/saturn-xvi/prometheus/blob/main/prometheus/entity_admin.h); [artpop2 player_spawner.cpp](https://raw.githubusercontent.com/saturn-xvi/prometheus/artpop2/Prometheus-Core/player_spawner.cpp)
- **Entity set for a player and game**
  - Order of events:
    1. The client sends 21601 (and later 21602) when the map is loaded.
    2. +0.3 s: 20302 {player entity}. It "has to come before the player's create, or the client does not add its command components (59, 63)".
    3. +0.6 s: one frame creates the placeables, the player entity (000E.003, flags 0x3C) and the **game-mode entity (0x04000000000016B2, component 114 MECGameMode: [u32[], mode GUID, ...])**.
    4. +0.7 s: the controller statescript.
  - The game-mode entity gets only a vars frame ("how an entity without graphs ... gets values that other graphs read"). In PvP, mode graphs set the game-mode entity's v1303 (0x0517) countdown.
  - "The hero's body comes with the pick ... the body with its movement state and an update of the player entity whose component 44 possesses it."
  - Component 44 = MECPossessorData [current, view target, primary possessable] = body ×3.
  - Component 75 = MECCharacterController [current hero, skin theme, ..., last valid hero].
  - The body gets component 123 MECCharacterBody [hero GUID], component 51 health and component 26 team bit.

  — `match.py`, `world.py`
- **Health / damage**
  - "STUHealthComponent: 16 health, 16 armour, 16 shield parts {u32 on, f32 now, f32 max, 4 bytes, 4×u8}, then u32, u32, entity, u8, u8". The field list is 48×blob:20 + u32,u32,entity,u8,u8.
  - `health()` = "Component 51 with one health part, as the HUD bar reads it" (pack `<IffII` 1, now, max, 1, 1). Every hero gets 200.

  — `world.py`, `match.py`. For 0.8 the equivalent is component 0x28 parts at +0x98/+0x1D8/+0x318. — [entity_admin.h](https://github.com/saturn-xvi/prometheus/blob/main/prometheus/entity_admin.h)
- **Hero-select UI**
  - 288B shows screen 008C.05A while v2438 (0x0986, server "open") and v31435 (0x7ACB, read by client-only nodes) are on.
  - The pick is 21616 {entity, params, 0x0240000000001361, instance}. 0x...1360 asks to open or close.
  - v25377 (0x6321) presence bit 0 shows the **skin selector** ("with it on, the client leaves the screen open after a pick, so the server closes it").
  - v8535 (0x2157) hides "ASSEMBLE YOUR TEAM".
  - A chosen skin goes to the lobby as 24500 and is applied via create flags 0x41 (skin theme).
  - Team list: "288A's state 1 starts 288D, whose client-only nodes post their entity (game message 134F.025) to the local player's 288B unless it is an enemy. On our own entity that puts us in the list."

  — `heroselect.py`
- **Main-menu hero model.** A retail config key, `MENU_HERO_KEY = 0x87053C32` in lobby message 36600, "can put any loaded hero record in the menu". — `content/menu_hero.py`. The hero catalogue/loadouts are 24900 and the account record is 24300. — `content/collection.py`. Relevant leads for gallery/preview cosmetics: they implement 24900 loadout slots and 24500 equip. No claim about the 3D preview in hero select was found.
- **Non-controlled entity replication**
  - Remote bodies are "placed by its transform, then moved by movement records from the next frame on (a movement state in the create would sit at frame 0xFFFFFFFE, and the client refuses every later record that is not newer)".
  - Every frame carries one ch3 movement record per other body, "standing or not, as the retail server sent them (OW2's live traffic)".
  - "A movement state is only kept when its command frame is newer than the newest one the entity has."
  - A hero switch replaces the body under a new id in the same frame; "the client ignores a destroyed id for 30 s".

  — `match.py`, `world.py`
- **Spawn position.** Map data gives the Practice spawn (team 0) at **(54.56507, 0.99999833, 42.147877)**, yaw −170.343, placeable 564 / entity index 443, tag 0x0D60000000000310. — `data/game_maps_174.json`
- **Weapons and abilities (prediction/rollback)**
  - "The client predicts them but rolls them back without the server's answers, so the server has to run the heroes' statescript graphs itself" (WIP.md).
  - Owner frames that only advance CmFD every 0.1 s, "else it replays old key presses" (`match.py`/`statescript.py`).
  - Prometheus artpop2: load weapon graphs with flag 0x8, set **instance var 0x001C = weapon target ID** per weapon graph, and set entity array 0x001D = valid weapon IDs.
  - Drahsid (0.8): "abilities ... wait on something from the server"; Recall was done by hacking. — [issue #35](https://github.com/saturn-xvi/prometheus/issues/35)
- **Blink/Recall and server position.** "The client then moves the body itself; it never tells the server where it is. The server moves a copy from the commands" (a FlatMover with no collision). This is the same limitation the project hit. — `match.py`, `mover.py`
- **Projectile origin and child entities.** The owdev wiki says entity prefix 0x60000000 is "Used when a projectile is spawned on the client using a LeaseBlock" and 0x80000000 is the only prefix clients may spawn. — [owdev ECS](https://owdev.wiki/wiki/index.php/Game/ECS). Prometheus's README notes D.Va floats "because the Mecha isnt spawned", which points to child/pet entities being server-spawned. Its Component 0x1F Backref has `override_views` and backref ids. — [entity_admin.h](https://github.com/saturn-xvi/prometheus/blob/main/prometheus/entity_admin.h)
- **Intermittent early instance failure** (no direct public diagnosis)
  - Related facts: "The handshake names the address the client dialed and the real port. The client dropped the connection when neither matched, as with a server listening on 0.0.0.0" (commit 82f994e). This is a lobby/referral handshake observation.
  - The transport never resends and drops seq below the expected value. 20300 +0x500 must equal the client's command-frame length.

  — [Boi fork commit history](https://github.com/Boi-027/overwatch-1.74-lobby-server)

### Inferences
- **The strongest HUD lead.** This project used mode 0x5A and created mode graphs 0x13C0/0x0C8E/0x0C90 *on the controller*. The 1.74 server instead uses mode 0x18, runs **13C1 as the controller graph**, and starts **0x20E4 as a server-created sub-instance via 13C1 state 42**. It keeps mode graphs off the player and on a game-mode entity (16B2, component 114). This project's HANDOFF already found that 0x01CF (hero HUD) waits for game message 0x1291, which only 0x20E4 #187 sends, and that "0x20e4 is client-spawned from 0x0c90". The Boi model says 20E4 is instead started by 13C1's SubScript in the Practice mode. That is a concrete, testable alternative path. It is unverified: their HUD is also not working.
- The project's red "no-entry" indicator and the missing hero HUD may be related to the missing game-mode entity and component 114, and to filter bits. The client's own default 0x10040001 includes the spectator bit, which "got the spectator's HUD panel".
- The 0.8 "alive" var 0x094C and the health vars 0x06C4/0x06C9 are worth looking up in 1.74 graph dumps to see whether the 1.74 hero HUD presenters read them.
- The spawn coordinates from the map data could replace the hand-found (48.71, 2.0, 42.0) and reduce Blink and geometry problems.

### Gaps
- No project has publicly shown a working 1.74 hero HUD, server-run ability graphs, child/hardpoint weapon entities, or the hero-select 3D preview.
- The Boi fork's claims are code comments and a WIP note. There is no video or independent verification. "ProCore's live tests" are not public.
- How retail picks between Practice mode 0x18 and 0x5A (map data lists both) is not documented publicly.

## Q5. Status as of Oct 2026 and legal issues

### Takeaway
Activity is concentrated in community Discords (Prometheus/owdev, AyakaPS). Prometheus's artpop2 branch was active until May 2026. The 1.74 lobby research is on hiatus (Sep 2026), and the 1.74 game-server WIP is from Oct 2026 but its original repo has disappeared. The only takedown found is of the 0.8 beta archive.org upload. No public DMCA against the code repos was found.

### Cited Findings
- **The 0.8 archive was removed.** The owdev wiki says: "Blizzard has taken down the archive.org link". It also points to a torrent (hash not reproduced here). — [owdev.wiki Game/Versions](https://owdev.wiki/wiki/index.php/Game/Versions). Prometheus issues #36 (closed Mar 11 2026, "Link to 0.8 Download has been taken down.") and #40 (Aug 12 2026, "0.8 Beta Archive Link No Longer Available") record the same thing. — [issues list](https://github.com/saturn-xvi/prometheus/issues?q=is%3Aissue)
- **Prometheus activity.** About 26 issues (Jan–Oct 2026) and 13 PRs; only #17, #22 and #28 were merged. Open PR #39 is about health. The maintainer: "currently working on more stuff", a new wiki and Discord (Feb 2026). — [issues](https://github.com/saturn-xvi/prometheus/issues?q=is%3Aissue); [PRs](https://github.com/saturn-xvi/prometheus/pulls?q=is%3Apr); [issue #35](https://github.com/saturn-xvi/prometheus/issues/35); [owdev.wiki](https://owdev.wiki/)
- **Plasmawatch.** login-server and OverLauncher were archived (2024–2025); the lobby repo is a placeholder (Aug 2026). — [Plasmawatch](https://github.com/plasmawatch)
- **1.74 lobby research.** "ON HIATUS INDEFINITLY" (Sep 17 2026). — [Boi-027 research](https://github.com/Boi-027/Overwatch-1-v1.74-Lobby-Research). The squeeeezy lobby-server upstream returns 404, and forks remain (Boi-027 updated Oct 7 2026). — [squeeeezy (404)](https://github.com/squeeeezy/overwatch-1.74-lobby-server); [Boi-027 fork](https://github.com/Boi-027/overwatch-1.74-lobby-server)
- **Origin of the 0.8 build.** A Blizzard forum reply says the 0.8 build was leaked by the archivist group Hidden Palace in September of the previous year. This is a user claim and was not verified against a Hidden Palace page. — [Blizzard forums](https://us.forums.blizzard.com/en/overwatch/t/beta-version-of-ow1-got-leaked-online/995710)
- **Background.** OW1 servers shut down on Oct 3 2022. OW2 was renamed "Overwatch" in Feb 2026. — [Wikipedia: Overwatch 2](https://en.wikipedia.org/wiki/Overwatch_2)
- **Press coverage.** No coverage by PC Gamer, Kotaku or Dexerto of an OW1 private server was found, and no official Blizzard statement was found. — search results summarized above (no hits)

### Inferences
- The legal pressure seen so far targets distribution of game binaries (the archive.org copy), not source code. Projects avoid shipping clients. Both 1.74 projects say "The game is not included", in line with this project's policy.
- The disappearance of the squeeeezy repo is unexplained. A takedown or a voluntary removal both fit the evidence; there is no source either way.

### Gaps
- No DMCA notice in github/dmca for these repos was checked. The GitHub DMCA repo was not searched, so this is a gap rather than a negative result.
- No reporting explains why the squeeeezy repo was removed.
