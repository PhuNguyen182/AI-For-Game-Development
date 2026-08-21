# Root Links — Unity 3D Mesh (Manual & Scripting API)

Source: the root index pages listed below, as provided for this skill.
Covers: the whole skill — provenance and version anchor for every file in
this folder.

Anchors every link in this folder to Unity's core Manual and Scripting API,
published without a version segment and therefore always resolving to the
current release (the Mesh components reference page identifies itself as
version 6.5 at the time this skill was written). Re-verify any default
against the Editor version the project actually builds with. The boundary
worth stating up front: this skill owns the `Mesh` asset, its scripting
API, and the `MeshFilter`/`MeshRenderer` pair that consumes it — not the
extra data a `SkinnedMeshRenderer` adds (bones, bind poses, blend shapes;
that's `unity-animation`), and not the `MeshCollider` cooking behaviour
built-in physics gives that same mesh (that's `unity-3d-physics`).

| Root | Holds | Source |
|---|---|---|
| Meshes (parent page) | Every mesh subtopic below, plus links to LOD and model-import pages this skill does not own | [Meshes](https://docs.unity3d.com/Manual/mesh.html) |
| Get started with meshes | Terminology overview and the Manual's own topic table | [Get started with meshes](https://docs.unity3d.com/Manual/get-started-with-meshes.html) |
| Creating and accessing meshes via script | The Mesh API and the quad-mesh worked example | [Creating and accessing meshes via script](https://docs.unity3d.com/Manual/creating-meshes.html) |
| Mesh components reference | Mesh Renderer, Skinned Mesh Renderer, Mesh Filter, Mesh asset Inspector | [Mesh components reference](https://docs.unity3d.com/Manual/mesh-components-reference.html) |
| Mesh scripting API root | Full `UnityEngine.Mesh` member list | [Mesh](https://docs.unity3d.com/ScriptReference/Mesh.html) |

## Topic → file map

| Topic | File | Source |
|---|---|---|
| Vertex attributes, index buffer, topology, bounds, deformable-mesh boundary | [mesh-anatomy.md](mesh-anatomy.md) | [Mesh data](https://docs.unity3d.com/Manual/AnatomyofaMesh.html) |
| `Mesh` class members, quad-mesh script, primitive GameObjects | [mesh-scripting-api.md](mesh-scripting-api.md) | [Access meshes via the Mesh API](https://docs.unity3d.com/Manual/UsingtheMeshClass.html) |
| `MeshDataArray`/`MeshData` for the C# Job System | [advanced-mesh-api-jobs.md](advanced-mesh-api-jobs.md) | [Mesh.AcquireReadOnlyMeshData](https://docs.unity3d.com/ScriptReference/Mesh.AcquireReadOnlyMeshData.html) |
| `MeshFilter`, `MeshRenderer`, Mesh asset Inspector, Mesh Preview | [mesh-components.md](mesh-components.md) | [Mesh components reference](https://docs.unity3d.com/Manual/mesh-components-reference.html) |
| Compression, `CombineMeshes`, `MarkDynamic`, `Optimize` | [mesh-optimization.md](mesh-optimization.md) | [Compressing mesh data for optimization](https://docs.unity3d.com/Manual/compressing-mesh-data-optimization.html) |

## Adjacent Manual sections this skill does not own

| Topic | Owner | Source |
|---|---|---|
| `SkinnedMeshRenderer`, bind poses, blend shapes, bone weights | `unity-animation` | [Mesh data for deformable meshes](https://docs.unity3d.com/Manual/mesh-data-deformable-meshes.html) |
| `MeshCollider` cooking and collision behaviour | `unity-3d-physics` | [Mesh Collider](https://docs.unity3d.com/Manual/class-MeshCollider.html) |
| LOD Group, Mesh LOD generator, GPU Resident Drawer | `unity-engineer` / `tech-lead-performance` | [Mesh LOD](https://docs.unity3d.com/Manual/lod/mesh-lod-introduction.html) |
| FBX/3D model import settings | `unity-engineer` | [Importing Models](https://docs.unity3d.com/Manual/ImportingModelFiles.html) |
| Text geometry (legacy `TextMesh`) | `unity-engineer` | [Text Mesh](https://docs.unity3d.com/Manual/class-TextMesh.html) |
