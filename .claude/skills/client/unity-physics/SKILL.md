---
name: unity-physics
description: >
  Technique for Unity Physics (`com.unity.physics`) — the deterministic,
  stateless, ECS/DOTS-native rigid body dynamics and spatial query engine.
  Covers physics-specific ECS components (`PhysicsCollider`, `PhysicsVelocity`,
  `PhysicsMass`, `PhysicsDamping`, `PhysicsGravityFactor`, `PhysicsWorldIndex`),
  collider shape selection (box/sphere/capsule/convex hull/mesh/terrain/
  compound), joints and motors, spatial queries (raycast, collider cast,
  distance queries, overlap) against `CollisionWorld`, the simulation
  pipeline's four stages and its `IBodyPairsJob`/`IContactsJob`/
  `IJacobiansJob`/`ICollisionEventsJob`/`ITriggerEventsJob` interception
  points, physics authoring/baking, runtime body creation in code, multiple
  physics worlds, and ghost-collision troubleshooting. This is a completely
  separate engine from Unity's built-in `UnityEngine.Physics`/PhysX
  (`Rigidbody`, `Collider`, `Physics.Raycast`, `FixedJoint`, etc.) — do not
  use this skill for ordinary GameObject/MonoBehaviour PhysX work (colliders,
  the layer collision matrix, Fixed Timestep tuning); that routine domain
  belongs to Unity Engineer per `performance-and-algorithms.md`'s Physics
  section. Only invoke this skill once ECS has already been adopted as an
  architecture-level decision (`unity-ecs-architecture`'s own prerequisite,
  per `performance-and-algorithms.md`'s escalation gate) — Unity Physics
  requires the Entities package to run at all. Do not use this for general,
  non-physics ECS component/system/query design — that's
  `unity-ecs-architecture`. Do not use this for job scheduling, `JobHandle`
  dependency chaining, or `NativeContainer` allocator lifetime — that's
  `unity-job-system-and-burst`, even for physics-specific job interfaces like
  `ICollisionEventsJob`. Do not use this to choose a collection type or
  allocator strategy — that's `unity-collections`, even though
  `CollisionEvents`/`TriggerEvents` are `NativeStream`-shaped and colliders
  are stored behind `BlobAssetReference<T>`. Do not use this for
  `Unity.Mathematics` vector/matrix/quaternion/`Random`/`noise` type or
  function choice — that's `unity-mathematics`, even though every physics
  component/joint parameter is typed with `float3`/`quaternion`. Do not use
  this for Burst compilation tuning — that's `unity-burst-compiler`, even
  though the entire `PhysicsSimulationGroup` is Burst-compiled by default.
---

# Unity Physics — Deterministic ECS Rigid Body Dynamics & Spatial Queries

Sources: see [references/](references/) for the Unity Manual root links, split by topic — [root-links.md](references/root-links.md), [design-and-pipeline.md](references/design-and-pipeline.md), [rigid-bodies-and-components.md](references/rigid-bodies-and-components.md), [colliders.md](references/colliders.md), [joints-and-motors.md](references/joints-and-motors.md), [spatial-queries-and-events.md](references/spatial-queries-and-events.md), [authoring-and-runtime-creation.md](references/authoring-and-runtime-creation.md), [troubleshooting-and-ghost-collisions.md](references/troubleshooting-and-ghost-collisions.md), [dots-relationship.md](references/dots-relationship.md).

## 1. Objective
Model rigid bodies, colliders, joints, and spatial queries correctly for Unity's deterministic, ECS-native physics engine — right component set, right collider shape, right pipeline interception point for custom behavior — without drifting into general ECS design, job scheduling, collection/allocator choice, math-type choice, or Burst tuning, which are sibling skills' territory, and without confusing this engine with the built-in PhysX system that most non-DOTS Unity projects use instead.

## 2. Role
Act as the Unity Physics specialist inside an already-ECS project: given a need for rigid body simulation or spatial queries in that project, you choose the right physics components, collider shapes, joints/motors, query type, and simulation-pipeline hook — you don't decide whether the project should be on ECS/DOTS Physics at all (that's the same escalation-gated decision `unity-ecs-architecture` sits on top of), and you don't re-derive the mechanics owned by the Job System, Collections, Mathematics, or Burst skills.

