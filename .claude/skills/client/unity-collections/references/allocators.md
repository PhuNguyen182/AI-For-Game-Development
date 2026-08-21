# Allocators — Built-in Lifetimes & Disposal

Source: [Use allocators to control unmanaged memory](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/allocation.html), [Allocator overview](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/allocator-overview.html).
Covers: SKILL.md §4 — **"Pick the allocator by actual data lifetime"**, **"Dispose every `Native-`/custom-allocator allocation on every code path"**.

The three built-in allocators and what disposal actually requires. `Native-`
and `Unsafe-` collections live outside the GC's awareness, so every allocation
is deallocated explicitly or it is a leak. Escalation past these three is
[rewindable-and-custom-allocators.md](rewindable-and-custom-allocators.md);
the routine allocator pick for data feeding one scheduled job belongs to
`unity-job-system-and-burst`, not here.

## The three built-in allocators

| Allocator | Effect | Use when | Source |
|---|---|---|---|
| `Allocator.Temp` | Fastest; auto-freed at the end of the frame or job; cannot cross threads | The data is consumed within the same frame or job that made it | [Allocator overview](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/allocator-overview.html) |
| `Allocator.TempJob` | Must be disposed within ~4 frames or it raises a leak warning | The data outlives one job but not the frame's job chain | [Allocator overview](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/allocator-overview.html) |
| `Allocator.Persistent` | Slowest to allocate; indefinite lifetime; always disposed manually | The data lives across frames with no defined checkpoint | [Allocator overview](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/allocator-overview.html) |

## Disposal mechanics

| Mechanism | Effect | Use when | Source |
|---|---|---|---|
| `Dispose()` | Frees immediately; illegal while a job still reads the container | Nothing scheduled is still using it | [Allocator overview](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/allocator-overview.html) |
| `Dispose(JobHandle)` | Defers the free until the given handle completes, returning a new handle | A scheduled job still holds the container | [Allocator overview](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/allocator-overview.html) |
| `IsCreated` | Reports whether the handle refers to a live allocation — survives struct copies and aliases | Guarding a disposal path that may run twice | [Allocator overview](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/allocator-overview.html) |

**Critical caveat**: `IsCreated` is per-allocation, not per-copy. Every struct
copy and every alias reports `true` until the one underlying allocation is
freed, and `false` for all of them afterward — it cannot tell you *which* copy
owns it. That is why §4 requires the owner to be named where an alias is
introduced.
