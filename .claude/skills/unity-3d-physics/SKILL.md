---
name: unity-3d-physics
description: >
  Unity built-in 3D physics (PhysX) on GameObjects — `Rigidbody` mass,
  drag, interpolation, collision detection mode, constraints, sleep;
  `Collider` shapes and `MeshCollider` cooking, `PhysicsMaterial`,
  `CharacterController` `Move`/`SimpleMove`, `FixedJoint`, `HingeJoint`,
  `SpringJoint`, `CharacterJoint`, `ConfigurableJoint`,
  `ArticulationBody`, Ragdoll Wizard, `Cloth`, `OnCollisionEnter`,
  `Physics.Raycast`, the layer matrix, and `Physics.simulationMode`.
  Use when a body tunnels, jitters, sinks, will not sleep, or a ragdoll
  or joint chain is unstable. Not for: 2D physics
  (`unity-2d-physics`), DOTS physics (`unity-physics`), pathfound agent
  movement (`unity-navmesh-navigation`), animation blending
  (`unity-animation`), shader-only cloth looks (`technical-artist`),
  damage and state rules (`csharp-engineer`), escalated optimisation
  (`tech-lead-performance`).
---

# Unity 3D Physics — PhysX Bodies, Characters, Joints, Ragdolls & Cloth

## Bundled resources

### References

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Manual section roots and the topic→file map | Starting any 3D physics task |
| [character-controller.md](references/character-controller.md) | Capsule locomotion, `Move` vs `SimpleMove`, tuning ratios | Building or fixing character movement |
| [rigidbody-physics.md](references/rigidbody-physics.md) | Mass, drag, interpolation, detection modes, forces | Configuring a body, or motion looks wrong |
| [collision.md](references/collision.md) | Collider shapes, `PhysicsMaterial`, contacts, layer matrix | Choosing a shape, or contacts fire or fail wrongly |
| [joints.md](references/joints.md) | The five joints, drives, limits, break settings | Constraining two bodies |
| [ragdoll-physics.md](references/ragdoll-physics.md) | Ragdoll Wizard, stability rules, `ArticulationBody` | Building a ragdoll, or a joint chain jitters or stretches |
| [cloth.md](references/cloth.md) | `Cloth` properties, constraints, collider pairing | Simulating a cape, skirt, or cloak |
| [physics-optimization.md](references/physics-optimization.md) | Profiler markers, memory techniques, tuning knobs | Physics costs too much, or the frame stutters |

## 1. Objective
Get 3D bodies, characters, joints, ragdolls, and cloth behaving as the design describes at a cost the platform can pay — and rule out the failures PhysX specialises in: a body driven through its Transform so the solver never sees it, a joint chain destabilised by a mass ratio rather than by its limits, a repeatedly moved static collider forcing a broadphase rebuild every frame, a `Cloth` component silently converting the renderer under it, and a stutter that is fixed-timestep catch-up rather than a physics cost at all.

## 2. Role
Act as the built-in 3D physics specialist for the client track — the skill reached for whenever `Rigidbody`, `Collider`, `CharacterController`, `Joint`, `ArticulationBody`, or `Cloth` must be configured on an ordinary GameObject, or whenever simulated motion does not match the design.

## 3. When to invoke this skill
- Choosing between `CharacterController` and Rigidbody-driven locomotion, or configuring either.
- Configuring a `Rigidbody` — mass, drag, `isKinematic`, interpolation, collision detection mode, constraints, sleep.
- Choosing collider shapes, cooking a `MeshCollider`, assigning a `PhysicsMaterial`, or pruning the layer collision matrix.
- Selecting a joint by degrees of freedom, or evaluating `ArticulationBody` against a Rigidbody-and-joint chain.
- Building a ragdoll, or stabilising one that jitters, stretches, or explodes on spawn.
- Setting up `Cloth` on a Skinned Mesh Renderer, including its colliders and constraint painting.
- A symptom report: a projectile passing through walls, a stack that never sleeps, a character stuck on a step, frame stutter under physics load.
- Negative trigger: `Rigidbody2D`, `Collider2D`, `Physics2D.*` — that's `unity-2d-physics`, a separate engine with the same vocabulary.
- Negative trigger: `PhysicsCollider`, `PhysicsVelocity`, `CollisionWorld` on an ECS project — that's `unity-physics`.
- Negative trigger: a character whose movement is driven by pathfinding — `NavMeshAgent` steering, avoidance, and off-mesh links are `unity-navmesh-navigation`'s, and this skill takes over only where the agent hands off to a physical body.
- Negative trigger: blending a ragdoll back into animation, or the Animator that drives the rig — that's `unity-animation`.
- Negative trigger: a cloth-*looking* effect with no mesh simulation — that's `technical-artist`.
- Negative trigger: deciding damage, knockback magnitude, or a state transition from a contact — that's `csharp-engineer`'s Shared Core, per `coding-principles.md`'s Shared Core integrity section.
- Negative trigger: a cost that survives shape simplification, matrix pruning, sleep, and timestep tuning — escalate to `tech-lead-performance`.

