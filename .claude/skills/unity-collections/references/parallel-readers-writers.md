# Parallel Readers & Writers — Concurrent Access & Ordering

Source: [Parallel readers and writers](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/parallel-readers.html).
Covers: SKILL.md §4 — **"For concurrent writes from a parallel job, decide on write order first"**.

Two ways to have several threads write one container, distinguished by what
they guarantee about order. Thread safety is not the deciding factor — both
are safe; the question is whether indeterministic ordering is acceptable
downstream.

## The two mechanisms

| Mechanism | Effect | Use when | Source |
|---|---|---|---|
| `ParallelWriter` (via `AsParallelWriter()`) | A nested accessor letting multiple threads append safely; simplest to adopt | Downstream logic does not depend on write order | [Parallel readers and writers](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/parallel-readers.html) |
| `NativeStream` / `UnsafeStream` | Separate per-thread buffers, so no cross-thread indeterminism exists to begin with | The ordering indeterminism is itself the problem | [Parallel readers and writers](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/parallel-readers.html) |

## Guarantees and limits

| Property | What it decides | Source |
|---|---|---|
| Thread safety | `ParallelWriter` guarantees it | [Parallel readers and writers](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/parallel-readers.html) |
| Write order | `ParallelWriter` does **not** guarantee it — order follows thread scheduling | [Parallel readers and writers](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/parallel-readers.html) |
| Capacity | A `NativeList<T>.ParallelWriter` can append but cannot grow the list; growing needs synchronization it does not provide | [Parallel readers and writers](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/parallel-readers.html) |

## Recovering determinism

| Approach | What it decides | Source |
|---|---|---|
| Switch to `NativeStream`/`UnsafeStream` | Removes the indeterminism at the source | [Parallel readers and writers](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/parallel-readers.html) |
| Divide work into predetermined index ranges | Each thread writes a known slot, so position encodes order | [Parallel readers and writers](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/parallel-readers.html) |
| Sort the result afterward | Accepts indeterministic writes and pays a sort to recover order | [Parallel readers and writers](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/parallel-readers.html) |

**Critical caveat**: pre-size a list before handing out its `ParallelWriter`.
Exceeding the capacity does not grow the list and does not throw a compile
error — the append simply does not fit.
