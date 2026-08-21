# Custom Physics Shape — Sprite Collision Geometry

Sources: [Create collision shapes for a sprite](https://docs.unity3d.com/Manual/sprite/create-collision-geometry.html), [Custom Physics Shape tab reference](https://docs.unity3d.com/Manual/sprite/sprite-editor/custom-physics-shape-editor-reference.html).
Covers: SKILL.md §4 — **"Author collision geometry once on the `Sprite` asset, never per instance"**.

This module writes a collision outline onto the `Sprite` asset itself, read
back at runtime through `Sprite.GetPhysicsShape` (see
[sprite-asset-reference.md](sprite-asset-reference.md)). Any `Collider2D`
with **Use Sprite Physics Shape** enabled — or a sprite imported with Generate
Physics Shape on and no custom shape authored — adopts it, so one authoring
pass serves every instance. Configuring the colliders and bodies that consume
the shape belongs to `unity-2d-physics`, not here.

## Controls

| Control | What it decides | Source |
|---|---|---|
| Outline Detail | Vertex count is paid on every collision check, so this is a runtime cost dial, not a fidelity dial — trace to the coarsest silhouette that still plays correctly | [Custom Physics Shape tab reference](https://docs.unity3d.com/Manual/sprite/sprite-editor/custom-physics-shape-editor-reference.html) |
| Alpha Tolerance | Alpha threshold for "opaque" when tracing — decides whether soft edges are inside the hitbox | [Custom Physics Shape tab reference](https://docs.unity3d.com/Manual/sprite/sprite-editor/custom-physics-shape-editor-reference.html) |
| Snap | Snaps vertices to the pixel grid | [Custom Physics Shape tab reference](https://docs.unity3d.com/Manual/sprite/sprite-editor/custom-physics-shape-editor-reference.html) |
| Generate / Generate All | Traces the selected sprite, or only sprites with no shape yet | [Custom Physics Shape tab reference](https://docs.unity3d.com/Manual/sprite/sprite-editor/custom-physics-shape-editor-reference.html) |
| Force Generate All | Overwrites every shape on the sheet including hand edits — destructive, confirmation-gated | [Custom Physics Shape tab reference](https://docs.unity3d.com/Manual/sprite/sprite-editor/custom-physics-shape-editor-reference.html) |
| Copy / Paste / Paste All | Transfers a shape between sprites | [Custom Physics Shape tab reference](https://docs.unity3d.com/Manual/sprite/sprite-editor/custom-physics-shape-editor-reference.html) |
| Paste from Custom Outline | Reuses the render outline as collision when both should match — see [custom-outline.md](custom-outline.md) | [Custom Physics Shape tab reference](https://docs.unity3d.com/Manual/sprite/sprite-editor/custom-physics-shape-editor-reference.html) |
| Edit Collider | Lets one *instance*'s collider diverge from the sprite's shared default — an override that is easy to forget exists, so use it only when that instance genuinely differs | [Create collision shapes](https://docs.unity3d.com/Manual/sprite/create-collision-geometry.html) |

## Editing gestures

| Gesture | Effect | Source |
|---|---|---|
| Drag a vertex | Moves it | [Create collision shapes](https://docs.unity3d.com/Manual/sprite/create-collision-geometry.html) |
| Click an edge | Inserts a vertex | [Create collision shapes](https://docs.unity3d.com/Manual/sprite/create-collision-geometry.html) |
| Select a vertex, press Delete | Removes it | [Create collision shapes](https://docs.unity3d.com/Manual/sprite/create-collision-geometry.html) |
| Ctrl+drag an edge | Moves the whole edge | [Create collision shapes](https://docs.unity3d.com/Manual/sprite/create-collision-geometry.html) |

**Critical caveat**: a traced polygon is not automatically the right answer.
When the silhouette is roughly convex, a `BoxCollider2D` or `CircleCollider2D`
configured in `unity-2d-physics` is both simpler and cheaper than any
sprite-derived polygon, per `performance-and-algorithms.md`'s Physics section.
