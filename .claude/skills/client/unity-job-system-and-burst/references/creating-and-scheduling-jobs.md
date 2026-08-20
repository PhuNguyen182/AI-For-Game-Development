# Creating & Scheduling Jobs

Covers SKILL.md steps 4, 7 (schedule early/complete late, always `.Complete()` before touching data on the main thread).

## Manual
- [Create and run a job](https://docs.unity3d.com/Manual/job-system-creating-jobs.html) — implement `IJob`, `Schedule()`, `Complete()`; scheduling-early/completing-late guidance; using `NativeArray` to read results back on the main thread.

## Scripting API
- [`JobHandle`](https://docs.unity3d.com/ScriptReference/Unity.Jobs.JobHandle.html) — `IsCompleted`, `Complete()`, `CombineDependencies`, `CompleteAll`, `ScheduleBatchedJobs`.
