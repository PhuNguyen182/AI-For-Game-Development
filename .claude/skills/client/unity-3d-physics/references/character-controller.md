# Character Controller — Kinematic Capsule Locomotion

Covers SKILL.md step 3 (choosing CharacterController vs. Rigidbody-driven locomotion, and configuring CharacterController).

## Overview

A Character Controller is a simple, capsule-shaped collider component with specialized features for behaving as a character in a game. It provides collision-based movement without requiring a Rigidbody: it does not apply momentum or other physics-realism effects, so a character can accelerate, brake, and change direction almost instantly under direct script control. It collides with static geometry (floors, walls) and can push Rigidbody objects aside while moving, but it is not itself accelerated or pushed by collisions with other objects — it is kinematic, moved only by explicit calls to `Move`/`SimpleMove`, never by physics forces.

This makes CharacterController well suited to first- and third-person games where responsive, intentionally unrealistic movement is desired over full physical simulation. Note that the CharacterController component itself is marked supported-but-legacy as of Unity 6.5; evaluate against a Rigidbody-driven character (see `rigidbody-physics.md`) for new work where realistic physical interaction matters.

## Manual

| Page | URL | Covers |
|---|---|---|
| Introduction to character control | https://docs.unity3d.com/Manual/CharacterControllers.html | Conceptual overview of CharacterController: capsule collider with no momentum/physics simulation, unaffected by incoming collisions, and when to prefer it over a Rigidbody-driven character. |
| Character Controller component reference | https://docs.unity3d.com/Manual/class-CharacterController.html | Full Inspector property reference for the Character Controller component, plus tuning recommendations (Skin Width, Step Offset, Slope Limit). |

## Component Inspector properties

| Property | Type | Description |
|---|---|---|
| Slope Limit | float (degrees) | Limits the collider to only climb slopes that are less steep (in degrees) than the indicated value. |
| Step Offset | float (meters) | The character will step up a stair only if it is closer to the ground than the indicated value. |
| Skin Width | float | Two colliders can penetrate each other as deep as their Skin Width. Larger Skin Widths reduce jitter. |
| Min Move Distance | float | If the character tries to move below the indicated value, it will not move at all. |
| Center | Vector3 | Offsets the Capsule Collider in world space, and does not affect how the Character pivots. |
| Radius | float | Length of the Capsule Collider's radius — the width of the collider. |
| Height | float | The Character's Capsule Collider height. Changing this scales the collider along the Y axis. |
| Layer Override Priority | int | Determines override precedence when colliders have conflicting layer-based collision settings. |
| Include Layers | LayerMask | Choose which Layers to include in collisions with this collider. |
| Exclude Layers | LayerMask | Choose which Layers to exclude in collisions with this collider. |

Tuning notes from the Manual: keep Skin Width at least 10% of Radius to prevent characters from getting stuck; keep Step Offset between 0.1–0.4 for 2-meter human characters; Slope Limit around 90 degrees gives optimal climbing behavior.

## Scripting API — properties

| Member | Description |
|---|---|
| `center` | The center of the character's capsule relative to the transform's position. |
| `collisionFlags` | What part of the capsule collided with the environment during the last `CharacterController.Move` call. |
| `detectCollisions` | Determines whether other rigidbodies or character controllers collide with this character controller (enabled by default). |
| `enableOverlapRecovery` | Enables or disables overlap recovery, used to depenetrate character controllers from static objects when an overlap is detected. |
| `height` | The height of the character's capsule. |
| `isGrounded` | Was the CharacterController touching the ground during the last move? |
| `minMoveDistance` | Gets or sets the minimum move distance of the character controller. |
| `radius` | The radius of the character's capsule. |
| `skinWidth` | The character's collision skin width. |
| `slopeLimit` | The character controller's slope limit in degrees. |
| `stepOffset` | The character controller's step offset in meters. |
| `velocity` | The current relative velocity of the character. |

## Scripting API — methods

| Member | Description |
|---|---|
| `Move(Vector3 motion)` → `CollisionFlags` | Moves the GameObject by the given absolute movement delta values, constrained by collisions. Returns a `CollisionFlags` value (`None`, `Sides`, `Above`, `Below`) indicating which direction a collision occurred. Does not apply gravity — gravity must be computed manually and included in the passed velocity. Intended to be called from `Update()`, typically with the motion scaled by `Time.deltaTime`. Only one call to `Move` or `SimpleMove` per frame is recommended. |
| `SimpleMove(Vector3 speed)` → `bool` | Moves the character using a velocity in units per second; the Y component of `speed` is ignored. Gravity is automatically applied. Returns `true` if the character is grounded at the time of the call. Only one call to `Move` or `SimpleMove` per frame is recommended. |

## Collision callback

| Member | Description |
|---|---|
| `OnControllerColliderHit(ControllerColliderHit hit)` | Called when the controller hits a collider while performing a `Move`. Receives a `ControllerColliderHit` with data about the contact. Used to implement behaviour like pushing rigidbodies, playing sounds, or triggering events in response to objects colliding with the character — e.g. reading the hit collider's attached `Rigidbody`, filtering out kinematic bodies, and applying a push force in the character's movement direction. |

For rigidbody-driven locomotion instead, see [rigidbody-physics.md](rigidbody-physics.md). For layer/collision matrix and PhysicsMaterial concerns, see [collision.md](collision.md).
