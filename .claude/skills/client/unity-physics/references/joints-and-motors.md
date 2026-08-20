# Joints & Motors

Covers SKILL.md step 5 (choosing joints/motors by required degrees of freedom).

## Manual
- [Joints](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/custom-joints.html) — the seven pre-built joint types: **ball and socket** (multi-axis rotation, e.g. hips/shoulders), **hinge** (free single-axis rotation, e.g. wheels), **limited hinge** (restricted single-axis rotation, e.g. knees/fingers), **fixed** (fully constrains two bodies together), **prismatic** (single-axis sliding), **ragdoll** (limited multi-axis motion for character physics), **stiff spring** (maintains a target distance). Each joint type has a static creation function on `Unity.Physics.JointData` (e.g. `CreateBallAndSocket`, `CreateLimitedHinge()`); input parameters vary by type.
- [Motors](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/custom-motors.html) — motors are `PhysicsJoint`s with one driven constraint that move a body toward a target: **position motor** (drives to a target relative position along an axis), **linear velocity motor** (drives to a target relative velocity along an axis), **rotation motor** (drives to a target angle around an axis), **angular velocity motor** (drives to a target rotational speed around an axis). Every motor type takes spring frequency and damping ratio parameters controlling convergence toward the target. Creatable via GameObject joint components (baked), the C# API directly, or Unity Physics's own authoring motor components (explicitly noted as educational-only, not for production).

## Scripting API
- [`Unity.Physics.PhysicsJoint`](https://docs.unity3d.com/Packages/com.unity.physics@6.6/api/Unity.Physics.PhysicsJoint.html) — the runtime joint component wrapping a `JointData` created via one of the static factory functions above.

For rotation/position target math (`float3`/`quaternion`), see `unity-mathematics` — this skill owns which joint/motor type to use, not the vector/quaternion math feeding it.
