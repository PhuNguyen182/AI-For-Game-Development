# Authoring Paths, Code-Created Bodies & Multiple Worlds

Sources: [Built-in physics authoring](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/built-in-components.html), [Creating bodies in code](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/create-body.html), [Multiple worlds](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/group-body.html).
Covers: SKILL.md §4 — **"State which authoring path each body uses"**.

The three ways a body comes into existence, and how simulation is partitioned.
General baking mechanics — when baking runs, how a `Baker<T>` works — are
`unity-ecs-architecture`'s.

## Authoring paths

| Path | What it decides | Source |
|---|---|---|
| Built-in `UnityEngine` components | `Rigidbody`, `BoxCollider`/`SphereCollider`/`CapsuleCollider`/`MeshCollider`, `CharacterJoint`/`ConfigurableJoint`/`SpringJoint`/`FixedJoint`/`HingeJoint` bake directly into ECS physics data — Editor-only authoring convenience that does **not** make the runtime PhysX | [Built-in authoring](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/built-in-components.html) |
| Unity Physics authoring components | `PhysicsShapeAuthoring`, `PhysicsBodyAuthoring` — the native alternative, exposing this engine's own settings such as bevel radius and Force Unique | [Custom shapes](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/custom-shapes.html) |
| Runtime creation in code | Build the component set directly — the path when bodies do not exist at design time | [Creating bodies in code](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/create-body.html) |

## Creating a body in code

| Requirement | What it decides | Source |
|---|---|---|
| Every body | `LocalTransform`, `LocalToWorld`, `PhysicsCollider`, `PhysicsWorldIndex` | [Creating bodies in code](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/create-body.html) |
| Dynamic bodies additionally | `PhysicsVelocity`, `PhysicsMass`, `PhysicsDamping`, `PhysicsGravityFactor` | [Creating bodies in code](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/create-body.html) |
| Mass computation | The documented example reaches collider properties through unsafe pointers to compute mass for dynamic bodies | [Creating bodies in code](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/create-body.html) |

## Multiple worlds

| Subject | What it decides | Source |
|---|---|---|
| `PhysicsWorldIndex.Value` | Selects the world; `0` is the main one | [PhysicsWorldIndex](https://docs.unity3d.com/Packages/com.unity.physics@6.6/api/Unity.Physics.PhysicsWorldIndex.html) |
| Assigning a world | Through `PhysicsWorldAuthoring` at authoring time, or the equivalent value at runtime | [Multiple worlds](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/group-body.html) |
| `CustomPhysicsSystemGroup` | A system group constructed with the target world index drives that world's simulation | [Multiple worlds](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/group-body.html) |
| Chunk consequence | Different world indices are different shared-component values, so worlds also partition ECS chunks | [Multiple worlds](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/group-body.html) |

**Critical caveat**: seeing `Rigidbody` and `BoxCollider` in a subscene does not
mean the project is running PhysX. Both engines accept the same authoring
components; only where the body ends up — an entity in a `PhysicsWorld`, or a
GameObject in the PhysX scene — settles which engine simulates it.
