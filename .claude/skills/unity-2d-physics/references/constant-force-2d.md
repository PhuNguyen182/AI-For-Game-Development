# ConstantForce2D — Continuous Force & Torque

Sources: [Constant Force 2D reference](https://docs.unity3d.com/Manual/2d-physics/constant-force-2d-reference.html), [ConstantForce2D API](https://docs.unity3d.com/ScriptReference/ConstantForce2D.html).
Covers: SKILL.md §4 — **"Use `ConstantForce2D` only for force that should keep accelerating a body"**.

`ConstantForce2D` applies linear force and torque to the `Rigidbody2D` on the
same GameObject on **every** physics update, where `AddForce` applies once.
The distinction that decides whether to use it: it is a force, not a speed, so
it keeps accelerating the body for as long as it is enabled.

| Property | What it decides | Source |
|---|---|---|
| `force` | Linear force in world axes each update — a thrust that does not rotate with the body | [Constant Force 2D reference](https://docs.unity3d.com/Manual/2d-physics/constant-force-2d-reference.html) |
| `relativeForce` | Linear force in the body's own axes — the choice for a rocket whose thrust must follow its facing | [Constant Force 2D reference](https://docs.unity3d.com/Manual/2d-physics/constant-force-2d-reference.html) |
| `torque` | Rotational force each update. There is no `relativeTorque` counterpart to 3D, because 2D rotation is a single scalar with no world-versus-local distinction | [ConstantForce2D API](https://docs.unity3d.com/ScriptReference/ConstantForce2D.html) |

**Critical caveat**: the resulting velocity is unbounded by this component.
Cap it with the body's Linear Damping or Angular Damping (see
[rigidbody-2d.md](rigidbody-2d.md)) — a constant force with no damping
accelerates until something stops it.

The Manual's own framing is a one-shot object that should build up speed
rather than start at full velocity — a rocket or a thrown projectile. Where the
design wants an immediate change in speed, a single `AddForce` with
`ForceMode2D.Impulse`, or a direct `linearVelocity` assignment, expresses it
without leaving a component running for the object's whole lifetime.
