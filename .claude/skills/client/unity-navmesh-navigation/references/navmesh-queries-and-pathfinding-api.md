# NavMesh Queries — static queries, filters, hits, paths

Sources: [NavMesh](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMesh.html), [NavMeshHit](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshHit.html), [NavMeshPath](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshPath.html), [NavMeshPathStatus](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshPathStatus.html), [NavMeshQueryFilter](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshQueryFilter.html), [NavMeshTriangulation](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshTriangulation.html).
Covers: SKILL.md §4 — **"Read a NavMesh raycast's true as blocked, not as clear"**.

What can be asked of the mesh without an agent, and the return conventions
that read backwards. Deciding what to do with an answer — pick a target,
abandon a chase — is `csharp-engineer`'s Shared Core.

## Queries

| Call | What it answers | Source |
|---|---|---|
| Sample position | The nearest point on the mesh within a radius — the correct way to turn an arbitrary world point, such as a click, into a valid destination | [NavMesh](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMesh.html) |
| Calculate path | A full path between two points into a caller-owned path object, without moving anything | [NavMesh](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMesh.html) |
| Raycast | Whether a straight line across the mesh is obstructed | [NavMesh](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMesh.html) |
| Find closest edge | The nearest mesh boundary and its normal, for keeping something away from a ledge | [NavMesh](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMesh.html) |
| Calculate triangulation | The whole mesh as vertices and indices, for debug visualisation or an offline analysis | [NavMeshTriangulation](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshTriangulation.html) |

**Critical caveat**: the raycast returns true when the line is **blocked**,
the inverse of the physics raycast it resembles. Code that reads it as the
physics convention compiles, runs, and behaves exactly backwards.

## Interpreting results

| Type | What it decides | Source |
|---|---|---|
| Hit struct | Carries the position, the distance, the normal, the area, and a validity flag — a call that returns without a valid hit has produced a position that means nothing | [NavMeshHit](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshHit.html) |
| Path object | Holds the corner list and the status; the corners are the actual route, and their count is what tells you whether a path exists at all | [NavMeshPath](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshPath.html) |
| Path status | Complete, partial, or invalid — partial means a route toward the target that does not reach it, which is the status most code forgets to test | [NavMeshPathStatus](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshPathStatus.html) |
| Reusing a path object | Path objects are reusable; allocating one per query in a per-frame check is avoidable garbage, per `performance-and-algorithms.md` | [NavMeshPath](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshPath.html) |

## Scoping a query

| Scope | Reach | Source |
|---|---|---|
| Query filter | Area mask and per-area costs for one query only, leaving every agent and the project untouched | [NavMeshQueryFilter](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshQueryFilter.html) |
| Agent cost setter | One agent, for the rest of its life — the right scope for a per-character preference | [NavMeshAgent](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshAgent.html) |
| Static cost setter | Every agent and every query in the project — a global change that is easy to reach for and rarely what was meant | [NavMesh](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMesh.html) |

## Link management from code

| Call | Effect | Source |
|---|---|---|
| Add and remove link | Creates a runtime link from link data and returns its handle, or removes it — see [navmesh-links.md](navmesh-links.md) | [NavMesh](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMesh.html) |
| Link validity, activity, occupancy | Whether a handle still refers to a real link, whether pathfinding uses it, and whether an agent is on it right now | [NavMesh](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMesh.html) |
| Area name and index lookup | Converts between the names shown in the Navigation window and the indices the API takes, so an area is not hardcoded as a magic number | [NavMesh](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMesh.html) |
