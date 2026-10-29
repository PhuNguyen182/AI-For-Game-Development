---
name: dotnet-memory-and-collections
description: "Allocation-conscious .NET memory and collections: Span, Memory, ArrayPool, stackalloc, immutable collections, collection choice by access pattern. Use when per-frame or per-tick code allocates."
user-invocable: false
---

# .NET Memory and Collections

Not for: `NativeArray`/`NativeList` and Burst jobs (`unity-collections`, `unity-job-system-and-burst`), zero-allocation LINQ (`zlinq-zero-allocation-linq`), zero-allocation strings (`zstring-zero-allocation-strings`), locks, `Interlocked`, `Channel<T>`, async (`dotnet-concurrency-and-async`; this skill only picks the container).
Docs: Microsoft Learn; API pages pinned `?view=netstandard-2.1` (what Unity's default Api Compatibility Level ships), so confirm Player Settings before using a member seen on a newer view.

| Reference | Read when |
|---|---|
| [span-memory-and-buffers.md](references/span-memory-and-buffers.md) | Slicing/parsing a buffer, pooling a transient array, or using `stackalloc` |
| [collections-selection.md](references/collections-selection.md) | Choosing plain vs concurrent vs immutable for shared state |

## Steps
1. **Decide whether the buffer crosses an `await`/`yield` or outlives the call** — no: `Span<T>`; yes: `Memory<T>` ([span-memory-and-buffers.md](references/span-memory-and-buffers.md)).
2. **Default synchronous buffer parameters to `Span<T>`/`ReadOnlySpan<T>`**; `Memory<T>` only for async signatures or stored fields.
3. **Rent large or per-call transient buffers on a hot path** with `ArrayPool<T>.Shared`, `Return` in `finally`.
4. **`stackalloc` only small, bounded sizes**, with a length check and a pool fallback above the bound.
5. **Pick the collection by the real sharing pattern** ([collections-selection.md](references/collections-selection.md)): single writer stays `List<T>`/`Dictionary`; concurrent types only for genuinely concurrent writers; immutable only for publish-once snapshots handed to several readers.
6. **Confirm the API exists at the project's compatibility level.**
7. **Buffer size, or whether producer and consumer share a thread/frame, unstated → `Blocked` naming it.**

## Never
- Store a `Span<T>` in a field, capture it, or hold it across `await`/`yield` — use `Memory<T>`.
- Leave a rented array unreturned on any exit path, exceptions included.
- Adopt a concurrent or immutable collection as a "safe" default with no measured need.

## Output
```
## .NET Memory & Collections — <module>
- Buffer: Span | Memory | ArrayPool — reason
- Collection: <type> — reason
- Allocation check: <measured evidence, or "not applicable">
- Compatibility: netstandard-2.1 availability confirmed
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Make the shared score table a `ConcurrentDictionary` in case of multiplayer" → declined: no second writer exists; `Dictionary` now, switch when one is introduced.
