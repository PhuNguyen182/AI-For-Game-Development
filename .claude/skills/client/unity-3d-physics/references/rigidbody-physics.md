# Rigidbody Physics — Dynamics, Forces & Interpolation

Covers SKILL.md step 4 (configuring Rigidbody mass/drag/interpolation/collision-detection-mode/constraints/sleep) and step 3 (Rigidbody-driven locomotion as an alternative to CharacterController).

## Overview

A Rigidbody is the component that puts a GameObject under PhysX's control: it simulates rigid-body dynamics (movement, gravity, collision response, joints) instead of relying on direct Transform edits. Move a Rigidbody with `AddForce`/`AddTorque` (or `MovePosition`/`MoveRotation` when kinematic) and let the physics engine resolve the result — manually writing to `transform.position` on a non-kinematic Rigidbody fights the simulation.

A Rigidbody can be **dynamic** (physics-driven: responds to forces, gravity, and collisions) or **kinematic** (`Is Kinematic` on: moved only via Transform/`MovePosition`/`MoveRotation`, ignores incoming forces, but still generates collisions and can push dynamic bodies). Physics simulation is computed in world space, so a child GameObject's Rigidbody moves independently of its parent hierarchy. To save CPU, a Rigidbody whose motion drops below `Sleep Threshold` goes to sleep and is excluded from simulation until a collision or force wakes it (`Sleep()`/`WakeUp()`/`IsSleeping()` give manual control).

## Manual

| Page | URL | Covers |
|---|---|---|
| Introduction to Rigidbody physics | https://docs.unity3d.com/Manual/RigidbodiesOverview.html | What a Rigidbody is, dynamic vs. kinematic, gravity, sleeping |
| Configure Rigidbody colliders | https://docs.unity3d.com/Manual/rigidbody-configure-colliders.html | Collider requirements for dynamic Rigidbodies (convex-only), Mesh Collider `Convex`, compound colliders |
| Apply constant force to a Rigidbody | https://docs.unity3d.com/Manual/rigidbody-constant-force.html | `ConstantForce` component usage, constant force vs. constant speed |
| Apply interpolation to a Rigidbody | https://docs.unity3d.com/Manual/rigidbody-interpolation.html | `Interpolate` vs. `Extrapolate`, when to enable, jitter |
| Rigidbody component reference | https://docs.unity3d.com/Manual/class-Rigidbody.html | Every Inspector property |
| Constant Force component reference | https://docs.unity3d.com/Manual/class-ConstantForce.html | `ConstantForce` Inspector properties |

## Rigidbody component Inspector properties

| Property | Type | Description |
|---|---|---|
| Mass | Float | Mass of the GameObject in kilograms (default 1). Does not affect fall speed under gravity; use damping to simulate resistance. |
| Linear Damping | Float | Decay rate of linear velocity to simulate drag/friction. Lower = slower decay, higher = faster slowdown. |
| Angular Damping | Float | Decay rate of rotational velocity (default 0.05). Cannot fully stop rotation at infinity. |
| Automatic Center Of Mass | Toggle | When on, the center of mass is predicted automatically from the attached colliders' shape/scale. Disable to set custom X/Y/Z. |
| Automatic Tensor | Toggle | When on, the inertia tensor is predicted automatically from the attached colliders. Disable for custom tensor values. |
| Inertia Tensor | Vector3 | Inertia tensor of the Rigidbody. Higher values require more torque to rotate. |
| Inertia Tensor Rotation | Vector3 | Rotation orientation of the inertia tensor. |
| Use Gravity | Toggle | Applies gravitational force to the Rigidbody (default on). |
| Is Kinematic | Toggle | Switches between physics-driven and kinematic (Transform-driven) movement (default off). |
| Interpolate | Dropdown | Smooths jittery motion: None, Interpolate, or Extrapolate. |
| Collision Detection | Dropdown | Discrete, Continuous, Continuous Dynamic, or Continuous Speculative. |
| Freeze Position | Flags | Restrict movement on X, Y, Z axes selectively. |
| Freeze Rotation | Flags | Restrict rotation around local X, Y, Z axes selectively. |
| Layer Override Priority | Integer | Priority for this Rigidbody's collision-layer override settings; higher values win over conflicting settings. |
| Include Layers | Layer Mask | Layers to include when this Rigidbody detects collisions. |
| Exclude Layers | Layer Mask | Layers to exclude when this Rigidbody detects collisions. |

