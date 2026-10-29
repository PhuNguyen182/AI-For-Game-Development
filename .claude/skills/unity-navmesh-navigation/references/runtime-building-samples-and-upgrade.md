# Runtime Building, Samples, Upgrading

The package has no runtime-building manual page; the workflow is assembled from the `NavMeshSurface` API and the samples (manual page `Samples`).

## Entry points
| Entry point | Use |
|---|---|
| Async incremental `Update` | Rebuilds only affected regions without the frame stall; default during play |
| Synchronous `Build` | Blocks; behind a loading screen only |
| Attach / detach data | Brings pre-baked meshes in and out without building; cheapest, and what streaming uses |
| Obstacle instead | Something moving more often than a rebuild is worth ([navmesh-obstacles-and-avoidance.md](navmesh-obstacles-and-avoidance.md)) |
| Link toggle instead | A shortcut that only sometimes opens costs nothing next to a rebuild ([navmesh-links.md](navmesh-links.md)) |

Agents holding a path across a rebuilt region do not notice: the path is stale, not invalid, so check `isPathStale` ([navmesh-agent.md](navmesh-agent.md)).

## Samples
Multiple agent sizes, Drop plank (walkable geometry added at play), Free orientation (non-horizontal surface), Sliding window (infinite and terrain; bounded build region following the agent), Modify mesh, Dungeon (pre-baked tiles joined by links with traversal animation), Height mesh, Cornering speed control. For streaming or procedural work start from the sliding-window samples; they solve region-boundary and link-stitching.

## Upgrading from the legacy system
- The Navigation Updater converts scene and prefab data, including legacy link components.
- Script references are not updated: code naming the legacy component compiles against a class stripped of its members.
- Several link members were renamed; old names remain as obsolete aliases ([navmesh-links.md](navmesh-links.md)).
- The legacy system stored the mesh with the scene; now it lives on a surface component, so an upgraded scene has no mesh until a surface exists and is baked.
