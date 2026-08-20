# Getting Started & the Compilation Model

Covers SKILL.md steps 1, 3, 10 (prerequisite framing, `[BurstCompile]` application levels, Play Mode compilation behavior).

## Manual
- [Get started](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/getting-started.html) — first Burst-compiled example, install/enable Burst.
- [HPC# overview](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/csharp-hpc-overview.html) — what High Performance C# is and how it relates to the full C# language.
- [Marking code for Burst compilation](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/compilation-burstcompile.html) — `[BurstCompile]` on jobs, classes (with `[BurstCompile]` static methods), structs, static methods; implicit entry-point compilation.
- [Defining Burst options for an assembly](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/compilation-burstcompile-assembly.html) — `[assembly: BurstCompile(...)]` project-wide defaults; precedence order (Editor menu > per-target attribute > assembly default).
- [Calling Burst-compiled code](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/csharp-calling-burst-code.html) — direct-call IL post-processing from managed C#, `DisableDirectCall`; generic methods/types unsupported.
- [Burst compilation in Play mode](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/compilation-synchronous.html) — async (default) vs. synchronous JIT compilation while in the Editor.
