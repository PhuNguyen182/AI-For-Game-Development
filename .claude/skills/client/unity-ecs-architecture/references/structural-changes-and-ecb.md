# Structural Changes & Entity Command Buffers

Covers SKILL.md step 7 (batching structural changes instead of calling EntityManager directly per-iteration).

## Manual
- [Entity command buffer overview](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/systems-entity-command-buffers.html) — an ECB is a thread-safe queue of commands you can record from a job and play back later on the main thread, consolidating multiple sync points into one.
- [Use an entity command buffer](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/systems-entity-command-buffer-use.html) — recording/playback API, both from jobs and from the main thread.
- [Use entity command buffers for structural changes](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/ecs-workflow-example-ecb.html) — worked example deferring structural changes (e.g. removing a component) until after iteration completes, instead of calling `EntityManager` mid-loop.

## Scripting API
- [Struct `EntityCommandBuffer`](https://docs.unity3d.com/Packages/com.unity.entities@6.6/api/Unity.Entities.EntityCommandBuffer.html) — thread-safe command buffer that records entity/component-affecting commands for later playback.
