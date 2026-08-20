# NavMeshObstacle — Dynamic Obstruction & Carving

## `NavMeshObstacle` (component)

[Scripting API — NavMeshObstacle](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshObstacle.html) — "An obstacle for NavMeshAgents to avoid." Namespace `UnityEngine.AI`. Concept/workflow documentation lives in the package manual: [AboutObstacles.html](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/AboutObstacles.html) and [CreateNavMeshObstacle.html](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/CreateNavMeshObstacle.html). Instance-only API; no custom methods documented, only inherited `Behaviour`/`Component`/`Object` members plus the properties below.

| Property | Type | Description |
|---|---|---|
| `shape` | [`NavMeshObstacleShape`](#navmeshobstacleshape-enum) | `Capsule` or `Box`. |
| `radius` | `float` | Capsule shape radius. |
| `height` | `float` | Cylinder shape height. |
| `size` | `Vector3` | Box shape dimensions, local space. |
| `center` | `Vector3` | Obstacle center, local space. |
| `carving` | `bool` | Whether this obstacle cuts an actual hole in the NavMesh (vs. just being locally avoided by agents — see the two modes below). |
| `carveOnlyStationary` | `bool` | When `carving` is on: only re-carve once the obstacle is stationary, rather than continuously. |
| `carvingTimeToStationary` | `float` | Wait time (used with `carveOnlyStationary`) before the obstacle is treated as stationary and re-carved. |
| `carvingMoveThreshold` | `float` | Distance threshold that triggers a moving-carved-hole update. |
| `velocity` | `Vector3` | Velocity the obstacle moves at around the NavMesh — feeds agents' local avoidance prediction. |

### `NavMeshObstacleShape` (enum)

[Scripting API — NavMeshObstacleShape](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshObstacleShape.html)

- `Capsule` — capsule-shaped obstacle.
- `Box` — box-shaped obstacle.

## Two operating modes — pick deliberately

Per [AboutObstacles.html](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/AboutObstacles.html):

1. **Obstruction only** (`carving = false`) — agents locally avoid the obstacle as a moving obstacle, no NavMesh modification. Best fit for anything **continuously moving** (a patrolling enemy, a rolling boulder) — carving a continuously-moving object would thrash the NavMesh every frame.
2. **Carving** (`carving = true`) — cuts an actual hole in the NavMesh so pathfinding routes around it, not just local steering. Has an inherent **one-frame delay** between the obstacle's change and the NavMesh update reflecting it — don't rely on carving for a same-frame-reactive block. Two carving strategies:
   - **Carve Only Stationary** (default) — waits for `carvingTimeToStationary` after movement drops below `carvingMoveThreshold`, then carves. Fits things that mostly sit still and occasionally move (a parked vehicle, a closed door that sometimes opens).
   - **Carve When Moved** — updates continuously once past `carvingMoveThreshold`, suited to large, slow-moving objects (a tank, a boss) where the pathfinding-level rerouting genuinely needs to track its motion, at higher rebuild cost than the stationary strategy.

Don't default every dynamic obstacle to carving "to be safe" — a fast/small mover is usually cheaper and looks just as correct as pure local obstruction; reserve carving for objects that genuinely need to close/reroute pathfinding-level routes.

## `NavMeshAgent` + `NavMeshObstacle` don't mix on one GameObject

Per the package manual's [MixingComponents.html](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/MixingComponents.html): **do not have both an active `NavMeshAgent` and an active `NavMeshObstacle` on the same GameObject at the same time.** A common pattern that needs both roles at different times (e.g. an NPC that stops to become a physical roadblock) is to toggle one `enabled = false` while the other is `true`, never both `true` simultaneously — never author code that assumes both are live together.
