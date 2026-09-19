# Runtime Building, Samples and Upgrading

Sources: [NavMeshSurface API](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/api/Unity.AI.Navigation.NavMeshSurface.html), [Samples](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/Samples.html), [Upgrade guide](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/UpgradeGuide.html), [NavMeshBuilder](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshBuilder.html).
Covers: SKILL.md §4 — **"Update a runtime NavMesh incrementally rather than rebuilding the surface"**.

How a mesh changes while the game is running, the worked examples that ship
with the package, and the path off the legacy system. The package has no
dedicated runtime-building manual page — the workflow is assembled from the
API and the samples below.

## Runtime entry points

| Entry point | What it decides | Source |
|---|---|---|
| Asynchronous incremental update | Rebuilds only the regions scene changes affected, without the frame stall a full rebuild causes — the default for anything happening during play | [NavMeshSurface API](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/api/Unity.AI.Navigation.NavMeshSurface.html) |
| Synchronous full build | Rebuilds everything and blocks; acceptable behind a loading screen, not during gameplay | [NavMeshSurface API](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/api/Unity.AI.Navigation.NavMeshSurface.html) |
| Attach and detach data | Brings a pre-baked mesh in and out of the live system without building anything — the cheapest option, and what streaming actually uses | [NavMeshSurface API](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/api/Unity.AI.Navigation.NavMeshSurface.html) |
| An obstacle instead of a rebuild | Something that changes position more often than a rebuild is worth belongs to [navmesh-obstacles-and-avoidance.md](navmesh-obstacles-and-avoidance.md), not to the builder | [NavMeshSurface API](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/api/Unity.AI.Navigation.NavMeshSurface.html) |
| A scripted link instead of a rebuild | A shortcut that only sometimes opens is a link toggle, which costs nothing next to rebuilding a region — see [navmesh-links.md](navmesh-links.md) | [NavMeshBuilder](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshBuilder.html) |

**Critical caveat**: agents holding a path across a region that was rebuilt
do not automatically notice. Their path is stale rather than invalid, which
is why a streaming world produces agents walking through geometry that is no
longer navigable — see [navmesh-agent.md](navmesh-agent.md).

## Shipped samples

| Sample | Demonstrates | Source |
|---|---|---|
| Multiple agent sizes | Different radii producing genuinely different routes through one scene | [Samples](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/Samples.html) |
| Drop plank | A player action adding walkable geometry and the mesh updating in response | [Samples](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/Samples.html) |
| Free orientation | An agent walking a non-horizontal surface, exercising up-axis alignment | [Samples](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/Samples.html) |
| Sliding window, infinite and terrain | The package's own streaming pattern — a bounded build region that follows the agent, over generated meshes and over terrain | [Samples](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/Samples.html) |
| Modify mesh | A deformable surface with the mesh rebuilding as it changes | [Samples](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/Samples.html) |
| Dungeon | Pre-baked tiles joined by links, with traversal animation on the links | [Samples](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/Samples.html) |
| Height mesh | Agent placement on stairs with and without the supplementary surface, side by side | [Samples](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/Samples.html) |
| Cornering speed control | Speed adjusted from the sharpness of the next turn | [Samples](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/Samples.html) |

For a streaming or procedural feature, start from the sliding-window samples
rather than deriving a scheme from the low-level API cold — they solve the
region-boundary and link-stitching problems that are the hard part.

## Upgrading from the legacy system

| Step | What it covers | Source |
|---|---|---|
| The Navigation Updater | Converts scene and prefab data, including legacy link components, to the current package's equivalents | [Upgrade guide](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/UpgradeGuide.html) |
| What it does not cover | Script references to the converted types are not updated — code still naming the legacy component compiles against a class stripped of its members | [Upgrade guide](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/UpgradeGuide.html) |
| Renamed link members | Several link fields were renamed in this package version, with the old names kept as obsolete aliases — see [navmesh-links.md](navmesh-links.md) | [Upgrade guide](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/UpgradeGuide.html) |
| Bake location | The legacy system stored the mesh with the scene; the current one stores it on a surface component, so an upgraded scene has no mesh until a surface exists and is baked | [Upgrade guide](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/UpgradeGuide.html) |
