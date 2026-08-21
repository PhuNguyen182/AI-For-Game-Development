# Sprite Texture Import Settings — Texture Type, Sprite Mode, PPU, Mesh Type

Sources: [Import images as sprites](https://docs.unity3d.com/Manual/sprite/import-images-sprites/import-images-sprites-landing.html), [Sprite (2D and UI) import settings reference](https://docs.unity3d.com/Manual/texture-type-sprite.html).
Covers: SKILL.md §4 — **"Settle Pixels Per Unit against the existing visual set before anything else"**, **"Pick Mesh Type by whether the sprite is 9-sliced, not by overdraw instinct"**.

Import settings are asset metadata, not scene state: they decide the sprite's
world size, its mesh, and the collision outline every instance inherits, so
they are settled before any component is wired. Setting **Texture Type** to
**Sprite (2D and UI)** is what exposes everything below. Compression and Max
Size decisions follow `performance-and-algorithms.md`'s Assets & memory
footprint section.

## Geometry and scale

| Setting | What it decides | Source |
|---|---|---|
| Sprite Mode | **Single** (whole texture is one sprite), **Multiple** (spritesheet cut in the Sprite Editor), **Polygon** (clipped to a custom polygon). Multiple is the only mode with per-sub-sprite rects, pivots, and borders | [Sprite import settings](https://docs.unity3d.com/Manual/texture-type-sprite.html) |
| Pixels Per Unit | Texture pixels per Unity world unit — sets both rendered world size and the scale of the sprite-derived physics shape, so a mismatch inside one visual set is an art bug and a hitbox bug at once | [Sprite import settings](https://docs.unity3d.com/Manual/texture-type-sprite.html) |
| Mesh Type | **Full Rect** is a plain quad and is mandatory for 9-slicing; **Tight** builds a mesh from the alpha shape to cut overdraw but cannot 9-slice. Unity forces Full Rect on any sprite under 32×32 regardless of this setting, so Tight is inert on small icons | [Sprite import settings](https://docs.unity3d.com/Manual/texture-type-sprite.html) |
| Extrude Edges | Pixels of padding around the generated mesh — raises it when a filtered or scaled sprite shows bleeding at its edge | [Sprite import settings](https://docs.unity3d.com/Manual/texture-type-sprite.html) |
| Pivot | Rotation/scale origin, preset or Custom X/Y. Single mode only — Multiple mode sets pivot per sub-sprite in the Sprite Editor | [Sprite import settings](https://docs.unity3d.com/Manual/texture-type-sprite.html) |
| Generate Physics Shape | Auto-traces a default collision outline from opaque pixels when no Custom Physics Shape was authored — leave off for purely decorative sprites, which otherwise carry outline data nothing reads. See [custom-physics-shape.md](custom-physics-shape.md) | [Create collision shapes](https://docs.unity3d.com/Manual/sprite/create-collision-geometry.html) |
| Open Sprite Editor | Opens the four authoring modules; requires the 2D Sprite package. See [sprite-editor.md](sprite-editor.md) | [Cut out sprites from a texture](https://docs.unity3d.com/Manual/sprite/sprite-editor/use-editor.html) |

## Colour and alpha

| Setting | What it decides | Source |
|---|---|---|
| sRGB (Color Texture) | On for anything meant to look correct on screen; off for a texture storing exact linear values (mask, data) — leaving it on silently gamma-shifts those values | [Sprite import settings](https://docs.unity3d.com/Manual/texture-type-sprite.html) |
| Alpha Source | **None**, **Input Texture Alpha**, or **From Gray Scale** — where alpha comes from when the source format has none | [Sprite import settings](https://docs.unity3d.com/Manual/texture-type-sprite.html) |
| Alpha Is Transparency | Dilates edge colour into transparent pixels; the fix for dark fringing on a filtered or scaled sprite | [Sprite import settings](https://docs.unity3d.com/Manual/texture-type-sprite.html) |

## Memory and platform

| Setting | What it decides | Source |
|---|---|---|
| Read/Write | Enables CPU pixel access and doubles the texture's memory — on only when a script genuinely reads pixels at runtime | [Sprite import settings](https://docs.unity3d.com/Manual/texture-type-sprite.html) |
| Generate Mip Maps | Wanted only when the sprite is scaled significantly in perspective; mipmapping pixel art at a fixed scale blurs it and costs a third more memory | [Sprite import settings](https://docs.unity3d.com/Manual/texture-type-sprite.html) |
| Filter Mode | **Point** for crisp pixel art, **Bilinear**/**Trilinear** for smooth-scaled art — Point is what keeps a pixel-art project from looking soft at non-integer scales | [Sprite import settings](https://docs.unity3d.com/Manual/texture-type-sprite.html) |
| Wrap Mode | Repeat/Clamp/Mirror, per-axis — matters for Tiled Draw Mode sprites, see [nine-slicing.md](nine-slicing.md) | [Sprite import settings](https://docs.unity3d.com/Manual/texture-type-sprite.html) |
| Non-Power of 2 | How NPOT dimensions are handled (scale up, pad, none) — relevant where the target platform's compression format requires POT | [Sprite import settings](https://docs.unity3d.com/Manual/texture-type-sprite.html) |
| Max Size / Format / Compression / Compressor Quality | The single largest lever on sprite memory footprint; set per platform, never left at one global default for both a PC and a mobile target | [Sprite import settings](https://docs.unity3d.com/Manual/texture-type-sprite.html) |
| Platform-specific overrides | A per-target tab overriding Max Size/Format/Compression without touching the default — the mechanism the rule above is applied through | [Sprite import settings](https://docs.unity3d.com/Manual/texture-type-sprite.html) |

**Critical caveat**: Pixels Per Unit is not a cosmetic scale knob. Because the
physics shape is expressed in the same units, changing PPU after colliders are
tuned rescales every hitbox derived from that sprite.