## 3. When to invoke this skill
- Modeling a new rigid body's ECS component set — `PhysicsCollider`, `PhysicsVelocity`, `PhysicsMass`, `PhysicsDamping`, `PhysicsGravityFactor`, `PhysicsWorldIndex`, `PhysicsCustomTags`, `PhysicsSolverType` — and knowing which are required vs. optional for static/dynamic/kinematic bodies.
- Choosing a collider shape (box, sphere, capsule, cylinder, convex hull, triangle/quad, mesh, terrain) by performance/accuracy trade-off, or combining several into a compound collider for a complex body.
- Choosing and creating a joint (ball and socket, hinge, limited hinge, fixed, prismatic, ragdoll, stiff spring) or a motor (position, linear velocity, rotation, angular velocity) via `Unity.Physics.JointData`'s static creation functions.
- Performing a spatial query — ray cast, collider cast, collider distance, point distance, or overlap — against a single collider or the whole `CollisionWorld` via `PhysicsWorldSingleton`.
- Reading collision/trigger events after a simulation step, via direct `SimulationSingleton.AsSimulation()` access or `ICollisionEventsJob`/`ITriggerEventsJob`.
- Hooking into the simulation pipeline's four stages (`PhysicsCreateBodyPairsGroup`/`PhysicsCreateContactsGroup`/`PhysicsCreateJacobiansGroup`/`PhysicsSolveAndIntegrateGroup`) via `IBodyPairsJob`/`IContactsJob`/`IJacobiansJob` to filter or modify default simulation behavior.
- Setting up physics authoring — baking built-in `UnityEngine` physics authoring components (`Rigidbody`, `BoxCollider`, `HingeJoint`, etc.) or Unity Physics's own authoring components (`PhysicsShapeAuthoring`, `PhysicsBodyAuthoring`) into runtime ECS physics data.
- Creating a rigid body entirely in code at runtime, or setting up multiple independent `PhysicsWorldIndex`-partitioned physics worlds.
- Diagnosing ghost collisions or other collision-detection artifacts at collider boundaries.
- Negative trigger: the project isn't on ECS/DOTS at all, or the task is ordinary GameObject physics (`Rigidbody`, `Collider`, `Physics.Raycast`, built-in `Joint` components at runtime, the layer collision matrix, Fixed Timestep) — that's Unity Engineer's routine PhysX work per `performance-and-algorithms.md`'s Physics section, not this skill, even though some of the same component *names* (`BoxCollider`, `HingeJoint`) appear as Unity Physics *authoring* inputs.
- Negative trigger: no prior architecture-level decision to adopt ECS at all — this skill sits on the exact same `performance-and-algorithms.md` escalation gate `unity-ecs-architecture` does; Unity Physics cannot run without the Entities package.
- Negative trigger: general, non-physics ECS component/system/query/baking design — that's `unity-ecs-architecture`, even for the physics-adjacent authoring→baking pipeline mechanics themselves.
- Negative trigger: scheduling the job that reads/writes physics data, `JobHandle` dependency chains, or `NativeContainer` allocator lifetime — that's `unity-job-system-and-burst`, even for physics-specific job interfaces like `ICollisionEventsJob`/`IContactsJob`.
- Negative trigger: choosing a collection type or allocator strategy — that's `unity-collections`, even though collision/trigger events stream through `NativeStream`-shaped storage and collider geometry lives behind `BlobAssetReference<T>`.
- Negative trigger: `Unity.Mathematics` vector/matrix/quaternion/`Random`/`noise` type or function choice — that's `unity-mathematics`, even though every physics component and joint parameter is typed with `float3`/`quaternion`.
- Negative trigger: Burst-specific compilation tuning — that's `unity-burst-compiler`, even though `PhysicsSimulationGroup` and query code are Burst-compiled by default and the docs recommend running queries inside Burst-compiled jobs.

