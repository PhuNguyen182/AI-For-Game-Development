# Sprite Shape Collision — Supported Colliders & Auto-Update

Sources: [Enabling Collision](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/manual/SSCollision.html), [SpriteShapeController API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SpriteShapeController.html).
Covers: SKILL.md §4 — **"Attach only `EdgeCollider2D` or `PolygonCollider2D`"**, **"Disable Update Collider before any manual collider edit"**.

Sprite Shape generates collider geometry from the same spline that drives the
mesh, into a collider you attach yourself. Two facts decide everything here:
only two collider types receive that geometry, and by default it is
regenerated on every spline change — which is convenient during art iteration
and destructive to a hand-tuned collider.

## Setup

| Step | What it decides | Source |
|---|---|---|
| Attach an `EdgeCollider2D` or `PolygonCollider2D` | The only two supported types. Any other `Collider2D` sits on the GameObject receiving no generated geometry and reporting nothing wrong | [Enabling Collision](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/manual/SSCollision.html) |
| Choose Edge versus Polygon | Edge encloses no area, so bodies cannot be inside the shape — right for a ground surface, wrong for a solid island. Polygon fills | [Enabling Collision](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/manual/SSCollision.html) |
| Additional Collider settings appear on the controller | Where detail, offset, and auto-update live once a supported collider exists | [Sprite Shape Controller](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/manual/SSController.html) |

## Controls

| Member | What it decides | Source |
|---|---|---|
| `autoUpdateCollider` (Update Collider) | Whether the collider regenerates on every spline or geometry change. **Disable it before any manual collider edit** — otherwise the next change silently overwrites the edit | [Enabling Collision](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/manual/SSCollision.html) |
| `colliderDetail` | Collider tessellation, independent of `splineDetail` — the dial that gives a visually detailed cliff a cheap walkable surface | [SpriteShapeController API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SpriteShapeController.html) |
| `optimizeCollider` | Reduces generated point count — fewer vertices per collision check, at some loss of silhouette fidelity | [SpriteShapeController API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SpriteShapeController.html) |
| `colliderOffset` | Offsets the generated shape from the outline — how a character's feet land on the visual surface rather than inside it | [SpriteShapeController API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SpriteShapeController.html) |
| `hasCollider` | Whether a supported collider is currently attached — the guard before assuming generation happens at all | [SpriteShapeController API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SpriteShapeController.html) |
| `edgeCollider` / `polygonCollider` | Returns whichever supported collider is attached, or `null` | [SpriteShapeController API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SpriteShapeController.html) |
| `BakeCollider()` | Forces an immediate collider update — a load-time or tooling operation, not per-frame work | [SpriteShapeController API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SpriteShapeController.html) |

Everything attached *to* that collider — the `Rigidbody2D`, the
`PhysicsMaterial2D`, effectors, joints — belongs to `unity-2d-physics`. This
file covers only the generation of the collider's geometry.
