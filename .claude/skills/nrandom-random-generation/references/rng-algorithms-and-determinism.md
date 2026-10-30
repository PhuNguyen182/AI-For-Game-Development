# RNG Algorithms and Determinism

Sources: files under `src/NRandom/` at `v2.0.2` (SKILL.md `Docs:` base): [a] IRandom.cs, [b] RandomEx.Shared.cs, [c] RandomEx.Next.cs, [d] RandomEx.Shuffle.cs, [e] RandomEx.GetItems.cs, [f] one file per algorithm.

## IRandom and seeding

| Member | Fact that decides |
|---|---|
| `IRandom.InitState(uint seed)` | Every implementation reseeds from one `uint`; capture it for replay [a] |
| `NextUInt()` / `NextULong()` | The only two primitives; every other `Next*` is built on them [a] |
| `RandomEx.Create()` | `new Xoshiro256StarStarRandom()` seeded via `RandomNumberGenerator.GetInt32`: non-deterministic [b] |
| `RandomEx.Shared` | `[ThreadStatic]`, lazily `Create()` per thread: thread-safe, not deterministic [b] |

**Caveat:** `Create()` and `Shared` are never reproducible run to run. Construct the implementation directly and `InitState(seed)` with a seed the caller can persist.

**Caveat:** no shipped `IRandom` exposes a public mid-stream get/set state (`Xoshiro256StarStarRandom.GetState()` is not public). For rollback/replay persist the seed plus draws consumed if the sequence must be fast-forwarded.

## Algorithms [f]

| Type | Fact |
|---|---|
| `Xoshiro256StarStarRandom` | NRandom's default; 256-bit state, fast, good quality |
| `Xorshift32/64/128Random` | Smaller state; `Xorshift128Random` also has a `(uint s0, s1, s2, s3)` constructor setting the words directly, bypassing `InitState` scrambling |
| `Pcg32Random` / `Sfc32Random` / `Sfc64Random` | One- or two-word state; use when state travels in a netcode payload |
| `MersenneTwisterRandom` | MT19937; only one with an `InitState(ulong seed)` overload |
| `ChaChaRandom(int rounds = 8)` | Much slower; for output hiding only, never plain rolls, and not for security (the library disclaims it) |

## Derived values (`RandomEx`, `this IRandom`)

| Method | Range |
|---|---|
| `NextInt()` / `(max)` / `(min, max)` [c] | full / `[0,max)` / `[min,max)`; `NextUInt`, `NextLong`, `NextULong`, `NextFloat`, `NextDouble` share the shape |
| `NextDoubleGaussian()` [c] | mean 0.0, standard deviation 1.0 |
| `NextBool()` [c] | `(NextUInt() & 1) == 1` |
| `NextBytes(byte[] / Span<byte>)` [c] | fills buffer; fast path for `Xoshiro128StarStarRandom` |
| `Shuffle<T>(T[] / Span<T>)` [d] | in-place Fisher-Yates |
| `GetItems<T>(ReadOnlySpan<T> choices, int length)` [e] | random picks with replacement |

```csharp
// Core: deterministic per-match RNG, injected, never RandomEx.Shared.
public sealed class LootRoller
{
    private readonly IRandom _random;

    public LootRoller(uint matchSeed)
    {
        this._random = new Xoshiro256StarStarRandom();
        this._random.InitState(matchSeed);
    }

    public int RollCriticalPercent()
    {
        return this._random.NextInt(0, 100);
    }
}
```
