# Package Components — NavMeshSurface, NavMeshModifier, NavMeshModifierVolume

The `com.unity.ai.navigation` package's declarative, Inspector-driven baking layer. Namespace `Unity.AI.Navigation`, assembly `Unity.AI.Navigation.dll`. This is the default, KISS-compliant way to bake a NavMesh — reach for [navmesh-baking-low-level-api.md](navmesh-baking-low-level-api.md)'s raw `NavMeshBuilder` API only when these components genuinely can't express what's needed.

## `NavMeshSurface`

[Manual — NavMesh Surface](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavMeshSurface.html) · [Manual — Create a NavMesh](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/CreateNavMesh.html) · [API — Unity.AI.Navigation.NavMeshSurface](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/api/Unity.AI.Navigation.NavMeshSurface.html)

Bakes and holds one NavMesh for one agent type. `[ExecuteAlways]`, `[DefaultExecutionOrder(-102)]`. Workflow: Add Component → Navigation → NavMesh Surface → configure → **Bake** button. **Dynamic `NavMeshAgent`/`NavMeshObstacle` objects are excluded from the bake by design** — they're runtime actors on top of the mesh, not mesh geometry themselves.

| Member | Type | Description |
|---|---|---|
| `agentTypeID` | `int` | Which agent type this surface's mesh serves. |
| `defaultArea` | `int` | Area assigned to un-modified geometry (Walkable by default; up to 29 custom slots exist). |
| `collectObjects` | [`CollectObjects`](#collectobjects-enum) | Which objects are considered as bake source geometry. |
| `size` / `center` | `Vector3` (local) | Used when `collectObjects == Volume` to define the collection bounding box. |
| `layerMask` | `LayerMask` | Include-layers filter for source geometry. |
| `useGeometry` | `NavMeshCollectGeometry` | Render Meshes vs. Physics Colliders — this is the *built-in* `UnityEngine.AI` enum, reused rather than redefined by the package; see [navmesh-baking-low-level-api.md](navmesh-baking-low-level-api.md#navmeshcollectgeometry-enum). |
| `ignoreNavMeshAgent` / `ignoreNavMeshObstacle` | `bool` | Exclude GameObjects carrying those components from the bake (on by default, per the dynamic-actor note above). |
| `overrideVoxelSize` / `voxelSize` | `bool` / `float` | Default voxel size is ⅓ of agent radius; smaller = more accurate/slower bake. |
| `overrideTileSize` / `tileSize` | `bool` / `int` | Default 256 voxels/tile; affects memory and parallel build behavior. |
| `minRegionArea` | `float` | Discards disconnected NavMesh islands below this surface area. |
| `buildHeightMesh` | `bool` | Generates a supplemental HeightMesh for accurate placement on stairs/slopes — see [HeightMesh.html](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/HeightMesh.html); Sample 8 ("Height Mesh") demonstrates the visible difference. |
| `navMeshData` | `NavMeshData` (RO) | The baked asset this surface currently holds — shows "None"/"Missing" states in the Inspector before/after a bad bake. |
| `activeSurfaces` | `List<NavMeshSurface>` (static) | Every active surface currently in the scene. |

**Methods**

| Method | Signature | Notes |
|---|---|---|
| `BuildNavMesh()` | `void` | Synchronous full (re)build + instantiate — what the Inspector's **Bake** button calls. |
| `UpdateNavMesh(NavMeshData data)` | `AsyncOperation` | **Asynchronous, incremental** rebuild restricted to regions affected by scene changes — the entry point for runtime rebuilding without a hard frame stall; see [runtime-building-samples-and-upgrade.md](runtime-building-samples-and-upgrade.md). |
| `AddData()` | `void` | Attaches/activates this surface's `NavMeshData` in the live navigation system. |
| `RemoveData()` | `void` | Detaches the `NavMeshData` from the system **without deleting the asset** — the mechanism behind streaming a surface's mesh in/out. |
| `GetBuildSettings()` | `NavMeshBuildSettings` | Snapshot of this surface's current build configuration. |

The Inspector's **Clear** button deletes the stored NavMesh asset entirely — use it before removing the component, rather than leaving an orphaned asset behind.

### `CollectObjects` (enum)

[API — Unity.AI.Navigation.CollectObjects](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/api/Unity.AI.Navigation.CollectObjects.html) — backs `NavMeshSurface.collectObjects`.

- `All` — every active object in the scene.
- `Volume` — objects intersecting the surface's bounding volume (`size`/`center`).
- `Children` — objects that are children of the `NavMeshSurface`'s own GameObject.
- `MarkedWithModifier` — only objects carrying a `NavMeshModifier` component.

## `NavMeshModifier`

[Manual — NavMesh Modifier](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavMeshModifier.html) · [API — Unity.AI.Navigation.NavMeshModifier](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/api/Unity.AI.Navigation.NavMeshModifier.html)

Per-GameObject override of how that object is treated during baking.

| Member | Type | Description |
|---|---|---|
| `ignoreFromBuild` | `bool` | Excludes the object (+ children, if `applyToChildren`) from the build entirely — the "Remove Object" mode in the Inspector. |
| `overrideArea` / `area` | `bool` / `int` (0–31; `1` = Not Walkable) | Enable and set an explicit area type for this object, instead of inheriting the surface's `defaultArea`. |
| `applyToChildren` | `bool` | Recurses into child hierarchy, unless a deeper `NavMeshModifier` further down overrides it. |
| `overrideGenerateLinks` / `generateLinks` | `bool` / `bool` | Enable and set an explicit link-generation override for this object. |
| `AffectsAgentType(int agentTypeID)` | `bool` (method) | Whether this modifier applies to the given agent type — the Inspector's "Affected Agents: All/None" setting resolved for a specific type. |
| `activeModifiers` | `List<NavMeshModifier>` (static) | Every active modifier currently in the scene. |

## `NavMeshModifierVolume`

[Manual — NavMesh Modifier Volume](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavMeshModifierVolume.html) · [API — Unity.AI.Navigation.NavMeshModifierVolume](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/api/Unity.AI.Navigation.NavMeshModifierVolume.html)

A **volumetric** (box) area-type override, applied to whatever NavMesh geometry falls inside the volume — independent of scene hierarchy, unlike `NavMeshModifier` which is attached to a specific object. Only affects NavMeshes built **after** the volume exists — it does not retroactively touch an already-baked mesh; re-bake after adding/moving one.

| Member | Type | Description |
|---|---|---|
| `size` / `center` | `Vector3` | Box dimensions and position, relative to the GameObject. |
| `area` | `int` (0–31; `1` = Not Walkable) | Area type applied inside the volume — when overlapping volumes/modifiers disagree, the **higher-index** area generally wins the tie, except Not Walkable always wins. |
| `AffectsAgentType(int agentTypeID)` | `bool` (method) | Same semantics as `NavMeshModifier`'s. |
| `activeModifiers` | `List<NavMeshModifierVolume>` (static) | Every active modifier volume currently in the scene. |

The Inspector's **Edit Volume** toggle enables interactive resize handles in the Scene view.

## When to reach for which

- Bake a NavMesh for a whole scene/region → `NavMeshSurface`.
- Override a specific object's area or exclude it from the build → `NavMeshModifier` on that object.
- Mark a region of space (not tied to one object's mesh) as a different area type, e.g. a lava pit that's "Not Walkable" regardless of what visual geometry sits there → `NavMeshModifierVolume`.
- Restrict which objects a given surface bakes from → `NavMeshSurface.collectObjects` (`Volume`/`Children`/`MarkedWithModifier`), combined with `NavMeshModifier` on the objects that should be marked.
