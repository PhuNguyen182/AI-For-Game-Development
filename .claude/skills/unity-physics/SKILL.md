---
name: unity-physics
description: >
  Technique for `com.unity.physics`, the deterministic stateless ECS rigid-body
  and spatial-query engine: `PhysicsCollider`, `PhysicsVelocity`, `PhysicsMass`,
  `PhysicsDamping`, `PhysicsGravityFactor`, `PhysicsWorldIndex`,
  `PhysicsCustomTags`, the scene-global `PhysicsStep`; collider shapes from box
  through convex hull, mesh, terrain and compound; joints and motors; ray,
  collider-cast, distance and overlap queries against `CollisionWorld`;
  `ICollisionEventsJob`, `ITriggerEventsJob`, `IBodyPairsJob`, `IContactsJob`,
  `IJacobiansJob`; authoring, runtime body creation, multiple worlds, ghost
  collisions. Use when entities must simulate or be queried.
  Not for: built-in PhysX bodies (`unity-3d-physics`); built-in Box2D
  (`unity-2d-physics`); the ECS-adoption decision and general entity design
  (`unity-ecs-architecture`); scheduling (`unity-job-system-and-burst`);
  container choice (`unity-collections`); `float3` maths (`unity-mathematics`);
  Burst tuning (`unity-burst-compiler`); prediction protocols
  (`netcode-engineer`).
---

# Unity Physics — Deterministic ECS Rigid Bodies & Spatial Queries

## Bundled resources

### References
Read-only context, loaded on demand so SKILL.md itself stays short.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Package manual and API roots plus the version pin | Starting any task here, or confirming the installed package version |
| [dots-relationship.md](references/dots-relationship.md) | What this package requires and which sibling skill owns each adjacent concern | A request spans physics plus ECS, jobs, containers, maths, or Burst |
| [design-and-pipeline.md](references/design-and-pipeline.md) | Determinism, statelessness, and the four simulation stages | Explaining why this is not PhysX, or considering a pipeline hook |
| [rigid-bodies-and-components.md](references/rigid-bodies-and-components.md) | The physics component set per body type, and `PhysicsStep` | Modeling a body, or tuning solver iterations and gravity |
| [colliders.md](references/colliders.md) | Shape set ranked by cost, compounds, bevel radius, Force Unique | Choosing a shape, or a collider behaves larger or shared-scaled than expected |
| [joints-and-motors.md](references/joints-and-motors.md) | The seven joint types and the four motor types | A mechanic constrains or drives one body relative to another |
| [spatial-queries-and-events.md](references/spatial-queries-and-events.md) | Query types, event streams and their validity window, pipeline interception | Asking a spatial question, reading events, or overriding simulation behaviour |
| [authoring-and-runtime-creation.md](references/authoring-and-runtime-creation.md) | Built-in versus native authoring, code-created bodies, multiple worlds | Deciding how a body gets built, or partitioning simulation |
| [troubleshooting-and-ghost-collisions.md](references/troubleshooting-and-ghost-collisions.md) | Ghost collisions, their causes and mitigations; stale static transforms | A collision fires where nothing should have touched, or a moved static body stops colliding |

## 1. Objective
Model bodies, colliders, joints, and queries correctly for an engine that is deterministic, stateless, and entirely separate from PhysX — the right component set for the body type, the cheapest collider shape the mechanic allows, the query that answers the actual question, and simulation overrides only where a filter cannot do the job. It prevents the failures specific to this engine: components that silently promote a body to dynamic, a shared collider instance that rescales every copy at once, events read outside the one window in which they exist, a static body that stops colliding after its parent moved, ghost collisions patched at the contact level instead of in the geometry, and PhysX habits applied to an engine that shares none of its runtime code.

## 2. Role
Act as the Unity Physics specialist for the client track — the tool reached for in an already-ECS project when entities must simulate as rigid bodies or answer spatial questions. You choose components, shapes, joints, queries, and hooks; you do not decide the project should be on ECS, and you do not re-derive the scheduling, container, maths, or Burst mechanics the sibling skills own.