## 4. How to use this skill
1. **Confirm which physics engine the project is actually on before touching a component**, per [root-links.md](references/root-links.md) — built-in PhysX, `Physics2D`, and DOTS `unity-physics` share nearly every type name and no behaviour, so a mis-scoped answer is wasted whole rather than partly useful.
2. **Choose the locomotion model by whether the character must be pushed**, per [character-controller.md](references/character-controller.md) — `CharacterController` is a kinematic capsule that pushes bodies but is never pushed, which is what makes it responsive and predictable; a Rigidbody character is the choice only when other dynamic bodies must genuinely move it. Note the component is documented as supported-but-legacy from Unity 6.5, so weigh it for new work — it is not `[Obsolete]`, so `coding-principles.md`'s Obsolete APIs section does not forbid it.
3. **Move every simulated body through the physics API, never through its Transform** — `MovePosition`/`MoveRotation` from `FixedUpdate` for a Rigidbody, `Move` or `SimpleMove` for a `CharacterController`. A Transform write teleports the body past contact generation, and it also desynchronises any joint the body belongs to.
4. **Configure the Rigidbody against how it is watched and how fast it moves**, per [rigidbody-physics.md](references/rigidbody-physics.md) — Interpolate whenever a following camera watches the body, a continuous detection mode for anything small and fast enough to cross a thin collider in one step, and sleep left enabled unless a specific requirement forbids it.
5. **Pick the simplest collider the requirement allows, and stop moving static ones**, per [collision.md](references/collision.md) and `performance-and-algorithms.md`'s Physics section — primitives before `MeshCollider`, and a Kinematic Rigidbody rather than repeatedly repositioning a collider that has none, which forces a broadphase rebuild. Prune the layer matrix rather than filtering inside `OnCollisionEnter`.
6. **Choose the joint by required degrees of freedom, not by generality**, per [joints.md](references/joints.md) — Fixed to weld, Hinge for one axis, Spring for an elastic link, Character for a limited three-axis limb. `ConfigurableJoint` is correct only when no named joint expresses the per-axis drive and limit combination, per KISS in `coding-principles.md`.
7. **Prefer `ArticulationBody` for anything that is structurally a chain**, per [ragdoll-physics.md](references/ragdoll-physics.md) — it solves the whole hierarchy together, which removes the pairwise instability long Rigidbody-and-joint chains suffer, at the cost of Character Joint's limit authoring.
8. **Fix ragdoll instability at the mass ratio and the limits before touching solver iterations** ([ragdoll-physics.md](references/ragdoll-physics.md)) — keep adjacent limb masses within roughly 2×, since about 10× is where the solver becomes unstable; never leave an angular limit at a small non-zero value, because under about 5° it jitters where exactly 0 locks cleanly; and avoid non-uniform scale anywhere in the hierarchy.
9. **Set up `Cloth` only on a Skinned Mesh Renderer**, per [cloth.md](references/cloth.md) — adding it to a plain Mesh Renderer silently converts that renderer. Paint constraints, assign capsule and sphere colliders for body interaction, and leave self-collision and inter-collision off until a visible problem needs them, since they are its most expensive settings.
10. **Keep the rule out of the physics callback**, per `coding-principles.md`'s Shared Core integrity section — PhysX results are not reproducible across platforms, so pass the contact point, normal, and relative velocity into `Game.Core.*` and let it decide the outcome that the server must be able to agree with.
11. **Diagnose with the tool that matches the symptom before tuning anything**, per [physics-optimization.md](references/physics-optimization.md) and `performance-and-algorithms.md`'s Verification section — the Profiler for solver cost, the Memory Profiler for callback and query allocation, and the Physics Debug window for colliders that never sleep. A `Physics.Simulate` call count climbing toward ten in one frame is fixed-timestep catch-up from a preceding heavy frame, so the fix is that frame, not the physics settings.
12. **When the symptom does not identify its cause, name the assumption before changing settings** — "the character falls through the floor" is a detection mode, a layer matrix entry, a Transform-driven move, or a collider that was never there, and each fix hides the other three.

## 5. Specific goals / tasks this skill performs
- Locomotion model selection and `CharacterController` tuning.
- `Rigidbody` configuration and physics-API-driven movement.
- Collider shape selection, `MeshCollider` cooking, `PhysicsMaterial` assignment, layer matrix pruning.
- Joint selection and `ArticulationBody` evaluation for jointed chains.
- Ragdoll construction and stability tuning.
- `Cloth` setup, constraint painting, and collider pairing.
- Physics diagnosis via Profiler, Memory Profiler, and Physics Debug window.
- Out of scope: 2D physics (`unity-2d-physics`), DOTS physics (`unity-physics`), agent pathing (`unity-navmesh-navigation`), animation blending (`unity-animation`), visual-only cloth (`technical-artist`), gameplay rules (`csharp-engineer`), escalated optimisation (`tech-lead-performance`).

