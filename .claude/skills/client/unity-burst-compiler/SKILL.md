---
name: unity-burst-compiler
description: >
  Technique for the Burst compiler itself — the High Performance C# (HPC#)
  language subset, `[BurstCompile]` attribute configuration (`FloatMode`,
  `FloatPrecision`, per-job/per-assembly options), verifying compiled output
  via the Burst Inspector, `Unity.Burst.Intrinsics` SIMD intrinsics, AOT
  build/platform settings, `FunctionPointer<T>`/`SharedStatic<T>`, and memory
  aliasing/`[NoAlias]`. Use this only on top of an already-justified Job
  System/Burst decision — per `performance-and-algorithms.md`, Burst/Job
  System/DOTS is architecture-level, escalation territory for Tech Lead –
  Performance, not a routine default. Do not use this to schedule jobs, chain
  `JobHandle` dependencies, or manage `NativeContainer` allocator lifetime —
  that's `unity-job-system-and-burst`. Do not use this for a GPU-driven
  visual effect — that's `compute-shader-vfx`.
---

# Unity Burst Compiler — HPC# Compilation, Verification & Tuning

Sources: see [references/](references/) for the Unity Manual/Scripting API root links, split by topic — [root-links.md](references/root-links.md), [getting-started-and-compilation-model.md](references/getting-started-and-compilation-model.md), [csharp-language-support.md](references/csharp-language-support.md), [intrinsics-and-simd.md](references/intrinsics-and-simd.md), [debugging-and-inspector.md](references/debugging-and-inspector.md), [aot-builds-and-platforms.md](references/aot-builds-and-platforms.md), [function-pointers-and-shared-static.md](references/function-pointers-and-shared-static.md), [aliasing-and-attributes.md](references/aliasing-and-attributes.md).

## 1. Objective
Get code Burst-compiling correctly and verifiably — within the HPC# language subset, with the right `[BurstCompile]` configuration for the accuracy/speed trade-off the workload actually needs — and confirm via the Burst Inspector that it took effect, rather than assuming the attribute alone guarantees it.

## 2. Role
Act as the Burst compilation specialist inside Tech Lead – Performance's escalation territory: given a job or static method that has already been decided (per `performance-and-algorithms.md` and `unity-job-system-and-burst`) to need Burst, you make it actually compile, verify it compiled, and tune its compilation options — you don't decide whether Burst is warranted in the first place, and you don't schedule the job or manage its `NativeContainer` lifetime.

## 3. When to invoke this skill
- Code that's supposed to be Burst-compiled hits an HPC# language-subset error (a managed/reference type snuck in, a non-blittable field, an unsupported C# construct) and needs to be brought inside the supported subset.
- Configuring `[BurstCompile]` parameters — `FloatMode`, `FloatPrecision`, `CompileSynchronously`, `DisableSafetyChecks` — at the job/method level or the assembly level via `[assembly: BurstCompile(...)]`.
- Verifying whether a target actually compiled with Burst (versus silently falling back to Mono/IL2CPP) and reading its generated assembly in the Burst Inspector.
- Reaching for `Unity.Burst.Intrinsics` (X86 SSE/AVX2, Arm Neon) for hand-tuned SIMD after standard Burst auto-vectorization has already been measured insufficient.
- Configuring Burst AOT Settings (CPU architecture targets, Player build behavior) for a specific target platform.
- Bridging managed C# and Burst code with `FunctionPointer<T>` or sharing mutable static state with `SharedStatic<T>`.
- Applying `[NoAlias]` or reasoning about memory aliasing to help Burst vectorize a loop that isn't auto-vectorizing.
- Negative trigger: scheduling a job, chaining `JobHandle` dependencies, or choosing a `NativeContainer` allocator — that's `unity-job-system-and-burst`, not this skill.
- Negative trigger: no prior measurement or architecture decision justifying Burst/Job System at all — per `performance-and-algorithms.md` this is escalation territory; get the measurement from `unity-profiler-diagnostics` and the go-ahead from Tech Lead – Performance first.
- Negative trigger: the deliverable is a GPU-driven visual effect (particle simulation, mesh deformation) — that's `compute-shader-vfx`, not this skill.

