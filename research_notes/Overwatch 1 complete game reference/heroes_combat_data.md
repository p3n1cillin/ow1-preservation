# Overwatch 1 final-state hero combat data (client 1.74.0.0.104319, ~Aug-Sept 2022)

Method note for the report writer: Wayback Machine, wiki.gg and fandom HTML were blocked to the fetch tool, but the overwatch.fandom.com MediaWiki API returned raw wikitext of historical revisions. Every hero's `{{Ability_details}}` templates were parsed mechanically from a dated revision (oldid linked per hero below). The late-July 2022 revisions were used because they contain the most precise frame data (e.g. "restores ammo after 0.592 s"). They were compared field by field against mid-April 2022 revisions, taken before the OW2 PvP beta of 26 Apr 2022. Two heroes' July pages had been rewritten with OW2-beta kits (Doomfist, Orisa), so their April revisions are used instead. Cassidy's July page also had an extra OW2 "Magnetic Grenade" block, which was dropped. All other April-to-July differences are measurement refinements (listed under Q1 findings), not balance changes. Raw wikitext is cached at /tmp/claude-0/-home-user-ow1-preservation/424abc39-411f-5f50-a73a-3d32fd754ab0/scratchpad/hc/ (heroes/, heroes_apr/, heroes_feb/, gen/). There is also a generator script tables_final.py.

## Q1. Final OW1 numbers per hero (with sources)

### Takeaway
The last OW1 balance changes on the live client came on 6 Jan 2022 and 25 Jan 2022 (a Mercy Resurrect quality-of-life change). Live patches after that date were events and bug fixes only, so the wiki values from Feb–July 2022 below describe build 104319 hero data. The exception is any wiki field that missed a patch, such as Earthshatter, listed under Inferences. Every number in the tables comes from the cited fandom revision. Wiki conventions: "X - Y" damage means falloff minimum to maximum. "restores ammo after N s" means the ammo is credited before the reload animation ends. "ult_req" is the ultimate cost in points.

### Cited Findings

