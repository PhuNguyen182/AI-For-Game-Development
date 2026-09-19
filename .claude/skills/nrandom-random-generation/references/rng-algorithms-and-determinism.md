# RNG Algorithms and Determinism — IRandom, RandomEx, Seeded Injection

Source: [IRandom.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom/IRandom.cs), [RandomEx.Shared.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom/RandomEx.Shared.cs), [RandomEx.Next.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom/RandomEx.Next.cs), [RandomEx.Shuffle.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom/RandomEx.Shuffle.cs), [RandomEx.GetItems.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom/RandomEx.GetItems.cs), [Xoshiro256StarStarRandom.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom/Xoshiro256StarStarRandom.cs), [Xorshift128Random.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom/Xorshift128Random.cs).
Covers: SKILL.md §4 — **"Confirm whether the roll needs to be reproducible across client prediction and server authority before touching `RandomEx.Shared`/`RandomEx.Create()`"**, **"Pick the algorithm by the actual requirement, not habit"**, **"Construct the chosen `IRandom` directly and call `InitState(seed)` with a seed the caller controls, then inject that instance through the constructor"**, **"Use the `RandomEx` extension methods for every derived value instead of hand-rolling range math on `NextUInt()`/`NextULong()`"**, **"Reserve `RandomEx.Shared` for client-only, non-gameplay randomness"**, **"Capture the seed rather than assuming a mid-stream get/set-state API exists"**.

Which `IRandom` implementation to construct, how `RandomEx.Create()`/
`RandomEx.Shared` are actually seeded, and why that makes them wrong for
`Game.Core.*` gameplay rolls. `weighted-collections-and-linq.md` owns
`WeightedList<T>`/`NRandom.Linq`; `numerics-and-unity-integration.md` owns
Vector/Quaternion/Color extensions and installation.

## IRandom and seeding

| Member | What it decides | Source |
|---|---|---|
| `IRandom.InitState(uint seed)` | Every implementation reseeds from a single `uint` — capture this seed value if the roll must be replayed later. | [IRandom.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom/IRandom.cs) |
| `IRandom.NextUInt()` / `NextULong()` | The only two primitive draws every implementation defines; every other `Next*` method below is built on these. | [IRandom.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom/IRandom.cs) |
| `RandomEx.Create()` | Returns `new Xoshiro256StarStarRandom()` seeded via `System.Security.Cryptography.RandomNumberGenerator.GetInt32` — a non-deterministic seed, unsuitable for anything that must replay identically. | [RandomEx.Shared.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom/RandomEx.Shared.cs) |
| `RandomEx.Shared` | A `[ThreadStatic]`-backed instance that lazily calls `RandomEx.Create()` per thread — thread-safe, but for the same reason as `Create()`, not deterministic. | [RandomEx.Shared.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom/RandomEx.Shared.cs) |

**Critical caveat**: `RandomEx.Create()` and `RandomEx.Shared` both trace back
to a cryptographically-seeded `Xoshiro256StarStarRandom`. Neither is
reproducible run-to-run, which breaks the moment `Game.Core.*` needs the
client's predicted roll to match the server's authoritative one. Construct
the `IRandom` implementation directly (`new Xoshiro256StarStarRandom()`) and
call `InitState(seed)` with a seed the caller controls and can persist or
replay, then inject that instance — never reach it through `RandomEx.Shared`.

## Algorithm selection

| Type | Characteristics | Source |
|---|---|---|
| `Xoshiro256StarStarRandom` | NRandom's own default (the type `RandomEx.Create()` instantiates internally); 256-bit state, fast, good statistical quality — default choice absent a specific constraint. | [Xoshiro256StarStarRandom.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom/Xoshiro256StarStarRandom.cs) |
| `Xorshift128Random` / `Xorshift32Random` / `Xorshift64Random` | Smaller/simpler state; `Xorshift128Random` also exposes a `(uint s0, uint s1, uint s2, uint s3)` constructor that sets the algorithm's internal words directly, bypassing `InitState`'s scrambling. | [Xorshift128Random.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom/Xorshift128Random.cs) |
| `Pcg32Random` / `Sfc32Random` / `Sfc64Random` | One- or two-word internal state — favor these when the seed/state itself must travel in a netcode payload. | [Pcg32Random.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom/Pcg32Random.cs) |
| `MersenneTwisterRandom` | MT19937; also exposes `InitState(ulong seed)`, a 64-bit seed overload none of the other algorithms have. | [MersenneTwisterRandom.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom/MersenneTwisterRandom.cs) |
| `ChaChaRandom(int rounds = 8)` | Stream-cipher-based; markedly more per-call work than the others — reserve for output-hiding needs, never for plain gameplay rolls, and never for actual cryptographic security (see Critical caveat below). | [ChaChaRandom.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom/ChaChaRandom.cs) |

## Derived-value extensions (`RandomEx`, all `this IRandom random`)

| Method | Range | Source |
|---|---|---|
| `NextInt()` / `NextInt(max)` / `NextInt(min, max)` | full range / `[0,max)` / `[min,max)` | [RandomEx.Next.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom/RandomEx.Next.cs) |
| `NextUInt()` / `NextUInt(max)` / `NextUInt(min, max)` | same shape, unsigned | [RandomEx.Next.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom/RandomEx.Next.cs) |
| `NextLong`/`NextULong`, `NextFloat`/`NextDouble` | same overload shape as `NextInt`/`NextUInt` | [RandomEx.Next.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom/RandomEx.Next.cs) |
| `NextDoubleGaussian()` | Gaussian, mean 0.0, standard deviation 1.0 | [RandomEx.Next.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom/RandomEx.Next.cs) |
| `NextBool()` | `(NextUInt() & 1) == 1` | [RandomEx.Next.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom/RandomEx.Next.cs) |
| `NextBytes(byte[]` / `Span<byte>)` | fills the buffer; fast-paths internally when the instance is `Xoshiro128StarStarRandom` | [RandomEx.Next.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom/RandomEx.Next.cs) |
| `Shuffle<T>(T[])` / `Shuffle<T>(Span<T>)` | in-place Fisher–Yates | [RandomEx.Shuffle.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom/RandomEx.Shuffle.cs) |
| `GetItems<T>(ReadOnlySpan<T> choices, int length)` | array of random picks from `choices`, with replacement | [RandomEx.GetItems.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom/RandomEx.GetItems.cs) |

```csharp
// Game.Core — deterministic per-match RNG, injected, never touching RandomEx.Shared.
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

**Critical caveat**: no `IRandom` implementation shipped by NRandom exposes a
public mid-stream get/set-state API — `Xoshiro256StarStarRandom.GetState()`
exists internally but is not `public`, and most other algorithm classes
expose no state accessor at all. For rollback/replay, persist the seed (and
how many draws have been consumed, if the sequence must be fast-forwarded)
rather than assuming a snapshot/restore method exists.
