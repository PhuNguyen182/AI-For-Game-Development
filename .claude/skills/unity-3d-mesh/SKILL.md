---
name: unity-3d-mesh
description: >
  Unity built-in 3D mesh authoring — the `Mesh` class (`vertices`,
  `triangles`, `normals`, `tangents`, `colors`, `uv` through `uv8`,
  `subMeshCount`, `bounds`, `indexFormat`), `SetVertices`, `SetTriangles`,
  `SetIndices`, `SetVertexBufferParams`, `SetIndexBufferParams`, and
  `SetSubMesh`, the Job System `MeshDataArray` and `MeshData` via
  `AcquireReadOnlyMeshData` and `AllocateWritableMeshData`,
  `RecalculateNormals`, `RecalculateBounds`, `RecalculateTangents`,
  `MarkDynamic`, `Optimize`, `CombineMeshes`, `MeshFilter`, `MeshRenderer`,
  `GameObject.CreatePrimitive` with `PrimitiveType`, mesh and vertex
  compression, and Read/Write Enabled. Use when building or debugging a
  procedural mesh, a mesh asset, or its Filter/Renderer wiring. Not for:
  skinning, blend shapes, bones (`unity-animation`), `MeshCollider`
  cooking (`unity-3d-physics`), materials/shaders (`shader-authoring`),
  LOD/batching escalation (`unity-engineer`, `tech-lead-performance`),
  model import settings (`unity-engineer`), sprite meshes
  (`unity-2d-sprite`).
---

# Unity 3D Mesh — Anatomy, Scripting API & Procedural Generation

## Bundled resources

### References

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Manual/API roots this skill is pinned to, and the topic→file map | Starting any mesh task, or checking whether a page is in scope |
| [mesh-anatomy.md](references/mesh-anatomy.md) | Vertex attributes, index buffer, topology, bounds, deformable-mesh boundary | A mesh renders wrong, or vertex-array data must be authored |
| [mesh-scripting-api.md](references/mesh-scripting-api.md) | Full `Mesh` class member table, quad-mesh script, primitive GameObjects | Writing or reading a `Mesh` from script |
| [advanced-mesh-api-jobs.md](references/advanced-mesh-api-jobs.md) | `MeshDataArray`/`MeshData`, `AcquireReadOnlyMeshData`, `AllocateWritableMeshData` | Procedural generation must run off the main thread or at scale |
| [mesh-components.md](references/mesh-components.md) | `MeshFilter`, `MeshRenderer` fields, Mesh asset Inspector, Mesh Preview panel | Wiring the component pair, or diagnosing via the Inspector |
| [mesh-optimization.md](references/mesh-optimization.md) | Mesh/vertex compression, Read/Write Enabled, `CombineMeshes`, `MarkDynamic`, `Optimize` | A mesh costs too much memory, too many draw calls, or won't update |

## 1. Objective
Get a `Mesh` asset's data correct, wired to its `MeshFilter`/`MeshRenderer` pair, and built at a cost the chosen technique tier can pay — and rule out the failures this pipeline specialises in: a vertex-index array length mismatch that throws, a stale bounds or missing normal that breaks culling or lighting silently, an `indexFormat` left at `UInt16` while the vertex count crosses 65535, a mesh read at runtime with Read/Write Enabled off, and an Advanced Mesh API reached for before anything justifies its complexity.

## 2. Role
Act as the 3D mesh authoring specialist for the client track — the skill reached for whenever a `Mesh` asset, a procedural mesh, or a `MeshFilter`/`MeshRenderer` pairing must be built, wired, or fixed.

## 3. When to invoke this skill
- Building a mesh procedurally via script — a quad, a plane, custom or voxel-style geometry.
- A mesh renders invisible, inverted, flat-shaded, or textured wrong — normals, winding order, UVs, or bounds are suspect.
- Choosing between legacy `Mesh` properties, `SetVertices`/`Set*` methods, and the Job-System `MeshDataArray` for a given update frequency and scale.
- Configuring Read/Write Enabled, mesh compression, or vertex compression on an imported or generated mesh.
- Deciding `CombineMeshes` versus static batching for a group of static meshes.
- Wiring `MeshFilter` and `MeshRenderer`, or creating a primitive at runtime with `GameObject.CreatePrimitive`.
- Negative trigger: bind poses, blend shapes, bone weights, or a `SkinnedMeshRenderer` — that's `unity-animation`; this skill covers only the static-mesh data that precedes it.
- Negative trigger: `MeshCollider` cooking, convexity, or collision behaviour — that's `unity-3d-physics`, even though the same `Mesh` asset is the input.
- Negative trigger: writing or modifying a shader or material's appearance — that's `shader-authoring`.
- Negative trigger: LOD Group, the Mesh LOD generator, or a batching/GPU-instancing cost that survives this skill's advice — escalate to `unity-engineer` first, `tech-lead-performance` if it persists.
- Negative trigger: FBX or other 3D-model import settings — that's `unity-engineer`'s asset pipeline.
- Negative trigger: `Sprite`/`SpriteRenderer` 2D mesh geometry — that's `unity-2d-sprite`.
- Negative trigger: deciding which mesh or material a game state should show — that's `csharp-engineer`'s Shared Core, per `coding-principles.md`'s Shared Core integrity section.

