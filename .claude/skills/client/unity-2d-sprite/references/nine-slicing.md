# 9-Slicing Sprites

Sources: https://docs.unity3d.com/Manual/sprite/9-slice/9-slice-landing.html, https://docs.unity3d.com/Manual/sprite/9-slice/9-slicing.html, https://docs.unity3d.com/Manual/sprite/9-slice/set-sprite-9slicing.html

## Concept

9-slicing divides a sprite into nine regions so it can be resized without distorting its detail or needing a separate sprite asset per target size:

- **4 corners** — fixed size, never stretched or tiled, regardless of how the sprite is resized. This is what keeps rounded corners/borders crisp.
- **4 edges** (top/bottom/left/right) — stretch or tile along a single axis only (top/bottom scale horizontally, left/right scale vertically).
- **1 center** — stretches or tiles along both axes.

This is the standard technique for scalable UI panels and repeatable/stretchable world geometry (walls, floors, platforms) without authoring a unique sprite per size.

## Setting it up

1. In the sprite's import settings, set **Mesh Type = Full Rect** and apply — **Tight** mesh type is incompatible with 9-slicing and will break it.
2. Open the Sprite Editor (see [sprite-editor.md](sprite-editor.md)), select the sprite, drag the green border handles inward (or enter explicit pixel values in the **L/R/T/B** fields) to define the border, then **Apply**.
3. On the GameObject's `SpriteRenderer`, set **Draw Mode** to **Sliced** or **Tiled** (see [sprite-renderer.md](sprite-renderer.md)).

## Sliced vs. Tiled

- **Sliced** — all nine regions stretch (scale) to fit the new size; smooth, continuous scaling, no repeating pattern.
- **Tiled** — the edges and center repeat the source texture pattern instead of stretching, with two fill sub-modes:
  - **Continuous** — the texture never stretches; tiles at the boundary may render a cropped partial tile.
  - **Adaptive** — the center stretches until it reaches the **Stretch Value** threshold (a multiple of the original size), then switches to repeating. A Stretch Value of 1 means it starts repeating once the sprite doubles in size; a lower value triggers repetition sooner.

## Collision on a 9-sliced sprite

Only `BoxCollider2D` or `PolygonCollider2D` can be added to a 9-sliced sprite's GameObject. Enable **Auto Tiling** on the collider so it updates automatically as the sprite is resized, instead of manually re-authoring the collider shape every time the Draw Mode's size changes. Configuring the collider component itself is `unity-2d-physics`'s territory — this skill only covers authoring the border and Draw Mode.

## Practical guidance

- Don't 9-slice a sprite that's always shown at a fixed size — per KISS in `coding-principles.md`, a static-size sprite doesn't need Sliced/Tiled Draw Mode; Simple is simpler and cheaper.
- Choose **Sliced** for UI panels/frames where a smooth scale reads correctly, and **Tiled** for anything where a repeating texture pattern is the intended look (a brick wall segment, a scrolling floor) — using the wrong one produces either an unwanted stretched-blur look (Sliced on a patterned texture) or unwanted visible seams (Tiled on a smooth gradient).
- Set the border generously enough to cover any rounded corner/frame detail, but no more — an oversized border needlessly shrinks how much of the sprite the stretch/tile regions can actually cover before looking distorted.
