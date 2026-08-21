---
name: unity-2d-physics
description: >
  Unity built-in 2D physics (Box2D) on GameObjects — `Rigidbody2D` body
  types, mass, linear and angular damping, gravity scale, interpolation,
  `CollisionDetectionMode2D`, sleep, `Slide`; `Collider2D` shapes
  (Box/Circle/Capsule/Polygon/Edge/Composite), `PhysicsMaterial2D` friction
  and bounciness combine modes, `Effector2D` (Area, Point, Platform,
  Surface, Buoyancy), the nine `Joint2D` types, `ConstantForce2D`,
  `OnCollisionEnter2D`, `OnTriggerEnter2D`, and the `Physics2D` layer
  matrix. Use when a 2D body tunnels, jitters, sticks, or ignores a
  collision. Not for: 3D physics (`unity-3d-physics`), DOTS physics
  (`unity-physics`), sprite shape authoring (`unity-2d-sprite`), tile
  collision generation (`unity-tilemap`), spline colliders
  (`unity-2d-spriteshape`), damage and state rules (`csharp-engineer`),
  escalated profiling (`tech-lead-performance`).
---

# Unity 2D Physics — Box2D Bodies, Colliders, Effectors & Joints

## Bundled resources

### References

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Manual roots and the topic→file map for this engine | Starting any 2D physics task |
| [rigidbody-2d.md](references/rigidbody-2d.md) | Body types, damping, interpolation, sleep, forces, `Slide` | Configuring or moving a body, or motion looks wrong |
| [collider-2d.md](references/collider-2d.md) | The six shapes, composite geometry, contact data, layer matrix | Choosing a shape, or a contact fires or fails unexpectedly |
| [physics-material-2d.md](references/physics-material-2d.md) | Friction, bounciness, and the combine-mode priority order | A surface is too slippery, too grippy, or bounces unexpectedly |
| [effectors-2d.md](references/effectors-2d.md) | The five effectors and their collider/trigger prerequisites | Building a one-way platform, force zone, conveyor, or fluid |
| [joints-2d.md](references/joints-2d.md) | All nine joints, the shared base, motors, limits, breaking | Constraining two bodies, or a joint sags, breaks, or fights |
| [constant-force-2d.md](references/constant-force-2d.md) | Continuous linear force and torque versus a one-shot impulse | Something must accelerate over time rather than start fast |

## 1. Objective
Get a 2D body to move, collide, and rest the way the design describes, using the cheapest configuration that expresses it — and rule out the silent failures this engine specialises in: a collider that never contacts because both sides are edges or the layer matrix excludes them, an effector wired to a collider with Used By Effector off, a body driven through its Transform so the solver never sees the motion, a shared material edited at runtime for every collider using it, and tunnelling that Discrete detection was never going to catch.

## 2. Role
Act as the built-in 2D physics specialist for the client track — the skill reached for whenever `Rigidbody2D`, `Collider2D`, `Effector2D`, `Joint2D`, or `ConstantForce2D` must be configured on an ordinary GameObject, or whenever a 2D body's observed behaviour does not match the design.

## 3. When to invoke this skill
- Configuring a `Rigidbody2D` — body type, mass, damping, gravity scale, interpolation, collision detection mode, constraints, or sleep.
- Choosing a `Collider2D` shape, pairing colliders through a `CompositeCollider2D`, or setting trigger versus solid.
- Assigning or tuning a `PhysicsMaterial2D`, or pruning the 2D layer collision matrix.
- Building behaviour that physics does not model on its own — a one-way platform, wind zone, magnet, conveyor, or buoyant volume.
- Constraining two bodies with a joint, or diagnosing a joint that sags, oscillates, or breaks.
- A symptom report: a fast body passing through a wall, a body jittering under a following camera, two objects that should collide and do not, a stack that never comes to rest.
- Negative trigger: `Rigidbody`, `Collider`, `CharacterController`, `Cloth`, or `Physics.*` — that's `unity-3d-physics`, a structurally similar but separate API.
- Negative trigger: `PhysicsCollider`, `PhysicsVelocity`, `CollisionWorld` on an ECS project — that's `unity-physics`, an unrelated engine that happens to share vocabulary.
- Negative trigger: authoring the sprite outline a collider derives its shape from — that's `unity-2d-sprite`; this skill consumes that geometry.
- Negative trigger: generating collision from painted tiles — `TilemapCollider2D` setup is `unity-tilemap`'s, and this skill takes over at the body and material on the result.
- Negative trigger: the collider a Sprite Shape spline auto-generates — that's `unity-2d-spriteshape`; this skill configures what is attached to it.
- Negative trigger: deciding damage, knockback magnitude, or a state transition from a contact — that's `csharp-engineer`'s Shared Core, per `coding-principles.md`'s Shared Core integrity section.
- Negative trigger: a physics cost that survives shape simplification, matrix pruning, and sleep tuning — escalate to `tech-lead-performance`.

