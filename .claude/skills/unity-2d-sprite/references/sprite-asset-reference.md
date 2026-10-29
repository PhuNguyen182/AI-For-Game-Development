# Sprite Asset Data and Placeholders

Page: https://docs.unity3d.com/Manual/class-Sprite.html

Some `Sprite` members describe the original texture, others the current one; for an atlas-packed sprite these differ, so wrong choices work in the Editor and throw once packing is on.

| Member | Note |
|---|---|
| `rect` | Location on the **original** texture; stable under packing, the default choice |
| `textureRect`, `textureRectOffset` | Location on the **current** texture; `textureRect` throws for a tightly packed sprite. Guard with `packed` / `packingMode` / `packingRotation` |
| `texture` | Atlas texture when packed, source otherwise |
| `bounds` | World-space centre and extents with pivot and PPU applied; use instead of deriving from `rect` and `pixelsPerUnit` |
| `pixelsPerUnit`, `pivot`, `border` | Import-time values |
| `triangles`, `uv`, `vertices` | Copies of the render mesh (reflects Custom Outline); each access copies, so cache |
| `spriteAtlasTextureScale` | Resolution scale when resolved through a Variant |
| `associatedAlphaSplitTexture` | Separate alpha texture forced by ETC1 (no alpha channel); a mobile-only second texture to count in memory budgets |
| `GetPhysicsShapeCount()`, `GetPhysicsShape(int, List<Vector2>)`, `GetPhysicsShapePointCount(int)` | Read the authored collision outlines; reuse the caller-owned list; point count sizes a buffer |
| `Sprite.Create(...)` | Runtime sprite for procedural content only; the caller owns the result |
| `OverrideGeometry(...)`, `OverridePhysicsShape(...)` | Replace mesh/collision at runtime, bypassing Sprite Editor data; an escape hatch |

## Placeholder sprites

GameObject > 2D Object > Sprites (2D Sprite package; the shape list varies by Editor version, read the live menu) creates a GameObject with a `SpriteRenderer` using a generated white primitive. Page: https://docs.unity3d.com/Manual/sprite/placeholder/placeholder-landing.html

- No texture backs it, so it cannot be opened in the Sprite Editor: no slicing, outline, physics shape or border.
- Swapping in final art is a reassignment of the renderer's Sprite; sorting, colliders and animation bindings survive.
- The swap carries no import decisions (PPU, Mesh Type, pivot, physics shape): a blockout scene changes size when real art lands at a different PPU, so run import-settings.md then.
