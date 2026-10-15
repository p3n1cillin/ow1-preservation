# Overwatch 1 maps (final OW1 state, 2022), Practice Range and Training

Scope: every OW1 map by mode, objective and spawn structure, public datamined identifiers and Workshop coordinates, and Practice Range/Training detail. The target is the final client, 1.74.0.0.104319.
Method notes for the report writer:
- Fandom wiki pages could not be fetched directly: WebFetch returned HTTP 402 and curl hit Cloudflare 403. The **OW1-era wikitext** came instead from the Fandom MediaWiki API, asking for the last revision on or before 2022-09-30 (`api.php?action=query&prop=revisions&rvstart=2022-09-30T00:00:00Z&rvdir=older`). Each Fandom citation below names the page and that revision's timestamp. The revision dates line up with the end of OW1 (OW2 replaced it on 2022-10-04).
- Liquipedia wikitext came from `?action=raw`. Liquipedia, overwatch.wiki.gg and web.archive.org could not be read through WebFetch.
- OverPy and OWLib were cloned read-only. Their code was not run. Commits: OverPy `5a7d0e29` (2026-10-06), OWLib `546efa19` (2026-10-11). Both are current OW2-era repositories, so their data includes OW2 maps. OW2-only entries are flagged below.

---

## 1. Complete OW1 map list by mode, with release dates and removals

