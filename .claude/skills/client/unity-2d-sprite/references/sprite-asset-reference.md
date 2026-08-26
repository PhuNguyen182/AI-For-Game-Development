# Sprite Asset — Runtime Data & Packing-Safe Members

Sources: [Sprite asset reference](https://docs.unity3d.com/Manual/class-Sprite.html), [Sprites](https://docs.unity3d.com/Manual/sprite/sprite-landing.html).
Covers: SKILL.md §4 — **"Read sprite data through the members that stay valid under packing"**.

Half of `Sprite`'s scripting surface describes the sprite on its *original*
texture and half describes it wherever it currently sits, which for an
atlas-packed sprite are different places. Choosing the wrong half produces
code that works in the Editor and throws once packing is enabled.

## Geometry and scale

| Member | What it decides | Source |
|---|---|---|
| `rect` | Location on the **original** source texture — stable regardless of atlas state, and therefore the default choice | [Sprite asset reference](https://docs.unity3d.com/Manual/class-Sprite.html) |
| `textureRect` | Location on the **current** texture — throws for a tightly packed atlas sprite, which has no simple rect | [Sprite asset reference](https://docs.unity3d.com/Manual/class-Sprite.html) |
| `textureRectOffset` | Offset of `textureRect` from the sprite's unpacked bounds | [Sprite asset reference](https://docs.unity3d.com/Manual/class-Sprite.html) |
| `texture` | The backing `Texture2D` — the atlas texture when packed, the source otherwise | [Sprite asset reference](https://docs.unity3d.com/Manual/class-Sprite.html) |
| `bounds` | World-space centre and extents, already accounting for pivot and PPU — use it instead of deriving size from `rect` and `pixelsPerUnit` by hand | [Sprite asset reference](https://docs.unity3d.com/Manual/class-Sprite.html) |
| `pixelsPerUnit`, `pivot`, `border` | The import-time values, readable at runtime — see [import-settings.md](import-settings.md) | [Sprite asset reference](https://docs.unity3d.com/Manual/class-Sprite.html) |
| `triangles`, `uv`, `vertices` | Copies of the render mesh, reflecting whatever [custom-outline.md](custom-outline.md) authored — each access copies, so cache rather than reading per frame | [Sprite asset reference](https://docs.unity3d.com/Manual/class-Sprite.html) |

## Packing and platform state

| Member | What it decides | Source |
|---|---|---|
| `packed`, `packingMode`, `packingRotation` | Whether and how the sprite is in an atlas — the guard to test before touching `textureRect` | [Sprite asset reference](https://docs.unity3d.com/Manual/class-Sprite.html) |
| `spriteAtlasTextureScale` | The resolution scale applied when the sprite resolved through a Variant atlas, see [sprite-atlas.md](sprite-atlas.md) | [Sprite asset reference](https://docs.unity3d.com/Manual/class-Sprite.html) |
| `associatedAlphaSplitTexture` | The separate alpha texture ETC1 compression forces, since ETC1 carries no alpha channel — a mobile-only second texture that is easy to forget in a memory budget | [Sprite asset reference](https://docs.unity3d.com/Manual/class-Sprite.html) |

## Physics shape and runtime construction

| Member | What it decides | Source |
|---|---|---|
| `GetPhysicsShapeCount()` / `GetPhysicsShape(int, List<Vector2>)` | Reads the outlines authored in [custom-physics-shape.md](custom-physics-shape.md); the list overload fills a caller-owned buffer, so reuse it rather than allocating per call | [Sprite asset reference](https://docs.unity3d.com/Manual/class-Sprite.html) |
| `GetPhysicsShapePointCount(int)` | Vertex count of one shape — the cheap way to size a buffer before reading | [Sprite asset reference](https://docs.unity3d.com/Manual/class-Sprite.html) |
| `Sprite.Create(...)` | Builds a sprite from a texture at runtime — for genuinely procedural content only, and the result is an object the caller now owns | [Sprite asset reference](https://docs.unity3d.com/Manual/class-Sprite.html) |
| `OverrideGeometry(...)` / `OverridePhysicsShape(...)` | Replaces mesh or collision data at runtime, bypassing everything authored in the Sprite Editor — an escape hatch, not a substitute for authoring | [Sprite asset reference](https://docs.unity3d.com/Manual/class-Sprite.html) |
