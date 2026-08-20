# NavMesh Links — Three Distinct Systems, Pick Correctly

Unity has **three separate "link" mechanisms** that all connect two NavMesh locations across a gap the mesh itself doesn't cover (a jump, a doorway, a ladder, a teleport-style shortcut). They are easy to conflate because they share vocabulary — confirm which one a task actually needs before writing code or dragging a component.

| System | What it is | Status | Use when |
|---|---|---|---|
| **`NavMeshLink` (package component)** | An Inspector-authored `MonoBehaviour` you place in a scene between two Transforms. | **Current — the default choice for anything authored by hand in the Editor.** | You're placing a fixed connector in a scene: a doorway, a jump gap, a ladder, a scripted shortcut between two known points. |
| **`OffMeshLink` (built-in component)** | The legacy Editor-authored link component. | **Deprecated — removed from the Add Component menu, stripped of its own members.** | Never for new work. Only relevant when migrating an old project — see the Upgrade Guide notes below. |
| **`NavMeshLinkData` / `NavMeshLinkInstance` (built-in scripted API)** | A runtime-only link created purely from code via `NavMesh.AddLink()`, with no GameObject/component at all. | **Current — the procedural/runtime-generation counterpart to the `NavMeshLink` component.** | The link's endpoints are computed at runtime (procedural level generation, a puzzle that only sometimes opens a shortcut) and don't correspond to a scene object worth authoring by hand. |

## `NavMeshLink` (package component) — the authored/Inspector link

[Manual — NavMeshLink](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavMeshLink.html) · [Manual — Create a NavMesh link](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/CreateNavMeshLink.html) · [API — Unity.AI.Navigation.NavMeshLink](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/api/Unity.AI.Navigation.NavMeshLink.html)

**Setup workflow**: place two small marker GameObjects at the two connection points, add a `NavMeshLink` component (Add Component → Navigation → NavMesh Link), assign `Start Transform`/`End Transform`.

| Member | Type | Notes |
|---|---|---|
| `startTransform` / `endTransform` | `Transform` | Take precedence over the raw point fields below when non-null. |
| `startPoint` / `endPoint` | `Vector3` (local) | Used only when the corresponding Transform field is unassigned. |
| `width` | `float` | Perpendicular width of the link's ends — independent of the GameObject's scale. |
| `costModifier` | `float` | **Negative = use the area's default cost; non-negative = override the cost explicitly.** This sign convention is easy to get backwards — a `0` is a valid explicit override, not "no override". |
| `bidirectional` | `bool` | Both directions vs. start→end only. |
| `area` | `int` | Area type assigned to the link (Walkable / Not Walkable / Jump / custom). |
| `agentTypeID` | `int` | Which agent type may use this link. |
| `activated` | `bool` | Enables/disables use in pathfinding. Scene view: black gizmo = active, red = inactive. |
| `autoUpdate` | `bool` | Keeps the link's ends synced to transform changes at runtime. |
| `occupied` | `bool` (RO) | True while an agent is currently on the link. |
| `UpdateLink()` | method | Rebuilds/replaces the link using its current settings — call after changing endpoints/width/area via script. |

**Obsolete members on this same class** (kept for migration awareness, don't use in new code): `autoUpdatePositions` → use `autoUpdate`; `biDirectional` → use `bidirectional`; `costOverride` → use `costModifier`; `UpdatePositions()` → use `UpdateLink()`.

**Troubleshooting a link that's ignored by an agent** (from the manual): confirm both ends actually touch the NavMesh (check via the Navigation overlay's "Show NavMesh"); confirm `activated` is `true`; confirm the traversing `NavMeshAgent`'s `areaMask` includes the link's area type — a link whose area isn't in the agent's mask is silently unusable by that agent, not an error.

## `OffMeshLink` (built-in, deprecated) — do not use for new work

