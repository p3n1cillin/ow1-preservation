# Blizzard's public GDC talks on Overwatch gameplay architecture, netcode, Statescript networking and replays, mapped to an OW1 server reimplementation

Scope note: all sources below describe the OW1 era (2016 developer update; GDC 2017, Feb 27 to Mar 3, 2017). The most authoritative primary source found is Dan Reed's own slide deck (PDF, 82 slides, downloaded from media.gdcvault.com and read in full). For Tim Ford's talk, no English transcript was reachable: YouTube caption access required login from this environment, and GDC Vault provides video only. The detailed Ford content therefore comes from the community Chinese translation by "kevinan" (made for Tencent GAD), mirrored at max2d.com. It is a near-verbatim translation with slide/figure numbers ("图39" etc.), but it is still a translation. No transcript or detailed write-up of Philip Orwig's replay talk was found. Its content here is limited to the official abstract and Ford's own description of the kill cam.

Slide references: "Reed slide N" = page N of the official PDF. "Ford fig. N" = figure numbers quoted in the kevinan translation, which follow Ford's slide numbering.

## Q1. Tim Ford, GDC 2017 "'Overwatch' Gameplay Architecture and Netcode": ECS, command frames, prediction/rollback, input buffering, hit registration

### Takeaway
Ford describes the whole netcode model as follows:
- **Shared timeline:** fixed 16 ms command frames (7 ms in tournament mode). The client runs about RTT/2 + 1 buffered frame ahead of the server.
- **Movement prediction:** deterministic and client-predicted, with ring buffers of movement state and input. On a mismatch the client restores the last server-validated MovementState and replays all inputs.
- **Server input buffer:** small, with starvation handled by duplicating the last input, a "time dilation" feedback signal to the client (16 to 15.2 ms), and a QuakeWorld-style sliding window of all unacknowledged inputs.
- **Abilities:** client-predicted Statescript with rollback/roll-forth.
- **Hit registration:** predicted on the client but validated server-side by backward reconciliation (rewind) of MovementState. Damage is never predicted.

Only a handful of systems are netcode-related, and only three are gameplay netcode systems.

