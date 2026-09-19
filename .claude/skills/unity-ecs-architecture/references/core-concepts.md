# Core ECS Concepts — Entities, Worlds, Archetypes & Chunks

Sources: [ECS concepts](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/concepts-intro.html), [Archetypes](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/concepts-archetypes.html), [Structural changes](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/concepts-structural-changes.html).
Covers: SKILL.md §4 — **"Model entities and archetypes before naming a single system"**.

The storage model a data design is actually judged against: what an entity is,
what groups entities into chunks, and what reorganizes that storage. Which
component *kind* to use is [component-types.md](component-types.md); the
container types a system reads from belong to `unity-collections`.

## The model

| Subject | What it decides | Source |
|---|---|---|
| Entity | An ID, not a container — it holds no data and no logic, so "put this on the entity" always means a component | [Entity concepts](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/concepts-entities.html) |
| Component | Data only; a tag component with no fields is a legitimate and free query filter | [Component concepts](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/concepts-components.html) |
| System | The only place logic lives; transforms component data from one state to the next | [System concepts](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/concepts-systems.html) |
| World | Owns one `EntityManager` and its systems; a system can only see entities in its own World, so a second World isolates rather than shares | [World concepts](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/concepts-worlds.html) |
| Archetype | The unique component-set combination; queries match archetypes, so the component set is the unit of query cost | [Archetypes](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/concepts-archetypes.html) |
| Chunk | Fixed 16 KiB block holding entities of one archetype — entities per chunk is that budget divided by per-entity size, which is why a wide archetype costs query throughput | [Archetypes](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/concepts-archetypes.html) |

## Structural changes

| Operation | What it decides | Source |
|---|---|---|
| Create / destroy entity | Reorganizes chunk memory; main-thread only; forces a sync point | [Structural changes](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/concepts-structural-changes.html) |
| Add / remove component | Moves the entity to a different archetype, so any handle into its old chunk is invalidated | [Structural changes](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/concepts-structural-changes.html) |
| Set a shared component value | Also structural — it re-partitions chunks, which is why per-entity-unique shared values fragment an archetype | [Structural changes](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/concepts-structural-changes.html) |

**Critical caveat**: a sync point completes every running job that could touch
the affected data, not only the one being changed — the cost is frame-wide,
which is why batching through an `EntityCommandBuffer` is a §4 requirement
rather than a preference. See [structural-changes-and-ecb.md](structural-changes-and-ecb.md).

## API index

| Type | Source |
|---|---|
| `EntityManager` | [EntityManager](https://docs.unity3d.com/Packages/com.unity.entities@6.6/api/Unity.Entities.EntityManager.html) |
| `World` | [World](https://docs.unity3d.com/Packages/com.unity.entities@6.6/api/Unity.Entities.World.html) |
