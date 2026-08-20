# Rigidbody2D — Body Types, Mass, Drag, Interpolation & Sleep

Covers SKILL.md step 3 (configuring Rigidbody2D body type/mass/drag/gravity scale/interpolation/collision-detection-mode/constraints/sleep).

## Overview

`Rigidbody2D` is the component that puts a GameObject under Unity's 2D physics engine (Box2D-backed): it drives the object's position and rotation through simulation instead of direct Transform edits, and any `Collider2D`/`Joint2D` on the same GameObject (or its children) moves and collides through it. A `Rigidbody2D`'s **Body Type** selects one of three behaviors: **Dynamic** (fully physics-driven — mass, drag, gravity, forces, and collisions with every other body type; the most interactive and most performance-expensive option), **Kinematic** (moved only under explicit script control via `MovePosition`/`MoveRotation`/velocity — ignores gravity and forces, and by default only collides with Dynamic bodies unless `useFullKinematicContacts` is enabled), and **Static** (never moves, acts as infinite mass, and is the least resource-intensive option; two Static bodies are not supported colliding with each other). A GameObject that has only a `Collider2D` and no `Rigidbody2D` at all is treated the same as an explicit Static body — Unity internally attaches it to a hidden Static Rigidbody2D, which is why you can drop many colliders into a scene without adding a `Rigidbody2D` component to each one; adding an explicit Static `Rigidbody2D` only pays off when that particular collider needs to move occasionally.

2D physics differs from 3D conceptually in three ways that shape how you configure a `Rigidbody2D`: simulation is restricted to a single plane (the XY plane, with Z fixed), rotation is a single Z-axis angle in degrees (`rotation`, `angularVelocity`) rather than a full 3D quaternion, and gravity is scaled per-body with a single `gravityScale` multiplier against the global 2D gravity (`Physics2D.gravity`) rather than a boolean `Use Gravity` toggle. Like 3D Rigidbody, a `Rigidbody2D` whose motion settles below the sleep threshold goes to sleep and is skipped by the simulation to save CPU until a collision, force, or script call (`WakeUp()`) wakes it again; `Sleeping Mode`/`sleepMode` controls whether a body starts awake, starts asleep, or never sleeps at all.

## Manual

| Page | URL | Covers |
|---|---|---|
| Rigidbody 2D | https://docs.unity3d.com/Manual/2d-physics/rigidbody/rigidbody-2d-landing.html | Landing page for the Rigidbody 2D section |
| Introduction to Rigidbody 2D | https://docs.unity3d.com/Manual/2d-physics/rigidbody/introduction-to-rigidbody-2d.html | What Rigidbody2D is, its relationship to Collider2D, why to move the Rigidbody2D rather than the Collider2D directly (canonical target of `class-Rigidbody2D.html`) |
| Rigidbody 2D Simulated property | https://docs.unity3d.com/Manual/2d-physics/rigidbody/rigidbody-2d-simulated-property.html | What `Simulated` does, and why toggling it is cheaper than disabling individual Collider2D/Joint2D components |
| Rigidbody 2D body types | https://docs.unity3d.com/Manual/2d-physics/rigidbody/body-types/rigidbody-2d-body-types-landing.html | Landing page for the three Body Type options and the performance note on switching body type at runtime |
| Introduction to Rigidbody 2D body types | https://docs.unity3d.com/Manual/2d-physics/rigidbody/body-types/introduction-to-rigidbody-2d-body-types.html | Conceptual overview of Dynamic/Kinematic/Static and why changing Body Type costs performance (mass recalculation, contact re-evaluation) |
| Dynamic body type | https://docs.unity3d.com/Manual/2d-physics/rigidbody/body-types/dynamic/dynamic-body-type-landing.html | Landing page for the Dynamic body type section |
| Dynamic body type fundamentals | https://docs.unity3d.com/Manual/2d-physics/rigidbody/body-types/dynamic/dynamic-body-type-fundamentals.html | Dynamic is fully physics-driven (mass, drag, gravity, forces), collides with every body type, most performance-expensive |
| Dynamic body type reference | https://docs.unity3d.com/Manual/2d-physics/rigidbody/body-types/dynamic/dynamic-body-type-reference.html | Full Inspector property table shown when Body Type is Dynamic |
| Kinematic body type | https://docs.unity3d.com/Manual/2d-physics/rigidbody/body-types/kinematic/kinematic-body-type-landing.html | Landing page for the Kinematic body type section |
| Kinematic body type fundamentals | https://docs.unity3d.com/Manual/2d-physics/rigidbody/body-types/kinematic/kinematic-body-type-fundamentals.html | Kinematic ignores gravity/forces, moved via `MovePosition`/`MoveRotation`/velocity, only collides with Dynamic bodies by default |
| Kinematic body type reference | https://docs.unity3d.com/Manual/2d-physics/rigidbody/body-types/kinematic/kinematic-body-type-reference.html | Full Inspector property table shown when Body Type is Kinematic |
| Static body type | https://docs.unity3d.com/Manual/2d-physics/rigidbody/body-types/static/static-body-type-landing.html | Landing page for the Static body type section |
| Static body type fundamentals | https://docs.unity3d.com/Manual/2d-physics/rigidbody/body-types/static/static-body-type-fundamentals.html | Static never moves, acts as infinite mass, colliders with no Rigidbody2D are implicitly Static, two Static bodies can't collide with each other |
| Static body type reference | https://docs.unity3d.com/Manual/2d-physics/rigidbody/body-types/static/static-body-type-reference.html | Full Inspector property table shown when Body Type is Static |

