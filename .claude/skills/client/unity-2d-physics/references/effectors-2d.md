# Effectors — Area, Point, Platform, Surface & Buoyancy

Covers SKILL.md step 5 (choosing/configuring an effector for non-physically-realistic behavior: one-way platforms, area forces, surface friction/conveyor, buoyancy).

## Overview

An Effector 2D component pairs with a `Collider2D` to apply designer-authored, non-physically-realistic forces or collision behavior to any other `Collider2D`/`Rigidbody2D` that interacts with it — direct the forces of physics when GameObject colliders come into contact with each other, rather than letting Box2D's default rigid-body response decide the outcome. This is the built-in tool for gameplay-authored physics feel: wind/gravity zones, magnets, one-way platforms, conveyor belts, and buoyant fluid volumes, without hand-rolling a per-frame force/velocity script for each.

Unity ships five effector types — Area, Buoyancy, Point, Platform, and Surface — all inheriting from the common `Effector2D` base class.

**Critical setup requirement:** an effector does nothing to a `Collider2D` unless that collider has **Used By Effector** enabled (`Collider2D.usedByEffector = true`). This is the single most commonly missed step — the component can be added, fully configured, and still silently produce no effect if the affected collider's `usedByEffector` flag is left off. In addition, most effector types expect a specific trigger configuration on the collider(s) involved (see each effector's own section below for its specific trigger requirement) — Platform Effector 2D is the exception, since its platform collider is typically left as a non-trigger so it still physically blocks contact.

## Manual

| Page | URL | Covers |
|---|---|---|
| Effectors 2D | https://docs.unity3d.com/Manual/2d-physics/effectors/effectors-2d-landing.html | Landing page; conceptual overview and links to all five effector reference pages |
| Area Effector 2D reference | https://docs.unity3d.com/Manual/2d-physics/effectors/area-effector-2d-reference.html | Properties for arbitrarily varying force and angle magnitude within an area |
| Point Effector 2D reference | https://docs.unity3d.com/Manual/2d-physics/effectors/point-effector-2d-reference.html | Properties for attracting/repulsing against a source point |
| Platform Effector 2D reference | https://docs.unity3d.com/Manual/2d-physics/effectors/platform-effector-2d-reference.html | Properties for one-way collisions and other platform behavior |
| Surface Effector 2D reference | https://docs.unity3d.com/Manual/2d-physics/effectors/surface-effector-2d-reference.html | Properties for conveyor-belt-style surface tangent forces |
| Buoyancy Effector 2D reference | https://docs.unity3d.com/Manual/2d-physics/effectors/buoyancy-effector-2d-reference.html | Properties for simulating buoyancy, fluid flow, and fluid drag |

## Effector2D base API

Members shared by every effector type (`AreaEffector2D`, `PointEffector2D`, `PlatformEffector2D`, `SurfaceEffector2D`, `BuoyancyEffector2D` all inherit from `Effector2D`).

| Member | Description |
|---|---|
| `useColliderMask` | Should the collider mask be used, or the global collision matrix? |
| `colliderMask` | The mask used to select specific layers allowed to interact with the effector. |

The `Collider2D.usedByEffector` flag itself is not a member of `Effector2D` — it lives on the `Collider2D` component that the effector acts through (see Overview above and [collider-2d.md](collider-2d.md)).

## Area Effector 2D

Applies a force within an area defined by the attached `Collider2D` when another (target) `Collider2D` comes into contact with the effector — the general-purpose tool for directional force zones: wind tunnels, gravity zones, force fields, push/pull volumes.

| Member | Description |
|---|---|
| `useGlobalAngle` | Should `forceAngle` use global (world) space, or local space relative to the object? |
| `forceAngle` | The angle of the force to be applied. |
| `forceMagnitude` | The magnitude of the force to be applied. |
| `forceVariation` | The variation of the magnitude of the force to be applied. |
| `forceTarget` (`EffectorSelection2D`) | The target for where the effector applies any force — Collider (can generate torque) or Rigidbody (applied at center of mass, no torque). |
| `linearDamping` | The linear damping to apply to rigid-bodies. |
| `angularDamping` | The angular damping to apply to rigid-bodies. |

Collider setup: the collider(s) the Area Effector 2D acts through are typically set as triggers, so other colliders can overlap with it (rather than physically collide) to have forces applied. A non-trigger collider still works, but forces are then only applied on contact rather than on overlap.

## Point Effector 2D

Attracts or repels against a source point, defined as either the position of a Rigidbody2D or the center of a Collider2D — the tool for magnets, black holes/singularities, explosion knockback zones, and pull/push-to-point mechanics.

| Member | Description |
|---|---|
| `forceMagnitude` | The magnitude of the force to be applied. |
| `forceVariation` | The variation of the magnitude of the force to be applied. |
| `distanceScale` | The scale applied to the calculated distance between source and target. |
| `forceSource` (`EffectorSelection2D`) | The source used to calculate the centroid point of the effector; distance to the target is measured from this point. |
| `forceTarget` (`EffectorSelection2D`) | The target for where the effector applies any force — Collider position (can generate torque) or Rigidbody center of mass. |
| `forceMode` (`EffectorForceMode2D`) | The mode used to apply the effector force — see enum table below. |
| `linearDamping` | The linear damping to apply to rigid-bodies. |
| `angularDamping` | The angular damping to apply to rigid-bodies. |

