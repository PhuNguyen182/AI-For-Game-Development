# Compilation model, precedence and AOT

Source: [Marking code](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/compilation-burstcompile.html), [Assembly options](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/compilation-burstcompile-assembly.html), [Play mode compilation](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/compilation-synchronous.html), [Calling Burst code](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/csharp-calling-burst-code.html), [Building your project](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/building-projects.html), [AOT Settings](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/building-aot-settings.html).

## Placement
- Job struct: compiles `Execute` and everything it reaches.
- Static method: the attribute is needed on both the method and its containing class; marking one is the usual reason a helper stays managed.
- `[assembly: BurstCompile(...)]`: option defaults for the assembly; marks nothing for compilation by itself.
- Direct call from managed C#: IL post-processing routes it to the compiled version; unavailable for generic methods; suppress with `DisableDirectCall`.

## Precedence and timing
- Editor menu (`Jobs > Burst`) beats the per-target attribute, which beats the assembly default; a menu toggle can hide a wrong attribute for everyone but the person who set it.
- Play Mode compiles asynchronously: early invocations run managed. `CompileSynchronously = true` forces compilation before first execution, the precondition for any Editor measurement.
- A first-run spike followed by fast runs is async compilation, not algorithm warm-up; re-time synchronously before optimizing.

## AOT (Player builds)
- Players compile ahead of time into dynamic libraries; the Editor JITs on demand. Play Mode success proves nothing about a build.
- `Edit > Project Settings > Burst AOT Settings` is per platform and has no effect on Play Mode.
- CPU Architecture (Windows, macOS, Linux, Android) decides which intrinsic families exist.
- Toolchain support differs per platform, so a late-added platform can fail at build time.
- A build with no Burst-compiled code still runs, at managed speed: it shows as a device-only perf regression, not a build error. Check the build log.
