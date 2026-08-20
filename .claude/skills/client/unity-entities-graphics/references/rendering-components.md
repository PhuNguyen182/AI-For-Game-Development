# Rendering Component Set

Covers SKILL.md step 3 — the baked/runtime component set an entity needs to render.

## Manual
- [Entities Graphics Features](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/entities-graphics-features.html) — index page for the three headline features: Material Property Overrides, Companion Components, the BatchRendererGroup API (each detailed in its own reference file here).

## API — Unity.Rendering namespace
- [RenderMeshUtility](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/api/Unity.Rendering.RenderMeshUtility.html) — helper class with static methods (notably `AddComponents`) for populating an entity so it's compatible with Entities Graphics; see [runtime-creation-and-performance.md](runtime-creation-and-performance.md) for the recommended usage pattern.
- [RenderMeshArray](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/api/Unity.Rendering.RenderMeshArray.html) — shared component holding the meshes/materials list many entities reference by index, avoiding per-entity duplication.
- [MaterialMeshInfo](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/api/Unity.Rendering.MaterialMeshInfo.html) — Burst-compatible unmanaged component selecting which mesh/material index (from the entity's `RenderMeshArray`) an entity actually uses.
- [RenderMeshDescription](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/api/Unity.Rendering.RenderMeshDescription.html) — struct describing rendering setup for `RenderMeshUtility.AddComponents` (shadow casting mode, light probe usage, layer, etc.).
- [RenderBounds](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/api/Unity.Rendering.RenderBounds.html) — unmanaged component holding an entity's render bounds, used for culling.
- [RenderMeshUnmanaged](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/api/Unity.Rendering.RenderMeshUnmanaged.html) — defines mesh/rendering properties during baking.

Baking produces this component set automatically from ordinary `MeshRenderer`/`MeshFilter`/`LODGroup` GameObjects (see [overview-and-setup.md](overview-and-setup.md)'s Overview entry) — hand-assembling it is only needed for runtime entity creation, covered in [runtime-creation-and-performance.md](runtime-creation-and-performance.md).
