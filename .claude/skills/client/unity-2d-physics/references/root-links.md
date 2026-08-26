# Root Links — Unity Built-in 2D Physics (Box2D)

Source: the Unity Manual section roots listed below, as provided for this skill.
Covers: the whole skill — provenance and version anchor for every file in this folder.

Anchors every link in this folder to Unity's core Manual, whose URLs carry no
version segment and always resolve to the currently published Manual. Treat
that as the pin: confirm a default or field name against the Editor the
project builds with before relying on it. The boundary this file exists to
state is engine identity — `UnityEngine.Physics2D` is Box2D on ordinary
GameObjects, and neither `UnityEngine.Physics` (PhysX, `unity-3d-physics`) nor
`com.unity.physics` (DOTS, `unity-physics`) shares its behaviour despite
sharing most of its vocabulary.

| Root | Holds | Source |
|---|---|---|
| 2D physics overview | Where 2D and 3D physics differ, and why they cannot be mixed | [2D and 3D physics](https://docs.unity3d.com/Manual/2d-and-3d-physics.html) |
| Rigidbody 2D | Body types and every dynamics setting | [Rigidbody 2D](https://docs.unity3d.com/Manual/2d-physics/rigidbody/rigidbody-2d-landing.html) |
| Collider 2D | All six shapes and the composite | [Collider 2D](https://docs.unity3d.com/Manual/2d-physics/collider/collider-2d-landing.html) |
| Effectors 2D | The five designed-behaviour effectors | [Effectors 2D](https://docs.unity3d.com/Manual/2d-physics/effectors/effectors-2d-landing.html) |
| Joints 2D | All nine constraint types | [2D Joints](https://docs.unity3d.com/Manual/2d-physics/joints/2d-joints-landing.html) |

## Topic → file map

| Topic | File | Source |
|---|---|---|
| Body type, damping, interpolation, sleep, movement | [rigidbody-2d.md](rigidbody-2d.md) | [Rigidbody 2D](https://docs.unity3d.com/Manual/2d-physics/rigidbody/rigidbody-2d-landing.html) |
| Shapes, contacts, composite, layer matrix | [collider-2d.md](collider-2d.md) | [Collider 2D](https://docs.unity3d.com/Manual/2d-physics/collider/collider-2d-landing.html) |
| Friction, bounciness, combine modes | [physics-material-2d.md](physics-material-2d.md) | [Physics Material 2D reference](https://docs.unity3d.com/Manual/2d-physics/physics-material-2d-reference.html) |
| One-way platforms, force zones, conveyors, buoyancy | [effectors-2d.md](effectors-2d.md) | [Effectors 2D](https://docs.unity3d.com/Manual/2d-physics/effectors/effectors-2d-landing.html) |
| Constraints, motors, limits, breaking | [joints-2d.md](joints-2d.md) | [2D Joints](https://docs.unity3d.com/Manual/2d-physics/joints/2d-joints-landing.html) |
| Continuous force and torque | [constant-force-2d.md](constant-force-2d.md) | [Constant Force 2D reference](https://docs.unity3d.com/Manual/2d-physics/constant-force-2d-reference.html) |

## Scripting namespace

| Type | Source |
|---|---|
| `UnityEngine.Physics2D` | [Physics2D](https://docs.unity3d.com/ScriptReference/Physics2D.html) |
| `UnityEngine.Rigidbody2D` | [Rigidbody2D](https://docs.unity3d.com/ScriptReference/Rigidbody2D.html) |
| `UnityEngine.Collider2D` | [Collider2D](https://docs.unity3d.com/ScriptReference/Collider2D.html) |

Every other link in this folder is a page under these roots. Because the core
Manual is published unversioned, any default value quoted here is current at
authoring time only.