## 4. How to use this skill
1. **Confirm the prerequisite.** State which already-justified Job System/Burst decision this tuning work sits on top of (same gate as `unity-job-system-and-burst` step 1) — this skill doesn't re-litigate whether Burst is warranted, it makes an already-approved target compile correctly.
2. **Check the HPC# subset before writing.** No managed/reference types, no boxing, blittable data only, static fields must be read-only and initialized before first Burst-side access, strings limited to `Debug.Log`/`FixedString` assignment — consult `csharp-language-support.md` rather than guessing at what compiles.
3. **Apply `[BurstCompile]` at the right level** — per-job/per-method, or `[assembly: BurstCompile(...)]` for a project-wide default — and know Editor menu settings override assembly settings, which override the attribute's own defaults.
4. **Choose `FloatMode` deliberately.** Default to `FloatMode.Strict`/`Deterministic` unless a specific, measured accuracy tolerance justifies `FloatMode.Fast`'s instruction reordering and reduced-precision SIMD — don't reach for `Fast` by habit.
5. **Verify compilation actually happened**, every time, via the Burst Inspector (`Jobs > Burst > Open Inspector`) or a build log — never assume the `[BurstCompile]` attribute alone guarantees the target compiled; a managed type anywhere in the call graph silently prevents it.
6. **Reach for `Unity.Burst.Intrinsics` only after measuring** that Burst's own auto-vectorization isn't enough — hand-written SIMD intrinsics are harder to read and platform-specific (X86 vs. Arm Neon), so they're a deliberate escalation, not a default.
7. **Configure AOT/Burst settings per target platform explicitly** (Project Settings > Burst AOT Settings, CPU architecture) rather than leaving Player-build compilation behavior implicit — AOT settings only affect Player builds, not Play Mode.
8. **Use `FunctionPointer<T>`/`SharedStatic<T>` only when genuinely bridging the managed/Burst boundary is required** — cache `FunctionPointer<T>.Invoke` in a static field for the best call performance, and always initialize a `SharedStatic<T>` from a static constructor before any Burst-side access.
9. **Use `[NoAlias]` sparingly and only with a genuine no-aliasing guarantee.** Most cases don't need it — Burst already infers no-alias information for `[NativeContainer]`-attributed structs and job struct fields; misapplying `[NoAlias]` on data that can actually alias is undefined behavior, not a performance-neutral mistake.
10. **Re-measure after any Burst-specific change**, via `unity-profiler-diagnostics` or the Burst Inspector's generated assembly — a `FloatMode`/intrinsics/aliasing change is only worth keeping if it's backed by an actual measurement, per the Verification section of `performance-and-algorithms.md`.

