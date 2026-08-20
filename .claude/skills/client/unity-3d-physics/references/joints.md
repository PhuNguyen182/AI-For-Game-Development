# Joints — Fixed, Hinge, Spring, Character & Configurable

Covers SKILL.md step 6 (choosing a joint by required degrees of freedom).

## Overview

A joint connects a Rigidbody to another Rigidbody, an ArticulationBody, or a fixed point in space, and constrains their relative motion. Joints apply forces to hold connected bodies together around a shared anchor point while joint-specific limits, springs, and motors restrict or drive that relative movement. Each connection can be configured with a break threshold so the joint physically separates once enough force or torque is applied to it.

Unity's built-in joint set — Fixed, Hinge, Spring, Character, and Configurable — covers most gameplay rigid-body constraints (doors, ragdolls, tethers, elastic links). For industrial-grade articulated mechanisms (robotic arms, precise multi-link chains) the Manual recommends ArticulationBody-based physics articulations instead of chaining standard joints.

## Manual

| Page | URL | Covers |
|---|---|---|
| Introduction to joints | https://docs.unity3d.com/Manual/Joints.html | Shared concepts: connected bodies, anchors, break force, drive/spring behavior; overview of all joint types |
| Fixed Joint | https://docs.unity3d.com/Manual/class-FixedJoint.html | Rigid attachment between two bodies without parenting |
| Hinge Joint | https://docs.unity3d.com/Manual/class-HingeJoint.html | Single rotation axis, with optional spring, motor, and angle limits |
| Spring Joint | https://docs.unity3d.com/Manual/class-SpringJoint.html | Elastic distance constraint between two anchor points |
| Character Joint | https://docs.unity3d.com/Manual/class-CharacterJoint.html | Extended ball-socket joint with per-axis angular limits, built for ragdolls |
| Create a configurable joint | https://docs.unity3d.com/Manual/create-configurable-joint.html | Tutorial-style guide to per-axis linear/angular motion, limits, and drives |
| Speculative CCD | https://docs.unity3d.com/Manual/speculative-ccd.html | Continuous collision detection mode relevant to fast-moving jointed/rigid bodies |

## Shared Joint base API

Members common to every joint type (`FixedJoint`, `HingeJoint`, `SpringJoint`, `CharacterJoint`, `ConfigurableJoint` all inherit from `Joint`).

| Member | Description |
|---|---|
| `anchor` | Position of the anchor around which the joint's motion is constrained (local space). |
| `axis` | Direction of the axis around which the body is constrained. |
| `connectedBody` | Reference to another Rigidbody this joint connects to; connects to the world if unset. |
| `connectedArticulationBody` | Reference to an ArticulationBody this joint connects to. |
| `connectedAnchor` | Position of the anchor relative to the connected body. |
| `autoConfigureConnectedAnchor` | When enabled, Unity automatically calculates the connected anchor position instead of using the manual `connectedAnchor` value. |
| `breakForce` | Force that must be applied to this joint for it to break. |
| `breakTorque` | Torque that must be applied to this joint for it to break. |
| `enableCollision` | Enables collision between the bodies connected by the joint. |
| `enablePreprocessing` | Toggles preprocessing; disabling can improve stability in otherwise impossible/degenerate joint configurations. |
| `massScale` | Scale factor applied to this body's inverse mass and inertia tensor. |
| `connectedMassScale` | Scale factor applied to the connected body's inverse mass and inertia tensor. |
| `currentForce` | Force currently applied by the solver to satisfy the joint's constraints (read-only). |
| `currentTorque` | Torque currently applied by the solver to satisfy the joint's constraints (read-only). |
| `OnJointBreak` | MonoBehaviour message invoked when the joint breaks. |

## Fixed Joint

Removes all relative translational and rotational freedom between two bodies — it rigidly sticks them together in their bound position, functioning like parenting but resolved through physics instead of the Transform hierarchy. Use it to connect two objects' movement without changing scene hierarchy, and where an easily breakable rigid connection is wanted (e.g. snapping a part off on impact via `breakForce`/`breakTorque`).

