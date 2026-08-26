# Colliders — Shapes, Compounds, Bevel & Uniqueness

Sources: [Colliders](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/physics-collider-components.html), [Compound colliders](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/concepts-compounds.html), [Custom Physics Shape component](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/custom-shapes.html).
Covers: SKILL.md §4 — **"Pick the simplest collider shape the gameplay requirement allows"**, **"Set bevel radius and Force Unique deliberately rather than by default"**.

Shape choice ordered by evaluation cost, plus the two authoring settings that
change behaviour rather than performance. Which authoring path bakes these is
[authoring-and-runtime-creation.md](authoring-and-runtime-creation.md).

## Shapes, cheapest first

| Shape | What it decides | Source |
|---|---|---|
| Box | Local centre plus 3D size — the cheapest general-purpose volume | [Colliders](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/physics-collider-components.html) |
| Sphere | Radius only; cheapest of all to evaluate | [Colliders](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/physics-collider-components.html) |
| Capsule | Inner segment plus radius — the standard character volume | [Colliders](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/physics-collider-components.html) |
| Cylinder | Position, orientation, height, radius | [Colliders](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/physics-collider-components.html) |
| Convex hull | Arbitrary convex shape from a point set — the recommended form for dynamic bodies that are not primitives | [Custom shapes](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/custom-shapes.html) |
| Triangle / quad | Flat, 3 or 4 coplanar vertices | [Colliders](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/physics-collider-components.html) |
| Mesh | Triangles and quads; significantly more calculation per contact — static or kinematic detail geometry only | [Custom shapes](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/custom-shapes.html) |
| Terrain | Uniform grid of height samples | [Colliders](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/physics-collider-components.html) |
| Compound | Several shapes under one body — detailed representation at primitive cost, the preferred alternative to a mesh for a dynamic body | [Compound colliders](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/concepts-compounds.html) |

## Authoring settings that change behaviour

| Setting | What it decides | Source |
|---|---|---|
| Bevel radius (default 0.05) | Inflates and rounds the hull for more robust contact generation — so the collider is slightly larger than the authored shape, which is why a body can rest visibly above a surface | [Custom shapes](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/custom-shapes.html) |
| Force Unique | Required before non-uniform runtime scaling — without it the collider instance is shared between shapes, and scaling one scales every body using it | [Custom shapes](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/custom-shapes.html) |
| Storage | Geometry lives behind `BlobAssetReference<Collider>` on `PhysicsCollider.Value`, which is what makes sharing the default | [Collider](https://docs.unity3d.com/Packages/com.unity.physics@6.6/api/Unity.Physics.Collider.html) |

**Critical caveat**: sharing is the default, not an optimization someone chose.
Any runtime mutation of collider geometry — scale included — affects every body
pointing at that blob until the shape is made unique.
