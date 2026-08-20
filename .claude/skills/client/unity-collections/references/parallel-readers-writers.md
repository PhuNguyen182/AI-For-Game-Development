# Parallel Readers & Writers

Covers SKILL.md step 7 (safe concurrent access from a parallel job, and the ordering trade-off).

## Manual
- [Parallel readers and writers](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/parallel-readers.html) — nested accessor types like `NativeList<T>.ParallelWriter` (via `AsParallelWriter()`) let multiple threads append safely; a `NativeList<T>.ParallelWriter` can append but not grow the list's capacity (growing needs synchronization it doesn't provide, so pre-size the list). `ParallelWriter` guarantees thread safety but **not** write order — order depends on thread scheduling. For deterministic results, use `NativeStream`/`UnsafeStream` (separate per-thread buffers, no cross-thread indeterminism) instead, or divide work into predetermined ranges / sort the result afterward.