## 4. How to use this skill
1. **Confirm which physics engine the project is actually on before touching a component**, per [root-links.md](references/root-links.md) — `Rigidbody2D` and `Rigidbody` share almost every concept name and no behaviour, and DOTS `unity-physics` shares the vocabulary again; a mis-scoped answer here is wasted whole, not partially useful.
2. **Choose the body type by who moves the body**, per [rigidbody-2d.md](references/rigidbody-2d.md) — Dynamic when the solver moves it, Kinematic when script or animation moves it and other bodies must still sense it, and no `Rigidbody2D` at all for immovable geometry, since a lone collider is already backed by a hidden static body. Add an explicit Static body only when that collider occasionally moves.
3. **Move every body through the physics API, never through its Transform** — `MovePosition`/`MoveRotation` in `FixedUpdate`, or `Slide` for character-style motion. Assigning `transform.position` teleports the body, skips contact generation entirely, and is the usual reason a moving platform passes through walls or fails to carry anything.
4. **Pick the simplest collider shape the silhouette allows**, per [collider-2d.md](references/collider-2d.md) and `performance-and-algorithms.md`'s Physics section — Circle, Box, or Capsule before Polygon, Polygon before a traced outline. Merge many adjacent colliders with a `CompositeCollider2D`, choosing Polygons geometry when bodies must be inside the shape and Outlines only when edges alone suffice.
5. **Prune the layer collision matrix instead of filtering inside callbacks** — a pair excluded in Project Settings costs nothing, while an `if` inside `OnCollisionEnter2D` has already paid for broadphase, narrowphase, and the managed callback. Reach for per-collider `includeLayers`/`excludeLayers` only for a genuine exception to a matrix rule.
6. **Assign a `PhysicsMaterial2D` asset rather than tuning friction per collider**, per [physics-material-2d.md](references/physics-material-2d.md) — and remember the result of a contact is decided by *both* materials: when their combine modes differ, the higher-priority mode wins along Average, Mean, Multiply, Minimum, Maximum, so a surface cannot be reasoned about from its own asset alone.
7. **Reach for an effector only when the design asks for behaviour real physics would not produce**, per [effectors-2d.md](references/effectors-2d.md) — one-way platforms, force volumes, conveyors, buoyancy. Every effector requires Used By Effector on the collider it acts through, and Area, Point, and Buoyancy expect a trigger while Platform and Surface expect a solid collider. A plain `AddForce` script is the simpler answer when the requirement is just "push it".
8. **Choose the joint by the constraint the design states, not by generality**, per [joints-2d.md](references/joints-2d.md) — Hinge for one pivot, Slider for one axis, Distance for a taut link, Spring for an elastic one, Wheel for suspension, Friction to bleed off relative motion, Fixed to weld, Target to chase a moving world point, Relative to hold an offset. Set Break Force deliberately or leave it infinite, and handle `OnJointBreak2D` if it can break.
9. **Use `ConstantForce2D` only for force that should keep accelerating a body**, per [constant-force-2d.md](references/constant-force-2d.md) — it is not a speed setting, so cap the resulting velocity with linear damping rather than expecting the component to level off.
10. **Keep the rule out of the physics callback**, per `coding-principles.md`'s Shared Core integrity section — Box2D's solver is not bit-identical across platforms, so a value derived inside a contact callback is exactly the kind of non-determinism that breaks client prediction against server authority. Pass the resolved contact point, normal, and relative velocity into `Game.Core.*` and let it decide the outcome.
11. **Confirm a physics fix with a measurement before reporting it**, per `performance-and-algorithms.md`'s Verification section — the Profiler's Physics2D markers for solver cost, and the Physics Debug window for colliders that never sleep or pairs that should never have been tested.
12. **When the symptom does not identify its layer, state the assumption and confirm** — "the player falls through the floor" is a body type, a detection mode, a layer matrix entry, or a Transform-driven move, and changing the wrong one hides the real cause rather than fixing it.

## 5. Specific goals / tasks this skill performs
- `Rigidbody2D` configuration and physics-API-driven movement, including `Slide`.
- Collider shape selection, composite merging, and trigger versus solid decisions.
- `PhysicsMaterial2D` authoring and combine-mode reasoning.
- Layer collision matrix pruning and per-collider layer overrides.
- Effector setup for designed non-physical behaviour.
- Joint selection, motor and limit tuning, and break handling.
- `ConstantForce2D` for continuous acceleration.
- Collision and trigger callback wiring that hands data to Shared Core.
- Out of scope: 3D physics (`unity-3d-physics`), DOTS physics (`unity-physics`), sprite physics-shape authoring (`unity-2d-sprite`), tile collision generation (`unity-tilemap`), Sprite Shape colliders (`unity-2d-spriteshape`), gameplay rules (`csharp-engineer`), escalated optimisation (`tech-lead-performance`).

