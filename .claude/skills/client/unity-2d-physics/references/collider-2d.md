# Collider2D — Shapes, Composites, Contact Data & the Layer Matrix

Sources: [Collider 2D](https://docs.unity3d.com/Manual/2d-physics/collider/collider-2d-landing.html), [Composite Collider 2D](https://docs.unity3d.com/Manual/2d-physics/collider/composite-collider/composite-collider-2d-landing.html), [Collider2D API](https://docs.unity3d.com/ScriptReference/Collider2D.html).
Covers: SKILL.md §4 — **"Pick the simplest collider shape the silhouette allows"**, **"Prune the layer collision matrix instead of filtering inside callbacks"**.

A `Collider2D` declares which area of a GameObject participates in the
simulation. Two hard constraints frame everything below: 2D and 3D colliders
cannot be mixed on one hierarchy, and a collider with no `Rigidbody2D` above
it is static. Shape choice is a runtime cost decision, and the layer matrix is
where contacts are cheapest to eliminate — before broadphase, not inside a
callback.

## Contents

- [Shapes](#shapes)
- [Composite collider](#composite-collider)
- [Trigger versus solid](#trigger-versus-solid)
- [Contact data](#contact-data)
- [Layer filtering](#layer-filtering)

## Shapes

| Shape | What it decides | Source |
|---|---|---|
| `CircleCollider2D` | Cheapest test there is — one radius comparison. First choice for anything round or roughly round | [Circle Collider 2D](https://docs.unity3d.com/Manual/2d-physics/collider/circle-collider-2d-reference.html) |
| `BoxCollider2D` | Rectangle with optional `edgeRadius` for rounded corners, and `autoTiling` to follow a tiled sprite's size — the default for rectangular art | [Box Collider 2D](https://docs.unity3d.com/Manual/2d-physics/collider/box-collider-2d-reference.html) |
| `CapsuleCollider2D` | Rounded ends on a chosen axis; the standard character body, because its rounded base does not catch on tile seams the way a box's corners do | [Capsule Collider 2D](https://docs.unity3d.com/Manual/2d-physics/collider/capsule-collider/capsule-collider-2d-landing.html) |
| `PolygonCollider2D` | Freeform closed shape, `CreateFromSprite` seeds it from the sprite's authored physics shape. `useDelaunayMesh` improves accuracy on complex shapes and costs performance, so enable it only when a specific inaccuracy is observed | [Polygon Collider 2D](https://docs.unity3d.com/Manual/2d-physics/collider/polygon-collider-2d-reference.html) |
| `EdgeCollider2D` | Open line strip enclosing no area — cliffs, ceilings, one-sided boundaries. **Cannot collide with another `EdgeCollider2D`** under any body type or trigger setting | [Edge Collider 2D](https://docs.unity3d.com/Manual/2d-physics/collider/edge-collider-2d-reference.html) |
| `CompositeCollider2D` | Merges Box and Polygon colliders marked Used By Composite into one generated shape — the fix for hundreds of per-tile colliders | [Composite Collider 2D](https://docs.unity3d.com/Manual/2d-physics/collider/composite-collider/composite-collider-2d-landing.html) |

Prefer Circle, Box, or Capsule over Polygon, and Polygon over a traced
per-pixel outline, per `performance-and-algorithms.md`'s Physics section. The
sprite-side authoring of that outline belongs to `unity-2d-sprite`.

## Composite collider

| Property | What it decides | Source |
|---|---|---|
| `geometryType` | **Polygons** produces filled area, so bodies can be inside the shape and overlap queries work; **Outlines** produces edges only, which is lighter but cannot answer "is this point inside" | [Composite Collider 2D](https://docs.unity3d.com/Manual/2d-physics/collider/composite-collider/composite-collider-2d-reference.html) |
| `generationType` | Synchronous regeneration on every change, or manual via `GenerateGeometry()` — manual is what keeps a large tilemap from rebuilding mid-edit | [Composite Collider 2D](https://docs.unity3d.com/Manual/2d-physics/collider/composite-collider/composite-collider-2d-reference.html) |
| `offsetDistance` / `vertexDistance` | Merge tolerance between shapes and minimum spacing between generated vertices — the two dials that close hairline gaps between adjacent tiles | [Composite Collider 2D](https://docs.unity3d.com/Manual/2d-physics/collider/composite-collider/composite-collider-2d-reference.html) |
| `edgeRadius` | Radius applied to every generated edge, which rounds the whole composite outline | [Composite Collider 2D](https://docs.unity3d.com/Manual/2d-physics/collider/composite-collider/composite-collider-2d-reference.html) |
| `compositeOperation` / `compositeOrder` on the source collider | Whether a member shape merges, subtracts, or intersects, and in what order — how a hole is cut in a merged surface | [Collider2D.compositeOperation](https://docs.unity3d.com/ScriptReference/Collider2D-compositeOperation.html) |

## Trigger versus solid

| Setting | What it decides | Source |
|---|---|---|
| `isTrigger` off | Produces a physical response and reports through `OnCollision*2D`, carrying full contact data | [Collider2D.isTrigger](https://docs.unity3d.com/ScriptReference/Collider2D-isTrigger.html) |
| `isTrigger` on | No physical response; reports overlap through `OnTrigger*2D`, which receives only the other `Collider2D` and no contact points | [Collider2D.isTrigger](https://docs.unity3d.com/ScriptReference/Collider2D-isTrigger.html) |
| `usedByEffector` | Opts the collider into an attached `Effector2D` — off by default and silently required, see [effectors-2d.md](effectors-2d.md) | [Collider2D.usedByEffector](https://docs.unity3d.com/ScriptReference/Collider2D-usedByEffector.html) |
| `density` | Feeds Use Auto Mass on the body — changing a collider's density silently changes body mass when that option is on | [Collider2D.density](https://docs.unity3d.com/ScriptReference/Collider2D-density.html) |

## Contact data

| Member | What it decides | Source |
|---|---|---|
| `Collision2D.relativeVelocity` | Impact speed — the value an impact-strength rule should be derived from, in `Game.Core.*` rather than in the callback | [Collision2D](https://docs.unity3d.com/ScriptReference/Collision2D.html) |
| `Collision2D.contactCount` / `GetContact(int)` | Per-contact access without touching `contacts`, which allocates an array on every access | [Collision2D.GetContact](https://docs.unity3d.com/ScriptReference/Collision2D.GetContact.html) |
| `ContactPoint2D.point` / `normal` | World contact position and surface normal — the two values a hit reaction is built from | [ContactPoint2D](https://docs.unity3d.com/ScriptReference/ContactPoint2D.html) |
| `ContactPoint2D.separation` | Distance between colliders at the contact; negative means penetration, which is how overlap depth is measured | [ContactPoint2D](https://docs.unity3d.com/ScriptReference/ContactPoint2D.html) |
| `ContactPoint2D.normalImpulse` / `tangentImpulse` | Impulse actually applied along and across the normal — the measured impact, as distinct from approach speed | [ContactPoint2D](https://docs.unity3d.com/ScriptReference/ContactPoint2D.html) |
| `Collider2D.GetContacts(...)` buffer overloads | Fills a caller-owned array instead of allocating, which is what keeps contact polling out of the GC per `performance-and-algorithms.md`'s Memory discipline section | [Collider2D.GetContacts](https://docs.unity3d.com/ScriptReference/Collider2D.GetContacts.html) |
| `Cast`, `Overlap`, `OverlapPoint`, `Distance`, `ClosestPoint`, `Raycast` | Direct queries from an existing collider — cheaper and more precise than a `Physics2D` world query the caller then filters | [Collider2D.Cast](https://docs.unity3d.com/ScriptReference/Collider2D.Cast.html) |

## Layer filtering

| Mechanism | What it decides | Source |
|---|---|---|
| Project Settings layer collision matrix | Excluded pairs never reach broadphase, so they cost nothing — always the first filter | [Physics2D.IgnoreLayerCollision](https://docs.unity3d.com/ScriptReference/Physics2D.IgnoreLayerCollision.html) |
| `Physics2D.SetLayerCollisionMask` / `GetLayerCollisionMask` | The same matrix at runtime, when a mode change must repartition what interacts | [Physics2D.SetLayerCollisionMask](https://docs.unity3d.com/ScriptReference/Physics2D.SetLayerCollisionMask.html) |
| `includeLayers` / `excludeLayers` on a collider or body | A per-object exception layered on the matrix — for one object that differs, not as a substitute for the matrix | [Collider2D.excludeLayers](https://docs.unity3d.com/ScriptReference/Collider2D-excludeLayers.html) |
| `layerOverridePriority` | Resolves which object's override wins when two disagree — without it the outcome depends on which side is evaluated | [Collider2D.layerOverridePriority](https://docs.unity3d.com/ScriptReference/Collider2D-layerOverridePriority.html) |
| `contactCaptureLayers` / `callbackLayers` | Which contacts are recorded and which raise managed callbacks — narrows callback cost without changing the simulation | [Collider2D.callbackLayers](https://docs.unity3d.com/ScriptReference/Collider2D-callbackLayers.html) |
| `forceSendLayers` / `forceReceiveLayers` | Which layers this collider may push and be pushed by, independently of whether they collide | [Collider2D.forceSendLayers](https://docs.unity3d.com/ScriptReference/Collider2D-forceSendLayers.html) |

An `if` inside `OnCollisionEnter2D` that discards unwanted pairs has already
paid broadphase, narrowphase, and a managed callback for each one. The matrix
is where that cost is actually removed.
