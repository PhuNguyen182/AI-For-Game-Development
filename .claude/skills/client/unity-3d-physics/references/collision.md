# Collision — Colliders, Surfaces & Events

Covers SKILL.md step 5 (choosing collider shapes, PhysicsMaterial, trigger vs. solid, and the layer collision matrix).

## Overview

A collider is a Unity component that defines the shape of a GameObject for the purposes of physical collisions — it's an invisible component that doesn't need to match the GameObject's rendered mesh shape. Collisions occur when configured GameObjects occupy the same physical space; Rigidbody components paired with colliders determine how objects behave during that overlap.

A collider becomes a **trigger** when its `isTrigger` property is enabled: instead of producing a physical collision response, it detects passing colliders and fires `OnTrigger` events. For any interaction (physical or trigger) to be reported at all, at least one of the two GameObjects involved must have a Rigidbody attached.

## Manual

| Page | URL | Covers |
|---|---|---|
| Introduction to collision | https://docs.unity3d.com/Manual/CollidersOverview.html | What a collider is, static/Rigidbody/trigger collider categories |
| Introduction to collider types | https://docs.unity3d.com/Manual/collider-types-introduction.html | Static, dynamic, and kinematic collider definitions |
| Collider shapes | https://docs.unity3d.com/Manual/collider-shapes.html | Box/Sphere/Capsule/Mesh/Wheel/Terrain/Compound shapes, accuracy vs. cost trade-off |
| Collider surfaces | https://docs.unity3d.com/Manual/collider-surfaces.html | PhysicsMaterial (friction, bounciness, combine modes) |
| Collider interactions | https://docs.unity3d.com/Manual/collider-interactions.html | `OnCollision` vs `OnTrigger` event families |
| Interaction between collider types | https://docs.unity3d.com/Manual/collider-types-interaction.html | Which static/dynamic/kinematic/trigger pairings produce which events |
| Collision detection | https://docs.unity3d.com/Manual/collision-detection.html | Discrete vs. continuous (CCD) algorithm selection |

## Collider types & body pairing behavior

Per-collider category, from `collider-types-introduction.html`:

| Category | Definition |
|---|---|
| Static collider | Collider with no Rigidbody attached. "Doesn't respond to simulated physics forces." Other colliders can hit it, but it never moves in response. |
| Dynamic collider | Collider + Rigidbody with `Is Kinematic` off. "Respond to simulated physics forces" — can collide with anything (including static colliders) and can be moved/forced by other colliders. |
| Kinematic collider | Collider + Rigidbody with `Is Kinematic` on. Does not respond to simulated physics forces; other colliders can hit it, but it only moves via Transform/`MovePosition`/`MoveRotation`. |
| Trigger collider | Any of the above with `isTrigger` enabled. Detects overlap without physical response; requires at least one Rigidbody among the two participants. |

Pairing outcome, from `collider-types-interaction.html`:

| Collider A | Collider B | Result |
|---|---|---|
| Dynamic (non-trigger) | Static (non-trigger) | `OnCollision` messages |
| Dynamic (non-trigger) | Dynamic (non-trigger) | `OnCollision` messages |
| Dynamic (non-trigger) | Kinematic (non-trigger) | `OnCollision` messages |
| Static (non-trigger) | Static (non-trigger) | No messages |
| Static (non-trigger) | Kinematic (non-trigger) | No messages |
| Kinematic (non-trigger) | Kinematic (non-trigger) | No messages |
| Trigger (dynamic or kinematic) | Any collider type | `OnTrigger` messages |
| Trigger (static) | Dynamic or Kinematic collider | `OnTrigger` messages |
| Trigger (static) | Static (non-trigger) | No messages |

A trigger collider never generates `OnCollision` messages — it exclusively produces `OnTrigger` events. `OnCollision` requires at least one of the two participants to have a non-kinematic (dynamic) Rigidbody.

## Collider shapes

