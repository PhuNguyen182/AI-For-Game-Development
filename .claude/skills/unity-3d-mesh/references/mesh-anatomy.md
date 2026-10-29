# Mesh Anatomy

Sources: [Mesh data](https://docs.unity3d.com/Manual/AnatomyofaMesh.html) (M), [vertex data](https://docs.unity3d.com/Manual/mesh-vertex-data.html) (V), [index data](https://docs.unity3d.com/Manual/mesh-index-data.html) (I), [topology](https://docs.unity3d.com/Manual/mesh-topology-data.html) (T).

## Vertex attributes (V)
- Position is the only required attribute. Every other array (`normals`, `tangents`, `colors`/`colors32`, `uv`..`uv8`) is separate and must match its length exactly, or the assignment throws. On a fresh mesh assign positions first, or resize all arrays together.
- Tangent has 4 components: `xyz` plus a `w` sign for the bitangent; normal-mapped shaders need it.
- `uv` channel 1 is reserved by convention for baked lightmap UVs.
- `colors32` is the cheaper byte-packed form.
- `Mesh.HasVertexAttribute` checks an attribute before reading it.

## Index data and topology (I, T)
- Indices reference the vertex array; faces sharing a vertex reuse it.
- Winding: clockwise seen from the visible side faces outward; the reverse is culled by default.
- `indexFormat`: `UInt16` default caps at 65,535 vertices; set `UInt32` before assigning a larger vertex array.
- `MeshTopology`: `Triangles`, `Quads`, `Lines`, `LineStrip`, `Points`; each submesh has its own topology (set via `SetIndices`).

## Submeshes and bounds (M)
- `subMeshCount` = independent index ranges = material slots.
- `bounds` is what culling reads; it goes stale after a vertex change until `RecalculateBounds` or an explicit set.

## Deformable data
Bind poses, blend shapes, bone weights and `SkinnedMeshRenderer` belong to `unity-animation`.
