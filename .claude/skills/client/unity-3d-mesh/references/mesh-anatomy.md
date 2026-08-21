# Mesh Anatomy — Vertex Attributes, Index Data, Topology & Bounds

Sources: [Mesh data](https://docs.unity3d.com/Manual/AnatomyofaMesh.html), [Mesh vertex data](https://docs.unity3d.com/Manual/mesh-vertex-data.html), [Mesh topology data](https://docs.unity3d.com/Manual/mesh-topology-data.html), [Mesh index data](https://docs.unity3d.com/Manual/mesh-index-data.html), [Mesh data for deformable meshes](https://docs.unity3d.com/Manual/mesh-data-deformable-meshes.html).
Covers: SKILL.md §4 — **"Assign vertex data through arrays that all share the vertex count"**, **"Switch `indexFormat` to `UInt32` before the vertex count can exceed 65535"**.

What a `Mesh` actually stores, and the facts that decide whether a given
array assignment is valid. `unity-animation` owns the extra data a
deformable mesh carries (bind poses, blend shapes, bone weights) — this
file states only where that boundary sits, not the mechanism on the other
side of it.

## Contents

- [Vertex attributes](#vertex-attributes)
- [Index data and topology](#index-data-and-topology)
- [Submeshes and bounds](#submeshes-and-bounds)
- [Deformable-mesh boundary](#deformable-mesh-boundary)

## Vertex attributes

| Attribute | What it decides | Source |
|---|---|---|
| Position (`Mesh.vertices`/`GetVertices`/`SetVertices`) | The only required attribute; every other array below must match its length exactly, or the assignment throws | [Mesh vertex data](https://docs.unity3d.com/Manual/mesh-vertex-data.html) |
| Normal (`normals`) | Surface direction per vertex, read by lighting; unset or wrong-facing normals read flat or lit from the wrong side | [Mesh vertex data](https://docs.unity3d.com/Manual/mesh-vertex-data.html) |
| Tangent (`tangents`) | Four components — `xyz` direction plus a `w` sign for bitangent orientation — required for normal-mapped shaders | [Mesh vertex data](https://docs.unity3d.com/Manual/mesh-vertex-data.html) |
| Color (`colors`/`colors32`) | Per-vertex tint independent of any texture; `colors32` is the cheaper byte-packed form | [Mesh vertex data](https://docs.unity3d.com/Manual/mesh-vertex-data.html) |
| Texture coordinates (`uv` through `uv8`, 8 channels) | Maps a texture onto the surface; channel 1 is reserved by convention for baked lightmap UVs | [Lightmap UVs](https://docs.unity3d.com/Manual/LightingGiUvs.html) |
| Bone weights / blend indices | Up to 256 bones per vertex for skinning — required only on a deformable mesh, not a static one | [Mesh vertex data](https://docs.unity3d.com/Manual/mesh-vertex-data.html) |
| `Mesh.HasVertexAttribute` | Checks whether a given `VertexAttribute` is present before reading it, instead of assuming | [Mesh.HasVertexAttribute](https://docs.unity3d.com/ScriptReference/Mesh.HasVertexAttribute.html) |

**Critical caveat**: all vertex data is stored in separate arrays of the
same size. Setting `vertices` to a shorter or longer array than an
already-assigned `normals`/`uv`/`colors`/`tangents` array throws
immediately — assign position data first on a fresh mesh, or resize every
array together.

## Index data and topology

| Concept | What it decides | Source |
|---|---|---|
| Index buffer (`Mesh.GetIndices`/`SetIndices`, legacy `triangles`) | Integers referencing the vertex array; a vertex is reused across every face that shares it rather than duplicated | [Mesh index data](https://docs.unity3d.com/Manual/mesh-index-data.html) |
| Winding order | Clockwise vertex order (viewed from the visible side) faces outward and renders; the reverse order culls by default | [Mesh index data](https://docs.unity3d.com/Manual/mesh-index-data.html) |
| `indexFormat` (`IndexFormat.UInt16`/`UInt32`) | `UInt16` is the default and caps a mesh at 65,535 vertices; switch to `UInt32` before assigning a larger vertex array, not after | [Mesh index data](https://docs.unity3d.com/Manual/mesh-index-data.html) |
| `MeshTopology` (`Triangles`, `Quads`, `Lines`, `LineStrip`, `Points`) | The face type the index buffer encodes; `Points` renders individual points rather than faces at all | [Mesh topology data](https://docs.unity3d.com/Manual/mesh-topology-data.html) |
| `Mesh.GetTopology`/parameter of `SetIndices` | Reads or sets a submesh's topology independently of any other submesh in the same mesh | [Mesh.SetIndices](https://docs.unity3d.com/ScriptReference/Mesh.SetIndices.html) |

## Submeshes and bounds

| Concept | What it decides | Source |
|---|---|---|
| `subMeshCount` | How many independent index ranges (and therefore material slots) the mesh exposes; see [mesh-components.md](mesh-components.md) for keeping `MeshRenderer.materials` in sync | [Mesh data](https://docs.unity3d.com/Manual/AnatomyofaMesh.html) |
| `bounds` | The bounding volume every renderer and culling system reads; stale after a vertex change until `RecalculateBounds` runs or it is set explicitly | [Mesh data](https://docs.unity3d.com/Manual/AnatomyofaMesh.html) |

## Deformable-mesh boundary

| Concept | Owner | Source |
|---|---|---|
| Blend shapes (sparse per-vertex deformation deltas) | `unity-animation` | [Mesh data for deformable meshes](https://docs.unity3d.com/Manual/mesh-data-deformable-meshes.html) |
| Bind poses (`Mesh.bindposes`) | `unity-animation` | [Mesh.bindposes](https://docs.unity3d.com/ScriptReference/Mesh-bindposes.html) |
| `SkinnedMeshRenderer` and its bone hierarchy | `unity-animation` | [Mesh data for deformable meshes](https://docs.unity3d.com/Manual/mesh-data-deformable-meshes.html) |
