# Constant Force 2D — Continuous Per-Frame Force & Torque

Covers SKILL.md step 7 (applying continuous force/torque to a Rigidbody2D via `ConstantForce2D`).

## Overview

`ConstantForce2D` applies both linear and angular (torque) force to a `Rigidbody2D` continuously, every physics update — distinct from a single call to `Rigidbody2D.AddForce`, which applies its force for one frame only. It is described in the Manual as "a quick utility for adding constant forces to a Rigidbody 2D" and has no effect unless a `Rigidbody2D` is present on the same GameObject, since all three of its fields act on that Rigidbody2D.

Constant force is not the same as constant speed: the Manual notes it works well for "one-shot objects like rockets, if you want them to accelerate over time rather than starting with a large velocity" — the force keeps accelerating the body every update, so the resulting velocity is a separate concern to cap (e.g. via the Rigidbody2D's linear drag) rather than something `ConstantForce2D` itself limits.

## Manual

| Page | URL | Covers |
|---|---|---|
| Constant Force 2D component reference | https://docs.unity3d.com/Manual/2d-physics/constant-force-2d-reference.html | `ConstantForce2D` Inspector properties, purpose, rocket/one-shot-acceleration use case |
| ConstantForce2D scripting API | https://docs.unity3d.com/ScriptReference/ConstantForce2D.html | `ConstantForce2D` class scripting API, same three fields |

## ConstantForce2D component

| Property | Description |
|---|---|
| `force` | The linear force applied to the Rigidbody2D at each physics update, in the scene's global axes. |
| `relativeForce` | The linear force applied at each physics update, relative to the Rigidbody2D's own coordinate system. |
| `torque` | The torque applied to the Rigidbody2D at each physics update. |

Unlike 3D `ConstantForce`, there is no separate `relativeTorque` field — 2D rotation has only a single axis (around Z), so one `torque` value fully covers it; there is no world-vs-local distinction to make for a scalar rotation.

Per the Manual's guidance, `ConstantForce2D` is well suited to a "one-shot object" that should accelerate over time instead of starting at a large velocity — e.g. a rocket or thrown projectile: add the component, set `Force` (or `Relative Force`, if the thrust should follow the object's own facing) to push it in the desired direction, and let the Rigidbody2D's linear/angular drag settings shape how the resulting speed levels off.

For the Rigidbody2D this component requires, see [rigidbody-2d.md](rigidbody-2d.md).
