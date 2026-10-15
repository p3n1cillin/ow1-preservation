# Overwatch game-server transport, connection lifecycle, replication and combat events (public sources + mapping to OW1-preservation open problems)

Scope note: the public record on Overwatch's game-server wire protocol is thin. Blizzard has published architecture-level material (Tim Ford's GDC 2017 talk "Overwatch Gameplay Architecture and Netcode", the April 2016 "Let's talk netcode" developer video with Tim Ford and Philip Orwig, the 2016 "High Bandwidth" update, and Philip Orwig's GDC 2017 replay talk). None of it documents packet layouts, the AES-GCM envelope, reliable channels or message ids. Several primary pages (GDC Vault, Valve wiki, GameStar/GamePro, TechRaptor) returned HTTP 403 or were paywalled in this session, so some details below come from secondary summaries and are flagged as such. Items drawn from general background knowledge, not fetched this session, are marked "[background, not verified this session]" and appear only under Inferences.

## Q1. What is publicly documented about Overwatch's UDP game protocol, tick/update rate, packet structure, encryption, timeouts, join process and client exit behaviour?

### Takeaway
Public sources document the simulation model: fixed ~16 ms command frames, a client clock that runs ahead of the server, redundant input, time dilation and rollback. They also document the update-rate history: 20.8/21 Hz server-to-client, raised to 63 Hz by "High Bandwidth" in 2016, with adaptive downgrade. No public source describes the UDP packet format, the encryption, the join handshake, timeout values or the client's exit behaviour. The project's reverse engineering (AES-256-GCM envelope, flags-3 handshake, 11 reliable channels) is ahead of anything public.

