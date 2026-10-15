# Overwatch 1 game modes: complete rules and match flow (final OW1 state, build 1.74.x, mid/late 2022)

Source notes (applies to everything below):
- **Official patch notes archive.** Blizzard's archive at `https://overwatch.blizzard.com/en-us/news/patch-notes/live/YYYY/MM/` still serves every OW1 live patch from 2016-05 to 2022-09. It is the primary, dated source for rule changes, and each monthly page was downloaded and searched. Citations use the month URL and the patch date.
- **Fandom wiki at the OW1 date.** Overwatch Fandom pages were read through the MediaWiki API, pinned to the **last revision before 2022-10-03**, which is the OW1 state of the wiki. Citations use `?oldid=` links. Where a page only exists in a later (OW2-era) revision, it is cited as "current revision", and any OW2-only values are flagged.
- **Pages that could not be fetched.** overwatch.wiki.gg (401/403), Liquipedia (403/429) and web.archive.org (connection reset) were all blocked. OWL rulebook PDFs and workshop.codes were not reached.
- **Uneven wiki coverage.** OW1-era wiki pages are thin for some modes, so some numbers come from OW2-era pages that describe historical OW1 mechanics. Each such case is marked.

---

## 1. Match phases and timers (hero select, setup, spawn doors, respawn, spawn room, hero swap, overtime, sudden death, end of match, POTG, cards, endorsements, leaving/backfill)

### Takeaway
A standard OW1 attack/defense round runs in this order:
1. "Assemble Your Team" hero select: 30 s at match start since March 2020; 25 s before the second round since October 2018.
2. Setup: 45 s since October 2018, previously 60 s. Defenders may leave spawn; attackers are held behind the spawn doors.
3. The round timer starts when the doors open.

Base respawn is 10 s. Overtime adds 2–3 s; the patch note says 2 s and the wiki says 3 s. The attacker-advantage system can add up to +5 s to defenders, for a maximum of 18 s.

Overtime starts if an attacker touches the objective within the last 3 s of the clock. Its fuse burns faster once overtime has lasted more than 20 s. Competitive "Sudden Death" existed only in Season 1 (June–Sept 2016) and was replaced by draws and the time bank in Season 2. The match ends with Play of the Game (Play of the Match in Competitive), then cards/voting, endorsements, and return-to-lobby or requeue.

### Cited Findings

