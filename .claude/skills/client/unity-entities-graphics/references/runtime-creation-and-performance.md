# Runtime Entity Creation, Performance & Known Issues

Covers SKILL.md steps 4 and 9 — creating renderable entities in code, and measuring/diagnosing the result.

## Manual — Runtime Entity Creation
- [Runtime Usage](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/runtime-usage.html) — index page pointing to Runtime Entity Creation for spawning/configuring renderable entities during gameplay rather than at design time.
- [Runtime Entity Creation](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/runtime-entity-creation.html) — `RenderMeshUtility.AddComponents` populates an entity with the required rendering components from a mesh, material, and `RenderMeshDescription`. **Recommended pattern**: build one prototype entity via `AddComponents`, then `Instantiate` it repeatedly and update per-instance data (transform, etc.) via `SetComponent` — instantiation performance doesn't depend on how the prototype was created, it avoids repeated expensive structural changes, and it composes with Burst jobs + `EntityCommandBuffer.ParallelWriter` for parallel bulk spawning. Calling `AddComponents` per spawn is the documented anti-pattern this avoids.

## Manual — Performance
- [Entities Graphics Performance](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/entities-graphics-performance.html) — rendering goes through `BatchRendererGroup` + DOTS Instancing, batching same-mesh/same-material instances into draw calls; efficiency is measured as **instances per draw command** (higher is better).
  - **Measurement tools**: FrameDebugger (shows "Hybrid Batch Groups," instance counts, draw-call info); `EntitiesGraphicsStatsDrawer` (Editor-only on-screen overlay for culling/rendering stats); Profiler (`SRPBRender.ApplyShader`, `BatchRendererGroup` markers).
  - **Caveats**: batch-creation overhead means Entities Graphics can be *slower* than GameObject rendering when few objects are batched; Android performance can suffer from persistent-GPU-data approaches; shader-property costs apply even when DOTS instancing properties go unused; OpenGL offers no guaranteed gain; differing shader variants or meshes fragment batches.

## Manual — Known Issues
- [Known Issues](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/known-issues.html)
  - **Lighting**: "Auto-generate lightmaps" unsupported with sub-scenes (manual baking required); a sub-scene can only store a single baked lightmap (a problem when loading/unloading multiple interdependent sub-scenes); a directional light inside a sub-scene causes missing ambient lighting and incorrect cascade shadow settings; mismatched fog/lightmap settings between a scene and its sub-scenes can render incorrectly in Player builds.
  - **RenderTexture**: a camera rendering into a RenderTexture assigned to a sub-scene `MeshRenderer` material's texture displays incorrectly at runtime.
  - **Shader stripping**: `DOTS_INSTANCING_ON` shader variants are always compiled and included in a Player build, which can lengthen build times and increase memory usage.
  - **Companion Components**: `ParticleSystem`/`VisualEffect` previews aren't available in Game View; `ParticleSystem` light modules don't render once converted to a companion component; HDRP `PlanarReflectionProbe` objects need "Maximum Planar Reflection Probes on Screen" increased.

Cross-check an unexplained symptom against this known-issues list before treating it as a new bug — per SKILL.md's edge-case guardrails.
