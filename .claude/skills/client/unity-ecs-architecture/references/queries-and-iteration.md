# Queries & Data Iteration

Covers SKILL.md step 6 (choosing the iteration approach that matches the case).

## Manual
- [Iterate over component data with SystemAPI.Query](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/systems-systemapi-query.html) — `foreach (var x in SystemAPI.Query<T>())` for straightforward main-thread iteration; source-generated, caches the underlying `EntityQuery`.
- [Iterate over component data with IJobEntity](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/iterating-data-ijobentity.html) — per-entity iteration as a schedulable, Burst-compilable job; the query is inferred from the job's `Execute()` parameters.
- [Implement IJobChunk](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/iterating-data-ijobchunk-implement.html) — the most direct, explicit form of chunk-level iteration; more setup than `IJobEntity`, but gives direct `NativeArray` access per chunk and lets you check optional components once per chunk instead of once per entity.

## Scripting API
- [Method `SystemAPI.Query`](https://docs.unity3d.com/Packages/com.unity.entities@6.6/api/Unity.Entities.SystemAPI.Query.html) — overloads for iterating up to seven component types from inside a system.
- [Struct `EntityQuery`](https://docs.unity3d.com/Packages/com.unity.entities@6.6/api/Unity.Entities.EntityQuery.html) — selects/filters entities by component composition; underlies `SystemAPI.Query`, `IJobEntity`, and `IJobChunk`.
