# Agent Types, Areas & the Navigation Window

Concept pages from the package manual covering how agent dimensions and area costs are configured project-wide, plus the task/how-to pages for common authoring workflows.

## Agent types

[Manual — About Agents](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/AboutAgents.html): an agent is modeled as an upright, orientation-independent cylinder (Radius × Height). Bake-time dimensions come from the **Navigation window's Agents tab**; per-instance runtime dimensions/behavior come from the `NavMeshAgent` component on that specific object (see [navmesh-agent.md](navmesh-agent.md)). **Base Offset** repositions the cylinder relative to the GameObject's pivot when the pivot isn't at the cylinder's base.

[Manual — Navigation window, Agents tab](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavigationWindow.html#agents-tab) (`Window > AI > Navigation`):

| Setting | Meaning |
|---|---|
| Name | Agent type identifier, referenced by `agentTypeID` throughout the API. |
| Radius | Minimum clearance from walls/ledges. |
| Height | Vertical clearance. |
| Step Height | Max climbable step height. |
| Max Slope | Max traversable ramp angle, degrees. |
| Drop Height | Max jump-down height for auto-generated links. |
| Jump Distance | Max jump-across distance for auto-generated links. |

Create a distinct agent type whenever a character genuinely needs different dimensions/slope tolerance than the default (a crouching enemy, a giant boss, a flying unit that ignores most constraints) — don't reuse one agent type across meaningfully different body sizes just to avoid the extra Inspector step; per KISS/YAGNI, also don't create a new agent type for a difference that doesn't actually change traversal (e.g. purely cosmetic scale).

## Areas & costs

[Manual — Navigation Areas and Costs](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/AreasAndCosts.html): 3 built-in area types (**Walkable**, **Not Walkable**, **Jump**) plus up to 29 custom slots, each with a **Name** and a **Cost** (multiplier on traveled distance for A*; default `1.0`). A cost of `2.0` makes the pathfinder treat that polygon's distance as twice as long, biasing paths away from it without making it impassable. When overlapping geometry/modifiers claim different area types, the **highest-index** area type generally wins the tie — except **Not Walkable always wins** regardless of index.

Each `NavMeshAgent` restricts itself to a subset of areas via `areaMask` — this is the mechanism behind **asymmetric traversal rules** (e.g. a "locked door" area only a keycard-holding agent type's mask includes, or a "human-only" corridor a zombie agent type's mask excludes). Scripted cost/area lookups: `NavMesh.GetAreaCost`/`SetAreaCost`/`GetAreaFromName`/`GetAreaNames`, `NavMeshAgent.GetAreaCost`/`SetAreaCost`, `NavMeshQueryFilter.GetAreaCost`/`SetAreaCost` — see [navmesh-queries-and-pathfinding-api.md](navmesh-queries-and-pathfinding-api.md) for how the three scopes (global/agent/filter) differ.

Deciding *which* area an enemy type should be excluded from, or *whether* a keycard should unlock a door's area, is a gameplay rule and belongs in `Game.Core.*` per `coding-principles.md`'s Shared Core integrity rule — this skill only wires the area mask/cost once that rule is decided.

## Task/how-to pages

[Manual — Navigation Overview](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavigationOverview.html) fans out to:

- [Create a NavMesh](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/CreateNavMesh.html) — the `NavMeshSurface` bake workflow (see [navmesh-components-surface-and-modifiers.md](navmesh-components-surface-and-modifiers.md)); re-bake is required after geometry, modifier, or agent-type changes — a stale bake is a common source of "the agent won't path there" bugs.
- [Create a NavMesh agent](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/CreateNavMeshAgent.html) — adding/configuring `NavMeshAgent`.
- [Create a NavMesh obstacle](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/CreateNavMeshObstacle.html) — see [navmesh-obstacles-and-avoidance.md](navmesh-obstacles-and-avoidance.md).
- [Create a NavMesh link](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/CreateNavMeshLink.html) — see [navmesh-links.md](navmesh-links.md).
- [Using NavMesh Agent with other components](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/MixingComponents.html) — explicitly warns **`NavMeshAgent` and `NavMeshObstacle` "do not mix well"** on the same GameObject simultaneously (see [navmesh-obstacles-and-avoidance.md](navmesh-obstacles-and-avoidance.md)); also documents Rigidbody/Animator interplay — a race condition risk when both a non-kinematic `Rigidbody` and `NavMeshAgent` drive the same transform, and the recommendation to feed `NavMeshAgent.velocity` into an Animator's blend parameters (or disable `updatePosition`/`updateRotation` when animation root motion should drive the agent instead — see the pitfalls list in [navmesh-agent.md](navmesh-agent.md)).
- [Advanced navigation how-tos](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavHowTos.html), fanning out further to:
  - [Move an agent to a destination](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavMoveToDestination.html)
  - [Move an agent to a clicked point](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavMoveToClickPoint.html)
  - [Patrol between points](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavAgentPatrol.html)
  - [Couple animation and navigation](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/CouplingAnimationAndNavigation.html) — driving Animator blend parameters from `NavMeshAgent.velocity`/`desiredVelocity`; actual Animator Controller/blend-tree authoring is `unity-animation`'s territory, this page only covers the navigation-side data to feed it.
  - [Control agent speed for cornering](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/ControlAgentSpeedForCornering.html) — slowing an agent based on upcoming turn sharpness; paired with Sample 9 ("Cornering Speed Control").

## Reference/window pages

[Manual — Reference (Navigation Interface hub)](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/Reference.html) fans out to:

- [Navigation window](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavigationWindow.html) — Agents/Areas tabs (above).
- [AI Navigation preferences](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavEditorPreferences.html)
- [AI Navigation overlay](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavigationOverlay.html) — the Scene view overlay with the "Show NavMesh" toggle referenced throughout this skill's troubleshooting notes.
- Component reference pages for `NavMeshAgent`, `NavMeshSurface`, `NavMeshModifier`, `NavMeshModifierVolume`, `NavMeshObstacle`, `NavMeshLink` — cross-referenced from their respective files in this folder.

## HeightMesh

[Manual — Build a HeightMesh for Accurate Character Placement](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/HeightMesh.html) — enabling `buildHeightMesh` on a `NavMeshSurface`/`NavMeshBuildSettings` generates a supplemental mesh so agents are placed at the true visual height (accurate stair/slope placement) rather than the coarser voxel-based NavMesh height alone. Costs extra bake time/memory — enable it only where visible foot/step placement error would actually be noticeable (staircases, uneven terrain), not as a blanket default on every surface.
