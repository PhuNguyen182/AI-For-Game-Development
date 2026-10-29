# Component Types and Blob Assets

Docs: https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/ (components-unmanaged, components-shared, components-buffer, components-enableable, blob-assets-concept, blob-assets-create).

## Kinds
| Kind | Storage consequence |
|---|---|
| `IComponentData` struct | Default: blittable, inline in the chunk, usable from jobs and Burst |
| `IComponentData` class | Managed, deprecated: GC-tracked, outside the chunk, unusable in jobs/Burst; never for new code |
| `ISharedComponentData` | Partitions chunks by value: entities with different values never share a chunk; a per-entity-unique value yields about one chunk per entity |
| `IBufferElementData` | Resizable `DynamicBuffer<T>`, in-chunk up to declared capacity, then spills to a heap allocation |
| `IEnableableComponent` | Toggles per entity with no structural change, so frequent flips cost no archetype move |

## Choosing
| Situation | Kind |
|---|---|
| Per-entity value read by a hot query | `IComponentData` struct |
| A few distinct values shared by thousands of entities (team, faction, material set) | `ISharedComponentData` |
| Value differs per entity | Never shared |
| Variable-length per-entity list (inventory, waypoints) | `IBufferElementData`, capacity = common case |
| State toggled several times per second (stunned, invulnerable) | `IEnableableComponent`, not add/remove churn |
| Filter with no payload | Empty tag `IComponentData` |

Queries match only entities where the component is enabled, unless `EntityQueryOptions.IgnoreComponentEnabledState` is set; `IJobChunk` must apply the enabled mask itself. Enableable removes the structural change, not the iteration. (Unverified against the 6.6 page; from Entities behaviour.)

## Blob assets
- `BlobAssetReference<T>`: a component-storable handle to one shared, permanently immutable allocation; copying the component copies the handle.
- No managed data (no arrays, strings, object references): use `BlobArray<T>` and `BlobString`, or the build fails.
- Per-entity-changing data is an ordinary component, not blob content.
- `BlobBuilder` allocates the root, fills nested arrays, produces the reference, and is disposed afterwards. Build it in a Baker so it is authored once into the entity scene.
- Internal pointers are relative offsets; read through the reference, never copy fields out of the allocation.
