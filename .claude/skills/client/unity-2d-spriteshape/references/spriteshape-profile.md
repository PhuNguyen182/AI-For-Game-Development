# Sprite Shape Profile — Topology, Angle Ranges, Corners & Fill

Sources: [Sprite Shape Profile](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/manual/SSProfile.html), [SpriteShape API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SpriteShape.html), [AngleRange API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.AngleRange.html).
Covers: SKILL.md §4 — **"Choose Open or Closed Shape before anything else"**, **"Cover the whole angle space with non-overlapping Angle Ranges"**, **"Verify the sprite import mode before assigning art to a Profile"**.

A Profile is the `ScriptableObject` (`SpriteShape`) that maps *outline angle*
to *sprite*. It is the shared palette: one Profile serves every controller
that should look alike, while each controller's spline supplies the
per-instance shape. Create it via **Assets > Create > Sprite Shape Profile**.

## Topology

| Preset | What it decides | Source |
|---|---|---|
| Open Shape | The outline has distinct start and end points — a platform edge, a rope. No fill geometry exists at all, so Fill settings are inert | [Sprite Shape Profile](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/manual/SSProfile.html) |
| Closed Shape | The outline loops — a pond, an island. The interior is filled from `fillTexture`, which is the only way to get a filled body | [Sprite Shape Profile](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/manual/SSProfile.html) |

## Angle Ranges

| Field | What it decides | Source |
|---|---|---|
| Start / End (`AngleRange.start`, `.end`) | The angle span this range answers for. **Ranges must not overlap** — an overlap makes selection ambiguous exactly at the boundary, where a shape most often bends | [AngleRange API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.AngleRange.html) |
| Order (`AngleRange.order`) | Render priority where sprites from different ranges meet at an intersection | [AngleRange API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.AngleRange.html) |
| Sprites (`AngleRange.sprites`) | The pool for this range; the **first** entry is the default, and a control point's `spriteIndex` picks another — see [spriteshape-controller.md](spriteshape-controller.md) | [AngleRange API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.AngleRange.html) |

Coverage is as important as non-overlap: an angle no range covers has no
sprite to draw. Author the ranges against the angles the design's outlines
will actually produce, then confirm in the Profile Inspector's live preview.

## Corner Sprites

| Concept | What it decides | Source |
|---|---|---|
| `CornerSprite` and `CornerType` | Pairs a sprite pool with one of the eight corner types — `InnerBottomLeft` through `OuterTopRight` — so a sharp bend uses purpose-made art instead of stretching an edge sprite around it | [CornerSprite API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.CornerSprite.html) |
| `SpriteShape.cornerSprites` | The configured set on the Profile | [SpriteShape API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SpriteShape.html) |
| Per-point `Corner` mode | `Automatic`, `Disable`, or `Stretched` on the control point overrides what Corner Threshold decided — so a corner sprite can be present and still not used | [Corner API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.Corner.html) |

**Critical caveat**: the Manual page documents Angle Ranges and Fill but does
not spell out the Corner Sprites Inspector layout; the data model above comes
from the Scripting API. Confirm the live Editor's controls before writing
step-by-step UI instructions.

## Fill (Closed shapes only)

| Field | What it decides | Source |
|---|---|---|
| `useSpriteBorders` | Draws the sprite's 9-slice borders at each control point instead of stretching the whole sprite — what keeps a bordered edge crisp around a bend | [Sprite Shape Profile](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/manual/SSProfile.html) |
| `fillTexture` | The `Texture2D` tiled across the interior; it must use Repeat wrap mode or the tiling seams | [Sprite Shape Profile](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/manual/SSProfile.html) |
| `fillOffset` | Border offset at the fill texture's edges | [Sprite Shape Profile](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/manual/SSProfile.html) |

## Import constraints on the art

| Requirement | Consequence if unmet | Source |
|---|---|---|
| Texture Type = Sprite (2D and UI) | The asset is not a sprite and cannot be assigned | [Sprite Shape manual](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/manual/index.html) |
| Sprite Mode = Single | A Multiple-mode sheet exposes sub-sprites the Profile cannot address as one tiling unit | [Sprite Shape manual](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/manual/index.html) |
| Mesh Type = Full Rect | Tight meshes break border-based tiling along the spline | [Sprite Shape manual](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/manual/index.html) |
| Atlas: Allow Rotation and Tight Packing off | Both distort the border data tiling relies on, so sprites shear or seam along the outline | [Sprite Shape manual](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/manual/index.html) |

Performing those imports is `unity-2d-sprite`'s work; this file states only
the constraint Sprite Shape imposes on them.