### Takeaway
At the end of OW1 (Sept 2022), Fandom listed 21 standard-play maps: 5 Assault, 6 Escort, 5 Hybrid and 5 Control, the Control maps having 3 sub-maps each. It also listed 9 Arcade-specific maps (4 Elimination, 4 Deathmatch, 1 CTF), 3 Lúcioball stadiums, event and PvE variants (Adlersbrunn, Uprising King's Row, Retribution Rialto, Storm Rising Havana, Yeti Hunter Nepal Village, Winter/Halloween/Lunar New Year skins), Practice Range, Tutorial, and the Workshop maps (Chamber, Expanse, Island, Green Screen, plus Night variants). Push, Circuit Royal, Midtown, Paraíso, Colosseo, Esperança, New Queen Street and the later maps belong to OW2, not the OW1 build.

### Cited Findings

**Standard play (QP/Competitive), as Fandom described it just before OW2**
- "There are 21 maps available for standard gameplay: 3 Assault maps, 6 Escort maps, 5 Hybrid maps, and 5 Control maps." In the same revision, the Assault gallery marks Horizon Lunar Colony and Paris as "(removed from rotation)". That revision dates from 2022-09-23, after the OW2 announcement. Treat it as the OW2 rotation change: both maps still exist as playable assets in OW1. — [Fandom "Map", rev. 2022-09-23](https://overwatch.fandom.com/wiki/Map)
- In the same revision, Circuit Royal, Midtown, Paraíso, Colosseo, Esperança, New Queen Street, Gothenburg, Suravasa ("India") and Shambali are all marked "(unreleased)", i.e. OW2. — [Fandom "Map", rev. 2022-09-23](https://overwatch.fandom.com/wiki/Map)
- Assault ("2CP") "will be removed from the playlist of Overwatch 2 ... Assault maps will still be available via custom settings." — [Fandom "Assault", rev. 2022-04-07](https://overwatch.fandom.com/wiki/Assault)

| Mode | Map | Location (Fandom/Liquipedia) | Release date (Liquipedia infobox unless noted) | Notes |
|---|---|---|---|---|
| Assault | Hanamura | Tokyo, Japan | 2015-10-27 | 2 checkpoints (A, B) |
| Assault | Temple of Anubis | Egypt | 2015-10-27 | 2 |
| Assault | Volskaya Industries | Russia | 2015-10-27 | 2 |
| Assault | Horizon Lunar Colony | Moon | 2017-06-20 (Liquipedia prose: announced 2017-05-31; "significant redesign" 2018-06-26) | 2; removed from OW2 rotation |
| Assault | Paris | France | 2019-02-19 | 2; removed from OW2 rotation |
| Escort | Dorado | Mexico | 2015-10-27 | 3 checkpoints; Evening/Night lighting |
| Escort | Route 66 | Albuquerque, New Mexico, US | added to the closed beta 2016-03-22 | 3 |
| Escort | Watchpoint: Gibraltar | Gibraltar | 2015-10-27 | 3 |
| Escort | Junkertown | Australia | 2017-09-19 (PTR 2017-08-29) | 3 |
| Escort | Rialto | Venice, Italy | 2018-05-03 | 3 |
| Escort | Havana | Havana, Cuba | 2019-05-07 | 3 |
| Hybrid | Hollywood | United States | 2015-11-10 | 3 |
| Hybrid | King's Row | London, UK | 2015-10-27 | 3 |
| Hybrid | Numbani | Africa (Nigeria/fictional) | 2015-10-27 | 3 |
| Hybrid | Eichenwalde | Germany | 2016-09-01 | 3 |
| Hybrid | Blizzard World | United States | 2018-01-23 | 3 |
| Control | Ilios (Lighthouse, Well, Ruins) | Greece | 2016-03-08 | 3 stages |
| Control | Lijiang Tower (Garden, Night Market, Control Center) | China | 2016-02-09 | 3 stages |
| Control | Nepal (Village, Shrine, Sanctum) | Nepal | 2016-02-09 | 3 stages |
| Control | Oasis (City Center, Gardens, University) | Iraq | 2017-01-03 | 3 stages |
| Control | Busan (Downtown, Sanctuary, MEKA Base) | South Korea | live with patch 1.28 on 2018-09-11 (PTR 2018-08-22) | 3 stages |

Sources for the table:
- Release dates, checkpoints and lighting come from the Liquipedia infoboxes: [Hanamura](https://liquipedia.net/overwatch/Hanamura), [Horizon Lunar Colony](https://liquipedia.net/overwatch/Horizon_Lunar_Colony), [Paris](https://liquipedia.net/overwatch/Paris), [Temple of Anubis](https://liquipedia.net/overwatch/Temple_of_Anubis), [Volskaya Industries](https://liquipedia.net/overwatch/Volskaya_Industries), [Dorado](https://liquipedia.net/overwatch/Dorado), [Havana](https://liquipedia.net/overwatch/Havana), [Junkertown](https://liquipedia.net/overwatch/Junkertown), [Rialto](https://liquipedia.net/overwatch/Rialto), [Watchpoint: Gibraltar](https://liquipedia.net/overwatch/Watchpoint:_Gibraltar), [Blizzard World](https://liquipedia.net/overwatch/Blizzard_World), [Eichenwalde](https://liquipedia.net/overwatch/Eichenwalde), [Hollywood](https://liquipedia.net/overwatch/Hollywood), [King's Row](https://liquipedia.net/overwatch/King%27s_Row), [Numbani](https://liquipedia.net/overwatch/Numbani), [Ilios](https://liquipedia.net/overwatch/Ilios), [Lijiang Tower](https://liquipedia.net/overwatch/Lijiang_Tower), [Nepal](https://liquipedia.net/overwatch/Nepal), [Oasis](https://liquipedia.net/overwatch/Oasis).
- Busan live date: [Liquipedia September 11, 2018 Patch](https://liquipedia.net/overwatch/September_11,_2018_Patch), [GameSpot](https://gamespot.com/articles/overwatchs-new-busan-map-now-live-on-pc-ps4-and-xb/1100-6461694/). Busan PTR on 2018-08-22: [Fandom "Busan", rev. 2022-08-11](https://overwatch.fandom.com/wiki/Busan).
- Route 66 beta patch of 2016-03-22: [Blizzard Watch](https://blizzardwatch.com/2016/03/22/overwatchs-latest-beta-patch-brings-new-map-weekly-brawls/). An April 19, 2016 beta patch slowed its payload by 10% ([over.gg](https://www.over.gg/272/overwatch-beta-patch-for-april-19-2016), via search summary).
- Locations and terrain: Fandom infoboxes, revisions of 2022 ([Hanamura](https://overwatch.fandom.com/wiki/Hanamura), [Route 66](https://overwatch.fandom.com/wiki/Route_66), [King's Row](https://overwatch.fandom.com/wiki/King%27s_Row), [Rialto](https://overwatch.fandom.com/wiki/Rialto), [Watchpoint: Gibraltar](https://overwatch.fandom.com/wiki/Watchpoint:_Gibraltar), [Havana](https://overwatch.fandom.com/wiki/Havana), [Paris](https://overwatch.fandom.com/wiki/Paris)).
- Liquipedia lists the stage names and lighting variants for each Control map ("Lighthouse/Well/Ruins", "Evening/Morning", and so on). Busan's stages appear in [Fandom "Control", rev. 2021-06-18](https://overwatch.fandom.com/wiki/Control).

**Arcade-specific maps**

| Mode family | Map | Location | Release (Liquipedia) |
|---|---|---|---|
| Elimination/Arena | Black Forest | Germany | 2017-05-23 |
| Elimination/Arena | Castillo | Mexico | 2017-05-23 |
| Elimination/Arena | Necropolis | Egypt | 2017-05-23 |
| Elimination/Arena | Ecopoint: Antarctica | Antarctica | 2016-11-15 (revealed at BlizzCon 2016) |
| Deathmatch | Château Guillard | France | 2017-08-29 |
| Deathmatch | Petra | Southern Jordan | 2018-05-22 |
| Deathmatch | Kanezaka | Tokyo, Japan | 2021-01-12 (PTR Dec 2020) |
| Deathmatch | Malevento | Italy | 2021-09-28 (PTR 2021-08-26; delayed from July 2021) |
| CTF | Ayutthaya | Thailand | 2018-02-08 |
| Lúcioball | Estádio das Rãs | Brazil | 2016-08-02 |
| Lúcioball | Sydney Harbour Arena | Australia | 2017-08-08 |
| Lúcioball | Busan Stadium | South Korea | 2018-08-09 |

- Liquipedia infoboxes: [Black Forest](https://liquipedia.net/overwatch/Black_Forest), [Castillo](https://liquipedia.net/overwatch/Castillo), [Necropolis](https://liquipedia.net/overwatch/Necropolis), [Ecopoint: Antarctica](https://liquipedia.net/overwatch/Ecopoint:_Antarctica), [Château Guillard](https://liquipedia.net/overwatch/Ch%C3%A2teau_Guillard), [Petra](https://liquipedia.net/overwatch/Petra), [Kanezaka](https://liquipedia.net/overwatch/Kanezaka), [Malevento](https://liquipedia.net/overwatch/Malevento), [Ayutthaya](https://liquipedia.net/overwatch/Ayutthaya), [Estádio das Rãs](https://liquipedia.net/overwatch/Est%C3%A1dio_das_R%C3%A3s), [Sydney Harbour Arena](https://liquipedia.net/overwatch/Sydney_Harbour_Arena), [Busan Stadium](https://liquipedia.net/overwatch/Busan_Stadium).
- Kanezaka was on the PTR in December 2020 and released the following January. — [Fandom "Kanezaka", rev. 2022-09-27](https://overwatch.fandom.com/wiki/Kanezaka)
- Malevento: PTR August 2021, "fully integrated in the game on September 28", and postponed from July 2021. — [Fandom "Malevento", rev. 2022-07-23](https://overwatch.fandom.com/wiki/Malevento)
- Ecopoint: Antarctica was revealed at BlizzCon 2016. — [Fandom "Ecopoint: Antarctica", rev. 2022-01-28](https://overwatch.fandom.com/wiki/Ecopoint:_Antarctica)

**Control maps split for Arcade**
- When Control maps are added to the Arcade, "the stages are split into maps of their own and are given a new time of day." Those split maps are Ilios Lighthouse/Ruins/Well, Lijiang Control Center/Garden/Night Market, Nepal Sanctum/Shrine/Village, and Oasis City Center/Gardens/University. Assault, Escort and Hybrid maps are cropped instead when used for Deathmatch. — [Fandom "Map", rev. 2022-09-23](https://overwatch.fandom.com/wiki/Map)
- OverPy's Workshop data agrees. Each split stage is its own Workshop map (for example `iliosLighthouse`, `lijiangGarden`, `oasisUniversity`), supporting elimination, ctf, ffa, bountyHunter and tdm, with recorded symmetry axes. — [OverPy maps.ts](https://github.com/Zezombye/overpy/blob/5a7d0e294b8cad73b9701987bb584d0551d7fa4d/src/data/maps.ts)

**Seasonal and event variants**
- Halloween Terror: Château Guillard, Eichenwalde and Hollywood. Winter Wonderland: Black Forest, Blizzard World, Ecopoint: Antarctica, Hanamura and King's Row. Lunar New Year: Busan Downtown, Busan Sanctuary and Lijiang Tower. "The normal versions of these maps are still available." — [Fandom "Map", rev. 2022-09-23](https://overwatch.fandom.com/wiki/Map)
- Event-exclusive brawl maps:
  - Junkenstein's Revenge takes place in "Adlersbrunn", "a modified nighttime version of Eichenwalde" built on the castle gate.
  - Mei's Snowball Offensive uses winter Black Forest and winter Ecopoint: Antarctica.
  - Yeti Hunt uses Nepal Village: one end spawns a team of Meis, a cave spawns the Yeti (Winston), and meat stations are scattered across the map.
  - Archives (PvE): Uprising is a daytime King's Row from about seven years earlier; Retribution is a nighttime Rialto from eight years earlier; Storm Rising is a stormy Havana from six years earlier.
  - [Fandom "Map", rev. 2022-09-23](https://overwatch.fandom.com/wiki/Map)
- In Adlersbrunn, unlike Eichenwalde, nothing can be fallen off: the bridge sides are pools of water and rocks block the right-hand drop. The co-op mode has 4 players. — [Fandom "Junkenstein's Revenge", rev. 2020-11-12](https://overwatch.fandom.com/wiki/Junkenstein%27s_Revenge)
- Storm Rising has four phases on Havana: garage spawn → streets to the distillery entrance (with a dropship) → distillery interior ambush → truck explosive to open the sea-fort doors → final sea-fort waves (snipers, assassin, Heavy Assault). — [Fandom "Storm Rising", rev. 2022-05-01](https://overwatch.fandom.com/wiki/Storm_Rising)
- OverPy's Workshop map list includes seasonal maps as separate Workshop maps: `blackForestWinter`, `blizzWorldWinter`, `busanDowntownLny`, `busanSanctuaryLny`, `chateauGuillardHalloween`, `ecopointAntarcticaWinter`, `eichenwaldeHalloween`, `hanamuraWinter`, `hollywoodHalloween`, `kingsRowWinter`, the Lijiang Lunar New Year variants (`lijiangTowerLny`, `lijiangGardenLny` and others), `nepalVillageWinter` (yetiHunter), and `junkenstein` (junkenstein mode). OverPy flags the Lúcioball stadiums `onlyInOw1`. — [OverPy maps.ts](https://github.com/Zezombye/overpy/blob/5a7d0e294b8cad73b9701987bb584d0551d7fa4d/src/data/maps.ts)

**Workshop maps**
- Workshop Chamber, Island and Expanse were introduced as custom-game-only maps. Chamber is an enclosed 40×40 m room. Island is the same size with no roof or walls. Expanse is a blank 900×900 m plane, "technically the largest map" the team made. They first appeared in the PTR notes of about 2020-02-04, alongside Subroutines and the Script Diagnostics panel. — [Blizzard "Workshop update grants unprecedented power for creators"](https://overwatch.blizzard.com/en-us/news/23303016) and [PTR notes Feb 4 2020 (devtrackers)](https://devtrackers.gg/overwatch/p/022ae269-overwatch-ptr-patch-notes-feb-4-2020) (via search summary)
- Workshop Green Screen already existed by the PTR notes of October 23, 2020, which fixed projectile collision with its walls. — [devtrackers PTR Oct 23 2020](https://devtrackers.gg/overwatch/p/21a0b3be-overwatch-ptr-patch-notes-october-23-2020) (via search summary). The Fandom stub was created 2021-03-28. — [Fandom "Workshop Green Screen"](https://overwatch.fandom.com/wiki/Workshop_Green_Screen)
- OverPy additionally lists `workshopExpanseNight` and `workshopIslandNight`, both symmetric about z=0. — [OverPy maps.ts](https://github.com/Zezombye/overpy/blob/5a7d0e294b8cad73b9701987bb584d0551d7fa4d/src/data/maps.ts)

**OW2-only maps in current data sources (exclude for the 1.74 client)**
- OverPy's current list also contains these OW2 maps: Aatlis, Antarctic Peninsula, Arena Victoriae, Gogadoro, Redwood Dam, Place Lacroix, Circuit Royal, Colosseo, Esperança, Grímsvötn, Hanaoka, Midtown, Neon Junction, New Junk City, New Queen Street, Paraíso, Runasapi, Samoa, Shambali Monastery, Suravasa and Throne of Anubis. — [OverPy maps.ts](https://github.com/Zezombye/overpy/blob/5a7d0e294b8cad73b9701987bb584d0551d7fa4d/src/data/maps.ts); OW2 timing per [Liquipedia Portal:Maps](https://liquipedia.net/overwatch/Portal:Maps)
- Liquipedia's current portal lists Push, Flashpoint, Clash and Payload Race (Stadium) as modes. All are OW2. — [Liquipedia Portal:Maps](https://liquipedia.net/overwatch/Portal:Maps)

### Inferences
- Liquipedia gives "2015-10-27" for the original maps. That is the closed-beta start date, not retail launch (May 24, 2016). For "available in the 1.74 client", all 21 standard maps, the 12 Arcade/Lúcioball maps above and the event variants are present. This is consistent with OverPy's list of seasonal Workshop maps and its `onlyInOw1` stadiums.
- In OW1's final state, Horizon Lunar Colony and Paris were still playable in-game (custom games and Arcade Deathmatch). The "removed from rotation" label reflects the OW2 announcement made before the wiki revision. For a reimplemented server they are fully valid OW1 content.
- Only the Lúcioball stadiums are flagged `onlyInOw1` in OverPy, so every other OW1 map persisted into OW2 data, possibly reworked.

### Gaps
- The exact retail-launch map list per patch (beyond the launch 12 plus additions) was not verified from patch notes. A patch-by-patch table would need Blizzard's patch-notes archive.
- No source gave the dates for Workshop Expanse Night and Island Night, or Green Screen's exact patch.
- No official date was found for the 2018-06-26 Horizon Lunar Colony redesign beyond Liquipedia's prose.
- The OW1 competitive map pools introduced in later seasons (rotations per season) were not researched.

---

## 2. Per-map objectives, checkpoints, payload, spawn rooms and health packs

### Takeaway
The structural rules by mode are well documented:
- Assault: points A and B; 3 spawn rooms (2 attacker, 1 defender).
- Escort: 3 checkpoints; 6 spawn rooms, with both teams' spawns moving at each checkpoint.
- Hybrid: point A then 2 payload checkpoints; defender spawn count varies by map.
- Control: 3 stages, best of 3, one spawn per team per stage.

Timings and capture rates are documented. Payload speeds per map are documented; full path lengths per map were only partly found. Health-pack counts per map exist from workshop.codes. The objective areas can be extracted with OWLib, which identifies objectives through the shared statescript graph 0x0580000000000E8E.

### Cited Findings

**Assault**
- Assault maps have two rectangular capture areas, A and B. "Objective A is between the attacker and defender spawn rooms, and Objective B is in front of the defender spawn room. In total, Assault maps have three spawn rooms (two attackers, one defender). After Objective A is captured, the second attacker spawn room is opened up next to it." — [Fandom "Map", rev. 2022-09-23](https://overwatch.fandom.com/wiki/Map)
- Timing: attackers get 4 minutes for point A; capturing it adds 3 minutes for point B (3 minutes on the clock if A falls in overtime). Defender spawn never changes. Capture speed caps at 3 players. The progress circle has 3 ticks that act as checkpoints, so progress only falls back to the last tick. — [Fandom "Assault", rev. 2022-04-07](https://overwatch.fandom.com/wiki/Assault)
- Point A capture times per tick (1p/2p/3p): 10/7/5 s, cumulative 20/13/10 and 30/20/15. Point B tick 1 takes 6/4/3 s; the rest of the table was not captured. — [Fandom "Assault", rev. 2022-04-07](https://overwatch.fandom.com/wiki/Assault)

**Escort**
- "Escort maps have a payload that the attackers must escort across three checkpoints. The payload is located next to the attackers' first spawn room. In total, Escort maps have six spawn rooms (three attackers, three defenders). Attacker and defender spawn rooms change every time a checkpoint is reached, with the new attacker spawn room being right next to the captured checkpoint and the new defender spawn room moderately behind the next checkpoint." — [Fandom "Map", rev. 2022-09-23](https://overwatch.fandom.com/wiki/Map)
- Payload mechanics:
  - The payload rolls back toward the last checkpoint if no attacker is near it for 10 s.
  - Defenders in range contest it.
  - Attackers in range are healed 10 HP/s.
  - Speed multiplier: 1 player = 100%, 2 = 116.5%, 3 = 133%.
  - [Fandom "Escort", rev. 2022-07-04](https://overwatch.fandom.com/wiki/Escort)
- Payload speeds in m/s for 1/2/3 players: Havana 1.4/1.65/1.85; Route 66 1.4/1.65/1.85; Junkertown 1.55/1.8/2.05; Dorado 1.55/1.8/2.05; Watchpoint: Gibraltar 1.7/2/2.25; Rialto 1.7/2/2.25. — [Fandom "Escort", rev. 2022-07-04](https://overwatch.fandom.com/wiki/Escort)
- OW2's current Escort rules give 2:30 and 1:30 bonus time at checkpoints 1 and 2 in competitive. That is the OW2 rule. The OW1-era page only says "each checkpoint reached adds extra time". — [Fandom API current "Escort"](https://overwatch.fandom.com/wiki/Escort) vs the 2022-07-04 revision

**Hybrid**
- "There is an Objective A for attackers to capture, and after it is captured, attackers must escort a payload across two checkpoints." The payload starts as part of the objective on Eichenwalde, Hollywood and Numbani, and must be unlocked on Blizzard World and King's Row. "The distance between Objective A and the first checkpoint is slightly longer than the distance between the first checkpoint and the second." Each stage has an attacker spawn room, and there is a defender spawn for Objective A. King's Row and Numbani have one defender spawn for both payload stages; Blizzard World, Eichenwalde and Hollywood have one per stage. — [Fandom "Map", rev. 2022-09-23](https://overwatch.fandom.com/wiki/Map)
- Hybrid point A capture times per tick (1p/2p/3p): 11/7/5, 21/14/10, 32/21/15 s. Payload speeds in m/s: Hollywood, King's Row and Numbani 1.55/1.8/2.05; Blizzard World and Eichenwalde 1.7/2/2.25. — [Fandom "Hybrid", rev. 2022-07-04](https://overwatch.fandom.com/wiki/Hybrid)
- Partial payload distances from the current Fandom Hybrid "map details" table (search snippet only; column meaning unclear): Blizzard World ~113.67 m + 111.61 m = 225.28 m; Eichenwalde ~127.96 m + 67.74 m = 195.7 m. The same snippet notes that some maps' payload speed was buffed in OW2. — [Fandom "Hybrid"](https://overwatch.fandom.com/wiki/Hybrid) (search summary, not verified against the page)

**Control**
- Best of three. The point unlocks 30 s after both teams leave spawn. Score progresses 1% every 1.2 s for the controlling team. Overtime triggers at 99%. Each Control map has three objective areas, "randomly chosen for every round". Until the end of Season 5, competitive matches were best of five. — [Fandom "Control", rev. 2021-06-18](https://overwatch.fandom.com/wiki/Control)
- Capture time for tick 1 (1p/2p/3p): 8/5/4 s. "All control objectives in Overwatch are rendered on a single map instance and sometimes can be seen from each other." — [Fandom "Control", rev. 2021-06-18](https://overwatch.fandom.com/wiki/Control)
- "Both teams are attackers and there is one spawn room for each team, for each stage, located at each end of the map ... Control maps are by default symmetrical." — [Fandom "Map", rev. 2022-09-23](https://overwatch.fandom.com/wiki/Map)
- In Workshop terms the three control points share one map at different coordinates and are reachable through `Objective Position(0..2)`. — [Blizzard forum "Workshop help, teleporting between maps"](https://us.forums.blizzard.com/en/overwatch/t/workshop-help-teleporting-between-maps/524696) (via search summary)

**Arcade modes and maps**
- Elimination (Arena) maps are "small, symmetrical maps with a spawn room at each end", also used for 1v1 Duels. Deathmatch maps "have no spawn room". CTF maps are "large, symmetrical maps with a spawn room at each end", with each flag area near a spawn. — [Fandom "Map", rev. 2022-09-23](https://overwatch.fandom.com/wiki/Map)
- CTF: first team to 3 captures wins. Overtime does not burn while a flag is outside its base. FFA Deathmatch has 8 players, first to 20 points or highest score at 10 minutes. TDM is 4v4, first to 30. Some Deathmatch maps are partitioned. — [Fandom "Capture the Flag" (game modes page), rev. 2022-06-30](https://overwatch.fandom.com/wiki/Capture_the_Flag)
- Lúcioball maps are "a simple field inside a transparent stadium" with launch pads, wall-ride sides and a goal at each end, plus a native-language announcer. — [Fandom "Map", rev. 2022-09-23](https://overwatch.fandom.com/wiki/Map)

**Spawn rooms (generic)**
- Every spawn room has a healing zone and a barrier. Enemies inside an enemy healing zone take damage until they die, and this is not counted as environmental damage. — [Fandom "Spawn Room", rev. 2021-06-27](https://overwatch.fandom.com/wiki/Spawn_Room)

**Health packs**
- Small packs restore 75 HP and respawn in 10 s. Large packs restore 250 HP and respawn in 15 s. Packs cleanse Ana, Ashe and Widow DoTs. Packs hacked by Sombra are unusable by enemies and respawn 4× faster. Control maps mirror health packs about the objective. — [Fandom "Health Pack", rev. 2021-09-12](https://overwatch.fandom.com/wiki/Health_Pack)
- workshop.codes has a community list of every health pack in Workshop coordinates (arrays `Global.A` small and `Global.B` large; page updated 2023-09-01, credited to a Blizzard forum post). Counts are small/large:
  - Assault: Hanamura (and Winter) 10/8; Horizon 7/6; Paris 10/3; Anubis 6/7; Volskaya 9/7.
  - Control:
    - Busan: Downtown 5/1, Sanctuary 7/3, MEKA Base 11/1.
    - Ilios: Lighthouse 4/4, Well 6/4, Ruins 0/7.
    - Lijiang: Night Market 5/7, Garden 5/7, Control Center 4/4.
    - Nepal: Village 3/6, Shrine 2/7, Sanctum 2/6.
    - Oasis: City Center 6/4, Gardens 5/5, University 6/3.
  - Hybrid: Blizzard World 12/9; Eichenwalde 12/6; Hollywood 8/7; King's Row 9/6; Numbani 10/7.
  - Escort: Dorado 11/8; Havana 10/4; Junkertown 5/8; Rialto 9/5; Route 66 6/6; Gibraltar 11/6.
  - Deathmatch variants:
    - Black Forest 3/1, Castillo 3/1, Château Guillard 3/2, Ecopoint 3/1.
    - Kanezaka 5/3, Malevento 7/1, Necropolis 4/1, Petra 9/1.
    - Hanamura 8/6, Horizon 6/4, Paris 4/2, Anubis 5/5, Volskaya 9/4.
    - Dorado 3/3, Havana 3/0, Eichenwalde 3/1, Hollywood 3/2, King's Row 3/1, Blizzard World Winter 5/2.
    - Ilios Lighthouse 4/6, Ilios Well 4/6, Ilios Ruins 0/7.
    - Lijiang Control Center 2/4, Garden 3/5, Night Market 3/5.
    - Nepal Sanctum 0/5, Shrine 4/5, Village 3/6.
    - Oasis City Center 4/4, Gardens 3/3, University 6/3.
  - CTF: Busan Downtown LNY 5/1; Busan Sanctuary LNY 8/3.
  - The same page also covers the OW2 Flashpoint maps.
  - [workshop.codes "health packs locations"](https://workshop.codes/wiki/articles/health-packs-locations)
- Ilios had a missing large health pack near the third control point, fixed in the 2016-03-10 beta patch. — [Liquipedia Ilios](https://liquipedia.net/overwatch/Ilios)

**Objective geometry sources**
- OWLib DataTool `extract-map-objectives` walks every map header (type 0x9F) and its variants. Its steps:
  - Pick each placeable ENTITY whose `STUStatescriptComponentInstanceData` references graph **0x0580000000000E8E** ("common script which seems to be used by all objectives").
  - Take the area UUID from its `STUTargetTagInstanceData.m_2746D7E4`.
  - Output the matching placeable AREA's boxes (orientation quaternion, translation, extents) to `MapObjectives/Areas.json`. Spheres and capsules are not supported.
  - [OWLib ExtractMapObjectives.cs](https://github.com/overtools/OWLib/blob/546efa19516d7df7ba138802d221c73ad886df28/DataTool/ToolLogic/Extract/ExtractMapObjectives.cs)
- "Patriq" extracted the true shape and height of every control point. The original findings are at patrickszela.github.io, and Workshop code WNSY6 verifies them in-game. Temple of Anubis A is 9 m high; Anubis B reaches the skybox; bounds without a height shown extend to the map ceiling. The workshop.codes article holds only images, no numbers. — [workshop.codes "control point bounds for every map"](https://workshop.codes/wiki/articles/control-point-bounds-for-every-map), [Patriq's site](https://patrickszela.github.io/overwatch-control-point-bounds/)

### Inferences
- For an authoritative server: objective volumes, checkpoint entities and spawn-room entities all live in the map's placeable data (ENTITY + AREA placeables) of the specific map variant. Objective logic runs in statescript graph 0x0580000000000E8E plus mode graphs, so the client draws objective UI from replicated statescript state. The project's Practice mode graphs 0x13c0/0x0c8e/0x0c90 are mode-level; 0x0E8E is the objective-entity graph to study for Assault, Escort, Hybrid and Control.
- Spawn-room counts per mode: Assault 3 (A1, A2, D); Escort 6 (3 + 3); Hybrid 3 attacker + 2–3 defender; Control 2 per stage, 6 per map; Elimination and CTF 2; Deathmatch none.

### Gaps
- Full payload path lengths for Escort maps and the remaining Hybrid maps could not be retrieved: the Fandom table is reachable only through truncated search snippets. A local `extract-maps` path or spline export would give exact lengths.
- Point B tick timings beyond tick 1 were not captured.
- No public per-map list of spawn-room coordinates or door positions was found. Deltin's pathfinding editor includes a spawn-room restriction feature, but its data was not checked.

---

## 3. Public datamined identifiers (OWLib/DataTool, OverPy/Workshop) and coordinates

### Takeaway
Map header GUIDs (type 0x9F, raw prefix 0x0790) share their index with the map GUID (type 0x08xx). DataTool derives the header as `(mapGUID & 0xFFFFFFFF) | 0x0790000000000000`, which matches the project's Practice Range header 0x0790000000000688 and map 0x0800000000000688. No public table maps 0x9F header indices to map names for gameplay maps, and none was found online. OWLib's GUIDNames.csv names only menu-background headers. OverPy's Workshop `guid` values are a different identifier, almost certainly the localized name strings: Practice Range's map and game mode share 0x2BA1. Its variant ids are type-0x1C identifier GUIDs (prefix 0x0D80).

### Cited Findings

**OWLib / DataTool**
- `STUMapHeader` (STU hash 0x02514B6A, 576 bytes) holds:
  - `m_map` (0x4E87690F) and `m_baseMap` (0x38F33424);
  - `m_celebrationOverrides` (0x5FF3ACFB);
  - `m_supportedGameModes` (0xD608E9F3, array of `STUGameMode` refs);
  - variant arrays `m_D97BC44F` / `m_78715D57`;
  - `m_mapName` (0x506FA8D8, string), `m_displayName` (0x5DB91CE2), `m_overrideName` (0x1C706502);
  - `m_mapType` (0x1DD3A0CD).
  - Field offsets are from the current OW2-era generated schema; 1.74 offsets may differ.
  - [OWLib STUMapHeader.cs](https://github.com/overtools/OWLib/blob/546efa19516d7df7ba138802d221c73ad886df28/TankLib/STU/Types/STUMapHeader.cs)
- `STUMapType`: OffenseDefenseMap = 0, MirroredMap = 1, PVE = 2. — [OWLib STUMapType.cs](https://github.com/overtools/OWLib/blob/546efa19516d7df7ba138802d221c73ad886df28/TankLib/STU/Types/Enums/STUMapType.cs)
- `MapHeader.LoadFromMap`: `mapHeaderGUID = (mapGuid & ~0xFFFFFFFF00000000) | 0x0790000000000000`. A celebration variant's header is `((teResourceGUID) info.m_map).WithType(0x9F)`. The unique name is `"{name}:{Index(MapGUID):X}"`. — [OWLib MapHeader.cs](https://github.com/overtools/OWLib/blob/546efa19516d7df7ba138802d221c73ad886df28/DataTool/DataModels/MapHeader.cs)
- `list-maps` iterates `TrackedFiles[0x9F]`. For each map it prints `Name:INDEX (MapGUID)`, Name, VariantName, Desc1/Desc2, Type, States A/B and GameModes (name plus GUID). — [OWLib ListMaps.cs](https://github.com/overtools/OWLib/blob/546efa19516d7df7ba138802d221c73ad886df28/DataTool/ToolLogic/List/ListMaps.cs)
- GUIDNames.csv lists 119 type-09F entries, all "Menu/..." main-menu backgrounds plus "Underworld". Examples:
  - 664 Menu/Hanamura, 675 Menu/Gibraltar, 676 Menu/Kings Row, 677 Menu/Volskaya, 678 Menu/Hollywood.
  - 794 Menu/Horizon Lunar Colony, 801 and E6E Menu/Junkertown, 8BE Menu/Rialto, AF0 Menu/Paris, B55 Menu/Havana.
  - CFE Menu/Sydney (Lucioball), CFF Menu/Busan (Lucioball), EF3/EFA/F11/F12 Menu/Kanezaka.
  - 1018 Underworld, 112B Menu/Malevento, EF0 Menu/Hero Gallery.
  - Indices above about 0xF00 are mostly OW2.
  - GUIDNames also names map-variant celebration ids (type 0C3): 14C/1E9 Winter, 254 Halloween, 211 April Fools.
  - [OWLib GUIDNames.csv](https://github.com/overtools/OWLib/blob/546efa19516d7df7ba138802d221c73ad886df28/DataTool/Static/GUIDNames.csv)
- The project's Prometheus beta-adapter source lists STUMapHeader GUIDs used by the beta build: 0x0790…0679, 00d4, 01c2, 01d4, 01db, 02af, 02c3, 005b, 067a, 067b, 0165, 0184, 0223, 0661, 0664, 0675, 0676, 0677, 0678. Its map menu builds names from `m_mapName` plus the internal name field 0x39824653 and keys them by `m_map` id. — [prometheus/dllmain.cpp](https://github.com/p3n1cillin/ow1-preservation/blob/main/prometheus/dllmain.cpp), [prometheus/window_manager/management_window.cpp](https://github.com/p3n1cillin/ow1-preservation/blob/main/prometheus/window_manager/management_window.cpp)

**OverPy (Workshop compiler) map data**
- Each Workshop map entry has `guid`, `gamemodes`, `variants`, an optional `isSymmetrical`/`symmetryAxis` (z = a·x + b, or x = const), and localized names. — [OverPy maps.ts](https://github.com/Zezombye/overpy/blob/5a7d0e294b8cad73b9701987bb584d0551d7fa4d/src/data/maps.ts)
- OverPy `guid` values for the OW1 maps (hex), with Workshop game modes in brackets:

| Map | guid | Workshop modes |
|---|---|---|
| Hanamura | 0138 | assault, skirmish, ffa, bh, tdm |
| King's Row | 0133 | hybrid, skirmish, ffa, bh, tdm |
| Watchpoint: Gibraltar | 02E9 | escort, skirmish |
| Numbani | 02EA | hybrid, skirmish |
| Volskaya | 02EB | assault, skirmish, ffa, bh, tdm |
| Hollywood | 053D | hybrid, … |
| Dorado | 08C1 | escort, … |
| Route 66 | 11D3 | escort, skirmish, ffa, tdm |
| Nepal | 138A | control |
| Lijiang Tower | 1D22 | control |
| Ilios | 22FA | control |
| Eichenwalde | 29AF | hybrid, … |
| Practice Range | 2BA1 | practiceRange |
| Estádio das Rãs | 4629 | lucioball |
| Oasis | 46D5 | control |
| Ecopoint: Antarctica | 47D3 | elim, freezethaw, ffa, bh, tdm |
| Junkenstein's Revenge | 4AF4 | junkenstein |
| Hollywood Halloween | 4EE3 | |
| Horizon Lunar Colony | 4EEE | assault, … |
| Hanamura Winter | 5479 | |
| King's Row Winter | 547A | |
| Necropolis | 53FB | |
| Lijiang Garden | 5623 | |
| Lijiang Night Market | 5631 | |
| Lijiang Control Center | 5724 | |
| Nepal Village | 5821 | |
| Nepal Shrine | 582C | |
| Ilios Well | 583B | |
| Ilios Lighthouse | 5847 | |
| Ilios Ruins | 5851 | |
| Nepal Sanctum | 56BA | |
| Oasis City Center | 5905 | |
| Oasis Gardens | 5931 | |
| Oasis University | 593F | |
| Black Forest | 59C3 | |
| Lijiang Tower LNY | 5A33 | |
| Castillo | 5C04 | |
| Junkertown | 5D7B | escort |
| Sydney Harbour Arena Classic | 63D5 | |
| Ayutthaya | 676E | ctf, elim, freezethaw |
| Blizzard World | 6905 | hybrid, … |
| Rialto | 6906 | escort |
| Château Guillard | 69CA | ffa, bh, tdm |
| Busan | 6D90 | control |
| Eichenwalde Halloween | 6E6B | |
| Nepal Village Winter | 6E1F | yetiHunter |
| Black Forest Winter | 70F4 | |
| Ecopoint Winter | 75A7 | |
| Lijiang Garden LNY | 7EF9 | |
| Lijiang Night Market LNY | 7EFA | |
| Lijiang Control Center LNY | 7EFB | |
| Petra | 81CB | ffa, bh, tdm |
| Paris | 831E | assault, … |
| Busan Stadium Classic | 8A19 | |
| Château Guillard Halloween | 9FA4 | |
| Blizzard World Winter | A933 | |
| Temple of Anubis | AB25 | assault, … |
| Havana | B8EA | escort |
| Busan Downtown LNY | D2C9 | ctf |
| Busan Sanctuary LNY | D2CA | ctf |
| Workshop Chamber | FFF0 | |
| Workshop Island | FFF1 | |
| Workshop Expanse | FFF2 | |
| Workshop Expanse Night | 10C6D | |
| Workshop Island Night | 10C71 | |
| Kanezaka | 10D1A | ffa, bh, tdm |
| Malevento | 10DFE | ffa, bh, tdm |
| Workshop Green Screen | 11F44 | |
| Sydney Harbour Arena | 112A6 | |
| Busan Stadium | 112AA | |

  Source: [OverPy maps.ts](https://github.com/Zezombye/overpy/blob/5a7d0e294b8cad73b9701987bb584d0551d7fa4d/src/data/maps.ts)
- OverPy game-mode `guid`s: Assault CD59, Escort CD5C, Hybrid CD5A, Control 5839, CTF 5A56, Elimination 5887, Deathmatch 6853, Team Deathmatch 6854, Skirmish 5A61, Lúcioball 4989, Mei's Snowball Offensive 525A, Junkenstein's Revenge 4AF4, Practice Range 2BA1, Yeti Hunter 6DF1, Snowball Deathmatch EC7B, Bounty Hunter 12841, Freezethaw 122DF. OW2: Push 1695F, Flashpoint 12628, Clash 1A04C. The Practice Range mode has `defaultTeam1Players: 6, defaultTeam2Players: 0`. — [OverPy gamemodes.ts](https://github.com/Zezombye/overpy/blob/5a7d0e294b8cad73b9701987bb584d0551d7fa4d/src/data/gamemodes.ts)
- OverPy map variant ids are decimal u64 values. Examples:
  - 972777519512068153 "night"
  - …154 "morning"
  - …292 "sunset/evening"
  - …194 "overcast"
  - …197 "dawn"
  - …063901 "default"
  - Practice Range default: 972777519512063901
  - Workshop Chamber: …064577
  - Gibraltar default: …099996
  - [OverPy maps.ts](https://github.com/Zezombye/overpy/blob/5a7d0e294b8cad73b9701987bb584d0551d7fa4d/src/data/maps.ts)
- Recorded symmetry axes (Workshop coordinates):
  - Ecopoint, Necropolis, Oasis University, Nepal stages, Workshop Chamber/Island/Expanse: z=0 (a=0, b=0).
  - Black Forest: z=5. Ayutthaya: z=-7.
  - Castillo: z = -0.19009x + 38.79879.
  - Lijiang stages: x=0 (Night Market x=1). Ilios Ruins: x=28.6.
  - Ilios Lighthouse: z = -0.41437x + 96.86593. Ilios Well: z = 1.00409x + 192.85907.
  - Oasis City Center: z = 1.00002x + 103.99783. Oasis Gardens: z = -1.00042x - 106.1637.
  - Busan Downtown LNY: x=51.9. Busan Sanctuary LNY: x=-328.565. Busan MEKA Base (comment): z = 2.32074x - 274.76433.
  - [OverPy maps.ts](https://github.com/Zezombye/overpy/blob/5a7d0e294b8cad73b9701987bb584d0551d7fa4d/src/data/maps.ts)

**Workshop coordinates and resources**
- workshop.codes health-pack arrays give explicit Workshop coordinates for every map (see section 2). The page links to the workshop.codes API for full arrays. — [workshop.codes health packs](https://workshop.codes/wiki/articles/health-packs-locations)
- Control-point bounds images by Patriq, made with DataTool extraction and verifiable with code WNSY6. — [workshop.codes control point bounds](https://workshop.codes/wiki/articles/control-point-bounds-for-every-map)

### Inferences
- **OverPy `guid` ≠ map header index.** The Practice Range header index is 0x688 per the project, while OverPy's value is 0x2BA1. OverPy gives 0x2BA1 to both the Practice Range *map* and the Practice Range *game mode*, and 0x4AF4 to both the Junkenstein map and the Junkenstein mode. Those values are therefore the localized display-name string GUIDs (type 0x7C, the `m_displayName` targets), not 0x9F, 0xC5 or 0x08 indices. They can still be used to recognize a map header at runtime: read its `m_displayName` GUID index and match it against this table.
- **OverPy variant ids are type-0x1C identifier GUIDs.** For example 972777519512063901 = 0x0D80000000008F9D; bits 48–59 = 0xD80 = bitrev12(0x1B), giving type 0x1C. OWLib GUIDNames also uses type 01C for identifiers such as "MapNight"/"MapRaining" and celebrations. These ids are likely the time-of-day/variant identifiers in the header's variant arrays (`m_D97BC44F[i].m_A9253C68`).
- Game modes: the project already uses type-0xC5 GUIDs with prefix 0x0230 (Practice Range 0x023000000000005A, plus 0x18). OWLib `list-maps` prints each map header's supported-mode GUIDs. Running it locally against the 1.74 install is the reliable way to get the full 0x9F → 0xC5 table.
- Indices 0x664/0x675–0x678 are named "Menu/Hanamura, Gibraltar, Kings Row, Volskaya, Hollywood" in GUIDNames. Prometheus treats them as STUMapHeader GUIDs, so menu backgrounds are themselves 0x9F map headers with `m_map` set. Gameplay headers must be told apart by `m_supportedGameModes` and `m_mapType`.

### Gaps
- **No public table of gameplay map header (0x9F) or map (0x08) indices per map name was found.** Web search returned no ListMaps dumps, and GitHub code search was unavailable in this environment (API restricted). Generate the table locally with DataTool `list-maps --json` against the 1.74 CASC, or with the project's own catalogue reader.
- Workshop "Map" enum values map to these string GUIDs in OverPy, but the in-binary Workshop map table was not inspected.
- Per-map spawn-point and objective coordinates as a complete public table were not found, beyond health packs and Patriq's control-point images.

---

## 4. Practice Range specifics

### Takeaway
Public sources are thin on exact geometry. The OW1 Practice Range ("Training Facility", location debated) has no objectives. It has 4 friendly and 11 hostile Training Bots (200 HP; they fire 8-damage projectiles at 60 m/s, 4/s, from 8-round magazines with a 1 s reload) and metre range markers on the ground. Its Workshop health packs are 2 small and 2 large at known coordinates.

### Cited Findings
- "There are no objectives ... There are four friendly and eleven hostile training bots on the map that perform various actions, such as staying still, shooting, and moving. There are also range markers (in meters) on the ground." Terrain: "Industrial", type "Tutorial". Location is debated: the facility appears in *Uprising* (Swiss HQ), but a map in the Gibraltar attacker spawn suggests northern Russia. Loading-screen trivia: it shows three targets where two training bots stand in the map. — [Fandom "Practice Range", rev. 2019-01-03](https://overwatch.fandom.com/wiki/Practice_Range)
- Training bot stats: health 200. Weapon "Duo Cannons": projectile, 8 damage per projectile, 60 m/s, 4 projectiles/s, 8 ammo, 1 s reload, can headshot. Voice: Aaron Phillips. Friendly and hostile bots both exist. — [Fandom "Training Bot", rev. 2022-04-19](https://overwatch.fandom.com/wiki/Training_Bot)
- Workshop-coordinate health packs: small at (16.701, 2, 1.725) and (70.398, -2, 33.784); large at (52.232, -2, -15.778) and (73.180, -2, -7.078). — [workshop.codes health packs](https://workshop.codes/wiki/articles/health-packs-locations)
- Forum users describe the right-hand side as the area "where there are tons of bots", and say OW2's range is a direct port of OW1's. — [Blizzard forum "Aim practice. Practice range"](https://us.forums.blizzard.com/en/overwatch/t/aim-practice-practice-range/65275) (via search summary)
- Community "Practice Range 2.0" Workshop mode reuses the map with added scenarios, such as a constantly grappling Widowmaker bot. — [Blizzard Watch](https://blizzardwatch.com/2019/12/16/overwatch-practice-range-2-0/) (via search summary)
- The Workshop Practice Range mode defaults to 6 players on team 1 and 0 on team 2. — [OverPy gamemodes.ts](https://github.com/Zezombye/overpy/blob/5a7d0e294b8cad73b9701987bb584d0551d7fa4d/src/data/gamemodes.ts)
- Its default Workshop variant id is 972777519512063901, with no time-of-day variants. — [OverPy maps.ts](https://github.com/Zezombye/overpy/blob/5a7d0e294b8cad73b9701987bb584d0551d7fa4d/src/data/maps.ts)

### Inferences
- The project's own measurements are a spawn-room interior near (48.7, 6.3, 37.8), with the spawn floor at y≈2.0. The Workshop health packs at y = -2 and 2 suggest the main firing floor sits about 4 m below the spawn floor, which is consistent with a raised spawn. The project should check that its engine world coordinates match Workshop coordinates: Workshop positions are normally the engine's world positions.
- The 15 bots (4 friendly + 11 hostile) are probably placed by map placeables or Practice-mode statescript, not hardcoded server logic. Behaviours (static, shooting, moving, the friendly bots used for healing and ult charge) would come from bot definitions and graphs. Inspect the map's placeable ENTITY list and the Practice graphs rather than inventing positions.

### Gaps
- No public source found with exact bot positions, range-marker distances (the specific metre values), sniper-lane distances, moving-bot paths, ult-charge or healing dummy behaviour, or spawn door positions. The current Fandom/wiki.gg Practice Range pages, which may describe the 2019+ friendly-bot changes, could not be fetched (402/401), and the 2019 revision lacks this detail.
- The patch that introduced friendly bots (healing practice) was not verified.

---

## 5. Training/Tutorial and Play vs AI maps

### Takeaway
OW1's Tutorial is a separate tutorial map in which Athena guides the player through movement, attacks and abilities as Soldier: 76, then unlocks the Practice Range. Practice vs AI is a 6v6 against AI on a random Assault, Control, Escort or Hybrid map, with a limited bot roster and three difficulties.

### Cited Findings
- "Tutorial is the opening Play Mode of Overwatch ... Athena guides the player through hero movement, attacks, and abilities, using the hero Soldier: 76. Upon completion of the tutorial proper, players gain access to a more open-ended tutorial map in the form of the Practice Range." — [Fandom "Tutorial", rev. 2020-09-20](https://overwatch.fandom.com/wiki/Tutorial)
- Fandom lists Practice Range and Tutorial under "Other maps ... used for learning the game. In them, there are training bots." — [Fandom "Map", rev. 2022-09-23](https://overwatch.fandom.com/wiki/Map)
- Practice vs AI (OW1):
  - 6 players versus an AI team, found under Training.
  - Difficulty Easy/Medium/Hard, dealing 25%/50%/100% damage; bots cannot headshot.
  - AI heroes: Roadhog, Zarya, Bastion, Cassidy, Mei, Reaper, Soldier: 76, Sombra, Torbjörn, Ana, Lúcio, Zenyatta.
  - Mode chosen at random from Assault, Control, Escort and Hybrid.
  - Always 90% XP.
  - [Fandom "Practice vs. AI", rev. 2022-03-09](https://overwatch.fandom.com/wiki/Practice_vs._AI)
- OW2 changed Practice vs AI to 5v5 with a 1-2-2 AI composition, and its tutorial is Tracer and Athena with Soldier: 76. These are OW2 facts, not OW1. — search summaries of [Fandom "Practice vs. AI"](https://overwatch.fandom.com/wiki/Practice_vs._AI) (current)

### Inferences
- OW1 has no AI-specific maps. Practice vs AI reuses standard Assault, Control, Escort and Hybrid maps, so supporting it needs bot navigation on those maps; Arcade maps are not involved. The Tutorial is a distinct map whose header id was not found publicly (see the gap below).

### Gaps
- The Tutorial map's name, location and header GUID were not identified in public sources. GUIDNames has no tutorial entry, and the OW1-era Fandom "Training" page had no pre-2022-09-30 revision available through the API. A local `list-maps` run would show it.
- The exact maps excluded from Practice vs AI were not found: whether every Assault, Control, Escort and Hybrid map supported AI navmeshes in OW1, and whether newer maps such as Paris, Havana or Busan were eligible.
