# Mesh Scripting API

Sources: [Mesh API](https://docs.unity3d.com/Manual/UsingtheMeshClass.html), [quad example](https://docs.unity3d.com/Manual/Example-CreatingaBillboardPlane.html), [primitives](https://docs.unity3d.com/Manual/PrimitiveObjects.html).

## Authoring tiers
| Tier | Use when |
|---|---|
| Legacy properties (`vertices`, `triangles`, `normals`, `uv`) | One-off or setup-time mesh; every access copies the full array |
| `SetVertices`/`SetTriangles`/`SetIndices`/`SetUVs`/`SetNormals`/`SetTangents`/`SetColors` | Occasional edits; avoids the getter copy |
| `SetVertexBufferParams`/`SetVertexBufferData`/`SetIndexBufferParams`/`SetIndexBufferData`/`SetSubMesh` | Control of vertex layout, still main thread |
| `MeshDataArray`/`MeshData` + jobs | Measured need to leave the main thread: [advanced-mesh-api-jobs.md](advanced-mesh-api-jobs.md) |

## Members worth knowing
- `RecalculateBounds`, `RecalculateNormals`, `RecalculateTangents` (needs normals and UVs); `Clear`.
- `GetIndices`/`SetIndices` take a submesh and topology; `triangles` addresses the default submesh only.
- `isReadable` (read-only), `vertexCount`, `HasVertexAttribute`.
- Mesh LOD members (`lodCount`, `GetLod`/`SetLod`) belong to `unity-performance-engineer`.

## Quad example
```csharp
var mesh = new Mesh();
mesh.vertices = new[] { new Vector3(0,0,0), new Vector3(w,0,0), new Vector3(0,h,0), new Vector3(w,h,0) };
mesh.triangles = new[] { 0, 2, 1, 2, 3, 1 };
mesh.normals = new[] { -Vector3.forward, -Vector3.forward, -Vector3.forward, -Vector3.forward };
mesh.uv = new[] { new Vector2(0,0), new Vector2(1,0), new Vector2(0,1), new Vector2(1,1) };
meshFilter.mesh = mesh;
```
Vertex order and winding together face the quad down `-Vector3.forward`; reversing one without the other flips the visible face. Normals are explicit because a flat quad's normal is known; otherwise call `RecalculateNormals`.

## Primitives
- `GameObject.CreatePrimitive(PrimitiveType)` (`Cube`, `Sphere`, `Capsule`, `Cylinder`, `Plane`, `Quad`) adds `MeshFilter`, `MeshRenderer` and a default collider; tuning that collider is `unity-3d-physics`.
- `Plane` is 10x10 units; the others are 1 unit (2 tall for `Cylinder`/`Capsule`).