### Cited Findings
- The GDC 2017 session "'Overwatch' Gameplay Architecture and Netcode" (Timothy Ford, Blizzard) covers "how Overwatch's networked simulation works and how it uses determinism for responsiveness and precision", built on an Entity Component System (ECS). Vault content is locked. — [GDC Vault 1024001](https://gdcvault.com/play/1024001/-Overwatch-Gameplay-Architecture-and)
- Secondary summary of that talk (Edgegap blog, not Blizzard):
  - Gameplay netcode is confined to three systems: **movement, weapon, and statescript**.
  - Standard command frames are **16 ms (~60 Hz)**; tournament mode uses 7 ms.
  - The client clock runs ahead of the server by **half RTT plus one buffered command frame** (about 96 ms at 160 ms RTT).
  - The simulation is fixed at 60 Hz, and the engine runs multiple ticks per rendered frame when rendering is slow.
  - Edgegap's ECS totals are internally inconsistent ("~46 client systems / 103 component types" versus "~150 systems" in its title).
  — [Edgegap: Game Backend Deep Dive – Overwatch](https://edgegap.com/blog/game-backend-deep-dive-overwatch-2016-netcode-architecture-rollback)
- The same summary describes **time dilation**:
  - When the server detects input starvation, it signals the client.
  - The client then treats its 16 ms step as about 15.2 ms, simulating faster and sending more input to rebuild the server's buffer, and later dilates back.
  - Without dilation, the server **duplicates the player's last known input** during starvation.
  — [Edgegap](https://edgegap.com/blog/game-backend-deep-dive-overwatch-2016-netcode-architecture-rollback)
- **Input redundancy:** each client packet carries every input since the last server-acknowledged movement state (sliding window, attributed to QuakeWorld). A lost packet's inputs arrive in the next one. — [Edgegap](https://edgegap.com/blog/game-backend-deep-dive-overwatch-2016-netcode-architecture-rollback)
- A GameDev.net thread paraphrases Ford's talk the same way: the client runs ahead by about RTT/2 plus one command frame so that commands arrive when the server reaches that tick. This is a commenter's reading, not primary. — [GameDev.net "command frames and tick synchronization"](https://gamedev.net/forums/topic/696756-command-frames-and-tick-synchronization) (the page returned 403 on fetch; the claim comes from the search snippet)
- **High Bandwidth (Aug–Sep 2016):**
  - Blizzard said the option "adjusts the game's client update rate from 21 updates per second to 63 updates per second" and became the default for Quick Play and Competitive on PC.
  - Blizzard "added in tech that will automatically and adaptively scale down your update rate if we find your connection can't keep up."
  - Orwig: "the server will dynamically figure out whether or not you're syncing the packets appropriately and adjust your rate up or down accordingly."
  - Consoles did not get the update at first.
  — [HEXUS](https://hexus.net/qac6rc), [PC Gamer](https://www.pcgamer.com/au/high-bandwidth-support-is-being-rolled-out-to-overwatch-at-this-very-moment), [Ubergizmo](https://ubergizmo.com/2016/08/high-bandwidth-servers-rolled-out-overwatch)
- PC Gamer says the option was first added to custom games in June 2016 and described it as "60Hz", which conflicts with Blizzard's 63 figure. German press titled the April 2016 video explanation "20,8 Hz Client-Tickrate". — [PC Gamer](https://www.pcgamer.com/au/high-bandwidth-support-is-being-rolled-out-to-overwatch-at-this-very-moment); [GamePro](https://www.gamepro.de/artikel/overwatch-blizzard-erklaert-den-netcode-208hz-client-tickrate,3270422.html) / [GameStar](https://www.gamestar.de/artikel/overwatch-blizzard-erklaert-den-netcode-208hz-client-tickrate,3270417.html) (titles only; bodies returned 403)
- The "Let's talk netcode" developer video (April 5, 2016, Ford and Orwig, just under 20 minutes) covers netcode, core programming values and known issues. — [Ten Ton Hammer](https://www.tentonhammer.com/news/overwatch-developer-update-let-s-talk-netcode.amp)
- **Ports:**
  - A Blizzard-forum port table lists Overwatch TCP 1119, 3724, 6113 and 80, with UDP 3478–3479, 5060, 5062, 6250 and 12000–64000 described as voice. The post date is unknown.
  - Older community sources list game UDP 26503–36503 (and 3724). No current Blizzard article confirms that range.
  — [Blizzard SC2 forum port post](https://us.forums.blizzard.com/en/sc2/t/how-to-put-in-ports-number-for-blizzard-games/7533); [VidaExtra](https://www.vidaextra.com/guias-y-trucos/caida-servidores-overwatch-como-solucionar-problemas-red-perdida-conexion-overwatch-2); [Netduma forum 2016](https://forum.netduma.com/topic/15789-setting-up-advanced-games-services/)
- **Timeouts (anecdotal only):**
  - A user reports sitting on "Connecting" and then getting "Timeout Communicating With Blizzard services" after about 15 seconds.
  - Another user reports "Disconnected from Game Server" with no lag warning, even in the Practice Range.
  - Blizzard has documented no threshold.
  — [Blizzard EU forum](https://eu.forums.blizzard.com/en/overwatch/t/overwatch-wont-log-in-only-says-connecting/23351); [Blizzard US forum](https://us.forums.blizzard.com/en/overwatch/t/disconnected-from-game-server/1026426)

### Inferences
- The project's "~62.5 Hz" client command rate equals 1000/16 ms. The public 16 ms command frame therefore matches the decoded module-3 command cadence. The public "63 updates/s" is probably the same 16 ms frame expressed per second (62.5 rounded); 21 Hz is one update per three command frames (62.5/3 = 20.8, which matches the German "20,8 Hz").
  - A server emulator should send server frames on that 16 ms cadence: either every frame (63 Hz mode) or every third frame (21 Hz mode). The original adaptive scaler implies the client tolerates either rate.
- Redundant input plus "ack of last server-acknowledged movement state" implies two things:
  - The client's module-3 command block likely contains a sliding window of commands starting after a server-acknowledged command frame.
  - The server's movement snapshot (or the module-3 server frame/ack field) likely carries the last processed command frame id.
  - Not replying with that ack would make the client's window grow and may eventually trigger client-side throttling or a disconnect. This should be checked against the decoded command-header u32 and window length (see Q4).
- Time dilation implies a server-to-client feedback field (input buffer health / "speed up" hint). The undecoded module-3 time bit / +16 field, or the server-frame compact u32, are candidates. This is a hypothesis to test by emulation, not established.

### Gaps
- No public description of the UDP envelope, AES-GCM, header fields, ack bitmap, flags-3 handshake or reliable-channel scheme. No public packet captures or reverse-engineering write-ups were found for the Overwatch game-server transport.
- No public statement of join or keepalive timeout values, maximum retransmissions of the join packet, or what the client does (exit code, error dialog) when the join fails.
- No public material on anti-cheat or integrity checks during the instance join; nothing was found in this session.
- The GDC talk video and slides (primary source) could not be accessed; the Edgegap figures (16 ms, 15.2 ms dilation, 220 ms) should be treated as secondary.

## Q2. Overwatch error codes (LC-202, LC-208, BC-153, etc.) and what they signal about the connection stage

### Takeaway
Public descriptions are coarse. LC-202 means "disconnected from / unable to connect to game server". LC-208 is a game-server connectivity error (mostly reported on console). BC-153 is a failed login, often following an LC error. "Timeout communicating with Battle.net services" relates to the BNet/lobby layer, not the instance. No public source maps codes to precise protocol stages.

### Cited Findings
- LC-202: "disconnected from game server". — [GamesRadar](https://www.gamesradar.com/overwatch-2-error-codes)
- Blizzard's official article 34859, "Overwatch 2 Console Error LC-202": treated as a game-server disconnect, with network troubleshooting steps. — [Blizzard Support 34859](https://us.support.blizzard.com/en/article/34859)
- A Blizzard forum moderator calls LC-202 "a general disconnection or unable to connect error" and says the cause is typically "some point between you and the game servers … dropping the connection". — [Blizzard forums](https://us.forums.blizzard.com/en/overwatch/t/i-need-help-with-error-code-lc-202-console/371069); [Blizzard forums (Cox ISP thread)](https://us.forums.blizzard.com/en/overwatch/t/lc-202-unable-to-connect-on-cox-communications-isp/307223?page=3)
- LC-208: "a server connectivity issue that primarily affects console players … from both local network connectivity issues, as well as server side problems". — [Gfinity](https://www.gfinityesports.com/guides/overwatch-2-error-codes); [esports.gg LC-208](https://esports.gg/news/overwatch/how-to-fix-overwatch-2-lc-208-disconnected-from-game-server-error)
- BC-153: caused by "failing to log in", often after another code such as LC-202; another source cites account restrictions or server maintenance. — [Gfinity](https://www.gfinityesports.com/guides/overwatch-2-error-codes); [Pocket Tactics](https://www.pockettactics.com/overwatch-2/codes)
- LC-202 also existed in the OW1 era (competitive-match complaints). — [Blizzard forum "Lc-202 is ruining comp in ow"](https://us.forums.blizzard.com/en/overwatch/t/lc-202-is-ruining-comp-in-ow/123210/2)
- "Time Out Communicating with Battle.net Services" is described as usually a disconnect while queued. — [Prima Games](https://primagames.com/tips/how-to-fix-overwatch-2-time-out-communicating-with-battle-net-services-error-explained)

### Inferences
- The "LC" prefix plausibly stands for a lobby or game-client connection class, and "BC" for a Battle.net connection class. This is unconfirmed naming inference.
- For the project's "early instance failure" (client sends 5–11 33-byte join packets, receives replies, then exits with code 1 and writes no dump), the codes suggest the following reading.
  - A normal instance failure in the retail client typically surfaces as a UI message (LC-202 / "Disconnected from game server") with a return to menu. It does not normally exit the process.
  - The project's own notes record the same pattern for a failed instance: an abort via 0xb64af0 sends lobby 21801/21802 and returns the UI to Training.
  - A **process exit with code 1 and no error UI** therefore points away from the normal LC-202 path. It points toward:
    - (a) a fatal-error/terminate path that the bounded launcher reports as exit code 1;
    - (b) an anti-tamper or integrity termination;
    - (c) the client deliberately quitting because the lobby (BGS) connection dropped or timed out concurrently. For example, the TCP named-pipe bridge or the BNet probe stalls while the client is blocked on instance join. The project already saw that a missing lobby server yields "time out communicating with Battle.net" behaviour.
- Concrete checks:
  - (1) Log every lobby (TCP) message and timing in failed runs. If 21801/21802 appear before the exit, it is the native abort path. If the lobby socket closes first, suspect the BGS side.
  - (2) Record whether the client's join packets in failed runs reuse the same UDP source port. The bridge allows one source port per run, so a client that rebinds after a failed first attempt would be silently dropped. In that case the "replies" the responder sends go to a port the client has abandoned.
  - (3) Check whether replies acknowledge a sequence the client has not sent yet, or arrive before the client's socket and codec are ready. The original receipt updater rejects old sequences, and a stale ack/bitmap on a retransmitted join could leave the peer stuck in state 1 until its join-retry budget is exhausted. Retry counts of 5–11 suggest a retry budget or timer rather than a single protocol error.
  - (4) Collect Windows Error Reporting / Event Log entries and the client's own log files for that PID. Exit code 1 with no dump is consistent with ExitProcess(1) from a handled fatal path rather than a crash.

### Gaps
- No public, authoritative Blizzard mapping of LC/BC codes to protocol stages, and no public list of OW1-era code meanings beyond the generic "disconnected/unable to connect".
- No public information on whether the retail client exits the process on any join or integrity failure.

## Q3. How Overwatch replicates remote (non-local) entities, lag compensation and hit validation, damage events, kill feed and health

### Takeaway
Public material indicates the following model:
- Remote entities are shown from server updates via an interpolation delay (about 60 ms at 21 Hz, about 20 ms at 63 Hz), with extrapolation in some cases.
- The local player's movement, abilities and weapons are predicted.
- Hit validation is server-side with rewind ("favor the shooter"), with exceptions for escape abilities and a latency cap (about 220–250 ms secondhand) beyond which hit prediction is disabled.

For the emulator, this means the client does not simulate gravity or animation for non-controlled entities. The server must continuously supply their movement state. Damage and kill events must be emitted as server events.

### Cited Findings
- Interpolation delay "typically hovered around 60ms" before High Bandwidth and is "closer to 20ms for many players" after it. Ford: "you will be shot around corners less and you'll be able to predict escape moves better". He also warned that if someone "acts within a 20ms window, that prediction will fail". — [GamesBeat](https://gamesbeat.com/overwatch-netcode-tick-rate-60hz/)
- HEXUS reported interpolation delay falling "from about 55-ish to about 20". — [HEXUS](https://hexus.net/qac6rc)
- Digital Trends: when a connection can't keep up, the server downgrades the player, "but the interpolation delay will increase". — [Digital Trends](https://uat4.www.digitaltrends.com/?p=1041672)
- The German write-up of the April 2016 video (seen only via search snippet) says it covers "Favor the Shooter", responsiveness, tick rate, interpolation and extrapolation. It describes "favor the shooter" as a hit counting when the shooter hits what they see even if the target has moved on, with an exception for escape abilities (e.g. Pharah's jetpack) where the target is favoured. — [GamePro](https://www.gamepro.de/artikel/overwatch-blizzard-erklaert-den-netcode-208hz-client-tickrate,3270422.html) (body not fetched; 403)
- Edgegap's summary of the GDC talk:
  - The server rewinds the world to the shooter's frame before testing hits.
  - It first tests the ray against a bounding volume covering about the last half-second of each entity's movement, and fully rewinds only entities that intersect.
  - Above about 220 ms RTT, hit-impact prediction is disabled and extrapolation (dead reckoning) is used instead.
  - Impact side effects are queued as "pending contact records" in a singleton component and processed in one system per frame.
  — [Edgegap](https://edgegap.com/blog/game-backend-deep-dive-overwatch-2016-netcode-architecture-rollback)
- A forum summary of a 2016 OW dev talk mentions "a 250ms limit to client-side hit-prediction in the past". It also says client-side hit registrations are denied when the server knows the target has activated a damage-mitigating ability. This is secondhand and partly about then-unshipped changes. — [AnandTech forums](https://forums.anandtech.com/threads/overwatch.2451315/post-38255056)
- Blizzard (OW2 era) said it wants hit registration "working pixel-perfectly" and attributed many reports to the replay tool not perfectly capturing aim alignment. — [Charlie INTEL](https://www.charlieintel.com/overwatch-2/overwatch-2-devs-respond-to-rubberbanding-hit-registration-issues-204321/)
- Orwig's GDC 2017 replay talk covers building a replay system "alongside the network model", transferring kill-cam reels within the respawn window, and an interruptible kill cam. The abstract only is available. — [GDC Vault 1024053](https://gdcvault.com/play/1024053/Replay-Technology-in-Overwatch-Kill)
- General literature on interpolation buffers (Gaffer On Games, "Snapshot Interpolation"):
  - Buffer enough delay to "lose two packets in a row" (about 3× the send interval plus jitter).
  - Too little buffer causes hitching on each lost packet.
  - Extrapolation "doesn't know anything about the physics simulation" and mispredicts collisions.
  - Hermite interpolation using sent velocity gives smooth motion.
  - At 60 pps the equivalent delay is about 85 ms; at 30 pps about 150 ms.
  — [Gaffer On Games – Snapshot Interpolation](https://gafferongames.com/post/snapshot_interpolation/)
- Halo: Reach ("I Shot You First", David Aldridge, GDC 2011), via secondary write-ups:
  - Replication splits into **state, events and control** data, each with its own reliability contract.
  - State is intentionally unreliable ("Tribes model"), which enables a per-client prioritization engine to fit 16 players into the bandwidth budget.
  - Approximate figures: ~250 kbit/s upstream for a 16-player host and ~45 kbit/s from host to one client.
  — [Edgegap search snippet for Halo Reach deep dive](https://edgegap.com/blog/game-backend-deep-dive-halo-reach-netcode-host-migration) (page fetched as marketing only; claims from snippet); [UCL reading group](https://ng.cs.ucl.ac.uk/?p=115)

### Inferences
- **Bots that don't fall or animate (problem 2).**
  - Overwatch's netcode only predicts and simulates movement for the locally controlled entity (movement is one of three netcode systems, with rollback for the local player). Remote entities are therefore almost certainly rendered from replicated movement state through the interpolation buffer, not simulated locally. The project already observed that "remote entities don't fall", which is consistent with this.
  - The server must run gravity, ground snapping and locomotion for bots itself.
  - It must stream each bot's movement state continuously on the 16 ms (or 48 ms) cadence: position, velocity, facing/aim, and grounded/air flags if present in the snapshot field map.
  - With a ~20–60 ms interpolation delay, a few isolated snapshots yield a frozen or teleporting entity, because the buffer underruns between them. Continuous streaming at a fixed cadence is required for smooth motion.
  - Third-person locomotion animation is probably derived client-side from interpolated velocity and the movement state flags. Velocity fields in the module-3 block (e.g. the +0x20 vector gated by bit 19) and the view-angle floats (fields 7/8) are the likely drivers. This is a hypothesis to test: send a steady velocity plus matching position deltas and watch for the run animation.
  - The selected/controlled-entity gate in 0x7c7f50 ("applies per frame if selected entity valid") suggests the per-entity module-3 path may be tied to the local controlled entity. Remote entities may instead need a separate interpolation path, such as component-1 transform updates via module-4 op 2 or another module. Worth checking whether module-3 items for non-selected entities are ever consumed. The project's bot-placement difficulty ("module-3 position snapshots do not place a non-controlled entity there") fits this.
- **Damage numbers, kill feed and health.**
  - "Pending contact records" processed once per frame is the server-side batching of impacts.
  - The project's observed 27500 combat-event family (three entity ids plus u64s) is the natural carrier for server-confirmed damage/kill events, plausibly (attacker, victim, inflictor/ability GUID, amount/flags). These would drive damage numbers, hit markers beyond client prediction, and the kill feed. Hypothesis: send a 27500 record per damage instance and a distinct kind for kills, after mapping its native handler.
  - 25800 (stats) likely drives scoreboard and career counters, not visuals.
- **Red vignette (problem 4).**
  - Health is almost certainly replicated as component state through the same reflection path as component 44/74 (u8 mask + raw LE fields).
  - The bot "component 51" path (op 2 'health' updates) already exists in the responder. Applying the same to the player hero's health component, with max and current health set at create time, is the obvious test.
  - The red vignette probably means the local health component is at 0 or uninitialized, which the HUD reads as critical or dead.
- **Hit validation design for the emulator.** Keep a per-entity position history keyed by 16 ms command frame (about 0.5 s, as in OW's bounding-volume rewind). For each fire command, rewind bots to the command's frame minus the client's interpolation delay. Test the ray from the replicated eye position using the yaw/pitch carried in that command. This replaces the current server-estimate test and matches "favor the shooter".
- [background, not verified this session] Valve's Source model computes command execution time as current server time minus packet latency minus client view interpolation, and rewinds hitboxes accordingly. The canonical page is https://developer.valvesoftware.com/wiki/Lag_Compensation (it returned 403 here).

### Gaps
- No public description of how Overwatch encodes remote-entity movement in packets, its priority/relevancy scheme, or whether it uses Hermite or linear interpolation.
- No public documentation of damage-event or kill-feed message formats, or of health replication.
- Primary text of the 2016 video's "favor the shooter" exceptions was not retrievable (403); only snippets are available.

## Q4. Client-side movement prediction and reconciliation; designing server-authoritative Blink/Recall

### Takeaway
Overwatch predicts movement and all abilities by default. On misprediction it rolls back to the server's authoritative movement snapshot and replays buffered inputs, relying on deterministic movement simulation. Server-side teleports drift because the server teleports without colliding against map geometry, and probably also without tying the correction to the command frame the client will replay from. The fix is to (a) resolve the destination with real collision (sweep plus depenetration) and (b) send the corrected state as a movement snapshot that references the last processed command frame. Alternatively, let the client predict Blink through its own ability graph and have the server only confirm.

### Cited Findings
- "Movement, all abilities, and weapons are predicted by default"; teams must opt out. — [Edgegap](https://edgegap.com/blog/game-backend-deep-dive-overwatch-2016-netcode-architecture-rollback)
- On misprediction, the client "rolls back to the server's authoritative movement snapshot and replays all buffered inputs to the present". Movement simulation is highly deterministic, so corrections are usually invisible. — [Edgegap](https://edgegap.com/blog/game-backend-deep-dive-overwatch-2016-netcode-architecture-rollback)
- Gaffer On Games, "Networked Physics (2004)":
  - Inputs carry time/sequence, and the server ignores stale input.
  - The server returns state together with the input it processed.
  - The client keeps "a circular buffer of saved moves", and "rewinds to the corrected physics state and time and replays the stored moves".
  - Small errors are smoothed with an exponentially smoothed moving average on position and orientation, while velocities are snapped.
  - For differences over about 2 m, the client snaps.
  — [Gaffer On Games – Networked Physics 2004](https://gafferongames.com/post/networked_physics_2004/)
- Ford's caveat: escape moves become more predictable at a higher update rate, and the server sometimes favours the target for escape abilities. Escape abilities therefore interact specially with hit validation. — [GamesBeat](https://gamesbeat.com/overwatch-netcode-tick-rate-60hz/); [GamePro snippet](https://www.gamepro.de/artikel/overwatch-blizzard-erklaert-den-netcode-208hz-client-tickrate,3270422.html)
- A secondhand community claim: the server denies client hit registrations when it has already registered a defensive-ability command, citing Tracer's Blink. This is unofficial. — [AnandTech forums](https://forums.anandtech.com/threads/overwatch.2451315/post-38255056)

### Inferences
- **Why Blink drifts into geometry (problem 3).** The project teleports by pushing absolute position snapshots (four times) to (x, z) targets such as x = 48.71, which lies inside a wall. Two things go wrong.
  - (1) The destination is never collision-resolved, so the client's deterministic movement code depenetrates the capsule. The repeatable landing spot around (52.5, 30, 14.3) when teleporting into geometry is consistent with a native "stuck" resolution or fallback.
  - (2) The snapshot probably isn't anchored to the command frame. In a rollback design, the client takes the server snapshot as the state at command frame N and replays its buffered commands N+1..now on top of it. If the server sends a position as though it were "now", the replay of W/strafe inputs adds extra displacement, giving drift proportional to RTT × speed. Sending the same snapshot four times compounds this if each is replayed from a different base.
- **Recommended designs, in order of fidelity.**
  - (A) Client-predicted Blink, as retail does. Activate the hero's Blink ability states through statescript, as already done for WeaponVolley/reload, and let the client's own movement code perform the predicted blink with real collision. The server then mirrors the result by echoing the client-reported movement state and does not invent a position. The project's earlier attempt to force BlinkEffect states crashed the client (run 160). That means the required state data or ancestor chain is incomplete, not that the approach is wrong.
  - (B) Server-authoritative Blink. Compute the destination with a capsule sweep against the map's collision mesh: Tracer's Blink is a short horizontal dash that stops at walls. Write one snapshot that carries the destination as the authoritative state for the specific command frame whose 0x2000/0x8 edge triggered it, then stop and let prediction continue. If the snapshot format has an "ack/last command frame" field, set it to that frame.
  - (C) Interim: use the client's own last reported position (decoded from its commands or prediction) as the origin, clamp the blink distance against known walls, and always land on the floor height (y = 2.0 in the spawn room). This approximates (B) without full collision.
- Recall (Tracer) is a rewind to a recorded position history about 3 s back. A server ring buffer of confirmed positions per command frame gives an exact target that is collision-safe by construction, since the player occupied those positions. Recall should be far more robust than Blink in a server-side implementation.
- Time dilation and input buffering matter for any server-side movement authority. If the server applies movement from its own clock instead of the client's command frames, it will diverge. The emulator should key all movement and ability effects to the client's command-frame id from the module-3 header u32.

### Gaps
- No public description of the exact movement-snapshot fields, of which field acknowledges the command frame, or of how Overwatch's client handles a server teleport (snap versus smooth threshold).
- No public description of how Blink/Recall are implemented in the retail ability system; only the general statement that all abilities are predicted.
- Halo Reach and Unreal CharacterMovement / Tribes primary texts were not fetched this session. [background, not verified this session] Unreal's CharacterMovementComponent uses saved moves with timestamps, ServerMove RPCs and ClientAdjustPosition corrections tied to a timestamp. The Tribes networking model (Frohnmayer & Gift) describes a move manager plus ghost manager with per-object priority. Both are conceptually the same as OW's rollback.

## Q5. Public analysis of Overwatch's AES-GCM transport, the Battle.net referral/"game utilities" flow, and related Blizzard titles' transports

### Takeaway
No public analysis of Overwatch's AES-GCM game transport, its referral keys, or a shared Blizzard game-transport library (HotS/SC2/D4) was found in this session. Public material stops at port lists and generic Battle.net login/lobby behaviour.

### Cited Findings
- Public port information lists Overwatch's Battle.net TCP 1119 (matching the project's BNet port) plus 3724/6113/80. Game UDP ranges are inconsistent between sources (26503–36503 community; 12000–64000 described as voice). — [Blizzard forum port post](https://us.forums.blizzard.com/en/sc2/t/how-to-put-in-ports-number-for-blizzard-games/7533); [VidaExtra](https://www.vidaextra.com/guias-y-trucos/caida-servidores-overwatch-como-solucionar-problemas-red-perdida-conexion-overwatch-2)
- Blizzard's Battle.net publications archive exists (historical engineering publications), but this session did not examine it for transport details. — [bnetarchive.elaztek.com publications](https://bnetarchive.elaztek.com/Inside/publications.html)
- A curated list of game-networking resources (useful general references; no Blizzard-specific transport analysis surfaced). — [unitycoder/Game-Networking-Resources](https://github.com/unitycoder/Game-Networking-Resources)

### Inferences
- Because no public analysis exists, the project's docs/BGS_PROTOCOL.md "Instance datagram format" is probably the most detailed public description of this transport. Any claims about HotS/SC2/D4 sharing the library would be speculation without binary comparison.
- [background, not verified this session] Older Blizzard titles (SC2/HotS) used Battle.net 2.0 BGS RPC over TCP 1119 for lobby services, consistent with the project's lobby layer. Their game-session transports are not publicly documented either.

### Gaps
- No public reverse engineering of the AES-256-GCM envelope, referral key fields, the 22-byte AAD header or the receipt bitmap.
- No public source compares Overwatch's transport with Heroes of the Storm / StarCraft II / Diablo IV transports. A targeted search for those titles' game-server protocols was not completed within the tool budget.
- No public info on server-side anti-cheat or integrity handshakes in the instance join.
