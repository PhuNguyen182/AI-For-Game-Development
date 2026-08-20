# NavMeshAgent

[Scripting API — NavMeshAgent](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshAgent.html) — "Navigation mesh agent." Namespace `UnityEngine.AI`, inherits `Behaviour`. The per-character component that moves a GameObject along the baked NavMesh: local avoidance, path following, and off-mesh-link traversal, all driven by properties below. The page's own "For more details" pointer routes to the [package manual](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/index.html) for conceptual/workflow guidance — Inspector field reference for this component actually lives in the package's manual at [Reference.html → NavMeshAgent.html](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavMeshAgent.html), organized as **Basic** (Agent Type, Base Offset), **Steering** (Speed, Angular Speed, Acceleration, Stopping Distance, Auto Braking), **Obstacle Avoidance** (Radius, Height, Quality, Priority — 0–99, lower value = higher priority), **Path Finding** (Auto Traverse Off Mesh Link, Auto Repath, Area Mask).

No Obsolete/Deprecated/Experimental members as of Unity 6000.5. No events are exposed on this component (no `onDestinationReached`/`onPathChanged` — poll `remainingDistance`/`pathStatus`/`hasPath` instead).

## Properties

| Property | Type | Notes |
|---|---|---|
| `agentTypeID` | `int` | Which agent type (from the Navigation window / package agent-type list) this instance uses. |
| `baseOffset` | `float` | Vertical displacement of the owning GameObject relative to the agent's simulated cylinder — needed when the GameObject's pivot isn't at the cylinder's base. |
| `speed` | `float` | Max movement speed. |
| `angularSpeed` | `float` | Max turn speed, degrees/sec. |
| `acceleration` | `float` | Max acceleration following a path, units/sec². |
| `stoppingDistance` | `float` | Distance from the target at which the agent is considered arrived. |
| `autoBraking` | `bool` | Whether the agent decelerates automatically as it nears its destination — turn off for continuously-patrolling or formation-following agents that shouldn't slow down at waypoints. |
| `radius` | `float` | Avoidance radius. |
| `height` | `float` | Clearance height under obstacles. |
| `obstacleAvoidanceType` | [`ObstacleAvoidanceType`](#obstacleavoidancetype-enum) | Avoidance quality vs. performance tier. |
| `avoidancePriority` | `int` | Lower value = higher priority in local avoidance resolution between agents. |
| `autoTraverseOffMeshLink` | `bool` | Whether the agent automatically moves itself across an off-mesh link/`NavMeshLink` it reaches, vs. waiting for a script to drive that traversal manually (see [navmesh-links.md](navmesh-links.md)). |
| `autoRepath` | `bool` | Whether the agent automatically recomputes its path if the current one becomes invalid. |
| `areaMask` | `int` | Bitmask of NavMesh areas this agent is permitted to traverse — the mechanism behind asymmetric traversal rules (a locked-door area only some agent types can use). |
| `destination` | `Vector3` | Get, or attempt-set, the world-space target. Setting it triggers path (re)calculation — prefer `SetDestination()` for the write side since it returns a success bool. |
| `path` | `NavMeshPath` | Get/set the agent's current path directly. |
| `hasPath` | `bool` (RO) | Whether the agent currently has a path assigned. |
| `pathPending` | `bool` (RO) | A path is being computed asynchronously and isn't ready yet — check this before trusting `path`/`pathStatus` right after `SetDestination`. |
| `pathStatus` | [`NavMeshPathStatus`](navmesh-queries-and-pathfinding-api.md#navmeshpathstatus-enum) | Complete / Partial / Invalid — see the pathfinding API reference for the partial-path pitfall. |
| `isPathStale` | `bool` (RO) | The current path may no longer reflect the actual NavMesh (e.g. after a runtime rebuild) — combine with `autoRepath` handling. |
| `remainingDistance` | `float` (RO) | Distance to destination along the path — the standard "have we arrived" signal. |
| `steeringTarget` | `Vector3` (RO) | The current immediate steering target along the path (not the final destination). |
| `desiredVelocity` | `Vector3` (RO) | Desired velocity including avoidance's contribution. |
| `velocity` | `Vector3` | Current velocity (get), or a manual override (set) — feed this into an Animator parameter for locomotion blending instead of computing speed separately; see [agent-types-areas-and-navigation-window.md](agent-types-areas-and-navigation-window.md)'s animation-coupling note. |
| `nextPosition` | `Vector3` | Get/set the agent's simulated position directly. |
| `isOnNavMesh` | `bool` (RO) | Whether the agent is currently bound to a NavMesh at all. |
| `isOnOffMeshLink` | `bool` (RO) | Whether the agent is currently traversing a link. |
| `currentOffMeshLinkData` / `nextOffMeshLinkData` | `OffMeshLinkData` | Data for the link currently being traversed / the next one on the path — see [navmesh-links.md](navmesh-links.md). |
| `navMeshOwner` | `Object` (RO) | The owning object of the NavMesh the agent currently sits on. |
| `isStopped` | `bool` | Set true to halt movement along the current path without discarding it; false to resume. |
| `updatePosition` | `bool` | Whether the component syncs the GameObject's `transform.position` from the simulated agent position — disable when animation root motion should drive the transform instead. |
| `updateRotation` | `bool` | Whether the component auto-updates `transform` orientation to face movement direction — disable for the same root-motion scenario. |
| `updateUpAxis` | `bool` | Whether the agent aligns to the up-axis of the NavMesh/link surface it's currently on (relevant for non-horizontal NavMeshes, e.g. walking on a tilted plane). |

## Methods

| Method | Purpose |
|---|---|
| `SetDestination(Vector3)` | Set/update the destination and trigger a new path calculation — the standard entry point for "go here." |
| `ResetPath()` | Clear the current path. |
| `CalculatePath(Vector3, NavMeshPath)` | Compute a path to a point into a caller-owned `NavMeshPath` **without** moving the agent or replacing its live path — use for speculative "can I reach X" checks. |
| `SetPath(NavMeshPath)` | Assign an already-computed path to the agent. |
| `Warp(Vector3)` | Teleport the agent to a position, bypassing normal movement/path invalidation concerns — the correct way to relocate an agent instantly (respawn, cutscene placement) instead of writing `transform.position` directly. |
| `Move(Vector3)` | Apply a relative movement delta to the current position. |
| `Raycast(Vector3, out NavMeshHit)` | Trace a straight path toward a target without moving the agent — agent-scoped equivalent of `NavMesh.Raycast`; same "`true` = blocked" return convention. |
| `FindClosestEdge(out NavMeshHit)` | Nearest NavMesh edge from the agent's current position. |
| `SamplePathPosition(int areaMask, float maxDistance, out NavMeshHit)` | Sample a position along the agent's current path. |
| `GetAreaCost(int)` / `SetAreaCost(int, float)` | Get/set traversal cost for an area, **scoped to this agent only** — contrast with `NavMesh.SetAreaCost`'s global effect (see [navmesh-queries-and-pathfinding-api.md](navmesh-queries-and-pathfinding-api.md)). |
| `CompleteOffMeshLink()` | Finish movement across the current off-mesh link/`NavMeshLink`. |
| `ActivateCurrentOffMeshLink(bool)` | Enable/disable the link the agent is currently on. |

## `ObstacleAvoidanceType` (enum)

[Scripting API — ObstacleAvoidanceType](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.ObstacleAvoidanceType.html) — "Level of obstacle avoidance." Quality and performance cost scale together monotonically; pick the cheapest tier that still looks correct for the given agent count rather than defaulting every agent to the top tier.

- `NoObstacleAvoidance` — avoidance disabled.
- `LowQualityObstacleAvoidance` — simple avoidance, low performance impact.
- `MedQualityObstacleAvoidance` — medium avoidance, medium impact.
- `GoodQualityObstacleAvoidance` — good avoidance, high impact.
- `HighQualityObstacleAvoidance` — highest precision, highest impact.

For crowds of many agents, consider a mixed strategy: high-priority/hero agents at a higher quality tier, background/filler agents at `Low`/`Med` — per `performance-and-algorithms.md`'s general "measured, not assumed" discipline, verify the actual frame cost per tier with the Profiler before deciding a project-wide default.

## MonoBehaviour + agent interaction pitfalls

- **`NavMeshAgent` and `NavMeshObstacle` do not mix well on the same GameObject simultaneously** — per the package manual's `MixingComponents.html` guidance, only one should be active at a time on a given object; see [navmesh-obstacles-and-avoidance.md](navmesh-obstacles-and-avoidance.md).
- A non-kinematic `Rigidbody` and `NavMeshAgent` driving the same transform can race each other — if a Rigidbody must coexist (e.g. for physical knockback reactions), make sure only one is authoritative over `transform.position` at any given moment, and hand off deliberately rather than letting both write it the same frame.
- When animation root motion should drive movement instead of the agent's own transform sync, set `updatePosition`/`updateRotation` to `false` and feed the resulting root-motion delta back into `nextPosition`, rather than fighting the agent's own transform writes.