## Rigidbody2D component Inspector properties

Which fields are visible in the Inspector depends on the selected **Body Type** — noted in the Description column where a field isn't shown for all three.

| Property | Type | Description |
|---|---|---|
| Body Type | Dropdown | Select to set the movement behavior and Collider2D interaction of this Rigidbody2D's component settings (Dynamic / Kinematic / Static). |
| Material | Object (Physics Material 2D) | Set a common physics material for all Collider2Ds attached to this Rigidbody2D. A Collider2D uses its own Material property if it has one set; if none is specified here or on the Collider2D, the default is None (Physics Material 2D). |
| Simulated | Toggle | Enable Simulated to have the Rigidbody2D and any attached Collider2Ds and Joint2Ds interact with the physics simulation during runtime. If disabled, these components do not interact with the simulation. |
| Use Auto Mass | Toggle (Dynamic only) | Enable this property to have the Rigidbody2D automatically detect the GameObject's mass from its Collider2D. |
| Mass | Float (Dynamic only) | Define the mass of the Rigidbody2D. This is grayed out if you have enabled Use Auto Mass. |
| Linear Damping | Float (Dynamic only) | Set the drag coefficient affecting positional movement. |
| Angular Damping | Float (Dynamic only) | Set the drag coefficient affecting rotational movement. |
| Gravity Scale | Float (Dynamic only) | Define the degree to which the GameObject is affected by gravity. |
| Full Kinematic Contact | Toggle (Kinematic only) | Enable this property if you want the Rigidbody2D to be able to collide with all other Rigidbody2D Body Types. |
| Collision Detection | Dropdown (Dynamic & Kinematic) | Define how collisions between Collider2Ds are detected. |
| Sleeping Mode | Dropdown (Dynamic & Kinematic) | Define how the GameObject "sleeps" to save processor time when it is at rest. |
| Interpolate | Dropdown (Dynamic & Kinematic) | Define how the GameObject's movement is interpolated between physics updates. |
| Constraints | Flags (Dynamic & Kinematic) | Define any restrictions on the Rigidbody2D's motion. |
| Layer Overrides → Include Layers | Layer Mask | Select the additional Layers that all Collider2Ds attached to this Rigidbody2D should include, when deciding if a collision with another Collider2D should occur or not. |
| Layer Overrides → Exclude Layers | Layer Mask | Select the additional Layers that all Collider2Ds attached to this Rigidbody2D should exclude, when deciding if a collision with another Collider2D should occur or not. |

## Rigidbody2D scripting API — properties