## 3. When to invoke this skill
- Modeling a body's component set and knowing which parts are required for a static, dynamic, or kinematic body.
- Choosing a collider shape or building a compound from several simple shapes, and setting bevel radius or Force Unique deliberately.
- Choosing a joint or a motor, and creating it through `Unity.Physics.JointData`'s static factories.
- Issuing a ray cast, collider cast, distance query, or overlap against one collider or the whole `CollisionWorld` via `PhysicsWorldSingleton`.
- Reading collision or trigger events after a step, directly or through `ICollisionEventsJob`/`ITriggerEventsJob`.
- Intercepting the simulation pipeline with `IBodyPairsJob`, `IContactsJob`, or `IJacobiansJob` when a filter cannot express the requirement.
- Setting up physics authoring, creating a body entirely in code, or partitioning simulation with `PhysicsWorldIndex`.
- A reported symptom: collisions firing at flat-ground seams, a body sinking or jittering, a static object that stopped colliding after being moved, or a collider that scales every instance at once.
- Negative trigger: ordinary GameObject physics — `Rigidbody`, `Collider`, `Physics.Raycast`, runtime `Joint` components, the layer collision matrix, Fixed Timestep — that is `unity-3d-physics`, and its 2D counterpart is `unity-2d-physics`; both share some authoring component names with this engine and none of its runtime behaviour.
- Negative trigger: no architecture-level decision adopting ECS — this skill sits on exactly the gate `unity-ecs-architecture` describes, because Unity Physics cannot run without the Entities package.
- Negative trigger: general non-physics component, system, query, or baking design — that is `unity-ecs-architecture`, including the `Baker<T>` mechanics physics authoring rides on.
- Negative trigger: scheduling any of the physics job interfaces, chaining `JobHandle`, or container lifetime — that is `unity-job-system-and-burst`; this skill says which interface fits, not how it is scheduled.
- Negative trigger: container or allocator choice — that is `unity-collections`, even though events stream through `NativeStream`-shaped storage and collider geometry sits behind `BlobAssetReference<Collider>`.
- Negative trigger: `Unity.Mathematics` type or function choice — that is `unity-mathematics`, even though every component and joint parameter is `float3`- or `quaternion`-typed.
- Negative trigger: Burst compilation tuning — that is `unity-burst-compiler`, even though `PhysicsSimulationGroup` is Burst-compiled by default and queries are meant to run inside Burst jobs.
- Negative trigger: designing a client-prediction or reconciliation protocol on top of this determinism — that is `netcode-engineer`.