#### Health pools summary (from each hero's infobox in the cited revisions; cross-checked with the Hit points page)
| Hero | Health | Armor | Shields | Notes |
|---|---|---|---|---|
| Ana | 200 | | | |
| Ashe | 200 | | | B.O.B. 1200 HP |
| Baptiste | 200 | | | |
| Bastion | 200 | 100 | | Ironclad: 20% damage reduction in Sentry/Tank |
| Brigitte | 150 | 50 | | |
| Cassidy | 225 | | | Increased from 200 to 225 on 29 Oct 2020 |
| D.Va | 300 (mech) / 150 (pilot) | 300 (mech) | | Mech changed from 200/400 to 300/300 on 10 Dec 2020 |
| Doomfist | 250 | | | Up to 150 temporary shields (The Best Defense) |
| Echo | 200 | | | |
| Genji | 200 | | | |
| Hanzo | 200 | | | |
| Junkrat | 200 | | | |
| Lúcio | 200 | | | |
| Mei | 250 | | | |
| Mercy | 200 | | | |
| Moira | 200 | | | |
| Orisa | 200 | 250 | | |
| Pharah | 200 | | | |
| Reaper | 250 | | | |
| Reinhardt | 300 | 200 | | Armor reduced from 250 to 200 on 22 Apr 2021 (total 500) |
| Roadhog | 600 | | | Enemies gain 25% less ultimate charge from damaging him |
| Sigma | 300 | | 100 | Kinetic Grasp: up to 400 temporary shields |
| Soldier: 76 | 200 | | | |
| Sombra | 200 | | | |
| Symmetra | 100 | | 125 | |
| Torbjörn | 200 | 50 | | Overload: +100 temporary armor |
| Tracer | 150 | | | |
| Widowmaker | 175 | | | Reduced from 200 on 29 Oct 2020 |
| Winston | 350 | 150 | | Changed from 400/100 to 350/150 on 18 Feb 2021; Primal Rage 850 HP |
| Wrecking Ball | 500 | 100 | | Adaptive Shield: 100 + 75 per enemy temporary shields |
| Zarya | 200 | | 200 | |
| Zenyatta | 50 | | 150 | |
Sources: hero infoboxes below, plus [Hit points, fandom oldid 125959 (21 Jul 2022)](https://overwatch.fandom.com/wiki/Hit_points?oldid=125959). Change dates come from each hero's "Balance Change Logs" in the April 2022 revisions. Every row above was re-checked against the parsed infobox fields.

#### Ultimate costs (points) — [Ultimate ability, fandom oldid 123286 (18 Feb 2022)](https://overwatch.fandom.com/wiki/Ultimate_ability?oldid=123286)
| Cost | Ultimates |
|---|---|
| 319.2 | Call Mech (D.Va pilot) |
| 1260 | Pulse Bomb |
| 1400 | EMP |
| 1540 | Earthshatter, Infra-Sight, Minefield, Primal Rage, Self-Destruct |
| 1610 | Blizzard |
| 1680 | Deadeye, Dragonstrike, Meteor Strike, Photon Barrier, Supercharger |
| 1820 | Valkyrie |
| 1925 | RIP-Tire |
| 1932 | Dragonblade |
| 1960 | Gravitic Flux |
| 2100 | Barrage, Death Blossom, Graviton Surge, Nano Boost |
| 2142 | Molten Core |
| 2240 | B.O.B., Whole Hog |
| 2254 | Duplicate |
| 2310 | Amplification Matrix, Configuration: Tank, Tactical Visor, Transcendence |
| 2800 | Coalescence, Rally |
| 2940 | Sound Barrier |

#### Per-hero ability tables (parsed verbatim from wiki templates)
Units: m, s, m/s. "pspeed" is projectile speed and "mspeed" is a movement speed modifier. "headshot ✓/✕" says whether the attack can crit. "spread" is in degrees. "[...]" is the wiki's tooltip text (frame data).


#### Ana
Source: [Ana, fandom late-July 2022 revision, oldid 126455](https://overwatch.fandom.com/wiki/Ana?oldid=126455)

Pool/role: role Support, health 200

| Ability | Stats |
|---|---|
| Biotic Rifle | **ability_type**: Weapon; **shot_type**: proj (unscoped) / hitscan (scoped); **damage**: 70 over 0.576 seconds [-2.24 hp, wait 0.192 s. -26.88, wait 0.192 s. -26.88, wait 0.192 s. -14.]; **heal**: 70 over 0.576 seconds [+2.24 hp, wait 0.192 s. +26.88, wait 0.192 s. +26.88, wait 0.192 s. +14.]; **headshot**: ✕; **fire_rate**: 1 shot every 0.8 seconds / 1.25 shots per second; **ammo**: 12; **reload_time**: 1.5 seconds animation [restores ammo after 0.592 seconds]; **spread**: Pinpoint; **pspeed**: 125 meters per second (unscoped); **radius**: 0.2 meters radius; **cast_time**: 0.5 seconds scoping in; **duration**: 0.576 second effect; **mspeed**: -65% [1.925 meters per second] penalty (scoped) |
| Sleep Dart | **ability_type**: Ability; **key**: ability 1; **shot_type**: proj; **damage**: 5; **headshot**: ✕; **spread**: Pinpoint; **pspeed**: 60 meters per second; **radius**: 0.2 meters radius; **cast_time**: 0.3 seconds; **duration**: 1.5 - 5 seconds; **cooldown**: 12 seconds |
| Biotic Grenade | **ability_type**: Ability; **key**: ability 2; **shot_type**: arc; **damage**: 60; **heal**: 100; **headshot**: ✕; **pspeed**: 30 meters per second; **radius**: 4 meters; **duration**: 4 seconds; **cooldown**: 10 seconds |
| Nano Boost | **ability_type**: Ultimate Ability; **shot_type**: targeted (allies); **damage**: +50% damage buff; **heal**: 250 health; **range**: 40 meters; **cast_time**: 0.144 seconds; **duration**: 8 seconds; **damage_reduction**: 50%; **ult_req**: 2100 points |

#### Ashe
Source: [Ashe, fandom late-July 2022 revision, oldid 126473](https://overwatch.fandom.com/wiki/Ashe?oldid=126473)

Pool/role: role Damage, health 200

| Ability | Stats |
|---|---|
| The Viper | **ability_type**: Weapon (Hip Fire); **shot_type**: hitscan; **damage**: 12 - 40; **damage_falloff_range**: 20 to 40 meters; **headshot**: ✓; **fire_rate**: 0.24 second recovery / (4 shots per second); **ammo**: 12; **reload_time**: 0.5 seconds (initial animation)  / +0.25 seconds per bullet  / 3.5 seconds (Full reload animation); **spread**: Max: 1.85 degrees |
| The Viper | **ability_type**: Weapon (ADS); **key**: secondary fire; **shot_type**: hitscan; **damage**: 22.5 - 75; **damage_falloff_range**: 30 to 50 meters; **headshot**: ✓; **fire_rate**: 0.64 second recovery / (~1.54 shots per second); **ammo**: 12; **reload_time**: 0.5 seconds (initial animation)  / +0.25 seconds per bullet  / 3.5 seconds (Full reload animation); **spread**: Pinpoint; **mspeed**: -25% [4.125 m/s] penalty |
| Dynamite | **ability_type**: Ability; **key**: ability 2; **shot_type**: arc; **damage**: Explosion: 20 - 50 / Burn: 100 [Deals 3.84 damage every 0.192 seconds.] / Self: 50% [60 - 75]; **pspeed**: 25 meters per second; **radius**: 5 meter radius; **cast_time**: 0.16 seconds (dynamite start exists) / 2 seconds for explode after landing; **duration**: 5 seconds (burn); **cooldown**: 12 seconds |
| Coach Gun | **ability_type**: Ability; **key**: ability 1; **shot_type**: shotgun (hitscan); **damage**: 6 per pellet / 90 per shot; **headshot**: ✕; **pellets**: 15; **range**: 9.4 meters (self-knock back); **cast_time**: 0.016 second; **cooldown**: 10 seconds |
| B.O.B. | **ability_type**: Ultimate Ability; **shot_type**: hitscan (arm cannon); **damage**: Charge: 120 / Arm cannon: 112 per second, 14 per bullet, 1092 overall [78 bullets]; **fire_rate**: 8 bullets per second; **range**: 70 meters (charge) / 40 meters (arm cannons); **duration**: 10 seconds (after collision); **mspeed**: 15 meters per second; **health**: 1200; **ult_req**: 2240 points |

#### Baptiste
Source: [Baptiste, fandom late-July 2022 revision, oldid 126495](https://overwatch.fandom.com/wiki/Baptiste?oldid=126495)

Pool/role: role Support, health 200

| Ability | Stats |
|---|---|
| Exo Boots | **ability_type**: Passive Ability; **key**: crouch; **range**: 9.1 meters (full charge) |
| Biotic Launcher | **ability_type**: Weapon (Primary Fire); **shot_type**: hitscan; **damage**: Three-round-burst / 7.2 - 24 per round; **damage_falloff_range**: 25 to 45 meters; **headshot**: ✓; **fire_rate**: 1 burst per 0.58 seconds [1 round insta, delay between next (x2) 0.096 second. 0.576 second recovery after first round]; **ammo**: 45; **reload_time**: 1.5 seconds animation [restores ammo after 0.896 second] |
| Biotic Launcher | **ability_type**: Weapon (Secondary Fire); **shot_type**: arc; **heal**: 70 (direct hit) / 50 (explosion); **fire_rate**: 1 shot per 0.9 seconds; **ammo**: 10; **reload_time**: 1.5 seconds animation [restores ammo after 0.896 second]s / 0.95 seconds while continuously firing; **pspeed**: 60 meters per second; **radius**: 3 meter radius |
| Regenerative Burst | **ability_type**: Ability; **key**: ability 1; **shot_type**: aoe; **heal**: 15 per second (allies), 75 overall / 30 per second (self), 150 overall; **radius**: 10 meter radius; **cast_time**: 0.38 seconds [Delay before healing starts. Not interruptable]; **duration**: 5 seconds; **cooldown**: 13 seconds |
| Immortality Field | **ability_type**: Ability; **key**: ability 2; **shot_type**: arc / aoe (field); **heal**: Any deficit from 10% HP; **pspeed**: 60 meters per second; **radius**: 6.5 meter radius; **cast_time**: 0.8 second cast animation [Time for the ability to go on cooldown]; **duration**: 5 seconds (generator) / 5.5 seconds (field); **cooldown**: 25 seconds; **health**: 150 |
| Amplification Matrix | **ability_type**: Ultimate Ability; **damage**: +100% damage amplified; **heal**: +100% healing amplified; **radius**: 9x5 meter rectangle, with 1 meter beneath the ground; **range**: 35 meters; **duration**: 10 seconds; **ult_req**: 2310 points |

#### Bastion
Source: [Bastion, fandom late-July 2022 revision, oldid 126244](https://overwatch.fandom.com/wiki/Bastion?oldid=126244)

Pool/role: role Damage, health 200, armor 100

| Ability | Stats |
|---|---|
| Ironclad | **ability_type**: Passive Ability; **damage_reduction**: 20% |
| Configuration: Recon | **ability_type**: Combat Mode; **shot_type**: hitscan; **damage**: 6 - 20; **damage_falloff_range**: 25 to 45 meters; **headshot**: ✓; **fire_rate**: 8 rounds per second; **ammo**: 35; **reload_time**: 1.5 seconds animation [restores ammo after 1.040 seconds]; **spread**: Max: 1.2 |
| Configuration: Sentry | **ability_type**: Combat Mode; **shot_type**: hitscan; **damage**: 4.5 - 15; **damage_falloff_range**: 30 to 50 meters; **headshot**: ✕; **fire_rate**: 30 rounds per second; **ammo**: 300; **reload_time**: 1.984 seconds animation [restores ammo after ? seconds]; **spread**: 1.8 - 2.7 degrees; **mspeed**: 0 |
| Reconfigure | **ability_type**: Ability; **key**: ability 1; **cast_time**: 1 second (into Sentry)  /  0.5 seconds (into Recon); **cooldown**: None |
| Self-Repair | **ability_type**: Ability; **key**: secondary fire; **heal**: 90 per second; **cast_time**: 0.5 second delay; **duration**: Up to 3.33 seconds; **cooldown**: 1 second |
| Configuration: Tank | **ability_type**: Ultimate Ability; **shot_type**: proj; **damage**: Direct hit: 205 / Splash: 42 - 140 / Self: 10.5 - 35 (becomes 8.4 - 28 due to Ironclad); **headshot**: ✕; **fire_rate**: 1 shot per second; **ammo**: ∞; **pspeed**: 60 meters per second; **radius**: 4 meter radius; **cast_time**: 1.5 seconds; **duration**: 8 seconds; **ult_req**: 2310 points |

#### Brigitte
Source: [Brigitte, fandom late-July 2022 revision, oldid 126440](https://overwatch.fandom.com/wiki/Brigitte?oldid=126440)

Pool/role: role Support, health 150, armor 50

| Ability | Stats |
|---|---|
| Inspire | **ability_type**: Passive Ability; **shot_type**: aoe; **heal**: 15 per second [Heals 3.12 per 0.192 second]; **radius**: 20 meter radius; **duration**: 6 seconds; **cooldown**: 1 second |
| Rocket Flail | **ability_type**: Weapon; **shot_type**: melee; **damage**: 35; **headshot**: ✕; **fire_rate**: 1 swing per 0.6 seconds; **range**: 6 meters; **cast_time**: 0.208 second (initial swing) / 0.240 second (dealing damage) / 0.384 second (recovery after initial swing ends) |
| Repair Pack | **ability_type**: Ability; **key**: ability 2; **shot_type**: targeted (allies); **heal**: 110 over 2 seconds [Heals 9.98 per 0.192 second]; **ammo**: 3; **pspeed**: 45 meters per second; **range**: 30 meters; **duration**: 2 seconds; **cooldown**: 6 seconds per charge / 3 charges |
| Whip Shot | **ability_type**: Ability; **key**: ability 1; **damage**: 70; **headshot**: ✕; **pspeed**: 80 meters per second; **radius**: 0.5 meters radius; **range**: 20 meters; **cast_time**: 0.2 seconds startup; **cooldown**: 4 seconds; **mspeed**: -50% [2.75 m/s] penalty; **knockback**: 10 meters |
| Barrier Shield | **ability_type**: Ability; **key**: secondary fire; **heal**: Regenerates 85 barrier health per second, after being down for 2 seconds; **cooldown**: 5 seconds if destroyed; **mspeed**: -30% [3.85 meters per second] penalty; **health**: 250; **cast time**: 0.08 seconds. |
| Shield Bash | **ability_type**: Ability; **key**: primary fire; **damage**: 5; **radius**: 60° front cone angle radius; **range**: 6.85 meters; **duration**: 0.75 second stun; **cooldown**: 7 seconds; **mspeed**: +500% buff, which becomes +470% [31.35 m/s] due to Barrier Shield's penalty; **knockback**: 2 meters |
| Rally | **ability_type**: Ultimate Ability; **shot_type**: aoe; **heal**: 15 armor per 0.5 seconds, up to 100 armor on self and allies; **radius**: 8.5 meter radius; **duration**: 10 seconds / Armor lasts 30 seconds; **mspeed**: +30% [7.15 meters per second] buff; **ult_req**: 2800 points |

#### Cassidy
Source: [Cassidy, fandom late-July 2022 revision, oldid 126313](https://overwatch.fandom.com/wiki/Cassidy?oldid=126313)

Pool/role: role Damage, health 225

| Ability | Stats |
|---|---|
| Peacekeeper | **ability_type**: Weapon (Primary Fire); **shot_type**: hitscan; **damage**: 21 - 70; **damage_falloff_range**: 20 to 40 meters; **headshot**: ✓; **fire_rate**: 0.5 second recovery / 2 shots per second; **ammo**: 6; **reload_time**: 1.5 seconds animation [restores ammo after 0.8 seconds]; **spread**: Pinpoint |
| Peacekeeper | **ability_type**: Weapon (Secondary Fire); **shot_type**: hitscan; **damage**: 15 - 50; **damage_falloff_range**: 20 to 40 meters; **headshot**: ✕; **fire_rate**: 1 shot per 0.13 seconds; **ammo**: 6; **ammo_drain**: up to 6; **reload_time**: 1.5 seconds animation [restores ammo after 0.8 seconds]; **spread**: Constant: 6.50 degrees |
| Combat Roll | **ability_type**: Ability; **key**: ability 1; **range**: ~6 meters; **duration**: 0.4 seconds; **cooldown**: 6 seconds; **mspeed**: 15 meters per second |
| Flashbang | **ability_type**: Ability; **key**: ability 2; **shot_type**: arc; **damage**: 25; **headshot**: ✕; **pspeed**: 30 meters per second; **radius**: 3 meters radius; **range**: 7 meters; **cast_time**: 0.35 second recovery [Time before Cassidy can shoot.] / 0.65 seconds before cooldown starts; **duration**: 0.8 second stun; **cooldown**: 10 seconds |
| Deadeye | **ability_type**: Ultimate; **shot_type**: hitscan; **damage**: 0.2 to 1.0 seconds: 100 per second; 80 overall / 1.0 to 1.5 seconds: 275 per second / After 1.5 seconds: 550 per second; **fire_rate**: 1 shot per 0.2 seconds; **ammo_drain**: 1 per target; **range**: 200 meters; **duration**: Up to 6.2 seconds; **mspeed**: -70% [1.65 m/s] penalty; **ult_req**: 1680 points |

#### D.Va
Source: [D.Va, fandom late-July 2022 revision, oldid 126422](https://overwatch.fandom.com/wiki/D.Va?oldid=126422)

Pool/role: role Tank, health 150 (Pilot)  / 300 (Mech), armor 300 (Mech)

| Ability | Stats |
|---|---|
| Eject! | **ability_type**: Passive Ability; **cast_time**: 1.5 seconds; **health**: 150 health |
| Fusion Cannons | **ability_type**: Weapon (Mech); **shot_type**: shotgun (hitscan); **damage**: 0.6 - 2; **damage_falloff_range**: 10 - 20 m; **headshot**: ✓; **fire_rate**: 0.15 second recovery / ~6.67 [1 / 0.15] shots per second; **pellets**: 11 per shot; **ammo**: ∞; **spread**: Constant: 4.15 degrees; **mspeed**: -40% [3.3 meters per second] penalty, except when using Boosters |
| Light Gun | **ability_type**: Weapon (Pilot); **shot_type**: proj; **damage**: 14; **headshot**: ✓; **fire_rate**: 7 rounds per second; **ammo**: 20; **reload_time**: 1.4 seconds; **pspeed**: 50 meters per second |
| Defense Matrix | **ability_type**: Ability (Mech); **key**: secondary fire; **range**: 10 meters; **duration**: Up to 2 seconds; **cooldown**: 1 second |
| Boosters | **ability_type**: Ability (Mech); **key**: ability 1; **shot_type**: melee; **damage**: 10; **headshot**: ✕; **range**: Up to 23.98 meters [11.99 meters per second * 2 second maximum duration]; **duration**: Up to 2 seconds; **cooldown**: 4 seconds; **mspeed**: +118% [11.99 meters per second] buff |
| Micro Missiles | **ability_type**: Ability (Mech); **key**: ability 2; **shot_type**: proj; **damage**: Direct hit: 7 per missile / Splash: 1 - 4 per missile / Self: 1 - 4 per missile; **headshot**: ✕; **fire_rate**: 11 missiles per second; **ammo**: 18; **pspeed**: 40 meters per second; **radius**: 1.5 meter radius; **cast_time**: 0.25 seconds; **cooldown**: 8 seconds |
| Self-Destruct | **ability_type**: Ultimate Ability (Mech); **shot_type**: aoe; **damage**: 100 - 1000; **headshot**: ✕; **radius**: 20 meter radius; **cast_time**: 3-second fuse; **ult_req**: 1540 points |
| Call Mech | **ability_type**: Ultimate Ability (Pilot); **damage**: 250; **headshot**: ✕; **range**: 2.5 meters; **cast_time**: 2 seconds; **health**: 300 health / 300 armor; **ult_req**: 319.2 points |

#### Doomfist
Source: [Doomfist, fandom April 2022 (pre-OW2-beta) revision, oldid 123812](https://overwatch.fandom.com/wiki/Doomfist?oldid=123812)

Pool/role: role Damage, health 250

| Ability | Stats |
|---|---|
| The Best Defense... | **ability_type**: Passive Ability; **health**: +30 temporary shields per enemy hit with any of the three normal abilities / +75 shields per enemy hit with the ultimate ability / Maximum of 150 |
| Hand Cannon | **ability_type**: Weapon; **shot_type**: shotgun (projectile); **damage**: 1.8 - 6 per pellet / 19.8 - 66 per shot; **damage_falloff_range**: 15 meters to 30 meters; **headshot**: ✓; **fire_rate**: 1 shot per 0.333 seconds; **pellets**: 11 per shot; **ammo**: 4; **reload_time**: 0.65 seconds (per shot); **spread**: Constant: 2.15 degrees; **pspeed**: 80 meters per second |
| Rising Uppercut | **ability_type**: Ability; **key**: ability 1; **shot_type**: melee; **damage**: 50; **radius**: 5 meters; **duration**: 0.6 seconds (air lock); **cooldown**: 6 seconds; **mspeed**: 10 meters per second |
| Seismic Slam | **ability_type**: Ability; **key**: ability 2; **shot_type**: aoe; **damage**: 25 - 125; **radius**: 8 meters; **range**: 15 meters (travel distance); **cooldown**: 6 seconds; **mspeed**: 25 meters per second (diagonal) |
| Rocket Punch | **ability_type**: Ability; **key**: secondary fire; **shot_type**: melee; **damage**: 50 - 100 (punch)  /  50 - 150 (wall impact); **range**: ~6.4 to 20 meters (depending on charge); **cast_time**: 1.4 seconds to fully charge / 2 second max. charge time; **duration**: 0.5 second stun; **cooldown**: 4 seconds; **mspeed**: -50% [2.75m/s] penalty (charging) / 45 meters per second (punch) |
| Meteor Strike | **ability_type**: Ultimate Ability; **shot_type**: aoe; **damage**: Inner ring: 300 / Outer ring: 15-200; **damage_falloff_range**: 2-8 meters; **radius**: Inner ring: 2 meters / Outer ring: 6 meters / Overall radius: 8 meters; **cast_time**: 1 second; **duration**: 4 seconds; **mspeed**: 16.5 meters per second [300% base normal speed]; **ult_req**: 1680 points |

#### Echo
Source: [Echo, fandom late-July 2022 revision, oldid 126507](https://overwatch.fandom.com/wiki/Echo?oldid=126507)

Pool/role: role Damage, health 200

| Ability | Stats |
|---|---|
| Glide | **ability_type**: Passive Ability; **key**: jump; **mspeed**: Horizontal: +50% [8.25 m/s] buff / Vertical: 4 m/s (down) |
| Tri-Shot | **ability_type**: Weapon; **shot_type**: proj; **damage**: 17 per pellet / 51 per shot; **headshot**: ✓; **fire_rate**: 0.3 second recovery / (3 shots per second); **pellets**: 3; **ammo**: 12; **reload_time**: 1.5 seconds animation [restores ammo after 1.040 seconds]; **pspeed**: 75 meters per second |
| Sticky Bombs | **ability_type**: Ability; **key**: secondary fire; **shot_type**: proj; **damage**: 6 bombs / Impact: 5 / Explosion: 25 / Self: 12.5; **headshot**: ✕; **fire_rate**: 1 bomb per 0.064 seconds; **pspeed**: 50 meters per second; **radius**: 2 meter explosion radius; **cast_time**: 1 second (after stick); **cooldown**: 6 seconds |
| Flight | **ability_type**: Ability; **key**: ability 1; **duration**: 3 seconds; **cooldown**: 6 seconds; **mspeed**: 8 meters per second |
| Focusing Beam | **ability_type**: Ability; **key**: ability 2; **shot_type**: beam; **damage**: 50 per second / 200 per second (on low targets); **headshot**: ✕; **range**: 16 meters; **duration**: 2 seconds; **cooldown**: 8 seconds |
| Duplicate | **ability_type**: Ultimate Ability; **shot_type**: Targeted; **range**: 40 meters; **cast_time**: 0.35 second activation + 1 second recovery; **duration**: 15 seconds; **ult_req**: 2254 points |

#### Genji
Source: [Genji, fandom late-July 2022 revision, oldid 126434](https://overwatch.fandom.com/wiki/Genji?oldid=126434)

Pool/role: role Damage, health 200

| Ability | Stats |
|---|---|
| Cyber-Agility | **ability_type**: Passive Ability; **key**: jump; **mspeed**: 7.8 meters per second [130% base movement speed] (vertical) |
| Shuriken | **ability_type**: Weapon (Primary Fire); **shot_type**: proj; **damage**: 29 [Damage per projectile]; **headshot**: ✓; **fire_rate**: 3 shurikens per 0.88 seconds [1 shuriken insta, delay between next (x2) 0.064 second. 0.88 second recovery after first shuriken]; **ammo**: 30; **reload_time**: 1.5 seconds animation [restores ammo after 0.912 seconds]; **spread**: Pinpoint; **pspeed**: 60 meters per second; **radius**: 0.1 meters shiruken radius |
| Shuriken | **ability_type**: Weapon (Secondary Fire); **shot_type**: proj; **damage**: 29; **headshot**: ✓; **fire_rate**: 3 shurikens per 0.67 second; **ammo**: 30; **ammo_drain**: 3; **reload_time**: 1.5 seconds animation [restores ammo after 0.912 seconds]; **spread**: 9; **pspeed**: 60 meters per second; **radius**: 0.1 meters shiruken radius |
| Swift Strike | **ability_type**: Ability; **key**: ability 1; **damage**: 50; **headshot**: ✕; **range**: 15 meters; **duration**: 0.4 seconds; **cooldown**: 8 seconds; **mspeed**: 50 meters per second |
| Deflect | **ability_type**: Ability; **key**: ability 2; **radius**: 1 meter radius / (front only); **duration**: 2 seconds; **cooldown**: 8 seconds |
| Dragonblade | **ability_type**: Ultimate Ability; **shot_type**: melee; **damage**: 110; **headshot**: ✕; **fire_rate**: 1 swing per 0.9 seconds; **range**: 5 meters; **cast_time**: 1 second (unsheathing) /  0.224 seconds (initial swing) / 1 second (sheathing); **duration**: 6 seconds; **mspeed**: +30% [7.8 m/s] buff; **ult_req**: 1932 points |

#### Hanzo
Source: [Hanzo, fandom late-July 2022 revision, oldid 126509](https://overwatch.fandom.com/wiki/Hanzo?oldid=126509)

Pool/role: role Damage, health 200

| Ability | Stats |
|---|---|
| Wall Climb | **ability_type**: Passive Ability; **key**: jump; **range**: Up to 4 meter vertical climb; **mspeed**: 7.15 meters per second [130% base movement speed] (vertical) |
| Storm Bow | **ability_type**: Weapon; **shot_type**: arc; **damage**: 27.2 - 125 (depending on charge); **headshot**: ✓; **fire_rate**: Up to 0.732 second to charge / 0.5 second recovery; **ammo**: ∞; **spread**: Pinpoint; **pspeed**: 25 - 110 m/s; **radius**: 0.1 meters arrow radius; **mspeed**: -30% [3.85 m/s] penalty |
| Sonic Arrow | **ability_type**: Ability; **key**: ability 1; **shot_type**: arc; **radius**: 9 meter vision radius  /  0.1 meters arrow radius; **duration**: 6 seconds; **cooldown**: 12 seconds |
| Storm Arrows | **ability_type**: Ability; **key**: ability 2; **shot_type**: arc; **damage**: 70; **headshot**: ✓; **fire_rate**: 1 shot per 0.25 seconds; **ammo**: 5; **spread**: Pinpoint; **pspeed**: 110 meters per second; **radius**: 0.1 meters arrow radius; **duration**: Up to 5 seconds; **cooldown**: 10 seconds |
| Lunge | **ability_type**: Ability; **key**: jump; **range**: 7.85 meters [On level ground with no additional movement]; **cooldown**: 5 seconds; **mspeed**: 15 meters per second (horizontal) |
| Dragonstrike | **ability_type**: Ultimate Ability; **shot_type**: proj (initial shot) / aoe (dragons); **damage**: Arrow: 125 / Dragons: 150 damage per second, per dragon / Up to 993.6 damage against a stationary target; **headshot**: Arrow: ✓ / Dragons: ✕; **fire_rate**: 1.5 seconds charging; **pspeed**: 20 meters per second; **radius**: 4 meter radius; **range**: Infinite travel distance; **cast_time**: 0.942 seconds (charging)  /  0.6 seconds (arrow before becoming dragons); **ult_req**: 1680 points |

#### Junkrat
Source: [Junkrat, fandom late-July 2022 revision, oldid 126460](https://overwatch.fandom.com/wiki/Junkrat?oldid=126460)

Pool/role: role Damage, health 200

| Ability | Stats |
|---|---|
| Total Mayhem | **ability_type**: Passive Ability; **shot_type**: projs; **damage**: 50 per grenade; **headshot**: ✕; **pellets**: 6 grenades; **cast_time**: 0.7 seconds (detonation) |
| Frag Launcher | **ability_type**: Weapon; **shot_type**: arc; **damage**: Direct hit: 120 / Splash: 10-80; **headshot**: ✕; **fire_rate**: 1 shot per 0.64 seconds; **ammo**: 5; **reload_time**: 1.5 seconds animation [restores ammo after 0.848 seconds]; **spread**: Pinpoint; **pspeed**: 25 meters per second; **radius**: 0.2 meters (projectile size) / 2 meters (splash radius) |
| Concussion Mine | **ability_type**: Ability; **key**: ability 1; **shot_type**: arc; **damage**: 30-120; **headshot**: ✕; **ammo**: 2 charges; **pspeed**: 25 meters per second; **radius**: 3 meters radius; **cast_time**: 0.13 second(mine start exists) / 0.24 second (after this time can detonate); **duration**: Until detonated; **cooldown**: 8 seconds per charge; **health**: 25 |
| Steel Trap | **ability_type**: Ability; **key**: ability 2; **shot_type**: arc; **damage**: 80; **headshot**: ✕; **pspeed**: 10 meters per second; **radius**: 1 meter radius; **duration**: 3 seconds root; **cooldown**: 10 seconds; **health**: 100 |
| RIP-Tire | **ability_type**: Ultimate Ability; **shot_type**: aoe; **damage**: 50 - 600; **headshot**: ✕; **radius**: 10 meter radius; **cast_time**: 1.536 seconds; **duration**: Up to 10 seconds; **mspeed**: Junkrat: Immobilized / Tire: 12 meters per second; **health**: 100; **ult_req**: 1925 points |

#### Lúcio
Source: [Lúcio, fandom late-July 2022 revision, oldid 126470](https://overwatch.fandom.com/wiki/Lúcio?oldid=126470)

Pool/role: role Support, health 200

| Ability | Stats |
|---|---|
| Wall Ride | **ability_type**: Passive Ability; **mspeed**: +30% buff +2.5 meters per second (wall leap) |
| Sonic Amplifier | **ability_type**: Weapon; **shot_type**: proj; **damage**: 4-round-burst / 20 per round; **headshot**: ✓; **fire_rate**: 1 burst per 0.75 seconds [1 round insta, delay between next (x3) 0.064 second. 0.752 second recovery after first round]; **ammo**: 20; **reload_time**: 1.5 seconds animation [restores ammo after 1.088 seconds]; **spread**: Pinpoint; **pspeed**: 50 meters per second |
| Soundwave | **ability_type**: Ability; **key**: secondary fire; **shot_type**: aoe; **damage**: 25; **headshot**: ✕; **range**: 8 meters; **cooldown**: 4 seconds |
| Crossfade | **ability_type**: Ability; **key**: ability 1; **shot_type**: aoe; **heal**: Allies: 16 [3.07 per 0.192 second] per second / Self: 12 [2.36 per 0.192 second] per second; **radius**: 12 meter radius; **cast_time**: 0.8 second animation duration; **mspeed**: +25% buff |
| Amp It Up | **ability_type**: Ability; **key**: ability 2; **shot_type**: aoe; **heal**: Allies: 52 [9.98 per 0.192 second] per second / Self: 40 [7.68 per 0.192 second] per second; **radius**: 12 meter radius; **duration**: 3 seconds; **cooldown**: 12 seconds; **mspeed**: +60% buff |
| Sound Barrier | **ability_type**: Ultimate Ability; **shot_type**: aoe; **radius**: 30 meter radius; **cast_time**: 0.72 seconds from flat ground; **duration**: 7 seconds [Shields last up to 6 seconds but Sound Barrier remains active for 7 seconds.]; **health**: 750 temporary shields; **ult_req**: 2940 points |

#### Mei
Source: [Mei, fandom late-July 2022 revision, oldid 126500](https://overwatch.fandom.com/wiki/Mei?oldid=126500)

Pool/role: role Damage, health 250

| Ability | Stats |
|---|---|
| Endothermic Blaster | **ability_type**: Weapon (Primary Fire); **shot_type**: beam (projectile-like); **damage**: 55 per second / 2.75 per round [per 0.048 second]; **headshot**: ✕; **ammo**: 120; **ammo_drain**: 20 rounds per second; **reload_time**: 1.5 seconds animation [restores ammo after 0.896 seconds]; **pspeed**: 20 meters per second; **range**: 10 meters; **duration**: 1 second (slow effect) / 1.3 seconds (frozen); **mspeed**: -20% at first, then -2.85% per tick (max. -70%) |
| Endothermic Blaster | **ability_type**: Weapon (Secondary Fire); **shot_type**: proj; **damage**: 75; **headshot**: ✓; **fire_rate**: 1 shot per 0.8 seconds; **ammo**: 120; **ammo_drain**: 10 per shot; **reload_time**: 1.5 seconds animation [restores ammo after 0.896 seconds]; **spread**: Pinpoint; **pspeed**: 115 meters per second; **cast_time**: 0.4 seconds |
| Cryo-Freeze | **ability_type**: Ability; **key**: ability 1; **heal**: ~50 [9.85 per 0.192 seconds] per second / Up to 200 overall; **duration**: Up to 4 seconds; **cooldown**: 12 seconds |
| Ice Wall | **ability_type**: Ability; **key**: ability 2; **radius**: 3x8 meters area; **range**: 35 meters; **duration**: Up to 5 seconds; **cooldown**: 12 seconds; **health**: 400 per pillar / 5 pillars |
| Blizzard | **ability_type**: Ultimate Ability; **shot_type**: arc (initial cast)  /  aoe (blizzard); **damage**: 20 per second / Up to 85 over the duration; **headshot**: ✕; **pspeed**: 20 meters per second; **radius**: 10 meters radius; **cast_time**: 0.5 seconds (throw); **duration**: 4.25 seconds; **mspeed**: -50% at first, then -20% per second (max. -70%); **ult_req**: 1610 points |

#### Mercy
Source: [Mercy, fandom late-July 2022 revision, oldid 126511](https://overwatch.fandom.com/wiki/Mercy?oldid=126511)

Pool/role: role Support, health 200

| Ability | Stats |
|---|---|
| Regeneration | **ability_type**: Passive Ability; **heal**: 20 health per second after not taking damage for 1 second |
| Angelic Descent | **ability_type**: Passive Ability; **key**: jump; **duration**: Until cancelled; **mspeed**: Vertical: 2 m/s (down) |
| Caduceus Staff | **ability_type**: Weapon 1; **shot_type**: targeted (lock-on); **damage**: +30% damage amplified; **heal**: 55 per second; **range**: 15 meters |
| Caduceus Blaster | **ability_type**: Weapon 2; **shot_type**: proj; **damage**: 20; **headshot**: ✓; **fire_rate**: 5 rounds per second; **ammo**: 20; **reload_time**: 1.4 seconds; **spread**: Pinpoint; **pspeed**: 50 meters per second; **radius**: 0.25 meters radius |
| Guardian Angel | **ability_type**: Ability; **key**: ability 1; **shot_type**: targeted (ally); **range**: 30 meters; **cooldown**: 1.5 seconds; **mspeed**: 17 meters per second |
| Resurrect | **ability_type**: Ability; **key**: ability 2; **shot_type**: targeted (fallen ally); **heal**: Restores full health to a fallen ally; **range**: 5 meters; **cast_time**: 1.758 seconds; **cooldown**: 30 seconds; **mspeed**: -75% [1.375 m/s normally, 2.25 m/s during Valkyrie] penalty; **ult_gain**: None |
| Valkyrie | **ability_type**: Ultimate Ability; **damage**: Chain-damage boost (30% per target); **heal**: 20 HP/s (Mercy) / 60 HP/s per target (Allies); **ammo**: ∞ (Blaster); **pspeed**: 100 m/s (Blaster); **range**: 10 meters (chain healing) / +100% range (Guardian Angel, Caduceus Staff); **duration**: 15 seconds; **mspeed**: 9 m/s (omni-directional flight) / 25 m/s (Guardian Angel); **ult_req**: 1820 points |

#### Moira
Source: [Moira, fandom late-July 2022 revision, oldid 125932](https://overwatch.fandom.com/wiki/Moira?oldid=125932)

Pool/role: role Support, health 200

| Ability | Stats |
|---|---|
| Biotic Grasp | **ability_type**: Weapon (Primary Fire); **shot_type**: beam; **heal**: 70 per second, then lingers to heal 35 over 2 seconds [17.5 per second]; **headshot**: ✕; **ammo**: 160 biotic energy; **ammo_drain**: 12.5 energy per second; **range**: 15 meters; **cast_time**: 0.1 seconds; **duration**: 2 seconds (remainder) |
| Biotic Grasp | **ability_type**: Weapon (Secondary Fire); **shot_type**: beam (no target indicator, soft lock-on); **damage**: 50 per second; **heal**: 24 per second (self); **headshot**: ✕; **ammo**: ∞; **range**: 20 meters |
| Biotic Orb | **ability_type**: Ability; **key**: ability 2; **shot_type**: proj; **damage**: 50 per second, up to 200 [Approx.; actually slightly more]; **heal**: 65 per second, up to 300 [Approx.; actually slightly more]; **headshot**: ✕; **pspeed**: 20 meters per second / 5.5 meters per second while tethered; **range**: 4 meters (damage orb) / 5 meters (healing orb); **duration**: 7 seconds, or until depleted; **cooldown**: 8 seconds |
| Fade | **ability_type**: Ability; **key**: ability 1; **range**: 15 meters (max); **duration**: 0.8 second; **cooldown**: 6 seconds; **mspeed**: +250% [19.25 m/s] buff |
| Coalescence | **ability_type**: Ultimate Ability; **shot_type**: beam; **damage**: 70 per second; **heal**: 140 per second / 50 per second (self); **headshot**: ✕; **range**: 30 meters; **cast_time**: 0.5 seconds; **duration**: 8 seconds; **mspeed**: +50% [8.25 m/s] buff; **ult_req**: 2800 points |

#### Orisa
Source: [Orisa, fandom April 2022 (pre-OW2-beta) revision, oldid 123790](https://overwatch.fandom.com/wiki/Orisa?oldid=123790)

Pool/role: role Tank, health 200, armor 250

| Ability | Stats |
|---|---|
| Fusion Driver | **ability_type**: Weapon; **shot_type**: proj; **damage**: 11; **headshot**: ✓; **fire_rate**: 12 rounds per second; **ammo**: 150; **reload_time**: 2.55 seconds; **spread**: Constant: 1.2 degree; **pspeed**: 120 meters per second; **mspeed**: -30% [3.85 m/s] penalty |
| Halt! | **ability_type**: Ability; **key**: secondary fire; **shot_type**: proj; **pspeed**: 25 meters per second; **radius**: 5 meter radius; **cast_time**: 0.1 seconds (launch) / 0.45 seconds (activation); **duration**: 0.65 seconds (snare); **cooldown**: 6 seconds; **mspeed**: 20 meters per second (pull speed) |
| Fortify | **ability_type**: Ability; **key**: ability 1; **duration**: 4 seconds; **cooldown**: 10 seconds; **damage_reduction**: 40% |
| Protective Barrier | **ability_type**: Ability; **key**: ability 2; **shot_type**: arc; **pspeed**: 25 meters per second; **duration**: 20 seconds; **cooldown**: 10 seconds; **health**: 600 |
| Supercharger | **ability_type**: Ultimate Ability; **damage**: +50% damage boost; **pspeed**: 7 meters per second (horizontal); **radius**: 25 meter radius; **cast_time**: 0.4 seconds (spawning Supercharger projectile); **duration**: 15 seconds; **health**: 200; **ult_req**: 1680 points |

#### Pharah
Source: [Pharah, fandom late-July 2022 revision, oldid 126469](https://overwatch.fandom.com/wiki/Pharah?oldid=126469)

Pool/role: role Damage, health 200

| Ability | Stats |
|---|---|
| Hover Jets | **ability_type**: Passive Ability; **key**: jump; **duration**: Up to 2 seconds; **mspeed**: +20% buff / 4.27 meters per second (vertically) |
| Rocket Launcher | **ability_type**: Weapon; **shot_type**: proj; **damage**: Direct hit: 120 / Explosion: ~24.6 [20 / 65 * 80] - 80 / Self: ~12.3 [10 / 32.5 * 40] - 40; **headshot**: ✕; **fire_rate**: 1 shot per 0.85 seconds; **ammo**: 6; **reload_time**: 1.5 seconds animation [restores ammo after 0.6 seconds]; **spread**: Pinpoint; **pspeed**: 35 meters per second; **radius**: 2.5 meter radius (explosion)  /  0.2 meter radius (projectile) |
| Jump Jet | **ability_type**: Ability; **key**: ability 1; **range**: 11.55 meters vertically; **duration**: 0.496 seconds; **cooldown**: 10 seconds |
| Concussive Blast | **ability_type**: Ability; **key**: ability 2; **shot_type**: proj; **damage**: Knockback; **headshot**: ✕; **pspeed**: 60 meters per second; **radius**: 8 meter radius; **cast_time**: 0.16 seconds; **cooldown**: 9 seconds |
| Barrage | **ability_type**: Ultimate Ability; **shot_type**: proj; **damage**: Direct hit: 40 / Splash: 9 - 30 / Self: 4.5 - 15; **headshot**: ✕; **fire_rate**: 30 rockets per second; **pspeed**: 45 meters per second; **radius**: 2 meter explosion radius; **duration**: 2.5 seconds; **mspeed**: Caster immobilized; **ult_req**: 2100 points |

#### Reaper
Source: [Reaper, fandom late-July 2022 revision, oldid 126250](https://overwatch.fandom.com/wiki/Reaper?oldid=126250)

Pool/role: role Damage, health 250

| Ability | Stats |
|---|---|
| The Reaping | **ability_type**: Passive Ability; **heal**: 35% of damage dealt |
| Hellfire Shotguns | **ability_type**: Weapon; **shot_type**: shotgun (hitscan); **damage**: 1.8 - 6 per pellet / 36 - 120 per shot; **damage_falloff_range**: 10 to 20 meters; **headshot**: ✓; **fire_rate**: 2 shots per second; **pellets**: 20 per shot; **ammo**: 8; **reload_time**: 1.5 seconds animation [restores ammo after 0.224 seconds]; **spread**: 6 |
| Wraith Form | **ability_type**: Ability; **key**: ability 1; **duration**: Up to 3 seconds; **cooldown**: 8 seconds; **mspeed**: +50% [8.25 meters per second] buff |
| Shadow Step | **ability_type**: Ability; **key**: ability 2; **range**: 35 meters; **cast_time**: 1.5 seconds; **duration**: 2 seconds; **cooldown**: 10 seconds |
| Death Blossom | **ability_type**: Ultimate Ability; **shot_type**: aoe; **damage**: 170 damage per second (34 damage per hit, 5 hits per second, per target)  /  510 damage overall; **headshot**: ✕; **radius**: 8 meter radius; **duration**: 3 seconds; **mspeed**: -50% [2.75 m/s] penalty; **ult_req**: 2100 points |

#### Reinhardt
Source: [Reinhardt, fandom late-July 2022 revision, oldid 126417](https://overwatch.fandom.com/wiki/Reinhardt?oldid=126417)

Pool/role: role Tank, health 300, armor 200

| Ability | Stats |
|---|---|
| Steadfast | **ability_type**: Passive Ability |
| Rocket Hammer | **ability_type**: Weapon; **shot_type**: melee; **damage**: 85; **headshot**: ✕; **fire_rate**: 1 swing per 0.94 second; **range**: 5 meters; **cast_time**: 0.416 second (initial swing)  /  0.208 second (dealing damage) /  0.528 second (recovery after initial swing ends) |
| Barrier Field | **ability_type**: Ability; **key**: secondary fire; **heal**: Regenerates 200 barrier health per second, after being down for 2 seconds; **radius**: Height 4.250 meters. Width 6.800 meters.; **cast_time**: 0.080 seconds for small size shield  /  0.112 seconds for full size shield; **cooldown**: 5 seconds if destroyed; **mspeed**: -30% [3.85 m/s] penalty; **health**: 1600 |
| Charge | **ability_type**: Ability; **key**: ability 1; **damage**: Pinned to a wall: 300 / Bump with no pin: 50; **range**: 49.5 meters; **cast_time**: 0.6 seconds; **duration**: 3 seconds / 0.65 second stun at the end of a pin; **cooldown**: 10 seconds; **mspeed**: +200% [16.5 m/s] buff |
| Fire Strike | **ability_type**: Ability; **key**: ability 2; **shot_type**: proj; **damage**: 100; **headshot**: ✕; **pspeed**: 25 meters per second; **cast_time**: ~0.4 second  /  0.72 second recovery; **cooldown**: 6 seconds; **radious**: 0.85 meters |
| Earthshatter | **ability_type**: Ultimate Ability; **shot_type**: aoe; **damage**: 50; **radius**: height 1.770 meters; **range**: 20 meters; **cast_time**: 0.45 seconds / 0.5 second recovery; **duration**: 2.5 second knock down; **ult_req**: 1540 points |

#### Roadhog
Source: [Roadhog, fandom late-July 2022 revision, oldid 126456](https://overwatch.fandom.com/wiki/Roadhog?oldid=126456)

Pool/role: role Tank, health 600

| Ability | Stats |
|---|---|
| Scrap Gun | **ability_type**: Weapon (Primary Fire); **shot_type**: shotgun (projectile); **damage**: 1.98 - 6.6 per pellet  /  49.5 - 165 per shot; **damage_falloff_range**: 15 to 30 meters; **headshot**: ✓; **fire_rate**: 0.85 second recovery (~1.18 shots per second); **pellets**: 25 pellets per shot; **ammo**: 5; **reload_time**: 2 seconds animation [restores ammo after 1 second]; **spread**: Constant: 20.1 degrees; **pspeed**: 80 meters per second |
| Scrap Gun | **ability_type**: Weapon (Secondary Fire); **shot_type**: Pre-detonation: / proj / Post-detonation: / shotgun (projectile); **damage**: Pre-detonation: 50 / Post-detonation: 1.98 - 6.6 per pellet, 49.5 - 165 per shot; **damage_falloff_range**: 23 to 38 meters [15 to 30 meters, starting at the point of detonation]; **headshot**: ✓; **fire_rate**: 0.85 second recovery (~1.18 shots per second); **pellets**: Post-detonation: 25 pellets; **ammo**: 5; **reload_time**: 2 seconds animation [restores ammo after 1 second]; **pspeed**: 80 meters per second; **range**: 8 meters (pre-detonation) |
| Take a Breather | **ability_type**: Ability; **key**: ability 2; **heal**: 300 health [Heals 14.40 per 0.048 second]; **cast_time**: 0.5 seconds  /  2 seconds total animation; **duration**: 1 second; **cooldown**: 8 seconds; **damage_reduction**: 50% |
| Chain Hook | **ability_type**: Ability; **key**: ability 1; **damage**: 30; **headshot**: ✕; **pspeed**: 40 meters per second; **radius**: 0.5 meter radius; **range**: 20 meters; **cast_time**: 0.16 seconds; **cooldown**: 8 seconds |
| Whole Hog | **ability_type**: Ultimate Ability; **shot_type**: shotgun (hitscan); **damage**: 7 per pellet, 4928 [704 pellets] overall; **headshot**: ✓; **fire_rate**: 128 pellets per second; **cast_time**: 0.5 seconds; **duration**: 5.5 seconds; **mspeed**: -25% [4.125 meters per second] penalty; **ult_req**: 2240 points |

#### Sigma
Source: [Sigma, fandom late-July 2022 revision, oldid 126501](https://overwatch.fandom.com/wiki/Sigma?oldid=126501)

Pool/role: role Tank, health 300, shield 100

| Ability | Stats |
|---|---|
| Hyperspheres | **ability_type**: Weapon; **shot_type**: arc; **damage**: 2 charges per burst, each: / 55 direct damage / 9 - 30 splash damage / 2.25 - 7.5 self damage; **headshot**: ✕; **fire_rate**: 1 burst per 1.42 seconds [1 shot instantly, the second after 0.160 seconds. recovery after first shot 1.424 seconds]; **ammo**: ∞; **pspeed**: 50 meters per second; **radius**: 3 meter implosion radius; **range**: 22 meters |
| Experimental Barrier | **ability_type**: Ability; **key**: secondary fire; **heal**: Regenerates 80 barrier health per second, after being down for 2 seconds; **pspeed**: 16.5 meters per second; **radius**: 4.5 meters height; 5 meters width at the poles, curves to 7 meters in the middle; **range**: ∞; **cast_time**: 0.064 seconds.; **cooldown**: 2 seconds when recalled / 5 seconds if destroyed; **health**: 700 |
| Kinetic Grasp | **ability_type**: Ability; **key**: ability 1; **range**: 3 meters; **duration**: 2 seconds; **cooldown**: 12 seconds; **health**: 60% of damage absorbed is converted to temporary shields (max. 400) |
| Accretion | **ability_type**: Ability; **key**: ability 2; **shot_type**: arc; **damage**: 70 direct damage / 12 - 40 splash damage / 6 - 20 self damage; **pspeed**: 37.5 meters per second; **radius**: 2.5 meter explosion radius; **range**: 4 meters knockback (direct) [horizontal only] / 1 - 2 meters knockback (splash) [horizontal only] / 2 meters knockback (self) [horizontal only]; **cast_time**: ~0.496 seconds; **duration**: 0.8 second knock down; **cooldown**: 10 seconds; **mspeed**: -75% [1.375 m/s] penalty |
| Gravitic Flux | **ability_type**: Ultimate Ability; **shot_type**: aoe; **damage**: 50 damage (lift) / 50% max HP (slam); **radius**: 7 meter radius; **range**: 35 meters; **cast_time**: ~0.5 seconds (intro) / 1 second (from confirm to suspend); **duration**: Up to 5 seconds to select the area / ~2 second(from suspend to high gravity) / 0.6 seconds (high gravity); **mspeed**: 7.15 meters per second  /; **ult_req**: 1960 points |

#### Soldier: 76
Source: [Soldier: 76, fandom late-July 2022 revision, oldid 126360](https://overwatch.fandom.com/wiki/Soldier:_76?oldid=126360)

Pool/role: role Damage, health 200

| Ability | Stats |
|---|---|
| Heavy Pulse Rifle | **ability_type**: Weapon; **shot_type**: hitscan; **damage**: 6 - 20; **damage_falloff_range**: 30 to 50 meters; **headshot**: ✓; **fire_rate**: 9 rounds per second; **ammo**: 30; **reload_time**: 1.5 seconds animation [restores ammo after 0.736 seconds] |
| Helix Rockets | **ability_type**: Ability; **key**: secondary fire; **shot_type**: proj; **damage**: Direct hit: 120 / Splash: 40-80 / Self: 20-40; **headshot**: ✕; **pspeed**: 50 meters per second; **radius**: 3 meter radius; **cooldown**: 6 seconds |
| Sprint | **ability_type**: Ability; **key**: ability 1; **duration**: Until cancelled; **mspeed**: +50% [8.25 meters per second] buff |
| Biotic Field | **ability_type**: Ability; **key**: ability 2; **heal**: 35 per second 35 per second [Heals 3.39 per 0.096 second]; **radius**: 4.5 meter radius; **cast_time**: 0.544 seconds; **duration**: 5 seconds; **cooldown**: 15 seconds |
| Tactical Visor | **ability_type**: Ultimate Ability; **reload_time**: 0.65 seconds; **cast_time**: 1.2 seconds; **duration**: 6 seconds; **ult_req**: 2310 points |

#### Sombra
Source: [Sombra, fandom late-July 2022 revision, oldid 126463](https://overwatch.fandom.com/wiki/Sombra?oldid=126463)

Pool/role: role Damage, health 200

| Ability | Stats |
|---|---|
| Opportunist | **ability_type**: Passive Ability |
| Machine Pistol | **ability_type**: Weapon; **shot_type**: hitscan; **damage**: 2.4–8; **damage_falloff_range**: 15 to 35 meters; **headshot**: ✓; **fire_rate**: 20 rounds per second; **ammo**: 60; **reload_time**: 1.4 seconds animation [restores ammo after 0.544 seconds]; **spread**: Max: 2.4 degrees |
| Hack | **ability_type**: Ability; **key**: secondary fire; **shot_type**: targeted; **range**: 15 meters; **cast_time**: 0.65 seconds; **duration**: Enemies & B.O.B.: 5 seconds / Health Packs: 60 seconds / Other: 10 seconds; **cooldown**: 8 seconds / 4 seconds (Health Pack) / 2 seconds (broken) [If Sombra takes damage while casting.] |
| Stealth | **ability_type**: Ability; **key**: ability 1; **radius**: 2 meter radius (detection); **cast_time**: 0.75 seconds (activate/disable); **duration**: ∞; **cooldown**: 6 seconds; **mspeed**: +65% [9.075 m/s] buff |
| Translocator | **ability_type**: Ability; **key**: ability 2; **shot_type**: arc; **pspeed**: 25 meters per second; **cast_time**: 0.496 seconds throw animation  /  1.472 seconds return to translocator; **duration**: ∞; **cooldown**: 6 seconds; **health**: 5 |
| EMP | **ability_type**: Ultimate Ability; **shot_type**: aoe; **damage**: 10,000 against barriers and shields; **radius**: 15 meters [Same range as Hack.]; **cast_time**: 0.35 second activation + 0.25 second recovery; **duration**: Same as Hack.; **ult_req**: 1400 points |

#### Symmetra
Source: [Symmetra, fandom late-July 2022 revision, oldid 126476](https://overwatch.fandom.com/wiki/Symmetra?oldid=126476)

Pool/role: role Damage, health 100, shield 125

| Ability | Stats |
|---|---|
| Photon Projector | **ability_type**: Weapon (Primary Fire); **shot_type**: beam; **damage**: 60/120/180; **headshot**: ✕; **ammo**: 70; **ammo_drain**: 7 per second / +7 per second gained against barriers; **reload_time**: 1.5 seconds animation [restores ammo after 1.088 seconds]; **radius**: 0.2 meter beam width; **range**: 12 meters |
| Photon Projector | **ability_type**: Weapon (Secondary Fire); **shot_type**: proj; **damage**: Direct hit: 120 (full charge) / Splash: 15-60 (full charge); **headshot**: ✕; **fire_rate**: 9 rounds per second while charging (max. 9) / 0.25 second recovery; **ammo**: 70; **ammo_drain**: 1-10 rounds based on charge time; **reload_time**: 1.5 seconds animation [restores ammo after 1.088 seconds]; **pspeed**: 25 meters per second; **radius**: 2 meter radius (explosion)  /  0.5 meter radius (projectile max charge) |
| Sentry Turret | **ability_type**: Ability; **key**: ability 1; **shot_type**: proj (before deployment) / beam (turret beam); **damage**: 40 per second [Deals 7.68 damage per 0.192 second]; **headshot**: ✕; **ammo**: 3 stored / Max 3 on the field; **pspeed**: 15 meters per second; **range**: 10 meters (turret beam); **cast_time**: 0.224 seconds (turret start exists) / ~1 second (deployment); **cooldown**: 10 seconds per charge; **mspeed**: −20% (slow); **health**: 30 |
| Teleporter | **ability_type**: Ability; **key**: ability 2; **heal**: Regenerates 30 shields per second, after avoiding damage for 3 seconds; **radius**: 1.5 meter (interact range); **range**: 30 meters (placement) / 40 meters (max. absolute range); **cast_time**: 1.5 seconds (deployment); **duration**: ∞; **cooldown**: 10 seconds; **health**: 50 health / 250 shields |
| Photon Barrier | **ability_type**: Ultimate Ability; **radius**: Entire map / (~484 m × 50 m); **range**: 25 meters; **duration**: 12 seconds; **health**: 4000; **ult_req**: 1680 points |

#### Torbjörn
Source: [Torbjörn, fandom late-July 2022 revision, oldid 126493](https://overwatch.fandom.com/wiki/Torbjörn?oldid=126493)

Pool/role: role Damage, health 200, armor 50

| Ability | Stats |
|---|---|
| Rivet Gun | **ability_type**: Weapon 1 (Primary Fire); **shot_type**: arc; **damage**: 70 per shot; **headshot**: ✓; **fire_rate**: 0.6 second recovery  /  ~1.67 shots per second; **ammo**: 18; **reload_time**: 2 seconds animation [restores ammo after 0.992 seconds]; **pspeed**: 70 meters per second |
| Rivet Gun | **ability_type**: Weapon 1 (Secondary Fire); **shot_type**: shotgun (projectile); **damage**: 3.75 - 12.5 per pellet  / 37.5 - 125 per shot; **damage_falloff_range**: 10 to 20 meters; **headshot**: ✓; **fire_rate**: 0.8 second recovery / 1.25 shots per second; **pellets**: 10; **ammo**: 18; **ammo_drain**: 3 per shot; **reload_time**: 2 seconds animation [restores ammo after 0.992 seconds]; **spread**: Constant: 4.15 degrees; **pspeed**: 120 meters per second |
| Forge Hammer | **ability_type**: Weapon 2; **shot_type**: melee; **damage**: 55; **heal**: 50 (to Torbjörn's turret); **headshot**: ✕; **fire_rate**: ~1.2 swings per second; **range**: 2.5 meters [Same as quick melee]; **cast_time**: 0.352 second (initial swing)  /  0.192 second (dealing damage) / 0.496 second (recovery after initial swing ends) |
| Deploy Turret | **ability_type**: Ability; **key**: ability 1; **shot_type**: arc (deploying turret) / hitscan (turret fire); **damage**: 14 per round / (56 per second); **headshot**: ✕; **fire_rate**: 4 rounds per second; **pspeed**: 17 meters per second; **range**: 15 meters (deploying turret) / 40 meters (attack range); **cast_time**: 3 seconds [Time to fully deploy.]; **duration**: Until destroyed; **cooldown**: 5 seconds / 10 seconds if destroyed while in combat; **health**: 250 |
| Overload | **ability_type**: Ability; **key**: ability 2; **fire_rate**: Rivet Gun: 0.42 second recovery (primary fire), 0.56 second recovery (alternate fire) / Forge Hammer: 0.62 second recovery, 0.24 seconds before initial swing; **reload_time**: 1.4 seconds (Rivet Gun); **cast_time**: 0.688 seconds; **duration**: 5 seconds; **cooldown**: 10 seconds; **mspeed**: +30% [7.15 meters per second] buff; **health**: +100 armor |
| Molten Core | **ability_type**: Ultimate Ability; **shot_type**: arc / aoe (pools); **damage**: Impact: 25 / Pools: 160 per second, +90 against armor; **fire_rate**: 0.144 second recovery; **ammo**: 10; **pspeed**: 40 meters per second; **radius**: 2.5 meter interact radius; **cast_time**: 0.77 seconds; **duration**: Up to 5.5 seconds (claw) / 10 seconds (pools); **ult_req**: 2142 points |

#### Tracer
Source: [Tracer, fandom late-July 2022 revision, oldid 126254](https://overwatch.fandom.com/wiki/Tracer?oldid=126254)

Pool/role: role Damage, health 150

| Ability | Stats |
|---|---|
| Pulse Pistols | **ability_type**: Weapon; **shot_type**: hitscan; **damage**: 1.8 - 6 per bullet / 3.6 - 12 per shot; **damage_falloff_range**: 12 to 20 meters; **headshot**: ✓; **fire_rate**: 20 shots per second; **pellets**: 2 bullets per shot; **ammo**: 40; **ammo_drain**: 2 rounds per shot; **reload_time**: 1 seconds animation [restores ammo after 0.686 seconds]; **spread**: Max: 3.6 degrees |
| Blink | **ability_type**: Ability; **key**: ability 1; **ammo**: 3 charges; **range**: 7.5 meters; **duration**: 0.1 seconds; **cooldown**: 3 seconds per charge / 9 seconds for all three charges |
| Recall | **ability_type**: Ability; **key**: ability 2; **heal**: Health returned to the highest value in the past 3 seconds; **duration**: 0.912 seconds rewinding / Rewinds 3 seconds back; **cooldown**: 12 seconds |
| Pulse Bomb | **ability_type**: Ultimate Ability; **shot_type**: arc; **damage**: Stick: 5 / Explosion: 70-350 / Self: 70-350; **headshot**: ✕; **pspeed**: 15 meters per second; **radius**: 5 meter explosion radius; **cast_time**: 0.15 seconds (throw) / 1 second (after stick); **ult_req**: 1260 points |

#### Widowmaker
Source: [Widowmaker, fandom late-July 2022 revision, oldid 126257](https://overwatch.fandom.com/wiki/Widowmaker?oldid=126257)

Pool/role: role Damage, health 175

| Ability | Stats |
|---|---|
| Widow's Kiss | **ability_type**: Weapon (Scope); **key**: secondary fire; **shot_type**: hitscan; **damage**: 3.6 - 12 (at 0% power) / 36 - 120 (at 100% power); **damage_falloff_range**: 70 to 100 meters; **headshot**: ✓ (2.5x multiplier); **fire_rate**: Up to 0.9 seconds to charge  /  0.5 second recovery before it starts charging again; **ammo**: 35; **ammo_drain**: 5 per shot; **reload_time**: 1.5 seconds animation [restores ammo after 0.816 seconds]; **spread**: Pinpoint; **cast_time**: 0.9 seconds charging  /  0.33 seconds scoping in/out; **mspeed**: -65% [1.925 meters per second] |
| Widow's Kiss | **ability_type**: Weapon (Automatic Fire); **shot_type**: hitscan; **damage**: 3.9 - 13; **damage_falloff_range**: 20 to 40 meters; **headshot**: ✓; **fire_rate**: 10 rounds per second; **ammo**: 35; **reload_time**: 1.5 seconds animation [restores ammo after 0.816 seconds]; **spread**: Max: 3.00 degrees |
| Grappling Hook | **ability_type**: Ability; **key**: ability 1; **range**: 20 meters; **cooldown**: 12 seconds; **mspeed**: 20 meters per second (pulling speed) |
| Venom Mine | **ability_type**: Ability; **key**: ability 2; **shot_type**: arc; **damage**: 115 per second [Deals 2.88 damage every 0.192 second] / 75 total; **headshot**: ✕; **pspeed**: 20 meters per second; **radius**: 3 meter interact radius; **cast_time**: 0.8 second; **duration**: 5 seconds after detonation; **cooldown**: 15 seconds; **health**: 1 |
| Infra-Sight | **ability_type**: Ultimate Ability; **radius**: Map-wide; **cast_time**: 0.5 seconds; **duration**: 15 seconds; **ult_req**: 1540 points |

#### Winston
Source: [Winston, fandom late-July 2022 revision, oldid 126439](https://overwatch.fandom.com/wiki/Winston?oldid=126439)

Pool/role: role Tank, health 350, armor 150

| Ability | Stats |
|---|---|
| Tesla Cannon | **ability_type**: Weapon; **shot_type**: beam (multi-target); **damage**: 60 per second [Deals 5.76 damage per 0.096 second]; **headshot**: ✕; **ammo**: 100; **ammo_drain**: 20 rounds per second; **reload_time**: 1.7 seconds animation [restores ammo after 1 second]; **radius**: 6 meter width; **range**: 8 meters |
| Jump Pack | **ability_type**: Ability; **key**: ability 1; **shot_type**: aoe (landing); **damage**: Jumping: 1 / Landing: 1-50; **headshot**: ✕; **radius**: 5 meter radius /  (landing damage); **range**: 18 - 22 meters; **cooldown**: 6 seconds / 2 seconds during Primal Rage; **mspeed**: 30 meters per second (initial) |
| Barrier Projector | **ability_type**: Ability; **key**: ability 2; **radius**: 5 meter radius; **cast_time**: 0.128 seconds; **duration**: 9 seconds; **cooldown**: 13 seconds; **health**: 700 |
| Primal Rage | **ability_type**: Ultimate Ability; **shot_type**: melee; **damage**: 40 per swing; **headshot**: ✕; **fire_rate**: 0.66 second recovery / ~1.5 swings per second; **range**: 4 meter swings; **duration**: 10 seconds; **mspeed**: +30% [7.15 meters per second] buff; **health**: 850 health, 150 armor; **ult_req**: 1540 points |

#### Wrecking Ball
Source: [Wrecking Ball, fandom late-July 2022 revision, oldid 126215](https://overwatch.fandom.com/wiki/Wrecking_Ball?oldid=126215)

Pool/role: role Tank, health 500, armor 100

| Ability | Stats |
|---|---|
| Quad Cannons | **ability_type**: Weapon; **shot_type**: hitscan; **damage**: 1.5 - 5 per shot; **damage_falloff_range**: 15 to 25 meters; **headshot**: ✓; **fire_rate**: 25 shots per second [1 round per 0.032 seconds] / 0.16 seconds recovery for shoot if stops; **ammo**: 80; **reload_time**: 2 seconds animation [restores ammo after 0.976 seconds]; **spread**: ~2 degrees |
| Grappling Claw | **ability_type**: Ability; **key**: secondary fire; **shot_type**: melee; **damage**: 50 (high speed); **range**: 23 meters (eventually retracts to 6 meters); **duration**: 6 seconds (max. grapple time) / 1.5 seconds (fireball) [Up to 2 seconds with jumps]; **cooldown**: 5 seconds; **mspeed**: +100% [20 m/s] buff (while using) / 18 m/s (fireball after end) / 22 meters per second (booped target) |
| Roll | **ability_type**: Ability; **key**: ability 1; **cast_time**: 0.4 s. (transform into default form); **cooldown**: 0.4 seconds; **mspeed**: 10 meters per second |
| Adaptive Shield | **ability_type**: Ability; **key**: ability 2; **radius**: 8 meter radius; **duration**: 9 seconds; **cooldown**: 15 seconds; **health**: 100 temporary shields + 75 additional shields per enemy within radius |
| Piledriver | **ability_type**: Ability; **key**: crouch; **shot_type**: aoe; **damage**: 20-100; **radius**: 8 meter radius; **cast_time**: 1 second; **duration**: slam deals damage then: / 0.5 seconds (enemy air lock) / 0.3 seconds (recovery for change form) / 0.2 seconds (recovery for ult); **cooldown**: 10 seconds; **mspeed**: 5 meters per second (charging) / 98 meters per second (downwards) |
| Minefield | **ability_type**: Ultimate Ability; **damage**: 130 per mine; **pspeed**: 12 meters per second; **radius**: 1.5 meter interact radius; **cast_time**: 0.1 seconds (deployment) + 0.3 seconds [0.304] recovery / 1.5 seconds (mines, after landing); **duration**: 20 seconds; **health**: 50 per mine; **ult_req**: 1540 points |

#### Zarya
Source: [Zarya, fandom late-July 2022 revision, oldid 126425](https://overwatch.fandom.com/wiki/Zarya?oldid=126425)

Pool/role: role Tank, health 200, shield 200

| Ability | Stats |
|---|---|
| Energy | **ability_type**: Passive Ability |
| Particle Cannon | **ability_type**: Weapon (Primary Fire); **shot_type**: beam; **damage**: 75 per second (at 0%) [14.40 per 0.192 second (at 0%)] / 170 per second (at 100%); **headshot**: ✕; **fire_rate**: 20 rounds per second; **ammo**: 100; **reload_time**: 1.5 seconds animation [restores ammo after 1.040 seconds]; **radius**: 0.15 meter beam width; **range**: 15 meters |
| Particle Cannon | **ability_type**: Weapon (Secondary Fire); **shot_type**: arc / (Explosive); **damage**: Enemy: 9.4-47 (at 0%) / Enemy: 19-95 (at 100%) / Self: 4.7-23.5 (at 0%) / Self: 9.5-47.5 (at 100%); **headshot**: ✕; **fire_rate**: 1 shot per second; **ammo**: 100; **ammo_drain**: 25 rounds per shot; **reload_time**: 1.5 seconds animation [restores ammo after 1.040 seconds]; **pspeed**: 25 meters per second; **radius**: 2.5 meter radius (explosion)  /  0.2 meter radius (projectile) |
| Particle Barrier | **ability_type**: Ability; **key**: ability 1; **shot_type**: Self; **radius**: 1.5 meter radius; **duration**: 2 seconds; **cooldown**: 10 seconds; **health**: 200 |
| Projected Barrier | **ability_type**: Ability; **key**: ability 2; **shot_type**: targeted (allies); **radius**: 1.5 meter radius; **range**: 30 meters; **duration**: 2 seconds; **cooldown**: 8 seconds; **health**: 200 |
| Graviton Surge | **ability_type**: Ultimate Ability; **shot_type**: arc /  (initial cast)  /  aoe (ability start); **damage**: Impact: 5 / Damage over time: 5 per second, up to 18.72; **pspeed**: 25 meters per second; **radius**: 6 meter radius (gravity)  /  0.2 meter radius (projectile); **duration**: 4 seconds; **ult_req**: 2100 points |

#### Zenyatta
Source: [Zenyatta, fandom late-July 2022 revision, oldid 126427](https://overwatch.fandom.com/wiki/Zenyatta?oldid=126427)

Pool/role: role Support, health 50, shield 150

| Ability | Stats |
|---|---|
| Orb of Destruction | **ability_type**: Weapon (Primary Fire); **shot_type**: proj; **damage**: 48; **headshot**: ✓; **fire_rate**: 1 shot every 0.4 second; **ammo**: 20; **reload_time**: 1.5 seconds animation [restores ammo after 1.182 second]; **spread**: Pinpoint; **pspeed**: 90 meters per second; **radius**: 0.15 meter radius |
| Orb of Destruction | **ability_type**: Weapon (Secondary Fire); **shot_type**: proj; **damage**: 48 per orb / Max 240 per volley; **headshot**: ✓; **fire_rate**: 9 shots per second (firing) / 1 orb per 0.52 seconds (charging) / 0.6 second recovery; **ammo**: 20; **ammo_drain**: Up to 5 per volley; **reload_time**: 1.5 seconds animation [restores ammo after 1.182 second]; **spread**: Pinpoint; **pspeed**: 90 meters per second |
| Orb of Harmony | **ability_type**: Ability; **key**: ability 1; **shot_type**: targeted; **heal**: 30 health per second [Heals 5.76 per 0.192 second]; **headshot**: ; **ammo**: One active; **pspeed**: 90 meters per second; **range**: 40 meters; **duration**: 3 seconds (if out of sight) |
| Orb of Discord | **ability_type**: Ability; **key**: ability 2; **shot_type**: targeted; **damage**: +25% damage received; **ammo**: One active; **pspeed**: 90 meters per second; **range**: 40 meters; **duration**: 3 seconds (if out of sight) |
| Transcendence | **ability_type**: Ultimate Ability; **shot_type**: aoe; **heal**: 300 health per second [Heals 57.6 per 0.192 second]; **range**: 10 meters radius; **duration**: 6 seconds; **mspeed**: 11 meters per second; **ult_req**: 2310 points |
#### Measurement refinements between the April 2022 and July 2022 revisions (same game data, newer measurements; prefer the July values)
Sources: the April and July revisions of each hero page linked above.
- Ana's Biotic Rifle damage/heal over time: "0.6 s" became 0.576 s in three 0.192 s ticks (2.24 + 26.88 + 26.88 + 14 = 70). Nano Boost cast time: 0.15 became 0.144 s.
- Ashe's Viper recovery: hip-fire 0.25 became 0.24 s, aim-down-sights 0.65 became 0.64 s. The 12 Jan 2021 patch changed ADS damage from 80 to 75 and ADS recovery from 0.7 to 0.65.
- Echo's Tri-Shot recovery: 0.33 became 0.3 s. Sticky Bombs interval: 0.065 became 0.064 s.
- Genji's Shuriken: April lists primary recovery as 0.68 s, matching the patch of 11 Mar 2021 (0.75 to 0.68). July lists "3 per 0.88 s (0.88 s after first)" for primary and "3 per 0.67 s" for Fan of Blades. **These conflict; check against the client.** Swift Strike duration: 0.3 became 0.4 s.
- Hanzo's Storm Bow charge time: 0.75 became 0.732 s.
- Junkrat's Frag Launcher: "0.667 s" became 0.64 s. Steel Trap: April says "1 s stun / 3 s root", July says only "3 s root" (**conflict**).
- Lúcio's Sonic Amplifier: April gives "4 rounds in 0.375 s + 0.56 s recovery". July gives the first round instantly, then 3 more at 0.064 s intervals, with 0.752 s recovery from the first round.
- Lúcio's Crossfade self-heal: ~12.3 became 12/s. Mei's Cryo-Freeze: ~51.28 became ~50/s, still 200 total, per the patch of 11 Mar 2021 (37.5 to 50 hps).
- Reinhardt's Rocket Hammer: 0.96 became 0.94 s per swing. Sigma's Hyperspheres: 1.5 became 1.42 s per burst, with the second sphere +0.16 s after the first.
- Torbjörn's Molten Core recovery: 0.1375 became 0.144 s. Tracer's Recall animation: 1.25 became 0.912 s (it still rewinds 3 s).
- Wrecking Ball's Piledriver charge: 7.07 became 5 m/s. Grappling Claw has a 6 s maximum grapple (patch of 6 Jan 2022).
- Zenyatta's Orb of Destruction: 2.5 shots/s, i.e. one every 0.4 s.
- Widowmaker's Venom Mine: July reads "115 per second", an obvious typo for 15/s. The tooltip gives 2.88 per 0.192 s, which is 15/s, and 75 total over 5 s.
- Small reload refinements from Feb to April 2022: D.Va Light Gun 1.45 became 1.4 s, Soldier 1.55 became 1.5 s, Sombra 1.5 became 1.4 s, Zarya 1.6 became 1.5 s. Symmetra's alt-fire drain: 2–10 became 1–10 rounds.

#### OW2 contamination detected in the July 2022 wiki revisions (do NOT use)
Source: the July revisions above.
- Doomfist: Power Block, Rocket Punch "15-30 impact / 20-40 wall", Seismic Slam "50", Meteor Strike outer "15-100", and Hand Cannon "5/pellet" are OW2-beta values. The OW1 values come from the April revision: Rocket Punch 50–100 / wall 50–150, Seismic Slam 25–125, Meteor Strike outer 15–200, Hand Cannon 6/pellet.
- Orisa: Augmented Fusion Driver, Energy Javelin, Javelin Spin, Terra Surge and Fortify 4.5 s are OW2. The OW1 values are Fusion Driver, Halt!, Fortify 4 s at 40% damage reduction, Protective Barrier 600, and Supercharger.
- Cassidy: the Magnetic Grenade block is OW2. OW1 has Flashbang (0.8 s stun in the table).
- The 11 Jul 2022 rule that "the final hit depleting armor is dynamically reduced" is an **OW2 PvP beta** change and was not in OW1 — [July 11, 2022 Patch](https://overwatch.fandom.com/wiki/July_11,_2022_Patch).

### Inferences
- Reinhardt's Earthshatter: every wiki revision shows damage 50. However, the official 6 Jan 2022 OW1 retail patch added "an additional 200 damage within 1.75 m of the impact area". The wiki infobox evidently never added it, so the server should model 50, plus 200 within 1.75 m — [January 6, 2022 Patch](https://overwatch.fandom.com/wiki/January_6,_2022_Patch); [Blizzard forum retail notes, 6 Jan 2022](https://us.forums.blizzard.com/en/overwatch/t/overwatch-retail-patch-notes-january-6-2022/647506).
- The same patch also made Hanzo's Storm Arrows ricochet once, let Cassidy roll in the air, cut Torbjörn's alt-fire cost from 3 to 2, gave Wrecking Ball a 6 s grapple cap, and let Moira jump much higher during Fade. Implement these behaviours.
- Damage values ending in .6/.8/.98 (Roadhog 6.6 per pellet, falloff minimums of 30%) show the global falloff curve: linear from 100% at the near distance to 30% at the far distance. Examples: Tracer 6 to 1.8 between 12 and 20 m, Soldier 20 to 6 between 30 and 50 m.
- Zenyatta's Orb of Discord: the Damage modification page (May 2021) still lists +25%. Zenyatta's own change log records an increase from 25% to 30% on 19 May 2020, so use **+30%**.

### Gaps
- Projectile hit-sphere radii are listed for only some abilities (Ana 0.2 m, Hanzo 0.1 m, Genji 0.1 m, Mercy 0.25 m, Junkrat 0.2 m). Most weapons have no radius on the wiki.
- Spread values exist for only some hitscan weapons (Tracer max 3.6°, Ashe hip max 1.85°, Sombra max 2.4°, Bastion Recon max 1.2°, Sentry 1.8–2.7°, D.Va 4.15°, Doomfist 2.15°, Cassidy fan 6.5°). Soldier's spread growth and recovery are not in the cached text.
- The Genji primary-fire cadence and the Junkrat Steel Trap stun conflict between revisions. Resolve them from client data, which the project can read via STU descriptors.

## Q2. Generic combat formulas and rules (final OW1)

### Takeaway
OW1 damage is: base × (1 + Σ dealt modifiers) × (1 + Σ taken modifiers) × headshot multiplier, with armor applied last. Armor subtracts 5 per instance, capped at 50% of the instance. It reduces beams by a flat 30% and does nothing against damage over time. Headshots are 2× (2.5× for a fully charged Widowmaker scoped shot). Shields regenerate 30/s after 3 s without damage. Health packs restore 75 HP (10 s respawn) or 250 HP (15 s respawn). Respawn takes 10 s, +3 s in overtime. Ultimate charge comes from 5 points/s passively plus 1 point per damage dealt to enemy heroes or per HP healed.

### Cited Findings
- **Damage formula:** Damage = base × (100% + damage dealt modifiers) × (100% + damage taken modifiers) × headshot multiplier − armor — [Damage modification, oldid 120815](https://overwatch.fandom.com/wiki/Damage_modification?oldid=120815)
- **Damage boosts (dealt):** Mercy's Caduceus Staff +30%, Nano Boost +50% (plus 50% damage reduction and 250 healing), Orisa's Supercharger +50%, Baptiste's Amplification Matrix +100% for projectiles passing through it. Boosts apply to projectiles only if the shooter was boosted when the projectile was released. Damage taken: Orb of Discord (+30%, per Zenyatta change log 2020-05-19; the page table still says 25%) — [Damage modification, oldid 120815](https://overwatch.fandom.com/wiki/Damage_modification?oldid=120815); [Zenyatta April 2022](https://overwatch.fandom.com/wiki/Zenyatta?oldid=123861)
- **Not boostable:** Ashe's B.O.B. (B.O.B.'s own damage can be amplified separately), D.Va's Self-Destruct, Hanzo's Dragonstrike dragons, Junkrat's Steel Trap and RIP-Tire, Sigma's Flux slam, Symmetra's turrets, Torbjörn's turret and Molten Core damage over time, Widowmaker's Venom Mine, Wrecking Ball's Minefield, and Zarya's Graviton damage over time — [Damage modification](https://overwatch.fandom.com/wiki/Damage_modification?oldid=120815)
- **Damage reduction examples:** Fortify 40%, Ironclad 20%, Take a Breather 50%, Nano Boost 50%. Armor is the very last modifier: a Fortified Orisa hit for 100 takes 100 × 0.6 = 60, minus 5 = 55. Hit for 10, she takes 6 after Fortify, then armor halves it to 3 — [Hit points, oldid 125959](https://overwatch.fandom.com/wiki/Hit_points?oldid=125959)
- **Armor:** Armor subtracts 5 per damage instance, but never more than 50% (hits under 10 are halved). One point of armor remaining is enough to apply the full reduction. Beams are reduced 30% instead: Echo's Focusing Beam, Mei's primary, Moira's Grasp damage and Coalescence, Symmetra's primary and turrets, Winston's Tesla Cannon and Zarya's primary. Damage over time ignores armor: Ana's rifle, Ashe's Dynamite burn, Hanzo's Dragonstrike, Mei's Blizzard, Moira's Biotic Orb, Torbjörn's Molten Core (which deals extra damage to armor), Widowmaker's Venom Mine and Zarya's Graviton — [Hit points](https://overwatch.fandom.com/wiki/Hit_points?oldid=125959)
- **Damage and heal priority:** Healing restores Health, then Armor, then Shields. Damage depletes temporary HP (shields, then armor) first, then recoverable HP (shields, then armor, then health). EMP damages only shields and bypasses temporary armor. If shields break mid-hit, armor reduces only the part of the damage it absorbs — [Hit points](https://overwatch.fandom.com/wiki/Hit_points?oldid=125959)
- **Shields:** Shields regenerate 30/s (5.76 per 0.192 s tick) after 3 s without damage. This counts as healing, so Biotic Grenade amplifies or blocks it. Barrier health regenerates only while the barrier is inactive, after 2 s, at a per-barrier rate: Reinhardt 200/s, Brigitte 85/s, Sigma 80/s — [Hit points](https://overwatch.fandom.com/wiki/Hit_points?oldid=125959); hero tables above
- **Temporary HP:**
  - Rally: 15 armor per 0.5 s up to 100, lasting 30 s.
  - Overload: 100 armor for 5 s.
  - The Best Defense: 30 shields per ability hit, 75 per Meteor Strike hit, maximum 150, decaying 3/s after 1 s.
  - Sound Barrier: 750 shields decaying over 6 s (125/s).
  - Kinetic Grasp: 60% of absorbed damage as shields, maximum 400, decaying 7/s after 3 s.
  - Adaptive Shield: 100 + 75 per enemy in range, lasting 7 s. Damaging these shields gives the attacker no ultimate charge.

  Source: [Hit points](https://overwatch.fandom.com/wiki/Hit_points?oldid=125959)
- **Low-health signals:** Health at or below 50% shows as "low" and 25% as "critical" (supports see the location). At or below 35% (70 HP for 150-HP heroes) a gasp sound plays and the screen edge turns red. The health bar has 25 HP segments — [Hit points](https://overwatch.fandom.com/wiki/Hit_points?oldid=125959)
- **Critical hits:** Headshots deal 2.0×. Fully charged Widowmaker scoped shots, Genji deflecting a scoped Widowmaker shot, and Echo duplicating Widowmaker deal 2.5×. A list of weapons that can crit is on the page. Deadeye and Tactical Visor always hit the body. The page's "6.9x vs 8x" note for Widowmaker is unexplained (likely relative to unscoped minimum damage) — [Critical hit, oldid 124419 (22 May 2022)](https://overwatch.fandom.com/wiki/Critical_hit?oldid=124419). Orisa's Fortify (since 18 Feb 2021) prevents critical headshot damage — [Orisa April 2022](https://overwatch.fandom.com/wiki/Orisa?oldid=123790)
- **Ultimate charge:**
  - Every hero gains 5 points/s passively.
  - Heroes gain 1 point per damage dealt to enemy heroes, including environmental kills. Self-damage, damage to non-heroes and damage from ultimates give nothing. Damage to Roadhog gives 75% (since 5 Aug 2021). Damage to Adaptive Shield gives nothing.
  - Heroes gain 1 point per HP healed on self or allies. Exceptions: The Reaping, Mercy's Regeneration and hacked health packs. Healing self-damage or environmental damage gives nothing.
  - Mercy gains charge equal to the damage her boost added.
  - Most heroes cannot charge while their ultimate is active, except Ashe, Hanzo, Torbjörn, Tracer and Wrecking Ball. Echo gains 6.5× charge while duplicating, toward the copied ultimate.
  - Maximum passive charge time = cost / 5 s (e.g. 2100 → 7 min).

  Source: [Ultimate ability, oldid 123286](https://overwatch.fandom.com/wiki/Ultimate_ability?oldid=123286)
- **Ultimate categories:** Cast-time ultimates can be interrupted during the cast. Channeled ones can be interrupted throughout. Transformations cannot. Built ultimates are paid for only once built. Exceptions: Graviton Surge and B.O.B. cannot be interrupted while casting, Meteor Strike cannot be interrupted, and Transcendence grants crowd-control immunity — [Ultimate ability](https://overwatch.fandom.com/wiki/Ultimate_ability?oldid=123286)
- **Health packs:** Small packs heal 75 and respawn in 10 s. Large packs heal 250 and respawn in 15 s. A pack cannot be used at full recoverable HP or while anti-healed. Packs cleanse the Biotic Rifle, Dynamite and Venom Mine damage over time. Biotic Grenade amplifies packs by 50% (75 → 112.5, 250 → 375). A Sombra-hacked pack is denied to enemies and respawns 4× faster — [Health pack, oldid 122064](https://overwatch.fandom.com/wiki/Health_pack?oldid=122064)
- **Other healing:** The spawn room heals 400 HP/s. The payload heals attackers within 5 m for 10 HP/s. Self-heal rules:
  - Mercy's Regeneration: 20/s after 1 s without damage.
  - Bastion's Self-Repair: 90/s.
  - Roadhog's Take a Breather: 300 over 1 s.
  - Reaper's The Reaping: 35% of damage dealt.
  - Moira's Grasp: 24/s self-heal. Coalescence: 50/s self-heal.
  - Tracer's Recall: restores the highest HP of the past 3 s.

  Source: [Healing, oldid 121867](https://overwatch.fandom.com/wiki/Healing?oldid=121867)
- **Movement:** The base forward speed is 5.5 m/s (6.0 for Tracer and Genji). Backward speed is 90% (4.95 m/s; 5.4 for Tracer/Genji), and diagonal-back is 14/15. Crouching is 3 m/s for everyone. Fixed speeds: Wrecking Ball's roll 10 m/s, Valkyrie 9 m/s, Gravitic Flux 7.15 m/s, Echo's Flight 8 m/s. Buffs, enemy slows and self penalties each stack additively within their category. A self penalty and an enemy slow do not stack (the larger applies). D.Va's Boosters (+118%) override the Fusion Cannons penalty (−40%) — [Movement speed, oldid 117302](https://overwatch.fandom.com/wiki/Movement_speed?oldid=117302)
- **Respawn:** 10 s, +3 s in overtime. A defender delay of up to +5 s applies if attackers outnumber defenders on the objective for 10 s or more (ramping to about 33 s). Deathmatch allows skipping at 3 s — [Respawn, oldid 117428](https://overwatch.fandom.com/wiki/Respawn?oldid=117428)
- **Environmental kills:** The last crowd-control applier gets credit. An environmental kill counts as damage equal to the victim's HP, which generates ultimate charge. The page lists the abilities that qualify, including quick melee — [Environmental kill, oldid 115969](https://overwatch.fandom.com/wiki/Environmental_kill?oldid=115969); [Ultimate ability](https://overwatch.fandom.com/wiki/Ultimate_ability?oldid=123286)
- **Crowd-control taxonomy:**
  - Knockback: explosive weapons except Echo's Sticky Bombs and Zarya's energy ball, plus Rocket Hammer, Primal Rage, Coach Gun and others.
  - Knock-up: B.O.B., Uppercut, Seismic Slam, Piledriver, Flux.
  - Stun: Flashbang, Rocket Punch, Shield Bash.
  - Knock-down: Earthshatter, Accretion.
  - Sleep: ends when the target takes any damage.
  - Slow: from enemies, stacks; from self, does not stack with enemy slows.
  - Pull ("graviton"): Hyperspheres, Halt!, Graviton Surge (which also disables mobility).
  - Root: Steel Trap, plus self-roots (Sentry, Cryo-Freeze, Barrage).
  - Anti-heal: Biotic Grenade.
  - Hack and EMP: block abilities and most passives, and EMP destroys barriers.

  Source: [Status effect, oldid 124015 (27 Apr 2022)](https://overwatch.fandom.com/wiki/Status_effect?oldid=124015)
- **Training bot:** 200 HP. Weapon "Duo Cannons": projectile, 8 damage, 60 m/s, 4 projectiles/s, 8 ammo, 1 s reload, can headshot — [Training bot, oldid 123913 (19 Apr 2022)](https://overwatch.fandom.com/wiki/Training_bot?oldid=123913)

### Inferences
- Implement falloff as a linear interpolation from 100% damage at the near range to 30% at the far range. This is consistent with every minimum/maximum pair in the tables (for example Ashe 40 to 12, Bastion Recon 20 to 6, Roadhog 6.6 to 1.98).
- The 0.192 s and 0.048 s tick values throughout the frame data (DoT, heals, shield regeneration) suggest server simulation ticks of 0.016 s (62.5 Hz), with DoT/HoT applied every 12 ticks (0.192 s). This matches the project's observed client command rate of 62.5/s in CLAUDE.md.
- Use hero-specific armor/beam rules from the Hit points page, not the OW2 armor rule. The OW2 rule was introduced on 11 Jul 2022 in the beta only.

### Gaps
- Gravity, jump height and jump velocity were not found on any fandom page fetched (no "Jump" or "Gravity" page exists). Fall damage: OW1 has none, but I found no citable page for this in the time budget.
- The fandom pages give no per-hero ultimate-charge multipliers (for example "Roadhog 25% less" is the only target modifier) and no per-ability charge exceptions beyond those listed.
- Hitbox sizes per hero are only referenced through a YouTube video on the Critical hit page.

## Q3. Practice Range, training bots and Tutorial

### Takeaway
The OW1 Practice Range has 4 friendly and 11 hostile training bots that stand still, shoot or move, plus distance markers on the ground. Training bots have 200 HP and a weak projectile weapon. The wiki has no authoritative per-bot layout, behaviour script or damage-number UI documentation.

### Cited Findings
- Practice Range: no objectives. Four friendly and eleven hostile training bots perform various actions (staying still, shooting, moving), and there are range markers in meters on the ground — [Practice Range, oldid 95841 (2019)](https://overwatch.fandom.com/wiki/Practice_Range?oldid=95841)
- Training bot: 200 HP. Duo Cannons fire 8-damage projectiles at 60 m/s, 4/s, with 8 ammo and a 1 s reload, and can headshot — [Training bot, oldid 123913](https://overwatch.fandom.com/wiki/Training_bot?oldid=123913)
- A community "Practice Range 2.0" with a grappling Widowmaker bot and a turret Symmetra bot was a Workshop mode, not official content — [Blizzard Watch, Dec 2019](https://blizzardwatch.com/2019/12/16/overwatch-practice-range-2-0/)
- Tutorial: the first play mode, in which Athena guides the player through movement and basics — [Tutorial, oldid 118449](https://overwatch.fandom.com/wiki/Tutorial?oldid=118449)
- Project-local evidence (repository CLAUDE.md, not a public source): hero records 02e0...016b–01f9 have no weapons and are AI/bot definitions. Gameplay definition 0x04000000000014d2 is shared by records 0x0170–0x0172 (skins 0a50...1afd/1aff/1b00). Record 016b uses definition 1403 and 0176 uses definition 16d6.

### Inferences
- Bot counts (4 friendly, 11 hostile) combined with the client's distinct bot definitions suggest that the Practice Range server spawns specific bot variants (stationary, moving, shooting) from map/game-mode data. The project should read the Practice Range mode/map statescript data (graphs 0x13c0, 0x0c8e, 0x0c90) instead of guessing positions.

### Gaps
- No source found for bot positions, movement paths, ultimate-charge behaviour, friendly "damaged" bots' HP, respawn timers, or whether OW1 showed floating damage numbers. As far as I know OW1 had no damage numbers; that is OW2. This is **not verified**. The Practice Range page revision is from 2019 and is thin.

## Q4. Which values changed in the last OW1 patches (2021–2022), so the data matches build 104319

### Takeaway
The final OW1 balance patch was 6 Jan 2022, followed by a Mercy QoL update on 25 Jan 2022. Every live patch from Feb to Sept 2022 contained only events, cosmetics and bug fixes. Patches labelled Apr 26 / May 5 / May 12 / Jun 28 / Jul 11 / Jul 14 / Aug 11 2022 belong to the separate OW2 PvP beta and must be ignored.

### Cited Findings
- **6 Jan 2022 (retail):**
  - Moira's Fade lets her jump much higher.
  - Reinhardt's Earthshatter deals +200 damage within 1.75 m of impact.
  - Hanzo's Storm Arrows ricochet once.
  - Cassidy can Combat Roll in the air.
  - Torbjörn's Rivet Gun alt-fire costs 2 ammo instead of 3.
  - Wrecking Ball's Grappling Claw has a 6 s maximum.
  - Bug fixes: Storm Arrows passing through barriers, Earthshatter penetrating barriers and walls.

  Sources: [January 6, 2022 Patch](https://overwatch.fandom.com/wiki/January_6,_2022_Patch); [Blizzard retail patch notes 6 Jan 2022](https://us.forums.blizzard.com/en/overwatch/t/overwatch-retail-patch-notes-january-6-2022/647506); [Upcomer coverage](https://upcomer.com/new-patch-notes-for-overwatch-include-the-return-of-ricochet-arrows/)
- **25 Jan 2022:** Mercy can resurrect allies who die over death pits. The marker freezes during the resurrect, and holding the button during cooldown queues a resurrect — [January 25, 2022 Patch](https://overwatch.fandom.com/wiki/January_25,_2022_Patch)
- **Later live patches with no balance changes:**
  - 27 Jan, 22 Feb, 15 Mar, 5 Apr, 19 Apr, 17 May and 14 Jun: events and bug fixes.
  - 19 Jul: Overwatch League skin.
  - 9 Aug: Remix Vol. 3, and a fix for Wrecking Ball's Grappling Claw cooldown wrongly resetting after other abilities.
  - 6 Sep: Credits last-chance event and Baptiste portrait/name fixes.

  Sources: [August 9, 2022 Patch](https://overwatch.fandom.com/wiki/August_9,_2022_Patch); [September 6, 2022 Patch](https://overwatch.fandom.com/wiki/September_6,_2022_Patch). Section headings of the other 2022 pages were checked through the same API.
- **OW2 beta-only patches** (source URLs under /patch-notes/beta/): 26 Apr, 5 May, 12 May, 28 Jun, 11 Jul (Mercy Guardian Angel rework, armor rule), 14 Jul, and 11 Aug (Moira beta revert) — [July 11, 2022 Patch](https://overwatch.fandom.com/wiki/July_11,_2022_Patch); [August 11, 2022 Patch](https://overwatch.fandom.com/wiki/August_11,_2022_Patch); [May 5, 2022 Patch](https://overwatch.fandom.com/wiki/May_5,_2022_Patch)
- **2021 balance timeline** (from hero change logs, April 2022 revisions):
  - **11 Mar 2021:** Genji recovery 0.75 → 0.68 and Dragonblade +15% cost. Mei Cryo-Freeze 37.5 → 50 hps. Pharah Hover Jets regeneration 35 → 43/s. Reaper 5.5 → 6 per pellet. Sigma barrier cooldown 2.5 → 2.0 s. Zarya drain 1.6 → 1.8/s.
  - **22 Apr 2021:** Baptiste heal explosion 60 → 50 with +20 on direct hit, and Immortality Field 20% → 10%. D.Va Call Mech damage 50 → 250. Echo Duplicate ends at max(prior HP, 100). Orisa Halt! 8 → 6 s. Reinhardt armor 250 → 200. Roadhog 6 → 6.6 per pellet. Sombra Stealth speed +50% → +65%.
  - **3 Jun 2021:** Baptiste Exo Boots charge 0.7 → 1 s. Cassidy reload 1.2 → 1.5 s and roll distance −20%. Echo Duplicate +15% cost. Reaper Reaping 30% → 35%. Zarya beam 95–170 → 75–170 dps.
  - **5 Aug 2021:** Doomfist cooldowns recharge 100% faster while airborne during Meteor Strike. Moira self-heal 20 → 24/s. Roadhog: enemies gain 25% less ultimate charge from damaging him.

  Source: [Cassidy April 2022](https://overwatch.fandom.com/wiki/Cassidy?oldid=123719) and the other hero revisions linked above (Balance Change Logs section).

### Inferences
- Build 1.74.0.0.104319 most likely corresponds to the 9 Aug or 6 Sep 2022 live patch, the last OW1 client patches before the 4 Oct 2022 OW2 launch. Its hero data therefore matches the post-6 Jan 2022 balance state above.

### Gaps
- I could not map build number 104319 to a specific patch date from public sources in this pass.
