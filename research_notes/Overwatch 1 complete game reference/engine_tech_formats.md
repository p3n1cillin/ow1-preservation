# Overwatch 1 engine ("Tank"), technology, file formats and protections

Scope note: the GDC 2017 netcode talk (Tim Ford) and the Statescript networking talk (Dan Reed) are listed in the catalogue for completeness only. Their content is deliberately not re-summarised. Source-code citations are to public OWLib/TACTLib commits that were cloned read-only on 2026-10-15: OWLib `546efa1` and TACTLib `129f977`. No key values, proprietary bytes or credentials are reproduced. "Project-internal" marks evidence from this repository's own runs. That evidence is not public and should be labelled as such in any report.

## 1. Catalogue of public technical talks, papers and articles on Overwatch tech

### Takeaway
Blizzard's public engineering material on OW1 is concentrated in GDC 2016–2018. That covers about 10 talks: data pipeline, replay, animation x3, audio, art, world-building, playtesting, plus the two excluded netcode/Statescript talks. I found no Blizzard OW1 rendering or AI talk. The only Blizzard rendering paper is REAC 2025 ("Evolving GI in Overwatch 2"), and it is also the best public description of the OW1-era lighting pipeline. A 39C3 (Dec 2025) community talk covers reverse-engineering of the 0.8 beta.