## 4. How to use this skill
1. **Confirm this is DOTS Physics and not PhysX before touching a component**, per [design-and-pipeline.md](references/design-and-pipeline.md) — the two engines share no runtime code path, only some authoring component names, so a request about a `Rigidbody` on an ordinary GameObject routes to `unity-3d-physics` instead. [root-links.md](references/root-links.md) pins the package version below.
2. **Name the ECS-adoption decision this physics work sits on top of**, per [dots-relationship.md](references/dots-relationship.md) — `PhysicsWorld` is rebuilt from ECS component data every step, so with no approved ECS adoption there is nothing to build on and the request routes to `tech-lead-performance`.
3. **Keep the game rule in `Game.Core.*` and treat physics output as input to it** — per `coding-principles.md`'s Shared Core integrity section, Unity Physics needs a live Entities `World` and therefore cannot live in Core; pass the resolved contact or query result into the pure Core function rather than deciding the outcome inside a physics system.
4. **Choose the body's component set from its body type**, per [rigid-bodies-and-components.md](references/rigid-bodies-and-components.md) — every body needs `PhysicsCollider`, a transform, and `PhysicsWorldIndex`; adding `PhysicsVelocity` and `PhysicsMass` is what makes a body dynamic, so putting them on something meant to stay static changes its behaviour rather than merely describing it.
5. **Pick the simplest collider shape the gameplay requirement allows**, per [colliders.md](references/colliders.md) and `performance-and-algorithms.md`'s Physics section — primitives first, convex hull for an arbitrary convex form, mesh only for static or kinematic detail geometry, and a compound of simple shapes in preference to one coarse hull when a body needs detail.
6. **Set bevel radius and Force Unique deliberately rather than by default** — the default bevel radius of 0.05 inflates the hull, which is why a body can rest a visible fraction above a surface, and a collider must be marked Force Unique before non-uniform runtime scaling, or the shared instance rescales every body using it.
7. **Choose a joint or motor by the degrees of freedom the mechanic needs**, per [joints-and-motors.md](references/joints-and-motors.md) — hinge or limited hinge for one rotational axis, prismatic for one translational axis, ball and socket or ragdoll for constrained multi-axis motion, stiff spring for a distance constraint; a motor is a joint with one driven constraint, tuned by spring frequency and damping ratio.
8. **Pick the query type from the question being asked**, per [spatial-queries-and-events.md](references/spatial-queries-and-events.md) — ray cast for a line segment, collider cast to sweep a shape along a path, collider or point distance for proximity, overlap for region containment; query one collider when the target is known and `CollisionWorld` when it is not, and express selection through collision filters rather than post-filtering results.
9. **Read collision and trigger events only inside their validity window** — they exist after `PhysicsSimulationGroup` completes and until it runs again next frame, so a system placed outside that window reads stale or empty streams and reports nothing rather than failing. Trigger colliders never collide; they raise an event where a collision would have been.
10. **Reach for a pipeline hook only after a filter has been ruled out** — `PhysicsCustomTags` and collision filters solve most selective-interaction requirements; `IBodyPairsJob`, `IContactsJob`, and `IJacobiansJob` each need correct placement relative to the pipeline's system groups and are the escalation, not the starting point.
11. **State which authoring path each body uses**, per [authoring-and-runtime-creation.md](references/authoring-and-runtime-creation.md) — built-in `UnityEngine` authoring components and Unity Physics's own both bake into identical runtime data, and neither makes the simulation PhysX; runtime creation is the third path, and multiple worlds are justified only when two body groups must never interact.
12. **Tune `PhysicsStep` once per scene, not per body**, per [rigid-bodies-and-components.md](references/rigid-bodies-and-components.md) — solver iteration and substep counts are the accuracy-versus-cost dial for the whole simulation, and only one `PhysicsStep` should exist; per-body deviation belongs in `PhysicsGravityFactor` or `PhysicsDamping`.
13. **Treat a boundary artifact as a collider-geometry problem first**, per [troubleshooting-and-ghost-collisions.md](references/troubleshooting-and-ghost-collisions.md) — ghost collisions come from shared edges, high-triangle shapes, and large time steps, so simplify geometry before writing an `IContactsJob`; if a moved static body stopped colliding, check its `LocalToWorld` is current before physics runs.
14. **Ask when the body's intended type is unstated** — if it is unclear whether something should be pushed by the simulation or only block it, model it static, say so, and flag it; the reverse assumption silently adds dynamics to level geometry.

## 5. Specific goals / tasks this skill performs
- Choosing the component set for static, dynamic, and kinematic bodies, and tuning the scene's single `PhysicsStep`.
- Selecting collider shapes and compounds, with bevel radius and Force Unique set deliberately.
- Choosing and creating joints and motors by required degrees of freedom.
- Issuing spatial queries against a collider or `CollisionWorld`, with filter-based selection.
- Reading collision and trigger events inside their validity window, directly or through the event job interfaces.
- Intercepting the simulation pipeline when filters cannot express the requirement.
- Setting up authoring, runtime body creation, and `PhysicsWorldIndex` partitioning.
- Diagnosing ghost collisions, stale static transforms, and shared-collider scaling artifacts.
- Out of scope: PhysX GameObject physics (`unity-3d-physics`), built-in 2D physics (`unity-2d-physics`); the ECS-adoption decision and general ECS design (`unity-ecs-architecture`); job scheduling (`unity-job-system-and-burst`); container and allocator choice (`unity-collections`); maths types (`unity-mathematics`); Burst tuning (`unity-burst-compiler`); prediction and reconciliation protocol design (`netcode-engineer`).

