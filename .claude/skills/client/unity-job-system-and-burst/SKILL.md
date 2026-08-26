---
name: unity-job-system-and-burst
description: >
  Technique for moving measured, CPU-bound bulk work onto worker threads with
  Unity's C# Job System: `IJob`, `IJobFor`, `IJobParallelFor`,
  `IJobParallelForTransform`, `Schedule`/`ScheduleParallel`, `JobHandle`
  chaining, `CombineDependencies`, batch sizing, `NativeArray` and
  `NativeContainer` safety, `[ReadOnly]`, `Allocator.Temp`/`TempJob`/`Persistent`
  lifetime and disposal, plus applying and verifying `[BurstCompile]`.
  Use when a Profiler capture already shows a parallelizable main-thread
  bottleneck, or when a job races, leaks, or stalls.
  Not for: whether to parallelize at all (`tech-lead-performance`); the capture
  that proves it (`unity-profiler-diagnostics`); HPC# subset, `FloatMode`,
  intrinsics, AOT (`unity-burst-compiler`); container type choice
  (`unity-collections`); entity, system, and query design
  (`unity-ecs-architecture`); which physics job interface fits (`unity-physics`);
  `float3` maths (`unity-mathematics`); GPU-driven effects (`compute-shader-vfx`).
---

# Unity Job System & Burst — Multithreaded CPU-Bound Work

## Bundled resources

### References
Read-only context, loaded on demand so SKILL.md itself stays short.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Job System manual and `Unity.Jobs` API roots, plus the versioning caveat | Starting any task here, or checking whether a page is version-pinned |
| [jobs-overview-and-types.md](references/jobs-overview-and-types.md) | Worker threads, blittable requirement, and the four job interfaces | Choosing which job interface a workload should implement |
| [creating-and-scheduling-jobs.md](references/creating-and-scheduling-jobs.md) | `Schedule`, `Complete`, flushing, reading results back | Deciding where in the frame a job is scheduled and where it is completed |
| [dependencies-and-parallel-jobs.md](references/dependencies-and-parallel-jobs.md) | `JobHandle` chaining, `CombineDependencies`, batch sizing, work stealing | Two jobs touch the same data, or a parallel batch size must be chosen |
| [native-containers-and-safety.md](references/native-containers-and-safety.md) | Allocators, `[ReadOnly]`, disposal, what the safety system does and does not catch | Allocating or disposing job data, or diagnosing a reported race or leak |
| [burst-compiler.md](references/burst-compiler.md) | `[BurstCompile]` placement, eligibility, and how to confirm it took effect | Applying Burst, or a job runs slower than the attribute implies it should |

## 1. Objective
Turn an already-measured, genuinely parallelizable CPU cost into correctly scheduled jobs — right job type, safe container lifetimes, explicit dependencies, Burst applied where it qualifies — so the work actually overlaps instead of merely relocating. It prevents the failures that compile cleanly and pass in the Editor: results written into a copy of the job struct and silently discarded, races the Editor's safety checks catch but a Player build does not, native allocations the GC can never reclaim, nondeterministic parallel accumulation, and a `.Complete()` placed so early the main thread simply waits instead of working.

## 2. Role
Act as the Job System and Burst specialist for the client track — the tool reached for once Tech Lead – Performance has an actual Profiler capture showing a CPU-bound, parallelizable bottleneck and the work has to be scheduled correctly. You author and audit the scheduling; you do not decide that parallelizing is warranted, and you do not take on Burst's deeper compilation tuning.

## 3. When to invoke this skill
- A Profiler capture has already shown a specific system is CPU-bound on the main thread and its work divides into independent per-element units.
- Converting a bulk per-element loop — batched pathfinding, large-scale simulation, procedural generation — into `IJobFor`/`ScheduleParallel` over `NativeArray` data.
- A reported symptom of scheduling gone wrong: a `WaitForJobGroup` marker dominating the main thread, results that come back unchanged, a native leak warning at play-mode exit, or output that differs between runs on identical input.
- Wiring dependencies between jobs that read and write the same containers, including `JobHandle.CombineDependencies` for a job with several producers.
- Applying `[BurstCompile]` to a job struct or its static helpers and confirming compilation actually happened.
- Negative trigger: no measurement yet, or nobody has decided this work is worth parallelizing — that is `tech-lead-performance`'s call, with the capture from `unity-profiler-diagnostics`; reaching here first is exactly what `performance-and-algorithms.md`'s Multithreading section forbids.
- Negative trigger: HPC# subset compliance, `FloatMode`/`FloatPrecision`, SIMD intrinsics, AOT and platform settings, `[NoAlias]`, `FunctionPointer<T>` — that is `unity-burst-compiler`; this skill applies the attribute and verifies it, nothing deeper.
- Negative trigger: choosing between `NativeList`, `NativeHashMap`, `NativeQueue`, `NativeStream`, `FixedString`, or a rewindable allocator — that is `unity-collections`; this skill covers lifetime and safety once the type is chosen.
- Negative trigger: modeling entities, systems, baking, or choosing `SystemAPI.Query`/`IJobEntity`/`IJobChunk` — that is `unity-ecs-architecture`; this skill takes over once an ECS job is being scheduled.
- Negative trigger: which physics job interface a task calls for (`ICollisionEventsJob`, `IContactsJob`, `IJacobiansJob`) — that is `unity-physics`; scheduling whichever one is chosen stays here.
- Negative trigger: `Unity.Mathematics` type or function choice — that is `unity-mathematics`.
- Negative trigger: a GPU-driven visual effect — that is `compute-shader-vfx`, despite both being "many elements in parallel".
- Negative trigger: an ordinary hot-path fix — a per-frame allocation, a missing pool, a wrong collection — needs no threading at all; apply `performance-and-algorithms.md`'s baseline directly.

