# Effectors 2D — Area, Point, Platform, Surface & Buoyancy

Sources: [Effectors 2D](https://docs.unity3d.com/Manual/2d-physics/effectors/effectors-2d-landing.html), [Platform Effector 2D reference](https://docs.unity3d.com/Manual/2d-physics/effectors/platform-effector-2d-reference.html), [Buoyancy Effector 2D reference](https://docs.unity3d.com/Manual/2d-physics/effectors/buoyancy-effector-2d-reference.html).
Covers: SKILL.md §4 — **"Reach for an effector only when the design asks for behaviour real physics would not produce"**.

An effector pairs with a `Collider2D` to impose designed, deliberately
non-physical behaviour on whatever interacts with it — the built-in answer to
one-way platforms, force volumes, magnets, conveyors, and fluid. All five
derive from `Effector2D`. The choice between them is a choice of *what shape
the force field has*, and getting that wrong produces motion that looks
plausible and behaves wrong.

**Critical caveat**: an effector affects nothing unless the collider it acts
through has **Used By Effector** enabled (`Collider2D.usedByEffector`). The
component can be added and fully tuned and still do absolutely nothing, with
no warning — check this before any other setting.

## Choosing one

| Effector | What it decides | Collider setup | Source |
|---|---|---|---|
| `AreaEffector2D` | A uniform directional force anywhere inside the area — wind, updraughts, force fields. The force does not fall off with distance | Trigger, so bodies overlap rather than collide | [Area Effector 2D](https://docs.unity3d.com/Manual/2d-physics/effectors/area-effector-2d-reference.html) |
| `PointEffector2D` | Attraction or repulsion relative to a source point, with distance scaling — magnets, singularities, explosion pushback | Trigger | [Point Effector 2D](https://docs.unity3d.com/Manual/2d-physics/effectors/point-effector-2d-reference.html) |
| `PlatformEffector2D` | One-way collision plus optional removal of side friction and bounce — the jump-up-through platform | **Not** a trigger: the platform must still physically block from the allowed side | [Platform Effector 2D](https://docs.unity3d.com/Manual/2d-physics/effectors/platform-effector-2d-reference.html) |
| `SurfaceEffector2D` | Tangential force along the contact surface toward a target speed — conveyor belts, moving walkways | Not a trigger: the effect is driven by real contact | [Surface Effector 2D](https://docs.unity3d.com/Manual/2d-physics/effectors/surface-effector-2d-reference.html) |
| `BuoyancyEffector2D` | Floating against a surface line, plus fluid drag and flow — water and other volumes a body settles in rather than is pushed out of | Trigger, with Used By Effector on | [Buoyancy Effector 2D](https://docs.unity3d.com/Manual/2d-physics/effectors/buoyancy-effector-2d-reference.html) |

## Shared filtering

| Property | What it decides | Source |
|---|---|---|
| `useColliderMask` / `colliderMask` | Which layers the effector acts on, independently of the collision matrix — how a wind zone pushes debris but not the player | [Effectors 2D](https://docs.unity3d.com/Manual/2d-physics/effectors/effectors-2d-landing.html) |
| `EffectorSelection2D` on `forceSource`/`forceTarget` | Whether a Point or Area effector measures from the body or from the collider centre — the difference shows on large or offset colliders | [Point Effector 2D](https://docs.unity3d.com/Manual/2d-physics/effectors/point-effector-2d-reference.html) |

## Platform effector specifics

| Property | What it decides | Source |
|---|---|---|
| Use One Way | Enables the one-way behaviour at all; without it the effector only strips friction and bounce | [Platform Effector 2D](https://docs.unity3d.com/Manual/2d-physics/effectors/platform-effector-2d-reference.html) |
| Surface Arc | The angular window counted as "the top" — too narrow and a body landing on a slope falls through, too wide and it cannot enter from the side | [Platform Effector 2D](https://docs.unity3d.com/Manual/2d-physics/effectors/platform-effector-2d-reference.html) |
| Use One Way Grouping | Treats all colliders on the platform as one for the one-way test, so a body cannot slip between two adjacent segments | [Platform Effector 2D](https://docs.unity3d.com/Manual/2d-physics/effectors/platform-effector-2d-reference.html) |
| Use Side Friction / Use Side Bounce | Whether the platform's sides grip or rebound — off is what stops a player sticking to a platform edge mid-jump | [Platform Effector 2D](https://docs.unity3d.com/Manual/2d-physics/effectors/platform-effector-2d-reference.html) |
| Side Arc | The angular window treated as "the side" for those two settings | [Platform Effector 2D](https://docs.unity3d.com/Manual/2d-physics/effectors/platform-effector-2d-reference.html) |

## Buoyancy specifics

| Property | What it decides | Source |
|---|---|---|
| Surface Level | The waterline in world Y — bodies above it are unaffected, so this and not the collider's top edge is what the fluid surface actually is | [Buoyancy Effector 2D](https://docs.unity3d.com/Manual/2d-physics/effectors/buoyancy-effector-2d-reference.html) |
| Density | Fluid density against body mass; a body denser than the fluid sinks, which is how floating versus sinking is authored | [Buoyancy Effector 2D](https://docs.unity3d.com/Manual/2d-physics/effectors/buoyancy-effector-2d-reference.html) |
| Linear / Angular Drag | Damping applied while submerged — what stops a floating body oscillating forever around the surface | [Buoyancy Effector 2D](https://docs.unity3d.com/Manual/2d-physics/effectors/buoyancy-effector-2d-reference.html) |
| Flow Angle / Magnitude / Variation | A current inside the volume, with optional randomised variation | [Buoyancy Effector 2D](https://docs.unity3d.com/Manual/2d-physics/effectors/buoyancy-effector-2d-reference.html) |

When the requirement is simply "push this in a direction", a script calling
`AddForce` on the body expresses it more directly than an effector — reach for
an effector when the *volume* is the thing being authored. See
[collider-2d.md](collider-2d.md) for the Used By Effector flag itself.
