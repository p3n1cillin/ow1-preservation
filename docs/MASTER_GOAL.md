# Master goal: complete Overwatch 1 preservation

Set by the project owner on 2026-10-16. This file summarizes the goal so every
Claude/Codex session starts from it; `HANDOFF.md` holds the current technical
checkpoint and `docs/PRACTICE_RANGE_PLAN.md` the near-term acceptance table.

## Objective

Make the unmodified final retail client 1.74.0.0.104319 a complete game again on
independently hosted infrastructure: launch, authenticate against our own
accounts, original menus, every hero, map and mode of the build, and genuine
server-authoritative online 6v6 matches between real original clients, with
progression, cosmetics and the full original UI. No Blizzard production
services, credentials or proprietary secrets; proprietary binaries and assets
stay outside Git; AGPL-3.0 obligations apply.

## Priority order (starting order, not a reason to ignore foundational blockers)

1. Hero HUD ownership/routing: correct player, controller, actor, model,
   statescript and HUD relationships.
2. One hero fully functional: camera, movement, collision, weapons, health,
   damage, abilities, HUD, death/respawn.
3. Convert local approximations into server-authoritative mechanics
   (movement prediction/reconciliation, hit detection, damage, cooldowns).
4. Two real original clients in one independent session, synchronized.
5. Multiplayer combat and objective loop.
6. 6v6 with complete match lifecycle and stable server operation.
7. Matchmaking, parties, custom games and backend services.
8. Full roster, maps, modes, cosmetics, progression and remaining features.

## Completion

Complete only when an ordinary user can sign in to a preservation account, use
the original menus, enter the full Practice Range, create/join private games,
queue into online 6v6 with eleven other real users, play complete matches under
the original rules with working weapons/abilities/ultimates, see correct
objectives, scores, kill feed and results, use supported cosmetics/progression,
change maps/modes and return to the menu to play again, all validated with real
original-client execution. Builds, menus, a rendered map, one controllable hero
or one finished match are milestones, not completion.

## Operating mode

Autonomous continuous development: analyze, prioritize, research, implement,
build, test against the original client, document, commit, repeat. When blocked,
record the blocker and move to other productive work. Never fabricate results or
mark unverified functionality complete. Keep `HANDOFF.md` current before stopping.
