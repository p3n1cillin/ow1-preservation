# Battle.net (BGS) online-service stack as used by Overwatch 1, and Overwatch matchmaking/server infrastructure

Scope note: public sources and open-source emulators only. No keys, certificates, credentials or
proprietary bytes are reproduced here. Several emulator repositories embed key material or
certificates (Plasmawatch ships hard-coded 64-byte k0..k3 hex strings and a .pfx with its
password in the README). Those values are deliberately NOT copied; only attribute names and
structure are described. Repositories were cloned read-only into the session scratchpad for grep
(TrinityCore sparse checkout of `src/server/proto/Client` + `src/server/bnetserver`, HearthSim
hs-proto, plasmawatch/login-server, Boi-027/Overwatch-1-v1.74-Lobby-Research, saturn-xvi/prometheus).
No third-party code was run.

## Q1. Public BGS protocol definitions: services, method ids, versions, authentication, Game Utilities

### Takeaway
TrinityCore's `bnetserver` is the most complete, current, maintained public BGS implementation:
it ships generated protobuf code for ~35 services/listeners across "legacy v1" (`bgs.protocol.*.v1`)
and the newer `api/client/v1|v2|v3` sets. Each one carries an `OriginalHash` (the FNV-1a hash of the
original fully-qualified descriptor name, sent on the wire as `Header.service_hash`) and per-method ids.
Authentication works like this: `Logon` returns an external challenge URL to a REST/HTML login page,
the page issues a `login_ticket`, and the client sends that ticket to `VerifyWebCredentials`. Games
then use `GameUtilities.ProcessClientRequest` (v1) or `ProcessTask` (v2) as a generic name/Variant
attribute RPC for game-specific requests.

