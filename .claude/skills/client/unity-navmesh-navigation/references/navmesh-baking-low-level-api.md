# NavMesh Baking — Low-Level Built-in API

The `UnityEngine.AI` types behind procedural/scripted NavMesh building — what `NavMeshSurface` (see [navmesh-components-surface-and-modifiers.md](navmesh-components-surface-and-modifiers.md)) calls internally, and what a fully custom runtime-generation pipeline would call directly instead of using the package component. Reach for this layer only when `NavMeshSurface`'s declarative Inspector workflow genuinely doesn't fit (highly custom procedural source geometry, a bespoke streaming scheme) — per KISS in `coding-principles.md`, prefer `NavMeshSurface` for anything an Inspector component can already express.

## `NavMeshBuilder` (static class)

[Scripting API — NavMeshBuilder](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/UnityEngine.AI.NavMeshBuilder.html) — "Navigation mesh builder interface." All-static.

| Method | Purpose |
|---|---|
| `CollectSources(...)` | Convenience method that builds a `List<NavMeshBuildSource>` from current scene geometry (render meshes or physics colliders, per [`NavMeshCollectGeometry`](#navmeshcollectgeometry-enum)) — the same collection step `NavMeshSurface` runs internally. |
| `BuildNavMeshData(...)` | Builds a `NavMeshData` object from a list of build sources plus `NavMeshBuildSettings`. |
| `UpdateNavMeshData(...)` | Synchronously, incrementally updates an existing `NavMeshData` from sources — cheaper than a full rebuild when only part of the world changed. |
| `UpdateNavMeshDataAsync(...)` | Same as above, asynchronously — the primitive behind `NavMeshSurface.UpdateNavMesh()`'s `AsyncOperation` return. |
| `Cancel(NavMeshData)` | Cancels an in-flight async update targeting the given `NavMeshData`. |

## `NavMeshData` (class)

[Scripting API — NavMeshData](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshData.html) — "Contains and represents NavMesh data." Add to the live system via `NavMesh.AddNavMeshData()`.

| Member | Type | Description |
|---|---|---|
| `position` | `Vector3` | World position (get/set). |
| `rotation` | `Quaternion` | Orientation (get/set). |
| `sourceBounds` | `Bounds` (RO) | Bounding volume of the input geometry this data was built from. |
| `NavMeshData()` | constructor | For the default agent type. |

## `NavMeshDataInstance` (struct)

[Scripting API — NavMeshDataInstance](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshDataInstance.html) — represents an added `NavMeshData` inside the running navigation system, the handle used to remove it later.

| Member | Description |
|---|---|
| `owner` | `Object`, get/set — owning object association. |
| `valid` | `bool` (RO) — whether this instance is currently active in the system. |
| `Remove()` | Removes this instance from the system. |

This is the mechanism behind streaming a baked NavMesh chunk in/out at runtime: bake or load a `NavMeshData`, `NavMesh.AddNavMeshData()` it in (returns a `NavMeshDataInstance`), later `.Remove()` it (or `NavMesh.RemoveNavMeshData()`) when the chunk unloads.

## `NavMeshBuildSettings` (struct)

[Scripting API — NavMeshBuildSettings](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshBuildSettings.html) — per-agent-type build configuration; obtain a fresh one via `NavMesh.CreateSettings()` or read an existing agent type's via `NavMesh.GetSettingsByID()`.

| Field | Type | Description |
|---|---|---|
| `agentTypeID` | `int` | Which agent type this settings entry bakes for. |
| `agentRadius` / `agentHeight` | `float` | Agent dimensions, world units — mirrors the Navigation window's Agents tab. |
| `agentSlope` | `float` | Max walkable slope angle, degrees. |
| `agentClimb` | `float` | Max vertical step size. |
| `ledgeDropHeight` | `float` | Max agent drop height (for auto-generated drop-down links). |
| `maxJumpAcrossDistance` | `float` | Max agent jump-across distance (for auto-generated jump links). |
| `minRegionArea` | `float` | Approx. minimum area for an individual NavMesh region — smaller disconnected islands below this are discarded. |
| `overrideVoxelSize` / `voxelSize` | `bool` / `float` | Custom voxel size toggle + value, world units. Default is roughly ⅓ of agent radius; smaller = more accurate, slower bake. |
| `overrideTileSize` / `tileSize` | `bool` / `float` | Custom tile size toggle + value, voxel units. Default 256 voxels/tile; affects memory and how well the build parallelizes. |
| `preserveTilesOutsideBounds` | `bool` | Keep NavMesh sections outside the current build bounds instead of discarding them — relevant for incremental/partial rebuilds. |
| `buildHeightMesh` | `bool` | Build supplementary height-mesh data for accurate placement on stairs/slopes — see [HeightMesh](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/HeightMesh.html) in the package manual. |
| `maxJobWorkers` | `int` | Max worker threads used for the build. |
| `debug` | [`NavMeshBuildDebugSettings`](#navmeshbuilddebugsettings-struct) | Debug-data collection options for this build. |
| `ValidationReport()` | method | Validates the settings struct's own field combination. |

## `NavMeshBuildSource` (struct)

[Scripting API — NavMeshBuildSource](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshBuildSource.html) — one entry in the input list the builder consumes.

| Field | Type | Description |
|---|---|---|
| `shape` | [`NavMeshBuildSourceShape`](#navmeshbuildsourceshape-enum) | Mesh / Terrain / Box / Sphere / Capsule / ModifierBox. |
| `sourceObject` | `Object` | The `Mesh` or `TerrainData` object, for those source types. |
| `transform` | `Matrix4x4` | Local-to-world transform. |
| `size` | `Vector3` | Shape dimensions. |
| `area` | `int` | Surface area type assigned to this source. |
| `component` | `Component` | Owning component if any, else `null`. |
| `generateLinks` | `bool` | Whether automatic link generation runs for this source. |

**Constraint**: a runtime `Mesh` source must have read/write enabled, and mesh sources must stay within 100,000 units of the world origin and not exceed 100,000 units on any axis-aligned dimension. Build a source list manually, or via `NavMeshBuilder.CollectSources()`.

### `NavMeshBuildSourceShape` (enum)

[Scripting API — NavMeshBuildSourceShape](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshBuildSourceShape.html) — `Mesh`, `Terrain`, `Box`, `Sphere`, `Capsule`, `ModifierBox`.

## `NavMeshBuildMarkup` (struct)

[Scripting API — NavMeshBuildMarkup](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshBuildMarkup.html) — per-object treatment when collecting sources for a build; the scripted equivalent of what `NavMeshModifier` configures declaratively (see [navmesh-components-surface-and-modifiers.md](navmesh-components-surface-and-modifiers.md)).

| Field | Type | Description |
|---|---|---|
| `root` | `GameObject` | Target object (+children) the markup applies to. |
| `overrideArea` / `area` | `bool` / `int` | Enable an area-type override for target+children, and the area to use. |
| `overrideIgnore` / `ignoreFromBuild` | `bool` / `bool` | Enable, and apply, exclusion of target+children from the build. |
| `overrideGenerateLinks` / `generateLinks` | `bool` / `bool` | Enable, and apply, an override of the default link-generation condition. |
| `applyToChildren` | `bool` | Whether children inherit these markup settings. |

## `NavMeshBuildDebugSettings` (struct)

[Scripting API — NavMeshBuildDebugSettings](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshBuildDebugSettings.html) — controls which intermediate build-stage data is retained for visualization. Build proceeds through 7 sequential stages (triangle decomposition through the final refined triangulated mesh); debug visualizations are session-only (not saved to disk), and debug data is **not** collected for local NavMesh patches recomputed due to `NavMeshObstacle` carving. Can be large despite internal compression — don't leave a verbose flag set enabled outside an active debugging session.

| Field | Type | Description |
|---|---|---|
| `flags` | [`NavMeshBuildDebugFlags`](#navmeshbuilddebugflags-enum) | Which debug data types to collect. |

### `NavMeshBuildDebugFlags` (enum, bitmask)

[Scripting API — NavMeshBuildDebugFlags](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshBuildDebugFlags.html)

- `None` — no debug data.
- `InputGeometry` — triangles of all base geometry.
- `Voxels` — voxelized walkable/unwalkable rasterization.
- `Regions` — segmentation of traversable surfaces into smaller regions.
- `RawContours` — contours precisely following each region's edges.
- `SimplifiedContours` — same, simplified (fewer vertices, straighter edges).
- `PolygonMeshes` — convex polygon meshes within unified adjacent-region contours.
- `PolygonMeshesDetail` — triangulated meshes with height detail approximating source geometry.
- `All` — everything above.

## `NavMeshCollectGeometry` (enum)

[Scripting API — NavMeshCollectGeometry](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshCollectGeometry.html) — used with `NavMeshBuilder.CollectSources` and as the type behind `NavMeshSurface.useGeometry` (the package reuses this built-in enum rather than defining its own).

- `RenderMeshes` — collect from rendered geometry (MeshRenderers + Terrain).
- `PhysicsColliders` — collect from the 3D physics collision representation (Colliders + Terrain).

No Obsolete/Deprecated/Experimental markers on any type in this file as of Unity 6000.5.
