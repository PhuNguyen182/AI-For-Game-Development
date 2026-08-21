---
name: dotnet-memory-and-collections
description: >
  Allocation-conscious memory and collection selection in pure .NET — Span<T>,
  ReadOnlySpan<T>, Memory<T>, ReadOnlyMemory<T>, System.Buffers.ArrayPool<T>,
  IMemoryOwner<T>, stackalloc, System.Collections.Immutable (ImmutableList<T>,
  ImmutableArray<T>, ImmutableDictionary<TKey,TValue>), System.Collections.
  Concurrent (ConcurrentQueue<T>, ConcurrentDictionary<TKey,TValue>,
  ConcurrentBag<T>). Use when slicing/parsing buffers, pooling transient
  arrays, or picking a shared-collection thread-safety story in Game.Core.*
  or Game.Client.* code with no Unity.Collections/Burst dependency. Not for:
  Unity.Collections NativeArray/NativeList and Burst jobs
  (`unity-collections`, `unity-job-system-and-burst`), zero-allocation LINQ
  (`zlinq-zero-allocation-linq`), zero-allocation string building
  (`zstring-zero-allocation-strings`).
---

# .NET Memory and Collections — Span, Memory, ArrayPool, and Collection Selection

## Bundled resources

### References
Read-only context, loaded on demand so SKILL.md itself stays short.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Doc/API root links and version pin for this skill | starting any task in this domain |
| [span-memory-and-buffers.md](references/span-memory-and-buffers.md) | Span<T>/Memory<T> usage rules, ArrayPool<T>, stackalloc | slicing/parsing a buffer or pooling a transient array |
| [collections-selection.md](references/collections-selection.md) | List/Dictionary vs. System.Collections.Concurrent vs. System.Collections.Immutable | choosing a shared-collection thread-safety story |

## 1. Objective
Guarantee that buffer slicing/parsing and shared-collection selection in `Game.Core.*`/`Game.Client.*` code use the correct .NET BCL type for the actual lifetime, sharing, and concurrency pattern — without leaking pooled arrays, storing a stack-only `Span<T>` past its lease, or defaulting to a concurrent/immutable collection nobody's contention pattern needs. Prevents: per-call heap allocation in a hot parsing path, an `ArrayPool<T>` rental that's never returned, and a `System.Collections.Concurrent`/`Immutable` type adopted as a "safe" default with no measured need.

## 2. Role
Act as the .NET memory and collections specialist for the client track — the tool reached for whenever Shared Core or client-side deterministic code needs to slice a buffer, pool a transient array, or pick a collection's thread-safety story, independent of Unity's `Unity.Collections`/Burst pipeline.

## 3. When to invoke this skill
- Parsing or slicing a byte/char buffer (save-data, network payload) without extra allocation.
- Renting a transient array for a hot-path operation instead of `new T[]` per call.
- Deciding whether a shared collection needs `System.Collections.Concurrent`, a plain generic collection, or an immutable snapshot.
- Negative trigger: the buffer/collection is `NativeArray<T>`/`NativeList<T>` consumed by a Burst-compiled job — that's `unity-collections`/`unity-job-system-and-burst`.
- Negative trigger: composing a query over a sequence with zero-allocation LINQ syntax — that's `zlinq-zero-allocation-linq`.
- Negative trigger: building a string without allocation — that's `zstring-zero-allocation-strings`.

## 4. How to use this skill
1. **Confirm the buffer's lifetime and whether it must cross an `await`/`yield` boundary before picking `Span<T>` vs. `Memory<T>`** — `Span<T>` is a stack-only `ref struct` and cannot be stored on the heap, captured in an async state machine, or boxed; `Memory<T>` can, per [span-memory-and-buffers.md](references/span-memory-and-buffers.md).
2. **Default a synchronous API's buffer parameter to `Span<T>`/`ReadOnlySpan<T>`**, per Rule #1 in [span-memory-and-buffers.md](references/span-memory-and-buffers.md); reserve `Memory<T>`/`ReadOnlyMemory<T>` for a parameter that must survive past the method's return (an async signature, a stored field).
3. **Rent, don't allocate, for a large or per-call transient buffer in a hot path** — use `ArrayPool<T>.Shared.Rent`/`Return` per [span-memory-and-buffers.md](references/span-memory-and-buffers.md), and pair every `Rent` with a `Return` in a `try`/`finally` so a thrown exception can't leak the array.
4. **Reserve `stackalloc` for small, bounded-size buffers guarded by an upper-bound check before the allocation**, per [span-memory-and-buffers.md](references/span-memory-and-buffers.md) — an unbounded or loop-nested `stackalloc` risks `StackOverflowException`; fall back to `ArrayPool<T>` above the bound.
5. **Choose the concurrent collection by the actual sharing pattern, not by default** — `System.Collections.Concurrent` types only once multiple threads genuinely add/remove concurrently; a single-writer/many-reader or single-threaded structure stays on `List<T>`/`Dictionary<TKey,TValue>`, per `performance-and-algorithms.md`'s Data structure selection section and [collections-selection.md](references/collections-selection.md).
6. **Reach for `System.Collections.Immutable` only when a shared, publish-once snapshot must be handed to multiple readers without defensive copying**, per [collections-selection.md](references/collections-selection.md) — every mutation allocates a new structurally-shared instance; don't adopt it for a collection its own owner mutates frequently (YAGNI in `coding-principles.md`).
7. **Verify the API is available at the project's Api Compatibility Level before shipping it** — confirm Unity's Player Settings against the `netstandard-2.1` pin in [root-links.md](references/root-links.md), per `coding-principles.md`'s Modern C# syntax section; if the Tech Spec doesn't state a target buffer size or concurrency pattern, ask rather than guessing one.

