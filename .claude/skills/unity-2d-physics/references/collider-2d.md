# Collider2D

Sources: Manual `2d-physics/collider/`; API `Collider2D`, `Collision2D`, `ContactPoint2D`, `Physics2D`. 2D and 3D colliders cannot mix on one hierarchy; a collider with no `Rigidbody2D` above it is static.

## Shapes

| Shape | Decides |
|---|---|
| `CircleCollider2D` | Cheapest test (one radius compare); first choice for round things |
| `BoxCollider2D` | `edgeRadius` rounds corners; `autoTiling` follows a tiled sprite |
| `CapsuleCollider2D` | Standard character body: the rounded base does not catch on tile seams |
| `PolygonCollider2D` | `CreateFromSprite` seeds from the sprite's physics shape; `useDelaunayMesh` costs performance, enable only for an observed inaccuracy |
| `EdgeCollider2D` | Open line strip, no area (cliffs, ceilings). **Cannot collide with another `EdgeCollider2D`** under any body/trigger setting |
| `CompositeCollider2D` | Merges Box/Polygon colliders marked Used By Composite into one shape: the fix for hundreds of per-tile colliders |

Order: Circle/Box/Capsule, then Polygon, then a traced per-pixel outline.

## Composite collider

| Property | Decides |
|---|---|
| `geometryType` | **Polygons**: filled, bodies can be inside, overlap queries work. **Outlines**: edges only, lighter, cannot answer "is this point inside" |
| `generationType` | Synchronous per change, or manual `GenerateGeometry()`; manual avoids rebuilds while editing a large tilemap |
| `offsetDistance` / `vertexDistance` | Merge tolerance and vertex spacing: close hairline gaps between tiles |
| `edgeRadius` | Rounds the whole composite outline |
| `compositeOperation` / `compositeOrder` (on source) | Merge, subtract or intersect, and order: how a hole is cut |

## Trigger vs solid

| Setting | Decides |
|---|---|
| `isTrigger` off | Physical response; `OnCollision*2D` with full contact data |
| `isTrigger` on | No response; `OnTrigger*2D` gets only the other `Collider2D`, no contact points |
| `usedByEffector` | Opt-in to an `Effector2D`; off by default (see [effectors-2d.md](effectors-2d.md)) |
| `density` | With Use Auto Mass, changing it changes body mass |

## Contact data

| Member | Decides |
|---|---|
| `Collision2D.relativeVelocity` | Impact speed; derive impact-strength rules in `Game.Core.*` |
| `contactCount` / `GetContact(int)` | `contacts` allocates an array on every access; use these |
| `ContactPoint2D.point` / `normal` | World position and surface normal for a hit reaction |
| `ContactPoint2D.separation` | Negative = penetration depth |
| `normalImpulse` / `tangentImpulse` | Impulse actually applied: measured impact, not approach speed |
| `Collider2D.GetContacts(buffer)` | Caller-owned array, no allocation |
| `Cast`, `Overlap`, `OverlapPoint`, `Distance`, `ClosestPoint`, `Raycast` | Direct queries from a collider: cheaper than a `Physics2D` world query then filtering |

## Layer filtering

| Mechanism | Decides |
|---|---|
| Project Settings layer matrix | Excluded pairs never reach broadphase: always the first filter. An `if` in `OnCollisionEnter2D` has already paid broadphase, narrowphase and the managed callback |
| `Physics2D.Set/GetLayerCollisionMask` | The matrix at runtime |
| `includeLayers` / `excludeLayers` | Per-object exception on the matrix |
| `layerOverridePriority` | Which override wins when two objects disagree; otherwise depends on evaluation side |
| `contactCaptureLayers` / `callbackLayers` | Which contacts are recorded / raise callbacks: narrows callback cost without changing the simulation |
| `forceSendLayers` / `forceReceiveLayers` | Which layers it may push / be pushed by, independent of collision |
