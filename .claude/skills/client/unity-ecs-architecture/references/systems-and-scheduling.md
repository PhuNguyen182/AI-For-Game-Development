# Systems, Update Order & Job System Integration

Covers SKILL.md steps 5, 6 (system type/placement, and the handoff point where ECS iteration becomes a Job System job).

## Manual
- [SystemBase overview](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/systems-systembase.html) — managed system class; `OnCreate`/`OnUpdate`/`OnDestroy`; can call managed APIs, but isn't itself Burst-compilable.
- [System groups](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/systems-update-order.html) — default root groups (`InitializationSystemGroup`, `SimulationSystemGroup`, `PresentationSystemGroup`); `UpdateBefore`/`UpdateAfter`/`OrderFirst`/`OrderLast` to control placement within a group; custom `ComponentSystemGroup` subclasses.
- [SystemAPI overview](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/systems-systemapi.html) — cached, source-generated access to queries, component lookups, and singletons from inside `ISystem`/`SystemBase`.
- [Job system in Entities introduction](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/systems-scheduling-jobs.html) — how systems schedule `IJobEntity`/`IJobChunk` jobs to iterate entity data on worker threads.

**Hand-off point:** once entity data iteration is scheduled as a job (`IJobEntity`/`IJobChunk`), it becomes an ordinary Job System job underneath — the same `JobHandle` dependency-chaining, `.Complete()`/dispose discipline, and `NativeContainer` allocator rules from `unity-job-system-and-burst` apply unchanged. This skill only covers designing the ECS-side query/iteration; it doesn't restate those scheduling mechanics.

## Scripting API
- [Interface `IJobEntity`](https://docs.unity3d.com/Packages/com.unity.entities@6.6/api/Unity.Entities.IJobEntity.html) — job that executes `Execute()` once per entity matching an inferred `EntityQuery`; simpler alternative to `IJobChunk` for straightforward per-entity work.
