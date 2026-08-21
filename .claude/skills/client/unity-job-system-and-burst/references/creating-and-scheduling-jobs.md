# Creating & Scheduling Jobs — Kick, Flush, Complete

Sources: [Create and run a job](https://docs.unity3d.com/Manual/job-system-creating-jobs.html), [JobHandle](https://docs.unity3d.com/ScriptReference/Unity.Jobs.JobHandle.html).
Covers: SKILL.md §4 — **"Schedule as soon as the input is ready and complete only where the result is read"**.

What actually happens between `Schedule` and `Complete`, including the flush
step that decides whether "schedule early" buys anything at all. Dependency
wiring between jobs is [dependencies-and-parallel-jobs.md](dependencies-and-parallel-jobs.md).

| Member | What it decides | Source |
|---|---|---|
| `Schedule()` | Queues the job and returns its `JobHandle`; the job struct is **copied**, so the worker never sees later changes to the original | [Create and run a job](https://docs.unity3d.com/Manual/job-system-creating-jobs.html) |
| `JobHandle.ScheduleBatchedJobs()` | Flushes queued jobs to worker threads — without it, work may not start until something completes or the frame ends, which quietly erases an early schedule | [JobHandle](https://docs.unity3d.com/ScriptReference/Unity.Jobs.JobHandle.html) |
| `Complete()` | Blocks until the job finishes, returns container ownership to the main thread, and clears safety-system state — the only sanctioned way to read results back | [JobHandle](https://docs.unity3d.com/ScriptReference/Unity.Jobs.JobHandle.html) |
| `IsCompleted` | Reports progress only; it neither returns ownership nor clears safety state, so reading a container after it alone is unsafe | [JobHandle](https://docs.unity3d.com/ScriptReference/Unity.Jobs.JobHandle.html) |
| `CompleteAll(...)` | Completes several handles in one call, for a frame boundary that must drain everything | [JobHandle](https://docs.unity3d.com/ScriptReference/Unity.Jobs.JobHandle.html) |

## Reading results back

| Situation | What it decides | Source |
|---|---|---|
| Job writes to a plain field on its own struct | Lost — the worker mutated a copy; this is the most common "the job did nothing" report | [Create and run a job](https://docs.unity3d.com/Manual/job-system-creating-jobs.html) |
| Job writes to a `NativeArray<T>` field | Survives — the container is a handle to shared native memory, not part of the copied struct | [Create and run a job](https://docs.unity3d.com/Manual/job-system-creating-jobs.html) |
| Single scalar result | Still needs a container — a one-element `NativeArray<T>` or `NativeReference<T>` | [Create and run a job](https://docs.unity3d.com/Manual/job-system-creating-jobs.html) |

**Critical caveat**: `Complete()` on the line after `Schedule()` is a
synchronous call with extra overhead. It is not a safe default; it is the
pattern that makes a job strictly slower than the loop it replaced.
