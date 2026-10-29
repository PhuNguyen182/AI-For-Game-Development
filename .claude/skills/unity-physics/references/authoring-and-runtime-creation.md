# Authoring paths, code-created bodies, multiple worlds

Sources (under `manual/`): `built-in-components.html`, `custom-shapes.html`, `create-body.html`, `group-body.html`; `api/Unity.Physics.PhysicsWorldIndex.html`.

## Authoring paths
| Path | Notes |
|---|---|
| Built-in `UnityEngine` components | `Rigidbody`, `Box/Sphere/Capsule/MeshCollider`, `CharacterJoint`/`ConfigurableJoint`/`SpringJoint`/`FixedJoint`/`HingeJoint` bake into ECS physics data. Authoring convenience only: a `Rigidbody` in a subscene does not make the runtime PhysX |
| Unity Physics authoring | `PhysicsShapeAuthoring`, `PhysicsBodyAuthoring`; expose bevel radius and Force Unique |
| Runtime code | When bodies do not exist at design time |

## Creating a body in code
- Every body: `LocalTransform`, `LocalToWorld`, `PhysicsCollider`, `PhysicsWorldIndex`.
- Dynamic additionally: `PhysicsVelocity`, `PhysicsMass`, `PhysicsDamping`, `PhysicsGravityFactor`.
- The documented example computes mass from collider properties through unsafe pointers.

## Multiple worlds
- `PhysicsWorldIndex.Value` selects the world; `0` is main. Assign via `PhysicsWorldAuthoring` or the value at runtime.
- A `CustomPhysicsSystemGroup` built with the target index drives that world.
- Different indices are different shared-component values, so worlds also split ECS chunks.
