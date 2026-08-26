# Text & Fonts — TextField, Rich Text, Font Assets

Sources: [Work with text](https://docs.unity3d.com/Manual/UIE-work-with-text.html), [TextField element](https://docs.unity3d.com/Manual/UIE-uxml-element-TextField.html), [Style text (Builder)](https://docs.unity3d.com/Manual/UIB-styling-ui-text.html), [Auto-sizing text elements](https://docs.unity3d.com/Manual/ui-systems/auto-sizing-text-elements.html), [Supported rich text tags](https://docs.unity3d.com/Manual/UIE-supported-tags.html), [Font assets](https://docs.unity3d.com/Manual/UIE-font-asset.html), [Migrate static font assets](https://docs.unity3d.com/Manual/ui-systems/migrate-static-font-assets.html), [Fallback fonts](https://docs.unity3d.com/Manual/UIE-fallback-font.html).
Covers: SKILL.md §4 — **"Author text with dynamic SDF font assets, never a static/bitmap asset"**.

Text elements, rich text markup, and the two font-asset technologies —
dynamic (SDF) versus bitmap — with the one deprecation that actually blocks
existing projects on the modern text renderer.

## TextField behavior

| Attribute | Effect | Source |
|---|---|---|
| `multiline` | Default is single-line; set `true` for multi-line input | [TextField element](https://docs.unity3d.com/Manual/UIE-uxml-element-TextField.html) |
| `maxLength` | Character-count cap | [TextField element](https://docs.unity3d.com/Manual/UIE-uxml-element-TextField.html) |
| `password` | Masks characters with a configurable mask character | [TextField element](https://docs.unity3d.com/Manual/UIE-uxml-element-TextField.html) |
| `is-delayed` | Defers value commit to Enter or focus loss instead of per-keystroke | [TextField element](https://docs.unity3d.com/Manual/UIE-uxml-element-TextField.html) |
| `textEdition.placeholder` | Placeholder text; **hidden the instant a non-empty `value` is set** | [TextField element](https://docs.unity3d.com/Manual/UIE-uxml-element-TextField.html) |
| `verticalScrollerVisibility` | Must be set explicitly — a multiline field does **not** get a scrollbar automatically | [TextField element](https://docs.unity3d.com/Manual/UIE-uxml-element-TextField.html) |
| Text-related USS properties | `-unity-font-style`, `font-size`, etc. propagate to child elements — unlike most other USS properties, per [uss-styling-and-layout.md](uss-styling-and-layout.md) | [Style text (Builder)](https://docs.unity3d.com/Manual/UIB-styling-ui-text.html) |

## Auto-sizing text

| Subject | What it decides | Source |
|---|---|---|
| `-unity-text-auto-size` | Syntax `-unity-text-auto-size: best-fit <minSize> <maxSize>;` — the only documented mode is `best-fit`; scales font size within the range based on available space, compatible with wrapping/ellipsis/alignment | [Auto-sizing text elements](https://docs.unity3d.com/Manual/ui-systems/auto-sizing-text-elements.html) |

## Rich text tags

| Subject | What it decides | Source |
|---|---|---|
| Supported set | 35 tags: `<a>`, `<align>`, `<allcaps>`, `<alpha>`, `<b>`, `<br>`, `<color>`, `<cspace>`, `<font>`, `<font-weight>`, `<gradient>`, `<i>`, `<indent>`, `<line-height>`, `<line-indent>`, `<lowercase>`, `<margin>`, `<mark>`, `<mspace>`, `<nobr>`, `<noparse>`, `<pos>`, `<s>`, `<size>`, `<smallcaps>`, `<space>`, `<sprite>`, `<style>`, `<sub>`, `<sup>`, `<u>`, `<uppercase>`, `<voffset>`, `<width>`, `<link>` | [Supported rich text tags](https://docs.unity3d.com/Manual/UIE-supported-tags.html) |
| `<align flush>` gotcha | Not supported by the **Advanced Text Generator** (the current default) even though `left`/`center`/`right`/`justified` are | [Supported rich text tags](https://docs.unity3d.com/Manual/UIE-supported-tags.html) |

## Font assets — dynamic (SDF) vs bitmap

| Subject | What it decides | Source |
|---|---|---|
| Dynamic font assets | Start with an empty atlas; glyphs are added on demand as text uses them | [Font assets](https://docs.unity3d.com/Manual/UIE-font-asset.html) |
| Dynamic OS font assets | Reference an OS-installed font file instead of a project source font, shrinking build size | [Font assets](https://docs.unity3d.com/Manual/UIE-font-asset.html) |
| Bitmap (static) font assets | Pre-rendered at creation time (SMOOTH/RASTER/COLOR); pixel-aligned, so it becomes jagged/blurry under scaling or rotation | [Font assets](https://docs.unity3d.com/Manual/UIE-font-asset.html) |
| SDF rendering | Stores per-texel contour-distance data, so edges stay smooth regardless of camera distance — why dynamic assets scale better than bitmap | [Font assets](https://docs.unity3d.com/Manual/UIE-font-asset.html) |
| Recommended SDF mode by use | **SDFAA** default (fastest to generate); best-practice split: SDFAA for input fields, SDF16 for labels, SDF32 for titles | [Font assets](https://docs.unity3d.com/Manual/UIE-font-asset.html) |
| Atlas sizing | `512×512` for ASCII-only sets; enable Multi Atlas Textures for large sets (CJK); keep roughly a 1:10 sampling-to-padding ratio | [Font assets](https://docs.unity3d.com/Manual/UIE-font-asset.html) |
| Atlas memory cost | A 1024×1024 atlas is ≈1 MB; a 2048×2048 CJK-covering atlas is ≈4 MB | [Migrate static font assets](https://docs.unity3d.com/Manual/ui-systems/migrate-static-font-assets.html) |
| Legacy `Font` field | Using a legacy `Font` object directly requires explicitly setting the Font Asset field to **None** | [Font assets](https://docs.unity3d.com/Manual/UIE-font-asset.html) |

**Critical caveat**: the default **Advanced Text Generator does not support
static (bitmap) font assets** — an existing project still on them must
migrate before text renders correctly. Three documented paths: rebuild as a
dynamic asset (subset the source font to keep the memory footprint down),
pre-populate a dynamic asset's atlas via Font Asset Creator to preserve
first-frame performance (often unnecessary once SDFAA is in use), or swap in
the original `.ttf`/`.otf` directly and lose prior customization. See
[Migrate static font assets](https://docs.unity3d.com/Manual/ui-systems/migrate-static-font-assets.html).

## Fallback fonts

| Subject | What it decides | Source |
|---|---|---|
| Resolution order for a missing glyph | (1) local element-level fallback list → (2) global fallback list (UITK Text Settings asset) → (3) default sprite asset → (4) Dynamic OS fallback → (5) missing-glyph placeholder | [Fallback fonts](https://docs.unity3d.com/Manual/UIE-fallback-font.html) |
| Use case | Covering large-alphabet scripts (CJK) or special characters outside the primary font | [Fallback fonts](https://docs.unity3d.com/Manual/UIE-fallback-font.html) |
| Cost | Each fallback lookup adds computation and can add draw calls — keep fallback fonts visually consistent with the primary one | [Fallback fonts](https://docs.unity3d.com/Manual/UIE-fallback-font.html) |
