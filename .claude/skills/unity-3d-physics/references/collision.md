# Collision

Sources: Manual `CollidersOverview`, `collider-shapes`, `collider-types-interaction`, `collider-surfaces`, `collision-detection`; API `Physics`, `Collider`, `Collision`.

Most "callback never fires" reports resolve to a row of the pairing matrix below.

## Shapes
- `SphereCollider` cheapest; `BoxCollider` cheap and exact (several boxes as a compound usually beat one mesh); `CapsuleCollider` rounded ends avoid floor-seam snags.
- `MeshCollider`: far more expensive. Convex is required to back a dynamic Rigidbody, capped at 255 triangles.
- Compound colliders (several primitives on one body) are almost always the answer instead of a mesh collider.
- `WheelCollider` and `TerrainCollider` are purpose-built and do not generalise.

## Categories
- Static: collider without Rigidbody. Repositioning one forces a broadphase rebuild.
- Dynamic: collider plus non-kinematic Rigidbody.
- Kinematic: collider plus kinematic Rigidbody.
- Trigger: `isTrigger`; reports overlap with no physical response, and at least one participant needs a Rigidbody.

## Events by pairing

| A | B | Result |
|---|---|---|
| Dynamic | Static / Dynamic / Kinematic | `OnCollision*` |
| Static | Static | Nothing |
| Static | Kinematic | Nothing (why a scripted platform ignores level geometry) |
| Kinematic | Kinematic | Nothing |
| Trigger (dynamic or kinematic) | Any | `OnTrigger*` |
| Trigger (static) | Dynamic or kinematic | `OnTrigger*` |

## Surfaces
- `PhysicsMaterial`: static friction, dynamic friction, bounciness. Combine mode (Average, Minimum, Maximum, Multiply) applies to the pair, so one material never decides alone.
- `Collider.material` instantiates a per-collider copy that leaks if never destroyed; `sharedMaterial` edits the asset for every user.

## Filtering and queries
- Layer collision matrix: excluded pairs never reach broadphase; the first filter, ahead of any `if` in a callback. Runtime form: `Physics.IgnoreLayerCollision`.
- `Physics.IgnoreCollision` suppresses one collider pair the matrix cannot express.
- `Physics.RaycastNonAlloc` and other `NonAlloc` variants fill a caller-owned buffer; the allocating overloads produce garbage per call.
- `QueryTriggerInteraction` decides whether a query hits triggers; it silently decides if a trigger volume blocks a line-of-sight test.
- `Collision.GetContact(int)` avoids the array allocation `contacts` makes on every read.
