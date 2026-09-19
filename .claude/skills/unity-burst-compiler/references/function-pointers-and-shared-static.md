# `FunctionPointer<T>` & `SharedStatic<T>` — Crossing the Boundary

Sources: [Function pointers](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/csharp-function-pointers.html), [SharedStatic](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/csharp-shared-static.html).
Covers: SKILL.md §4 — **"Cross the managed boundary with `FunctionPointer<T>` or `SharedStatic<T>` only where it is required"**.

The two supported bridges between managed C# and HPC#, and the initialization
rule that makes one of them safe. Both exist because the ordinary constructs —
delegates and mutable statics — are exactly what the HPC# subset in
[csharp-language-support.md](csharp-language-support.md) rejects.

| Subject | What it decides | Source |
|---|---|---|
| Why not a delegate | Delegates are managed; Burst cannot compile a call through one, so indirection needs `FunctionPointer<T>` instead | [Function pointers](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/csharp-function-pointers.html) |
| `BurstCompiler.CompileFunctionPointer<T>` | Produces the pointer from a `[BurstCompile]`-marked static method | [FunctionPointer](https://docs.unity3d.com/Packages/com.unity.burst@1.8/api/Unity.Burst.FunctionPointer-1.html) |
| Caching `.Invoke` | Storing `Invoke` in a static field avoids re-resolving on every call, which is the difference between a cheap and an expensive boundary crossing | [Function pointers](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/csharp-function-pointers.html) |
| Passing into a job | A function pointer can be a job field, which is how per-instance behaviour reaches Burst-compiled code without a delegate | [Function pointers](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/csharp-function-pointers.html) |
| `SharedStatic<T>` | The only supported mutable static shared between managed C# and HPC# | [SharedStatic](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/csharp-shared-static.html) |
| Initialization order | Must be initialized from a static constructor before any Burst-side access; reading it earlier gives an undefined state rather than a default | [SharedStatic](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/csharp-shared-static.html) |

**Critical caveat**: both bridges widen what Burst-compiled code can reach, and
each one is a place where a managed assumption can re-enter. Add them because a
requirement forces it, not to make an existing managed design compile unchanged.
