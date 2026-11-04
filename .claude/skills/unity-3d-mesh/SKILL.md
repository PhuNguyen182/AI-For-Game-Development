---
name: unity-3d-mesh
description: "Procedural meshes: Mesh API, SetVertices, MeshData, 32-bit indices, CombineMeshes. Use when generating meshes in code."
user-invocable: false
---

# Unity 3D Mesh

- **Not for:** skinning, blend shapes, bones (`unity-animation`).
- **Not for:** `MeshCollider` cooking (`unity-3d-physics`).
- **Not for:** materials and shaders (`shader-authoring`).
- **Not for:** LOD, batching escalation, model import settings (`unity-performance-engineer`; no owning skill yet: flag the gap).
- **Not for:** sprite meshes (`unity-2d-sprite`).
- **Not for:** GPU-only deformation never read back (`compute-shader-vfx`; this skill owns the CPU-readable `Mesh`).
- **Not for:** job scheduling and allocator lifetime (`unity-job-system-and-burst`).
- **Not for:** which mesh or material a game state shows (Shared Core, `csharp-engineer`).
- **Docs:** https://docs.unity3d.com/Manual/mesh.html and /ScriptReference/Mesh.html — unversioned (current release; components page says 6.5).
  - **Editor version:** check the project's.

## References
- **[mesh-anatomy.md](references/mesh-anatomy.md):** A mesh renders invisible, inverted, flat or throws on assignment; choosing `indexFormat`, topology, submeshes.
- **[mesh-scripting-api.md](references/mesh-scripting-api.md):** Choosing an authoring tier, or writing a quad or primitive.
- **[advanced-mesh-api-jobs.md](references/advanced-mesh-api-jobs.md):** Profiling shows per-frame or large-scale generation must leave the main thread.
- **[mesh-components.md](references/mesh-components.md):** Wiring `MeshFilter`/`MeshRenderer`, material count vs submeshes, or checking a mesh in the Inspector/Preview.
- **[mesh-optimization.md](references/mesh-optimization.md):** Mesh memory, Read/Write, compression, `CombineMeshes`, `MarkDynamic` or `Optimize`.

## Steps
1. **Pick the authoring tier by update frequency:** per [mesh-scripting-api.md](references/mesh-scripting-api.md).
   - **One-off setup:** legacy properties.
   - **Occasional edits:** `Set*` methods.
   - **Profiling justifies it:** `MeshDataArray`, and only then.
2. **Every vertex array must equal the vertex count:** a mismatch throws.
3. **Switch `indexFormat` to `UInt32` before the vertex count can exceed 65535:** not after corruption.
4. **After any vertex change, set or recalculate `bounds`, normals and tangents:**
   - **Stale bounds:** break culling silently.
   - **Unset normals:** light flat or black.
5. **`MarkDynamic` before the first write on a mesh rewritten every frame:** never on one that is not ([mesh-optimization.md](references/mesh-optimization.md)).
6. **Keep `MeshRenderer.materials` count equal to `subMeshCount`:** per [mesh-components.md](references/mesh-components.md).
7. **Set Read/Write Enabled and compression:** by whether runtime code reads or measures the data back.
8. **`CombineMeshes` over static batching:** only when per-object culling can be lost.
9. **"Renders wrong" without a named layer:** geometry, normals, UVs, material and lighting have different owners.
   - **Before editing data:** state the assumption.
10. **Confirm a data or cost claim:** in the Mesh Preview panel or the Profiler (`unity-profiler-diagnostics`) before reporting it.

## Never
- **Call a `Mesh` getter or `AcquireReadOnlyMeshData` on a mesh with `isReadable` false at runtime:** it throws `InvalidOperationException`.
- **Use `MeshDataArray`:** for a one-off or `Start()`-time mesh.
- **Decide in Client code which state a mesh or material shows:** Core resolves the state; the client only maps state to asset.

## Output
```
## 3D Mesh Work — <mesh>
- Technique: <legacy / Set* / MeshDataArray+Jobs> — why
- Vertex data: <count>, indexFormat <UInt16/UInt32>, attributes <list>
- Core boundary: <what Core decides vs what this builds>
- Bounds/normals/tangents: <how set>
- Submeshes/materials: subMeshCount <n>, materials match <yes/no>
- Read/Write & compression: <Read/Write on/off + why>, Mesh Compression <level>, Vertex Compression <mask/n.a.>
- Combine/batching: <CombineMeshes / static batching / neither>
```

## Example
- **"Use MeshDataArray for this one-off mesh, it is the fastest API":** declined — a `Start()`-time mesh gains nothing.
  - **Did instead:** used `SetVertices`/`SetTriangles`, explicit `Vector3.up` normals and one `RecalculateBounds`.
