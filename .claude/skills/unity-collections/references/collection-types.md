# Collection Types — Native Container Selection

Source: [Collections overview](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/collections-overview.html), [Collection types](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/collection-types.html).
Covers: SKILL.md §4 — **"Confirm the actual access pattern before picking a type"**.

Holds the per-type behaviour that settles which container fits a given access
pattern, plus the three-way split between `Native-`, `Unsafe-`, and
non-allocating types. Allocator choice for the type picked here is
[allocators.md](allocators.md); concurrent-write mechanics are
[parallel-readers-writers.md](parallel-readers-writers.md).

## Container categories

| Category | Namespace | Disposal / thread-safety checks | Source |
|---|---|---|---|
| `Native-` collections | `Unity.Collections` | Yes — the correct default | [Collections overview](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/collections-overview.html) |
| `Unsafe-` collections | `Unity.Collections.LowLevel.Unsafe` | None — lower overhead, no bug reporting | [Collections overview](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/collections-overview.html) |
| Small non-allocated types | `Unity.Collections` | Not applicable — nothing is allocated | [Collections overview](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/collections-overview.html) |

**Critical caveat**: a `Native-` collection cannot contain another `Native-`
collection. Nesting requires the `Unsafe-` counterpart as the inner type.

## Type-by-access-pattern

| Type | What it decides | Source |
|---|---|---|
| `NativeArray\<T\>` | Fixed length set at allocation; the baseline when the count is known up front and never changes | [Collection types](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/collection-types.html) |
| `NativeList\<T\>` | Resizable append; the only choice when the final count is unknown at allocation time | [Collection types](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/collection-types.html) |
| `NativeHashMap\<TKey,TValue\>` | Single-threaded key-value lookup, low memory overhead — pick this unless a job writes it in parallel | [Collection types](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/collection-types.html) |
| `NativeParallelHashMap\<TKey,TValue\>` | Multithreaded key-value writes at higher memory overhead; the cost is only justified by an actual parallel writer | [Collection types](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/collection-types.html) |
| `NativeHashSet\<T\>` | Uniqueness checks only — no value payload, so it never substitutes for a map | [Collection types](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/collection-types.html) |
| `NativeQueue\<T\>` | Resizable FIFO; use when consumption order must match production order | [Collection types](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/collection-types.html) |
| `NativeStream` | Append-only, **untyped**, per-thread buffers — the deterministic alternative to a `ParallelWriter` | [Collection types](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/collection-types.html) |
| `NativeReference\<T\>` | A single element that must cross into a job; no disposal-free shortcut exists for one value | [Collection types](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/collection-types.html) |
| `NativeSlice\<T\>` | A view over an existing allocation, not an allocation — see [unsafe-collections-and-aliasing.md](unsafe-collections-and-aliasing.md) | [Collections overview](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/collections-overview.html) |

## API index

| Type | Source |
|---|---|
| `NativeList\<T\>` | [NativeList\<T\>](https://docs.unity3d.com/Packages/com.unity.collections@6.6/api/Unity.Collections.NativeList-1.html) |
| `NativeParallelHashMap\<TKey,TValue\>` | [NativeParallelHashMap\<TKey,TValue\>](https://docs.unity3d.com/Packages/com.unity.collections@6.6/api/Unity.Collections.NativeParallelHashMap-2.html) |
| `NativeHashSet\<T\>` | [NativeHashSet\<T\>](https://docs.unity3d.com/Packages/com.unity.collections@6.6/api/Unity.Collections.NativeHashSet-1.html) |