Collider setup: colliders used with the Point Effector 2D would typically be set as triggers, so other colliders can overlap with it to have forces applied; non-triggers still work, but forces are then only applied when colliders come into contact with it.

## Platform Effector 2D

Applies platform-specific, non-physically-realistic collision behavior — one-way collisions (jump up through, land on top of, from below), and removal of side friction/bounce — the standard tool for one-way/jump-through platforms.

| Member | Description |
|---|---|
| `useOneWay` | Should the one-way collision behavior be used? |
| `useOneWayGrouping` | Ensures that all contacts controlled by the one-way behavior act the same, for platforms built from multiple colliders that need to behave as one group. |
| `surfaceArc` | The angle of an arc, centered on the local "up," that defines the surface which doesn't allow colliders to pass (used by the one-way behavior). |
| `useSideFriction` | Should friction be used on the platform sides? |
| `useSideBounce` | Should bounce be used on the platform sides? |
| `sideArc` | The angle of an arc, centered on the local "left" and "right," that defines the sides of the platform. |
| `rotationalOffset` | The rotational offset angle from the local "up." |

Collider setup: the collider(s) used with the Platform Effector 2D are typically **not** set as triggers, so other colliders can physically collide with it (unlike Area/Point Effector, where the interacting collider is usually a trigger) — the platform must still physically block movement from the allowed side(s) while one-way behavior lets bodies pass through the disallowed side(s).

## Surface Effector 2D

Applies tangential force along the surface of the colliders it acts through, driving contacting bodies toward a target surface speed — the standard tool for conveyor belts and moving-surface mechanics.

| Member | Description |
|---|---|
| `speed` | The speed to be maintained along the surface. |
| `speedVariation` | Speed variation (from zero to this value) added to the base speed. |
| `forceScale` | The scale of the impulse force applied while attempting to reach the surface speed (0–1; entering 1 applies full force, which can counteract other forces acting on the body). |
| `useContactForce` | Should the impulse force be applied at the contact point (rather than at the body's center), which may cause rotation? |
| `useFriction` | Should friction be used for any contact with the surface? |
| `useBounce` | Should bounce be used for any contact with the surface? |

Collider setup: colliders used with the Surface Effector 2D are set as non-triggers, so other colliders can physically come into contact with the surface — the conveyor effect is driven by real contact, not overlap.

## Buoyancy Effector 2D

Defines simple fluid behavior — floating, plus fluid drag and flow — for any body that enters the area below a defined fluid surface line. The standard tool for water/fluid volumes a Rigidbody2D can float, sink, or drift in.

| Member | Description |
|---|---|
| `surfaceLevel` | Defines an arbitrary horizontal line representing the fluid surface; buoyancy forces apply to whatever is below it. Specified as a world-space offset along the y-axis, scaled by the GameObject's Transform. |
| `density` | The density of the fluid used to calculate buoyancy forces. Colliders with a higher density than this sink; colliders with a lower density float. |
| `linearDamping` | The drag coefficient affecting positional (linear) movement of a GameObject; only applies while inside the fluid. |
| `angularDamping` | The drag coefficient affecting rotational (angular) movement of a GameObject; only applies while inside the fluid. |
| `flowAngle` | The world-space angle, in degrees, for the direction of fluid flow. |
| `flowMagnitude` | The magnitude of the fluid-flow force; a negative value reverses the flow direction by 180 degrees. |
| `flowVariation` | Random variation applied to the fluid-flow force. |

Collider setup: as with the other overlap-driven effectors (Area, Point), the fluid-volume collider the Buoyancy Effector 2D is attached to needs `Used By Effector` enabled to take effect; the live Manual reference page for this effector does not spell out a distinct trigger requirement beyond that shared baseline (see Overview above).

### EffectorSelection2D

Used by `forceSource`/`forceTarget` on Point Effector 2D and `forceTarget` on Area Effector 2D, to choose whether the source/target point is defined by the Rigidbody2D or the Collider2D.

| Member | Description |
|---|---|
| `Rigidbody` | The source/target is defined by the Rigidbody2D. |
| `Collider` | The source/target is defined by the Collider2D. |

### EffectorForceMode2D

Used by `PointEffector2D.forceMode` to choose how the point effector's force falls off with distance.

| Member | Description |
|---|---|
| `Constant` | The force is applied at a constant rate, independent of distance. |
| `InverseLinear` | The force is applied inverse-linear relative to the distance from the source point. |
| `InverseSquared` | The force is applied inverse-squared relative to the distance from the source point. |

For the Collider2D "Used By Effector" flag and trigger configuration, see [collider-2d.md](collider-2d.md). For Rigidbody2D body types effectors act on, see [rigidbody-2d.md](rigidbody-2d.md).