## Rigidbody scripting API — properties

| Member | Description |
|---|---|
| `angularDamping` | The angular damping of the object. |
| `angularVelocity` | Angular velocity vector of the Rigidbody, in radians per second. |
| `automaticCenterOfMass` | Whether to calculate the center of mass automatically. |
| `automaticInertiaTensor` | Whether to calculate the inertia tensor automatically. |
| `centerOfMass` | The center of mass relative to the transform's origin. |
| `collisionDetectionMode` | The Rigidbody's collision detection mode. |
| `constraints` | Controls which degrees of freedom are allowed for this Rigidbody's simulation. |
| `detectCollisions` | Whether collision detection is enabled (on by default). |
| `excludeLayers` | Layers that colliders should exclude when detecting contact. |
| `freezeRotation` | Controls whether physics changes this object's rotation. |
| `includeLayers` | Layers that colliders should include when detecting contact. |
| `inertiaTensor` | The inertia tensor of this body, defined as a diagonal matrix in the space of `inertiaTensorRotation`. |
| `inertiaTensorRotation` | The rotation of the inertia tensor. |
| `interpolation` | Manages the appearance of jitter in movement. |
| `isKinematic` | Controls whether physics affects the Rigidbody. |
| `linearDamping` | The linear damping of the Rigidbody's linear velocity. |
| `linearVelocity` | Linear velocity vector of the Rigidbody; rate of change of position. |
| `mass` | The mass of the Rigidbody. |
| `maxAngularVelocity` | Maximum angular velocity of the Rigidbody, in radians per second. |
| `maxDepenetrationVelocity` | Maximum velocity at which the Rigidbody moves out of a penetrating state. |
| `maxLinearVelocity` | Maximum linear velocity of the Rigidbody, in meters per second. |
| `position` | The position of the Rigidbody. |
| `rotation` | The rotation of the Rigidbody. |
| `sleepThreshold` | Mass-normalized energy threshold below which objects start going to sleep. |
| `solverIterations` | Determines accuracy of joint and contact-resolution position solving. |
| `solverVelocityIterations` | Affects accuracy of joint and contact-resolution velocity solving. |
| `useGravity` | Controls whether gravity affects this Rigidbody. |
| `worldCenterOfMass` | The center of mass of the Rigidbody in world space (read only). |

## Rigidbody scripting API — methods

| Member | Description |
|---|---|
| `AddExplosionForce()` | Applies a force to the Rigidbody that simulates explosion effects. |
| `AddForce()` | Adds a force to the Rigidbody. |
| `AddForceAtPosition()` | Applies a force at a position; results in both force and torque on the object. |
| `AddRelativeForce()` | Adds a force to the Rigidbody relative to its coordinate system. |
| `AddRelativeTorque()` | Adds a torque to the Rigidbody relative to its coordinate system. |
| `AddTorque()` | Adds a torque to the Rigidbody. |
| `ClosestPointOnBounds()` | Closest point to the bounding box of the attached colliders. |
| `GetAccumulatedForce()` | Returns the force accumulated by the Rigidbody before the simulation step. |
| `GetAccumulatedTorque()` | Returns the torque accumulated by the Rigidbody before the simulation step. |
| `GetPointVelocity()` | Velocity of the Rigidbody at a given point in global space. |
| `GetRelativePointVelocity()` | Velocity of the Rigidbody at a given point in local space. |
| `IsSleeping()` | Is the Rigidbody sleeping? |
| `Move()` | Moves the Rigidbody to a position and rotates it to a rotation. |
| `MovePosition()` | Moves a kinematic Rigidbody towards a position. |
| `MoveRotation()` | Rotates the Rigidbody to a rotation. |
| `PublishTransform()` | Applies the Rigidbody's position and rotation to its Transform component. |
| `ResetCenterOfMass()` | Resets the center of mass of the Rigidbody. |
| `ResetInertiaTensor()` | Resets the inertia tensor value and rotation. |
| `Sleep()` | Forces the Rigidbody to sleep until woken up. |
| `SweepTest()` | Tests whether the Rigidbody would collide with anything if it moved through the scene. |
| `SweepTestAll()` | Like `SweepTest()`, but returns all hits. |
| `WakeUp()` | Forces the Rigidbody to wake up. |

