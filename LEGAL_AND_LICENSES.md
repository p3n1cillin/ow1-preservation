# Source and asset boundaries

The original Prometheus [LICENSE](LICENSE) remains GNU Affero General Public License v3. This branch preserves that license for its modifications and newly authored project code. Maintain corresponding source availability and the applicable AGPL notices/obligations when conveying builds or offering a modified program over a network; do not remove upstream notices. Public distribution is source-only; no preservation-branch binary release or game service is deployed.

No Blizzard executable, CASC data, hero/map/audio content, credentials or private certificates were downloaded into or added to this repository. Original game files remain an external user-supplied dependency. Source licensing does not grant redistribution rights to proprietary game resources. Preserve authorized backups separately; metadata hashes are not game payloads.

## Dependencies and research candidates

| Component | License evidenced in inspected source/package | Treatment |
|---|---|---|
| Prometheus | AGPL-3.0 | Foundation; LICENSE retained |
| nlohmann/json | MIT | Pinned vcpkg dependency; retain copyright/license |
| IXWebSocket | BSD-3-Clause | Pinned vcpkg transport; retain notices |
| MinHook | BSD-2-Clause plus included third-party notices | Pinned DLL dependency; retain full package notice |
| Dear ImGui / imnodes | MIT | Pinned dependency/submodule; retain notices |
| FreeType | FreeType License / GPL alternatives in package notices | Retain selected applicable license and full notices with binary packaging |
| fast-cpp-csv-parser | BSD-3-Clause | Pinned dependency; retain notices |
| mbedTLS | Apache-2.0 | IXWebSocket transitive dependency; retain license/notices |
| zlib / libpng / bzip2 / Brotli | Respective package license notices | Transitive libraries; collect complete package notices, including bundled components |
| Microsoft vcpkg | MIT | Build tooling/submodule; pinned revisions retained |
| OWLib / TACTLib | MIT | External research; final manifest probe links the exact 104319 provider from external revision `388f8dd6a7e67a72904bab9b5bffaa163ecbe59c`. Provider not vendored; full notice included at `research-tools/final-manifest-probe/TACTLib-LICENSE` and copied beside built output. OWLib serialized STU format/reference algorithms are used by newly authored bounded metadata readers; full OWLib notice at `docs/licenses/OWLib.txt`. No assets vendored |
| CascLib | MIT | External independent storage verification, revision `38a3466`; no DLL vendored. Envelope constants/format referenced by newly authored tools; full notice retained in `docs/licenses/CascLib.txt` |
| Jenkins lookup3 | Public-domain algorithm, Bob Jenkins | Newly authored Python implementation; attribution in storage tool |
| OW1-Emulator | BSD-2-Clause text | Inspected Workshop source only; no code imported |
| Plasmawatch Login-Server / OverLauncher | No license found in inspected checkouts | No code, certs or keys imported |
| BlizzGet | No license found in inspected checkout | External isolated local research; no source vendored and no linked binary distributed |

The dependency installation contains full notices in `<BuildRoot>\installed\x64-windows\share\<package>\copyright`; imnodes has `external/imnodes/LICENSE.md`. This table is an index, not a replacement for those texts. Future distributable packages must include all linked runtime notices and corresponding project source as applicable. The current CI preserves logs only and no longer automatically replaces an upstream binary release.

The committed `research-tools/blizzget-probe` consists of newly authored glue using an external checkout. Building it locally links external code whose redistribution license has not been established. Do not include that executable in project releases without establishing rights.

Server testing uses independent local services and synthetic fixtures. Supplied-client launch testing uses an offline AppContainer; proprietary staging files and memory diagnostics stay outside Git. Do not use real Battle.net credentials or import bundled private keys from experimental servers. The inspected Login-Server is a hardcoded-account demonstration; it is not an authenticated local account system suitable for this project. This branch does not contact production authentication services.
