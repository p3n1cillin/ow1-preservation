# Overwatch 1 Workshop, Custom Games and AI bots: engine capabilities a reimplemented server must provide

Scope: final OW1 (client 1.74.0.0.104319, 2022). Primary machine-readable source: the OverPy project's data files (GPL-3.0) at the **last pre-OW2 commit** `b24553ab` (2022-03-10). Its `src/data/actions.js` was last changed on 2021-10-06, so it is the final OW1 Workshop catalogue. I diffed it against current OverPy `main` (TypeScript data) by GUID to flag OW2-only additions. I cloned OverPy read-only into the session scratchpad and parsed its JSON blocks; I did not run its code. Fandom wiki pages were read as MediaWiki wikitext through `api.php`, including **pre-OW2 revisions** (`rvstart=2022-09-30`), because current wiki pages describe OW2.

Shorthand source links used below:
- OPY-A = https://github.com/Zezombye/overpy/blob/b24553ab0120ea4fcc040787e0b124ed617b9dda/src/data/actions.js
- OPY-V = https://github.com/Zezombye/overpy/blob/b24553ab0120ea4fcc040787e0b124ed617b9dda/src/data/values.js
- OPY-O = https://github.com/Zezombye/overpy/blob/b24553ab0120ea4fcc040787e0b124ed617b9dda/src/data/other.js
- OPY-C = https://github.com/Zezombye/overpy/blob/b24553ab0120ea4fcc040787e0b124ed617b9dda/src/data/constants.js
- OPY-S = https://github.com/Zezombye/overpy/blob/b24553ab0120ea4fcc040787e0b124ed617b9dda/src/data/customGameSettings.js
- OPY-M = https://github.com/Zezombye/overpy/blob/b24553ab0120ea4fcc040787e0b124ed617b9dda/src/data/maps.js
- OPY-MAIN = https://github.com/Zezombye/overpy/tree/main/src/data (current, includes OW2)
- OPY-GV = https://github.com/Zezombye/overpy/blob/main/src/globalVars.ts ; OPY-COMP = https://github.com/Zezombye/overpy/blob/main/src/compiler/compiler.ts

## (1) Workshop: events, actions, values, limits and maps relevant to a server reimplementation

### Takeaway
The final OW1 Workshop has 14 event types, 222 actions and 265 values; the full catalogue is below. Almost every action is an authoritative server-side primitive: damage, healing, statuses, impulses, forced position, throttle, facing, hero forcing, bots, HUD and effect entities, ult charge, cooldowns, ammo, scaling and collision. A Workshop-compatible server therefore needs an entity/status/damage/movement-override layer and a rule VM. Only three Workshop actions are OW2-only: Create Projectile, Create Homing Projectile and Create Projectile Effect. Note that the assignment's "July 2020" date is wrong: the Workshop reached the PTR on 2019-04-24 and went live on 2019-05-21.

### Cited Findings

