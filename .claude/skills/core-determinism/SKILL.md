---
name: core-determinism
description: "Game.Core determinism: agreement gate, float vs fixed-point routing, MathF/Math and IL2CPP/Mono float drift, string.GetHashCode, Dictionary/HashSet order, stable hash, per-tick replay test. Use when Core results must reproduce across machines."
user-invocable: false
---

# Core Determinism

Not for: the RNG API and seeding (`nrandom-random-generation`), auditing a diff for violations (`shared-core-boundary-audit`), Burst `FloatMode`/`FloatPrecision` (`unity-burst-compiler`), the sync model — lockstep, rollback, state sync (`netcode-architecture-decision`), save-file checksums (`save-data-versioning-migration`), running Core tests outside the Editor (`core-tests-without-unity`).
Docs: https://learn.microsoft.com/en-us/dotnet/ — API pages under `api/`, pinned `?view=netstandard-2.1` (Unity's default Api Compatibility Level); C# spec under `csharp/language-reference/language-specification/`; Microsoft documents CoreCLR, not Mono or IL2CPP, and Unity documents no float guarantee for managed code on either backend.

| Reference | Read when |
|---|---|
| [float-and-fixed-point.md](references/float-and-fixed-point.md) | An outcome-deciding Core value is computed in `float`/`double` and must agree across machines, or someone proposes fixed-point or integer units |
| [stable-hashing-and-ordering.md](references/stable-hashing-and-ordering.md) | A hash is persisted, sent, seeded from or compared across processes; a `Dictionary`/`HashSet` is iterated or a list sorted where order reaches an outcome, a save or a message |
| [replay-test.md](references/replay-test.md) | Writing the replay test, or a desync report needs its first diverging tick |

## Steps
1. **Gate: decide whether cross-machine agreement is needed at all.** Name every consumer of the result. Cross-machine when any of: lockstep or rollback netcode, server re-simulation of client input, replay files, ghost/leaderboard verification, cross-platform play. Otherwise only same-run reproducibility applies (seeded RNG, injected tick clock — `csharp.md` Boundaries) and step 2 is skipped. Spec silent on the consumers → `Needs-decision`, `Next: technical-architect`.
2. **Route float vs fixed-point; never decide it.** Cross-machine and the rule computes in `float`/`double`: list each site with its risk class per [float-and-fixed-point.md](references/float-and-fixed-point.md). One system → `technical-architect`; a fixed-point library or a project-wide numeric standard → `cto` (`/decide`). Name no library. Until a decision is on file, return `Needs-decision` with the site list.
3. **Implement the decided numeric form, quantizing once at the boundary.** Client-supplied floats (physics, input axes) convert to the decided Core form at the Core entry point with a stated rounding rule. A float path the decision accepted keeps transcendental calls and float-to-int casts of unchecked range out of outcome comparisons, per the same file.
4. **Remove hash and order dependence from every outcome, save and message**, per [stable-hashing-and-ordering.md](references/stable-hashing-and-ordering.md). Criterion: each hash-collection iteration and each sort in an outcome path is either order-independent (stated why) or ordered by a total, stable key.
5. **Close the remaining ambient inputs.** RNG per `nrandom-random-generation`; time as tick index × fixed step passed in; number parsing and string ordering culture-invariant; no accumulation order that depends on thread scheduling. A source that must stay ambient → `Needs-decision`, `Next: technical-architect`.
6. **Prove it with a per-tick state-hash replay test**, per [replay-test.md](references/replay-test.md): same seed + recorded inputs, two fresh runs, bit-exact hash per tick, failure names the first diverging tick. Cross-machine work also compares against a committed golden hash list, in every runner the project has (`core-tests-without-unity`). Player runs on target devices belong to `build-release-engineer` on the GD's request; until one runs, "cross-platform" is a known limitation, not a claim.
7. **Fill `Determinism:` in the return** (csharp-engineer Return extras) from the Output below.

## Never
- Fix a desync by widening an epsilon or rounding a comparison — the divergence moves to a later tick and the replay test stops seeing it.
- Compare state hashes with a tolerance, or hash floats through `ToString()` — the hash must be bit-exact over the raw bits.
- Treat two runs in one process as cross-process proof — per-process hash seeds are identical within that process.

## Output
```
## Determinism — <module>
- Agreement needed: <same-run only | cross-machine: consumers>
- Numerics: <integer/quantized | float accepted by <architect/ADR> | Needs-decision → technical-architect/cto, sites listed>
- Hashing/ordering: <stable hash; each hash-collection iteration and sort, order-free or keyed by what>
- Ambient inputs: <seed source, tick clock, culture, threading>
- Replay test: <test, ticks × seeds, golden file, result — or "not run">
- Verified: <runners that ran: Editor Edit Mode / dotnet mirror / Player <platform> — or "not run">
- Known limitations: <e.g. no Player run on <platform>>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Swap every `float` in combat for a fixed-point NuGet package" → declined: adopting a library is `cto`'s call; returned `Needs-decision`, `Next: cto`, with the agreement requirement and the 14 float sites by risk class.
