---
name: nrandom-random-generation
description: >
  Seeded, injectable pseudorandom number generation via NRandom's `IRandom`
  abstraction and `RandomEx` extensions — `Xoshiro256StarStarRandom`,
  `Xorshift128Random`, `Pcg32Random`, `Sfc32Random`/`Sfc64Random`,
  `MersenneTwisterRandom`, `ChaChaRandom`,
  `NextInt`/`NextFloat`/`NextDoubleGaussian`/`Shuffle`,
  `WeightedList<T>`/`IWeightedCollection<T>`
  loot tables, `NRandom.Linq`'s `RandomElement`/`RandomEnumerable`, and
  `NRandom.Numerics`/`NRandom.Unity`'s Vector/Quaternion/Color extensions.
  Use when a gameplay roll, loot table, or shuffle needs to be deterministic
  and replayable across client prediction and server authority, replacing
  `UnityEngine.Random`/`System.Random`. Not for: cryptographically secure
  randomness (`System.Security.Cryptography.RandomNumberGenerator` directly —
  no skill in this project owns it), Burst/Job System native random
  (`unity-job-system-and-burst`), general Task/async composition
  (`dotnet-concurrency-and-async`), Span/buffer/collection selection unrelated
  to weighted RNG (`dotnet-memory-and-collections`).
---

# NRandom Random Generation — Seeded IRandom, Weighted Tables, Vector/Color Extensions

## Bundled resources

### References
Read-only context, loaded on demand so SKILL.md itself stays short.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Repo/NuGet root links and the `v2.0.2` version pin for this skill | starting any task in this domain |
| [rng-algorithms-and-determinism.md](references/rng-algorithms-and-determinism.md) | `IRandom`, `RandomEx.Create`/`.Shared` seeding, the 13 algorithm implementations, `RandomEx` derived-value extensions | choosing/constructing an `IRandom` instance, or deciding whether a roll must be deterministic |
| [weighted-collections-and-linq.md](references/weighted-collections-and-linq.md) | `WeightedList<T>`, `IWeightedCollection<T>`, `WeightedValue<T>`, `NRandom.Linq`'s `RandomElement`/`Shuffle`/`Repeat`/`ToWeightedList` | building a loot table or a randomized sequence operation |
| [numerics-and-unity-integration.md](references/numerics-and-unity-integration.md) | `NRandom.Numerics`/`NRandom.Unity` Vector/Quaternion/Color extensions, `SerializableWeightedList<T>`, installation steps | randomizing a position/rotation/color, or setting up the package |

## 1. Objective
Guarantee that every gameplay-affecting random roll in `Game.Core.*` is deterministic and replayable — driven by an explicitly seeded, injected `IRandom` instance — while non-gameplay client-only randomness (VFX flavor, idle animation variance) may use NRandom's convenience surface freely. Prevents: client-prediction/server-authority divergence from a hidden non-deterministic seed, a hand-rolled weighted-roll loop duplicating what `WeightedList<T>` already does correctly, and `UnityEngine`-dependent extensions leaking into Shared Core.

## 2. Role
Act as the NRandom specialist for the client track — the tool reached for whenever `Game.Core.*` gameplay rules need a seeded RNG, a weighted loot table, or a randomized shuffle/sequence, and whenever `Game.Client.*` needs Vector/Quaternion/Color randomization or Inspector-editable weighted tables built on the same library.

## 3. When to invoke this skill
- Replacing a `UnityEngine.Random`/`System.Random` call in `Game.Core.*` with a seeded, injectable RNG, per `coding-principles.md`'s Shared Core integrity section.
- Building a loot table, gacha roll, or any weighted-probability drop.
- Shuffling a deck/sequence, or picking a uniformly random element, in a way that must be reproducible.
- Randomizing a spawn position, rotation, or VFX color/tint in `Game.Client.*`.
- Negative trigger: the randomness must be cryptographically secure (tokens, anti-collusion secrets) — NRandom's own documentation explicitly disclaims this use; use `System.Security.Cryptography.RandomNumberGenerator` directly instead.
- Negative trigger: bulk parallel random generation inside a Burst-compiled job over `NativeArray<T>` — that's `unity-job-system-and-burst`.
- Negative trigger: the task is general async/Task composition or Span/collection selection with no RNG involved — that's `dotnet-concurrency-and-async`/`dotnet-memory-and-collections`.

