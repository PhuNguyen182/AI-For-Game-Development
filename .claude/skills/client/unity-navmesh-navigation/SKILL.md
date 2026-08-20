---
name: unity-navmesh-navigation
description: >
  Technique for Unity's NavMesh and AI navigation stack, spanning both the
  built-in engine module (`UnityEngine.AI` — `NavMesh` static queries,
  `NavMeshAgent` steering/pathfinding, `NavMeshObstacle` carving/avoidance,
  low-level `NavMeshBuilder`/`NavMeshData`/`NavMeshBuildSettings` procedural
  baking, runtime-scripted `NavMeshLinkData`/`NavMeshLinkInstance` links) and
  the `com.unity.ai.navigation` package (`NavMeshSurface` baking component,
  `NavMeshModifier`/`NavMeshModifierVolume` area overrides, the authored
  `NavMeshLink` component, multiple agent types and area costs via the
  Navigation window). Use this for any task touching `NavMeshAgent`,
  `NavMeshObstacle`, `NavMeshSurface`, `NavMeshModifier`,
  `NavMeshModifierVolume`, `NavMeshLink`, `NavMesh.*` static calls, or
  scripted NavMesh building/streaming — e.g. "bake a NavMesh for this level
  and place a patrolling enemy on it", "make the player character pathfind
  to a clicked point", "add a jump gap agents can cross between two
  platforms", "the enemy should carve a hole in the NavMesh when it stops
  moving", "stream in NavMesh chunks as the player explores an open world",
  "convert this old project's baked-in NavMesh and OffMesh Links to the
  current package", "a boss with multiple agent-size variants needs
  different navigable areas". Do not use this for the actual AI
  decision-making that chooses a destination or triggers movement — behavior
  trees, utility AI, target selection, patrol-route logic, or any rule that
  decides *whether*/*where* an agent should go belongs in `Game.Core.*` per
  `coding-principles.md`'s Shared Core integrity rule; this skill only
  executes an already-decided move via NavMesh queries/agents. Do not use
  this for `com.unity.physics`/DOTS collision or built-in PhysX
  `Rigidbody`/`Collider` mechanics unrelated to navigation — those are
  `unity-physics`/`unity-3d-physics`'s territory; this skill only touches
  physics-adjacent NavMesh geometry collection (`NavMeshCollectGeometry.PhysicsColliders`).
  Do not use this to author the Animator Controller/blend tree that visualizes
  an agent's locomotion — that's `unity-animation`; this skill only supplies
  the navigation-side data (`NavMeshAgent.velocity`/`desiredVelocity`) an
  Animator consumes.
---

# Unity NavMesh & AI Navigation — Built-in Module + AI Navigation Package

Sources: see [references/](references/) for the Scripting API/Manual root links, split by topic — [root-links.md](references/root-links.md), [navmesh-queries-and-pathfinding-api.md](references/navmesh-queries-and-pathfinding-api.md), [navmesh-agent.md](references/navmesh-agent.md), [navmesh-obstacles-and-avoidance.md](references/navmesh-obstacles-and-avoidance.md), [navmesh-links.md](references/navmesh-links.md), [navmesh-baking-low-level-api.md](references/navmesh-baking-low-level-api.md), [navmesh-components-surface-and-modifiers.md](references/navmesh-components-surface-and-modifiers.md), [agent-types-areas-and-navigation-window.md](references/agent-types-areas-and-navigation-window.md), [runtime-building-samples-and-upgrade.md](references/runtime-building-samples-and-upgrade.md), [scripting-api.md](references/scripting-api.md).

## 1. Objective
Get characters moving correctly across a baked or runtime-built NavMesh — the right bake setup (`NavMeshSurface`/modifiers), the right agent configuration (`NavMeshAgent`), the right dynamic-obstacle strategy (`NavMeshObstacle`), and the right connector for gaps the mesh doesn't cover (`NavMeshLink`, or a runtime-scripted `NavMeshLinkData` link) — without drifting into the actual AI decision logic that chooses destinations, PhysX/DOTS physics unrelated to navigation, or Animator authoring, all of which are sibling skills'/roles' territory.

## 2. Role
Act as the navigation specialist: given a scene or feature that needs a NavMesh, a moving agent, a dynamic obstacle, or a scripted shortcut across a gap, you choose and configure the right `UnityEngine.AI`/`Unity.AI.Navigation` component or API call — you don't decide *where* an agent should go or *why* (that's Shared Core's job), and you don't author the visual locomotion blend or the physics rig underneath a character, both of which are sibling skills' territory.

## 3. When to invoke this skill
- Baking a NavMesh for a scene or region: configuring `NavMeshSurface` (agent type, collect-objects mode, geometry source, voxel/tile size, minimum region area, HeightMesh), or dropping to the low-level `NavMeshBuilder`/`NavMeshBuildSource` API for a fully custom procedural pipeline.
- Overriding bake behavior for specific objects or regions: `NavMeshModifier` (area override, exclude from build, per-agent-type scoping) or `NavMeshModifierVolume` (volumetric area override).
- Configuring a `NavMeshAgent`: speed/acceleration/steering, obstacle avoidance quality/priority, area mask, stopping behavior, path status handling, or wiring `SetDestination`/`Warp`/`CalculatePath`.
- Setting up a dynamic obstacle: `NavMeshObstacle` shape, and choosing obstruction-only vs. carving (and which carving strategy) for a specific moving/stationary object.
- Connecting a gap the NavMesh doesn't cover: authoring a `NavMeshLink` component, or building one procedurally at runtime via `NavMesh.AddLink(NavMeshLinkData)` — and correctly routing away from the deprecated `OffMeshLink`.
- Building or streaming a NavMesh at runtime: `NavMeshSurface.UpdateNavMesh()`/`BuildNavMesh()`/`AddData()`/`RemoveData()`, or a fully custom `NavMeshBuilder.UpdateNavMeshDataAsync()` pipeline.
- Configuring multiple agent types or area costs via the Navigation window (Agents/Areas tabs), including asymmetric traversal rules driven by `NavMeshAgent.areaMask`.
- Querying the NavMesh directly for gameplay-adjacent (not gameplay-deciding) purposes: `NavMesh.SamplePosition`/`CalculatePath`/`Raycast`/`FindClosestEdge`, or their `NavMeshQueryFilter`-scoped overloads.
- Migrating an older project's baked-in-scene NavMesh/`OffMeshLink` setup to the current package via the Navigation Updater.
- Negative trigger: the actual decision of *what* destination to path toward, *when* to move, or *which* target to chase (behavior tree, utility AI, state machine, patrol-route selection logic) — that's `csharp-engineer`'s Shared Core, per `coding-principles.md`'s Shared Core integrity rule; this skill only executes an already-chosen destination through `NavMeshAgent`/`NavMesh` API.
- Negative trigger: `com.unity.physics`/DOTS rigid-body physics, or PhysX `Rigidbody`/`Collider`/joint mechanics with no navigation involvement — `unity-physics`/`unity-3d-physics`.
- Negative trigger: authoring the Animator Controller/blend tree/state machine that visualizes an agent's locomotion — `unity-animation`; this skill only supplies the `NavMeshAgent.velocity`/`desiredVelocity` data an Animator parameter consumes.
- Negative trigger: Cinemachine camera paths/dolly tracks that merely resemble a "waypoint route" — unrelated system, `unity-cinemachine-authoring`.

## 4. How to use this skill
1. **Confirm which doc layer the task actually needs**, per [root-links.md](references/root-links.md): the package (`Unity.AI.Navigation.*`, Navigation window) for authoring/baking, the built-in module (`UnityEngine.AI.*`) for runtime queries/scripted building. Most real features touch both — don't assume one is sufficient just because it's more familiar.
2. **Bake declaratively first.** Add a `NavMeshSurface`, configure agent type/collect-objects/geometry source, and use `NavMeshModifier`/`NavMeshModifierVolume` for per-object/per-region overrides, per [navmesh-components-surface-and-modifiers.md](references/navmesh-components-surface-and-modifiers.md) — only drop to the raw `NavMeshBuilder`/`NavMeshBuildSource` API ([navmesh-baking-low-level-api.md](references/navmesh-baking-low-level-api.md)) when the declarative components genuinely can't express the required source geometry, per KISS in `coding-principles.md`.
3. **Configure agent types and areas deliberately** via the Navigation window, per [agent-types-areas-and-navigation-window.md](references/agent-types-areas-and-navigation-window.md) — a new agent type only when dimensions/slope tolerance genuinely differ, area costs/masks only when the design actually needs asymmetric or weighted traversal, not as a default.
4. **Configure `NavMeshAgent` to the actual movement requirement**, per [navmesh-agent.md](references/navmesh-agent.md): steering parameters matched to the character's feel, `obstacleAvoidanceType` picked deliberately (don't default every agent to the highest/most expensive tier without a measured reason), and always check `pathStatus`/`isPathStale` after `SetDestination` rather than assuming a `true` return means "arrived."
5. **Choose the obstacle strategy deliberately**, per [navmesh-obstacles-and-avoidance.md](references/navmesh-obstacles-and-avoidance.md): obstruction-only for continuously-moving objects, carving (with the right stationary/moved strategy) only for objects that genuinely need to close off pathfinding-level routes — and never combine an active `NavMeshAgent` with an active `NavMeshObstacle` on the same GameObject at the same time.
6. **Pick the correct link mechanism**, per [navmesh-links.md](references/navmesh-links.md): the package's `NavMeshLink` component for anything hand-placed in a scene, `NavMesh.AddLink(NavMeshLinkData)` for purely runtime/procedural connections, and never author a new `OffMeshLink` — it's deprecated and stripped down as of Unity 6000.5. When migrating an old project, run the Navigation Updater's converters, per [runtime-building-samples-and-upgrade.md](references/runtime-building-samples-and-upgrade.md), then fix up script references by hand.
7. **For runtime/streaming NavMesh needs**, use `NavMeshSurface.UpdateNavMesh()` (async, incremental) over `BuildNavMesh()` (sync, full) during actual gameplay, and `AddData()`/`RemoveData()` for streaming pre-baked chunks in/out — start from the package's Sliding Window Infinite/Terrain samples' pattern rather than re-deriving a streaming scheme from scratch, per [runtime-building-samples-and-upgrade.md](references/runtime-building-samples-and-upgrade.md).
8. **Respect the Shared Core boundary.** This skill executes movement/queries; it never decides a destination, a target, or a patrol route — that decision is made in `Game.Core.*` and handed to this layer as an already-resolved `Vector3`/target, per `coding-principles.md`'s Shared Core integrity rule.
9. **Hand off what's out of scope explicitly**: Animator Controller/blend-tree authoring that consumes `NavMeshAgent.velocity` → `unity-animation`. PhysX/DOTS physics unrelated to navigation → `unity-3d-physics`/`unity-physics`. Deep, escalated navigation performance work beyond Profiler-measured bake-time/tile-size/voxel-size tuning → `tech-lead-performance`.
10. **Validate any performance claim with a measurement** (Unity Profiler bake time, frame cost of avoidance quality tiers, NavMesh memory footprint), not asserted from documentation guidance alone, per `performance-and-algorithms.md`'s Verification section.

## 5. Specific goals / tasks this skill performs
- Baking a NavMesh via `NavMeshSurface`, with `NavMeshModifier`/`NavMeshModifierVolume` overrides where needed.
- Configuring `NavMeshAgent` steering, avoidance, area mask, and destination/path handling.
- Choosing and configuring `NavMeshObstacle` obstruction vs. carving strategy.
- Authoring `NavMeshLink` connectors, or building runtime-scripted links via `NavMesh.AddLink`.
- Configuring multiple agent types and area costs via the Navigation window.
- Building/streaming a NavMesh at runtime (`UpdateNavMesh`, `AddData`/`RemoveData`, or low-level `NavMeshBuilder`).
- Running NavMesh spatial queries (`SamplePosition`, `CalculatePath`, `Raycast`, `FindClosestEdge`) for gameplay-adjacent (not gameplay-deciding) purposes.
- Migrating a legacy baked-in-scene NavMesh/`OffMeshLink` setup to the current package.
- Out of scope: AI decision logic that chooses destinations/targets (`csharp-engineer`'s Shared Core); PhysX/DOTS physics unrelated to navigation (`unity-3d-physics`/`unity-physics`); Animator Controller/blend-tree authoring (`unity-animation`); deep escalated performance work (`tech-lead-performance`).

## 6. Output format
```
## Navigation Work — <feature/agent name>
- Doc layer(s) touched: built-in UnityEngine.AI / com.unity.ai.navigation package / both
- Bake setup: NavMeshSurface config (agent type, collect-objects mode, geometry source) + modifiers used, or "low-level NavMeshBuilder pipeline" + why
- Agent types / areas: types defined, area costs/masks configured, rationale
- NavMeshAgent config (if applicable): steering params, obstacleAvoidanceType, areaMask, key behavior notes
- NavMeshObstacle config (if applicable): shape, obstruction-only vs. carving strategy, rationale
- Links (if applicable): NavMeshLink component / scripted NavMeshLinkData — which, and why
- Runtime building (if applicable): BuildNavMesh / UpdateNavMesh / AddData/RemoveData usage, streaming pattern followed
- Shared Core boundary: confirmed no destination/target-selection decision made in navigation-layer code
- Verified on: <Profiler bake time / frame cost measurement, or "not yet measured">
- Hand-off: <Animator coupling → unity-animation / physics → unity-3d-physics or unity-physics / deep perf → tech-lead-performance, as applicable>
- Known limitations: <...>
```

## 7. Examples
**Example 1**
- Input: "Bake a NavMesh for this dungeon level, add a patrolling guard, and let it jump across a broken bridge gap."
- Output: added a `NavMeshSurface` on the level root (`collectObjects = Children`, `useGeometry = PhysicsColliders`, default voxel/tile size, `minRegionArea` raised slightly to drop tiny disconnected slivers behind decor), baked; configured a `NavMeshModifierVolume` over a hazard pit as `Not Walkable`; added `NavMeshAgent` to the guard (moderate `obstacleAvoidanceType`, `areaMask` = default Walkable) with its patrol *route selection* left to `csharp-engineer`'s Shared Core state machine, this skill only wired `SetDestination()` per waypoint the Core layer supplies; placed a `NavMeshLink` across the broken bridge gap with `width` sized to the gap and `bidirectional = true`, verified both ends touch the baked mesh via the Navigation overlay's "Show NavMesh".
- Hand-off: patrol waypoint sequencing/decision logic → `csharp-engineer`; guard idle/walk/run Animator blending driven by `NavMeshAgent.velocity` → `unity-animation`.

**Example 2**
- Input: "A tank should physically block a corridor when parked, but not thrash the NavMesh while driving through it."
- Output: added `NavMeshObstacle` with `shape = Box` sized to the tank's footprint, `carving = true`, `carveOnlyStationary = true` with `carvingTimeToStationary` tuned so the hole appears shortly after the tank actually stops (not while merely slowing down), and left `carving` off equivalent behavior implicit while moving since `carveOnlyStationary` already skips carving during motion; confirmed no `NavMeshAgent` is simultaneously active on the same GameObject, per the Mixing Components guidance.
- Verified on: Profiler confirmed no per-frame NavMesh rebuild cost while the tank is driving, only a one-time carve cost shortly after it parks.

## 8. Edge cases & guardrails
- Never author a new `OffMeshLink` component — it's deprecated, stripped of its own members as of Unity 6000.5, and removed from the Add Component menu. Use the package's `NavMeshLink` for authored connectors, or `NavMesh.AddLink(NavMeshLinkData)` for purely runtime-scripted ones.
- Never cite a classic built-in Manual page (`nav-BuildingNavMesh.html`, `nav-CreateNavMeshAgent.html`, `OffMeshLinks.html`, etc.) — every one of them 404s as of Unity 6000.5; the `com.unity.ai.navigation` package manual is the sole current source of conceptual documentation, confirmed by the built-in `NavMeshAgent` scripting page itself linking there instead.
- Never treat `NavMesh.Raycast`/`NavMeshAgent.Raycast`'s `true` return as "reached the target unobstructed" — it means the opposite: `true` = blocked, `false` = arrived clear. Double-check this inversion in any code review of navigation-layer raycasts.
- Never treat a `CalculatePath`/`SetDestination` call's `true` return, or a non-`Invalid` `pathStatus`, as proof the agent will actually reach the destination — always check specifically for `NavMeshPathStatus.PathPartial` before assuming arrival.
- Never run an active `NavMeshAgent` and an active `NavMeshObstacle` on the same GameObject simultaneously — toggle between them if a single object genuinely needs both roles at different times.
- Never default every obstacle to `carving = true` "to be safe" — reserve carving for objects that genuinely need pathfinding-level rerouting; a fast/small mover is usually cheaper and looks equally correct as obstruction-only avoidance.
- Never assume `NavMesh.SetAreaCost` (global, affects every agent) and `NavMeshAgent.SetAreaCost`/`NavMeshQueryFilter.SetAreaCost` (scoped) are interchangeable — pick the scope the task actually needs.
- Never let navigation-layer code decide a gameplay outcome (target selection, patrol logic, "should this enemy give up the chase") — that decision belongs in `Game.Core.*` per `coding-principles.md`'s Shared Core integrity rule; this skill only executes an already-decided destination/target.
- Never claim a bake-time, tile/voxel-size, or avoidance-quality performance improvement without a Profiler measurement backing it, per `performance-and-algorithms.md`'s Verification section.
- If a task needs the sparsely-documented `Unity.AI.Navigation.LowLevel` types (`NavWorld`, `NavNode`, etc.), say plainly that Unity's own docs don't yet expose member-level detail for them at this version, rather than inventing plausible-sounding members.
- Don't chase the known-dead `BuildingOffMeshLinksAutomatically.html` link referenced from `NavMeshSurface`'s manual page — it 404s at package version 2.0; treat automatic link generation as covered by `NavMeshSurface`/`NavMeshModifier`'s `generateLinks` fields instead.
