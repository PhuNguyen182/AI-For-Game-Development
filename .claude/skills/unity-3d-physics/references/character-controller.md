# Character Controller

Sources: Manual `CharacterControllers`, `class-CharacterController`; API `CharacterController`.

A kinematic capsule: collides, pushes Rigidbodies, immune to forces, gravity and impacts. That gives instant acceleration and a pose that reconciles cleanly against `Game.Core.*` input state. Weigh a Rigidbody character when real physical interaction matters.

## Tuning

| Property | Rule |
|---|---|
| Skin Width | At least 10% of Radius; below that characters snag. Larger reduces jitter |
| Step Offset | 0.1-0.4 for a 2 m character; above Height is undefined |
| Slope Limit | Degrees; ~90 is most permissive |
| Min Move Distance | Motion below it is discarded; leave 0 |
| Center | Offsets the capsule without moving the rotation pivot |
| Include / Exclude Layers | Per-controller filter on top of the project matrix |
| `enableOverlapRecovery` | Depenetrates from static geometry it spawned in |
| `detectCollisions` | Whether other bodies collide with it; default on |

## Moving

| Member | Behavior |
|---|---|
| `Move(Vector3 motion)` | Absolute delta constrained by collisions; returns `CollisionFlags`. **No gravity**: the caller integrates it into the vector |
| `SimpleMove(Vector3 speed)` | Units per second, applies gravity, **ignores Y** so it cannot jump |
| `isGrounded` | Result of the last move, stale until the next |
| `collisionFlags` | Capsule side hit last move (ceiling contact cancels upward velocity) |
| `velocity` | Resulting velocity, read-only |
| `OnControllerColliderHit` | Per contact during a move; the hook for pushing Rigidbodies, skip kinematic ones |

Call `Move` or `SimpleMove` once per frame, never both.
