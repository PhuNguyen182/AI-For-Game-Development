# Root Links — Unity Built-in 3D Physics (PhysX)

Source: the Unity Manual section roots listed below, as provided for this skill.
Covers: the whole skill — provenance and version anchor for every file in this folder.

Anchors every link in this folder to Unity's core Manual, published without a
version segment and therefore always resolving to the current release. Treat
that as the pin and re-verify any default against the Editor the project
builds with. The boundary worth stating up front is engine identity:
`UnityEngine.Physics` is PhysX on ordinary GameObjects, and neither
`UnityEngine.Physics2D` (`unity-2d-physics`) nor `com.unity.physics` (DOTS,
`unity-physics`) behaves like it despite sharing most type names.

| Root | Holds | Source |
|---|---|---|
| Physics overview | The parent page for every section below | [Physics](https://docs.unity3d.com/Manual/PhysicsOverview.html) |
| Character controllers | Capsule locomotion without a Rigidbody | [Character controllers](https://docs.unity3d.com/Manual/character-control-section.html) |
| Rigidbody physics | Dynamics, forces, interpolation, sleeping | [Rigidbody physics](https://docs.unity3d.com/Manual/rigidbody-physics-section.html) |
| Collision | Shapes, surfaces, events, detection modes | [Collision](https://docs.unity3d.com/Manual/collision-section.html) |
| Joints | The five built-in joint types | [Joints](https://docs.unity3d.com/Manual/joints-section.html) |
| Ragdoll physics | Wizard, stability, articulation | [Ragdoll physics](https://docs.unity3d.com/Manual/ragdoll-physics-section.html) |
| Cloth | Skinned-mesh fabric simulation | [Cloth](https://docs.unity3d.com/Manual/class-Cloth.html) |
| Physics optimization | Diagnosis and tuning | [Optimize the physics system](https://docs.unity3d.com/Manual/physics-optimization.html) |

## Topic → file map

| Topic | File | Source |
|---|---|---|
| Capsule locomotion and its tuning ratios | [character-controller.md](character-controller.md) | [Character controllers](https://docs.unity3d.com/Manual/CharacterControllers.html) |
| Body settings, forces, interpolation, sleep | [rigidbody-physics.md](rigidbody-physics.md) | [Rigidbody physics](https://docs.unity3d.com/Manual/RigidbodiesOverview.html) |
| Shapes, materials, contacts, layer matrix | [collision.md](collision.md) | [Collision](https://docs.unity3d.com/Manual/CollidersOverview.html) |
| Constraints, drives, limits, breaking | [joints.md](joints.md) | [Joints](https://docs.unity3d.com/Manual/Joints.html) |
| Ragdolls and articulated chains | [ragdoll-physics.md](ragdoll-physics.md) | [Joint and ragdoll stability](https://docs.unity3d.com/Manual/RagdollStability.html) |
| Fabric simulation | [cloth.md](cloth.md) | [Cloth](https://docs.unity3d.com/Manual/class-Cloth.html) |
| Profiling and tuning knobs | [physics-optimization.md](physics-optimization.md) | [Optimize the physics system](https://docs.unity3d.com/Manual/physics-optimization.html) |

## Scripting namespace

| Type | Source |
|---|---|
| `UnityEngine.Physics` | [Physics](https://docs.unity3d.com/ScriptReference/Physics.html) |
| `UnityEngine.Rigidbody` | [Rigidbody](https://docs.unity3d.com/ScriptReference/Rigidbody.html) |
| `UnityEngine.Collider` | [Collider](https://docs.unity3d.com/ScriptReference/Collider.html) |
| `UnityEngine.CharacterController` | [CharacterController](https://docs.unity3d.com/ScriptReference/CharacterController.html) |

3D physics types live directly in `UnityEngine`, not in a dedicated
sub-namespace — which is why a `using` line never disambiguates 2D from 3D and
the type name has to.
