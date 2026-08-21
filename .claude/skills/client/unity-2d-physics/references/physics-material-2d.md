# PhysicsMaterial2D — Friction, Bounciness & Combine Priority

Source: [Physics Material 2D reference](https://docs.unity3d.com/Manual/2d-physics/physics-material-2d-reference.html).
Covers: SKILL.md §4 — **"Assign a `PhysicsMaterial2D` asset rather than tuning friction per collider"**.

A Physics Material 2D asset (**Assets > Create > 2D > Physics Material 2D**)
carries the friction and bounciness of a surface. The fact that decides how it
is used: a contact combines *both* colliders' materials, and when their
combine modes disagree the higher-priority mode wins — so a surface can never
be reasoned about from its own asset alone.

## Properties

| Property | What it decides | Source |
|---|---|---|
| Friction | 0 is frictionless ice, 1 is high grip; the coefficient applied along the contact tangent | [Physics Material 2D reference](https://docs.unity3d.com/Manual/2d-physics/physics-material-2d-reference.html) |
| Bounciness | 0 absorbs the impact, 1 rebounds with no energy loss — values above the design's intent are the usual cause of objects that never settle | [Physics Material 2D reference](https://docs.unity3d.com/Manual/2d-physics/physics-material-2d-reference.html) |
| Friction Combine | How the pair's friction values combine; **Mean** is the default | [Physics Material 2D reference](https://docs.unity3d.com/Manual/2d-physics/physics-material-2d-reference.html) |
| Bounce Combine | How the pair's bounciness values combine; **Maximum** is the default, which is why one bouncy object makes every contact bouncy | [Physics Material 2D reference](https://docs.unity3d.com/Manual/2d-physics/physics-material-2d-reference.html) |

## Combine modes, in priority order

| Mode | Result | Priority | Source |
|---|---|---|---|
| `Average` | Arithmetic mean of the two values | Lowest | [Physics Material 2D reference](https://docs.unity3d.com/Manual/2d-physics/physics-material-2d-reference.html) |
| `Mean` | Geometric mean of the two values | Second | [Physics Material 2D reference](https://docs.unity3d.com/Manual/2d-physics/physics-material-2d-reference.html) |
| `Multiply` | Product of the two values | Third | [Physics Material 2D reference](https://docs.unity3d.com/Manual/2d-physics/physics-material-2d-reference.html) |
| `Minimum` | The smaller value — the mode that lets one slippery surface win | Fourth | [Physics Material 2D reference](https://docs.unity3d.com/Manual/2d-physics/physics-material-2d-reference.html) |
| `Maximum` | The larger value — the mode that lets one grippy or bouncy surface win | Highest | [Physics Material 2D reference](https://docs.unity3d.com/Manual/2d-physics/physics-material-2d-reference.html) |

When the two materials specify different modes, the one higher in this list
decides. A material set to `Average` never takes effect against a material set
to `Maximum`.

## Assignment and scripting

| Member | What it decides | Source |
|---|---|---|
| `Collider2D.sharedMaterial` | The material for that collider. `Collider2D` has **no** per-instance `material` property, unlike 3D `Collider` — writing here edits the shared asset and therefore every collider using it | [Collider2D.sharedMaterial](https://docs.unity3d.com/ScriptReference/Collider2D-sharedMaterial.html) |
| `Rigidbody2D.sharedMaterial` | A default applied to every attached collider that has none of its own — the efficient place to set one surface for a whole body | [Rigidbody2D.sharedMaterial](https://docs.unity3d.com/ScriptReference/Rigidbody2D-sharedMaterial.html) |
| `Collider2D.friction` / `bounciness` / `frictionCombine` / `bounceCombine` | Per-collider values used when no material asset is assigned — fine for a one-off, but they cannot be reused or tuned centrally | [Collider2D.friction](https://docs.unity3d.com/ScriptReference/Collider2D-friction.html) |
| `PhysicsMaterial2D.GetCombinedValues(...)` | Computes the effective value a given pair would produce — the way to confirm a combine outcome without running the scene | [PhysicsMaterial2D](https://docs.unity3d.com/ScriptReference/PhysicsMaterial2D.html) |

For which collider carries the material, see [collider-2d.md](collider-2d.md).
