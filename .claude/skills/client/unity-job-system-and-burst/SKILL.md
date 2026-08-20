---
name: unity-job-system-and-burst
description: >
  Technique for authoring genuinely parallelizable, CPU-bound bulk work with
  Unity's C# Job System (`IJob`/`IJobFor`/`IJobParallelFor`, `JobHandle`
  scheduling/dependencies, `NativeArray`/`NativeContainer` safety) and the
  Burst compiler (`[BurstCompile]`). Use this only once a measurement has
  already shown a genuinely CPU-bound, parallelizable bottleneck (large-scale
  simulation, batched pathfinding, bulk per-element math) — per
  `performance-and-algorithms.md`, Job System/Burst/DOTS is an
  architecture-level decision, not a routine optimization default, and is
  Tech Lead – Performance's territory. Do not use this as a first response to
  "make this faster" without that measurement — get it from
  `unity-profiler-diagnostics` first. Do not use this for a GPU-driven visual
  effect — that's `compute-shader-vfx`. Do not use this for ordinary hot-path
  allocation/pooling/data-structure fixes that don't need multithreading at
  all — that's the baseline covered in `performance-and-algorithms.md`
  directly.
---

# Unity Job System & Burst — Multithreaded CPU-Bound Work

Sources: see [references/](references/) for the Unity Manual/Scripting API root links, split by topic — [root-links.md](references/root-links.md), [jobs-overview-and-types.md](references/jobs-overview-and-types.md), [creating-and-scheduling-jobs.md](references/creating-and-scheduling-jobs.md), [dependencies-and-parallel-jobs.md](references/dependencies-and-parallel-jobs.md), [native-containers-and-safety.md](references/native-containers-and-safety.md), [burst-compiler.md](references/burst-compiler.md).

## 1. Objective
Move genuinely parallelizable, CPU-bound bulk work off the main thread correctly — safe `NativeContainer` usage, correct job dependencies, Burst-compiled inner loops — without introducing a race condition, a leaked native allocation, or a main-thread stall that erases the parallelism gain.

## 2. Role
Act as the Job System/Burst specialist inside Tech Lead – Performance's escalation territory: you take an already-measured, already-justified CPU-bound bottleneck and turn it into correctly-scheduled jobs over `NativeContainer` data, Burst-compiled where the workload qualifies — you don't make the "should we parallelize this" call yourself if it hasn't already been made per `performance-and-algorithms.md`.

## 3. When to invoke this skill
- A Profiler measurement (per `unity-profiler-diagnostics`) has already shown a specific system is CPU-bound on the main thread and the work is genuinely parallelizable (large-scale simulation, batched pathfinding, per-element math over a large data set).
- Tech Lead – Performance (or whoever owns that escalation) has already decided Job System/Burst is the right tool for this specific bottleneck — this skill authors the solution, it doesn't make that architecture call.
- Converting a bulk per-element loop (physics-adjacent simulation, large-scale batch transforms, procedural bulk generation) into `IJobFor`/`IJobParallelFor` over `NativeArray` data, with correct dependency chaining via `JobHandle`.
- Applying `[BurstCompile]` to a job (or a static method) whose inner loop is numeric/blittable enough to qualify, and diagnosing why a job isn't Burst-compiling if it silently falls back to Mono/IL2CPP.
- Negative trigger: no prior measurement, or the workload isn't clearly CPU-bound and parallelizable — don't reach for this as a first-pass "make it faster" default; that's exactly the case `performance-and-algorithms.md` warns against.
- Negative trigger: the deliverable is a GPU-driven visual effect (particle simulation, mesh deformation) — that's `compute-shader-vfx`, not this skill, even though both involve "many elements processed in parallel."
- Negative trigger: an ordinary hot-path fix — removing a per-frame allocation, pooling, picking the right collection — doesn't need the Job System at all; apply `performance-and-algorithms.md`'s baseline guidance directly instead of reaching for multithreading.