## 4. How to use this skill
1. **Confirm this is actually a DOTS Physics task, not PhysX.** If the project (or this specific system) isn't on ECS, or the request is about a `Rigidbody`/`Collider`/`Physics.Raycast` on an ordinary GameObject, stop and hand off to Unity Engineer's routine PhysX work instead — the two engines share almost no code path despite similar-sounding component names in the authoring layer.
2. **Confirm the ECS-adoption prerequisite**, exactly as `unity-ecs-architecture` requires — state which architecture-level decision justified ECS (and, specifically, Unity Physics as the physics engine within it) for this feature.
3. **Choose the rigid body's component set by body type.** Every body needs `PhysicsCollider` plus a transform (`LocalTransform`/`LocalToWorld`) and `PhysicsWorldIndex`; a dynamic body additionally needs `PhysicsVelocity` and `PhysicsMass`, with `PhysicsDamping`/`PhysicsGravityFactor` as optional per-body tuning. Don't add dynamic-only components to a body that's meant to stay static or kinematic.
4. **Pick the collider shape by the accuracy/performance trade-off**, per `performance-and-algorithms.md`'s "simplest shape the requirement allows" principle applied to this engine's own shape set: primitives (box/sphere/capsule/cylinder) first, convex hull for an arbitrary-but-still-convex shape, mesh only for static/kinematic detail geometry, and a compound collider when one body genuinely needs several simple shapes combined (e.g. a humanoid's separate limb colliders) rather than one coarse hull.
5. **Choose joints/motors by required degrees of freedom**, not by habit — ball and socket for multi-axis rotation, hinge/limited hinge for one rotational axis, prismatic for one translational axis, fixed to rigidly attach, ragdoll for limited multi-axis character physics, stiff spring for a distance constraint; motors are joints with one driven constraint toward a target position/velocity, tuned via spring frequency and damping ratio.
6. **Pick the spatial query type by what's actually being asked** — ray cast for a line-segment intersection test, collider cast to sweep a shape along a path, collider/point distance for closest-point/proximity checks, overlap for bounding-box containment — against a single collider when the target is already known, or the whole `CollisionWorld` (via `PhysicsWorldSingleton`) when it isn't. Run queries inside Burst-compiled jobs for the performance the docs recommend, but leave that Burst-eligibility verification itself to `unity-burst-compiler`.
7. **Read collision/trigger events at the right point in the frame.** Events are valid only after `PhysicsSimulationGroup` finishes and before it runs again next frame — read them via direct `SimulationSingleton` stream access for simple cases, or `ICollisionEventsJob`/`ITriggerEventsJob` when the read itself should be a scheduled job (hand the actual scheduling/dependency mechanics to `unity-job-system-and-burst`).
8. **Reach for a deeper pipeline hook only when the four stock stages genuinely don't fit** — `IBodyPairsJob` to filter/disable pairs after broadphase, `IContactsJob` to modify contact properties after narrowphase, `IJacobiansJob` to adjust solver constraints before solving; each requires correct `[UpdateAfter]`/`[UpdateBefore]` placement relative to the pipeline's system groups. Don't reach for pipeline modification when a simpler `PhysicsCustomTags`-based filter or a collision-filter/layer setting already solves the problem.
9. **Set up authoring/baking deliberately.** Unity Physics can bake either its own authoring components (`PhysicsShapeAuthoring`, `PhysicsBodyAuthoring`, etc.) or the *built-in* `UnityEngine` physics components (`Rigidbody`, `BoxCollider`, `HingeJoint`, and others) as sub-scene authoring input — both are valid, GameObject-side, Editor-only inputs that bake into the same runtime ECS physics data; neither path makes the runtime simulation PhysX. State which authoring path a given body uses.
10. **State the hand-off explicitly.** Once components/colliders/joints/queries are chosen, scheduling the jobs that use them is `unity-job-system-and-burst`'s territory, their container/allocator choices are `unity-collections`'s, their vector/quaternion math is `unity-mathematics`'s, and their Burst compilation tuning is `unity-burst-compiler`'s — don't extend this skill's guidance into any of them.

## 5. Specific goals / tasks this skill performs
- Choosing a rigid body's ECS component set by body type (static/dynamic/kinematic).
- Choosing collider shapes, including compound colliders, by the accuracy/performance trade-off.
- Choosing and creating joints/motors by required degrees of freedom.
- Choosing and issuing spatial queries (raycast/collider cast/distance/overlap) against a collider or the `CollisionWorld`.
- Reading collision/trigger events and, when needed, hooking deeper simulation-pipeline stages (`IBodyPairsJob`/`IContactsJob`/`IJacobiansJob`).
- Setting up physics authoring/baking (built-in or Unity Physics's own authoring components) and creating bodies in code at runtime.
- Setting up multiple physics worlds via `PhysicsWorldIndex`/`CustomPhysicsSystemGroup` when independent simulation groups are genuinely needed.
- Diagnosing ghost collisions and other boundary-artifact issues.
- Out of scope: ordinary PhysX GameObject physics (Unity Engineer, per `performance-and-algorithms.md`); the ECS-adoption decision itself and general non-physics ECS design (`unity-ecs-architecture`); job scheduling/`JobHandle`/`NativeContainer` lifetime (`unity-job-system-and-burst`); collection type/allocator choice (`unity-collections`); `Unity.Mathematics` type/function choice (`unity-mathematics`); Burst compilation tuning (`unity-burst-compiler`).

## 6. Output format
```
## Physics Work — <body/system name>
- ECS-adoption prerequisite: <which already-approved decision this sits on top of>
- Body type: <static / dynamic / kinematic> — component set chosen
- Collider shape: <box/sphere/capsule/cylinder/convex hull/mesh/terrain/compound> — rationale
- Joint/motor: <type chosen, or "none"> — degrees of freedom needed
- Spatial query: <type, single collider vs. CollisionWorld — or "none">
- Event handling: <direct stream access / ICollisionEventsJob / ITriggerEventsJob — or "none">
- Pipeline hook: <IBodyPairsJob/IContactsJob/IJacobiansJob — or "none, stock pipeline">
- Authoring path: <built-in UnityEngine components / Unity Physics authoring components / runtime code creation>
- Multiple worlds: <yes/no — PhysicsWorldIndex setup if applicable>
- Hand-off: <job scheduling → unity-job-system-and-burst / collections → unity-collections / math → unity-mathematics / Burst → unity-burst-compiler, as applicable>
- Known limitations: <...>
```

## 7. Examples
**Example 1**
- Input: an already-ECS combat prototype (approved for ECS per Tech Lead – Performance) needs melee hit detection — a weapon collider sweeps an arc each swing and should report which enemy bodies it would hit, without physically pushing them.
- Output: modeled the weapon as a `PhysicsCollider`-only kinematic body (no `PhysicsMass`/`PhysicsVelocity`, since it never needs dynamics) tagged with `PhysicsCustomTags` for a "weapon" filter bit; chose a collider-cast spatial query swept along the swing arc against the whole `CollisionWorld` rather than per-enemy raycasts; handed the actual query scheduling to `unity-job-system-and-burst` as a Burst-compiled job (verified separately via `unity-burst-compiler`) and the `float3`/`quaternion` arc-sampling math to `unity-mathematics`.

**Example 2**
- Input: "Add a ground-check raycast to the player controller using `Physics.Raycast`" — the project uses ECS/Unity Physics for its combat simulation, but the player controller itself is still an ordinary MonoBehaviour with a `CharacterController`.
- Output: declined to bring Unity Physics into this — since the player's ground check runs against ordinary GameObject/PhysX colliders, not `CollisionWorld` entities, `Physics.Raycast` is correct as asked; this stays Unity Engineer's routine PhysX territory, and mixing the two physics engines for the same query would need its own deliberate justification (e.g. if ground geometry is itself ECS-baked), which wasn't the case here.

## 8. Edge cases & guardrails
- Never assume `Rigidbody`/`Collider`/`Physics.Raycast`/built-in `Joint` runtime behavior applies here — Unity Physics is a separate, stateless, deterministic engine; the only overlap with PhysX is that its authoring layer can optionally bake the same-named built-in components as design-time input.
- Don't add `PhysicsVelocity`/`PhysicsMass` to a body that's meant to stay static or purely kinematic — those components signal "dynamic" to the simulation.
- Don't reach for a mesh collider or a coarse convex hull when a compound of simple shapes would give both better accuracy and better performance — this engine's own docs recommend primitives/compounds over mesh colliders for anything but static/kinematic detail geometry.
- Don't read `CollisionEvents`/`TriggerEvents` outside their valid window — they're valid only after `PhysicsSimulationGroup` finishes and before it runs again next frame; reading them earlier/later gets stale or empty data.
- Don't reach for a deeper pipeline hook (`IBodyPairsJob`/`IContactsJob`/`IJacobiansJob`) before checking whether a collision filter, layer setting, or `PhysicsCustomTags` filter already solves the problem more simply.
- Watch for ghost collisions at collider boundaries (shared edges/vertices between adjacent colliders, fast-moving objects, high-triangle-count shapes) — mitigate via narrowphase contact modification, simpler collider shapes, or smaller time steps, not by patching over symptoms per-collision.
- Multiple physics worlds are for genuinely independent simulation groups — don't introduce one without a concrete reason two sets of bodies must never interact.
- This engine's determinism (no cached state, same inputs always produce the same outputs) is what makes multi-step-per-frame simulation and rollback-style netcode straightforward — but the actual client-prediction/reconciliation protocol design, when the multiplayer track is active, belongs to Netcode Engineer, not this skill.
