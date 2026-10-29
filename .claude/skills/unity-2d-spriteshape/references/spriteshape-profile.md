# Sprite Shape Profile

Sources: `manual/SSProfile.html` (profile), `manual/index.html` (index), `api/UnityEngine.U2D.SpriteShape.html`, `.AngleRange.html`, `.CornerSprite.html`, `.Corner.html`.

A Profile (`SpriteShape` ScriptableObject, **Assets > Create > Sprite Shape Profile**) maps outline angle to sprite and is shared by every controller that should look alike.

## Topology (profile)
- Open Shape: distinct start and end (platform edge, rope). No fill geometry, so Fill settings are inert.
- Closed Shape: the outline loops (pond, island); the interior fills from `fillTexture`, the only way to get a filled body.

## Angle Ranges
- Start/End (`AngleRange.start`, `.end`): ranges must not overlap (ambiguous exactly where shapes bend). An angle no range covers has no sprite. Author against the angles the outlines will produce, then check the Inspector's live preview.
- Order (`AngleRange.order`): render priority where sprites from different ranges meet.
- Sprites (`AngleRange.sprites`): the first entry is the default; a control point's `spriteIndex` picks another.

## Corner Sprites
- `CornerSprite` pairs a sprite pool with one of eight `CornerType`s, `InnerBottomLeft` through `OuterTopRight`, so a sharp bend uses purpose-made art instead of a stretched edge sprite. Set on `SpriteShape.cornerSprites`.
- A per-point `Corner` mode (`Automatic`, `Disable`, `Stretched`) overrides Corner Threshold, so a corner sprite can exist and not be used.
- Unverified: the Manual does not spell out the Corner Sprites Inspector layout (model from the Scripting API); confirm the live Editor before writing UI steps.

## Fill (Closed only)
- `useSpriteBorders`: draws 9-slice borders at each control point instead of stretching the sprite.
- `fillTexture`: tiled across the interior; must use Repeat wrap or the tiling seams.
- `fillOffset`: border offset at the fill texture's edges.

## Art import constraints (index)
| Requirement | If unmet |
|---|---|
| Texture Type = Sprite (2D and UI) | Cannot be assigned |
| Sprite Mode = Single | Multiple exposes sub-sprites the Profile cannot address as one tiling unit |
| Mesh Type = Full Rect | Tight meshes break border-based tiling |
| Atlas: Allow Rotation and Tight Packing off | Both distort the border data; sprites shear or seam |
