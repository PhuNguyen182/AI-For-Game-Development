# Collection selection — plain, concurrent, immutable

Source: Microsoft Learn "Thread-Safe Collections", "ImmutableList&lt;T&gt; Class". `NativeArray<T>` choices belong to `unity-collections`.

## Concurrent (`System.Collections.Concurrent`)
| Type | Use when |
|---|---|
| `ConcurrentQueue<T>` | Several threads enqueue/dequeue FIFO work |
| `ConcurrentDictionary<TKey,TValue>` | Several threads add/update/remove pairs |
| `ConcurrentBag<T>` | Several threads add/remove unordered items, each favouring its own |
| `List<T>` / `Dictionary` | One thread owns all writes, even if others read a completed snapshot |

`List<T>` and other `System.Collections.Generic` types give no synchronisation for concurrent writers. A `Synchronized` wrapper locks per access and does not scale: move to a concurrent type once concurrent writers are real.

## Immutable (`System.Collections.Immutable`)
- `ImmutableList<T>`, `ImmutableArray<T>`, `ImmutableDictionary<TKey,TValue>`: a snapshot published once to readers (possibly on other threads) that must never see it change.
- `.Add`/`.Remove`/`.SetItem` return a new structurally-shared instance; the original is untouched.

```csharp
ImmutableList<string> updated = tags.Add("rare"); // 'tags' unchanged
```

Every mutation allocates. A collection its single owner mutates often stays `List<T>`/`Dictionary`.

`Frozen*` collections (`FrozenDictionary`/`FrozenSet`) are .NET 8+, absent at netstandard-2.1; use `ImmutableArray` or a plain readonly snapshot.
