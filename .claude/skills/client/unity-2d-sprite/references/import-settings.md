# Sprite Texture Import Settings

Sources: https://docs.unity3d.com/Manual/sprite/import-images-sprites/import-images-sprites-landing.html, https://docs.unity3d.com/Manual/texture-type-sprite.html

## Enabling a texture as a sprite

Select the imported texture in the Project window, and in the Inspector set **Texture Type** to **Sprite (2D and UI)**. This exposes the sprite-specific import settings below in place of the generic texture settings.

## Core sprite settings

| Setting | Values / description |
|---|---|
| Sprite Mode | **Single** — the whole texture is one sprite. **Multiple** — the texture is a spritesheet cut into multiple sub-sprites via the Sprite Editor. **Polygon** — the sprite is clipped to a custom polygon outline. |
| Pixels Per Unit | How many texture pixels map to one Unity world-space unit. Drives both the sprite's rendered world size and its default physics shape scale. |
| Mesh Type | **Full Rect** — a simple quad covering the whole sprite rect; required for 9-sliced sprites and any sprite under ~32×32 px (Unity forces Full Rect below that size regardless of the setting). **Tight** — a mesh generated from the sprite's alpha shape, reducing overdraw on irregular sprites but incompatible with 9-slicing. |
| Extrude Edges | Padding (in pixels) added around the generated mesh, to avoid texture bleeding at the sprite's edges when filtered/scaled. |
| Pivot | The transform origin used for rotation/scaling. Preset options (Center, corners, edge midpoints) or **Custom** with explicit X/Y (Single mode only — Multiple mode sets pivot per sub-sprite in the Sprite Editor). |
| Generate Physics Shape | When enabled, Unity auto-generates a default physics shape from the sprite's opaque-pixel outline if no custom physics shape was authored in the Sprite Editor's Custom Physics Shape module. See [custom-physics-shape.md](custom-physics-shape.md). |
| Open Sprite Editor | Button that opens the Sprite Editor for this texture (requires the 2D Sprite package). See [sprite-editor.md](sprite-editor.md). |

## Color / alpha settings

| Setting | Description |
|---|---|
| sRGB (Color Texture) | Import in gamma space for a color texture; disable for a texture that must store exact linear values (e.g. a mask or data texture, not something meant to look "correct" on screen). |
| Alpha Source | **None**, **Input Texture Alpha**, or **From Gray Scale** — where the sprite's alpha channel comes from. |
| Alpha Is Transparency | Dilates edge colors into fully-transparent pixels to prevent dark fringing when the sprite is filtered/scaled. |

## Advanced / platform settings

| Setting | Description |
|---|---|
| Non-Power of 2 | How Unity handles NPOT texture dimensions (scale up, pad, or none, depending on target). |
| Read/Write | Enables CPU-side access via `Texture2D` script APIs; doubles the texture's memory footprint — leave off unless a script genuinely reads/writes pixel data at runtime. |
| Generate Mip Maps | Builds a mipmap chain — almost never wanted for 2D sprites viewed at a fixed pixel scale (mipmapping a pixel-art sprite blurs it); leave off unless the sprite is scaled significantly in 3D/perspective space. |
| Filter Mode | **Point (no filter)** for crisp pixel-art sprites, **Bilinear**/**Trilinear** for smooth-scaled art. |
| Wrap Mode | Repeat / Clamp / Mirror / Mirror Once / per-axis — matters mainly for Tiled-draw-mode sprites (see [nine-slicing.md](nine-slicing.md)). |
| Max Size / Format / Compression / Compressor Quality | Standard texture compression controls — set deliberately per platform per `performance-and-algorithms.md`'s "Assets & memory footprint" rule; an oversized or uncompressed sprite texture is a common source of both load-time and runtime memory bloat, especially on mobile. |
| Platform-specific overrides | A per-platform tab to override Max Size/Format/Compression for a specific build target without changing the default settings. |

## Practical guidance

- Pick **Sprite Mode = Multiple** the moment a texture is a spritesheet (animation frames, a tile/icon sheet) — don't hand-slice separate texture assets when one spritesheet plus the Sprite Editor's slicing tools does the job.
- Set **Pixels Per Unit** consistently across a project's sprites (or at least within one visual "set") — mismatched PPU between sprites that appear together produces inconsistent apparent scale.
- Only enable **Generate Physics Shape** when the sprite actually needs `Collider2D` collision derived from its silhouette; per `coding-principles.md`'s KISS principle, a sprite that's purely decorative doesn't need this on.
- Route final compression/Max Size decisions through per-platform overrides rather than a single global setting whenever PC and mobile targets have different memory budgets — this is the same "deliberate per-platform texture setting" rule `performance-and-algorithms.md` states for all textures, not something sprite import gets to skip.
