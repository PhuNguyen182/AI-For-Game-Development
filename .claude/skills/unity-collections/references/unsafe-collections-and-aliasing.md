# Unsafe collections and aliasing

Source: [Collections overview](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/collections-overview.html), [Aliasing allocators](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/allocator-aliasing.html).

Both give up a guarantee for overhead; both fail silently, not at compile time.

## Native- vs Unsafe-
- `Native-` reports use-after-dispose and cross-thread races; `Unsafe-` reports nothing. Keep `Native-` unless a measurement shows the checks are the bottleneck.
- The `Unity.Collections.LowLevel.Unsafe` `using` is the review signal that a justification is owed.
- Only an `Unsafe-` collection can be the inner type of another collection.

## Aliasing
- An alias owns nothing: it shares the parent's allocation.
- Only the original is disposed; `Dispose()` on an alias is wrong, and disposing the parent covers every alias.
- A write through any alias is visible through all and the parent.
- Parent disposal invalidates every alias at once.

Shapes: type conversion (same bytes as another collection type, no copy), subrange view (hide the rest from a consumer), element reinterpretation (sizes must divide evenly).
