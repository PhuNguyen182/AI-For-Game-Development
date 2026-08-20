# Allocators — Baseline

Covers SKILL.md step 6's baseline (the three built-in allocators). Deep allocator-lifetime discipline for a container feeding a scheduled job is `unity-job-system-and-burst`'s territory — this page exists so this skill's own type-choice guidance isn't decoupled from allocator reality.

## Manual
- [Use allocators to control unmanaged memory](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/allocation.html) — `Native-`/`Unsafe-` collections live outside the GC's awareness; you're responsible for deallocating everything you no longer need, or you risk memory waste that degrades performance or crashes the application. Entry point to allocator topics: basics, aliasing, rewindable allocators, custom allocators, and benchmarks.
- [Allocator overview](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/allocator-overview.html) — `Allocator.Temp` (fastest, same-frame/same-job, cannot cross threads, auto-freed at frame/job end), `Allocator.TempJob` (must be disposed within ~4 frames or you get a leak warning), `Allocator.Persistent` (slowest, indefinite lifetime, must be manually disposed). Covers `Dispose(JobHandle)` for deferred disposal after a dependency completes, and `IsCreated` behavior across struct copies/aliases.
