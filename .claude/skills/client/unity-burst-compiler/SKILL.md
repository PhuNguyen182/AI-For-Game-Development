---
name: unity-burst-compiler
description: >
  Technique for the Burst compiler itself: the High Performance C# (HPC#)
  subset and its type restrictions, `[BurstCompile]` placement and options
  (`FloatMode`, `FloatPrecision`, `CompileSynchronously`, `DisableSafetyChecks`,
  `[assembly: BurstCompile]`), reading generated assembly in the Burst
  Inspector, `Unity.Burst.Intrinsics` SSE/AVX2/Neon, Burst AOT Settings and CPU
  architecture targets, `FunctionPointer<T>`, `SharedStatic<T>`, and
  `[NoAlias]` aliasing. Use when code that should be Burst-compiled is not, or
  when compiled output must be tuned or verified.
  Not for: scheduling, `JobHandle` chains, allocator lifetime
  (`unity-job-system-and-burst`); whether Burst is warranted
  (`tech-lead-performance`); the capture proving it (`unity-profiler-diagnostics`);
  entity and system design (`unity-ecs-architecture`); container type choice
  (`unity-collections`); `float3` maths (`unity-mathematics`); GPU-driven effects
  (`compute-shader-vfx`).
---

# Unity Burst Compiler — HPC# Compilation, Verification & Tuning

## Bundled resources

### References
Read-only context, loaded on demand so SKILL.md itself stays short.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Burst manual and API roots plus the version pin | Starting any task here, or confirming which Burst version the project installs |
| [getting-started-and-compilation-model.md](references/getting-started-and-compilation-model.md) | Where `[BurstCompile]` applies, option precedence, Play Mode JIT behaviour | Deciding where the attribute goes, or Editor timings look wrong on the first run |
| [csharp-language-support.md](references/csharp-language-support.md) | The HPC# subset: types, strings, static fields | Code fails to compile under Burst, or new Burst-targeted code is being written |
| [debugging-and-inspector.md](references/debugging-and-inspector.md) | Burst Inspector, the `Jobs > Burst` menu, debugger limits | Confirming a target compiled, or reading its generated assembly |
| [aliasing-and-attributes.md](references/aliasing-and-attributes.md) | `FloatMode`, `FloatPrecision`, `[NoAlias]`, job-field aliasing rules | Choosing float behaviour, or a loop that should vectorize does not |
| [intrinsics-and-simd.md](references/intrinsics-and-simd.md) | `Unity.Burst.Intrinsics`, X86 and Arm Neon families, support probes | Auto-vectorization has been measured insufficient and hand-written SIMD is on the table |
| [aot-builds-and-platforms.md](references/aot-builds-and-platforms.md) | Burst AOT Settings, CPU architecture, AOT versus JIT scope | Configuring a Player build, or something works in Play Mode but not in a build |
| [function-pointers-and-shared-static.md](references/function-pointers-and-shared-static.md) | `FunctionPointer<T>`, `SharedStatic<T>`, initialization order | Managed code must call into Burst code, or mutable static state must be shared |

## 1. Objective
Make an already-approved Burst target actually compile, prove it compiled, and tune its options to the accuracy and platform requirements the workload really has. It prevents the failures Burst produces silently rather than loudly: an entry point that quietly runs managed because one call in its graph is ineligible, a first-run Editor timing taken while async compilation was still in flight, `FloatMode.Fast` reordering arithmetic that a server has to reproduce exactly, a `[NoAlias]` asserted on memory that does alias, a `SharedStatic<T>` read before its static constructor ran, and AOT settings that only fail once a real build exists.

## 2. Role
Act as the Burst compilation specialist for the client track — the tool reached for once `unity-job-system-and-burst` or `unity-ecs-architecture` has a target that is supposed to be Burst-compiled and either is not, or needs its compilation tuned and verified. You make compilation happen and prove it; you do not decide that Burst is warranted, and you do not schedule the work.

## 3. When to invoke this skill
- Code meant to be Burst-compiled fails the HPC# subset — a managed or reference type, a non-blittable field, a mutable static, an unsupported construct — and must be brought inside it.
- Setting `[BurstCompile]` options at method, job, or assembly level: `FloatMode`, `FloatPrecision`, `CompileSynchronously`, `DisableSafetyChecks`.
- A reported symptom of compilation not happening: a job missing from the Burst Inspector's Compile Targets list, performance identical with and without the attribute, or a first-frame spike that disappears on later runs.
- Reading generated assembly in the Burst Inspector to check whether a loop vectorized.
- Reaching for `Unity.Burst.Intrinsics` (X86 SSE through AVX2, Arm Neon) after auto-vectorization has been measured insufficient.
- Configuring Burst AOT Settings and CPU architecture targets, or diagnosing something that works in Play Mode and fails in a Player build.
- Bridging managed and Burst code with `FunctionPointer<T>`, or sharing mutable static state with `SharedStatic<T>`.
- Negative trigger: scheduling a job, chaining `JobHandle` dependencies, choosing an allocator, or disposing a container — that is `unity-job-system-and-burst`; a job can be perfectly scheduled and still not Burst-compile, and the two are diagnosed separately.
- Negative trigger: no decision or measurement justifying Burst at all — that is `tech-lead-performance`'s call, on a capture from `unity-profiler-diagnostics`.
- Negative trigger: modeling entities, systems, or queries — that is `unity-ecs-architecture`; this skill's rules apply unchanged whether the Burst target is a plain job or an `ISystem`.
- Negative trigger: choosing a container type or allocator strategy — that is `unity-collections`.
- Negative trigger: choosing `Unity.Mathematics` types or functions — that is `unity-mathematics`, even though those types are exactly what the vectorization guidance here is written around.
- Negative trigger: a GPU-driven visual effect — that is `compute-shader-vfx`.

