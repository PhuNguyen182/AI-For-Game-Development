# Colliders — Shapes & Compound Colliders

Covers SKILL.md step 4 (choosing a collider shape by accuracy/performance trade-off).

## Manual
- [Colliders](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/physics-collider-components.html) — the shape types Unity Physics supports, ranked from computationally cheapest to most expensive: **box** (local center + 3D size), **sphere** (radius), **capsule** (inner line segment + radius), **cylinder** (position/orientation + height/radius), **convex hull** (arbitrary convex shape from a point set), **triangle/quad** (flat, 3 or 4 coplanar vertices), **mesh** (triangles and quads), **terrain** (uniform grid of height samples), and **compound** (groups multiple colliders under one body). Primitive shapes are recommended over mesh colliders wherever the gameplay requirement allows — mesh colliders require significantly more calculation during collision detection, consistent with `performance-and-algorithms.md`'s "simplest collider shape" guidance applied to this engine.
- [Compound colliders](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/concepts-compounds.html) — attaching multiple collision shapes to a single body in a hierarchy, to build a detailed representation (e.g. a humanoid's torso/limbs/head as separate simple shapes) without the cost of a full mesh collider — "collision detection remains fast yet detailed."
- [Custom Physics Shape component](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/custom-shapes.html) — the `PhysicsShapeAuthoring` authoring component covering the same shape set (sphere, capsule, plane, box, cylinder, convex hull, mesh); convex shapes are recommended for dynamic bodies, mesh colliders for static/kinematic bodies only; a bevel radius (default 0.05) inflates/rounds the collider hull for more robust contact generation; the "Force Unique" property is required to allow non-uniform runtime scaling without sharing a collider instance between shapes.

## Scripting API
- [`Unity.Physics.Collider`](https://docs.unity3d.com/Packages/com.unity.physics@6.6/api/Unity.Physics.Collider.html) — base collider type; concrete shapes are accessed through `BlobAssetReference<Collider>` on `PhysicsCollider.Value` (see [dots-relationship.md](dots-relationship.md) for the blob-asset relationship with `unity-collections`).

For which authoring path (built-in `UnityEngine` components vs. `PhysicsShapeAuthoring`) bakes into these shapes, see [authoring-and-runtime-creation.md](authoring-and-runtime-creation.md).
