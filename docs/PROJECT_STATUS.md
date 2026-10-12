# Verified project status — 2026-10-13

Active target: final OW1 **1.74.0.0.104319**. Public source:
[ow1-preservation](https://github.com/p3n1cillin/ow1-preservation).
The old 1.0 ISO is not a dependency. Work is consolidated onto `main`.

| Milestone | Evidence/status |
|---|---|
| M1: existing project/build understood | Source, continuation and native captures inspected; build/test evidence in TESTING.md. |
| M2: original client communicates with private backend | Real TLS 1.2, WebSocket, Connect, Logon, GameUtilities referral, lobby proofs and own-key credential handshake exercised. |
| M3: independent authentication/menu | Local 'Pro' account grant accepted and enters logged-in referral flow. Native lobby reaches handshake state 6 with our key. Main menu and persistent application session unverified. |
| M4: original map | Practice header loads and default context activates; context unready. No rendered final map. |
| M5–M6: playable hero/roster | No controllable final-retail hero or verified combat/abilities. |
| M7–M9: authoritative multiplayer/6v6 | Not implemented or verified against real final clients. |
| M10: automatic 6v6 matchmaking | Not implemented or verified. |
| M11–M12: complete content/stable hosting | Pending preceding original-client milestones. |

Current frontier: after the encrypted lobby credential is accepted, the client
sends a three-byte big-endian packet length and a **10-byte body beginning with
1**. It closes about ten seconds later without a gateway application reply.
Decode this application exchange before inventing responses or claiming menu
access. The two 128-bit identifiers and trailing uint32 in the credential
envelope are server-assigned experiment values; downstream semantics remain
unverified.

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
