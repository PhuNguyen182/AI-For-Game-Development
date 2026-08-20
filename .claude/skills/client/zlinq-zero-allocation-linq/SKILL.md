---
name: zlinq-zero-allocation-linq
description: >
  Technique for allocation-free LINQ-style queries via ZLinq's
  `AsValueEnumerable()` and struct-based `ValueEnumerable<T>` operators
  (`Where`, `Select`, `Sum`, etc.), usable in both `Game.Core.*` and
  `Game.Client.*` since ZLinq itself has no `UnityEngine` dependency. This
  is specifically how to satisfy `coding-principles.md`'s and
  `performance-and-algorithms.md`'s "never use LINQ inside a hot path" rule
  when the readability of a LINQ-style query chain is still wanted in
  `Update()`/`FixedUpdate()`/per-tick code — it is not a general license to
  reintroduce query chains everywhere. Do not use this in ordinary,
  non-performance-critical code (editor tooling, one-off setup, SDK/config
  code) where plain `System.Linq` is already explicitly allowed by
  `coding-principles.md` — reaching for `AsValueEnumerable()` there is
  unnecessary ceremony for no measured benefit (KISS). Do not use this as a
  substitute for actually picking the right data structure for a problem —
  that's `performance-and-algorithms.md`'s Data structure selection section;
  a zero-allocation query over the wrong collection type is still the wrong
  collection type. Do not use this inside a Burst-compiled job — Burst has
  its own compilation constraints and `unity-job-system-and-burst`/
  `unity-collections` own that territory; ZLinq targets ordinary managed C#
  method bodies, not Burst-compiled job structs.
---

# ZLinq — Zero-Allocation LINQ

