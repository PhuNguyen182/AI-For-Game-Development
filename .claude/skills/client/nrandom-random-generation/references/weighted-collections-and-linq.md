# Weighted Collections and LINQ — WeightedList&lt;T&gt;, IWeightedCollection&lt;T&gt;, NRandom.Linq

Source: [WeightedList.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom/Collections/WeightedList.cs), [IWeightedCollection.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom/Collections/IWeightedCollection.cs), [WeightedCollectionExtensions.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom/Collections/WeightedCollectionExtensions.cs), [WeightedValue.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom/Collections/WeightedValue.cs), [RandomEnumerable.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom/Linq/RandomEnumerable.cs).
Covers: SKILL.md §4 — **"Build loot tables and weighted drop rolls with `WeightedList<T>`/`IWeightedCollection<T>.GetRandom(IRandom)` instead of a hand-rolled cumulative-weight loop"**, **"Compose sequence-level randomness through the `NRandom.Linq` extensions with an explicit `IRandom` argument"**.

Building loot tables and randomized sequence operations against
`NRandom.Collections`/`NRandom.Linq`, always with an explicit `IRandom`
argument. `rng-algorithms-and-determinism.md` owns which `IRandom` instance
to construct and how it is seeded.

## WeightedList&lt;T&gt; and IWeightedCollection&lt;T&gt;

| Member | Effect | Use when | Source |
|---|---|---|---|
| `WeightedList<T>.Add(T value, double weight)` | Appends an entry and accumulates `TotalWeight` incrementally, not by full recompute. | Building or growing a loot/drop table. | [WeightedList.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom/Collections/WeightedList.cs) |
| `WeightedList<T>[index]` get/set | Replaces an entry; adjusts `TotalWeight` by the weight delta. | Editing one table entry's weight at runtime. | [WeightedList.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom/Collections/WeightedList.cs) |
| `WeightedList<T>.RemoveRandom(IRandom random, out T item)` | Draws and removes one entry, weighted by `Weight`, without replacement. | Consuming a limited-supply reward pool. | [WeightedList.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom/Collections/WeightedList.cs) |
| `IWeightedCollection<T>.GetRandom(IRandom random)` (via `WeightedCollectionExtensions`) | Draws one weighted value without removing it. | A repeatable weighted roll (loot table reused across many rolls). | [WeightedCollectionExtensions.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom/Collections/WeightedCollectionExtensions.cs) |
| `IWeightedCollection<T>.GetRandom(IRandom random, int length)` | Draws `length` values, with replacement, into a new array. | Rolling several loot slots in one call. | [WeightedCollectionExtensions.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom/Collections/WeightedCollectionExtensions.cs) |
| `IEnumerable<T>.ToWeightedList(Func<T,double> weightSelector)` (`NRandom.Linq`) | Builds a `WeightedList<T>` from an existing sequence plus a weight selector. | Converting existing item definitions into a weighted table. | [RandomEnumerable.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom/Linq/RandomEnumerable.cs) |
| `WeightedValue<T>` | `record struct` holding `Value`/`Weight` as public fields (fields, not properties, specifically so Unity's Inspector can serialize them). | The element type every `WeightedList<T>` operation above returns/accepts. | [WeightedValue.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom/Collections/WeightedValue.cs) |

**Critical caveat**: every parameterless overload of `GetRandom`/`RemoveRandom`
(no `IRandom` argument) defaults to `RandomEx.Shared` — the non-deterministic,
cryptographically-seeded instance covered in
[rng-algorithms-and-determinism.md](rng-algorithms-and-determinism.md).
Always pass the injected `IRandom` explicitly from `Game.Core.*` code.

```csharp
// Game.Core — deterministic weighted roll, explicit IRandom.
WeightedList<ItemId> table = new();
table.Add(ItemId.Legendary, weight: 0.5);
table.Add(ItemId.Common, weight: 60.0);

ItemId rolled = table.GetRandom(this._random); // this._random is the injected, seeded IRandom.
```

## NRandom.Linq (`RandomEnumerable`)

| Method | Effect | Source |
|---|---|---|
| `sequence.RandomElement(IRandom random)` | Picks one element uniformly at random; specialized fast paths exist for `T[]`/`List<T>`/`IReadOnlyList<T>`. | [RandomEnumerable.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom/Linq/RandomEnumerable.cs) |
| `sequence.Shuffle(IRandom random)` | Lazily yields a Fisher–Yates-shuffled sequence (deferred, not in-place — unlike `RandomEx.Shuffle`). | [RandomEnumerable.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom/Linq/RandomEnumerable.cs) |
| `RandomEnumerable.Repeat(min, max, length, IRandom random)` | Yields `length` values in `[min,max)`; overloaded for `int`/`uint`/`long`/`ulong`/`float`/`double`. | [RandomEnumerable.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom/Linq/RandomEnumerable.cs) |

**Critical caveat**: `RandomElement`/`Shuffle` also have a no-`IRandom`
overload defaulting to `RandomEx.Shared` — the same rule as above applies;
pass the instance explicitly in `Game.Core.*`.
