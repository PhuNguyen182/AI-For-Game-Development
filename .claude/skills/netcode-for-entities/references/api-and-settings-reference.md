# API and Settings Reference — every Netcode-specific component, and Project Settings

Sources: [Netcode-specific components and types](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/entities-list.html), [Netcode Project Settings reference](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/project-settings.html).
Covers: SKILL.md §4 — **"Stand up client and server Worlds through `ClientServerBootstrap` before any networked system exists"**.

Look-up table for an exact component/setting name whose behavior is
explained in another file — use this to confirm spelling and placement, not
as the first place to learn a concept. Every entry below traces to a
concept file: connection components to
[transport-and-connection.md](transport-and-connection.md), ghost
components to [ghost-authoring.md](ghost-authoring.md) and
[ghost-spawning-and-groups.md](ghost-spawning-and-groups.md), RPC/command
types to [rpcs-and-commands.md](rpcs-and-commands.md), user-settable
singletons to the file matching their subject.

## Connection

| Type | Role |
|---|---|
| `NetworkStreamConnection` | Transport handle on the connection entity |
| `NetworkSnapshotAck` | Tracks what this connection has received |
| `CommandTarget` | Entity a connection's commands read/write |
| `LocalConnection` | Tags whether a connection is the local client/host |
| `IncomingRpcDataStreamBuffer` / `OutgoingRpcDataStreamBuffer` | RPC wire buffers, processed by `RpcSystem` |
| `IncomingCommandDataStreamBuffer` / `OutgoingCommandDataStreamBuffer` | Command-stream wire buffers |
| `IncomingSnapshotDataStreamBuffer` | Received snapshot buffer, processed by `GhostReceiveSystem` |
| `NetworkId` | Uniquely identifies a connection |
| `NetworkStreamInGame` | Marks a connection ready for snapshots/commands (manual add) |
| `NetworkStreamRequestDisconnect` | Requests connection close |
| `NetworkStreamSnapshotTargetSize` | Per-connection snapshot byte cap |
| `GhostConnectionPosition` | Feeds distance-based importance |
| `PrespawnSectionAck` | Server's record of which subscenes a client has loaded |
| `EnablePacketLogging` | Enables packet dumps for one connection |

## Ghost

| Type | Role |
|---|---|
| `GhostInstance` | Marks an entity as a ghost |
| `GhostType` / `SharedGhostTypeComponent` | Ghost's prefab type; shared-component form keeps types in separate chunks |
| `SnapshotData` / `SnapshotDataBuffer` / `SnapshotDynamicDataBuffer` | Received-snapshot metadata and raw data |
| `PredictedGhost` | Marks a client-predicted ghost (all ghosts, on the server) |
| `GhostDistancePartitionShared` | Added when distance-based importance is active |
| `GhostChildEntity` / `GhostGroup` | Ghost-group membership / root — see [ghost-spawning-and-groups.md](ghost-spawning-and-groups.md) |
| `PredictedGhostSpawnRequest` | Marks an entity as a predicted (not-yet-confirmed) spawn |
| `GhostOwner` / `GhostOwnerIsLocal` | Owning connection / whether that owner is the local client |
| `AutoCommandTarget` | Auto-routes commands to the owned ghost |
| `SubSceneGhostComponentHash` / `PreSpawnedGhostIndex` | Pre-spawned ghost identity within a subscene |
| `PreSerializedGhost` | Enables preserialization — see [optimization-and-bandwidth.md](optimization-and-bandwidth.md) |
| `SwitchPredictionSmoothing` | Transient, added during a prediction-mode switch |
| `PrefabDebugName` | Debug-only prefab name |

## RPC and Command

| Type | Role |
|---|---|
| `IRpcCommand` | Interface for a specific RPC |
| `SendRpcCommandRequest` / `ReceiveRpcCommandRequest` | Send-side / receive-side RPC marker components |
| `ICommandData` / `CommandDataInterpolationDelay` | Base command interface / optional interpolation-delay accessor |

## Netcode-created singletons (read, don't author)

| Type | Role |
|---|---|
| `GhostCollection` / `GhostCollectionPrefab` / `GhostCollectionPrefabSerializer` | Registered ghost prefabs and their serializers |
| `GhostSpawnQueueComponent` / `GhostSpawnBuffer` | Pending predicted-spawn queue — see [ghost-spawning-and-groups.md](ghost-spawning-and-groups.md) |
| `NetworkProtocolVersion` | Exchanged protocol/RPC/ghost hash — see [transport-and-connection.md](transport-and-connection.md) |
| `NetworkTime` | Current tick/interpolation state — see [time-and-interpolation.md](time-and-interpolation.md) |
| `NetDebug` | Log-level singleton — see [testing-and-debugging.md](testing-and-debugging.md) |
| `NetworkStreamDriver` | Holds the `NetworkDriverStore` reference |
| `GhostPredictionSmoothing` / `GhostPredictionHistoryState` | Smoothing-action registry / internal predicted-state history — see [prediction-caveats.md](prediction-caveats.md) |
| `GhostStats` family | Network Debugger connection/prediction/snapshot stats |
| `GhostSendSystemData` | Tunable settings for `GhostSendSystem` — see [optimization-and-bandwidth.md](optimization-and-bandwidth.md) |
| `SpawnedGhostEntityMap` | Last predicted full-tick state of every predicted ghost |

## User-created singletons (settings you author)

| Type | Role | Detail file |
|---|---|---|
| `ClientServerTickRate` | Server tick-rate settings | [setup-and-worlds.md](setup-and-worlds.md) |
| `ClientTickRate` | Client-only tick-rate settings | [time-and-interpolation.md](time-and-interpolation.md) |
| `LagCompensationConfig` | Config for `PhysicsWorldHistory` | [prediction-caveats.md](prediction-caveats.md) |
| `GameProtocolVersion` | Game-specific protocol version, layered on `NetworkProtocolVersion` | [transport-and-connection.md](transport-and-connection.md) |
| `GhostImportance` / `GhostDistanceData` | Importance-scaling configuration | [optimization-and-bandwidth.md](optimization-and-bandwidth.md) |
| `PredictedPhysicsNonGhostWorld` | Declares which physics world a predicted group uses | [physics-integration.md](physics-integration.md) |
| `NetCodeDebugConfig` | Log level / packet dump config | [testing-and-debugging.md](testing-and-debugging.md) |
| `DisableAutomaticPrespawnSectionReporting` | Disables automatic subscene-loaded tracking | [ghost-spawning-and-groups.md](ghost-spawning-and-groups.md) |

## Project Settings (Edit → Project Settings → Multiplayer)

| Setting | Effect |
|---|---|
| Netcode Client Target | `ClientAndServer` (players can host) vs. `ClientOnly` (`CreateServerWorld` throws `NotSupportedException`) |
| Build Type | Drives `UNITY_CLIENT`/`UNITY_SERVER` defines — table in [setup-and-worlds.md](setup-and-worlds.md) |
| Excluded Baking System Assemblies | Assembly definitions excluded from baking, settable per client/server |
| Additional Scripting Defines | Extra defines to exclude client- or server-only code from compilation |
| `NetCodeConfig` asset | No-code editing of `ClientServerTickRate`/`ClientTickRate`/`GhostSendSystemData`/transport `NetworkConfigParameter` |
