# Overwatch Statescript: architecture, networking, prediction and runtime model (public sources)

Scope: public material only. The primary sources are Dan Reed's GDC 2017 slides (82 pages; the text was extracted from the public PDF), a full Chinese translation of Reed's talk *including speaker narration and Q&A* (lfzxb.top), Tim Ford's GDC 2017 netcode talk (Chinese translation plus an English secondary write-up), the Prometheus beta (0.8.0.24919) reverse-engineering repo and README, OWLib's generated STU type definitions (retail-hash names) plus its pre-hash-change known-name lists, and the 39C3 "Prometheus" talk subtitles. "Inference" lines are my hypotheses for the OW1 1.74 preservation problems. They are not sourced facts.

Primary URLs used throughout:
- Reed slides PDF: https://media.gdcvault.com/gdc2017/Presentations/Reed_Dan_NetworkingScriptedWeapons.pdf
- Reed talk abstract: https://gdcvault.com/play/1024041/Networking-Scripted-Weapons-and-Abilities
- Reed talk, Chinese transcript-style translation (烟雨迷离半世殇, 2021-02-25): https://www.lfzxb.top/ow-gdc-weapon-and-skillsystem/
- Tim Ford talk, Chinese translation: https://www.lfzxb.top/ow-gdc-gameplay-architecture-and-netcode/ ; GDC Vault: https://www.gdcvault.com/play/1024001/-Overwatch-Gameplay-Architecture-and ; English secondary summary: https://edgegap.com/blog/game-backend-deep-dive-overwatch-2016-netcode-architecture-rollback
- Prometheus (beta RE): https://github.com/saturn-xvi/prometheus (README, prometheus/Statescript.h, player_spawner.cpp, entity_admin.cpp, game.h, statescript_logger.h)
- OWLib generated STU types: https://github.com/overtools/OWLib/tree/develop/TankLib/STU/Types ; pre-hash names: https://github.com/overtools/OWLib/tree/develop/TankLibHelper/DataPreHashChange (KnownTypes.csv, KnownFields.csv)
- 39C3 talk "Prometheus: Reverse-Engineering Overwatch" (breakingbread): https://media.ccc.de/v/39c3-prometheus-reverse-engineering-overwatch ; subtitles: https://static.media.ccc.de/media/congress/2025/1266-d08f6f41-a731-57f7-ba40-8f38464f2dcd-eng.vtt

---

## Q1. How does Statescript replicate (instances, states, variables, remote sync, game messages, timers)? Server authority vs client-only nodes, what the client predicts, and how mispredictions are reconciled

### Takeaway
Statescript is server-authoritative and "eventually consistent". Each frame the server records per-entity StatescriptDeltas: instance create/destroy, changed instance vars, changed state indices, executed action indices and changed owner vars. Per client it then sends StatescriptPackets: the union of the deltas over a command-frame range [start,end], serialized as *current values*; a range starting at 0 means a full snapshot. Each packet carries a Local/Remote flag. Remote packets contain only SYNC_ALL ("remote-sync") nodes and the sync vars they reference, and the client merely copies them. Local packets contain everything (all states, instance vars, events), and the client handles them as rollback → replicate → re-simulate from buffered input. Client-only subgraphs always run fully on the client while their owning state is active.

