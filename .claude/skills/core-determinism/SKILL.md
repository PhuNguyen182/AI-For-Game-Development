---
name: core-determinism
description: "Core determinism: fixed-point, MathF drift, GetHashCode, Dictionary order. Use when Core must reproduce across machines."
user-invocable: false
---

# Core Determinism

- **Not for:** the RNG API and seeding (`nrandom-random-generation`).
- **Not for:** auditing a diff for violations (`shared-core-boundary-audit`).
- **Not for:** Burst `FloatMode`/`FloatPrecision` (`unity-burst-compiler`).
- **Not for:** the sync model — lockstep, rollback, state sync (`netcode-architecture-decision`).
- **Not for:** save-file checksums (`save-data-versioning-migration`).
- **Not for:** running Core tests outside the Editor (`core-tests-without-unity`).
- **Docs:** https://learn.microsoft.com/en-us/dotnet/
  - **API pages:** under `api/`, pinned `?view=netstandard-2.1` (Unity's default Api Compatibility Level).
  - **C# spec:** under `csharp/language-reference/language-specification/`.
  - **Version caveat:** Microsoft documents CoreCLR, not Mono or IL2CPP.
  - **Float guarantee:** Unity documents none for managed code on either backend.

## References
- **[float-and-fixed-point.md](references/float-and-fixed-point.md):** An outcome-deciding Core value is computed in `float`/`double` and must agree across machines, or someone proposes fixed-point or integer units.
- **[stable-hashing-and-ordering.md](references/stable-hashing-and-ordering.md):** A hash is persisted, sent, seeded from or compared across processes.
  - **Also:** a `Dictionary`/`HashSet` is iterated or a list sorted where order reaches an outcome, a save or a message.
- **[replay-test.md](references/replay-test.md):** Writing the replay test, or a desync report needs its first diverging tick.

## Scripts
- **[DistanceUnits.cs](scripts/DistanceUnits.cs):** adapt into `Assets/_Project/Scripts/Combat/Core/DistanceUnits.cs` → float metres to integer millimetres with a stated rounding rule and range.
- **[StableHash.cs](scripts/StableHash.cs):** adapt into `Assets/_Project/Scripts/Shared/Core/StableHash.cs` → FNV-1a 64 `Add` overloads for `int`, `float` and `string`.
- **[MatchReplayTests.cs](scripts/MatchReplayTests.cs):** adapt into `Assets/_Project/Scripts/Match/Tests/EditMode/MatchReplayTests.cs` → same-seed double run plus golden-list comparison.

## Steps
1. **Gate: decide whether cross-machine agreement is needed at all:** name every consumer of the result.
   - **Cross-machine when any of:** lockstep or rollback netcode, server re-simulation of client input, replay files, ghost/leaderboard verification, cross-platform play.
   - **Otherwise:** only same-run reproducibility applies (seeded RNG, injected tick clock — `csharp.md` Boundaries) and step 2 is skipped.
   - **Spec silent on the consumers:** `Needs-decision`, `Next: technical-architect`.
2. **Route float vs fixed-point; never decide it:** when cross-machine and the rule computes in `float`/`double`, list each site with its risk class per [float-and-fixed-point.md](references/float-and-fixed-point.md).
   - **One system:** `technical-architect`.
   - **Fixed-point library or project-wide numeric standard:** `cto` (`/decide`).
   - **Library:** name none.
   - **No decision on file:** until one is, return `Needs-decision` with the site list.
3. **Implement the decided numeric form, quantizing once at the boundary:** client-supplied floats (physics, input axes) convert to the decided Core form.
   - **Where and how:** at the Core entry point, with a stated rounding rule.
   - **Float path the decision accepted:** keeps transcendental calls and float-to-int casts of unchecked range out of outcome comparisons, per [float-and-fixed-point.md](references/float-and-fixed-point.md).
4. **Remove hash and order dependence from every outcome, save and message:** per [stable-hashing-and-ordering.md](references/stable-hashing-and-ordering.md).
   - **Criterion:** each hash-collection iteration and each sort in an outcome path is either order-independent (stated why) or ordered by a total, stable key.
5. **Close the remaining ambient inputs:** RNG, time, number parsing, string ordering, accumulation order.
   - **RNG:** per `nrandom-random-generation`.
   - **Time:** tick index × fixed step, passed in.
   - **Number parsing and string ordering:** culture-invariant.
   - **Accumulation order:** no order that depends on thread scheduling.
   - **A source that must stay ambient:** `Needs-decision`, `Next: technical-architect`.
6. **Prove it with a per-tick state-hash replay test:** per [replay-test.md](references/replay-test.md).
   - **Replay test:** same seed + recorded inputs, two fresh runs, bit-exact hash per tick, failure names the first diverging tick.
   - **Cross-machine work:** also compares against a committed golden hash list, in every runner the project has (`core-tests-without-unity`).
   - **Player runs on target devices:** belong to `build-release-engineer` on the GD's request.
   - **Until a Player run happens:** "cross-platform" is a known limitation, not a claim.
7. **Fill `Determinism:` in the return:** from the Output below (csharp-engineer Return extras).

## Never
- **Widening an epsilon:** fixing a desync by widening an epsilon or rounding a comparison — the divergence moves to a later tick and the replay test stops seeing it.
- **Tolerant state hashes:** comparing state hashes with a tolerance, or hashing floats through `ToString()` — the hash must be bit-exact over the raw bits.
- **Two runs in one process:** treating them as cross-process proof — per-process hash seeds are identical within that process.

## Output
```
## Determinism — <module>
- Agreement needed: <same-run only | cross-machine: consumers>
- Numerics: <integer/quantized | float accepted by <architect/ADR> | Needs-decision → technical-architect/cto, sites listed>
- Hashing/ordering: <stable hash; each hash-collection iteration and sort, order-free or keyed by what>
- Ambient inputs: <seed source, tick clock, culture, threading>
- Replay test: <test, ticks × seeds, golden file, result — or "not run">
```

## Example
- **"Swap every `float` in combat for a fixed-point NuGet package":** declined — adopting a library is `cto`'s call.
  - **Done instead:** returned `Needs-decision`, `Next: cto`, with the agreement requirement and the 14 float sites by risk class.
