# Verified project status — 2026-10-12

Active target: final OW1 **1.74.0.0.104319**. Public source:
[ow1-preservation](https://github.com/p3n1cillin/ow1-preservation).
The old 1.0 ISO is not a dependency. Work is consolidated onto `main`.

| Milestone | Evidence/status |
|---|---|
| M1: existing project/build understood | Existing source and Claude's continuation inspected; native captures available; build/test evidence in TESTING.md. |
| M2: original client communicates with private backend | Real TLS 1.2 handshakes complete with our loopback observer, including a control without CA import. The client closes before an RPC header. Original RPC compatibility remains unverified. |
| M3: independent authentication/menu | Not implemented or verified. |
| M4: original map | Native Practice header loads and default context activates; state-4 updates observed. Context unready; no rendered final map. |
| M5–M6: playable hero/roster | No final-retail controllable hero or verified combat/abilities. |
| M7–M9: authoritative multiplayer/6v6 | Not implemented or verified against real final clients. |
| M10: automatic 6v6 matchmaking | Not implemented or verified. |
| M11–M12: complete content/stable hosting | Pending preceding original-client milestones. |

The immediate login frontier is the client's state after TLS 1.2 connects.
Default TLS negotiation still fails before completion; its cause is unverified.
The original certificate-store API accepts our public CA in a bounded probe,
but this does not make RPC/login work. Win32 87 on mapped-page writes persists;
queried dynamic-code policy flags are zero, so ACG is not a verified explanation.
The parallel loading track has an empty native context
cache. The retained SDK kind-13 operation is **local Hotfix enumeration**, with
structured error 3/2/-1, rather than an empty backend response.

Existing documents supply the handoff's roadmap, protocol research,
compatibility/hero/map/mode matrix, test results and development log:
[ROADMAP](../ROADMAP.md), [RESEARCH](../RESEARCH.md),
[COMPATIBILITY](../COMPATIBILITY.md), [FEATURE_MATRIX](../FEATURE_MATRIX.md),
[TESTING](../TESTING.md), [DEVLOG](../DEVLOG.md).
Native reproduction commands: [FINAL_RETAIL](../FINAL_RETAIL.md).
Persistent continuation instructions: [CLAUDE](../CLAUDE.md).