## 4. How to use this skill
1. **Decide the authoring tier by update frequency and scale before writing any code** — legacy `vertices`/`triangles`/`normals`/`uv` for a one-off setup, `SetVertices`/`SetTriangles`/`SetIndices` for occasional edits, and the Job-System path only once justified, per [mesh-scripting-api.md](references/mesh-scripting-api.md) and [advanced-mesh-api-jobs.md](references/advanced-mesh-api-jobs.md).
2. **Assign vertex data through arrays that all share the vertex count** — normals, UVs, colors, and tangents index by vertex position, and a mismatched array length throws immediately rather than degrading gracefully, per [mesh-anatomy.md](references/mesh-anatomy.md).
3. **Recalculate or set bounds and normals immediately after any vertex change**, per [mesh-scripting-api.md](references/mesh-scripting-api.md) — a stale `bounds` silently breaks culling, and geometry with no normals set reads flat or black under lighting until `RecalculateNormals`/`RecalculateTangents` runs.
4. **Switch `indexFormat` to `UInt32` before the vertex count can exceed 65535**, per [mesh-anatomy.md](references/mesh-anatomy.md) — the `UInt16` default is Unity's own choice for the common case, not a safe ceiling to leave unexamined on procedural or voxel-style geometry.
5. **Reach for the Advanced Mesh API only once profiling justifies its manual buffer-layout cost**, per [advanced-mesh-api-jobs.md](references/advanced-mesh-api-jobs.md) — `MeshDataArray`/`MeshData` earns its complexity for per-frame or large-scale procedural generation off the main thread, not for a `Start()`-time mesh, per KISS/YAGNI in `coding-principles.md`.
6. **Call `MarkDynamic` before the first write on a mesh that will be rewritten every frame, and never on one that will not**, per [mesh-optimization.md](references/mesh-optimization.md) — it reserves a different GPU buffer strategy that costs memory a static mesh never recovers.
7. **Keep `MeshRenderer.materials` in sync with `MeshFilter.mesh`'s `subMeshCount`**, per [mesh-components.md](references/mesh-components.md) — changing the referenced mesh does not resize or reassign the renderer's material list, so a mismatch renders extra submeshes with the last material stacked onto them.
8. **Decide Read/Write Enabled and mesh/vertex compression by whether runtime code ever reads the data back**, per [mesh-optimization.md](references/mesh-optimization.md) — reading vertex data on a mesh with `isReadable` false throws, and compression trades precision for size, which is wrong for a mesh a gameplay system measures exactly.
9. **Choose `CombineMeshes` over static batching only when per-object culling can be sacrificed**, per [mesh-optimization.md](references/mesh-optimization.md) and `performance-and-algorithms.md`'s Rendering & draw calls section — a combined mesh draws in full the moment any part of it is visible.
10. **Keep which mesh or material is active a Shared Core decision, never one made in the rendering layer**, per `coding-principles.md`'s Shared Core integrity section — this skill builds and assigns already-resolved data, it never decides what should be shown.
11. **Confirm any rendering-cost or mesh-data claim with the Profiler or the Mesh asset's Preview panel before reporting it**, per [mesh-components.md](references/mesh-components.md) and `performance-and-algorithms.md`'s Verification section.
12. **When a "renders wrong" report doesn't name its layer, state the assumption before editing data** — geometry, normals, UVs, material, and lighting are four different owners, and guessing wrong edits data another system depends on.

## 5. Specific goals / tasks this skill performs
- Procedural mesh construction via the legacy `Mesh` properties, the modern `Set*` methods, or the Advanced Mesh API.
- Diagnosing invisible, inverted, flat-shaded, or wrongly-textured meshes back to vertex data, normals, or winding order.
- `indexFormat`, bounds, and normal/tangent recalculation correctness.
- `MeshFilter`/`MeshRenderer` wiring and submesh-to-material consistency.
- Read/Write Enabled, mesh compression, and vertex compression configuration.
- `CombineMeshes` versus static batching selection for static geometry groups.
- Primitive GameObject creation via `GameObject.CreatePrimitive`.
- Out of scope: skinning/blend shapes (`unity-animation`), `MeshCollider` physics (`unity-3d-physics`), shaders/materials (`shader-authoring`), LOD/batching escalation (`unity-engineer`, `tech-lead-performance`), model import settings (`unity-engineer`), sprite meshes (`unity-2d-sprite`), gameplay rules (`csharp-engineer`).

