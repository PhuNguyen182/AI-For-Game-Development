---
name: unity-2d-physics
description: >
  Technique for Unity's built-in 2D physics engine (`UnityEngine.Physics2D`,
  Box2D-backed, GameObject/MonoBehaviour-driven) — `Rigidbody2D` dynamics
  (body type, mass, linear/angular drag, gravity scale, interpolation,
  collision detection, constraints, sleep), `Collider2D` shapes
  (Box/Circle/Capsule/Polygon/Edge/Composite) and `PhysicsMaterial2D`
  surface properties (friction/bounciness), 2D effectors (Area, Point,
  Platform, Surface, Buoyancy) and their required effector-enabled
  collider/trigger setup, 2D joints (Distance, Fixed, Friction, Hinge,
  Relative, Slider, Spring, Target, Wheel), `ConstantForce2D`, and the 2D
  layer collision matrix. Use this for any task touching `Rigidbody2D`,
  `Collider2D`, `Joint2D`, `Effector2D`, `ConstantForce2D`,
  `PhysicsMaterial2D`, or `Physics2D.*` static calls on an ordinary
  GameObject. Do not use this for built-in 3D physics (`Rigidbody`,
  `Collider`, `CharacterController`, `Joint`, `ArticulationBody`, `Cloth`,
  `Physics.*`) — that's `unity-3d-physics`, a separate, structurally
  similar but distinct API surface. Do not use this for `com.unity.physics`
  (ECS/DOTS-native, deterministic rigid body physics) — that's
  `unity-physics`, a structurally unrelated engine. Do not use this for
  actual gameplay rule logic that happens to consume 2D physics data
  (damage formulas, state machines, ability cooldowns) — that belongs in
  Shared Core, per `coding-principles.md`'s Shared Core integrity rule;
  this skill only covers wiring the Unity-side 2D physics components
  themselves. Do not use this for deep, escalated performance work beyond
  Profiler-driven baseline optimization (native plugin-level, GPU-level) —
  that's `tech-lead-performance`.
---

# Unity 2D Physics — Built-in Box2D Rigid Body, Collider, Effector & Joint Simulation

Sources: see [references/](references/) for the Unity Manual root links, split by topic — [root-links.md](references/root-links.md), [rigidbody-2d.md](references/rigidbody-2d.md), [collider-2d.md](references/collider-2d.md), [effectors-2d.md](references/effectors-2d.md), [joints-2d.md](references/joints-2d.md), [constant-force-2d.md](references/constant-force-2d.md), [physics-material-2d.md](references/physics-material-2d.md).

## 1. Objective
Configure Unity's built-in 2D Box2D physics correctly on ordinary GameObjects — right `Rigidbody2D` body type and settings, right `Collider2D` shape and `PhysicsMaterial2D`, right effector for the required non-physically-realistic behavior (one-way platforms, area forces, buoyancy), right joint for the required constraint — without drifting into 3D physics, DOTS/ECS physics, or gameplay rule logic that belong to sibling skills or roles.

## 2. Role
Act as the built-in 2D physics specialist: given a need for 2D rigid body dynamics, collision response, effector-driven behavior, or joint constraints on a normal (non-ECS) GameObject, you choose and configure the right `UnityEngine.Physics2D`-namespace components and settings — you don't decide gameplay outcomes from physics data (that's Shared Core's job) and you don't reach for 3D physics, DOTS/ECS physics, or deep native/GPU-level optimization, which are sibling skills'/roles' territory.

