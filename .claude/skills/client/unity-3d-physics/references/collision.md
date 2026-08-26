# Collision — Shapes, Surfaces, Event Pairings & Detection

Sources: [Introduction to collision](https://docs.unity3d.com/Manual/CollidersOverview.html), [Collider shapes](https://docs.unity3d.com/Manual/collider-shapes.html), [Interaction between collider types](https://docs.unity3d.com/Manual/collider-types-interaction.html), [Collision detection](https://docs.unity3d.com/Manual/collision-detection.html).
Covers: SKILL.md §4 — **"Pick the simplest collider the requirement allows, and stop moving static ones"**.

A collider defines a physical shape independent of the rendered mesh. The
single most useful table here is the pairing matrix: which combinations of
static, dynamic, kinematic, and trigger colliders actually raise events. Most
"my collision callback never fires" reports resolve to a row in it, not to a
misconfigured collider.

## Contents

- [Shapes](#shapes)
- [Collider categories](#collider-categories)
- [Which pairings raise events](#which-pairings-raise-events)
- [Surfaces](#surfaces)
- [Detection and filtering](#detection-and-filtering)

## Shapes

| Shape | What it decides | Source |
|---|---|---|
| `SphereCollider` | Cheapest test available; first choice wherever roundness is acceptable | [Collider shapes](https://docs.unity3d.com/Manual/collider-shapes.html) |
| `BoxCollider` | Cheap and exact for rectangular volumes; several boxes as a compound usually beat one mesh | [Collider shapes](https://docs.unity3d.com/Manual/collider-shapes.html) |
| `CapsuleCollider` | Rounded ends stop a body catching on floor seams — the standard character and prop body | [Collider shapes](https://docs.unity3d.com/Manual/collider-shapes.html) |
| `MeshCollider` | Arbitrary geometry, dramatically more expensive. **Convex is required to back a dynamic Rigidbody**, and convex meshes are capped at 255 triangles | [Collider shapes](https://docs.unity3d.com/Manual/collider-shapes.html) |
| Compound colliders | Several primitives on one body approximating a complex shape — almost always the right answer instead of a mesh collider | [Configure Rigidbody colliders](https://docs.unity3d.com/Manual/rigidbody-configure-colliders.html) |
| `WheelCollider`, `TerrainCollider` | Purpose-built for vehicle wheels and terrain heightmaps; neither generalises to other geometry | [Collider shapes](https://docs.unity3d.com/Manual/collider-shapes.html) |

## Collider categories

| Category | What it decides | Source |
|---|---|---|
| Static — collider, no Rigidbody | Never moves in response to anything. Cheapest, but repositioning one forces a broadphase rebuild, so anything that moves needs a kinematic body instead | [Introduction to collider types](https://docs.unity3d.com/Manual/collider-types-introduction.html) |
| Dynamic — collider plus non-kinematic Rigidbody | Responds to forces and collides with every other category | [Introduction to collider types](https://docs.unity3d.com/Manual/collider-types-introduction.html) |
| Kinematic — collider plus kinematic Rigidbody | Moved only by script; pushes dynamic bodies without being pushed | [Introduction to collider types](https://docs.unity3d.com/Manual/collider-types-introduction.html) |
| Trigger — any of the above with `isTrigger` | Detects overlap with no physical response; at least one participant must carry a Rigidbody for anything to be reported | [Collider interactions](https://docs.unity3d.com/Manual/collider-interactions.html) |

## Which pairings raise events

| Collider A | Collider B | Result | Source |
|---|---|---|---|
| Dynamic | Static | `OnCollision*` | [Interaction between collider types](https://docs.unity3d.com/Manual/collider-types-interaction.html) |
| Dynamic | Dynamic | `OnCollision*` | [Interaction between collider types](https://docs.unity3d.com/Manual/collider-types-interaction.html) |
| Dynamic | Kinematic | `OnCollision*` | [Interaction between collider types](https://docs.unity3d.com/Manual/collider-types-interaction.html) |
| Static | Static | **Nothing** | [Interaction between collider types](https://docs.unity3d.com/Manual/collider-types-interaction.html) |
| Static | Kinematic | **Nothing** — the usual reason a scripted platform ignores level geometry | [Interaction between collider types](https://docs.unity3d.com/Manual/collider-types-interaction.html) |
| Kinematic | Kinematic | **Nothing** | [Interaction between collider types](https://docs.unity3d.com/Manual/collider-types-interaction.html) |
| Trigger (dynamic or kinematic) | Any | `OnTrigger*` | [Interaction between collider types](https://docs.unity3d.com/Manual/collider-types-interaction.html) |
| Trigger (static) | Dynamic or kinematic | `OnTrigger*` | [Interaction between collider types](https://docs.unity3d.com/Manual/collider-types-interaction.html) |

## Surfaces

| Concept | What it decides | Source |
|---|---|---|
| `PhysicsMaterial` friction and bounciness | Static friction, dynamic friction, and restitution for the surface | [Collider surfaces](https://docs.unity3d.com/Manual/collider-surfaces.html) |
| Combine modes | Average, Minimum, Maximum, Multiply — applied to the *pair*, so one collider's material never decides the contact alone | [Collider surfaces](https://docs.unity3d.com/Manual/collider-surfaces.html) |
| `Collider.material` vs `sharedMaterial` | Reading `material` instantiates a per-collider copy and leaks it if never destroyed; `sharedMaterial` edits the asset for every user — a direct instance of `performance-and-algorithms.md`'s Memory discipline concern | [Collider.material](https://docs.unity3d.com/ScriptReference/Collider-material.html) |

## Detection and filtering

| Mechanism | What it decides | Source |
|---|---|---|
| Layer collision matrix | Excluded pairs never reach broadphase, so they cost nothing — always the first filter, ahead of any `if` inside a callback | [Physics.IgnoreLayerCollision](https://docs.unity3d.com/ScriptReference/Physics.IgnoreLayerCollision.html) |
| `Physics.IgnoreCollision` | Suppresses one specific collider pair, for an exception the matrix cannot express | [Physics.IgnoreCollision](https://docs.unity3d.com/ScriptReference/Physics.IgnoreCollision.html) |
| `Physics.Raycast` and the `NonAlloc` variants | World queries; the allocating overloads produce garbage per call, which the buffer overloads avoid | [Physics.RaycastNonAlloc](https://docs.unity3d.com/ScriptReference/Physics.RaycastNonAlloc.html) |
| `QueryTriggerInteraction` | Whether a query hits triggers — the parameter that silently decides whether a line of sight test is blocked by a trigger volume | [Physics.Raycast](https://docs.unity3d.com/ScriptReference/Physics.Raycast.html) |
| `Collision.GetContact(int)` versus `contacts` | Indexed access avoids the array allocation `contacts` performs on every read | [Collision.GetContact](https://docs.unity3d.com/ScriptReference/Collision.GetContact.html) |
