# Compilation Model — Placement, Precedence & Play Mode

Sources: [Marking code for Burst compilation](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/compilation-burstcompile.html), [Assembly-level Burst options](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/compilation-burstcompile-assembly.html), [Burst compilation in Play mode](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/compilation-synchronous.html).
Covers: SKILL.md §4 — **"Apply `[BurstCompile]` at the level the target actually needs"**.

Where the attribute goes, which setting wins when several disagree, and why an
Editor timing taken too early measures the wrong code.

## Placement

| Target | What it decides | Source |
|---|---|---|
| Job struct | Compiles the job's `Execute` and everything it reaches | [Marking code](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/compilation-burstcompile.html) |
| Static method | Needs the attribute on **both** the method and its containing class — marking one is the common reason a helper stays managed | [Marking code](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/compilation-burstcompile.html) |
| `[assembly: BurstCompile(...)]` | Sets project-wide option defaults for that assembly, without marking anything for compilation by itself | [Assembly options](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/compilation-burstcompile-assembly.html) |
| Direct call from managed C# | IL post-processing routes a managed call into the compiled version; unavailable for generic methods, and suppressible with `DisableDirectCall` | [Calling Burst code](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/csharp-calling-burst-code.html) |

## Precedence and timing

| Subject | What it decides | Source |
|---|---|---|
| Precedence order | Editor menu (`Jobs > Burst`) beats the per-target attribute, which beats the assembly default — so a menu toggle can hide a wrong attribute for everyone but the person who set it | [Assembly options](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/compilation-burstcompile-assembly.html) |
| Async compilation (Play Mode default) | Early invocations run the managed version while Burst compiles in the background | [Play mode compilation](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/compilation-synchronous.html) |
| `CompileSynchronously = true` | Forces compilation before first execution — the precondition for any Editor measurement to mean anything | [Play mode compilation](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/compilation-synchronous.html) |
| Editor JIT versus Player AOT | Two different compilation paths; Player behaviour is governed by AOT settings, see [aot-builds-and-platforms.md](aot-builds-and-platforms.md) | [Get started](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/getting-started.html) |

**Critical caveat**: a first-run frame spike followed by fast later runs is the
signature of async compilation, not of a warm-up cost in the algorithm. Time it
again with `CompileSynchronously` before optimizing anything.
