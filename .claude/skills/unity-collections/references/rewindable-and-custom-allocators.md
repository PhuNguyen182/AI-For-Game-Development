# Rewindable & Custom Allocators — Escalation Path

Source: [Rewindable allocator overview](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/allocator-rewindable.html), [Use a custom allocator](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/allocator-custom-use.html).
Covers: SKILL.md §4 — **"Pick the allocator by actual data lifetime"**, escalation branch.

Read only after Temp/TempJob/Persistent ([allocators.md](allocators.md)) have
been shown not to fit. Both options below trade setup complexity for control
over *when* memory is released, and neither is justified by a lifetime the
built-in three already cover.

## Choosing the escalation

| Option | Effect | Use when | Source |
|---|---|---|---|
| Rewindable allocator | Linear/bump allocation from pre-allocated blocks; one rewind frees every allocation it made | Many short-lived allocations share one release point, and per-allocation `Dispose()` bookkeeping is the actual cost | [Rewindable allocator overview](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/allocator-rewindable.html) |
| Custom allocator | A user-defined allocation strategy registered globally | A lifetime or strategy neither the built-in three nor a rewindable allocator covers | [Use a custom allocator](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/allocator-custom-use.html) |

## Rewindable allocator mechanics

| Property | What it decides | Source |
|---|---|---|
| Block alignment | 64-byte minimum alignment on every block | [Rewindable allocator overview](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/allocator-rewindable.html) |
| Block growth | Blocks double in size up to a cap, then grow linearly | [Rewindable allocator overview](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/allocator-rewindable.html) |
| Rewind semantics | Frees every allocation at once; some blocks are retained for reuse, others released | [Rewindable allocator overview](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/allocator-rewindable.html) |
| Creation | Created through `AllocatorHelper` | [Rewindable allocator overview](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/allocator-rewindable.html) |

## Custom allocator lifecycle

| Stage | Call | Source |
|---|---|---|
| Create | Declare and create via `AllocatorHelper`, register globally, then initialize | [Use a custom allocator](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/allocator-custom-use.html) |
| Allocate `Native-` | `CollectionHelper.CreateNativeArray` / `CollectionHelper.Dispose` | [Use a custom allocator](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/allocator-custom-use.html) |
| Allocate `Unsafe-` | `AllocatorManager.Allocate` / `AllocatorManager.Free` | [Use a custom allocator](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/allocator-custom-use.html) |
| Tear down | Rewind the handle, unregister it, then free its backing memory | [Use a custom allocator](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/allocator-custom-use.html) |

**Critical caveat**: the teardown order is load-bearing. Unregistering before
rewinding leaks the blocks the allocator still holds, and nothing reports it.
