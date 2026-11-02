---
name: zstring-zero-allocation-strings
description: "ZString: Format, Concat, Utf16/Utf8 builders, TMP SetText. Use when building strings per frame or tick."
user-invocable: false
---

# ZString

- **Not for:** one-off formatting outside a hot path (plain interpolation, `csharp-standards` → `coding-principles.md`).
- **Not for:** whether the UI should update at all (`r3-reactive-extensions`).
- **Not for:** binary serialization (`memorypack-serialization`).
- **Not for:** allocating query chains (`zlinq-zero-allocation-linq`).
- **Layer:** usable in Core (no UnityEngine dependency); `TextMeshProExtensions` is Client code only.

## Steps
1. **Measure first:** convert only a site the Profiler attributes an allocation to (`csharp-standards` → `performance-and-algorithms.md` Verification).
   - **No capture and the site is not plainly per-frame:** `Blocked` naming the capture needed.
2. **Cut frequency before cost:** a label rebuilt 60×/s for a value that changes a few times a minute is fixed by gating on value change (`performance-and-algorithms.md` Scripting & GC).
   - **Survivors:** the sites that remain may need no conversion.
3. **Single result:** `ZString.Format` / `ZString.Concat` instead of interpolation or `+` (no boxing, no intermediate `ToString()`).
4. **Loop:** `using var sb = ZString.CreateStringBuilder()` — the `using` returns the pooled buffer; without it every pass leaks the rental.
5. **TMP labels:** `TextMeshProExtensions.SetText` / `SetTextFormat` write into the component's char buffer, so no `string` is created.
   - **Overloads:** stay within the fixed-arity `SetTextFormat` overloads; overflowing falls back to a `params` array and reintroduces the allocation.
6. **Byte destination (log sink, network text, file):** `Utf8ValueStringBuilder`, skipping UTF-16→UTF-8 conversion.
7. **Keep the builder inside the synchronous method that created it:** no field, closure or `await`; `.ToString()` where another scope needs the result.
8. **Re-profile and confirm the site reads 0B:** library benchmarks are not evidence about this call site.

## Never
- **Structured or binary data:** using ZString for it.

## Output
```
## ZString Work — <call site>
- Location: <file:line> — hot path confirmed by <Profiler capture>
- Before: interpolation / + / StringBuilder — <measured GC Alloc>
- Update frequency: gated on value change — <mechanism> | already gated | n/a
- After: ZString.Format / Concat / CreateStringBuilder / SetText / SetTextFormat
- Builder disposal: `using` declaration — confirmed | no builder used
- Encoding: Utf16ValueStringBuilder / Utf8ValueStringBuilder — <why>
- Measured result: <GC Alloc before vs after>
- Layer: Core / Client
```

## Example
- **"Convert the score label's per-frame interpolation to `ZString.Format`, it allocates":** fixed differently — the score changes a few times per match while the label rebuilt every frame.
  - **Done instead:** gating on an actual change removed nearly all calls, and the survivors need no conversion.