## 4. How to use this skill
1. **Name the approved Job System or ECS work this compilation sits on top of** — per `performance-and-algorithms.md`'s Multithreading section, Burst is not adopted on its own; with no such decision, route to `tech-lead-performance` rather than tuning. [root-links.md](references/root-links.md) pins the Burst version every option below belongs to.
2. **Bring the whole call graph inside the HPC# subset, not just the entry point**, per [csharp-language-support.md](references/csharp-language-support.md) — Burst compiles from an entry point outward, so one managed type, boxed value, or mutable static in any method it reaches disqualifies the entry point itself. Static fields must be `readonly` and compile-time evaluable; strings survive only as `FixedString` or a `Debug.Log` argument.
3. **Apply `[BurstCompile]` at the level the target actually needs**, per [getting-started-and-compilation-model.md](references/getting-started-and-compilation-model.md) — on the job struct, or on both a static method and its containing class, or `[assembly: BurstCompile(...)]` for a project default. Precedence runs Editor menu over per-target attribute over assembly default, so a menu toggle can mask a wrong attribute.
4. **Pick `FloatMode` from whether the result must be reproducible**, per [aliasing-and-attributes.md](references/aliasing-and-attributes.md) — anything feeding a game rule the server also evaluates stays `Deterministic` or `Strict`, because `coding-principles.md`'s Shared Core integrity section forbids float behaviour that can diverge across platforms. `FloatMode.Fast` reorders arithmetic and takes reduced-precision SIMD paths, so it is for presentation-only maths with a stated tolerance.
5. **Verify in the Burst Inspector that the target compiled**, per [debugging-and-inspector.md](references/debugging-and-inspector.md) — `Jobs > Burst > Open Inspector`, confirm the target appears in Compile Targets and has generated assembly. The attribute's presence is never evidence; a silent fallback costs nothing at compile time and everything at runtime.
6. **Set `CompileSynchronously = true` before timing anything in the Editor** — Play Mode compiles asynchronously by default, so the first invocations run managed while Burst works in the background, and an early capture measures the fallback rather than the compiled code.
7. **Reach for `Unity.Burst.Intrinsics` only after generated assembly shows auto-vectorization fell short**, per [intrinsics-and-simd.md](references/intrinsics-and-simd.md) — hand-written SIMD is per-architecture (X86 versus Neon), and any `IsXXXSupported` probe returns false when Burst is disabled, so every intrinsic path needs a scalar fallback that produces the same result.
8. **Cross the managed boundary with `FunctionPointer<T>` or `SharedStatic<T>` only where it is required**, per [function-pointers-and-shared-static.md](references/function-pointers-and-shared-static.md) — delegates are managed and uncompilable; cache `FunctionPointer<T>.Invoke` in a static field, and initialize every `SharedStatic<T>` from a static constructor before any Burst-side read.
9. **Apply `[NoAlias]` only with a guarantee you can state in one sentence** — Burst already infers no-alias for `[NativeContainer]` structs and job fields, so explicit use is rare, and asserting it over memory that can overlap is undefined behaviour rather than a lost optimization.
10. **Set Burst AOT Settings per target platform explicitly**, per [aot-builds-and-platforms.md](references/aot-builds-and-platforms.md) — `Project Settings > Burst AOT Settings` governs Player builds only, never Play Mode, so a wrong CPU architecture target surfaces first on a real device.
11. **Leave `DisableSafetyChecks` off unless a measurement names it as the cost** — it removes the Editor-only container checks that are the project's only race and leak detection, and per `performance-and-algorithms.md`'s Verification section an unmeasured trade of correctness for speed is not a trade at all.
12. **Re-measure after every compilation change and report what moved** — a `FloatMode`, intrinsics, or aliasing change is kept only on evidence from `unity-profiler-diagnostics` or a generated-assembly diff, not on the expectation that it should have helped.
13. **Ask when the required accuracy tolerance is unstated** — if nobody has said whether a value must reproduce exactly, assume it must, keep `FloatMode.Strict`, and flag the assumption; the reverse mistake is discovered only as a desync.

