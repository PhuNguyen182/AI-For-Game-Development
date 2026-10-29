# NavMeshAgent

The destination is `csharp-engineer`'s; the Animator that consumes velocity is `unity-animation`'s.

## Steering
| Member | Decides |
|---|---|
| `speed`, `angularSpeed`, `acceleration` | High speed with low angular speed gives wide arcs (reads as a vehicle) |
| `stoppingDistance` | Too small and the agent oscillates trying to hit an exact point |
| `autoBraking` | Right for a single target, wrong for a patrol (slows at every waypoint) |
| `radius`, `height` | Per-instance avoidance cylinder, distinct from the agent type's bake dimensions; a mismatch makes the agent clip walls it was baked to clear |
| `baseOffset` | Cylinder offset from the pivot |
| `obstacleAvoidanceType` | Avoidance quality tier; trades CPU for crowd untangling |
| `avoidancePriority` | Lower number wins; reads backwards at first |
| `areaMask` | Traversable areas ([agent-types-areas-and-navigation-window.md](agent-types-areas-and-navigation-window.md)) |

## Path state
`SetDestination`'s return, `pathPending` and `pathStatus` answer three different questions; checking only the first reports success for a destination never reached.

| Member | Note |
|---|---|
| `SetDestination` return | Request accepted, not reachable |
| `pathPending` | Path still computing; path and status are stale until false |
| `pathStatus` | Complete / partial / invalid; partial walks as far as possible and stops short silently |
| `isPathStale` | Path may no longer match the mesh after a rebuild (streaming world: agents walking through walls) |
| `remainingDistance` | Zero while pending; an arrival check that ignores `pathPending` fires on the request frame |
| `isOnNavMesh` | An agent spawned off the mesh silently refuses every command |
| `isStopped` | Pause keeping the path; `ResetPath` discards work |

## Transform and Animator
| Member | Note |
|---|---|
| `velocity`, `desiredVelocity` | Feed the Animator speed parameter; a separate transform delta will disagree |
| `updatePosition`, `updateRotation` | Off when root motion drives the transform |
| `nextPosition` | Simulated position; root-motion movement writes it back so simulation and visible character do not diverge |
| `updateUpAxis` | Alignment to a tilted/curved world mesh |
| `steeringTarget` | Next path corner (for cornering-speed rules; manual page `ControlAgentSpeedForCornering`) |

## Methods
| Method | Effect |
|---|---|
| `Warp` | Relocate agent and simulation together; the way to teleport |
| `CalculatePath` | Path into a caller-owned object without moving or replacing the live path; speculative reachability |
| `SetPath` / `ResetPath` | Assign a precomputed path / clear it |
| `Raycast` | Same inverted return as the static one ([navmesh-queries-and-pathfinding-api.md](navmesh-queries-and-pathfinding-api.md)) |
| `SetAreaCost` | This agent only, unlike the static setter |
