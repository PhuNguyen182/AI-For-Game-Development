# Sprite Shape collision

Sources: `manual/SSCollision.html`, `api/UnityEngine.U2D.SpriteShapeController.html`.

Collider geometry is generated from the same spline into a collider you attach yourself. Only two types receive it, and it regenerates on every spline change by default.

- Attach `EdgeCollider2D` or `PolygonCollider2D`. Any other `Collider2D` receives nothing and reports nothing wrong.
- Edge encloses no area (bodies cannot be inside): right for a ground surface. Polygon fills: right for a solid island.
- Detail, offset and auto-update appear on the controller once a supported collider exists.

| Member | Decides |
|---|---|
| `autoUpdateCollider` | Regenerate on every change. Disable before a manual edit or it is overwritten |
| `colliderDetail` | Collider tessellation, independent of `splineDetail`; a detailed cliff can have a cheap walkable surface |
| `optimizeCollider` | Fewer generated points, some silhouette loss |
| `colliderOffset` | Offsets the shape from the outline so feet land on the visual surface |
| `hasCollider` | Whether a supported collider is attached; guard before assuming generation |
| `edgeCollider` / `polygonCollider` | The attached collider, or `null` |
| `BakeCollider()` | Immediate update; load-time or tooling only |
