# Verified project status — 2026-10-13

Active target: final OW1 **1.74.0.0.104319**. Public source:
[ow1-preservation](https://github.com/p3n1cillin/ow1-preservation).
The old 1.0 ISO is not a dependency. Work is consolidated onto `main`.

| Milestone | Evidence/status |
|---|---|
| M1: existing project/build understood | Source, continuation and native captures inspected; build/test evidence in TESTING.md. |
| M2: original client communicates with private backend | Real TLS 1.2, WebSocket, Connect, Logon, GameUtilities referral, lobby proofs and own-key credential handshake exercised. |
| M3: independent authentication/menu | Local 'Pro' account grant and own-key credential accepted. Group-13 gateway negotiates and heartbeats. Our initial identity reply advances the original UI to **ENTERING GAME…**. **Main menu reached (2026-10-13, run screen8):** with the full initial-data sequence the original client shows PLAY/TRAINING/HERO GALLERY/LOOT BOX/…/EXIT GAME, then the new-player TUTORIAL prompt (direct window capture). The 3D menu backdrop is absent (no world requested). Reproduced as Mercy#1002 through the local-account launcher (`tools/ow1_launcher.py`). |
| M4: original map | Practice header loads and default context activates; context unready. No rendered final map. |
| M5–M6: playable hero/roster | No controllable final-retail hero or verified combat/abilities. |
| M7–M9: authoritative multiplayer/6v6 | Not implemented or verified against real final clients. |
| M10: automatic 6v6 matchmaking | Not implemented or verified. |
| M11–M12: complete content/stable hosting | Pending preceding original-client milestones. |

Current frontier: the `full` initial-data sequence reaches the original main
menu, and the party of one enables Training. Direct Computer Use screenshots
and input reproduced Training -> Practice Range on 2026-10-13. The client
sends 24000 and shows **ENTERING PRACTICE RANGE**. An opt-in plain 20600
loopback referral creates a native slot-120 instance-referral job, observed
immediately in both the private prototype and reproducible public probe.
This job is transient: later snapshots report it absent. No additional TCP
connection was observed, and the final world state is WAITING with no pending
request. Game assignment, instance transport and map load remain unresolved;
the 24000/20600 pairing is an experiment, not a demonstrated complete protocol.
The default launcher continues to use the verified menu path.

Numeric schemas cover all 34 queue-family messages and the 20600 referral.
`retail_login_state.py --queue-state` reports bounded queue-record counts and
native job/marker booleans without exporting session inputs. Peer-identifier
bits, referral fields beyond the traced endpoint and several identity fields
remain experimental.

Work continues in the project directory. New private analysis/run files use
ignored `.local/`; existing native build/client/key caches are reused as inputs.

The opt-in launcher installs our RSA-2048/e=65537 public modulus into a guarded
native heap key. Original RSA/address/HMAC verifiers remain enabled. A native
control with the original trusted modulus rejects the same own-key credential
and sends no post-handshake packet. Client files remain unchanged. These are
bounded loopback diagnostics, not a deployable multiplayer service.

The independent loading track still has an empty native context cache. SDK
kind 13 is local Hotfix enumeration, with structured error 3/2/-1. Earlier
handshake-only/error-1016 and empty-backend-reply descriptions are superseded
by the later evidence; historical DEVLOG entries remain for provenance.

See [FINAL_RETAIL](../FINAL_RETAIL.md), [BGS_PROTOCOL](BGS_PROTOCOL.md),
[TESTING](../TESTING.md), [DEVLOG](../DEVLOG.md), [CLAUDE](../CLAUDE.md),
[ROADMAP](../ROADMAP.md), [COMPATIBILITY](../COMPATIBILITY.md) and
[FEATURE_MATRIX](../FEATURE_MATRIX.md). The BSON relay and beta DLL are
separate historical/synthetic implementations, not final-retail gameplay.
