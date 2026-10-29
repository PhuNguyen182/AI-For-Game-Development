# Setup and Worlds

Pages (6.6): `installation`, `client-server-worlds`, `project-settings`, API `Unity.NetCode.ClientServerBootstrap`. The hub pages `set-up-client-server-worlds` and `creating-multiplayer-gameplay` hold no content; facts come from their child pages.

- Packages: `com.unity.netcode`, `com.unity.entities.graphics`. IDE with Roslyn source generators: Visual Studio 2022+ or Rider 2021.3.3+.

## World types

| World | Runs |
|---|---|
| `ClientSimulation` (`WorldFlags.GameClient`) | Local simulation, prediction, presentation |
| `ServerSimulation` (`WorldFlags.GameServer`) | Authoritative simulation, no `PresentationSystemGroup` |
| `ThinClientSimulation` | Stripped test client: no rendering, no ghost spawning |
| `LocalSimulation` | No Netcode systems; not a multiplayer World |

- `[WorldSystemFilter(WorldSystemFilterFlags.X)]` (flags `|`-combinable) restricts a system; a system in an `[UpdateInGroup]` group inherits the group's filter.
- `PresentationSystemGroup` exists only on the client. `GhostInputSystemGroup` exists on client, thin-client and local Worlds, never the server.

## `ClientServerBootstrap`
- `CreateClientWorld(name)`, `CreateServerWorld(name)`, `CreateThinClientWorld()`, `CreateLocalWorld(name)`; static accessors `ClientWorld(s)`, `ServerWorld(s)`, `ThinClientWorlds`.
- `RequestedPlayType` (`PlayType`): `Client` (must connect out), `Server` (listen only), `ClientAndServer` (Editor default).
- `AutoConnectPort` default 0; non-zero auto-connects using `DefaultConnectAddress`/`DefaultListenAddress`.
- `k_MaxNumThinClients` = 1000, the Editor cap.

## Tick and handshake settings (`ClientServerTickRate`)
- `SimulationTickRate` default 60, `NetworkTickRate` (see [prediction-core.md](prediction-core.md)), `MaxSimulationStepsPerFrame`, `TargetFrameRateMode` (`BusyWait`/`Sleep`/`Auto`), `HandshakeApprovalTimeoutMS` default 5000.
- The client sends nothing of its own here: it receives `ClientServerTickRate` in the handshake. Client prediction runs at the server's fixed rate; the rest of the client loop uses a dynamic timestep.

## Build target and defines (Edit → Project Settings → Multiplayer)

| Netcode Client Target | Defines |
|---|---|
| `ClientAndServer` | Neither `UNITY_CLIENT` nor `UNITY_SERVER`; a player can host (prerequisite for [host-migration.md](host-migration.md)) |
| `ClientOnly` | `UNITY_CLIENT` in builds; `CreateServerWorld` throws `NotSupportedException` |
| Dedicated Server platform | `UNITY_SERVER`, automatic |

- Also in Project Settings: Excluded Baking System Assemblies (per client/server) and Additional Scripting Defines.
- The `NetCodeConfig` asset sets `ClientServerTickRate`, `ClientTickRate`, `GhostSendSystemData` and transport `NetworkConfigParameter` without code.
