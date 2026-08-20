# Unity NavMesh & AI Navigation — Scripting API Index

Consolidated Scripting API index across both doc trees: the built-in `UnityEngine.AI` module and the `com.unity.ai.navigation` package's `Unity.AI.Navigation` namespace. Each entry links the confirmed page and points to the topic file in this folder with full member detail — use this page to jump to the right file, not as a replacement for reading it.

## Built-in module — `UnityEngine.AI` (ships with the Editor, no package install)

### Core query/simulation classes

- [NavMesh](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMesh.html) — static query/pathfinding entry point (`SamplePosition`, `CalculatePath`, `Raycast`, `FindClosestEdge`, area/settings/link management). Full detail: [navmesh-queries-and-pathfinding-api.md](navmesh-queries-and-pathfinding-api.md).
- [NavMeshAgent](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshAgent.html) — per-character navigation component. Full detail: [navmesh-agent.md](navmesh-agent.md).
- [NavMeshObstacle](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshObstacle.html) — dynamic obstruction/carving component. Full detail: [navmesh-obstacles-and-avoidance.md](navmesh-obstacles-and-avoidance.md).
- [OffMeshLink](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.OffMeshLink.html) — **deprecated**, use the package's `NavMeshLink` instead. Full detail: [navmesh-links.md](navmesh-links.md).

### Query/pathfinding support structs & enums

- [NavMeshHit](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshHit.html), [NavMeshPath](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshPath.html), [NavMeshPathStatus](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshPathStatus.html), [NavMeshQueryFilter](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshQueryFilter.html), [NavMeshTriangulation](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshTriangulation.html) — see [navmesh-queries-and-pathfinding-api.md](navmesh-queries-and-pathfinding-api.md).
- [ObstacleAvoidanceType](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.ObstacleAvoidanceType.html) — see [navmesh-agent.md](navmesh-agent.md).
- [NavMeshObstacleShape](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshObstacleShape.html) — see [navmesh-obstacles-and-avoidance.md](navmesh-obstacles-and-avoidance.md).
- [OffMeshLinkData](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.OffMeshLinkData.html), [OffMeshLinkType](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.OffMeshLinkType.html) — see [navmesh-links.md](navmesh-links.md).
- [NavMeshLinkData](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshLinkData.html), [NavMeshLinkInstance](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshLinkInstance.html) — runtime-scripted links, see [navmesh-links.md](navmesh-links.md).

### Baking/build support classes, structs & enums

- [NavMeshBuilder](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/UnityEngine.AI.NavMeshBuilder.html) (note the full `UnityEngine.AI.` URL prefix — this page's URL doesn't follow the shorter `AI.*` pattern the sibling pages use), [NavMeshData](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshData.html), [NavMeshDataInstance](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshDataInstance.html), [NavMeshBuildSettings](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshBuildSettings.html), [NavMeshBuildSource](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshBuildSource.html), [NavMeshBuildSourceShape](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshBuildSourceShape.html), [NavMeshBuildMarkup](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshBuildMarkup.html), [NavMeshBuildDebugSettings](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshBuildDebugSettings.html), [NavMeshBuildDebugFlags](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshBuildDebugFlags.html), [NavMeshCollectGeometry](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshCollectGeometry.html) — see [navmesh-baking-low-level-api.md](navmesh-baking-low-level-api.md).

### New-in-Unity-6 low-level namespace — `Unity.AI.Navigation.LowLevel` (sparsely documented)

- `NavWorld`, `NavLocation`, `NavNode`, `NavQueryBuffer` (structs), `NavNodeType`, `NavQueryStatus` (enums) — each resolves to a real page, but as of Unity 6000.5 Unity's own docs render only a one-line purpose statement with no member tables. Not flagged Obsolete/Deprecated/Experimental either — treat as "exists, under-documented" rather than assuming a fetch failure. No page in this skill's references relies on these; mention them to the user only if they specifically ask about low-level/job-based navigation querying, and flag that Unity's own docs don't yet expose member-level detail.

## Package — `Unity.AI.Navigation` (`com.unity.ai.navigation`, install via Package Manager)

The package's entire public scripting surface is genuinely small — 4 classes + 1 enum, confirmed via the namespace listing page:

- [NavMeshSurface](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/api/Unity.AI.Navigation.NavMeshSurface.html) — bakes/holds a NavMesh for one agent type. See [navmesh-components-surface-and-modifiers.md](navmesh-components-surface-and-modifiers.md).
- [NavMeshModifier](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/api/Unity.AI.Navigation.NavMeshModifier.html) — per-object bake-property override. See [navmesh-components-surface-and-modifiers.md](navmesh-components-surface-and-modifiers.md).
- [NavMeshModifierVolume](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/api/Unity.AI.Navigation.NavMeshModifierVolume.html) — volumetric area-type override. See [navmesh-components-surface-and-modifiers.md](navmesh-components-surface-and-modifiers.md).
- [NavMeshLink](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/api/Unity.AI.Navigation.NavMeshLink.html) — authored point-to-point connector, current replacement for `OffMeshLink`. See [navmesh-links.md](navmesh-links.md).
- [CollectObjects](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/api/Unity.AI.Navigation.CollectObjects.html) (enum) — backs `NavMeshSurface.collectObjects`. See [navmesh-components-surface-and-modifiers.md](navmesh-components-surface-and-modifiers.md).

Everything else the package's components reference at the type level (`NavMeshBuildSettings`, `NavMeshData`, `NavMeshCollectGeometry`, `NavMeshAgent`, `NavMeshObstacle`, `AsyncOperation`) belongs to the built-in `UnityEngine.AI`/`UnityEngine` namespaces above, not to this package — the package deliberately reuses them rather than redefining equivalents.

## Cross-reference note

The built-in `NavMeshAgent` scripting page itself points to the package manual for conceptual detail (`https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/index.html`) rather than any built-in Manual page — confirming that, as of Unity 6000.5, **every classic built-in navigation Manual page (`nav-*.html`, `OffMeshLinks.html`) 404s** and the package manual is the sole current source of conceptual/workflow documentation. Never cite a `docs.unity3d.com/.../Manual/nav-*.html` URL as current.
