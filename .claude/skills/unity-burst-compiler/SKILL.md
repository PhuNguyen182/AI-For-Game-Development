---
name: unity-burst-compiler
description: "Burst itself: HPC# limits, [BurstCompile] FloatMode, FunctionPointer, [NoAlias]. Use when Burst output or settings fail."
user-invocable: false
---

# Unity Burst Compiler

- **Not for:** scheduling, `JobHandle` chains, allocator lifetime (`unity-job-system-and-burst`).
- **Not for:** whether Burst is warranted (`technical-architect`).
- **Not for:** the capture proving it (`unity-profiler-diagnostics`).
- **Not for:** entity/system design (`unity-ecs-architecture`).
  - **ISystem:** the Burst rules in this skill apply unchanged to an `ISystem`.
- **Not for:** container choice (`unity-collections`).
- **Not for:** `float3` maths (`unity-mathematics`).
- **Not for:** GPU effects (`compute-shader-vfx`).
- **Docs:** https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/index.html — pinned `@1.8`.
  - **Version:** substitute the version in `manifest.json`; option defaults changed between releases.

## References
- **[getting-started-and-compilation-model.md](references/getting-started-and-compilation-model.md):** Placing `[BurstCompile]`, option precedence, first-run Editor timings, Player-build (AOT) settings.
- **[csharp-language-support.md](references/csharp-language-support.md):** Code fails under Burst, or managed code must call Burst (`FunctionPointer<T>`, `SharedStatic<T>`).
- **[debugging-and-inspector.md](references/debugging-and-inspector.md):** Confirming a target compiled, or reading its assembly.
- **[aliasing-and-attributes.md](references/aliasing-and-attributes.md):** Choosing `FloatMode`/`FloatPrecision`, or a loop that should vectorize does not.
- **[intrinsics-and-simd.md](references/intrinsics-and-simd.md):** Auto-vectorization is measured insufficient and hand-written SIMD is proposed.

## Steps
1. **Name the approved Job System or ECS work this sits on:** per `csharp-standards` → `performance-and-algorithms.md` (Multithreading), Burst is not adopted alone.
   - **None:** route to `technical-architect`.
2. **Bring the whole call graph inside HPC#, not just the entry point:** per [csharp-language-support.md](references/csharp-language-support.md).
   - **Why:** one managed type, boxed value or mutable static in any reachable method drops the entry point to managed.
3. **Place `[BurstCompile]` at the needed level:** job struct; static method plus its class; `[assembly: BurstCompile]` default.
   - **Precedence:** Editor menu over attribute over assembly default, per [getting-started-and-compilation-model.md](references/getting-started-and-compilation-model.md).
4. **Pick `FloatMode` by reproducibility:** per [aliasing-and-attributes.md](references/aliasing-and-attributes.md).
   - **Feeding a rule the server also evaluates:** stays `Deterministic` or `Strict` (`csharp-standards` → `coding-principles.md`, Shared Core integrity).
   - **`Fast`:** only for presentation maths with a stated tolerance, scoped per target, never per assembly.
   - **Tolerance unstated:** keep `Strict` and flag it.
5. **Verify in the Burst Inspector that the target compiled:** `Jobs > Burst > Open Inspector`, Compile Targets plus generated assembly, per [debugging-and-inspector.md](references/debugging-and-inspector.md).
   - **The attribute:** never evidence.
6. **Set `CompileSynchronously = true` before timing in the Editor:** Play Mode compiles async, so early frames run managed.
7. **Intrinsics only after generated assembly shows auto-vectorization fell short:** per [intrinsics-and-simd.md](references/intrinsics-and-simd.md).
   - **Each intrinsics path:** has a scalar fallback giving the same result.
8. **`FunctionPointer<T>` / `SharedStatic<T>`:** use only where required.
   - **`FunctionPointer<T>.Invoke`:** cache it in a static field.
   - **`SharedStatic<T>`:** initialize every one from a static constructor before Burst reads it.
9. **Apply `[NoAlias]` only with a guarantee stated in one sentence:** Burst already infers it for `[NativeContainer]` structs and job fields.
10. **Set Burst AOT Settings per platform explicitly:** Player builds only, per [getting-started-and-compilation-model.md](references/getting-started-and-compilation-model.md).
11. **Re-measure after each compilation change:** keep the change only on evidence (`unity-profiler-diagnostics` or an assembly diff).

## Never
- **Use `DisableSafetyChecks` without a measurement naming it as the cost:** it removes the only race and leak detection (`csharp-standards` → `performance-and-algorithms.md`, Verification).
- **Read a `SharedStatic<T>` before its static constructor ran:** the result is undefined, not default.

## Output
```
## Burst Compilation Work — <job/method/system name>
- Approved by: <Job System or ECS work this belongs to>
- HPC# issues: <violation and where in the call graph, or "none">
- Attribute placement: <method / job struct / assembly, precedence that mattered>
- FloatMode/FloatPrecision: <value, and whether the result must reproduce across platforms>
- Compilation verified: <Burst Inspector result, or fell back and why>
- CompileSynchronously used for timing: <yes/no>
- Intrinsics: <family, shortfall that justified it, scalar fallback — or "none">
- AOT settings: <platforms and CPU architectures touched, or "untouched">
- FunctionPointer/SharedStatic/[NoAlias]: <used and why, or "none">
- Measurement: <before/after, or assembly diff>
- Layer: <Core / Client>
```

## Example
- **"Set `FloatMode.Fast` on the whole gameplay assembly":** declined, it would cover movement and damage maths the server re-evaluates.
  - **Did instead:** applied `Fast` only to presentation particle/camera-shake jobs; simulation jobs stay `Strict`.