[Scripting API — OffMeshLink](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.OffMeshLink.html) — page banner verbatim: *"The OffMeshLink component is no longer supported and will be removed. Use NavMeshLink instead."* As of Unity 6000.5 the class is stripped down to only inherited `Behaviour`/`Component`/`Object` members — its classic fields (`activated`, `autoUpdatePositions`, `biDirectional`, `costOverride`, `occupied`, `startTransform`, `endTransform`) are gone from the page entirely. It's also removed from the Add Component menu, and omitted from the `UnityEngine.AIModule` landing page's class listing even though the URL still resolves.

Related still-live supporting types (not themselves deprecated, but only meaningful in the legacy-link/migration context):

- [`OffMeshLinkData`](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.OffMeshLinkData.html) (struct) — "State of OffMeshLink." Members: `activated`, `endPos`, `startPos`, `linkType` (`OffMeshLinkType`), `owner`, `valid` — all read-only except `owner`. Still populated on `NavMeshAgent.currentOffMeshLinkData`/`nextOffMeshLinkData` **for whatever link type the agent is currently traversing**, including a `NavMeshLink`, so this struct is still relevant even though the `OffMeshLink` component itself is not.
- [`OffMeshLinkType`](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.OffMeshLinkType.html) (enum) — `LinkTypeManual`, `LinkTypeDropDown` (vertical drop), `LinkTypeJumpAcross` (horizontal jump).

**Migration**: [Manual — Upgrade Guide](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/UpgradeGuide.html) documents a `Window > AI > Navigation Updater` tool with an "OffMesh Link Converter" that auto-migrates `OffMeshLink` instances to `NavMeshLink`; **script references to the old component must still be updated by hand** via Unity's Script Updating Consent utility — the automated converter only touches scene/prefab data, not code.

## `NavMeshLinkData` / `NavMeshLinkInstance` (built-in scripted links)

Purely procedural — no component, no GameObject required. This is the mechanism behind connecting NavMesh chunks generated at runtime (streaming worlds, procedural dungeons) without hand-placing a `NavMeshLink` for every connection.

### `NavMeshLinkData` (struct)

[Scripting API — NavMeshLinkData](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshLinkData.html) — "Used for runtime manipulation of links connecting polygons of the NavMesh." Passed to `NavMesh.AddLink()`.

| Field | Type | Description |
|---|---|---|
| `startPosition` / `endPosition` | `Vector3` | The link's two endpoints. |
| `width` | `float` | If positive, the link is a rectangle aligned along the start→end line rather than a zero-width line. |
| `costModifier` | `float` | If positive, overrides the pathfinder's cost to traverse the link. |
| `bidirectional` | `bool` | Traversable both directions if `true`; start→end only otherwise. |
| `area` | `int` | Area type/category for the link. |
| `agentTypeID` | `int` | Which agent type this link is available to. |

### `NavMeshLinkInstance` (struct)

[Scripting API — NavMeshLinkInstance](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshLinkInstance.html) — "Represents a link available for pathfinding." The handle `NavMesh.AddLink()` returns; a default-constructed/empty instance is invalid and inactive by definition, not a real link. Managed entirely through `NavMesh` static methods: `NavMesh.RemoveLink()`, `NavMesh.IsLinkValid()`, `NavMesh.IsLinkOccupied()`, `NavMesh.IsLinkActive()`, `NavMesh.SetLinkActive()`, `NavMesh.GetLinkOwner()`/`NavMesh.SetLinkOwner()` — see [navmesh-queries-and-pathfinding-api.md](navmesh-queries-and-pathfinding-api.md).

## Decision guide

- Fixed, hand-placed connector visible in the scene → **`NavMeshLink` component**.
- Old project still has `OffMeshLink` instances → run the **Navigation Updater**'s OffMesh Link Converter, then fix up script references manually; never author a new `OffMeshLink`.
- Endpoints only known/computed at runtime, no sensible scene object to hang a component on → **`NavMesh.AddLink(NavMeshLinkData)`**.
