---
name: unity-navmesh-navigation
description: "AI Navigation 2.0: NavMeshSurface/Modifier bake, NavMeshAgent pathStatus, NavMeshObstacle carving, NavMeshLink, area masks and costs, NavMeshBuilder runtime rebuild, NavMesh.Raycast. Use for AI pathfinding."
user-invocable: false
---

# Unity NavMesh Navigation

Not for: choosing the destination (`csharp-engineer`), the input behind a click-to-move (`unity-input-system`), locomotion blending (`unity-animation`), physics unrelated to navigation (`unity-3d-physics`, `unity-physics`).
Docs: package manual `https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/` (page slugs: `NavMeshSurface`, `NavMeshModifier`, `NavMeshLink`, `AboutObstacles`, `AreasAndCosts`, `UpgradeGuide`), package API `.../ai.navigation@2.0/api/Unity.AI.Navigation.html`, built-in runtime API `https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMesh.html` (Unity 6000.5). Substitute the installed Editor/package versions. The package owns authoring and baking, the built-in `UnityEngine.AI` module owns runtime queries and scripted building. Classic built-in navigation Manual pages no longer resolve; a remembered page title is not a source.

| Reference | Read when |
|---|---|
| [navmesh-components-surface-and-modifiers.md](references/navmesh-components-surface-and-modifiers.md) | Baking a mesh, or a region bakes wrong |
| [navmesh-baking-low-level-api.md](references/navmesh-baking-low-level-api.md) | Source geometry has no scene object to collect |
| [agent-types-areas-and-navigation-window.md](references/agent-types-areas-and-navigation-window.md) | Adding an agent type, area costs, or asymmetric traversal |
| [navmesh-agent.md](references/navmesh-agent.md) | Configuring or scripting a moving character, or an agent stops short |
| [navmesh-obstacles-and-avoidance.md](references/navmesh-obstacles-and-avoidance.md) | Something dynamic must block or reroute agents |
| [navmesh-links.md](references/navmesh-links.md) | Bridging a gap, or a link is ignored |
| [navmesh-queries-and-pathfinding-api.md](references/navmesh-queries-and-pathfinding-api.md) | Querying the mesh from code |
| [runtime-building-samples-and-upgrade.md](references/runtime-building-samples-and-upgrade.md) | Rebuilding or streaming at runtime, or migrating a legacy project |

## Steps
1. **Bake through `NavMeshSurface`**; drop to the low-level builder only when no scene object holds the source geometry.
2. **Override areas with a modifier (per object) or modifier volume (per region)**, never by editing geometry. Re-bake after any geometry, modifier or agent-type change: a stale bake looks identical to a correct one.
3. **Add an agent type only when dimensions or slope tolerance genuinely differ**; each type is another baked mesh.
4. **Configure agent steering to the character** (braking, stopping distance, avoidance tier and priority). The highest avoidance tier is the most expensive, so it is a choice, not a default.
5. **Check `pathPending` then `pathStatus`, never the `SetDestination` return**: it only says the request was accepted, and a partial path stops short silently.
6. **Obstruction for anything continuously moving; carving only where pathfinding must reroute.** Carving lags a frame and cannot block same-frame.
7. **Pick the link mechanism by endpoint origin**: authored `NavMeshLink` for hand-placed, `NavMeshLinkData` for runtime-computed. Both ends must touch the mesh.
8. **Update a runtime mesh incrementally** (async `Update`, or attach/detach pre-baked data to stream); start from the package streaming samples.
9. **`NavMesh.Raycast` returns true when blocked**, the inverse of the physics raycast.
10. **Feed the Animator from the agent's `velocity`/`desiredVelocity`**, not transform deltas (Animator side is `unity-animation`'s).
11. **Back any bake-time or avoidance-tier claim with a Profiler measurement** (`csharp-standards` Verification).
12. **Low-level types lack member docs at this version**: say so instead of inventing members.

## Never
- Author the deprecated `OffMeshLink` component (members stripped, removed from the component menu); a tutorial using it describes an API that no longer exists.
- Leave an agent and an obstacle both enabled on one object; toggle between them.
- Relocate an agent by writing its transform; use `Warp`.
- Choose a target or abandon a chase in navigation-layer code; it moves to a point `Game.Core.*` decided.
- Carve by default.
- Call static `NavMesh.SetAreaCost` for a per-agent preference; use the agent or filter scope ([navmesh-queries-and-pathfinding-api.md](references/navmesh-queries-and-pathfinding-api.md)).

## Output
```
## Navigation Work — <feature or agent>
- Bake: <NavMeshSurface config or "low-level builder" and why>
- Modifiers / agent types / areas: <overrides, types, costs and masks with the traversal rule>
- Agent config: <steering, avoidance tier and priority, area mask, transform sync>
- Path handling: <pathPending/pathStatus checks, partial-path behaviour>
- Obstacles and links: <obstruction or carving; authored or runtime link; why>
- Runtime building: <incremental update, attach/detach, or "bake-time only">
- Verified on: <Profiler evidence, or "no claim made">
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Add an `OffMeshLink` for the ladder, the tutorial uses it" -> declined (deprecated, stripped); used an authored `NavMeshLink`. An old project carrying the component has a converter, but script references need updating by hand.
