# Component Types

Covers SKILL.md step 2 (choosing the right component kind deliberately).

## Manual
- [Unmanaged components](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/components-unmanaged.html) — the default: a struct implementing `IComponentData` with blittable, unmanaged fields; stored directly in chunks; usable in jobs and Burst-compiled code.
- [Managed components](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/components-managed.html) — a class implementing `IComponentData`; **deprecated** — can't be accessed in jobs or Burst-compiled code, requires garbage collection, stored out-of-chunk with an extra index lookup. Default to unmanaged components instead.
- [Shared components introduction](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/components-shared-introducing.html) — `ISharedComponentData` groups entities within an archetype's chunks by matching value, de-duplicating data; unique values per entity fragments chunks — use only when many entities genuinely share the same value.
- [Dynamic buffer components](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/components-buffer.html) — `IBufferElementData` gives an entity a resizable, array-like `DynamicBuffer<T>`; stored in-chunk until it exceeds capacity, then spills to an external allocation.
- [Enableable components](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/components-enableable.html) — `IEnableableComponent` (on `IComponentData`/`IBufferElementData`) toggles a component on/off per-entity at runtime without a structural change; use for frequently/unpredictably changing state instead of add/remove churn.
- [Use enableable components](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/components-enableable-use.html) — enabling/disabling API, and how queries can filter on enabled state.