**History and dates**
- Workshop announced by Jeff Kaplan and put on the PTR 2019-04-24, described as a "simplified game scripting system" with an Inspector debugger. It is not a map editor and was PC-PTR-only at first. — [Engadget 2019-04-24](https://www.engadget.com/2019/04/24/overwatch-custom-games-workshop-scripting-mode/); [EU forum PTR notes 2019-04-24](https://eu.forums.blizzard.com/en/overwatch/t/overwatch-ptr-patch-notes-april-24-2019/16342)
- Officially released on live servers 21 May 2019. — [Overwatch Fandom "Workshop" (wikitext)](https://overwatch.fandom.com/wiki/Workshop) citing [Retail patch notes May 21 2019](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2019/05)
- The Feb 2020 PTR update ("Workshop update grants unprecedented power for creators") added:
  - Workshop maps: Chamber (enclosed 40x40 m room), Island (same size, no roof or walls) and Expanse (blank 900x900 m plane).
  - Subroutines.
  - A Script Diagnostics panel that shows how close a script is to the size limits.
  - Removal of the rule that loops need a preceding Wait.
  - Dan Reed (gameplay engineer) and Zach Metcalf are quoted.
  — [devtrackers mirror of Blizzard article](https://devtrackers.gg/overwatch/p/48631d3a-workshop-update-grants-unprecedented-power-for-creators)
- May 19, 2020 live patch:
  - Strings can be stored in variables, and conditions/actions display in C-style syntax.
  - New actions: Break, Continue, Set Crouch/Melee/Jump Enabled, Declare Round Draw, Set Ability Cooldown, Cancel Primary Action.
  - New values: Is Meleeing, Is Jumping, Event Direction, Button, Event Ability, Ability Cooldown, Ability Icon String, Array, If-Then-Else.
  - Night versions of the Workshop Island and Expanse maps.
  — [Blizzard live patch notes 2020/05](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2020/05). A May 2020 PTR also increased the overall script size limit 4x (search summary of PTR notes; not independently fetched) — [GameRevolution PTR May 2](https://www.gamerevolution.com/?p=534557)
- Oct 20, 2020 PTR:
  - Max Workshop **Element Count raised to 32768**; Workshop Settings get Sort Order and a **max of 128 settings**.
  - New actions: Log To Inspector, Wait Until, Set Knockback Dealt/Received, Set Environment Credit Player, Start/Stop/Stop All Assists, Create/Destroy Progress Bar HUD/In-World Text.
  - New values: Color, Custom Color, Workshop Setting Combo/Hero, Evaluate Once, Update Every Frame, Magnitude Of, Number of Slots, Spawn Points, String Contains/Length/Slice, Last Assist ID, Is Communicating Any Spray, Player Stat, Player Hero Stat.
  - New "Workshop Green Screen" map and a custom-game "Minimum Latency" option, which delays low-latency players to a target, generally within 8 ms.
  - Bug fix for "extra 0.016-second delays when multiple Waits run on the same player or global entity".
  — [devtrackers mirror, PTR notes 2020-10-20](https://devtrackers.gg/overwatch/p/a1831caf-overwatch-ptr-patch-notes-october-20-2020). The element limit was 20,000 before that (forum user report) — [Blizzard forum](https://us.forums.blizzard.com/en/overwatch/t/advanced-workshop-scripting-help-needed/501882)
- March 9, 2021 retail patch:
  - **Workshop Extensions**, enabled with "Extension Points, which are earned by either disabling player slots, disabling all non-Workshop maps" or both. The extensions are Beam Effects, Beam Sounds, Buff Status Effects, Debuff Status Effects, Buff and Debuff Sounds, Energy Explosion Effects, Kinetic Explosion Effects, Explosion Sounds, Play More Effects and Spawn More Dummy Bots.
  - New actions: Enable/Disable Text Chat and Voice Chat, Start Game Mode, Return to Lobby, Restart Match, Move Player to Team, Remove Player, Start/Stop Forcing Dummy Bot Name.
  - New values: DoT/HoT/Text/Damage-Modification/Healing-Modification/Assist/Entity Count, Local Player, Char In String, Index Of String Char, String Split, String Replace.
  - Spawn Points now returns an array of entities rather than position vectors.
  — [devtrackers mirror, retail notes 2021-03-09](https://devtrackers.gg/overwatch/p/0324dfd7-overwatch-retail-patch-notes-march-9-2021). Point cost per extension in OverPy schema: Beam Effects 2, Beam Sounds 1, Buff and Debuff Sounds 2, Buff Status Effects 2, Debuff Status Effects 2, Energy Explosion Effects 4, Explosion Sounds 2, Kinetic Explosion Effects 4, Play More Effects 1, Spawn More Dummy Bots 2 — [OPY-S](https://github.com/Zezombye/overpy/blob/b24553ab0120ea4fcc040787e0b124ed617b9dda/src/data/customGameSettings.js)

**Limits (OW1 final)**
- Element limit 32768 (`ELEMENT_LIMIT`). Custom-string limits: 128 characters and 3 format arguments per string, so longer strings are split. Numeric literals above ~10,000,000 behave oddly. — [OPY-GV](https://github.com/Zezombye/overpy/blob/main/src/globalVars.ts)
- 128 global variables, 128 player variables (indices 0..127) and 128 subroutines. — [OPY-COMP](https://github.com/Zezombye/overpy/blob/main/src/compiler/compiler.ts)
- Arrays "can go up to 1000" elements (OverPy helper description). — [OverPy data/opy/functions.ts](https://github.com/Zezombye/overpy/blob/main/src/data/opy/functions.ts)
- Workshop Setting names and categories: custom string literals of at most 128 characters. — [OPY-V](https://github.com/Zezombye/overpy/blob/b24553ab0120ea4fcc040787e0b124ed617b9dda/src/data/values.js)
- Server Load: "a percentage representing the CPU load of the current game instance. As this number approaches or exceeds 100, it becomes increasingly likely that the instance will be shut down because it is consuming too many resources". Server Load Average and Server Load Peak cover the last two seconds. — [OPY-V](https://github.com/Zezombye/overpy/blob/b24553ab0120ea4fcc040787e0b124ed617b9dda/src/data/values.js)
- Update Every Frame: "Increases the update frequency of the provided value to once per tick … values, such as getPosition(), that normally only update every few ticks … interpolated client-side if the framerate is higher than the tick rate. May increase server load". This means Workshop values are evaluated server-side at reduced rate by default. — [OPY-V](https://github.com/Zezombye/overpy/blob/b24553ab0120ea4fcc040787e0b124ed617b9dda/src/data/values.js)
- Entity-creating actions fail when "too many entities have been created". The same applies to damage modifications and assists ("will fail if too many … have been started"). Health pools: "Up to 16 health pools of a given health type (health, armor, or shields) may exist on a player (including base pools and pools generated by abilities)". — [OPY-A](https://github.com/Zezombye/overpy/blob/b24553ab0120ea4fcc040787e0b124ed617b9dda/src/data/actions.js)
- Dummy bots: "Up to 6 bots may be added to each team, or 12 bots to the free-for-all team, regardless of lobby settings". Without workshop actions the bot "will only move, fire, or use abilities if executing workshop actions". — [OPY-A](https://github.com/Zezombye/overpy/blob/b24553ab0120ea4fcc040787e0b124ed617b9dda/src/data/actions.js)
- Workshop Inspector: Enable/Disable Inspector Recording and Log To Inspector (Oct 2020) exist as actions. Kaplan described the Inspector as showing "why certain things are happening". — [OPY-A](https://github.com/Zezombye/overpy/blob/b24553ab0120ea4fcc040787e0b124ed617b9dda/src/data/actions.js); [Engadget](https://www.engadget.com/2019/04/24/overwatch-custom-games-workshop-scripting-mode/)

**Rule structure, events and enums**
- Rule keywords: rule, event, conditions, actions, disabled, variables (global/player), subroutines, settings. — [OPY-O](https://github.com/Zezombye/overpy/blob/b24553ab0120ea4fcc040787e0b124ed617b9dda/src/data/other.js)
- **Events (14, with OverPy GUID suffix):**

  | Event | GUID |
  | --- | --- |
  | Ongoing - Global | 07895 |
  | Ongoing - Each Player | 07897 |
  | Player Earned Elimination | 078F7 |
  | Player Dealt Final Blow | 078F8 |
  | Player Dealt Damage | 0B52D |
  | Player Took Damage | 0B313 |
  | Player Died | 0B314 |
  | Player Dealt Healing | 0CC16 |
  | Player Received Healing | 0CC17 |
  | Player Joined Match | 0CC18 |
  | Player Left Match | 0CC19 |
  | Player Dealt Knockback | 105BB |
  | Player Received Knockback | 105BC |
  | Subroutine | 0FFF6 |

  Per-player events also filter by team (All / Team 1 / Team 2) and by slot (Slot 0–11) or hero (All). — [OPY-O](https://github.com/Zezombye/overpy/blob/b24553ab0120ea4fcc040787e0b124ed617b9dda/src/data/other.js)
- Event-context values for a server event bus to supply:
  - Event Player, Attacker, Victim, Healer, Healee
  - Event Damage, Event Healing, Event Direction, Event Ability
  - Event Was Critical Hit, Event Was Environment, Event Was Health Pack
  — [OPY-V](https://github.com/Zezombye/overpy/blob/b24553ab0120ea4fcc040787e0b124ed617b9dda/src/data/values.js)
- **Status constants (10) with GUID suffix:** Asleep 0B36A, Burning 0B36C, Frozen 0B369, Hacked 0B36D, Invincible 0B367, Knocked Down 0B36B, Phased Out 0B366, Rooted 0B365, Stunned 0B565, Unkillable 0B368. — [OPY-C](https://github.com/Zezombye/overpy/blob/b24553ab0120ea4fcc040787e0b124ed617b9dda/src/data/constants.js)
- **Logical buttons:** Primary Fire, Secondary Fire, Ability 1, Ability 2, Ultimate, Interact, Jump, Crouch, Melee, Reload. — [OPY-C](https://github.com/Zezombye/overpy/blob/b24553ab0120ea4fcc040787e0b124ed617b9dda/src/data/constants.js)
- **Other enums:** all from [OPY-C](https://github.com/Zezombye/overpy/blob/b24553ab0120ea4fcc040787e0b124ed617b9dda/src/data/constants.js).
  - Health types: Health / Armor / Shields.
  - Impulse motion: Cancel Contrary Motion / Cancel Contrary Motion XYZ / Incorporate Contrary Motion.
  - Relativity: To World / To Player.
  - Invisible-to: All / Enemies / None.
  - LOS checks: Off / Surfaces / Surfaces And All Barriers / Surfaces And Enemy Barriers.
  - Barrier LOS: Enemy Barriers Block / All Barriers Block / Barriers Do Not Block.
  - Wait behaviour: Ignore Condition / Abort When False / Restart When True.
  - Throttle: Replace / Add to existing.
  - Outline visibility: Default / Occluded / Always.
  - Spectator visibility: Default / Always / Never.
  - Reevaluation enums per action (e.g. DamageReeval: None / Receivers and Damagers / Receivers Damagers and Damage Percent).
  - 17 named colours plus Custom Color RGBA.
  - 36 icons, 71 persistent effect types, 100 one-shot "dynamic" effects (hero-ability explosions and sounds), 20 beam types and 36 communication types.
  - 33 Player Hero Stat and 20 Player Stat categories.
- Final OW1 hero list (32): Ana, Ashe, Baptiste, Bastion, Brigitte, Doomfist, D.Va, Echo, Genji, Wrecking Ball, Hanzo, Junkrat, Lúcio, Cassidy, Mei, Mercy, Moira, Orisa, Pharah, Reaper, Reinhardt, Roadhog, Sigma, Soldier: 76, Sombra, Symmetra, Torbjörn, Tracer, Widowmaker, Winston, Zarya, Zenyatta. — [OverPy heroes.js @b24553a](https://github.com/Zezombye/overpy/blob/b24553ab0120ea4fcc040787e0b124ed617b9dda/src/data/heroes.js)
- 70 map entries, each tagged with its supported modes. Practice Range (GUID 02BA1) supports only `practiceRange`. Workshop maps support skirmish, elimination, ffa, bountyHunter and tdm:

  | Workshop map | GUID suffix |
  | --- | --- |
  | Workshop Chamber | 0FFF0 |
  | Workshop Island | 0FFF1 |
  | Workshop Expanse | 0FFF2 |
  | Workshop Expanse Night | 10C6D |
  | Workshop Island Night | 10C71 |
  | Workshop Green Screen | 11F44 |

  — [OPY-M](https://github.com/Zezombye/overpy/blob/b24553ab0120ea4fcc040787e0b124ed617b9dda/src/data/maps.js)

**OW2-only additions (flag; not in OW1 104319)**
- A GUID diff of OverPy `main` against `b24553a` finds exactly three new actions: Create Projectile (GUID 1978E), Create Homing Projectile (1A77B) and Create Projectile Effect (1A9A7). It also finds two values new as separate entries, "Number" (0AC38) and "Team" (0BB26); these are probably literal/constant wrappers rather than gameplay features. No OW1 action or value was removed. OW2 heroes (Junker Queen, Kiriko, etc.) and maps exist only in OW2 constants. — [OPY-MAIN](https://github.com/Zezombye/overpy/tree/main/src/data) vs [OPY-A](https://github.com/Zezombye/overpy/blob/b24553ab0120ea4fcc040787e0b124ed617b9dda/src/data/actions.js)
- The current Fandom Workshop page mentions extension points for "custom projectiles that look like the ones from hero-specific weapons". That is the OW2 projectile extension. — [Fandom Workshop](https://overwatch.fandom.com/wiki/Workshop)

**Key action semantics (verbatim OverPy/Blizzard descriptions), most relevant to server design.** All from [OPY-A](https://github.com/Zezombye/overpy/blob/b24553ab0120ea4fcc040787e0b124ed617b9dda/src/data/actions.js) / [OPY-V](https://github.com/Zezombye/overpy/blob/b24553ab0120ea4fcc040787e0b124ed617b9dda/src/data/values.js):
- **Set Status(Player, Assister, Status, Duration):**
  - "Applies a status… for the specified duration or until it is cleared". Statuses "behave similarly to statuses applied from hero abilities".
  - The Assister "will be awarded assist credit should the affected player … be killed while the status is in effect". Use 9999 for an indefinite status.
  - Has Status is true "either from the set status action or from a non-scripted game mechanic", so engine statuses and script statuses share one status set.
- **Damage(Player, Damager, Amount):** "may be modified by buffs, debuffs, or armor"; a null damager means no credit. **Kill(Player, Killer).** **Heal(Player, Healer, Amount).** **Set Player Health:** "Sets the health … without affecting stats or granting damage/healing credit".
- **Start Damage Over Time / Start Heal Over Time:** these take a duration, a rate and a credited source. **Start Damage Modification(Receivers, Damagers, %, Reeval)** is a pairwise damage multiplier. **Start Healing Modification** works the same way for healing.
- **Set Damage Dealt / Damage Received / Healing Dealt / Healing Received / Knockback Dealt / Knockback Received, Set Max Health, Set Move Speed, Set Gravity, Set Jump Vertical Speed, Set Projectile Speed / Gravity, Set Aim Speed, Set Slow Motion:** all are percent multipliers. Slow motion "only rates up to 100%" and affects "all players, projectiles, effects, and game mode logic".
- **Apply Impulse(Player, Direction, Speed, Relative, Motion):** an "instantaneous change in velocity"; the direction is normalized. **Start Accelerating(Player, Direction, Rate m/s², Max Speed, …).**
- **Start Forcing Player Position(Player, Position, Reevaluate):** with reevaluation "the position is evaluated every frame". **Teleport(Player, Position).** **Attach Players(Child, Parent, Offset):** the child "will be unable to move freely until detached or teleported away".
- **Input overrides:**
  - Start Forcing Throttle sets min/max forward, backward and sideways input.
  - Start Throttle In Direction sets or adds a directional throttle.
  - Start Transforming Throttle scales and rotates the throttle.
  - Press Button presses "virtually for a single frame"; Start/Stop Holding Button holds one.
  - Allow/Disallow Button and Set Primary/Secondary/Ability1/Ability2/Ultimate/Melee/Jump/Crouch/Reload Enabled enable or disable inputs.
  - These are the same input channels that Workshop dummy-bot "AI" uses.
- **Facing:** Start Facing(Player, Direction, Turn Rate deg/s, Relative, Reeval) and Set Facing. **Camera:** Start Camera(Player, Eye Position, Look At, Blend Speed) "Reevaluates continuously".
- **Create Dummy Bot(Hero, Team, Slot, Position, Facing)** and Destroy Dummy Bot / Destroy All Dummy Bots. **Is Dummy Bot** is a value. **Start Forcing Dummy Bot Name** "only works with AI and dummy bots".
- **Ultimate and abilities:** Set Ultimate Charge (percent of maximum), Set Ultimate Ability Enabled, Set Ability Cooldown / Charge / Resource, Set Ammo / Max Ammo (per clip), Set Weapon (1 or 2), Cancel Primary Action.
- **Hero control:**
  - Start Forcing Player To Be Hero "respawns them immediately in their current location".
  - Set Player Allowed Heroes forces a re-pick if the current hero becomes unavailable.
  - Reset Player Hero Availability.
  - Preload Hero "using the skins of the specified player".
  - Respawn ("appropriate spawn location with full health"), Resurrect ("at the location they died with no transition"), Set Respawn Max Time.
  - Start Forcing Spawn Room(Team, Room).
- **Match flow:**
  - Declare Team/Player Victory, Declare Match/Round Draw, Declare Round Victory.
  - Set/Pause/Unpause Match Time, Go To Assemble Heroes.
  - Disable/Enable Built-In Game Mode Completion, Scoring, Respawning, Announcer and Music.
  - Set Objective Description; Modify/Set Team Score and Player Score.
  - Start Game Mode, Restart Match, Return To Lobby, Move Player to Team, Remove Player.
- **Presentation entities:**
  - Create HUD Text(Visible To, Header, Subheader, Text, Location Left/Top/Right, Sort Order, three colours, Reevaluation, Spectators).
  - Create In-World Text, Create Progress Bar HUD / In-World Text, Create Icon, Create Effect, Create Beam Effect, Play Effect.
  - Big Message (above the reticle) and Small Message.
  - Disable/Enable Hero HUD, Game Mode HUD, Game Mode In-World UI, Kill Feed, Scoreboard, Messages and Nameplates.
  - Start Forcing Player Outlines, Set Invisible.
  - "Visible To" is evaluated per viewer, so these are server-owned entities filtered per client.
- **Collision and scaling:** Disable Movement Collision With Environment (optionally including floors) and With Players; Start Scaling Player "including mode, movement collision, hit detection, and certain abilities"; Start Scaling Barriers; Start Modifying Hero Voice Lines (pitch). The current OverPy data has these in the pre-OW2 commit, so they are OW1 features.
- **Credit plumbing:** Start Assist(Assisters, Targets) ("If the Target … allied to the Assister, this will be a defensive assist. Otherwise … offensive"); Set Environment Credit Player (credit for environmental kills "before landing on the ground").
- **Spatial queries the server must answer:**
  - **Nearest Walkable Position**: "The position closest to the specified position that can be stood on and is accessible from a spawn point". This implies a navigation and walkability representation connected to spawn points.
  - **Is In Line of Sight**(Start, End, Barrier mode): a player argument uses "a position 2 meters above the player's feet".
  - **Ray Cast Hit Position / Normal / Player**(Start, End, Include, Exclude, Include Player Owned Objects).
  - Players Within Radius(…, LOS check), Closest/Farthest Player To, Player Closest To Reticle, Players in View Angle, Is In View Angle.
  - Altitude Of, Is On Ground, Is On Wall, Is In Air.
  - Spawn Points(Team), Is In Spawn Room ("being healed and able to change heroes").
  - Objective Position, Payload Position / Progress, Point Capture Percentage, Control Mode Scoring Percentage, Flag Position.
- **Local Player:** "different for each end user and thus can only be accessed in actions which affect visuals or the HUD. This value cannot be stored in variables". This marks the client/server split: everything else is server-evaluated.

**Full final-OW1 catalogue extracted from OverPy @b24553a**
Format: OverPy `guid` suffix (low 5 hex digits of the 12-digit identifier; the identifier's upper digits are zero), English name, arguments, first sentence of the description. [const] marks values OverPy flags as compile-time constants.
- Actions (222) — [OPY-A](https://github.com/Zezombye/overpy/blob/b24553ab0120ea4fcc040787e0b124ed617b9dda/src/data/actions.js):

```text
0BB09 Abort() - Stops execution of the action list.
0BB04 Abort If(Condition) - Stops execution of the action list if this action's condition evaluates to true.
0BB02 Abort If Condition Is False() - Stops execution of the action list if at least one condition in the condition list is false.
0BB03 Abort If Condition Is True() - Stops execution of the action list if all conditions in the condition list are true.
11423 Add Health Pool To Player(Player, Health Type, Max Health, Is Recoverable, Reevaluation) - Adds a temporary health pool to a player or players.
0B9D0 Allow Button(Player, Button) - Undoes the effect of the disallow button action for one or more players.
078F6 Apply Impulse(Player, Direction, Speed, Relative, Motion) - Applies an instantaneous change in velocity to the movement of one or more players.
10E4F Attach Players(Child, Parent, Offset) - Attaches the player (the 'child') to another player (the 'parent').
0BA88 Big Message(Visible To, Header) - Displays a large message above the reticle that is visible to specific players.
105B6 Break() - Goes to the end of the innermost `switch` statement, or `do/while`, `while` or `for` loop.
1001E Call Subroutine(Subroutine) - Pauses execution of the current rule and begins executing a subroutine rule (which is a rule with a subroutine event type).
109CB Cancel Primary Action(Player) - Cancels the active abilities for one or more players.
0B840 Chase Global Variable At Rate(Variable, Destination, Rate, Reevaluation) - Gradually modifies the value of a global variable at a specific rate.
0B842 Chase Global Variable Over Time(Variable, Destination, Duration, Reevaluation) - Gradually modifies the value of a global variable over time.
0B83F Chase Player Variable At Rate(Player, Variable, Destination, Rate, Reevaluation) - Gradually modifies the value of a player variable at a specific rate.
0B841 Chase Player Variable Over Time(Player, Variable, Destination, Duration, Reevaluation) - Gradually modifies the value of a player variable over time.
0B595 Clear Status(Player, Status) - Clears a status that was applied from a set status action from one or more players.
0B9E3 Communicate(Player, Type) - Causes one or more players to use an emote, voice line, or other equipped communication.
105B7 Continue() - Goes back to the start of the innermost loop.
0CE80 Create Beam Effect(Visible To, Type, Start Position, End Position, Color, Reevaluation) - Creates an in-world beam effect entity.
0CA6A Create Dummy Bot(Hero, Team, Slot, Position, Facing) - Adds a new bot to the specified slot on the specified team so long as the slot is available.
0B8AF Create Effect(Visible To, Type, Color, Position, Radius, Reevaluation) - Creates an in-world effect entity.
0BAD3 Create HUD Text(Visible To, Header, Subheader, Text, Location, Sort Order, Header Color, Subheader Color, Text Color, Reevaluation, Spectators) - Creates hud text visible to specific players at a specific location on the screen.
0ACFA Create Icon(Visible To, Position, Icon, Reevaluation, Icon Color, Show When Offscreen) - Creates an in-world icon entity.
0BAD0 Create In-World Text(Visible To, Header, Position, Scale, Clipping, Reevaluation, Text Color, Spectators) - Creates in-world text visible to specific players at a specific position in the world.
122F3 Create Progress Bar HUD Text(Visible To, Value, Text, Location, Sort Order, Progress Bar Color, Text Color, Reevaluation, Non-Team Spectators) - Creates a progress bar HUD text visible to specified players at a specific location on the screen.
1233A Create Progress Bar In-World Text(Visible To, Value, Text, Position, Scale, Clipping, Progress Bar Color, Text Color, Reevaluation, Non-Team Spectators) - Creates a progress bar in-world text visible to the specific players at a specific position in the world.
07876 Damage(Player, Damager, Amount) - Applies instantaneous damage to one or more players, possibly killing the players.
0B9F1 Declare Match Draw() - Instantly ends the match in a draw.
0AD30 Declare Player Victory(Player) - Instantly ends the match with the specific player as the winner.
1098F Declare Round Draw() - Declare a draw for the current round.
0BF93 Declare Round Victory(Round Winning Team) - Declare a team as the current round winner.
078FD Declare Team Victory(Team) - Instantly ends the match with the specified team as the winner.
0D1D4 Destroy All Dummy Bots() - Removes all dummy bots from the match.
0B8AD Destroy All Effects() - Destroys all effect entities created by create effect.
0BAD1 Destroy All HUD Text() - Destroys all hud text that was created by the create hud text action.
0B8AC Destroy All Icons() - Destroys all icon entities created by create icon.
0B8AB Destroy All In-World Text() - Destroys all in-world text created by create in-world text.
122E2 Destroy All Progress Bar HUD Text() - Destroys all Progress Bar HUD text that were created by the Create Progress Bar HUD Text Action.
12334 Destroy All Progress Bar In-World Text() - Destroys all progress bar in-world texts that were created by the createProgressBarInWorldText() Action.
0CC21 Destroy Dummy Bot(Team, Slot) - Removes the specified dummy bot from the match.
0B8AE Destroy Effect(Entity) - Destroys an effect entity that was created by create effect.
0BAD2 Destroy HUD Text(Text Id) - Destroys hud text that was created by create hud text.
0B4E7 Destroy Icon(Entity) - Destroys an icon entity that was created by create icon.
0BACF Destroy In-World Text(Text Id) - Destroys in-world text that was created by create in-world text.
122E4 Destroy Progress Bar HUD Text(Text ID) - Destroys the progress bar HUD text that was created by progressBarHud().
12336 Destroy Progress Bar In-World Text(Text ID) - Destroys the progress bar in-world text that was created by createProgressBarInWorldText().
10E52 Detach Players(Children) - Undoes the attachment caused by the 'attachTo' action for one or more players.
0C3F8 Disable Built-In Game Mode Announcer() - Disables game mode announcements from the announcer until reenabled or the match ends.
0AD2D Disable Built-In Game Mode Completion() - Disables completion of the match from the game mode itself, only allowing the match to be completed by scripting commands.
0C3F4 Disable Built-In Game Mode Music() - Disables all game mode music until reenabled or the match ends.
0B87A Disable Built-In Game Mode Respawning(Players) - Disables automatic respawning for one or more players, only allowing respawning by scripting commands.
0ABFA Disable Built-In Game Mode Scoring() - Disables changes to player and team scores from the game mode itself, only allowing scores to be changed by scripting commands.
0B9B5 Disable Death Spectate All Players(Player) - Undoes the effect of the enable death spectate all players action for or more players.
0B9B3 Disable Death Spectate Target HUD(Player) - Undoes the effect of the enable death spectate target hud action for or more players.
110A8 Disable Game Mode HUD(Player) - Disables the game mode HUD for one or more players until reenabled.
11242 Disable Game Mode In-World UI(Player) - Disables the game mode In-World UI for one or more players until reenabled.
1109E Disable Hero HUD(Player) - Disables the Hero HUD for one or more players until reenabled.
0FB2F Disable Inspector Recording() - Causes the workshop inspector to stop recording new entries.
11093 Disable Kill Feed(Player) - Disables the kill feed for one or more players until reenabled.
110AE Disable Messages(Player) - Disables messages for one or more players until reenabled.
112F9 Disable Movement Collision With Environment(Player, Include Floors) - Causes a player or players to stop colliding with the environment (walls, ceilings, certain objects, etc.)
112F7 Disable Movement Collision With Players(Player) - Causes a player or players to stop colliding with other Players.
11254 Disable Nameplates(Viewed Players, Viewing Players) - Disables the nameplate on one or more viewed players from the perspective of one or more viewing players.
110A5 Disable Scoreboard(Player) - Disables the scoreboard for one or more players until reenabled.
12BB6 Disable Text Chat(Player) - Disables Text Chat for one or more Players until reenabled
12BBC Disable Voice Chat(Player, disable Team Voice Chat, disable Match Voice Chat, disable Group Voice Chat) - Disables voice chat for one or more players until reenabled
0B9CF Disallow Button(Player, Button) - Disables a logical button for one or more players such that pressing it has no effect.
0FB34 Else() - Denotes the beginning of a series of actions that will only execute if the previous If or Else If action's condition was false.
0FB33 Else If(Condition) - Denotes the beginning of a series of actions that will only execute if the specified condition is true and the previous If or Else If action's condition was false.
0C3FA Enable Built-In Game Mode Announcer() - Undoes the effect of the disable built-in game mode announcer action.
0AD2F Enable Built-In Game Mode Completion() - Undoes the effect of the disable built-in game mode completion action.
0C3F6 Enable Built-In Game Mode Music() - Undoes the effect of the disable built-in game mode music action.
0B878 Enable Built-In Game Mode Respawning(Players) - Undoes the effect of the disable built-in game mode respawning action for one or more players.
0ABF8 Enable Built-In Game Mode Scoring() - Undoes the effect of the disable built-in game mode scoring action.
0B9AE Enable Death Spectate All Players(Player) - Allows one or more players to spectate all players when dead, as opposed to only allies.
0B9B4 Enable Death Spectate Target HUD(Player) - Causes one or more players to see their spectate target's hud instead of their own while death spectating.
110A7 Enable Game Mode HUD(Player) - Undoes the effect of the Disable Game Mode HUD Action for one or more players.
1123F Enable Game Mode In-World UI(Player) - Undoes the effect of the Disable Game Mode In-World UI Action for one or more players.
1109B Enable Hero HUD(Player) - Undoes the effect of the Disable Hero HUD Action for one or more players.
0FB2E Enable Inspector Recording() - Causes the workshop inspector to resume recording new entries (in case it had been disabled earlier).
11092 Enable Kill Feed(Player) - Undoes the effect of the Disable Kill Feed Action for one or more players.
110AD Enable Messages(Player) - Undoes the effect of the Disable Messages Action for one or more players.
112FA Enable Movement Collision With Environment(Player) - Undoes the effect of the Disable Movement Collision With Enviroment action for one or more players.
112F8 Enable Movement Collision With Players(Player) - Undoes the effect of the Disable Movement Collision With Players action for one or more players.
11253 Enable Nameplates(Viewed Players, Viewing Players) - Undoes the effect of Disable Nameplates for one or more viewed players from the perspective of one or more viewing players.
110A1 Enable Scoreboard(Player) - Undoes the effect of the Disable Scoreboard Action for one or more players.
12BB3 Enable Text Chat(Player) - Undoes the effect of the Disable Text Chat Action for one or more players.
12BB9 Enable Voice Chat(Player) - Undoes the effect of the Disable Voice Chat Action for one or more players.
0FB37 End() - Denotes the end of a series of actions started by an if, else if, else, while, or for action.
0FEE2 For Global Variable(Control Variable, Range Start, Range Stop, Step) - Denotes the beginning of a series of actions that will execute in a loop, modifying the control variable on each loop.
0FEE1 For Player Variable(Control Player, Control Variable, Range Start, Range Stop, Step) - Denotes the beginning of a series of actions that will execute in a loop, modifying the control variable on each loop.
0C5B5 Go To Assemble Heroes() - Returns the match to the assemble heroes phase of the game mode.
07875 Heal(Player, Healer, Amount) - Provides an instantaneous heal to one or more players.
0FB32 If(Condition) - Denotes the beginning of a series of actions that will only execute if the specified condition is true.
07877 Kill(Player, Killer) - Instantly kills one or more players.
12449 Log To Inspector(Text) - Causes the workshop inspector to record a log entry.
078F5 Loop() - Restarts the action list from the beginning.
0BB06 Loop If(Condition) - Restarts the action list from the beginning if this action's condition evaluates to true.
0BB05 Loop If Condition Is False() - Restarts the action list from the beginning if at least one condition in the condition list is false.
07874 Loop If Condition Is True() - Restarts the action list from the beginning if every condition in the condition list is true.
0786E Modify Global Variable(Variable, Operation, Value) - Modifies the value of a global variable, which is a variable that belongs to the game itself.
0C7E1 Modify Global Variable At Index(Variable, Index, Operation, Value) - Modifies the value of a global variable at an index, which is a variable that belongs to the game itself.
07873 Modify Player Score(Player, Score) - Modifies the score (kill count) of one or more players.
0786F Modify Player Variable(Player, Variable, Operation, Value) - Modifies the value of a player variable, which is a variable that belongs to a specific player.
0C7DF Modify Player Variable At Index(Player, Variable, Index, Operation, Value) - Modifies the value of a player variable at an index, which is a variable that belongs to a specific player.
0BB24 Modify Team Score(Team, Score) - Modifies the score of one or both teams.
12C2E Move Player to Team(Player, Team, Slot) - Move one or more players to the specified team and slot.
0B9EF Pause Match Time() - Pauses the match time.
0BB27 Play Effect(Visible To, Type, Color, Position, Radius) - Plays an effect at a position in the world.
0B9B1 Preload Hero(Player, Hero) - Preemptively loads the specified hero or heroes into memory using the skins of the specified player or players, available memory permitting.
078FB Press Button(Player, Button) - Forces one or more players to press a button virtually for a single frame.
11433 Remove All Health Pools From Player(Player) - Removes all health pools that were added to a player or players via the Add Health Pool action.
11425 Remove Health Pool From Player(Id) - Removes a health pool that was added via the Add Health Pool action.
12C2B Remove Player(Player) - Removes one or more players from the custom game.
0BA5A Reset Player Hero Availability(Player) - Restores the list of heroes available to one or more players to the list specified by the game settings.
078FC Respawn(Player) - Respawns one or more players at an appropriate spawn location with full health, even if they were already alive.
12C22 Restart Match() - Restarts the match.
07878 Resurrect(Player) - Instantly resurrects one or more players at the location they died with no transition.
02C4C Return To Lobby() - Returns the gamemode back to the custom game lobby.
0B9B8 Set Ability 1 Enabled(Player, Enabled) - Enables or disables ability 1 for one or more players.
0B9B7 Set Ability 2 Enabled(Player, Enabled) - Enables or disables ability 2 for one or more players.
1120C Set Ability Charge(Player, Button, Charge Count) - Set the ability charge count for one or more players.
109CA Set Ability Cooldown(Player, Button, Cooldown) - Set the ability cooldown time for one or more players.
1120F Set Ability Resource(Player, Button, Resource Percent) - Set the ability resource percentage for one or more players.
0C364 Set Aim Speed(Player, Turn Speed Percent) - Sets the aim speed of one or more players to a percentage of their normal aim speed.
110F1 Set Ammo(Player, Clip, Ammo) - Set the ammo of one or more players.
105A3 Set Crouch Enabled(Player, Enabled) - Enables or disables crouch for one or more players.
0B995 Set Damage Dealt(Player, Damage Dealt Percent) - Sets the damage dealt of one or more players to a percentage of their raw damage dealt.
0B997 Set Damage Received(Player, Damage Received Percent) - Sets the damage received of one or more players to a percentage of their raw damage received.
11C08 Set Environment Credit Player(Target, Environment Credit Player) - Sets the player who will received credit if the specified target player or players die to the environment before landing on the ground.
0BB29 Set Facing(Player, Direction, Relative) - Sets the facing of one or more players to the specified direction.
077DE Set Global Variable(Variable, Value) - Stores a value into a global variable, which is a variable that belongs to the game itself.
0BBAA Set Global Variable At Index(Variable, Index, Value) - Finds or creates an array on a global variable, which is a variable that belongs to the game itself, then stores a value in the array at the specified index.
0B999 Set Gravity(Player, Gravity Percent) - Sets the movement gravity for one or more players to a percentage regular movement gravity.
0B991 Set Healing Dealt(Player, Healing Dealt Percent) - Sets the healing dealt of one or more players to a percentage of their raw healing dealt.
0B993 Set Healing Received(Player, Healing Received Percent) - Sets the healing received of one or more players to a percentage of their raw healing received.
0B9ED Set Invisible(Player, Invisible To) - Causes one or more players to become invisible to either all other players or just enemies.
105A5 Set Jump Enabled(Player, Enabled) - Enables or disables jump for one or more players.
1122D Set Jump Vertical Speed(Player, Jump Vertical Speed Percent) - Sets the jump vertical speed of one or more players to a percentage of their raw jump vertical speed.
11FA9 Set Knockback Dealt(Player, Knockback Dealt Percent) - Sets the knockback dealt of one or more players to a percentage of their raw knockback dealt.
11FAA Set Knockback Received(Player, Knockback Received Percent) - Sets the knockback received of one or more players to a percentage of their raw knockback received.
0AD31 Set Match Time(Time) - Sets the current match time (which is visible at the top of the screen).
110F2 Set Max Ammo(Player, Clip, Ammo) - Set the max ammo of one or more players.
078FA Set Max Health(Player, Health Percent) - Sets the max health of one or more players as a percentage of their max health.
10596 Set Melee Enabled(Player, Enabled) - Enables or disables melee for one or more players.
0B998 Set Move Speed(Player, Move Speed Percent) - Sets the move speed of one or more players to a percentage of their raw move speed.
0BA85 Set Objective Description(Visible To, Header, Reevaluation) - Sets the text at the top center of the screen that normally describes the objective to a message visible to specific players.
0BA5B Set Player Allowed Heroes(Player, Hero) - Sets the list of heroes available to one or more players.
11440 Set Player Health(Player, Amount) - Sets the health of a player or players without affecting stats or granting damage/healing credit.
0BB22 Set Player Score(Player, Score) - Sets the score (kill count) of one or more players.
077DF Set Player Variable(Player, Variable, Value) - Stores a value into a player variable, which is a variable that belongs to a specific player.
0BBA9 Set Player Variable At Index(Player, Variable, Index, Value) - Finds or creates an array on a player variable, which is a variable that belongs to a specific player, then stores a value in the array at the specified index.
0C6C5 Set Primary Fire Enabled(Player, Enabled) - Enables or disables primary fire for one or more players.
0B99B Set Projectile Gravity(Player, Projectile Gravity Percent) - Sets the projectile gravity for one or more players to a percentage of regular projectile gravity.
0B99D Set Projectile Speed(Player, Projectile Speed Percent) - Sets the projectile speed for one or more players to a percentage of projectile speed.
11068 Set Reload Enabled(Player, Enabled) - Enables or disables Reload for one or more players.
0B9CD Set Respawn Max Time(Player, Time) - Sets the duration between death and respawn for one or more players.
0C6C4 Set Secondary Fire Enabled(Player, Enabled) - Enables or disables secondary fire for one or more players.
0B9F2 Set Slow Motion(Speed Percent) - Sets the simulation rate for the entire game, including all players, projectiles, effects, and game mode logic.
0B588 Set Status(Player, Assister, Status, Duration) - Applies a status to one or more players.
0BB25 Set Team Score(Team, Score) - Sets the score for one or both teams.
0B9B6 Set Ultimate Ability Enabled(Player, Enabled) - Enables or disables the ultimate ability of one or more players.
0BB1C Set Ultimate Charge(Player, Charge Percent) - Sets the ultimate charge for one or more players as a percentage of maximum charge.
1105C Set Weapon(Player, Weapon) - Sets the weapon of one or more players.
0BB01 Skip(Number Of Actions) - Skips execution of a certain number of actions in the action list.
0BB00 Skip If(Condition, Number Of Actions) - Skips execution of a certain number of actions in the action list if this action's condition evaluates to true.
0BA87 Small Message(Visible To, Header) - Displays a small message beneath the reticle that is visible to specific players.
0BB0D Start Accelerating(Player, Direction, Rate, Max Speed, Relative, Reevaluation) - Starts accelerating one or more players in a specified direction.
12200 Start Assist(Assisters, Targets, Reevaluation) - Starts granting assist credit toward to one or more assisters when one or more targets are eliminated.
0C393 Start Camera(Player, Eye Position, Look At Position, Blend Speed) - Places your camera at a location, facing a direction.
0C639 Start Damage Modification(Receivers, Damagers, Damage Percent, Reevaluation) - Starts modifying how much damage one or more receivers will receive from one or more damagers.
0B9C5 Start Damage Over Time(Player, Damager, Duration, Damage Per Second) - Starts an instance of damage over time.
0BB20 Start Facing(Player, Direction, Turn Rate, Relative, Reevaluation) - Starts turning one or more players to face the specified direction.
12E8B Start Forcing Dummy Bot Name(Player, Name) - Starts forcing the name for the specified player or players (only works with AI and dummy bots).
112EC Start Forcing Player Outlines(Viewed Players, Viewing Players, Visible, Color, Visibility) - Starts forcing the visibility and color of the outlines of the specified viewed player or players from the perspective of one or more viewing players.
10E85 Start Forcing Player Position(Player, Position, Reevaluate) - Starts forcing a player to be in a given position.
0ABFB Start Forcing Player To Be Hero(Player, Hero) - Starts forcing one or more players to be a specific hero and, if necessary, respawns them immediately in their current location.
0B573 Start Forcing Spawn Room(Team, Room) - Forces a team to spawn in a particular spawn room, regardless of the spawn room normally used by the game mode.
0BB0F Start Forcing Throttle(Player, Min Forward, Max Forward, Min Backward, Max Backward, Min Sideways, Max Sideways) - Defines minimum and maximum movement input values for one or more players, possibly forcing or preventing movement.
12C1F Start Game Mode() - Starts the gamemode.
0B9C2 Start Heal Over Time(Player, Healer, Duration, Healing Per Second) - Starts an instance of heal over time.
0FD40 Start Healing Modification(Receivers, Healers, Healing Percent, Reevaluation) - Starts modifying how much healing one or more receivers will receive from one or more healers.
0B9D3 Start Holding Button(Player, Button) - Forces one or more players to hold a button virtually until stopped by the stop holding button action.
113C1 Start Modifying Hero Voice Lines(Player, Pitch Scalar, Reevaluation) - Modifies the way hero voice lines sound for a player or players.
10022 Start Rule(Subroutine, If Already Executing) - Begins simultaneous execution of a subroutine rule (which is a rule with a Subroutine event type).
112FC Start Scaling Barriers(Player, Scale, Reevaluation) - Start modifying the size of barriers for a player or players.
112FE Start Scaling Player(Player, Scale, Reevaluation) - Starts modifying the size of a player or players (including mode, movement collision, hit detection, and certain abilities).
0CEA4 Start Throttle In Direction(Player, Direction, Magnitude, Relative, Behavior, Reevaluation) - Sets or adds to the throttle (directional input control) of a player or players such that they begin moving in a particular direction.
0CC26 Start Transforming Throttle(Player, X Axis Scalar, Y Axis Scalar, Relative Direction) - Starts transforming (scaling and rotating) the throttle (directional input control) of a player or players.
0BB0C Stop Accelerating(Player) - Stops the acceleration started by the start accelerating action for one or more players.
121FA Stop All Assists() - Stops all assists that were started using the Start Assist Action.
0C647 Stop All Damage Modifications() - Stops all damage modifications that were started using the start damage modification action.
0B9C3 Stop All Damage Over Time(Player) - Stops all damage over time started by start damage over time for one or more players.
0B9C0 Stop All Heal Over Time(Player) - Stops all heal over time started by start heal over time for one or more players.
0FD3B Stop All Healing Modifications() - Stops all healing modifications that were started using the start healing modification action.
121FC Stop Assist(Assist ID) - Stops an assist that was started by the Start Assist Action.
0C3B1 Stop Camera(Player) - Restores the camera to the default view.
0B83E Stop Chasing Global Variable(Variable) - Stops an in-progress chase of a global variable, leaving it at its current value.
0B83D Stop Chasing Player Variable(Player, Variable) - Stops an in-progress chase of a player variable, leaving it at its current value.
0C649 Stop Damage Modification(Damage Modification) - Stops a damage modification that was started by the start damage modification action.
0B9C4 Stop Damage Over Time(Damage Over Time Id) - Stops an instance of damage over time started by the start damage over time action.
0BB21 Stop Facing(Player) - Stops the turning started by the start facing action for one or more players.
12E88 Stop Forcing Dummy Bot Name(Player) - Cancels the behavior of `startForcingName` for the specified player or players.
112ED Stop Forcing Player Outlines(Viewed Players, Viewing Players) - Cancels the behavior of Start Forcing Player Outlines for the specified viewed player or players from the perspective of one or more viewing players.
10E8D Stop Forcing Player Position(Player) - Cancels the behavior of `startForcingPosition()` for the specified player or players.
0AC1B Stop Forcing Player To Be Hero(Player) - Stops forcing one or more players to be a specific hero.
0B574 Stop Forcing Spawn Room(Team) - Undoes the effect of the start forcing spawn room action for the specified team.
0BB0E Stop Forcing Throttle(Player) - Undoes the effect of the start forcing throttle action for one or more players.
0B9C1 Stop Heal Over Time(Heal Over Time Id) - Stops an instance of heal over time started by the start heal over time action.
0FD37 Stop Healing Modification(Healing Modification Id) - Stops a healing modification that was started by the start healing modification action.
0B9D2 Stop Holding Button(Player, Button) - Undoes the effect of the start holding button action for one or more players.
113C0 Stop Modifying Hero Voice Lines(Player) - Undoes the effect of the Starting Modifying Hero Voice Lines action for one or more players.
112FB Stop Scaling Barriers(Player) - Stops overriding the size of the barriers of a Player or Players.
112FD Stop Scaling Player(Player) - Stops overring the size of a player or players.
0CEA3 Stop Throttle In Direction(Player) - Cancels the behavior caused by start throttle in direction.
0CC25 Stop Transforming Throttle(Player) - Stops the throttle transform started by start transforming throttle for one or more players.
0B9BA Teleport(Player, Position) - Teleports one or more players to the specified position.
0B9F0 Unpause Match Time() - Unpauses the match time.
07872 Wait(Time, Wait Behavior) - Pauses the execution of the action list.
121C2 Wait Until(Continue Condition, Timeout) - Waits until the Continue Condition is true or Timeout seconds elapse.
0FB35 While(Condition) - Denotes the beginning of a series of actions that will execute in a loop as long as the specified condition is true.
```

- Values (265) — [OPY-V](https://github.com/Zezombye/overpy/blob/b24553ab0120ea4fcc040787e0b124ed617b9dda/src/data/values.js):

```text
11216 Ability Charge(Player, Button) - The ability charge count for a player associated by button.
109B3 Ability Cooldown(Player, Button) - The ability cooldown time in seconds for a player associated by button.
10B52 Ability Icon String(Hero, Button) [const] - Converts a Hero and Button parameter into a string that shows up as an icon (up to 4 per string).
11218 Ability Resource(Player, Button) - The ability resource percent for a player associated by button.
0C358 Absolute Value(Value) [const] - The absolute value of the specified value.
0C408 Add(Value, Value) [const] - The sum of two numbers or vectors.
0D40A All Damage Heroes() [const] - The array of all damage heroes in overwatch.
0B265 All Dead Players(Team) - An array containing all dead players on a team or in the match.
0BF58 All Heroes() [const] - The array of all heroes in overwatch.
0B264 All Living Players(Team) - An array containing all living players on a team or in the match.
0B261 All Players(Team) - An array containing all players on a team or in the match.
0B267 All Players Not On Objective(Team) - An array containing all players occupying neither a payload nor a control point (either on a team or in the match).
0B266 All Players On Objective(Team) - An array containing all players occupying a payload or control point (either on a team or in the match).
0D40B All Support Heroes() [const] - The array of all support heroes in overwatch.
0D40C All Tank Heroes() [const] - The array of all tank heroes in overwatch.
0BBA8 Allowed Heroes(Player) - The array of heroes from which the specified player is currently allowed to select.
0B11D Altitude Of(Player) - The player's current height in meters above a surface.
110E8 Ammo(Player, Clip) - The current ammo of a player.
0B273 And(Value, Value) [const] - Whether both of the two inputs are true (or equivalent to true).
0C813 Angle Between Vectors(Vector, Vector) [const] - The angle in degrees between two directional vectors (no normalization required).
0B282 Angle Difference(Angle, Angle) [const] - The difference in degrees between two angles.
0C41A Append To Array(Array, Value) [const] - A copy of an array with one or more values appended to the end.
0C809 Arccosine In Degrees(Value) [const] - Arccosine in degrees of the specified value.
0C807 Arccosine In Radians(Value) [const] - Arccosine in radians of the specified value.
0C805 Arcsine In Degrees(Value) [const] - Arcsine in degrees of the specified value.
0C803 Arcsine In Radians(Value) [const] - Arcsine in radians of the specified value.
0C801 Arctangent In Degrees(Numerator, Denominator) [const] - Arctangent in degrees of the specified numerator and denominator (often referred to as atan2).
0C7FF Arctangent In Radians(Numerator, Denominator) [const] - Arctangent in radians of the specified numerator and denominator (often referred to as atan2).
0B836 Array([0]) [const] - An array constructed from the listed values.
0C336 Array Contains(Array, Value) [const] - Whether the specified array contains the specified value.
0B597 Array Slice(Array, Start Index, Count) [const] - A copy of the specified array containing only values from a specified index range.
12B9E Assist Count() - The current number of Assist instances started from the Start Assist Action.
0B32F Attacker() - The player that dealt the damage for the event currently being processed by this rule.
0B11B Backward() [const] - Shorthand for the directional vector(0, 0, -1), which points backward.
10B3B Button(Button) [const] - A button constant.
12D5E Char In String(String, Index) - The character found at a specified index of a String.
0B1DE Closest Player To(Center, Team) - The player closest to a position, optionally restricted by team.
11D42 Color(Color) [const] - A Color Constant
0B276 Compare(Value, Comparison, Value) [const] - Whether the comparison of the two inputs is true.
0B37C Control Mode Scoring Percentage(Team) - The score percentage for the specified team in control mode.
0B39A Control Mode Scoring Team() - The team that is currently accumulating score percentage in control mode.
0C33E Cosine From Degrees(Angle) [const] - Cosine of the specified angle in degrees.
0C342 Cosine From Radians(Angle) [const] - Cosine of the specified angle in radians.
0B26E Count Of(Array) [const] - The number of elements in the specified array.
0C35D Cross Product(Value, Value) [const] - The cross product of the specified values.
0B5B9 Current Array Element() [const] - The current array element being considered.
111B5 Current Array Index() [const] - The current array index being considered.
0F163 Current Game Mode() [const] - The current game mode of the custom game.
0D418 Current Map() [const] - The current map of the custom game.
11DA2 Custom Color(Red, Green, Blue, Alpha) [const] - A custom color with the specified red, green, blue and alpha values.
0CE3C Custom String(String, {0}, {1}, {2}) [const] - ty magzie for adding that
12B9C Damage Modification Count() - The current number of Damage Modification instances started from the Start Damage Modification Action.
12B99 Damage Over Time Count() - The current number of Damage Over Time instances started from the Damage Over Time action.
0BB2D Direction From Angles(Horizontal Angle, Vertical Angle) [const] - The unit-length direction vector corresponding to the specified angles.
0B1EA Direction Towards(Start Pos, End Pos) [const] - The unit-length direction vector from one position to another.
0B1E7 Distance Between(Start Pos, End Pos) [const] - The distance between two positions in meters.
0C40F Divide(Value, Value) [const] - The ratio of two numbers or vectors.
0C35A Dot Product(Value, Value) [const] - The dot product of the specified values.
0B119 Down() [const] - Shorthand for the directional vector(0, -1, 0), which points downward.
0BF5A Empty Array() [const] - An array with no elements.
12B9F Entity Count() - The current number of Entities created from the Create Effect, Create Beam Effect, or Create Icon Action.
0B619 Entity Exists(Entity) - Whether the specified player, icon entity, or effect entity still exists.
12214 Evaluate Once(Input Value) [const] - Makes a copy of the provided value.
109CF Event Ability() - The ability for the event currently being processed by this rule associated by button.
0C635 Event Damage() - The amount of damage received by the victim for the event currently being processed by this rule.
107D5 Event Direction() - The incoming direction for the event currently being processed by this rule.
0CC33 Event Healing() - The amount of healing received by the healee for the event currently being processed by this rule.
0B331 Event Player() - The player executing this rule, as specified by the event.
0C637 Event Was Critical Hit() - Whether the damage was a critical hit (such as a headshot) for the event currently being processed by this rule.
1107C Event Was Environment() - Whether the elimination was due to the environment for the event currently being processed by this rule.
0FC80 Event Was Health Pack() - Whether the healing was a health pack for the event currently being processed by this rule.
0C595 Eye Position(Player) - The position of a player's first person view (used for aiming)
0B281 Facing Direction Of(Player) - The unit-length directional vector of a player's current facing relative to the world.
0AC3A False() [const] - The boolean value of false.
0B1DF Farthest Player From(Center, Team) - The player farthest from a position, optionally restricted by team.
0B5B7 Filtered Array(Array, Condition) [const] - A copy of the specified array with any values that do not match the specified condition removed.
0B5C2 First Of(Array) [const] - The value at the start of the specified array.
0B3A0 Flag Position(Team) - The position of a specific team's flag in capture the flag.
0B11A Forward() [const] - Shorthand for the directional vector(0, 0, 1), which points forward.
0F161 Game Mode(Game Mode) [const] - A game mode constant.
0EB1F Global() - 
0B0F9 Global Variable(Variable) - The current value of a global variable, which is a variable that belongs to the game itself.
0C192 Has Spawned(Entity) - Whether an entity has spawned in the world.
0B363 Has Status(Player, Status) - Whether the specified player has the specified status, either from the set status action or from a non-scripted game mechanic.
12B9A Heal Over Time Count() - The current number of Heal Over Time instances started from the Heal Over Time action.
0CC1C Healee() - The player that received the healing for the event currently being processed by this rule.
0CC1A Healer() - The player that dealt the healing for the event currently being processed by this rule.
12B9D Healing Modification Count() - The current number of Healing Modification instances started from the Start Healing Modification Action.
081C2 Health(Player) - The current health of a player, including armor and shields.
11448 Health Of Type(Player, Health) - The current health of the specified player, filtered by the given health type.
0ACAA Hero(Hero) [const] - A hero constant.
10E6A Hero Being Duplicated(Player) - The hero currently being duplicated by the specified player.
0C1FE Hero Icon String(Value) [const] - Converts a hero parameter into a string that shows up as an icon.
0ACA9 Hero Of(Player) - The current hero of a player.
0BB2C Horizontal Angle From Direction(Direction) [const] - The horizontal angle in degrees corresponding to the specified direction vector.
0B27D Horizontal Angle Towards(Player, Position) - The horizontal angle in degrees from a player's current forward direction to the specified position.
0B27F Horizontal Facing Angle Of(Player) - The horizontal angle in degrees of a player's current facing relative to the world.
0B25E Horizontal Speed Of(Player) - The current horizontal speed of a player in meters per second.
0CC1E Host Player() - The player that is currently the host of the custom game.
0CCDC Icon String(Icon) [const] - Allows you to use an icon inside of a string.
10BC7 If-Then-Else(If, Then, Else) [const] - Results in the Then value when the If condition is true; otherwise, results in the Else value.
0C330 Index Of Array Value(Array, Value) [const] - The index of a value within an array or -1 if no such value can be found.
12D5F Index Of String Char(String, Character) - The index of a character within a String or -1 if no such character can be found.
111B7 Input Binding String(Button) [const] - Converts a button parameter into a string that shows up based on the player's input bindings.
0B278 Is Alive(Player) - Whether a player is alive.
0B35C Is Assembling Heroes() - Whether the match is currently in its assemble heroes phase.
0B35F Is Between Rounds() - Whether the match is between rounds.
0B2F3 Is Button Held(Player, Button) - Whether a player is holding a specific button.
0B3A4 Is CTF Mode In Sudden Death() - Whether the current game of capture the flag is in sudden death.
0B268 Is Communicating(Player, Type) - Whether a player is using a specific communication type (such as emoting, using a voice line, etc.).
0B9E5 Is Communicating Any(Player) - Whether a player is using any communication type (such as emoting, using a voice line, etc.).
0B9E8 Is Communicating Any Emote(Player) - Whether a player is using an emote.
12290 Is Communicating Any Spray(Player) - Whether a Player is using a spray.
0B9E7 Is Communicating Any Voice line(Player) - Whether a player is using a voice line.
0B37B Is Control Mode Point Locked() - Whether the point is locked in control mode.
0B289 Is Crouching(Player) - Whether a player is crouching.
0B277 Is Dead(Player) - Whether a player is dead.
0CEDF Is Dummy Bot(Player) - Whether a player is a dummy bot.
10E65 Is Duplicating(Player) - Whether the specified player is duplicating another hero.
0C3E7 Is Firing Primary(Player) - Whether the specified player's primary weapon attack is being used.
0C3E9 Is Firing Secondary(Player) - Whether the specified player's secondary weapon attack is being used.
0B3A1 Is Flag At Base(Team) - Whether a specific team's flag is at its base in capture the flag.
0B3A2 Is Flag Being Carried(Team) - Whether a specific team's flag is being carried by a member of the opposing team in capture the flag.
0B35E Is Game In Progress() - Whether the main phase of the match is in progress (during which time combat and scoring are allowed).
0B292 Is Hero Being Played(Hero, Team) - Whether a specific hero is being played (either on a team or in the match).
0B28B Is In Air(Player) - Whether a player is airborne.
10E62 Is In Alternate Form(Player) - Whether the specified player is currently in an alternate form: - Hammond's ball form - Baby Dva - Bastion's turret and tank forms - Lucio's speed song - Mercy's pistol -
0B1EC Is In Line of Sight(Start Pos, End Pos, Barriers) - Whether two positions have line of sight with each other.
0B35D Is In Setup() - Whether the match is currently in its setup phase.
0B3B1 Is In Spawn Room(Player) - Whether a specific player is in the spawn room (and is thus being healed and able to change heroes).
0BF7C Is In View Angle(Player, Location, View Angle) - Whether a location is within view of a player.
105A0 Is Jumping(Player) - Whether the specified player is jumping.
0B360 Is Match Complete() - Whether the match has finished.
1059A Is Meleeing(Player) - Whether the specified player is meleeing.
0B288 Is Moving(Player) - Whether a player is moving (defined as having a nonzero current speed).
0B378 Is Objective Complete(Number) - Whether the specified objective has been completed.
0BF70 Is On Ground(Player) - Whether a player is on the ground (or other walkable surface).
0B3B2 Is On Objective(Player) - Whether a specific player is currently occupying a payload or capture point.
0BB0B Is On Wall(Player) - Whether a player is on a wall (climbing or riding).
0B3B3 Is Portrait On Fire(Player) - Whether a specific player's portrait is on fire.
11065 Is Reloading(Player) - Whether the specified player is reloading.
0B287 Is Standing(Player) - Whether a player is standing (defined as both not moving and not in the air).
0B359 Is Team On Defense(Team) - Whether the specified team is currently on defense.
0B354 Is Team On Offense(Team) - Whether the specified team is currently on offense.
0B5BA Is True For All(Array, Condition) [const] - Whether the specified condition evaluates to true for every value in the specified array.
0B5BB Is True For Any(Array, Condition) [const] - Whether the specified condition evaluates to true for any value in the specified array.
0C3EB Is Using Ability 1(Player) - Whether the specified player is using ability 1.
0C3ED Is Using Ability 2(Player) - Whether the specified player is using ability 2.
0B9D4 Is Using Ultimate(Player) - Whether a player is using an ultimate ability.
0B35B Is Waiting For Players() - Whether the match is waiting for players to join before starting.
121F2 Last Assist ID() - An ID representing the most recent Start Assist Action that was executed by the Event Player (or executed at the Global level).
0B362 Last Created Entity() - A reference to the last effect or icon entity created by the event player (or created at the global level).
11439 Last Created Health Pool() - An ID representing the most recent Add Health Pool action that was executed by the event player (or executed at the global level).
0C64A Last Damage Modification ID() - An id representing the most recent start damage modification action that was executed by the event player (or executed at the global level).
0B263 Last Damage Over Time ID() - An id representing the most recent damage over time action that was executed by the event player (or executed at the global level).
0B262 Last Heal Over Time ID() - An id representing the most recent heal over time action that was executed by the event player (or executed at the global level).
0FD2A Last Healing Modification ID() - An id representing the most recent start healing modification action that was executed by the event player (or executed at the global level).
0B5C1 Last Of(Array) [const] - The value at the end of the specified array.
0BAFE Last Text ID() - A reference to the last piece of text created by the event player (or created at the global level) via the create hud text or create in-world text action.
0B116 Left() [const] - Shorthand for the directional vector(1, 0, 0), which points to the left.
12BB1 Local Player() - The player being controlled on the end user's computer.
0B342 Local Vector Of(World Vector, Relative Player, Transformation) - The vector in local coordinates corresponding to the provided vector in world coordinates.
11F55 Magnitude Of(vector) [const] - The magnitude (length) of the specified vector
0D415 Map(Map) [const] - A map constant.
11228 Mapped Array(Array, Condition) [const] - A copy of the specified array with the values mapped according to the mapping expression that is evaluated for each element.
0B375 Match Round() - The current round of the match, counting up from 1.
0AD3B Match Time() - The amount of time in seconds remaining in the current game mode phase.
0C418 Max(Value, Value) [const] - The greater of two numbers.
110EA Max Ammo(Player, Clip) - The current max ammo of a player.
081C4 Max Health(Player) - The max health of a player, including armor and shields.
11446 Max Health Of Type(Player, Health) - The max health of the specified player, filtered by the given health type.
0C416 Min(Value, Value) [const] - The lesser of two numbers.
0C410 Modulo(Value, Value) [const] - The remainder of the left-hand operand divided by the right-hand operand.
0C40D Multiply(Value, Value) [const] - The product of two numbers or vectors.
0C324 Nearest Walkable Position(Position) - The position closest to the specified position that can be stood on and is accessible from a spawn point.
0C344 Normalize(Vector) [const] - The unit-length normalization of a vector.
081C3 Normalized Health(Player) - The current health of a player, including armor and shields, normalized between 0 and 1.
0B275 Not(Value) [const] - Whether the input is false (or equivalent to false).
0B594 Null() [const] - The absence of a player.
0B29A Number Of Dead Players(Team) - The number of dead players on a team or in the match.
0B103 Number Of Deaths(Player) - The number of deaths a specific player has earned.
0B101 Number Of Eliminations(Player) - The number of eliminations a specific player has earned.
0B102 Number Of Final Blows(Player) - The number of final blows a specific player has earned.
0B296 Number Of Heroes(Hero, Team) - The number of players playing a specific hero on a team or in the match.
0B297 Number Of Living Players(Team) - The number of living players on a team or in the match.
0B295 Number Of Players(Team) - The number of players on a team or in the match.
0B29B Number Of Players On Objective(Team) - The number of players occupying a payload or control point (either on a team or in the match).
11CB7 Number Of Slots(Team) [const] - The number of slots on a team or in the match.
0B37D Objective Index() - The control point, payload checkpoint, or payload destination currently active (either 0, 1, or 2).
0B355 Objective Position(Number) [const] - The position in the world of the specified objective (either a control point, a payload checkpoint, or a payload destination).
0BB0A Opposite Team Of(Team) [const] - The team opposite the specified team.
0B274 Or(Value, Value) [const] - Whether either of the two inputs are true (or equivalent to true).
0B356 Payload Position() - The position in the world of the active payload.
0B357 Payload Progress Percentage() - The current progress towards the destination for the active payload (expressed as a percentage).
0B3A3 Player Carrying Flag(Team) - The player carrying a particular team's flag in capture the flag.
0C328 Player Closest To Reticle(Player, Team) - The player closest to the reticle of the specified player, optionally restricted by team.
12505 Player Hero Stat(Player, Hero, Stat) - Provides a statistic of the specified player's time playing a specific hero (limited to the current match).
12507 Player Stat(Player, Statistic) - Provides a statistic of the specified player (limited to the current match).
0B0FD Player Variable(Player, Variable) - The current value of a player variable, which is a variable that belongs to a specific player.
0B334 Players In Slot(Slot, Team) - The player or array of players who occupy a specific slot in the game.
0B338 Players On Hero(Hero, Team) - The array of players playing a specific hero on a team or in the match.
0B1E0 Players Within Radius(Center, Radius, Team, Los Check) - An array containing all players within a certain distance of a position, optionally restricted by team and line of sight.
0C32F Players in View Angle(Player, Team, View Angle) - The players who are within a specific view angle of a specific player's reticle, optionally restricted by team.
0B358 Point Capture Percentage() - The current progress towards capture for the active control point (expressed as a percentage).
0B11C Position Of(Player) - The current position of a player as a vector.
0C414 Raise To Power(Value, Value) [const] - The left-hand operand raised to the power of the right-hand operand.
0B59B Random Integer(Min, Max) - A random integer between the specified min and max, inclusive.
0B59A Random Real(Min, Max) - A random real number between the specified min and max.
0B599 Random Value In Array(Array) - A random value from the specified array.
0B598 Randomized Array(Array) - A copy of the specified array with the values in a random order.
0C613 Ray Cast Hit Normal(Start Pos, End Pos, Players To Include, Players To Exclude, Include Player Owned Objects) - The surface normal at the ray cast hit position (or from end pos to start pos if no hit occurs).
0C611 Ray Cast Hit Player(Start Pos, End Pos, Players To Include, Players To Exclude, Include Player Owned Objects) - The player hit by the ray cast (or null if no player is hit).
0C597 Ray Cast Hit Position(Start Pos, End Pos, Players To Include, Players To Exclude, Include Player Owned Objects) - The position where the ray cast hits a surface, object, or player (or the end pos if no hit occurs).
0C421 Remove From Array(Array, Value) [const] - A copy of an array with one or more values removed (if found).
0B117 Right() [const] - Shorthand for the directional vector(-1, 0, 0), which points to the right.
0C354 Round To Integer(Value, Rounding Type) [const] - The integer to which the specified value rounds.
0AD3C Score Of(Player) - The current score of a player.
0C961 Server Load() - Provides a percentage representing the CPU load of the current game instance.
0C997 Server Load Average() - Provides a percentage representing the average CPU load of the current game instance over the last two seconds.
0C996 Server Load Peak() - Provides a percentage representing the highest CPU load of the current game instance over the last two seconds.
0C33C Sine From Degrees(Angle) [const] - Sine of the specified angle in degrees.
0C340 Sine From Radians(Angle) [const] - Sine of the specified angle in radians.
0BB7F Slot Of(Player) - The slot number of the specified player.
0B5C0 Sorted Array(Array, Value Rank) [const] - A copy of the specified array with the values sorted according to the value rank that is evaluated for each element.
11FE7 Spawn Points(Team) - The active spawn points for a team or for the match, provided as an array of position vectors.
0B25D Speed Of(Player) - The current speed of a player in meters per second.
0B260 Speed Of In Direction(Player, Direction) - The current speed of a player in a specific direction in meters per second.
0C356 Square Root(Value) [const] - The square root of the specified value.
0BA60 String(String, {0}, {1}, {2}) [const] - Text formed from a selection of strings and specified values.
12070 String Contains(String, Substring) [const] - Whether the specified string contains the specified substring.
124A2 String Length(String) [const] - The length in characters of the provided string.
12D61 String Replace(String, Pattern, Replacement) - Results in a String Value.
124A6 String Slice(String, Substring Start Index, Substring Length) [const] - The substring of the provided string.
12D60 String Split(String, Separator) - Results in an Array of String Values.
0C40A Subtract(Value, Value) [const] - The difference between two numbers or vectors.
0C7F8 Tangent From Degrees(Angle) [const] - Tangent of the specified angle in degrees.
0C7FD Tangent From Radians(Angle) [const] - Tangent of the specified angle in radians.
0B279 Team Of(Player) - The team of a player.
0B353 Team Score(Team) - The current score for the specified team.
12B9B Text Count() - The current number of Text instances started from the Create HUD Text, Create In-World Text, Create Progress Bar HUD text, or Create Progress Bar In-World Text Action.
0B2F5 Throttle Of(Player) - The directional input of a player, represented by a vector with horizontal input on the x component (positive to the left) and vertical input on the z component (positive
0B361 Total Time Elapsed() - The total time in seconds that have elapsed since the game instance was created (including setup time and transitions).
0AC39 True() [const] - The boolean value of true.
081C5 Ultimate Charge Percent(Player) - The current ultimate ability charge percentage of a player.
0B118 Up() [const] - Shorthand for the directional vector(0, 1, 0), which points upward.
1232B Update Every Frame(Value) [const] - Increases the update frequency of the provided value to once per tick.
0B52A Value In Array(Array, Index) [const] - The value found at a specific element of an array.
0B0F1 Vector(X, Y, Z) [const] - A vector composed of three real numbers (x, y, z) where x is left, y is up, and z is forward.
0B1EB Vector Towards(Start Pos, End Pos) [const] - The displacement vector from one position to another.
0B25C Velocity Of(Player) - The current velocity of a player as a vector.
0BB2B Vertical Angle From Direction(Direction) [const] - The vertical angle in degrees corresponding to the specified direction vector.
0B27E Vertical Angle Towards(Player, Position) - The vertical angle in degrees from a player's current forward direction to the specified position.
0B280 Vertical Facing Angle Of(Player) - The vertical angle in degrees of a player's current facing relative to the world.
0B25F Vertical Speed Of(Player) - The current vertical speed of a player in meters per second.
0B330 Victim() - The player that received the damage for the event currently being processed by this rule.
11059 Weapon(Player) - The currently held weapon of a player.
11CC0 Workshop Setting Combo(Category, Name, Default, Options, Sort Order) - Provides the value (a choice of Custom Strings) of a new option setting that will appear in the Workshop Settings card as a combo box.
11CBC Workshop Setting Hero(Category, Name, Default, Sort Order) - Provides the value of a new hero setting that will appear in the Workshop Settings card as a hero list.
11375 Workshop Setting Integer(Category, Name, Default, Min, Max, Sort Order) [const] - Provides the value of a new integer setting that will appear in the workshop settings card as a slider.
1137B Workshop Setting Real(Category, Name, Default, Min, Max, Sort Order) [const] - Provides the value of a new real number setting that will appear in the workshop settings card as a slider.
1136B Workshop Setting Toggle(Category, Name, Default, Sort Order) [const] - Provides the value (true or false) of a new toggle setting that will appear in the workshop settings card as a checkbox.
0B33A World Vector Of(Local Vector, Relative Player, Transformation) - The vector in world coordinates corresponding to the provided vector in local coordinates.
0B26F X Component Of(Value) [const] - The x component of the specified vector, usually representing a leftward amount.
0B270 Y Component Of(Value) [const] - The y component of the specified vector, usually representing an upward amount.
0B272 Z Component Of(Value) [const] - The z component of the specified vector, usually representing a forward amount.
```

### Inferences
- **Workshop as a server checklist.** Workshop scripts run server-side. Only Local Player is client-local, and "Update Every Frame" mentions server load, tick rate and client-side interpolation. So every action above corresponds to authoritative state that the original server replicates to the client: statuses, health pools, multipliers, forced movement and throttle, facing, camera, HUD and effect entities. A reimplemented server that aims at Workshop parity needs:
  - an entity status set (10 named statuses plus engine-only ones);
  - per-pair damage and healing modifiers;
  - DoT and HoT instances;
  - credit and assist bookkeeping;
  - movement overrides (impulse, acceleration, forced position, throttle transforms, gravity, speed);
  - input injection for bots;
  - spatial queries (raycast, LOS with barrier filtering, walkable-position projection);
  - per-viewer visibility for HUD and world entities.
- **Rule VM.** The 14 events plus 128-variable / 128-subroutine / 32768-element limits bound the VM a server would need to execute imported Workshop code. Reevaluation enums mean many action parameters are continuously re-evaluated server-side expressions.
- **GUID numbering.** The OverPy 12-hex "guid" values (for example 0000000078F6 for Apply Impulse) identify localized display strings, not script opcodes. Lower numbers date from the earliest Workshop (2019) and 12xxx values from 2021. Their mapping to client STU string assets (and a type prefix) is not established. They may help locate Workshop descriptor tables in the 104319 client.
- **Project anchors.** Is In Spawn Room ("being healed and able to change heroes") matches the project's discovery that a component-74 spawn-room flag gates hero change. The "2 m above feet" convention for player LOS/raycasts is a useful default for the project's bot hit tests, which currently use bot center +2.4 m.

### Gaps
- Exact OW1 script-size limit beyond the element count (the "4x" increase in May 2020) and the Extension Points budget: points per disabled slot or map, and the maximum. Patch notes give no numbers. In-game text or workshop.codes would be needed.
- The workshop.codes wiki pages for most actions were not fetched; the semantics above come from Blizzard's in-game descriptions as mirrored by OverPy.
- Whether OverPy's Mar-2022 snapshot exactly matches client 104319's Workshop table (OW1's last patches mid-2022) is unverified. No Workshop data changes appeared in OverPy between 2021-10-06 and the OW2 launch.
- Internal opcode/serialization IDs of Workshop elements in the client (as opposed to string GUIDs) were not found in public sources.

## Status effects and crowd control semantics (mapping to server-side status components)

### Takeaway
The Workshop exposes 10 statuses whose effects partition into four groups:
- full disable (Stunned, Frozen, Asleep, Knocked Down);
- ability lockout (Hacked);
- movement lockout (Rooted);
- protection (Invincible, Unkillable, Phased Out); and
- a cosmetic damage marker (Burning).

Ability-only effects such as anti-heal, discord, nano, damage boost, slow and knockback are not statuses. They are expressed as damage or healing modifications, multipliers and impulses, so a server needs both a status set and a modifier stack.

### Cited Findings
- **Status semantics (workshop.codes wiki):**

  | Status | Effect | Hero source |
  | --- | --- | --- |
  | Hacked | Can't use abilities or ultimates; weapons still work | Sombra |
  | Burning | Visual; no listed restrictions | Ashe dynamite |
  | Knocked Down | Blocks movement, aiming, weapons, abilities | Earthshatter |
  | Asleep | Same as Knocked Down | Sleep Dart |
  | Frozen | Same as Knocked Down | Mei |
  | Stunned | Same as Knocked Down | Flashbang |
  | Unkillable | Health can't drop below 1 | — |
  | Invincible | "does not take damage" | — |
  | Rooted | Blocks movement unless moved by another player/object; aiming unaffected | — |
  | Phased Out | Passes through players and avoids all enemy attacks | Wraith |

  — [workshop.codes wiki: status](https://workshop.codes/wiki/articles/status)
- Forum reports say Phased Out can prevent other statuses (for example Frozen) from being applied on top of it. These are user reports, not official. — [Blizzard forum "Phased out is bugged"](https://us.forums.blizzard.com/en/overwatch/t/phased-out-is-bugged/536143) (via search summary)
- Oct 2020 PTR fixed "inconsistent Phased Out behavior on dead players". — [devtrackers PTR 2020-10-20](https://devtrackers.gg/overwatch/p/a1831caf-overwatch-ptr-patch-notes-october-20-2020)
- **Pre-OW2 (2022-08-27) wiki "Crowd control/Status effect" taxonomy:**
  - **Knock Back:** all explosive weapons except Energy Ball and Sticky Bombs, plus quick melee (small). Knockback into an environmental kill grants ult charge for the remaining health.
  - **Knock Up:** B.O.B., Rising Uppercut, Seismic Slam, Piledriver, Gravitic Flux. The player cannot control movement until landing.
  - **Stun:** Flashbang, Rocket Punch, Shield Bash. Mei's Blizzard and Endothermic Blaster produce a freeze after enough damage ticks, and it can be cleansed.
  - **Knock Down:** Earthshatter, Accretion. It lowers the hitbox and changes states, for example Bastion's Sentry configuration. Similar effects: Sleep Dart ("Ends upon the sleeping hero receiving any damage"), Reinhardt Charge pin, Chain Hook. Mutual collisions of Shield Bash, Charge, Rocket Punch and charging B.O.B. cause knockdown.
  - **Slow:** enemy slows stack with each other but not with self-slows; the greatest applies.
  - **Graviton:** Hyperspheres, Halt!, Graviton Surge (which also disables mobility).
  - **Root:** prevents movement and mobility abilities but allows fighting (Steel Trap; self-roots from Sentry, Cryo-Freeze, Barrage).
  - **Anti-Heal:** Biotic Grenade.
  - **Hack:** Sombra Hack and EMP; "This also disables most passives"; EMP destroys barriers.

  — [Fandom "Status effect" revision 2022-08-27 via API](https://overwatch.fandom.com/api.php?action=query&prop=revisions&titles=Crowd_control&rvstart=2022-09-30T00:00:00Z&rvdir=older&rvlimit=1&rvprop=content|timestamp&rvslots=main&format=json&redirects=1)
- **Knockback is a first-class event channel:** the Player Dealt/Received Knockback events, the Set Knockback Dealt/Received multipliers, and per-hero custom settings such as "Boosters Knockback Scalar [0–400%]", "Helix Rockets Knockback Scalar [0–400%]", "Grappling Claw/Minefield Knockback Scalar" and "Particle Cannon Secondary Knockback Scalar". Mei has "Weapon Freeze Duration Scalar [20–500%]", "Weapon Freeze Minimum", "Weapon Freeze Rate Scalar", "Freeze Stacking" and "Blizzard Freeze Minimum / Rate Scalar". — [OPY-O](https://github.com/Zezombye/overpy/blob/b24553ab0120ea4fcc040787e0b124ed617b9dda/src/data/other.js); [OPY-S](https://github.com/Zezombye/overpy/blob/b24553ab0120ea4fcc040787e0b124ed617b9dda/src/data/customGameSettings.js)
- Workshop "dynamic effect" and "effect" constants name the client-side visuals of statuses: "Sombra Hacked Starting/Looping Effect", "Ana Sleeping Effect/Sound", "Mei Frozen Effect/Sound", "Cassidy Flashbang Stunned Effect", "Ana Biotic Grenade No Healing Effect", "Zenyatta Orb of Discord Target Sound", "Ana Nano Boosted Effect/Sound", "Mercy Damage Boosted Effect", "Baptiste Immortality Field Protected Effect". The Mar-2021 "Buff/Debuff Status Effects" extensions gate these visuals. — [OPY-C](https://github.com/Zezombye/overpy/blob/b24553ab0120ea4fcc040787e0b124ed617b9dda/src/data/constants.js); [retail notes 2021-03-09](https://devtrackers.gg/overwatch/p/0324dfd7-overwatch-retail-patch-notes-march-9-2021)

### Inferences
- Discord (damage taken +X%), nano (damage dealt/received modifiers), Mercy damage boost and anti-heal are not Workshop statuses. They map onto the same multiplier channels as Set Damage Received / Start Damage Modification / Set Healing Received (0%). Their visuals are separate effect assets. Server model: a status set plus a stack of signed multipliers per (receiver, source), plus cosmetic effect attachments.
- Asleep ending on any damage is an ability-side rule (Sleep Dart). Whether the Workshop "Asleep" status also breaks on damage is not stated in the sources found.

### Gaps
- Exact stacking and precedence rules among statuses (e.g. Invincible vs Unkillable; Phased Out blocking new statuses) are not officially documented.
- "Boop" rules for knockback magnitude, vertical component and tank resistance (e.g. Hero Bot "tanks receive less knockback") have no authoritative numeric source here.

## (2) Custom games: lobby/settings structure, browser, presets, share codes, team sizes

### Takeaway
An OW1 custom game is a settings document: Main (Description, Mode Name), Lobby, Modes (General plus per-mode), Maps, Heroes (General, per-hero and per-ability) and Workshop (Extensions, settings, script). It is identified by an uploaded share code that the owner can re-upload since May 2020. The game browser got Popular/Favorites/Recent/All tabs and search-by-share-code in Aug 2021. The settings schema with exact ranges is machine-readable in OverPy.

### Cited Findings
- **Settings schema top level** (OverPy): `main`, `lobby`, `gamemodes`, `heroes`, `workshop`, `extensions`. Main has Description and Mode Name. — [OPY-S](https://github.com/Zezombye/overpy/blob/b24553ab0120ea4fcc040787e0b124ed617b9dda/src/data/customGameSettings.js)
- **Lobby settings** (default in parentheses), from [OPY-S](https://github.com/Zezombye/overpy/blob/b24553ab0120ea4fcc040787e0b124ed617b9dda/src/data/customGameSettings.js):
  - Map Rotation: After Mirror Match / After Game / Paused.
  - Return To Lobby: Never / After Game / After Mirror Match.
  - Team Balancing: Off / After Mirror Match / After Game.
  - Swap Teams After Match (Yes).
  - Max Team 1 Players and Max Team 2 Players: int 0–12 (6).
  - Max FFA Players: 0–12 (12).
  - Max Spectators: 0–12 (2).
  - Allow Players Who Are In Queue (No), Use Experimental Update If Available (No).
  - Match Voice Chat (Disabled), Pause Game On Player Disconnect (No).
  - Data Center Preference (Best Available plus a regional list).
  - Minimum Latency ms (0).
- **General mode settings** (default in parentheses), from [OPY-S](https://github.com/Zezombye/overpy/blob/b24553ab0120ea4fcc040787e0b124ed617b9dda/src/data/customGameSettings.js):
  - Enemy Health Bars (On), Kill Cam (On), Kill Feed (On), Skins (On).
  - Game Mode Start: All Slots Filled / Immediately / Manual.
  - Health Pack Respawn Time Scalar 10–500%.
  - Spawn Health Packs: Mode Dependent / Enabled / Disabled.
  - Allow Hero Switching (On).
  - Hero Limit: Off / 1 Per Team / 2 Per Team / 1 Per Game / 2 Per Game.
  - Limit Roles: Off / 2 Of Each Role Per Team.
  - Respawn As Random Hero (Off), Respawn Time Scalar 0–100%.
  - Enabled/Disabled maps.
- **Per-mode settings**, from [OPY-S](https://github.com/Zezombye/overpy/blob/b24553ab0120ea4fcc040787e0b124ed617b9dda/src/data/customGameSettings.js):
  - **Assault:** Capture Speed 10–500%, Competitive Rules.
  - **Control:** Capture Speed; Limit Valid Control Points (All / First / Second / Third); Score To Win 1–3 (2); Scoring Speed 10–500%.
  - **Escort:** Payload Speed 10–500%. **Hybrid:** Capture plus Payload speed.
  - **Elimination / Freezethaw Elimination:**
    - Hero Selection Time 20–60; Score To Win 1–9 (3).
    - Restrict Previously Used Heroes: Off / After Round Won / After Round Played.
    - Hero Selection: Any / Limited / Random / Mirrored Random; Limited Choice Pool: team size +0..+3.
    - Capture Objective Tiebreaker; Tiebreaker After 30–300 s (105); Time To Capture 1–7 (3).
    - Draw After 60–300 s (135); Reveal Heroes After 0–180 s (75).
  - **FFA Deathmatch:** Game Length 5–15 min (10), Score To Win 1–5000 (20), Self Initiated Respawn.
  - **TDM:** Score 1–200 (30), Mercy Resurrect Counteracts Kills, Imbalanced Team Score To Win, Team 1 and Team 2 Score To Win.
  - **Bounty Hunter:** Base Score for Killing a Bounty Target 0–1000 (300), Score per Kill (100), Score per Kill as Bounty Target (300), Bounty Increase per Kill, Bounty Target Count 1.
  - **CTF:**
    - Blitz Flag Locations, Damage Interrupts Flag Interaction.
    - Flag Carrier Abilities: All / None / Restricted.
    - Flag Dropped Lock Time 0–10 (5), Flag Pickup Time 0–5 (0), Flag Return Time 0–5 (4), Flag Score Respawn Time 0–20 (15).
    - Game Length 5–15 (8), Respawn Speed Buff Duration 0–60, Score To Win 1–9 (3), Team Needs Flag At Base To Score.
  - **Skirmish:** Limit Valid Control Points.
  - **Practice Range:** **Spawn Training Bots (On), Training Bot Respawn Time Scalar 10–500%, Training Partner (On)**.
  - Also present: Junkenstein's Revenge, Lúcioball, Yeti Hunter, Snowball FFA / Mei's Snowball Offensive.
- **Hero settings** (each available globally, per team and per hero), from [OPY-S](https://github.com/Zezombye/overpy/blob/b24553ab0120ea4fcc040787e0b124ed617b9dda/src/data/customGameSettings.js):
  - **General-only:** Ability Cooldown Time 0–500%; Ultimate Generation 10–500%; Ultimate Generation Combat 0–500% and Passive 0–500%; Ultimate Ability.
  - **General and per-hero:**
    - Quick Melee, Spawn With Ultimate Ready, Ultimate Duration 25–500%, Infinite Ultimate Duration.
    - Damage Dealt / Received, Healing Dealt / Received, Health: each 10–500%.
    - Jump Vertical Speed 25–800%, Movement Gravity 25–400%, Movement Speed 50–300%.
    - Projectile Gravity / Speed 0–500%.
    - Receive Headshots Only, Primary Fire, Ammunition Clip Size Scalar 25–500%, No Ammunition Requirement.
  - **Per-ability:** On/Off; Cooldown Time 0–500%; resource abilities have Maximum Time 20–500% and Recharge Rate 0–500%. Per-hero ultimate generation; Secondary Fire; No Automatic Fire; No Scope.
  - **Hero-specific examples:** D.Va "Spawn Without Mech", Wrecking Ball "Roll Always Active", Mercy "Weapons Enabled", plus knockback scalars.
  - Enabled/Disabled heroes lists.
- **Share codes:**
  - May 19, 2020: "Existing Share Codes can now be re-uploaded with new Custom Game Settings (requires same original owner)". An owner may "re-upload settings to a code that has expired", making it valid again.
  - Same patch: "Skirmish can now override which Control Points are valid on Control Maps". The Game Browser filter "Only Show Games with Space For Party" options were renamed "room in game" / "room in lobby".
  — [Blizzard live patch notes 2020/05](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2020/05)
- **Custom Game Browser (Aug 12, 2021 PTR):** tabs Popular ("most-played modes as well as modes that have started to trend"), Favorites (star icon), Recent and All Games (the standard lobby list). A new "Mode Name" setting "will be used to represent modes in the Custom Game Browser tabs". "We've also added the ability to search for lobbies by share code." — [Blizzard PTR patch notes 2021/08](https://overwatch.blizzard.com/en-us/news/patch-notes/ptr/2021/08)
- Mar 2021 Social options added "Custom Game Invite Filter" and "Custom Game Invite Requests". — [retail notes 2021-03-09](https://devtrackers.gg/overwatch/p/0324dfd7-overwatch-retail-patch-notes-march-9-2021)
- 2017 wiki revision: the Game Browser was reached from the Arcade menu, where players "create their own custom game, or find and join another player's game". — [Fandom Game Browser (2017 rev) via API](https://overwatch.fandom.com/api.php?action=query&prop=revisions&titles=Game_Browser&rvstart=2022-09-30T00:00:00Z&rvdir=older&rvlimit=1&rvprop=content|timestamp&rvslots=main&format=json)
- **Current (OW2-era) wiki description of the lobby, partly applicable to OW1:**
  - Lobby buttons are Move, Settings, Invite and Add AI.
  - Visibility is Friends Only (default) / Invite Only / Everyone; "Everyone" requires Endorsement Level 3.
  - Spectator slots are configurable up to 12 (default 2).
  - Settings tabs: Presets, Lobby, Modes, Maps, Heroes, Workshop and Summary.
  - Preset groups: Saved, Standard, Arcade and Workshop examples. The examples are Molten Floor, One Ultimate, Hide and Seek, Double Jump, Fire Dome, Balanced Mystery Heroes, Mirrored Deathmatch, Zombie, Hero Gauntlet and Server Load.
  - "AI only works on standard game modes."
  - **OW2-only items on that page:** Push, Flashpoint, Clash, the 8 AI difficulties, and "Recommended Role AI" 1/2/2.
  — [Fandom "Custom Game" (current wikitext)](https://overwatch.fandom.com/wiki/Custom_Game)

### Inferences
- Team sizes:
  - OverPy's schema allows Max Team players 0–12, but Create Dummy Bot caps bots at 6 per team / 12 FFA. The standard OW1 lobby was 6v6 + spectators (default 2, up to 12) or FFA up to 12.
  - The OverPy 0–12 per-team range may reflect the 12-slot index space (Slot 0–11 in event filters) rather than a confirmed live 12v12 option. Treat 12-per-team as unverified for OW1.
  - Extension points come from disabling player slots, which confirms that slot count is a server-resource budget.
- A settings document plus share code is server/service-side state (the "lobby service"), independent of the game-server instance. A reimplementation needs a share-code store (upload / re-upload by owner, expiry) and a browser index (popular / trending / recent / favourites / search). The OW1 client already has UI for these, which the project could exercise through lobby messages.
- The practice-range mode itself has only three custom settings (Spawn Training Bots, Training Bot Respawn Time Scalar, Training Partner). These are the natural knobs for the project's server-side training bots.

### Gaps
- No primary source found for when custom-game share codes were introduced; the May 2020 notes treat them as existing. Code format and length are unverified. Six-character codes are documented for replays, not necessarily for custom-game codes.
- "Skirmish" semantics (no-score free roam before matchmaking, available as a preset and mode) were not separately sourced.
- Exact per-team maximum (6 vs 12) for OW1 live lobbies is not confirmed by a Blizzard source.

## (3) AI bots: Practice vs AI, custom-game AI, Workshop dummy bots, Practice Range training bots, Blizzard talks

### Takeaway
OW1 had three distinct bot systems:
- **Hero AI** ("Practice vs AI" and custom-game "Add AI"): 12 heroes; Easy/Medium/Hard scale damage 25/50/100% with no headshots; Assault, Control, Escort and Hybrid only.
- **Workshop dummy bots:** zero AI; every motion comes from script input-injection actions.
- **Practice Range training bots:** scripted map entities, 200 HP in OW1, with simple shooting/moving patterns and custom-game respawn and enable settings.

No Blizzard GDC talk on OW1 bot AI was found. The relevant public engineering talk is Dan Reed's GDC 2017 "Networking Scripted Weapons and Abilities" (Statescript).

### Cited Findings
- **OW1 Practice vs AI (wiki revision of 2022-03-09):**
  - 6 players vs an AI team, under Training.
  - "the party leader must select a difficulty: Easy, Medium, or Hard. Higher difficulties improve accuracy and damage output of the AI. Easy deals 25% damage, Medium 50%, and Hard 100%. Bots cannot deal critical damage through headshots."
  - AI heroes: "Roadhog, Zarya, Bastion, Cassidy, Mei, Reaper, Soldier: 76, Sombra, Torbjörn, Ana, Lúcio, and Zenyatta".
  - "The game will select one of the four following modes at random: Assault, Control, Escort, and Hybrid".
  - It is the "sole mode with matchmaking that contains bots" except special events, and "always yields 90% experience, regardless of difficulty".
  — [Fandom "Practice vs. AI" rev 2022-03-09 via API](https://overwatch.fandom.com/api.php?action=query&prop=revisions&titles=Practice_vs._AI&rvstart=2022-09-30T00:00:00Z&rvdir=older&rvlimit=1&rvprop=content|timestamp&rvslots=main&format=json)
- An early (2016-era) player thread lists only six bot heroes: Roadhog, Zenyatta, Reaper, Soldier 76, Bastion, Zarya. — [GameFAQs thread](https://gamefaqs.gamespot.com/boards/878359-overwatch/73842715) (via search summary; anecdotal)
- **OW2 changes (flag, not OW1):**
  - 5v5 against 1 Tank / 2 Damage / 2 Support bots.
  - Difficulties renamed Casual / Hard / Lethal; custom games offer Beginner, Practice, Casual, Hard, Lethal, Extreme, Ultimate and Aimbot.
  - Most heroes have AI, with exceptions such as D.Va, Wrecking Ball, Echo and Pharah.
  — [Fandom "Practice vs. AI" current](https://overwatch.fandom.com/wiki/Practice_vs._AI); [Fandom "Training" current](https://overwatch.fandom.com/wiki/Training)
- **Bot behaviour characteristics** (current wiki; mostly OW2 bots, but some behaviours likely predate it):
  - Bots "cannot crouch".
  - They cannot use movement abilities outside spawn, except e.g. Lúcio's Amp It Up and Soldier's Sprint.
  - They "only jump to navigate map terrain; never in combat".
  - They "immediately attempt to find cover when specific Ultimates are activated by the enemy".
  - They switch heroes after a number of deaths, but not if their ultimate is ready.
  - They "ignore enemies slept by Sleep Dart".
  - They "greet each other in the spawn room during setup" and call out ultimate readiness.
  - They "may retreat to the spawn room and wait for allies" if outnumbered.
  - Damage and support bots follow the tank to the objective (citation needed on the wiki).
  - Listed abilities bots never use: Baptiste Exo Boots, Genji Cyber-Agility, Hanzo/Kiriko wall climb, Lúcio Wall Ride, Mercy Angelic Descent, Reaper Shadow Step, Symmetra Teleporter, Widowmaker Grappling Hook, Zenyatta alt fire.
  - Bots "destroy any breakable terrain object they come into contact with" and "cannot be moved around by human players walking into them, but they can be bodyblocked".
  — [Fandom "Practice vs. AI" current wikitext](https://overwatch.fandom.com/wiki/Practice_vs._AI)
- Custom-game "Add AI" (lobby button) lets the host pick hero or role, difficulty, count and team. "AI only works on standard game modes" (current wiki; the OW1 lobby had the same Add AI button with Easy/Medium/Hard). — [Fandom "Custom Game"](https://overwatch.fandom.com/wiki/Custom_Game)
- **Workshop dummy bots:**
  - Create Dummy Bot(Hero, Team, Slot −1 = first free, Position, Facing). "This bot will only move, fire, or use abilities if executing workshop actions."
  - Caps are 6 per team / 12 FFA regardless of lobby settings. The Mar-2021 "Spawn More Dummy Bots" extension costs 2 points.
  - Bots are driven through Start Throttle In Direction / Start Forcing Throttle, Start Facing, Press / Start Holding Button, Set Facing, Teleport, Start Forcing Player Position and similar actions.
  - Navigation helpers: Nearest Walkable Position ("accessible from a spawn point"), Is In Line of Sight, Ray Cast Hit Position.
  - Is Dummy Bot identifies them; Start Forcing Dummy Bot Name works "with AI and dummy bots".
  — [OPY-A](https://github.com/Zezombye/overpy/blob/b24553ab0120ea4fcc040787e0b124ed617b9dda/src/data/actions.js); [OPY-V](https://github.com/Zezombye/overpy/blob/b24553ab0120ea4fcc040787e0b124ed617b9dda/src/data/values.js); [OPY-S](https://github.com/Zezombye/overpy/blob/b24553ab0120ea4fcc040787e0b124ed617b9dda/src/data/customGameSettings.js)
- **Community "AI" built from those primitives:** the long-running "Legendary Custom Bots" workshop mode reached 300 rules in V10 and adds per-hero bot behaviours (e.g. Brigitte melee, Mercy follows player). — [Blizzard forum V10 thread](https://us.forums.blizzard.com/en/overwatch/t/custom-legendary-bots-v10-300-rules-final-patch-notes-trailer/431370); [V11](https://us.forums.blizzard.com/en/overwatch/t/patch-notes-legendary-custom-bots-v11/546765) (titles/snippets via search)
- **Practice Range (OW1, 2019 revision):** "four friendly and eleven hostile training bots on the map that perform various actions, such as staying still, shooting, and moving", plus range markers in metres. — [Fandom "Practice Range" rev 2019-01-03 via API](https://overwatch.fandom.com/api.php?action=query&prop=revisions&titles=Practice_Range&rvstart=2022-09-30T00:00:00Z&rvdir=older&rvlimit=1&rvprop=content|timestamp&rvslots=main&format=json)
- **Training bot (2022-04 revision):**
  - Health 200 in OW1; the current OW2 page says 250.
  - Weapon "Duo Cannons": projectile, 8 damage per projectile, 60 m/s, 4 projectiles/s, ammo 8, reload 1 s, headshots allowed.
  - Voice actor Aaron Phillips.
  — [Fandom "Training bot" rev 2022-04-19 via API](https://overwatch.fandom.com/api.php?action=query&prop=revisions&titles=Training_bot&rvstart=2022-09-30T00:00:00Z&rvdir=older&rvlimit=1&rvprop=content|timestamp&rvslots=main&format=json); [current](https://overwatch.fandom.com/wiki/Training_bot)
- **Current (OW2) Practice Range page:**
  - Bot types: Training Bot, Friendly Bot (200 HP), Standard Bot (250 HP; only two shoot), Friendly Heavy Bot, Tank Bot (200/400 HP with shield), Sniper Bot (200 HP, "lock on sniper"), Rocket Bot (200 HP) and a Hero Bot ("cannot use abilities, passive abilities still apply").
  - Moving bots "move in a looping pattern"; swapped-to-friendly moving bots "slowly lose health until they reach a minimum".
  - Consoles toggle bot types. Other features: ultimate accelerators, a jump pad and a firing range.
  - Many of these features postdate OW1, so verify against the 104319 map.
  — [Fandom "Practice Range" current](https://overwatch.fandom.com/wiki/Practice_Range)
- **Patch history of training bots:**
  - March 21, 2017: destroyed training bots appear in the kill feed.
  - May 3, 2018: fixed bots not returning "to their normal position and behavior after an ability hit them, such as Lúcio's Soundwave".
  — [Liquipedia March 21, 2017 patch](https://liquipedia.net/overwatch/March_21,_2017_Patch); [Blizzard forum May 3 2018 notes](https://us.forums.blizzard.com/en/overwatch/t/all-overwatch-patch-notes-may-3-2018/87211/4) (via search summary)
- **Blizzard talks:**
  - Dan Reed, GDC 2017, "Networking Scripted Weapons and Abilities": Overwatch's proprietary visual scripting language Statescript drives hero weapons and abilities. It covers "how prediction and replication of script behavior is automated", addressing "responsiveness, security, bandwidth usage, seamlessness, and ease of implementation". — [GDC Vault 1024041](https://gdcvault.com/play/1024041/Networking-Scripted-Weapons-and-Abilities); [GDC preview article](https://www.gamedeveloper.com/design/attend-gdc-and-see-how-blizzard-scripts-i-overwatch-i-s-weapons-and-powers)
  - A GDC AI Summit navigation session ("AI Navigation: It's Not a Solved Problem – Yet") includes Blizzard's James Anhalt. It is a 2011-era StarCraft II-period talk with no evidence of Overwatch content. — [GDC Vault 1014514](https://gdcvault.com/play/1014514/AI-Navigation-It-s-Not)

### Inferences
- **Hero AI is server-side and uses the same input-injection path as Workshop dummy bots.** Workshop dummy bots need input injection, "AI and dummy bots" share the name-forcing path, and bots are "Players" in slots. To the client, a bot is an ordinary replicated player entity in a team slot, and its control loop lives entirely on the server. This matches the project's finding that skinned non-controlled hero entities render and that the server must drive their movement snapshots.
- **Navmesh existence.** Bots navigate maps, only jumping "to navigate map terrain", and the Workshop exposes Nearest Walkable Position "accessible from a spawn point". The original server therefore had per-map navigation/walkability data and connectivity to spawn points. Whether that data ships in client assets is not established. A reimplementation will likely need to generate its own navmesh (for example Recast over map collision) and expose raycast/LOS against map geometry and barriers.
- **Minimum hero-AI behaviour set for OW1 parity:**
  - follow lane or path to the objective, with supports trailing the tank;
  - target selection (support-priority is uncited);
  - aim with difficulty-scaled accuracy and damage multipliers (25/50/100%) and no crits;
  - use a limited ability set (no mobility outside spawn);
  - take cover on enemy ultimate;
  - switch heroes after deaths;
  - perform spawn-room social emotes and callouts;
  - only on Assault, Control, Escort and Hybrid.
- **Practice Range for the project:** model fixed-position targets (200 HP), shooting bots (Duo Cannons parameters above), moving bots on looping paths and one training-partner/hero bot, with respawn timing scaled by "Training Bot Respawn Time Scalar".

### Gaps
- The patch timeline for when each OW1 hero became available as AI (6 heroes at launch → 12 by 2022) was not found in primary patch notes.
- No Blizzard GDC or tech talk specifically on Overwatch bot AI, behaviour trees or navmesh was found. OW2 PvE / Hero Mastery AI talks were not located either.
- The OW1 custom-game AI difficulty list: OW1 Practice vs AI used Easy/Medium/Hard; whether custom games exposed more tiers in OW1 is unverified.
- OW1 Practice Range per-bot list, health and moving-bot speeds/paths (as opposed to the OW2 page) need confirmation from the 104319 map data.
- Tim Ford's GDC 2017 "Overwatch Gameplay Architecture and Netcode" (ECS, input prediction) is highly relevant but was not fetched or verified in this session.
