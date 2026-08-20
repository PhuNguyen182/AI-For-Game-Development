# NavMesh Queries & Pathfinding — Core Static API

The `UnityEngine.AI.NavMesh` static class plus its supporting query structs. This is the layer to reach for when a script needs to ask a question about the baked NavMesh (where's the nearest walkable point, can I get from A to B, is this line of sight blocked) without necessarily involving a `NavMeshAgent`.

## `NavMesh` (static class)

[Scripting API — NavMesh](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMesh.html) — "Singleton class to access the baked NavMesh." Namespace `UnityEngine.AI`. 100% static — no instance to construct.

**Static properties**

| Member | Type | Description |
|---|---|---|
| `AllAreas` | `int` (const) | Area mask constant including every NavMesh area — pass this when a query/agent shouldn't be area-restricted. |
| `avoidancePredictionTime` | `float` | How far into the future agents predict collisions for local avoidance. |
| `onPreUpdate` | `NavMesh.OnNavMeshPreUpdate` (delegate field) | Registers callback(s) invoked before the NavMesh system updates each frame. Note: this is a static delegate field, not a C# `event` — subscribe/unsubscribe like any multicast delegate. |
| `pathfindingIterationsPerFrame` | `int` | Max pathfinding nodes processed per frame for async path requests — tune under load if async path completion is visibly stalling. |

**Static methods — queries** (most common entry points for scripted navigation logic)

| Method | Signature | Notes |
|---|---|---|
| `SamplePosition` | `bool SamplePosition(Vector3 sourcePosition, out NavMeshHit hit, float maxDistance, int areaMask)` (+ `NavMeshQueryFilter` overload) | Finds the nearest point on the NavMesh within `maxDistance` (a **vertical projection**, not a full 3D nearest-point search). `hit.normal` is always `(0,0,0)` for this call specifically. Keep `maxDistance` tight (≈2× agent height) — it's a real cost driver. |
| `CalculatePath` | `bool CalculatePath(Vector3 sourcePosition, Vector3 targetPosition, int areaMask, NavMeshPath path)` (+ `NavMeshQueryFilter` overload) | Synchronous path computation into a caller-owned `NavMeshPath`. Returns `true` for both a **complete and a partial** path — always check `path.status` afterward, don't treat the bool return alone as "reached the destination". |
| `Raycast` | `bool Raycast(Vector3 sourcePosition, Vector3 targetPosition, out NavMeshHit hit, int areaMask)` (+ `NavMeshQueryFilter` overload) | Traces a straight line along the NavMesh surface. **Counter-intuitive return value: `true` means the ray was BLOCKED before reaching the target; `false` means it arrived unobstructed.** If it terminates on the NavMesh's own outer edge, `hit.mask == 0`; otherwise `hit.mask` holds the blocking polygon's area mask. Good for line-of-sight-along-the-floor checks. |
| `FindClosestEdge` | `bool FindClosestEdge(Vector3 sourcePosition, out NavMeshHit hit, int areaMask)` (+ `NavMeshQueryFilter` overload) | Locates the nearest NavMesh edge from a point — useful for "back away from the ledge" or edge-hugging behavior. |
| `CalculateTriangulation` | `NavMeshTriangulation CalculateTriangulation()` | Triangulates every NavMesh currently present in the scene — expensive, call sparingly (debug visualization, one-off spatial analysis), never per-frame. |

**Static methods — global area/settings/link management**

| Method | Purpose |
|---|---|
| `GetAreaCost(int)` / `SetAreaCost(int areaIndex, float cost)` | Get/set an area's traversal cost. **`NavMesh.SetAreaCost` is global — it affects every agent.** For a per-agent or per-query override use `NavMeshAgent.SetAreaCost`/`NavMeshQueryFilter.SetAreaCost` instead (same method name, narrower scope — don't conflate the three). |
| `GetAreaFromName(string)` / `GetAreaNames()` | Resolve an area's Inspector-configured name to its bitmask index, or list every area name — areas are project-configured (Navigation window Areas tab, or the package's per-agent-type area list), not fixed constants. |
| `AddNavMeshData(NavMeshData)` → `NavMeshDataInstance` / `RemoveNavMeshData(NavMeshDataInstance)` / `RemoveAllNavMeshData()` | Attach/detach baked `NavMeshData` to/from the live navigation system — the mechanism behind streaming NavMesh chunks in and out at runtime. |
| `AddLink(NavMeshLinkData)` → `NavMeshLinkInstance` / `RemoveLink(NavMeshLinkInstance)` | Add/remove a runtime-scripted link (see [navmesh-links.md](navmesh-links.md) for how this differs from the package's `NavMeshLink` component). |
| `IsLinkValid` / `IsLinkActive` / `SetLinkActive` / `IsLinkOccupied` / `GetLinkOwner` / `SetLinkOwner` | Query/manage a `NavMeshLinkInstance`'s state. |
| `CreateSettings()` → `NavMeshBuildSettings` / `GetSettingsByID(int)` / `GetSettingsByIndex(int)` / `GetSettingsCount()` / `GetSettingsNameFromID(int)` / `RemoveSettings(int)` | Manage the set of registered per-agent-type build settings entries — see [navmesh-baking-low-level-api.md](navmesh-baking-low-level-api.md). |

## `NavMeshQueryFilter` (struct)

[Scripting API — NavMeshQueryFilter](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshQueryFilter.html) — "Specifies which agent type and areas to consider when searching the NavMesh." Pass one to any `NavMesh.*` query overload that accepts it, instead of a bare `areaMask` int, when the query also needs to be scoped to a specific agent type or needs a per-query area cost override.

| Member | Type | Description |
|---|---|---|
| `agentTypeID` | `int` | Which agent type's NavMesh to query. |
| `areaMask` | `int` | Bitmask of traversable area types for this query. |
| `GetAreaCost(int areaIndex)` | `float` | Per-filter area cost multiplier. |
| `SetAreaCost(int areaIndex, float cost)` | — | Per-filter cost override — scoped to this filter instance only, unlike `NavMesh.SetAreaCost`'s global effect. |

## `NavMeshHit` (struct)

[Scripting API — NavMeshHit](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshHit.html) — "Information about a position that is the result of a query ran on the NavMesh." Returned by `SamplePosition`, `FindClosestEdge`, `Raycast`, and the corresponding `NavMeshAgent` instance methods.

| Member | Type | Description |
|---|---|---|
| `position` | `Vector3` | The resulting hit position. |
| `normal` | `Vector3` | Normal of the polygon edge the query terminated on. **Always `(0,0,0)` specifically for `SamplePosition` results** — meaningful for `Raycast`/`FindClosestEdge`. |
| `distance` | `float` | Distance from the query's source to the hit point. |
| `mask` | `int` | NavMesh area bitmask at the hit point. |
| `hit` | `bool` | Set for a particular valid-result situation (check alongside the calling method's own bool return). |

A result is only meaningful when both `distance` and `position` are finite — always check the calling method's `bool` return before trusting the `out NavMeshHit`.

## `NavMeshPath` (class)

[Scripting API — NavMeshPath](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshPath.html) — "A path as calculated by the navigation system," expressed as waypoints.

| Member | Description |
|---|---|
| `corners` | `Vector3[]` (read-only) — the path's waypoints. |
| `status` | [`NavMeshPathStatus`](#navmeshpathstatus-enum) (read-only). |
| `ClearCorners()` | Removes all corners from the path. |
| `GetCornersNonAlloc(Vector3[] results)` | Fetches corners into a caller-provided array — use this in any hot path instead of reading `corners` repeatedly, to avoid the array allocation `corners`'s getter implies each call. |

Constructed via `new NavMeshPath()`; passed to `NavMesh.CalculatePath`, `NavMeshAgent.CalculatePath`, `NavMeshAgent.path`/`NavMeshAgent.SetPath`.

### `NavMeshPathStatus` (enum)

[Scripting API — NavMeshPathStatus](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshPathStatus.html)

- `PathComplete` — the path terminates at the actual destination.
- `PathPartial` — the path cannot reach the destination; it terminates at the closest reachable point instead. **Always check for this after a `CalculatePath`/`SetDestination` call that returned `true`** — a partial path is not a failure signal by itself, but silently treating it as "arrived" is a common bug.
- `PathInvalid` — the path is not valid at all.

## `NavMeshTriangulation` (struct)

[Scripting API — NavMeshTriangulation](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshTriangulation.html) — "Contains data describing a triangulation of a navmesh." Returned by `NavMesh.CalculateTriangulation()`.

| Member | Type | Description |
|---|---|---|
| `vertices` | `Vector3[]` | Triangulation vertices. |
| `indices` | `int[]` | Triangle indices into `vertices`. |
| `areas` | `uint[]` | NavMesh area index per triangle. |

Use for debug visualization or one-off spatial analysis (e.g. custom minimap generation) — not a per-frame call, per the note under `CalculateTriangulation` above.

## Scope note

Everything on this page is **query/read-side** API — it answers "where can I go" and "how do I get there", it never decides *whether* an agent should go there. That decision (what to path toward, when to flee, target selection) is gameplay/AI logic and belongs in `Game.Core.*` per `coding-principles.md`'s Shared Core integrity rule — this skill's API only executes the already-decided move. See the Shared Core boundary guardrail in [SKILL.md](../SKILL.md).