## 6. Output format
```
## 3D Physics Work — <feature/body name>
- Engine confirmed: built-in PhysX (not Physics2D, not DOTS Unity Physics)
- Locomotion (if applicable): CharacterController / Rigidbody-driven — why, and gravity handling
- Rigidbody: mass <n>, drag <n>/<n>, isKinematic <bool>, interpolation <mode>, detection <mode>, constraints <list>, sleep <on/off>
- Movement path: <MovePosition/Move/AddForce> — why the Transform is not used
- Collider: shape(s), MeshCollider cooking <settings or n/a>, PhysicsMaterial <friction/bounce>, layer matrix pruned <list or none>
- Joint / ArticulationBody (if applicable): type, degrees of freedom, break settings, why not the alternative
- Ragdoll (if applicable): mass ratios <range>, angular limits <values or locked>, solver iterations <n>, preprocessing <on/off>
- Cloth (if applicable): stiffness/damping/tethers, colliders assigned, self-collision <on/off + why>
- Shared Core boundary: <data handed to Core vs decision left in the callback>
- Verification: Profiler <finding>, Memory Profiler <finding>, Physics Debug <finding>, or "not yet measured"
- Layer: Game.Client.*
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what the delivered solution does not cover — omit this line entirely if there are genuinely none>
- Latent concerns: <failure modes not yet triggered: assumptions that hold only under current conditions, thresholds not yet reached, trade-offs knowingly deferred>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: "Third-person player that walks and jumps, and gets thrown back by an explosion."
- Output: `CharacterController` for ordinary locomotion — a kinematic capsule with no momentum is what makes walk and jump feel immediate and keeps the pose easy to reconcile against Core's input state. Since `Move` applies no gravity, gravity is integrated by hand into the motion vector each frame, and `isGrounded` is read from the previous move rather than assumed. Knockback runs as a temporary Rigidbody-driven phase with `AddForce(..., ForceMode.Impulse)`, returning control once velocity settles. The force *magnitude* came from Shared Core's knockback formula; this skill applied an already-resolved vector. Skin Width was set to 10% of Radius and Step Offset to 0.3 for a 2 m character, per the Manual's tuning ratios.

**Example 2**
- Input: "The ragdoll flails and stretches. Let's just raise solver iterations to 50."
- Output: declined as the first move — solver iterations are the fourth thing to try and the most expensive. The chain's forearm was about 12× the mass of its hand, past the roughly 10× point where the pairwise joint solver becomes unstable, and two joints carried 2° angular limits, which jitter where exactly 0 would lock the axis cleanly. Fixed the mass ratios to within 2×, set the two axes to 0, and disabled Enable Preprocessing on the joints that spawned overlapping level geometry. Solver iterations then only needed 10–20, not 50, and the cost is paid by every jointed body in the scene rather than by this ragdoll alone.

**Example 3**
- Input: "Frame stutters badly in the physics-heavy arena, but the Profiler says each physics step is cheap."
- Output: each step *is* cheap — the Calls column showed `Physics.Simulate` running close to ten times in the stuttering frame. That is fixed-timestep catch-up: a preceding expensive frame left simulation debt that PhysX repays all at once, compounding an already slow frame. Raised `Time.fixedDeltaTime` as immediate relief, then traced and fixed the originating heavy frame, which was an asset load, not physics at all. Hand-off: if it had survived that, the cost profile would go to `tech-lead-performance`.

## 8. Edge cases & guardrails
- Never move a simulated or joint-connected body by writing its Transform — it teleports past contact generation and desynchronises the joint solver.
- Never assume `CharacterController.Move` applies gravity — it does not; only `SimpleMove` does, and `SimpleMove` ignores the Y component of the speed passed to it.
- Never call `Move` and `SimpleMove` in the same frame, or either one more than once per frame — the results compound in ways the collision flags will not report.
- Never move a static collider repeatedly — it rebuilds the broadphase; give it a Kinematic Rigidbody instead.
- Never leave a joint angular limit at a small non-zero value — under roughly 5° it jitters, where exactly 0 locks the axis cleanly.
- Never connect bodies with an extreme mass ratio — past roughly 10× the joint solver becomes unstable, and no iteration count reliably compensates.
- Never apply non-uniform scale in a jointed or ragdoll hierarchy — collider and joint robustness degrade in ways that read as tuning problems.
- Never add `Cloth` to a plain Mesh Renderer expecting it to be ignored — Unity replaces the renderer with a Skinned Mesh Renderer.
- Never cache the `Collision` object from a callback when `Physics.reuseCollisionCallbacks` is on — one instance is reused for every callback, so the cached reference changes underneath.
- Never let a physics callback decide a game outcome — PhysX results differ across platforms, which `coding-principles.md`'s Shared Core integrity section forbids depending on.
- Never claim a physics optimisation without a Profiler, Memory Profiler, or Physics Debug measurement, per `performance-and-algorithms.md`'s Verification section.
- If a symptom fits several causes, say which one is assumed before changing settings — fixing the wrong one usually masks the real cause rather than leaving it visible.
