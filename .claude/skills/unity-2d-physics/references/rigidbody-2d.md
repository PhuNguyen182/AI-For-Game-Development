# Rigidbody2D

Sources: Manual `2d-physics/rigidbody/`; API `Rigidbody2D`, `ConstantForce2D`. 2D differs from 3D: XY plane only, rotation is one Z scalar, gravity is a per-body `gravityScale`.

## Body types

| Type | Behaviour |
|---|---|
| Dynamic | Solver owns motion (mass, damping, gravity, forces); contacts every type; most expensive |
| Kinematic | Script/animation owns motion; ignores gravity and forces; contacts **only Dynamic** unless `useFullKinematicContacts` is on |
| Static | Never moves, cheapest; two Static bodies never collide |
| No `Rigidbody2D` | Unity attaches a hidden Static body; add an explicit Static body only if the collider occasionally moves |

Changing Body Type at runtime recalculates mass and re-evaluates every contact: occasional, never per frame.

## Settings

| Property | Decides |
|---|---|
| Simulated | Off removes body, colliders and joints from simulation in one toggle; cheaper than disabling each |
| Material | `PhysicsMaterial2D` for attached colliders that have none of their own |
| Use Auto Mass | Mass from collider density; the Mass field greys out, so a density change moves mass |
| Mass | Dynamic only; forces divide by it, so a `Force` value is not portable between masses |
| Linear / Angular Damping | Correct place to cap speed a continuous force keeps raising |
| Gravity Scale | Multiplier on `Physics2D.gravity`; 0 = weightless but still Dynamic |
| Collision Detection | **Discrete** tests only the new position, so fast bodies cross thin colliders; **Continuous** sweeps and fixes tunnelling |
| Interpolate | **Interpolate** smooths the rendered pose, fixes jitter under a following camera; **Extrapolate** can overshoot on direction change |
| Sleeping Mode | `StartAwake` / `StartAsleep` / `NeverSleep`; `NeverSleep` is a permanent per-body cost to justify |
| Constraints | Freeze X/Y/Z rotation: cheap way to keep a character upright without a joint |
| Include / Exclude Layers | Per-body override on the matrix, for one exception (see [collider-2d.md](collider-2d.md)) |

## Moving a body

| Member | Decides |
|---|---|
| `MovePosition` / `MoveRotation` | Moves inside the simulation so contacts are generated; call in `FixedUpdate`, pair with Interpolate |
| `Slide` | Velocity integration with slide, gravity and step handling: the built-in character-motion path, instead of hand-rolling on Kinematic |
| `AddForce` / `AddTorque` | `ForceMode2D` is only **Force** and **Impulse** (no Acceleration/VelocityChange) |
| `AddForceX/Y`, `AddRelativeForce` | Single-axis / body-local variants |
| `linearVelocity`, `angularVelocity` | Overrides rather than accumulates: right for a hard clamp, wrong for feel |
| `Cast`, `Overlap`, `Distance`, `ClosestPoint` | Query all attached colliders at once, ignoring the body's own |
| `IsTouching*`, `GetContacts` | Contact state without a callback; use the buffer overloads to avoid array allocation |
| `Sleep`, `WakeUp`, `IsSleeping` | Manual sleep control |

Assigning `transform.position` on a simulated body teleports it; no detection mode compensates because there is no movement to sweep.

## ConstantForce2D

Applies force/torque to the same-GameObject body on **every** physics update; `AddForce` applies once. It is a force, not a speed, so velocity is unbounded: cap it with damping.

| Property | Decides |
|---|---|
| `force` | World-axis linear force |
| `relativeForce` | Body-axis force: thrust that follows facing |
| `torque` | Rotation; no `relativeTorque` (2D rotation is one scalar) |

For an immediate speed change use one `AddForce(..., ForceMode2D.Impulse)` or set `linearVelocity` rather than a component running for the object's lifetime.
