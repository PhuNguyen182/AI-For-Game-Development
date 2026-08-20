---
name: zstring-zero-allocation-strings
description: >
  Technique for allocation-free string building via ZString —
  `ZString.Format`/`ZString.Concat` (no boxing, no intermediate `.ToString()`
  calls) and `ZString.CreateStringBuilder()`'s struct-based
  `Utf16ValueStringBuilder`, plus its `TextMeshProExtensions`
  (`SetText`/`SetTextFormat`) that write directly into TMP's buffer with no
  string allocation at all. ZString has no `UnityEngine` dependency for its
  core API, so it's usable in `Game.Core.*` as well as `Game.Client.*`. Use
  this specifically for hot-path or per-frame string construction — a
  repeatedly-updated UI label, per-frame debug text, log formatting inside a
  loop — where `performance-and-algorithms.md` already calls for
  `StringBuilder`/careful string handling instead of allocating
  interpolation/concatenation. Do not use this for one-off, non-hot-path
  string formatting — `performance-and-algorithms.md` already permits plain
  string interpolation there, and reaching for `ZString.Format` on a
  one-time string is unnecessary ceremony (KISS). Do not use this as a
  reason to update UI text unconditionally every frame — pair it with
  `r3-reactive-extensions`'s "only update on actual change" guidance, since
  a zero-allocation format call repeated needlessly every frame is still
  wasted work, just without the GC cost. Do not use this for anything other
  than string/text construction — it is not a general serialization tool;
  binary data crossing a boundary is `memorypack-serialization`'s territory.
---

# ZString — Zero-Allocation String Building

Source: [github.com/Cysharp/ZString](https://github.com/Cysharp/ZString).

## 1. Objective
Build strings in a hot or per-frame path (a repeatedly-updated HUD label, per-frame debug overlay text) without the boxing and intermediate allocations plain string interpolation/`+`-concatenation would cost — without applying it where a one-off string is already fine, and without letting "it's zero-allocation now" excuse an unconditional per-frame update that shouldn't be happening at all.

## 2. Role
Act as the allocation-conscious string-building specialist for the client track: the tool reached for once a specific hot-path string construction site has been identified as an allocation source, per `performance-and-algorithms.md`'s Scripting & GC section.

## 3. When to invoke this skill
- A `Text`/TMP label, debug overlay, or log line is rebuilt every frame (or very frequently) using string interpolation/`+`-concatenation and is showing up as a GC allocation source.
- Building a formatted string inside a loop (appending per-iteration) where a plain `StringBuilder` would still allocate its own backing buffer growth — `ZString.CreateStringBuilder()`'s struct-based builder rents from a pool instead.
- Writing directly to a TextMeshPro label via `SetText`/`SetTextFormat` (`TextMeshProExtensions`) to skip string allocation entirely for UI text that updates often.
- Negative trigger: a one-off, non-hot-path string (a one-time log message, an editor tool label, a config-driven message built once) — plain interpolation already satisfies `performance-and-algorithms.md` there; don't add ceremony for no measured benefit.
- Negative trigger: the actual problem is updating UI unconditionally every frame regardless of whether the value changed — fix that with `r3-reactive-extensions`'s "update only on change" pattern first; a cheaper format call that still runs every frame for no reason is still wasted work.
- Negative trigger: serializing structured/binary data — that's `memorypack-serialization`; ZString is text/string construction only.

## 4. How to use this skill
1. **Confirm the call site is actually hot** before converting it — per `performance-and-algorithms.md`'s Verification rule, this is a targeted fix for a measured allocation source, not a default replacement for every string operation in the codebase.
2. **Use `ZString.Format`/`ZString.Concat` for a single formatted/concatenated result** instead of string interpolation or `+`-chains in that hot path — these avoid boxing struct arguments and the intermediate `.ToString()` calls interpolation compiles down to.
3. **Use `ZString.CreateStringBuilder()` for building up a string across a loop** instead of `System.Text.StringBuilder` in a hot path — its struct-based builder rents pooled buffers rather than allocating and growing its own backing array; dispose it (it implements `IDisposable`) once the built string is materialized.
4. **Write directly through `TextMeshProExtensions.SetText`/`SetTextFormat` for frequently-updated TMP labels** to skip string materialization entirely, when the label's content is going straight to display and doesn't need to exist as a `string` for any other purpose.
5. **Update text only when the underlying value actually changed** — pair every ZString-based UI update with the "only update on change" rule from `performance-and-algorithms.md`'s Scripting & GC section (`r3-reactive-extensions`'s `DistinctUntilChanged` is a natural way to gate this) rather than calling a zero-allocation formatter unconditionally every frame anyway.
6. **Verify with the Profiler**, per `performance-and-algorithms.md`'s Verification rule — confirm the specific call site's GC alloc column actually reads 0B after the conversion, not just that ZString's own benchmarks claim it should.

## 5. Specific goals / tasks this skill performs
- Converting a profiler-flagged, frequently-updated string construction site from interpolation/`+`-concatenation to `ZString.Format`/`ZString.Concat`.
- Replacing `System.Text.StringBuilder` with `ZString.CreateStringBuilder()` in a loop-heavy hot path.
- Wiring `TextMeshProExtensions.SetText`/`SetTextFormat` for a frequently-updated TMP label to skip string allocation entirely.
- Auditing that a converted UI update site is still gated on "value actually changed," not called unconditionally every frame.
- Out of scope: one-off/non-hot-path string formatting (plain interpolation is fine), binary/structured serialization (`memorypack-serialization`), the "should this update every frame" decision itself (`r3-reactive-extensions`).

## 6. Output format
```
## ZString Work — <call site>
- Location: <file:line, hot path confirmed>
- Before: string interpolation / + concatenation / StringBuilder (allocates)
- After: ZString.Format / ZString.Concat / ZString.CreateStringBuilder / TextMeshProExtensions.SetText
- Update gating: confirmed only runs when the underlying value changed — <mechanism>
- Measured result: <Profiler GC Alloc delta, before vs. after>
- Known limitations: <...>
```

## 7. Examples
**Example 1**
- Input: an FPS counter's TMP label is updated every frame with `text.text = $"FPS: {fps:F1}"`, showing a small but constant per-frame allocation.
- Output: converted to `label.SetTextFormat("FPS: {0:F1}", fps)` via `TextMeshProExtensions`, gated behind a check that only calls it when the displayed integer FPS value actually changed frame-to-frame; re-profiled and confirmed 0B GC Alloc for the update.

**Example 2**
- Input: an editor tool prints a one-time summary string when an asset import finishes.
- Output: left as plain string interpolation — a one-time, non-hot-path message is exactly the case `performance-and-algorithms.md` already permits; converting it to `ZString.Format` would add ceremony for no measured benefit.

## 8. Edge cases & guardrails
- Never convert a one-off, non-hot-path string to ZString without a measured reason — that's unjustified complexity for no benefit (KISS).
- Never leave a `ZString.CreateStringBuilder()` instance undisposed once the built string is materialized — it rents pooled resources that need returning.
- Never treat "now zero-allocation" as license to skip the "only update on change" rule — an unconditional per-frame call is still wasted work even without GC cost.
- Never use ZString for structured/binary data — that's `memorypack-serialization`'s job.
- Never claim the allocation is gone without a Profiler measurement confirming the specific call site's GC Alloc column.
