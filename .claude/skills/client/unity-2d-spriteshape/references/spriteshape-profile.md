# Sprite Shape Profile (`SpriteShape` asset)

Sources: https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/manual/SSProfile.html, `UnityEngine.U2D.SpriteShape`/`AngleRange`/`CornerSprite`/`Corner`/`CornerType` scripting API.

A **Sprite Shape Profile** is the `ScriptableObject` asset (type `SpriteShape`) that defines *which sprites render at which outline angle* — the paint palette a `SpriteShapeController`'s spline draws from. Create one via **Assets > Create > Sprite Shape Profile**, choosing an **Open Shape** or **Closed Shape** preset as the starting point.

- **Open Shape** — the outline has distinct start/end points (a platform edge, a rope); no fill geometry.
- **Closed Shape** — the outline loops back on itself (a pond, an island); the interior is filled with `fillTexture`.

## Angle Ranges

An Angle Range assigns a pool of sprites to a span of outline angles — as a spline segment's angle relative to the shape changes, Unity picks the sprite from whichever Angle Range covers that angle.

| Inspector field | Scripting API member | Description |
|---|---|---|
| Start (degrees) | `AngleRange.start` | Starting angle for the range, in degrees. |
| End (degrees) | `AngleRange.end` | Ending angle for the range, in degrees. Angle Ranges must not overlap with each other. |
| Order | `AngleRange.order` | Display/render priority when multiple sprites could apply at an intersection. |
| Sprites | `AngleRange.sprites` (`List<Sprite>`) | The sprite pool for this range; the first sprite in the list is the default. A control point's `spriteIndex` (see [spriteshape-controller.md](spriteshape-controller.md)) selects which sprite in this list renders at that point. |

Workflow: **Creating Angle Ranges** (define the angle spans first) → **Assigning Sprites** (drag sprites into each range's pool) → **Previewing Sprites of multiple Angle Ranges** (the Profile Inspector renders a live preview as ranges/sprites change).

## Fill (closed shapes)

| Inspector field | Scripting API member | Description |
|---|---|---|
| Use Sprite Borders | `SpriteShape.useSpriteBorders` | Draws the Sprite's 9-slice borders at each control point instead of stretching the whole sprite. |
| Texture (Fill) | `SpriteShape.fillTexture` | The `Texture2D` tiled across the shape's interior; should use Repeat wrap mode. |
| Offset | `SpriteShape.fillOffset` | Border offset applied at the fill texture's edges. |

## Corner Sprites

`CornerSprite` associates a `CornerType` (`InnerBottomLeft`/`InnerBottomRight`/`InnerTopLeft`/`InnerTopRight`/`OuterBottomLeft`/`OuterBottomRight`/`OuterTopLeft`/`OuterTopRight`) with a sprite pool, so a 90°-ish corner in the outline renders a purpose-made corner sprite instead of stretching an edge sprite around the bend. `SpriteShape.cornerSprites` (`List<CornerSprite>`) holds the configured set.

Whether a given control point actually uses a corner sprite is controlled per-point by the `Corner` enum (`Automatic`/`Disable`/`Stretched`) — see [spriteshape-controller.md](spriteshape-controller.md)'s `SplineControlPoint.cornerMode`.

Note: the fetched Manual page (`SSProfile.html`) documents Angle Ranges and the Fill fields in detail but does not spell out the exact Corner Sprites Inspector UI (button labels, list layout) — the fields/API above are sourced from the Scripting API instead. Verify the exact Inspector control layout against the live Editor before writing step-by-step UI instructions for it.

## Sprite import requirements

Any sprite used in an Angle Range or Corner Sprite pool must be imported with (per the package manual's landing page):
- **Texture Type** = Sprite (2D and UI)
- **Sprite Mode** = Single
- **Mesh Type** = Full Rect

If the sprite lives in a Sprite Atlas, disable **Allow Rotation** and **Tight Packing** on that atlas — both distort the border data Sprite Shape relies on to tile correctly. Route the actual import-settings work to the sibling `unity-2d-sprite` skill; this skill only states the constraint.

## Practical guidance

- Keep Angle Ranges non-overlapping and ordered by ascending angle — an accidental overlap silently makes sprite selection ambiguous at the boundary, per the Manual's own "Angles cannot overlap with others" constraint on `AngleRange.end`.
- Reuse one Profile across every `SpriteShapeController` that should look the same (e.g. all "grass platform" edges) rather than duplicating Angle Range/Corner Sprite setup per instance — the Profile is the shared palette, the spline on each `SpriteShapeController` is the per-instance shape.
- Don't encode a gameplay decision (which terrain type is "safe" vs. "hazard") into which Profile is assigned — that's Shared Core state; the Profile only controls how a shape *looks*, per `coding-principles.md`'s Shared Core integrity rule.
