---
name: unity-3d-physics
description: >
  Technique for Unity's built-in 3D physics engine (`UnityEngine.Physics`,
  PhysX-backed, GameObject/MonoBehaviour-driven) — `CharacterController`
  locomotion, `Rigidbody` dynamics (mass/drag/interpolation/collision
  detection mode/constraints/sleep), `Collider` shapes and `PhysicsMaterial`
  surface properties, collision/trigger events and the layer collision
  matrix, joints (`FixedJoint`, `HingeJoint`, `SpringJoint`,
  `CharacterJoint`, `ConfigurableJoint`), `ArticulationBody` chains, ragdoll
  setup via the Ragdoll Wizard and joint/ragdoll stability tuning, the
  `Cloth` component for Skinned Mesh Renderer fabric simulation, and
  Profiler/Memory Profiler/Physics Debug window-driven physics optimization.
  Use this for any task touching `Rigidbody`, `Collider`, `CharacterController`,
  `Joint`, `ArticulationBody`, `Cloth`, or `Physics.*` static calls on an
  ordinary GameObject. Do not use this for `com.unity.physics`
  (ECS/DOTS-native, deterministic, stateless rigid body physics) — that's
  `unity-physics`, a structurally unrelated engine despite some shared
  authoring-component names. Do not use this for 2D physics
  (`Rigidbody2D`, `Collider2D`, `Joint2D`, `Physics2D.*`) — a separate,
  structurally similar but distinct API surface this skill does not cover.
  Do not use this for actual gameplay rule logic that happens to consume
  physics data (damage formulas, state machines, ability cooldowns) — that
  belongs in Shared Core, per `coding-principles.md`'s Shared Core
  integrity rule; this skill only covers wiring the Unity-side physics
  components themselves. Do not use this for shader/particle-based
  cloth-like or cloth-adjacent visual effects with no actual `Cloth`
  component or mesh-deformation physics involved — that's
  `technical-artist`. Do not use this for deep, escalated performance work
  beyond Profiler/Memory Profiler/Physics Debug-window-driven optimization
  (native plugin-level, GPU-level) — that's `tech-lead-performance`.
---

# Unity 3D Physics — Built-in PhysX Rigid Body, Character, Joint & Cloth Simulation

Sources: see [references/](references/) for the Unity Manual root links, split by topic — [root-links.md](references/root-links.md), [character-controller.md](references/character-controller.md), [rigidbody-physics.md](references/rigidbody-physics.md), [collision.md](references/collision.md), [joints.md](references/joints.md), [ragdoll-physics.md](references/ragdoll-physics.md), [physics-optimization.md](references/physics-optimization.md), [cloth.md](references/cloth.md).

## 1. Objective
Configure Unity's built-in 3D PhysX physics correctly on ordinary GameObjects — right locomotion approach, right Rigidbody/Collider settings, right joint for the required degrees of freedom, a stable ragdoll, a correctly-scoped Cloth setup — and keep the whole thing measurably performant, without drifting into DOTS/ECS physics, 2D physics, gameplay rule logic, or performance escalation territory that belong to sibling skills or roles.

## 2. Role
Act as the built-in 3D physics specialist: given a need for character movement, rigid body dynamics, collision response, joints, ragdolls, or cloth simulation on a normal (non-ECS) GameObject, you choose and configure the right `UnityEngine.Physics`-namespace components and settings — you don't decide gameplay outcomes from physics data (that's Shared Core's job) and you don't reach for DOTS/ECS physics, 2D physics, or deep native/GPU-level optimization, which are sibling skills'/roles' territory.

