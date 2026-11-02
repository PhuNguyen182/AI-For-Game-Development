---
name: dotnet-memory-and-collections
description: "Span, Memory, ArrayPool, stackalloc, immutable collections, collection choice. Use when per-frame code allocates."
user-invocable: false
---

# .NET Memory and Collections

- **Not for:** `NativeArray`/`NativeList` and Burst jobs (`unity-collections`, `unity-job-system-and-burst`).
- **Not for:** zero-allocation LINQ (`zlinq-zero-allocation-linq`).
- **Not for:** zero-allocation strings (`zstring-zero-allocation-strings`).
- **Not for:** locks, `Interlocked`, `Channel<T>`, async (`dotnet-concurrency-and-async`); this skill only picks the container.
- **Docs:** Microsoft Learn; API pages pinned `?view=netstandard-2.1` (what Unity's default Api Compatibility Level ships).
  - **Version caveat:** confirm Player Settings before using a member seen on a newer view.

## References
- **[span-memory-and-buffers.md](references/span-memory-and-buffers.md):** Slicing/parsing a buffer, pooling a transient array, or using `stackalloc`.
- **[collections-selection.md](references/collections-selection.md):** Choosing plain vs concurrent vs immutable for shared state.

## Steps
1. **Decide whether the buffer crosses an `await`/`yield` or outlives the call:** per [span-memory-and-buffers.md](references/span-memory-and-buffers.md).
   - **No:** `Span<T>`.
   - **Yes:** `Memory<T>`.
2. **Default synchronous buffer parameters to `Span<T>`/`ReadOnlySpan<T>`:** `Memory<T>` only for async signatures or stored fields.
3. **Rent large or per-call transient buffers on a hot path:** with `ArrayPool<T>.Shared`, `Return` in `finally`.
4. **`stackalloc` only small, bounded sizes:** with a length check and a pool fallback above the bound.
5. **Pick the collection by the real sharing pattern:** per [collections-selection.md](references/collections-selection.md).
   - **Single writer:** stays `List<T>`/`Dictionary`.
   - **Concurrent types:** only for genuinely concurrent writers.
   - **Immutable:** only for publish-once snapshots handed to several readers.
6. **API availability:** confirm the API exists at the project's compatibility level.
7. **Missing input:** buffer size, or whether producer and consumer share a thread/frame, unstated → `Blocked` naming it.

## Never
- **Storing a `Span<T>`:** in a field, capturing it, or holding it across `await`/`yield` — use `Memory<T>`.
- **Unreturned rented array:** leaving one unreturned on any exit path, exceptions included.
- **Default concurrent or immutable collections:** adopting one as a "safe" default with no measured need.

## Output
```
## .NET Memory & Collections — <module>
- Buffer: Span | Memory | ArrayPool — reason
- Collection: <type> — reason
- Allocation check: <measured evidence, or "not applicable">
- Compatibility: netstandard-2.1 availability confirmed
```

## Example
- **"Make the shared score table a `ConcurrentDictionary` in case of multiplayer":** declined — no second writer exists.
  - **Done instead:** `Dictionary` now, switch when one is introduced.