## 3. When to invoke this skill
- Configuring a `Rigidbody2D`'s body type (Dynamic/Kinematic/Static), mass, linear/angular drag, gravity scale, interpolation, collision detection mode, constraints, or sleep behavior.
- Choosing a `Collider2D` shape (Box/Circle/Capsule/Polygon/Edge/Composite), setting up a `PhysicsMaterial2D` (friction/bounciness), configuring trigger vs. solid colliders, or tuning the 2D layer collision matrix.
- Setting up a 2D effector (Area, Point, Platform, Surface, Buoyancy) and its required "Used By Effector"-enabled collider/trigger configuration.
- Choosing and creating a 2D joint (Distance, Fixed, Friction, Hinge, Relative, Slider, Spring, Target, Wheel) by required degrees of freedom or constraint behavior.
- Applying a continuous force to a `Rigidbody2D` via `ConstantForce2D`.
- Reading/handling 2D collision or trigger events (`OnCollisionEnter2D`/`OnTriggerEnter2D` and their `Stay`/`Exit` counterparts).
- Negative trigger: built-in 3D physics work (`Rigidbody`, `Collider`, `CharacterController`, `Joint`, `ArticulationBody`, `Cloth`) — that's `unity-3d-physics`, a separate skill despite the structurally similar naming.
- Negative trigger: the project is ECS/DOTS and the task is `com.unity.physics` component/collider/joint/query work — that's `unity-physics`, a completely separate engine.
- Negative trigger: the actual gameplay decision built on top of 2D physics data (damage calculation on collision, a state machine transition, an ability's cooldown/economy math) — that's `csharp-engineer`'s Shared Core, per `coding-principles.md`'s Shared Core integrity rule; this skill stops at wiring the physics component and handing already-resolved data (e.g. a contact point, a hit normal) to Core.
- Negative trigger: a physics performance problem that survives the Profiler-driven baseline (e.g. needs a native plugin or compute-shader-level fix) — escalate to `tech-lead-performance`, per its own scope definition.

## 4. How to use this skill
1. **Confirm scope first.** This skill is classic built-in 2D Box2D physics (`UnityEngine.Physics2D`, GameObject/MonoBehaviour-driven) — `Rigidbody2D`, `Collider2D`, `Effector2D`, `Joint2D`, `ConstantForce2D`. If the task is 3D, stop and hand off to `unity-3d-physics`. If the project is on ECS/DOTS and the task is `com.unity.physics` work, stop and hand off to `unity-physics`.
2. **Respect the Shared Core boundary.** Any gameplay decision that happens to be triggered by a 2D physics event (damage on collision, a knockback amount, an ability's hit resolution) is computed in `Game.Core.*`; this skill's components only detect/resolve the physical event and hand already-resolved data (contact point, normal, relative velocity) to Core — they never decide an outcome themselves, per `coding-principles.md`'s Shared Core integrity rule.
3. **Choose the Rigidbody2D body type deliberately**, per [rigidbody-2d.md](references/rigidbody-2d.md): Dynamic for anything driven by forces/gravity/collision response, Kinematic for script/animation-driven bodies that still need to be sensed by other physics bodies, Static (a `Collider2D` alone, no `Rigidbody2D`) only for genuinely immovable geometry. Set gravity scale, linear/angular drag, interpolation (`Interpolate` when watched by a moving/following camera), and collision detection mode (`Continuous` for small/fast-moving bodies that could tunnel) deliberately rather than leaving defaults unexamined.
4. **Configure Collider2D shapes deliberately**, per [collider-2d.md](references/collider-2d.md): the simplest shape the sprite's silhouette allows (Circle/Box/Capsule over Polygon, Polygon over per-pixel-accurate custom shapes) per `performance-and-algorithms.md`'s simplest-collider-shape rule; Composite Collider 2D when merging multiple tile/sprite colliders into one efficient shape; a dedicated `PhysicsMaterial2D` (see [physics-material-2d.md](references/physics-material-2d.md)) for any surface whose friction/bounciness matters instead of leaving it unset; trigger vs. solid chosen by whether the collider should physically block or only detect overlap; the 2D layer collision matrix pruned to skip pairs that should never interact, instead of filtering them in a collision callback after the fact.
5. **Reach for an effector only when the *design* explicitly calls for non-physically-realistic behavior** (one-way platforms, area-of-effect wind/gravity zones, conveyor-like surface friction, buoyancy in a fluid volume) — per [effectors-2d.md](references/effectors-2d.md). Effectors require the affected `Collider2D` to have "Used By Effector" enabled and, for most effector types, the interacting collider set as a trigger; don't add an effector when a plain Rigidbody2D + force/velocity script already expresses the requirement more simply (KISS in `coding-principles.md`).
6. **Choose the 2D joint by required constraint behavior**, per [joints-2d.md](references/joints-2d.md): Distance to hold two bodies a fixed/max distance apart, Fixed to rigidly weld two bodies while still simulated as two Rigidbody2Ds, Friction to damp relative linear/angular motion, Hinge for a single rotational pivot (doors, swinging platforms), Slider for constrained linear motion along an axis, Spring for a distance constraint with spring/damper behavior, Wheel for suspension-like vehicle wheel behavior, Target for pulling a body toward a moving world-space point, Relative to maintain another body's relative position/rotation over time. Don't reach for a more general joint when a named, narrower joint already expresses the requirement.
7. **Use `ConstantForce2D`** (per [constant-force-2d.md](references/constant-force-2d.md)) only for a genuinely continuous per-frame force/torque (wind, thrust) — not as a substitute for a one-shot `AddForce` impulse.
8. **State the hand-off explicitly.** Gameplay decisions built on top of 2D physics data → `csharp-engineer`'s Shared Core. Performance problems that survive Profiler-driven baseline tuning → `tech-lead-performance`. 3D physics → `unity-3d-physics`. DOTS/ECS physics → `unity-physics`.

## 5. Specific goals / tasks this skill performs
- Configuring `Rigidbody2D` body type/mass/drag/gravity scale/interpolation/collision-detection-mode/constraints/sleep.
- Choosing `Collider2D` shapes, configuring `PhysicsMaterial2D`, trigger vs. solid, and the 2D layer collision matrix.
- Setting up effectors (Area, Point, Platform, Surface, Buoyancy) with correctly configured "Used By Effector" colliders.
- Choosing/creating 2D joints (Distance/Fixed/Friction/Hinge/Relative/Slider/Spring/Target/Wheel) by required constraint behavior.
- Applying `ConstantForce2D` for continuous per-frame force/torque.
- Handling 2D collision/trigger events.
- Out of scope: built-in 3D physics (`unity-3d-physics`); `com.unity.physics`/DOTS physics (`unity-physics`); gameplay rule logic consuming physics data (`csharp-engineer`'s Shared Core); performance work beyond the profiler-driven baseline (`tech-lead-performance`).

## 6. Output format
```
## 2D Physics Work — <feature/body name>
- Scope confirmed: built-in 2D Box2D (not 3D Physics, not DOTS Unity Physics)
- Rigidbody2D settings (if applicable): body type <Dynamic/Kinematic/Static>, mass <n>, drag <n>/<n>, gravity scale <n>, interpolation <mode>, collision detection <mode>, constraints <list>
- Collider2D setup: shape(s) chosen, PhysicsMaterial2D (friction/bounciness), trigger vs. solid, layer matrix pruned <yes/no>
- Effector (if applicable): type chosen, "Used By Effector" collider configuration, rationale over a plain force/velocity script
- Joint2D (if applicable): type chosen, constraint behavior needed
- ConstantForce2D (if applicable): force/torque values, rationale over a one-shot impulse
- Shared Core boundary: confirmed no gameplay decision made in physics-layer code
- Hand-off: <gameplay logic → csharp-engineer / deep perf → tech-lead-performance / 3D → unity-3d-physics / DOTS → unity-physics, as applicable>
- Known limitations: <...>
```

## 7. Examples
**Example 1**
- Input: "Make a one-way platform the player can jump up through but stands on from above, plus a wind zone that pushes projectiles sideways."
- Output: added a `PlatformEffector2D` on the platform's `Collider2D` (Used By Effector enabled, collider set as non-trigger, `Use One Way` on) for the jump-through-from-below behavior; added a separate trigger `Collider2D` with an `AreaEffector2D` (Used By Effector enabled on the trigger collider, `Force Direction`/`Force Magnitude` tuned) over the wind zone, rather than scripting manual per-frame velocity changes for either — both are effector-shaped problems, not gameplay-rule problems.
- Hand-off: none — both are pure physics-layer configuration; no gameplay decision was made here.

**Example 2**
- Input: "A rope-swing mechanic: the player attaches to an anchor point and swings on a rope."
- Output: used a `DistanceJoint2D` on the player's `Rigidbody2D` connecting to a `Rigidbody2D` at the anchor point, with `Max Distance Only` enabled so the rope only constrains at full extension (free movement inside the radius) rather than a `SpringJoint2D`, since the design called for a taut rope, not elastic give.
- Hand-off: grapple-attach input handling and swing-release gameplay timing → `csharp-engineer`'s Shared Core; this skill only configured the joint constraint itself.

## 8. Edge cases & guardrails
- Never assume built-in 3D `Physics`/`Rigidbody`/`Collider` behavior applies here — this is the Box2D-backed 2D engine (`UnityEngine.Physics2D`) on ordinary GameObjects; route 3D physics work to `unity-3d-physics` instead.
- Never assume `com.unity.physics` (ECS/DOTS) behavior applies here; route that work to `unity-physics` instead.
- Never make a gameplay decision (damage, score, state transition) inside a `Rigidbody2D`/`Collider2D` physics callback — resolve the outcome in Shared Core and let the physics-layer code only detect the event and pass along already-resolved data.
- An effector does nothing unless the affected `Collider2D` has "Used By Effector" enabled — a commonly missed setup step; verify it explicitly rather than assuming the effector is active just because the component was added.
- Don't reach for an effector or a general-purpose joint (Target/Relative) when a plain Rigidbody2D force/velocity script or a named, narrower joint already expresses the requirement — see KISS in `coding-principles.md`.
- Don't leave `interpolation`/`collisionDetectionMode` at their unexamined defaults for camera-watched or fast-moving 2D bodies — visible jitter and tunneling are the direct symptom of skipping this.
- Never claim a physics optimization worked without a Profiler measurement backing it, per `performance-and-algorithms.md`'s Verification section.
- If a physics performance problem doesn't resolve at this skill's baseline (collider simplification, layer matrix pruning, sleep tuning), escalate to `tech-lead-performance` rather than reaching for native/GPU-level techniques here.