Source: [github.com/Cysharp/ZLinq](https://github.com/Cysharp/ZLinq).

## 1. Objective
Let LINQ-style, readable query chains run inside a hot path (`Update()`, per-tick Shared Core evaluation, a per-frame gameplay loop) without the per-call allocation `System.Linq`'s `IEnumerable<T>`-based operators and enumerator boxing would otherwise cost — without reaching for it where plain `System.Linq` is already fine, and without treating it as a substitute for choosing the right data structure in the first place.

## 2. Role
Act as the allocation-conscious-LINQ specialist for the client track: the tool reached for specifically when a hot path wants a query chain's readability but `performance-and-algorithms.md` forbids `System.Linq`'s allocation there.

## 3. When to invoke this skill
- A hot path (`Update()`/`FixedUpdate()`/`LateUpdate()`, or a per-tick Shared Core evaluation) currently uses `System.Linq` (or would read more clearly with a query chain than a hand-rolled loop) and needs to stop allocating per call.
- A `Game.Core.*` algorithm needs LINQ-style composition (filter/transform/aggregate) without introducing a `UnityEngine` dependency — ZLinq is one of the few libraries in this stack that's safe there.
- Converting an existing `System.Linq` call chain in a profiler-flagged allocation hotspot to `.AsValueEnumerable()...` and confirming the allocation is actually gone.
- Negative trigger: ordinary non-performance-critical code (editor tooling, one-off setup/config code) — `coding-principles.md` already allows plain `System.Linq` there; don't add `AsValueEnumerable()` ceremony for no measured benefit.
- Negative trigger: the real problem is data-structure choice (e.g. a linear scan over a `List<T>` where a `Dictionary<TKey,TValue>` lookup is actually needed) — fix the structure per `performance-and-algorithms.md` first; a zero-allocation query over the wrong structure is still the wrong structure.
- Negative trigger: inside a Burst-compiled job — that's `unity-job-system-and-burst`/`unity-collections` territory with its own compilation and container constraints; ZLinq targets ordinary managed method bodies.

## 4. How to use this skill
1. **Confirm the call site is actually a hot path** before reaching for this — per `performance-and-algorithms.md`'s Verification section, "no LINQ in hot paths" is the existing rule this skill exists to satisfy, not a reason to sprinkle `AsValueEnumerable()` everywhere by default.
2. **Call `.AsValueEnumerable()` at the start of the chain**, then compose with the same operator names (`Where`, `Select`, `Sum`, `OrderBy`, etc.) — the query reads identically to `System.Linq`, so the change is mechanical once the entry point is right.
3. **Know that `ValueEnumerable<T>` is a `ref struct`** on modern .NET targets and cannot be stored in a field, captured in a closure, or returned across an `async` boundary — consume it fully within the same synchronous method it's created in; if a caller needs the result stored or handed elsewhere, materialize it (`.ToArray()`/`.ToList()`) at that point instead of trying to hold the `ValueEnumerable<T>` itself.
4. **Prefer the concrete source type ZLinq optimizes for** (`Array`, `List<T>`, `Span<T>`, `Dictionary<TKey,TValue>`, etc.) over an `IEnumerable<T>`-typed reference at the call site — the zero-allocation path depends on ZLinq knowing the concrete backing type; an interface-typed source loses some of that optimization.
5. **Verify the allocation is actually gone**, per `performance-and-algorithms.md`'s Verification rule — a Profiler capture (Allocation Tracking) showing 0B for the converted call site, not an assumption based on the library's claims alone.
6. **Don't chain an excessively long query over a very small collection** and expect a win — per the same file's "small-N structures" reasoning, struct-copying overhead across many chained operators can lose to a plain loop at small N; measure rather than assume ZLinq always wins.

## 5. Specific goals / tasks this skill performs
- Converting a profiler-flagged `System.Linq` allocation hotspot in a hot path to `.AsValueEnumerable()`-based ZLinq operators.
- Writing allocation-free query composition inside `Game.Core.*` algorithms that need it.
- Verifying via Profiler Allocation Tracking that a conversion actually removed the allocation.
- Out of scope: non-hot-path code where plain `System.Linq` already applies, data-structure selection itself (`performance-and-algorithms.md`), Burst-compiled job bodies (`unity-job-system-and-burst`/`unity-collections`).

## 6. Output format
```
## ZLinq Work — <call site>
- Location: <file:line, hot path confirmed — Update/FixedUpdate/per-tick evaluation>
- Before: System.Linq chain (allocates per call)
- After: AsValueEnumerable() chain — operators used
- Source type: <concrete collection type ZLinq is optimizing over>
- Consumption: fully consumed synchronously within <method> — not stored/captured
- Measured result: <Profiler Allocation Tracking delta, before vs. after>
- Known limitations: <...>
```

## 7. Examples
**Example 1**
- Input: `Update()` does `enemies.Where(e => e.IsAlive).OrderBy(e => e.DistanceToPlayer).FirstOrDefault()` every frame, showing up as a per-frame GC allocation in the Profiler.
- Output: converted to `enemies.AsValueEnumerable().Where(e => e.IsAlive).OrderBy(e => e.DistanceToPlayer).FirstOrDefault()` against the concrete `List<Enemy>` backing field; re-profiled and confirmed the per-frame allocation dropped to 0B.

**Example 2**
- Input: an editor-only inspector tool filters a list of assets with `System.Linq` for a one-time import step.
- Output: declined to convert — this is exactly the non-performance-critical, one-off tooling case `coding-principles.md` already permits plain `System.Linq` for; converting it would be unnecessary ceremony with no measured benefit.

## 8. Edge cases & guardrails
- Never reach for ZLinq outside a confirmed hot path — that's solving a problem that doesn't exist there, per KISS.
- Never store a `ValueEnumerable<T>` in a field, capture it in a closure, or hold it across an `await` — it's a `ref struct`; materialize (`.ToArray()`/`.ToList()`) before doing any of that.
- Never treat a ZLinq conversion as a substitute for fixing the underlying data-structure choice — verify the structure is right first.
- Never claim an allocation win without a Profiler measurement — per `performance-and-algorithms.md`'s Verification rule.
- Never use ZLinq operators inside a `[BurstCompile]` job body — that's outside this library's target and `unity-job-system-and-burst`'s/`unity-collections`'s territory instead.
