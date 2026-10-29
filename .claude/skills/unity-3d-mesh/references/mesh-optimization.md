# Mesh Optimization

Sources: [mesh compression](https://docs.unity3d.com/Manual/configure-mesh-compression.html) (C), [vertex compression](https://docs.unity3d.com/Manual/configure-vertex-compression.html) (V), [combining](https://docs.unity3d.com/Manual/combining-meshes.html) (B), [Mesh](https://docs.unity3d.com/ScriptReference/Mesh.html) (M).

## Mesh compression (import, C)
- Model Import Settings > Meshes > Mesh Compression: `Off`/`Low`/`Medium`/`High`; precision loss is silent.
- Approximate ratios, Low to High: vertices 1.6x-3.2x, normals 4.6x-7.4x, tangents 4.4x-6.7x, UVs 2.0x-4.0x.
- Keep `Off` for a mesh gameplay reads back and measures exactly.

## Vertex compression (project, V)
- Player Settings > Other Settings > Optimization > Vertex Compression: per-channel FP16 mask, independent of mesh compression.
- Default mask: Normal, Tangent, Tex Coord 0, 2, 3. Position and Tex Coord 1 (lightmap UVs) are excluded because compressing them distorts geometry.
- Applies only when Read/Write is off, the mesh is not skinned, the platform supports FP16, Mesh Compression is `Off`, and the mesh is not dynamically batched.

## Read/Write Enabled
- Off (`isReadable` false): any runtime read throws `InvalidOperationException`. On: extra runtime memory. Default off for meshes only the GPU touches.

## Combine vs static batching (B)
- `Mesh.CombineMeshes`: one draw call, but the whole combined mesh draws when any part is visible. Worth it for a tight always-co-visible static cluster.
- Static batching keeps per-object culling.
- `CombineMeshes(combine, mergeSubMeshes, useMatrices, hasLightmapData)`: `mergeSubMeshes = true` folds all inputs into one submesh, correct only when all share material and topology; `false` keeps one submesh per input.

## MarkDynamic and Optimize (M)
- `MarkDynamic`: once, before the first update, on a mesh rewritten every frame or close to it. On a static mesh it wastes the GPU memory it reserves.
- `Optimize`, `OptimizeIndexBuffers`, `OptimizeReorderVertexBuffer`: only on a finished mesh; reordering invalidates earlier index assumptions.
