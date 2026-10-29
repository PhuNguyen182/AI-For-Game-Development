# Systems, Update Order and Iteration

Docs: https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/ (systems-update-order, systems-systembase, systems-systemapi, systems-iterating-data).

## System type
- `ISystem`: unmanaged struct, Burst-compilable (the only one that can be `[BurstCompile]`d); the default.
- `SystemBase`: managed class; only when a managed API is required; not Burst-compilable.
- `SystemAPI`: source-generated cached access to queries, lookups, singletons; usable only inside a system.

## Update order
- `InitializationSystemGroup` first (setup), `SimulationSystemGroup` for most feature systems, `PresentationSystemGroup` last (display reads).
- `[UpdateBefore]`/`[UpdateAfter]` order within one group only; a cross-group expectation written this way silently does nothing.
- `[OrderFirst]`/`[OrderLast]` pin to the edge of the group, ahead of the Before/After sort.
- A custom `ComponentSystemGroup` is worth it only when several systems share ordering and update rate.

## Job hand-off
- Choosing to schedule an `IJobEntity` instead of iterating on the main thread is decided here.
- `JobHandle` chaining, `.Complete()` placement and container disposal are `unity-job-system-and-burst`.
- Burst verification of the system is `unity-burst-compiler`.
- Assign the scheduled job back to `state.Dependency`; otherwise the next system may read the same data concurrently.

## Iteration form
All three sit on `EntityQuery`.
| Form | Use when |
|---|---|
| `SystemAPI.Query<T>` | Main-thread `foreach`, caches its query; a few dozen entities, or managed APIs |
| `IJobEntity` | Per-entity `Execute()`, schedulable and Burst-compilable, query inferred from parameters; thousands of uniform entities |
| `IJobChunk` | Raw per-chunk `NativeArray` access; branch on an optional component once per chunk instead of per entity |

- Entity-to-entity lookups: either job form plus a `ComponentLookup<T>`, `[ReadOnly]` where possible.
- `IJobEntity` infers its query from `Execute()` parameters: adding a parameter silently narrows the entities touched, so a job processing fewer entities is usually a signature change, not a data change.
