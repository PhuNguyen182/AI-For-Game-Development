# Core ECS Concepts

Docs: https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/ (concepts-entities, concepts-archetypes, concepts-structural-changes).

| Subject | Fact |
|---|---|
| Entity | An ID, not a container; "put this on the entity" means a component |
| Component | Data only; an empty tag component is a free query filter |
| System | The only place logic lives |
| World | Owns one `EntityManager` and its systems; a system sees only its own World, so a second World isolates rather than shares |
| Archetype | The unique component-set combination; queries match archetypes, so the component set is the unit of query cost |
| Chunk | Fixed 16 KiB block of one archetype; entities per chunk = 16 KiB / per-entity size, so a wide archetype costs query throughput |

## Structural changes
- Create/destroy an entity: reorganizes chunk memory, main-thread only, forces a sync point.
- Add/remove a component: moves the entity to another archetype; handles into the old chunk become invalid.
- Setting a shared component value is also structural: it re-partitions chunks.
- A sync point completes every running job that could touch the affected data, so the cost is frame-wide. Batching: [structural-changes-and-ecb.md](structural-changes-and-ecb.md).
