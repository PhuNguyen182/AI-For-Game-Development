# Surface and Modifiers

Procedural geometry with no scene object goes to [navmesh-baking-low-level-api.md](navmesh-baking-low-level-api.md).

## NavMeshSurface fields
| Field | Decides |
|---|---|
| Agent type | One surface bakes one type; several types need several surfaces and meshes |
| Collect objects (`CollectObjects`) | Sources from whole scene, a bounding volume, the component's children, or only objects carrying a modifier |
| Use geometry | Render meshes (what is seen) or physics colliders (usually what is walkable) |
| Layer mask | Filters source geometry first |
| Default area | Area for geometry no modifier claims |
| Voxel size override | Defaults to a fraction of agent radius; smaller resolves narrow gaps at proportionally higher bake cost |
| Tile size override | Memory, build parallelism, and how much rebuilds when one region changes |
| Minimum region area | Discards small disconnected islands (slivers on props and behind decor) |
| Build Height Mesh | Accurate placement on stairs/slopes ([agent-types-areas-and-navigation-window.md](agent-types-areas-and-navigation-window.md)) |

## NavMeshSurface methods
| Method | Effect |
|---|---|
| Build | Synchronous full rebuild (Inspector bake button); fine behind a loading screen |
| Update | Async incremental rebuild of affected regions; the runtime entry point ([runtime-building-samples-and-upgrade.md](runtime-building-samples-and-upgrade.md)) |
| Add / remove data | Attach or detach baked data without rebuilding; the streaming mechanism |
| Get build settings | Snapshot for the low-level builder |

Agents and obstacles are excluded from the bake by design; permanent geometry needs real geometry.

## Modifiers
- **NavMesh Modifier**: overrides the area of one object and its children, or excludes it, optionally scoped to specific agent types (walkable for a small agent, excluded for a large one).
- **NavMesh Modifier Volume**: overrides the area inside a box with no geometry of its own (hazard, water line, preferred lane).
- With collect mode "marked objects only", a modifier is what makes an object a source at all.

## Rules
- Geometry, modifier and agent-type edits do not update the mesh until re-baked.
- The Inspector's clear action deletes the stored asset; removing the component without clearing leaves an orphaned asset.