**Hero select ("Assemble Your Team" / "Assemble Heroes") and setup**
- **Oct 9, 2018:** "Reduced the setup timer for Assault, Escort, and Assault/Escort maps from 1 minute to 45 seconds." The same patch: "Assemble Your Team timer increased from 10 to 25 seconds in the second round on Assault, Assault/Escort, and Escort maps" — [Patch notes Oct 2018](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2018/10/)
- **Feb 2020:** "The initial Assemble Heroes timer for games using the Assault, Hybrid, Control, and Payload game modes has been reduced from 40 to 35 seconds" — [Patch notes Feb 2020](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2020/02/)
- **Mar 2020:** The same timer was "further reduced from 35 to 30 seconds". This is the final OW1 value — [Patch notes Mar 2020](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2020/03/)
- **Setup phase (OW1 wiki):** At the start of each round the defending team is given setup time before attackers may leave spawn — [Assault (OW1 rev)](https://overwatch.fandom.com/wiki/Assault?oldid=123635); [Escort (OW1 rev)](https://overwatch.fandom.com/wiki/Escort?oldid=125449)
- **OW2-era Escort page:** It states setup is 45 s, consistent with the Oct 2018 patch — [Escort (current revision)](https://overwatch.fandom.com/wiki/Escort)
- **Mystery Heroes, Sept 2017:** "Players will no longer see the Assemble Your Team screen at the beginning of a game" — [Patch notes Sept 2017](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2017/09/)
- **Elimination hero selection:** The custom-game default is 20 s, settable up to 60 s (custom-game settings list; current revision, but the option dates from OW1) — [Custom Game (current revision)](https://overwatch.fandom.com/wiki/Custom_Game)
- **Skin selection:** Added to the Hero Select screen at match start on Feb 7, 2018 — [Patch notes Feb 2018](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2018/02/)
- **Hero Select during loading:** A Feb 2018 bug fix stopped players using the Hero Select screen during the loading screen, so hero select starts after loading — [Patch notes Feb 2018](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2018/02/)

**Respawn**
- **Base respawn is 10 s.** OW1 wiki: "It takes 10 seconds to respawn after you have been killed. Overtime increases the respawn timer by 3.0 seconds." — [Respawn (OW1 rev 2020)](https://overwatch.fandom.com/wiki/Respawn?oldid=117428)
- **Conflicting overtime penalty.** The patch of July 19, 2016 says "Players now respawn more slowly during Overtime (increased spawn time by 2 seconds)" — [Patch notes July 2016](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2016/07/). This conflicts with the wiki's +3 s; the actual value may have been changed later without a note.
- **Defender respawn standardized, Aug 2016:** "Respawn time for defenders has been standardized to 10 seconds on all maps" — [Patch notes Aug 2016](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2016/08/)
- **Attacker-advantage respawn delay**
  - **Added Feb 2017:** "When attackers outnumber defenders while taking a control point on Assault, Escort and Assault/Escort maps, the defenders' respawn time will slowly increase until it hits a maximum value or the defense manages to gain the upper hand." — [Patch notes Feb 2017](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2017/02/)
  - **Aug 2017:** The delay now ramps earlier — [Patch notes Aug 2017](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2017/08/)
  - **July 2018:** It ramps "even faster" on final objectives — [Patch notes July 2018](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2018/07/)
  - **Numbers:** The ramp starts once the attacker-advantage timer exceeds 10 s and reaches +5.0 s at about 33 s. The timer counts back down if the advantage is not kept. It stacks with the overtime delay, for a maximum of 18 s — [Respawn (OW1 rev)](https://overwatch.fandom.com/wiki/Respawn?oldid=117428). The OW2-era page confirms this "attacker advantage timer" was removed in OW2 — [Respawn (current)](https://overwatch.fandom.com/wiki/Respawn)
- **Assault defender respawn after losing A, June 2019:** "Upon losing Point A, any defenders that are dead, or that die shortly thereafter, will have a maximum respawn of 3.5 seconds." — [Patch notes June 2019](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2019/06/)
- **Group respawn (OW1 non-competitive modes)**
  - When a player is eliminated and their timer is within 5 s of a previously eliminated teammate's remaining timer, all affected timers are averaged.
  - Example: 10 s and 6 s become 8 s each. Groups can chain.
  - It does not apply during overtime.
  - It was replaced by Wave Respawn in OW2 Season 12, which also raised the base respawn to 12 s. **OW2 only; do not use for OW1** — [Respawn (current revision, History section)](https://overwatch.fandom.com/wiki/Respawn)
- **Deathmatch respawn:** The timer can be skipped at the 3 s mark by pressing Jump. Spawns are fixed points chosen relative to other players' positions — [Respawn (OW1 rev)](https://overwatch.fandom.com/wiki/Respawn?oldid=117428)

**Spawn room**
- **OW1-era wiki:** Each spawn room has a healing zone and a barrier. Enemies inside an enemy spawn's healing zone take damage until they die, and this is not shown as environmental damage — [Spawn Room (OW1 rev)](https://overwatch.fandom.com/wiki/Spawn_Room?oldid=121624)
- **OW2-era page, likely carried over from OW1 but unverified:**
  - Heroes in spawn heal at 400 HP/s, are invulnerable, and may swap heroes.
  - Intruders take 400 HP/s, counted as self-damage, so it gives no ult charge.
  - When a spawn moves, the old spawn stays partially active for 7 s: healing stays on, doors stay locked to enemies, hero swap is disabled, and Interact teleports to the new spawn.
  - In Assault, the attacker spawn moves forward after A is captured; defenders always spawn behind B. In Escort/Hybrid, both spawns move at each checkpoint.
  - [Spawn Room (current revision)](https://overwatch.fandom.com/wiki/Spawn_Room)
- **Hero swap:** Allowed in the spawn room. The custom-game option "Allow hero switching" defaults to Enabled — [Custom Game (current revision)](https://overwatch.fandom.com/wiki/Custom_Game). In Role Queue, players may only pick heroes of their queued role for the whole match — [Competitive Play (OW1 rev)](https://overwatch.fandom.com/wiki/Competitive_Play?oldid=128194)

**Overtime**
- **OW1 wiki:** Overtime is awarded when an attacker touches the objective with 3 s left. While an attacker is on the objective the bar is reset to full and does not deplete. After more than 20 s of overtime, the fuse depletes increasingly quickly. Respawn is +3 s in overtime — [Overtime (OW1 rev 2020)](https://overwatch.fandom.com/wiki/Overtime?oldid=115974)
- **Patch of July 19, 2016:** "If a match goes into Overtime for more than 20 seconds, the fuse will now start to 'burn down' more quickly" — [Patch notes July 2016](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2016/07/)
- **Exact fuse lengths (OW2-era page, mechanics likely inherited from OW1):** The fuse is 5 s and resets while any attacker is on the objective. After 20 s of overtime it becomes 3 s; after 30 s it becomes 1.5 s. There is no hard cap.
- **Control overtime window:** In Control the check happens at 99%, giving a 4.2 s window. Capturing the point counts as a contest by the team losing it, so retaking at 99% triggers overtime.
- **OW2-specific values on that page:** Respawn of 14 s in overtime and Wave Respawn disabled are OW2 values.
- Source for the three points above: [Overtime (current revision)](https://overwatch.fandom.com/wiki/Overtime)
- **Escort overtime:** If attackers reach an intermediate checkpoint during overtime, the time is added and overtime ends — [Escort (OW1 rev)](https://overwatch.fandom.com/wiki/Escort?oldid=125449)
- **Assault overtime:** If A is captured in overtime, play continues with the time added for B (3 min) — [Assault (OW1 rev)](https://overwatch.fandom.com/wiki/Assault?oldid=123635)

**Sudden Death (Competitive Season 1 only)**
- **Season 1 format:** If both teams completed the map, one abbreviated round was played. Attackers were chosen by coin flip and had to take the first point or checkpoint within a time limit — [Sudden Death (current revision)](https://overwatch.fandom.com/wiki/Sudden_Death); [Competitive Play (OW1 rev)](https://overwatch.fandom.com/wiki/Competitive_Play?oldid=128194)
- **Duration changed July 2016** from a uniform 1m45s to per-map values (Hollywood stayed at 1m45s) — [Patch notes July 2016](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2016/07/):

  | Mode | Map | Sudden Death time |
  |---|---|---|
  | Assault | Hanamura | 1m35s |
  | Assault | Temple of Anubis | 1m30s |
  | Assault | Volskaya Industries | 1m35s |
  | Escort | Dorado | 1m30s |
  | Escort | Route 66 | 1m35s |
  | Escort | Watchpoint: Gibraltar | 1m35s (second checkpoint, per the wiki) |
  | Hybrid | King's Row | 1m30s |
  | Hybrid | Numbani | 1m50s |
  | Hybrid | Hollywood | 1m45s (unchanged) |

- **Removed Sept 2, 2016 (Season 2):** "Instead of going into sudden death, tied competitive matches will now result in a draw" — [Patch notes Sept 2016](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2016/09/)
- **Capture the Flag:** CTF has its own Sudden Death, added 2018 (see Section 7).

**End of match: Play of the Game, cards, endorsements**
- **POTG:** Shown at the end of every match from the perspective of the selected player. In Competitive, a "Play of the Match" variant covered all rounds. Categories: High Score, Lifesaver, Shutdown, Sharpshooter — [Play of the Game (OW1 rev)](https://overwatch.fandom.com/wiki/Play_of_the_Game?oldid=124458)
- **POTG timing (OW2-era page, unverified for OW1):** 5 s highlight intro plus 12 s of gameplay, 17 s total. A player who quits before the end cannot get POTG — [Play of the Game (current revision)](https://overwatch.fandom.com/wiki/Play_of_the_Game)
- **End-of-match card voting existed in OW1.** A Feb 2018 fix "prevented bots from voting on cards at the end of the match on Hybrid and Control maps" — [Patch notes Feb 2018](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2018/02/)
- **Endorsements (added June 2018):**
  - Three types: Shot Caller and Good Teammate (teammates only), Sportsmanship (teammates or enemies).
  - A player can endorse 3 players per match, earning 50 XP for each endorsement given.
  - The same player can only be endorsed again after 12 hours.
  - Endorsement levels run 1–5 and can decay.
  - Sources: [Patch notes June 2018](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2018/06/); [Endorsements (OW1 rev)](https://overwatch.fandom.com/wiki/Endorsements?oldid=120339)
- **Aug 2019:** Endorsements extended to Mystery Heroes, No Limits, Deathmatch, Total Mayhem and Low Grav — [Patch notes Aug 2019](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2019/08/)

**Leaving and backfill**
- **Quick Play:** Leavers are backfilled. Repeated early leaving gives a −75% XP penalty on later matches, cleared by finishing matches — [Unranked/Quick Play (OW1 rev)](https://overwatch.fandom.com/wiki/Quick_Play?oldid=119861)
- **Competitive leavers:** They cannot join any other game until the match ends and are **not backfilled**. If they fail to rejoin, they automatically lose 50 SR and receive an escalating suspension, up to a season ban — [Competitive Play (OW1 rev)](https://overwatch.fandom.com/wiki/Competitive_Play?oldid=128194)
- **Competitive leaver rule changes by date:**
  - **July 2016:** Leaving a single match more than 3 times gives a leave penalty even if the match is completed. Leaving without rejoining counts as a loss — [Patch notes July 2016](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2016/07/)
  - **Aug 2016:** A leaver waits at least 10 min before the next competitive match — [Patch notes Aug 2016](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2016/08/)
  - **Oct 2016:** Rejoin is allowed any time while the match is in progress. Teammates of a disconnected player may exit after **2 minutes** (formerly 1) with no leaver penalty, but receive a loss — [Patch notes Oct 2016](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2016/10/)
  - **Sept 2020:** "Penalties are now more severe and will lead to a season ban more quickly" — [Patch notes Sept 2020](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2020/09/)
- **Priority requeue:**
  - **June 2020:** Granted after a competitive game "collapses" due to a leaver — [Patch notes June 2020](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2020/06/)
  - **Aug 2020:** Granted after finishing a game you backfilled into — [Patch notes Aug 2020](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2020/08/)
- **Deathmatch AFK timer:** Increased from 60 to 120 s in June 2018 — [Patch notes June 2018](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2018/06/)
- **Return to lobby (custom-game options):**
  - Map Rotation: default after a mirror match, or after a game, or paused.
  - Return to Lobby: default after a mirror match, or after a game, or never.
  - Team balancing: off, after a mirror match, or after a game.
  - Swap teams after match: default no.
  - Source: [Custom Game (current revision)](https://overwatch.fandom.com/wiki/Custom_Game)

### Inferences
- A server-side match state machine for standard modes needs these phases: LoadIn → AssembleHeroes (30 s; 25 s for round 2 of attack/defense maps) → Setup (45 s, defenders free, attacker doors closed) → InProgress (round clock) → [Overtime] → RoundEnd → (side swap in Competitive or Control rounds) → MatchEnd → POTG/POTM (~17 s) → cards/endorsements → lobby/requeue.
- The 2 s versus 3 s overtime respawn conflict is unresolved; +3 s matches the later wiki and common recollection. Treat the 10 s base and the 18 s maximum (10 + 5 + 3) as the documented OW1 numbers.
- The 400 HP/s spawn healing and the 7 s stranded-spawn rule come from an OW2 page. They probably predate OW2, but no OW1 citation was found.

### Gaps
- No primary source gives the OW1 Control "Assemble Heroes" time between rounds.
- The exact OW1 attacker-advantage formula (ramp curve), and how much "even faster" sped it up in July 2018, were not found.
- The OW1 POTG intro/clip lengths, the card-voting time and the end-of-match screen durations were not found in OW1-dated sources.
- The OW1 spawn-room heal rate and intruder damage per second are only documented on an OW2-era page.

---

## 2. Assault (2CP)

### Takeaway
- **Timer:** Attackers get 4:00 for point A. Capturing A adds 3:00, a change made in June 2019 (previously 4:00). Quick Play Assault was cut from 5:00 to 4:00 per point in July 2018.
- **Capture rates:** Speed scales with up to 3 attackers. Point A takes 30/20/15 s and point B takes 18/12/10 s for 1/2/3 attackers.
- **Ticks:** Progress is split into three ticks (33/66/100%) that act as checkpoints; progress only falls back to the last completed tick.
- **Contest:** Any defender on the point freezes capture.
- **Competitive:** Two rounds plus time-bank extra rounds. Progress must reach at least 33.3% to count for tiebreaks.

### Cited Findings
- **Capture rule:** "Whenever there are one or more attackers in the capture area with no defenders present, the capture progress goes up. Capture time speeds up to 3 players." The bar has 3 equal ticks that act as checkpoints; with no attackers present, progress "only falls back to the last tick" — [Assault (OW1 rev)](https://overwatch.fandom.com/wiki/Assault?oldid=123635)
- **Seconds to capture by number of attackers** — [Assault (OW1 rev)](https://overwatch.fandom.com/wiki/Assault?oldid=123635):

  | Point | Progress | 1 attacker | 2 attackers | 3+ attackers |
  |---|---|---|---|---|
  | A | 1 tick | 10 | 7 | 5 |
  | A | 2 ticks | 20 | 13 | 10 |
  | A | 3 ticks | 30 | 20 | 15 |
  | B | 1 tick | 6 | 4 | 3 |
  | B | 2 ticks | 12 | 8 | 6 |
  | B | 3 ticks | 18 | 12 | 10 |

- **Time:** "The attacking team always has 4 initial minutes to capture point A. If they succeed, 3 more minutes will be added to capture point B. If point A is captured in Overtime, the game will continue normally with 3 minutes on the clock." — [Assault (OW1 rev)](https://overwatch.fandom.com/wiki/Assault?oldid=123635)
- **Time changes by date:**
  - **June 2019:** "Time awarded for capturing Point A on all Assault maps has been reduced from 4 minutes to 3 minutes", shortening the round from 8 to 7 minutes — [Patch notes June 2019](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2019/06/)
  - **July 2018:** "Objective time reduced from 5 minutes to 4 minutes per control point in Quick Play and Arcade modes" — [Patch notes July 2018](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2018/07/)
  - **Sept 2016:** Competitive time for taking objectives on Hanamura, Temple of Anubis and Volskaya was reduced from 5 to 4 minutes — [Patch notes Sept 2016](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2016/09/)
- **Maps (final OW1):** Hanamura, Horizon Lunar Colony, Paris, Temple of Anubis, Volskaya Industries — [Game Modes (OW1 rev)](https://overwatch.fandom.com/wiki/Game_Modes?oldid=124830). Horizon and Paris were removed from Competitive on April 14, 2020 — [Competitive Play (OW1 rev)](https://overwatch.fandom.com/wiki/Competitive_Play?oldid=128194)
- **Spawns:** Defenders always spawn behind B; the attacker spawn moves forward after A — [Assault (OW1 rev)](https://overwatch.fandom.com/wiki/Assault?oldid=123635)
- **Capture HUD, Oct 2017:** The progress bar was "broken into three segments" with animation and audio cues, and the HUD shows the number of defenders as well as attackers on the point — [Patch notes Oct 2017](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2017/10/)
- **Invisible players, July 2018:** Sombra "No longer can contest objectives while invisible" — [Patch notes July 2018](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2018/07/)
- **Defender respawn after A falls:** Capped at 3.5 s (June 2019) — [Patch notes June 2019](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2019/06/)
- **Experimental rework (not shipped):** A July 30, 2020 Experimental card tested a reworked Assault: 6-minute banks, points scored per capture, 8 s attacker and 11.5 s defender respawn. Blizzard called it "the failed experiment" and it never became the live rule — [Assault (current revision)](https://overwatch.fandom.com/wiki/Assault)
- **OW2:** Assault maps were removed from all playlists on Oct 4, 2022 and kept only in Custom Games — [Patch notes Oct 2022](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2022/10/)

### Inferences
- Capture-rate multipliers implied by the table are 1 : 1.5 : 2 for 1/2/3 attackers. Point A base rate is 1/30 per second; point B base rate is 1/18 per second.
- B ticks at 3/6/10 s with 3 players are not exactly linear, probably because of rounding in the source data.
- The decay speed back to the last tick, and any delay before decay starts, are not documented. These need native tracing or video measurement.

### Gaps
- The rate at which progress decays toward the last tick, and whether defenders standing on the point speed it up, were not found.
- Whether the "capture speed" table applies uniformly to all five Assault maps or varies per map was not found.

---

## 3. Escort (payload)

### Takeaway
**Payload movement:**
- Payload speed is map-specific. The base is 1.4–1.7 m/s for one pusher, with 2 pushers giving +16.5% and 3+ giving +33%.
- Any defender in range stops it.
- After 10 s with no attackers nearby it rolls back toward the last checkpoint.
- Attackers near it are healed at 10 HP/s in OW1; OW2 reduced this to 5 HP/s.

**Time:**
- Competitive initial time is 4:00 since Sept 2016 (previously 5:00).
- Checkpoint time additions are per map and are not fully documented. Example: Route 66 Competitive got an extra 60 s at checkpoint 1 in March 2017.

### Cited Findings
- **Payload behaviour:** An attacker in range moves the payload. It rolls back "towards the last checkpoint if no attacking players are near it for ten seconds." Defenders in range contest it and stop it moving. "Attackers within range of the payload are healed at a rate of 10 health per second." — [Escort (OW1 rev)](https://overwatch.fandom.com/wiki/Escort?oldid=125449)
- **Payload speed (m/s)** — [Escort (OW1 rev)](https://overwatch.fandom.com/wiki/Escort?oldid=125449):

  | Map | 1 pusher | 2 pushers | 3+ pushers |
  |---|---|---|---|
  | Havana | 1.4 | 1.65 | 1.85 |
  | Route 66 | 1.4 | 1.65 | 1.85 |
  | Junkertown | 1.55 | 1.8 | 2.05 |
  | Dorado | 1.55 | 1.8 | 2.05 |
  | Watchpoint: Gibraltar | 1.7 | 2.0 | 2.25 |
  | Rialto | 1.7 | 2.0 | 2.25 |

  Formula: 1 pusher = 100%, 2 = 116.5%, 3 = 133%.
- **Speed tuning patches:**
  - **Aug 2016:** Gibraltar payload speed "slightly reduced" — [Patch notes Aug 2016](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2016/08/)
  - **Sept 2016:** Eichenwalde payload speed increased — [Patch notes Sept 2016](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2016/09/)
  - **Sept 2018:** Rialto payload travel speed "slightly increased" and its checkpoint pause time reduced — [Patch notes Sept 2018](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2018/09/)
- **Time:**
  - **Sept 2016 (Competitive):** Time for taking objectives on Dorado, Route 66, Watchpoint: Gibraltar, Hollywood, King's Row and Numbani was reduced from 5 minutes to 4 — [Patch notes Sept 2016](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2016/09/)
  - **Mar 2017 (Competitive):** "On Route 66, the attacking team is now given 60 additional seconds after pushing the payload to the first checkpoint." — [Patch notes Mar 2017](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2017/03/)
- **OW2 timers (do not use as OW1 values):** The OW2-era page gives a 4:00 start (5:00 in Unranked), +2:30 and +1:30 at checkpoints (3:00 and 2:00 Unranked), 5 HP/s payload healing, and a 0.3 m/s rollback speed. It also notes healing "was reduced from 10 to 5" at an unknown time, which matches the OW1 page's 10 HP/s — [Escort (current revision)](https://overwatch.fandom.com/wiki/Escort)
- **Overtime:** Triggered if an attacker is within payload range when, or shortly before, the timer expires. Reaching a checkpoint during overtime adds time and ends overtime — [Escort (OW1 rev)](https://overwatch.fandom.com/wiki/Escort?oldid=125449)
- **Maps (final OW1):** Dorado, Havana, Junkertown, Rialto, Route 66, Watchpoint: Gibraltar. Circuit Royal was OW2-beta only — [Game Modes (OW1 rev)](https://overwatch.fandom.com/wiki/Game_Modes?oldid=124830)
- **Forced movement:** Some sections move the payload as if 3 attackers were pushing, and it cannot be stopped there (OW2-era page; geometry inherited from OW1 maps) — [Escort (current revision)](https://overwatch.fandom.com/wiki/Escort)
- **King's Row starting position, July 2016:** The payload no longer retreats inside its starting location if attackers fail to push — [Patch notes July 2016](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2016/07/)

### Inferences
- Escort Quick Play times probably match Competitive (4:00 start) after the 2016 standardization, but no OW1 source confirms the QP-specific initial time or per-map checkpoint additions. The OW2 "Unranked 5:00 / +3:00 / +2:00" values must not be assumed for OW1.
- The rollback speed in OW1 is undocumented; 0.3 m/s comes from an OW2 page.

### Gaps
- Per-map OW1 checkpoint time additions for each Escort/Hybrid map in final OW1 (Dorado, Havana, Junkertown, Rialto, Route 66, Gibraltar) were not found in reachable sources. The likely sources are the blocked OW1 wiki.gg / Liquipedia map pages or native map data.
- The pause duration at checkpoints was not found.
- The radius of the payload capture area was not found.

---

## 4. Hybrid

### Takeaway
Hybrid is an Assault point A (1p/2p/3p: 32/21/15 s for three ticks) followed by Escort rules. It uses the same 1/1.165/1.33 payload multipliers, 10 HP/s healing near the payload, and the 10 s rollback.

### Cited Findings
- **Point A capture (seconds, 1/2/3 attackers):** Tick 1 = 11/7/5, Tick 2 = 21/14/10, Tick 3 = 32/21/15. Capture is capped at 3x speed even though the HUD shows up to 6 — [Hybrid (OW1 rev)](https://overwatch.fandom.com/wiki/Hybrid?oldid=125447)
- **Payload speeds (m/s, 1/2/3 pushers)** — [Hybrid (OW1 rev)](https://overwatch.fandom.com/wiki/Hybrid?oldid=125447):

  | Map | 1 pusher | 2 pushers | 3+ pushers |
  |---|---|---|---|
  | Hollywood | 1.55 | 1.8 | 2.05 |
  | King's Row | 1.55 | 1.8 | 2.05 |
  | Numbani | 1.55 | 1.8 | 2.05 |
  | Blizzard World | 1.7 | 2.0 | 2.25 |
  | Eichenwalde | 1.7 | 2.0 | 2.25 |

  The payload becomes pushable only after point A is captured; rollback after 10 s; 10 HP/s healing.
- **Maps (final OW1):** Blizzard World, Eichenwalde, Hollywood, King's Row, Numbani. Midtown and Paraíso were OW2 beta — [Hybrid (OW1 rev)](https://overwatch.fandom.com/wiki/Hybrid?oldid=125447)
- **Blizzard World:** Added Jan 2018 and disabled in Competitive until Season 9 — [Patch notes Jan 2018](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2018/01/)

### Gaps
- Hybrid initial time and checkpoint time additions per map in OW1 were not found. Sept 2016 says the Competitive objective time on Hollywood, King's Row and Numbani went from 5 to 4 min.

---

## 5. Control

### Takeaway
- **Format:** Best-of-3 in both QP and Competitive. Competitive was best-of-5 until the end of Season 5 (Aug 2017).
- **Unlock:** The point unlocks 30 s after the round starts.
- **Capture:** Takes 8/5/4 s with 1/2/3+ players. Any enemy on the point blocks it.
- **Scoring:** The owning team's percentage rises 1% every 1.2 s.
- **99% rule:** At 99% the team can only win if the enemy is not contesting; contact at or near 99% triggers overtime.
- **Map sections:** Three sections per map, chosen randomly for each round. In the old Bo5 format the order was shuffled again after round 3.

### Cited Findings
- **Round rules:** "Once the match has started and both teams have left the spawn, the control point takes 30 seconds to unlock." "The objective score will progress 1% every 1.2 seconds in favor of the team controlling the point. The round is won once one team reaches 100%. If a member of the non-controlling team touches the point when the score hits 99% or shortly before, Overtime will be activated. The first team to win two rounds wins the match." — [Control (OW1 rev)](https://overwatch.fandom.com/wiki/Control?oldid=121392)
- **Capture time (s) for 1/2/3+ players:** 8/5/4 — [Control (OW1 rev)](https://overwatch.fandom.com/wiki/Control?oldid=121392)
- **Bo5 history:** Competitive Control was Bo5 until the end of Season 5. Map sectors were randomized for the first three rounds, then reshuffled so each sector appeared at least once. It became Bo3 from Season 6 (Sept 2017) — [Control (OW1 rev)](https://overwatch.fandom.com/wiki/Control?oldid=121392); [Competitive Play (OW1 rev)](https://overwatch.fandom.com/wiki/Competitive_Play?oldid=128194)
- **No round clock:** "This game mode does not have a time limit" — [Game Modes (OW1 rev)](https://overwatch.fandom.com/wiki/Game_Modes?oldid=124830)
- **Maps and sections:**
  - Nepal: Village, Shrine, Sanctum
  - Lijiang Tower: Night Market, Garden, Control Center
  - Ilios: Lighthouse, Ruins, Well
  - Oasis: City Center, Gardens, University
  - Busan: Downtown, Sanctuary, MEKA Base
  - Source: [Control (OW1 rev)](https://overwatch.fandom.com/wiki/Control?oldid=121392)
- **Overtime window (OW2-era page; mechanics likely from OW1):** Checked at 99%, giving a 4.2 s window (about 96.5%). A team losing control is counted as contesting. The page also records an OW2 bug, fixed Dec 6, 2022, where retaking at 99% skipped overtime — [Overtime (current revision)](https://overwatch.fandom.com/wiki/Overtime)
- **Mystery Heroes on Control, Aug 2019:** Heroes are reset between rounds — [Patch notes Aug 2019](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2019/08/)
- **Custom-game Control options** (current revision listing; options existed in OW1) — [Custom Game (current revision)](https://overwatch.fandom.com/wiki/Custom_Game):
  - Capture speed modifier: default 100%, range 0–500%
  - Scoring speed modifier: default 100%, range 0–500%
  - Score to win: default 2, options 1–3
  - Limit valid control points: All / First / Second / Third
  - Competitive rules: on/off

### Inferences
- With no contest, 100% takes 120 s of continuous ownership (1% per 1.2 s).
- Capture rate multipliers are about 1 : 1.6 : 2 (8/5/4 s).

### Gaps
- Whether a partially captured point decays while uncontested in Control was not found.
- Whether the 30 s unlock also applies to rounds 2 and 3, and the between-round "Assemble" time, were not found.

---

## 6. Competitive Play specifics (OW1, Seasons 1–36)

### Takeaway
- **Matches:** 6v6, two-sided rounds, best-of-3 Control, and time-bank extra rounds on Assault/Escort/Hybrid. Draws are possible.
- **Tiebreak:** At least 33.3% capture progress is needed to break ties on Assault and Hybrid point A.
- **Queues:** Role Queue 2/2/2 started with the Role Queue beta on Aug 13, 2019 and became official in Season 18 (Sept 3, 2019). Competitive Open Queue was re-added as a separate queue in Season 23 (July 2020).
- **Rank:** SR runs 1–5000 (1–100 in Season 1). Placements are 5 per role in RQ and 10 in OQ.
- **Rewards:** 15 competitive points for a win, 5 for a draw.

### Cited Findings
- **Escort scoring:** The farther push wins. An equal distance, or no movement by either team, is a draw. The best distance counts even if the payload later rolls back. If both teams complete the map, extra rounds use the time bank — [Competitive Play (OW1 rev)](https://overwatch.fandom.com/wiki/Competitive_Play?oldid=128194)
- **Assault scoring:** More points captured, or more progress, wins. If the first attacker did not fully capture but reached at least 33.3%, the second must exceed it. If neither team reaches 33.3% on the same point, or both reach an exact equal percentage below 100%, it is a draw — same source.
- **Hybrid scoring:** Analogous. A draw results if neither team reaches 33.3% on point A or moves the payload, or if both are exactly equal — same source.
- **Tiebreak history:** The progress-tracking tiebreak for Assault/Hybrid was added April 11, 2017 with a 1% threshold. Late April 2017 raised it to 33% — [Patch notes Apr 2017](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2017/04/)
- **Escort/Hybrid time bank** (when both teams complete) — [Competitive Play (OW1 rev)](https://overwatch.fandom.com/wiki/Competitive_Play?oldid=128194):
  - Both teams ≥120 s: the lower bank is reduced to 120 s and the other is reduced by the same amount.
  - Both 60–119 s: no change.
  - A team below 60 s while the other has ≥60 s (or both below 60 s): the lower bank is raised to 60 s and the other gets the same increment.
  - The team with less time attacks first in the new rotation.
  - No time is added at checkpoints in extra rounds.
- **Assault/Hybrid extras** — same source:
  - A team with 0 s while the other has ≥60 s: only the other team attacks. It wins with at least 33.3% progress on the first point; otherwise the match is a draw.
  - Both teams at 0 s: both get 60 s.
  - In Assault extra rounds, capturing point A adds only **30 s**.
  - In Hybrid extra rounds, nothing is added at checkpoints.
- **Mar 2020 change:** "when both teams complete a round of offense and have more than 2 minutes of time bank then each team's time bank is equally reduced until one of the teams has a 2 minutes remaining". Example: 4:37 and 2:50 become 3:47 and 2:00 — [Patch notes Mar 2020](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2020/03/)
- **Time bank history:** Added to Dorado, Hollywood, King's Row, Numbani, Route 66 and Gibraltar, and refined on the Assault maps, in Season 2 (Sept 2016) — [Patch notes Sept 2016](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2016/09/)
- **Hero limit:** "Competitive Play matches can now only have one of each hero per team" (July 2016) — [Patch notes July 2016](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2016/07/)
- **Role Queue:**
  - Teams are "two tanks, two supports, and two damage heroes". Players pick their role before queuing and choose heroes only within it — [Patch notes Aug 2019](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2019/08/)
  - Season 17 ended early (Aug 13, 2019) for a Role Queue beta. Season 18 (Sept 3, 2019) made it official, with placements cut from 10 to 5 per role. Open Queue returned as a separate queue in Season 23 (July 2, 2020) — [Competitive Play (OW1 rev)](https://overwatch.fandom.com/wiki/Competitive_Play?oldid=128194)
  - Party Flex (Jan 2020): party members may select multiple roles — [Patch notes Jan 2020](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2020/01/)
  - Open Queue Competitive (June 2020) has its own SR and leaderboard — [Patch notes June 2020](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2020/06/)
- **Map and hero pools:**
  - Map pools started in Season 19 (Nov 2019) with 12 maps, 3 per mode — [Patch notes Nov 2019](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2019/11/). They were removed Apr 14, 2020 — [Competitive Play (OW1 rev)](https://overwatch.fandom.com/wiki/Competitive_Play?oldid=128194)
  - Hero pools/bans ran in Seasons 21–22 and were removed June 8, 2020 — [Patch notes Feb 2020](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2020/02/); [Competitive Play (OW1 rev)](https://overwatch.fandom.com/wiki/Competitive_Play?oldid=128194)
- **SR and ranks:**
  - SR runs 1–5000 and was 1–100 in Season 1 (Sept 2016) — [Patch notes Sept 2016](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2016/09/)
  - Draws give no SR change. New players get bigger swings for their first 10–20 matches — [Competitive Play (OW1 rev)](https://overwatch.fandom.com/wiki/Competitive_Play?oldid=128194)
  - Tier demotion: Silver to Diamond demote after failing the minimum over 5 games; Master and above demote immediately — same source.
- **Group SR limits:** Diamond and below within 1000 SR; Master within 500; GM/Top 500 within 350 and duos only — [Competitive Play (OW1 rev)](https://overwatch.fandom.com/wiki/Competitive_Play?oldid=128194). GM was 250 (Nov 2017) and became 350 in Sept 2018 — [Patch notes Sept 2018](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2018/09/). From Aug 2020, a party with any player at ≥3900 SR is limited to 2 players — [Patch notes Aug 2020](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2020/08/)
- **SR decay:**
  - Introduced Sept 2016: Diamond and above lose 50 SR every 24 h after 7 days idle, with a floor of 3000 — [Patch notes Sept 2016](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2016/09/)
  - Reduced Aug 2017 to 25 SR/day, with each match adding 36 h before decay — [Patch notes Aug 2017](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2017/08/)
- **Competitive points:**
  - 15 for a win, 5 for a draw, 0 for a loss. Accrual stops at 6000 unspent — [Competitive Play (OW1 rev)](https://overwatch.fandom.com/wiki/Competitive_Play?oldid=128194); [Competitive Points (OW1 rev)](https://overwatch.fandom.com/wiki/Competitive_Points?oldid=124074)
  - End-of-season rewards per role (RQ): Bronze 25, Silver 50, Gold 100, Platinum 200, Diamond 300, Master 500, GM 650.
  - End-of-season rewards (OQ): 65, 125, 250, 500, 750, 1200, 1750.
  - Season 2 values were 10 per win and 3 per draw (Sept 2016) — [Patch notes Sept 2016](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2016/09/)
- **Unlock and season length:** Competitive unlocked at player level 25 in OW1. Seasons were 2 months long from Season 6 — [Competitive Play (OW1 rev)](https://overwatch.fandom.com/wiki/Competitive_Play?oldid=128194); [Patch notes Aug 2017](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2017/08/)
- **OW2 changes, Oct 4, 2022 (not OW1):** 5v5, new Competitive system, Role Queue removed from all modes except "Quick Play – Role Queue", Assault retired, player levels retired — [Patch notes Oct 2022](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2022/10/)

### Inferences
- The final OW1 Competitive rules for the server are:
  - Two-round mirrored attack/defense; Control best-of-3.
  - Time bank as above, including the Mar 2020 2:00 equalization.
  - 33.3% progress threshold for tiebreaks.
  - One copy of each hero per team.
  - 2/2/2 role lock in RQ; any composition in OQ.

### Gaps
- The SR gain/loss formula is not public.
- No OWL rulebook PDF was reachable to compare tournament rules (pauses, tech timeouts).

---

## 7. Arcade, Deathmatch, Elimination, Capture the Flag and other modes

### Takeaway
- **Deathmatch:** FFA has 8 players, first to 20 points, 10 min. Team Deathmatch is 4v4, first to 30, 10 min. A final blow gives +1; a self or environmental death gives −1. In TDM a Mercy resurrection removes the enemy's point.
- **Elimination:** No respawn within a round; first to 3 round wins (1v1 is first to 5). Lockout variants lock heroes that won a round. There is a capture-point tiebreaker (custom default: point after 105 s, 3 s capture, draw at 135 s without the tiebreaker).
- **CTF (final OW1, 2018 rules):**
  - Instant pickup.
  - A dropped flag is locked for 5 s.
  - Return takes 4 s and is not interrupted by damage.
  - 8-minute match, 3 captures to win.
  - The flag respawns 15 s after a score.
  - Restricted abilities drop the flag.
  - Sudden Death has flags moved toward the center.
  - Blitz CTF (2020) has closer flags.
- **Mystery Heroes, No Limits, Total Mayhem, Low Gravity:** Rule modifiers on standard modes.

### Cited Findings

**Deathmatch**
- **Launch rules, Aug 2017:**
  - FFA: 8 players to 20 points. "1 point whenever they land the final blow on an opponent and will lose 1 point whenever they die to environmental damage ... or self-inflicted damage."
  - TDM: 4v4 to 30. "If players are resurrected before they respawn, the corresponding point for their death will be deducted from the enemy team's score."
  - Source: [Patch notes Aug 2017](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2017/08/)
- **Timer and placement:** The 10-minute timer decides the winner if the score is not reached. The top 4 of FFA get win credit — [Arcade (OW1 rev)](https://overwatch.fandom.com/wiki/Arcade?oldid=127559); [Game Modes (OW1 rev)](https://overwatch.fandom.com/wiki/Game_Modes?oldid=124830)
- **Ana:** Can Nano Boost herself in FFA (May 2018) — [Patch notes May 2018](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2018/05/)
- **Map additions:** Petra was added and Competitive FFA Deathmatch introduced in May 2018 (Petra and Château Guillard) — same source
- **B.O.B.:** "Killing B.O.B no longer grants score for FFA and Team Deathmatch" (Feb 2020) — [Patch notes Feb 2020](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2020/02/)
- **Custom ranges** (current revision listing) — [Custom Game (current revision)](https://overwatch.fandom.com/wiki/Custom_Game):
  - FFA: length 10 min (5–15), score 20 (1–5000), self-initiated respawn on
  - TDM: length 10 (5–15), score 30 (1–200), Mercy resurrect counteracts kills (default on), optional imbalanced team scores

**Elimination**
- **Rules:** 1v1, 3v3 or 6v6, first to 3 round wins (1v1 is first to 5). A killed player cannot respawn that round. Lockout: "Heroes played during a winning round cannot be used again." — [Game Modes (OW1 rev)](https://overwatch.fandom.com/wiki/Game_Modes?oldid=124830); [Arcade (OW1 rev)](https://overwatch.fandom.com/wiki/Arcade?oldid=127559)
- **Arcade variants (OW1):** 1v1 Mystery Duel (same random hero; Bastion, D.Va, Lúcio, Mercy, Reinhardt, Torbjörn, Winston and Zarya unavailable), 1v1 Limited Duel (choice of 3 random heroes per round), 3v3 Elimination, 3v3 Lockout and 6v6 Lockout — [Arcade (OW1 rev)](https://overwatch.fandom.com/wiki/Arcade?oldid=127559)
- **May 2017:** Added 3v3/1v1 rule sets and "options for Hero Lockout, Limited Hero Pool, Tiebreakers, and Hero Reveal for Elimination mode" — [Patch notes May 2017](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2017/05/)
- **Custom-game defaults** (current listing; options date from OW1) — [Custom Game (current revision)](https://overwatch.fandom.com/wiki/Custom_Game):
  - Hero selection time 20 s (max 60)
  - Score to win 3 (1–9)
  - Restrict previously used heroes: Off / After round won / After round played
  - Hero selection: Any / Limited / Random / Random (Mirrored); limited pool = team size +2 by default
  - Capture objective tiebreaker: enabled, after 105 s (30–300), time to capture 3 s (1–7)
  - Draw after 135 s if no tiebreaker (60–300)
  - Reveal heroes: disabled by default, after 75 s (0–180)

**Capture the Flag**
- **2017 Capture the Rooster (Lijiang only):** 6v6, the first team to 3 captures or the most when the **7-minute** timer ends wins; ties are a draw — [Capture the Rooster (OW1 rev)](https://overwatch.fandom.com/wiki/Capture_the_Rooster?oldid=116963)
- **Feb 2017:** Became a permanent Arcade mode on Nepal, Lijiang, Ilios and Oasis — [Patch notes Feb 2017](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2017/02/)
- **Mar 2017 clarification:** "each team's flag will need to be secured before they can score" — [Patch notes Mar 2017](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2017/03/)
- **Feb 8, 2018 rule changes (Ayutthaya release; final OW1 baseline):**
  - Flag pickup is instant.
  - A flag cannot be picked up for 5 s after it is dropped.
  - Flag return takes 4 s and does not stop when taking damage.
  - Match length is 8 minutes.
  - After scoring, the flag takes 15 s to respawn.
  - Restricted abilities drop the flag:
    - Doomfist: Meteor Strike, Seismic Slam, Rising Uppercut, Rocket Punch
    - Genji: Swift Strike
    - Pharah: Jump Jet, self-applied Concussive Blast
    - Reaper: Shadowstep, Wraith Form
    - Soldier: 76: Sprint
    - Sombra: Stealth, Translocator
    - Tracer: Blink, Recall
    - Junkrat: self-applied Concussion Mine
    - Mei: Cryo-freeze
    - Widowmaker: Grappling Hook
    - D.Va: Boosters, Self-Destruct, and mech destroyed
    - Reinhardt: Charge
    - Winston: Jump Pack, Primal Rage
    - Lúcio: Amp It Up, Crossfade speed
    - Mercy: Valkyrie, Guardian Angel
    - Moira: Fade, Coalescence
    - Zenyatta: Transcendence
  - **Sudden Death:** "Matches no longer end in a draw. When time runs out, a new round is started and flags are moved closer to the center of the map. The first team to score wins."
  - Source: [Blizzard forum, CTF Updates Feb 8, 2018](https://us.forums.blizzard.com/en/overwatch/t/capture-the-flag-updates-february-8-2018/23)
- **Feb 13, 2018:** Lúcio's Wall Ride now drops the flag — [Patch notes Feb 2018](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2018/02/)
- **OW1 wiki summary:** First to 3 or most when the timer ends. The game will not end while a team's flag is outside its base; this triggers overtime, and the overtime wick does not burn until both flags are secured. A tie after regulation/overtime goes to Sudden Death with closer flags and one point to win. The wiki still says "5-minute timer", which conflicts with the 2018 official 8 minutes — [Game Modes (OW1 rev)](https://overwatch.fandom.com/wiki/Game_Modes?oldid=124830)
- **Seasons and Blitz:** Competitive CTF seasons ran 2018–2022, with Season 5 in Jan 2022. "Blitz CTF" was added Jan 2020 — [Patch notes Jan 2020](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2020/01/); [Patch notes Jan 2022](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2022/01/)
- **Custom CTF defaults** (current revision; the default values exactly match the 2018 rules) — [Custom Game (current revision)](https://overwatch.fandom.com/wiki/Custom_Game):

  | Setting | Default | Range / options |
  |---|---|---|
  | Game length | 8 min | 5–15 |
  | Score to win | 3 | 1–9 |
  | Flag dropped lock time | 5 s | 0–10 |
  | Flag pick-up time | 0 s | 0–5 |
  | Flag return time | 4 s | 0–5 |
  | Flag score respawn time | 15 s | 0–20 |
  | Respawn speed buff duration | 0 s | 0–60 |
  | Damage interrupts flag interaction | Disabled | — |
  | Flag carrier abilities | Restricted | None / All |
  | Team needs flag at base to score | No | — |
  | Blitz flag locations | No | — |

- **CTF respawn times:** The OW2-era Respawn page gives 13 s for CTF and 5 s for Blitz. These were not verified as OW1 values — [Respawn (current revision)](https://overwatch.fandom.com/wiki/Respawn)

**Rule-modifier Arcade modes**
- **Total Mayhem:** 200% health, 150% ultimate gain, 75% faster cooldowns; Escort/Hybrid maps — [Arcade (OW1 rev)](https://overwatch.fandom.com/wiki/Arcade?oldid=127559)
- **Low Gravity:** Standard modes with gravity at 25% — same source
- **No Limits:** No hero selection limit — same source
- **Mystery Heroes:** A random hero on each respawn; standard objectives.
  - Sept 2017: no Assemble screen; self-kills no longer reroll the hero but reset ult and despawn deployables; no respawning as the same hero — [Patch notes Sept 2017](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2017/09/)
  - Aug 2019: heroes reset between Control rounds — [Patch notes Aug 2019](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2019/08/)
  - The OW2 Mystery Heroes page limits each team to 3 heroes per role. This was not verified for OW1 — [Mystery Heroes (current revision)](https://overwatch.fandom.com/wiki/Mystery_Heroes)
- **Bounty Hunter (Feb 2021):** FFA; the first kill makes you the Target, who scores extra; whoever kills the Target becomes the next Target — [Patch notes Feb 2021](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2021/02/)
  - "Bounty targets will lose their target status if they take too long to get a kill" — same source
  - Custom defaults (current revision): 100 per kill, 300 for killing the Target, 300 per kill as Target, 1 Target, 10 min, 20 to win — [Custom Game (current revision)](https://overwatch.fandom.com/wiki/Custom_Game)
- **Other competitive Arcade modes:** Copa Lúcioball (2017), Competitive CTF (2018), 6v6 Lockout Elimination, FFA Deathmatch, 3v3 Group Elimination, Team Deathmatch and No Limits (Nov 2020) — [Competitive Play (OW1 rev)](https://overwatch.fandom.com/wiki/Competitive_Play?oldid=128194); [Patch notes Nov 2020](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2020/11/)
- **Arcade rewards:** 1 loot box per 3 wins, up to 3 per week, resetting Tuesday 00:00 EST — [Arcade (OW1 rev)](https://overwatch.fandom.com/wiki/Arcade?oldid=127559)
- **Skirmish:** Practice without score while queuing. In Dec 2019 it became part of "While You Wait" (Skirmish or Deathmatch) — [Patch notes Dec 2019](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2019/12/). The custom Skirmish option "limit valid control points" was added May 2020 — [Patch notes May 2020](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2020/05/)
- **Hero Gauntlet:** In OW1 it was a Workshop example. Custom-game presets list "Hero Gauntlet" under Workshop examples — [Custom Game (current revision)](https://overwatch.fandom.com/wiki/Custom_Game)

### Inferences
- For a server implementation, CTF state is: flag {home, carried, dropped(lockout 5 s), returning(4 s channel)}, score respawn 15 s, 8-minute clock, overtime while a flag is out, then Sudden Death with alternate flag positions.

### Gaps
- Blitz CTF exact differences (score to win, timer, respawn 5 s) are only on OW2-era pages.
- The Elimination round timer before the tiebreak, the size of the Elimination capture point and whether ult charge carries between rounds were not documented for OW1.
- Exact rules for Lockout Elimination's "Limited pool" in the Arcade versions were not documented.

---

## 8. Training, Practice Range, Play vs AI and seasonal/PvE modes

### Takeaway
- **Practice Range:** No objectives. It has 4 friendly and 11 hostile training bots with 200 HP; hostile shooting bots deal 8 damage per projectile.
- **Practice vs AI:** Easy, Medium and Hard deal 25%, 50% and 100% damage, with no AI headshots and 90% XP. A limited AI hero list plays on random Assault, Control, Escort or Hybrid maps.
- **Seasonal PvE:** Junkenstein's Revenge, Uprising, Retribution and Storm Rising are 4-player co-op with Normal, Hard, Expert and Legendary difficulty. Uprising downs players with a 40 s revive window.
- **Seasonal PvP:** Lúcioball is 3v3, 4 min (Copa 6 min), with a goal-lead mercy rule. Yeti Hunt is 5 Meis against a 5000 HP Yeti. Mei's Snowball Offensive uses one-shot snowballs.

### Cited Findings
- **Practice Range:** No objectives; 4 friendly and 11 hostile training bots; range markers in meters — [Practice Range (OW1 rev)](https://overwatch.fandom.com/wiki/Practice_Range?oldid=95841)
- **Training bot:** 200 HP. Duo Cannons: 8 damage per projectile, 60 m/s, 4 shots/s, 8 ammo, 1 s reload, can headshot — [Training bot (OW1 rev)](https://overwatch.fandom.com/wiki/Training_bot?oldid=123913)
- **Custom Practice Range options** (current listing) — [Custom Game (current revision)](https://overwatch.fandom.com/wiki/Custom_Game):
  - Spawn training bots: on by default
  - Training bot respawn time scalar: 100% (10–500%)
  - Training partner: on by default
- **Practice vs AI:** Difficulty Easy/Medium/Hard = 25%/50%/100% damage; bots never headshot. AI heroes: Roadhog, Zarya, Bastion, Cassidy, Mei, Reaper, Soldier: 76, Sombra, Torbjörn, Ana, Lúcio, Zenyatta. Modes are random among Assault, Control, Escort and Hybrid. Always 90% XP — [Practice vs. AI (OW1 rev)](https://overwatch.fandom.com/wiki/Practice_vs._AI?oldid=123429)
- **Tutorial:** Athena guides the player through movement, attacks and abilities as Soldier: 76, then leads into the Practice Range — [Tutorial (OW1 rev)](https://overwatch.fandom.com/wiki/Tutorial?oldid=118449)
- **Lúcioball:**
  - 3v3, 4 minutes; overtime on a tie ends at the next goal. Copa Lúcioball (Competitive) is 6 minutes.
  - Mercy rule: before Summer Games 2020, a 10-goal lead ended the game. The OW1 page text says a lead of "more than 5" ends it.
  - Remix (2020) adds extra balls, golden 3-point balls and a 10-point lead rule.
  - Source: [Lúcioball (OW1 rev)](https://overwatch.fandom.com/wiki/L%C3%BAcioball?oldid=126444)
- **Yeti Hunt:**
  - 5 Hunters (Mei) against 1 Yeti (Winston), with 5000 HP, on Nepal Village.
  - Each piece of meat gives 25% ult; at 100% Primal Rage triggers automatically.
  - Hunters' Cryo-Freeze heals over 2 s; their ult is a Yeti Trap.
  - Hunters win by killing the Yeti. The Yeti wins with 5 Hunter kills.
  - A capture point activates if too much time passes. A Yeti that falls respawns with a health penalty.
  - Source: [Yeti Hunt (OW1 rev)](https://overwatch.fandom.com/wiki/Yeti_Hunt?oldid=103230)
- **Mei's Snowball Offensive:** 6v6 Mei-only on Ecopoint: Antarctica. One-shot snowball refilled at snow piles. The ult (Flurry) gives temporary infinite ammo — [Mei's Snowball Offensive (OW1 rev)](https://overwatch.fandom.com/wiki/Mei%27s_Snowball_Offensive?oldid=80822). Freezethaw Elimination is 4v4 (Dec 2020) — [Patch notes Dec 2020](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2020/12/)
- **Junkenstein's Revenge:** 4-player co-op defense of the Adlersbrunn gate (Eichenwalde) with fixed heroes Ashe/McCree, Soldier, Hanzo and Ana (later versions differ). Difficulties are Normal, Hard, Expert and Legendary (2017+). Endless mode has 12 waves — [Junkenstein's Revenge (OW1 rev)](https://overwatch.fandom.com/wiki/Junkenstein%27s_Revenge?oldid=118963)
- **Overwatch Uprising (King's Row):**
  - 4 players.
  - A downed player can be revived within 40 s; the mission fails if all are down.
  - Stages: hack 3 terminals; defend the payload for 4 minutes; escort it (speed does not scale with players); destroy 4 OR14s.
  - Source: [Overwatch Uprising (OW1 rev)](https://overwatch.fandom.com/wiki/Overwatch_Uprising?oldid=122607)
- **Retribution (Rialto) and Storm Rising (Havana):** Wave-clear progression with Heavy Assault bosses. On Expert/Legendary Storm Rising spawns an extra Heavy Assault — [Overwatch Retribution (OW1 rev)](https://overwatch.fandom.com/wiki/Overwatch_Retribution?oldid=124034); [Overwatch Storm Rising (OW1 rev)](https://overwatch.fandom.com/wiki/Overwatch_Storm_Rising?oldid=124043)

### Gaps
- Per-difficulty PvE enemy health and damage multipliers, Junkenstein gate HP and wave timings were not collected.

---

## 9. Custom game / tournament settings that alter rules

### Takeaway
Custom Games (OW1 "Game Browser") expose per-mode multipliers:
- Capture speed modifier: 100% default, 0–500%
- Payload speed modifier: 100% default, 0–500%
- Scoring speed modifier: 100% default, 0–500%
- Respawn time scalar: 100% default, can only go **down** to 0% since Sept 2018
- Health pack respawn scalar: 100% default, 0–500%
- Control score to win: 2 default, 1–3
- Game length and score-to-win for CTF, DM, TDM and Elimination (tables above)
- Hero limit, role limit, competitive rules toggle, and an option to use the latest Experimental update
- Per-hero modifiers, including ultimate generation

### Cited Findings
- **Respawn time scalar, Sept 2018:** "Modified the Respawn Time Scalar custom game option to prevent respawn times longer than the default." This gives a range of 0–100% — [Patch notes Sept 2018](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2018/09/)
- **General settings** (current listing; most date from OW1) — [Custom Game (current revision)](https://overwatch.fandom.com/wiki/Custom_Game):
  - Enemy health bars
  - Game Mode Start: All slots filled / Immediately / Manual
  - Health pack respawn scalar: 100% (0–500%)
  - Kill cam and kill feed toggles
  - Skins toggle
  - Spawn health packs: determined by mode / enabled / disabled
- **Hero settings** — same source:
  - Allow hero switching
  - Hero limit: 1 per team (default), 2 per team, 1 per game, 2 per game, off
  - Respawn as random hero
  - Random hero role limit per team
  - Respawn time scalar
  - The default role limit and tank role passive listed there are OW2 (1/2/2). The OW1 equivalent was 2/2/2 or off.
- **Per-mode settings** — same source:
  - Assault: capture speed 100% (0–500%), competitive rules
  - Control: capture speed, scoring speed, score to win, limit valid points, competitive rules
  - Escort: payload speed 100% (0–500%), competitive rules
  - Hybrid: payload speed and capture speed, competitive rules
  - Lobby: Max Team 1/2 players (OW2 default 5; OW1 default was 6), max FFA players up to 12, max spectators default 2 (up to 12), pause on disconnect, data center preference (added Jan 2020)
- **Data center preference:** Added Jan 2020 — [Patch notes Jan 2020](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2020/01/)
- **Experimental (Feb 2020):** Experimental card added, first with a 1-3-2 "Triple Damage" test — [Patch notes Feb 2020](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2020/02/)
- **Skirmish in custom games:** No EXP from skirmishes in custom games and AFK detection added (Mar 2017) — [Patch notes Mar 2017](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2017/03/)
- **Mode presets:** OW1 custom presets included 1v1 Limited/Mystery Duel, 3v3 Elimination/Lockout, 4v4 TDM, 8-player FFA, Capture the Flag (and "Capture the Flag – 2017", the old rules), CTF Blitz, Mystery Heroes, No Limits, Total Mayhem, Skirmish and others. The list is the current revision; the "2017 CTF" preset implies OW1 kept both rule sets — [Custom Game (current revision)](https://overwatch.fandom.com/wiki/Custom_Game)

### Gaps
- The full OW1 per-hero settings list (damage/healing dealt and received, ultimate generation passive/combat, cooldown, health, movement speed, projectile speed, gravity) and their ranges were not retrieved from an OW1-era source. The wiki's OW1 Custom Game page was a stub, and wiki.gg/workshop.codes were blocked.
- OWL tournament rulebooks (pauses, ready checks, tech timeouts) could not be fetched.

---

## 10. Ultimate charge rules

### Takeaway
**Charge sources:**
- Ultimates charge passively at 5 points/s.
- Damage to enemy heroes gives charge 1:1; damage to Roadhog gives 75%.
- Healing gives charge 1:1, excluding self-damage recovery and some named exceptions.
- Mercy gains charge from damage she amplifies.
- Ultimate damage gives no charge.

**Spending and modifiers:**
- Charge is spent immediately on activation (since Oct 2017).
- Costs per hero range from 1260 to 2940 points (Call Mech is 319.2).
- Total Mayhem applies 150% gain.

**Carry-over between rounds is not documented** (see Gaps).

### Cited Findings
- **Charge sources (OW1 rev, Feb 2022)** — [Ultimate ability (OW1 rev)](https://overwatch.fandom.com/wiki/Ultimate_ability?oldid=123286):
  - "Heroes gain 5 charge every second."
  - Damage to enemy players gives charge 1:1, including environmental kills. Self-damage and damage to non-heroes give none.
  - Damage to Wrecking Ball's Adaptive Shield gives none. Ultimate damage gives none.
  - Damage to Roadhog gives 75%.
  - Healing gives charge 1:1, except Reaper's The Reaping, Mercy's Regeneration, Sombra-hacked packs, healing of self-damage and healing of environmental damage.
  - Mercy gains charge equal to damage she amplified.
  - Most heroes cannot gain charge while their ult is active. Exceptions: Ashe, Hanzo, Torbjörn, Tracer, Wrecking Ball. Echo's gain while using Duplicate is ×6.5 toward the copied ult.
- **Roadhog charge change, Aug 2021:** "Enemies now generate 25% less Ultimate Charge from damage dealt to Roadhog" — [Patch notes Aug 2021](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2021/08/)
- **Oct 2017:** "Ultimate charge is now immediately expended when a hero's ultimate ability is activated, instead of depleting over a short period of time" — [Patch notes Oct 2017](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2017/10/)
- **Ultimate costs (points)** — [Ultimate ability (OW1 rev)](https://overwatch.fandom.com/wiki/Ultimate_ability?oldid=123286):
  - Call Mech: 319.2 (64 s passive)
  - Pulse Bomb: 1260 (4:12 passive)
  - EMP: 1400
  - Self-Destruct, Earthshatter, Infra-Sight, Minefield, Primal Rage: 1540
  - Meteor Strike: 1680
  - Nano Boost: 2100
  - B.O.B.: 2240
  - Amplification Matrix, Configuration: Tank: 2310
  - Rally: 2800
  - Maximum listed: 2940
  - Max passive time = cost / 5.
  - Baptiste's ult cost was later scaled down (Sept 2020) — [Patch notes Sept 2020](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2020/09/)
- **Total Mayhem:** 150% ultimate gain — [Arcade (OW1 rev)](https://overwatch.fandom.com/wiki/Arcade?oldid=127559)
- **Mystery Heroes:** A self-kill resets the ult (Sept 2017) — [Patch notes Sept 2017](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2017/09/). The OW2 page notes a self-elimination respawns as the same hero with 0% ult — [Mystery Heroes (current revision)](https://overwatch.fandom.com/wiki/Mystery_Heroes)
- **Ult charge retained across a skin change:** A Feb 2018 fix concerned "hero ultimate charges to reset after the first death if a player changed their skin ... a second before the match began". This implies charge is persistent state across deaths and is normally retained — [Patch notes Feb 2018](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2018/02/)
- **Custom ultimate generation:** Passive and combat generation are separately settable; Mercy's damage-boost charge is a separate category unaffected by those settings — [Ultimate ability (OW1 rev)](https://overwatch.fandom.com/wiki/Ultimate_ability?oldid=123286)

### Inferences
- Charge accounting on the server, per tick:
  - `charge += 5*dt*passive_mult` (unless the ult is active and the hero is not on the exception list)
  - `charge += damage_to_enemy_heroes*combat_mult*(0.75 if target is Roadhog)`
  - `charge += effective_healing*combat_mult`
  - Clamp at cost; the ult is ready when charge equals cost.
- Commonly understood OW1 behaviour, **not verified by a source here**:
  - Ult charge is reset to 0 when switching heroes (with exceptions).
  - Ult charge is kept between Control rounds but not carried from attack to defense in 2CP/Escort/Hybrid round swaps.

### Gaps
- No source was found for ult charge carry-over between Competitive halves or Control rounds, or for the ult retention/reset rule on hero switch (including the OW1 "switch heroes loses ult" rule). These should be verified against native client data or replays.
- "Combo" rules (e.g. kill/assist bonuses) were not found; no evidence that OW1 had any ult bonus beyond damage, healing and passive charge.

---

## 11. OW1 vs OW2 confusion flags (do NOT implement in an OW1 server)
- **Team size:** 5v5 and role passives are OW2 (Oct 4, 2022). OW1 is 6v6 with Role Queue 2/2/2 or Open Queue — [Patch notes Oct 2022](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2022/10/)
- **Respawn:** Wave Respawn and a 12 s base are OW2 Season 12. Overtime respawn of 13/14 s is OW2. OW1 uses a 10 s base, group respawn in non-competitive modes, the attacker-advantage delay and an overtime penalty — [Respawn (current revision)](https://overwatch.fandom.com/wiki/Respawn); [Overtime (current revision)](https://overwatch.fandom.com/wiki/Overtime)
- **Escort timers and healing:** "4:00 / +2:30 / +1:30", "Unranked 5:00 / +3:00 / +2:00" and 5 HP/s payload healing are documented on OW2 pages. OW1 healing is 10 HP/s — [Escort (current revision)](https://overwatch.fandom.com/wiki/Escort); [Escort (OW1 rev)](https://overwatch.fandom.com/wiki/Escort?oldid=125449)
- **Assault:** Removed from playlists in OW2 (custom only) — [Patch notes Oct 2022](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2022/10/)
- **OW2-only modes:** Push, Flashpoint and Clash (Clash's custom capture speed defaults to 45%). Push / Hero Missions / Story were announced pre-OW2 — [Game Modes (OW1 rev)](https://overwatch.fandom.com/wiki/Game_Modes?oldid=124830); [Custom Game (current revision)](https://overwatch.fandom.com/wiki/Custom_Game)
- **Unlocks:** OW2 FTUE (new-player locks, 50 QP wins to unlock Competitive) is OW2. OW1 unlocked Competitive at level 25 — [Competitive Play (OW1 rev)](https://overwatch.fandom.com/wiki/Competitive_Play?oldid=128194)

### Inferences
- The project's target build 1.74.0.0.104319 predates the Oct 2022 OW2 notes. Every OW2-era page value above should be treated only as a hint until it is confirmed against native client data, such as the Practice-mode ruleset/statescript graphs the project already reads.

### Gaps
- Native mode/ruleset records in the 1.74 client (graphs such as the game-mode records referenced in project notes) are likely the most authoritative source for exact timers. They were not part of this web research.
