---
name: zstring-zero-allocation-strings
description: >
  ZString — allocation-free string building: `ZString.Format` and
  `ZString.Concat` with no boxing and no intermediate `.ToString()`, the
  struct-based `ZString.CreateStringBuilder()` (`Utf16ValueStringBuilder`,
  `Utf8ValueStringBuilder`) renting pooled buffers, and `TextMeshProExtensions`
  (`SetText`, `SetTextFormat`) writing straight into TMP's own char buffer with
  no string materialized at all. The core API has no `UnityEngine` dependency,
  so it works in `Game.Core.*` as well as `Game.Client.*`. Use on a
  profiler-confirmed per-frame or hot-path string construction site.
  Not for: one-off formatting outside a hot path (plain interpolation, per `coding-principles.md`), whether the UI should update at all (`r3-reactive-extensions`), binary serialization (`memorypack-serialization`), query chains (`zlinq-zero-allocation-linq`).
---

# ZString — Zero-Allocation String Building

## 1. Objective
Remove the boxing and intermediate allocations that string interpolation and `+`-concatenation cost at a measured hot-path construction site — without applying it where a one-off string was already fine, and without letting "it allocates nothing now" excuse an update that should not be running every frame in the first place.

## 2. Role
Act as the allocation-conscious string-building specialist for the client track — the tool reached for after a specific construction site has been identified as an allocation source, per `performance-and-algorithms.md`'s Scripting & GC section, never as a blanket replacement for string handling across the codebase.

## 3. When to invoke this skill
- A TMP or `Text` label, debug overlay, or log line is rebuilt every frame with interpolation or `+`-concatenation and shows a per-frame GC allocation in the Profiler.
- A string is assembled across a loop, where `System.Text.StringBuilder` still allocates its own backing array and grows it.
- Frequently-updated TMP text can be written straight into the component's buffer, making the intermediate `string` unnecessary entirely.
- A `Game.Core.*` path needs formatted output without pulling in a `UnityEngine` dependency.
- Negative trigger: a one-off string outside a hot path — a single log message, an editor tool label, a message built once at startup. `coding-principles.md`'s Performance discipline section already permits plain interpolation there, and converting it is ceremony for no measured gain.
- Negative trigger: the real defect is updating UI unconditionally every frame regardless of whether the value changed — that decision belongs to `r3-reactive-extensions`, and a cheaper call that still runs pointlessly is still waste.
- Negative trigger: turning structured data into bytes — that is `memorypack-serialization`; ZString builds text, not wire formats.
- Negative trigger: an allocating query chain in the same hot path — that is `zlinq-zero-allocation-linq`, a separate conversion from the string it may feed.

## 4. How to use this skill
1. **Measure the call site before converting anything**, per `performance-and-algorithms.md`'s Verification section — this is a targeted fix for an allocation the Profiler actually attributed to this line, and an unmeasured conversion trades readability for a benefit nobody confirmed.
2. **Ask whether the call should run at all before making it cheaper** — if the underlying value changes a few times a minute but the label rebuilds sixty times a second, gating the update on an actual change removes almost every call, and the survivors may not need converting. Fixing frequency first is strictly larger than fixing cost, per the same file's "only update UI when the value changed" rule.
3. **Use `ZString.Format` or `ZString.Concat` for a single formatted result** in place of interpolation or a `+`-chain — these avoid boxing the struct arguments and skip the intermediate `.ToString()` calls interpolation compiles down to.
4. **Build across a loop with `using var sb = ZString.CreateStringBuilder()`, never without the `using`** — the builder is a struct renting pooled buffers, so an undisposed instance leaks the rental rather than being collected. Per `coding-principles.md`'s Exception handling section, the `using` declaration is the required form here, not a manual `try/finally`.
5. **Write frequently-updated TMP labels through `TextMeshProExtensions.SetText` or `SetTextFormat`** — these write into the component's own char buffer, so no `string` is materialized at all, which beats a zero-allocation format followed by a string assignment.
6. **Match an arity-specific `SetTextFormat` overload rather than passing a long argument list** — the fixed-arity overloads exist precisely to avoid a `params` array, and overflowing them reintroduces the allocation the call was chosen to remove.
7. **Reach for `Utf8ValueStringBuilder` when the destination consumes bytes** — a log sink, a network text payload, or a file write — so the UTF-16 to UTF-8 conversion never happens at all.
8. **Keep a builder inside the synchronous method that created it** — do not store it in a field, capture it in a closure, or hold it across an `await`. Materialize with `.ToString()` at the point another scope needs the result.
9. **Re-profile and confirm the specific call site reads 0B** before claiming the allocation is gone, per `performance-and-algorithms.md`'s Verification section — the library's own benchmarks are not evidence about this call site.
10. **Ask for a profiler capture when none exists and the site is not obviously per-frame** — converting on suspicion produces unfalsifiable claims and churn in code that was already correct.