## 5. Specific goals / tasks this skill performs
- Slice/parse buffers (save-data, network payload bytes/chars) with `Span<T>`/`ReadOnlySpan<T>` without extra allocations.
- Rent/return pooled arrays via `ArrayPool<T>` for transient hot-path buffers instead of `new T[]` per call.
- Pick the correct thread-safety story for a shared collection: a plain generic collection, a `System.Collections.Concurrent` type, or an immutable snapshot.
- Out of scope: `Unity.Collections` `NativeArray`/`NativeList` and Burst-compiled jobs (`unity-collections`, `unity-job-system-and-burst`), allocation-free LINQ query composition (`zlinq-zero-allocation-linq`), allocation-free string building (`zstring-zero-allocation-strings`).

## 6. Output format
```
## .NET Memory & Collections Work — <feature/module name>
- Buffer type: Span<T> / Memory<T> / pooled array via ArrayPool<T> — rationale
- Collection: List<T>/Dictionary / System.Collections.Concurrent.<Type> / System.Collections.Immutable.<Type> — rationale
- Allocation check: <measured evidence the hot path allocates 0/bounded bytes, or "not applicable">
- Runtime compatibility: Api Compatibility Level confirmed against netstandard-2.1 pin
- Layer: Game.Core.* / Game.Client.*
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.**
```
- Known limitations: <what the delivered solution does not cover — omit if genuinely none>
- Latent concerns: <assumptions holding only under current buffer size/thread count, deferred trade-offs>
- Future remediation: <the concrete fix for each concern, with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: parse a fixed-format 20-byte save-data header out of a `byte[]` loaded from disk, in `Game.Core`, called on every load — must avoid allocating.
- Output: a `ReadOnlySpan<byte>` slice over the array, fields read via `Slice`/`BinaryPrimitives`, zero extra allocation; `Layer: Game.Core.*`, per [span-memory-and-buffers.md](references/span-memory-and-buffers.md).

**Example 2**
- Input: "just make the shared score table a `ConcurrentDictionary` in case we add multiplayer later."
- Output: declined — no second writer thread exists yet, which is exactly the speculative extensibility YAGNI forbids in `coding-principles.md`; use `Dictionary<TKey,TValue>` now, escalate to `ConcurrentDictionary<TKey,TValue>` only once a second writer thread is actually introduced, per [collections-selection.md](references/collections-selection.md).

**Example 3**
- Input: encode a chat message (unbounded length from the player) into a `stackalloc` buffer for a hot network-send path.
- Output: declined as written — `stackalloc` on unbounded input risks `StackOverflowException`; guard with a length check and fall back to `ArrayPool<byte>.Shared.Rent` above a fixed small-message threshold, per [span-memory-and-buffers.md](references/span-memory-and-buffers.md)'s Critical caveat.

## 8. Edge cases & guardrails
- Never store a `Span<T>`/`ReadOnlySpan<T>` in a field, capture it in a lambda, or use it across an `await`/`yield` boundary — the compiler rejects most of these directly, but use `Memory<T>` for anything that must actually survive past the current method call.
- Never skip `Return`ing a rented `ArrayPool<T>` array on any exit path, including exceptions — a leaked rental defeats the pool's purpose and silently degrades back to per-call allocation.
- Never reach for `System.Collections.Immutable` or `System.Collections.Concurrent` as a default "safe" choice — both carry real overhead over a plain collection with no measured concurrency/sharing need, per `performance-and-algorithms.md`'s Verification section.
- If it's unclear whether a buffer's producer and consumer run on the same thread/frame, ask rather than assuming `Span<T>` is safe to use across that boundary.
