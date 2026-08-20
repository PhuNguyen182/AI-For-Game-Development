# Jobs Overview & Job Types

Covers SKILL.md steps 1–2 (what the Job System is, picking `IJob`/`IJobFor`/`IJobParallelFor`/`IJobParallelForTransform`).

## Manual
- [Job system overview](https://docs.unity3d.com/Manual/job-system-overview.html) — worker threads, work stealing, blittable-data requirement, safety system, why Burst is recommended alongside it.
- [Jobs overview](https://docs.unity3d.com/Manual/job-system-jobs.html) — `IJob`, `IJobParallelFor`, `IJobParallelForTransform`, `IJobFor`; main-thread-only scheduling constraint.

## Scripting API
- [`IJob`](https://docs.unity3d.com/ScriptReference/Unity.Jobs.IJob.html) — single unit of background work.
- [`IJobFor`](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/Unity.Jobs.IJobFor.html) — current recommendation for per-element work; `Run`/`Schedule`/`ScheduleParallel`; batch-size guidance (32–128 for simple work, down to 1 for expensive work).
- [`IJobParallelFor`](https://docs.unity3d.com/ScriptReference/Unity.Jobs.IJobParallelFor.html) — older per-element parallel API, kept mainly for backward compatibility; prefer `IJobFor` for new code.
