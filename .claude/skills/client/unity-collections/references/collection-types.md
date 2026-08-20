# Collection Types

Covers SKILL.md step 1 (choosing the right container for the access pattern).

## Manual
- [Collections overview](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/collections-overview.html) — `Native-` collections (in `Unity.Collections`) carry disposal/thread-safety checks; `Unsafe-` collections (in `Unity.Collections.LowLevel.Unsafe`) don't; a third category of small, non-allocated types (e.g. `NativeReference`) has no disposal/thread-safety concern at all. `Native-`/`Unsafe-` pairs exist for most types (`NativeList`/`UnsafeList`, `NativeHashMap`/`UnsafeHashMap`); `Native-` collections cannot contain other `Native-` collections.
- [Collection types](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/collection-types.html) — the type-by-type reference: `NativeList` (resizable list), `NativeHashMap` (single-threaded, low memory overhead) vs. `NativeParallelHashMap` (multithreaded, higher memory overhead), `NativeHashSet` (set of unique values), `NativeQueue` (resizable queue), `NativeStream` (append-only, untyped, per-thread buffers), `NativeReference` (single-element container).

## API
- [NativeList\<T\>](https://docs.unity3d.com/Packages/com.unity.collections@6.6/api/Unity.Collections.NativeList-1.html)
- [NativeParallelHashMap\<TKey,TValue\>](https://docs.unity3d.com/Packages/com.unity.collections@6.6/api/Unity.Collections.NativeParallelHashMap-2.html)
- [NativeHashSet\<T\>](https://docs.unity3d.com/Packages/com.unity.collections@6.6/api/Unity.Collections.NativeHashSet-1.html)
- [NativeQueue\<T\>](https://docs.unity3d.com/Packages/com.unity.collections@6.6/api/Unity.Collections.NativeQueue-1.html)
- [NativeStream](https://docs.unity3d.com/Packages/com.unity.collections@6.6/api/Unity.Collections.NativeStream.html)
- [NativeReference\<T\>](https://docs.unity3d.com/Packages/com.unity.collections@6.6/api/Unity.Collections.NativeReference-1.html)

`NativeArray<T>`/`NativeSlice<T>` are the core array-like types the rest of the package extends — see the Scripting API index in [root-links.md](root-links.md) for their pages.