### Cited Findings
**Object model**
- A played script creates a *Statescript Instance*. An instance is owned by an Entity; instances can be added and removed dynamically; multiple instances of the same script are allowed. — [Reed slides](https://media.gdcvault.com/gdc2017/Presentations/Reed_Dan_NetworkingScriptedWeapons.pdf)
- Node kinds are Entry, Condition, Action and State. — [Reed slides](https://media.gdcvault.com/gdc2017/Presentations/Reed_Dan_NetworkingScriptedWeapons.pdf). The 39C3 talk adds: there are only two entry types, "Play script" (pulses immediately on script load) and "game message" (pulses when a game message arrives, which is "just a resource ID … with some optional STU data"). It counts about 113 actions, 157 states, 4 condition types and about 990 config-var types in the beta. — [39C3 subtitles](https://static.media.ccc.de/media/congress/2025/1266-d08f6f41-a731-57f7-ba40-8f38464f2dcd-eng.vtt)
- Runtime structures shown on Reed's slides:
  - `StatescriptComponent { int m_internalCommandFrame; Array<StatescriptInstance*> m_instances; StatescriptVarBag m_ownerVars; StatescriptSyncMgr m_syncMgr; }`
  - `StatescriptInstance { int m_instanceID; const STUStatescriptGraph* m_stuGraph; Array<StatescriptState*> m_states; List<StatescriptEvent*> m_futureEvents; StatescriptVarBag m_instanceVars; }`
  - Timing is based on Command Frames, and playing scripts requires a StatescriptComponent.
  — [Reed slides](https://media.gdcvault.com/gdc2017/Presentations/Reed_Dan_NetworkingScriptedWeapons.pdf)
- Variables:
  - Bags hold "Instance Variables" and "Owner Variables". The key is a **16-bit identifier**, and primitives are stored in a **128-bit union**.
  - A variable is a primitive or an array of primitives. Variables are dependency providers and "optionally reference a StatescriptState" ("state-defined" variables).
  — [Reed slides](https://media.gdcvault.com/gdc2017/Presentations/Reed_Dan_NetworkingScriptedWeapons.pdf). The narration says instance vars are private per instance (e.g. Ammo, Clip), while owner vars are shared by all instances on the entity (e.g. AbilityLock). — [lfzxb translation](https://www.lfzxb.top/ow-gdc-weapon-and-skillsystem/)
- State virtuals (slides):
  - `OnActivate`, `OnDeactivate`, `OnTimerEvent`, `OnFrameTick`, `OnInternalDependencyChanged`, `OnBecameActiveThisTick`, `OnBecameInactiveThisTick`, `OnActivationChangedThisTick`, `GetStateDefinedValue`
  - Helpers: `EnqueueTimerEvent`, `EnqueueAbortStateEvent`, `EnqueueFinishStateEvent`, `SetFrameTickingEnabled`
  - The Wait state calls `EnqueueFinishStateEvent(GetFloat(m_timeout))` in OnActivate.

  So timers are future events queued on the instance (`m_futureEvents`). — [Reed slides](https://media.gdcvault.com/gdc2017/Presentations/Reed_Dan_NetworkingScriptedWeapons.pdf)
- Beta notification (event) types: 0 Lifetime (begin/finish/abort state), 1 Timer, 2 EvaluateExits, 3 TraverseFrom, 4 SetVar, 5 SetVarArray, 6 StopInstance, 7 LogicalButton (button id + going-down flag), 8 OnAttributeDependencyChanged. Each has an `m_timestamp` and an `m_instanceId`. — [Prometheus Statescript.h](https://github.com/saturn-xvi/prometheus)

**Synchronized vs unsynchronized; local vs remote**
- "Synchronized Instances: Server and client describe the same Instance; Eventually consistent. Unsynchronized Instances: Receive messages from Synchronized Instances; Read variables off of Synchronized Instances; Independent." — [Reed slides](https://media.gdcvault.com/gdc2017/Presentations/Reed_Dan_NetworkingScriptedWeapons.pdf)
- Played synchronized: weapons, abilities, emotes, game modes, map entities. Played unsynchronized: menus, Hero Gallery, end-of-match flow, music. — [Reed slides](https://media.gdcvault.com/gdc2017/Presentations/Reed_Dan_NetworkingScriptedWeapons.pdf). Narration: a game-mode instance can control a music instance through messages. — [lfzxb](https://www.lfzxb.top/ow-gdc-weapon-and-skillsystem/)
- "A single networked Entity is allowed to be controlled by the player. This Entity is local. All other networked Entities are remote. The server keeps track of which Entities are local to which clients." — [Reed slides](https://media.gdcvault.com/gdc2017/Presentations/Reed_Dan_NetworkingScriptedWeapons.pdf). Narration: there may be *no* local entity, e.g. while watching a death replay. — [lfzxb](https://www.lfzxb.top/ow-gdc-weapon-and-skillsystem/)
- "Statescript is server-authoritative. Communication is mostly server-to-client. Button input and aim is client-to-server." The client sends input for CF = server CF + RTT, plus a little extra lead for jitter. — [Reed slides](https://media.gdcvault.com/gdc2017/Presentations/Reed_Dan_NetworkingScriptedWeapons.pdf); [lfzxb](https://www.lfzxb.top/ow-gdc-weapon-and-skillsystem/)
- Containers (visual): grey is a plain container; red marks which states belong to a subgraph; **blue is client-only**; **purple is server-only**. — [lfzxb](https://www.lfzxb.top/ow-gdc-weapon-and-skillsystem/). Per-node flags `m_clientOnly` (0xE1B0C07F) and `m_serverOnly` (0x9A861B79) exist on `STUStatescriptBase` in retail types. `STUStatescriptComponent` (0xFD024F42, derives `STUMirroredEntityComponent`) also has its own component-level `m_clientOnly` byte. — [OWLib STUStatescriptBase.cs / STUStatescriptComponent.cs](https://github.com/overtools/OWLib/tree/develop/TankLib/STU/Types)

**Server side: Deltas / Ghosts / Packets**
- StatescriptDeltas: Command Frame; array of changed synchronized instances (Instance ID; flags for creation/destruction; changed instance vars with identifier and, for arrays, the affected index range; indices of states that changed; indices of actions that executed); array of changed owner vars. A delta is stored until all clients have acked its CF. — [Reed slides](https://media.gdcvault.com/gdc2017/Presentations/Reed_Dan_NetworkingScriptedWeapons.pdf)
- StatescriptGhost (one per client): Client ID, last acknowledged CF, and outstanding packets. Ack/Nack come from the network layer. — [Reed slides](https://media.gdcvault.com/gdc2017/Presentations/Reed_Dan_NetworkingScriptedWeapons.pdf); [lfzxb](https://www.lfzxb.top/ow-gdc-weapon-and-skillsystem/)
- StatescriptPacket:
  - Header: **Local/Remote flag**; **Command Frame range (start and end)**.
  - Payload: "Create a union of all StatescriptDeltas in the CF range; serialize the *current values* of the objects referenced by this union. If the CF range starts at 0, just send the current values of all objects." Packets are stored and reused until all clients ack their end CF.
  — [Reed slides](https://media.gdcvault.com/gdc2017/Presentations/Reed_Dan_NetworkingScriptedWeapons.pdf)
- Packet-loss example (narration): packets for CF100 and CF103 are sent. At CF106 the server suspects 100 was lost and sends the *union* 100∪103. The client does **not** apply a lone 103 packet, because that would produce an illegal intermediate state; it waits for the union. — [lfzxb](https://www.lfzxb.top/ow-gdc-weapon-and-skillsystem/)

**Client side**
- "The local entity stores input and predictions. When receiving a StatescriptPacket: send acknowledgement; ignore packet if redundant or out-of-order; if remote: Replicate; if local: Rollback, Replicate, Simulate." — [Reed slides](https://media.gdcvault.com/gdc2017/Presentations/Reed_Dan_NetworkingScriptedWeapons.pdf)
- Remote entities are mostly "dumb". They usually don't follow links or process events; they only refresh states that need refreshing. **Exception: client-only subgraphs are fully simulated whenever their owning State is active.** — [lfzxb](https://www.lfzxb.top/ow-gdc-weapon-and-skillsystem/). "Remote Entities do not simulate Statescript Instances." — [Reed slides](https://media.gdcvault.com/gdc2017/Presentations/Reed_Dan_NetworkingScriptedWeapons.pdf)
- Predicted-packet timeline (slides): the client is at CF105 with internal CF (ICF) 103 when it receives the server's CF100 packet. It rolls back to ICF100, replicates, and re-simulates ICF101–105. Mispredicted case: the server's CF95 packet causes a rollback to ICF95 and re-simulation of 96–100. — [Reed slides](https://media.gdcvault.com/gdc2017/Presentations/Reed_Dan_NetworkingScriptedWeapons.pdf)
- Misprediction (narration): if a predicted action is never confirmed (e.g. the player was stunned or killed), the client rolls back that frame and re-simulates from the next frame. This all happens in one frame and is invisible to the player. — [lfzxb](https://www.lfzxb.top/ow-gdc-weapon-and-skillsystem/)
- Replication "does not follow links". It only sets variables and updates states. **SetVar and MovementMod actions are not replicated**: SetVar because the variable itself is replicated, MovementMod because it does its own replication. — [lfzxb](https://www.lfzxb.top/ow-gdc-weapon-and-skillsystem/)
- Sync utilities for states:
  - `OnActivate/OnDeactivate(reason)`, `IsRollingBack()`, `IsReplicating()`, `IsRollingForth()`, `GetActivationSummary()`, `OnBecameActiveThisTick/InactiveThisTick`, `PutUpdate(DataStore*)/GetUpdate(DataStore*)`
  - For actions: `DoRollback()`, `GetRollbackStorage()`
  - Mirrored data: `WriteMirroredData/ReadMirroredData`, generated from `mirror MStatescriptStateChaseVar { Vec3A m_curVal; s64 m_lastTickTime; s32 m_timeRemainingMS; bool m_isVec; bool m_hasDuration; bool m_hasReachedDestination; }`.

  — [Reed slides](https://media.gdcvault.com/gdc2017/Presentations/Reed_Dan_NetworkingScriptedWeapons.pdf). Narration: PutUpdate/GetUpdate were tedious and error-prone, so they moved to a structured *mirror* database that is replicated and rolled back automatically. OnBecameActive/InactiveThisTick run at end of tick and suit presentation-only states (effects, sound, UI), so these don't replay during rollback. — [lfzxb](https://www.lfzxb.top/ow-gdc-weapon-and-skillsystem/)
- Beta state vtable: Prometheus names slots `bsDataStore_WriteData` (+0x1F0) and `bsDataStore_readData` (+0x1F8), i.e. Put/GetUpdate. It also has `needs_clientonly_update`, an instance-level `IsGraphNodeClientOnly`, `GetClientOnlyStateByMStateIndex`, `E_IsReferencedStateClientOnly`, inc/dec client-only counters, `RedoCheckIsAimEnt`, and `SyncHistoryStuff`. — [Prometheus Statescript.h](https://github.com/saturn-xvi/prometheus)
- Named mirror types in the pre-hash list: `MStatescriptStateChaseVar`, `MStatescriptStateAbility`, `MStatescriptStateBooleanSwitch`, `MStatescriptStateGameMessageEntry`, `MStatescriptStateLogicalButton`, `MStatescriptStateTrackMovement`. — [OWLib KnownTypes.csv](https://github.com/overtools/OWLib/tree/develop/TankLibHelper/DataPreHashChange)
- History: *historical data is kept for* all variables and states on the local Entity, button input and aim, and positions/poses for all entities. There is *no historical data for* variables/states on remote entities or for data from other entity components (health, filtering). — [Reed slides](https://media.gdcvault.com/gdc2017/Presentations/Reed_Dan_NetworkingScriptedWeapons.pdf). Q&A: they store predictions (past values) and restore them, rather than saving server updates and re-deserializing. Rollback is about 2000 lines in one file. Remote processing is actually the more expensive path. — [lfzxb](https://www.lfzxb.top/ow-gdc-weapon-and-skillsystem/)

**Remote-sync compilation (efficiency)**
- "Statescript analyzes scripts to discover synchronization requirements. Local entities: packets must contain everything. Remote: only States and Actions that remote instances care about, and variables referenced by those." — [Reed slides](https://media.gdcvault.com/gdc2017/Presentations/Reed_Dan_NetworkingScriptedWeapons.pdf)
- The `[STUStatescriptNode::SYNC_ALL]` attribute: with it, states and actions transmit locally and remotely (runtime objects may opt out). Without it, "States only transmit locally; Actions do not transmit". The compiler emits `array<internal<STUStatescriptNode>> m_remoteSyncNodes; array<inline<STUStatescriptSyncVar>> m_syncVars; s32 m_nodesBitCount; m_statesBitCount; m_remoteSyncNodesBitCount; m_syncVarsBitCount;` (bit widths for indexing nodes and vars in packets). — [Reed slides](https://media.gdcvault.com/gdc2017/Presentations/Reed_Dan_NetworkingScriptedWeapons.pdf)
- Retail `STUStatescriptGraph` (0x7236F6E3) has exactly these fields: `m_remoteSyncNodes` (0x41A83970), `m_syncVars` (0x434A5521, `STUStatescriptSyncVar` = identifier + `Enum_143375DF` 2-valued + byte), `m_nodesBitCount`, `m_statesBitCount`, `m_remoteSyncNodesBitCount`, `m_syncVarsBitCount`. Also `m_publicSchema`, `m_map`, and a `uint m_BE8E52CD` just before the bit counts. Retail `STUStatescriptBase` carries two arrays of `STUStatescriptRemoteSyncVar` (0xBF5B22B7, 0x8BF03679) plus two unnamed enums (13-value `Enum_46B5ADCA`, 6-value `Enum_CEBBB217`). — [OWLib STUStatescriptGraph.cs / STUStatescriptBase.cs](https://github.com/overtools/OWLib/tree/develop/TankLib/STU/Types)
- The beta graph layout has `m_playScriptHotReloadBehavior, ?, ?, m_predictionBehavior, m_nodesBitCount, …` (`m_predictionBehavior` field hash 0E4C38E1 in the pre-hash list). — [Prometheus Statescript.h](https://github.com/saturn-xvi/prometheus); [OWLib KnownFields.csv](https://github.com/overtools/OWLib/tree/develop/TankLibHelper/DataPreHashChange)
- Bandwidth figures, from Tracer firing a full clip and reloading (2 s):

  | | Local | Remote |
  |---|---|---|
  | States | 463 b | 190 b |
  | Instance vars | 519 b | 246 b |
  | Owner vars | 54 b | 54 b |
  | Events | **431 b** | **0 b** |
  | Other | 561 b | 316 b |
  | Total | 2028 b (1.0 Kb/s) | 806 b (0.4 Kb/s) |

  — [Reed slides](https://media.gdcvault.com/gdc2017/Presentations/Reed_Dan_NetworkingScriptedWeapons.pdf)
- Eventual consistency caveat: intermediate states aren't all synced, and variables go out only at frame end. Example bug: Symmetra's projectile showed scale 0 on remotes because a scalar var replicated first; the fix was a separate client-visual scale var. — [Reed slides](https://media.gdcvault.com/gdc2017/Presentations/Reed_Dan_NetworkingScriptedWeapons.pdf); [lfzxb](https://www.lfzxb.top/ow-gdc-weapon-and-skillsystem/)
- Ford's talk: abilities use the same roll-back/roll-forth principle as movement. In his Reaper Wraith example the client predicts the state's activation, and the server later says "rewind, re-activate these states, re-simulate all input". "Only three systems are responsible for gameplay netcode: movement, weapon, and state script." Overwatch predicts by default and opts out where needed. — [lfzxb Ford translation](https://www.lfzxb.top/ow-gdc-gameplay-architecture-and-netcode/); [Edgegap summary](https://edgegap.com/blog/game-backend-deep-dive-overwatch-2016-netcode-architecture-rollback)
- Command frames are 16 ms. Prediction systems use `UpdateFixed`. The client runs ahead by about RTT/2 plus one buffered frame. Ford: damage via ModifyHealthQueue is *not* predicted. — [lfzxb Ford](https://www.lfzxb.top/ow-gdc-gameplay-architecture-and-netcode/). The beta has a fixed 62.5 Hz update. — [39C3 subtitles](https://static.media.ccc.de/media/congress/2025/1266-d08f6f41-a731-57f7-ba40-8f38464f2dcd-eng.vtt)

### Inferences
- **Mapping to the project's tags (hypothesis).**
  - `SFSF` base frame + `SFDt` delta most likely encode Reed's packet CF range [start, end].
  - `CmFD`/full snapshot is likely the "range starts at 0 → send current values of all objects" case.
  - `Part`/`Size` look like payload chunking.
  - The project's observed apply rule fits Reed's "ignore if redundant or out-of-order" plus "don't apply a lone later packet". The rule is: discard if base+delta ≤ current frame; wait if base > cf+1 or part ≥ 0.
  - `Inst` create/destroy matches "flags for creation/destruction". `IVDt`/`UVGu` match instance/owner var changes, and `StDt` matches "indices of States that changed". `TmrU` likely carries the instance's future (timer) events, which are local-only ("Events 0 bits remote").
- **Local vs Remote packet form.** Reed puts a Local/Remote flag on each packet, and local packets "must contain everything" (all states via `m_statesBitCount`, all instance vars, events, executed actions). The project's current "remote-sync states (index into m_remoteSyncNodes) + 32 sync-var slots" encoding is therefore probably the **remote** form. The client will not predict an entity it receives remote packets for; it only replicates. Check whether the decoder (0x996450/0xa0e3c0 family) branches on a local/remote bit or uses `m_nodesBitCount`/`m_statesBitCount` widths for the local entity. That would be the key to prediction (Q2).
- **Server-only nodes.** Server-only nodes and SetVar/MovementMod side effects never run on remote clients. Anything the client needs from them (e.g. hero-select results, teleports) must arrive as replicated variables, states or component data. This matches the project's experience.
- **No component rollback.** Health and filter components are not part of Statescript history, so health must come from its own component replication. The red vignette with no health is consistent with this.

### Gaps
- No public source gives the bit-level wire format of StatescriptPackets or the exact meaning of the retail Enum_46B5ADCA/Enum_CEBBB217/m_BE8E52CD fields. That mapping is inference.
- Reed's video narration in English was not accessible (GDC Vault is members-only). The narration details come from a Chinese translation and are second-hand.

---

## Q2. How are movement abilities (Blink, Recall, dashes) implemented and predicted with Statescript and the movement system?

### Takeaway
Movement abilities are Statescript graphs whose states invoke code-backed movement nodes: Blink Effect, Teleport, Teleport Over Duration, Movement Mod State/Action, History Builder/Rewinder, Suppress Movement Prediction, Find Ground and Track Validated Position. Prediction happens on the **local** entity by running the same graph on the client and rolling back/forward with buffered input. The movement result itself is replicated by the movement system (MovementState snapshots, deterministic replay), not by Statescript.

### Cited Findings
- Statescript example scripts include "Tracer's Recall ability". — [Reed slides](https://media.gdcvault.com/gdc2017/Presentations/Reed_Dan_NetworkingScriptedWeapons.pdf). The 39C3 talk: Statescript "controls some movement, such as Tracer's blink, animation, spawning of cosmetics, abilities, some user interface interactions". — [39C3 subtitles](https://static.media.ccc.de/media/congress/2025/1266-d08f6f41-a731-57f7-ba40-8f38464f2dcd-eng.vtt)
- Reed's node list (in order of creation across heroes) includes:
  - Movement and history: Movement Mod Action, **Blink Effect**, **History Builder**, **History Rewinder**, Movement Mod State, **Teleport**, Find Ground, Move To, Steer, Wall Move, Track Movement, Track Validated Position, **Teleport Over Duration**, **Suppress Movement Prediction**.
  - Also: Logical Button State, Weapon Volley, Cosmetic Entity, Phase Out, Possess Control/View, Limit Aim, Aim Speed, Camera 3P, Camera Transform, Animated Camera, Camera Look At.

  — [Reed slides](https://media.gdcvault.com/gdc2017/Presentations/Reed_Dan_NetworkingScriptedWeapons.pdf)
- Pre-hash type names confirm these as STU classes:
  - `STUStatescriptStateBlinkEffect`, `STUStatescriptStateHistoryBuilder`, `STUStatescriptStateHistoryRewinder`, `STUStatescriptStateTeleportOverDuration`, `STUStatescriptStateSuppressMovementPrediction`, `STUStatescriptStateMovementMod`, `STUStatescriptStateMovementModOp`, `STUStatescriptActionMovementModOp`, `STUStatescriptActionMovementMod`, `STUStatescriptActionBlockRewinding`, `STUStatescriptStateTrackMovement` (with mirror `MStatescriptStateTrackMovement`), `STUStatescriptStateLogicalButton` (mirror `MStatescriptStateLogicalButton`).

  — [OWLib KnownTypes.csv](https://github.com/overtools/OWLib/tree/develop/TankLibHelper/DataPreHashChange). Retail `STUStatescriptStateBlinkEffect` = 0x99B885B8 (size 232) with an embedded `STUStatescriptEffect`, two `STU_B8F4347B` and one config var. — [OWLib STUStatescriptStateBlinkEffect.cs](https://github.com/overtools/OWLib/tree/develop/TankLib/STU/Types)
- "MovementMod … does its own replication", so it is not replicated by Statescript. — [lfzxb](https://www.lfzxb.top/ow-gdc-weapon-and-skillsystem/)
- Reaper example: hold secondary fire for 1 s → third person, `ReadyToLaunch = true`; on release, if ReadyToLaunch, launch into the air (MovementMod). The debugger shows the server setting the var then running MovementMod. The client rolls back, replicates everything except SetVar/MovementMod, and re-simulates. — [lfzxb](https://www.lfzxb.top/ow-gdc-weapon-and-skillsystem/); [Reed slides](https://media.gdcvault.com/gdc2017/Presentations/Reed_Dan_NetworkingScriptedWeapons.pdf)
- Movement netcode (Ford):
  - The client keeps ring buffers of movement-state history and input. The server returns validated movement snapshots about one RTT old.
  - On mismatch, the client rolls back to the last validated state and replays all subsequent inputs; this is deterministic.
  - The client sends a sliding window of inputs since the last acked state. Time dilation (16 → 15.2 ms) handles input starvation.
  - Example misprediction: Tracer runs on the client but the server says she was stunned (McCree flashbang).

  — [lfzxb Ford](https://www.lfzxb.top/ow-gdc-gameplay-architecture-and-netcode/); [Edgegap](https://edgegap.com/blog/game-backend-deep-dive-overwatch-2016-netcode-architecture-rollback)
- Positions/poses of all entities are part of rollback history (slide "Historical Data"). — [Reed slides](https://media.gdcvault.com/gdc2017/Presentations/Reed_Dan_NetworkingScriptedWeapons.pdf)
- Beta: "If an object needs to dynamically move in the map, the MovementStateSystem updates the entity's position, you cannot force-set the position in Component 1." Component 12 (STUMovementState) "holds all the deltas sent down from the server and does interpolation". "For the local player, there are some flags which you NEED to set in order for you to be able to move around." — [Prometheus README](https://github.com/saturn-xvi/prometheus)
- Reed Q&A: Reaper's Wraith form blocks server rewind (hit rewind), and "Statescript has a dedicated node to block rewinding" (beta name `STUStatescriptActionBlockRewinding`). — [lfzxb](https://www.lfzxb.top/ow-gdc-weapon-and-skillsystem/); [OWLib KnownTypes.csv](https://github.com/overtools/OWLib/tree/develop/TankLibHelper/DataPreHashChange)

### Inferences
- **Native Blink/Recall need prediction on the local hero.** For Blink/Recall to work natively (client-predicted rather than server teleports), the hero must be treated as the client's **local** Statescript entity, receiving local-form packets. Its LogicalButton state should then react to the client's own button input during simulate/re-simulate, and BlinkEffect/Teleport would issue a movement-system op that the movement prediction replays.
- **The server must also simulate.** The server must eventually confirm with (a) a Statescript packet whose CF range covers the press frame, showing the same states, and (b) a movement snapshot reflecting the teleport. Otherwise the client rolls back to the server state at that CF. Once the input falls outside the re-simulation window, the prediction is lost (snap-back).
- **Without a server-side simulator, mirror the outcome.** A responder with no graph simulator would have to reproduce the outcome: state activation in the packet at the press CF, plus movement state.
- **History Builder/Rewinder is likely Recall.** It probably records the past positions that Recall rewinds to. `Suppress Movement Prediction` is an explicit opt-out; check whether any Tracer graph uses it, since that would mean server-driven movement for that ability.
- **The project's server-teleport approach is consistent.** Teleporting via movement snapshots matches how *results* arrive ("MovementMod does its own replication"). It lacks only the client-side prediction.

### Gaps
- No public description of Blink's or Recall's specific graphs, the movement-op wire format, or how BlinkEffect interacts with the MovementState system.

---

## Q3. How does Statescript drive UI/HUD (UX presenters, data binding, UX nodes), and which entity owns HUD graphs?

### Takeaway
UI is mostly *unsynchronized* Statescript: menus, Hero Gallery, end-of-match flow, client-local UI instances. Unsynchronized instances get their data by **receiving messages from** and **reading variables off** synchronized instances (game mode, hero, map entities). In-game UI elements tied to synchronized gameplay live in **client-only subgraphs** of synchronized graphs. These run fully on every client, but only while their owning (replicated) state is active. UX nodes include UX Screen, UX View Mode, UI In World, UXPresenter, UXHealth and UXReticleOverride.

### Cited Findings
- Example scripts include "Common UI elements". Unsynchronized scripts include "Menus, Hero Gallery, End-of-match flow, Music". — [Reed slides](https://media.gdcvault.com/gdc2017/Presentations/Reed_Dan_NetworkingScriptedWeapons.pdf)
- Unsynchronized instances "receive messages from synchronized instances; read variables off of synchronized instances; independent". — [Reed slides](https://media.gdcvault.com/gdc2017/Presentations/Reed_Dan_NetworkingScriptedWeapons.pdf)
- Client-only subgraphs on remote entities are fully simulated whenever their owning state is active. — [lfzxb](https://www.lfzxb.top/ow-gdc-weapon-and-skillsystem/)
- Presentation-only states (effects, sound, **UI**) should use OnBecameActiveThisTick/OnBecameInactiveThisTick, evaluated at end of tick, so they don't fire repeatedly during rollback/replicate. — [lfzxb](https://www.lfzxb.top/ow-gdc-weapon-and-skillsystem/); [Reed slides](https://media.gdcvault.com/gdc2017/Presentations/Reed_Dan_NetworkingScriptedWeapons.pdf)
- Config-var utilities include "Is Hero Select Active", "Get Entity Position" and expressions like `dist({0},{1}) > 3`. — [Reed slides](https://media.gdcvault.com/gdc2017/Presentations/Reed_Dan_NetworkingScriptedWeapons.pdf)
- UX node names:
  - Reed's slides: "UX - Screen", "UX - View Mode", "UX - UI In World".
  - Pre-hash STU names: `STUStatescriptStateUXBase`, `UXPresenter`, `UXScreen`, `UXHealth`, `UXReticleOverride`, `UXHeroHelp`, `UXLoading`, `UXMatchStatus`, `UXMatchRecap`, `UXMatchPlayer`, `UXToast`, `UXFade`, `UXSubtitles`, `UXSocialMenu`, `UXProgression`, `UXParty`, `UXMatchmaking`, `UXCustomGameBrowserFilter/Details`, `UIInWorld`; also `STUStatescriptScreenVM`, `STUStatescriptProgressionScreenVM`, `STUUXViewModel`, `STUUXViewModelSchema`, `STUUXViewSource`.

  — [Reed slides](https://media.gdcvault.com/gdc2017/Presentations/Reed_Dan_NetworkingScriptedWeapons.pdf); [OWLib KnownTypes.csv](https://github.com/overtools/OWLib/tree/develop/TankLibHelper/DataPreHashChange)
- Retail `STUStatescriptStateUXPresenter` (0x7A7F2732, size 296) has an inline `STU_5F31962C`, arrays `STU_398F9098[]`, `STU_EB19DAFA[]` (the UX-event entries the project already identified) and `STU_8D95EFA2[]`, two config vars and a `STU_076E0DBA` (dynamic-var/out reference). — [OWLib STUStatescriptStateUXPresenter.cs](https://github.com/overtools/OWLib/tree/develop/TankLib/STU/Types)
- Beta entity layout:
  - **Entity admins.** There is a single LobbyEntityAdmin entity holding Statescript for lobby/login UI, login flow and music. The beta SyncMgr has `entity_admin_scope` (0 owner ent, 1 game EA, 2 lobby EA, 3 embedAI, 4 lobby-map EA).
  - **Controller vs model in game.** In-game, the beta controller entity has **no** Statescript instance; "only the model has one which controls abilities". The Game EA holds a "local entity" uint that "must reference the controller entity", and "systems use Components 2F (local player) and 20 (model reference) out of that entity to display the local player on screen."

  — [Prometheus README](https://github.com/saturn-xvi/prometheus); [Prometheus Statescript.h](https://github.com/saturn-xvi/prometheus)
- Beta spawner, after spawning the controller and model:
  - It calls a native function at beta RVA 0xd07830 (named `tell_statescript_this_is_localent(model, &controller->entity_id)`) on the model.
  - It sets component 0x20 `aim_entid`/`cam_attach_entid`/`movement_attach_entid` to the model.
  - It sets PlayerInfo (0x3F) `hero_select_enabled`, `hero_was_selected`, `m_slot=3`, `selected_heroid`, `localplayer_heroselected`.
  - It sets FilterBits team/0x800000.
  - It sets the model's entity var 0x0D800000000000FD = 1 and the weapon array 0x0D8000000000001D = [1].

  — [Prometheus entity_admin.cpp / player_spawner.cpp](https://github.com/saturn-xvi/prometheus)
- Beta known issues: "Press H to select Hero" is always shown because "this is controlled by the server by setting a boolean flag in component". "Player tablist … can be force-enabled in a Statescript script." — [Prometheus README](https://github.com/saturn-xvi/prometheus)
- 39C3: ViewModels ("VM") are the bridge between UI code and components (play button, keybinds, hero select screen). — [39C3 subtitles](https://static.media.ccc.de/media/congress/2025/1266-d08f6f41-a731-57f7-ba40-8f38464f2dcd-eng.vtt)

### Inferences
- **For the 0x1291 HUD problem.** By Reed's model, the client-only sender spawned from game-mode graph 0x0c90 runs only while its owning state in the *synchronized* game-mode instance is active on the client. The server must therefore replicate that owning state (probably a SYNC_ALL / remote-sync node, or a state under a local packet) as active.
  - If the sender sits under a state that is *not* SYNC_ALL, a remote packet can never activate it.
  - If the game-mode instance is attached to the controller (the project's current setup), the client may treat it as the **local** entity. It then expects local-form packets and would roll back client-side activations that the server's next packet does not contain.
  - Activating a client-only container's parent via a *full* snapshot may be needed, so the client re-evaluates the subgraph.
- **HUD presenters may bind to the local/aim entity via native context.** In the beta, the hero model's Statescript component was explicitly told who the local controller is (0xd07830 → `is_aim_ent`/`is_aim_ent_assigned` in the SyncMgr). Finding the retail equivalent of this "set local entity on Statescript component" call, and the server message that triggers it, is a strong lead. It may explain both "presenters run but nothing draws" and the prediction gate.
- **"Is Hero Select Active"-style predicates read native state, not graph vars.** Utility config vars read native game state (PlayerInfo, ViewModels). HUD visibility gates may depend on PlayerInfo/ViewModel data (e.g. hero selected flag, slot, team) set by server component replication, not on Statescript variables.

### Gaps
- No public documentation of HUD_Root creation, UXPresenter data-binding semantics or STU_5F31962C/STU_8D95EFA2 field meanings.
- Which entity owns the HUD graphs in retail 1.74 is not stated publicly. The beta README says the controller had no Statescript, which contradicts the project's retail observation of Statescript on the controller; the beta and retail may differ.

---

## Q4. Game messages: semantics, scoping and server→client delivery

### Takeaway
Game messages are 8-byte GUIDs (type 0x024) with optional STU parameter data, observable by Statescript entry nodes and by GameMessageEntry states. Both client and server can publish them, and non-Statescript systems can too. Entries filter recipients with an `m_filter` (ConfigVarFilter); senders choose `m_targets`. Messages also link unsynchronized and synchronized instances.

### Cited Findings
- "[Game Messages] are 8 byte GUIDs able to be sent from the client and server and able to be observed by Statescript. Can have optional, additional data. As far as I can see other systems than Statescript can also send GameMessages." — [Prometheus README](https://github.com/saturn-xvi/prometheus)
- The beta debug UI publishes a message locally with `publish(0, msgid | 0x0240000000000000)` (beta RVA 0xc44dd0; first argument 0). The Insert key publishes 0x0240000000000164. — [Prometheus game.h / windows/game_msg_window.h / dllmain.cpp](https://github.com/saturn-xvi/prometheus)
- 39C3: the game-message entry "sends a pulse if a 'game message' arrives, which is just a resource ID … with some optional STU data that Statescript can process". — [39C3 subtitles](https://static.media.ccc.de/media/congress/2025/1266-d08f6f41-a731-57f7-ba40-8f38464f2dcd-eng.vtt)
- Retail types:
  - `STUStatescriptEntryGameMessage` (0x8A7E9DA8): `m_params` (STU_EF930FD7[]), `m_gameMessage` (config var), three `STU_076E0DBA` outputs, **`m_filter` (STUConfigVarFilter)**, and a byte.
  - `STUStatescriptStateGameMessageEntry` (0x9D6CF8AC): `m_params`, `m_filter`, `m_gameMessage`, four `STU_076E0DBA`, two subgraph plugs, an output plug, a 3-valued `Enum_0B105E0B` and two bytes.
  - `STUStatescriptActionSendGameMessage` (0xBD6F5F83): base `STU_473D3BBD` plus **`m_targets`** (config var).
  - `STUConfigVarGameMessage` and `STUGameMessage` exist.

  — [OWLib types](https://github.com/overtools/OWLib/tree/develop/TankLib/STU/Types); [OWLib KnownTypes.csv](https://github.com/overtools/OWLib/tree/develop/TankLibHelper/DataPreHashChange)
- The beta instance vtable has `PrepareGameMessageEntry` and `PreparePlayScriptEntryProbably`, so game-message and play-script entries are the two entry kinds. — [Prometheus Statescript.h](https://github.com/saturn-xvi/prometheus)
- Synchronized → unsynchronized communication is via messages (e.g. game mode → music). — [lfzxb](https://www.lfzxb.top/ow-gdc-weapon-and-skillsystem/); [Reed slides](https://media.gdcvault.com/gdc2017/Presentations/Reed_Dan_NetworkingScriptedWeapons.pdf)
- Synced deltas carry "indices of Actions that executed" (actions transmit only with SYNC_ALL, and only locally otherwise). — [Reed slides](https://media.gdcvault.com/gdc2017/Presentations/Reed_Dan_NetworkingScriptedWeapons.pdf)

### Inferences
- **Delivering a message from the server to a client-only GameMessageEntry.**
  - Option (a): a replicated SendGameMessage action. Replicated actions are executed-action indices in the packet; with SYNC_ALL they reach remote clients, otherwise only the local client.
  - Option (b): the project's remote-message records (RMFr/RMSz/TrID ≈ "remote message" frame/size/trigger id).
  - Option (c): native code (non-Statescript systems).
  - A client-only *sender* (like the one in 0x0c90) publishes locally, so the recipient must exist and match `m_filter` on the client.
- **`m_filter`/`m_targets` explain scoping.** Entity-local versus broadcast delivery is probably decided by the receiving entry's `m_filter` and the sender's `m_targets`, not by a separate channel. The 3-valued enum on GameMessageEntry is a candidate scope/mode selector (unverified).

### Gaps
- No public description of the game-message wire record, scope enum semantics or parameter encoding.

---

## Q5. Public documentation of node types and Blizzard statements about the Statescript editor/tools

### Takeaway
There is no official public node reference. The best public node catalogues are:
- Reed's slide list of node names (about 90, grouped by when they were added).
- OWLib's retail STU classes (72 named `STUStatescript*` files, most fields hashed).
- OWLib's pre-hash KnownTypes/KnownFields lists (about 130 Statescript class names).
- Prometheus' beta runtime structs: vtables, notification types, the expression opcode VM and primitive types.

Blizzard has said Statescript began in 2011 (Titan) and is a C++-coupled in-house tool with an editor and debugger. Players' Workshop is described only as "based on the tools the development team uses"; I found no explicit public statement that it is Statescript.

### Cited Findings
- Why Statescript: non-programmers create high-level logic; it defines game state rather than just reacting to it; it encourages modular code; it gives "painless synchronized state machines" and works with the rest of the engine. Features:
  - Subgraphs, Containers and Config Vars (literals, variables, utilities, expressions), each type implemented by a C++ function.
  - Lifetime guarantees (OnDeactivate cleanup).
  - Imperative vs declarative styles.

  — [Reed slides](https://media.gdcvault.com/gdc2017/Presentations/Reed_Dan_NetworkingScriptedWeapons.pdf)
- Structured Data (.stu) compiles to code with attributes and runtime reflection. Example schema: `class STUStatescriptStateWait : STUStatescriptState { [Constraint(typeof(STUConfigVarNumeric))] embed<STUConfigVar> m_timeout; embed<STUStatescriptOutputPlug> m_onAbortPlug; embed<STUStatescriptOutputPlug> m_onFinishedPlug; }`, with C++ `IMPLEMENT_STATESCRIPT_FACTORY_AND_RTTI`. — [Reed slides](https://media.gdcvault.com/gdc2017/Presentations/Reed_Dan_NetworkingScriptedWeapons.pdf)
- History and tools (Q&A narration):
  - Statescript development began in 2011 and was used on Titan. Reed spent about half his time from late 2013 on the runtime, SyncMgr, compiler and debugger. A tools engineer spent several person-months on the editor.
  - Assets require exclusive checkout.
  - The C++ debugger records every entity's history and can switch between server and client views.
  - Raycasts stay in C++.
  - Portability is low because it is tightly coupled to Blizzard's asset system, networking layer and STU.

  — [lfzxb](https://www.lfzxb.top/ow-gdc-weapon-and-skillsystem/); [Reed slides](https://media.gdcvault.com/gdc2017/Presentations/Reed_Dan_NetworkingScriptedWeapons.pdf)
- Benefits and challenges: "New gameplay features can be added without writing synchronization or state machine logic in code." There is a "hefty up-front implementation cost for the runtime, an editor, and a debugger". "The eventual-consistency networking model does not provide a perfect blow-by-blow replication." — [Reed slides](https://media.gdcvault.com/gdc2017/Presentations/Reed_Dan_NetworkingScriptedWeapons.pdf)
- Bill Warnecke: "It's written in C++, we have an internal scripting language called statescript". — [BlizzardWatch 2017 interview](https://blizzardwatch.com/2017/11/14/overwatch-interview-jeff-kaplan-bill-warnecke-talks-mercy-moira)
- Workshop: Reed was one of the first engineers supporting Workshop development in 2017. The Blizzard article does not mention Statescript. — [Blizzard news](https://overwatch.blizzard.com/en-us/news/23303016). A PushSquare article's *author* says the Workshop is "based on the tools the development team uses to create official modes" (not a Reed quote). — [PushSquare](https://www.pushsquare.com/news/2019/05/overwatch_workshop_allows_players_to_create_custom_game_modes_on_ps4)
- Beta runtime details:
  - **Primitive types:** BYTE 1, INT 2, FLT 3, INT64 4, STRING 5, VEC3 6, INTVEC4 7, SS_INSTANCEID 8, FLT16VEC4 9, ENTITY 0xB.
  - **Expression VM opcodes:**
    - 0: exit
    - 2–5: conditional jumps
    - 30: config var
    - 31: dynamic var
    - 32–40: array search and count
    - 70: float constant
    - 100–106: arithmetic
    - 120: NOT
    - 140–145: comparisons
    - 160–175: math and vector operations
    - 200–207: min/max/clamp/round/random
  - **Node classification:** via RTTI into Entry/Action/State/Condition.
  - **`STUStatescriptBase` fields:** `m_isState`, `m_clientOnly`, `m_serverOnly`.
  - **StateStack:** priority, top/under subgraph plugs, and a SyncMgr stack-state table.

  — [Prometheus Statescript.h](https://github.com/saturn-xvi/prometheus)
- `STUStatescriptComponentInstanceData` (0x75526BC2) holds two separate `STUStatescriptGraphWithOverrides[]` arrays plus a schema. `STUStatescriptGraphWithOverrides` = graph ref + `STUStatescriptSchemaEntry[]` (identifier → config-var value) + a byte. — [OWLib types](https://github.com/overtools/OWLib/tree/develop/TankLib/STU/Types)
- The CCC 39C3 talk (Dec 2025) covers Statescript, STU, ViewModels, JAM and DataFlow on the 0.8 beta. Its demo synchronized only movement state ("No state script, animations … synchronized"). — [39C3 page/subtitles](https://media.ccc.de/v/39c3-prometheus-reverse-engineering-overwatch)
- I found no job postings that mention Statescript. Current Overwatch hero-designer postings ask only for "good knowledge of scripting languages". — [gamejobs.co listing](https://gamejobs.co/Hero-Designer-Overwatch-at-Blizzard-Entertainment)

### Inferences
- **`StDt` per-state data is the mirror data.** The project's "StDt has-data + state data" for some state types (WeaponVolley, Anim, Stack) is very likely Reed's per-state `PutUpdate/GetUpdate` / mirror data (`M*` structs). The set of state types that carry it corresponds to states that implement mirroring. The beta `bsDataStore_WriteData/readData` vtable slots are the natural place to enumerate them in retail.
- **The two instance-data arrays may split by sync class.** The two `GraphWithOverrides` arrays may separate synchronized from unsynchronized/client-only graphs (component-level `m_clientOnly`). This is unverified.

### Gaps
- No official node reference, editor screenshots beyond the GDC slides, or Overwatch 2 developer material on Statescript was found.
- The English audio of Reed's talk is on GDC Vault (members) and possibly YouTube/Bilibili (https://www.bilibili.com/video/BV1VE411b7tV/). It was not transcribed here.
- Reddit/Discord datamining write-ups on Statescript were not found by search.
