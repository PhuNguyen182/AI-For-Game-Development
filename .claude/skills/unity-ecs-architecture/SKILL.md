---
name: unity-ecs-architecture
description: "Entities/ECS 6.6: IComponentData, archetypes and chunks, Baker<T> baking, ISystem/SystemBase, SystemAPI.Query, IJobEntity, IJobChunk, EntityCommandBuffer, BlobAssetReference. Use when designing or writing ECS code."
user-invocable: false
---

# Unity ECS Architecture

Not for: job scheduling, `JobHandle` chains, allocator lifetime (`unity-job-system-and-burst`); HPC# subset, `FloatMode`, AOT (`unity-burst-compiler`); container choice (`unity-collections`); `float3`/`quaternion` maths (`unity-mathematics`); colliders, joints (`unity-physics`); `RenderMeshArray`, DOTS Instancing (`unity-entities-graphics`); ghosts and replication (`netcode-for-entities`); GPU effects (`compute-shader-vfx`); whether ECS is warranted at all (`technical-architect`).
Docs: https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/index.html and /api/index.html — pinned to 6.6; check the installed version in `manifest.json` before relying on a member.

| Reference | Read when |
|---|---|
| [core-concepts.md](references/core-concepts.md) | Modeling a feature's data, chunk layout, or sync points |
| [component-types.md](references/component-types.md) | Choosing how a value is stored on an entity, or sharing immutable bulk data (blobs) |
| [systems-and-scheduling.md](references/systems-and-scheduling.md) | Placing a system, or choosing `SystemAPI.Query` / `IJobEntity` / `IJobChunk` |
| [baking-and-authoring.md](references/baking-and-authoring.md) | Design-time GameObject data has to reach entities |
| [structural-changes-and-ecb.md](references/structural-changes-and-ecb.md) | Entities or components are created, added, removed or destroyed during iteration |

## Steps
1. **Name the architecture decision that approved ECS for this feature.** None exists → stop and route to `technical-architect`; needing threads is not a reason to adopt ECS (Job System + Burst work without entities).
2. **Keep the game rule in `Game.Core.*`; the system only iterates**: read components, call the pure Core function, write back. A formula rewritten in `OnUpdate` is a second implementation (`Unity.Entities` cannot be referenced from Core).
3. **Model entities and archetypes before naming a system** ([core-concepts.md](references/core-concepts.md)); component sets follow access pattern, not code structure.
4. **Pick each component kind by how its value changes**: unmanaged `IComponentData` by default; `ISharedComponentData` only when many entities share a value; `IBufferElementData` for variable-length data; `IEnableableComponent` for state that toggles often ([component-types.md](references/component-types.md)).
5. **Budget the archetype against the 16 KiB chunk**: every field on a hot archetype means fewer entities per chunk. Split rarely-read data into its own component.
6. **Read authoring data through the Baker's own dependency APIs**, never off the authoring object ([baking-and-authoring.md](references/baking-and-authoring.md)).
7. **Prefer `ISystem` in an existing group**; `SystemBase` only for a required managed API. `UpdateBefore`/`UpdateAfter` only for a real data dependency.
8. **Choose the iteration form by what the loop needs per chunk** ([systems-and-scheduling.md](references/systems-and-scheduling.md)).
9. **Batch structural changes through an `EntityCommandBuffer`**, with a stable sort key on every parallel write ([structural-changes-and-ecb.md](references/structural-changes-and-ecb.md)).
10. **Re-acquire every handle after a structural change** (`DynamicBuffer<T>`, `ComponentLookup<T>`, `RefRW<T>`): the stale view reads plausible garbage.
11. **Share immutable bulk data through a `BlobAssetReference<T>`** instead of copying it per entity ([component-types.md](references/component-types.md)).
12. **Confirm the built layout in `Window > Entities > Hierarchy`** (actual baked component set per World; Authoring/Runtime/Mixed modes) **and `Window > Entities > Systems`** (resolved order per group) before claiming it. A system absent from Systems was not created (query matched nothing, or other World) — check presence before debugging order. Performance claims need a before/after capture from `unity-profiler-diagnostics`.
13. **Shared or per-entity value ambiguous**: model per-entity (`IComponentData`), say so and flag it; never silently pick `ISharedComponentData`.

## Never
- Reimplement a Shared Core rule inside a system.
- Call `EntityManager` structural APIs inside a job or an iteration loop (sync point completes every job that could touch the data).
- Use a component handle acquired before a structural change.
- Leave a parallel ECB write without a deterministic sort key (breaks prediction and server reconciliation, reproduces intermittently).
- Use managed `IComponentData` classes (deprecated; unusable in jobs/Burst) or `IAspect` (removed in the Entities 6.x line; use `SystemAPI.Query<T>`/`IJobEntity`/`IJobChunk`).
- Create extra Worlds or override default update order without a stated reason.

## Output
```
## ECS Architecture Work — <feature/system>
- Approved by: <architecture decision and who made it>
- Core boundary: <rule logic kept in Game.Core.*, what the system calls>
- Components: <kind per value, chunk-density consequence>
- Authoring/baking: <authoring + Baker<T>, or "none">
- System(s): <ISystem/SystemBase, group, ordering and its data reason>
- Iteration: <SystemAPI.Query / IJobEntity / IJobChunk — why>
- Structural changes: <ECB + sort key, or "none">
- Blob assets: <data and why, or "none">
- Verified via: <Hierarchy / Systems window — what was confirmed>
- Measurement: <before/after from unity-profiler-diagnostics, or "no performance claim made">
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Give each enemy an `ISharedComponentData` with faction ID and current target" → declined as written: the per-entity target makes the value unique, fragmenting the archetype into about one chunk per enemy. Faction ID stays shared; target becomes an ordinary `IComponentData`.
