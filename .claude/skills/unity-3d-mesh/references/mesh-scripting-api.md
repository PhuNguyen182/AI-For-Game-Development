# Mesh Scripting API — Building, Reading & Primitives

Sources: [Access meshes via the Mesh API](https://docs.unity3d.com/Manual/UsingtheMeshClass.html), [Create a quad mesh via script](https://docs.unity3d.com/Manual/Example-CreatingaBillboardPlane.html), [Mesh scripting reference](https://docs.unity3d.com/ScriptReference/Mesh.html), [Introduction to primitive models](https://docs.unity3d.com/Manual/PrimitiveObjects.html).
Covers: SKILL.md §4 — **"Decide the authoring tier by update frequency and scale before writing any code"**, **"Recalculate or set bounds and normals immediately after any vertex change"**.

The `Mesh` class's full member surface, plus the two lowest-tier authoring
techniques: the legacy whole-array properties and their modern
`Get*`/`Set*` equivalents. Reach for [advanced-mesh-api-jobs.md](advanced-mesh-api-jobs.md)
only once this tier is confirmed insufficient by measurement.

## Contents

- [Authoring tiers](#authoring-tiers)
- [Full Mesh member table](#full-mesh-member-table)
- [Worked example — quad mesh via script](#worked-example--quad-mesh-via-script)
- [Primitive GameObjects](#primitive-gameobjects)

## Authoring tiers

| Tier | Use when | Source |
|---|---|---|
| Legacy whole-array properties (`vertices`, `triangles`, `normals`, `uv`) | A one-off or setup-time mesh; simplest to read and write, at the cost of a full-array copy on every access | [Access meshes via the Mesh API](https://docs.unity3d.com/Manual/UsingtheMeshClass.html) |
| Modern `Get*`/`Set*` methods (`SetVertices`, `SetTriangles`, `SetIndices`, `SetUVs`) | An occasional edit where avoiding a full property-getter copy already matters, without needing manual buffer layout | [Mesh vertex data](https://docs.unity3d.com/Manual/mesh-vertex-data.html) |
| Raw buffer methods (`SetVertexBufferParams`, `SetVertexBufferData`, `SetIndexBufferParams`, `SetIndexBufferData`, `SetSubMesh`) | Maximum control over vertex layout and GPU buffer format, still on the main thread | [Access meshes via the Mesh API](https://docs.unity3d.com/Manual/UsingtheMeshClass.html) |
| `MeshDataArray`/`MeshData` with the Job System | Per-frame or large-scale procedural generation that measurement shows needs to run off the main thread — see [advanced-mesh-api-jobs.md](advanced-mesh-api-jobs.md) | [Mesh.AcquireReadOnlyMeshData](https://docs.unity3d.com/ScriptReference/Mesh.AcquireReadOnlyMeshData.html) |

## Full Mesh member table

| Member | Kind | What it does | Source |
|---|---|---|---|
| `vertices`, `GetVertices`/`SetVertices` | Property / methods | Vertex positions in local space | [Mesh](https://docs.unity3d.com/ScriptReference/Mesh.html) |
| `normals`, `GetNormals`/`SetNormals` | Property / methods | Per-vertex surface orientation, read by lighting | [Mesh](https://docs.unity3d.com/ScriptReference/Mesh.html) |
| `tangents`, `GetTangents`/`SetTangents` | Property / methods | Per-vertex tangent for normal-mapped shaders | [Mesh](https://docs.unity3d.com/ScriptReference/Mesh.html) |
| `colors`/`colors32`, `GetColors`/`SetColors` | Property / methods | Per-vertex tint | [Mesh](https://docs.unity3d.com/ScriptReference/Mesh.html) |
| `uv` through `uv8`, `GetUVs`/`SetUVs` | Property / methods | Texture-coordinate channels 0–7 | [Mesh](https://docs.unity3d.com/ScriptReference/Mesh.html) |
| `triangles`, `GetTriangles`/`SetTriangles` | Property / methods | Legacy whole-array index access for the default submesh | [Mesh](https://docs.unity3d.com/ScriptReference/Mesh.html) |
| `GetIndices`/`SetIndices` | Methods | Index buffer access for a specific submesh and topology | [Mesh.SetIndices](https://docs.unity3d.com/ScriptReference/Mesh.SetIndices.html) |
| `indexFormat` | Property | `UInt16` (default, 65,535-vertex cap) or `UInt32` | [Mesh index data](https://docs.unity3d.com/Manual/mesh-index-data.html) |
| `subMeshCount`, `GetSubMesh`/`SetSubMesh`/`SetSubMeshes` | Property / methods | Number and definition of independent index ranges | [Mesh](https://docs.unity3d.com/ScriptReference/Mesh.html) |
| `bounds` | Property | The mesh's bounding volume, read by culling and renderers | [Mesh-bounds](https://docs.unity3d.com/ScriptReference/Mesh-bounds.html) |
| `RecalculateBounds` | Method | Recomputes `bounds` from current vertex data | [Mesh](https://docs.unity3d.com/ScriptReference/Mesh.html) |
| `RecalculateNormals` | Method | Recomputes normals from triangles and vertices | [Mesh](https://docs.unity3d.com/ScriptReference/Mesh.html) |
| `RecalculateTangents` | Method | Recomputes tangents from normals and UVs | [Mesh](https://docs.unity3d.com/ScriptReference/Mesh.html) |
| `Clear` | Method | Clears all vertex data and triangle indices | [Mesh](https://docs.unity3d.com/ScriptReference/Mesh.html) |
| `isReadable` | Property (read-only) | Whether Read/Write Enabled lets runtime code read this mesh's data; see [mesh-optimization.md](mesh-optimization.md) | [Mesh-isReadable](https://docs.unity3d.com/ScriptReference/Mesh-isReadable.html) |
| `vertexCount` | Property (read-only) | Current vertex count | [Mesh](https://docs.unity3d.com/ScriptReference/Mesh.html) |
| `HasVertexAttribute`, `GetVertexAttribute*` | Methods | Query which attributes and formats a mesh actually carries | [Mesh](https://docs.unity3d.com/ScriptReference/Mesh.html) |
| `SetVertexBufferParams`/`SetVertexBufferData` | Methods | Define and fill vertex buffer layout directly | [Mesh.SetVertexBufferParams](https://docs.unity3d.com/ScriptReference/Mesh.SetVertexBufferParams.html) |
| `SetIndexBufferParams`/`SetIndexBufferData` | Methods | Define and fill the index buffer directly | [Mesh.SetIndexBufferParams](https://docs.unity3d.com/ScriptReference/Mesh.SetIndexBufferParams.html) |
| `MarkDynamic`, `Optimize`, `CombineMeshes` | Methods | See [mesh-optimization.md](mesh-optimization.md) | [Mesh](https://docs.unity3d.com/ScriptReference/Mesh.html) |
| `bindposes`, `boneWeights`, blend-shape members | Property / methods | Deformable-mesh data — owned by `unity-animation`, per [mesh-anatomy.md](mesh-anatomy.md) | [Mesh](https://docs.unity3d.com/ScriptReference/Mesh.html) |
| `lodCount`, `GetLod`/`SetLod`, `lodSelectionCurve` | Property / methods | Mesh LOD data baked into one mesh's index buffer — workflow owned by `unity-engineer`/`tech-lead-performance`, per [root-links.md](root-links.md) | [Mesh](https://docs.unity3d.com/ScriptReference/Mesh.html) |

## Worked example — quad mesh via script

```csharp
using UnityEngine;

public class QuadCreator : MonoBehaviour
{
    public float width = 1;
    public float height = 1;

    public void Start()
    {
        MeshRenderer meshRenderer = gameObject.AddComponent<MeshRenderer>();
        meshRenderer.sharedMaterial = new Material(Shader.Find("Standard"));

        MeshFilter meshFilter = gameObject.AddComponent<MeshFilter>();

        Mesh mesh = new Mesh();

        Vector3[] vertices = new Vector3[4]
        {
            new Vector3(0, 0, 0),
            new Vector3(width, 0, 0),
            new Vector3(0, height, 0),
            new Vector3(width, height, 0)
        };
        mesh.vertices = vertices;

        int[] tris = new int[6]
        {
            0, 2, 1, // lower left triangle
            2, 3, 1  // upper right triangle
        };
        mesh.triangles = tris;

        Vector3[] normals = new Vector3[4]
        {
            -Vector3.forward, -Vector3.forward, -Vector3.forward, -Vector3.forward
        };
        mesh.normals = normals;

        Vector2[] uv = new Vector2[4]
        {
            new Vector2(0, 0), new Vector2(1, 0), new Vector2(0, 1), new Vector2(1, 1)
        };
        mesh.uv = uv;

        meshFilter.mesh = mesh;
    }
}
```

Vertex order (bottom-left, bottom-right, top-left, top-right) and the two
triangles' winding both point the quad's normal down `-Vector3.forward`;
reversing either without reversing the other flips the visible face. UV
corners are `0`/`1` on every axis so each quad corner lands on a texture
corner. `Mesh.RecalculateNormals` was skipped here deliberately — a flat
quad's normal is already known, so computing it would be redundant work;
recalculating is still the right default whenever the value is not
already certain, per SKILL.md §4's normals/bounds directive. Source:
[Create a quad mesh via script](https://docs.unity3d.com/Manual/Example-CreatingaBillboardPlane.html).

## Primitive GameObjects

| Member | What it does | Source |
|---|---|---|
| `GameObject.CreatePrimitive(PrimitiveType)` | Creates a GameObject with a `MeshFilter`, `MeshRenderer`, and an appropriate default collider already attached | [GameObject.CreatePrimitive](https://docs.unity3d.com/ScriptReference/GameObject.CreatePrimitive.html) |
| `PrimitiveType` values: `Cube`, `Sphere`, `Capsule`, `Cylinder`, `Plane`, `Quad` | The six built-in mesh shapes; `Plane` is 10×10 units, the rest are 1 unit (2 units tall for `Cylinder`/`Capsule`) | [Introduction to primitive models](https://docs.unity3d.com/Manual/PrimitiveObjects.html) |

```csharp
GameObject cube = GameObject.CreatePrimitive(PrimitiveType.Cube);
cube.transform.position = new Vector3(0, 0.5f, 0);
```

**Critical caveat**: `CreatePrimitive` attaches a default collider matching
the shape (a `BoxCollider` for `Cube`, a `SphereCollider` for `Sphere`,
and so on) — tuning that collider is `unity-3d-physics`'s territory, not
this skill's, the moment it needs anything beyond the default shape.
