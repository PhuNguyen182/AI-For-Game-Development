# Enabling Collision

Sources: https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/manual/SSCollision.html, `SpriteShapeController.autoUpdateCollider`/`optimizeCollider`/`colliderOffset`/`edgeCollider`/`polygonCollider`/`hasCollider`/`BakeCollider()` scripting API.

## Setup

1. Attach a `Collider2D` component to the Sprite Shape GameObject. **Only `EdgeCollider2D` and `PolygonCollider2D` are supported** — other `Collider2D` types don't integrate with Sprite Shape's mesh generation.
2. Attaching one of these exposes the **Additional Collider settings** section in the `SpriteShapeController` Inspector (see [spriteshape-controller.md](spriteshape-controller.md)).
3. By default the collider mesh **automatically reshapes** to match the Sprite Shape every time the spline is edited.

## Manual collider editing

To edit the collider mesh directly instead of letting it auto-regenerate, disable **Update Collider** in the `SpriteShapeController`'s Collider settings (clears the checkbox that drives `autoUpdateCollider`) before making manual edits — otherwise the next spline edit or bake overwrites manual changes.

## Scripting API

| Member | Description |
|---|---|
| `autoUpdateCollider` (`bool`) | Whether the collider mesh regenerates automatically on spline/geometry changes. |
| `optimizeCollider` (`bool`) | Whether generated collider geometry is optimized (fewer points). |
| `colliderDetail` (`int`) | Level of detail for collider geometry generation — independent from `splineDetail`'s render-mesh detail. |
| `colliderOffset` (`float`) | Offset applied to the generated collider shape. |
| `hasCollider` (`bool`) | Whether this object currently has a supported collider attached. |
| `edgeCollider` (`EdgeCollider2D`) / `polygonCollider` (`PolygonCollider2D`) | Returns whichever supported collider is attached, or `null`. |
| `BakeCollider()` | Forces an immediate collider update. |

## Practical guidance

- Route the resulting `EdgeCollider2D`/`PolygonCollider2D`'s `Rigidbody2D`, physics material, effectors, and joints to the sibling `unity-2d-physics` skill — this file only covers the collider *mesh generation*, not 2D physics dynamics built on top of it.
- Leave `autoUpdateCollider` on for any shape whose spline is still under art iteration — hand-editing a collider mesh that then gets silently overwritten on the next spline tweak is a common source of confusing bugs. Turn it off only once the shape is finalized and a specific manual collider adjustment is needed.
- `colliderDetail` doesn't have to match `splineDetail` — a visually detailed shape can use a coarser, cheaper collider if exact silhouette-matching collision isn't gameplay-critical (`performance-and-algorithms.md`'s measured-tradeoff principle).
