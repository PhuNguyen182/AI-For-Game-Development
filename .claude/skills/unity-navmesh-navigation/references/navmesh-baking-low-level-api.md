# Low-Level Baking — NavMeshBuilder, build settings, build sources

Sources: [NavMeshBuilder](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshBuilder.html), [NavMeshData](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshData.html), [NavMeshBuildSettings](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshBuildSettings.html), [NavMeshBuildSource](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshBuildSource.html), [NavMeshBuildMarkup](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshBuildMarkup.html), [UnityEngine.AIModule](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/UnityEngine.AIModule.html).
Covers: SKILL.md §4 — **"Bake through `NavMeshSurface` before reaching for the low-level builder"**, escalation branch.

The escape hatch for source geometry that has no scene object to collect
from. Everything here is more code and more lifetime management than the
surface component in [navmesh-components-surface-and-modifiers.md](navmesh-components-surface-and-modifiers.md),
so it earns its place only when that component cannot see the geometry at all.

## When this layer is actually needed

| Case | Why the component does not fit | Source |
|---|---|---|
| Geometry generated at runtime with no GameObject | The collect modes all walk scene objects, so there is nothing for them to find | [NavMeshBuilder](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshBuilder.html) |
| Sources assembled from several origins under custom rules | The component's filters are layer, volume, hierarchy and modifier; anything else has to build the source list itself | [NavMeshBuildSource](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshBuildSource.html) |
| Data built off the main thread and applied later | The asynchronous update entry point takes a data object the caller owns | [NavMeshBuilder](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshBuilder.html) |
| Anything a surface can already express | Not a case — this layer costs code and explicit data lifetime that the component handles, per KISS in `coding-principles.md` | [NavMeshBuilder](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshBuilder.html) |

## The pieces

| Type | Role | Source |
|---|---|---|
| `NavMeshBuilder` | Static entry point: collects sources, builds data, and updates existing data synchronously or asynchronously | [NavMeshBuilder](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshBuilder.html) |
| `NavMeshData` | The built mesh as an object the caller owns; it does nothing until it is added to the navigation system | [NavMeshData](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshData.html) |
| `NavMeshDataInstance` | The handle returned when data is added, and the only way to remove it again — losing it leaks the mesh into the system | [UnityEngine.AIModule](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/UnityEngine.AIModule.html) |
| `NavMeshBuildSettings` | Agent dimensions, voxel and tile size, region thresholds — the same knobs the surface exposes, as a struct | [NavMeshBuildSettings](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshBuildSettings.html) |
| `NavMeshBuildSource` | One piece of source geometry: a mesh, a terrain, or a primitive shape, with its transform and area | [NavMeshBuildSource](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshBuildSource.html) |
| `NavMeshBuildMarkup` | Per-object overrides applied during collection — the scripted equivalent of a modifier | [NavMeshBuildMarkup](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshBuildMarkup.html) |

## Constraints that bite

| Constraint | Consequence | Source |
|---|---|---|
| Runtime mesh sources need read and write enabled on the asset | A mesh without it contributes nothing to the build, and the failure is silent rather than an exception | [NavMeshBuildSource](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshBuildSource.html) |
| World-space bounds | Sources must stay within a large but finite distance of the world origin and within a finite extent per axis — a far-flung procedural world has to be built in shifted chunks | [NavMeshBuildSource](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshBuildSource.html) |
| Data lifetime is manual | Built data must be explicitly added to be used and explicitly removed to be freed; nothing collects it for you | [NavMeshData](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshData.html) |
| Settings validation | Build settings can express a combination that produces an empty mesh — validate them rather than assuming a build that returned produced anything | [NavMeshBuildSettings](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshBuildSettings.html) |

**Critical caveat**: a build that completes and a mesh that exists are
different things. An empty result from bad settings, an unreadable mesh
source, or geometry outside the supported bounds all look like a successful
build until an agent has nowhere to stand.

## Geometry source selection

| Option | What it decides | Source |
|---|---|---|
| Render meshes | Builds from what is drawn, which includes visual detail agents were never meant to walk on | [UnityEngine.AIModule](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/UnityEngine.AIModule.html) |
| Physics colliders | Builds from what the player can actually collide with, which usually matches the intended walkable surface more closely | [UnityEngine.AIModule](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/UnityEngine.AIModule.html) |
