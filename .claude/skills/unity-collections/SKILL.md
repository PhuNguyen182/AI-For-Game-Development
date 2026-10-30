---
name: unity-collections
description: "Unity.Collections unmanaged containers: NativeArray/List/HashMap/Queue/Stream, allocators (Temp/TempJob/Persistent/rewindable), Dispose, Unsafe- aliasing, FixedString/FixedList, ParallelWriter. Use for Job/Burst-compatible data."
user-invocable: false
---

# Unity Collections

Not for: job scheduling and `JobHandle` chains, and the routine allocator pick for one scheduled job's data (`unity-job-system-and-burst`), Burst tuning (`unity-burst-compiler`), ECS component/buffer/query design (`unity-ecs-architecture`), `float3`/`Random`/`noise` (`unity-mathematics`), `BlobAssetReference<Collider>` and collision-event streams (`unity-physics`), `RenderMeshArray` (`unity-entities-graphics`).
Docs: https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/index.html — pinned `@6.6`; keep the segment, another version's API may differ.

| Reference | Read when |
|---|---|
| [collection-types.md](references/collection-types.md) | Choosing a container, or sizing a `FixedString`/`FixedList` |
| [allocators.md](references/allocators.md) | Choosing an allocator, auditing disposal, or Temp/TempJob/Persistent do not fit |
| [unsafe-collections-and-aliasing.md](references/unsafe-collections-and-aliasing.md) | An `Unsafe-` variant is proposed, or two collections share one allocation |
| [parallel-readers-writers.md](references/parallel-readers-writers.md) | Several threads write one container in a parallel job |

## Steps
1. **Confirm access pattern, boundary and data lifetime; if any is unstated, ask.** Guessing picks the wrong container. Pick the type per [collection-types.md](references/collection-types.md); do not default to `NativeList<T>` the way managed code defaults to `List<T>`.
2. **Keep managed if no job, Burst method or ECS component is crossed**: unmanaged costs allocator bookkeeping that only a boundary repays (`csharp-standards` → `performance-and-algorithms.md`). Collections works in plain MonoBehaviour code; using a container does not oblige jobs, Burst or ECS.
3. **Use `FixedString*Bytes`/`FixedList*Bytes<T>` for small data crossing a boundary**; smallest size that fits (by-value copies).
4. **`Native-` unless a measured safety-check cost** (or a custom container, or nesting) justifies `Unsafe-`, per [unsafe-collections-and-aliasing.md](references/unsafe-collections-and-aliasing.md).
5. **Name the owner wherever an alias is introduced**; the alias dies with its parent.
6. **Pick the allocator by real lifetime**; escalate to rewindable/custom only when Temp/TempJob/Persistent provably do not fit, per [allocators.md](references/allocators.md).
7. **Decide write order first for concurrent writes**, per [parallel-readers-writers.md](references/parallel-readers-writers.md).
8. **Dispose every `Native-`/custom-allocator allocation on every path**, early returns included (`csharp-standards` → `performance-and-algorithms.md`, Memory discipline). An alias is exempt: the parent's disposal covers it.
9. **State the hand-off** once the container is chosen and populated: scheduling to `unity-job-system-and-burst`, Burst tuning to `unity-burst-compiler`.

## Never
- Touch an alias after its parent is disposed (undefined behaviour, not a stale read).
- Assume `ParallelWriter` order is deterministic, or that it can grow a list.

## Output
```
## Collections Work — <system/data name>
- Access pattern: <sequential / key-value / set / FIFO / per-thread append / single value>
- Collection type: <type> — rationale
- Managed vs. unmanaged: <the boundary that forced unmanaged, or "kept managed — no boundary crossed">
- Unsafe- variant: <yes/no — justification>
- Aliasing: <yes/no — owning collection>
- Allocator: <Temp / TempJob / Persistent / rewindable / custom> — rationale
- Concurrent-write pattern: <ParallelWriter / NativeStream / UnsafeStream / none>
- Disposal: <confirmed on every code path>
- Layer: <Core / Client / Editor-only>
- Known limitations: <...>
```

## Example
- "Make this main-thread-only debug label a `NativeHashMap<int, FixedString64Bytes>` for our Burst job" → declined: nothing crosses into a job; kept `Dictionary<int, string>`.
