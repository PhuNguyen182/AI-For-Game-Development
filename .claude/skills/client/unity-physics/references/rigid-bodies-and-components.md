# Rigid Bodies, Their Components & `PhysicsStep`

Sources: [Rigid bodies](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/concepts-data.html), [Physics Step](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/component-step.html).
Covers: SKILL.md §4 — **"Choose the body's component set from its body type"**, **"Tune `PhysicsStep` once per scene, not per body"**.

The component set is not descriptive — it is what decides how the simulation
treats a body. Creating this set in code rather than by baking is
[authoring-and-runtime-creation.md](authoring-and-runtime-creation.md).

## Body components

| Component | What it decides | Source |
|---|---|---|
| `PhysicsCollider` | The shape; required for anything that can collide at all | [Rigid bodies](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/concepts-data.html) |
| `PhysicsVelocity` | Linear and angular velocity — required for any moving body, and part of what marks a body as simulated rather than fixed | [PhysicsVelocity](https://docs.unity3d.com/Packages/com.unity.physics@6.6/api/Unity.Physics.PhysicsVelocity.html) |
| `PhysicsMass` | Centre of mass and inertia tensor — its presence alongside velocity is what makes a body dynamic | [PhysicsMass](https://docs.unity3d.com/Packages/com.unity.physics@6.6/api/Unity.Physics.PhysicsMass.html) |
| `PhysicsDamping` | Per-step velocity reduction; optional per-body drag | [Rigid bodies](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/concepts-data.html) |
| `PhysicsGravityFactor` | Per-body multiplier over the scene's global gravity — the sanctioned way to make one body fall differently | [Rigid bodies](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/concepts-data.html) |
| `PhysicsCustomTags` | Custom filter flags — the cheap alternative to intercepting the pipeline | [Rigid bodies](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/concepts-data.html) |
| `PhysicsSolverType` | Iterative or Direct solver for this body | [Rigid bodies](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/concepts-data.html) |
| `PhysicsWorldIndex` | Required **shared** component naming the body's world — being shared, it also partitions chunks | [PhysicsWorldIndex](https://docs.unity3d.com/Packages/com.unity.physics@6.6/api/Unity.Physics.PhysicsWorldIndex.html) |
| Transform components | Dynamic bodies need `LocalTransform`; static bodies need `LocalTransform` or `LocalToWorld` | [Rigid bodies](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/concepts-data.html) |

## `PhysicsStep` — one per scene

| Setting | What it decides | Source |
|---|---|---|
| Gravity | The scene-global value every body inherits unless it carries `PhysicsGravityFactor` | [Physics Step](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/component-step.html) |
| Solver iteration and substep counts | The accuracy-versus-cost dial for the entire simulation — raising it fixes soft or jittery stacks at a global price | [Physics Step](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/component-step.html) |
| Multithreading toggle | Whether the simulation spreads across worker threads | [Physics Step](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/component-step.html) |
| Collision tolerance, depenetration limits, broadphase options | Contact generation and recovery behaviour | [Physics Step](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/component-step.html) |
| Gyroscopic torque | Optional extra fidelity for spinning bodies | [Physics Step](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/component-step.html) |

**Critical caveat**: only one `PhysicsStep` should exist per scene. A second
one is not additive configuration — it is ambiguity about which settings the
simulation is actually running.
