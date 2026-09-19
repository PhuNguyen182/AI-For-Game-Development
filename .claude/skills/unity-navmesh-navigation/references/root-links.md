# Root Links — Unity 6000.5 navigation module and AI Navigation 2.0

Source: the root index pages listed below, as provided for this skill.
Covers: the whole skill — provenance and version anchor for every file in
this folder.

Anchors every link in this folder to Unity 6000.5's Scripting API and
`com.unity.ai.navigation@2.0`. Navigation is documented across two trees this
skill treats as one system, and knowing which tree owns a question is the
first decision in every task here.

## The two layers

| Layer | Owns | Source |
|---|---|---|
| Built-in `UnityEngine.AI` module | Runtime queries and simulation: static queries, the agent, the obstacle, the low-level builder, runtime link data — what a script actually calls | [UnityEngine.AIModule](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/UnityEngine.AIModule.html) |
| `com.unity.ai.navigation` package | Authoring and baking: the surface, the modifiers, the authored link, the Navigation window, and every current conceptual page | [AI Navigation Manual](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/index.html) |
| Package API surface | The five authoring types the package adds | [Unity.AI.Navigation namespace](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/api/Unity.AI.Navigation.html) |

**Critical caveat**: at this Editor version the classic built-in navigation
Manual pages no longer resolve. The package manual is the only current
conceptual source, and the built-in agent's scripting page links there rather
than to a built-in page. A remembered Manual page title is not a source.

## Which file answers which question

| Question | File | Source |
|---|---|---|
| How do I bake, and how do I change what a bake sees | [navmesh-components-surface-and-modifiers.md](navmesh-components-surface-and-modifiers.md) | [NavMesh Surface](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavMeshSurface.html) |
| How do I build from geometry that has no scene object | [navmesh-baking-low-level-api.md](navmesh-baking-low-level-api.md) | [NavMeshBuilder](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshBuilder.html) |
| How are agent sizes and area costs defined | [agent-types-areas-and-navigation-window.md](agent-types-areas-and-navigation-window.md) | [Areas and costs](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/AreasAndCosts.html) |
| Why does my character move like that, or stop short | [navmesh-agent.md](navmesh-agent.md) | [NavMeshAgent](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshAgent.html) |
| How does something dynamic block agents | [navmesh-obstacles-and-avoidance.md](navmesh-obstacles-and-avoidance.md) | [About obstacles](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/AboutObstacles.html) |
| How do I bridge a gap, and why is my link ignored | [navmesh-links.md](navmesh-links.md) | [NavMesh Link](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavMeshLink.html) |
| What can I ask the mesh from code | [navmesh-queries-and-pathfinding-api.md](navmesh-queries-and-pathfinding-api.md) | [NavMesh](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMesh.html) |
| How do I build at runtime, or migrate an old project | [runtime-building-samples-and-upgrade.md](runtime-building-samples-and-upgrade.md) | [Upgrade guide](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/UpgradeGuide.html) |

## Core type index

| Type | Source |
|---|---|
| `NavMesh` | [NavMesh](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMesh.html) |
| `NavMeshAgent` | [NavMeshAgent](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshAgent.html) |
| `NavMeshObstacle` | [NavMeshObstacle](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshObstacle.html) |
| `NavMeshPath`, `NavMeshHit`, `NavMeshQueryFilter` | [UnityEngine.AIModule](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/UnityEngine.AIModule.html) |
| `NavMeshBuilder`, `NavMeshData`, `NavMeshBuildSettings` | [NavMeshBuilder](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshBuilder.html) |
| `NavMeshLinkData`, `NavMeshLinkInstance` | [NavMeshLinkData](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshLinkData.html) |
| `NavMeshSurface`, `NavMeshModifier`, `NavMeshModifierVolume`, `NavMeshLink`, `CollectObjects` | [Unity.AI.Navigation namespace](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/api/Unity.AI.Navigation.html) |

Keep the `6000.5` and `@2.0` segments when following any link. Page slugs are
stable across nearby versions, so substitute the installed Editor and package
versions rather than assuming these ones.
