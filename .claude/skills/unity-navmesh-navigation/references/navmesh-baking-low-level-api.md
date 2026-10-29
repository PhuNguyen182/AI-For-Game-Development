# Low-Level Baking — NavMeshBuilder

Use only when [navmesh-components-surface-and-modifiers.md](navmesh-components-surface-and-modifiers.md) cannot see the geometry: runtime-generated geometry with no GameObject, sources assembled under custom rules (the component filters only by layer, volume, hierarchy, modifier), or data built off the main thread and applied later. Anything a surface expresses stays on the surface.

| Type | Role |
|---|---|
| `NavMeshBuilder` | Static: collect sources, build and update data, sync or async |
| `NavMeshData` | The built mesh, caller-owned; inert until added to the navigation system |
| `NavMeshDataInstance` | Handle from adding data and the only way to remove it; losing it leaks the mesh |
| `NavMeshBuildSettings` | Agent dimensions, voxel/tile size, region thresholds (same knobs as the surface) |
| `NavMeshBuildSource` | One mesh, terrain or primitive with transform and area |
| `NavMeshBuildMarkup` | Per-object overrides during collection; scripted modifier |

## Constraints
- Runtime mesh sources need Read/Write enabled; otherwise they contribute nothing, silently.
- Sources must stay within a large but finite distance of the world origin and finite extent per axis; build a far-flung world in shifted chunks.
- Data lifetime is manual: add to use, remove to free.
- Settings can express a combination that yields an empty mesh. A build that returned is not a mesh that exists; validate settings and confirm agents have somewhere to stand.
