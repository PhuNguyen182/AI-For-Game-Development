# Runtime creation, batching metrics, known issues

Sources (under `manual/`): `runtime-entity-creation.html`, `entities-graphics-performance.html`, `known-issues.html`, `batch-renderer-group-api.html`.

## Runtime creation
- `RenderMeshUtility.AddComponents` populates an entity from a mesh, material and `RenderMeshDescription`.
- Recommended: build one prototype, `Instantiate` it; instantiation cost does not depend on how the prototype was built.
- Vary per instance with `SetComponent` (transform, override values), not a rebuilt component set.
- Bulk spawns compose with Burst jobs and `EntityCommandBuffer.ParallelWriter`.
- `AddComponents` per spawn is the documented anti-pattern: one structural change per instance.

## Batching
- Metric: instances per draw command; higher is better.
- Tools: FrameDebugger "Hybrid Batch Groups"; `EntitiesGraphicsStatsDrawer` (Editor-only culling/render stats); Profiler markers `SRPBRender.ApplyShader` and `BatchRendererGroup`.
- Differing shader variants or meshes split batches.
- Low object counts: batch-creation overhead can make this slower than GameObject rendering.
- Android suffers from persistent-GPU-data approaches; OpenGL has no guaranteed gain; shader-property costs apply even when instancing properties go unused.
- `BatchRendererGroup` is the engine API underneath, called internally. It explains how draws group; custom BRG code is a rendering-architecture decision, outside this skill.

## Known issues (check before filing a bug)
- Auto-generated lightmaps do nothing in subscenes; bake manually.
- One baked lightmap per subscene limits loading interdependent subscenes together.
- A directional light inside a subscene breaks ambient lighting and cascade shadow settings.
- Scene/subscene fog or lightmap mismatch renders wrong in Player builds only.
- RenderTexture on a subscene material displays wrong at runtime.
- `DOTS_INSTANCING_ON` variants are always compiled into a Player build (build time, memory).
- `ParticleSystem`/`VisualEffect` previews are missing in Game View; particle light modules stop rendering once converted.

Several present as content bugs (missing ambient light, black RenderTexture, right in Editor and wrong in a build); check this list before blaming authoring.
