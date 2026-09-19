# Runtime Creation, Batching Metrics & Known Issues

Sources: [Runtime Entity Creation](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/runtime-entity-creation.html), [Entities Graphics Performance](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/entities-graphics-performance.html), [Known Issues](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/known-issues.html).
Covers: SKILL.md §4 — **"Create runtime entities from one prototype and `Instantiate` it"**, **"Measure batching as instances per draw command"**.

## Contents
- [Runtime creation](#runtime-creation)
- [Batching efficiency](#batching-efficiency)
- [Known issues](#known-issues)

Spawning renderable entities in code, the metric that says whether it worked,
and the documented failures worth checking before filing a bug.

## Runtime creation

| Subject | What it decides | Source |
|---|---|---|
| `RenderMeshUtility.AddComponents` | Populates an entity with the rendering components from a mesh, material, and `RenderMeshDescription` | [Runtime Entity Creation](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/runtime-entity-creation.html) |
| Prototype plus `Instantiate` | The recommended pattern — instantiation cost does not depend on how the prototype was built, and it avoids a structural change per spawn | [Runtime Entity Creation](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/runtime-entity-creation.html) |
| Per-instance variation | Applied with `SetComponent` after cloning — transform and override values, not a rebuilt component set | [Runtime Entity Creation](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/runtime-entity-creation.html) |
| Bulk spawning | Composes with Burst jobs and `EntityCommandBuffer.ParallelWriter`, so large spawns stay off the main thread | [Runtime Entity Creation](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/runtime-entity-creation.html) |
| `AddComponents` per spawn | The documented anti-pattern — one structural change per instance | [Runtime Entity Creation](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/runtime-entity-creation.html) |

## Batching efficiency

| Subject | What it decides | Source |
|---|---|---|
| Instances per draw command | The efficiency metric; higher is better, and it is what a batching claim must cite | [Performance](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/entities-graphics-performance.html) |
| FrameDebugger — Hybrid Batch Groups | Shows batch groups, instance counts, and draw-call info | [Performance](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/entities-graphics-performance.html) |
| `EntitiesGraphicsStatsDrawer` | Editor-only on-screen culling and rendering stats | [Performance](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/entities-graphics-performance.html) |
| Profiler markers | `SRPBRender.ApplyShader` and `BatchRendererGroup` markers attribute the cost | [Performance](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/entities-graphics-performance.html) |
| Batch fragmentation | Differing shader variants or meshes split batches — the usual reason instance counts per command stay low | [Performance](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/entities-graphics-performance.html) |
| Low object counts | Batch-creation overhead can make this **slower** than GameObject rendering | [Performance](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/entities-graphics-performance.html) |
| Platform caveats | Android suffers from persistent-GPU-data approaches; OpenGL offers no guaranteed gain; shader-property costs apply even when instancing properties go unused | [Performance](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/entities-graphics-performance.html) |

## Known issues

| Symptom | What it decides | Source |
|---|---|---|
| Auto-generated lightmaps do nothing in subscenes | Manual baking is required — not a project misconfiguration | [Known Issues](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/known-issues.html) |
| One baked lightmap per subscene | Constrains loading several interdependent subscenes together | [Known Issues](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/known-issues.html) |
| Directional light inside a subscene | Causes missing ambient lighting and wrong cascade shadow settings | [Known Issues](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/known-issues.html) |
| Scene/subscene fog or lightmap mismatch | Renders incorrectly in Player builds specifically | [Known Issues](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/known-issues.html) |
| RenderTexture on a subscene material | Displays incorrectly at runtime | [Known Issues](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/known-issues.html) |
| `DOTS_INSTANCING_ON` variants | Always compiled into a Player build, raising build time and memory | [Known Issues](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/known-issues.html) |
| Companion previews | `ParticleSystem`/`VisualEffect` previews missing in Game View; particle light modules stop rendering once converted | [Known Issues](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/known-issues.html) |

**Critical caveat**: several of these present as content bugs rather than
package bugs — missing ambient light, a black RenderTexture, a subscene that
looks right in the Editor and wrong in a build. Check this list before
attributing any of them to authoring.
