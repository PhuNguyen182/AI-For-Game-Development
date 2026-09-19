---
name: zlinq-zero-allocation-linq
description: >
  ZLinq — allocation-free LINQ: `.AsValueEnumerable()` opening a chain of
  struct-based `ValueEnumerable<T>` operators (`Where`, `Select`, `OrderBy`,
  `Sum`, `Any`, `FirstOrDefault`, `Aggregate`) over a concrete `List<T>`,
  array, `Span<T>`, or `Dictionary<TKey,TValue>`, plus `.ToArray()`/`.ToList()`
  materialization. No `UnityEngine` dependency, so it works in `Game.Core.*`
  and `Game.Client.*`. Use to satisfy the "never LINQ in a hot path" rule when
  a query chain's readability is still wanted inside `Update()`,
  `FixedUpdate()`, or per-tick Core evaluation.
  Not for: outside a hot path, where `System.Linq` is already permitted (`coding-principles.md`), data-structure choice (`unity-collections`), Burst job bodies (`unity-job-system-and-burst`), string building (`zstring-zero-allocation-strings`).
---

# ZLinq — Zero-Allocation LINQ

## 1. Objective
Keep a query chain's readability inside a hot path without the per-call allocation `System.Linq`'s `IEnumerable<T>` operators and boxed enumerators cost — while catching the two conversions that look successful and are not: a capturing lambda that still allocates a closure, and a chain that ends in materialization.

## 2. Role
Act as the allocation-conscious query specialist for the client track — reached for when `performance-and-algorithms.md` forbids `System.Linq` at a specific measured site but a hand-rolled loop would genuinely read worse than the chain it replaces.

## 3. When to invoke this skill
- A per-frame or per-tick path uses `System.Linq` and the Profiler attributes an allocation to that chain.
- A `Game.Core.*` algorithm wants filter, transform, or aggregate composition without introducing a `UnityEngine` dependency.
- A hand-rolled nested loop in a hot path has become hard to read, and a query chain would state the intent more directly at no allocation cost.
- Negative trigger: editor tooling, one-off setup, or SDK and config code — `coding-principles.md`'s `var` and LINQ section already permits plain `System.Linq` there, so converting adds ceremony for no measured gain.
- Negative trigger: the real defect is the collection type, such as a linear scan where a keyed lookup belongs — fix the structure first per `performance-and-algorithms.md`'s Data structure selection section; `unity-collections` owns the unmanaged container choice.
- Negative trigger: inside a `[BurstCompile]` job body — that is `unity-job-system-and-burst` territory with its own container and compilation constraints; ZLinq targets ordinary managed method bodies.
- Negative trigger: the allocating thing in that path is string construction — that is `zstring-zero-allocation-strings`, a separate conversion.

## 4. How to use this skill
1. **Measure before converting**, per `performance-and-algorithms.md`'s Verification section — this skill resolves an allocation the Profiler attributed to a specific chain, and a speculative conversion changes readable code for an unproven benefit.
2. **Check that the collection type is right before optimizing the query over it** — a zero-allocation scan of the wrong structure is still the wrong structure, and no operator chain recovers the complexity a keyed lookup would have given.
3. **Open the chain with `.AsValueEnumerable()` on the concrete collection**, not on an `IEnumerable<T>`- or `IList<T>`-typed reference — the struct enumerator path depends on ZLinq seeing the backing type, and an interface-typed source gives that away before the first operator runs.
4. **Eliminate capturing lambdas in the predicates, because ZLinq does not make them free** — `Where(e => e.IsAlive)` captures nothing and is cached once, while `Where(e => e.Health < threshold)` allocates a closure per call for the captured local. This is the most common reason a converted chain still shows allocation; pass the value through an operator overload that takes state, or restructure so the predicate captures nothing.
5. **Do not end the chain in `.ToArray()` or `.ToList()` inside the hot path** — materialization allocates the result collection, so a chain converted to ZLinq and then materialized has moved the allocation rather than removed it. Consume with `foreach`, an aggregate, or a single-element operator instead.
6. **Consume the chain fully inside the synchronous method that created it** — `ValueEnumerable<T>` is a stack-bound value type, so it cannot be stored in a field, captured in a closure, or held across an `await`. If another scope needs the result, materialize deliberately at that boundary and accept the allocation there.
7. **Prefer a plain loop when the chain is long and the collection is small** — per `performance-and-algorithms.md`'s small-N reasoning, struct copying across many chained operators has a real constant cost that can lose to an obvious loop, and KISS in `coding-principles.md` favours the loop when the readability argument is weak.
8. **Re-profile and confirm the specific site reads 0B** before claiming the allocation is gone — the library's benchmarks say nothing about this call site, and steps 4 and 5 fail silently without an after-capture.
9. **Ask for a capture when none exists and the path is not plainly per-frame** — without one there is no way to tell a real conversion from churn.

