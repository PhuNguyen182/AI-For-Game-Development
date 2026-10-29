# Parallel readers and writers

Source: [Parallel readers and writers](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/parallel-readers.html).

Both mechanisms are thread-safe; the question is whether indeterministic order is acceptable downstream.

- `ParallelWriter` (`AsParallelWriter()`): simplest; thread-safe but order follows thread scheduling. A `NativeList<T>.ParallelWriter` appends but cannot grow the list.
- `NativeStream` / `UnsafeStream`: per-thread buffers, so no cross-thread indeterminism; use when order is the problem.

Recovering determinism: switch to `NativeStream`/`UnsafeStream`; divide work into predetermined index ranges so position encodes order; or accept indeterministic writes and sort afterward.

Pre-size a list before handing out its `ParallelWriter`: exceeding capacity never grows it: with safety checks on, `AddNoResize` throws `InvalidOperationException`; with them off (release players) it writes out of bounds. Pre-size to the worst case.
