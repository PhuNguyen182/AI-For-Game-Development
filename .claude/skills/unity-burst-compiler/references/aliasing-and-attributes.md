# Float modes, precision and aliasing

Source: [Memory aliasing](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/aliasing.html), [NoAlias](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/aliasing-noalias.html), [Aliasing and the job system](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/aliasing-job-system.html), [FloatMode](https://docs.unity3d.com/Packages/com.unity.burst@1.8/api/Unity.Burst.FloatMode.html), [BurstCompileAttribute](https://docs.unity3d.com/Packages/com.unity.burst@1.8/api/Unity.Burst.BurstCompileAttribute.html).

Both families are correctness decisions first.

## Float behaviour
- `FloatMode.Strict`: no reordering, special values respected; whenever a result must reproduce across platforms.
- `FloatMode.Deterministic`: aims at identical results across targets; shared client/server maths.
- `FloatMode.Fast`: permits reordering and reduced-precision SIMD; presentation-only maths with a stated tolerance.
- `FloatPrecision`: accuracy demanded of transcendental functions, independent of `FloatMode`.
- `DisableSafetyChecks`: drops container safety checks for the target; a measured trade or not made.

At assembly scope `Fast` silently covers every job in the assembly, including any computing a rule the server evaluates. With server authority, scope it per target.

## Aliasing
- Knowing two pointers cannot overlap lets Burst vectorize and clone functions; otherwise it assumes the worst.
- No-alias is already inferred for `[NativeContainer]` structs and job struct fields.
- `[NoAlias]` applies to parameters, struct fields, whole structs and return values.
- Misapplied `[NoAlias]` is undefined behaviour; damage appears far from the attribute.
- `[NativeDisableContainerSafetyRestriction]` suppresses the safety system's objection to job-field aliasing.
