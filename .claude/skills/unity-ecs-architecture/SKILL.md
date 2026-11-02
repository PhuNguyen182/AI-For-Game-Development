---
name: unity-ecs-architecture
description: "Entities/ECS 6.6: IComponentData, Baker<T>, ISystem, SystemAPI.Query, IJobEntity, ECB. Use when writing ECS code."
user-invocable: false
---

# Unity ECS Architecture

- **Not for:** job scheduling, `JobHandle` chains, allocator lifetime (`unity-job-system-and-burst`).
- **Not for:** HPC# subset, `FloatMode`, AOT (`unity-burst-compiler`).
- **Not for:** container choice (`unity-collections`).
- **Not for:** `float3`/`quaternion` maths (`unity-mathematics`).
- **Not for:** colliders, joints (`unity-physics`).
- **Not for:** `RenderMeshArray`, DOTS Instancing (`unity-entities-graphics`).
- **Not for:** ghosts and replication (`netcode-for-entities`).
- **Not for:** GPU effects (`compute-shader-vfx`).
- **Not for:** whether ECS is warranted at all (`technical-architect`).
- **Docs:** https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/index.html and /api/index.html — pinned to 6.6.
  - **Version:** check the installed version in `manifest.json` before relying on a member.

## References
- **[core-concepts.md](references/core-concepts.md):** Modeling a feature's data, chunk layout, or sync points.
- **[component-types.md](references/component-types.md):** Choosing how a value is stored on an entity, or sharing immutable bulk data (blobs).
- **[systems-and-scheduling.md](references/systems-and-scheduling.md):** Placing a system, or choosing `SystemAPI.Query` / `IJobEntity` / `IJobChunk`.
- **[baking-and-authoring.md](references/baking-and-authoring.md):** Design-time GameObject data has to reach entities.
- **[structural-changes-and-ecb.md](references/structural-changes-and-ecb.md):** Entities or components are created, added, removed or destroyed during iteration.

## Steps
1. **Name the architecture decision that approved ECS for this feature:**
   - **None exists:** stop and route to `cto` (a foundation choice).
   - **Needing threads:** not a reason to adopt ECS (Job System + Burst work without entities).
2. **Keep the game rule in Core; the system only iterates:** read components, call the pure Core function, write back.
   - **Formula rewritten in `OnUpdate`:** a second implementation (`Unity.Entities` cannot be referenced from Core).
3. **Model entities and archetypes before naming a system:** component sets follow access pattern, not code structure ([core-concepts.md](references/core-concepts.md)).
4. **Pick each component kind by how its value changes:** per [component-types.md](references/component-types.md).
   - **Default:** unmanaged `IComponentData`.
   - **`ISharedComponentData`:** only when many entities share a value.
   - **`IBufferElementData`:** variable-length data.
   - **`IEnableableComponent`:** state that toggles often.
5. **Budget the archetype against the 16 KiB chunk:** every field on a hot archetype means fewer entities per chunk.
   - **Rarely-read data:** split it into its own component.
6. **Read authoring data through the Baker's own dependency APIs:** never off the authoring object ([baking-and-authoring.md](references/baking-and-authoring.md)).
7. **Prefer `ISystem` in an existing group:** `SystemBase` only for a required managed API.
   - **`UpdateBefore`/`UpdateAfter`:** only for a real data dependency.
8. **Choose the iteration form by what the loop needs per chunk:** per [systems-and-scheduling.md](references/systems-and-scheduling.md).
9. **Batch structural changes through an `EntityCommandBuffer`:** with a stable sort key on every parallel write ([structural-changes-and-ecb.md](references/structural-changes-and-ecb.md)).
10. **Re-acquire every handle after a structural change:** `DynamicBuffer<T>`, `ComponentLookup<T>`, `RefRW<T>`; the stale view reads plausible garbage.
11. **Share immutable bulk data through a `BlobAssetReference<T>`:** instead of copying it per entity ([component-types.md](references/component-types.md)).
12. **Confirm the built layout before claiming it:**
    - **`Window > Entities > Hierarchy`:** the actual baked component set per World; Authoring/Runtime/Mixed modes.
    - **`Window > Entities > Systems`:** the resolved order per group.
    - **System absent from Systems:** it was not created (query matched nothing, or other World); check presence before debugging order.
    - **Performance claims:** need a before/after capture from `unity-profiler-diagnostics`.
13. **Shared or per-entity value ambiguous:** model per-entity (`IComponentData`), say so and flag it.
    - **`ISharedComponentData`:** never silently pick it.

## Never
- **Shared Core rule in a system:** never reimplement it there.
- **Call `EntityManager` structural APIs inside a job or an iteration loop:** a sync point completes every job that could touch the data.
- **Component handle acquired before a structural change:** never use it.
- **Leave a parallel ECB write without a deterministic sort key:** it breaks prediction and server reconciliation, and reproduces intermittently.
- **Use managed `IComponentData` classes:** they are deprecated and unusable in jobs/Burst.
- **Use `IAspect` or `Entities.ForEach`:** both are deprecated since Entities 1.4; use `SystemAPI.Query<T>`/`IJobEntity`/`IJobChunk`.
- **Extra Worlds and default update order:** never create extra Worlds or override default update order without a stated reason.

## Output
```
## ECS Architecture Work — <feature/system>
- Approved by: <architecture decision and who made it>
- Core boundary: <rule logic kept in Core, what the system calls>
- Components: <kind per value, chunk-density consequence>
- Authoring/baking: <authoring + Baker<T>, or "none">
- System(s): <ISystem/SystemBase, group, ordering and its data reason>
- Iteration: <SystemAPI.Query / IJobEntity / IJobChunk — why>
- Structural changes: <ECB + sort key, or "none">
- Blob assets: <data and why, or "none">
- Measurement: <before/after from unity-profiler-diagnostics, or "no performance claim made">
```

## Example
- **"Give each enemy an `ISharedComponentData` with faction ID and current target":** declined as written.
  - **Why:** the per-entity target makes the value unique, fragmenting the archetype into about one chunk per enemy.
  - **Did instead:** faction ID stays shared; target becomes an ordinary `IComponentData`.
