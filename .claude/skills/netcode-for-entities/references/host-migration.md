# Host Migration

Pages (6.6): `host-migration/` set (introduction, API and components, add to project, requirements, considerations, systems and data, Lobby and Relay integration, limitations). Only for client-hosted (`ClientAndServer`) topology; a dedicated server has no host to lose.

## Status
Experimental. Enable with the `ENABLE_HOST_MIGRATION` scripting define. Manual: "Host migration is an experimental feature so the API and implementation can change in the future." Flag it in the handoff.

## Prerequisites
- Unity Cloud project linked ("Connect to Unity Cloud"); Lobby, Relay and Authentication services; `com.unity.services.multiplayer` alongside `com.unity.netcode`.

## Captured in a snapshot
Connected clients, added components, loaded scenes, ghost and prefab info, user components on server connection entities (+ `NetworkStreamInGame`), all ghost component data (not only `[GhostField]`), server-only components with at least one `[GhostField]`, tick and elapsed time, and components in `NonGhostMigrationComponents` on an `IncludeInMigration` entity.

## API

| Member | Effect |
|---|---|
| `HostMigrationData.Get(fromWorld, toData)` / `.Set(fromData, toWorld)` | Pull data out of / deploy into a server World |
| `EnableHostMigration` | Singleton that turns collection on |
| `HostMigrationConfig` | `StoreOwnGhosts` (false), `MigrationTimeout` (10 s), `ServerUpdateInterval` (2 s, 0 = every update) |
| `HostMigrationInProgress` | Present until done; gate initialization systems on its absence |
| `NetworkStreamIsReconnected` | Lets code tell a reconnect from a first connect |
| `IncludeInMigration` + `NonGhostMigrationComponents` | Opt a non-ghost component in |
| `IsMigrated` | On every migrated entity; use to re-resolve references that do not survive |

```csharp
serverWorld.EntityManager.CreateEntity(ComponentType.ReadOnly<EnableHostMigration>()); // collect
var ctor = new HostMigrationDriverConstructor(hostRelayData, new RelayServerData());
if (!HostMigration.MigrateDataToNewServerWorld(ctor, ref migrationDataArray)) { /* failed */ }
```

`MigrateDataToNewServerWorld` creates the server World, deploys via `HostMigrationUtility.SetHostMigrationData`, listens on IPC and repoints the local client. `HostMigration.ConfigureClientAndConnect` does it for clients whose role is unchanged, using the new host's Relay allocation.

## Lobby and Relay
- Player ID stays stable (`AuthenticationService.Instance.PlayerId`). Clients detect a host change by polling the Lobby's `HostId`/`relayJoinCode` data through `LobbyEventCallbacks.LobbyChanged`.
- After migration the whole Relay allocation and join sequence is invalidated. Race: players can learn of the new host before its join code is ready. Pair the code with the player ID that made the allocation and ignore it until that matches the Lobby's current host.

## Hard limits

| Limit | Value |
|---|---|
| Snapshot size | 10 MiB |
| Migration data region | Always US Central |
| Relay keepalive before disconnect signal | 10 s, fixed |
| Host election | Random, no ranking |
| Ghosts with child entities | Unsupported |
| WebGL | Unsupported |

- Lobby timers (Active Lifespan, Disconnect Removal Time, Disconnect Host Migration Time; suggested 120 s / 60 s / 5 s) are separate from the fixed 10 s Relay keepalive; both gate detection speed, so tune together.
- Destroyed entities and pre-spawned ghosts in entity scenes are not tracked for destruction and can reappear on the new host. Verify the specific state your feature needs survives.
