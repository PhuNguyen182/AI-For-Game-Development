# Custom Instrumentation

Covers SKILL.md step 9 (making an opaque system's cost visible in the Profiler window).

## Manual
- [Adding profiling information to your code — introduction](https://docs.unity3d.com/Manual/profiler-adding-information-code-intro.html) — `ProfilerMarker` vs. `Profiler.BeginSample`, and the `com.unity.profiling.core` package for `ProfilerCounter`/custom modules.

## Scripting API
- [`ProfilerMarker`](https://docs.unity3d.com/ScriptReference/Unity.Profiling.ProfilerMarker.html) — the recommended, lower-overhead way to mark a code block; `Begin`/`End` compile away to zero overhead in non-Development builds. Jobs/Burst-compatible.
- [`ProfilerRecorder`](https://docs.unity3d.com/ScriptReference/Unity.Profiling.ProfilerRecorder.html) — reads a marker's or counter's value back at runtime (e.g. an in-game debug overlay), in both Editor and Player builds.
- [`Profiler.BeginSample`](https://docs.unity3d.com/ScriptReference/Profiling.Profiler.BeginSample.html) — the older API; transfers the full string label per call, more overhead than `ProfilerMarker`. Prefer `ProfilerMarker` for new code.
- [`CustomSampler`](https://docs.unity3d.com/ScriptReference/Profiling.CustomSampler.html) — a pre-created sampler handle, cheaper than `Profiler.BeginSample` when the label doesn't need to be dynamic.
- [`Profiler` class](https://docs.unity3d.com/ScriptReference/Profiling.Profiler.html) — `enabled`, `logFile`/`enableBinaryLog` for saving a full profiling capture to a file from a standalone build.
