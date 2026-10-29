# Effectors 2D

Sources: Manual `2d-physics/effectors/`. All five derive from `Effector2D`; the choice is the shape of the force field.

An effector does nothing unless the collider it acts through has **Used By Effector** (`Collider2D.usedByEffector`) on, with no warning. Check this first.

| Effector | Decides | Collider |
|---|---|---|
| `AreaEffector2D` | Uniform directional force inside the area, no distance falloff (wind, updraught) | Trigger |
| `PointEffector2D` | Attraction/repulsion from a point with distance scaling (magnet, explosion pushback) | Trigger |
| `PlatformEffector2D` | One-way collision, optional side friction/bounce removal | **Not** trigger: must still block from the allowed side |
| `SurfaceEffector2D` | Tangential force along the surface toward a target speed (conveyor) | Not trigger: driven by real contact |
| `BuoyancyEffector2D` | Floating against a surface line plus fluid drag/flow | Trigger |

## Shared filtering

| Property | Decides |
|---|---|
| `useColliderMask` / `colliderMask` | Layers the effector acts on, independent of the matrix (wind pushes debris, not the player) |
| `EffectorSelection2D` on `forceSource`/`forceTarget` | Measure from body or collider centre; matters on large or offset colliders |

## Platform

| Property | Decides |
|---|---|
| Use One Way | Without it the effector only strips friction/bounce |
| Surface Arc | Angular window counted as "top": too narrow and a body landing on a slope falls through, too wide and it cannot enter from the side |
| Use One Way Grouping | Treats all colliders on the platform as one so a body cannot slip between adjacent segments |
| Use Side Friction / Bounce, Side Arc | Off stops a player sticking to a platform edge mid-jump |

## Buoyancy

| Property | Decides |
|---|---|
| Surface Level | Waterline in world Y, not the collider's top edge; bodies above it are unaffected |
| Density | Against body mass; denser than fluid sinks |
| Linear / Angular Drag | Damping while submerged: stops endless oscillation at the surface |
| Flow Angle / Magnitude / Variation | A current inside the volume |

Plain "push in a direction" is a script `AddForce`; use an effector when the volume is the thing authored.
