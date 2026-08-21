# Setup and Worlds — installation, ClientServerBootstrap, World types, build targets

Sources: [Installation](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/installation.html), [Set up client and server worlds](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/set-up-client-server-worlds.html), [Client and server worlds networking model](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/client-server-worlds.html), [Netcode Project Settings reference](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/project-settings.html), [ClientServerBootstrap API](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/api/Unity.NetCode.ClientServerBootstrap.html).
Covers: SKILL.md §4 — **"Stand up client and server Worlds through `ClientServerBootstrap` before any networked system exists"**.

Which `World` a system runs in, how those Worlds get created, and which
build-time defines and Project Settings decide the shipped topology. The
transport/driver that gets attached to a World is
[transport-and-connection.md](transport-and-connection.md); exact component
names live in [api-and-settings-reference.md](api-and-settings-reference.md).

## Installation

| Requirement | Value | Source |
|---|---|---|
| Minimum Editor version | 2022.3.0f1, or Unity 6 LTS | [Installation](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/installation.html) |
| Required packages | `com.unity.netcode`, `com.unity.entities.graphics` | [Installation](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/installation.html) |
| IDE (Roslyn source generators) | Visual Studio 2022+, or Rider 2021.3.3+ | [Installation](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/installation.html) |
| Install method | Package Manager → "Add package by name" per package id | [Installation](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/installation.html) |

## World types

| World / flag | Runs | Source |
|---|---|---|
| `ClientSimulation` (`WorldFlags.GameClient`) | Local client simulation, prediction, presentation | [Client and server worlds](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/client-server-worlds.html) |
| `ServerSimulation` (`WorldFlags.GameServer`) | Authoritative simulation, no `PresentationSystemGroup` | [Client and server worlds](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/client-server-worlds.html) |
| `ThinClientSimulation` | Stripped test client — no rendering, no ghost spawning | [Client and server worlds](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/client-server-worlds.html) |
| `LocalSimulation` | No Netcode systems at all — not a multiplayer World | [Client and server worlds](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/client-server-worlds.html) |

`[WorldSystemFilter(WorldSystemFilterFlags.ClientSimulation)]` (and the
`ServerSimulation`/`ThinClientSimulation`/`LocalSimulation` variants, `|`-
combinable) restricts a system to the matching World types; a system inside
an `[UpdateInGroup]` group inherits that group's filter. `PresentationSystemGroup`
exists only in the client World; `GhostInputSystemGroup` exists in client,
thin-client, and local Worlds, never on the server.

## `ClientServerBootstrap`

| Member | Effect | Source |
|---|---|---|
| `CreateClientWorld(name)` / `CreateServerWorld(name)` | Create one client or server `World` | [ClientServerBootstrap](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/api/Unity.NetCode.ClientServerBootstrap.html) |
| `CreateThinClientWorld()` | Create a stripped test-client `World` | [ClientServerBootstrap](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/api/Unity.NetCode.ClientServerBootstrap.html) |
| `CreateLocalWorld(name)` | Create a World with no Netcode systems | [ClientServerBootstrap](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/api/Unity.NetCode.ClientServerBootstrap.html) |
| `RequestedPlayType` | The active `PlayType` — configures which Worlds/drivers get built | [ClientServerBootstrap](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/api/Unity.NetCode.ClientServerBootstrap.html) |
| `ClientWorld(s)` / `ServerWorld(s)` / `ThinClientWorlds` | Static accessors for existing Worlds of each kind | [ClientServerBootstrap](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/api/Unity.NetCode.ClientServerBootstrap.html) |
| `AutoConnectPort` | Default `0`; non-zero triggers auto-connect using `DefaultConnectAddress`/`DefaultListenAddress` | [ClientServerBootstrap](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/api/Unity.NetCode.ClientServerBootstrap.html) |
| `k_MaxNumThinClients` | Constant `1000` — hard cap on Editor-spawned thin clients | [ClientServerBootstrap](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/api/Unity.NetCode.ClientServerBootstrap.html) |

### `PlayType` enum

| Value | Meaning | Source |
|---|---|---|
| `Client` | Client World only — must connect out | [PlayType](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/api/Unity.NetCode.ClientServerBootstrap.PlayType.html) |
| `Server` | Server World only — can only listen | [PlayType](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/api/Unity.NetCode.ClientServerBootstrap.PlayType.html) |
| `ClientAndServer` (default in-Editor) | Both — can host and play locally at once | [PlayType](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/api/Unity.NetCode.ClientServerBootstrap.PlayType.html) |

## Server fixed-timestep loop

| Setting (on `ClientServerTickRate`) | Effect | Source |
|---|---|---|
| `SimulationTickRate` | Server simulation rate — **default 60**/second | [Client and server worlds](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/client-server-worlds.html) |
| `NetworkTickRate` | Snapshot send rate; must be **less than and a common factor of** `SimulationTickRate` | [Introduction to prediction](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/intro-to-prediction.html) |
| `MaxSimulationStepsPerFrame` | Caps simulation steps per frame | [Client and server worlds](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/client-server-worlds.html) |
| `TargetFrameRateMode` | `BusyWait` / `Sleep` / `Auto` | [Client and server worlds](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/client-server-worlds.html) |
| `HandshakeApprovalTimeoutMS` | Default **5000 ms** before an unapproved connection times out | [Connecting server and clients](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/network-connection.html) |

The client's own loop runs at a dynamic timestep, except the prediction code,
which runs at the server's fixed `SimulationTickRate` — the client receives
`ClientServerTickRate` during the connection handshake so both sides agree.
See [prediction-core.md](prediction-core.md) for the tick-batching mechanics
this feeds.

## Build target and scripting defines

| Netcode Client Target | Build Type | Defines set | Source |
|---|---|---|---|
| `ClientAndServer` | Standalone Client | Neither `UNITY_CLIENT` nor `UNITY_SERVER`, in Editor or build | [Project Settings](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/project-settings.html) |
| `ClientOnly` | Standalone Client | `UNITY_CLIENT` (build only) — `ClientServerBootstrap.CreateServerWorld` throws `NotSupportedException` | [Project Settings](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/project-settings.html) |
| — | Dedicated Game Server platform target | `UNITY_SERVER` (Editor and build, automatic) | [Project Settings](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/project-settings.html) |

`ClientAndServer` lets a player host their own server from inside the game
executable (client-hosted / listen-server topology, the prerequisite for
[host-migration.md](host-migration.md)); `ClientOnly` strips that capability
so only a dedicated-server build can host. Pick this from the GDD's topology
before writing bootstrap code — it decides which code paths even compile.
`NetCodeConfig` (a `ScriptableObject`, Edit → Project Settings → Multiplayer)
lets `ClientServerTickRate`/`ClientTickRate`/`GhostSendSystemData`/transport
`NetworkConfigParameter` be set without code.

**Critical caveat**: `set-up-client-server-worlds.html` and
`creating-multiplayer-gameplay.html` are navigation-hub pages in the 6.6
manual with no content of their own — the facts above were traced to the
child pages actually linked from them (Installation, Client and server
worlds, Project Settings, the `ClientServerBootstrap`/`PlayType` API pages).
