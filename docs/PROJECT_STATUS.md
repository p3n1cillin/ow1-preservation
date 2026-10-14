# Verified project status — 2026-10-14

Active target: final OW1 **1.74.0.0.104319**. Public source:
[ow1-preservation](https://github.com/p3n1cillin/ow1-preservation).
The old 1.0 ISO is not a dependency. Work is consolidated onto `main`.

| Milestone | Evidence/status |
|---|---|
| M1: existing project/build understood | Source, continuation and native captures inspected; build/test evidence in TESTING.md. |
| M2: original client communicates with private backend | Real TLS 1.2, WebSocket, Connect, Logon, GameUtilities referral, lobby proofs and own-key credential handshake exercised. |
| M3: independent authentication/menu | Local 'Pro' account grant and own-key credential accepted. Group-13 gateway negotiates and heartbeats. Our initial identity reply advances the original UI to **ENTERING GAME…**. **Main menu reached (2026-10-13, run screen8):** with the full initial-data sequence the original client shows PLAY/TRAINING/HERO GALLERY/LOOT BOX/…/EXIT GAME, then the new-player TUTORIAL prompt (direct window capture). The 3D menu backdrop is absent (no world requested). Reproduced as Mercy#1002 through the local-account launcher (`tools/ow1_launcher.py`). |
| M4: original map | Canonical Practice assignment, opt-in header preload and map-placeable creates reach WORLD_RUNNING. Practice geometry and the in-game menu visibly render in livecodec59/livecamera60. Player/hero control and normal header initiation remain unresolved. |
| M5–M6: playable hero/roster | No controllable final-retail hero or verified combat/abilities. |
| M7–M9: authoritative multiplayer/6v6 | Not implemented or verified against real final clients. |
| M10: automatic 6v6 matchmaking | Not implemented or verified. |
| M11–M12: complete content/stable hosting | Pending preceding original-client milestones. |

Latest (2026-10-14, liveowned93): hero preload, controller actor link, statescript
game-mode/hero graphs and the ownership create flag give an original-client
first-person view. Movement authority, health and combat remain open.

Earlier control: livetime62 reproduces visible Practice geometry with the optional
timing field enabled. The client receives that field, but its controlled-actor
marker remains invalid. The diagnostic selected entity lacks component 44,
required by the traced first-person owner lookup. Guarded read-only reports and
six synthetic fixtures now distinguish this prerequisite from entity resolution.
All 25 CTest targets pass; playable hero initialization remains the next milestone.

The next continuation creates a verified definition entity through the native
server-create path and selects it through 20302. The engine constructs component
44 and the components required by the post-create callbacks. The selected entity
now passes that prerequisite, but its actor link remains unset. See the latest
definition-create evidence in TESTING.md and DEVLOG.md.

Hero creation now works when the hero is preloaded through the original 20505
list 0 (opt-in `--lobby-hero-list`): Soldier: 76's gameplay entity is created
and selected, the world stays running and a hero model visibly renders. Without the
preload, the client aborts with a missing entity definition. The controller's
component-44 actor link now works: its create can include the reflected component
state (public `controlled_actor`). The selected controller resolves to the hero,
and with the module-3 time field the client records a valid controlled-actor marker.
The default fixed view remains, so first-person camera and controls are unresolved.

Current frontier: the `full` initial-data sequence reaches the original main
menu, and the party of one enables Training. Direct Computer Use screenshots
and input reproduced Training -> Practice Range on 2026-10-13. The client
sends 24000 and shows **ENTERING PRACTICE RANGE**. An opt-in plain 20600
loopback referral creates a native slot-120 instance-referral job, observed
immediately in both the private prototype and reproducible public probe.
This job is transient: later snapshots report it absent. A corrected second
endpoint string and opt-in UDP loopback bridge deliver native datagrams.
Read-only disassembly recovers the scrambled nonce/key blocks and correct
send/receive roles, matching our generated referral inputs. In `udpflags7`,
authenticated flags-3 replies advance the original UI to **ENTERING GAME**,
with advancing acknowledgements and nonempty type-1 packets. All **161 client
packets / 100 replies** authenticate and regenerate with our independent codec.
That bounded dump remains world WAITING/no pending request. Complete game
assignment, application negotiation and map load remain unresolved;
the 24000/20600 pairing is an experiment, not a demonstrated complete protocol.
The default launcher continues to use the verified menu path.

Latest source checkpoint: **25/25 CTest targets pass**. Primary common-channel
reliable records 21600/21610/21627 are decoded; 1003 complete saved client
bodies across three welcome runs authenticate and re-encode exactly. A 20300
server welcome is accepted and answered by the original client with 21600.
Supplying the Practice map creates pending world requests, but no rendered map.

The current blocker is more specific: the original WAITING handler polls the
map-header load state and advances only at status 3. Saved udpapp11/21 requests
have catalogue entries but no header load-cache object (status 0), despite 28
other cache entries. A read-only diagnostic reproduces this distinction.
The normal application path that initiates and retains that load remains
unresolved. Two new bounded private-session controls explicitly request the
header once through the original loader. Header/mode reach raw state 3 and
both world managers reach WORLD LOADING. The repeat visibly shows the original
Practice Range loading screen, where it remains; hero selection and playable
gameplay remain unverified. This opt-in diagnostic is not a solved protocol
load trigger. The corrected WORLD LOADING diagnostic finds all three native
resource groups complete in the header-assignment controls, but scene readiness
false and no active/pending scene handles. Working UI now reproduced two more
Practice selections. Assigning the exact typed map reference from the loaded
header creates pending scene objects; both end at raw state 1. A further run with
the canonical map identifier completes the typed asset and advances scene
controllers to state 5, with active scenes and readiness true. Its final dump
contains WORLD LOADED and WORLD REPLICATING managers. The next frontier is
replication initialization. A normal 20302 notification now assigns a valid
selected entity; using the full packed ID also resolves its native object.
The submitted world still remains WORLD REPLICATING. The new read-only
`--replication-state` diagnostic separates unset IDs, generation mismatches and
successful entity resolution. None of these checks establishes playable
replication or a controllable hero. Claude subsequently identified the four
pending entries as server-replicated map placeables. Minimal creates for those
placeables clear the queue and reach WORLD_RUNNING, independently reproduced
in liveverify58 and with the reusable codec in livecodec59/livecamera60.
The latter runs visibly render Practice geometry; Escape opens the in-game
menu. There is no hero HUD, weapon or hero selection, and short input checks
do not establish movement or camera control. Local-player replication is the
next frontier. The later
WORLD LOADED handler was previously mislabeled as the current gate. No gameplay
scene or hero control is verified.
Later bounded native runs udpmeta22/24/25/26 accept a 20318
metadata record into the original cache, but its empty diagnostic descriptor
exhausts ten acquisition attempts without content. The header remains
unrequested, and the world remains WAITING. The older report field
`current_context_present` describes the staged slot, not the active slot;
the corrected reader finds an active default context in udpmeta26/28/29.
Creating the owned Hotfix directory and granting only its own package SID
modify access did not resolve this. A read-only observer in udpmeta26 catches
six completed, live-referenced kind-14 requests with error 3/2/-3: the native
filesystem label is "failed to open". Later udpmeta27 storage probes can write
directly to the owned Hotfix folder while ancestor attribute checks return
access denied. A temporary DOS path alias in udpmeta28 passes the access probes
and changes four observed kind-14 errors to 9/2/6, but does not load the map.
This narrows the file-provider failure without establishing valid content.
The earlier private names "action pointer/marker" were incorrect: the metadata
entry's +0x80 is a retry deadline and +0x88 counts completed attempts.

`retail_login_state.py --metadata-state` separates registration, native content
presence, acquisition failure/retries, active/staged contexts and initialization
completion. The original updater promotes a default context from staged to
active without setting its content-ready flag. An empty staged slot or an
unset default-context ready flag therefore does not establish failed context
processing. In udpmeta29 the active default context has zero records; the
Practice header remains absent from the load cache. The numeric
20318 profile contains no payloads; accepted registration does not establish
a valid Hotfix descriptor or playable map. Native verifiers remain enabled;
the original EXE hash/signature match. All owned runs have ended and scoped
ACLs were restored.

The structured resource API also has a native engine preloader path.
`retail_login_state.py --preload-state` validates its engine-owned context and
reports configured/retained queue counts, map-header counts and submission
counts. All four saved udpapp11/21/udpmeta26/29 snapshots have empty queues.
This does not establish their earlier activity or prove that this queue is the
only header-loading path. The descriptor producer and its conditional inputs
remain a tracing target. New bounded live tests on 2026-10-14 reproduce
Practice Range -> ENTERING GAME with a header assignment, an additional
header/mode resource list, and a map-root assignment. The list is verified
inside both native pending requests (count 2), but the header remains unloaded.
The map-root comparison has only about 20 seconds after selection. Live
read-only samples show empty engine queues throughout the observed intervals;
sampling cannot exclude shorter transitions or a different world queue.
Hero Gallery also remains empty after all visible filters are enabled. These
tests establish neither rendered heroes nor gameplay. The normal header-load
trigger and the gallery's roster/initialization path remain unresolved.

Numeric schemas cover all 34 queue-family messages and the 20600 referral.
`retail_login_state.py --queue-state` reports bounded queue-record counts and
native job/marker booleans without exporting session inputs. Peer-identifier
bits, referral fields beyond the two traced endpoint forms and several identity fields
remain experimental.

Work continues in the project directory. New private analysis/run files use
ignored `.local/`; existing native build/client/key caches are reused as inputs.

The opt-in launcher installs our RSA-2048/e=65537 public modulus into a guarded
native heap key. Original RSA/address/HMAC verifiers remain enabled. A native
control with the original trusted modulus rejects the same own-key credential
and sends no post-handshake packet. Client files remain unchanged. These are
bounded loopback diagnostics, not a deployable multiplayer service.

Earlier independent-loading runs have an empty native metadata-entry cache;
later Practice runs activate a default context without sending 20318. SDK
kind 13 is local Hotfix enumeration, with structured error 3/2/-1. Earlier
handshake-only/error-1016 and empty-backend-reply descriptions are superseded
by the later evidence; historical DEVLOG entries remain for provenance.

See [FINAL_RETAIL](../FINAL_RETAIL.md), [BGS_PROTOCOL](BGS_PROTOCOL.md),
[TESTING](../TESTING.md), [DEVLOG](../DEVLOG.md), [CLAUDE](../CLAUDE.md),
[ROADMAP](../ROADMAP.md), [COMPATIBILITY](../COMPATIBILITY.md) and
[FEATURE_MATRIX](../FEATURE_MATRIX.md). The BSON relay and beta DLL are
separate historical/synthetic implementations, not final-retail gameplay.