## 6. Output format
```
## 2D Physics Work — <feature/body name>
- Engine confirmed: built-in 2D Box2D (not 3D PhysX, not DOTS Unity Physics)
- Rigidbody2D: body type <Dynamic/Kinematic/Static/none>, mass <n>, damping <linear>/<angular>, gravity scale <n>, interpolation <mode>, detection <Discrete/Continuous>, constraints <list>, sleep <mode>
- Movement path: <MovePosition/Slide/AddForce/solver-driven> — why the Transform is not used
- Collider: shape(s) <list>, trigger <yes/no>, composite <yes/no + geometry type>
- Material: <asset or per-collider>, friction <n>, bounciness <n>, combine <friction/bounce modes>
- Layer matrix: pairs pruned <list or none>, per-collider overrides <list or none>
- Effector / Joint (if applicable): type, Used By Effector <yes/no>, break force, rationale over the simpler alternative
- Shared Core boundary: <data handed to Core vs decision left in the callback>
- Verification: Profiler Physics2D <finding>, Physics Debug <finding>, or "not yet measured"
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
- Input: "Bullets sometimes pass straight through enemies at high speed."
- Output: tunnelling, and the fix has two halves. Set the bullet `Rigidbody2D`'s Collision Detection to Continuous — Discrete only tests the body's new position, so a body that crosses a thin collider within one step never registers. Then confirmed the bullet is moved by velocity rather than by `transform.position`, since a Transform assignment teleports past the sweep that Continuous exists to perform. Kept the bullet's collider a Circle rather than the sprite-traced polygon it had, per `performance-and-algorithms.md`'s Physics section. Hand-off: the damage the hit resolves to → `csharp-engineer`'s Shared Core.

**Example 2**
- Input: "Add an `AreaEffector2D` to the water so things float in it."
- Output: declined as written — Area applies a directional force and does not model a fluid surface, so a body pushed upward accelerates out of the water instead of settling. Used a `BuoyancyEffector2D` with its Surface Level at the waterline, plus Density, Linear Drag, and Angular Drag for the settling feel, on a trigger collider with Used By Effector enabled. Noted that leaving that flag off is the single most common reason a fully configured effector does nothing at all.

**Example 3**
- Input: "The crate slides on ice but our ice material's Friction is already 0."
- Output: the contact uses both materials. The crate's own material specified Friction Combine = Maximum, which outranks the ice material's Mean on the priority order, so the effective friction came from the crate, not the ice. Set the crate to Mean and left ice at 0; also flagged that `Collider2D` exposes only `sharedMaterial`, so editing that asset at runtime would have changed every collider referencing it rather than just this crate.

## 8. Edge cases & guardrails
- Never move a simulated body by assigning `transform.position` — it teleports without generating contacts, and no detection mode compensates.
- Never assume two edge colliders will collide — `EdgeCollider2D` cannot contact another `EdgeCollider2D` regardless of body type or trigger setting.
- Never assume a Kinematic body collides with static or other kinematic bodies — it only meets Dynamic bodies until `useFullKinematicContacts` is enabled.
- Never add an effector without enabling Used By Effector on the collider it acts through — the component configures cleanly and does nothing, with no warning.
- Never reason about friction or bounciness from one material — the higher-priority combine mode of the pair decides, in the order Average, Mean, Multiply, Minimum, Maximum.
- Never write to `sharedMaterial` at runtime expecting a per-instance change — `Collider2D` has no per-instance `material` property, unlike its 3D counterpart, so the edit is global.
- Never port a 3D force call unchanged — `ForceMode2D` offers only Force and Impulse, and there is no `relativeTorque`, because 2D rotation is a single scalar.
- Never switch Body Type every frame — the change recalculates mass and re-evaluates contacts, and is a per-switch cost, not a free toggle.
- Never let a physics callback decide a game outcome — the solver's results vary across platforms, which is precisely what `coding-principles.md`'s Shared Core integrity section forbids relying on.
- Never claim a physics optimisation without a Profiler or Physics Debug measurement, per `performance-and-algorithms.md`'s Verification section.
- If a body's misbehaviour could be body type, detection mode, layer matrix, or movement path, name which one is being assumed before changing settings — each of the four produces the same visible symptom.
