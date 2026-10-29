# Mesh Components

Sources: [MeshFilter](https://docs.unity3d.com/Manual/class-MeshFilter.html) (F), [MeshRenderer](https://docs.unity3d.com/Manual/class-MeshRenderer.html) (R), [Mesh Inspector](https://docs.unity3d.com/Manual/class-Mesh.html), [Preview](https://docs.unity3d.com/Manual/view-mesh-data-visualizations.html).

## MeshFilter / MeshRenderer
- A `MeshRenderer` without a `MeshFilter` renders nothing (F).
- Changing `MeshFilter.mesh` does not resize or reassign the renderer's materials; matching `subMeshCount` is the caller's job (F).
- Materials: one slot per submesh; extra materials stack onto the last submesh and cost performance if opaque (R).
- Reading `MeshFilter.mesh` at runtime instantiates a private copy if none exists; `sharedMesh` touches the shared asset (same trap as `renderer.material`).
- `SkinnedMeshRenderer` needs no `MeshFilter`; its settings are `unity-animation`'s.

## Mesh asset Inspector
Shows vertex/index counts, on-disk and runtime memory, bounds center/size (confirms `RecalculateBounds` ran) and Read/Write Enabled. Check generator output here first.

## Preview panel
Modes: Shaded, UV Checker, UV Layout, Normals, Tangents, Vertex Color. Normals/Tangents confirm a winding or normal fix. All but UV Layout have a wireframe toggle.
