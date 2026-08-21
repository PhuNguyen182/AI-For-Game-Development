# NavMesh Links — three mechanisms, and why a link is ignored

Sources: [NavMesh Link](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavMeshLink.html), [Create a NavMesh link](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/CreateNavMeshLink.html), [NavMeshLink API](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/api/Unity.AI.Navigation.NavMeshLink.html), [OffMeshLink](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.OffMeshLink.html), [NavMeshLinkData](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshLinkData.html), [NavMeshLinkInstance](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshLinkInstance.html), [OffMeshLinkData](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.OffMeshLinkData.html).
Covers: SKILL.md §4 — **"Pick the link mechanism from where its endpoints come from"**.

Three systems connect two mesh locations across a gap, and they share enough
vocabulary to be routinely confused. One is current and authored, one is
current and scripted, one is deprecated. Whether a shortcut should exist at
all is a game rule and belongs to `csharp-engineer`.

## Choosing

| Mechanism | What it is | Status | Use when | Source |
|---|---|---|---|---|
| The authored link component | A component placed in a scene between two transforms | Current, and the default for hand-placed connectors | The endpoints are known at author time: a doorway, a ladder, a fixed jump | [NavMesh Link](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavMeshLink.html) |
| Runtime link data | A link created purely from code, with no component and no object | Current, and the procedural counterpart | The endpoints are computed at runtime — generated levels, streamed chunks, a shortcut that only sometimes exists | [NavMeshLinkData](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshLinkData.html) |
| The legacy link component | The pre-package authored link | Deprecated — stripped of its own members and removed from the component menu | Never for new work; only when migrating a project that still contains it | [OffMeshLink](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.OffMeshLink.html) |

**Critical caveat**: any tutorial or answer that configures fields on the
legacy component is describing an API that no longer exists at this version.
The URL still resolves, which makes the page look current when it is not.

## The authored component

| Member | What it decides | Source |
|---|---|---|
| Start and end transforms | The endpoints; they take precedence over the raw point fields, so a link with both set ignores the points entirely | [NavMeshLink API](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/api/Unity.AI.Navigation.NavMeshLink.html) |
| Width | The perpendicular extent of the connection, independent of the object's scale — a zero width is a single-file line rather than a doorway | [NavMeshLink API](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/api/Unity.AI.Navigation.NavMeshLink.html) |
| Cost modifier | Negative means use the area's own cost; any non-negative value is an explicit override, so zero is a free link rather than "no override" | [NavMeshLink API](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/api/Unity.AI.Navigation.NavMeshLink.html) |
| Bidirectional | Both ways, or start to end only — a one-way link is how a drop-down is modelled without letting agents climb it | [NavMeshLink API](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/api/Unity.AI.Navigation.NavMeshLink.html) |
| Area and agent type | Which area the link belongs to and which agent type may use it, both of which gate usability silently | [NavMeshLink API](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/api/Unity.AI.Navigation.NavMeshLink.html) |
| Activated | Whether pathfinding considers it at all, toggled at runtime for a shortcut that opens | [NavMeshLink API](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/api/Unity.AI.Navigation.NavMeshLink.html) |
| Auto update | Keeps the link following its transforms as they move, at the cost of continuous revalidation | [NavMeshLink API](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/api/Unity.AI.Navigation.NavMeshLink.html) |
| Occupied | Reports that an agent is currently on the link, for gating a second agent from entering it | [NavMeshLink API](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/api/Unity.AI.Navigation.NavMeshLink.html) |
| Update method | Rebuilds the link after its settings change from script; changing fields alone does not re-register it | [NavMeshLink API](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/api/Unity.AI.Navigation.NavMeshLink.html) |

Older names for several of these members remain on the class as obsolete
aliases; new code uses the current names, per `coding-principles.md`'s
Obsolete APIs section.

## Why a link is ignored

| Cause | Detail | Source |
|---|---|---|
| An end does not touch the mesh | The most common cause, and it reports nothing — verify with the Navigation overlay rather than by eye | [Create a NavMesh link](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/CreateNavMeshLink.html) |
| Not activated | A deactivated link is invisible to pathfinding while still visible in the scene | [NavMeshLink](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavMeshLink.html) |
| Area outside the agent's mask | The link is valid and simply unusable by that agent — see [agent-types-areas-and-navigation-window.md](agent-types-areas-and-navigation-window.md) | [NavMesh Link](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavMeshLink.html) |
| Wrong agent type | A link is registered for one agent type, so another type's mesh has no connection there | [NavMeshLink API](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/api/Unity.AI.Navigation.NavMeshLink.html) |

## Runtime links

| Type | Role | Source |
|---|---|---|
| Link data | The struct describing endpoints, width, cost, direction, area and agent type, handed to the static add call | [NavMeshLinkData](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshLinkData.html) |
| Link instance | The handle the add call returns, and the only way to remove, activate, or query the link afterwards — losing it strands the link for the session | [NavMeshLinkInstance](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.NavMeshLinkInstance.html) |
| Link state on an agent | The agent reports the link it is currently traversing through a struct named for the legacy system, and it is still populated for current links — so the legacy-sounding member is the right one to read | [OffMeshLinkData](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AI.OffMeshLinkData.html) |
