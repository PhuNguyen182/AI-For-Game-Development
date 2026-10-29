# Advanced Mesh API

Sources: [AcquireReadOnlyMeshData](https://docs.unity3d.com/ScriptReference/Mesh.AcquireReadOnlyMeshData.html), [AllocateWritableMeshData](https://docs.unity3d.com/ScriptReference/Mesh.AllocateWritableMeshData.html).

`MeshDataArray`/`MeshData` are the only thread-safe way to read or build `Mesh` geometry, so a Burst job can use them. Scheduling and allocator lifetime: `unity-job-system-and-burst`.

## Reading
- `AcquireReadOnlyMeshData(Mesh)` or `(Mesh[])`/`(List<Mesh>)`; prefer one call for several meshes (each call has memory-tracking overhead).
- Throws `InvalidOperationException` if `isReadable` is false.
- No allocation or copy while the array is disposed before the source mesh is modified; modifying earlier forces a copy. A mesh modified after acquisition does not update the snapshot.
- Copy out with `data.GetVertices(NativeArray<Vector3>)`.

## Writing
1. `Mesh.AllocateWritableMeshData(count)` — usable on any thread, including in a job.
2. Per `MeshData`: `SetVertexBufferParams` then `GetVertexData<T>`; `SetIndexBufferParams` then `GetIndexData<T>`; fill.
3. `Mesh.ApplyAndDisposeWritableMeshData(array, mesh)` uploads and disposes.
4. Applying does not compute normals or bounds: call `RecalculateNormals`/`RecalculateBounds` on the result.

Dispose every read-only `MeshDataArray` (use `using`); an undisposed one leaks native tracking memory.