## 5. Specific goals / tasks this skill performs
- Diagnosing and fixing HPC# subset violations anywhere in a Burst entry point's call graph.
- Setting `[BurstCompile]` options at method, job, or assembly level, with precedence understood.
- Verifying compilation in the Burst Inspector and diagnosing a silent managed fallback.
- Choosing `FloatMode`/`FloatPrecision` against the reproducibility the value actually requires.
- Applying `Unity.Burst.Intrinsics` after a measured auto-vectorization shortfall, with a scalar fallback.
- Configuring Burst AOT Settings and CPU architecture targets for Player builds.
- Bridging managed and Burst code with `FunctionPointer<T>` and `SharedStatic<T>`, initialization order included.
- Out of scope: whether Burst is warranted (`tech-lead-performance`); the Profiler capture behind it (`unity-profiler-diagnostics`); scheduling and container lifetime (`unity-job-system-and-burst`); entity and system design (`unity-ecs-architecture`); container selection (`unity-collections`); maths types (`unity-mathematics`); GPU-driven effects (`compute-shader-vfx`).

## 6. Output format
```
## Burst Compilation Work — <job/method/system name>
- Approved by: <the Job System or ECS work this compilation belongs to>
- HPC# issues found: <the specific violation and where in the call graph — or "none">
- Attribute placement: <method / job struct / assembly — and any precedence that mattered>
- FloatMode/FloatPrecision: <value — and whether the result must reproduce across platforms>
- Compilation verified: <Burst Inspector result — compiled, or fell back and why>
- Timing method: <CompileSynchronously used for measurement — yes/no>
- Intrinsics: <which family, the shortfall that justified it, and the scalar fallback — or "none">
- AOT settings: <platforms and CPU architectures touched — or "untouched">
- FunctionPointer/SharedStatic: <used and why — or "none">
- [NoAlias]: <where, and the guarantee in one sentence — or "none">
- Measurement: <before/after evidence, or generated-assembly diff>
- Layer: <Game.Core.* logic compiled / Game.Client.* jobs and systems>
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
- Input: an `IJobFor` already approved for Burst shows the same frame cost with and without `[BurstCompile]`, and does not appear in the Burst Inspector's Compile Targets list.
- Output: traced to two ineligible constructs reachable from `Execute` — an interpolated managed string passed to `Debug.Log`, and a `List<T>` field read through a static helper. Replaced the log with a `FixedString128Bytes` call gated to the Editor, precomputed the lookup into a `NativeArray` supplied as job data, and confirmed the target now appears in Compile Targets with generated assembly present; re-timed with `CompileSynchronously = true` so the measurement was not taken against the async fallback.

**Example 2**
- Input: "Set `FloatMode.Fast` on the whole gameplay assembly — it is free speed on the maths-heavy jobs."
- Output: declined at assembly scope — `Fast` permits arithmetic reordering and reduced-precision SIMD, so applying it across the assembly would cover the movement and damage maths the server independently re-evaluates, and `coding-principles.md`'s Shared Core integrity section requires those to agree bit-for-bit. Applied `Fast` only to the presentation-side particle and camera-shake jobs, with the accepted tolerance stated in the handoff, and left the simulation jobs on `Strict`.

**Example 3**
- Input: a Burst job with Arm Neon intrinsics produces correct results in the Editor but wrong ones on a QA build with Burst compilation disabled.
- Output: the intrinsic path was guarded by `IsNeonSupported`, which returns false under reference-Mono when Burst is off, and the else-branch had drifted from the vector implementation. Rewrote the scalar fallback to compute the same result and added it to the same test case, per §4's intrinsics step, so both paths are exercised rather than only the one Burst takes.

## 8. Edge cases & guardrails
- Never treat the `[BurstCompile]` attribute as evidence of compilation — one ineligible call anywhere in the entry point's graph drops the whole target to managed with no error.
- Never measure Burst code in the Editor without `CompileSynchronously` — async compilation means early frames run the managed fallback, and the number recorded is that fallback.
- Never use `FloatMode.Fast` for anything the server also evaluates — reordered arithmetic breaks the bit-for-bit agreement prediction and authority depend on.
- Never assert `[NoAlias]` without a stated guarantee — misapplied it is undefined behaviour, which surfaces as corrupted results far from the attribute.
- Never read a `SharedStatic<T>` before its static constructor has run — the value is undefined, not a default.
- Never leave an intrinsic path without an equivalent scalar fallback — `IsXXXSupported` is false whenever Burst is disabled, and an untested else-branch is where the divergence hides.
- Never enable `DisableSafetyChecks` to buy speed without a measurement naming it — it removes the only race and leak detection the project has, and only in the environment where those bugs are still catchable.
- Remember AOT settings govern Player builds only — a wrong CPU architecture is invisible in Play Mode and appears first on a device.
- If the required accuracy tolerance is unstated, keep `FloatMode.Strict` and flag it — the opposite assumption is discovered as a desync, long after the change.
