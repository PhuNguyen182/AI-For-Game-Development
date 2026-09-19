# Host Migration — surviving the loss of a client-hosted server

Sources: [Host migration](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/host-migration/host-migration.html), [Introduction to host migration](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/host-migration/host-migration-intro.html), [Host migration API and components](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/host-migration/host-migration-api.html), [Add host migration to your project](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/host-migration/add-host-migration.html), [Requirements](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/host-migration/host-migration-requirements.html), [Considerations](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/host-migration/host-migration-considerations.html), [Systems and data](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/host-migration/host-migration-systems.html), [Lobby and Relay integration](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/host-migration/lobby-relay-integration.html), [Limitations and known issues](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/host-migration/host-migration-limitations.html).
Covers: SKILL.md §4 — **"Add host migration only for a client-hosted topology that actually needs to survive the host leaving"**.

Only relevant to a **client-hosted / listen-server** topology (`Netcode
Client Target = ClientAndServer`, per [setup-and-worlds.md](setup-and-worlds.md))
— a dedicated-server topology has no "host" to lose and does not need this.

## Status: experimental

Must be manually enabled with the **`ENABLE_HOST_MIGRATION`** scripting
define (Project Settings → Player). Verbatim from the manual: *"Host
migration is an experimental feature so the API and implementation can
change in the future."* Flag this explicitly in the Handoff note per
`coding-principles.md`'s Handoff section — it is not a stable, load-bearing
guarantee yet.

## Prerequisites

- Unity Cloud Dashboard project, linked via "Connect to Unity Cloud".
- Services: Unity **Lobby**, **Relay**, **Authentication**.
- Packages: `com.unity.services.multiplayer` (Multiplayer Services SDK) alongside `com.unity.netcode`.

## What gets captured in a migration snapshot

Connected-clients list, added components, loaded scenes, ghost/ghost-prefab
info, all user components on server connection entities (plus
`NetworkStreamInGame` presence), **all** ghost component data (not just
`[GhostField]`-marked fields), server-only components with at least one
`[GhostField]`, current tick and elapsed time, and any component listed in
the `NonGhostMigrationComponents` buffer on an `IncludeInMigration`-tagged
entity.

## Core API

| Member | Effect | Source |
|---|---|---|
| `HostMigrationData.Get(fromWorld, toData)` / `.Set(fromData, toWorld)` | Pull migration data out of / deploy it into a server World | [Host migration systems and data](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/host-migration/host-migration-systems.html) |
| `EnableHostMigration` | Singleton component that turns the collection system on | [Host migration API](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/host-migration/host-migration-api.html) |
| `HostMigrationConfig` | `StoreOwnGhosts` (default `false`), `MigrationTimeout` (default 10 s), `ServerUpdateInterval` (default 2 s, `0` = every system update) | [Host migration API](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/host-migration/host-migration-api.html) |
| `HostMigrationInProgress` | Present while migration is incomplete — gate initialization systems on its **absence** | [Considerations](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/host-migration/host-migration-considerations.html) |
| `NetworkStreamIsReconnected` | Added to a connection so client/server code can react to a reconnect distinctly from a first connect | [Host migration API](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/host-migration/host-migration-api.html) |
| `IncludeInMigration` + `NonGhostMigrationComponents` buffer | Opt a non-ghost component into migration explicitly | [Introduction](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/host-migration/host-migration-intro.html) |
| `IsMigrated` | Added to every entity that came through a migration — use it to re-resolve entity references that don't survive the host change | [Considerations](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/host-migration/host-migration-considerations.html) |

## Enabling collection and migrating a new host

```csharp
// New host: start collecting migration data.
var serverWorld = ClientServerBootstrap.ServerWorld;
serverWorld.EntityManager.CreateEntity(ComponentType.ReadOnly<EnableHostMigration>());

// Elected host: deploy previously downloaded migration data into a fresh server world.
var driverConstructor = new HostMigrationDriverConstructor(hostRelayData, new RelayServerData());
if (!HostMigration.MigrateDataToNewServerWorld(driverConstructor, ref migrationDataArray))
    Debug.LogError("Host migration failed while migrating data to new server world");
```

`MigrateDataToNewServerWorld` creates the server World via
`ClientServerBootstrap.CreateServerWorld`, deploys the snapshot through
`HostMigrationUtility.SetHostMigrationData`, listens on IPC, and reconfigures
the local client to connect to it — `HostMigration.ConfigureClientAndConnect`
does the same for clients whose role does not change, pointed at the new
host's fresh Relay allocation instead.

## Lobby + Relay flow (why the host can be found again)

Player ID stays stable across a migration
(`AuthenticationService.Instance.PlayerId`); the Lobby's `HostId`/`relayJoinCode`
Data properties are what a client polls via `LobbyEventCallbacks.LobbyChanged`
to detect a host change and fetch the new Relay join code.

**Critical caveat**: after a migration, the **entire Relay allocation and
join sequence is invalidated** — every previously used allocation ID and
join code stops working, and there is a documented race where other players
can be notified of the host change before the new host's Relay join code is
actually ready. Pair the join code with the player ID that created the
allocation, and have clients ignore it until that ID matches the lobby's
current host.

## Hard limits (not configurable)

| Limit | Value | Source |
|---|---|---|
| Migration snapshot size | **10 MiB** per snapshot | [Limitations](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/host-migration/host-migration-limitations.html) |
| Migration data region | Always US Central | [Limitations](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/host-migration/host-migration-limitations.html) |
| Relay keepalive before disconnect signal | 10 s, fixed | [Introduction](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/host-migration/host-migration-intro.html) |
| Host election | Random — no candidate ranking | [Limitations](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/host-migration/host-migration-limitations.html) |
| Ghosts with child entities | **Not supported** for migration | [Limitations](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/host-migration/host-migration-limitations.html) |
| WebGL | Not supported | [Limitations](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/host-migration/host-migration-limitations.html) |

The Lobby's own dashboard-configurable timers (Active Lifespan, Disconnect
Removal Time, Disconnect Host Migration Time — recommended starting values
120 s / 60 s / 5 s) are a **separate** knob from the fixed 10 s Relay
keepalive — both gate how fast a lost host is actually detected, and both
must be tuned together.

**Critical caveat**: destroyed entities and pre-spawned ghosts inside
entity scenes are **not** tracked for destruction across a migration — they
can reappear on the new host. Do not treat host migration as a full,
lossless world snapshot; verify the specific game state your feature
depends on actually survives before shipping it.
