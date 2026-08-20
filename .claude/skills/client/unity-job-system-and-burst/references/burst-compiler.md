# Burst Compiler

Covers SKILL.md step 6 (`[BurstCompile]` eligibility and verification).

## Manual
- [Burst](https://docs.unity3d.com/Manual/com.unity.burst.html) — package landing page; links to the installed version's full manual.
- [Get started with Burst](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/getting-started.html) — `[BurstCompile]` on job structs and on static methods (both the method and its parent class need the attribute); JIT compilation in Editor Play Mode vs. AOT in Player builds; no managed/reference types allowed in Burst-compiled code.

Note: version-substitute the `@1.8` segment for the Burst package version actually installed in the project (`Window > Package Manager` or `manifest.json`).

For deep Burst-specific compilation tuning beyond this basic setup — the HPC# language subset, `[BurstCompile]` parameters (`FloatMode`, `FloatPrecision`), the Burst Inspector, SIMD intrinsics, AOT/platform settings, `FunctionPointer<T>`/`SharedStatic<T>`, or `[NoAlias]`/memory aliasing — see the dedicated `unity-burst-compiler` skill instead.
