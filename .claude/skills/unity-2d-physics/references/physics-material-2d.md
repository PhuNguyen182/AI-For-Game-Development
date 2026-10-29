# PhysicsMaterial2D

Source: Manual `2d-physics/physics-material-2d-reference.html`; API `Collider2D`, `Rigidbody2D`, `PhysicsMaterial2D`. Asset: Assets > Create > 2D > Physics Material 2D.

A contact combines **both** colliders' materials; when combine modes differ, the higher-priority mode wins, so a surface cannot be judged from its own asset.

| Property | Decides |
|---|---|
| Friction | 0 = ice, 1 = high grip |
| Bounciness | 0 absorbs, 1 loses no energy; values above intent are the usual cause of objects that never settle |
| Friction Combine | Default **Mean** |
| Bounce Combine | Default **Maximum**: one bouncy object makes every contact bouncy |

## Combine priority (lowest to highest)

| Mode | Result |
|---|---|
| `Average` | Arithmetic mean |
| `Mean` | Geometric mean |
| `Multiply` | Product |
| `Minimum` | Smaller value: one slippery surface wins |
| `Maximum` | Larger value: one grippy/bouncy surface wins |

`Average` never takes effect against `Maximum`.

## Assignment

| Member | Decides |
|---|---|
| `Collider2D.sharedMaterial` | Has **no** per-instance `material` (unlike 3D): writing edits the shared asset for every collider using it |
| `Rigidbody2D.sharedMaterial` | Default for attached colliders with none of their own |
| `Collider2D.friction` / `bounciness` / `*Combine` | Per-collider values when no asset is assigned; not reusable |
| `PhysicsMaterial2D.GetCombinedValues(...)` | Effective value for a pair, without running the scene |
