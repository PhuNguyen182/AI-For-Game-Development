# Function Pointers & SharedStatic

Covers SKILL.md step 8 (bridging the managed/Burst boundary deliberately, not by default).

## Manual
- [Function pointers](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/csharp-function-pointers.html) — `FunctionPointer<T>` as the Burst-compatible alternative to C# delegates (which Burst treats as managed and can't compile); caching `Invoke` for best call performance; passing function pointers into jobs.
- [SharedStatic struct](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/csharp-shared-static.html) — sharing mutable static data between C# and HPC#; must be initialized from a static constructor before any Burst-side access.

## Scripting API
- [`FunctionPointer<T>`](https://docs.unity3d.com/Packages/com.unity.burst@1.8/api/Unity.Burst.FunctionPointer-1.html) — `Invoke`, `IsCreated`, `Value`; compiled via `BurstCompiler.CompileFunctionPointer<T>`.
- [`SharedStatic<T>`](https://docs.unity3d.com/Packages/com.unity.burst@1.8/api/Unity.Burst.SharedStatic-1.html) — shares mutable static data between C# and HPC#.