## 4. How to use this skill
1. **Confirm the prerequisite before writing a single job.** State the measurement that justified this (which Profiler capture, which system, what frame-time/CPU-time cost) — per `performance-and-algorithms.md`, Job System/Burst is not a default, it's a response to a demonstrated, genuinely parallelizable CPU-bound bottleneck.
2. **Pick the right job type.** `IJob` for a single self-contained unit of background work; `IJobFor`/`ScheduleParallel` for per-element work across a `NativeArray`-backed data set (`IJobFor` is Unity's current recommendation over the older `IJobParallelFor`, which exists mainly for backward compatibility); `IJobParallelForTransform` only for the specific case of bulk `Transform` access. Each iteration scheduled in parallel must be fully independent of every other iteration — the safety system enforces this, but design for it explicitly rather than fighting the compiler afterward.
3. **Move data into `NativeContainer` types deliberately**, and pick the allocator by actual lifetime: `Allocator.Temp` for same-frame, single-job-chain data (cheapest, must not survive past the frame); `Allocator.TempJob` for data that needs to survive up to ~4 frames across a scheduled job; `Allocator.Persistent` only for data that genuinely needs to outlive several frames. Mark a container `[ReadOnly]` whenever a job only reads it — this is what allows multiple jobs to access it concurrently instead of serializing on it.
4. **Schedule early, complete late.** Call `Schedule`/`ScheduleParallel` as soon as the job's input data is ready, and don't call `.Complete()` until the results are actually needed later in the frame — completing immediately after scheduling defeats the entire point of parallelism and just adds job-system overhead to a synchronous call.
5. **Chain dependencies explicitly via `JobHandle`**, never by scheduling one job inside another or by guessing at ordering. Pass a producing job's `JobHandle` into the consuming job's `Schedule` call; use `JobHandle.CombineDependencies` when a job depends on more than one prior job. An implicit ordering assumption between two independently-scheduled jobs touching the same data is a race condition waiting to happen, not a minor style issue.
6. **Apply `[BurstCompile]` to the job struct** (and to any static method it calls, which also needs the attribute) once the inner loop is Burst-eligible — no managed types/reference types, blittable data only. Don't assume Burst compiled silently; verify via the Burst Inspector or a build log rather than assuming the attribute alone guarantees it took effect.
7. **Always call `.Complete()`, never rely on `IsCompleted` alone, before touching the container from the main thread.** `.Complete()` is what actually hands the `NativeContainer` back to the main thread and cleans up the safety system's tracking state — skipping it while only polling `IsCompleted` leaks safety-system state and risks a race.
8. **Dispose every `NativeContainer` you allocate**, on every code path including an early return — an undisposed `NativeContainer` is a native memory leak the managed GC can never see or reclaim, the Job System's specific case of the project's Memory discipline rule.
9. **Verify with the Profiler, not by inspection.** Confirm the change actually reduced main-thread time and didn't just relocate the cost — a `WaitForJobGroup` marker showing up on the main thread in `unity-profiler-diagnostics`'s CPU Usage Timeline means something is calling `.Complete()` too early and stalling on a worker thread instead of genuinely overlapping work.
10. **Report the trade-off honestly.** Job System/Burst adds real complexity (safety-system discipline, allocator lifetime rules, Burst eligibility constraints) — state that cost plainly in the handoff rather than presenting it as a free win, per the Verification section of `performance-and-algorithms.md`.

## 5. Specific goals / tasks this skill performs
- Converting an already-measured, CPU-bound bulk-per-element loop into `IJobFor`/`IJobParallelFor` over `NativeArray` data with correct `[ReadOnly]` usage and allocator choice.
- Chaining job dependencies correctly via `JobHandle`/`JobHandle.CombineDependencies` instead of implicit ordering assumptions.
- Applying and verifying `[BurstCompile]` on Burst-eligible job structs and their static helper methods.
- Auditing `NativeContainer` lifetime for leaks (missing `.Dispose()`) and races (missing dependency chaining, incorrect `[ReadOnly]` usage).
- Out of scope: deciding *whether* a bottleneck warrants Job System/Burst in the first place (`performance-and-algorithms.md`/Tech Lead – Performance's call); the initial Profiler measurement that justifies this work (`unity-profiler-diagnostics`); GPU-driven visual effects (`compute-shader-vfx`); ordinary non-multithreaded hot-path fixes (`performance-and-algorithms.md` baseline).

## 6. Output format
```
## Job System Work — <system/bottleneck name>
- Prerequisite measurement: <Profiler finding that justified this — source: unity-profiler-diagnostics session>
- Job type(s): IJob / IJobFor / IJobParallelFor / IJobParallelForTransform — rationale
- NativeContainer(s): <type, allocator (Temp/TempJob/Persistent), ReadOnly where applicable>
- Dependency chain: <JobHandle wiring, or "none — independent job">
- Burst: applied — yes/no; verified via: <Burst Inspector / build log>
- Disposal: confirmed on every code path — yes/no
- Before/after measurement: <main-thread time delta, from unity-profiler-diagnostics>
- Complexity cost disclosed: <yes — summary>
- Known limitations: <...>
```

## 7. Examples
**Example 1**
- Input: Tech Lead – Performance confirmed (via a `unity-profiler-diagnostics` capture showing 8ms of main-thread CPU Usage time) that the large-scale boid simulation's per-agent neighbor-avoidance math is the frame's dominant cost and is fully data-parallel.
- Output: converted the per-agent update to `IJobFor` over `NativeArray<AgentData>` (`Allocator.TempJob`, neighbor data marked `[ReadOnly]`), `[BurstCompile]` applied and confirmed via the Burst Inspector, scheduled at the start of the frame and completed just before the render-relevant read later that frame; re-measured in `unity-profiler-diagnostics` showing main-thread time dropped from 8ms to 1.2ms with the rest genuinely overlapped on worker threads; `NativeArray` disposed in `OnDestroy` with an early-return guard covered.

**Example 2**
- Input: "Can you just wrap the enemy pathfinding batch in a job to make it faster?" — no prior profiling.
- Output: declined to jump straight to Job System; ran a `unity-profiler-diagnostics` CPU Usage capture first, which showed the pathfinding batch wasn't actually the frame's bottleneck (a different, allocation-heavy system was) — reported that finding back per `performance-and-algorithms.md` instead of introducing Job System complexity for a system that didn't need it.

## 8. Edge cases & guardrails
- Never introduce Job System/Burst without a prior Profiler measurement showing a genuinely CPU-bound, parallelizable bottleneck — this is architecture-level complexity per `performance-and-algorithms.md`, not a routine default.
- Never call `.Complete()` immediately after `Schedule`/`ScheduleParallel` — that serializes the work and defeats the purpose; schedule early, complete only when the result is actually needed.
- Never rely on `JobHandle.IsCompleted` alone before touching a `NativeContainer` from the main thread — always call `.Complete()`.
- Never leave a `NativeContainer` undisposed on any code path, including early returns — it's a native memory leak, not a GC-managed one.
- Never assume two independently-scheduled jobs touching the same data are safely ordered without an explicit `JobHandle` dependency — that's a race condition, not a style choice.
- Don't assume `[BurstCompile]` took effect just because the attribute is present — verify via the Burst Inspector or build log; managed/reference types anywhere in the job silently prevent Burst compilation.
- A `WaitForJobGroup` marker on the main thread in the Profiler is a signal something is completing too early — investigate the dependency chain, don't just accept the stall.
- Always disclose the added complexity cost (safety-system discipline, allocator lifetime rules) in the handoff — don't present Job System/Burst as a free performance win.
