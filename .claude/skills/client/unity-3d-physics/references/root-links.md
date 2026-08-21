# Root Links — Unity Built-in 3D Physics (PhysX)

Given by the requester as the canonical entry points for this skill's documentation. These are Unity Manual **section** pages (table-of-contents pages, not single articles) — each one fans out into the child pages covered by this skill's other reference files. All URLs point at the current Unity Manual; re-verify against the project's installed Editor/LTS version, since manual content can shift slightly between LTS releases.

## Manual — section root pages

| # | Section | URL | Covered in |
|---|---|---|---|
| 1 | Character controllers | [character-control-section.html](https://docs.unity3d.com/Manual/character-control-section.html) | [character-controller.md](character-controller.md) |
| 2 | Rigidbody physics | [rigidbody-physics-section.html](https://docs.unity3d.com/Manual/rigidbody-physics-section.html) | [rigidbody-physics.md](rigidbody-physics.md) |
| 3 | Collision | [collision-section.html](https://docs.unity3d.com/Manual/collision-section.html) | [collision.md](collision.md) |
| 4 | Joints | [joints-section.html](https://docs.unity3d.com/Manual/joints-section.html) | [joints.md](joints.md) |
| 5 | Ragdoll physics | [ragdoll-physics-section.html](https://docs.unity3d.com/Manual/ragdoll-physics-section.html) | [ragdoll-physics.md](ragdoll-physics.md) |
| 6 | Physics optimization | [physics-optimization.html](https://docs.unity3d.com/Manual/physics-optimization.html) | [physics-optimization.md](physics-optimization.md) |
| 7 | Cloth | [class-Cloth.html](https://docs.unity3d.com/Manual/class-Cloth.html) | [cloth.md](cloth.md) |

## Parent context

| Page | URL | Note |
|---|---|---|
| Built-in 3D physics overview | [PhysicsOverview.html](https://docs.unity3d.com/Manual/PhysicsOverview.html) | Parent page of all seven sections above — the entry point into Unity's built-in PhysX-based 3D physics engine (`UnityEngine.Physics` namespace), as distinct from `UnityEngine.Physics2D` and from the separate `com.unity.physics` DOTS package covered by `unity-physics`. |

## Scripting API — namespace roots

| Namespace / type | URL | Note |
|---|---|---|
| `UnityEngine` (Physics-relevant types) | [ScriptReference/UnityEngine.html](https://docs.unity3d.com/ScriptReference/UnityEngine.html) | 3D physics types (`Rigidbody`, `Collider`, `CharacterController`, `Joint`, `Cloth`, etc.) live directly in `UnityEngine`, not a dedicated sub-namespace. |
| `Physics` (static class) | [ScriptReference/Physics.html](https://docs.unity3d.com/ScriptReference/Physics.html) | Global physics settings and static query methods (`Raycast`, `SphereCast`, `IgnoreCollision`, `gravity`, layer collision matrix access). |

All other reference files in this skill link to the specific child pages and Scripting API pages under these roots.
