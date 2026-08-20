# Runtime NavMesh Building, Samples & Upgrading From the Legacy System

## Building/updating a NavMesh at runtime

There is **no dedicated "runtime building" manual page** in the package docs (confirmed absent from the manual's table of contents) — the workflow is assembled from the API itself plus a couple of cross-links:

1. **`NavMeshSurface.UpdateNavMesh(NavMeshData data)`** → `AsyncOperation` — the primary runtime entry point: an asynchronous, incremental rebuild restricted to the regions actually affected by scene changes, avoiding a hard frame stall. Prefer this over `BuildNavMesh()` (synchronous, full rebuild) for anything happening during gameplay rather than at edit time or a loading screen.
2. **`NavMeshSurface.AddData()` / `RemoveData()`** — attach/detach a surface's `NavMeshData` from the live navigation system without rebuilding it — the mechanism for streaming a pre-baked NavMesh chunk in and out as the player moves between world regions.
3. **Combine with `NavMeshObstacle`** for anything that changes shape/position more often than a full surface rebuild is worth — see [navmesh-obstacles-and-avoidance.md](navmesh-obstacles-and-avoidance.md) for the obstruction-vs-carving trade-off. A one-off scripted `NavMesh.AddLink()`/`RemoveLink()` (see [navmesh-links.md](navmesh-links.md)) is usually cheaper than a rebuild for a shortcut that only sometimes opens.
4. For a fully custom procedural pipeline where `NavMeshSurface` doesn't fit (e.g. building `NavMeshData` from generated-at-runtime source geometry with no corresponding scene object), drop to the low-level `NavMeshBuilder`/`NavMeshBuildSource` API directly — see [navmesh-baking-low-level-api.md](navmesh-baking-low-level-api.md).

An external community walkthrough exists at [A guide on using the new AI Navigation package](https://discussions.unity.com/t/a-guide-on-using-the-new-ai-navigation-package-in-unity-2022-lts-and-above) (linked from the package manual's index page) — treat it as a supplementary community resource, not an authoritative Unity doc; verify anything it claims against the actual API pages in this skill's references before relying on it.

## Samples shipped with the package

[Manual — Samples](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/Samples.html) — installable via Package Manager's Samples tab for this package. 9 samples, each a worked example rather than documentation prose:

| # | Sample | Demonstrates |
|---|---|---|
| 1 | Multiple Agent Sizes | Different agent radii producing different navigable paths through the same scene — see [agent-types-areas-and-navigation-window.md](agent-types-areas-and-navigation-window.md). |
| 2 | Drop Plank | Player-triggered runtime addition of walkable planks, dynamically altering the NavMesh — a worked runtime-rebuild example. |
| 3 | Free Orientation | A controllable agent walking on a tilted (non-horizontal) plane — exercises `NavMeshAgent.updateUpAxis`. |
| 4 | Sliding Window Infinite | Agents in a dynamically-generated infinite world; the NavMesh is built only within a bounded region that follows the agent — the package's worked example of runtime/streaming NavMesh building. |
| 5 | Sliding Window Terrain | Same sliding-window streaming approach, over a `Terrain` instead of generated meshes. |
| 6 | Modify Mesh | A player-deformable plane mesh with the NavMesh updating in response — another runtime-rebuild worked example. |
| 7 | Dungeon | Pre-baked maze tiles connected via `NavMeshLink`s, with customizable traversal animations — a worked link + animation-coupling example. |
| 8 | Height Mesh | Side-by-side comparison of agent placement on stairs with vs. without `buildHeightMesh` enabled. |
| 9 | Cornering Speed Control | Adjusts agent speed based on upcoming turn sharpness — pairs with [Control agent speed for cornering](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/ControlAgentSpeedForCornering.html). |

For any genuinely runtime-generation-heavy feature (streaming open world, procedural dungeon), start from Sample 4/5's sliding-window pattern rather than re-deriving a streaming scheme from the low-level API cold.

## Upgrading from the legacy built-in system

[Manual — Upgrade Guide](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/UpgradeGuide.html): since Unity 2022.2, `com.unity.ai.navigation` is the standard navigation package; an existing project can stay on the legacy baked-in-scene system or convert. Only relevant when touching an older project — new work should never target the legacy system.

1. **Remove any legacy community `NavMeshComponents`** package (the pre-official [Unity-Technologies/NavMeshComponents](https://github.com/Unity-Technologies/NavMeshComponents) GitHub package) first — its types share names with this package's components and will conflict.
2. **Run `Window > AI > Navigation Updater`** — choose the **NavMesh Scene Converter** (migrates baked-in scene NavMeshes to `NavMeshSurface` components, and "Navigation Static"-flagged objects to `NavMeshModifier` components) or the **OffMesh Link Converter** ( `OffMeshLink` → `NavMeshLink`, see [navmesh-links.md](navmesh-links.md)). Run **Initialize Converters** to detect eligible assets, then **Convert Assets**.
3. **Create/assign matching agent types** if different scenes used different legacy bake settings — via `Window > AI > Navigation`'s Agents tab, per [agent-types-areas-and-navigation-window.md](agent-types-areas-and-navigation-window.md) — then assign them to the converted `NavMeshSurface`/`NavMeshAgent` components.
4. **Fix up script references by hand.** The automated converters only touch scene/prefab data — any script that referenced the old `OffMeshLink` component's members must be updated manually (Unity's Script Updating Consent utility can assist, but doesn't do this automatically).

### What changed in package version 2.0.0

[Manual — What's New](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/whats-new.html):

- **Added**: `NavMeshLink` endpoints settable via `startTransform`/`endTransform` Transform references (previously point-only); new `NavMeshLink.activated` property.
- **Changed**: `NavMeshLink.costModifier` is now `float` (see the Obsolete-members list in [navmesh-links.md](navmesh-links.md) for the renamed members this superseded).
- **Deprecated**: the `OffMeshLink` component removed entirely from the Add Component menu — new work must use `NavMeshLink`.

### Known dead link

`https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/BuildingOffMeshLinksAutomatically.html` **404s** even though the live `NavMeshSurface.html` manual page links to it from its "Generate Links" description (`NavMeshSurface.generateLinks` fallback behavior for auto-generated drop/jump links). This is a known-dead cross-reference in Unity's own docs at package version 2.0 — don't spend time chasing it, and don't cite it as a working URL in any output this skill produces.
