# Rigidbody — Dynamics, Forces, Interpolation & Sleep

Sources: [Introduction to Rigidbody physics](https://docs.unity3d.com/Manual/RigidbodiesOverview.html), [Apply interpolation to a Rigidbody](https://docs.unity3d.com/Manual/rigidbody-interpolation.html), [Rigidbody component reference](https://docs.unity3d.com/Manual/class-Rigidbody.html).
Covers: SKILL.md §4 — **"Move every simulated body through the physics API, never through its Transform"**, **"Configure the Rigidbody against how it is watched and how fast it moves"**.

A `Rigidbody` hands the GameObject to PhysX. Simulation happens in world
space, so a child body moves independently of its parent hierarchy — a
frequent surprise when a body is nested under an animated transform. Bodies
below the sleep threshold are excluded from simulation until something wakes
them, which is the cheapest performance win in a scene full of settled props.

## Dynamic versus kinematic

| Mode | What it decides | Source |
|---|---|---|
| Dynamic (`isKinematic` off) | Responds to forces, gravity, and collisions; the solver owns the pose. Requires **convex** colliders — a non-convex `MeshCollider` cannot back a dynamic body | [Configure Rigidbody colliders](https://docs.unity3d.com/Manual/rigidbody-configure-colliders.html) |
| Kinematic (`isKinematic` on) | Ignores incoming forces, moves only via `MovePosition`/`MoveRotation`, still generates collisions and still pushes dynamic bodies — the correct backing for a moving platform | [Introduction to Rigidbody physics](https://docs.unity3d.com/Manual/RigidbodiesOverview.html) |

## Settings

| Property | What it decides | Source |
|---|---|---|
| Mass | Kilograms, default 1. Does **not** change fall speed under gravity — damping does, so "it falls too fast" is never a mass problem | [Rigidbody reference](https://docs.unity3d.com/Manual/class-Rigidbody.html) |
| Linear / Angular Damping | Velocity decay rates; angular defaults to 0.05 and cannot fully stop rotation even at very high values | [Rigidbody reference](https://docs.unity3d.com/Manual/class-Rigidbody.html) |
| Automatic Center Of Mass / Automatic Tensor | Derived from the attached colliders unless disabled; turning them off is how a top-heavy or deliberately unbalanced object is authored | [Rigidbody reference](https://docs.unity3d.com/Manual/class-Rigidbody.html) |
| Inertia Tensor / Rotation | Resistance to angular acceleration and its orientation — higher values need more torque for the same spin | [Rigidbody reference](https://docs.unity3d.com/Manual/class-Rigidbody.html) |
| Use Gravity | Whether global gravity applies; off is not the same as kinematic, since forces still act | [Rigidbody reference](https://docs.unity3d.com/Manual/class-Rigidbody.html) |
| Interpolate | **Interpolate** smooths the rendered pose from past physics steps and is the fix for jitter under a following camera; **Extrapolate** predicts ahead and visibly overshoots on direction changes | [Apply interpolation](https://docs.unity3d.com/Manual/rigidbody-interpolation.html) |
| Collision Detection | **Discrete** tests the new position only; **Continuous** sweeps against static geometry; **Continuous Dynamic** also sweeps against other continuous bodies; **Continuous Speculative** is cheaper, handles rotation, and can report contacts slightly early | [Collision detection](https://docs.unity3d.com/Manual/collision-detection.html) |
| Freeze Position / Freeze Rotation | Per-axis constraints — the cheap way to keep a body upright without a joint | [Rigidbody reference](https://docs.unity3d.com/Manual/class-Rigidbody.html) |
| Include / Exclude Layers, Layer Override Priority | Per-body layer filtering over the project matrix, and which side wins when two overrides disagree | [Rigidbody reference](https://docs.unity3d.com/Manual/class-Rigidbody.html) |

## Moving and forcing

| Member | What it decides | Source |
|---|---|---|
| `MovePosition` / `MoveRotation` | Moves a kinematic body inside the simulation so contacts are generated; call from `FixedUpdate` | [Rigidbody.MovePosition](https://docs.unity3d.com/ScriptReference/Rigidbody.MovePosition.html) |
| `AddForce` / `AddTorque` | Accumulates over the step. `ForceMode` selects the interpretation: Force and Acceleration integrate over time, Impulse and VelocityChange apply instantly, and the Acceleration and VelocityChange pair ignore mass | [Rigidbody.AddForce](https://docs.unity3d.com/ScriptReference/Rigidbody.AddForce.html) |
| `AddForceAtPosition` | Applies force off the centre of mass, producing torque as well — how an off-centre hit spins an object | [Rigidbody.AddForceAtPosition](https://docs.unity3d.com/ScriptReference/Rigidbody.AddForceAtPosition.html) |
| `linearVelocity` / `angularVelocity` | Direct assignment overrides rather than accumulates — right for a hard clamp, wrong for feel | [Rigidbody.linearVelocity](https://docs.unity3d.com/ScriptReference/Rigidbody-linearVelocity.html) |
| `Sleep` / `WakeUp` / `IsSleeping` | Manual sleep control against `Physics.sleepThreshold` — sleeping bodies cost nothing until disturbed | [Rigidbody.Sleep](https://docs.unity3d.com/ScriptReference/Rigidbody.Sleep.html) |
| `maxDepenetrationVelocity` | How fast overlapping bodies separate; lowering it turns an explosive pop-out into a smooth push, which matters for anything spawned inside geometry | [Rigidbody.maxDepenetrationVelocity](https://docs.unity3d.com/ScriptReference/Rigidbody-maxDepenetrationVelocity.html) |
| `ConstantForce` component | Continuous force and torque every step, with a `relativeForce`/`relativeTorque` local-space pair — for an object that should build speed rather than start fast | [Apply constant force](https://docs.unity3d.com/Manual/rigidbody-constant-force.html) |

**Critical caveat**: writing `transform.position` on a non-kinematic body
fights the simulation rather than overriding it — the body is teleported, no
contacts are generated for the movement, and any joint it belongs to is left
describing a pose that no longer exists.
