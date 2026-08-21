---
name: unity-navmesh-navigation
description: >
  Technique for Unity's navigation stack across both of its layers — the
  built-in `UnityEngine.AI` module (`NavMesh` queries, `NavMeshAgent`
  steering, `NavMeshObstacle` carving, `NavMeshBuilder` and `NavMeshData`,
  `NavMeshLinkData` runtime links) and the `com.unity.ai.navigation` package
  (`NavMeshSurface` baking, `NavMeshModifier` and `NavMeshModifierVolume` area
  overrides, the authored `NavMeshLink`, agent types and area costs in the
  Navigation window). Use when a character must path, a mesh must bake or
  stream, or a gap needs a connector. Not for: choosing the destination
  (`csharp-engineer`); the input behind a click-to-move
  (`unity-input-system`); locomotion blending (`unity-animation`); physics
  unrelated to navigation (`unity-3d-physics`, `unity-physics`).
---

# Unity NavMesh Navigation — Baking, Agents, Obstacles, Links, Runtime Building

## Bundled resources

### References
Read-only context, loaded on demand so SKILL.md itself stays short.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Both documentation trees, the version pins, which layer owns what, the type index | Starting any task here, or a Manual page fails to resolve |
| [navmesh-components-surface-and-modifiers.md](references/navmesh-components-surface-and-modifiers.md) | `NavMeshSurface` fields and methods, collect modes, `NavMeshModifier`, `NavMeshModifierVolume` | Baking a mesh, or a region bakes wrong |
| [navmesh-baking-low-level-api.md](references/navmesh-baking-low-level-api.md) | `NavMeshBuilder`, `NavMeshData`, build settings, build sources, markup, debug flags | The declarative components cannot express the source geometry |
| [agent-types-areas-and-navigation-window.md](references/agent-types-areas-and-navigation-window.md) | Agent-type dimensions, area types and costs, mask semantics, HeightMesh | Adding an agent type, or making traversal asymmetric |
| [navmesh-agent.md](references/navmesh-agent.md) | Steering, avoidance, path state, transform-sync fields, methods | Configuring or scripting a moving character |
| [navmesh-obstacles-and-avoidance.md](references/navmesh-obstacles-and-avoidance.md) | Obstruction against carving, carving strategies, the agent-and-obstacle conflict | Something dynamic must block or reroute agents |
| [navmesh-links.md](references/navmesh-links.md) | The three link mechanisms, their fields, and why a link is ignored | Connecting a gap the mesh does not cover |
| [navmesh-queries-and-pathfinding-api.md](references/navmesh-queries-and-pathfinding-api.md) | `NavMesh` static queries, filters, hit and path types, path status | Querying the mesh from code |
| [runtime-building-samples-and-upgrade.md](references/runtime-building-samples-and-upgrade.md) | Runtime rebuild and streaming entry points, the shipped samples, the upgrade path | Building at runtime, or migrating a legacy project |

## 1. Objective
Get characters moving across a mesh that is actually there, through gaps that are actually connected. Navigation fails quietly in a distinctive way: a path is returned, the agent moves, and it stops somewhere short — because the status was partial rather than complete and nothing checked. A link whose area is outside the agent's mask is unusable and reports nothing. A raycast returns true and reads as success when it means blocked. A stale bake looks identical to a correct one until an agent refuses to enter a room.

## 2. Role
Act as the navigation specialist for the client track — the tool reached for whenever a mesh must be baked or streamed, a character must move across it, something must block it, or a gap must be bridged. You execute movement that has already been decided; you never choose the destination, blend the locomotion, or simulate the body.

## 3. When to invoke this skill
- Baking a NavMesh for a scene or region, or overriding how specific objects and volumes contribute to that bake.
- Configuring a `NavMeshAgent`: steering, avoidance, area mask, stopping, path handling.
- Making something dynamic block or reroute agents.
- Connecting a gap the mesh does not cover — a jump, a ladder, a doorway, a shortcut that only sometimes opens.
- Building or streaming a mesh at runtime for a procedural or open world.
- Defining agent types or area costs, including asymmetric traversal where some agents may use a route and others may not.
- Querying the mesh from code for a position, a path, or an edge.
- Migrating a project off the legacy in-scene bake and its deprecated link component.
- An agent stops short of its destination, refuses a link, or will not enter a region that looks navigable.
- Negative trigger: which destination to move to, when to move, or which target to chase — behaviour trees, utility scoring, patrol-route selection — that is `csharp-engineer`'s Shared Core, per `coding-principles.md`'s Shared Core integrity rule; this skill executes an already-chosen destination.
- Negative trigger: reading the click, tap, or stick behind a move order — that is `unity-input-system`, which hands this skill a screen position or a world point.
- Negative trigger: the Animator Controller and blend tree that visualise the movement — that is `unity-animation`; this skill supplies the agent's velocity it consumes.
- Negative trigger: rigid bodies, colliders, joints, or DOTS physics with no navigation involvement — `unity-3d-physics` and `unity-physics`; this skill only touches collider geometry as a bake source.
- Negative trigger: a Cinemachine dolly track that resembles a waypoint route — unrelated system, `unity-cinemachine-authoring`.