## 4. How to use this skill
1. **Name the Profiler capture that justified parallelizing this work** — which system, which marker, how many milliseconds of main-thread time; per `performance-and-algorithms.md`'s Multithreading section this is escalation territory, so with no capture, stop and route to `tech-lead-performance`. [root-links.md](references/root-links.md) pins the documentation set these APIs come from.
2. **Pick the job type from how the work divides, not from how much of it there is**, per [jobs-overview-and-types.md](references/jobs-overview-and-types.md) — `IJob` for one self-contained unit, `IJobFor` with `ScheduleParallel` for independent per-element work (Unity's current recommendation over the older `IJobParallelFor`), `IJobParallelForTransform` only for bulk `Transform` access.
3. **Prove every parallel iteration is independent before scheduling one** — worker threads run in an unspecified order, so any iteration that accumulates into shared state produces a run-dependent result. Write per-index outputs and reduce them serially afterwards; per `coding-principles.md`'s Shared Core integrity section, a nondeterministic result cannot back client prediction or server authority.
4. **Pick the allocator by how long the data must live**, per [native-containers-and-safety.md](references/native-containers-and-safety.md) — `Allocator.TempJob` for data handed to a scheduled job, `Allocator.Persistent` for data spanning many frames, `Allocator.Temp` only for main-thread scratch that never enters a job at all.
5. **Treat the job struct as a copy, because it is** — `Schedule` copies the struct to the worker, so any plain field the job writes is lost and any field the main thread changes after scheduling is not seen. Every result must travel through a `NativeContainer`; a job that "runs but changes nothing" is almost always this.
6. **Mark every container a job only reads as `[ReadOnly]`** — that attribute is what lets several jobs read the same container concurrently; without it the safety system serializes them, and the parallelism disappears with no error to explain why.
7. **Schedule as soon as the input is ready and complete only where the result is read**, per [creating-and-scheduling-jobs.md](references/creating-and-scheduling-jobs.md) — scheduled work is not kicked to workers until the batch is flushed, so call `JobHandle.ScheduleBatchedJobs` when a long gap separates scheduling from completion, and never `.Complete()` on the next line.
8. **Size the parallel batch against per-element cost**, per [dependencies-and-parallel-jobs.md](references/dependencies-and-parallel-jobs.md) — roughly 32–128 elements per batch for cheap arithmetic, down towards 1 for genuinely expensive elements; too small and scheduling overhead dominates, too large and one slow batch strands idle workers.
9. **Chain every ordering relationship through an explicit `JobHandle`** — pass the producer's handle into the consumer's `Schedule`, and use `JobHandle.CombineDependencies` for several producers. Two independently scheduled jobs touching the same data are a race, not an ordering convention.
10. **Apply `[BurstCompile]` and verify it took effect**, per [burst-compiler.md](references/burst-compiler.md) — the attribute is needed on the job struct and on any static method it calls plus that method's containing class, and a single managed or reference type anywhere inside silently drops the job back to Mono/IL2CPP. Confirm in the Burst Inspector, never from the attribute's presence.
11. **Dispose every native allocation on every code path**, including early returns and exception paths — an undisposed `NativeContainer` is native memory the GC cannot see, per `performance-and-algorithms.md`'s Memory discipline section. Use `Dispose(JobHandle)` when a scheduled job still holds it.
12. **Re-measure, and report the complexity cost with the win** — confirm main-thread time actually dropped rather than moving into a `WaitForJobGroup` stall, per `performance-and-algorithms.md`'s Verification section, and state the added discipline (allocator lifetimes, safety rules, Burst constraints) plainly rather than presenting it as free.
13. **Stop and ask when independence cannot be established from the code in front of you** — if it is unclear whether two iterations can touch the same element, do not parallelize on the assumption they cannot; say what is ambiguous and what evidence would settle it.

## 5. Specific goals / tasks this skill performs
- Converting a measured, independent per-element loop into `IJobFor`/`ScheduleParallel` over native data, with batch size justified.
- Allocator lifetime, `[ReadOnly]` marking, and disposal audits across every code path.
- Dependency wiring via `JobHandle` and `CombineDependencies`, replacing implicit ordering assumptions.
- Applying `[BurstCompile]` and confirming compilation in the Burst Inspector.
- Diagnosing races, leaks, discarded results, `WaitForJobGroup` stalls, and run-to-run nondeterminism.
- Out of scope: whether the bottleneck warrants threading (`tech-lead-performance`); the Profiler capture that proves it (`unity-profiler-diagnostics`); Burst compilation tuning (`unity-burst-compiler`); container type selection (`unity-collections`); ECS modeling (`unity-ecs-architecture`); physics job interface choice (`unity-physics`); maths types (`unity-mathematics`); GPU-driven effects (`compute-shader-vfx`).

## 6. Output format
```
## Job System Work — <system/bottleneck name>
- Prerequisite capture: <system, marker, main-thread cost that justified this>
- Job type(s): <IJob / IJobFor / IJobParallelForTransform — what decided it>
- Independence: <why every parallel iteration is independent; how any reduction is made deterministic>
- Containers: <type, allocator, [ReadOnly] where it applies>
- Batch size: <value — and the per-element cost it was chosen against>
- Dependency chain: <JobHandle wiring, or "none — independent job">
- Burst: <applied yes/no — verified via Burst Inspector / build log>
- Disposal: <confirmed on every path, including early returns>
- Measurement: <before/after main-thread time from unity-profiler-diagnostics>
- Complexity cost disclosed: <the discipline this adds for whoever maintains it>
- Layer: <Game.Core.* pure logic invoked / Game.Client.* job and scheduling code>
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what the delivered solution does not cover>
- Latent concerns: <failure modes not yet triggered: assumptions that hold only under current conditions, thresholds not yet reached, trade-offs knowingly deferred>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: a Profiler capture attributes 8 ms of main-thread time to per-agent neighbour avoidance in a boid simulation, and Tech Lead – Performance approved parallelizing it.
- Output: converted to `IJobFor` over `NativeArray<AgentData>` (`Allocator.TempJob`), neighbour data marked `[ReadOnly]` so the read-only pass runs concurrently; each agent writes only its own index, so no reduction and no ordering dependence; batch size 64 against the measured per-agent cost; `[BurstCompile]` applied to the struct and confirmed in the Burst Inspector; scheduled at frame start with `ScheduleBatchedJobs` and completed just before the render read; re-measured at 1.2 ms main-thread with the rest overlapped; arrays disposed in `OnDestroy` with the early-return path covered.

**Example 2**
- Input: "The job runs but the array still holds the old values — can you add a `Complete()` earlier and see if that fixes it?"
- Output: declined — completing earlier only hides the timing, and the values were never written where the caller was reading. The job accumulated into an `int` field on the job struct, which `Schedule` copies to the worker, so the result died with the copy. Moved the output into a `NativeArray<int>` indexed per element, per §4's copy-semantics step; `.Complete()` stayed where the result is actually read.

**Example 3**
- Input: a parallel damage-resolution job passes in the Editor and in QA, but a Player build occasionally applies damage twice.
- Output: traced to two iterations writing the same target index, a genuine race that only the Editor's safety checks were catching — those checks are compiled out of Player builds, so "passes in a build" was never evidence. Restructured to per-source output slots with a serial reduce, restoring determinism per §4's independence step, and flagged that any prior build-only validation of job code needs re-running in the Editor.

## 8. Edge cases & guardrails
- Never introduce jobs without a Profiler capture and an owner's decision — per `performance-and-algorithms.md` this is escalation-level complexity, not a routine speed-up.
- Never treat an Editor-clean run as proof of safety — the safety system's race and leak checks do not exist in a Player build, so an unsafe job simply corrupts data there instead of reporting.
- Never write a job's result to anything but a `NativeContainer` — the job struct is a copy and any other field is discarded silently.
- Never accumulate into shared state across parallel iterations — the result depends on thread scheduling, which breaks the determinism prediction and server authority require.
- Never call `.Complete()` immediately after scheduling — that is a synchronous call with extra overhead, and it shows up as a main-thread `WaitForJobGroup` stall.
- Never rely on `JobHandle.IsCompleted` before touching a container from the main thread — only `.Complete()` hands ownership back and clears the safety state.
- Never leave a native allocation undisposed on any path — it is a leak the GC can never reclaim, however small.
- Never assume `[BurstCompile]` took effect — one managed type inside the job drops it back to Mono/IL2CPP with no error; verify in the Burst Inspector.
- If independence between iterations cannot be established, do not parallelize and say why — a race that only appears under load is far costlier than the main-thread time it saved.
