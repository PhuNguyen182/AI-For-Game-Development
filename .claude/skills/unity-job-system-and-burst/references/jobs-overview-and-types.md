# Jobs Overview and Job Types

Sources: [o] `Manual/job-system-overview.html`, [j] `Manual/job-system-jobs.html`, [f] `6000.0/Documentation/ScriptReference/Unity.Jobs.IJobFor.html`, all under `https://docs.unity3d.com/`.

## Constraints every job shares

| Subject | Fact that decides |
|---|---|
| Blittable data only | Only unmanaged blittable fields and native containers: no class, string or array reference, which rules out most gameplay types without a data rewrite [o] |
| Main-thread scheduling | `Schedule` is called from the main thread; a job cannot schedule a job from inside itself [j] |
| Work stealing | Idle workers take queued batches, so throughput needs batches small enough to redistribute [o] |
| Safety system | Race and leak checks are Editor-only, compiled out of Player builds [o] |

## Interfaces

| Interface | Fact that decides |
|---|---|
| `IJob` | One self-contained background task, not a per-element sweep |
| `IJobFor` | Current recommendation for per-element work; `Run` (main thread), `Schedule` (single worker, in order), `ScheduleParallel` (many workers) from one implementation [f] |
| `IJobParallelFor` | Older per-element parallel API kept for compatibility; prefer `IJobFor` in new code |
| `IJobParallelForTransform` | Only path to bulk `Transform` access from a job, via `TransformAccessArray`; normal `Transform` APIs are main-thread only [j] |

**Caveat:** `IJobFor.Schedule` and `ScheduleParallel` are not interchangeable. `Schedule` runs indices in order on one worker; only `ScheduleParallel` distributes them and requires every index to be independent. Switching changes the correctness requirement, not only the speed.
