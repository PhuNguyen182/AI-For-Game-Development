# Stable Hashing and Ordering

Sources below the SKILL.md `Docs:` base (`api/`, `?view=netstandard-2.1`): [a] `system.string.gethashcode`, [b] `system.object.gethashcode`, [c] `system.hashcode`, [d] `system.collections.generic.dictionary-2`, [e] `system.collections.generic.hashset-1`, [f] `system.collections.generic.list-1.sort`.

## Hash APIs that must never leave the process

| API | Fact that decides |
|---|---|
| `string.GetHashCode()` | Can differ across .NET implementations, versions and 32/64-bit; "two subsequent runs of the same program may return different hash codes"; never persist it or use it outside the app domain [a] |
| `object.GetHashCode()` default, `RuntimeHelpers.GetHashCode` | Reference-based; "in some cases, hash codes may be computed on a per-process or per-application domain basis"; never serialize or send [b] |
| `HashCode.Combine` / `HashCode.Add` | "Statically initialized random seed … only deterministic within the scope of an operating system process" [c] |
| `ValueType.GetHashCode` default, record/anonymous-type hashes | Built from the field hashes above, so they inherit every field's instability |

**Caveat:** forbidden uses in Core: persisted in a save, sent in a message, used as an RNG seed, used as an ID, compared between client and server, or deciding iteration order of anything that reaches an outcome.

**Caveat:** on CoreCLR string hashes change between runs [a], so a `dotnet test` mirror can expose a hash-order dependency the Mono Editor run hides; the shipped build still carries it.

## Stable hash for seeds, IDs and replay state

FNV-1a 64 over a canonical byte sequence: fixed field order, integers little-endian byte by byte, strings as UTF-16 code units ordinal with the length first, floats as raw bits. Pure, allocation-free, identical on every runtime.

```csharp
using System;

namespace _Project.Scripts.Shared.Core
{
    public static class StableHash
    {
        public const ulong OffsetBasis = 14695981039346656037UL;
        private const ulong Prime = 1099511628211UL;
        private const int BitsPerByte = 8;
        private const int BitsPerInt = 32;

        public static ulong Add(ulong hash, int value)
        {
            unchecked
            {
                for (int shift = 0; shift < BitsPerInt; shift += BitsPerByte)
                {
                    hash ^= (byte)(value >> shift);
                    hash *= Prime;
                }
            }

            return hash;
        }

        public static ulong Add(ulong hash, float value)
        {
            return Add(hash, BitConverter.SingleToInt32Bits(value));
        }

        public static ulong Add(ulong hash, string value)
        {
            hash = Add(hash, value.Length);
            for (int i = 0; i < value.Length; i++)
            {
                hash = Add(hash, (int)value[i]);
            }

            return hash;
        }
    }
}
```

**Caveat:** `+0f` and `-0f` hash differently, and so do NaN payloads. That is correct for a replay hash (bit-exact), but a NaN in simulation state is already a defect to fix, not to normalize.

**Caveat:** a hash that changes algorithm invalidates every stored seed, ID and golden replay file. Version it like a save format.

## Ordering

| Construct | Fact that decides | Deterministic form |
|---|---|---|
| `foreach` over `Dictionary<K,V>` | "The order in which the items are returned is undefined" [d] | Iterate a key list kept sorted, or a parallel `List<K>` maintained on insert/remove |
| `foreach` over `HashSet<T>` | Elements are "in no particular order" [e] | Same; or prove the fold is order-free (integer sum, count, any/all) |
| `List<T>.Sort`, `Array.Sort` | "Performs an unstable sort; … if two elements are equal, their order might not be preserved" [f] | Comparer ends with a unique tiebreak (entity id) |
| `Enumerable.OrderBy` | Stable, but allocates | Not on a per-tick path (`csharp.md` Hot paths) |
| `string.CompareTo`, `OrderBy(s => s)` default comparer | Culture-sensitive; the device's culture decides the order | `StringComparer.Ordinal` / `string.CompareOrdinal` |
| Float accumulation over partitions or threads | Addition order follows scheduling | Fixed partition order, integer accumulator, or single-threaded (`dotnet-concurrency-and-async` for the threading itself) |

**Caveat:** "it iterates in insertion order on my machine" is an implementation detail with removals and resizes in play; it is not a contract on any runtime.

Unverified: whether Unity's Mono or IL2CPP class libraries randomize `string.GetHashCode` per process (not documented by Microsoft or Unity); whether `Dictionary` enumeration order for the same operation sequence matches between Unity's class libraries and CoreCLR.