### Cited Findings
**GDC 2016**
- "Overwatch – The Elusive Goal: Play by Sound", Scott Lawlor and Tomas Neumann (Design/Audio). Systems "that effected all aspects of the Music, SFX and Dialog", with 12 players. — [GDC Vault 1023317](https://gdcvault.com/play/1023317/Overwatch-The-Elusive-Goal-Play). Details are in §6.
- "Animation Bootcamp: Overwatch: How A Hero Is Mei-d", with David Gibson (Blizzard) presenting alongside Tim Borrelli and Michael Jungbluth. — [GDC Vault 1023473](https://gdcvault.com/play/1023473/Animation-Bootcamp-Overwatch-How-A). A secondhand summary says animators deliberately "broke" rigs (McCree's arm, D.Va's leg), used smear frames and overshoot/hold, kept arm timing asymmetric, and designed idles for personality plus function. — [Eva Sokolova summary](https://evasokolova.wordpress.com/2016/04/03/gdc-overwatch-animation-talk-summary/)
- Wwise Tour 2016 (Montreal, 20 June 2016), Lawlor and Neumann, 7-part video series. — [Audiokinetic video](https://www.audiokinetic.com/learn/videos/fGDOgn2WXLs). Blog write-ups exist ([part 1](https://www.audiokinetic.com/en/blog/overwatch-game-audio-using-wwise-1/), [part 2](https://www.audiokinetic.com/en/overwatch-game-audio-using-wwise-part-2)), but they returned HTTP 403 to my fetches. Content below comes from search-result extracts.

**GDC 2017**
- "The Data Building Pipeline of 'Overwatch'", David Clyde (Programming). Free slides PDF. — [GDC Vault 1024444/1024019](https://www.gdcvault.com/play/1024444/The-Data-Building-Pipeline-of); [slides](https://media.gdcvault.com/gdc2017/Presentations/Clyde_David_TheDataBuilding.pdf). This is the richest primary source on the asset/GUID system; see §2/§3.
- "Replay Technology in 'Overwatch': Kill Cam, Gameplay, and Highlights", Philip Orwig (Programming). The abstract covers developing the replay system in parallel with the network model, generating and transferring reels "within a hard respawn deadline", refactoring the client architecture for an interruptible kill cam, and "custom scripting support" for kill cams. — [GDC Vault 1024053](https://www.gdcvault.com/play/1024053/Replay-Technology-in-Overwatch-Kill)
- "The Animation Pipeline of 'Overwatch'", Jesse Davis (Visual Arts). It covers "Blizzard's animation system and hero rigs" and "first-person animation-driven performances" for 23 heroes. — [GDC Vault 1024267](http://www.gdcvault.com/play/1024267/The-Animation-Pipeline-of-Overwatch)
- "Animation Bootcamp: The First Person Animation of 'Overwatch'", Matthew Boehm. The abstract asks "How would McCree reload a revolver and can you do it in 45 frames?" — [GDC Vault 1024319](http://www.gdcvault.com/play/1024319/Animation-Bootcamp-The-First-Person)
- "The Art of 'Overwatch': Evolving a Legacy", Bill Petras and Arnold Tsang. Art direction covers diversity, a hopeful future and a vibrant world; hero/map design; post-launch events. — [GDC Vault 1024268](http://www.gdcvault.com/play/1024268/The-Art-of-Overwatch-Evolving)
- "Thinking Globally: Building the Optimistic Future of 'Overwatch'", Michael Chu (world-building/narrative). — [GDC Vault 1024266](http://www.gdcvault.com/play/1024266/Thinking-Globally-Building-the-Optimistic)
- Excluded (already covered elsewhere): "'Overwatch' Gameplay Architecture and Netcode", Timothy Ford — [GDC Vault 1024001](https://www.gdcvault.com/play/1024001/-Overwatch-Gameplay-Architecture-and); "Networking Scripted Weapons and Abilities in 'Overwatch'", Dan Reed — [GDC Vault 1024041](https://www.gdcvault.com/play/1024041/Networking-Scripted-Weapons-and-Abilities)
- VFX: Hadidjah Chamberlin (Blizzard) co-presented the generic "Visual Effects Bootcamp: Artistic Principles of VFX design" with Jason Keyser (Riot). It is not Overwatch-specific. — [Game Developer](https://gamedeveloper.com/art/video-applying-artistic-principles-to-vfx-design-for-games)
- SIGGRAPH 2017 Production Session on the Overwatch animated shorts covers a cinematic pipeline on the GPU renderer Redshift, not the game engine. — [ACM DL](https://dl.acm.org/doi/10.1145/3078345.3099617)

**GDC 2018–2025**
- "Tools Tutorial Day: Playtesting 'Overwatch'", Rowan Hamilton (2018, Programming). A "playtesting first" approach guided the data pipeline, build system and server stack, because iteration needed 12 developers in one game. — [GDC Vault 1025012](https://gdcvault.com/play/1025012/Tools-Tutorial-Day-Playtesting-Overwatch)
- "Social Systems Design, Implementation, and Impacts in 'Overwatch'", Natasha Miller (2019, Design): endorsements and LFG. — [Game Developer](https://www.gamedeveloper.com/production/see-blizzard-deconstruct-i-overwatch-i-s-social-systems-at-gdc-2019-)
- "Designing Stadium: Crafting a New Game Mode for 'Overwatch'", Scott Hwang and Larry Wu (OW2 era). — [GDC Vault 1035697](https://gdcvault.com/play/1035697/Designing-Stadium-Crafting-a-New)

**Other venues**
- REAC 2025 (Rendering Engine Architecture Conference), Will Pearce (Blizzard), "Evolving Global Illumination in Overwatch 2". Free PDF with speaker notes. — [REAC_2025_Overwatch.pdf](https://enginearchitecture.org/downloads/REAC_2025_Overwatch.pdf). Details are in §4.
- 39C3 (Dec 2025), "Prometheus: Reverse-Engineering Overwatch", by breakingbread. It is a 37-minute CC BY 4.0 recording on build 0.8.0.0.24919 (beta). It calls the engine "Tank", says it "reportedly reuses core components" from the cancelled Titan project, and describes an entity-component architecture with "a deterministic, graph-based scripting engine". — [media.ccc.de](https://media.ccc.de/v/39c3-prometheus-reverse-engineering-overwatch); [39C3 hub](https://events.ccc.de/congress/2025/hub/en/event/detail/prometheus-reverse-engineering-overwatch)
- Blizzard "Evolving the Art" panel recap (OW2) covers new shaders and lighting, more expressive faces, improved cloth, more particles, weather (fog/rain/wind/ash) and cinematics-built "sequenced events". — [Blizzard news](https://overwatch.blizzard.com/en-gb/news/23189038/revving-up-the-engine-overwatch-2-evolving-the-art-panel-recap/)
- A community index of the official talks for 2016–2018 is at [awesome-overwatch](https://github.com/likethemammal/awesome-overwatch).

### Inferences
- The GDC Vault mediaProxy links for these sessions resolve to video players. Apart from Clyde's, no free slide PDFs are hosted at the conventional media.gdcvault.com paths (403). The videos on the GDC YouTube channel are therefore the only primary source for the animation, replay and audio internals.
- The Replay talk's "custom scripting support" and "interruptible kill cam" match the owdev finding of a separate Replay Entity Admin (§2). Kill cam probably runs a second ECS world fed by recorded network data. This is not verified.

### Gaps
- I found no Blizzard talk on OW1's renderer (deferred pipeline, shadows, TAA/AA, materials), on VFX tech, on bot/PvE AI, on level design tooling, or on the Workshop runtime.
- I could not retrieve the Audiokinetic articles (403) or the transcripts of the 2017 animation/replay talks.

## 2. Engine architecture: ECS, scripting, STU, GUID/resource system, streaming

### Takeaway
"Tank" is a component engine with several independent ECS worlds ("entity admins": Lobby, LobbyMap, Game, Replay). Data is defined in "StructuredData" (STU), a binary tagged format with CRC32-hashed class and field names. Every asset is addressed by a 64-bit GUID carrying engine/type/platform/region/locale/index bit-fields. Assets compile through DataBuild into manifests, packages and bundles, and are streamed asynchronously from CASC/TACT at runtime.

### Cited Findings
- **Engine identity:** the engine is called "Tank" and reportedly reuses Titan core components. — [39C3 talk page](https://media.ccc.de/v/39c3-prometheus-reverse-engineering-overwatch). The OWLib/TankLib naming uses the prefix `te` (e.g. "Tank Texture, type 004", "Tank GUID"). — [teTexture.cs](https://github.com/overtools/OWLib/blob/546efa19516d7df7ba138802d221c73ad886df28/TankLib/teTexture.cs), [teResourceGUID.cs](https://github.com/overtools/OWLib/blob/546efa19516d7df7ba138802d221c73ad886df28/TankLib/teResourceGUID.cs). PCGamesN, reporting on the GDC 2016 audio talk, says "Blizzard built a new in-house engine for the game". — [PCGamesN](https://pcgamesn.com/overwatch/overwatch-devs-on-creating-a-game-you-can-play-by-sound-and-announcing-dolby-atmos-support)
- **ECS scale:** a third-party AI summary of Ford's talk reports about 46 systems and 103 component types. — [Glasp](https://glasp.co/youtube/W3aieHjyNvw). Edgegap separately says ECS reduced the netcode surface to "three systems out of hundreds". — [Edgegap](https://edgegap.com/blog/game-backend-deep-dive-overwatch-2016-netcode-architecture-rollback). The two framings conflict, and neither is primary.
- **Entity admins:** OW has "multiple" ECS worlds called Entity Admins: Lobby, LobbyMap, Game and Replay. — [owdev: Game/ECS](https://owdev.wiki/wiki/index.php/Game/ECS), [owdev: ECS/Systems](https://owdev.wiki/wiki/index.php/Game/ECS/Systems)
- The owdev system table classifies systems by:
  - movement vtable ("Callback functions in this vtable apply all different movement from systems");
  - NetworkInterfacer (network messages are bsDataStore structures);
  - map-load notifications from the world state system;
  - MirrorSystem pre/post MirrorData-deserialization callbacks;
  - component create/destroy subscriptions.
  — [owdev: ECS/Systems](https://owdev.wiki/wiki/index.php/Game/ECS/Systems)
- **Entity IDs (0.8 beta):** prefix 0x20000000 = 'P' (player/synchronised?), 0x40000000 = 'S' (server), 0x60000000 = client-spawned projectile using a "LeaseBlock", 0x80000000 = the only prefix clients may spawn. There is a leftover formatter `"%cE:{%08X}"`. Entities may reference an STUEntityDefinition, an STUSkinTheme (an override, not an addition) and an STUSkinBase. Components come from the definition's `m_componentMap`. One example: component 0x28 = STUHealthComponent (name hash 0xaebe9baa). A partial ID→name table follows: 4 Model, 7 Camera, 0xD Effect, 0x12 MovementState, 0x13 PlayerController, 0x15 CharacterMover, 0x19 Payload, 0x1A CaptureArea, 0x22 FirstPerson, and so on. — [owdev: Game/ECS](https://owdev.wiki/wiki/index.php/Game/ECS)
- **Startup structure (0.8):**
  - Managers (window, rendering, dataflow, CASC/TACT) initialise before ECS.
  - The Lobby admin spawns a singleton container entity and a startup entity holding the Statescript component for UI/music. It loads graphs 0x58000000000041a (login/music/pause menu), …41b (after datapacks) and …41c (in-game: HeroSelect, victory, scoreboard, spectate).
  - The Game and Replay admins then initialise.
  - "Overwatch PC executables are obfuscated and have an anticheat, which gradually increased in complexity over the years."
  — [owdev: Game/Structure](https://owdev.wiki/wiki/index.php/Game/Structure)
- **0.8 launch options** include `--account`, `--key`, `--automationRoutine`, `--gatherEffectStats`, `--noautoconnect`, `--dumpAssetNames`, `--startPosition`, `--matchmake`, `--console`, `--DefaultHero`, `--BNetServer`, `--BNetSegKey`, `--QuickLogin` and `--BNetEnabled`. The invalid-argument usage printout was removed in later versions. — [owdev: Launch Options](https://owdev.wiki/wiki/index.php/Game/Launch_Options)
- **StructuredData (STU):** a "custom made binary tagged format" with "auto generated classes using simple structure definition language". Each asset row holds a GUID, commit ID, flags and a ≤64 KB compressed binary payload (name, optional backing-file SHA1, StructuredData). — [Clyde slides](https://media.gdcvault.com/gdc2017/Presentations/Clyde_David_TheDataBuilding.pdf)
- STU class and field names are CRC32-hashed and case-insensitive. The test vector is `teString` → 0xbbca304b. The compiled form has magic `STUD` (v1). — [owdev: STU](https://owdev.wiki/wiki/index.php/Game/Resources_%26_Managers/STU). OWLib reads "Version1" (STUD magic, per-instance hash) and "Version2" (CRC64 over a 36-byte header; instance-info hash table) assets. — [teStructuredData.cs](https://github.com/overtools/OWLib/blob/546efa19516d7df7ba138802d221c73ad886df28/TankLib/STU/teStructuredData.cs)
- **GUID anatomy (official):** 4 bits engine (0xF000…), 12 bits type mask (0x0FFF…), 4 bits platform, 5 bits region, 5 bits locale, 32-bit unique index. Default platform/region/locale = "Development" = 0. The worked example `0x0DE0000000000001` "Welcome to Overwatch" becomes `0x0DE0100000000001` "on PS4" and `0x0DE0100100000001` "in German". — [Clyde slides](https://media.gdcvault.com/gdc2017/Presentations/Clyde_David_TheDataBuilding.pdf)
- OWLib's mask set adds a 2-bit "Reserved" field at 0x0000006000000000. Its `Type()` bit-reverses the 12-bit field (and +1) to give the familiar type numbers (004 texture, 006 animation, …). — [teResourceGUID.cs](https://github.com/overtools/OWLib/blob/546efa19516d7df7ba138802d221c73ad886df28/TankLib/teResourceGUID.cs). owdev shows the native FLIP_BITS routine and `type = FLIP_BITS(guid & 0xFFFF000000000000) + 1`. The index is "just an increasing ID … no hash", so original names cannot be recovered. — [owdev: Resources & Managers](https://owdev.wiki/wiki/index.php/Game/Resources_%26_Managers)
- **Pipeline scale (2017):**
  - 203 asset types: 170 built, 180 processed. StructuredDataBuilder handles 80% of types, derived builders 15%, custom engine builders 5%.
  - Specialisation: 6 types by region, 13 by platform, 16 by locale. Builds target 3 platforms (PC, XB1, PS4), 2 regions and 13 locales.
  - Each configuration gets its own manifest (a list of GUID, size, MD5); 65 configurations in total.
  - A dev build is 350k assets (12 h on 8 cores; 4 h with 30 distributed workers). Retail is ~3M assets.
  - Over 10k materials generate over 22k unique shaders, each taking up to 5 s.
  - A build is ~1 GB of executables/DLLs and ~8 GB of compiled data; source assets total 900 GB.
  — [Clyde slides](https://media.gdcvault.com/gdc2017/Presentations/Clyde_David_TheDataBuilding.pdf)
- **Packages:** "Collection of compiled assets necessary for a feature", auto-generated by builders. They "can specify when they ship and with what encryption". Runtime presence/status queries support behaviour such as "If not all heroes are downloaded only open tutorial" and "If you cannot decrypt seasonal content yet don't show any of it". A "Blacklist" tool scans the manifest, executable and asset data for hero/map names that ship in "too early" an encryption. — [Clyde slides](https://media.gdcvault.com/gdc2017/Presentations/Clyde_David_TheDataBuilding.pdf)
- **Client loading:** the "Core resource system is async, no blocking load in retail". It always loads from an archive container: CASC with a TACT logical layer in retail, and HTTP from an AssetServer in dev builds. Loading is on demand. A playtest needs only "Executable, Manifest, HTTP Server". — [Clyde slides](https://media.gdcvault.com/gdc2017/Presentations/Clyde_David_TheDataBuilding.pdf). owdev adds that resources "either come from the CASC archives or are streamed from the Blizzard CDN, the latter not being done in a production environment but still possible". — [owdev: Resources & Managers](https://owdev.wiki/wiki/index.php/Game/Resources_%26_Managers)
- **Data validation tools (2017):** Data CI, Data Compare (shuffled build order; 3 memory initialisations to catch uninitialised memory), Package Manager, and load-time/size reports per hero/skin/weapon and map. — [Clyde slides](https://media.gdcvault.com/gdc2017/Presentations/Clyde_David_TheDataBuilding.pdf)
- Map content is built from "Placeables": static models, lights, reflection volumes, fog volumes, water, certain sounds and effects. "During map compile placeables of a type are all grouped together." — [REAC 2025](https://enginearchitecture.org/downloads/REAC_2025_Overwatch.pdf)

### Inferences
- The Lobby/Game/Replay entity-admin split explains several project observations:
  - lobby and world statescript graphs (0x041a/041b/041c) live on a root-owned UI entity rather than a world entity;
  - client-spawned entity IDs use the 0x8… prefix class;
  - kill cam/replay is presumably a separate admin consuming recorded snapshots.
- Clyde's "encrypt content at a feature level", together with runtime package presence queries, is the design origin of TACT encrypted blocks and TACTLib's keyring. Content gated behind keys the client lacks is hidden rather than errored.

### Gaps
- I found no primary figure for the systems/components count. The 46/103 numbers need confirmation from the Ford video.
- The owdev ECS/system tables are for 0.8 beta. Retail 1.74 offsets and system numbers differ, and owdev does not document them.

## 3. On-disk formats: CASC/TACT manifests, bundles, encryption keyring, STU, texture/model/animation/audio/movie

### Takeaway
Overwatch content sits in CASC under TACT product code "pro". The root file lists per-locale encrypted **CMF** (content manifest: GUID → CKey/size) files, plus **APM** package manifests (≤1.47) or a **TRG** "resource graph" (≥1.48, build 68309 PTR). Assets may live inside **bundles** (GUID + offset tables). CMF and TRG headers are AES-CBC encrypted using per-build key/IV derivation routines. TACTLib ships one routine per build, including `ProCMF_104319.cs` and `ProTRG_104319.cs` for this project's target. Individual BLTE blocks may additionally be encrypted (Salsa20/ARC4) with 64-bit-named keys from a keyring. Asset payloads are teChunkedData (models, effects), STU (most data), teTexture, teAnimation, Wwise banks/WEM, and Bink 2.

### Cited Findings
- **CMF:**
  - Header v26 (1.48+): build version, patch-record counts, data count, entry count and magic. Pre-1.48 builds use the CMFHeader25 layout.
  - Encryption is detected by magic>>8 == 0x636D66 ("cmf"); the format version is the top byte of the byte-swapped magic.
  - Entries are `{u32 index, u64 hashA, u64 hashB}`. Hash records are `{u64 GUID, u32 size, u8 unknown, 16-byte CKey}` (1.35+), sorted for binary search.
  - Overwatch 1.29 or earlier is rejected as unsupported.
  — [ContentManifestFile.cs](https://github.com/overtools/TACTLib/blob/129f977b604b2576bfd048e0f2be8b44ee983f39/TACTLib/Core/Product/Tank/ContentManifestFile.cs)
- **Manifest crypto:** `ManifestCryptoHandler.GenerateKeyIV` picks a provider by exact build number. Fallback to the nearest older build is optional and off by default. The provider derives a 32-byte key from the header and a 16-byte IV from the header plus a digest of the manifest name; decryption is AES-CBC with no padding. The repo holds 253 CMF providers, including `ProCMF_104319.cs`, and a parallel TRG set including `ProTRG_104319.cs`. — [ManifestCryptoHandler.cs](https://github.com/overtools/TACTLib/blob/129f977b604b2576bfd048e0f2be8b44ee983f39/TACTLib/Core/Product/Tank/ManifestCryptoHandler.cs), [CMF dir](https://github.com/overtools/TACTLib/tree/129f977b604b2576bfd048e0f2be8b44ee983f39/TACTLib/Core/Product/Tank/CMF)
- **Root/manifests:**
  - The root lists .cmf/.apm/.trg files, filtered by data platform and region (China vs global).
  - "speech" and "text" CMFs are per-locale and selected by speech and text language respectively.
  - `VERSION_148_PTR = 68309` switches from APM packages to the resource graph.
  - Fake package indices -1/-2/-3 represent the text, speech and root CMFs.
  — [ProductHandler_Tank.cs](https://github.com/overtools/TACTLib/blob/129f977b604b2576bfd048e0f2be8b44ee983f39/TACTLib/Core/Product/Tank/ProductHandler_Tank.cs)
- **APM:**
  - Header: build, packageCount, entryCount.
  - Each package entry carries `{packageGUID (type 077), keyID, …}`.
  - Package records are 12 bytes `{GUID, flags}`, with a Bundle flag.
  - Per-package bundle lists.
  — [AssetPackageManifest.cs](https://github.com/overtools/TACTLib/blob/129f977b604b2576bfd048e0f2be8b44ee983f39/TACTLib/Core/Product/Tank/AssetPackageManifest.cs)
- **TRG (ResourceGraph):** header versions 5–14. Fields are package count/block size, skin count/block size, type-bundle-index count/size (v7+), graph block size and footer magic. — [ResourceGraph.cs](https://github.com/overtools/TACTLib/blob/129f977b604b2576bfd048e0f2be8b44ee983f39/TACTLib/Core/Product/Tank/ResourceGraph.cs)
- **Bundles:** the header is `{i32 entryCount, u8 offsetSize}` (1.48+). Before 1.48 there is an extra i32 flags field. Entries are `{u64 GUID, offset}` with a 1-, 2- or 4-byte offset. — [Bundle.cs](https://github.com/overtools/TACTLib/blob/129f977b604b2576bfd048e0f2be8b44ee983f39/TACTLib/Core/Product/Tank/Bundle.cs). Clyde says DataBuild "also builds Packages and Bundles". — [Clyde slides](https://media.gdcvault.com/gdc2017/Presentations/Clyde_David_TheDataBuilding.pdf)
- **Keyring (concept only):** BLTE 'E' (encrypted) blocks name their encryption as 'S' (Salsa20) or 'A' (ARC4). — [BLTEDecoder.cs](https://github.com/overtools/TACTLib/blob/129f977b604b2576bfd048e0f2be8b44ee983f39/TACTLib/Core/BLTEDecoder.cs). Keys load from the installation's `Keyring` config, a local `{Product}.keyring` file, and an optional remote keyring URL. — [Keyring.cs](https://github.com/overtools/TACTLib/blob/129f977b604b2576bfd048e0f2be8b44ee983f39/TACTLib/Config/Keyring.cs). OWLib's `TankLib/Overwatch.keyring` has about 313 lines of `keyname keyvalue enabled # comment`; comments tie keys to patches and events (e.g. "Ana", "Summer Games 2016", "Halloween Terror 2016"). — [Overwatch.keyring](https://github.com/overtools/OWLib/blob/546efa19516d7df7ba138802d221c73ad886df28/TankLib/Overwatch.keyring). Values deliberately not reproduced.
- **teChunkedData:** magic 0xF123456F, followed by tagged chunks. — [teChunkedData.cs](https://github.com/overtools/OWLib/blob/546efa19516d7df7ba138802d221c73ad886df28/TankLib/teChunkedData.cs)
  - Model chunks: `MDLC` (model), `MRNM` (render mesh), `mskl` (skeleton), `MHRP` (hardpoints), `CLTH` (cloth), `MSTU` (embedded STU).
  - Effect chunks: `ECMP`, `ECSS` (shader setup), `ECEF` (effect), `ECEN` (entity), `ECEC` (entity control), `ECMD` (model), `ECPR` (particle), `ECRR` (ribbon renderer), `ECSO` (sound), `ECVS` (voice stimulus), `ECAT`, `ESHT`.
  — [Chunks dir](https://github.com/overtools/OWLib/tree/546efa19516d7df7ba138802d221c73ad886df28/TankLib/Chunks)
- **teTexture (type 004, also 0F1):**
  - Header: `{flags u16, mipCount, format, surfaces, usageCategory, payloadCount, …, width u16, height u16, dataSize, …}`.
  - Flags include Cube/Tex3D/Array.
  - Large textures store mips in separate payload assets of type 04D (`teTexturePayload {mips, surfaces, imageSize, headerSize}`).
  - The format byte maps to DXGI/DDS formats.
  — [teTexture.cs](https://github.com/overtools/OWLib/blob/546efa19516d7df7ba138802d221c73ad886df28/TankLib/teTexture.cs), [teTexturePayload.cs](https://github.com/overtools/OWLib/blob/546efa19516d7df7ba138802d221c73ad886df28/TankLib/teTexturePayload.cs)
- **teAnimation (type 006):**
  - Header: priority (often 16), group, boneCount, flags, duration (s), FPS, AnimationEffect ref (type 08F), then offsets to the bone list, info table and a "new animation param table (float tracks)".
  - Per-bone info table: scale/position/rotation key counts and index/data offsets.
  - Flags: NewScaleCompression 0x100, LegacyPositionFormat 0x200, NewRotationCompression 0x400, F2048 0x800.
  — [teAnimation.cs](https://github.com/overtools/OWLib/blob/546efa19516d7df7ba138802d221c73ad886df28/TankLib/teAnimation.cs)
- **GUID type map (from DataTool usage):**

  | Type | Content |
  |---|---|
  | 0x003 | STUEntityDefinition |
  | 0x004/0x0F1 | texture |
  | 0x006 | animation |
  | 0x008/0x127 | material |
  | 0x00C (+0x118) | model |
  | 0x00D/0x04A/0x08E/0x08F/0x0D4/0x12B | effects (0x0D4 "sequence") |
  | 0x01A/0x119 | model look |
  | 0x01B | STUStatescriptGraph |
  | 0x020 | STUAnimBlendTree |
  | 0x021 | STUAnimBlendTreeSet |
  | 0x02C | STUSound |
  | 0x03F/0x0BB | Wwise WEM audio |
  | 0x043 | sound bank |
  | 0x054 | generic settings |
  | 0x05F | STUVoiceSet |
  | 0x071 | subtitles |
  | 0x075 | hero |
  | 0x07F | profanity filter |
  | 0x086/0x088 | shaders |
  | 0x090 | resource keys |
  | 0x09E | abilities |
  | 0x09F | map header |
  | 0x0A5 | unlocks |
  | 0x0A6 | skin theme |
  | 0x0A8 | effect look |
  | 0x0B3 | material data |
  | 0x0B6 | movies |
  | 0x0BD | lighting manifest |
  | 0x0C0/0x0C6 | game rulesets / ruleset schemas |
  | 0x0C7 | brawls |
  | 0x0CF | lootbox |
  | 0x0D0 | voice conversations |
  | 0x0D5 | tips |
  | 0x0EE | arcade modes |
  | 0x14B | intel database |

  — [Combo.cs](https://github.com/overtools/OWLib/blob/546efa19516d7df7ba138802d221c73ad886df28/DataTool/FindLogic/Combo.cs); [ToolLogic/Extract](https://github.com/overtools/OWLib/tree/546efa19516d7df7ba138802d221c73ad886df28/DataTool/ToolLogic/Extract); [teLightingManifest.cs](https://github.com/overtools/OWLib/blob/546efa19516d7df7ba138802d221c73ad886df28/TankLib/teLightingManifest.cs)
- **Movies** are written out as Bink 2 `.bk2`. **Sound** is Wwise banks/`.wem`, converted to `.ogg` via vgmstream/revorb. — [ExtractMovies.cs](https://github.com/overtools/OWLib/blob/546efa19516d7df7ba138802d221c73ad886df28/DataTool/ToolLogic/Extract/ExtractMovies.cs), [WwiseBank.cs](https://github.com/overtools/OWLib/blob/546efa19516d7df7ba138802d221c73ad886df28/DataTool/ConvertLogic/WEM/WwiseBank.cs)
- **Map chunks** (teMapPlaceableData) contain placeable types MODEL_GROUP, ENTITY, LIGHT, SINGLE_MODEL, MODEL, REFLECTIONPOINT, TEXT, SOUND, EFFECT, SEQUENCE and AREA. — [teMapChunk.cs](https://github.com/overtools/OWLib/blob/546efa19516d7df7ba138802d221c73ad886df28/TankLib/teMapChunk.cs)
- Project-internal: rebuilding a minimal CASC install required `.build.info` columns (`IM Size`, `Armadillo`, `Last Activated`), a big-endian index archive-limit field, and the archive envelope's seeded Jenkins hash plus offset-dependent checksum, matching [CascLib's reader](https://github.com/ladislav-zezula/CascLib/blob/38a34665624b8775bb875274b36191b21c38d97b/src/CascReadFile.cpp). Source: this repo's `DISC_RUNTIME.md`.

### Inferences
- Build 104319 post-dates 1.48, so the active client uses CMF plus TRG (resource graph) rather than APM. TACTLib's dedicated 104319 CMF/TRG providers are therefore the reference for reading this exact build offline.
- OWLib's STU class set (468 generated type files) is a subset needed by DataTool. The client's runtime reflection has more types: the project counted 486 state types and 1586 graphs internally. Unnamed OWLib fields (`m_XXXXXXXX`) are CRC32 hashes whose names are unknown.

### Gaps
- I did not find public documentation of TRG graph semantics beyond header layout, of model vertex-stream formats, or of material/shader binaries. Those are only in OWLib source, which I did not review in depth for the mesh layouts.

## 4. Rendering, lighting and VFX

### Takeaway
The renderer is a deferred (GBuffer) pipeline. It uses baked indirect lighting from **Geomerics/ARM Enlighten**: lightmaps for static geometry, probes for dynamic objects, and artist-made "target meshes" in Maya. It adds baked cube-map local reflections plus optional dynamic (screen-based) reflections, volumetric "local fog", and per-map prebaked lighting scenarios fixed at match start. OW1 on PC is D3D11; DX12 arrived only as an OW2 beta in 2025. VFX are data-driven effect assets built from chunked effect components (particles, ribbons, models, sounds, voice stimuli, entities).

### Cited Findings
- "Our current GI solution is using Enlighten … a mix between baked lightmaps for static geometry and baked probes for dynamic objects."
  - Target meshes are "Hand-made by artists in Maya". They give fewer lightmap charts and seams and faster bakes.
  - Enlighten decomposes static geometry into "clusters" with sample points ("dusters") and precomputes cluster-to-cluster visibility. Baking takes "30 minutes to well over an hour depending on map".
  - Maps can have multiple lighting scenarios (e.g. day/night). "Time of day is set at match start, does not change during a match."
  — [REAC 2025](https://enginearchitecture.org/downloads/REAC_2025_Overwatch.pdf)
- OW2 replacement: DDGI-style artist-placed nested probe volumes, each producing a pair of BC6 octahedral textures (irradiance 8x8 = 64 B/probe compressed, visibility 16x16 = 256 B/probe). Probes are baked with Embree against Enlighten cluster meshes. Maps use either lightmaps or DDGI, never both. Performance was tested with "the GBuffer … full", and a GBuffer flag marks dynamic objects. Switch had about a 10 ms deficit (a third of its frame budget) before half-resolution evaluation and 16-bit shader types. — [REAC 2025](https://enginearchitecture.org/downloads/REAC_2025_Overwatch.pdf)
- A 2016 interview lists Overwatch among Enlighten titles. — [GamingBolt](https://gamingbolt.com/geomerics-and-enlighten-interview-pushing-the-boundaries-of-global-illumination). OWLib has an `STUEnlightenData` type referencing a texture. — [STUEnlightenData.cs](https://github.com/overtools/OWLib/blob/546efa19516d7df7ba138802d221c73ad886df28/TankLib/STU/Types/STUEnlightenData.cs)
- Graphics options:
  - Per a search-result summary of community guides, the devs said "local reflections use baked cube maps" while dynamic reflections compute real-time reflections from the rendered scene, and local fog is "the volumetric light-scattering effect around the camera". — [Digital Trends](https://digitaltrends.com/gaming/overwatch-performance-guide/), [GamersNexus](https://gamersnexus.net/game-bench/2861-complete-overwatch-graphics-optimization-guide). These are secondary; the developer quote was not seen in the original.
  - Dynamic reflections and local fog are the largest performance levers. — same sources
- Shader scale (2017): over 10k materials compile to over 22k unique shaders. — [Clyde slides](https://media.gdcvault.com/gdc2017/Presentations/Clyde_David_TheDataBuilding.pdf)
- DX12 first arrived as an OW2 beta in Feb 2025 (patch 3.94); DX11 remains the lead API. — [Blizzard news](https://news.blizzard.com/en-us/article/24173128/), [mp1st](https://mp1st.com/title-updates-and-patches/overwatch-2-update-3-94-deployed-for-directx-12-support-bug-fixes). Project-internal: DXGI and hardware/WARP D3D11 device creation succeed for the client inside an AppContainer (`DISC_RUNTIME.md`).
- Switch port (Iron Galaxy, 2019): 30 fps at 900p docked and 720p portable, with gyro aiming. — [VGC](https://www.videogameschronicle.com/news/overwatch-for-switch-will-run-at-30fps-developed-by-iron-galaxy)
- VFX:
  - Effect assets are chunked component lists (particle, ribbon renderer, model, sound, voice stimulus, entity, entity control, shader setup). — [OWLib Chunks](https://github.com/overtools/OWLib/tree/546efa19516d7df7ba138802d221c73ad886df28/TankLib/Chunks)
  - The 0.8 client has a `--gatherEffectStats` option. — [owdev](https://owdev.wiki/wiki/index.php/Game/Launch_Options)
  - Senior VFX artist Rachel Day describes the role as blending technical work and art, including writing shaders. — [VFX Voice](https://vfxvoice.com/rachel-day-the-game-changing-gamemaker-behind-overwatch/)

### Inferences
- REAC 2025 describes the OW2 engine. Because it says "our current GI solution is using Enlighten" and existing maps keep the lightmap path, the deferred-GBuffer plus Enlighten-lightmap/probe pipeline almost certainly describes OW1 1.74 maps too.
- The `.0BD` lighting manifest and `STUEnlightenData` are the likely containers for per-scenario Enlighten output.
- A preservation client loading a map needs the map's selected lighting scenario resident. This is consistent with this project's header/mode resource-gate work.

### Gaps
- Unpublished in public sources: shadow technique, anti-aliasing, material/BRDF model, post-processing chain, hero outline/highlight rendering, and occlusion culling (e.g. whether Umbra is used).

## 5. Animation, movement and physics

### Takeaway
Animation is data-driven: blend trees with ~28 node types (state machines, 1D/2D blends, additive/override layers, bone partitions, strafe, IK-to-target). Animations carry their own effect tracks (type 08F) and float parameter tracks. Separate first-person and third-person performances are authored. Movement is component-based (CharacterMover, MovementState, parametric and simple movement components). Ragdoll, cloth and collision are configured per entity, but no public source names a physics middleware.

### Cited Findings
- Animation blend-tree node types in OWLib:
  - AnimBlendTreeProxy, Animation, AnimationPose2d, AnimationTrackOverride, Blend1d, Blend2d, BlendPartition (with extra partition bones), BranchByCategory, Identity;
  - LayerAdditive, LayerIsolate, LayerOverride, LockMain, Random, Sequence, StateMachine, Strafe (+profile override), ToTargetDirectionIK / ToTargetBoneIK, TransitionToChildBase.
  - Related types: bone weight masks, AnimGameData_Skeleton, AnimTriangulationMap, AnimParamUpdater.
  — [OWLib STU Types](https://github.com/overtools/OWLib/tree/546efa19516d7df7ba138802d221c73ad886df28/TankLib/STU/Types)
- The animation header references an "AnimationEffect" (type 08F) and a float-track parameter table. — [teAnimation.cs](https://github.com/overtools/OWLib/blob/546efa19516d7df7ba138802d221c73ad886df28/TankLib/teAnimation.cs)
- Blizzard's animation system, hero rigs and "first-person animation-driven performances" are covered by Davis (GDC 2017). — [GDC Vault 1024267](http://www.gdcvault.com/play/1024267/The-Animation-Pipeline-of-Overwatch). Boehm's talk addresses the first-person personality versus gameplay-timing constraint (McCree reload in 45 frames). — [GDC Vault 1024319](http://www.gdcvault.com/play/1024319/Animation-Bootcamp-The-First-Person)
- Movement and physics component and config types: STUCharacterMoverComponent (refs a hardpoint plus tuning floats), owdev components 0x12 MovementState, 0x15 CharacterMover, 0x16 SimpleMovement, 0x17 ParametricMovement, STURagdollConfig (modes plus params), STUClothConfig (+ CLTH model chunk), STUCollisionConfig, STUFallingDamageComponent, STUStatescriptStatePhysicsExplosion, and projectile Statescript states (Motion/Entity/Visual/ExplosionRing/DataFlow, DeflectProjectiles). — [OWLib STU Types](https://github.com/overtools/OWLib/tree/546efa19516d7df7ba138802d221c73ad886df28/TankLib/STU/Types), [owdev: Game/ECS](https://owdev.wiki/wiki/index.php/Game/ECS)
- Hitboxes (community analyses):
  - Projectiles have their own collision radius, so hits are more generous than hitscan. — [GameSkinny](https://www.gameskinny.com/video/overwatch-hitboxes-are-weird/)
  - Some heroes' head hitboxes include shoulders (Winston, Roadhog). — [mein-MMO](https://mein-mmo.de/en/overwatch-koepfe-hitbox-helden,155447/)
  - Hit registration uses favour-the-shooter. — [Blizzard forums](https://us.forums.blizzard.com/en/overwatch/t/hanzos-projectiles-are-not-that-fast/340118)
  - OW2 Season 9 (Feb 2024) enlarged most projectile sizes. This is not OW1 behaviour. — [Kotaku](https://kotaku.com/overwatch-2-season-9-projectile-size-headshot-hitbox-1851256140)
- Project-internal (not public): the movement snapshot reader decodes position as q/1024 deltas and drives component-28 movement state. Teleporting the hero requires the module-3 snapshot path; the create-transform flag does not move it. See HANDOFF/CLAUDE.md "Module-3 hero snapshots".

### Inferences
- Animation events (sounds, VFX, voice stimuli) are carried by per-animation effect assets (08F) rather than by Statescript. A replacement server does not need to drive cosmetic animation events, only gameplay states.

### Gaps
- I found no public source on the physics engine (custom versus middleware), character-controller collision shapes, official hitbox dimensions, or animation compression math in Blizzard's own words.

## 6. Audio and the voice-line system

### Takeaway
Audio uses Wwise, the Dolby Atmos binaural plug-in and Blizzard's in-house "TED" editor. Its signature feature is a gameplay-driven "importance" mixer: threat scoring by on-screen size, aim and interaction, combined with path-distance occlusion from a pathfinding query rather than straight-line distance. Voice lines are data-driven "voice stimuli" with criteria, categories and interrupt rules, triggered from effects and Statescript.

### Cited Findings
- **Pillars and Wwise setup:**
  - Five pillars: Hero VO, clear mix, pinpoint accuracy, gameplay information, Pavlovian response.
  - Occlusion and obstruction come from raycasts plus path diversion, driving RTPC curves on volume, LPF, HPF and aux sends.
  - Obstruction/occlusion is set in Blizzard's TED game editor.
  - The Wwise Master-Mixer and Actor-Mixer hierarchies are organised by positioning type (2D/3D) and routing.
  - The team used the Dolby Atmos Binaural Mixer plug-in.
  — [Audiokinetic part 2 (search extract)](https://www.audiokinetic.com/en/overwatch-game-audio-using-wwise-part-2)
- **Importance system:** the team "tried HDR audio" but built a system that "hears" what is important: greatest threat, who you are looking at, who is shooting nearby. — [Audiokinetic part 1 (search extract)](https://www.audiokinetic.com/en/blog/overwatch-game-audio-using-wwise-1/)
- **Threat scoring:** each of the other players gets an importance value, initially "how large the player appears on the enemy's screen". Enemies aiming at you outrank closer ones that are not.
  - Path-distance occlusion was "developed while building flight-path AI for flying characters". It muffles enemies in hiding spots and raises threat as they approach.
  - Every character has a unique footstep.
  - Dolby Atmos for stereo headphones was announced for PC.
  — [PCGamesN](https://pcgamesn.com/overwatch/overwatch-devs-on-creating-a-game-you-can-play-by-sound-and-announcing-dolby-atmos-support)
- Enemy footsteps are made louder than allies'. — [Game Developer](https://www.gamedeveloper.com/audio/video-how-i-overwatch-i-was-designed-so-people-could-play-by-sound-)
- **Data types:**
  - Audio: STUSound (0x2C), STUSoundBank, STUSoundSwitch, STUSoundParameter, and STUSoundImportanceFactor (fields such as `m_weight` default 0.2).
  - Voice: STUVoiceSet (0x5F), STUVoiceSetComponent, STUVoiceLineSet, STUVoiceLine, STUVoiceLineInstance, STUVoiceStimulus (`m_category`, `m_criteria` STUCriteriaContainer, `m_interrupt`), STUVoiceCategory, STUVoiceConversation (0xD0) and subtitles (0x71).
  - Effects can embed a voice-stimulus component (ECVS).
  — [OWLib STU Types](https://github.com/overtools/OWLib/tree/546efa19516d7df7ba138802d221c73ad886df28/TankLib/STU/Types), [teEffectComponentVoiceStimulus.cs](https://github.com/overtools/OWLib/blob/546efa19516d7df7ba138802d221c73ad886df28/TankLib/Chunks/teEffectComponentVoiceStimulus.cs)
- Speech audio ships in per-locale "speech" CMF manifests, separate from text. — [ProductHandler_Tank.cs](https://github.com/overtools/TACTLib/blob/129f977b604b2576bfd048e0f2be8b44ee983f39/TACTLib/Core/Product/Tank/ProductHandler_Tank.cs)

### Inferences
- Voice lines are client-side reactions to stimuli. Events such as ability use, kills and ultimate status raise stimuli that are filtered by criteria. A replacement server needs to replicate the gameplay state and events that raise stimuli, not to choose lines. The path-distance threat mix also means audio quality depends on the client's navigation data being loaded.

### Gaps
- Unconfirmed: how stimuli are raised (Statescript node versus native), and whether voice-line choice is deterministic or synchronised across clients. Concrete numbers (voice limits, RTPC values) are only in the inaccessible Wwise Tour material.

## 7. AI and bots

### Takeaway
No Blizzard talk documents OW1 bot AI. From data types: AI behaviour is per-game-mode Statescript graphs with overrides and schemas, plus difficulty profiles, weapon fire-control info, hit reactions and body-part damage groups. Spatial reasoning uses precomputed "AI cell" data and "tactical volumes" with neighbour links. Built-in AI exists only for a subset of heroes. Workshop "dummy bots" (2019) are empty shells driven by scripts.

### Cited Findings
- STUAIBehaviorComponent holds seven `STUGameModeSpecificBehaviorScripts` fields (each `STUStatescriptGraphWithOverrides[]` plus an `STUStatescriptSchema`) and `m_difficultyProfiles` (STUAIDifficultyProfile[]).
- Other AI types: STUAIWeaponFireControlInfo (references a hardpoint), STUAIHitReaction, STUAIBodyPartDamageGroup, STUAICellData/STUAICellBytes, STUAITacticalVolume (uint array, neighbour list, vec3, extents), STUAILevelPlacedMetaData.
- Sources: [STUAIBehaviorComponent.cs](https://github.com/overtools/OWLib/blob/546efa19516d7df7ba138802d221c73ad886df28/TankLib/STU/Types/STUAIBehaviorComponent.cs), [OWLib STU Types](https://github.com/overtools/OWLib/tree/546efa19516d7df7ba138802d221c73ad886df28/TankLib/STU/Types)
- Workshop dummy bots: a developer (Darwin) said the old limitation was that bots' own AI has higher priority than Workshop commands. The new dummy bots "are just empty shells". — [PC Gamer](https://www.pcgamer.com/overwatchs-workshop-now-has-programmable-bots-enabling-training-modes-and-auto-chess-like-experiments/). "Only a certain set of heroes have built-in AI." — [BlizzardWatch](https://blizzardwatch.com/2019/09/18/junkensteins-revenge-new-overwatch-workshop-pve-mode-is-playable-right-now/)
- Path-distance queries used by audio originated in "flight-path AI for flying characters". — [PCGamesN](https://pcgamesn.com/overwatch/overwatch-devs-on-creating-a-game-you-can-play-by-sound-and-announcing-dolby-atmos-support)
- Practice vs. AI uses role-limited bot compositions, and only some heroes are available as AI (fan wiki, OW2-era). — [Overwatch Fandom](https://overwatch.fandom.com/wiki/Practice_vs._AI)
- Project-internal: training-bot gameplay definitions (e.g. hero records 0x02e0…0170–0172 → definition 0x04000000000014d2) render only when created with a skin theme. Bots are plain entity definitions without weapons.

### Inferences
- Bot AI in the original game was probably server-side Statescript (graphs selected per game mode from the AI behaviour component) plus native navigation over AI cell and tactical-volume data. A preservation server must reimplement bot decision-making; the client only renders replicated state. This is consistent with the project's server-side bot tracking.

### Gaps
- I found no public description of the navigation representation (navmesh versus cells), of how bot difficulty maps to aim error, or of the Uprising/Junkenstein PvE AI.

## 8. Protection, anti-cheat, integrity and crash reporting

### Takeaway
Blizzard has never publicly named the client protector. Community RE (Boi-027) describes it as Arxan (GuardIT): encrypted .rdata, on-demand code decryption, executable pages that cannot be re-protected, hardware-breakpoint detection that crashes the process, and anti-debug patches such as ntdll!DbgBreakPoint → `ret`. Blizzard's own legal filings name **Warden** as Overwatch's anti-cheat. OW2's "Defense Matrix" is an account/behaviour initiative (SMS Protect, ML on text/voice), not a client protector. This project measured zero dynamic-code policy, so ACG is **not** established as the reason page writes fail.

### Cited Findings
- Boi-027 (1.74 lobby research, MIT):
  - "Inline code hooking inside Overwatch.exe is impossible (VirtualProtect denied on all 11,408 executable pages). Heap writes and external-module hooks work. Hardware breakpoints (debug registers) are detected and crash the process. Read-only memory polling is safe."
  - The 1.74 message schema was "live-decrypted from Arxan'd .rdata".
  - Some functions are "NOT Arxan-encrypted" (example: prologue `48 83 c1 f0`).
  — [Boi-027 README](https://github.com/Boi-027/Overwatch-1-v1.74-Lobby-Research)
- Overwatch-Dump-Fix was an x64dbg plugin that "removes anti-dumping and obfuscation techniques" from Overwatch; it was later forked as WoWDumpFix.
  - The game patches ntdll!DbgBreakPoint from 0xCC to 0xC3; the plugin restores 0xCC on process-creation debug events.
  - For Overwatch 1.11.1.2.36859, the IAT stopped being null-terminated: the second null became a pointer to a `ret 0` instruction.
  - Dumping uses Scylla's advanced IAT search.
  — [WoWDumpFix README](https://raw.githubusercontent.com/adde88/WoWDumpFix/master/README.md)
- Arxan's generic feature set (other titles): instruction mutation, control-flow obfuscation, function encryption, anti-debug checks, integrity checks, and responses ranging from crashing via stack/control-flow corruption to repairing code. — [me3 Arxan reversing blog](https://me3.help/en/latest/blog/posts/arxan-reversing-1/). It terminates on a detected debugger or checksum mismatch. — [ssno.cc TAC analysis](https://ssno.cc/posts/reversing-tac-1-4-2025/)
- Warden: Blizzard's 2016 suit against Bossland (Watchover Tyrant) alleged the cheat "has been engineered specifically to avoid detection by Warden", which "scans for known unauthorized programs". The claims were DMCA anti-circumvention, copyright and EULA. — [PC Gamer](https://www.pcgamer.com/au/blizzard-is-suing-the-creator-of-an-overwatch-cheat-program), [Engadget](https://engadget.com/2016/07/05/blizzard-sues-overwatch-cheat-developer). The reported $8.5M judgment is weakly sourced. — [InvenGlobal](https://www.invenglobal.com/articles/1500/blizzard-wins-85m-copyright-infringement-case-against-cheat-maker-bossland)
- owdev: "Overwatch PC executables are obfuscated and have an anticheat, which gradually increased in complexity over the years". It recommends the 0.8 beta plus the Prometheus project for debugging. — [owdev: Game/Structure](https://owdev.wiki/wiki/index.php/Game/Structure)
- Defense Matrix (OW2, Sept 2022): SMS Protect (phone number required; prepaid and VOIP numbers rejected), ML to "detect and prevent disruptive behavior, cheating, and disruptive text chat", and transcription of reported players' voice chat. — [Blizzard news](https://overwatch.blizzard.com/en-us/news/23857517/defense-matrix-activated-fortifying-gameplay-integrity-and-positivity-in-overwatch-2/)
- Crash reporting:
  - Official: Overwatch error reports are at `Documents\Overwatch\Logs\Errors\Overwatch.txt`. The "BlizzardError" Temp folder is documented officially only for StarCraft Remastered. — [Blizzard Support 82454](https://support.blizzard.com/article/82454)
  - Forum users report `CrashMailer_64.exe` in an `Overwatch_retail_ErrorReporting` folder. — [Blizzard forums](https://us.forums.blizzard.com/en/overwatch/t/unsupported-16-bit-application/895994)
- Project-internal evidence (this repo, not public):
  - Execute-read mapped-page writes fail with Win32 87 while the queried dynamic-code (ACG) policy flags are 0, so "ACG is not an established cause" (`RESEARCH.md`, `ROADMAP.md`).
  - The executable "decrypts code on demand". At startup it runs a WMI hardware query (`IWbemServices`) that null-dereferences (`0xC0000005` at RVA 0x415EBB) when WMI is denied in an AppContainer.
  - The original client "detects a debugger and exits early" (`DISC_RUNTIME.md`).
  - Intermittent "early instance failures" end with exit code 1 (`CLAUDE.md` runs 124/128/134/142).
  - A lobby credential includes a 64-byte client-local integrity input checked by original RSA/HMAC code (`CLAUDE.md`, `FINAL_RETAIL.md`).

### Inferences
- The two observations "VirtualProtect denied on executable pages" (Boi-027) and "dynamic-code policy flags are zero" (this project) are compatible. Re-protection is refused by something other than ACG, plausibly the protector's own hooks or section/mapping attributes. Report this as unresolved, not as ACG.
- Because the code decrypts on demand and integrity checks are present, read-only observation, heap/data writes, and server-side emulation (this project's approach) are the robust strategies. Inline patching and debugger attachment are not.

### Gaps
- No primary Blizzard or vendor statement confirms Arxan in Overwatch. I found no public technical write-up of Warden's Overwatch module, server-side detection, ban waves' methodology, or exit-code meanings beyond community reports.

## 9. Overwatch 2 engine changes (to separate from OW1 1.74 behaviour)

### Takeaway
OW2 runs on the same engine lineage. The documented changes are rendering and lighting (new shaders and lighting, DDGI volumes replacing Enlighten lightmaps on some maps, DX12 beta in 2025), cloth/particles/weather, cinematic sequenced events, larger PvE spaces, and account security (Defense Matrix). Treat any OW2-sourced behaviour as potentially absent from OW1 1.74.

### Cited Findings
- "Evolving the Art" covers new shaders and lighting, more expressive faces, improved cloth, more particles, weather systems and cinematic sequenced events. — [Blizzard news](https://overwatch.blizzard.com/en-gb/news/23189038/revving-up-the-engine-overwatch-2-evolving-the-art-panel-recap/)
- DDGI GI is shipping "in several maps" while Enlighten lightmaps remain for others. Low-end and Switch constraints drive design choices. — [REAC 2025](https://enginearchitecture.org/downloads/REAC_2025_Overwatch.pdf)
- DX12 beta needs feature level 12_2 and Windows 10 1909 or later; DX11 remains the lead API. — [Blizzard news](https://news.blizzard.com/en-us/article/24173128/)
- Press described "significant engine upgrades" (pre-release framing). — [TweakTown](https://www.tweaktown.com/news/68537/overwatch-2-significant-engine-upgrades-better-graphics-more/index.html). A 2026 social-media report of new ambient lighting and cloth/hair/fur work is unverified. — [Threads](https://www.threads.com/@owcavalry_/post/DUZTQSqCMz5/visual-improvements-coming-to-overwatch-blizzard-are-working-on-engine-updates?hl=en)
- OW2 Season 9 changed projectile sizes. — [Kotaku](https://kotaku.com/overwatch-2-season-9-projectile-size-headshot-hitbox-1851256140)
- TACTLib's CMF/TRG providers continue past build 104319 (e.g. 105760 … 154088), so OW2-era builds keep the same manifest/crypto architecture with per-build routines. — [TACTLib TRG dir](https://github.com/overtools/TACTLib/tree/129f977b604b2576bfd048e0f2be8b44ee983f39/TACTLib/Core/Product/Tank/TRG)

### Inferences
- OWLib's current master targets OW2 data. When reading the 1.74 client offline, pin tool versions or check that type layouts (STU field sets, chunk versions) match build 104319. TACTLib's explicit 104319 providers make the container layer safe, but OWLib STU class definitions may have drifted.

### Gaps
- I found no public source quantifying OW1 to OW2 changes in ECS, Statescript or netcode internals.
