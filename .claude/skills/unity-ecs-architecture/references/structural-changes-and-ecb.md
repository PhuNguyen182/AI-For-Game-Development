# Structural Changes & Entity Command Buffers

Sources: [Entity command buffer overview](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/systems-entity-command-buffers.html), [Use an entity command buffer](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/systems-entity-command-buffer-use.html).
Covers: SKILL.md §4 — **"Batch every structural change through an `EntityCommandBuffer`"**.

What a structural change actually costs, and how an ECB converts many of them
into one. The set of operations that count as structural is in
[core-concepts.md](core-concepts.md).

## Why batching is required

| Subject | What it decides | Source |
|---|---|---|
| Sync point | A structural change completes every running job that could touch the affected data — the cost is frame-wide, not local to the call | [Structural changes](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/concepts-structural-changes.html) |
| Main-thread restriction | `EntityManager` structural APIs cannot be called from a job at all, so an in-job change must be recorded rather than performed | [Structural changes](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/concepts-structural-changes.html) |
| `EntityCommandBuffer` | A queue of recorded commands played back later on the main thread, consolidating many sync points into one | [ECB overview](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/systems-entity-command-buffers.html) |

## Recording and playback

| Subject | What it decides | Source |
|---|---|---|
| Record from the main thread | Simplest form; still worth it purely to defer changes past an in-flight iteration | [Use an ECB](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/systems-entity-command-buffer-use.html) |
| `AsParallelWriter()` | Allows recording from a parallel job; playback order follows the supplied sort key, so the key is what makes the result reproducible | [Use an ECB](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/systems-entity-command-buffer-use.html) |
| ECB system (`BeginSimulationEntityCommandBufferSystem` and siblings) | Provides a buffer whose playback happens at a defined point in the frame, so the change lands at a predictable time | [ECB overview](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/systems-entity-command-buffers.html) |
| Deferred entities | An entity created into an ECB is a placeholder until playback; it cannot be read back inside the same job | [Use an ECB](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/systems-entity-command-buffer-use.html) |
| Worked example | Removing a component after iteration instead of mid-loop | [ECB workflow example](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/ecs-workflow-example-ecb.html) |

**Critical caveat**: playing back one buffer twice throws. An ECB is
single-playback; a buffer obtained from an ECB system is played back by that
system, so recording into it and also calling `Playback` manually is a
double-playback bug rather than a redundant call.

## API index

| Type | Source |
|---|---|
| `EntityCommandBuffer` | [EntityCommandBuffer](https://docs.unity3d.com/Packages/com.unity.entities@6.6/api/Unity.Entities.EntityCommandBuffer.html) |
