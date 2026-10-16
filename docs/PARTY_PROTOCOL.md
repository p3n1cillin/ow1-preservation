# Local party protocol, final client 104319

The public numeric layouts in `protocol/party-104319.json` describe five
messages used in bounded, two-original-client party experiments. They contain
field kinds, offsets, widths and counts only. Gateway entries still come from
the negotiated catalogue; never hardcode an entry number.

| Message | Direction | Observed behavior / fields |
| --- | --- | --- |
| 20700 | Server to client | Party snapshot at +0x78. Its +0x00 member list contains embedded player records, status +0xe0 and leader flag +0xe2. +0x60 identifies the party. |
| 20701 | Server to client | Group suggestion: +0x78 proposer player record, +0xe0 candidate player record. Opens Invite / Don't Invite. This is not the incoming merge request. |
| 22102 | Client to server | Clicking Invite sends the candidate game identity at +0x78 (two inline u64 words). |
| 20703 | Server to client | Group merge request: +0x78 proposer player record, +0xe0 proposed party snapshot. The client reports that the proposer requested to merge groups and presents No / Yes. |
| 22110 | Client to server | Clicking Yes sends an identity at +0x78 (two inline u64 words). In these fixtures it equals both the proposer and party identity; their distinct roles have not been tested. |

Server party messages use schema decimal 605150806; client requests use
3003079262. The 20700 layout also exists in the initial lobby descriptor bundle;
the regression check requires both copies to agree. Unknown fields remain zero.
The two clients keep their own game account identities throughout the merge.

`protocol/nearby-players-104319.json` adds the verified **20815** notification
(schema 446200228). Its +0x78 array contains player records: game identity at
+0x00, account identity at +0x10, and BattleTag at +0x40. Other fields stay zero.
In run 381 this created the native **Nearby Players** tab with one selectable
account. Right-clicking that account and choosing **Invite to Group** sent the
same 22102 target identity as the earlier suggestion experiment. This establishes
nearby-player discovery; it does not establish Friends or Recent Players support.

## Live evidence and scope

`pair-party-377` established the suggestion / Invite request distinction.
`pair-party-378` used a server-issued merge fixture, then the real client's Yes
action. Both clients displayed the resulting two-member party. Training was
disabled on the follower; the leader's Practice Range card remained enabled,
while Tutorial displayed its group restriction.

The leader alone selected Training / Practice Range. The diagnostic backend
forwarded that accepted queue request to the follower's lobby session, generating
a fresh referral for each client's own loopback endpoint (1119 and 1129). Both
clients entered hero select, picked Tracer, spawned with first-person weapons
and HUD, and the follower rendered the leader's proxy. Both remained alive to
the shared bound; all twelve cleanup/integrity audit fields passed. One leader
weapon volley and stop were recorded.

`pair-party-379` repeated the flow starting from the leader's actual Invite
click on the seeded suggestion. The backend generated the merge request only
after receiving 22102 for the configured other account, and sent the roster
only after that account's real 22110 acceptance. One leader launch again
brought both clients to hero select and first-person Tracer gameplay with HUD.
Follower Blink moved to the doorway and its HUD charge count fell from 3 to 2.

`pair-social-381` removed the seeded group suggestion: 20815 exposed Tracer in
Mercy's Nearby Players list, native Invite sent 22102, and Tracer's Yes sent
22110. Both received the two-member roster. Mercy alone started Practice; both
clients received one referral to their own endpoint and spawned as Tracer with
weapons and HUD. Follower Blink consumed one charge (3 to 2). Both remained
alive at the shared bound, with no bind refusals or stderr; all twelve cleanup
and integrity fields passed. The nearby list was supplied by the configured
two-account diagnostic backend; automatic presence tracking is not implemented.

`pair-social-382` repeated the complete route from fresh clients with 20815
sent at login. Both again spawned with HUD, follower Blink consumed a charge,
and leader fire/stop events were recorded. Both remained alive at the bound;
each received one referral to its own endpoint, with no bind refusals or stderr
and all twelve cleanup/integrity checks passing.

This is a bounded diagnostic implementation. Friends does not yet populate.
The backend's instance worlds retain separate bot state, and the visible peer proxy floats in a fixed
pose without weapon animation or PvP damage. This does not establish complete
parties, matchmaking, authoritative multiplayer, or a finished Practice Range.

## Reproduction in the shared research workspace

The ignored `.local/re/party_probe.py` adds the party experiment to the existing
probe wrapper only when `OW1_PARTY_EXPERIMENT` names a run manifest under
`.local/runs`. The manifest names the two local accounts and leader. Start the
existing `run-live-pair-game.ps1` with proxies enabled and no automated UI helper.
Clear both tutorial overlays before writing `{"suggest":1}` to the manifest's
`-control.json` companion. Click Invite on the leader and Yes on the follower,
then start Practice only from the leader. A changed suggestion number can
reissue an expired suggestion. Normal recipes leave the environment variable unset.

For Nearby Players, also set `OW1_SOCIAL_EXPERIMENT` to the same manifest and
write `{"mid":20815,"version":1}` to its `-social-control.json` companion.
The private `.local/re/social_probe.py` sends the other configured account to
each client once. Open Social / Nearby Players, right-click the other account,
and use Invite to Group. No `suggest` control is needed for this path.

Per-account `-events-<id>.jsonl` files record native Invite, native acceptance,
roster delivery, leader queue request and follower forwarding. Datagram logs,
screenshots, manifest/signalling files and all session inputs stay ignored.
Wait for the pair driver's cleanup audit before the next run, build or CTest.
`HANDOFF.md` records the latest complete run and remaining work.
