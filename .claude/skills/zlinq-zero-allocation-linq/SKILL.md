---
name: zlinq-zero-allocation-linq
description: "ZLinq allocation-free LINQ: AsValueEnumerable, struct operators, span sources, tree traversal. Use when LINQ readability is wanted in hot paths."
user-invocable: false
---

# ZLinq

Not for: code outside a hot path (plain `System.Linq`, `csharp-standards` → `coding-principles.md` `var` and LINQ), container choice (`unity-collections`), `[BurstCompile]` job bodies (`unity-job-system-and-burst`), string building (`zstring-zero-allocation-strings`).

## Steps
Usable in `Game.Core.*` (no UnityEngine dependency).

1. **Measure first** — convert only a chain the Profiler attributes an allocation to (`csharp-standards` → `performance-and-algorithms.md` Verification). No capture and the path is not plainly per-frame → ask for one.
2. **Check the collection type before the query** — a zero-allocation scan of the wrong structure is still wrong; fix the structure first (`performance-and-algorithms.md` Data structure selection).
3. **Open with `.AsValueEnumerable()` on the concrete collection** (`List<T>`, array, `Span<T>`), never an `IEnumerable<T>`/`IList<T>`-typed reference — that loses the struct-enumerator path before the first operator.
4. **Remove capturing lambdas** — `Where(e => e.IsAlive)` is cached once; `Where(e => e.Health < threshold)` allocates a closure per call. Use an operator overload that takes state, or restructure so the predicate captures nothing. This is the usual reason a converted chain still allocates.
5. **No `.ToArray()` / `.ToList()` in the hot path** — it moves the allocation to the last operator. End in `foreach`, an aggregate or a single-element operator.
6. **Consume fully inside the synchronous method that created it** — `ValueEnumerable<T>` is stack-bound: no field, closure or `await`. Materialize deliberately at a boundary and accept the allocation there.
7. **Long chain over a small collection → prefer a plain loop** — struct copying across many operators has a constant cost (`performance-and-algorithms.md` small-N reasoning; KISS in `coding-principles.md`).
8. **Re-profile and confirm the site reads 0B** — steps 4 and 5 fail silently otherwise.

## Never
- Use ZLinq operators inside a `[BurstCompile]` job body.

## Output
```
## ZLinq Work — <call site>
- Location: <file:line> — hot path confirmed by <Profiler capture>
- Data structure: <collection type> — confirmed appropriate
- Before: System.Linq chain — <GC Alloc per call>
- After: .AsValueEnumerable() — <operators>
- Source typing: concrete <List<T>/array/Span<T>>
- Closures: none captured | <captured value, how removed>
- Termination: foreach / aggregate / single-element — no in-path .ToArray()/.ToList()
- Consumption: fully consumed in <method>
- Measured result: <GC Alloc before vs after>
- Layer: Game.Core.* / Game.Client.*
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- A chain still allocates after `.AsValueEnumerable()` → two causes: the predicate captured a local `range` (hoisted into a field) and the chain ended in `.ToList()` feeding a `foreach` (iterate the chain directly). Only then 0B.
