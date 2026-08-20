# Custom Physics Shape — Sprite Collision Geometry

Sources: https://docs.unity3d.com/Manual/sprite/create-collision-geometry.html, https://docs.unity3d.com/Manual/sprite/sprite-editor/custom-physics-shape-editor-reference.html

## Purpose

The Custom Physics Shape module authors the default collision outline stored on the `Sprite` asset itself (`Sprite.GetPhysicsShape`/`GetPhysicsShapeCount`, see [sprite-asset-reference.md](sprite-asset-reference.md)). When a `Collider2D` on a GameObject has **Use Sprite Physics Shape** enabled (or when `Generate Physics Shape` was left on at import with no custom shape authored — see [import-settings.md](import-settings.md)), Unity uses this outline as the collider's shape for every instance of that sprite — one shape authored once, reused by every GameObject that references the sprite, instead of hand-placing a `PolygonCollider2D` outline per instance.

**Scope boundary**: this module authors the *geometry* a `Collider2D` consumes. Choosing/configuring the `Rigidbody2D`/`Collider2D`/joint/effector components that actually simulate physics with that geometry is `unity-2d-physics`'s territory, not this skill's — see that skill's own scope definition.

## Toolbar controls

Same shared toolbar as [custom-outline.md](custom-outline.md) (Preview/Revert/Apply/Color/Zoom/Mipmap Level), plus:

| Control | Behavior |
|---|---|
| Outline Detail | Higher values produce a closer-fitting, higher-vertex collision outline; lower values simplify it. Per `performance-and-algorithms.md`, a physics shape with more vertices costs more per collision check — don't default to maximum detail. |
| Alpha Tolerance | Alpha threshold for what counts as "opaque" when tracing the outline. |
| Snap | Snaps vertices to the nearest pixel. |
| Generate / Generate All / Force Generate All | Same semantics as Custom Outline — trace from the sprite's opaque pixels; Force Generate All is destructive to hand-edited shapes and requires explicit confirmation. |
| Copy / Paste / Paste All | Transfer a physics shape between sprites. |
| Paste from Custom Outline | Copies the render-mesh outline over as the physics shape, when both should match. |
| Edit Collider | Lets an individual sprite *instance*'s collider diverge from the sprite asset's default shape without altering the shared default. |

## Editing

Same vertex/edge interactions as Custom Outline: drag to move a vertex, click an edge to add one, Delete to remove, Ctrl+drag to move an edge. The shape displays as a white outline with square vertex handles, distinct from the render outline's display.

## Practical guidance

- Prefer a **simple collider shape** the gameplay actually needs — per `performance-and-algorithms.md`'s "simplest collider shape" rule, a low-Outline-Detail physics shape (or, when the sprite's silhouette is roughly convex, an ordinary `BoxCollider2D`/`CircleCollider2D` set up directly in `unity-2d-physics` instead of a sprite-derived polygon) is both simpler and cheaper than a highly detailed traced outline.
- Author this once per unique sprite silhouette (e.g. once for a character's idle frame reused across many instances), not per GameObject instance — that's the entire point of storing it on the `Sprite` asset rather than hand-drawing a `PolygonCollider2D` per object.
- Only reach for **Edit Collider** (per-instance override) when a specific instance genuinely needs different collision geometry than its sibling instances of the same sprite — otherwise it silently diverges from the shared default in a way that's easy to forget.
- Hand off actual `Collider2D`/`Rigidbody2D` configuration, layer collision matrix pruning, and joint/effector setup to `unity-2d-physics` — this module's output is just the shape data those components consume.
