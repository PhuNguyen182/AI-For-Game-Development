# Sprite Asset Reference

Sources: https://docs.unity3d.com/Manual/class-Sprite.html, `UnityEngine.Sprite` scripting API

## Inspector (on the sprite sub-asset itself)

| Property | Description |
|---|---|
| Name | The sprite's identifier — becomes its asset name (also settable per sub-sprite in the [Sprite Editor's slicing panel](sprite-editor.md)). |
| Pivot | Normalized (0,0 bottom-left to 1,1 top-right) transform origin used for rotation/scaling. |
| Border (L/R/T/B) | The 9-slice border in pixels — see [nine-slicing.md](nine-slicing.md). |

## Scripting API surface

| Member | Description |
|---|---|
| `texture` | The underlying `Texture2D` — points at the atlas texture if packed, the source texture otherwise. |
| `textureRect` | The sprite's rectangle on its texture, in pixels — throws if the sprite is tightly packed in an atlas (tight-packed sprites don't have a simple rect). |
| `textureRectOffset` | Offset of `textureRect` relative to the sprite's original (unpacked) bounds. |
| `rect` | The sprite's location on its *original* source texture, in pixels — stable regardless of atlas packing. |
| `pivot` | Pivot location in pixels on the original texture (Inspector's `Pivot` expressed in pixel space). |
| `pixelsPerUnit` | The sprite's Pixels Per Unit value — see [import-settings.md](import-settings.md). |
| `border` | The 9-slice border, as a `Vector4` (L, B, R, T). |
| `bounds` | World-space bounds (center + extents) — useful for camera framing/culling math without hand-deriving it from `rect`/`pixelsPerUnit`. |
| `packed`, `packingMode`, `packingRotation` | Whether/how the sprite is packed into a [Sprite Atlas](sprite-atlas.md). |
| `triangles`, `uv`, `vertices` | Copies of the render mesh's triangle indices, UVs, and vertex positions — reflects whatever [Custom Outline](custom-outline.md) authored. |
| `associatedAlphaSplitTexture` | The separate alpha-channel texture for ETC1-compressed sprites (ETC1 doesn't support alpha directly, so Unity splits it into a second texture). |
| `spriteAtlasTextureScale` | The resolution scale applied if this sprite came from a [Variant atlas](sprite-atlas.md). |
| `blendShapeCount` | Blend shape count — only relevant to 2D Animation package content, out of scope for this skill. |
| `GetPhysicsShapeCount()` / `GetPhysicsShape(int index, List<Vector2> buffer)` | Reads however many [Custom Physics Shape](custom-physics-shape.md) outlines are stored on the sprite. |
| `GetPhysicsShapePointCount(int index)` | Vertex count for a specific physics shape. |
| `Create(...)` | Builds a `Sprite` at runtime from a `Texture2D`/rect/pivot — used for procedurally-generated sprite content rather than an imported asset. |
| `OverrideGeometry(...)` / `OverridePhysicsShape(...)` | Replaces the sprite's render mesh / physics shape at runtime — an advanced, infrequently-needed override; prefer authoring geometry in the Sprite Editor modules for anything that isn't genuinely procedural. |

## Practical guidance

- Use `rect` (original-texture-space, always valid) over `textureRect` (atlas-packed-space, throws when tightly packed) unless code specifically needs the packed texture's actual UV layout.
- `bounds` already accounts for `pixelsPerUnit` and pivot — don't hand-recompute world-space size from `rect`/`pixelsPerUnit` when `bounds` already gives the answer.
- `Sprite.Create`/`OverrideGeometry`/`OverridePhysicsShape` are runtime-procedural escape hatches — reach for them only when a sprite's shape is genuinely generated at runtime (e.g. a procedurally-cut texture atlas region), not as a substitute for authoring shape data in the Sprite Editor for ordinary imported art (YAGNI in `coding-principles.md`).