### Collision callback messages

| Message | Description |
|---|---|
| `OnCollisionEnter()` | Called when this collider/Rigidbody has begun touching another rigidbody/collider. |
| `OnCollisionExit()` | Called when this collider/Rigidbody has stopped touching another rigidbody/collider. |
| `OnCollisionStay()` | Called once per frame for every collider/Rigidbody touching this one. |

## Constant Force component

`ConstantForce` applies continuous linear/rotational force to a Rigidbody every frame, unlike `Rigidbody.AddForce`, which applies force for a single frame only. The same four fields are exposed both in the Inspector (`class-ConstantForce.html`) and the scripting API (`ScriptReference/ConstantForce.html`).

| Property | Description |
|---|---|
| `force` | Linear force applied to the Rigidbody every frame. Direction is in the scene's global axes. |
| `relativeForce` | Linear force applied every frame, relative to the Rigidbody's local axes. |
| `torque` | Torque applied to the Rigidbody every frame, around the scene's global axes. |
| `relativeTorque` | Torque applied every frame, relative to the Rigidbody's local axes. |

Constant force is not the same as constant speed — velocity accelerates over time while the force is applied. By default linear acceleration is unbounded while angular acceleration caps at 50 rad/s; adjust via `Rigidbody.maxLinearVelocity` and `Rigidbody.maxAngularVelocity`. To build a constantly-accelerating object (e.g. a rocket): add `ConstantForce`, set `Relative Force` Z to a positive value, disable `Use Gravity` on the Rigidbody so it doesn't fight the thrust, and tune `Linear Damping` to cap the resulting top speed — expect to iterate by feel.

## Key enums

### ForceMode

| Value | Description |
|---|---|
| `Force` | Add a continuous force to the Rigidbody, using its mass. |
| `Acceleration` | Add a continuous acceleration to the Rigidbody, ignoring its mass. |
| `Impulse` | Add an instant force impulse to the Rigidbody, using its mass. |
| `VelocityChange` | Add an instant velocity change to the Rigidbody, ignoring its mass. |

### RigidbodyInterpolation

| Value | Description |
|---|---|
| `None` | No interpolation. |
| `Interpolate` | Always lags a little behind the true simulated pose (uses the previous two physics updates) but is smoother than extrapolation — the recommended default when jitter needs fixing. |
| `Extrapolate` | Predicts the Rigidbody's position from its current velocity; can overshoot/mispredict when velocity changes or other physics forces intervene. |

### CollisionDetectionMode

| Value | Description |
|---|---|
| `Discrete` | Continuous collision detection is off for this Rigidbody. |
| `Continuous` | Continuous collision detection is on for colliding with static mesh geometry. |
| `ContinuousDynamic` | Continuous collision detection is on for colliding with both static and dynamic geometry. |
| `ContinuousSpeculative` | Speculative continuous collision detection is on for both static and dynamic geometries. |

### RigidbodyConstraints

| Value | Description |
|---|---|
| `None` | No constraints. |
| `FreezePositionX` | Freeze motion along the X-axis; limits motion to the YZ plane only. |
| `FreezePositionY` | Freeze motion along the Y-axis; limits motion to the XZ plane only. |
| `FreezePositionZ` | Freeze motion along the Z-axis; limits motion to the XY plane only. |
| `FreezeRotationX` | Freeze rotation along the X-axis. |
| `FreezeRotationY` | Freeze rotation along the Y-axis. |
| `FreezeRotationZ` | Freeze rotation along the Z-axis. |
| `FreezePosition` | Combines `FreezePositionX`/`Y`/`Z` — freeze motion on all axes. |
| `FreezeRotation` | Combines `FreezeRotationX`/`Y`/`Z` — freeze rotation on all axes. |
| `FreezeAll` | Freeze rotation and motion along all axes. |

For CharacterController-based locomotion instead, see [character-controller.md](character-controller.md). For collider/PhysicsMaterial configuration attached to a Rigidbody, see [collision.md](collision.md).