| Shape | Component | Performance note |
|---|---|---|
| Box | `BoxCollider` | Primitive, pre-calculated shape — computationally efficient. |
| Sphere | `SphereCollider` | Primitive, pre-calculated shape — computationally efficient. |
| Capsule | `CapsuleCollider` | Primitive, pre-calculated shape — computationally efficient. |
| Mesh (non-convex) | `MeshCollider` | Matches the associated mesh geometry for extremely accurate collisions, at higher computational cost than primitives. |
| Wheel | `WheelCollider` | Uses raycasting to form wheel-shaped collision geometry with suspension and tyre friction, for vehicle physics. |
| Terrain | `TerrainCollider` | Matches terrain shape for extremely accurate collisions with the associated terrain object. |
| Compound | Multiple colliders on child GameObjects | Combines multiple primitive/mesh colliders sharing a single center of mass, for complex shapes. |

Per `performance-and-algorithms.md`'s "simplest collider shape" rule: prefer Box/Sphere/Capsule over `MeshCollider` wherever gameplay allows — a mesh collider is dramatically more expensive to evaluate.

## Collider component APIs (shape-specific properties)

### Collider (base class)

| Member | Description |
|---|---|
| `enabled` | Enabled colliders collide with other colliders; disabled ones don't. |
| `isTrigger` | Specifies if this collider is configured as a trigger. |
| `material` | The physics material applied by the collider component. |
| `sharedMaterial` | The shared physics material of this collider. |
| `bounds` | The world space bounding volume of the collider (read-only). |
| `attachedRigidbody` | The Rigidbody the collider is attached to. |
| `attachedArticulationBody` | The articulation body the collider is attached to. |
| `contactOffset` | Contact offset value of this collider. |
| `excludeLayers` | Layers this collider excludes when detecting contact. |
| `includeLayers` | Layers this collider includes when detecting contact. |
| `hasModifiableContacts` | Whether contacts generated by this collider can be modified. |
| `layerOverridePriority` | Decision priority assigned to this collider, used when there is a conflicting layer-override decision. |
| `ClosestPoint(Vector3 position)` | Returns the closest point on the collider to the given location. |
| `ClosestPointOnBounds(Vector3 position)` | Returns the closest point on the collider's bounding box. |
| `Raycast(Ray ray, out RaycastHit hitInfo, float maxDistance)` | Casts a ray that ignores all colliders except this one. |
| `GetGeometry()` | Retrieves the collider's geometric shape data. |

### BoxCollider

| Property | Description |
|---|---|
| `center` | The center of the box, measured in the object's local space. |
| `size` | The size of the box, measured in the object's local space. |

### SphereCollider

| Property | Description |
|---|---|
| `center` | The center of the sphere in the object's local space. |
| `radius` | The radius of the sphere, measured in the object's local space. |

### CapsuleCollider

| Property | Description |
|---|---|
| `center` | The center of the capsule, measured in the object's local space. |
| `radius` | The radius of the capsule's cylindrical/spherical cross-section, measured in the object's local space. |
| `height` | The height of the capsule (end to end), measured in the object's local space. |
| `direction` | The axis (X, Y, or Z) the capsule extends along. |

### MeshCollider

| Property | Description |
|---|---|
| `sharedMesh` | The mesh object used for collision detection. |
| `convex` | Use a convex collider generated from the mesh, instead of the exact mesh shape. Required for a MeshCollider on a dynamic Rigidbody. |
| `cookingOptions` | Options to enable or disable certain features during mesh cooking. |

## PhysicsMaterial — surface friction & bounciness

| Property | Description |
|---|---|
| `staticFriction` | The friction coefficient used when an object is lying on a surface (not yet moving). |
| `dynamicFriction` | The friction used when the object is already moving. Usually between 0 and 1. |
| `bounciness` | How bouncy the surface is. 0 = no bounce, 1 = bounces without any loss of energy. |
| `frictionCombine` | Determines how the friction values of the two colliding materials are combined. |
| `bounceCombine` | Determines how the bounciness values of the two colliding materials are combined. |

Combine mode enum values (`PhysicsMaterialCombine`):

| Value | Description |
|---|---|
| `Average` | Averages the friction/bounce of the two colliding materials. |
| `Minimum` | Uses the smaller friction/bounce of the two colliding materials. |
| `Maximum` | Uses the larger friction/bounce of the two colliding materials. |
| `Multiply` | Multiplies the friction/bounce of the two colliding materials. |

When two colliding materials specify different combine modes, the higher-priority mode wins. Priority, lowest to highest: `Average` < `Minimum` < `Multiply` < `Maximum`.

## Collision & trigger events

