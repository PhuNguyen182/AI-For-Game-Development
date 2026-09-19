# Jobs Overview & Job Types — Which Interface Fits

Sources: [Job system overview](https://docs.unity3d.com/Manual/job-system-overview.html), [Jobs overview](https://docs.unity3d.com/Manual/job-system-jobs.html).
Covers: SKILL.md §4 — **"Pick the job type from how the work divides, not from how much of it there is"**.

The four job interfaces and the constraints every one of them shares. Which
container the job reads is `unity-collections`; whether the work should be
parallelized at all is `tech-lead-performance`.

## Shared constraints

| Subject | What it decides | Source |
|---|---|---|
| Blittable data only | A job struct may hold only unmanaged, blittable fields and native containers — no class, string, or array reference, which rules out most existing gameplay types without a data rewrite | [Job system overview](https://docs.unity3d.com/Manual/job-system-overview.html) |
| Main-thread scheduling | `Schedule` must be called from the main thread; a job cannot schedule another job from inside itself | [Jobs overview](https://docs.unity3d.com/Manual/job-system-jobs.html) |
| Work stealing | Idle workers steal queued batches, so throughput depends on batches being small enough to redistribute | [Job system overview](https://docs.unity3d.com/Manual/job-system-overview.html) |
| Safety system | Tracks races and leaks **in the Editor**; the checks are compiled out of Player builds, so an unsafe job fails silently there | [Job system overview](https://docs.unity3d.com/Manual/job-system-overview.html) |

## The interfaces

| Interface | What it decides | Source |
|---|---|---|
| `IJob` | One self-contained unit of background work — use when the work is a single task, not a per-element sweep | [IJob](https://docs.unity3d.com/ScriptReference/Unity.Jobs.IJob.html) |
| `IJobFor` | Current recommendation for per-element work; `Run` (main thread), `Schedule` (single worker, ordered), `ScheduleParallel` (many workers) from one implementation | [IJobFor](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/Unity.Jobs.IJobFor.html) |
| `IJobParallelFor` | The older per-element parallel API, retained for compatibility — prefer `IJobFor` in new code | [IJobParallelFor](https://docs.unity3d.com/ScriptReference/Unity.Jobs.IJobParallelFor.html) |
| `IJobParallelForTransform` | The one path to bulk `Transform` access from a job, via `TransformAccessArray` — ordinary `Transform` APIs are main-thread only | [Jobs overview](https://docs.unity3d.com/Manual/job-system-jobs.html) |

**Critical caveat**: `IJobFor.Schedule` and `IJobFor.ScheduleParallel` are not
interchangeable. `Schedule` runs indices in order on one worker; only
`ScheduleParallel` distributes them, and only it requires every index to be
independent. Switching from one to the other changes the correctness
requirement, not just the speed.
