---
name: unity-physics
description: "Unity Physics (DOTS, deterministic): PhysicsCollider, PhysicsVelocity, collision filters, events. Use for ECS physics."
user-invocable: false
---

# Unity Physics (DOTS)

- **Not for:** PhysX bodies (`unity-3d-physics`).
- **Not for:** Box2D (`unity-2d-physics`).
- **Not for:** whether to adopt ECS and general entity/baking design (`unity-ecs-architecture`).
- **Not for:** job scheduling (`unity-job-system-and-burst`).
- **Not for:** containers (`unity-collections`).
- **Not for:** `float3` maths (`unity-mathematics`).
- **Not for:** Burst tuning (`unity-burst-compiler`).
- **Not for:** prediction/reconciliation protocols (`netcode-engineer`).
- **Docs:** https://docs.unity3d.com/Packages/com.unity.physics@6.6/ (`manual/`, `api/`) — pinned 6.6 (Unity 2022.3 LTS and Unity 6 LTS).
  - **Version:** check the installed version before relying on a member.

## References
- **[rigid-bodies-and-components.md](references/rigid-bodies-and-components.md):** Modeling a body, or tuning `PhysicsStep`.
- **[colliders.md](references/colliders.md):** Choosing a shape, or a collider rests above a surface or scales every copy.
- **[joints-and-motors.md](references/joints-and-motors.md):** One body must be constrained or driven relative to another.
- **[spatial-queries-and-events.md](references/spatial-queries-and-events.md):** A query, collision/trigger events, or a pipeline hook is needed.
- **[authoring-and-runtime-creation.md](references/authoring-and-runtime-creation.md):** Choosing how a body is built, creating one in code, or using multiple worlds.
- **[troubleshooting-and-ghost-collisions.md](references/troubleshooting-and-ghost-collisions.md):** A contact fires where nothing touched, or a moved static body stops colliding.

## Steps
1. **Confirm DOTS Physics, not PhysX:**
   - **Determinism:** DOTS Physics is deterministic and stateless (no cached contacts, so geometry flaws show).
   - **Feature set:** smaller than PhysX.
   - **Shared code:** it shares no runtime code with PhysX, only some authoring component names.
   - **`Rigidbody` on a plain GameObject:** routes to `unity-3d-physics`.
2. **Require an approved ECS adoption:** `PhysicsWorld` is rebuilt from ECS component data every step and needs a live Entities `World`.
   - **None:** route to `cto`.
3. **Keep game rules in Core:** physics cannot live in Core; pass the resolved contact or query result into a pure Core function (`csharp-standards` → `coding-principles.md` → Shared Core integrity).
4. **Choose the component set from the body type:** per [rigid-bodies-and-components.md](references/rigid-bodies-and-components.md).
   - **Dynamic:** `PhysicsVelocity` + `PhysicsMass` make a body dynamic.
   - **Static or kinematic:** never add `PhysicsVelocity` + `PhysicsMass` to a body meant to stay static or kinematic.
   - **Body type unstated:** model it static and flag the assumption.
5. **Pick the cheapest collider the mechanic allows:** per [colliders.md](references/colliders.md):
   - **Options:** primitives; convex hull for arbitrary convex; mesh only for static/kinematic; compound over one coarse hull.
   - **Bevel radius and Force Unique:** set both deliberately.
6. **Choose a joint or motor by the degrees of freedom needed:** per [joints-and-motors.md](references/joints-and-motors.md).
7. **Pick the query from the question:** per [spatial-queries-and-events.md](references/spatial-queries-and-events.md).
   - **Selection:** express it with collision filters, not post-filtering.
   - **Events:** read them only inside their validity window.
8. **Use a pipeline hook only after ruling out a filter or `PhysicsCustomTags`:** `IBodyPairsJob`, `IContactsJob` and `IJacobiansJob` each need correct `[UpdateAfter]`/`[UpdateBefore]` placement.
9. **State the authoring path per body:** per [authoring-and-runtime-creation.md](references/authoring-and-runtime-creation.md).
   - **Second physics world:** only when two body groups must never interact.
10. **Tune `PhysicsStep` once per scene:** per-body deviation goes in `PhysicsGravityFactor` or `PhysicsDamping`.
11. **Treat boundary artifacts as geometry first:** per [troubleshooting-and-ghost-collisions.md](references/troubleshooting-and-ghost-collisions.md): simplify colliders before writing an `IContactsJob`.
    - **Static body that stops colliding under a moving parent:** make its `LocalToWorld` current before physics systems run.

## Never
- **Run a query on the main thread when it can run in a Burst job:** it works but gives up parallelism and codegen.

## Output
```
## Physics Work — <body/system name>
- ECS prerequisite: <the adoption decision this sits on>
- Core boundary: <what stayed in Core, what physics data is passed in>
- Body type: <static / dynamic / kinematic> — component set and why
- Collider: <shape or compound, bevel radius, Force Unique — rationale>
- Joint/motor: <type and driven constraint — or "none">
- Query: <type, single collider or CollisionWorld, filter — or "none">
- Events: <direct stream / ICollisionEventsJob / ITriggerEventsJob, and where in the frame — or "none">
- Pipeline hook: <interface, placement, filter ruled out first — or "none">
- Authoring path: <built-in components / Unity Physics authoring / runtime code>
- PhysicsStep: <iterations, substeps, gravity — or "untouched">
- Worlds: <PhysicsWorldIndex partitioning — or "main world only">
```

## Example
- **"Add an `IContactsJob` to discard bad contacts at flat terrain seams":** declined first, seam contacts are the documented ghost-collision case from adjacent colliders sharing edges.
  - **Did instead:** replaced the raw mesh collider on seam tiles with a convex-hull approximation.
