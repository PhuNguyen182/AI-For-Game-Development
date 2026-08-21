# Mesh Components — MeshFilter, MeshRenderer, Inspector & Preview

Sources: [Mesh components reference](https://docs.unity3d.com/Manual/mesh-components-reference.html), [Mesh Filter component reference](https://docs.unity3d.com/Manual/class-MeshFilter.html), [Mesh Renderer component reference](https://docs.unity3d.com/Manual/class-MeshRenderer.html), [Mesh asset Inspector window reference](https://docs.unity3d.com/Manual/class-Mesh.html), [View mesh data visualizations](https://docs.unity3d.com/Manual/view-mesh-data-visualizations.html), [Select the mesh asset of a GameObject](https://docs.unity3d.com/Manual/mesh-select-mesh-asset.html).
Covers: SKILL.md §4 — **"Keep `MeshRenderer.materials` in sync with `MeshFilter.mesh`'s `subMeshCount`"**, **"Confirm any rendering-cost or mesh-data claim with the Profiler or the Mesh asset's Preview panel before reporting it"**.

The component pair every static mesh is wired through, the Inspector
window that shows a mesh asset's own statistics, and the Preview panel
used to confirm a fix instead of asserting it. `SkinnedMeshRenderer` is
listed only for the boundary it marks — its actual configuration is
`unity-animation`'s.

## Contents

- [MeshFilter](#meshfilter)
- [MeshRenderer](#meshrenderer)
- [SkinnedMeshRenderer boundary](#skinnedmeshrenderer-boundary)
- [Mesh asset Inspector](#mesh-asset-inspector)
- [Mesh Preview panel](#mesh-preview-panel)

## MeshFilter

| Member | What it decides | Source |
|---|---|---|
| `MeshFilter.mesh` | The `Mesh` instance a sibling `MeshRenderer` renders; a `MeshRenderer` alone with no `MeshFilter` renders nothing | [Mesh Filter component reference](https://docs.unity3d.com/Manual/class-MeshFilter.html) |
| Changing the referenced mesh | Does **not** update the sibling `MeshRenderer`'s material list or any other of its settings — a mismatch against the new mesh's `subMeshCount` is the caller's responsibility | [Mesh Filter component reference](https://docs.unity3d.com/Manual/class-MeshFilter.html) |
| `MeshFilter.mesh` vs `sharedMesh` | Reading `mesh` at runtime instantiates a private copy if none exists yet; `sharedMesh` reads/writes the shared asset directly, the same instance-vs-shared distinction `coding-principles.md`'s Memory discipline guidance applies to materials | [MeshFilter.mesh](https://docs.unity3d.com/ScriptReference/MeshFilter-mesh.html) |

## MeshRenderer

| Property | What it decides | Source |
|---|---|---|
| `Materials` (`Size`/`Element`) | One slot per submesh is the intended mapping; more materials than submeshes stacks extras onto the last submesh, which can hurt performance if they're opaque | [Mesh Renderer component reference](https://docs.unity3d.com/Manual/class-MeshRenderer.html) |
| `Cast Shadows` | On / Off / Two Sided / Shadows Only — whether and how this renderer casts a shadow from a suitable light | [Mesh Renderer component reference](https://docs.unity3d.com/Manual/class-MeshRenderer.html) |
| `Receive Shadows` | Whether shadows cast by other objects appear on this renderer; has no effect without Baked or Realtime GI enabled | [Mesh Renderer component reference](https://docs.unity3d.com/Manual/class-MeshRenderer.html) |
| `Light Probes` | Off / Blend Probes / Use Proxy Volume / Custom Provided — how this renderer samples baked indirect lighting | [Mesh Renderer component reference](https://docs.unity3d.com/Manual/class-MeshRenderer.html) |
| `Reflection Probes` | Off / Blend Probes / Blend Probes and Skybox / Simple — how this renderer samples reflection data | [Mesh Renderer component reference](https://docs.unity3d.com/Manual/class-MeshRenderer.html) |
| `Motion Vectors` | Camera Motion Only / Per Object Motion / Force No Motion — per-pixel motion tracking for motion blur and similar effects | [Mesh Renderer component reference](https://docs.unity3d.com/Manual/class-MeshRenderer.html) |
| Mesh LOD section (`LOD Override`, `Override Level`, `LOD Selection Bias`) | Forces or biases which Mesh LOD level renders — the authoring workflow behind it belongs to `unity-engineer`/`tech-lead-performance`, per [root-links.md](root-links.md) | [Mesh LOD](https://docs.unity3d.com/Manual/lod/mesh-lod-introduction.html) |

## SkinnedMeshRenderer boundary

| Concept | Owner | Source |
|---|---|---|
| `Root Bone`, `Quality`, `Update When Offscreen`, blend-shape weights | `unity-animation` | [Skinned Mesh Renderer component reference](https://docs.unity3d.com/Manual/class-SkinnedMeshRenderer.html) |
| Requires no `MeshFilter` — the deformed mesh is generated per frame instead of read from one | `unity-animation` | [Skinned Mesh Renderer component reference](https://docs.unity3d.com/Manual/class-SkinnedMeshRenderer.html) |

## Mesh asset Inspector

| Field | What it shows | Source |
|---|---|---|
| Vertices / Indices counts | Total counts plus on-disk storage and runtime memory used by vertex and index data — the first place to confirm a generator produced the expected geometry | [Mesh asset Inspector window reference](https://docs.unity3d.com/Manual/class-Mesh.html) |
| Bounds Center / Bounds Size | The mesh's bounding box, useful for confirming `RecalculateBounds` actually ran | [Mesh asset Inspector window reference](https://docs.unity3d.com/Manual/class-Mesh.html) |
| Read/Write Enabled | Whether runtime code can read this mesh's data back — see [mesh-optimization.md](mesh-optimization.md) | [Mesh.isReadable](https://docs.unity3d.com/ScriptReference/Mesh-isReadable.html) |

## Mesh Preview panel

| View mode | Shows | Source |
|---|---|---|
| Shaded | Basic lit view, one color per submesh | [View mesh data visualizations](https://docs.unity3d.com/Manual/view-mesh-data-visualizations.html) |
| UV Checker / UV Layout | A checkerboard overlay, or the unwrapped 2D UV map | [View mesh data visualizations](https://docs.unity3d.com/Manual/view-mesh-data-visualizations.html) |
| Normals / Tangents | Color-coded direction visualization — the direct way to confirm a winding-order or normal fix actually took effect | [View mesh data visualizations](https://docs.unity3d.com/Manual/view-mesh-data-visualizations.html) |
| Vertex Color | Vertex colors rendered independent of any material | [View mesh data visualizations](https://docs.unity3d.com/Manual/view-mesh-data-visualizations.html) |

Every mode but UV Layout supports a wireframe toggle. Press `F` while
hovering the preview to reset zoom/pan. This panel, together with the
Profiler per `performance-and-algorithms.md`'s Verification section, is
what turns a mesh-data claim into a measured one.
