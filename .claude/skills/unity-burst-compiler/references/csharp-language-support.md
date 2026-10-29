# HPC# subset and managed bridges

Source: [Language support](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/csharp-language-support.html), [Type support](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/csharp-type-support.html), [Static read-only](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/csharp-static-read-only-support.html), [Strings](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/csharp-string-support.html), [Calling Burst code](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/csharp-calling-burst-code.html), [Function pointers](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/csharp-function-pointers.html), [SharedStatic](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/csharp-shared-static.html).

Eligibility belongs to the whole reachable graph: a spotless job still falls back if a helper three calls down touches a managed type, so the Burst Inspector, not reading the job, settles it.

## Types
- Managed and reference types (`class`, delegate, boxed value): unsupported anywhere in the graph; they disqualify the entry point.
- Structs, enums, pointers, spans, tuples: supported; rewriting into blittable structs is the normal fix.
- Generics: supported inside a job, not across the managed direct-call boundary; a generic entry point called from C# will not compile.
- `string`: only as a `Debug.Log` argument or assigned into a `FixedString`.

## Statics
- Static fields must be `readonly` and compile-time evaluable; a mutable static is a compile failure.
- Mutable shared state needs `SharedStatic<T>`.

## Bridges (add only because a requirement forces it)
- Delegates are managed and uncompilable. `BurstCompiler.CompileFunctionPointer<T>` makes a `FunctionPointer<T>` from a `[BurstCompile]` static method.
- Cache `Invoke` in a static field to avoid re-resolving per call.
- A function pointer can be a job field, giving per-instance behaviour without a delegate.
- `SharedStatic<T>` is the only supported mutable static shared between managed C# and HPC#; initialize it from a static constructor before any Burst access, or the state is undefined.
