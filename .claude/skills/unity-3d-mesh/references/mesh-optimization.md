# Mesh Optimization — Compression, Read/Write, Combining & Dynamic Meshes

Sources: [Compressing mesh data for optimization](https://docs.unity3d.com/Manual/compressing-mesh-data-optimization.html), [Configure mesh compression](https://docs.unity3d.com/Manual/configure-mesh-compression.html), [Configure vertex compression](https://docs.unity3d.com/Manual/configure-vertex-compression.html), [Manually combining meshes](https://docs.unity3d.com/Manual/combining-meshes.html), [Mesh.CombineMeshes](https://docs.unity3d.com/ScriptReference/Mesh.CombineMeshes.html).
Covers: SKILL.md §4 — **"Call `MarkDynamic` before the first write on a mesh that will be rewritten every frame, and never on one that will not"**, **"Decide Read/Write Enabled and mesh/vertex compression by whether runtime code ever reads the data back"**, **"Choose `CombineMeshes` over static batching only when per-object culling can be sacrificed"**.

The three cost knobs that apply after a mesh's geometry is already
correct: how much its data costs at rest (compression, Read/Write
Enabled), how it costs to draw (combine vs. batch), and how it costs to
update (`MarkDynamic`). None of these are safe defaults to leave
unexamined on a mesh a gameplay system depends on.

## Contents

- [Mesh compression (import-time)](#mesh-compression-import-time)
- [Vertex compression (project setting)](#vertex-compression-project-setting)
- [Read/Write Enabled](#readwrite-enabled)
- [Combining meshes vs. static batching](#combining-meshes-vs-static-batching)
- [MarkDynamic and Optimize](#markdynamic-and-optimize)

## Mesh compression (import-time)

| Setting | What it decides | Source |
|---|---|---|
| Model Import Settings → Meshes → Mesh Compression (`Off`/`Low`/`Medium`/`High`, or `ModelImporterMeshCompression` from script) | Compresses vertex/normal/tangent/UV precision to shrink file size; higher settings shrink more at the cost of precision | [Configure mesh compression](https://docs.unity3d.com/Manual/configure-mesh-compression.html) |
| Compression ratio by channel (approximate, Low → High) | Vertices 1.6×→3.2×, Normals 4.6×→7.4×, Tangents 4.4×→6.7×, UVs 2.0×→4.0× | [Configure mesh compression](https://docs.unity3d.com/Manual/configure-mesh-compression.html) |
| When to leave it `Off` | Any mesh a gameplay system reads back and measures exactly — precision loss from compression is silent, not an error | synthesized from [Configure mesh compression](https://docs.unity3d.com/Manual/configure-mesh-compression.html) |

## Vertex compression (project setting)

| Setting | What it decides | Source |
|---|---|---|
| Project Settings → Player → Other Settings → Optimization → Vertex Compression | A per-channel mask (`Position`, `Normal`, `Tangent`, `Color`, `Tex Coord 0–3`) converting those channels to FP16 at runtime, independent of import-time Mesh Compression | [Configure vertex compression](https://docs.unity3d.com/Manual/configure-vertex-compression.html) |
| Default mask | `Normal`, `Tangent`, `Tex Coord 0`, `Tex Coord 2`, `Tex Coord 3` — `Position` and `Tex Coord 1` (lightmap UVs) are excluded by default because compressing them is more likely to visibly distort geometry | [Configure vertex compression](https://docs.unity3d.com/Manual/configure-vertex-compression.html) |
| Eligibility | Only applies when Read/Write Enabled is off, the mesh is not skinned, the target platform supports FP16, Mesh Compression is `Off`, and the mesh is not (or has disabled) dynamic batching | [Configure vertex compression](https://docs.unity3d.com/Manual/configure-vertex-compression.html) |

## Read/Write Enabled

| Rule | Consequence | Source |
|---|---|---|
| `isReadable` false (Read/Write Enabled off) | Any runtime read of vertex data — the legacy properties, `Get*` methods, or `AcquireReadOnlyMeshData` — throws `InvalidOperationException` | [Mesh.isReadable](https://docs.unity3d.com/ScriptReference/Mesh-isReadable.html) |
| Turning it off when nothing reads back | Reduces the mesh's runtime memory footprint — the correct default for a mesh nothing but the GPU ever touches | [Mesh asset Inspector window reference](https://docs.unity3d.com/Manual/class-Mesh.html) |

## Combining meshes vs. static batching

| Technique | Trade-off | Source |
|---|---|---|
| `Mesh.CombineMeshes` (manual combine) | One draw call for the combined result, but if any part of it is visible the *entire* combined mesh draws — no per-object culling survives the combine | [Manually combining meshes](https://docs.unity3d.com/Manual/combining-meshes.html) |
| Static batching | Also collapses draw calls for static geometry, but preserves individual culling — the default choice when culling still matters | [Manually combining meshes](https://docs.unity3d.com/Manual/combining-meshes.html) |
| `CombineMeshes(combine, mergeSubMeshes, useMatrices, hasLightmapData)` | `mergeSubMeshes = true` folds every input into one submesh — correct only when every input shares material and topology; `false` keeps each input as its own submesh | [Mesh.CombineMeshes](https://docs.unity3d.com/ScriptReference/Mesh.CombineMeshes.html) |
| When to combine anyway | A tightly-grouped, always-co-visible static cluster (a cupboard with drawers) where the lost culling costs nothing in practice | [Manually combining meshes](https://docs.unity3d.com/Manual/combining-meshes.html) |

## MarkDynamic and Optimize

| Member | What it does | Use when | Source |
|---|---|---|---|
| `Mesh.MarkDynamic` | Hints to Unity that this mesh's geometry will be updated frequently, so it should pick a GPU buffer strategy suited to frequent writes | Called once, before the first update, on a mesh that is rewritten every frame or close to it | [Mesh](https://docs.unity3d.com/ScriptReference/Mesh.html) |
| `Mesh.Optimize`, `OptimizeIndexBuffers`, `OptimizeReorderVertexBuffer` | Reorders vertex/index data to improve rendering performance | On a finished, static mesh — never on one still being edited, since the reordering invalidates any external index assumptions made before it ran | [Mesh](https://docs.unity3d.com/ScriptReference/Mesh.html) |

**Critical caveat**: calling `MarkDynamic` on a mesh that never actually
changes wastes the GPU memory strategy it reserves for updates; calling
`Optimize` on a mesh that is still being procedurally rebuilt wastes the
optimization pass on data about to be replaced. Match each call to the
mesh's real lifecycle, not to habit.
