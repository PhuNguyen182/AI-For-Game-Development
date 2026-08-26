# Character Controller — Kinematic Capsule Locomotion

Sources: [Introduction to character control](https://docs.unity3d.com/Manual/CharacterControllers.html), [Character Controller component reference](https://docs.unity3d.com/Manual/class-CharacterController.html).
Covers: SKILL.md §4 — **"Choose the locomotion model by whether the character must be pushed"**.

`CharacterController` is a capsule that collides but is never simulated: it
pushes Rigidbodies out of its way and is itself immune to forces, gravity, and
impacts. That asymmetry is the entire reason to choose it — instant
acceleration and direction change, and a pose that reconciles cleanly against
`Game.Core.*` input state. Unity documents the component as supported-but-legacy
from 6.5; it is not `[Obsolete]`, so it remains valid for new work under
`coding-principles.md`'s Obsolete APIs section, but a Rigidbody character is
the alternative to weigh when real physical interaction matters.

## Shape and tuning

| Property | What it decides | Source |
|---|---|---|
| Radius / Height | The capsule's footprint and stature; Height scales along Y from Center | [Character Controller reference](https://docs.unity3d.com/Manual/class-CharacterController.html) |
| Center | Offsets the capsule without changing the pivot the character rotates about | [Character Controller reference](https://docs.unity3d.com/Manual/class-CharacterController.html) |
| Skin Width | How deeply colliders may interpenetrate; larger values reduce jitter, and the Manual's rule is **at least 10% of Radius** — below that characters snag and stick | [Character Controller reference](https://docs.unity3d.com/Manual/class-CharacterController.html) |
| Step Offset | Maximum step height climbed automatically; **0.1–0.4** for a 2 m human character, and a value above Height produces undefined behaviour | [Character Controller reference](https://docs.unity3d.com/Manual/class-CharacterController.html) |
| Slope Limit | Steepest walkable slope in degrees; around 90 gives the most permissive climbing | [Character Controller reference](https://docs.unity3d.com/Manual/class-CharacterController.html) |
| Min Move Distance | Motion below this is discarded entirely — usually left at 0, since a non-zero value silently swallows small movements | [Character Controller reference](https://docs.unity3d.com/Manual/class-CharacterController.html) |
| Include / Exclude Layers, Layer Override Priority | Per-controller layer filtering on top of the project matrix | [Character Controller reference](https://docs.unity3d.com/Manual/class-CharacterController.html) |

## Moving it

| Member | What it decides | Source |
|---|---|---|
| `Move(Vector3 motion)` | Applies an absolute delta constrained by collisions and returns `CollisionFlags` naming which side was hit. **Applies no gravity** — gravity must be integrated by the caller into the motion vector | [CharacterController.Move](https://docs.unity3d.com/ScriptReference/CharacterController.Move.html) |
| `SimpleMove(Vector3 speed)` | Takes a velocity in units per second, applies gravity automatically, and **ignores the Y component** — so it cannot jump | [CharacterController.SimpleMove](https://docs.unity3d.com/ScriptReference/CharacterController.SimpleMove.html) |
| `isGrounded` | Whether the controller touched ground during the **last** move — a result, not a live query, so it is stale until the next move | [CharacterController.isGrounded](https://docs.unity3d.com/ScriptReference/CharacterController-isGrounded.html) |
| `collisionFlags` | Which part of the capsule hit something last move — how ceiling contact cancels upward velocity | [CharacterController.collisionFlags](https://docs.unity3d.com/ScriptReference/CharacterController-collisionFlags.html) |
| `velocity` | Relative velocity resulting from the last move, not a value the caller sets | [CharacterController.velocity](https://docs.unity3d.com/ScriptReference/CharacterController-velocity.html) |
| `enableOverlapRecovery` | Depenetrates the capsule from static geometry it spawned inside — the setting that stops a character sinking through a floor it started overlapping | [CharacterController.enableOverlapRecovery](https://docs.unity3d.com/ScriptReference/CharacterController-enableOverlapRecovery.html) |
| `detectCollisions` | Whether other bodies collide with this controller at all; on by default | [CharacterController.detectCollisions](https://docs.unity3d.com/ScriptReference/CharacterController-detectCollisions.html) |
| `OnControllerColliderHit` | Raised per contact during a move — the hook for pushing Rigidbodies, filtering out kinematic ones first | [OnControllerColliderHit](https://docs.unity3d.com/ScriptReference/MonoBehaviour.OnControllerColliderHit.html) |

**Critical caveat**: call `Move` or `SimpleMove` **once** per frame, never
both. Each call resolves collisions independently, so two calls in one frame
produce a compounded result that `collisionFlags` and `isGrounded` describe
only partially.

For a body that must be pushed by the world rather than only push it, see
[rigidbody-physics.md](rigidbody-physics.md).