Fixed Joint has almost no unique properties beyond the base `Joint` class — its Inspector surface is effectively the shared Joint properties above (Connected Body, Break Force, Break Torque, Enable Collision, Enable Preprocessing, Mass Scale, Connected Mass Scale).

| Property | Description |
|---|---|
| *(none beyond base Joint)* | FixedJoint adds no class-specific members; all configuration comes from the base `Joint` API. |

## Hinge Joint

Constrains two Rigidbodies to rotate together around a single shared axis, like a door on a hinge, a chain link, or a pendulum. Optional sub-features add a motor (continuous driven rotation), a spring (pulls toward a target angle), and limits (clamps the rotation range).

| Property | Description |
|---|---|
| `useMotor` | Enables the joint's motor (disabled by default). |
| `motor` (`JointMotor`) | Applies force up to a maximum force to reach a target velocity, in degrees/second. |
| `useSpring` | Enables the joint's spring (disabled by default). |
| `spring` (`JointSpring`) | Attempts to reach a target angle by applying spring and damping forces. |
| `useAcceleration` | Whether the spring outputs accelerations instead of forces. |
| `useLimits` | Enables the joint's angular limits (disabled by default). |
| `limits` (`JointLimits`) | Limit of angular rotation (in degrees) on the hinge joint. |
| `extendedLimits` | When enabled, extends the limit range to [-360, 360] degrees. |
| `angle` | Current angle, in degrees, relative to the rest position (read-only). |
| `velocity` | Current angular velocity, in degrees/second (read-only). |

## Spring Joint

Connects two Rigidbodies with an elastic constraint: it pulls the two anchor points toward each other with force proportional to how far apart they are, rather than rigidly fixing distance. Useful for elastic tethers, bungee-style connections, and chains of springy links.

| Property | Description |
|---|---|
| `spring` | Spring force used to keep the two objects together. |
| `damper` | Damper force used to dampen the spring force (reduces oscillation). |
| `minDistance` | Minimum distance between the bodies, relative to their initial distance, within which no spring force is applied. |
| `maxDistance` | Maximum distance between the bodies, relative to their initial distance, within which no spring force is applied. |
| `tolerance` | Maximum allowed error between the current spring length and the length defined by `minDistance`/`maxDistance`. |

## Character Joint

An extended ball-and-socket joint that lets each rotational axis be limited independently — a twist axis plus two swing axes. Purpose-built for ragdoll limbs, where each joint (shoulder, elbow, hip, knee) needs realistic, anatomically-limited rotation. Cross-reference [ragdoll-physics.md](ragdoll-physics.md) for ragdoll-specific setup and tuning.

| Property | Description |
|---|---|
| `swingAxis` | Secondary (swing) rotation axis, defined relative to the joint's primary `axis`. |
| `twistLimitSpring` | Spring configuration (spring + damper) attached to the twist-axis limits; zero spring is rigid, non-zero is elastic. |
| `lowTwistLimit` | Lower rotation limit around the primary (twist) axis, in degrees. |
| `highTwistLimit` | Upper rotation limit around the primary (twist) axis, in degrees. |
| `swingLimitSpring` | Spring configuration attached to the swing-axis limits. |
| `swing1Limit` | Angular limit of rotation, in degrees, around the swing axis. |
| `swing2Limit` | Angular limit of rotation, in degrees, around the axis orthogonal to swing (not gizmo-visualized). |
| `enableProjection` | Brings violated constraints back into alignment even when the solver fails to resolve them directly. |
| `projectionDistance` | Linear tolerance threshold before projection kicks in. |
| `projectionAngle` | Angular tolerance threshold, in degrees, before projection kicks in. |

Each limit (twist, swing1, swing2) also exposes bounciness (0–1) and a contact distance to prevent jitter, configured via the Inspector's limit sub-properties.

## Configurable Joint

The most flexible joint: every linear axis (X/Y/Z) and every angular axis (X/Y/Z) can independently be set Free, Locked, or Limited, and driven toward a target position/rotation/velocity with spring-like drives. Use it to emulate any other joint type, build custom skeletal joints, or implement physics-driven movement toward a moving target. Because of the large configuration surface, the Manual explicitly advises iterating experimentally to get the desired feel.