## 3. When to invoke this skill
- Choosing between `CharacterController`-driven and `Rigidbody`-driven character locomotion, or configuring either one.
- Configuring a `Rigidbody`'s mass, drag/angular drag, `isKinematic`, interpolation, collision detection mode, constraints, or sleep behavior.
- Choosing a `Collider` shape, setting up a `PhysicsMaterial` (friction/bounciness), configuring trigger vs. solid colliders, or tuning the layer collision matrix.
- Reading/handling collision or trigger events (`OnCollisionEnter`/`OnTriggerEnter` and their `Stay`/`Exit` counterparts), or choosing a collision detection algorithm for fast-moving bodies.
- Choosing and creating a joint (Fixed, Hinge, Spring, Character, Configurable) by required degrees of freedom, or evaluating whether `ArticulationBody` is a better fit than a Rigidbody+Joint chain.
- Building or stabilizing a ragdoll via the Ragdoll Wizard.
- Setting up a `Cloth` component on a Skinned Mesh Renderer for character fabric simulation, including its colliders and self-collision/constraint tuning.
- Diagnosing or fixing a physics performance problem using the Unity Profiler, Memory Profiler, or Physics Debug window.
- Negative trigger: the project is ECS/DOTS and the task is `com.unity.physics` component/collider/joint/query work (`PhysicsCollider`, `PhysicsVelocity`, `CollisionWorld`, etc.) — that's `unity-physics`, a completely separate engine despite some shared authoring-component *names*.
- Negative trigger: 2D physics (`Rigidbody2D`, `Collider2D`, `HingeJoint2D`, `Physics2D.Raycast`, etc.) — a structurally similar but distinct API surface this skill does not cover.
- Negative trigger: the actual gameplay decision built on top of physics data (damage calculation on collision, a state machine transition, an ability's cooldown/economy math) — that's `csharp-engineer`'s Shared Core, per `coding-principles.md`'s Shared Core integrity rule; this skill stops at wiring the physics component and handing already-resolved data (e.g. a contact point, a hit normal) to Core.
- Negative trigger: shader/particle-driven cloth-like or fabric-like visual effects with no real `Cloth` component or mesh-deformation physics involved — that's `technical-artist`.
- Negative trigger: a physics performance problem that survives the Profiler/Memory Profiler/Physics Debug-window-driven baseline in this skill (e.g. needs a native plugin or compute-shader-level fix) — escalate to `tech-lead-performance`, per its own scope definition.
- Negative trigger: camera-side physics-driven raycasting for click-to-move/aim picking is fine to call `Physics.Raycast`/`Physics.RaycastNonAlloc` from, but the camera scripting itself (coordinate conversions, follow/shake) is `unity-camera-fundamentals`'s territory, not this skill's.

## 4. How to use this skill
1. **Confirm scope first.** This skill is classic built-in 3D PhysX (`UnityEngine.Physics`, GameObject/MonoBehaviour-driven) — `Rigidbody`, `Collider`, `CharacterController`, `Joint`, `ArticulationBody`, `Cloth`. If the project is on ECS/DOTS and the task is `com.unity.physics` work, stop and hand off to `unity-physics`. If the task is 2D, stop — this skill doesn't cover `Physics2D`.
2. **Respect the Shared Core boundary.** Any gameplay decision that happens to be triggered by a physics event (damage on collision, a knockback amount, an ability's hit resolution) is computed in `Game.Core.*`; this skill's components only detect/resolve the physical event and hand already-resolved data (contact point, normal, relative velocity) to Core — they never decide an outcome themselves, per `coding-principles.md`'s Shared Core integrity rule.
3. **Choose the locomotion approach deliberately.** `CharacterController` — a kinematic capsule moved manually via `Move`/`SimpleMove`, not affected by forces, doesn't interact with other rigidbodies via physics — fits most player/NPC locomotion. Rigidbody-driven movement (`Rigidbody.MovePosition`/`AddForce` on a non-kinematic body) fits when the character must be realistically pushed by, or push, other dynamic rigidbodies. Don't default to one without checking which behavior the design actually needs; see [character-controller.md](references/character-controller.md) and [rigidbody-physics.md](references/rigidbody-physics.md).
4. **Configure the Rigidbody deliberately**, per [rigidbody-physics.md](references/rigidbody-physics.md): mass and drag/angular drag sized to the body's actual scale and desired feel; `isKinematic` only for bodies driven purely by script/animation; `interpolation` set to `Interpolate` (visual smoothing against `FixedUpdate`) when a Rigidbody's motion is watched by a moving/following camera, `Extrapolate` only when genuinely needed; `collisionDetectionMode` set to a continuous variant for small/fast-moving bodies that could tunnel through thin colliders at `Discrete`; sleep behavior left enabled unless a specific reason forces bodies to stay always-awake.
5. **Configure Colliders deliberately**, per [collision.md](references/collision.md): primitive shapes (box/sphere/capsule) over Mesh Colliders wherever the requirement allows, per `performance-and-algorithms.md`'s simplest-collider-shape rule; a dedicated `PhysicsMaterial` for any surface whose friction/bounciness matters instead of leaving Default on everything; trigger vs. solid chosen by whether the collider should physically block or only detect overlap; the layer collision matrix pruned to skip pairs that should never interact, instead of filtering them in `OnCollisionEnter`/`OnTriggerEnter` after the fact — this is the same principle `performance-and-algorithms.md`'s Physics section already states, applied here at the component-configuration level.
6. **Choose the joint by required degrees of freedom**, per [joints.md](references/joints.md): Fixed to rigidly attach two bodies, Hinge for a single rotational axis (doors, wheels without drive), Spring for a distance constraint with spring/damper behavior, Character Joint for a 3-axis limited-rotation constraint (ragdoll limbs), Configurable Joint only when the required per-axis linear/angular drive-and-limit combination genuinely isn't expressible by a named joint — reaching for Configurable Joint by default when a named joint already fits is unnecessary complexity, per KISS in `coding-principles.md`.
7. **Consider `ArticulationBody` instead of a Rigidbody+Joint chain** for anything that's structurally a jointed mechanical/kinematic chain (multi-link ragdolls, robotic arms, vehicle suspensions) — it solves the whole chain together for better stability than sequentially-solved individual joints; see [ragdoll-physics.md](references/ragdoll-physics.md).
8. **Build ragdolls through the Ragdoll Wizard** on a rigged humanoid skeleton, then tune per [RagdollStability guidance](references/ragdoll-physics.md) — sane mass ratios between adjacent limbs, joint limits that aren't so loose the ragdoll folds unnaturally nor so stiff it looks frozen — rather than accepting the wizard's generated defaults uncritically.
9. **Set up Cloth only on a Skinned Mesh Renderer**, per [cloth.md](references/cloth.md): tune stretching/bending stiffness, damping, and tethers for the fabric's desired stiffness/behavior; assign capsule/sphere colliders for character-body interaction; enable self/inter-collision only when visibly needed, since it's the most expensive Cloth setting. This is a real mesh-deformation physics simulation, not a substitute for a shader-based cloth-like visual effect with no actual `Cloth` component (`technical-artist`'s territory when that's genuinely all that's needed).
10. **Apply the optimization discipline from [physics-optimization.md](references/physics-optimization.md) before calling physics performance work done**: profile with the Unity Profiler (`Physics.FixedUpdate`/`Physics.Simulate`, broadphase/narrowphase cost), the Memory Profiler (collision-callback array/GC churn), and the Physics Debug window (overly complex colliders, unnecessary interaction pairs, bodies failing to enter sleep) — matching `performance-and-algorithms.md`'s Verification section's "measured, not asserted" rule, applied specifically to physics.
11. **State the hand-off explicitly.** Gameplay decisions built on top of physics data → `csharp-engineer`'s Shared Core. Performance problems that survive this skill's Profiler/Memory Profiler/Physics Debug-window baseline → `tech-lead-performance`. Visual-only cloth-like or particle effects with no real mesh physics → `technical-artist`. DOTS/ECS physics → `unity-physics`. 2D physics → out of this skill's scope entirely.

## 5. Specific goals / tasks this skill performs
- Choosing `CharacterController` vs. Rigidbody-driven locomotion for a character.
- Configuring `Rigidbody` mass/drag/interpolation/collision-detection-mode/constraints/sleep.
- Choosing collider shapes, configuring `PhysicsMaterial`, trigger vs. solid, and the layer collision matrix.
- Handling collision/trigger events and choosing an appropriate collision detection algorithm for fast-moving bodies.
- Choosing/creating joints (Fixed/Hinge/Spring/Character/Configurable) by required degrees of freedom, and evaluating `ArticulationBody` for jointed chains.
- Building and stabilizing ragdolls via the Ragdoll Wizard.
- Setting up `Cloth` on a Skinned Mesh Renderer, including colliders and stiffness/self-collision tuning.
- Diagnosing and fixing physics performance issues via Profiler/Memory Profiler/Physics Debug window.
- Out of scope: `com.unity.physics`/DOTS physics (`unity-physics`); 2D physics (not covered by any skill in this set); gameplay rule logic consuming physics data (`csharp-engineer`'s Shared Core); shader/particle-only cloth-like VFX (`technical-artist`); performance work beyond the profiler-driven baseline here (`tech-lead-performance`).

## 6. Output format
```
## Physics Work — <feature/body name>
- Scope confirmed: built-in 3D PhysX (not DOTS Unity Physics, not Physics2D)
- Locomotion approach (if applicable): CharacterController / Rigidbody-driven — rationale
- Rigidbody settings (if applicable): mass <n>, drag <n>/<n>, isKinematic <bool>, interpolation <mode>, collision detection <mode>, constraints <list>
- Collider setup: shape(s) chosen, PhysicsMaterial (friction/bounciness), trigger vs. solid, layer matrix pruned <yes/no>
- Joint/ArticulationBody (if applicable): type chosen, degrees of freedom needed
- Ragdoll (if applicable): Wizard used, stability tuning applied
- Cloth (if applicable): stiffness/damping/tethers, colliders assigned, self-collision <on/off + why>
- Shared Core boundary: confirmed no gameplay decision made in physics-layer code
- Optimization check: Profiler / Memory Profiler / Physics Debug window findings, or "not yet measured"
- Hand-off: <gameplay logic → csharp-engineer / deep perf → tech-lead-performance / VFX-only → technical-artist / DOTS → unity-physics, as applicable>
- Known limitations: <...>
```

## 7. Examples
**Example 1**
- Input: "Add a third-person player controller that can walk, jump, and get pushed back by an explosion."
- Output: chose `CharacterController` for the player's day-to-day walk/jump locomotion (manual `Move`, no unwanted physics interaction, predictable and easy to reconcile against Shared Core input state), but modeled the explosion knockback as a temporary switch to a Rigidbody-driven impulse phase (`AddForce` with `ForceMode.Impulse`) for the duration of the knockback, then handed control back to `CharacterController` once the character's velocity settled — the actual knockback *magnitude* came from Shared Core's damage/knockback formula, this skill only applied the already-resolved force vector.
- Hand-off: knockback magnitude formula → `csharp-engineer`.

**Example 2**
- Input: "The boss's cape should react physically to movement and wind, and the boss ragdolls on death."
- Output: added a `Cloth` component to the boss's cape Skinned Mesh Renderer, tuned stretching/bending stiffness and `Use Gravity`/`External Acceleration` for a heavy-fabric feel, added capsule colliders along the boss's spine/shoulders for body collision; built the death ragdoll via the Ragdoll Wizard on the boss's skeleton, then tuned joint limits and adjacent-limb mass ratios per [RagdollStability guidance](references/ragdoll-physics.md) after the wizard's defaults looked visibly too stiff on the shoulders.
- Optimization check: Physics Debug window confirmed the cape's self-collision was off (not visually needed at this cloth's resolution) to avoid its extra solver cost.

## 8. Edge cases & guardrails
- Never assume `com.unity.physics` (`PhysicsCollider`, `CollisionWorld`, etc.) or `Physics2D` behavior applies here — this is the built-in `UnityEngine.Physics` (PhysX) engine on ordinary GameObjects; route ECS/DOTS physics work to `unity-physics` instead.
- Never make a gameplay decision (damage, score, state transition) inside a `Rigidbody`/`Collider` physics callback — resolve the outcome in Shared Core and let the physics-layer code only detect the event and pass along already-resolved data.
- Don't leave `interpolation`/`collisionDetectionMode` at their unexamined defaults for camera-watched or fast-moving bodies — visible jitter and tunneling are the direct symptom of skipping this.
- Don't reach for a Mesh Collider or Configurable Joint by default when a primitive collider or a named joint (Fixed/Hinge/Spring/Character) already expresses the requirement — see KISS in `coding-principles.md`.
- Don't accept the Ragdoll Wizard's generated joint limits/mass ratios uncritically — verify visually and tune per [RagdollStability guidance](references/ragdoll-physics.md) before calling a ragdoll done.
- `Cloth` only works on a Skinned Mesh Renderer — it is not a general-purpose fabric/rope/flag solution for non-skinned meshes; don't reach for it outside that constraint, and don't enable self/inter-collision unless a visible problem actually needs it, since it's Cloth's most expensive setting.
- Never claim a physics optimization worked without a Profiler/Memory Profiler/Physics Debug-window measurement backing it, per `performance-and-algorithms.md`'s Verification section — asserted-from-Big-O-alone claims aren't acceptable here either.
- If a physics performance problem doesn't resolve at this skill's baseline (collider simplification, layer matrix pruning, sleep tuning, simulation frequency), escalate to `tech-lead-performance` rather than reaching for native/GPU-level techniques here.
