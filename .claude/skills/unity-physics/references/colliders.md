# Colliders

Sources (under `manual/`): `physics-collider-components.html`, `concepts-compounds.html`, `custom-shapes.html`; `api/Unity.Physics.Collider.html`.

## Shapes, cheapest first
| Shape | Notes |
|---|---|
| Sphere | Radius only; cheapest |
| Box | Centre + 3D size; cheapest general volume |
| Capsule | Inner segment + radius; standard character volume |
| Cylinder | Position, orientation, height, radius |
| Convex hull | Arbitrary convex point set; recommended for non-primitive dynamic bodies |
| Triangle / quad | Flat, 3 or 4 coplanar vertices |
| Mesh | Significantly more cost per contact; static or kinematic detail geometry only |
| Terrain | Uniform grid of height samples |
| Compound | Several shapes under one body; detail at primitive cost, preferred over mesh for a dynamic body |

## Settings that change behaviour
- **Bevel radius (default 0.05)** inflates and rounds the hull for robust contacts, so the collider is slightly larger than authored and a body can rest visibly above a surface.
- **Force Unique** is required before non-uniform runtime scaling. Geometry sits behind a shared `BlobAssetReference<Collider>` (`PhysicsCollider.Value`); any runtime mutation, scale included, affects every body pointing at that blob until the shape is made unique.
