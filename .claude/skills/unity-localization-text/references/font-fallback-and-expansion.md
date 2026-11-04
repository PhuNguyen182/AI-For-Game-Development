# Font fallback and text expansion

Sources: TMP in uGUI 2.6.0 at https://docs.unity3d.com/Packages/com.unity.ugui@2.6/: [a] `manual/TextMeshPro/FontAssetsFallback.html`, [b] `manual/TextMeshPro/FontAssetsDynamicFonts.html`, [c] `api/TMPro.TMP_FontAsset.html`, [d] `api/TMPro.AtlasPopulationMode.html` (API pages read at 2.0). Localization `Docs:` base: [e] `manual/Pseudo-Localization.html`, [f] `manual/Pseudo-Localization-Methods.html`, which cites [g] https://www.andiamo.co.uk/resources/expansion-and-contraction-factors/.

## TMP fallback search order [a]

1. The text object's primary font asset
2. That asset's local fallback list (`fallbackFontAssetTable` [c]), recursively through each fallback's own list
3. The text object's sprite asset
4. The general fallback list in TMP Settings (applies to every font asset)
5. The default sprite asset
6. The default font asset
7. The missing-glyph character

**Caveat:** the search is recursive and visits each asset once even with circular references [a]. When two assets in the chain cover the same script, the first one found wins every glyph and the second atlas is dead memory.

## Font asset per script

| Subject | Fact that decides |
|---|---|
| `AtlasPopulationMode.Static` | Glyph set baked at authoring; nothing added at runtime. Fits a locale whose character set is known (Latin, Cyrillic, Greek) |
| `AtlasPopulationMode.Dynamic` | Starts empty, adds glyphs as used; its source font file ships in the build; costs more CPU than static [b]. Fits user-entered text and CJK |
| `AtlasPopulationMode.DynamicOS` | Exists in TMP 2.x [d]; behaviour and platform font choice → `unity:optimize-text-mesh-pro` |
| `isMultiAtlasTexturesEnabled` | Creates additional atlas textures as needed [c]: each new page is another full-size texture |
| Reset (dynamic asset) | Shrinks the asset to the glyphs current text objects use; an unused asset drops to a 0 × 0 atlas [b] |
| UI Toolkit text | Its own `FontAsset` and Text Settings fallback list, not `TMP_FontAsset`: `ui-toolkit` → `text-and-fonts.md` |

## Atlas memory per asset

Cost = width × height × bytes per pixel × pages. At 1 byte per pixel:

| Atlas | Memory per page |
|---|---|
| 512 × 512 | 0.25 MB |
| 1024 × 1024 | 1 MB |
| 2048 × 2048 | 4 MB |
| 4096 × 4096 | 16 MB |

The UI Toolkit Manual gives the same order (1024² ≈ 1 MB, 2048² CJK ≈ 4 MB, per `ui-toolkit` → `text-and-fonts.md`). A device number needs a Memory Profiler capture (`unity-profiler-diagnostics`).

## Pseudo-localization

| Subject | Fact that decides |
|---|---|
| Create | Assets > Create > Localization > Pseudo-Locale; set Source Locale (the table strings come from). Default methods: Accenter, Expander, Encapsulator [e] |
| Activate | Set `SelectedLocale` to the Pseudo-Locale: Locale Game View Menu in the Editor, or script [e] |
| Preserve Tags | Keeps rich-text tags intact for every later method: place it first [f] |
| Accenter | Accented replacements: exposes missing glyphs and text clipped in height [f] |
| Encapsulator | Brackets each string (`[ ]` by default): a missing or split bracket marks concatenation or truncation [f] |
| Character Substitutor | To Upper, To Lower, List, Map modes [f] |
| Expander | Pads by a multiplier of string length; default Location End; Minimum String Length wins when larger; 93 padding characters [f] |

Expander default rules [f]:

| Source length (chars) | Multiplier |
|---|---|
| 0–10 | 2 |
| 10–20 | 1 |
| 20–30 | 0.8 |
| 30–50 | 0.6 |
| 50–70 | 0.7 |
| 70+ | 0.3 |

## Expansion from English [f][g]

| Language | Change | Language | Change |
|---|---|---|---|
| German | +10% to +35% | Hindi | +15% to +35% |
| Polish | +20% to +30% | Portuguese | +15% to +30% |
| Spanish | +15% to +30% | Italian | +10% to +25% |
| French | +15% to +20% | Croatian | 15% |
| Russian | 15% | Czech, Greek | 10% |
| Danish | −10% to −15% | Korean | −10% to −15% |
| Norwegian | −5% to −10% | Swedish | −10% |
| Finnish | −25% to −30% | Japanese | −10% to −55% |

**Caveat:** these are averages over running text; short labels expand far more, which is why the Expander doubles strings under 10 characters. Size containers from the Expander pass, not from this table.

Unverified: TMP SDF atlases as Alpha8 (1 byte per pixel) and colour-glyph (emoji) atlases as RGBA32 (4 bytes, 4× the table); whether a dynamic atlas keeps a CPU-readable copy that doubles its cost; whether a Pseudo-Locale works in a player build; `Clear Dynamic Data On Build` appears in `unity:optimize-text-mesh-pro` but not on the TMP 2.x API page.
