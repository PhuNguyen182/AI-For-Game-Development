---
name: nrandom-random-generation
description: "Seeded, injectable RNG with NRandom: IRandom, Xoshiro/PCG generators, RandomEx, weighted selection, shuffle, distributions. Use for any randomness in Shared Core or tests that must be reproducible."
user-invocable: false
---

# NRandom Random Generation

Not for: cryptographically secure randomness (use `System.Security.Cryptography.RandomNumberGenerator` directly; no skill owns it), the struct RNG for Burst/job/ECS sites (`unity-mathematics`, `unity-job-system-and-burst`), async composition (`dotnet-concurrency-and-async`), non-RNG Span/collection choice (`dotnet-memory-and-collections`).
Docs: https://github.com/nuskey8/NRandom/tree/v2.0.2/src/NRandom (README: https://github.com/nuskey8/NRandom/blob/v2.0.2/README.md, `#installation`, `#unity`) — pinned `v2.0.2`; check the installed version before trusting a signature. Needs .NET Standard 2.1+.

| Reference | Read when |
|---|---|
| [rng-algorithms-and-determinism.md](references/rng-algorithms-and-determinism.md) | Constructing an `IRandom`, or deciding whether a roll must be deterministic |
| [weighted-collections-and-linq.md](references/weighted-collections-and-linq.md) | Building a loot table or a randomized sequence operation |
| [numerics-and-unity-integration.md](references/numerics-and-unity-integration.md) | Randomizing a vector, rotation or colour, or installing the package |

## Steps
1. **Decide whether the roll must replay identically** across client prediction and server authority. `RandomEx.Create()` and `RandomEx.Shared` are seeded from `RandomNumberGenerator`: never deterministic. Per [rng-algorithms-and-determinism.md](references/rng-algorithms-and-determinism.md).
2. **Pick the algorithm by requirement:** `Xoshiro256StarStarRandom` by default; `Pcg32Random`/`Sfc32Random`/`Sfc64Random` when seed/state travels in a netcode payload; never `ChaChaRandom` for a plain roll. Same file.
3. **Construct the `IRandom` directly, `InitState(seed)` with a caller-controlled seed, inject through the constructor.** Never static or ambient (`csharp-standards` → `coding-principles.md`, Dependency Inversion and Shared Core integrity).
4. **Derive values with the `RandomEx` extensions**, not hand-rolled range math on `NextUInt()`/`NextULong()`.
5. **`RandomEx.Shared` only for client-only, non-gameplay randomness** (VFX variance, idle flavor, UI shuffle).
6. **Weighted rolls use `WeightedList<T>`/`IWeightedCollection<T>.GetRandom(IRandom)`, sequence randomness the `NRandom.Linq` extensions, always with the injected `IRandom` argument.** `WeightedList<T>` picks with `NextDouble() * totalWeight` over a double running sum: a roll two machines must agree on goes through `core-determinism` step 2, or uses integer weights with `NextInt`. Per [weighted-collections-and-linq.md](references/weighted-collections-and-linq.md).
7. **`NRandom.Numerics` in Core; `NRandom.Unity` only in Client code.** Per [numerics-and-unity-integration.md](references/numerics-and-unity-integration.md).
8. **Capture the seed**; no public mid-stream get/set state exists. If the Tech Spec does not say how rollback/replay rebuilds RNG state, or which layer owns the instance's lifetime (per-match, session, call) → `Needs-decision`, `Next: technical-architect`.

## Never
- Call `RandomEx.Create()`/`RandomEx.Shared`, or a parameterless `GetRandom`/`RemoveRandom`/`RandomElement`/`Shuffle`, in Core gameplay code: silent client-server divergence, no compile-time signal.
- Use any NRandom algorithm, `ChaChaRandom` included, for security: the README disclaims it. Use `RandomNumberGenerator` and route token design to `security-reviewer`.
- Assume an `IRandom` can be snapshotted and restored.

## Output
```
## NRandom RNG Work — <feature/module>
- Algorithm: <IRandom implementation — rationale>
- Seeding: <seed source and where captured for replay, or n/a>
- Determinism: <injected instance in Core / RandomEx.Shared client-only>
- Weighted/sequence API: <WeightedList<T> / NRandom.Linq, or n/a>
- Layer: <Core / Client>
- Known limitations: <...>
```

## Example
- "Use `RandomEx.Shared.NextInt` for the crit roll in Core, simpler" → declined: it is seeded per thread from `RandomNumberGenerator`, so client and server diverge on the first roll. Injected a `Xoshiro256StarStarRandom` initialised with the match seed; the server rebuilds the same instance to validate.
