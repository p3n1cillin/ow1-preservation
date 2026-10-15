# Public OWLib / DataTool / TankLib STU knowledge relevant to an OW1 1.74 server reimplementation

Pinned sources (read-only clone, no code executed):
- OWLib `ow1` branch head **243caa939efacc28eab7af8e8944f89f123b586b** (2022-10-21, "sync formats"). The `overwatch/1.74` branch head is 7afe5f52706e7002ed8c2717299cd60846f3fa3a (2022-09-07). On `develop`, commit 3b00642 "1.74" (2022-09-07) is an ancestor of `ow1`. Below, **B** = `https://github.com/overtools/OWLib/blob/243caa939efacc28eab7af8e8944f89f123b586b`.
- For comparison only: OWLib `develop` head 546efa19516d7df7ba138802d221c73ad886df28 (2026-10-11, OW2 2.25). Below, **D** = `https://github.com/overtools/OWLib/blob/546efa19516d7df7ba138802d221c73ad886df28`.
- Beta-era runtime structures in this project's AGPL upstream (Prometheus fork): `https://github.com/p3n1cillin/ow1-preservation/blob/main/prometheus/player_spawner.cpp` and `.../prometheus/entity_admin.h`.

**Version caveat, important for all sections.** On the OW1 line (`ow1` / `overwatch/1.74`), `TankLib/STU/Types` last changed in 0d17c0a ("reformat files", 2022-01-01), after c60c470 ("regen stus", 2022-01-01). The 1.74 commit 3b00642 only bumped TACTLib and the keyring. The generated type set therefore comes from an early-2022 OW1 build, not from 104319 itself. Commit 7477f57 ("tank: update STUs", 2022-04-23) is **not** an ancestor of the `ow1` branch; it belongs to the OW2 line. Instance and field hashes are the same 32-bit values the 104319 runtime reflection uses, and earlier project work matched them. Byte offsets and sizes in the `[STUField(hash, offset)]` attributes are the serialized/runtime layout of that generation and may drift slightly in 104319. Treat offsets as hints and hashes as the stable identifiers. The OWLib field names (`m_gameplayEntity` etc.) are community-assigned names for hashes; unnamed ones are `m_<HASH>` / `STU_<HASH>`.

