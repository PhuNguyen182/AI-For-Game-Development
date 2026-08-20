# Job Dependencies & Parallel Jobs

Covers SKILL.md steps 2, 5 (chaining `JobHandle` dependencies explicitly, ParallelFor batching).

## Manual
- [Job dependencies](https://docs.unity3d.com/6000.5/Documentation/Manual/job-system-job-dependencies.html) — passing a producing job's `JobHandle` into a consuming job's `Schedule()`; combining multiple dependencies.
- [Parallel jobs](https://docs.unity3d.com/6000.1/Documentation/Manual/job-system-parallel-for-jobs.html) — splitting a `NativeArray`-sized workload across worker threads, batch sizing, work stealing, `ParallelForTransform`.

## Scripting API
- [`JobHandle.CombineDependencies`](https://docs.unity3d.com/ScriptReference/Unity.Jobs.JobHandle.CombineDependencies.html) — merges multiple prior `JobHandle`s into a single dependency, since schedule methods take only one.