## 5. Specific goals / tasks this skill performs
- Convert a profiler-attributed per-frame string construction from interpolation or concatenation to `ZString.Format`/`ZString.Concat`.
- Replace `System.Text.StringBuilder` with a pooled `ZString.CreateStringBuilder()` in a loop-heavy hot path.
- Wire `TextMeshProExtensions.SetText`/`SetTextFormat` so a frequently-updated label materializes no string.
- Route byte-destined output through `Utf8ValueStringBuilder` instead of building UTF-16 and converting.
- Confirm a converted UI site is still gated on an actual value change rather than called unconditionally.
- Out of scope: non-hot-path formatting (plain interpolation is already permitted), the "should this update at all" decision (`r3-reactive-extensions`), binary serialization (`memorypack-serialization`), query-chain allocation (`zlinq-zero-allocation-linq`).

## 6. Output format
```
## ZString Work — <call site>
- Location: <file:line> — hot path confirmed by <Profiler capture>
- Before: interpolation / + concatenation / StringBuilder — <measured GC Alloc>
- Update frequency fix: gated on value change — <mechanism> | already gated | not applicable
- After: ZString.Format / ZString.Concat / CreateStringBuilder / SetText / SetTextFormat
- Builder disposal: `using` declaration — confirmed | no builder used
- Encoding: Utf16ValueStringBuilder / Utf8ValueStringBuilder — <why>
- Measured result: <Profiler GC Alloc, before vs. after>
- Layer: Game.Core.* / Game.Client.*
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what the conversion did not cover — other allocating sites in the same path>
- Latent concerns: <what holds only at the current argument count, text length, or update frequency>
- Future remediation: <the trigger for each — an added format argument, a longer string, a frequency change>
```

## 7. Examples
**Example 1**
- Input: an FPS counter's TMP label is assigned `$"FPS: {fps:F1}"` every frame, showing a small constant per-frame allocation in the Profiler.
- Output: converted to `label.SetTextFormat("FPS: {0:F1}", fps)` through `TextMeshProExtensions`, using the single-argument overload so no `params` array is created, and gated to fire only when the displayed value actually changed. Re-profiled: the site reads 0B GC Alloc and now runs a few times a second instead of every frame.

**Example 2**
- Input: "convert the score label's per-frame interpolation to `ZString.Format`, it is allocating."
- Output: declined as framed, and fixed differently. The Profiler confirmed the allocation, but the score changes a handful of times per match while the label rebuilt every frame — so the defect was frequency, not cost. Gating the assignment on an actual score change removed effectively all the calls; the few survivors are one-off strings that plain interpolation already covers, so no ZString conversion was needed at all.

**Example 3**
- Input: a debug overlay concatenates one line per tracked entity, roughly forty per frame, through `StringBuilder`.
- Output: converted to `using var sb = ZString.CreateStringBuilder();` with per-entity `sb.AppendFormat(...)` inside the loop, materialized once at the end. The `using` declaration is what returns the pooled buffer; without it the rental leaks every frame. Re-profiled to confirm the builder's own growth allocations are gone, and the overlay was additionally gated behind an editor-only flag so the whole path is absent from shipped builds.

## 8. Edge cases & guardrails
- Never convert a string site without a Profiler capture attributing an allocation to it — unmeasured conversions cost readability and prove nothing.
- Never optimize the cost of a call that should not be running, per §4 — gate on value change first, then convert what remains.
- Never create a `ZString.CreateStringBuilder()` without a `using` — the pooled buffer is rented, and an undisposed builder leaks it on every pass.
- Never hold a builder in a field, a closure, or across an `await` — materialize with `.ToString()` before the value leaves the method.
- Never overflow the fixed-arity `SetTextFormat` overloads — the `params` fallback reintroduces exactly the allocation being removed.
- Never use ZString for structured or binary data — that is `memorypack-serialization`'s territory.
- Never claim a zero-allocation result without the after-capture showing 0B at that specific site.