## 6. Output format
```
## Physics Work — <body/system name>
- ECS prerequisite: <the adoption decision this sits on top of>
- Engine confirmed: <DOTS Physics — and why this is not a PhysX task>
- Core boundary: <what stayed in Game.Core.*, and what physics data is passed into it>
- Body type: <static / dynamic / kinematic> — component set and why
- Collider: <shape or compound, bevel radius, Force Unique — rationale>
- Joint/motor: <type and driven constraint — or "none">
- Query: <type, single collider or CollisionWorld, filter used — or "none">
- Events: <direct stream / ICollisionEventsJob / ITriggerEventsJob, and where in the frame — or "none">
- Pipeline hook: <interface and placement, and the filter ruled out first — or "none, stock pipeline">
- Authoring path: <built-in components / Unity Physics authoring / runtime code>
- PhysicsStep: <solver iterations, substeps, gravity — or "untouched">
- Worlds: <PhysicsWorldIndex partitioning — or "main world only">
- Layer: <Game.Core.* rules invoked / Game.Client.* physics components and systems>
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what the delivered solution does not cover>
- Latent concerns: <failure modes not yet triggered: assumptions that hold only under current conditions, thresholds not yet reached, trade-offs knowingly deferred>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: an already-ECS combat prototype needs melee hit detection — a weapon sweeps an arc each swing and must report which enemies it would hit without pushing them.
- Output: modeled the weapon as `PhysicsCollider` plus transform and `PhysicsWorldIndex` only, deliberately omitting `PhysicsVelocity` and `PhysicsMass` so it never becomes dynamic; tagged it with `PhysicsCustomTags` and expressed enemy selection as a collision filter rather than filtering results afterwards; chose a collider cast swept along the arc against `CollisionWorld` rather than a fan of per-enemy ray casts; damage resolution stayed in `Game.Core.Combat`, taking the hit list as input; scheduling handed to `unity-job-system-and-burst`, `[BurstCompile]` verification to `unity-burst-compiler`, and the arc `float3`/`quaternion` maths to `unity-mathematics`.

**Example 2**
- Input: "Ground checks are missing collisions on the flat terrain seams — can you add an `IContactsJob` to discard the bad contacts?"
- Output: declined as a first move — spurious contacts at seams are the documented ghost-collision case, caused by adjacent colliders sharing edges that are evaluated independently, and a contact-level filter treats the symptom while leaving the geometry that produces it. Replaced the raw mesh collider on the seam tiles with a convex-hull approximation per §4's boundary-artifact step, which removed the artifact; the pipeline hook stayed available for a case where geometry genuinely cannot be simplified.

**Example 3**
- Input: scaling one crate prefab at runtime resizes every crate in the scene, and a platform that moves with its parent has stopped colliding entirely.
- Output: two separate documented causes. The crates share one collider instance, so non-uniform runtime scaling requires Force Unique on the shape before each body owns its own; the platform is a static body under a moving parent, whose `LocalToWorld` was not current when physics ran, so the simulation still saw its original position. Fixed the transform ordering and marked the crate shape unique, per §4's collider and troubleshooting steps.

## 8. Edge cases & guardrails
- Never carry PhysX assumptions across — this engine is stateless and deterministic, and shares nothing with `UnityEngine.Physics` at runtime beyond some authoring component names.
- Never add `PhysicsVelocity` or `PhysicsMass` to a body meant to stay static or kinematic — those components make it dynamic, they do not merely describe it.
- Never scale a collider non-uniformly at runtime without Force Unique — the instance is shared, so one body's scale becomes every body's scale.
- Never read collision or trigger events outside their window — outside it the streams are stale or empty, and the system reports nothing instead of failing.
- Never reach for a pipeline hook before ruling out a collision filter or `PhysicsCustomTags` — interception is harder to place correctly and harder to reason about later.
- Never treat ghost collisions as contact-level bugs — check shared edges, triangle counts, and time step first, and simplify geometry before modifying contacts.
- Never let a static body move under a parent without ensuring `LocalToWorld` is current before physics systems run — it will simply stop colliding where it appears to be.
- Never create a second physics world without a concrete reason two body groups must never interact — the partitioning is a shared-component value, so it also splits chunks.
- If a body's intended type is unstated, model it static and flag the assumption — silently adding dynamics to level geometry is the costlier mistake.
