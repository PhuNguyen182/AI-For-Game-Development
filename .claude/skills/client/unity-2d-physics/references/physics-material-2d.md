# PhysicsMaterial2D — Friction & Bounciness Surface Properties

Covers SKILL.md step 5 (configuring collider friction/bounciness).

## Overview

A Physics Material 2D is an asset (created via `Assets > Create > 2D > Physics Material 2D`) that adjusts the friction and bounce that occur between 2D physics objects when they collide. It attaches by assigning it to the `Material` property of either a `Collider2D` component (via `Collider2D.sharedMaterial`) or a `Rigidbody2D` component (via `Rigidbody2D.sharedMaterial`, which applies the material to all `Collider2D` shapes attached to that Rigidbody2D). Unity notes this asset is the 2D equivalent of the 3D `PhysicsMaterial` asset.

When two colliding `Collider2D` components each have their own `PhysicsMaterial2D` assigned, Unity combines the two materials' `friction` and `bounciness` values independently, each using its own `PhysicsMaterialCombine2D` algorithm (`frictionCombine` and `bounceCombine`). If the two materials specify different combine modes, the mode with the higher priority wins — priority order, lowest to highest: `Average` < `Mean` < `Multiply` < `Minimum` < `Maximum`. For example, if one material uses `Average` and the other uses `Maximum`, the combined result uses `Maximum` because it has higher priority.

## Manual

| Page | URL | Covers |
|---|---|---|
| Physics Material 2D reference | https://docs.unity3d.com/Manual/2d-physics/physics-material-2d-reference.html | Asset creation, Friction/Bounciness/Friction Combine/Bounce Combine properties and their combine-mode options |

## Physics Material 2D asset properties

| Property | Type | Description |
|---|---|---|
| Friction | float (0–1) | Coefficient of friction for this collider. 0 = no friction (like ice), 1 = very high friction (like rubber). |
| Bounciness | float (0–1) | Degree to which collisions rebound from the surface. 0 = no bounce, 1 = perfect bounce with no loss of energy. |
| Friction Combine | `PhysicsMaterialCombine2D` | How to combine both materials' friction values when two colliders interact. Options: `Average` (average of the two values), `Mean` (geometric mean of the two values — **default**), `Multiply` (product of the two values), `Minimum` (smaller value), `Maximum` (larger value). |
| Bounce Combine | `PhysicsMaterialCombine2D` | How to combine both materials' bounciness values when two colliders interact. Same five options as Friction Combine, but `Maximum` is the **default** here. |

## Scripting API

| Member | Description |
|---|---|
| `PhysicsMaterial2D` (class) | Asset type that specifies the surface characteristics of a `Collider2D`. |
| `friction` | Coefficient of friction. |
| `bounciness` | Coefficient of restitution. |
| `frictionCombine` | Determines how the effective friction is calculated when two `Collider2D` come into contact. |
| `bounceCombine` | Determines how the effective bounciness is calculated when two `Collider2D` come into contact. |
| `PhysicsMaterial2D.GetCombinedValues(...)` (static) | Calculates the effective value used when two `Collider2D` with their own `PhysicsMaterial2D` come into contact. |
| `PhysicsMaterialCombine2D` (enum) | `Average`, `Mean`, `Multiply`, `Minimum`, `Maximum` — the combine algorithm selected for `frictionCombine`/`bounceCombine`. |

Assignment happens on the collider or body side, not on the material itself: `Collider2D.sharedMaterial` sets "The PhysicsMaterial2D that is applied to this collider," and `Rigidbody2D.sharedMaterial` sets "The PhysicsMaterial2D that is applied to all Collider2D attached to this Rigidbody2D." Unlike the 3D `Collider` base class, `Collider2D` exposes only `sharedMaterial` — there is no separate per-instance `material` property.

For attaching a material to a specific collider shape, see [collider-2d.md](collider-2d.md).