## 5. Specific goals / tasks this skill performs
- Diagnosing and fixing HPC# language-subset compile errors (managed types, non-blittable fields, unsupported constructs).
- Configuring `[BurstCompile]` parameters at the job/method or assembly level (`FloatMode`, `FloatPrecision`, `CompileSynchronously`).
- Verifying Burst compilation actually occurred via the Burst Inspector or build log, and diagnosing a silent Mono/IL2CPP fallback.
- Applying `Unity.Burst.Intrinsics` SIMD intrinsics after a measured shortfall in Burst's own auto-vectorization.
- Configuring Burst AOT Settings / CPU architecture targets for Player builds.
- Bridging managed/Burst code with `FunctionPointer<T>` and `SharedStatic<T>`.
- Applying `[NoAlias]` and reasoning about memory aliasing to help vectorization, backed by a genuine no-aliasing guarantee.
- Out of scope: deciding *whether* a workload warrants Burst/Job System at all (`performance-and-algorithms.md`/Tech Lead – Performance's call); the initial Profiler measurement that justifies this work (`unity-profiler-diagnostics`); scheduling jobs, `JobHandle` dependency chains, `NativeContainer` allocator lifetime (`unity-job-system-and-burst`); GPU-driven visual effects (`compute-shader-vfx`).

## 6. Output format
```
## Burst Compilation Work — <job/method or system name>
- Prerequisite decision: <which already-approved Job System/Burst work this sits on top of>
- HPC# subset issue(s) found/fixed: <managed type, non-blittable field, unsupported construct — or "none">
- [BurstCompile] configuration: <FloatMode, FloatPrecision, level applied (method/assembly)>
- Compilation verified via: <Burst Inspector / build log> — result: <compiled / fell back, why>
- Intrinsics used: <yes/no — which, and the measurement that justified them>
- AOT/platform settings touched: <yes/no — which>
- FunctionPointer<T>/SharedStatic<T> used: <yes/no — why>
- [NoAlias] applied: <yes/no — the no-aliasing guarantee backing it>
- Before/after measurement: <from unity-profiler-diagnostics or Burst Inspector assembly diff>
- Known limitations: <...>
```

## 7. Examples
**Example 1**
- Input: an `IJobFor` already approved for Burst compilation (per `unity-job-system-and-burst`) was silently falling back to managed execution; the Burst Inspector showed it missing from the Compile Targets list.
- Output: traced it to a `Debug.Log` call passing an interpolated managed string and a cached `List<T>` field referenced inside the job — replaced the log with a `FixedString128Bytes`-based call gated for Editor-only use, moved the list-based lookup to precomputed `NativeArray` data outside the job; reconfirmed via the Burst Inspector that the job now appears in Compile Targets and its generated assembly is present; re-measured in `unity-profiler-diagnostics` to confirm the CPU-time drop the original approval was based on.

**Example 2**
- Input: "Can you add Arm Neon intrinsics to this Burst job to squeeze out more speed?" — no measurement showing the existing `[BurstCompile]` job (already auto-vectorized) was still short of the target.
- Output: declined to add hand-written intrinsics without justification — reran the job through the Burst Inspector's generated assembly and a `unity-profiler-diagnostics` capture first, which showed the existing auto-vectorized code was already within the frame budget; reported that finding back instead of introducing platform-specific, harder-to-maintain intrinsic code for a gain that wasn't needed.

## 8. Edge cases & guardrails
- Never assume `[BurstCompile]` took effect just because the attribute is present anywhere in the call chain — a single managed/reference type reachable from the entry point silently prevents compilation; verify via the Burst Inspector or build log every time.
- Don't reach for `FloatMode.Fast` by default — it reorders floating-point operations and can use lower-precision SIMD paths; only use it with a measured, accepted accuracy tolerance.
- Don't reach for `Unity.Burst.Intrinsics` before measuring that Burst's own auto-vectorization is insufficient — hand-written intrinsics are platform-specific (X86 vs. Arm Neon) and harder to maintain.
- Never apply `[NoAlias]` without a genuine no-aliasing guarantee — misuse produces undefined behavior that's hard to trace back to its cause, not a neutral no-op.
- Remember AOT/Burst build settings only govern Player builds — Play Mode in the Editor uses JIT compilation, so a Player-only AOT misconfiguration won't surface until an actual build.
- Always initialize a `SharedStatic<T>` from a static constructor before any Burst-side code accesses it — accessing it uninitialized leads to an undefined initialization state, not a clean default value.
- Cache `FunctionPointer<T>.Invoke` in a static field rather than re-resolving it on every call — re-resolving adds avoidable overhead on the managed-to-Burst call boundary.
- Don't confuse this skill's HPC#/compilation-model concerns with `unity-job-system-and-burst`'s scheduling/dependency/`NativeContainer`-lifetime concerns — a job can be correctly scheduled and still silently fail to Burst-compile, and vice versa; check both independently.
