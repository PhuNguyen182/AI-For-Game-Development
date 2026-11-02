---
name: zlinq-zero-allocation-linq
description: "ZLinq: AsValueEnumerable, struct operators, span sources, tree traversal. Use when LINQ is wanted in hot paths."
user-invocable: false
---

# ZLinq

- **Not for:** code outside a hot path (plain `System.Linq`, `csharp-standards` → `coding-principles.md` `var` and LINQ).
- **Not for:** container choice (`unity-collections`).
- **Not for:** `[BurstCompile]` job bodies (`unity-job-system-and-burst`).
- **Not for:** string building (`zstring-zero-allocation-strings`).
- **Layer:** usable in a Core assembly (no UnityEngine dependency).

## Steps
1. **Measure first:** convert only a chain the Profiler attributes an allocation to (`csharp-standards` → `performance-and-algorithms.md` Verification).
   - **No capture and the path is not plainly per-frame:** `Blocked` naming the capture needed.
2. **Check the collection type before the query:** a zero-allocation scan of the wrong structure is still wrong; fix the structure first (`performance-and-algorithms.md` Data structure selection).
3. **Open with `.AsValueEnumerable()` on the concrete collection (`List<T>`, array, `Span<T>`):** never an `IEnumerable<T>`/`IList<T>`-typed reference.
   - **Why:** that loses the struct-enumerator path before the first operator.
4. **Remove capturing lambdas:** `Where(e => e.IsAlive)` is cached once; `Where(e => e.Health < threshold)` allocates a closure per call.
   - **Fix:** hoist the value into a non-capturing form (a static predicate over precomputed data), or fall back to a plain `for` loop.
   - **Limit:** ZLinq has no state-passing overloads.
   - **Why it matters:** this is the usual reason a converted chain still allocates.
5. **No `.ToArray()` / `.ToList()` in the hot path:** it moves the allocation to the last operator.
   - **Instead:** end in `foreach`, an aggregate or a single-element operator.
6. **Consume fully inside the synchronous method that created it:** `ValueEnumerable<T>` is stack-bound: no field, closure or `await`.
   - **Boundary:** materialize deliberately at a boundary and accept the allocation there.
7. **Long chain over a small collection → prefer a plain loop:** struct copying across many operators has a constant cost.
   - **See:** `performance-and-algorithms.md` small-N reasoning; KISS in `coding-principles.md`.
8. **Re-profile and confirm the site reads 0B:** steps 4 and 5 fail silently otherwise.

## Never
- **ZLinq in Burst jobs:** using ZLinq operators inside a `[BurstCompile]` job body.

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
- Layer: Core / Client
```

## Example
- **A chain still allocates after `.AsValueEnumerable()`:** two causes — the predicate captured a local `range` and the chain ended in `.ToList()` feeding a `foreach`.
  - **Fix:** hoisted `range` into a field and iterated the chain directly; only then 0B.