## 4. How to use this skill
1. **Confirm which documentation layer the task actually needs** — the package owns authoring and baking, the built-in module owns runtime queries and scripted building, and most features touch both, per [root-links.md](references/root-links.md). The classic built-in navigation Manual pages no longer resolve, so a remembered page title is not a source.
2. **Bake through `NavMeshSurface` before reaching for the low-level builder** — the component expresses collect mode, geometry source, voxel and tile size, and minimum region area declaratively, per [navmesh-components-surface-and-modifiers.md](references/navmesh-components-surface-and-modifiers.md). Drop to [navmesh-baking-low-level-api.md](references/navmesh-baking-low-level-api.md)'s builder only when the source geometry has no scene object to collect from, per KISS in `coding-principles.md`.
3. **Override areas per object and per region with modifiers rather than by editing geometry** — a modifier marks one object, a modifier volume marks a space with no geometry of its own, and both keep the art untouched, per [navmesh-components-surface-and-modifiers.md](references/navmesh-components-surface-and-modifiers.md). Re-bake after any change to geometry, modifiers, or agent types, because a stale bake looks exactly like a correct one.
4. **Add an agent type only when a character's dimensions or slope tolerance genuinely differ** — the type drives the bake, so each one is another mesh to build and hold, per [agent-types-areas-and-navigation-window.md](references/agent-types-areas-and-navigation-window.md). Cosmetic scale differences do not need one.
5. **Configure the agent's steering to the character rather than leaving the defaults** — braking, stopping distance, avoidance tier and priority all change how the movement reads, and the highest avoidance tier is the most expensive one, so it is a choice rather than a safe default, per [navmesh-agent.md](references/navmesh-agent.md).
6. **Check `pathStatus` and `pathPending` rather than the call's return value** — a destination request succeeds when the request was accepted, not when the destination is reachable, and a partial path moves the agent as close as it can before stopping short with nothing reported, per [navmesh-agent.md](references/navmesh-agent.md).
7. **Choose obstruction or carving from how the object actually moves** — obstruction for anything continuously moving, carving only where pathfinding itself must reroute, and carving carries a frame of delay so it cannot block same-frame, per [navmesh-obstacles-and-avoidance.md](references/navmesh-obstacles-and-avoidance.md). Never leave an agent and an obstacle both enabled on one object.
8. **Pick the link mechanism from where its endpoints come from** — the authored component for anything placed by hand, the scripted link data for endpoints computed at runtime, and never the deprecated component, which no longer carries its own members, per [navmesh-links.md](references/navmesh-links.md). A link both ends of which do not touch the mesh is silently unusable.
9. **Update a runtime NavMesh incrementally rather than rebuilding the surface** — the asynchronous update touches only affected regions, and attaching or detaching pre-baked data is what streams a world without rebuilding anything, per [runtime-building-samples-and-upgrade.md](references/runtime-building-samples-and-upgrade.md). Start from the package's own streaming samples rather than deriving a scheme cold.
10. **Read a NavMesh raycast's true as blocked, not as clear** — the return is inverted from the physics raycast it resembles, and the mistake produces logic that behaves exactly backwards while compiling and running, per [navmesh-queries-and-pathfinding-api.md](references/navmesh-queries-and-pathfinding-api.md).
11. **Feed the Animator from the agent's own velocity** — the agent already knows its speed and its desired speed, so computing one separately from transform deltas produces a second, disagreeing number. The Animator side of that handoff is `unity-animation`'s.
12. **Keep the destination decision in `Game.Core.*`** — which target, which route, whether to give up the chase, are all game rules, per `coding-principles.md`'s Shared Core integrity rule; this layer receives a resolved point and moves to it.
13. **Back any bake-time or avoidance-tier claim with a measurement** — voxel size, tile size and avoidance quality all trade cost against accuracy in ways that depend on the scene, per `performance-and-algorithms.md`'s Verification section.

## 5. Specific goals / tasks this skill performs
- Baking a NavMesh through `NavMeshSurface`, with modifier and volume overrides.
- Dropping to the low-level builder for procedural source geometry with no scene representation.
- Defining agent types and area costs, including asymmetric traversal through area masks.
- Configuring agent steering, avoidance, and path-state handling.
- Choosing and configuring obstruction or carving for dynamic blockers.
- Authoring links, or creating them at runtime from computed endpoints.
- Building and streaming meshes at runtime.
- Querying the mesh for positions, paths, and edges.
- Migrating a legacy in-scene bake and its deprecated links to the current package.
- Out of scope: destination and target selection (`csharp-engineer`); the input behind a move order (`unity-input-system`); locomotion blending (`unity-animation`); physics unrelated to navigation (`unity-3d-physics`, `unity-physics`); escalated navigation performance work (`tech-lead-performance`).

