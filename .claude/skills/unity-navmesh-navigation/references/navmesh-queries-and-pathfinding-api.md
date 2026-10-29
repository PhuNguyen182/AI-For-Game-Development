# NavMesh Queries

What to do with an answer (pick a target, abandon a chase) is `csharp-engineer`'s Shared Core.

| Call | Answers |
|---|---|
| `SamplePosition` | Nearest mesh point within a radius; turns an arbitrary world point (a click) into a valid destination |
| `CalculatePath` | Full path into a caller-owned `NavMeshPath`, moving nothing |
| `Raycast` | Whether a straight line across the mesh is obstructed |
| `FindClosestEdge` | Nearest boundary and normal, to keep something off a ledge |
| `CalculateTriangulation` | Whole mesh as vertices/indices, for debug or offline analysis |

**`Raycast` returns true when the line is blocked**, the inverse of the physics raycast; read the physics way, code compiles and behaves backwards.

## Results
- `NavMeshHit`: position, distance, normal, area. A call returning without a valid hit yields a meaningless position.
- `NavMeshPath`: corners and status; the corner count tells whether a path exists.
- `NavMeshPathStatus`: complete / partial / invalid. Partial is a route toward the target that does not reach it, the status most code forgets to test.
- `NavMeshPath` is reusable; allocating one per query in a per-frame check is avoidable garbage.

## Cost scopes
| Scope | Reach |
|---|---|
| `NavMeshQueryFilter` | One query only |
| `NavMeshAgent.SetAreaCost` | One agent for its life |
| `NavMesh.SetAreaCost` (static) | Every agent and query in the project; easy to reach for, rarely intended |

## Links and areas from code
Add/remove link returns/consumes a handle ([navmesh-links.md](navmesh-links.md)); validity, activity and occupancy queries take that handle. Use the area name/index lookup rather than hardcoded magic numbers.
