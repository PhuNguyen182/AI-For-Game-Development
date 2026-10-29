# NavMeshObstacle

A blocker that never moves is level geometry and belongs in the bake ([navmesh-components-surface-and-modifiers.md](navmesh-components-surface-and-modifiers.md)).

| Mode | Effect | Fits |
|---|---|---|
| Obstruction only | Agents steer around it locally; mesh untouched, pathfinding still routes through it | Anything continuously moving (carving would rebuild every frame) |
| Carving | Cuts a hole so pathfinding reroutes | Something that closes a route (parked vehicle, shut door) |

Carving updates a frame behind the obstacle and cannot block on the frame it appears: a door must be carved before an agent reaches it. Every carve is a partial rebuild, so a crowd defaulted to carving is continuous mesh work.

## Carving strategy
- **Carve only when stationary**: waits for movement below a threshold for `carvingTimeToStationary`, then carves once. Tune so the hole appears after it stops; too short and a slowing vehicle carves and un-carves repeatedly.
- **Carve when moved**: re-carves once movement passes `carvingMoveThreshold` (which also stops jitter triggering rebuilds); for large slow movers, at higher rebuild cost.

## Fields
`shape` (box for a vehicle footprint, capsule for a character-shaped blocker), `size`/`radius`/`height`/`center`, and `velocity` (feeds agents' avoidance prediction so a moving obstruction is anticipated).

## Mixing with an agent
Never both enabled on one object; a character that must also block toggles between them. Obstacles never appear in the baked mesh.
