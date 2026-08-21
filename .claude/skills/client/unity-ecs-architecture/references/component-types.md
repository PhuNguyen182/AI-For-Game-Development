# Component Types — The Five Kinds & Their Storage Cost

Sources: [Unmanaged components](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/components-unmanaged.html), [Shared components](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/components-shared-introducing.html), [Enableable components](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/components-enableable.html).
Covers: SKILL.md §4 — **"Choose each component kind from how its value changes, not from what it holds"**.

Each kind has a different storage consequence, and the consequence — not the
data's type — is what decides the choice. The field types inside a component
(`float3`, `quaternion`) are `unity-mathematics`'s territory, not this file's.

## The five kinds

| Kind | What it decides | Source |
|---|---|---|
| `IComponentData` on a struct | The default: blittable, stored inline in the chunk, readable from jobs and Burst-compiled code | [Unmanaged components](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/components-unmanaged.html) |
| `IComponentData` on a class | Managed and **deprecated** — GC-tracked, stored outside the chunk behind an extra indirection, unusable in jobs or Burst; never the answer for new code | [Managed components](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/components-managed.html) |
| `ISharedComponentData` | Partitions the archetype's chunks by value: entities with different values never share a chunk, so a value that is unique per entity yields roughly one chunk per entity | [Shared components](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/components-shared-introducing.html) |
| `IBufferElementData` | Gives the entity a resizable `DynamicBuffer<T>`, stored in-chunk up to its declared capacity and spilling to a heap allocation past it | [Dynamic buffer components](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/components-buffer.html) |
| `IEnableableComponent` | Toggles a component on or off per entity with **no** structural change, so frequently-flipping state costs no archetype move | [Enableable components](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/components-enableable.html) |

## Choosing between them

| Situation | Kind | Source |
|---|---|---|
| Ordinary per-entity value read by a hot query | `IComponentData` struct | [Unmanaged components](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/components-unmanaged.html) |
| A handful of distinct values shared by thousands of entities (team, faction, material set) | `ISharedComponentData` | [Shared components](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/components-shared-introducing.html) |
| A value that differs per entity | Never `ISharedComponentData` — it fragments the archetype | [Shared components](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/components-shared-introducing.html) |
| Variable-length per-entity list (inventory slots, waypoints) | `IBufferElementData`, capacity set to the common case | [Dynamic buffer components](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/components-buffer.html) |
| State toggled several times per second (stunned, invulnerable) | `IEnableableComponent`, not add/remove churn | [Use enableable components](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/components-enableable-use.html) |
| Query filter with no payload | Empty tag `IComponentData` — free at rest, matched by the query | [Component concepts](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/concepts-components.html) |

**Critical caveat**: a query does not skip a disabled `IEnableableComponent`
for free by default — filtering on enabled state is a query option, and a
query written without it still visits those entities. Enableable components
remove the *structural change*, not the iteration.
