# Evidence-based feature status — 2026-10-12

Statuses: **Not investigated**, **Researching**, **Partially implemented**, **Implemented but untested**, **Verified working**, **Blocked**. Verification below is limited to its named test context. No gameplay milestones have been verified in an original game client.

| Feature | Status | Evidence / missing work |
|---|---|---|
| Windows source build: Prometheus DLL | Verified working | MSBuild Release/x64 succeeded before and after changes |
| Windows source build: patcher | Verified working | .NET 8 Release build; patching/launch not executed |
| Standalone relay build and start | Verified working | CMake build; process starts on loopback in integration test |
| Full build workflow | Verified working | `scripts/Build.ps1` completed dependency install, build, CTest and patcher stages locally; cache reused |
| GitHub Actions workflow | Verified working | Public Windows build completed dependency install, source builds and all 12 tests on 2026-10-12; legacy ACL restoration regression covered |
| Read-only executable inspection | Verified working | Synthetic x64 PE/malformed input, then real disc executable and numeric fixed version on 2026-10-11 |
| Disc `1.0.1.27578` fingerprint and manifest inspection | Verified working | 2026-10-11: real signed x64 executable, matching install hash/size, fixed PE version and full disc record-header scan; subsequent isolated launch documented separately |
| Disc offline installation / compatible adapter | Partially implemented | Native title renders; guarded speech-omitting adapter reaches state 5 and partial Hanamura rendering; loading overlay persists, no playable session |
| Final retail build identification | Verified working | Supplied signed x64 EXE fingerprinted; exact BuildConfig MD5 and decrypted CMF build 104319 verified |
| Final retail client acquisition | Verified working | User-supplied archive fully extracted / integrity passed; complete archive contents preserved outside Git. Full logical-asset completeness still unverified |
| Final retail isolated startup | Partially implemented | Unmodified title/login display directly observed; later window input denied. Interactive helper implemented; no playable final session |
| Final retail native Practice request | Verified working | Native API allocates/publishes its own map descriptor; guarded dump confirms index 0x688. Existence query alone leaves state 2. A native header resource request changes the raw resource state 0 to 3 and world state 2 to 3; no rendered map/hero/session result |
| Final retail native loading context | Partially implemented | Native type-2 constructor/activation accepts the resident default identifier. Immediate tracing returns at state 4; a captured 433 updates retain the request. Native context readiness remains 0 and its metadata cache is empty; no loaded map or session |
| Final retail metadata request path | Researching | Original initialization/processing handlers return; a retained internal kind-13 request is accepted/completed with a null data pointer. Cache remains empty. Internal kind is not a verified wire opcode; no private-backend response implemented |
| Final retail manifest / bundled map-header inspection | Verified working | Exact base/text/speech CMFs hash-checked and decoded; 130 map headers hash-verified in 41 checked bundles. STU V2 names/references parsed for all 130; Hanamura/Practice map-root hashes verified. Sample keys unavailable; full asset audit pending |
| Beta client initialization and launch | Blocked | No compatible game files; fixed offsets not runtime validated |
| Map loading and transitions | Partially implemented | Disc Hanamura GUID loaded / world state 5 and geometry visible beneath loading overlay; five-minute bounded probe survives with original callback restored. Gameplay transition and repeat unload remain unverified |
| Controllable hero, movement and collision | Implemented but untested | Upstream client simulation/spawner; no original client test |
| Hero resource/component guards | Implemented but untested | DLL compiled; game resource lookups not exercised |
| Demo wire BSON interoperability | Verified working | Independent golden assignment document plus schema/roundtrip tests |
| Input schema and malformed-frame rejection | Verified working | Invalid BSON, sizes, unknown types, missing fields, overflow/nonfinite values; offending real socket closed |
| Connection-owned player identity | Verified working | Spoofed IDs rewritten in pure core and actual socket tests; no account authentication |
| Hero selection cache and reselection | Verified working | Relay stores latest hero, invalidates earlier movement; tested synthetic IDs |
| Late-join movement snapshots | Verified working | Real sockets receive meaningful numeric positions after join; no rendered game entities |
| Two-way movement relay | Verified working | Synthetic participants exchange BSON positions through a dedicated process |
| 12 simultaneous participants and capacity rejection | Verified working | Actual WebSocket connections and movement; 13th denied. No teams or 6v6 match |
| Disconnect/reconnect relay lifecycle | Verified working | Leave broadcast, released slot, new identity and latest state replay |
| Client receive worker / cached selection / disconnect UI | Implemented but untested | Compiled DLL; no in-game regression test |
| Client remote-entity removal | Implemented but untested | Erase on leave, clear on disconnect; compiled only |
| Message rate and outbound queue limits | Partially implemented | Limits in code; room/input schema tested; clock refill and slow-consumer stress not verified |
| Original game JAM/mirror protocol | Researching | Source paths examined; custom relay does not implement it |
| Beta-to-retail version profiles | Researching | Exact final startup fingerprint guarded; no validated final gameplay hooks or alternate entity layouts |
| Original STU/CASC inspection/extraction | Partially implemented | Disc IN/EN/ROOT/APMs and selected old package graphs hash-verified; encoded records preserved. English speech has confirmed absent blobs; native STU imports exceed declared package graphs |
| Local accounts and expiring sessions | Researching | Login-Server evaluated; no independent account service implemented |
| Lobbies/parties/presence/admin roles | Researching | Single relay room is not a lobby implementation |
| Teams/match configuration/start/end | Not investigated | No client service mapping or backend rules implemented |
| Server-authoritative movement/physics | Not investigated | Relay trusts positions; no inputs, reconciliation or collision authority |
| Primary/secondary fire and weapons | Partially implemented | Upstream local tooling exists; README reports weapons not shooting; unverified locally |
| Abilities, cooldowns, ultimates and passives | Not investigated | No verified client-to-server gameplay event mapping or synchronization |
| Projectiles, hits, damage/healing and shields | Not investigated | No authoritative combat model or cross-client verification |
| Death/respawn and elimination events | Not investigated | No synchronized lifecycle |
| Objectives/timers/overtime/rounds/win conditions | Not investigated | No Assault/Escort/Hybrid/Control rules implemented |
| Original menus/HUD/hero selection | Partially implemented | Upstream hooks/tools; original JAM-dependent interface incomplete |
| Audio/animations/kill feed/scoreboard/results | Not investigated | No end-to-end verification |
| Profiles/stats/progression/cosmetics/settings persistence | Not investigated | No account storage or complete historical data definitions |
| Highlights / Play of the Game / replay fidelity | Not investigated | Replay entity-admin references alone are not implementation |
| One full private match | Blocked | Client, combat and objectives missing |
| Complete original 6v6 preservation | Blocked | Ultimate target remains unmet; 12-socket test is infrastructure evidence only |
