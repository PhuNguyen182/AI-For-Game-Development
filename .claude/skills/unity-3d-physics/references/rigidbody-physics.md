# Rigidbody

Sources: Manual `RigidbodiesOverview`, `rigidbody-interpolation`, `class-Rigidbody`, `collision-detection`; API `Rigidbody`.

Simulation runs in world space, so a child body moves independently of its parent hierarchy (surprise under an animated transform). Sleeping bodies cost nothing until woken.

## Dynamic vs kinematic
- Dynamic: solver owns the pose; needs convex colliders (a non-convex `MeshCollider` cannot back it).
- Kinematic: ignores forces, moves only via `MovePosition`/`MoveRotation`, still collides and pushes dynamic bodies; the backing for a moving platform.

## Settings

| Property | Note |
|---|---|
| Mass | Default 1 kg. Does not change fall speed; damping does, so "falls too fast" is never mass |
| Linear / Angular Damping | Angular default 0.05; cannot fully stop rotation even when very high |
| Automatic Center Of Mass / Tensor | Derived from colliders; disable to author a top-heavy object |
| Inertia Tensor / Rotation | Manual override, editable when automatic tensor is off |
| Use Gravity | Off is not kinematic; forces still act |
| Interpolate | Fixes jitter under a following camera. Extrapolate overshoots on direction changes |
| Collision Detection | Discrete: new position only. Continuous: sweeps static geometry. Continuous Dynamic: also other continuous bodies. Continuous Speculative: cheaper, handles rotation, may report contacts slightly early. Set per body |
| Freeze Position / Rotation | Cheap upright constraint without a joint |
| Include / Exclude Layers, Layer Override Priority | Per-body filter over the matrix |

## Moving and forcing

| Member | Behavior |
|---|---|
| `MovePosition` / `MoveRotation` | Kinematic move inside the simulation; call from `FixedUpdate` |
| `AddForce` / `AddTorque` | Force and Acceleration integrate over time; Impulse and VelocityChange apply instantly; Acceleration and VelocityChange ignore mass |
| `AddForceAtPosition` | Off-centre force also produces torque |
| `linearVelocity` / `angularVelocity` | Assignment overrides, not accumulates: right for a hard clamp, wrong for feel |
| `Sleep` / `WakeUp` / `IsSleeping` | Against `Physics.sleepThreshold` |
| `maxDepenetrationVelocity` | Lower it so a body spawned in geometry pushes out smoothly instead of popping |
| `ConstantForce` | Per-step force/torque, with `relativeForce`/`relativeTorque` in local space |

Writing `transform.position` on a non-kinematic body teleports it with no contacts and leaves its joints describing a pose that no longer exists.
