---
name: unity-job-system-and-burst
description: "Worker-thread jobs: IJob/IJobFor, ScheduleParallel, JobHandle, [BurstCompile] jobs. Use after profiling shows CPU bound."
user-invocable: false
---

# Unity Job System and Burst

- **Not for:** whether to parallelize (`technical-architect`).
- **Not for:** the capture proving it (`unity-profiler-diagnostics`).
- **Not for:** HPC# subset, `FloatMode`, intrinsics, AOT (`unity-burst-compiler`).
- **Not for:** container type choice (`unity-collections`).
- **Not for:** entities, systems, queries (`unity-ecs-architecture`).
- **Not for:** physics job interface choice (`unity-physics`).
- **Not for:** `float3` maths (`unity-mathematics`).
- **Not for:** GPU-driven effects (`compute-shader-vfx`).
- **Not for:** `Task`/`async`/`lock`/producer-consumer work that is not blittable per-element data (`dotnet-concurrency-and-async`).
- **Docs:** https://docs.unity3d.com/6000.5/Documentation/Manual/job-system.html (Unity 6).
  - **Page forms:** job-system manual pages exist unversioned (`/Manual/…`, current docs) and pinned (`/6000.5/Documentation/Manual/…`).
  - **Wording that matters for an Editor version:** use the pinned form.

## References
- **[jobs-overview-and-types.md](references/jobs-overview-and-types.md):** Choosing a job interface, or a field type is rejected by a job.
- **[creating-and-scheduling-jobs.md](references/creating-and-scheduling-jobs.md):** Placing `Schedule` and `Complete` in the frame, or a job "runs but changes nothing".
- **[dependencies-and-parallel-jobs.md](references/dependencies-and-parallel-jobs.md):** Two jobs touch the same data, or a batch size must be chosen.
- **[native-containers-and-safety.md](references/native-containers-and-safety.md):** Choosing an allocator, disposing job data, or diagnosing a reported race or leak.

## Steps
1. **Name the Profiler capture that justified this:** system, marker, main-thread milliseconds.
   - **No capture or no owner decision:** stop and route to `technical-architect` (`csharp-standards` → `performance-and-algorithms.md` "Multithreading").
   - **Ordinary hot-path fix:** per-frame allocation, missing pool or wrong collection needs no threading.
2. **Pick the job type from how the work divides:** per [jobs-overview-and-types.md](references/jobs-overview-and-types.md):
   - **`IJob`:** one unit.
   - **`IJobFor` + `ScheduleParallel`:** independent per-element work (preferred over `IJobParallelFor`).
   - **`IJobParallelForTransform`:** only for bulk `Transform` access.
3. **Prove every parallel iteration independent:** worker order is unspecified, so accumulating into shared state is run-dependent.
   - **Outputs:** write per-index outputs and reduce serially.
   - **Nondeterminism:** cannot back prediction or server authority (`csharp-standards` → `coding-principles.md` "Shared Core integrity").
   - **Independence cannot be established from the code:** do not parallelize; say what is ambiguous and what evidence would settle it.
4. **Pick the allocator by lifetime:** per [native-containers-and-safety.md](references/native-containers-and-safety.md):
   - **`TempJob`:** data handed to a job.
   - **`Persistent`:** across frames.
   - **`Temp`:** main-thread scratch only.
5. **Treat the job struct as a copy:** a plain field the job writes is lost, and a field the main thread changes after scheduling is not seen.
   - **Results:** every result travels through a `NativeContainer`.
6. **Mark read-only containers `[ReadOnly]`:** without it the safety system serializes jobs sharing the container, with no error.
7. **Schedule when the input is ready, complete where the result is read:** per [creating-and-scheduling-jobs.md](references/creating-and-scheduling-jobs.md).
   - **Long gap after scheduling:** use `JobHandle.ScheduleBatchedJobs`.
8. **Size the batch against per-element cost:** per [dependencies-and-parallel-jobs.md](references/dependencies-and-parallel-jobs.md).
9. **Chain every ordering relationship through a `JobHandle`:** `CombineDependencies` for several producers; two unchained jobs on the same data are a race.
10. **Apply `[BurstCompile]` and verify it in the Burst Inspector:** see `unity-burst-compiler`.
    - **Job struct:** the attribute is needed on the job struct only; Burst compiles everything the job calls.
    - **Static method and its class:** need it only when managed code calls them directly as a Burst entry point.
    - **One managed or reference type inside:** drops the job to Mono/IL2CPP with no error.
11. **Dispose every native allocation on every path:** early returns and exceptions included (`csharp-standards` → `performance-and-algorithms.md` "Memory discipline").
    - **Allocation a scheduled job still holds:** use `Dispose(JobHandle)`.
12. **Re-measure:** main-thread time must drop rather than move into a `WaitForJobGroup` stall (`csharp-standards` → `performance-and-algorithms.md` "Verification").
    - **Disclosure:** state the added discipline (allocator lifetimes, safety rules, Burst constraints) with the win.

## Never
- **Treat an Editor-clean run as proof of safety in either direction:**
  - **Why:** race and leak checks exist only in the Editor.
  - **Unsafe job:** silently corrupts data in a Player build.
  - **Build-only pass:** proves nothing.
  - **Build-only validation:** re-run it in the Editor.
- **Call `.Complete()` on the line after `Schedule`:** it is a synchronous call with extra overhead, shown as a `WaitForJobGroup` stall.
- **Rely on `JobHandle.IsCompleted` before touching a container on the main thread:** only `.Complete()` returns ownership and clears safety state.

## Output
```
## Job System Work — <system/bottleneck>
- Prerequisite capture: <system, marker, main-thread cost>
- Job type(s): <IJob / IJobFor / IJobParallelForTransform — what decided it>
- Independence: <why iterations are independent; how any reduction stays deterministic>
- Containers: <type, allocator, [ReadOnly] where it applies>
- Batch size: <value — per-element cost it was chosen against>
- Dependency chain: <JobHandle wiring, or "none">
- Burst: <applied yes/no — verified via Burst Inspector / build log>
- Disposal: <confirmed on every path>
- Measurement: <before/after main-thread time>
- Complexity cost disclosed: <discipline this adds for maintainers>
```

## Example
- **"The array still holds the old values, add a `Complete()` earlier":** declined, the job accumulated into an `int` field on the struct, which `Schedule` copies to the worker.
  - **Did instead:** moved the output into a per-element `NativeArray<int>`; `Complete()` stays where the result is read.
