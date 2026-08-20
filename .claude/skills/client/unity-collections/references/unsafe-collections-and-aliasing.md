# Unsafe Collections & Aliasing

Covers SKILL.md steps 4–5 (when to reach for `Unsafe-` variants, and reasoning about shared-memory aliasing).

## Manual
- [Collections overview](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/collections-overview.html) — `Unsafe-` collections (`Unity.Collections.LowLevel.Unsafe`) drop the disposal/thread-safety checks that `Native-` collections carry, trading safety for lower overhead; use only for a specific, justified low-level case (e.g. building a custom container on top of one).
- [Aliasing allocators](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/allocator-aliasing.html) — an alias is a collection that shares another collection's existing allocation instead of owning its own; it doesn't need its own `Dispose()` (only the original does), writes through any alias affect all of them, and an alias becomes unusable once its parent is disposed. Common uses: converting between collection types, viewing a subrange, or reinterpreting the same bytes as a different element type.
