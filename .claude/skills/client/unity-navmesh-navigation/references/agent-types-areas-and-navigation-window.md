# Agent Types, Areas and Costs — the project-wide navigation settings

Sources: [About agents](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/AboutAgents.html), [Navigation window](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavigationWindow.html), [Areas and costs](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/AreasAndCosts.html), [HeightMesh](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/HeightMesh.html).
Covers: SKILL.md §4 — **"Add an agent type only when a character's dimensions or slope tolerance genuinely differ"**.

The settings that live once per project rather than per scene or per
character, and the mechanism behind letting some agents use a route that
others cannot. Which agent should be excluded from which area is a game rule
and belongs to `csharp-engineer`.

## Agent types

| Setting | What it decides | Source |
|---|---|---|
| Radius | Minimum clearance from walls and ledges, and the basis for the default voxel size — the single field that most changes what bakes as navigable | [Navigation window](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavigationWindow.html) |
| Height | Vertical clearance needed to pass under geometry | [Navigation window](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavigationWindow.html) |
| Step Height | The tallest step the agent walks up without a link, which is what separates stairs that bake as walkable from stairs that do not | [Navigation window](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavigationWindow.html) |
| Max Slope | The steepest ramp that bakes navigable | [Navigation window](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavigationWindow.html) |
| Drop Height and Jump Distance | The limits for automatically generated links, so a gap wider than the jump distance simply produces no connection | [Navigation window](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavigationWindow.html) |
| Base Offset | Repositions the simulated cylinder relative to the object's pivot, for a model whose pivot is not at its feet | [About agents](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/AboutAgents.html) |

**Critical caveat**: an agent is simulated as an upright cylinder regardless
of the model. Every dimension above describes that cylinder, and each agent
type requires its own baked mesh — so a new type is another bake, another
asset, and another thing to keep current.

## Areas and costs

| Subject | What it decides | Source |
|---|---|---|
| Built-in areas | Walkable, not walkable, and jump exist by default, with a bounded set of custom slots beyond them | [Areas and costs](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/AreasAndCosts.html) |
| Cost | A multiplier on traversed distance, so a higher cost biases paths away from an area without making it impassable — the difference between "avoid the mud" and "cannot enter the mud" | [Areas and costs](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/AreasAndCosts.html) |
| Overlap resolution | Where geometry or modifiers claim different areas, the higher-indexed area generally wins, except that not walkable always wins regardless of index | [Areas and costs](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/AreasAndCosts.html) |
| Area mask on an agent | Restricts which areas that agent may traverse at all — the mechanism behind asymmetric routes, such as a door only some agents can use | [Areas and costs](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/AreasAndCosts.html) |
| Cost scopes | Costs can be set globally, per agent, or per query filter, and the three are not interchangeable — see [navmesh-queries-and-pathfinding-api.md](navmesh-queries-and-pathfinding-api.md) | [Areas and costs](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/AreasAndCosts.html) |

| Consequence | Detail | Source |
|---|---|---|
| A link's area must be in the agent's mask | Otherwise the link exists, is active, touches the mesh, and is still unusable by that agent, with nothing reported — see [navmesh-links.md](navmesh-links.md) | [Areas and costs](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/AreasAndCosts.html) |
| Cost is not a barrier | A high cost still permits the route when no cheaper one exists, so a cost is the wrong tool for a hard restriction | [Areas and costs](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/AreasAndCosts.html) |

## Height Mesh

| Subject | What it decides | Source |
|---|---|---|
| Purpose | A supplementary surface used for placing agents accurately on stairs and slopes, where the simplified navigable mesh otherwise leaves them floating or sunk | [HeightMesh](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/HeightMesh.html) |
| Cost | Extra bake time and memory, so it is enabled where the placement error is visible rather than everywhere | [HeightMesh](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/HeightMesh.html) |
