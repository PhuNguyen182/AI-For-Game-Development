# Unsafe Collections & Aliasing — Shared Allocations

Source: [Collections overview](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/collections-overview.html), [Aliasing allocators](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/allocator-aliasing.html).
Covers: SKILL.md §4 — **"Reach for an `Unsafe-` variant only for a specific, justified low-level case"**, **"Use aliasing deliberately, and name the owner"**.

Two ways to give up a guarantee in exchange for overhead: `Unsafe-` variants
drop the safety checks, and an alias drops independent ownership of an
allocation. Both are correct only with a stated reason; the failure mode of
each is silent, not a compile error.

## Native- vs Unsafe-

| Aspect | Effect | Use when | Source |
|---|---|---|---|
| Safety checks | `Native-` reports use-after-dispose and cross-thread races; `Unsafe-` reports nothing | Keep `Native-` unless a measurement shows the checks are the bottleneck | [Collections overview](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/collections-overview.html) |
| Namespace | `Unsafe-` types live in `Unity.Collections.LowLevel.Unsafe` | The `using` itself is the review signal that a justification is owed | [Collections overview](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/collections-overview.html) |
| Nesting | Only an `Unsafe-` collection may be the inner type of another collection | A container of containers is genuinely required | [Collections overview](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/collections-overview.html) |

## Aliasing rules

| Rule | Effect | Use when | Source |
|---|---|---|---|
| An alias owns nothing | It shares the parent's existing allocation instead of making its own | A second view is needed without a second allocation | [Aliasing allocators](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/allocator-aliasing.html) |
| Only the original is disposed | Calling `Dispose()` on an alias is wrong; disposing the parent covers every alias | Auditing disposal paths — an alias is the sole exemption | [Aliasing allocators](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/allocator-aliasing.html) |
| Writes propagate | A write through any alias is visible through all of them and the parent | Two views must stay in sync by construction | [Aliasing allocators](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/allocator-aliasing.html) |
| Parent disposal invalidates | Every alias becomes unusable the instant the parent is disposed | Reasoning about lifetime order between the two | [Aliasing allocators](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/allocator-aliasing.html) |

## Common alias shapes

| Shape | What it decides | Source |
|---|---|---|
| Type conversion | Reinterpret the same bytes as a different collection type without copying | [Aliasing allocators](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/allocator-aliasing.html) |
| Subrange view | Expose part of a larger allocation to a consumer that must not see the rest | [Aliasing allocators](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/allocator-aliasing.html) |
| Element reinterpretation | Read the same bytes as a different element type — sizes must divide evenly | [Aliasing allocators](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/allocator-aliasing.html) |
