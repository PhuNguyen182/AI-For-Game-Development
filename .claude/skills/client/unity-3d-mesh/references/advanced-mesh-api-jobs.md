# Advanced Mesh API — MeshDataArray, MeshData & the Job System

Sources: [Mesh.AcquireReadOnlyMeshData](https://docs.unity3d.com/ScriptReference/Mesh.AcquireReadOnlyMeshData.html), [Mesh.AllocateWritableMeshData](https://docs.unity3d.com/ScriptReference/Mesh.AllocateWritableMeshData.html), [Mesh.ApplyAndDisposeWritableMeshData](https://docs.unity3d.com/ScriptReference/Mesh.ApplyAndDisposeWritableMeshData.html), [Access meshes via the Mesh API](https://docs.unity3d.com/Manual/UsingtheMeshClass.html).
Covers: SKILL.md §4 — **"Reach for the Advanced Mesh API only once profiling justifies its manual buffer-layout cost"**.

`MeshDataArray`/`MeshData` are the only thread-safe way to read or build
`Mesh` geometry, which is what makes them usable from a Burst/Job-System
job. This file exists to serve the escalation branch of authoring-tier
selection in [mesh-scripting-api.md](mesh-scripting-api.md) — read it once
that file's lower tiers are confirmed insufficient, not before.

## Contents

- [Reading mesh data: AcquireReadOnlyMeshData](#reading-mesh-data-acquirereadonlymeshdata)
- [Writing mesh data: AllocateWritableMeshData](#writing-mesh-data-allocatewritablemeshdata)
- [Disposal and lifetime rules](#disposal-and-lifetime-rules)

## Reading mesh data: AcquireReadOnlyMeshData

| Overload | What it decides | Source |
|---|---|---|
| `AcquireReadOnlyMeshData(Mesh mesh)` | Snapshot of one mesh | [Mesh.AcquireReadOnlyMeshData](https://docs.unity3d.com/ScriptReference/Mesh.AcquireReadOnlyMeshData.html) |
| `AcquireReadOnlyMeshData(Mesh[] meshes)` / `(List<Mesh> meshes)` | Snapshot of several meshes in one call — always preferred over one call per mesh, since each call carries its own memory-tracking overhead | [Mesh.AcquireReadOnlyMeshData](https://docs.unity3d.com/ScriptReference/Mesh.AcquireReadOnlyMeshData.html) |

```csharp
using Unity.Collections;
using UnityEngine;

public class ExampleScript : MonoBehaviour
{
    void Start()
    {
        Mesh mesh = new Mesh();
        mesh.vertices = new[] { Vector3.one, Vector3.zero };

        using (Mesh.MeshDataArray dataArray = Mesh.AcquireReadOnlyMeshData(mesh))
        {
            Mesh.MeshData data = dataArray[0];
            NativeArray<Vector3> gotVertices =
                new NativeArray<Vector3>(mesh.vertexCount, Allocator.TempJob);
            data.GetVertices(gotVertices);
            gotVertices.Dispose();
        }
    }
}
```

**Critical caveat**: this call throws `InvalidOperationException` if the
mesh's `isReadable` is false — the same Read/Write Enabled gate documented
in [mesh-optimization.md](mesh-optimization.md). A mesh modified after the
snapshot was acquired does not update the already-acquired `MeshData`.

## Writing mesh data: AllocateWritableMeshData

| Member | What it does | Source |
|---|---|---|
| `AllocateWritableMeshData(int meshCount)` | Returns a `MeshDataArray` of writable `MeshData` structs, accessible from any thread including inside a job | [Mesh.AllocateWritableMeshData](https://docs.unity3d.com/ScriptReference/Mesh.AllocateWritableMeshData.html) |
| `MeshData.SetVertexBufferParams`/`GetVertexData<T>` | Defines the vertex layout for one `MeshData`, then exposes it as a typed buffer to write into | [Mesh.AllocateWritableMeshData](https://docs.unity3d.com/ScriptReference/Mesh.AllocateWritableMeshData.html) |
| `MeshData.SetIndexBufferParams`/`GetIndexData<T>` | Defines the index buffer format for one `MeshData`, then exposes it as a typed buffer to write into | [Mesh.AllocateWritableMeshData](https://docs.unity3d.com/ScriptReference/Mesh.AllocateWritableMeshData.html) |
| `ApplyAndDisposeWritableMeshData(dataArray, mesh)` | Uploads the populated `MeshData` into the actual `Mesh` object(s) and disposes the array in one call | [Mesh.ApplyAndDisposeWritableMeshData](https://docs.unity3d.com/ScriptReference/Mesh.ApplyAndDisposeWritableMeshData.html) |

Usage pattern: allocate, configure each `MeshData`'s buffer params, fill
the buffers (directly or from inside a scheduled job), apply-and-dispose,
then call `RecalculateNormals`/`RecalculateBounds` on the resulting `Mesh`
— applying the data does not recompute either for you, per the same rule
stated for the lower tiers in [mesh-scripting-api.md](mesh-scripting-api.md).

## Disposal and lifetime rules

| Rule | Consequence if broken | Source |
|---|---|---|
| Always dispose a `MeshDataArray` once done with it | Undisposed arrays leak the underlying native memory tracking | [Mesh.AcquireReadOnlyMeshData](https://docs.unity3d.com/ScriptReference/Mesh.AcquireReadOnlyMeshData.html) |
| `AcquireReadOnlyMeshData` causes no allocation or copy, as long as the array is disposed before the source mesh is modified | Modifying the mesh while a snapshot is still open forces a copy Unity would otherwise avoid | [Mesh.AcquireReadOnlyMeshData](https://docs.unity3d.com/ScriptReference/Mesh.AcquireReadOnlyMeshData.html) |
| Prefer a `using` block over a manual dispose call | Matches `coding-principles.md`'s Exception handling section's guidance for any `IDisposable` | synthesized |
