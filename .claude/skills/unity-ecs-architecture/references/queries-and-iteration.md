# Queries & Data Iteration — Choosing Between the Three Forms

Sources: [Iterate with SystemAPI.Query](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/systems-systemapi-query.html), [Iterate with IJobEntity](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/iterating-data-ijobentity.html), [Implement IJobChunk](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/iterating-data-ijobchunk-implement.html).
Covers: SKILL.md §4 — **"Pick the iteration form by what the loop needs per chunk"**.

All three sit on the same `EntityQuery`; they differ in where the loop runs and
how much per-chunk control it gets. Once one of the job forms is chosen, its
scheduling and disposal are `unity-job-system-and-burst`'s.

## The three forms

| Form | What it decides | Source |
|---|---|---|
| `SystemAPI.Query<T>` | Main-thread `foreach`, source-generated, caches its `EntityQuery` — the simplest correct answer when the work is not worth a job | [SystemAPI.Query](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/systems-systemapi-query.html) |
| `IJobEntity` | Per-entity `Execute()`, schedulable and Burst-compilable, query inferred from the parameter list — the default when work should run on worker threads | [IJobEntity](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/iterating-data-ijobentity.html) |
| `IJobChunk` | Raw per-chunk `NativeArray` access; lets an optional component be tested once per chunk instead of once per entity, at the cost of explicit setup | [IJobChunk](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/iterating-data-ijobchunk-implement.html) |

## What decides it

| Situation | Form | Source |
|---|---|---|
| A few dozen entities, or logic that must call managed APIs | `SystemAPI.Query<T>` | [SystemAPI.Query](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/systems-systemapi-query.html) |
| Thousands of entities, uniform per-entity work | `IJobEntity` | [IJobEntity](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/iterating-data-ijobentity.html) |
| The loop branches on an optional component, or needs the chunk's arrays directly | `IJobChunk` | [IJobChunk](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/iterating-data-ijobchunk-implement.html) |
| The loop needs entity-to-entity lookups | Either job form plus a `ComponentLookup<T>`, marked `[ReadOnly]` where possible | [EntityQuery](https://docs.unity3d.com/Packages/com.unity.entities@6.6/api/Unity.Entities.EntityQuery.html) |

**Critical caveat**: `IJobEntity` infers its query from `Execute()`'s
parameters, so adding a parameter silently narrows which entities the job
touches. A job that suddenly processes fewer entities than expected is usually
a signature change, not a data change.

## API index

| Type | Source |
|---|---|
| `SystemAPI.Query` | [SystemAPI.Query](https://docs.unity3d.com/Packages/com.unity.entities@6.6/api/Unity.Entities.SystemAPI.Query.html) |
| `EntityQuery` | [EntityQuery](https://docs.unity3d.com/Packages/com.unity.entities@6.6/api/Unity.Entities.EntityQuery.html) |
| `IJobEntity` | [IJobEntity](https://docs.unity3d.com/Packages/com.unity.entities@6.6/api/Unity.Entities.IJobEntity.html) |
