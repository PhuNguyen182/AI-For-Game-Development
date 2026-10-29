---
name: unity-physics
description: "Unity Physics (DOTS, deterministic): PhysicsCollider/Velocity/Mass, simulation groups, queries, collision filters, events, stateless stepping. Use for ECS physics."
user-invocable: false
---

# Unity Physics (DOTS)

Not for: PhysX bodies (`unity-3d-physics`), Box2D (`unity-2d-physics`), whether to adopt ECS and general entity/baking design (`unity-ecs-architecture`), job scheduling (`unity-job-system-and-burst`), containers (`unity-collections`), `float3` maths (`unity-mathematics`), Burst tuning (`unity-burst-compiler`), prediction/reconciliation protocols (`netcode-engineer`).
Docs: https://docs.unity3d.com/Packages/com.unity.physics@6.6/ (`manual/`, `api/`) — pinned 6.6 (Unity 2022.3 LTS and Unity 6 LTS); check the installed version before relying on a member.

| Reference | Read when |
|---|---|
| [rigid-bodies-and-components.md](references/rigid-bodies-and-components.md) | Modeling a body, or tuning `PhysicsStep` |
| [colliders.md](references/colliders.md) | Choosing a shape, or a collider rests above a surface or scales every copy |
| [joints-and-motors.md](references/joints-and-motors.md) | One body must be constrained or driven relative to another |
| [spatial-queries-and-events.md](references/spatial-queries-and-events.md) | A query, collision/trigger events, or a pipeline hook is needed |
| [authoring-and-runtime-creation.md](references/authoring-and-runtime-creation.md) | Choosing how a body is built, creating one in code, or using multiple worlds |
| [troubleshooting-and-ghost-collisions.md](references/troubleshooting-and-ghost-collisions.md) | A contact fires where nothing touched, or a moved static body stops colliding |

## Steps
1. **Confirm DOTS Physics, not PhysX** — it is deterministic and stateless (no cached contacts, so geometry flaws show), has a smaller feature set than PhysX, and shares no runtime code with it, only some authoring component names. A `Rigidbody` on a plain GameObject routes to `unity-3d-physics`.
2. **Require an approved ECS adoption** — `PhysicsWorld` is rebuilt from ECS component data every step and needs a live Entities `World`. None → `cto`.
3. **Keep game rules in `Game.Core.*`** — physics cannot live in Core; pass the resolved contact or query result into a pure Core function (`csharp-standards` → `coding-principles.md` → Shared Core integrity).
4. **Choose the component set from the body type**, per [rigid-bodies-and-components.md](references/rigid-bodies-and-components.md). `PhysicsVelocity` + `PhysicsMass` make a body dynamic. Never add them to a body meant to stay static or kinematic. Body type unstated → model it static and flag the assumption.
5. **Pick the cheapest collider the mechanic allows**, per [colliders.md](references/colliders.md): primitives, convex hull for arbitrary convex, mesh only for static/kinematic, compound over one coarse hull. Set bevel radius and Force Unique deliberately.
6. **Choose a joint or motor by the degrees of freedom needed**, per [joints-and-motors.md](references/joints-and-motors.md).
7. **Pick the query from the question**, per [spatial-queries-and-events.md](references/spatial-queries-and-events.md). Express selection with collision filters, not post-filtering. Read events only inside their validity window.
8. **Use a pipeline hook only after ruling out a filter or `PhysicsCustomTags`** — `IBodyPairsJob`, `IContactsJob` and `IJacobiansJob` each need correct `[UpdateAfter]`/`[UpdateBefore]` placement.
9. **State the authoring path per body**, per [authoring-and-runtime-creation.md](references/authoring-and-runtime-creation.md). A second physics world only when two body groups must never interact.
10. **Tune `PhysicsStep` once per scene**; per-body deviation goes in `PhysicsGravityFactor` or `PhysicsDamping`.
11. **Treat boundary artifacts as geometry first**, per [troubleshooting-and-ghost-collisions.md](references/troubleshooting-and-ghost-collisions.md): simplify colliders before writing an `IContactsJob`. A static body that stops colliding under a moving parent: make its `LocalToWorld` current before physics systems run.

## Never
- Run a query on the main thread when it can run in a Burst job; it works but gives up parallelism and codegen.

## Output
```
## Physics Work — <body/system name>
- ECS prerequisite: <the adoption decision this sits on>
- Core boundary: <what stayed in Game.Core.*, what physics data is passed in>
- Body type: <static / dynamic / kinematic> — component set and why
- Collider: <shape or compound, bevel radius, Force Unique — rationale>
- Joint/motor: <type and driven constraint — or "none">
- Query: <type, single collider or CollisionWorld, filter — or "none">
- Events: <direct stream / ICollisionEventsJob / ITriggerEventsJob, and where in the frame — or "none">
- Pipeline hook: <interface, placement, filter ruled out first — or "none">
- Authoring path: <built-in components / Unity Physics authoring / runtime code>
- PhysicsStep: <iterations, substeps, gravity — or "untouched">
- Worlds: <PhysicsWorldIndex partitioning — or "main world only">
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Add an `IContactsJob` to discard bad contacts at flat terrain seams" → declined first: seam contacts are the documented ghost-collision case from adjacent colliders sharing edges; replaced the raw mesh collider on seam tiles with a convex-hull approximation.
