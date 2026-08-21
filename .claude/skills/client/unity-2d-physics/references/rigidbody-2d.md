# Rigidbody2D — Body Types, Damping, Interpolation, Sleep & Movement

Sources: [Introduction to Rigidbody 2D](https://docs.unity3d.com/Manual/2d-physics/rigidbody/introduction-to-rigidbody-2d.html), [Rigidbody 2D body types](https://docs.unity3d.com/Manual/2d-physics/rigidbody/body-types/rigidbody-2d-body-types-landing.html), [Rigidbody2D API](https://docs.unity3d.com/ScriptReference/Rigidbody2D.html).
Covers: SKILL.md §4 — **"Choose the body type by who moves the body"**, **"Move every body through the physics API, never through its Transform"**.

`Rigidbody2D` is what hands a GameObject's position and rotation to the
simulation; every `Collider2D` on it or under it then moves and collides
through it. Three differences from 3D shape every setting below: motion is
confined to the XY plane, rotation is a single Z scalar in degrees, and
gravity is a per-body `gravityScale` multiplier rather than a boolean.

## Body types

| Type | What it decides | Source |
|---|---|---|
| Dynamic | The solver owns the motion — mass, damping, gravity, forces, and contact with every other body type. The most interactive and the most expensive | [Dynamic body type](https://docs.unity3d.com/Manual/2d-physics/rigidbody/body-types/dynamic/dynamic-body-type-fundamentals.html) |
| Kinematic | Script or animation owns the motion via `MovePosition`/`MoveRotation`; gravity and forces are ignored, and it contacts **only Dynamic bodies** until `useFullKinematicContacts` is enabled | [Kinematic body type](https://docs.unity3d.com/Manual/2d-physics/rigidbody/body-types/kinematic/kinematic-body-type-fundamentals.html) |
| Static | Never moves, behaves as infinite mass, cheapest of the three; two Static bodies cannot collide with each other | [Static body type](https://docs.unity3d.com/Manual/2d-physics/rigidbody/body-types/static/static-body-type-fundamentals.html) |
| No `Rigidbody2D` at all | Unity attaches a hidden Static body, so a bare collider is already static — adding an explicit Static body only pays off when that collider occasionally moves | [Static body type](https://docs.unity3d.com/Manual/2d-physics/rigidbody/body-types/static/static-body-type-fundamentals.html) |

**Critical caveat**: changing Body Type at runtime recalculates mass and
re-evaluates every contact. It is a deliberate, occasional operation, not a
per-frame toggle.

## Dynamics settings

| Property | What it decides | Source |
|---|---|---|
| Body Type | The three behaviours above, and which of the fields below are even shown | [Rigidbody 2D body types](https://docs.unity3d.com/Manual/2d-physics/rigidbody/body-types/rigidbody-2d-body-types-landing.html) |
| Simulated | Removes the body and its colliders and joints from simulation in one toggle — cheaper than disabling each component individually | [Simulated property](https://docs.unity3d.com/Manual/2d-physics/rigidbody/rigidbody-2d-simulated-property.html) |
| Material | A `PhysicsMaterial2D` applied to every attached collider that has none of its own — see [physics-material-2d.md](physics-material-2d.md) | [Rigidbody2D API](https://docs.unity3d.com/ScriptReference/Rigidbody2D-sharedMaterial.html) |
| Use Auto Mass | Derives mass from attached collider density instead of the Mass field, which then greys out — convenient until a collider changes and mass moves with it | [Rigidbody2D API](https://docs.unity3d.com/ScriptReference/Rigidbody2D-useAutoMass.html) |
| Mass | Dynamic only; what force calls are divided by, so a `ForceMode2D.Force` value is not portable between bodies of different mass | [Rigidbody2D API](https://docs.unity3d.com/ScriptReference/Rigidbody2D-mass.html) |
| Linear / Angular Damping | Bleeds off linear and rotational velocity over time — the correct place to cap the speed a continuous force would otherwise keep raising | [Rigidbody2D API](https://docs.unity3d.com/ScriptReference/Rigidbody2D-linearDamping.html) |
| Gravity Scale | Per-body multiplier on `Physics2D.gravity`; 0 makes a body weightless without leaving Dynamic | [Rigidbody2D API](https://docs.unity3d.com/ScriptReference/Rigidbody2D-gravityScale.html) |
| Full Kinematic Contact | Kinematic only; enables kinematic-vs-kinematic and kinematic-vs-static contacts, which are off by default | [Rigidbody2D API](https://docs.unity3d.com/ScriptReference/Rigidbody2D-useFullKinematicContacts.html) |
| Collision Detection | **Discrete** tests only the body's new position, so a fast body crosses a thin collider unnoticed; **Continuous** sweeps the movement and is what fixes tunnelling | [Rigidbody2D API](https://docs.unity3d.com/ScriptReference/Rigidbody2D-collisionDetectionMode.html) |
| Interpolate | **Interpolate** smooths the rendered pose from previous physics positions and is the fix for jitter under a following camera; **Extrapolate** predicts forward and can visibly overshoot on direction changes | [Rigidbody2D API](https://docs.unity3d.com/ScriptReference/Rigidbody2D-interpolation.html) |
| Sleeping Mode | `StartAwake`, `StartAsleep`, or `NeverSleep` — sleeping bodies are skipped by the simulation, so `NeverSleep` is a permanent per-body cost to justify | [Rigidbody2D API](https://docs.unity3d.com/ScriptReference/Rigidbody2D-sleepMode.html) |
| Constraints | Freeze position X/Y or Z rotation — the cheap way to keep a 2D character upright without a joint | [Rigidbody2D API](https://docs.unity3d.com/ScriptReference/Rigidbody2D-constraints.html) |
| Include / Exclude Layers | Per-body layer overrides on top of the project matrix, for one genuine exception rather than a policy — see [collider-2d.md](collider-2d.md) | [Rigidbody2D API](https://docs.unity3d.com/ScriptReference/Rigidbody2D-includeLayers.html) |

## Moving a body

| Member | What it decides | Source |
|---|---|---|
| `MovePosition` / `MoveRotation` | Moves a body inside the simulation so contacts are generated along the way; call from `FixedUpdate`, and pair with Interpolate for smooth rendering | [Rigidbody2D.MovePosition](https://docs.unity3d.com/ScriptReference/Rigidbody2D.MovePosition.html) |
| `Slide` | Integrates a velocity with configurable slide, gravity, and step handling — the built-in path for character-style 2D motion, instead of hand-rolling one on a Kinematic body | [Rigidbody2D.Slide](https://docs.unity3d.com/ScriptReference/Rigidbody2D.Slide.html) |
| `AddForce` / `AddTorque` | Accumulates force over the step; `ForceMode2D` offers only **Force** and **Impulse**, with no Acceleration or VelocityChange counterpart to 3D | [Rigidbody2D.AddForce](https://docs.unity3d.com/ScriptReference/Rigidbody2D.AddForce.html) |
| `AddForceX` / `AddForceY` / `AddRelativeForce` | Single-axis and body-local variants, useful when preserving the other axis matters | [Rigidbody2D.AddForceX](https://docs.unity3d.com/ScriptReference/Rigidbody2D.AddForceX.html) |
| `linearVelocity`, `angularVelocity` | Direct velocity control, which overrides rather than accumulates — the right tool for a hard clamp, the wrong one for feel | [Rigidbody2D.linearVelocity](https://docs.unity3d.com/ScriptReference/Rigidbody2D-linearVelocity.html) |
| `Cast`, `Overlap`, `Distance`, `ClosestPoint` | Queries against every attached collider at once, ignoring the body's own colliders — cheaper and less error-prone than looping per collider | [Rigidbody2D.Cast](https://docs.unity3d.com/ScriptReference/Rigidbody2D.Cast.html) |
| `IsTouching`, `IsTouchingLayers`, `GetContacts` | Contact state without waiting for a callback; the buffer overloads avoid the per-call allocation the array overloads make | [Rigidbody2D.GetContacts](https://docs.unity3d.com/ScriptReference/Rigidbody2D.GetContacts.html) |
| `Sleep`, `WakeUp`, `IsSleeping` | Manual sleep control, for a body that must settle or must not | [Rigidbody2D.Sleep](https://docs.unity3d.com/ScriptReference/Rigidbody2D.Sleep.html) |

**Critical caveat**: assigning `transform.position` on a simulated body
teleports it. No collision detection mode compensates, because there is no
movement for the solver to sweep — the body simply exists somewhere new.