## 6. Output format
```
## Navigation Work — <feature or agent name>
- Layers touched: <built-in module / package / both>
- Bake: <NavMeshSurface config — collect mode, geometry source, voxel and tile size, minimum region area — or "low-level builder" and why>
- Modifiers: <per-object and per-volume overrides applied — or "none">
- Agent types and areas: <types defined, area costs and masks, and the traversal rule behind each>
- Agent config: <steering, avoidance tier and priority, area mask, transform-sync fields>
- Path handling: <how pathPending and pathStatus are checked, and what happens on a partial path>
- Obstacles: <obstruction or carving, strategy, and why — or "none">
- Links: <authored component or runtime link data, and why that one>
- Runtime building: <incremental update, data attach and detach, or "bake-time only">
- Shared Core boundary: confirmed no destination or target chosen in navigation-layer code
- Verified on: <Profiler bake time or frame cost behind any performance claim, or "no claim made">
- Layer: Game.Client.* components and scripts
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what the delivered navigation setup does not cover>
- Latent concerns: <failure modes not yet triggered: agent counts untested, regions unbaked, trade-offs knowingly deferred>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: "Bake this dungeon, add a patrolling guard, and let it cross the broken bridge."
- Output: one `NavMeshSurface` on the level root collecting children from physics colliders, with the minimum region area raised so tiny slivers behind decor stop appearing as navigable islands. A modifier volume marks the hazard pit not walkable rather than the art being changed. The guard's agent uses a moderate avoidance tier, and the patrol route itself comes from Shared Core — this layer only receives each waypoint. An authored link spans the bridge gap, with both ends confirmed to touch the baked mesh, since a link that misses is silently ignored.

**Example 2**
- Input: "The agent says the path succeeded but stops halfway to the objective."
- Output: the request return value only reports that the request was accepted. The status was partial, which the agent honours by walking as far as it can and stopping — no warning, no failure. Added a partial-path check and, in this scene, a missing link across a raised platform that had left the far room disconnected from the bake.

**Example 3**
- Input: "Add an `OffMeshLink` for the ladder, that is what the tutorial uses."
- Output: declined — that component is deprecated and, at this Editor version, has been stripped of its own members and removed from the component menu, so a tutorial predating that is describing an API that no longer exists. Used the package's authored link instead, and noted that an old project carrying the deprecated component has a converter, though script references to it still need updating by hand.

**Example 4**
- Input: "A tank should block a corridor when parked, without thrashing the mesh while it drives."
- Output: an obstacle sized to the tank's footprint, carving enabled but restricted to stationary, with the time-to-stationary tuned so the hole appears after it actually stops rather than while it is slowing. Confirmed no agent component is enabled on the same object at the same time, since the two conflict. A Profiler capture confirmed no per-frame rebuild while driving, and one carve cost after parking.

## 8. Edge cases & guardrails
- Never read a successful destination request as a reachable destination — check the path status, and handle partial explicitly.
- Never read a NavMesh raycast's true as clear — it means blocked, the opposite of the physics raycast it resembles.
- Never author the deprecated link component — it has been stripped of its members and removed from the component menu; use the authored package component or runtime link data.
- Never cite a classic built-in navigation Manual page — they no longer resolve, and the package manual is the only current conceptual source.
- Never leave an agent and an obstacle both enabled on one object — toggle between them if the object genuinely needs both roles.
- Never carve by default — a small or fast mover is cheaper and looks identical as obstruction, and carving is delayed by a frame regardless.
- Never assume a link is being used because it exists — both ends must touch the mesh, it must be activated, and its area must be inside the traversing agent's mask, and none of those failures report anything.
- Never confuse the three area-cost scopes — the global setter reaches every agent, and the agent and filter setters do not.
- Never leave a bake stale after changing geometry, a modifier, or an agent type — a stale mesh is indistinguishable from a correct one until something refuses to path.
- Never relocate an agent by writing its transform — use the warp call, or the agent and its simulated position disagree.
- Never let navigation-layer code choose a target or abandon a chase — it moves to a point `Game.Core.*` already decided on.
- Never claim a bake-time or avoidance-tier improvement without a measurement, per `performance-and-algorithms.md`'s Verification section.
- If a task needs the sparsely documented low-level navigation types, say plainly that member-level documentation does not exist at this version rather than inventing plausible members.