### Cited Findings
**Session basics**
- Official abstract: "'Overwatch' uses a cutting-edge Entity Component System (ECS) architecture"; Ford covers "how this networked simulation works, and how it leverages determinism to achieve responsiveness and precision." Speaker: Timothy Ford, Programming track, GDC 2017, marked "free content" on GDC Vault — [GDC Vault 1024001](https://gdcvault.com/play/1024001/-Overwatch-Gameplay-Architecture-and)
- Free YouTube upload found by YouTube search: "Overwatch Gameplay Architecture and Netcode", video id 8QHHVpBiG-I — [YouTube](https://www.youtube.com/watch?v=8QHHVpBiG-I); the same video is linked by [Edgegap](https://edgegap.com/blog/game-backend-deep-dive-overwatch-2016-netcode-architecture-rollback)

**ECS architecture** (translation of the talk — [max2d.com mirror of kevinan translation](https://max2d.com/archives/956))
- A World ("EntityAdmin") holds all Systems plus a hash table of entities keyed by entity ID.
- The entity ID is a 32-bit unsigned integer that uniquely identifies the entity in the entity array.
- Each entity also stores its ID and an optional "resource handle" pointing at the asset that defines it.
- Component is a base class with hundreds of subclasses. Polymorphism is used only for lifecycle (Create, destructor) plus simple accessor helpers.
- Systems have behaviour but no state. Components have state but no behaviour.
- Overwatch's client had about 46 Systems and 103 component types, and there was a separate server list.
- Systems iterate a "primary" component and then fetch sibling components (tuples).
- Example: the AFK-kick System iterates Connection components, whose tuple includes InputStream and Stats.
- Bots have no Connection or InputStream component, only Stats, so the AFK System never touches them.
- **Singleton components:** they belong to a single anonymous entity reachable through the EntityAdmin. About 40% of all components are singletons. Example: SingletonInput. InputSystem fills it from the OS, and CommandSystem (which owns PostBuildPlayerCommand) builds the PlayerCommand structure. PlayerCommands are "very important data structures which will be synchronized over the network and used to simulate the game".
- Singletons came out of the kill-cam work. The kill cam needed a second EntityAdmin ("liveGame" and "replayGame"), which broke global System access.
- **Utility functions:** shared behaviour lives in utilities with few component dependencies and few side effects. Examples:
  - `CombatUtilityIsHostile(entityA, entityB)` reads three optional components: filter bits (stores team index), pet master and pet. Two entities without filter bits (e.g., two doors) are not hostile. A projectile's hostility is traced back to its shooter.
  - `CharacterMoveUtil` moves the player each tick. It has exactly two call sites: server simulation of player input commands, and client prediction of player input.
- **Deferment:** the "Contact" singleton holds pending impact records. ResolveContactSystem creates the effects late in the frame, before render prep, with LOD and per-frame budgeting.
- Deferred entity creation caused bugs (an entity requested in System A was only usable a frame later in System B). It was changed after launch to allow mid-frame creation, in patch "1.2 or 1.3". Deferred destruction was kept.
- ECS rules ("took about 1.5 years"): components have no functions, systems have no state, shared code goes in utils, complex side effects are deferred through queues (especially singletons), and systems do not call other systems.
- Multithreading: projectile simulation, ResolveContactSystem effect creation, AIPetDataSystem and PathValidationSystem use fork/join workers hidden behind "iceberg" systems.
- Pathing (blue walkable surfaces) "is not only used for AI but also many hero abilities, so it must be synchronized between server and client".

**Determinism and command frames** — [max2d.com translation](https://max2d.com/archives/956)
- Determinism relies on clock synchronisation, a fixed update period and quantisation. Time is quantised into "command frames".
- Each command frame is a fixed 16 ms, or 7 ms in esports/tournament play. Wall clock is converted to a command-frame number with a looping accumulator.
- Any System that predicts, or simulates from player input, uses `UpdateFixed` instead of `Update`. UpdateFixed is called once per command frame.
- Assuming a steady input stream, the client is ahead of the server by about half the RTT plus one buffered frame (RTT = ping plus processing time). The example in fig. 39 uses a 160 ms RTT, giving 80 ms + 16 ms.
- The client simulates and sends input for frame 19. The server simulates that frame roughly RTT/2 plus the buffer later.
- "The game runs at 60 Hz" (the animations shown were slowed to 1/100 speed).

**Movement prediction and reconciliation** — [max2d.com translation](https://max2d.com/archives/956)
- Responsive actions: movement, abilities, weapons with abilities, and hit registration. They must respond instantly "even at 250 ms ping".
- The client prediction System reads current input and simulates movement. The server returns a validated movement-state snapshot a full RTT plus buffer later.
- The client keeps a ring buffer of its historical movement states to compare against the server result. A mismatch is a misprediction and must be reconciled.
- A second ring buffer stores the player's inputs. Because movement code is deterministic, the client restores the last server-validated movement state and replays all inputs up to the present. Example (fig. 41): a client thinks Tracer is running, but the server says she was stunned by McCree's flashbang at frame 17, received when the client is at frame 27.
- Ford's misprediction demo: at 250 ms ping a jump is rejected because the player was frozen by Mei. The ability cooldown had already been predicted.

**Input transport, buffering, time dilation and the sliding window** — [max2d.com translation](https://max2d.com/archives/956)
- Input is sent via "custom reliable UDP".
- The server keeps a small buffer of unsimulated inputs. When it is empty, the server must guess from the last input (duplicate it) and later reconciles.
- On packet loss the server duplicates the previous input, predicts, and tells the client that loss is occurring.
- The client then performs time dilation: it simulates faster than the agreed rate, pretending the frame time is 15.2 ms instead of 16 ms. Inputs arrive faster and the server buffer grows.
- When the network is healthy again, the server tells the client, and the client dilates back so the server buffer shrinks.
- Sliding window (credited to QuakeWorld): the client sends not only the current frame's input but every input since the last movement state the server acknowledged. Example: last ack frame 4, current frame 19, so all 15 frames go in one packet. This compresses well because input changes rarely. After loss, the next packet fills the holes before simulation.
- Edgegap's secondary summary of the same talk gives the same 16 to 15.2 ms figures — [Edgegap](https://edgegap.com/blog/game-backend-deep-dive-overwatch-2016-netcode-architecture-rollback)
- 云风 (codingnow) summary, reprinted on GCORES, adds the commentator's numbers "60 fps to 65 fps". That is consistent with 16 to 15.2 ms (1000/15.2 is about 65.8) but is a commentator's paraphrase — [GCORES reprint](https://www.gcores.com/articles/190857)

**Abilities via Statescript** — [max2d.com translation](https://max2d.com/archives/956)
- All abilities are built in Statescript, which "can travel back and forth through time".
- Abilities use the same principle as movement: roll back to the last validated snapshot state, then replay input up to now.
- Example (fig. 45): Reaper's Wraith Form states are predicted on the client. When the server's update arrives ("I predicted the wraith form, rewind, turn these states on, re-simulate all inputs, turn them off"), the client rolls back and rolls forth.
- "Being able to predict movement means we can predict every ability, and we do; likewise for weapons."
- Ford defers details to Dan Reed's talk.

**Hit registration, damage and backward reconciliation** — [max2d.com translation](https://max2d.com/archives/956)
- An entity can be hit if it is hostile and has a `ModifyHealthQueue` component.
- ModifyHealthQueue holds all damage and healing recorded by the server. It is deferred like the Contact singleton.
- "Damage is never predicted on the client because they're all cheaters." Hit registration (impact prediction) is done on the client.
- Remote entities with a `MovementState` (not controlled by the local player) are repositioned by the movement System, interpolating between the last two received MovementStates ("since Quake").
- The System does not care whether it is a moving platform, turret, door or Pharah. MovementState also stores the ring buffer.
- The server rewinds hostile MovementState holders to the frame the attacker reported (backward reconciliation). Doors, platforms and payloads are rewound too, so blocked shots stay blocked. Rewinding is done by utility functions. Damage is the separate deferred behaviour.
- Culling: each entity's bounding volume is the union of its snapshots over about the last half second. Only entities whose volume the shot intersects are rewound (fig. 47).
- Above 220 ms ping, some hit effects are deferred and impacts are no longer predicted. The client waits for the server, because targets are already extrapolated and the server should not rewind that far, so a victim who reached cover is not killed.
- At 300 ms impact prediction is off and remote targets are dead-reckoned (extrapolated). At 0 ping, impact collisions are predicted but hit points and health bars wait for the server.
- Misprediction examples at 150 ms:
  - A Mei ice wall raised the shooter, so the predicted blood effect appeared but no health bar or decal.
  - Reaper entered Wraith Form before the arrow hit: "most of the time favour the attacker, unless the victim did something to mitigate."
- Most hit mispredictions were fixed by making client and server agree on positions.

**Netcode systems** — [max2d.com translation](https://max2d.com/archives/956)
- A player is "an entity controlled by something with a Connection component".
- Core netcode systems: NetworkEvent and NetworkMessage, which receive input and send output.
- Gameplay-netcode systems (fig. 52): InterpolateMovement, Weapons, Statescript, MovementState. Ford says only three systems are gameplay-related.
- The components those systems use are mostly read-only. The one that writes is ModifyHealthQueue.

**Kill cam (as described by Ford)** — [max2d.com translation](https://max2d.com/archives/956)
- The server sends roughly 8–12 seconds of network game data.
- The client flips to the second world (replayAdmin), renders it, and feeds the data to replayAdmin "pretending it really came from the network". No System or component knows it is not live or predicted.
- Ford refers listeners to Phil Orwig's talk the next day at 11:00.

### Inferences
**What this means for the OW1 server reimplementation**
- **Command frame and command rate.** The project observed about 62.5 commands/s and 6 m/s per 16 ms step. This matches the 16 ms command frame exactly; 62.5 Hz is 1000/16. The server's movement snapshots should therefore be indexed by command frame. The client most likely reconciles its ring buffer against the command frame the server says it has processed.
  - If the reimplemented server never acknowledges client command frames in its movement snapshots, the client's input window keeps growing, and reconciliation may compare against the wrong history.
  - Inference only; the exact ack field in the module-3 snapshot is not described publicly.
- **Client command packets.** These should contain redundant input history from "last acked movement state" to "current frame" (sliding window).
  - The project's module-3 command decoder (42 bits plus a header u32 per block, several blocks) is consistent with this.
  - The server should process each command frame exactly once, discard duplicates, and advance its acknowledgement so the window shrinks.
- **Time dilation.** There must be a server-to-client signal ("loss detected / healthy") that makes the client simulate at 15.2 ms instead of 16 ms. The reimplemented server does not need to send it, but it should tolerate slightly faster command rates. It must not, for example, treat 65 commands/s as a speed hack.
- **Damage is server-only.** The client predicts impact effects but never health. A server-sent health component update (the project's op 2 / ModifyHealth-like state) is required for any health-bar change. The project's "red vignette = no health replication" observation fits this.
- **Hit registration for bots and other remote entities.** The server should rewind targets' MovementState to the attacker's command frame (attacker command frame minus interpolation delay). The project's current server-estimate ray test against fixed bot positions is a simplified version of this.
- **Remote entity rendering.** Remote movement uses interpolation between the last two MovementStates. The server therefore needs to stream periodic MovementState snapshots for non-controlled entities, which ties in with the project's open "remote-entity position replication".
- **Kill cam.** Because the kill cam re-feeds the network stream into a second client world, the client keeps (or receives) a copy of recent network messages. The client-side replay world (a second EntityAdmin) explains why the project sees two world managers. Plausible but unverified; the project's "two managers" may instead be the world/sub-world split.

### Gaps
- No English verbatim transcript or official slide PDF of Ford's talk was reachable. YouTube captions required login; GDC Vault offers video only. Numbers come from the kevinan translation and agree with Edgegap's independent summary.
- The talk does not describe:
  - the handshake/connection establishment;
  - the packet format;
  - how the movement-state ack is encoded;
  - how the server signals time dilation;
  - the exact interpolation delay.

  Ford says explicitly that he skips generic replication, remote entity interpolation and backward-reconciliation details.
- Nothing about the "occasional early instance join failure" or HUD initialisation.

## Q2. Dan Reed, GDC 2017 "Networking Scripted Weapons and Abilities in 'Overwatch'": Statescript networking, prediction, misprediction

### Takeaway
Statescript is server-authoritative and eventually consistent.
- **What crosses the wire:** only button input and aim go client to server. The server records per-command-frame StatescriptDeltas (instance creation/destruction, changed instance variables, changed state indices, executed action indices, changed owner variables).
- **Per-client acknowledgement:** per-client "ghosts" track the last acknowledged command frame. Packets carry the union of deltas over a command-frame range, or a full current-value snapshot when the range starts at 0.
- **Local entity (predicted):** exactly one networked entity per client. It receives "everything" and does rollback, replicate, then simulate (roll forth) using an internal command frame.
- **Remote entities (not simulated):** they receive only SYNC_ALL nodes and the variables those nodes reference, with bit widths precomputed at script compile time.
- **Unsynchronized instances:** menus, Hero Gallery, end-of-match flow and music run unsynchronized and only read variables off synchronized instances and receive messages from them.

### Cited Findings
All from the official slide deck unless noted — [Reed slides PDF](https://media.gdcvault.com/gdc2017/Presentations/Reed_Dan_NetworkingScriptedWeapons.pdf)

**Talk framing**
- Free video on GDC Vault — [GDC Vault 1024653](https://gdcvault.com/play/1024653/Networking-Scripted-Weapons-and-Abilities)
- YouTube upload found: odSBJ49rzDo — [YouTube](https://www.youtube.com/watch?v=odSBJ49rzDo)
- Bilibili mirror — [bilibili](https://www.bilibili.com/video/BV1VE411b7tV/)
- Overview (slide 2): the talk explicitly does not cover projectiles, hit registration, or tech for specific abilities. It runs about 15 min of what and how, 30 min of networking, 5 min of benefits.

**Language and runtime structure**
- Instances (slide 5): playing a script creates a "Statescript Instance". Instances are owned by an Entity, can be added and removed dynamically, and multiple instances of the same script are allowed.
- Example scripts (slide 4): Tracer's Recall, the Lucio buff, common UI elements.
- Node kinds: Entry, Condition, Action, State.
- Variables (slide 7): "bags" of Instance Variables and Owner Variables; primitive or arrays of primitives; can be "state-defined".
- Config Vars (slides 8–9): literals, variables, utilities ("Is Hero Select Active", "Get Entity Position", ...) and expressions. Subgraphs and containers exist (slides 10–11).
- Runtime (slides 21–22):
  - timing is based on Command Frames;
  - playing scripts requires a StatescriptComponent with `int m_internalCommandFrame; Array<StatescriptInstance*> m_instances; StatescriptVarBag m_ownerVars; StatescriptSyncMgr m_syncMgr;`;
  - each instance has `int m_instanceID; const STUStatescriptGraph* m_stuGraph; Array<StatescriptState*> m_states; List<StatescriptEvent*> m_futureEvents; StatescriptVarBag m_instanceVars;`.
- State API (slides 23–25): GetBool/Int/Float/Vec/EntityID; EnqueueTimerEvent/AbortStateEvent/FinishStateEvent; SetFrameTickingEnabled; OnActivate/OnDeactivate/OnTimerEvent/OnFrameTick/OnInternalDependencyChanged/OnBecameActiveThisTick/OnBecameInactiveThisTick/OnActivationChangedThisTick/GetStateDefinedValue. There is a dependency listener/provider pattern.
- Variables (slide 26):
  - VarBags are tables keyed by a **16-bit identifier**;
  - StatescriptVarPrimitive / StatescriptVarPrimitiveArray;
  - primitives are stored in a **128-bit union**;
  - vars are dependency providers and optionally reference a StatescriptState.
- Data (slides 27–29): assets are "Structured Data (stu)" compiled to generated code with runtime reflection. The example `STUStatescriptStateWait { embed<STUConfigVar> m_timeout; embed<STUStatescriptOutputPlug> m_onAbortPlug; m_onFinishedPlug; }` is implemented by `StatescriptStateWait::OnActivate -> EnqueueFinishStateEvent(GetFloat(stu->m_timeout))`.

**Networking model** (slides 31–41)
- Requirements: usability (non-invasive), responsiveness, security ("preventing hackers from influencing server behavior"), efficiency, seamlessness.
- Synchronized Instances (slide 38): server and client describe the same instance and are "eventually consistent".
- Unsynchronized instances (slide 38): receive messages from synchronized instances, read variables off synchronized instances, and are otherwise independent.
- Played synchronized (slide 39): weapons, abilities, emotes, game modes, map entities. Played unsynchronized: menus, Hero Gallery, end-of-match flow, music.
- Local vs remote (slide 40): "A single networked Entity is allowed to be controlled by the player. This Entity is local; all other networked Entities are remote. The server keeps track of which Entities are local to which clients."
- Server authority (slide 41): "Statescript is server-authoritative. Communication is mostly server-to-client. Button input and aim is client-to-server."
- Client input timing (slide 42): with RTT = 5 command frames (80 ms), client CF 100 + RTT = server CF 105.

**Server synchronization** (slides 43–50)
- Pipeline: gather input from clients, simulate, store changes in StatescriptDeltas, send deltas to clients.
- A StatescriptDelta is keyed by command frame and contains:
  - an array of all synchronized instances that changed, each with instance ID, flags for creation/destruction, changed instance variables (identifier; for arrays the affected index range), indices of states that changed, and indices of actions that executed;
  - an array of all owner variables that changed.
- Deltas are stored until all clients have acknowledged receipt of their command frame.
- StatescriptGhost (one per client): client ID, last acknowledged command frame, pointers to outstanding StatescriptPackets. It exists until the client disconnects.
- StatescriptPacket: Local/Remote flag, command-frame range (start and end), payload.
  - The payload is built as the union of all StatescriptDeltas in the CF range, then serialised as the current values of the objects referenced by that union.
  - "If the Command Frame range starts at 0, then just send the current values of all objects."
  - Packets are stored and reused, and kept until all clients acknowledge their end CF.
- Demo (slide 50): server CF 100/103/106/108/111 with a lost packet. The next packet's range covers the union since the last ack.

**Client synchronization, prediction and misprediction** (slides 51–57)
- The local entity stores input and predictions.
- On receiving a StatescriptPacket the client:
  - sends an acknowledgement;
  - ignores the packet if it is redundant or out of order;
  - if remote: replicates;
  - if local: rolls back, replicates, simulates.
- Remote entity (slide 52): the client just applies the server state at CF 100/103/105.
- Predicted packet (slide 53): the client is at CF 105 using internal command frames (ICF). On receiving server CF 100, it rolls back to ICF 100, replicates, and re-simulates ICF 101–105. Diagram labels "ICF 103, 100" and "ICF 104-108".
- Mispredicted packet (slide 54): the server reports CF 95. The client rolls back to ICF 95 and re-simulates ICF 96–100.
- C++ hooks (slides 55–56):
  - for states: OnActivate(ActivationReason), OnDeactivate(DeactivationReason), IsRollingBack(), IsReplicating(), IsRollingForth(), GetActivationSummary(), PutUpdate(DataStore*), GetUpdate(DataStore*);
  - for actions: DoRollback(), GetRollbackStorage().
- Mirrored data (slide 58): states declare a `mirror` struct in .stu (example `MStatescriptStateChaseVar { Vec3A m_curVal; s64 m_lastTickTime; s32 m_timeRemainingMS; bool m_isVec; bool m_hasDuration; bool m_hasReachedDestination; }`) and use WriteMirroredData/ReadMirroredData. This is per-state data that gets synchronized.
- Historical data (slide 60):
  - kept: all variables and states on the local entity; button input and aim; positions and poses for all entities;
  - not kept: variables and states on remote entities; data from other entity components "(such as for health and filtering)".

**Efficiency** (slides 62–68)
- Statescript analyzes scripts to discover synchronization requirements.
- Local entities: "StatescriptPackets must contain everything".
- Remote entities "do not simulate Statescript Instances". Their packets need only the states and actions remote instances care about, plus the variables those reference.
- `[STUStatescriptNode::SYNC_ALL]` attribute (slides 64–65):
  - with it, states and actions transmit locally and remotely, though runtime objects may opt out;
  - without it, states only transmit locally and actions do not transmit.
- Compiled per graph (slide 66): `array<internal<STUStatescriptNode>> m_remoteSyncNodes; array<inline<STUStatescriptSyncVar>> m_syncVars; s32 m_nodesBitCount; s32 m_statesBitCount; s32 m_remoteSyncNodesBitCount; s32 m_syncVarsBitCount;`.
- Numbers (slide 68), Tracer firing a full clip and reloading, exactly 2 s:

  | | Local | Remote |
  |---|---|---|
  | States | 463 bits | 190 bits |
  | Instance vars | 519 bits | 246 bits |
  | Owner vars | 54 bits | 54 bits |
  | Events | 431 bits | 0 bits |
  | Other | 561 bits | 316 bits |
  | **Total** | **2028 bits (1.0 Kb/s)** | **806 bits (0.4 Kb/s)** |

**Node catalogue and conclusions** (slides 70–79)
- Node type catalogue (slides 70–71):
  - State, Wait, Set Var, Chase Var, Boolean Switch, Cosmetic Entity, Logical Button State, Data Flow Mapping, Invisible, Stack, Weapon Volley;
  - Movement Mod Action, **Blink Effect**, **History Builder**, **History Rewinder**, Health Pool, Animation, Track Targets, Modify Health, Target Effect, Phase Out, Movement Mod State, **Teleport**, **Find Ground**, Camera 3P;
  - Send Game Message, Effect State/Action, Switch, Watch, Eject Cosmetic Entity, Aim Speed, Camera Transform, Extending Ledge Finder, Move To, Apply Aura;
  - **UX - Screen, UX - View Mode, UX - UI In World**, Destroy Entity, Animated Camera, Steer, Track Slamming, Camera Look At, Play Script, Create Entity State, Shockwave, **Suppress Movement Prediction**;
  - Beam Effect, Resurrect, Create Entity Action, Override Model Look, Object Placement Validation, Pet, Track Movement, Wall Move Raycast Action, Possess Control, Possess View, Deflect Projectiles (+ Effects), Limit Aim, Pause Anim, Combat Mod Filter, Restart Anim, Raycast State, Track Ray, Contact Set State, **Track Validated Position**, **Teleport Over Duration**.
- Benefits: new heroes need "little to no new code" and there are fewer lifetime and desync bugs.
- Challenge (slide 79): "The eventual-consistency networking model does not provide a perfect blow-by-blow replication".

**Third-party adaptation**
- The open-source Godot "FracturalStateScript" addon explicitly reimplements this rollback-friendly design (third-party, not Blizzard) — [GitHub](https://github.com/Fractural/FracturalStateScript)

### Inferences
**Mapping to the project's decoded statescript fields** (inference: names match the RE findings in CLAUDE.md)

| Reed concept | Project's reverse-engineered field |
|---|---|
| Packet CF range start/end; "range starts at 0 = all current values" | 'SFSF'/'SFDt' (base frame plus delta) and the "full snapshot / CmFD" path |
| Instance creation/destruction flags + instance ID | 'Inst' instance-ID delta, the destroy bit, create = graph u16 |
| Changed instance variables (id + array index range) | 'IVDt' / 'UVGu' and ArrC/ArrS/ArrE (array start/end) |
| Owner variables | Entity-global vars (m_60DB8F99=1 vars, global UVGu list) |
| Changed state indices | 'StDt' |
| Executed action indices | 'EIns' (likely "executed instances/actions"; unverified) |
| 16-bit var identifier | Project's u16 var ids (printed byte-swapped) |
| m_syncVars / m_remoteSyncNodes / bit counts | Project's GRAPH_COUNTS (32 sync vars, 146 states) and "remote-sync index" |
| Mirrored data (PutUpdate/GetUpdate) | Per-state "state data" read by 0x1b72060 / WeaponVolley data |

**Local vs remote packets.** The project should keep separate local and remote serialisations.
- For the **local** entity (controller plus controlled hero), "packets must contain everything", i.e. state indices over all `m_statesBitCount` states and events.
- For **remote** entities (bots, other players), only SYNC_ALL nodes are sent, indexed by `m_remoteSyncNodesBitCount`, plus the sync vars.
- Sending a local-form packet for a remote entity, or the reverse, would misalign the bitstream. This is consistent with the project's early "misaligned StDt" bugs.

**HUD and other UI.**
- Reed says menus, the Hero Gallery and end-of-match flow are unsynchronized, client-run scripts. They only *read variables off synchronized instances* and *receive messages from synchronized instances*.
- So the hero HUD is almost certainly client-local Statescript (UX - Screen / UX - View Mode / UX - UI In World nodes). It is gated by variables on the local entity's synchronized instances (owner/instance vars) and by game messages. It is not something the server instantiates.
- This matches the project's finding that the UI root (0x041a) is client-local and root-owned. It also suggests the missing HUD trigger is a synced variable or game message from a synchronized game-mode/hero instance, or the client's "local entity" designation (the Local/Remote flag in packets).
- Config var "Is Hero Select Active" is an example utility the UI reads.

**Movement abilities (Blink, Recall).**
- These are Statescript states such as "Blink Effect", "Teleport", "Find Ground", "Track Validated Position", "History Builder"/"History Rewinder" (Recall's position history) and "Teleport Over Duration".
- They are predicted on the client for the local entity: the client simulates the script from its own button input, and the server simulates the same script from the same input and confirms via deltas.
- The correct server behaviour is to enter the same Blink/Recall states in the hero's synchronized instance at the command frame the button was pressed, so the client's prediction matches. It is not to teleport the hero with position snapshots.
- Collision-safe destinations come from Find Ground / Track Validated Position logic, run identically on client and server. The project's server-side teleports ignore this and drift into geometry.
- The node "Suppress Movement Prediction" shows that movement prediction is the default and is selectively disabled by script.
- Inference: the project's earlier client exit when activating BlinkEffect may come from the local client not being in a rollback-capable/predicting state (no internal command frame history) when receiving a replicated, not predicted, Blink activation.

**History and health.** Health and filtering components are not kept historically or rolled back, so health is plain server-replicated component state. Damage feedback needs a component update, not statescript prediction.

**Acks and retransmission.**
- The server should track per client the last acked CF. It should send the union of all changes since that CF (current values), or a full snapshot (range start 0) when the client has never acked.
- Lost packets are not retransmitted verbatim; the next packet's range simply grows.
- The client ignores redundant and out-of-order packets, so the CF range end must increase monotonically.

### Gaps
- The slide text does not show:
  - the exact bit layout;
  - how the internal command frame relates to the server CF;
  - how predicted instance IDs are allocated for client-created instances (the project saw negative/65534+ client IDs, which is consistent with client-local instances);
  - how game messages (Send Game Message) are serialized.
- Speaker narration was not available (no transcript). The Chinese translation (CSDN wangchewen) and the Programmer Sought translation were unreachable: CSDN blocked, DNS failure.
- No public statement specifically on how Blink/Recall prediction is confirmed beyond the generic rollback model.

## Q3. Philip Orwig, GDC 2017 "Replay Technology in 'Overwatch': Kill Cam, Gameplay, and Highlights"

### Takeaway
Only the abstract and Ford's cross-reference are available.
- Replays were developed "in parallel with your network model": reels are generated and transferred within a hard respawn deadline, and the client architecture was refactored for an interruptible kill cam.
- Ford adds that kill cam is a second client ECS world fed about 8–12 s of recorded network data as if it were live network traffic.

### Cited Findings
- Abstract: kill cams "help you understand how your hero died"; Highlights and Play of the Game; "replays prove invaluable in reproducing bugs" — [GDC Vault 1024053](https://gdcvault.com/play/1024053/Replay-Technology-in-Overwatch-Kill)
- Listed topics, same source:
  - how to develop a replay system in parallel with your network model;
  - generating and transferring reels within a hard respawn deadline;
  - refactoring the client architecture for an interruptible kill cam;
  - accuracy/polish challenges;
  - custom scripting support for kill cams.
- Free on GDC Vault ("free content") and on GDC's YouTube channel; official YouTube id W4oZq4tn57w (embedded in Game Developer's article) — [Game Developer](https://www.gamedeveloper.com/design/video-how-blizzard-designed-and-built-i-overwatch-i-s-replay-tech); a second upload id A5KW5d15J7I was found by YouTube search.
- Ford's description: the server sends roughly 8–12 s of network data; the client switches rendering to the replayAdmin world and forwards the data to it as if from the network; systems do not know they are not predicted — [max2d.com translation](https://max2d.com/archives/956)
- Ford: singleton components were introduced because adding the kill-cam world (two EntityAdmins) broke global system access — [max2d.com translation](https://max2d.com/archives/956)
- Context: the high-bandwidth (63 Hz) change was partly motivated by kill cams not matching what players saw — [GamesBeat](https://gamesbeat.com/overwatch-netcode-tick-rate-60hz/)

### Inferences
- **Kill cam traffic.** Kill cam data is network replication data (entity creates/updates plus statescript packets) for the relevant entities. The server likely sends a recorded reel to the dying client.
  - A reimplemented server can skip kill cams initially. If the client expects a kill-cam reel after death, missing data may only disable the feature.
  - "Hard respawn deadline" suggests the client tolerates absence.
- **Replay packets.** Because replays reuse the normal replication stream, statescript packets in replays presumably use the "range starts at 0 / all current values" form at reel start.
- **Second world.** The project's second world-manager / replay world may be this replay EntityAdmin. The session "mode" values involving "replay" (project found reason string 7 = replay) are consistent with the replay world existing in the client.

### Gaps
- No transcript, slides or detailed blog summary of Orwig's talk was found in English or Chinese. YouTube captions were not retrievable (login required).
- Reel format, snapshot/delta structure, highlight selection and the interruptible-kill-cam refactor details remain unknown from public text sources. Watching the free video is required.

## Q4. Other Blizzard public material: "Let's Talk Netcode" developer update (2016), tick rate / high-bandwidth changes, other GDC talks

### Takeaway
The June 2016 developer update by Tim Ford and Philip Orwig explained favor-the-shooter with mitigation exceptions. The Aug–Sep 2016 "high bandwidth" change raised the server-to-client update rate from about 21 Hz (20.8) to 63 Hz on PC, with adaptive down-scaling. That cut interpolation delay from about 60 ms to about 20 ms. Simulation remained 16 ms command frames.

### Cited Findings
- **Who presented:** "Developer Update | Let's Talk Netcode | Overwatch" (found via YouTube search), presented by Tim Ford and Philip Orwig. It explains that "favor the shooter" logic applies regardless of the shooter's connection — [Gazzetta.gr](https://www.gazzetta.gr/entertainment/904022/lets-talk-netcode-video-gia-overwatch)
- **Exception to favor the shooter:** German coverage says Overwatch favours the shooter, so no leading for ping is needed, except escape abilities (e.g., Pharah's jetpack), where the server can favour the escaping player and drop the hit. Snippet only; page fetch was blocked (403) — [GameStar](https://www.gamestar.de/artikel/overwatch-blizzard-erklaert-den-netcode-208hz-client-tickrate,3270417.html)
- **Ford's GDC wording on mitigation:** "most of the time favour the attacker, unless the victim did something to mitigate", e.g. Reaper's Wraith Form — [max2d.com translation](https://max2d.com/archives/956)
- **Lylirra (Blizzard), Aug 2016:** high bandwidth changes the client update rate "from 21 updates per second to 63 updates per second", and Blizzard will "automatically and adaptively scale down your update rate" if a connection can't keep up — [Ten Ton Hammer](https://www.tentonhammer.com/news/overwatch-high-bandwidth-servers-rolling-out.amp)
- **GamesBeat on the PC high-bandwidth mode (Sep 2016):**
  - interpolation delay goes from typically about 60 ms to about 20 ms;
  - console was excluded at the time (Orwig: still working on console);
  - Ford: "you will be shot around corners less and you'll be able to predict escape moves better"; "all of our stuff is still predictive."

  [GamesBeat](https://gamesbeat.com/overwatch-netcode-tick-rate-60hz/) (the article loosely says "60Hz" and "21 ticks").
- **Rollout:** high-bandwidth option first in Custom Games (June 2016 patch notes mention stability fixes for it), later Quick Play and Competitive on PC — [Blizzard patch notes June 2016](https://overwatch.blizzard.com/en-us/news/patch-notes/live/2016/6/); [PC Gamer](https://www.pcgamer.com/au/high-bandwidth-support-is-being-rolled-out-to-overwatch-at-this-very-moment)
- **Other Blizzard GDC 2017 talks found (not networking):**
  - "Animation Bootcamp: The First Person Animation of Overwatch" (Matthew Boehm). 4Gamer reports Overwatch had 9 GDC 2017 sessions — [4Gamer](https://www.4gamer.net/games/280/G028066/20170228101/)
  - "The Animation Pipeline of 'Overwatch'" (Jesse Davis) — [GDC Vault](https://www.gdcvault.com/play/1024267/The-Animation-Pipeline-of-Overwatch)
  - "Thinking Globally: Building the Optimistic Future of 'Overwatch'" (Michael Chu) — [GDC Vault](https://gdcvault.com/play/1024266/)
  - "The Data Building Pipeline of 'Overwatch'" and "Overwatch – The Elusive Goal: Play by Sound (GDC 2016)" appeared in YouTube search results (titles only, not reviewed).

### Inferences
- **Two rates.** The client-to-server command rate (62.5 Hz, one per 16 ms command frame) and the server-to-client update rate (about 20.8 Hz before Aug 2016; 63 Hz high-bandwidth, adaptive) are separate.
  - 20.8 Hz is about one update per 3 command frames (48 ms); 63 Hz is about one per frame.
  - The final 1.74 client likely supports both and an adaptive rate, so the reimplemented server can choose to send one module-3/statescript frame per 16 ms or per 48 ms. The client should interpolate remote entities with a delay of about 2 update intervals.
- **Escape-ability exception.** This implies server-side hit validation must check whether the victim entered a mitigating state (Wraith Form, Pharah's jump, Blink) between the shooter's rewound frame and the present. That is server logic, not a protocol field.

### Gaps
- No transcript of "Let's Talk Netcode" was obtained, so its exact figures are not verified first-hand (e.g., the commonly cited "20.8 Hz", and statements on interpolation buffers).
- No Blizzard talk on Overwatch AI/bots, UI/HUD architecture or "The Visual Effects of Overwatch" was found in this pass. None of the networking talks address HUD construction beyond Reed's "UX" node names and the unsynchronized-instance rule.

## Q5. Where slides, videos and transcripts are available

### Takeaway
All three core GDC 2017 talks are marked free on GDC Vault and are on YouTube. Only Reed's slide PDF is publicly downloadable. A full Chinese translation of Ford's talk exists (several mirrors). No transcript of Orwig's talk was found.

### Cited Findings
- **Ford**
  - GDC Vault (free) — [1024001](https://gdcvault.com/play/1024001/-Overwatch-Gameplay-Architecture-and)
  - YouTube 8QHHVpBiG-I — [link](https://www.youtube.com/watch?v=8QHHVpBiG-I)
  - Chinese translation by kevinan for Tencent GAD — [max2d.com](https://max2d.com/archives/956), [cnblogs](https://www.cnblogs.com/herenzhiming/articles/7126477.html), [Tencent GWB](https://gwb.tencent.com/community/detail/114516), [juejin](https://juejin.cn/post/6844903635864780813) (anti-bot page), [lfzxb.top](https://www.lfzxb.top/ow-gdc-gameplay-architecture-and-netcode/)
  - 云风 commentary via [GCORES](https://www.gcores.com/articles/190857)
  - English secondary summary: [Edgegap](https://edgegap.com/blog/game-backend-deep-dive-overwatch-2016-netcode-architecture-rollback). It says client "46 systems / 103 components" but elsewhere "~150 systems"; treat its intro numbers with caution.
- **Reed**
  - Slides — [PDF](https://media.gdcvault.com/gdc2017/Presentations/Reed_Dan_NetworkingScriptedWeapons.pdf)
  - GDC Vault — [1024653](https://gdcvault.com/play/1024653/Networking-Scripted-Weapons-and-Abilities) / [1024041](https://gdcvault.com/play/1024041/Networking-Scripted-Weapons-and-Abilities)
  - YouTube [odSBJ49rzDo](https://www.youtube.com/watch?v=odSBJ49rzDo)
  - [Bilibili](https://www.bilibili.com/video/BV1VE411b7tV/)
  - Chinese translation on [CSDN](https://blog.csdn.net/wangchewen/article/details/120261782) (not retrievable here)
- **Orwig**
  - GDC Vault — [1024053](https://gdcvault.com/play/1024053/Replay-Technology-in-Overwatch-Kill)
  - YouTube W4oZq4tn57w via [Game Developer](https://www.gamedeveloper.com/design/video-how-blizzard-designed-and-built-i-overwatch-i-s-replay-tech)

### Inferences
- The highest-value next step for the open problems is to watch Reed's video, in particular slides 50–60 narration on rollback, and Orwig's video. A local transcript could be produced from an authenticated YouTube session or the GDC Vault player.

### Gaps
- Ford's and Orwig's slide PDFs were not found on media.gdcvault.com. The Vault pages list no slide links.
