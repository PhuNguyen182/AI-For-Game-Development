---
name: nrandom-random-generation
description: "NRandom: IRandom, Xoshiro/PCG, RandomEx, weighted selection, shuffle. Use for reproducible randomness in Core or tests."
user-invocable: false
---

# NRandom Random Generation

- **Not for:** cryptographically secure randomness (use `System.Security.Cryptography.RandomNumberGenerator` directly; no skill owns it).
- **Not for:** the struct RNG for Burst/job/ECS sites (`unity-mathematics`, `unity-job-system-and-burst`).
- **Not for:** async composition (`dotnet-concurrency-and-async`).
- **Not for:** non-RNG Span/collection choice (`dotnet-memory-and-collections`).
- **Docs:** https://github.com/nuskey8/NRandom/tree/v2.0.2/src/NRandom — pinned `v2.0.2`; check the installed version before trusting a signature.
  - **README:** https://github.com/nuskey8/NRandom/blob/v2.0.2/README.md, `#installation`, `#unity`.
  - **Runtime:** needs .NET Standard 2.1+.

## References
- **[rng-algorithms-and-determinism.md](references/rng-algorithms-and-determinism.md):** Constructing an `IRandom`, or deciding whether a roll must be deterministic.
- **[weighted-collections-and-linq.md](references/weighted-collections-and-linq.md):** Building a loot table or a randomized sequence operation.
- **[numerics-and-unity-integration.md](references/numerics-and-unity-integration.md):** Randomizing a vector, rotation or colour, or installing the package.

## Scripts
- **[LootRoller.cs](scripts/LootRoller.cs):** adapt into `Assets/_Project/Scripts/<Feature>/Core/LootRoller.cs` → a Core roller with an injected `IRandom` initialised with the match seed.

## Steps
1. **Decide whether the roll must replay identically across client prediction and server authority:** per [rng-algorithms-and-determinism.md](references/rng-algorithms-and-determinism.md).
   - **`RandomEx.Create()` and `RandomEx.Shared`:** seeded from `RandomNumberGenerator`; never deterministic.
2. **Pick the algorithm by requirement:** per [rng-algorithms-and-determinism.md](references/rng-algorithms-and-determinism.md).
   - **Default:** `Xoshiro256StarStarRandom`.
   - **Seed/state travels in a netcode payload:** `Pcg32Random`/`Sfc32Random`/`Sfc64Random`.
   - **Plain roll:** never `ChaChaRandom`.
3. **Construct the `IRandom` directly, `InitState(seed)` with a caller-controlled seed, inject through the constructor:** never static or ambient.
   - **Reference:** `csharp-standards` → `coding-principles.md`, Dependency Inversion and Shared Core integrity.
4. **Derive values with the `RandomEx` extensions:** not hand-rolled range math on `NextUInt()`/`NextULong()`.
5. **`RandomEx.Shared` only for client-only, non-gameplay randomness:** VFX variance, idle flavor, UI shuffle.
6. **Weighted rolls use `WeightedList<T>`/`IWeightedCollection<T>.GetRandom(IRandom)`:** per [weighted-collections-and-linq.md](references/weighted-collections-and-linq.md).
   - **Sequence randomness:** the `NRandom.Linq` extensions.
   - **Argument for both:** always the injected `IRandom`.
   - **`WeightedList<T>` pick:** `NextDouble() * totalWeight` over a double running sum.
   - **A roll two machines must agree on:** goes through `core-determinism` step 2, or uses integer weights with `NextInt`.
7. **`NRandom.Numerics` in Core; `NRandom.Unity` only in Client code:** per [numerics-and-unity-integration.md](references/numerics-and-unity-integration.md).
8. **Capture the seed:** no public mid-stream get/set state exists.
   - **Tech Spec silent on how rollback/replay rebuilds RNG state:** `Needs-decision`, `Next: technical-architect`.
   - **Tech Spec silent on which layer owns the instance's lifetime (per-match, session, call):** `Needs-decision`, `Next: technical-architect`.

## Never
- **Ambient RNG calls in Core gameplay code:** `RandomEx.Create()`/`RandomEx.Shared`, or a parameterless `GetRandom`/`RemoveRandom`/`RandomElement`/`Shuffle`.
  - **Consequence:** silent client-server divergence, no compile-time signal.
- **NRandom for security:** using any NRandom algorithm, `ChaChaRandom` included — the README disclaims it. Use `RandomNumberGenerator` and route token design to `security-reviewer`.
- **Snapshot and restore:** assuming an `IRandom` can be snapshotted and restored.

## Output
```
## NRandom RNG Work — <feature/module>
- Algorithm: <IRandom implementation — rationale>
- Seeding: <seed source and where captured for replay, or n/a>
- Determinism: <injected instance in Core / RandomEx.Shared client-only>
- Weighted/sequence API: <WeightedList<T> / NRandom.Linq, or n/a>
- Layer: <Core / Client>
```

## Example
- **"Use `RandomEx.Shared.NextInt` for the crit roll in Core, simpler":** declined — it is seeded per thread from `RandomNumberGenerator`, so client and server diverge on the first roll.
  - **Done instead:** injected a `Xoshiro256StarStarRandom` initialised with the match seed; the server rebuilds the same instance to validate.