## 5. Specific goals / tasks this skill performs
- Convert a profiler-attributed `System.Linq` chain in a hot path to `.AsValueEnumerable()` operators.
- Remove closure allocations from predicates that a struct-enumerable conversion leaves behind.
- Keep chains free of in-path materialization so the removed allocation does not reappear at the end.
- Write allocation-free composition inside `Game.Core.*` without a `UnityEngine` dependency.
- Confirm by measurement that the converted site allocates nothing.
- Out of scope: non-hot-path code where `System.Linq` already applies, container and data-structure selection (`unity-collections`, per `performance-and-algorithms.md`), Burst job bodies (`unity-job-system-and-burst`), string construction (`zstring-zero-allocation-strings`).

## 6. Output format
```
## ZLinq Work — <call site>
- Location: <file:line> — hot path confirmed by <Profiler capture>
- Data structure: <collection type> — confirmed appropriate before conversion
- Before: System.Linq chain — <measured GC Alloc per call>
- After: .AsValueEnumerable() — <operators used>
- Source typing: concrete <List<T>/array/Span<T>> — not interface-typed
- Closures: no capturing lambda in the chain — confirmed | <captured value, and how it was removed>
- Termination: foreach / aggregate / single-element operator — no in-path .ToArray()/.ToList()
- Consumption: fully consumed in <method> — not stored, captured, or awaited
- Measured result: <Profiler GC Alloc, before vs. after>
- Layer: Game.Core.* / Game.Client.*
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <other allocating sites in the same path this did not address>
- Latent concerns: <what holds only at the current collection size or operator count>
- Future remediation: <the trigger for each — an added operator, a captured value, growth past small N>
```

## 7. Examples
**Example 1**
- Input: `Update()` runs `enemies.Where(e => e.IsAlive).OrderBy(e => e.DistanceToPlayer).FirstOrDefault()` every frame against a `List<Enemy>` field, showing a per-frame allocation.
- Output: converted to `enemies.AsValueEnumerable().Where(...).OrderBy(...).FirstOrDefault()` on the concrete `List<Enemy>`. Both lambdas capture nothing, so no closure is created per call. The chain ends in a single-element operator rather than materializing. Re-profiled: 0B at that site.

**Example 2**
- Input: an editor inspector filters a project asset list with `System.Linq` during a one-time import step.
- Output: declined. This is exactly the non-hot-path tooling case `coding-principles.md` permits plain `System.Linq` for, and the import runs once. Converting it would add an unfamiliar entry point and a `ref struct` consumption constraint to code with no measured problem.

**Example 3**
- Input: a converted chain still shows a per-frame allocation after switching to `.AsValueEnumerable()`.
- Output: two causes found, both invisible from the operator names. The predicate captured a local `range` value, allocating a closure per call — hoisted into a field so the lambda captures nothing. The chain also ended in `.ToList()` feeding a `foreach`, which allocated the list every frame — replaced by iterating the chain directly. Only after both fixes did the site read 0B, which is why §4 requires the after-capture rather than trusting the conversion.

## 8. Edge cases & guardrails
- Never convert a chain without a Profiler capture attributing an allocation to it — an unmeasured conversion is churn with a confident-sounding justification.
- Never treat a ZLinq conversion as a fix for the wrong data structure — the complexity problem survives the allocation fix.
- Never leave a capturing lambda in a converted chain, per §4 — the closure allocates per call no matter how the sequence is enumerated.
- Never end a converted chain in `.ToArray()` or `.ToList()` inside the hot path — that reintroduces the allocation at the last operator.
- Never store a `ValueEnumerable<T>` in a field, capture it, or hold it across an `await` — it is stack-bound; materialize at that boundary instead.
- Never open a chain on an interface-typed source — the struct enumerator path is lost before the first operator.
- Never use ZLinq operators inside a `[BurstCompile]` job body — that is a different toolchain with different constraints.
- Never claim the allocation is gone without an after-capture showing 0B at that site.
