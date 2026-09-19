# Collection Selection — System.Collections.Concurrent vs. System.Collections.Immutable

Source: [Thread-Safe Collections](https://learn.microsoft.com/en-us/dotnet/standard/collections/thread-safe/), [ImmutableList&lt;T&gt; Class](https://learn.microsoft.com/en-us/dotnet/api/system.collections.immutable.immutablelist-1?view=netstandard-2.1).
Covers: SKILL.md §4 — **"Choose the concurrent collection by the actual sharing pattern, not by default"**, **"Reach for `System.Collections.Immutable` only when a shared, publish-once snapshot must be handed to multiple readers without defensive copying"**.

Picking the thread-safety story for a shared collection: plain generic,
concurrent, or immutable. `unity-collections` owns the equivalent decision
for `NativeArray<T>`/`NativeList<T>` consumed by Burst-compiled jobs.

## System.Collections.Concurrent

| Type | Use when | Source |
|---|---|---|
| `ConcurrentQueue<T>` | Multiple threads genuinely enqueue/dequeue FIFO work concurrently; lock-free via `Interlocked`. | [Thread-Safe Collections](https://learn.microsoft.com/en-us/dotnet/standard/collections/thread-safe/) |
| `ConcurrentDictionary<TKey,TValue>` | Multiple threads genuinely add/update/remove key-value pairs concurrently. | [Thread-Safe Collections](https://learn.microsoft.com/en-us/dotnet/standard/collections/thread-safe/) |
| `ConcurrentBag<T>` | Multiple threads add/remove unordered items concurrently, each thread favoring its own locally-added items. | [Thread-Safe Collections](https://learn.microsoft.com/en-us/dotnet/standard/collections/thread-safe/) |
| `List<T>` / `Dictionary<TKey,TValue>` | A single thread owns all writes (even if other threads only read a completed snapshot) — no concurrent-collection overhead needed. | [Thread-Safe Collections](https://learn.microsoft.com/en-us/dotnet/standard/collections/thread-safe/) |

**Critical caveat**: `System.Collections`/`System.Collections.Generic` types
(`ArrayList`, `List<T>`) provide no built-in synchronization for concurrent
writers — a `Synchronized` wrapper locks the whole collection on every
access and doesn't scale; use a `System.Collections.Concurrent` type instead
once concurrent writers are real, per Thread-Safe Collections above.

## System.Collections.Immutable

| Type | Use when | Source |
|---|---|---|
| `ImmutableList<T>` / `ImmutableArray<T>` / `ImmutableDictionary<TKey,TValue>` | A snapshot is published once and handed to multiple readers (possibly on other threads) that must never see it mutate underneath them. | [ImmutableList&lt;T&gt; Class](https://learn.microsoft.com/en-us/dotnet/api/system.collections.immutable.immutablelist-1?view=netstandard-2.1) |
| `.Add`/`.Remove`/`.SetItem` on an immutable collection | Returns a *new* instance sharing structure with the original — the original is never mutated. | [ImmutableList&lt;T&gt; Class](https://learn.microsoft.com/en-us/dotnet/api/system.collections.immutable.immutablelist-1?view=netstandard-2.1) |

```csharp
ImmutableList<string> tags = ImmutableList.Create("boss", "elite");
ImmutableList<string> updated = tags.Add("rare"); // 'tags' is unchanged
```

**Critical caveat**: every mutation on an immutable collection allocates a
new structurally-shared instance. A collection mutated frequently by its own
single owner should stay `List<T>`/`Dictionary<TKey,TValue>` — adopting
`System.Collections.Immutable` there trades a real, measurable allocation
cost for a safety guarantee nothing needs, which is exactly the speculative
complexity YAGNI forbids in `coding-principles.md`.