## 4. How to use this skill
1. **Confirm whether the roll needs to be reproducible across client prediction and server authority before touching `RandomEx.Shared`/`RandomEx.Create()`** — both trace back to a `Xoshiro256StarStarRandom` seeded from `System.Security.Cryptography.RandomNumberGenerator`, so neither is deterministic, per [rng-algorithms-and-determinism.md](references/rng-algorithms-and-determinism.md).
2. **Pick the algorithm by the actual requirement, not habit** — default to `Xoshiro256StarStarRandom` for general gameplay rolls; use `Pcg32Random`/`Sfc32Random`/`Sfc64Random` when the seed/state must stay small in a netcode payload; never `ChaChaRandom` for a plain roll, since it's markedly slower for no benefit a gameplay roll needs, per [rng-algorithms-and-determinism.md](references/rng-algorithms-and-determinism.md).
3. **Construct the chosen `IRandom` directly and call `InitState(seed)` with a seed the caller controls, then inject that instance through the constructor** — never hold it as static/ambient state, per `coding-principles.md`'s Dependency Inversion section and [rng-algorithms-and-determinism.md](references/rng-algorithms-and-determinism.md).
4. **Use the `RandomEx` extension methods for every derived value instead of hand-rolling range math on `NextUInt()`/`NextULong()`** — `NextInt`/`NextFloat`/`NextDouble`/`NextBool`/`NextBytes`/`Shuffle`/`GetItems` already handle bias-free range mapping, per [rng-algorithms-and-determinism.md](references/rng-algorithms-and-determinism.md).
5. **Reserve `RandomEx.Shared` for client-only, non-gameplay randomness** (VFX variance, idle-animation flavor, UI shuffle) where cross-client/server determinism doesn't matter, per [rng-algorithms-and-determinism.md](references/rng-algorithms-and-determinism.md)'s Critical caveat.
6. **Build loot tables and weighted drop rolls with `WeightedList<T>`/`IWeightedCollection<T>.GetRandom(IRandom)` instead of a hand-rolled cumulative-weight loop**, always passing the injected `IRandom` explicitly rather than the parameterless overload, per [weighted-collections-and-linq.md](references/weighted-collections-and-linq.md).
7. **Compose sequence-level randomness through the `NRandom.Linq` extensions with an explicit `IRandom` argument** (`RandomElement`, `Shuffle`, `RandomEnumerable.Repeat`, `ToWeightedList`) rather than plain `System.Linq`, per [weighted-collections-and-linq.md](references/weighted-collections-and-linq.md).
8. **Use `NRandom.Numerics` in `Game.Core.*` and `NRandom.Unity` only in `Game.Client.*`** — the former has no `UnityEngine` dependency, the latter's Color/`SerializableWeightedList<T>` helpers do, per `naming-convention.md`'s namespace boundary and [numerics-and-unity-integration.md](references/numerics-and-unity-integration.md).
9. **Capture the seed rather than assuming a mid-stream get/set-state API exists** — most `IRandom` implementations expose no public state accessor, per [rng-algorithms-and-determinism.md](references/rng-algorithms-and-determinism.md)'s Critical caveat; if the Tech Spec doesn't say how a rollback/replay should reconstruct RNG state, ask rather than guessing one.

## 5. Specific goals / tasks this skill performs
- Wire a seeded, injectable `IRandom` into `Game.Core.*` gameplay-rule code as the deterministic RNG `coding-principles.md`'s Shared Core integrity section requires.
- Build weighted loot/drop tables and randomized sequence operations with `WeightedList<T>` and `NRandom.Linq`.
- Add Vector/Quaternion/Color randomization via `NRandom.Numerics`/`NRandom.Unity` at the correct layer.
- Out of scope: cryptographically secure randomness (flag it — no skill in this project owns it, do not substitute NRandom), Burst/Job System native random (`unity-job-system-and-burst`), general Task/async composition (`dotnet-concurrency-and-async`), Span/buffer/collection selection unrelated to weighted RNG (`dotnet-memory-and-collections`).

## 6. Output format
```
## NRandom RNG Work — <feature/module name>
- Algorithm: IRandom implementation (e.g. Xoshiro256StarStarRandom) — rationale
- Seeding: seed source, and where it is captured for replay — or "not applicable"
- Determinism: injected instance in Game.Core.* / RandomEx.Shared (client-only, non-deterministic) — confirmed
- Weighted/sequence API used: WeightedList<T> / NRandom.Linq — or "not applicable"
- Layer: Game.Core.* / Game.Client.*
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.**
```
- Known limitations: <what the delivered solution does not cover — omit if genuinely none>
- Latent concerns: <assumptions that hold only under the current seed/replay scheme, deferred trade-offs>
- Future remediation: <the concrete fix for each concern, with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: Tech Spec asks for a critical-hit roll in `Game.Core` that the server must be able to replay identically given the same match seed.
- Output: `LootRoller`/damage-resolution class constructs `new Xoshiro256StarStarRandom()`, calls `InitState(matchSeed)` once at match start, and injects the instance via constructor; the roll itself uses `_random.NextInt(0, 100)`; the server reconstructs an identical instance from the same `matchSeed` to validate, per [rng-algorithms-and-determinism.md](references/rng-algorithms-and-determinism.md).

**Example 2**
- Input: "just call `RandomEx.Shared.NextInt(...)` for the crit-chance roll in `Game.Core`, it's simpler."
- Output: declined — `RandomEx.Shared` is seeded from `RandomNumberGenerator` per thread, so client and server diverge on the very first roll; inject a seeded `IRandom` instead, per [rng-algorithms-and-determinism.md](references/rng-algorithms-and-determinism.md)'s Critical caveat and `coding-principles.md`'s Shared Core integrity section.

**Example 3**
- Input: "we need encryption-grade randomness for a matchmaking anti-collusion token — use NRandom's `ChaChaRandom` since it's the crypto-sounding one."
- Output: declined — NRandom's own README explicitly states the library, including `ChaChaRandom`, is "not for security purposes"; use `System.Security.Cryptography.RandomNumberGenerator` directly and route the token-handling design to `tech-lead-sdk-platform`/`security-reviewer`, per [rng-algorithms-and-determinism.md](references/rng-algorithms-and-determinism.md).

## 8. Edge cases & guardrails
- Never call `RandomEx.Create()`/`RandomEx.Shared` inside `Game.Core.*` gameplay-rule code — both resolve to a `RandomNumberGenerator`-seeded `Xoshiro256StarStarRandom`, silently breaking client-server determinism with no compile-time signal.
- Never use `ChaChaRandom` or any other NRandom algorithm for cryptographic/security purposes — the library's own documentation explicitly disclaims this; use `System.Security.Cryptography.RandomNumberGenerator` instead.
- Never assume a mid-stream `IRandom` instance can be snapshotted/restored via a public API — only the initial seed is guaranteed capturable; treat anything else as an unverified assumption and ask.
- If the Tech Spec doesn't say which layer owns the RNG instance's lifetime (per-match, per-session, or per-call), ask rather than defaulting to a static/shared instance.
