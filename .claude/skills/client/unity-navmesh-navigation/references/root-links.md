# Root Links

Root/index pages this skill is built from (Unity 6000.5 Scripting API + `com.unity.ai.navigation` package version 2.0). Follow their own in-page navigation for anything not covered by the other files in this folder.

- [Scripting API — UnityEngine.AIModule](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/UnityEngine.AIModule.html) — the built-in engine module's class/struct/enum landing page (namespace `UnityEngine.AI`, plus six new `Unity.AI.Navigation.LowLevel.*` types).
- [AI Navigation package — Manual](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/index.html) — the package's conceptual documentation landing page (Navigation System overview, component reference, how-tos, samples, upgrade guide).
- [AI Navigation package — API index](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/api/index.html) — chrome-only landing page; the real class listing is one level down.
- [AI Navigation package — Unity.AI.Navigation namespace](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/api/Unity.AI.Navigation.html) — the actual 5-type API surface (`NavMeshSurface`, `NavMeshModifier`, `NavMeshModifierVolume`, `NavMeshLink`, `CollectObjects`).
- [Scripting API — NavMesh](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMesh.html) — the core static query/pathfinding entry point.
- [Scripting API — NavMeshAgent](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshAgent.html) — the per-character navigation component.

## How the two doc sets relate

Unity's navigation surface is split across **two separate documentation trees that this skill treats as one system**:

1. **`UnityEngine.AI` (built-in engine module, `UnityEngine.AIModule`)** — ships with the Editor itself, no package install needed. Owns the runtime *query and simulation* layer: `NavMesh` (static queries), `NavMeshAgent` (per-character steering), `NavMeshObstacle` (dynamic carving/avoidance), the low-level build types (`NavMeshBuilder`, `NavMeshData`, `NavMeshBuildSettings`, `NavMeshBuildSource`, …), and the runtime-scripted link API (`NavMeshLinkData`/`NavMeshLinkInstance`). This is what a script actually calls at runtime.
2. **`com.unity.ai.navigation` (package, installed via Package Manager)** — the modern authoring/baking layer: `NavMeshSurface`, `NavMeshModifier`, `NavMeshModifierVolume`, `NavMeshLink` (the authored-in-the-Inspector component), the Navigation window (Agents/Areas tabs), and all current conceptual documentation (workflows, how-tos, samples, upgrade guide). **As of Unity 6000.5, every classic built-in Manual page for navigation (`nav-BuildingNavMesh.html`, `nav-CreateNavMeshAgent.html`, `OffMeshLinks.html`, etc.) 404s** — this package's manual is the sole current source of conceptual documentation; the `NavMeshAgent` scripting page itself now links out to the package manual instead of a built-in Manual page.

Confirm which layer a task actually needs before citing a page: baking/placing a NavMesh in a scene, or configuring per-object area/link authoring → the **package** (`Unity.AI.Navigation.*`, Navigation window); a script doing pathfinding queries, driving an agent at runtime, or building `NavMeshData` procedurally from code → the **built-in module** (`UnityEngine.AI.*`). Most real features touch both.

Page slugs are stable across nearby Unity versions; re-derive the exact version segment (`6000.5`, package `@2.0`) if the installed Editor/package version differs.
