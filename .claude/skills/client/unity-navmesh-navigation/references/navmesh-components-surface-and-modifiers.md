# Surface and Modifiers — the declarative baking layer

Sources: [NavMesh Surface](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavMeshSurface.html), [Create a NavMesh](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/CreateNavMesh.html), [NavMeshSurface API](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/api/Unity.AI.Navigation.NavMeshSurface.html), [NavMesh Modifier](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavMeshModifier.html), [NavMesh Modifier Volume](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavMeshModifierVolume.html), [CollectObjects](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/api/Unity.AI.Navigation.CollectObjects.html), [HeightMesh](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/HeightMesh.html).
Covers: SKILL.md §4 — **"Bake through `NavMeshSurface` before reaching for the low-level builder"**, **"Override areas per object and per region with modifiers rather than by editing geometry"**.

The components that turn scene geometry into a navigable mesh, and the two
ways to change what a bake sees without touching the art. Procedural geometry
with no scene object goes to [navmesh-baking-low-level-api.md](navmesh-baking-low-level-api.md) instead.

## NavMeshSurface

| Field | What it decides | Source |
|---|---|---|
| Agent type | Which agent type this surface's mesh serves — one surface bakes one type, so several types mean several surfaces and several meshes | [NavMesh Surface](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavMeshSurface.html) |
| Collect objects | Whether sources come from the whole scene, a bounding volume, the component's own children, or only objects carrying a modifier | [CollectObjects](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/api/Unity.AI.Navigation.CollectObjects.html) |
| Use geometry | Render meshes or physics colliders as the source — colliders usually match what the player can actually walk on, render meshes match what they see | [NavMesh Surface](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavMeshSurface.html) |
| Layer mask | Filters source geometry by layer before anything else is considered | [NavMesh Surface](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavMeshSurface.html) |
| Default area | The area assigned to geometry no modifier claims | [NavMesh Surface](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavMeshSurface.html) |
| Voxel size override | Defaults to a fraction of agent radius; smaller resolves narrow gaps and thin ledges at a directly higher bake cost | [NavMesh Surface](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavMeshSurface.html) |
| Tile size override | Governs memory and how the build parallelises; it also decides how much has to be rebuilt when one region changes | [NavMesh Surface](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavMeshSurface.html) |
| Minimum region area | Discards disconnected islands below this size — the setting that removes navigable slivers on top of props and behind decor | [NavMesh Surface](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavMeshSurface.html) |
| Build Height Mesh | Adds a supplementary surface for accurate placement on stairs and slopes, where the flat mesh otherwise floats or sinks agents | [HeightMesh](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/HeightMesh.html) |

| Method | Effect | Source |
|---|---|---|
| Build | Synchronous full rebuild — what the Inspector's bake button calls, and what a loading screen can afford | [NavMeshSurface API](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/api/Unity.AI.Navigation.NavMeshSurface.html) |
| Update | Asynchronous incremental rebuild limited to affected regions — the runtime entry point, see [runtime-building-samples-and-upgrade.md](runtime-building-samples-and-upgrade.md) | [NavMeshSurface API](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/api/Unity.AI.Navigation.NavMeshSurface.html) |
| Add and remove data | Attaches or detaches this surface's baked data from the live system without rebuilding it — the streaming mechanism | [NavMeshSurface API](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/api/Unity.AI.Navigation.NavMeshSurface.html) |
| Get build settings | Snapshots the current configuration, for handing to the low-level builder | [NavMeshSurface API](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/api/Unity.AI.Navigation.NavMeshSurface.html) |

**Critical caveat**: agents and obstacles are excluded from the bake by
design — they are actors on the mesh, not geometry in it. A character that
should also be permanent level geometry needs real geometry, not a component.

## Modifiers

| Component | What it decides | Source |
|---|---|---|
| NavMesh Modifier | Overrides the area of one object and its children, or excludes it from the build entirely, optionally scoped to specific agent types | [NavMesh Modifier](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavMeshModifier.html) |
| NavMesh Modifier Volume | Overrides the area inside a box that has no geometry of its own — the way to mark a hazard, a water line, or a preferred lane without modelling one | [NavMesh Modifier Volume](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavMeshModifierVolume.html) |
| Per-agent-type scoping | Both modifiers can apply to one agent type only, which is how the same geometry is walkable for a small agent and excluded for a large one | [NavMesh Modifier](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavMeshModifier.html) |
| Collect mode interaction | With the collect mode set to marked objects only, a modifier is what makes an object a source at all rather than merely changing its area | [CollectObjects](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/api/Unity.AI.Navigation.CollectObjects.html) |

| Rule | Consequence | Source |
|---|---|---|
| Re-bake after any change | Geometry, modifier and agent-type edits do not update the mesh; a stale bake is visually identical to a correct one | [Create a NavMesh](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/CreateNavMesh.html) |
| Clearing a surface | The Inspector's clear action deletes the stored asset; removing the component without clearing leaves an orphaned asset behind | [NavMesh Surface](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavMeshSurface.html) |