| Property | Description |
|---|---|
| `xMotion` / `yMotion` / `zMotion` | Linear motion mode (Free, Locked, or Limited) along the local X/Y/Z axis. |
| `angularXMotion` / `angularYMotion` / `angularZMotion` | Rotational motion mode (Free, Locked, or Limited) around the local X/Y/Z axis. |
| `linearLimit` | Boundary restricting movement based on distance from the joint's origin (applies when a motion axis is Limited). |
| `linearLimitSpring` | Spring configuration attached to the linear limit. |
| `lowAngularXLimit` | Lower rotation boundary around the X axis. |
| `highAngularXLimit` | Upper rotation boundary around the X axis. |
| `angularYLimit` | Rotation restriction around the Y axis. |
| `angularZLimit` | Rotation restriction around the Z axis. |
| `angularXLimitSpring` | Spring configuration for the X rotation limit. |
| `angularYZLimitSpring` | Spring configuration for the Y and Z rotation limits. |
| `xDrive` / `yDrive` / `zDrive` | Defines how the joint's linear movement is driven along the local X/Y/Z axis. |
| `angularXDrive` | Defines how the joint's rotation is driven around the local X axis. |
| `angularYZDrive` | Defines how the joint's rotation is driven around the local Y and Z axes. |
| `slerpDrive` | Defines how the joint's rotation is driven around all local axes simultaneously (spherical interpolation). |
| `rotationDriveMode` | Selects whether rotation is controlled via X & YZ drives or via the single Slerp drive. |
| `targetPosition` | Desired position the joint should move into. |
| `targetVelocity` | Desired linear velocity the joint should move along. |
| `targetRotation` | Desired rotation (Quaternion) the joint should rotate into. |
| `targetAngularVelocity` | Desired angular velocity (Vector3) the joint should rotate into. |
| `configuredInWorldSpace` | When enabled, all target values are calculated in world space instead of local space. |
| `secondaryAxis` | The joint's secondary axis (used together with `axis` to define the full local frame). |
| `swapBodies` | Swaps the order in which the physics engine processes the connected Rigidbodies. |
| `projectionMode` | Brings violated constraints back into alignment even when the solver fails to resolve them directly. |
| `projectionDistance` | Linear tolerance threshold for projection. |
| `projectionAngle` | Angular tolerance threshold, in degrees, for projection. |

## Speculative CCD

Speculative CCD (continuous collision detection) increases a fast-moving object's broad-phase AABB based on its linear and angular motion, predicts likely contacts before the next physics step, and feeds them into the solver — preventing tunneling without the full cost of sweep-based CCD. It is cheaper computationally than sweep CCD, making it suitable for performance-sensitive scenes with many fast-moving bodies.

It has two failure modes to be aware of: it can produce false collisions (inaccurate contact normals causing unexpected sliding/jumping), and it can still miss a collision if a body gains enough energy during the solve step to exit the inflated AABB before the next detection pass. For fast-moving jointed bodies (e.g. a jointed limb or projectile swung hard by a motor/drive), enabling Speculative CCD on the Rigidbody reduces tunneling risk without the full cost of sweep-based continuous detection.

## Choosing a joint by degrees of freedom

| Requirement | Joint |
|---|---|
| Rigidly attach two bodies (no relative motion, still breakable) | Fixed Joint |
| Single rotation axis, optional motor/spring/limits (door, wheel, pendulum) | Hinge Joint |
| Distance constraint with elastic give (tether, bungee) | Spring Joint |
| 3-axis limited rotation for a ragdoll limb (twist + 2 swing axes) | Character Joint |
| Fully custom per-axis linear/angular constraint and/or driven target motion | Configurable Joint |
| Precise multi-link articulated mechanism (robotic arm, kinematic chain) | ArticulationBody (not a Joint subclass) |

For ArticulationBody as an alternative to Rigidbody+Joint chains, and ragdoll-specific Character Joint tuning, see [ragdoll-physics.md](ragdoll-physics.md).