| Member | Description |
|---|---|
| `angularDamping` | The angular damping of the Rigidbody2D angular velocity. |
| `angularVelocity` | Angular velocity in degrees per second. |
| `attachedColliderCount` | Returns the number of Collider2D attached to this Rigidbody2D. |
| `bodyType` | The physical behaviour type of the Rigidbody2D. |
| `centerOfMass` | The center of mass of the rigidBody in local space. |
| `collisionDetectionMode` | The method used by the physics engine to check if two objects have collided. |
| `constraints` | Controls which degrees of freedom are allowed for the simulation of this Rigidbody2D. |
| `excludeLayers` | The additional Layers that all Collider2D attached to this Rigidbody2D should exclude when deciding if a contact with another Collider2D should happen or not. |
| `freezeRotation` | Controls whether physics will change the rotation of the object. |
| `gravityScale` | The degree to which this object is affected by gravity. |
| `includeLayers` | The additional Layers that all Collider2D attached to this Rigidbody2D should include when deciding if a contact with another Collider2D should happen or not. |
| `inertia` | The Rigidbody's resistance to changes in angular velocity (rotation). |
| `interpolation` | Physics interpolation used between updates. |
| `linearDamping` | The linear damping of the Rigidbody2D linear velocity. |
| `linearVelocity` | The linear velocity of the Rigidbody2D represents the rate of change over time of the Rigidbody2D position in world-units. |
| `linearVelocityX` | The X component of the linear velocity of the Rigidbody2D in world-units per second. |
| `linearVelocityY` | The Y component of the linear velocity of the Rigidbody2D in world-units per second. |
| `localToWorldMatrix` | The transformation matrix used to transform the Rigidbody2D to world space. |
| `mass` | Mass of the Rigidbody. |
| `position` | The position of the rigidbody. |
| `rotation` | The rotation of the rigidbody. |
| `sharedMaterial` | The PhysicsMaterial2D that is applied to all Collider2D attached to this Rigidbody2D. |
| `simulated` | Indicates whether the rigid body should be simulated or not by the physics system. |
| `sleepMode` | The sleep state that the rigidbody will initially be in. |
| `totalForce` | The total amount of force that has been explicitly applied to this Rigidbody2D since the last physics simulation step. |
| `totalTorque` | The total amount of torque that has been explicitly applied to this Rigidbody2D since the last physics simulation step. |
| `useAutoMass` | Should the total rigid-body mass be automatically calculated from the Collider2D.density of attached colliders? |
| `useFullKinematicContacts` | Should kinematic/kinematic and kinematic/static collisions be allowed? |
| `worldCenterOfMass` | Gets the center of mass of the rigidBody in global space. |

## Rigidbody2D scripting API — methods

| Member | Description |
|---|---|
| `AddForce()` | Apply a force to the rigidbody. |
| `AddForceAtPosition()` | Apply a force at a given position in space. |
| `AddForceX()` | Adds a force to the X component of the Rigidbody2D.linearVelocity only, leaving the Y component of the world space Rigidbody2D.linearVelocity untouched. |
| `AddForceY()` | Adds a force to the Y component of the Rigidbody2D.linearVelocity only, leaving the X component of the world space Rigidbody2D.linearVelocity untouched. |
| `AddRelativeForce()` | Adds a force to the local space Rigidbody2D.linearVelocity — the force is applied in the rotated coordinate space of the Rigidbody2D. |
| `AddRelativeForceX()` | Adds a force to the X component of the Rigidbody2D.linearVelocity in the local space of the Rigidbody2D only, leaving the Y component of the local space linearVelocity untouched. |
| `AddRelativeForceY()` | Adds a force to the Y component of the Rigidbody2D.linearVelocity in the local space of the Rigidbody2D only, leaving the X component of the local space linearVelocity untouched. |
| `AddTorque()` | Apply a torque at the rigidbody's centre of mass. |
| `Cast()` | All the Collider2D shapes attached to the Rigidbody2D are cast into the Scene starting at each Collider position, ignoring the Colliders attached to the same Rigidbody2D. |
| `ClosestPoint()` | Returns a point on the perimeter of all enabled Colliders attached to this Rigidbody that is closest to the specified position. |
| `Distance()` | Calculates the minimum distance of this collider against all Collider2D attached to this Rigidbody2D. |
| `GetAttachedColliders()` | Returns all Collider2D that are attached to this Rigidbody2D. |
| `GetContactColliders()` | Retrieves all colliders in contact with this Rigidbody, with the results filtered by the contactFilter. |
| `GetContacts()` | Retrieves all contact points for all of the Collider(s) attached to this Rigidbody. |
| `GetPoint()` | Get a local space point given the point in rigidBody global space. |
| `GetPointVelocity()` | The velocity of the rigidbody at the given point in global space. |
| `GetRelativePoint()` | Get a global space point given the relativePoint in rigidBody local space. |
| `GetRelativePointVelocity()` | The velocity of the rigidbody at the given point in local space. |
| `GetRelativeVector()` | Get a global space vector given the relativeVector in rigidBody local space. |
| `GetShapes()` | Gets all the PhysicsShape2D used by all Collider2D attached to the Rigidbody2D. |
| `GetVector()` | Get a local space vector given the vector in rigidBody global space. |
| `IsAwake()` | Is the rigidbody "awake"? |
| `IsSleeping()` | Is the rigidbody "sleeping"? |
| `IsTouching()` | Checks whether the collider is touching any of the collider(s) attached to this rigidbody or not. |
| `IsTouchingLayers()` | Checks whether any of the collider(s) attached to this rigidbody are touching any colliders on the specified layerMask or not. |
| `MovePosition()` | Moves the rigidbody to position. |
| `MovePositionAndRotation()` | Moves the rigidbody position to position and the rigidbody angle to angle. |
| `MoveRotation()` | Rotates the Rigidbody to angle (given in degrees). |
| `Overlap()` | Get a list of all Colliders that overlap all Colliders attached to this Rigidbody2D. |
| `OverlapPoint()` | Check if any of the Rigidbody2D colliders overlap a point in space. |
| `SetRotation()` | Sets the rotation of the Rigidbody2D to angle (given in degrees). |
| `Sleep()` | Make the rigidbody "sleep". |
| `Slide()` | Slide the Rigidbody2D using the specified velocity integrated over deltaTime using the configuration specified by slideMovement. |
| `WakeUp()` | Disables the "sleeping" state of a rigidbody. |