### Cited Findings
**Proto sets / repositories**
- TrinityCore keeps generated BGS protobuf C++ (`*.pb.h/.pb.cc`) for: account, authentication, challenge, connection, friends, game_utilities, notification, presence (service + listener), report, resource; plus `api/client/v1` (block_list, club, club_membership), `api/client/v2` (account, authentication, friends, game_utilities, notification, presence, report, whisper) and `api/client/v3` (report). Each service class embeds `OriginalHash` and `NameHash` constants — [TrinityCore proto/Client](https://github.com/TrinityCore/TrinityCore/tree/master/src/server/proto/Client)
- TrinityCore's server-side handlers that are actually implemented are only Account, Authentication, Connection and GameUtilities (`src/server/bnetserver/Services/{Account,Authentication,Connection,GameUtilities}Service.cpp`). Friends/presence/club exist only as generated stubs — [TrinityCore bnetserver/Services](https://github.com/TrinityCore/TrinityCore/tree/master/src/server/bnetserver/Services)
- HearthSim `hs-proto` holds message-only protos decompiled from the Hearthstone client (version 13.0.9.28556) with the decompiler [HearthSim/proto-extractor](https://github.com/hearthsim/proto-extractor). It includes the older `bnet.protocol` packages that TrinityCore no longer has: `channel`, `channel_invitation`, `chat`, `game_master` (FindGame/GameFound/JoinGame/ConnectInfo/GameFactoryDescription), `server_pool`, `invitation`, `profanity`. These files contain message definitions but no `service`/rpc blocks — [HearthSim/hs-proto](https://github.com/HearthSim/hs-proto)
- Plasmawatch's OW1 login server (Go) has generated Go protos for connection, authentication, challenge, game_utilities, presence_types, channel_types, invitation_types, account_types, rpc_config, and a `rest/login` FormInputs/LoginForm proto. It implements Connection, Authentication and GameUtilities handlers — [plasmawatch/login-server](https://github.com/plasmawatch/login-server)
- A web search for public `club_service.proto`/`whisper_service.proto` repositories found nothing beyond TrinityCore. [BNETDocs](https://bnetdocs.org/document/10) documents the much older Battle.net 1.x chat (BNCS) protocol, which is unrelated to BGS — [BNETDocs web repo](https://github.com/BNETDocs/bnetdocs-web)

**Service hashes (OriginalHash = wire `service_hash`) and method ids, extracted from TrinityCore generated code** — [TrinityCore proto/Client](https://github.com/TrinityCore/TrinityCore/tree/master/src/server/proto/Client)

| Service (proto file) | OriginalHash | Methods (id name) |
|---|---|---|
| ConnectionService (v1) | 0x65446991 | 1 Connect, 2 Bind, 3 Echo, 4 ForceDisconnect, 5 KeepAlive, 6 Encrypt, 7 RequestDisconnect |
| AuthenticationService (v1) | 0x0DECFC01 | 1 Logon, 7 VerifyWebCredentials, 8 GenerateWebCredentials |
| AuthenticationListener (v1, server->client) | 0x71240E35 | 4 OnServerStateChange, 5 OnLogonComplete, 10 OnLogonUpdate, 11 OnVersionInfoUpdated, 12 OnLogonQueueUpdate, 13 OnLogonQueueEnd |
| ChallengeListener (v1) | 0xBBDA171F | 3 OnExternalChallenge, 4 OnExternalChallengeResult |
| AccountService (v1) | 0x62DA0891 | 13 ResolveAccount, 25 Subscribe, 26 Unsubscribe, 30 GetAccountState, 31 GetGameAccountState, 32 GetLicenses, 33 GetGameTimeRemainingInfo, 34 GetGameSessionInfo, 35 GetCAISInfo, 37 GetAuthorizedData, 44 GetSignedAccountState, 45 GetAccountInfo, 46 GetAccountPlatformRestrictions |
| AccountListener (v1) | 0x54DFDA17 | 1 OnAccountStateUpdated, 2 OnGameAccountStateUpdated, 3 OnGameAccountsUpdated, 4 OnGameSessionUpdated |
| GameUtilitiesService (v1) | 0x3FC1274D | 1 ProcessClientRequest, 2 PresenceChannelCreated, 6 ProcessServerRequest, 7 OnGameAccountOnline, 8 OnGameAccountOffline, 10 GetAllValuesForAttribute, 11 RegisterUtilities, 12 UnregisterUtilities |
| GameUtilitiesService (api v2) | 0x5DBB51C2 | 1 ProcessTask, 2 GetAllValuesForAttribute |
| FriendsService (v1) | 0xA3DDB1BD | 1 Subscribe, 2 SendInvitation, 3 AcceptInvitation, 4 RevokeInvitation, 5 DeclineInvitation, 6 IgnoreInvitation, 8 RemoveFriend, 9 ViewFriends, 10 UpdateFriendState, 11 Unsubscribe, 12 RevokeAllInvitations, 13 GetFriendList, 14 CreateFriendship |
| FriendsListener (v1) | 0x6F259A13 | 1 OnFriendAdded, 2 OnFriendRemoved, 3 OnReceivedInvitationAdded, 4 OnReceivedInvitationRemoved, 5 OnSentInvitationAdded, 6 OnSentInvitationRemoved, 7 OnUpdateFriendState |
| FriendsService (api v2) | 0x5869BE8C | 1 Subscribe, 2 Unsubscribe, 3 GetSentInvitations, 4 GetReceivedInvitations, 5 GetFriends, 6 IsFriend, 7 ViewFriends, 8 SendInvitation, 9 AcceptInvitation, 10 RevokeInvitation, 11 RevokeAllInvitations, 12 IgnoreInvitation, 13 RemoveFriend, 14 UpdateFriendState |
| FriendsListener (api v2) | 0xDBC01A89 | same 1..7 as v1 |
| PresenceService (v1) | 0xFA0796FF | 1 Subscribe, 2 Unsubscribe, 3 Update, 4 Query, 8 BatchSubscribe, 9 BatchUnsubscribe |
| PresenceListener (v1, presence_listener.proto) | 0x890AB85F | 1 OnSubscribe, 2 OnStateChanged |
| PresenceService (api v2) | 0x138D200C | 3 BatchSubscribe, 4 BatchUnsubscribe, 5 Query, 6 Update |
| PresenceListener (api v2) | 0xF4729709 | 1 OnPresenceStateUpdated, 2 OnSubscribeFailure |
| NotificationService (v1) | 0x0CBE3C43 | 1 SendNotification, 6 Subscribe, 7 Unsubscribe, 8 Publish |
| NotificationListener (v1) | 0xE1CB2EA8 | 1 OnNotificationReceived |
| NotificationService / Listener (api v2) | 0xF8E1EB98 / 0x2362BECD | 1 SendNotification / 1 OnNotificationReceived |
| WhisperService (api v2) | 0xFEE1AA14 | 1 Subscribe, 2 Unsubscribe, 3 GetWhisperHistory, 4 SendWhisper, 5 AdvanceViewTime, 6 AdvanceClearTime, 7 SetTypingIndicator |
| WhisperListener (api v2) | 0x62615E21 | 1 OnWhisper, 2 OnWhisperEcho, 3 OnWhisperUpdated, 4 OnAdvanceViewTime, 5 OnAdvanceClearTime, 6 OnTypingIndicator |
| ReportService (v1) | 0x7CAF61C9 | 1 SendReport, 2 SubmitReport |
| ReportService (api v2 / v3) | 0x3A4218FB / 0xC341E463 | 1 SubmitReport |
| ResourcesService (v1) | 0xECBE75BA | 1 GetContentHandle, 2 GetTitleIcons |
| BlockListService / Listener (api v1) | 0x8E8F5FB0 / 0xB5DD8A75 | 1 Subscribe, 2 Unsubscribe, 3 GetState, 4 BlockPlayer, 5 UnblockPlayer, 6 BlockPlayerForSession, 7 PassExternalBlockList / 1 OnBlockedPlayerAdded, 2 OnBlockedPlayerRemoved |
| ClubService (api v1) | 0xE273DE0E | 1 Subscribe, 2 Unsubscribe, 3 Create, 4 Destroy, 5 GetDescription, 6 GetClubType, 7 UpdateClubState, 8 UpdateClubSettings, 30 Join, 31 Leave, 32 Kick, 33 GetMember, 34 GetMembers, 35 UpdateMemberState, 36 UpdateSubscriberState, 37 AssignRole, 38 UnassignRole, 50-55 Send/Accept/Decline/Revoke/Get/GetInvitation(s), 60-64 Suggestions, 70-74 Tickets, 80-83 Bans, 100-109 Streams (incl. 108 GetStreamVoiceToken), 150-157 Messages (CreateMessage ... GetStreamMessage) |
| ClubListener (api v1) | 0x80909D73 | 1 OnSubscribe ... 30-34 member events, 50/51 invitations, 70/71 suggestions, 100-102 streams, 150-155 stream messages/typing/unread |
| ClubMembershipService / Listener (api v1) | 0x94B94786 / 0x2B34597B | 1 Subscribe, 2 Unsubscribe, 3 GetState, 4 UpdateClubSharedSettings, 5-7 stream mentions / 1 OnClubAdded, 2 OnClubRemoved, 3/4 received invitations, 5 OnSharedSettingsChanged, 6-8 mentions |
| AccountService (api v2) | 0x22DC2464 | 1 GetSignedAccountState, 101 GetAccountInfo, 103 GetOptIns, 104 GetRestriction, 105 GetSecurityStatus, 106 GetCAIS, 107 GetParentalControl, 108 GetGameAccountLinks, 201 GetGameAccountInfo, 203 GetGameAccountRestriction |
| AuthenticationService / Listener (api v2) | 0xC02F8216 / 0x9DA8116B | 1 Logon, 2 VerifyAuthToken, 3 GenerateAuthToken / 1 OnLogonComplete, 2 OnLogonQueueUpdate, 3 OnLogonQueueEnd, 4 OnExternalChallenge |

- TrinityCore's dispatcher masks the method id with `methodId & 0x3FFFFFFF` before switching (the upper bits are flags) — [TrinityCore game_utilities_service.pb.cc](https://github.com/TrinityCore/TrinityCore/blob/master/src/server/proto/Client/game_utilities_service.pb.cc)

**Authentication (web credentials / login ticket)**
- TrinityCore `HandleLogon` checks program/platform/locale. If `LogonRequest.cached_web_credentials` is present it goes straight to `VerifyWebCredentials`; otherwise the server sends `ChallengeListener.OnExternalChallenge` with a login URL — [TrinityCore AuthenticationService.cpp](https://github.com/TrinityCore/TrinityCore/blob/master/src/server/bnetserver/Services/AuthenticationService.cpp)
- TrinityCore's REST login service registers `GET /bnetserver/login/` (form description), `POST /bnetserver/login/` (credentials -> `login_ticket`), `POST /bnetserver/login/srp/`, `POST /bnetserver/refreshLoginTicket/` (ticket expiry refresh), `GET /bnetserver/gameAccounts/` and `GET /bnetserver/portal/`. Tickets are generated as `"TC-" + 20 random bytes hex` — [TrinityCore LoginRESTService.cpp](https://github.com/TrinityCore/TrinityCore/blob/master/src/server/bnetserver/REST/LoginRESTService.cpp)
- `VerifyWebCredentials` checks ticket expiry, IP/country lock and bans, then calls `sendLogonComplete` (AuthenticationListener.OnLogonComplete) — [TrinityCore AuthenticationService.cpp](https://github.com/TrinityCore/TrinityCore/blob/master/src/server/bnetserver/Services/AuthenticationService.cpp)
- For Overwatch, Plasmawatch's `Logon` and `GenerateWebCredentials` return the payload URL `http://<host>:6969/battlenet/login?externalChallenge=login&app=pro` (sent through ChallengeListener). Its web server serves a `LOGIN_FORM` with inputs `account_name` ("Email or Phone", max 320) and `password`, sets `web.id`/`JSESSIONID` cookies, and on POST returns JSON with a `login_ticket` of the form `US-<32 hex>-<number>`. The ports used are TLS RPC 1119 and auth webserver 6969 — [plasmawatch/login-server README](https://github.com/plasmawatch/login-server), [webserver.go](https://github.com/plasmawatch/login-server/blob/main/webserver/webserver.go), [authentication_service.go](https://github.com/plasmawatch/login-server/blob/main/services/authentication_service.go)

**Game Utilities usage pattern**
- In WoW, TrinityCore's `ProcessClientRequest` takes a list of `Attribute{name, Variant}`. The parameter whose name starts with `Command_` selects the request (`Command_RealmListTicketRequest_v1`, `Command_LastCharPlayedRequest_v1`, `Command_RealmListRequest_v1`, `Command_RealmJoinRequest_v1`, `Command_FetchBleepProxiesRequest_v1`; the dispatch hashes the name with FNV-1a). The server answers with `Param_*` attributes (e.g. `Param_RealmListTicket`, `Param_RealmList`, `Param_RealmJoinTicket`, `Param_ServerAddresses`, `Param_JoinSecret`). v2 `ProcessTask` uses the same handler with `v2.Attribute` — [TrinityCore GameUtilitiesService.cpp](https://github.com/TrinityCore/TrinityCore/blob/master/src/server/bnetserver/Services/GameUtilitiesService.cpp)

### Inferences
- The hashes for the services the project already speaks match TrinityCore exactly: Connection 0x65446991, Authentication 0x0DECFC01/Listener 0x71240E35, GameUtilities v2 0x5DBB51C2 ([project BGS_PROTOCOL.md](https://github.com/p3n1cillin/ow1-preservation/blob/main/docs/BGS_PROTOCOL.md)). TrinityCore's hash table can therefore seed hashes for the friends/presence/notification/whisper/club services. The project should still confirm against the 104319 client's embedded descriptors, the same way it did for the existing three.
- Discrepancy to check: the project's BGS_PROTOCOL.md lists `ConnectionService.Bind = 1` and `Encrypt = 1`, flagged as "approximate". TrinityCore has Bind = 2 and Encrypt = 6. The client uses bindless RPC, so Bind is never sent, but the table should be corrected or re-extracted.
- In Overwatch, the Balancer referral is the Game Utilities "Command"-style request. Instead of `Command_*_v1` names, OW uses `service_type`/`request_type` attributes (see Q2).

### Gaps
- No public `.proto` source text with full `service` blocks for the 2019-2022 api/client sets was found other than TrinityCore's generated code. Field-level message definitions for whisper/club/presence v2 must be read from TrinityCore `.pb.h` or extracted from the OW client.
- No public source documents a "UserManager" service (recent players/block list, as in the Diablo III era) for modern BGS. TrinityCore has BlockListService (api v1) instead. Whether OW 1.74 uses UserManager, BlockList or neither is unverified.
- Legacy `ChannelService`/`ChannelInvitationService` (party/chat channels) appear only as message definitions in Hearthstone 13.x protos. No current open-source server implements them.

## Q2. How Overwatch specifically uses BGS (Game Utilities attributes, Balancer referral, presence, party, chat)

### Takeaway
On the BGS side, Overwatch's essential path is Connection -> Authentication (external web challenge + login ticket) -> Game Utilities "Balancer"/"Referral". The referral returns `ReferralInfo` with `k0..k3` (64-byte HMAC key slots), `cid` and `hostv4`. Everything game-specific is then carried on the Overwatch lobby ("JAM") protocol, not on BGS: identity, player data, queues/matchmaking, loadouts and probably party/groups. No public source documents Overwatch rich-presence fields, BGS party use or chat use.

### Cited Findings
- Plasmawatch answers the OW client's `GameUtilities.ProcessClientRequest` (v1) with attributes `response_type="ReferralInfo"`, `k0`, `k1`, `k2`, `k3` (blob), `cid` (uint) and `hostv4` (string `host:port`), sent as a response with service id 254 — [plasmawatch game_utilities_service.go](https://github.com/plasmawatch/login-server/blob/main/services/game_utilities_service.go) (key values intentionally not reproduced)
- Boi-027's notes confirm that the lobby session keys are "DELIVERED by the bnet response GameUtilities.ProcessClientRequest, as attributes literally named k0/k1/k2/k3 plus cid and hostv4". The schedule is MAC1 = HMAC-SHA256(k0, cn‖sn), MAC2 = HMAC-SHA256(k1, sn‖cn), c2s key = HMAC-SHA256(k3, sn‖cn), s2c key = HMAC-SHA256(k2, cn‖sn). Tournament mode zeroes all four — [Boi-027 README](https://github.com/Boi-027/Overwatch-1-v1.74-Lobby-Research), [PROJECT_STATE.txt](https://github.com/Boi-027/Overwatch-1-v1.74-Lobby-Research/blob/main/docs/PROJECT_STATE.txt)
- The project's live-verified 104319 request uses GameUtilities **v2 ProcessTask** with attributes `service_type="Balancer"`, `request_type="Referral"`, `version=3`, `build=104319`, `cluster="Pro"`, `platform_available="pc_1"` and `payload` (empty blob). Other response types are `ReferralQueued` (callback_delay, approx_queue_position, payload) and `ReferralError` (error_code, psplus_product_code). The game-account EntityId high word is `(2<<56)|(region<<32)|0x0050726f` ("Pro") — [project docs/BGS_PROTOCOL.md](https://github.com/p3n1cillin/ow1-preservation/blob/main/docs/BGS_PROTOCOL.md)
- Plasmawatch uses `app=pro` in the external-challenge URL; "Pro" / "prometheus" is Overwatch's product code — [plasmawatch authentication_service.go](https://github.com/plasmawatch/login-server/blob/main/services/authentication_service.go); the `-game=prometheus` Battle.net shortcut flag is used to force an Overwatch beta install — [Neozone](https://www.neozone.org/jeux-video/overwatch-comment-forcer-linstallation-de-la-beta)
- The BGS transport for OW is TLS on 1119 and then WebSocket with `Sec-WebSocket-Protocol: v1.rpc.battle.net`. Each message is `[u16-BE header length][Header][body]` and uses bindless RPC (`use_bindless_rpc=true`) — [project docs/BGS_PROTOCOL.md](https://github.com/p3n1cillin/ow1-preservation/blob/main/docs/BGS_PROTOCOL.md)
- Boi-027 found that the 1.74 client's 1119 TLS goes through cURL/OpenSSL/BoringSSL. The earlier wall was certificate pinning, with an empty SNI because the client connected by IP — [Boi-027 PROJECT_STATE.txt §7D](https://github.com/Boi-027/Overwatch-1-v1.74-Lobby-Research/blob/main/docs/PROJECT_STATE.txt)
- Plasmawatch implements only Connection, Authentication, Challenge and GameUtilities. Its `PresenceChannelCreated` and `GetPlayerVariables` handlers are `panic("implement me")` stubs, so no public OW emulator implements presence/friends/chat — [plasmawatch game_utilities_service.go](https://github.com/plasmawatch/login-server/blob/main/services/game_utilities_service.go)

### Inferences
- Plasmawatch uses v1 `ProcessClientRequest` while the 104319 client uses v2 `ProcessTask`. Either Plasmawatch targeted an earlier client build, or the final client accepts both. The project's byte-verified v2 path is authoritative for 104319.
- BGS's own legacy matchmaking (`game_master`: FindGame/GameFoundNotification/ConnectInfo, in [hs-proto game_master.proto](https://github.com/HearthSim/hs-proto/blob/master/bnet/protocol/game_master/game_master.proto)) is not on Overwatch's path. OW replaces it with Balancer referral + its own lobby queue messages (23300 family / 24000 / 20600 in this project).
- Overwatch's in-game groups were probably lobby-side state (lobby message bands), with BGS used for friends/presence/invite plumbing. This is not confirmed by any source and must be verified from the client's registered BGS listeners and the lobby schema.

### Gaps
- Overwatch rich-presence field keys (program "Pro" presence fields: hero/map/mode/"in queue"/party size): no public source found.
- Whether OW 1.74 party invites use BGS (friends/notification/club/legacy channel_invitation) or lobby-native messages: no public source found.
- Whether OW 1.74 chat/whisper uses BGS WhisperService v2, legacy NotificationService "whisper" notifications, or an Overwatch voice/text channel service: no public source. Boi-027 notes a separate VoiceChat client subsystem in the binary that was mistaken for the lobby, which suggests chat/voice is its own subsystem ([PROJECT_STATE.txt §8 VOID](https://github.com/Boi-027/Overwatch-1-v1.74-Lobby-Research/blob/main/docs/PROJECT_STATE.txt)).
- A community rentry continuing Boi-027's notes ("Channel Setup, Login and Loot Boxes", https://rentry.co/3bswrgmw) exists, but its content could not be retrieved or summarized with the tools available. Read it manually if needed.

## Q3. Overwatch matchmaking architecture, server allocation, tick rate, regions

### Takeaway
Public developer posts describe an SR/MMR matchmaker that targets equal-sized groups and refuses matches below a 40% predicted win chance (2018). It enforced group SR spread limits per tier (Season 8, 2017) and moved to per-role queues/SR with 2-2-2 Role Queue in 2019, plus Open Queue in 2020. Game servers ran on Blizzard's OpenStack private cloud with autoscaling (2019 talk), and a 2020 Google Cloud deal followed. The tick/update rate went from about 20.8 Hz to 60 Hz ("high bandwidth"). No public source describes the internal referral/allocation protocol.

### Cited Findings
- Scott Mercer, "Groups and Matchmaking in Overwatch" (June 20, 2018): "The matchmaker was designed to try and create games with equivalent-sized groups, especially for solo players". Each team's predicted win% is computed from SR, and "If one of the teams doesn't have at least a predicted 40% win rate, then we simply don't create the game". Group size does not change SR math, and grouped players' SR is not inflated. Stats for Feb 1 to May 28, 2018: about 16% of games all-solo; the most common matchup was 2,1,1,1,1 vs 2,1,1,1,1 (about 28%); 6-stacks faced groups of 4 or more about 84% of the time; 6-stack win rate 52.88% — [Blizzard forums](https://us.forums.blizzard.com/en/overwatch/t/groups-and-matchmaking-in-overwatch/134776)
- Mercer (Dec 8, 2017) on Season 8: limit the SR spread within a team, and keep grouping limits of 1000 SR for Bronze–Diamond, 500 for Master and 250 for Grandmaster (per search-result summaries of the post and coverage). He also removed performance-based SR adjustments for Diamond+ — [Blizzard Watch](https://blizzardwatch.com/2017/12/12/competitive-matchmaking-changes-coming-overwatch-season-8/), [Icy Veins grouping stats](https://www.icy-veins.com/forums/topic/37963-grouping-stats-effects-on-matchmaking-skill-rating-and-more/). Note: the exact GM value comes from search summaries; the original post was not fetched.
- Role Queue was announced on July 18, 2019: 2 Tank / 2 Damage / 2 Support, a role is picked before queueing, and Competitive gets per-role SR. Kaplan said it required "months and months of rewriting on the matchmaking system" — [GamingBolt](https://gamingbolt.com/overwatch-introducing-role-queue-for-quick-play-competitive-modes), [Dexerto](https://www.dexerto.com/overwatch/overwatch-community-reacts-2-2-2-role-lock-announced-820259/), [PCGamesN](https://www.pcgamesn.com/overwatch/overwatch-league-meta). Competitive Open Queue (no role lock) followed in May 2020 — [IPS News (2020 article)](https://ipsnews.net/business/2020/05/13/overwatch-is-adding-a-competitive-mode-that-doesnt-require-role-locks/)
- OW2-era (Season 3 retrospective; Morgan Maddren and Scott Mercer): "Role delta is the difference in skill between the best-paired players within each role across teams". The matchmaker considers group structure, may "hold some parties in queue a bit longer", and is "being built to predict future queue state". Season 4 "prioritize[s] quality backfills over quick backfills". New players start at a Bronze MMR. Calibration models per-role variance and solo-vs-group — [Blizzard news](https://news.blizzard.com/en-gb/article/23938059/matchmaking-update-season-three-retrospective-and-future-plans) (OW2, post-1.74; only the concepts carry over)
- Tick/update rate: servers were 20.8 Hz; a PC "high bandwidth" patch (2016) moved to 60 updates/s, with a dynamic fallback for poor connections and consoles initially excluded. Tim Ford: fewer "shot around corners" cases, but still predictive — [GamesBeat](https://gamesbeat.com/overwatch-netcode-tick-rate-60hz/). The architecture/netcode talk is Timothy Ford, "'Overwatch' Gameplay Architecture and Netcode", GDC 2017 — [GDC Vault](https://gdcvault.com/play/1024001/-Overwatch-Gameplay-Architecture-and)
- Infrastructure: Blizzard engineers Duc Truong and Jude Cross presented "How Blizzard Entertainment uses autoscaling with Overwatch" (OpenStack Senlin) at Open Infrastructure Summit Denver, April 30, 2019. Coverage (via search summary) reports CPU/RAM being poor scaling signals for game servers and a ~40% VM footprint reduction — [OpenStack event page](https://www.openstack.org/summit/denver-2019/summit-schedule/events/23379/how-blizzard-entertainment-uses-autoscaling-with-overwatch); [Computing.co.uk](https://www.computing.co.uk/news/3074870/how-gaming-firm-blizzard-autoscaled-overwatch-on-openstack) (returned HTTP 403 to fetch; details from search snippet only). Later Blizzard OpenDev talks reported about 12,000 OpenStack compute nodes and NUMA pinning for game-server workloads (search summary of [superuser.openinfra.org](https://superuser.openinfra.dev/articles/upgrades-in-large-scale-openstack-infrastructure-openinfra-live-episode-6/))
- January 2020: Activision Blizzard named Google Cloud its "preferred provider for game hosting infrastructure" (YouTube esports deal at the same time). No source confirms that Overwatch servers moved — [Stevivor](https://stevivor.com/news/activision-blizzard-google-partnership-google-cloud-youtube/), [TVBEurope](https://www.tvbeurope.com/tvbeverywhere/activision-blizzard-announces-google-cloud-youtube-partnerships)

### Inferences
- For a preservation server, the public design implies this minimal matchmaker: per queue (QP, Competitive role/open, Arcade modes, Custom), groups are atomic units; a role assignment comes from each player's queued role; team balance uses a win-probability check (e.g. reject below 40%); and 2-2-2 composition applies under Role Queue. The client-visible side is the lobby queue family (23300 / 24000 / 20600 in this project). Server-side matching policy is free to reimplement.
- Server allocation in the original stack is a referral: a Balancer/lobby assigns an instance and sends the client an endpoint plus per-session AEAD keys (20600 in this project). A local emulator can allocate a UDP game-server process per match and hand out that endpoint. Multi-client sessions need one game-server instance per match, with each client given its own referral keys and entity IDs.

### Gaps
- No public source describes Overwatch's internal lobby/matchmaker/game-server service topology (service names, how instances register, data-center selection protocol, backfill wire flow).
- Region selection: the Battle.net app region selector (Americas/Europe/Asia) is public knowledge, but no source was found that documents how the OW client reports ping or data-center preference to the matchmaker.
- The original Mercer 2017 Season 8 post was not fetched directly; GM grouping limit numbers come from secondary summaries.
- No source gives the exact 1.74-era tick rate figure beyond "60 updates/s" (a commonly cited 62.5/63 Hz figure is unsourced here; the project's own runs measure about 62.5 command blocks/s).

## Q4. Battle.net Agent / launcher handshake and launch arguments

### Takeaway
The Battle.net Agent is a local HTTP service on 127.0.0.1:1120 that manages installs. Its launch/auth-token handoff to games is undocumented publicly. For emulation, what matters is that the OW client connects itself to a BGS endpoint (`--BNetServer=host:1119`) and authenticates through the external-challenge web login. The developer/tournament flags (`--tank_TournamentMode`, `--lobbyServer=`) bypass BGS.

### Cited Findings
- The Agent is a local HTTP service at `http://127.0.0.1:1120`; "Documentation of the agent's HTTP endpoints is pending" (third-party cascette-rs docs) — [cascette-rs agent](https://cascette-rs.readthedocs.io/en/latest/client/agent.html). Port 1120 is IANA-registered as "bnetfile" — [connected.app port 1120](https://www.connected.app/ports/1120). Blizzard support only says the Agent/AgentSwitcher are required to install/update/run games — [Blizzard support 28445](https://support.blizzard.com/en/article/28445)
- Community workaround: `--BNetServer=us.actual.battle.net:1119` as an Overwatch launch option pins the BGS endpoint — [Steam discussion](https://steamcommunity.com/app/2357570/discussions/0/597396312337418340/?l=german)
- `-game=prometheus --install` on a Battle.net shortcut forces the Overwatch (beta) install, confirming "prometheus" as the product code — [Neozone](https://www.neozone.org/jeux-video/overwatch-comment-forcer-linstallation-de-la-beta)
- Tournament/esports path: `Overwatch.exe --tank_TournamentMode --lobbyServer=127.0.0.1:3724 --console --tank_logpath <dir>`. The production OWL launch line was `--tank_tournamentmode --tank_locale <L> --tank_audiolocale <A> --tank_disablestreaming 1 --tank_disabledevdata 1`, with pod addresses from `showmodeLobbyLocations.json` next to the exe. `--tank_tournamentmodeadmin` runs `OverwatchGM.exe`. Tournament mode zeroes k0..k3 and bypasses BGS — [Boi-027 PROJECT_STATE.txt](https://github.com/Boi-027/Overwatch-1-v1.74-Lobby-Research/blob/main/docs/PROJECT_STATE.txt), [Boi-027 README](https://github.com/Boi-027/Overwatch-1-v1.74-Lobby-Research)
- Launching the game executable directly (without Battle.net) was tested in WineHQ bug reports — [WineHQ bug 40479](https://www.winehq.org/pipermail/wine-bugs/2016-June/446195.html); Blizzard forum thread on starting OW without the Battle.net app — [Blizzard forums](https://us.forums.blizzard.com/en/overwatch/t/start-overwatch-without-using-blizzard-battle-net/222947)

### Inferences
- When `LogonRequest.cached_web_credentials` is absent, the game falls back to an external web challenge (TrinityCore's logic; the OW Plasmawatch flow matches). An emulator therefore does not need the Agent: a launcher can start the client directly with a BGS endpoint, and the client fetches its own login ticket. The project's `tools/ow1_launcher.py` already does this. Cached web credentials (the Agent's normal handoff) are the likely mechanism for "auto-login" from the Battle.net app.
- "Offline mode" in Battle.net does not apply to Overwatch: the game requires the BGS referral and the lobby. No public source documents an offline mode for OW.

### Gaps
- The Agent's HTTP endpoints, its authorization, and how the Battle.net app passes a token/`-uid`/`-launch` arguments to Overwatch: no public documentation found. A `-uid prometheus` argument could not be confirmed by any source.

## Q5. Open-source Overwatch-specific findings (Plasmawatch, Boi-027, Prometheus)

### Takeaway
Plasmawatch provides the OW BGS login emulation pattern (1119 TLS RPC + 6969 web login + Balancer-style ReferralInfo). Boi-027 (MIT) documents the 1.74 lobby ("JAM") transport: key schedule, framing, wire message-id encoding, protocol pool table, message-id bands, and the existence of keyless retail captures of custom-game/queue flows. Prometheus (OW 0.8 beta) documents the client's Entity Admin architecture and that main-menu actions are JAM requests to the server.

### Cited Findings
- Plasmawatch: Go "bnet-mock"; TLS RPC on 1119, auth webserver on 6969; a public Discord; recommends a reverse proxy for public hosting — [plasmawatch/login-server](https://github.com/plasmawatch/login-server)
- Boi-027 lobby transport: the "JAM" stream cipher (the project identifies it as Panama-LE) with a published known-answer test; handshake `HELLO PRO CLIENT`/`HELLO PRO SERVER`, nonce exchange, MAC1/MAC2, encrypted 292-byte blob; first accepted server message `0x0102`; keepalive `0x0003` answers the `0x0103` polls; the "reject" is a 5-second timeout — [Boi-027 README](https://github.com/Boi-027/Overwatch-1-v1.74-Lobby-Research)
- Framing: `[u24be frame_len][u16be msgid][...]`, with `wire_msgid = (channel << 8) | (message_id - pool_messageBase)`. Channel assignment is dynamic; retail ran 28 distinct server->client channels — [PROJECT_STATE.txt §2/§5](https://github.com/Boi-027/Overwatch-1-v1.74-Lobby-Research/blob/main/docs/PROJECT_STATE.txt)
- Protocol descriptor struct: `m_protocolCRC`, `m_messageBase`, `m_messageMax` (exclusive), `m_protocolFlags`, `m_untrustedServer`, `m_protocolName`; the bootstrap pool is CRC 0x11D82194, base 1, max 5. 105 protocol pools and 922 message registrations were recovered. Message ids are banded by hundreds: 20300-20323, 20400-20407, 20500-20510, 20600-20603, 20700-20713, 20800-20826, 21600-21634, ... up to 60900-60907 — [PROJECT_STATE.txt](https://github.com/Boi-027/Overwatch-1-v1.74-Lobby-Research/blob/main/docs/PROJECT_STATE.txt)
- Bodies are sequences of `[u32le block_len][protobuf-like block]` interleaved with fixed fields. 16-byte entity handles are `[u32le id][8 zero bytes][u32le type]`. The client has both binary and JSON decode paths, selected by a "Protocol Type". Retail opening exchange: C->S 0x0000 (334 B connect), S->C 0x0002 bare ack, C->S 0x1200 (730 B), S->C 0x3004, 0x3005 (21 KB map/asset manifest), 0x4e0d x4 (identity + account data) — [PROJECT_STATE.txt §5](https://github.com/Boi-027/Overwatch-1-v1.74-Lobby-Research/blob/main/docs/PROJECT_STATE.txt)
- Retail captures exist for `arcade_tdm_cancel`, `competitive`, `custom_game` and `queue_qp` (mid-session, no keys), plus decoded ground truth `arcadecontents` and `customgamepopular`. A full keyed session (`packets.pcap`) was published by AyakaPS/Plasmawatch on 2024-05-19. Retail message ids do not match 1.74 (different protocol CRCs), so only the grammar transfers — [PROJECT_STATE.txt](https://github.com/Boi-027/Overwatch-1-v1.74-Lobby-Research/blob/main/docs/PROJECT_STATE.txt)
- Prometheus (0.8 beta): the client initializes Lobby, Game and Replay Entity Admins. The lobby admin has one statescript entity driving the login UI/flow/music. "Main menu buttons only send JAM messages to the server saying 'hey i want to join a game'". The lobby hero display depends on JAM-sent info — [saturn-xvi/prometheus README](https://github.com/saturn-xvi/prometheus). Talk: "Prometheus: Reverse-Engineering Overwatch", 39C3, Dec 28, 2025 — [CCC hub](https://events.ccc.de/congress/2025/hub/en/event/detail/prometheus-reverse-engineering-overwatch)

### Inferences
- Boi-027's "u16 msgid" is the same thing as this project's decoded `[entry byte][message id − base]`: a channel/protocol entry index plus a message delta. The two analyses agree.
- The `custom_game` / `queue_qp` / `arcade` retail captures are the best existing ground truth for custom-game browser and queue flows. They are useless without their k0..k3, and their message ids would need mapping by protocol CRC/name rather than by number.

### Gaps
- The contents of the 105-pool / 922-message dataset in Boi-027's repo (which pools cover friends/groups/chat/custom games) were not examined in detail here. The project already has its own descriptor extraction (`protocol/*.json`).

## Q6. Mapping to what the project still needs

### Takeaway
For friends, presence, whisper, block list and clubs, BGS hashes and method ids are publicly available in TrinityCore. Implement them as BGS services on the existing 1119 RPC server, after confirming which ones the 104319 client actually binds. Matchmaking queues, custom game browser, groups and reconnect are lobby-protocol features with no public wire documentation. They must come from the client's own lobby schema (this project's descriptor extraction) and the retail-capture grammar.

### Cited Findings
- BGS services available to implement, with hashes/method ids, are listed in Q1 — [TrinityCore proto/Client](https://github.com/TrinityCore/TrinityCore/tree/master/src/server/proto/Client)
- The project currently implements only Connection/Authentication/GameUtilities v2 on BGS, plus lobby families 20500/20502/20504/20505/20802/24000/20600/23300/24900 — [project docs/BGS_PROTOCOL.md](https://github.com/p3n1cillin/ow1-preservation/blob/main/docs/BGS_PROTOCOL.md)
- BGS `ReferralQueued` (callback_delay, approx_queue_position) exists as a Balancer response type and could model login/referral queues — [project docs/BGS_PROTOCOL.md](https://github.com/p3n1cillin/ow1-preservation/blob/main/docs/BGS_PROTOCOL.md)
- In the 2018-2019 era, matchmaking groups are atomic and matched to similarly-sized groups, with a 40% win-probability floor; Role Queue is 2-2-2 with per-role SR — [Mercer 2018](https://us.forums.blizzard.com/en/overwatch/t/groups-and-matchmaking-in-overwatch/134776), [GamingBolt](https://gamingbolt.com/overwatch-introducing-role-queue-for-quick-play-competitive-modes)

### Inferences
- Friends: FriendsService v1 (0xA3DDB1BD) + FriendsListener (0x6F259A13), or the api v2 pair (0x5869BE8C / 0xDBC01A89), depending on which descriptor the client embeds. Needed: Subscribe (initial friend list), SendInvitation/Accept/Decline, RemoveFriend and the listener pushes.
- Presence: PresenceService v1 (0xFA0796FF) Subscribe/Update/Query with PresenceListener OnSubscribe/OnStateChanged, or v2 BatchSubscribe/Update/Query + OnPresenceStateUpdated. OW-specific presence field keys must be captured from the client's Update calls (log-and-echo first).
- Whisper/chat: try WhisperService v2 (0xFEE1AA14) if the client registers WhisperListener 0x62615E21. Otherwise, legacy NotificationService (0x0CBE3C43) SendNotification/OnNotificationReceived. Team/match chat is probably in the lobby or instance protocol (unverified).
- Party/groups: probably split between BGS invitation/notification and lobby group messages. First step: grep the 104319 descriptor dump for `bnet.protocol.channel`, `channel_invitation`, `club`, `notification`. Then log every BGS call made when the UI's "Invite to group" is used.
- Report / block: ReportService v1/v2/v3 SubmitReport and BlockListService (api v1) are simple ack-only services. Stub them to return success so UI flows complete.
- Account: AccountService v1 GetAccountState/GetGameAccountState/GetLicenses may be requested after login. Answer with minimal states.
- Multi-client sessions and reconnect: each client needs its own Balancer referral (cid, k0..k3, hostv4) and lobby session. Reconnect most likely re-runs the referral and the lobby login, followed by the instance referral (20600) for an in-progress match (inference). Boi-027's observation that the client re-requests a Balancer referral roughly 60 s after a stalled lobby (also in project docs) shows referral retry is built in.
- Custom game browser: needs the lobby schema families for custom games (Boi-027's `customgamepopular` naming hints at a "popular custom games" list response). Map these by protocol name/CRC in the project's descriptor extraction.

### Gaps
- Which BGS services the 104319 client actually registers (beyond Connection/Authentication/GameUtilities) has not been confirmed from public sources. The project needs to extract them from the client's embedded descriptors.
- Overwatch-specific attribute names for any GameUtilities requests other than the Balancer referral (e.g. queue status, regional data-center lists) were not found publicly.
