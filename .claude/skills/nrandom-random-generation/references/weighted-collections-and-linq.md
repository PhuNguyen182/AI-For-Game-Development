# Weighted Collections and LINQ

Sources: files under `src/NRandom/` at `v2.0.2`: [a] Collections/WeightedList.cs, [b] Collections/WeightedCollectionExtensions.cs, [c] Collections/WeightedValue.cs, [d] Linq/RandomEnumerable.cs.

## WeightedList&lt;T&gt; and IWeightedCollection&lt;T&gt;

| Member | Fact |
|---|---|
| `WeightedList<T>.Add(T value, double weight)` | Accumulates `TotalWeight` incrementally [a] |
| `WeightedList<T>[index]` get/set | Replaces an entry; adjusts `TotalWeight` by the delta [a] |
| `RemoveRandom(IRandom random, out T item)` | Weighted draw without replacement, for limited-supply pools [a] |
| `GetRandom(IRandom random)` | One weighted draw, not removed [b] |
| `GetRandom(IRandom random, int length)` | `length` draws with replacement into a new array [b] |
| `IEnumerable<T>.ToWeightedList(Func<T,double>)` (`NRandom.Linq`) | Builds a table from existing definitions [d] |
| `WeightedValue<T>` | `record struct` with public fields `Value`/`Weight` (fields so Unity can serialize) [c] |

**Caveat:** every overload without an `IRandom` argument defaults to `RandomEx.Shared`, the non-deterministic instance (see [rng-algorithms-and-determinism.md](rng-algorithms-and-determinism.md)). Pass the injected `IRandom` explicitly in `Game.Core.*`.

```csharp
WeightedList<ItemId> table = new();
table.Add(ItemId.Legendary, weight: 0.5);
table.Add(ItemId.Common, weight: 60.0);
ItemId rolled = table.GetRandom(this._random); // injected, seeded IRandom
```

## NRandom.Linq (`RandomEnumerable`) [d]

| Method | Fact |
|---|---|
| `RandomElement(IRandom random)` | Uniform pick; fast paths for `T[]`/`List<T>`/`IReadOnlyList<T>` |
| `Shuffle(IRandom random)` | Lazy Fisher-Yates, deferred and not in place (unlike `RandomEx.Shuffle`) |
| `RandomEnumerable.Repeat(min, max, length, IRandom random)` | `length` values in `[min,max)`; `int`/`uint`/`long`/`ulong`/`float`/`double` |

`RandomElement` and `Shuffle` also have no-`IRandom` overloads defaulting to `RandomEx.Shared`: same rule.