Web search found no public wiki or documentation for STU beyond the code. Two queries ("overtools OWLib STU structured data wiki", "github Overwatch STUHero m_gameplayEntity") returned nothing relevant except the 2025 CCC talk "Prometheus: Reverse-Engineering Overwatch" ([fahrplan](https://fahrplan.events.ccc.de/congress/2025/fahrplan/event/prometheus-reverse-engineering-overwatch)), which the search summary says covers STU and the ECS on an early archived build. The README points support and discussion to the overtools Discord, which is not publicly indexable ([B/README.md](https://github.com/overtools/OWLib/blob/243caa939efacc28eab7af8e8944f89f123b586b/README.md)).

## Q1. STUHero, skins, unlocks, progression, and what supplies the hero-select / gallery 3D model (problem a)

### Takeaway
DataTool treats five `STUHero` entity-definition references as the hero's distinct "presentation" entities:
- `m_gameplayEntity` (0x950BBA06) = "Gameplay3P"
- `m_previewEmoteEntity` (0xAC91BECC) = "PreviewEmote"
- `m_322C521A` = "Showcase"
- `m_26D71549` = "HeroGallery"
- `m_8125713E` = "HighlightIntro"

Separate preview **weapon** entities with loadout, rotation and position live in `m_previewWeaponEntities` (0xFCD2B649) and `m_C2FE396F`. The hero-select or gallery 3D model is therefore most likely a separate client-spawned entity from `m_322C521A` / `m_26D71549` / `m_previewWeaponEntities` (plus an applied skin theme), not the gameplay entity. Default skins and unlocks come from `STUHero.m_heroProgression` -> `STUProgressionUnlocks.m_7846C401` (level-0 "Default" unlock lists). Skins resolve through `STUUnlock_SkinTheme.m_skinTheme` -> `STUSkinTheme`, or directly through `STUHero.m_skinThemes[].m_5E9665E3`.

### Cited Findings

**STUHero (instance hash 0x7C3457DC) in the OW1 generation** ([B/TankLib/STU/Types/STUHero.cs](https://github.com/overtools/OWLib/blob/243caa939efacc28eab7af8e8944f89f123b586b/TankLib/STU/Types/STUHero.cs))

Field order (hash, OW1-generation offset):

| Hash | Offset | Type | Field |
|---|---|---|---|
| 0x950BBA06 | 32 | `teStructuredDataAssetRef<STUEntityDefinition>` | `m_gameplayEntity` |
| 0x0EDCE350 | 48 | | name string ref (`Hero.cs` reads it via GetString) |
| 0xE04197AF | 64 | | `m_gameRulesetSchemas[]` |
| 0x2C54AEAF | 80 | | `m_category` |
| 0xF2D8DE15 | 96 | | `m_F2D8DE15[]` |
| 0x3446F580 | 112 | | description |
| 0x322C521A | 128 | EntityDefinition | |
| 0x26D71549 | 144 | EntityDefinition | |
| 0x8125713E | 160 | EntityDefinition | |
| 0xAC91BECC | 176 | | `m_previewEmoteEntity` |
| 0xFCD2B649 | 192 | `STU_A0872511[]` inline | `m_previewWeaponEntities` |
| 0xC2FE396F | 208 | `STU_A0872511[]` | |
| 0x8203BFE1 | 224 | `STU_1A496D3C[]` | GUI images: `m_id`, `m_texture` |
| 0xFC833C02 | 240 | | |
| 0xA341183E | 256 | | |
| 0x77FED604 | 272 | | `m_heroLoadout[]` (`STULoadout`, GUID type 0x9E) |
| 0xD12CB4EA | 288 | | |
| 0x485AA39C | 304 | | `m_heroProgression` (`STUProgressionUnlocks`, type 0x58) |
| 0x418F797D | 320 | | |
| 0xFF3C2071 | 336 | | `m_achievements` |
| 0xA5C9CA02 | 352 | | `m_internalName` |
| 0x893AAB2B | 368 | | `m_heroEffects` |
| 0xE1258EC1 | 384 | | |
| 0x84625AA3 | 400 | `STU_63172E83[]` | `m_skinThemes` |
| 0xE25DDDA1 | 416 | | `m_heroColor` |
| 0x44D13CC2 | 432 | | |
| 0xAF4EC410 | 436 | | `m_heroSize` |
| 0x7D88A63A | 440 | | `m_gender` |
| 0x62746D34 | 444 | byte | |
| 0x906C3711 | 445 | byte | |
| 0x40B57B0B | 446 | byte | |

The `ow1` branch has no `[STU]` size attribute visible in that paste. The class attribute is `STU(0x7C3457DC)`. For comparison, OW2 adds 0x5DCD82C0, 0xB25192D9, 0xECBDC792, 0xC837EB47, 0x0F4BFD2C, 0xD207D258 and an `STUHardPoint` ref 0xAEF1C962, and its size is 912 ([D/TankLib/STU/Types/STUHero.cs](https://github.com/overtools/OWLib/blob/546efa19516d7df7ba138802d221c73ad886df28/TankLib/STU/Types/STUHero.cs)).

**DataTool reads the hero flags this way**
- `IsHero = m_62746D34 > 0`, `SupportsAi = m_906C3711 > 0`, `GalleryColor = m_heroColor`, and loadouts come from `m_heroLoadout` ([B/DataTool/DataModels/Hero/Hero.cs](https://github.com/overtools/OWLib/blob/243caa939efacc28eab7af8e8944f89f123b586b/DataTool/DataModels/Hero/Hero.cs), lines ~72-97).
- `STULoadout` (0x07A0E32F) has these fields ([B/DataTool/DataModels/Hero/Loadout.cs](https://github.com/overtools/OWLib/blob/243caa939efacc28eab7af8e8944f89f123b586b/DataTool/DataModels/Hero/Loadout.cs)):
  - `m_name`, `m_description`, `m_logicalButton`, `m_9290B942`, `m_texture`, `m_infoMovie`, `m_7E3ED979`, `m_B1124918`
  - `m_category` (LoadoutCategory)
  - `m_0E679979`: DataTool says `>=1` means hidden ability and `==2` means secondary weapon.

**The presentation-entity naming in DataTool is explicit**

`SaveLogic/Unlock/SkinTheme.Save` calls `FindLogic.Combo.Find` on each of the five entity references with the skin's replacement map, then `SetEntityName`:
- `m_gameplayEntity` -> "Gameplay3P"
- `m_previewEmoteEntity` -> "PreviewEmote"
- `m_322C521A` -> "Showcase"
- `m_26D71549` -> "HeroGallery"
- `m_8125713E` -> "HighlightIntro"

For each `STUHeroWeapon` in the skin's `m_heroWeapons`, it walks `m_previewWeaponEntities` and `m_C2FE396F`, finds `weaponEntity.m_entityDefinition` with the weapon's replacements, and names it by loadout ([B/DataTool/SaveLogic/Unlock/SkinTheme.cs](https://github.com/overtools/OWLib/blob/243caa939efacc28eab7af8e8944f89f123b586b/DataTool/SaveLogic/Unlock/SkinTheme.cs), lines ~31-66 and `SetPreviewWeaponNames`).

**STU_A0872511 (preview weapon placement)** ([B/TankLib/STU/Types/Misc.cs](https://github.com/overtools/OWLib/blob/243caa939efacc28eab7af8e8944f89f123b586b/TankLib/STU/Types/Misc.cs), ~line 35037)
- 0x38F997AB `m_entityDefinition` (EntityDefinition)
- 0xC68C8155 `m_loadout` (STULoadout)
- 0xAF9D3A0C `m_rotation` (teQuat, default identity)
- 0x0827AB28 vec3: an offset/position, by inference

**STU_63172E83 (entry of `STUHero.m_skinThemes`)** (same Misc.cs, ~line 21402)
- 0x5E9665E3 `STUSkinTheme`
- 0x0029461B `STUSkin`
- 0x88F5CF3E `m_heroWeapons[]` (STUHeroWeapon, GUID type 0xAD)
- 0x7B95C2A2 byte

DataTool uses `m_skinThemes` directly for NPC skins and for voice extraction. That makes it the hero's built-in list of skin themes, independent of unlocks ([B/DataTool/ToolLogic/Extract/ExtractHeroUnlocks.cs](https://github.com/overtools/OWLib/blob/243caa939efacc28eab7af8e8944f89f123b586b/DataTool/ToolLogic/Extract/ExtractHeroUnlocks.cs), ~line 194; [B/DataTool/DataModels/Hero/SkinTheme.cs](https://github.com/overtools/OWLib/blob/243caa939efacc28eab7af8e8944f89f123b586b/DataTool/DataModels/Hero/SkinTheme.cs)).

**Skin types (OW1 generation)** ([STUUnlock_SkinTheme.cs](https://github.com/overtools/OWLib/blob/243caa939efacc28eab7af8e8944f89f123b586b/TankLib/STU/Types/STUUnlock_SkinTheme.cs), [STUSkinTheme.cs](https://github.com/overtools/OWLib/blob/243caa939efacc28eab7af8e8944f89f123b586b/TankLib/STU/Types/STUSkinTheme.cs), [STUSkinBase.cs](https://github.com/overtools/OWLib/blob/243caa939efacc28eab7af8e8944f89f123b586b/TankLib/STU/Types/STUSkinBase.cs), [Misc.cs](https://github.com/overtools/OWLib/blob/243caa939efacc28eab7af8e8944f89f123b586b/TankLib/STU/Types/Misc.cs))
- `STUUnlock_SkinTheme` (0xE05E4446) : `STU_3021DDED` : `STUUnlock`
  - 0x4C167404 `m_skinTheme`
  - 0x650CA813 `STU_EF85B312` ref
- `STUSkinTheme` (0x42270D59, GUID type 0xA6) : `STUSkinBase`
  - 0xA5C9CA02 `m_internalName`
  - 0xECCC4A5D: portrait texture, per DataTool
  - 0x88F5CF3E `m_heroWeapons[]`
  - 0x71818BC5 effects[]
  - 0xB8DC6D46 `m_teamColor` (STUTeamColor, type 0xCE)
  - 0x70D5F086 `STU_882807BA[]`
  - 0x02F889AE: parent STUSkinTheme
  - 0xC3E03C7F `m_color`
  - 0xE9DA85BB byte
- `STUSkinBase` (0xB7EEA3BE) : `STUShippable`
  - 0xAA8E1BB0 `m_targetTags`
  - 0xBCC55571 `STU_47C34433[]`
  - 0x50FDDF83 TeamColor
  - **0x258A7D5C `m_runtimeOverrides`** (`teStructuredDataHashMap<STUSkinRuntimeOverride>`)
  - 0x16051DC7 ulong
- `STUSkinRuntimeOverride` (0x3E88143F): 0x3D884507 replacement GUID, 0x61B88251.
- `STUSkin` (0xF6CCDAFC) : `STUSkinBase`
  - 0x40996075
  - 0x0EDCE350
  - 0xA5C9CA02 `m_internalName`
  - 0xF61E3F46 `m_skinCode`
  - 0x84625AA3 `m_skinThemes[]`
  - 0x37AB13D3 `m_hero`
  - 0x053595FD `m_skinThumbnail`
  - 0xDBEF61FE `m_skinEffects`
  - 0x38BFB46C `m_resourceKey`
  - 0x49A51309
  - 0x62746D34
- `STUHeroWeapon` (0xF2646A89) : `STUSkinBase` (`m_internalName`)

**Skin application is GUID substitution.** `SkinTheme.GetReplacements` turns `m_runtimeOverrides` into a `Dictionary<original GUID, replacement GUID>`, using `value.m_3D884507`. That dictionary is passed into every `Combo.Find`, so models, looks, effects and voice are swapped by mapping GUIDs ([B/DataTool/SaveLogic/Unlock/SkinTheme.cs](https://github.com/overtools/OWLib/blob/243caa939efacc28eab7af8e8944f89f123b586b/DataTool/SaveLogic/Unlock/SkinTheme.cs), `GetReplacements`). DataTool also narrows weapon replacements to GUID type 0x1A (ModelLook) when naming weapon looks (same file).

**Unlock base and progression** ([STU_3021DDED in Misc.cs](https://github.com/overtools/OWLib/blob/243caa939efacc28eab7af8e8944f89f123b586b/TankLib/STU/Types/Misc.cs); [STUProgressionUnlocks.cs](https://github.com/overtools/OWLib/blob/243caa939efacc28eab7af8e8944f89f123b586b/TankLib/STU/Types/STUProgressionUnlocks.cs); [ProgressionUnlocks.cs](https://github.com/overtools/OWLib/blob/243caa939efacc28eab7af8e8944f89f123b586b/DataTool/DataModels/ProgressionUnlocks.cs); [ExtractHeroUnlocks.cs](https://github.com/overtools/OWLib/blob/243caa939efacc28eab7af8e8944f89f123b586b/DataTool/ToolLogic/Extract/ExtractHeroUnlocks.cs); [ListHeroUnlocks.cs](https://github.com/overtools/OWLib/blob/243caa939efacc28eab7af8e8944f89f123b586b/DataTool/ToolLogic/List/ListHeroUnlocks.cs))
- `STUUnlock` base fields: `m_name`, `m_DAD2E3A2`, `m_resourceKey`, `m_resourceKeyId`, `m_A7B393BF`.
- `STU_3021DDED` adds:
  - 0xBEE9BCDA categories
  - 0x53145FAF "AvailableIn" string
  - 0xAA8E1BB0 targetTags
  - 0x3446F580 description
  - 0x0B1BA7C1 team definition (DataTool `TeamDefinition`)
  - 0xC92AF903 sub-unlocks
  - 0xBB99FCD3 `m_rarity`
- `STUProgressionUnlocks` (0x8CE1D110, GUID type 0x58):
  - 0x9135A4B2 `STUUnlocks` (DataTool: "UnknownUnlocks")
  - 0xBF482AA3 `m_otherUnlocks` (achievement/OWL rewards)
  - 0x7846C401 `STU_1757E817[]` = {0xDB803F2F `m_unlocks`, 0x2C01908B `m_level`}: "LevelUnlocks"
  - 0x473494FF `m_lootBoxesUnlocks` (`STULootBoxUnlocks`: `m_unlocks`, 0x7AB4E3F8 `m_lootboxType`)
  - 0x160B0466: parent `STUProgressionUnlocks`
- DataTool extracts every `LevelUnlocks` list under event key **"Default"** ("// default unlocks"). `ListHeroUnlocks` likewise prints `LevelUnlocks` as "Default". So the publicly understood definition of a hero's default/base unlock set is `m_heroProgression.m_7846C401[*].m_unlocks`. Loot-box lists are named per event type.

**GUID type map (TankTonka enum), with raw-prefix arithmetic** ([D/TankTonka/Models/Common.cs](https://github.com/overtools/OWLib/blob/546efa19516d7df7ba138802d221c73ad886df28/TankTonka/Models/Common.cs); [teResourceGUID.Type](https://github.com/overtools/OWLib/blob/546efa19516d7df7ba138802d221c73ad886df28/TankLib/teResourceGUID.cs): type = FlipTypeBits(bits 48-59) + 1)

| Type | Name | Raw prefix |
|---|---|---|
| 0x1A | ModelLook | |
| 0x1B | StatescriptGraph | 0x0580 |
| 0x25 | GameMessage | **0x0240** |
| 0x36 | UXLink | |
| 0x45 | UXIDLookup | |
| 0x58 | ProgressionUnlocks | 0x0ea0 |
| 0x5A | UXScreen | **0x09a0** |
| 0x75 | Hero | |
| 0x7C | UXDisplayText | |
| 0x9E | Loadout | |
| 0x9F | MapHeader | |
| 0xA5 | Unlock | |
| 0xA6 | SkinTheme | |
| 0xAD | HeroWeapon | |
| 0xB0 | UXViewModelSchema | |
| 0xC5 | GameMode | |
| 0xC6 | GameRulesetSchema | |
| 0xCE | TeamColor | |
| 0x103 | CustomizableSkinTheme | |

I computed the raw prefixes with the same bit flip, as a self-check:
- 0x0240 -> 0x25: the project's "0x024 game messages" are GUID type **0x25 GameMessage**.
- 0x09a0 -> 0x5A: "UX layers" are **UXScreen** assets.
- 0x0a88 -> 0x116, 0x0d60 -> 0x6C, 0x0a40 (config vars) -> 0x26. None of these is named in the TankTonka enum.

### Inferences
- The hero-select and Hero Gallery 3D model is very likely spawned client-side from `STUHero.m_26D71549` ("HeroGallery") or `m_322C521A` ("Showcase"), with `m_previewWeaponEntities` placed by its rotation/offset and the selected `STUSkinTheme`'s `m_runtimeOverrides` applied as GUID substitutions. These definitions (and their models, looks and anims) must be resident or loadable. The project has a 20505 list-1 preload path that could be used to preload them as a test. Gallery counts of "0/0 cosmetics" are probably computed by the client from `m_heroProgression` unlock lists intersected with the account's owned-unlock records (lobby 24900). Two things to verify: the server sends the exact `STUUnlock` GUIDs (type 0xA5) from `m_7846C401` lists, and the GUIDs are catalogue-present in that build. These are not established by OWLib; they are inferences from the data shapes.
- The project's earlier notes name record refs 03d0 (322c521a), 09fc (26d71549), 0dda (8125713e) and 1438 (previewEmote). They map exactly to DataTool's Showcase / HeroGallery / HighlightIntro / PreviewEmote entities.

### Gaps
- OWLib does not describe *runtime* gallery or hero-select logic, i.e. which client system spawns the HeroGallery/Showcase entity or what triggers it. No public source was found.
- `STU_3021DDED`'s ownership/"default owned" semantics (e.g. `m_5B66C189`, `m_EF7AAE4A`, `m_1A546C64`, `m_40926C4A`) are unnamed. The meaning of `STUUnlock_SkinTheme.m_650CA813` (`STU_EF85B312`) in OW1 is also unknown. In OW2 this field became `m_type` (Enum_D32A5854) ([D/STUUnlock_SkinTheme.cs](https://github.com/overtools/OWLib/blob/546efa19516d7df7ba138802d221c73ad886df28/TankLib/STU/Types/STUUnlock_SkinTheme.cs)).

## Q2. STUEntityDefinition, components, child entities and hardpoints, weapons (problem b)

### Takeaway
`STUEntityDefinition.m_childEntityData` (0xF29E4995) is an inline array of `STUChildEntityDefinition` with four fields:
- `m_child` (0x436BEFE6): the child EntityDefinition
- `m_hardPoint` (0x2D3CDFA9): a type-0x3C hardpoint ID
- `m_49F782CE`: an STUIdentifier used as the child's identifier/slot
- `m_2263EA37`: byte flag

DataTool resolves the hardpoint against the *parent model's* `STUModel.m_hardPoints[]` / MHRP chunk, which gives the hardpoint GUID, parent bone GUID, rotation and position. Weapon models attach to bones that way. Weapon logic is a separate component (`STUWeaponComponent`: manager script plus `m_weapons[]` scripts/graphs). `STUFirstPersonComponent.m_entity` points to a separate first-person entity definition.

### Cited Findings

**Entity definition and children** ([STUEntityDefinition.cs](https://github.com/overtools/OWLib/blob/243caa939efacc28eab7af8e8944f89f123b586b/TankLib/STU/Types/STUEntityDefinition.cs); [STUChildEntityDefinition.cs](https://github.com/overtools/OWLib/blob/243caa939efacc28eab7af8e8944f89f123b586b/TankLib/STU/Types/STUChildEntityDefinition.cs))
- `STUEntityDefinition` (0x73BB2F3A, OW1 generation):

  | Hash | Offset | Field |
  |---|---|---|
  | 0x8B9A461F | 8 | EntityDefinition ref (parent/template) |
  | 0x04A8896C | 24 | EntityDefinition ref |
  | 0xF29E4995 | 40 | `m_childEntityData` (inline `STUChildEntityDefinition[]`) |
  | 0x8AF8F4F5 | 56 | `m_componentMap` (`teStructuredDataHashMap<STUEntityComponent>`, keyed by component hash) |
  | 0x87916047 | 72 | Enum_790E517D |
  | 0xBE8E52CD | 76 | uint |

  OW2 adds byte 0xBAD21E97 ([D/STUEntityDefinition.cs](https://github.com/overtools/OWLib/blob/546efa19516d7df7ba138802d221c73ad886df28/TankLib/STU/Types/STUEntityDefinition.cs)).
- `STUChildEntityDefinition` (0x1D9159F2): offsets 8 / 24 / 40 / 56 for the four fields listed in the takeaway.

**DataTool child handling** ([B/DataTool/FindLogic/Combo.cs](https://github.com/overtools/OWLib/blob/243caa939efacc28eab7af8e8944f89f123b586b/DataTool/FindLogic/Combo.cs), `case 0x3`, lines ~509-610; `ChildEntityReference`, lines ~245-255)
- For each child, DataTool recurses `Find(child)` with `ChildEntityIdentifier = m_49F782CE`. It keeps a `ChildEntityReference{m_defGUID (after skin replacement), m_hardpointGUID, m_identifier}`, and it also indexes `m_entitiesByIdentifier[identifier]`.
- Component processing sorts `STUModelComponent` / `STUEffectComponent` first, because model and effect context is needed. It then handles:
  - `STUStatescriptComponent.m_B634821A[]` graphs
  - `STUWeaponComponent` (`m_managerScript`, plus `m_weapons[].m_script` and `.m_graph`)
  - `STUVoiceSetComponent`
  - `STUFirstPersonComponent.m_entity`
  - `STUHealthComponent.m_63FBB2D3`
  - local and mirrored idle anim components
- The `.owentity` writer records, for each child: child name, hardpoint GUID, identifier GUID, indices, and `"hardpoint_<idx>"` as the attach name ([B/DataTool/SaveLogic/Entity.cs](https://github.com/overtools/OWLib/blob/243caa939efacc28eab7af8e8944f89f123b586b/DataTool/SaveLogic/Entity.cs), lines ~47-65).

**Hardpoints**
- `STUModel` (0x871BD3D0) ([Misc/STUModel in B types](https://github.com/overtools/OWLib/blob/243caa939efacc28eab7af8e8944f89f123b586b/TankLib/STU/Types/STUModel.cs)):
  - 0x818D011C `m_skeleton`
  - 0xFD232466 `STU_F0E34581[]`
  - **0xC45F5F6F `m_hardPoints` (`STUModelHardpoint[]`)**
  - 0x37ED05D0: another STUModel
  - 0x81AF6609 `m_usageCategory`
- `STUModelHardpoint` (0xBE9DDFDF) : `STU_F0E34581` (0xF0E34581), which has:
  - 0xB48F1D22 `m_name` (string)
  - 0x888BCD8B STUBoneLabel
  - **0xEDF0511C hardpoint GUID (u64)**
  - **0xFF592924 parent bone GUID (u64)**
  - 0xAF9D3A0C `m_rotation` (quat)
  - 0x7DC1550F `m_position` (vec3)
- `STUHardPoint` (0xF9134815) has no fields; it is the 0x3C asset type.
- The model exporter resolves the bone by matching `Index(m_FF592924)` against skeleton IDs. It computes the world matrix as `RotationQuaternion(m_rotation) * Translation(m_position)` times the bone's world space ([B/TankLib/ExportFormats/OverwatchModel.cs](https://github.com/overtools/OWLib/blob/243caa939efacc28eab7af8e8944f89f123b586b/TankLib/ExportFormats/OverwatchModel.cs), lines ~177-205).
- Legacy chunk format: MHRP has a header {count, unk count, offsets}. Each `Hardpoint` is {4x4 matrix, 0x3C hardpoint GUID, 0x12 bone GUID, 2 unknown u64} ([B/TankLib/Chunks/teModelChunk_Hardpoint.cs](https://github.com/overtools/OWLib/blob/243caa939efacc28eab7af8e8944f89f123b586b/TankLib/Chunks/teModelChunk_Hardpoint.cs)).
- Other hardpoint references:
  - `STUCharacterMoverComponent` has an `STUHardPoint` ref 0x761CC74E.
  - `STUModelComponent` has `STUHardPoint` 0x2070AB9E.
  - `STUConfigVarHardPoint` (0xE39B4C43) exists.
  - Pre-hash-change field names include `m_aimHardpoint`, `m_attachHardpoint`, `m_eyeHardpoint`, `m_effectHardpoint`, `m_sourceHardpoint`, `m_targetHardpoint` ([B/TankLibHelper/DataPreHashChange/KnownFields.csv](https://github.com/overtools/OWLib/blob/243caa939efacc28eab7af8e8944f89f123b586b/TankLibHelper/DataPreHashChange/KnownFields.csv)).

**Weapons and first person** ([STUWeaponComponent.cs](https://github.com/overtools/OWLib/blob/243caa939efacc28eab7af8e8944f89f123b586b/TankLib/STU/Types/STUWeaponComponent.cs); [types dir](https://github.com/overtools/OWLib/tree/243caa939efacc28eab7af8e8944f89f123b586b/TankLib/STU/Types))
- `STUWeaponComponent` (0x15CB6532) : `STUMirroredEntityComponent`:
  - 0xC63E11DD `m_managerScript` (`STU_6BE90C5C` = statescript graph asset)
  - 0x3BD16B9E `m_weapons` (`STUWeaponDefinition[]`)
- `STUWeaponDefinition` (0x61386B75):
  - 0xC71EA6BC `m_graph` (`STUStatescriptGraphWithOverrides`, inline)
  - 0x4D5597A8 `m_script` (graph asset)
- `STUStatescriptGraphWithOverrides`: `m_graph` asset, `m_1EB5A024` schema-entry overrides (`STUStatescriptSchemaEntry` {0x0D09D2D9 id, 0x07DD813E `m_value` ConfigVar}), byte 0x75408640.
- `STUFirstPersonComponent` (0x9D28963F):
  - 0xA83C2C26 `m_entity` (the first-person entity definition)
  - floats 0x4B75D84E, 0xE29993A5 (default 1.55), 0x816B830F (default 1.15)
- `STUModelComponent` (0x191835F9):
  - 0x2D124BE2 `m_model`
  - 0x9297ADB4 `m_look`
  - 0x523339C1 `m_animBlendTreeSet`
  - 0x36F54327 blend tree
  - 0x2070AB9E hardpoint
  - plus collision / ragdoll / cloth configs

### Inferences
- Tracer's projectile and tracer origin (problem b) depends on the weapon entities being children of the gameplay or first-person entity, attached to their model's hardpoint via `m_hardPoint`. The child definitions (`m_child`) in the hero gameplay entity's `m_childEntityData`, and in the `STUFirstPersonComponent.m_entity` definition, are where the server-created child entities should come from. Use the same identifier `m_49F782CE` for the slot.
- DataTool only treats children as static attachments. Whether the OW1 network protocol replicates children as independent creates with a parent link, or the client instantiates `m_childEntityData` itself, cannot be learned from OWLib.

### Gaps
- No public semantics for `m_2263EA37` (the child flag; possibly client-only or spawn-with-parent) or for `STUEntityDefinition.m_8B9A461F` / `m_04A8896C`.
- OWLib does not map STU component hashes to runtime component type indices. The project's own native map (0xf525e0) remains the authority.

## Q3. Statescript graphs, UX presenters, UXScreen/UX family, data binding (problem c)

### Takeaway
OWLib names the full statescript graph container. `STUStatescriptGraph` (0x7236F6E3) holds nodes, states, entries, remote-sync nodes, sync vars, bit counts and a `m_predictionBehavior` enum. UX presenters are `STUStatescriptStateUXPresenter` (0x7A7F2732) subclasses with:
- a condition (`m_3DBF6FD2` -> `STU_5F31962C{m_condition ConfigVar, enum}`)
- input plugs (`m_AC8CB6BC`) and output plugs/UX events (`m_8D6AF7DD` = `STU_EB19DAFA[]` keyed by STUIdentifier `m_id`)
- a data-context list `m_4FF3A882` (`STU_294F6168{m_id, STU_076E0DBA value}`)
- a priority/layer block `m_45216F79`
- config var `m_EC32138E`, plus another dynamic or expression var

The UI layout side is a WPF/XAML-like object model: `STUUXScreen` (GUID type 0x5A) -> `STU_BB7E7366.m_rootElement` -> `STUUXElement` / Panel / Control trees, with `STUUXBinding` / `STUUXMultiBinding` / `STUUXViewModel`. OWLib's DataTool does **not** extract or interpret UX screens or statescript logic.

### Cited Findings

**Graph container** ([B/TankLib/STU/Types/STUStatescriptGraph.cs](https://github.com/overtools/OWLib/blob/243caa939efacc28eab7af8e8944f89f123b586b/TankLib/STU/Types/STUStatescriptGraph.cs))

`STUStatescriptGraph` (0x7236F6E3, size 392) fields:
- 0xC71EA6BC `m_graph`
- 0x9B2111C5 `m_nodes`
- 0xE6E7A042 `m_states`
- 0x16B4863C `m_entries`
- 0xD9E7CAA2 asset refs
- 0x44D31832 / 0xA1183166 / 0x0D92E2AF identifier arrays
- 0x2919DF46 / 0x680A2CB2 int arrays
- 0x9CEC6985
- 0x41A83970 `m_remoteSyncNodes`
- 0x434A5521 `m_syncVars` (`STUStatescriptSyncVar` {0x0D09D2D9 id, 0x56341592 enum, 0xAC9480C7 byte})
- 0x58CEA0CF / 0x27FBFF72 `STUStatescriptOperationPattern[]`
- 0xF3CFCE23
- 0x85EE1391 ConfigVar
- 0xFF44FD8B schema, 0x151AD444 `m_publicSchema`
- 0xF63B1D41 `m_playScriptHotReloadBehavior`
- 0x55B1663D `m_predictionBehavior`
- **0xEBCF63C6 `m_nodesBitCount`, 0x1754C98D `m_statesBitCount`, 0x02FABAC2 `m_remoteSyncNodesBitCount`, 0x475EA078 `m_syncVarsBitCount`**
- 0xEC5B637A, 0x50AAA58E
- bytes 0x75408640, 0xBB90784A, 0xCAA6714F

The bit-count fields are directly relevant to the replication bit widths the project already uses (e.g. `GRAPH_COUNTS`).

**Node bases** (types dir B)
- `STUStatescriptBase` (0xC2DC60F6) : `STUGraphNode`:
  - 0xBF5B22B7 / 0x8BF03679 `STUStatescriptRemoteSyncVar[]` (id + enum)
  - 0xA2287776 enum
  - 0x871A8203, 0x602E1F8F ints
  - 0xAED90719 enum
  - bytes 0x2BBEEAB8, 0xADEB6E05, **0xE1B0C07F `m_clientOnly`, 0x9A861B79 `m_serverOnly`**
- `STUStatescriptState` (0x7C37840C):
  - 0xE390CDB8 `m_stateGroup`
  - 0xC4E39595 `m_transitionPlug`
  - 0x4F8F2F3F int[]
  - 0x0B1AA8CA `STUStatescriptSubGraph`
  - 0xE965193B `m_beginPlug`
  - 0x984573B1 `m_onBeginPlug`
  - 0x8BC64AEB `m_onEndPlug`
  - 0x64338F79 `m_subgraphPlug`
  - 0x26B6454C int
- `STUStatescriptStateHero` (0x91428992): 0x176ED263 `m_controller`, 0x37AB13D3 `m_hero`, plus four more ConfigVars. Its hashes match the project's 0x0c90 state 0.
- `STU_BB7F6C27` is a state with 0x37AB13D3 `m_hero` + 0xC0A83121 `m_skin` ConfigVars, which makes it a candidate hero+skin presentation state.
- `STUConfigVarDynamic` (0x4B093107): 0x4D2DB658 `m_identifier` (ushort var id), 0x60DB8F99 byte. This matches the project's "m_60DB8F99=1 => entity-global" finding.
- `STUConfigVarExpression` (0xA7E04FB2): `m_expression`, `m_configVars[]`.
- `STUConfigVarHero` (0xCBEDB8FD): `m_hero`.

**UX presenter** ([B/TankLib/STU/Types/STUStatescriptStateUXPresenter.cs](https://github.com/overtools/OWLib/blob/243caa939efacc28eab7af8e8944f89f123b586b/TankLib/STU/Types/STUStatescriptStateUXPresenter.cs); Misc.cs)

Fields, with OW1 offsets:

| Hash | Offset | Type / field |
|---|---|---|
| 0x3DBF6FD2 | 232 | `STU_5F31962C` {0xBAA74493 `m_condition` ConfigVar, 0x4BA4C058 Enum_CEBBB217} |
| 0xAC8CB6BC | 256 | `STU_398F9098[]` input plugs with 0x11B47C68 `m_id` |
| 0x8D6AF7DD | 272 | `STU_EB19DAFA[]` output plugs with `m_id` (the project's UX event ids 0d80…65d0/65d3) |
| 0x4FF3A882 | 288 | `STU_294F6168[]` {`m_id`, 0x51F3DB2A `STU_076E0DBA` dynamic/expression var}: by inference, named data-context slots bound into the screen |
| 0x45216F79 | 304 | `STU_4586592B` (polymorphic: `STU_43A1F049`{2 ConfigVars} or `STU_99CEEC04`{0x25521BD9 `STU_A1BAFA3E`, 2 ConfigVars, 0xBB16810A `m_priority`}) |
| 0xEC32138E | 312 | ConfigVar |
| 0x45017CEA | 320 | `STU_076E0DBA` |

- About 110 presenter subclasses exist, mostly unnamed. Named ones: `STUStatescriptStateUXLoading` (0xD1674894), `UXMatchRecap` (0x02F7FEA4), `UXCustomGameDetails` (0x4573639A).
- Presenters with hero context:
  - `STU_82811BF6` {`m_unlock`, `m_hero`, ...}
  - `STU_9700865B` {`m_entityID` 0xB141AAE4, `m_hero`, ...}
  - `STU_B6CA503C`, `STU_4988FCB3`, `STU_D30D15AC` {`m_hero`}
  - `STU_CB6C0ED7` {`m_entity` 0xA83C2C26, ...}
  - `STU_D68203F6` {`m_unlocks` 0xDB803F2F}
- Pre-hash-change type names list more presenters whose retail hashes are unknown: `STUStatescriptStateUXHeroHelp`, `UXMatchStatus`, **`UXReticleOverride`**, **`UXScreen`**, `UXSocialMenu`, `UXCustomGameBrowserFilter` ([KnownTypes.csv](https://github.com/overtools/OWLib/blob/243caa939efacc28eab7af8e8944f89f123b586b/TankLibHelper/DataPreHashChange/KnownTypes.csv)).

**UX object model** (types dir B; GUID types from [TankTonka Common.cs](https://github.com/overtools/OWLib/blob/546efa19516d7df7ba138802d221c73ad886df28/TankTonka/Models/Common.cs))
- `STUUXScreen` (0x1C68E74D) : `STU_BB7E7366` {**`m_rootElement` STUUXElement**, two bytes 0x850D29D4 / 0x1352FC17}. It adds `m_sampleData` (`STU_C811573A` ref), `m_resourceKeyLookup` (`STU_EDCF5A52`) and `m_loadBehavior` (`STU_C1210E7A`).
- `STUUXTemplate` (0x092AFD09) : `STU_BB7E7366`.
- Element and control classes: `STUUXElement`, Panel, Grid, StackPanel, ContextRoot (0x2D18F0FA), ContentControl, ItemsControl, Selector, Button, TextBox, Popup, Storyboard, VisualStateManager.
- `STUUXBinding` (0x7D211E22) : `STUUXBindingBase`:
  - 0x27437CA7 teString (path text)
  - 0x95FBB12E `STUUXPropertyPath`
  - `m_F0E5E268`
  - `m_source` (STUUXObject)
  - `m_B792BE50`
  - `m_mode`
- `STUUXMultiBinding`, `STUUXPriorityBinding`
- `STUUXViewModel` {`m_keys` ulong[], `m_values` STUUXObject[]}
- `STUUXResource` {`m_resourceKey` string}
- `STUUXComponent` (0x440D818B): an entity component with no fields
- `STUUXDisplayText` (0xB456B24F) {`m_text`}, GUID type 0x7C
- `STUUXLogicalButton`
- Type 0xB0 `UXViewModelSchema` exists as a GUID type.
- **No `STUUXLayer` class exists in OWLib's OW1 types.** The project's "UX layer" GUIDs (raw 0x09a0…) decode to GUID type 0x5A = **UXScreen**.

**DataTool does not handle UX** in the OW1 branch. A grep for STUUX / UXScreen / UXPresenter across DataTool and TankView finds only `FindLogic/Combo.cs`, and only commented-out statescript code there. There is no UX extractor ([B/DataTool/FindLogic/Combo.cs](https://github.com/overtools/OWLib/blob/243caa939efacc28eab7af8e8944f89f123b586b/DataTool/FindLogic/Combo.cs), lines ~470-505, commented block).

### Inferences
- For the HUD gap: each HUD presenter's draw gating is most plausibly its `m_3DBF6FD2.m_condition` ConfigVar plus its `m_45216F79` priority/visibility block. Its data context comes from the `m_4FF3A882` slot vars (dynamic var ids), which the project could read per HUD presenter from the graph assets with existing graph tools, and evaluate.
- HUD_Root etc. are UXScreen (0x5A) assets. Their `m_loadBehavior` (`STU_C1210E7A`) is worth decoding offline. If `m_loadBehavior` requires a native "HUD context" (e.g. a world-owned UI context, as the project already suspects), that would explain the absent HUD.
- `STUStatescriptGraph.m_predictionBehavior` (0x55B1663D) is the per-graph STU property behind client prediction. The project's prediction gate investigation could compare its value on hero graphs.

### Gaps
- No public field names for `STU_4586592B` subclasses, `STU_C1210E7A` load behavior, or the binding context resolution. OWLib has no documentation of how presenter context binds to UXScreen data context.
- Retail hashes for `UXReticleOverride` / `UXScreen` presenter types are not given (only pre-hash-change CRCs).

## Q4. Team / filter bits, health, model and skin components (problem d)

### Takeaway
There is **no FilterBits, Team, PlayerInfo or Skin entity component in OWLib's STU types**. Of the 104 component classes found, 24 are named; examples:
- `STUAIBehaviorComponent`, `STUCharacterMoverComponent`, `STUEffectComponent`, `STUFirstPersonComponent`
- `STUHealthComponent` (0xA658CA1C), `STUModelComponent`
- `STUPvPGameComponent` (0x2DB5899F)
- `STUStatescriptComponent` (0xFD024F42), `STUTargetTagComponent` (0x445E7678)
- `STUUXComponent`, `STUVoiceSetComponent`, `STUWeaponComponent`

Team and filter bits are runtime/replicated state, not authored data. The beta Prometheus code sets them on runtime component 0x10 (FilterBits) and 0x3F (PlayerInfo). Teams in authored data appear only in game-mode or ruleset records.

### Cited Findings

**Health component** ([STUHealthComponent.cs](https://github.com/overtools/OWLib/blob/243caa939efacc28eab7af8e8944f89f123b586b/TankLib/STU/Types/STUHealthComponent.cs))
- `STUHealthComponent` (0xA658CA1C) : `STUMirroredEntityComponent`:
  - 0x73AEA60D `STU_9EA55F3D[]` (embedded health pools, by inference)
  - 0x28994152 `m_deathEffect`
  - 0x63FBB2D3, 0x0AEA1B48, 0x9AF692CD effect refs
  - 0xE64867CE int (default -1)
  - 0x5AF3C1F6 float (default 7.5)
  - bytes 0x5A007127, 0xCDB100D1 (1), 0xF6CE4EAC, 0xA80BAB3F (1)
- Statescript health types: `STUStatescriptStateHealthPool` (0x8CC3BD5A), `STUStatescriptStateModifyHealth` (0x826613B7), `STUStatescriptModifyHealth` (0xA8BC2948).
- Pre-hash name "MirroredHealthPool" exists ([KnownTypes.csv](https://github.com/overtools/OWLib/blob/243caa939efacc28eab7af8e8944f89f123b586b/TankLibHelper/DataPreHashChange/KnownTypes.csv)).

**Teams in authored data** (types dir B)
- **`STUGameMode` (0x494C33C4)**:
  - 0xA43573F4 identifiers
  - **0xCF63B633 game-mode script (`STU_6BE90C5C`)**
  - 0x3CE93B76 var pairs
  - 0xF88BA3B9 second script
  - 0xAD4BF17F var pairs
  - `m_displayName`
  - 0xE04197AF `m_gameRulesetSchemas`
  - **0xD440A0F7 `m_teams` (`STUGameModeTeam[]`)**
  - 0xDA642982 `m_loadoutOverrides`
  - 0x8A5415B9 `m_gameModeType`
  - several bytes
- **`STUGameModeTeam` (0xD797394C)**:
  - **0xA2781AA4 `m_controllerScript`**
  - 0x6F71E9AA var pairs
  - **0x76E8C82A `m_bodyScript`**
  - 0xEA2B516F `m_bodyVars` (`STUGameModeBodyVars` {`m_vars`, `m_hero`})
  - 0x59C86C8D `m_availableHeroes` (`STU_5427ADC1` {0x62E537BD skin themes[]})
  - **0x33B0B2B6 `m_team` (TeamIndex)**
  - three ints
- `TeamIndex` enum: TeamBlue = 0, TeamRed = 1, 2, 3, FFA = 4, 5, plus aliases ([B/TankLib/STU/Types/Enums/TeamIndex.cs](https://github.com/overtools/OWLib/blob/243caa939efacc28eab7af8e8944f89f123b586b/TankLib/STU/Types/Enums/TeamIndex.cs)).
- Also present: `STUGameRulesetTeam` (0x87C00EC0), `STUCriteria_Team` (0xBDD783B9 {`m_team`}), and many ConfigVar types with `m_team` / `m_filter` fields (e.g. EntityID-filter config vars).
- `STUMapHeader` (0x02514B6A): 0x4E87690F `m_map`, 0x38F33424 `m_baseMap`, 0xD608E9F3 `m_supportedGamemodes`, loading-screen refs, 0x1DD3A0CD `m_mapType`.

**Beta runtime FilterBits/PlayerInfo** (project fork; [player_spawner.cpp](https://github.com/p3n1cillin/ow1-preservation/blob/main/prometheus/player_spawner.cpp) ~lines 58-78; [entity_admin.h](https://github.com/p3n1cillin/ow1-preservation/blob/main/prometheus/entity_admin.h) ~lines 191-230)
- `Component_3F_PlayerInfo` sets:
  - `hero_select_enabled`, `hero_was_selected`
  - `m_slot = 3`
  - `selected_heroid`
  - `localplayer_heroselected`
- `Component_10_FilterBits` layout:
  - `pre_filter_bits` at +0x90, `filter_bits` at +0x98
  - team bits: team 0 = 0x40000, 1 = 0x80000, 2 = 0x100000, 3 = 0x200000 (mask 0x3C0000)
  - spectator setter: +0x8C = 0x101, +0x8E = 1, `pre_filter_bits` 0x400001
- Note: the spawner calls `set_team(team)` and then assigns `filter_bits = 0x800000`, which **overwrites** the team bits before `FilterBitsMakeFinal()`. This is beta (fixed-offset) code, not 1.74.

### Inferences
- `STUGameModeTeam.m_controllerScript` / `m_bodyScript` hashes equal the project's Practice-mode references 0x0c90 (a2781aa4) and 0x0c8e (76e8c82a). That suggests 0x0c90 is the per-player **controller** script and 0x0c8e the hero **body** script for the mode's team. Similarly, `STUGameMode.m_CF63B633` -> 0x13c0 is the **game-mode** script. This confirms the project's role assignment from authored data.
- The project found component 74 field 2 = team. In 1.74 the replicated team (and probably filter bits) is likely carried in that kind of runtime component state. Expect it to need values consistent with `TeamIndex` (0/1, or 4 for FFA). Practice Range's `STUGameModeTeam` entries (team index plus `m_availableHeroes`) are worth reading offline to choose the team value.

### Gaps
- No STU type for the "skin" runtime component. Skin application in authored data is only `STUSkinBase.m_runtimeOverrides` (GUID remaps) plus `m_teamColor`.
- The 1.74 runtime ids and layouts of FilterBits/PlayerInfo are not public. Prometheus offsets are beta-only.

## Q5. Version mapping and hash-name resources

### Takeaway
- Use OWLib branch `ow1` @ 243caa9 or `overwatch/1.74` @ 7afe5f5 for OW1. Their STU types date from the 2022-01-01 regeneration.
- `develop` from about Oct 2022 onward (e.g. b5d1d6f "update STU" 2022-10-10, 7f7b0b1 "2.1.1.0.106617 stu update" 2022-10-26, fb62363 "Update STU for 2.2.0.2.107804") is OW2.
- Name lists: `TankLibHelper/DataPreHashChange/*.csv` hold beta-era CRC names; `TankLibHelper/Data/Known*.csv` and `RegisteredSTUTypes.json` hold current names; `DataTool/Static/GUIDNames.csv` names GUIDs.

### Cited Findings
- OW1 update commits on develop: a7c0e78 "Update for Overwatch 1.70.0.0.94910" (2022-03-16), e23091f 1.71.0.0.96081, 3874257 1.72.0.0.98315, c0275b1 1.72.1.0.99843, 22f568f 1.72.1.0.100672, f95d5bf 1.72.2.0.101600 (2022-07-20), 3b00642 "1.74" (2022-09-07). These commits update TACTLib and the keyring rather than STUs (`git log` of [OWLib](https://github.com/overtools/OWLib/commits/develop); [3b00642](https://github.com/overtools/OWLib/commit/3b006420529554fd012e9efa1f998ab05c2c4aff)).
- Branches: `ow1` head [243caa9](https://github.com/overtools/OWLib/tree/243caa939efacc28eab7af8e8944f89f123b586b) (2022-10-21 "sync formats"); `overwatch/1.74` head [7afe5f5](https://github.com/overtools/OWLib/tree/7afe5f52706e7002ed8c2717299cd60846f3fa3a); also `overwatch/1.14` exists. Last OW1-line STU type change: c60c470 "regen stus" / 0d17c0a "reformat files" (2022-01-01). 7477f57 "tank: update STUs" (2022-04-23) is not on the OW1 line.
- The `ow1` branch has 558 type files (about 5,255 classes, mostly in `Misc*.cs`). The OW2 develop head has 468 files.
- Name resources:
  - `TankLibHelper/DataPreHashChange/KnownTypes.csv` (915 lines) and `KnownFields.csv` (1,275 lines): beta-era hashes and names, e.g. `A1815CAB, STUChildEntityDefinition`; `3B6EE2B7, m_childEntityData`; `DA37BCF8, m_hardPoint`. These hashes differ from retail instance hashes (retail `STUChildEntityDefinition` = 0x1D9159F2) ([KnownTypes.csv](https://github.com/overtools/OWLib/blob/243caa939efacc28eab7af8e8944f89f123b586b/TankLibHelper/DataPreHashChange/KnownTypes.csv), [KnownFields.csv](https://github.com/overtools/OWLib/blob/243caa939efacc28eab7af8e8944f89f123b586b/TankLibHelper/DataPreHashChange/KnownFields.csv)).
  - `TankLibHelper/Data/KnownTypes.csv` (471) / `KnownFields.csv` (525) / `RegisteredSTUTypes.json` (hash, parent hash, fields with type hash, serialization type, size, offset) ([B/TankLibHelper/Data](https://github.com/overtools/OWLib/tree/243caa939efacc28eab7af8e8944f89f123b586b/TankLibHelper/Data)).
  - `DataTool/Static/GUIDNames.csv` (GUID index, type, name) ([D/DataTool/Static/GUIDNames.csv](https://github.com/overtools/OWLib/blob/546efa19516d7df7ba138802d221c73ad886df28/DataTool/Static/GUIDNames.csv)).
- A debug tool `ExtractSTUType.cs` exists in `DataTool/ToolLogic/Extract/Debug` (B tree).
- The 2025 CCC talk "Prometheus: Reverse-Engineering Overwatch" is described as covering STU and the ECS on the first archived build ([CCC fahrplan](https://fahrplan.events.ccc.de/congress/2025/fahrplan/event/prometheus-reverse-engineering-overwatch); [CCC hub](https://events.ccc.de/congress/2025/hub/en/event/detail/prometheus-reverse-engineering-overwatch)). I did not review the talk's content beyond the search summary.

### Inferences
- `RegisteredSTUTypes.json` in the OW1 branch carries per-field serialization type and size for every type. It is the best public machine-readable schema for writing an independent STU reader. The project should still regenerate or verify against 104319's own reflection tables, given the Jan-2022 provenance.

### Gaps
- No public "overwatch-stu-names"-style repo beyond OWLib was found. Two web searches returned unrelated results.
- I did not verify whether TACTLib's 1.74 support changes any STU-relevant behaviour. Its role is CASC/TACT access, not STU semantics.
