# Text and fonts

Sources: [Text](https://docs.unity3d.com/Manual/UIE-work-with-text.html), [TextField](https://docs.unity3d.com/Manual/UIE-uxml-element-TextField.html), [Auto-size](https://docs.unity3d.com/Manual/ui-systems/auto-sizing-text-elements.html), [Rich text](https://docs.unity3d.com/Manual/UIE-supported-tags.html), [Font assets](https://docs.unity3d.com/Manual/UIE-font-asset.html), [Migrate static](https://docs.unity3d.com/Manual/ui-systems/migrate-static-font-assets.html), [Fallback](https://docs.unity3d.com/Manual/UIE-fallback-font.html).

## TextField
- Single-line by default; `multiline` for more. A multiline field gets no scrollbar until `verticalScrollerVisibility` is set.
- `is-delayed` commits on Enter/focus loss instead of per keystroke; `maxLength`; `password` mask.
- `textEdition.placeholder` disappears as soon as a non-empty `value` is set.
- Font USS properties inherit to children (unlike most USS properties).
- `-unity-text-auto-size: best-fit <min> <max>;` is the only documented mode.

## Rich text
- 35 tags supported (`<b>`, `<color>`, `<size>`, `<sprite>`, `<link>`, `<noparse>`, ...); the Rich text page lists them.
- `<align flush>` is unsupported by the Advanced Text Generator (default), though `left`/`center`/`right`/`justified` work.

## Font assets
- Dynamic: empty atlas, glyphs added on demand. Dynamic OS font assets reference an OS font file to shrink the build.
- Bitmap (static): pre-rendered, pixel-aligned, jagged/blurry under scale or rotation.
- SDF stores contour distance, so edges stay smooth at any scale. SDFAA is the default (fastest to generate); split: SDFAA input fields, SDF16 labels, SDF32 titles.
- Atlas: 512×512 for ASCII; Multi Atlas Textures for large sets (CJK); keep about 1:10 sampling-to-padding. 1024² ≈ 1 MB, 2048² CJK ≈ 4 MB.
- A legacy `Font` object used directly needs the Font Asset field set to None.

**Static font assets are unsupported by the Advanced Text Generator**: existing ones must migrate. Three paths: rebuild as a dynamic asset (subset the source font); pre-populate a dynamic atlas in Font Asset Creator to keep first-frame performance (often unneeded with SDFAA); or swap in the original `.ttf`/`.otf` and lose customization.

## Fallback fonts
- Missing glyph resolution: element fallback list → global fallback list (UITK Text Settings asset) → default sprite asset → Dynamic OS fallback → placeholder.
- Each lookup adds cost and can add draw calls; keep fallbacks visually consistent.