## 6. Output format
```
## 3D Mesh Work — <feature/mesh name>
- Technique: <legacy Mesh properties / Set* methods / MeshDataArray+Jobs> — why this tier
- Vertex data: <vertex count>, indexFormat <UInt16/UInt32>, attributes set <list>
- Bounds/normals/tangents: <Recalculate* called, or explicit values, and why>
- Submeshes/materials: subMeshCount <n>, MeshRenderer.materials matches count <yes/no>
- Read/Write & compression: Read/Write Enabled <on/off + why>, Mesh Compression <Off/Low/Medium/High>, Vertex Compression mask <channels or n/a>
- Combine/batching (if applicable): <CombineMeshes / static batching / neither> — culling trade-off noted
- Shared Core boundary: <what Core decides vs what this layer builds/renders>
- Verification: <Mesh Preview/Profiler finding, or "not yet measured">
- Layer: Game.Client.*
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what the delivered solution does not cover — omit this line entirely if there are genuinely none>
- Latent concerns: <failure modes not yet triggered: assumptions that hold only under current conditions, thresholds not yet reached, trade-offs knowingly deferred>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: "Generate a flat ground plane mesh at runtime, sized from a design-time width/depth parameter, once at startup."
- Output: legacy `SetVertices`/`SetTriangles`/`SetUVs` on a new `Mesh` — a one-time `Start()` call is nowhere near the frequency or scale that justifies the Advanced Mesh API. Normals were set explicitly to a repeated `Vector3.up` rather than calling `RecalculateNormals`, since a flat plane's normal is already known and constant. `indexFormat` was left at the `UInt16` default (well under 65535 for a simple grid), and `RecalculateBounds` was called once after assignment. Wired through a new `MeshFilter`/`MeshRenderer` pair with one material matching the mesh's single submesh.

**Example 2**
- Input: "Just use MeshDataArray and the Job System for this one-off mesh too — it's the fastest API Unity has."
- Output: declined. A `Start()`-time mesh with no per-frame rebuild gets nothing from `MeshDataArray`'s manual vertex-buffer-layout and thread-safety machinery — the legacy `Set*` methods are simpler, per KISS/YAGNI in `coding-principles.md`, and equally fast at this scale and frequency. The Job-System path was reserved for the moment a system actually regenerates meshes every frame or at a scale profiling flags as a bottleneck, per [advanced-mesh-api-jobs.md](references/advanced-mesh-api-jobs.md).

**Example 3**
- Input: "A spawned voxel-terrain chunk with over 100,000 vertices renders as garbage geometry."
- Output: the mesh's `indexFormat` had been left at its `UInt16` default while the chunk's vertex count exceeded 65535, corrupting the index buffer once assignment crossed that ceiling. Fixed by setting `mesh.indexFormat = IndexFormat.UInt32` before assigning the vertex array, per [mesh-anatomy.md](references/mesh-anatomy.md). Verified by checking the Mesh asset Inspector's reported vertex/index counts against the generator's expected values.

## 8. Edge cases & guardrails
- Never leave `bounds` stale after modifying vertices — call `RecalculateBounds` or set it explicitly, or culling breaks silently with no console error.
- Never assign `vertices`, `normals`, `uv`, `colors`, or `tangents` arrays of mismatched length — the length must always equal the vertex count, or the assignment throws immediately.
- Never leave `indexFormat` at its `UInt16` default once a mesh's vertex count can cross 65535 — switch to `UInt32` before assignment, not after diagnosing corrupted geometry.
- Never call a `Mesh` getter (`vertices`, `GetVertices`, `GetTriangles`, etc.) on a mesh with `isReadable` false at runtime — it throws `InvalidOperationException`; check `isReadable` or keep Read/Write Enabled on for any mesh runtime code inspects.
- Never reach for `MeshDataArray`/the Job System for a one-off or low-frequency mesh — reserve it for per-frame or large-scale procedural generation a measurement actually justifies.
- Never call `Mesh.CombineMeshes` across meshes that must be individually culled — the combined result draws in full the instant any part of it is visible.
- Never decide which mesh or material a game state uses inside `Game.Client.*` — that decision belongs to `Game.Core.*`, per `coding-principles.md`'s Shared Core integrity section.
- Never claim a mesh or rendering performance fix without a Profiler or Mesh Preview measurement, per `performance-and-algorithms.md`'s Verification section.
- If a "renders wrong" report doesn't identify whether the cause is geometry, normals, UVs, material, or lighting, name the assumption being made before changing any data — the four routes lead to different owners and a wrong guess edits data another system depends on.
