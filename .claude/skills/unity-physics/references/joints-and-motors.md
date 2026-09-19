# Joints & Motors — Choosing by Degrees of Freedom

Sources: [Joints](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/custom-joints.html), [Motors](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/custom-motors.html).
Covers: SKILL.md §4 — **"Choose a joint or motor by the degrees of freedom the mechanic needs"**.

Seven joint types and four motor types, selected by what motion must remain
possible rather than by what the mechanic is called. The `float3`/`quaternion`
maths feeding their parameters is `unity-mathematics`.

## Joints

| Type | What it decides | Source |
|---|---|---|
| Ball and socket | Multi-axis rotation about a shared point — hips, shoulders | [Joints](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/custom-joints.html) |
| Hinge | Free rotation about one axis — wheels, doors | [Joints](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/custom-joints.html) |
| Limited hinge | One axis with angular limits — knees, fingers | [Joints](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/custom-joints.html) |
| Fixed | Fully constrains two bodies together | [Joints](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/custom-joints.html) |
| Prismatic | Sliding along a single translational axis | [Joints](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/custom-joints.html) |
| Ragdoll | Limited multi-axis motion tuned for character physics | [Joints](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/custom-joints.html) |
| Stiff spring | Maintains a target distance rather than a fixed pose | [Joints](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/custom-joints.html) |
| `Unity.Physics.JointData` factories | Each type is created by its own static function (`CreateBallAndSocket`, `CreateLimitedHinge`, …) with type-specific parameters | [PhysicsJoint](https://docs.unity3d.com/Packages/com.unity.physics@6.6/api/Unity.Physics.PhysicsJoint.html) |

## Motors

| Type | What it decides | Source |
|---|---|---|
| Position motor | Drives towards a target relative position along an axis | [Motors](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/custom-motors.html) |
| Linear velocity motor | Drives towards a target relative velocity along an axis | [Motors](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/custom-motors.html) |
| Rotation motor | Drives towards a target angle about an axis | [Motors](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/custom-motors.html) |
| Angular velocity motor | Drives towards a target rotational speed about an axis | [Motors](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/custom-motors.html) |
| Spring frequency and damping ratio | Every motor takes both; together they decide how fast it converges and whether it overshoots | [Motors](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/custom-motors.html) |

**Critical caveat**: Unity Physics's own authoring motor components are
documented as educational, not production. Create production motors from baked
GameObject joint components or the C# API directly.
