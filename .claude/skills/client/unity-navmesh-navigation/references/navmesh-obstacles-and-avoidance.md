# NavMeshObstacle — obstruction, carving, and the agent conflict

Sources: [NavMeshObstacle](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshObstacle.html), [About obstacles](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/AboutObstacles.html), [Create a NavMesh obstacle](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/CreateNavMeshObstacle.html), [Mixing components](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/MixingComponents.html).
Covers: SKILL.md §4 — **"Choose obstruction or carving from how the object actually moves"**.

The component for things that block agents without being part of the bake,
and the one decision it forces. A blocker that never moves is level geometry
and belongs in the bake instead — see
[navmesh-components-surface-and-modifiers.md](navmesh-components-surface-and-modifiers.md).

## The two modes

| Mode | What happens | Fits | Source |
|---|---|---|---|
| Obstruction only | Agents steer around it locally; the mesh is untouched, so pathfinding still routes through the space it occupies | Anything continuously moving — a patrolling enemy, a rolling boulder — where carving would rebuild the mesh every frame | [About obstacles](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/AboutObstacles.html) |
| Carving | Cuts a hole so pathfinding itself reroutes, not just steering | Something that genuinely closes a route — a parked vehicle, a shut door — where agents should path a different way entirely | [About obstacles](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/AboutObstacles.html) |

**Critical caveat**: carving updates a frame behind the obstacle. It cannot
block anything on the same frame it appears, so a door that must be shut
before an agent reaches it needs the carve to have already happened.

## Carving strategy

| Strategy | Behaviour | Fits | Source |
|---|---|---|---|
| Carve only when stationary | Waits until movement drops below a threshold for a set time, then carves once | Things that mostly sit still and occasionally move; tune the time so the hole appears after it stops rather than while it is slowing | [NavMeshObstacle](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshObstacle.html) |
| Carve when moved | Re-carves continuously once movement passes a distance threshold | Large slow movers where pathfinding must track the motion, at a higher rebuild cost | [NavMeshObstacle](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshObstacle.html) |

| Field | What it decides | Source |
|---|---|---|
| `shape`, `size`, `radius`, `height`, `center` | A box or a capsule and its extent — the box is the right fit for a vehicle footprint, the capsule for a character-shaped blocker | [NavMeshObstacle](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshObstacle.html) |
| `carvingTimeToStationary` | How long stillness must last before the hole appears; too short and a slowing vehicle carves and un-carves repeatedly | [NavMeshObstacle](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshObstacle.html) |
| `carvingMoveThreshold` | How far it must move before an existing hole is updated, which is what stops small jitter triggering rebuilds | [NavMeshObstacle](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshObstacle.html) |
| `velocity` | Feeds agents' local avoidance prediction, so a moving obstruction is anticipated rather than reacted to | [NavMeshObstacle](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshObstacle.html) |

## Mixing with an agent

| Rule | Consequence | Source |
|---|---|---|
| Never both enabled on one object | An active agent and an active obstacle on the same object conflict; a character that must also become a blocker toggles between them | [Mixing components](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/MixingComponents.html) |
| Both excluded from the bake | Obstacles and agents are runtime actors, not bake geometry, so an obstacle never appears in the baked mesh regardless of settings | [NavMesh Surface](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavMeshSurface.html) |
| Carving is not free | Every carve is a partial rebuild; defaulting every dynamic object to carving turns a crowd into continuous mesh work | [About obstacles](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/AboutObstacles.html) |
