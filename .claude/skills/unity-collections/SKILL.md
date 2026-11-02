---
name: unity-collections
description: "Unity.Collections: NativeArray/List/HashMap, allocators, Dispose, FixedString, ParallelWriter. Use for Job/Burst data."
user-invocable: false
---

# Unity Collections

- **Not for:** job scheduling and `JobHandle` chains (`unity-job-system-and-burst`).
  - **Also there:** the routine allocator pick for one scheduled job's data.
- **Not for:** Burst tuning (`unity-burst-compiler`).
- **Not for:** ECS component/buffer/query design (`unity-ecs-architecture`).
- **Not for:** `float3`/`Random`/`noise` (`unity-mathematics`).
- **Not for:** `BlobAssetReference<Collider>` and collision-event streams (`unity-physics`).
- **Not for:** `RenderMeshArray` (`unity-entities-graphics`).
- **Docs:** https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/index.html — pinned `@6.6`.
  - **Version:** keep the segment, another version's API may differ.

## References
- **[collection-types.md](references/collection-types.md):** Choosing a container, or sizing a `FixedString`/`FixedList`.
- **[allocators.md](references/allocators.md):** Choosing an allocator, auditing disposal, or Temp/TempJob/Persistent do not fit.
- **[unsafe-collections-and-aliasing.md](references/unsafe-collections-and-aliasing.md):** An `Unsafe-` variant is proposed, or two collections share one allocation.
- **[parallel-readers-writers.md](references/parallel-readers-writers.md):** Several threads write one container in a parallel job.

## Steps
1. **Confirm access pattern, boundary and data lifetime:** pick the type per [collection-types.md](references/collection-types.md).
   - **Default:** do not default to `NativeList<T>` the way managed code defaults to `List<T>`.
   - **Any of the three unstated:** step 10.
2. **Keep managed if no job, Burst method or ECS component is crossed:** unmanaged costs allocator bookkeeping that only a boundary repays (`csharp-standards` → `performance-and-algorithms.md`).
   - **Plain MonoBehaviour code:** Collections works there; using a container does not oblige jobs, Burst or ECS.
3. **Use the fixed-size string and list types for small data crossing a boundary:** `FixedString*Bytes`/`FixedList*Bytes<T>`, the smallest size that fits (by-value copies).
4. **`Native-` unless a measured safety-check cost justifies `Unsafe-`:** per [unsafe-collections-and-aliasing.md](references/unsafe-collections-and-aliasing.md).
   - **Also justifying `Unsafe-`:** a custom container, or nesting.
5. **Name the owner wherever an alias is introduced:** the alias dies with its parent.
6. **Pick the allocator by real lifetime:** per [allocators.md](references/allocators.md).
   - **Rewindable/custom:** escalate only when Temp/TempJob/Persistent provably do not fit.
7. **Decide write order first for concurrent writes:** per [parallel-readers-writers.md](references/parallel-readers-writers.md).
8. **Dispose every `Native-`/custom-allocator allocation on every path:** early returns included (`csharp-standards` → `performance-and-algorithms.md`, Memory discipline).
   - **An alias:** exempt, because the parent's disposal covers it.
9. **State the hand-off once the container is chosen and populated:**
   - **Scheduling:** `unity-job-system-and-burst`.
   - **Burst tuning:** `unity-burst-compiler`.
10. **Missing input:** access pattern, boundary or data lifetime unstated → dispatched agent `Blocked` or `Needs-decision`; main session `AskUserQuestion`.
    - **Why:** guessing picks the wrong container.

## Never
- **Touch an alias after its parent is disposed:** the result is undefined behaviour, not a stale read.
- **`ParallelWriter` assumptions:** never assume its order is deterministic, or that it can grow a list.

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
```

## Example
- **"Make this main-thread-only debug label a `NativeHashMap<int, FixedString64Bytes>` for our Burst job":** declined, nothing crosses into a job.
  - **Did instead:** kept `Dictionary<int, string>`.
