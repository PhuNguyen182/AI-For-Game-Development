# Float Modes, Precision & Memory Aliasing

Sources: [Memory aliasing](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/aliasing.html), [NoAlias attribute](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/aliasing-noalias.html), [FloatMode](https://docs.unity3d.com/Packages/com.unity.burst@1.8/api/Unity.Burst.FloatMode.html).
Covers: SKILL.md §4 — **"Pick `FloatMode` from whether the result must be reproducible"**, **"Apply `[NoAlias]` only with a guarantee you can state in one sentence"**.

The two option families that change results rather than just speed. Both are
correctness decisions first: one changes what arithmetic produces, the other
asserts something about memory that the compiler then trusts absolutely.

## Float behaviour

| Value | What it decides | Source |
|---|---|---|
| `FloatMode.Strict` | No reordering; special values respected — the choice whenever a result must reproduce across platforms | [FloatMode](https://docs.unity3d.com/Packages/com.unity.burst@1.8/api/Unity.Burst.FloatMode.html) |
| `FloatMode.Deterministic` | Aims at identical results across targets, which is what shared client/server maths requires | [FloatMode](https://docs.unity3d.com/Packages/com.unity.burst@1.8/api/Unity.Burst.FloatMode.html) |
| `FloatMode.Fast` | Permits reordering and reduced-precision SIMD — presentation-only maths with a stated tolerance | [FloatMode](https://docs.unity3d.com/Packages/com.unity.burst@1.8/api/Unity.Burst.FloatMode.html) |
| `FloatPrecision` | Sets the accuracy demanded of transcendental functions, independently of `FloatMode` | [BurstCompileAttribute](https://docs.unity3d.com/Packages/com.unity.burst@1.8/api/Unity.Burst.BurstCompileAttribute.html) |
| `DisableSafetyChecks` | Drops container safety checks for this target — removes the Editor's race and leak detection, so it is a measured trade or not made | [BurstCompileAttribute](https://docs.unity3d.com/Packages/com.unity.burst@1.8/api/Unity.Burst.BurstCompileAttribute.html) |

## Aliasing

| Subject | What it decides | Source |
|---|---|---|
| Why aliasing matters | Knowing two pointers cannot overlap is what lets Burst vectorize and clone functions; without it, it must assume the worst | [Memory aliasing](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/aliasing.html) |
| Inference already done | Burst infers no-alias for `[NativeContainer]` structs and job struct fields, so most code needs no attribute at all | [NoAlias](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/aliasing-noalias.html) |
| `[NoAlias]` placement | Applies to parameters, struct fields, whole structs, and return values | [NoAlias](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/aliasing-noalias.html) |
| Misapplied `[NoAlias]` | Undefined behaviour — the compiler optimizes on an assertion that is false, and the damage appears far from the attribute | [NoAlias](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/aliasing-noalias.html) |
| `[NativeDisableContainerSafetyRestriction]` | Job-field aliasing rules and the escape hatch that suppresses the safety system's objection | [Aliasing and the job system](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/aliasing-job-system.html) |

**Critical caveat**: `FloatMode.Fast` set at assembly scope silently covers
every job in that assembly, including any that computes a rule the server also
evaluates. Scope it per target, never per assembly, in a project with server
authority.
