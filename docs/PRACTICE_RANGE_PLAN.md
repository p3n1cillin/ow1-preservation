# Fully functioning Practice Range

The active objective is a fully functioning Practice Range in the original final
OW1 client, 1.74.0.0.104319. Completion requires live evidence for the whole range.
Passing codec tests or reaching first person proves only those individual steps.

## Completion requirements

| Area | Required behavior | Current evidence and remaining work |
|---|---|---|
| Entry and lifecycle | Enter through Training, load the original range, select/spawn a hero, leave and re-enter reliably. | Entry/spawn work in bounded runs. Repeated complete lifecycle and stability coverage remain. |
| HUD and hero selection | Original health, ammo, crosshair, abilities, cooldowns and ultimate display update correctly; hero selection and repeated changes work with the original models and previews. | Repeated hero changes work (218). The original hero HUD renders (348): health card, ultimate meter, ability icons and ammo; ammo drains/refills and Blink charges update live. Required inputs: team filter bits, team colours (lobby 23310 + welcome +0x518), no 0x0717 hide-HUD message, and the server-driven presenter states. Health value reads 0, crosshair and hit markers are absent. Preview models absent. |
| Movement and physics | Walk, look, jump, crouch, interact with doors and traverse the map with correct collision, gravity and spawn/recovery behavior. | First-person movement/look work. Server teleports (respawn, Recall, Blink) land correctly once the hero has a team; earlier 'launches' were the spawn-room barrier ejecting a team-less hero (340). Out-of-bounds respawn is a server approximation (345). Full traversal and prediction behavior are unverified. |
| Weapons | Each available hero's primary/secondary fire, projectiles, muzzle origin, spread, cadence, ammo, reload and weapon switching behave correctly. | Tracer/Soldier/McCree firing and reload work. Tracer now uses 40 rounds per second and a 1.0 s reload (268). Other hero tuning, wrong Tracer muzzle origin and incomplete roster coverage remain. |
| Abilities | Every available hero's abilities, charges, resources, cooldowns and ultimate work with correct movement, effects and outcomes. | Native Tracer Blink with collision and server-tracked charges works and is user-confirmed (274/277). Recall rewinds 3 s server-side and lands correctly (341); its native screen effect is absent. Tracer's ultimate is not predicted by the client and forcing its Ability state exits the client (349/350). Complete roster ability behavior remains. |
| Combat and health | Damage, healing, armor/shields, range, critical hits, death, respawn and relevant feedback agree with the original client data. | Estimated bot hit tests and respawn work; bots are hostile (team 1). Native hit confirms (channel 2 / 25001) fill the controller hit ring (352). Death presentation is absent: bots vanish on destroy, and health 0 or the trailing component-51 fields do not start it (344/353). Authoritative collision/combat and complete feedback remain. |
| Range actors and objects | Original training targets/bots, their movement/attacks, friendly targets, health packs and interactive range objects function in their intended locations. | The best recipe creates 13 static training bots. A fake patrol clipped through walls and was removed; authored movement/AI and complete object behavior remain. |
| Backend independence | Original client operates against the local backend using reproducible local setup; no official service dependency or patched client files is required. | Local authentication/menu/instance flow demonstrated. Native header preload remains an opt-in diagnostic rather than a resolved normal load trigger. |
| Reliability and regression | Repeat representative sessions across the available roster; no missing models, stuck state streams or unexpected crashes; teardown restores owned-process permissions and client integrity. | Cleanup checks and 25 CTest targets pass. Intermittent early instance failure remains: the client sends the normal 21627/21600/21610, then exits with code 1 (335/335b). Broader live regression coverage remains. |

## Work order and evidence

1. Finish HUD ownership, widget parent handles and entity bindings. Preserve the
   working gameplay recipe while changing experimental graph placement.
2. Resolve normal map loading and correct movement/prediction/collision. Replace
   geometry-blind ability teleports with behavior that satisfies range traversal.
3. Derive weapon and combat parameters from each hero's client data; establish
   correct projectile origins and authoritative hit outcomes.
4. Implement and test all available heroes' abilities and range actor behavior.
5. Exercise the original UI, previews and complete leave/rejoin lifecycle, then
   run a roster regression covering weapons, abilities, damage and recovery.

For each area, save the recipe, server events, observed original-client behavior
and bounded cleanup result in shared private storage. Record failures and exact
coverage in `HANDOFF.md` / `TESTING.md`. Retain only useful reference dumps.
Do not mark the goal complete while any required area is missing or unverified.