### Collision callback messages

| Message | Description |
|---|---|
| `OnCollisionEnter2D()` | Sent when an incoming collider makes contact with this object's collider (2D physics only). |
| `OnCollisionExit2D()` | Sent when a collider on another object stops touching this object's collider (2D physics only). |
| `OnCollisionStay2D()` | Sent each frame where a collider on another object is touching this object's collider (2D physics only). |
| `OnTriggerEnter2D()` | Sent when another object enters a trigger collider attached to this object (2D physics only). |
| `OnTriggerExit2D()` | Sent when another object leaves a trigger collider attached to this object (2D physics only). |
| `OnTriggerStay2D()` | Sent once per physics update when another object is within a trigger collider attached to this object (2D physics only). |

## Key enums

### RigidbodyType2D

| Value | Description |
|---|---|
| `Dynamic` | Sets the Rigidbody2D to have dynamic behaviour. |
| `Kinematic` | Sets the Rigidbody2D to have kinematic behaviour. |
| `Static` | Sets the Rigidbody2D to have static behaviour. |

### RigidbodyInterpolation2D

| Value | Description |
|---|---|
| `None` | Do not apply any smoothing to the object's movement. |
| `Interpolate` | Smooth movement based on the object's positions in previous frames. |
| `Extrapolate` | Smooth an object's movement based on an estimate of its position in the next frame. |

### RigidbodySleepMode2D

| Value | Description |
|---|---|
| `NeverSleep` | Rigidbody2D never automatically sleeps. |
| `StartAwake` | Rigidbody2D is initially awake. |
| `StartAsleep` | Rigidbody2D is initially asleep. |

### CollisionDetectionMode2D

| Value | Description |
|---|---|
| `Discrete` | When a Rigidbody2D moves, only collisions at the new position are detected. |
| `Continuous` | Ensures that all collisions are detected when a Rigidbody2D moves. |

### RigidbodyConstraints2D

| Value | Description |
|---|---|
| `None` | No constraints. |
| `FreezePositionX` | Freeze motion along the X-axis. |
| `FreezePositionY` | Freeze motion along the Y-axis. |
| `FreezeRotation` | Freeze rotation along the Z-axis. |
| `FreezePosition` | Freeze motion along the X-axis and Y-axis. |
| `FreezeAll` | Freeze rotation and motion along all axes. |

### ForceMode2D

| Value | Description |
|---|---|
| `Force` | Add a force to the Rigidbody2D, using its mass. |
| `Impulse` | Add an instant force impulse to the Rigidbody2D, using its mass. |

For collider shapes and PhysicsMaterial2D, see [collider-2d.md](collider-2d.md). For joints, see [joints-2d.md](joints-2d.md).
