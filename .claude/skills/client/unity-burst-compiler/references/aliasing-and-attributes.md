# Memory Aliasing & Compilation Attributes

Covers SKILL.md steps 4, 9 (`FloatMode`/`FloatPrecision` choice, `[NoAlias]` used sparingly with a genuine guarantee).

## Manual
- [Memory aliasing](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/aliasing.html) — how telling Burst that memory regions don't overlap enables vectorization and function cloning.
- [NoAlias attribute](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/aliasing-noalias.html) — usage on parameters, struct fields, structs, and return values; Burst already infers no-alias info for `[NativeContainer]` structs and job fields, so explicit use is rare; misuse is undefined behavior.
- [Aliasing and the job system](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/aliasing-job-system.html) — aliasing rules specific to job struct fields, `[NativeDisableContainerSafetyRestriction]`.

## Scripting API
- [`BurstCompileAttribute`](https://docs.unity3d.com/Packages/com.unity.burst@1.8/api/Unity.Burst.BurstCompileAttribute.html) — tags jobs/function pointers for Burst compilation; constructors/properties for `FloatPrecision`, `FloatMode`, `DisableSafetyChecks`, `CompileSynchronously`.
- [`FloatMode`](https://docs.unity3d.com/Packages/com.unity.burst@1.8/api/Unity.Burst.FloatMode.html) — `Default`/`Strict` (no reordering, respects special values), `Fast` (reordering, reduced-precision SIMD), `Deterministic`.
