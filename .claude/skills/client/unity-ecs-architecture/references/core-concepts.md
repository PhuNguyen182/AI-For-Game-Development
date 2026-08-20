# Core ECS Concepts

Covers SKILL.md steps 1–3 (data modeling, entity/archetype design for query efficiency).

## Manual
- [Entity Component System concepts](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/concepts-intro.html) — entities as IDs linking components together; components hold data; systems hold the transform logic; no logic lives on an entity or component itself.
- [Entity concepts](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/concepts-entities.html) — an entity as a lightweight, unmanaged alternative to a GameObject; an ID, not a container.
- [World concepts](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/concepts-worlds.html) — a World owns an EntityManager and a set of Systems; systems only access entities in their own World; multiple Worlds can coexist.
- [System concepts](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/concepts-systems.html) — a system provides the logic that transforms component data from its current state to its next state.
- [Archetypes concepts](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/concepts-archetypes.html) — an archetype is the unique combination of component types shared by a group of entities; chunk-based storage and query efficiency depend on this.
- [Component concepts](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/concepts-components.html) — component role overview: unmanaged/managed data, tag components, resizable buffers.
- [Structural changes concepts](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/concepts-structural-changes.html) — creating/destroying entities, adding/removing components, and setting shared component values all reorganize chunk memory, must run on the main thread, and cause sync points.

## Scripting API
- [`EntityManager`](https://docs.unity3d.com/Packages/com.unity.entities@6.6/api/Unity.Entities.EntityManager.html) — struct providing create/read/update/destroy APIs for entities and components within a World.
- [`World`](https://docs.unity3d.com/Packages/com.unity.entities@6.6/api/Unity.Entities.World.html) — encapsulates a set of entities, component data, and systems; multiple isolated Worlds can exist concurrently.