| Callback | Fires when |
|---|---|
| `OnCollisionEnter(Collision collision)` | This collider/Rigidbody has begun touching another Rigidbody/collider. Requires at least one non-kinematic Rigidbody among the two participants. |
| `OnCollisionStay(Collision collision)` | Once per physics update while this collider/Rigidbody continues touching another. Not sent for sleeping Rigidbodies. |
| `OnCollisionExit(Collision collision)` | This collider/Rigidbody has stopped touching another Rigidbody/collider. Not called if either object is destroyed before separation. |
| `OnTriggerEnter(Collider other)` | Fired on the physics `FixedUpdate` iteration when Unity first detects the collider has entered the trigger. Requires at least one of the two colliders to be a trigger and at least one to have a Rigidbody. |
| `OnTriggerStay(Collider other)` | Once per physics update, for every collider touching the trigger, while contact persists. |
| `OnTriggerExit(Collider other)` | Fired when a collider stops touching a trigger it was previously touching. |

Both the trigger collider's GameObject and the colliding object's GameObject receive `OnTrigger*` callbacks if they implement them. Trigger callbacks are sent even to disabled MonoBehaviours (useful for re-enabling a script from a trigger event); the collision parameter can be omitted from the method signature if unused, which avoids the cost of populating it.

## Collision message data (`Collision` class)

| Member | Description |
|---|---|
| `collider` | The Collider that was hit (read-only). |
| `rigidbody` | The Rigidbody that was hit (read-only); `null` if the object hit is a collider with no Rigidbody attached. |
| `body` | The Rigidbody or ArticulationBody of the collider your component collided with (read-only). |
| `gameObject` | The GameObject whose collider you are colliding with. |
| `transform` | The Transform of the object hit (read-only). |
| `contacts` | The contact points generated by the physics engine. Avoid using directly — it produces memory garbage; use `GetContact`/`GetContacts` instead. |
| `contactCount` | Total number of contact points for this collision event. |
| `relativeVelocity` | Relative linear velocity between the two colliding objects (read-only). |
| `angularVelocity` | Angular velocity of the colliding object's physics body (read-only). |
| `linearVelocity` | Linear velocity of the colliding object's physics body (read-only). |
| `impulse` | The total impulse applied to this contact pair to resolve the collision. |
| `GetContact(int index)` | Returns a single contact point at the given index. |
| `GetContacts(...)` | Returns all contact points generated during the collision. |

## Collision detection modes & algorithm selection

Per `collision-detection.html`: Unity provides different collision detection algorithms so the most efficient approach can be chosen per physics body.

- **Discrete** collision detection calculates and resolves collisions based on the pose of objects at the end of each physics simulation step — high efficiency, but a fast-moving small object can "tunnel" through a thin collider between steps.
- **Continuous** collision detection (CCD) modes trade some efficiency for high accuracy, checking for collisions along the path an object travels during a step rather than only its end pose.

The specific mode (`Discrete`, `Continuous`, `Continuous Dynamic`, `Continuous Speculative`) is configured per-Rigidbody via `collisionDetectionMode` — see [rigidbody-physics.md](rigidbody-physics.md) for the full enum and its Inspector dropdown. Use Discrete by default; switch a specific fast-moving or small Rigidbody to a continuous mode only when tunneling is an observed problem, per the Verification guidance in `performance-and-algorithms.md`.

## Layer collision matrix API

| Member | Description |
|---|---|
| `Physics.IgnoreLayerCollision(int layer1, int layer2, bool ignore = true)` | Makes the collision detection system disregard all collisions between colliders on `layer1` and `layer2`. Resets the trigger state of affected colliders, so `OnTriggerExit`/`OnTriggerEnter` may fire in response to calling this. |
| `Physics.GetIgnoreLayerCollision(int layer1, int layer2)` | Returns whether collisions between the two layers are currently ignored — the value set by `IgnoreLayerCollision` or in the Physics inspector's layer collision matrix. |

Per `performance-and-algorithms.md`'s Physics guidance: configure the layer collision matrix to prune collision checks between layers that should never interact, instead of relying on runtime `if` checks inside `OnCollision`/`OnTrigger` callbacks to filter them out after the fact.

For Rigidbody-side collision detection mode configuration, see [rigidbody-physics.md](rigidbody-physics.md). For joint-based constraints between colliders, see [joints.md](joints.md).
