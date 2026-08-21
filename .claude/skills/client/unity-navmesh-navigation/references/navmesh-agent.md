# NavMeshAgent — steering, avoidance, path state, transform sync

Sources: [NavMeshAgent](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshAgent.html), [ObstacleAvoidanceType](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.ObstacleAvoidanceType.html), [Control agent speed for cornering](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/ControlAgentSpeedForCornering.html), [UnityEngine.AIModule](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/UnityEngine.AIModule.html).
Covers: SKILL.md §4 — **"Configure the agent's steering to the character rather than leaving the defaults"**, **"Check `pathStatus` and `pathPending` rather than the call's return value"**, **"Feed the Animator from the agent's own velocity"**.

The component that moves one character, and the handful of members that
decide whether the movement reads correctly and whether the code above it can
trust what it is told. The Animator that consumes the velocity is
`unity-animation`'s; the destination is `csharp-engineer`'s.

## Steering

| Member | What it decides | Source |
|---|---|---|
| `speed`, `angularSpeed`, `acceleration` | The movement's character — a high speed with low angular speed produces wide arcs, which reads as a vehicle rather than a person | [NavMeshAgent](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshAgent.html) |
| `stoppingDistance` | How close counts as arrived; too small and the agent oscillates on the spot trying to reach an exact point | [NavMeshAgent](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshAgent.html) |
| `autoBraking` | Deceleration near the destination — correct for a single target, wrong for a patrol, where it makes the agent slow at every waypoint | [NavMeshAgent](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshAgent.html) |
| `radius` and `height` | The per-instance avoidance cylinder, distinct from the agent type's bake-time dimensions — the two disagreeing is why an agent clips walls it was baked to clear | [NavMeshAgent](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshAgent.html) |
| `baseOffset` | Vertical offset of that cylinder from the object's pivot, for a model whose origin is not at its feet | [NavMeshAgent](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshAgent.html) |
| `obstacleAvoidanceType` | Quality tier for local avoidance between agents, from none to highest; the tiers trade CPU directly for how well a crowd untangles | [ObstacleAvoidanceType](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.ObstacleAvoidanceType.html) |
| `avoidancePriority` | Who yields when two agents meet — a lower number wins, which reads backwards to most people the first time | [NavMeshAgent](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshAgent.html) |
| `areaMask` | Which areas this agent may traverse — see [agent-types-areas-and-navigation-window.md](agent-types-areas-and-navigation-window.md) | [NavMeshAgent](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshAgent.html) |

## Path state

| Member | What it decides | Source |
|---|---|---|
| `SetDestination` return | Reports that the request was accepted, not that the destination is reachable — treating it as arrival confirmation is the single most common mistake here | [NavMeshAgent](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshAgent.html) |
| `pathPending` | A path is still being computed, so the path and its status are not yet meaningful — read immediately after a destination request, both are stale | [NavMeshAgent](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshAgent.html) |
| `pathStatus` | Complete, partial, or invalid; a partial path is honoured by walking as far as possible and stopping short, silently | [NavMeshAgent](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshAgent.html) |
| `isPathStale` | The path may no longer match the mesh after a rebuild, which is what turns a streaming world into agents walking through walls | [NavMeshAgent](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshAgent.html) |
| `remainingDistance` | Distance along the path, and zero while the path is pending — an arrival check that does not also test pending fires immediately on the frame of the request | [NavMeshAgent](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshAgent.html) |
| `isOnNavMesh` | Whether the agent is bound to a mesh at all; an agent spawned off the mesh silently refuses every command | [NavMeshAgent](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshAgent.html) |
| `isStopped` | Halts movement while keeping the path, which is the correct pause; clearing the path instead discards work that has to be redone | [NavMeshAgent](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshAgent.html) |

**Critical caveat**: the request return value, the pending flag, and the path
status answer three different questions. Code that checks only the first
reports success for a destination the agent will never reach.

## Driving the transform and the Animator

| Member | What it decides | Source |
|---|---|---|
| `velocity` and `desiredVelocity` | Current motion and intended motion including avoidance — the values an Animator's speed parameter should read, rather than a separately computed transform delta that will disagree | [NavMeshAgent](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshAgent.html) |
| `updatePosition` and `updateRotation` | Whether the component writes the transform at all; both go off when animation root motion should drive it instead, and the agent's simulated position is then read separately | [NavMeshAgent](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshAgent.html) |
| `nextPosition` | The simulated position, which is what root-motion-driven movement writes back so the simulation and the visible character do not diverge | [NavMeshAgent](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshAgent.html) |
| `updateUpAxis` | Alignment to a non-horizontal surface, for a mesh baked on a tilted or curved world | [NavMeshAgent](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshAgent.html) |
| `steeringTarget` | The next corner on the path rather than the destination — the value a cornering-speed rule reads | [Control agent speed for cornering](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/ControlAgentSpeedForCornering.html) |

## Methods

| Method | Effect | Source |
|---|---|---|
| `Warp` | Relocates the agent and its simulation together — the correct way to teleport, since writing the transform leaves the simulation behind | [NavMeshAgent](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshAgent.html) |
| `CalculatePath` | Computes a path into a caller-owned object without moving the agent or replacing its live path — the speculative reachability check | [NavMeshAgent](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshAgent.html) |
| `SetPath` and `ResetPath` | Assigns a precomputed path, or clears the current one entirely | [NavMeshAgent](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshAgent.html) |
| `Raycast` | Agent-scoped straight-line test with the same inverted return as the static one — see [navmesh-queries-and-pathfinding-api.md](navmesh-queries-and-pathfinding-api.md) | [NavMeshAgent](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshAgent.html) |
| `SetAreaCost` | Adjusts a cost for this agent only, unlike the static setter that reaches every agent in the project | [NavMeshAgent](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshAgent.html) |
