# Engineering roadmap

The eight gameplay milestones from the project request remain unverified. Infrastructure tests do not substitute for original client gameplay. No completion percentages are assigned.

1. **Obtain and fingerprint an authorized client.** Final `1.74.0.0.104319` was supplied, extracted and fingerprinted on 2026-10-12; selected original manifests and bundled map headers are verified (FINAL_RETAIL.md). The acquisition prerequisite is met for final retail; full dependency completeness remains unverified. A complete beta `0.8.0.24919` backup would still permit testing the existing baseline. Run the read-only inspector; preserve unmodified executable/CASC and build metadata outside Git. If another CDN source is evidenced, retry the exact final build config before considering a payload download. Acceptance: complete files, recorded hashes/version and independently checked executable identity.
2. **Guard the beta loader before launch testing.** Establish verified expected bytes, file size and executable hash. Replace patcher assumptions with a version profile and reject unknown builds before mutation; guard DLL initialization similarly. Reproduce a local launch under a debugger with logs. Acceptance: repeatable launch and safe rejection of an unrelated executable. A version string alone is insufficient.
3. **Validate one map/hero and two real clients.** Use identical beta copies on an isolated local environment. Verify spawn, camera, collision, hero changes, remote entities, late join, disconnect/reconnect and repeated map unload/load. Measure cadence and queue behavior. Acceptance: visible synchronized movement and no stale entities/crashes, with recordings/logs. This addresses user milestones 1, movement part of 2, and 3–4; combat remains separately required.
4. **Establish retail compatibility evidence.** Compare startup/service state machines, STU V1/V2 parsing, entity layouts and serialization using a verified final client. Build a separate adapter, retain beta regression coverage and document every offset/schema assumption. Acceptance: final client initialization and resource access demonstrated without applying beta offsets. Neither BlizzGet nor a generic TLS RPC skeleton provides this adapter.
5. **Research a minimum authoritative combat slice.** Trace one hero's input, weapon event, projectile/hit and damage states. Define historically sourced rules and server authority. Acceptance: two actual clients observe the same damage, death and respawn; malformed inputs cannot directly assign health/position. Only then expand abilities and roster. Keep original-client behavior distinct from approximations.
6. **Add local account/lobby/match lifecycle.** Independent development accounts, secure expiring sessions, room admission, map/build negotiation, teams, host roles and start/stop. Integrate only demonstrated client service interfaces. Acceptance: reconnect/auth expiry, incompatible-build rejection and two clients join one configured match. Never use Battle.net production credentials or bundled third-party private keys.
7. **Complete one historical mode with 6v6.** Add objectives, spawn rooms, timers, overtime, round transitions, outcomes and cross-client HUD state. Acceptance: twelve real players complete repeated matches under correct team/rule constraints. Extend maps/modes/heroes after this vertical slice works.
8. **Restore completeness and deployment.** Profile bandwidth/ticks, interpolation/reconciliation, stability and crash diagnostics; add progression/settings/history where supported. Validate Windows and Linux backend deployment separately. Original UI/audio/results/replay fidelity need their own evidence and tests.

Current priority is final retail login: the client reaches our loopback TLS
observer but closes during handshake. Candidate writes to mapped verification
pages fail Win32 87; queried dynamic-code policy flags are 0, so ACG is not
established. Investigate mapping constraints and narrowly scoped private trust
before implementing demonstrated RPC/login/session interfaces. The parallel
loading track publishes Practice's request, loads its header and activates the
default context, with immediate updates reaching state 4. The corrected SDK
result is a local Hotfix-directory error (status/domain/code 3/2/-1), not an empty
backend reply. Cache initialization and readiness remain unresolved. No final
map, hero or private session is verified. Do not reuse beta/disc offsets or
invent login/combat messages. See FINAL_RETAIL.md and docs/PROJECT_STATUS.md.
