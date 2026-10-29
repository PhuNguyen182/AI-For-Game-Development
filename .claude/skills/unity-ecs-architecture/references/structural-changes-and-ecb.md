# Structural Changes and EntityCommandBuffer

Docs: https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/ (systems-entity-command-buffers, entity-command-buffer-use). Which operations are structural: [core-concepts.md](core-concepts.md).

- `EntityManager` structural APIs cannot run in a job, and each is a frame-wide sync point; record into an `EntityCommandBuffer` and play back once on the main thread.
- Recording from the main thread is still worth it to defer changes past an in-flight iteration.
- `AsParallelWriter()` records from a parallel job; playback order follows the sort key, so use a stable key (the entity-in-query index) for reproducible results.
- An ECB system (`BeginSimulationEntityCommandBufferSystem` and siblings) plays back at a defined frame point.
- An entity created into an ECB is a placeholder until playback and cannot be read back in the same job.
- An ECB is single-playback: playing one twice throws. A buffer from an ECB system is played back by that system, so also calling `Playback` manually is a double-playback bug.
