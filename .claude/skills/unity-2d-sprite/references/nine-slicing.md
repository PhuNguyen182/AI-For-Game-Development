# 9-Slicing — Border, Draw Mode & Fill

Sources: [9-slicing sprites](https://docs.unity3d.com/Manual/sprite/9-slice/9-slicing.html), [9-slice a sprite](https://docs.unity3d.com/Manual/sprite/9-slice/set-sprite-9slicing.html).
Covers: SKILL.md §4 — **"Reach for 9-slicing or `SpriteMask` only when the design actually resizes or reveals something"**.

9-slicing lets one sprite serve every size a panel, wall, or platform needs,
by holding the corners fixed while the edges and centre absorb the resize. It
requires two settings in two different places — a Border on the sprite asset
and a Draw Mode on the renderer — and it is inert without both.

## The nine regions

| Region | Behaviour under resize | Source |
|---|---|---|
| 4 corners | Never stretch or tile — this is what keeps rounded borders crisp at any size | [9-slicing](https://docs.unity3d.com/Manual/sprite/9-slice/9-slicing.html) |
| 4 edges | Stretch or tile along one axis only: top/bottom horizontally, left/right vertically | [9-slicing](https://docs.unity3d.com/Manual/sprite/9-slice/9-slicing.html) |
| 1 centre | Stretches or tiles on both axes | [9-slicing](https://docs.unity3d.com/Manual/sprite/9-slice/9-slicing.html) |

## Setup

| Step | What it decides | Source |
|---|---|---|
| Mesh Type = Full Rect | A hard prerequisite — Tight silently breaks 9-slicing, see [import-settings.md](import-settings.md) | [9-slice a sprite](https://docs.unity3d.com/Manual/sprite/9-slice/set-sprite-9slicing.html) |
| Border L/R/T/B in the Sprite Editor | Where the corners end; generous enough to cover the frame detail, no more, since an oversized border leaves less area for the stretch regions to work with | [9-slice a sprite](https://docs.unity3d.com/Manual/sprite/9-slice/set-sprite-9slicing.html) |
| Draw Mode on the `SpriteRenderer` | Simple ignores the border entirely; Sliced and Tiled activate it — see [sprite-renderer.md](sprite-renderer.md) | [9-slice a sprite](https://docs.unity3d.com/Manual/sprite/9-slice/set-sprite-9slicing.html) |

## Sliced vs Tiled

| Option | What it decides | Source |
|---|---|---|
| Sliced | All nine regions scale — smooth and continuous, correct for UI frames and gradients, wrong for a patterned texture, which blurs | [9-slicing](https://docs.unity3d.com/Manual/sprite/9-slice/9-slicing.html) |
| Tiled — Continuous | Edges and centre repeat the source pattern and never stretch; boundary tiles may render cropped | [9-slicing](https://docs.unity3d.com/Manual/sprite/9-slice/9-slicing.html) |
| Tiled — Adaptive | Stretches until the Stretch Value multiple of original size is reached, then starts repeating — Stretch Value 1 begins repeating once the sprite doubles | [9-slicing](https://docs.unity3d.com/Manual/sprite/9-slice/9-slicing.html) |

**Critical caveat**: only `BoxCollider2D` and `PolygonCollider2D` can follow a
9-sliced sprite, and only with **Auto Tiling** enabled — otherwise the
collider keeps the shape it had when the sprite was last resized. Configuring
that collider is `unity-2d-physics`'s work.
