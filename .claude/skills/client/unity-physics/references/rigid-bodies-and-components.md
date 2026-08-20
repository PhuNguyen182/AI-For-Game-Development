# Rigid Bodies & Core Physics Components

Covers SKILL.md step 3 (choosing a rigid body's component set by body type).

## Manual
- [Principal data components](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/core-components.html) — entry point listing the components covered by this section: rigid bodies, colliders, joints, motors.
- [Rigid bodies](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/concepts-data.html) — the ECS component set for a rigid body: `PhysicsCollider` (shape, needed for any body that can collide), `PhysicsVelocity` (linear/angular velocity, required for any moving body), `PhysicsMass` (center of mass and moment of inertia, for dynamic bodies), optional `PhysicsDamping` (per-step velocity reduction/drag) and `PhysicsGravityFactor` (per-body gravity multiplier), `PhysicsCustomTags` (custom filter flags), `PhysicsSolverType` (Iterative vs. Direct solver), and `PhysicsWorldIndex` (a required shared component denoting which physics world the entity belongs to). All bodies also need `Unity.Transforms` components — dynamic bodies need `LocalTransform`, static bodies need `LocalTransform` or `LocalToWorld`.
- [Physics Step: Configuring your physics simulation](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/component-step.html) — the single, scene-global `PhysicsStep` component: global gravity (overridable per-body via `PhysicsGravityFactor`), optional gyroscopic torque simulation, solver iteration count and substep count (accuracy vs. performance trade-off), multithreading toggle, collision tolerance, depenetration velocity limits, broadphase options, and Direct-solver contact stiffness/damping/joint parameters. Only one `PhysicsStep` component should exist per scene.

## Scripting API
- [`Unity.Physics.PhysicsMass`](https://docs.unity3d.com/Packages/com.unity.physics@6.6/api/Unity.Physics.PhysicsMass.html) — mass properties struct (inverse mass, inverse inertia tensor, center of mass).
- [`Unity.Physics.PhysicsVelocity`](https://docs.unity3d.com/Packages/com.unity.physics@6.6/api/Unity.Physics.PhysicsVelocity.html) — linear/angular velocity struct.

For creating this component set entirely in code at runtime (as opposed to authoring/baking it), see [authoring-and-runtime-creation.md](authoring-and-runtime-creation.md).
