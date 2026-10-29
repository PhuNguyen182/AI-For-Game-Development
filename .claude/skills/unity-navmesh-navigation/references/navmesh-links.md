# NavMesh Links

Whether a shortcut should exist is a game rule (`csharp-engineer`).

| Mechanism | Status | Use when |
|---|---|---|
| Authored `NavMeshLink` component | Current | Endpoints known at author time (doorway, ladder, fixed jump) |
| Runtime `NavMeshLinkData` | Current | Endpoints computed at runtime (generated levels, streamed chunks, a shortcut that only sometimes exists) |
| `OffMeshLink` component | Deprecated: members stripped, removed from the component menu | Never for new work; only when migrating a project that contains it |

The `OffMeshLink` docs URL still resolves, so the page looks current. Any tutorial configuring its fields describes an API that no longer exists.

## NavMeshLink members
| Member | Note |
|---|---|
| Start/End transforms | Take precedence over the raw point fields |
| Width | Perpendicular extent, independent of scale; zero is single-file, not a doorway |
| Cost modifier | Negative = use the area's cost; any non-negative is an override, so 0 is a free link |
| Bidirectional | Off = start to end only (a drop-down agents cannot climb) |
| Area, agent type | Both gate usability silently |
| Activated | Toggle at runtime for a shortcut that opens |
| Auto update | Follows moving transforms at continuous revalidation cost |
| Occupied | An agent is on the link; gate a second agent |
| Update method | Changing fields from script does not re-register the link; call it |

Older member names remain as obsolete aliases; new code uses the current names.

## Why a link is ignored (none report anything)
1. An end does not touch the mesh (most common); verify with the Navigation overlay, not by eye.
2. Not activated.
3. Area outside the agent's mask ([agent-types-areas-and-navigation-window.md](agent-types-areas-and-navigation-window.md)).
4. Wrong agent type: another type's mesh has no connection there.

## Runtime links
- `NavMeshLinkData`: endpoints, width, cost, direction, area, agent type, passed to the static add call.
- `NavMeshLinkInstance`: handle from the add call and the only way to remove, activate or query the link; losing it strands the link for the session.
- An agent reports the link it is traversing through `OffMeshLinkData`, a struct named for the legacy system but still populated for current links.
