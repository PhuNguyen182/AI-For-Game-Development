# Transport and Connection

Pages (6.6): `network-connection`, multi-driver architecture, Relay with NfE, network protocol checks. The UTP driver API itself is `unity-transport`'s.

## Drivers
`NetworkDriverStore` holds up to 3 `NetworkDriver`s per World. `NetworkStreamReceiveSystem` builds them at World creation from `NetworkStreamReceiveSystem.DriverConstructor` (`INetworkStreamDriverConstructor`); set it before World creation to customize.

| Interface | Use |
|---|---|
| `IPCNetworkInterface` | Client and server in one process (self-host, Editor Client&Server) |
| `UDPNetworkInterface` | External connections, non-web platforms |
| `WebSocketNetworkInterface` | External connections on WebGL |

- `DefaultDriverBuilder`: `RegisterClientUdpDriver`, `RegisterClientWebSocketDriver`, `RegisterServerUdpDriver`, `RegisterServerWebSocketDriver`, `RegisterServerIpcDriver`.
- `NetworkStreamDriver.ResetDriverStore(...)` reconfigures an existing World, only while no live `NetworkStreamConnection` exists.

## Relay
- The default setup is not Relay-aware. Either implement `INetworkStreamDriverConstructor` before World creation or call `ResetDriverStore` after it, both with `settings.WithRelayParameters(ref relayServerData)`.
- Server pattern: IPC driver first (local client-hosted play), then a Relay driver on the same port. Client falls back to IPC only when Relay data is invalid and the topology is `ClientAndServer`.

## Protocol check
- `NetworkProtocolVersion` (RPC hash + ghost-component hash + netcode version) is exchanged at connect. Mismatch: both peers self-disconnect with `NetworkStreamDisconnectReason.BadProtocolVersion`. `GameProtocolVersion` layers a game version on top.
- `RpcCollection.DynamicAssemblyList = true` disables the strict check, but an unknown hash then errors mid-game, and every RPC grows by 6 bytes. Set it in `InitializationSystemGroup`, after `RpcSystem.OnCreate` and before `RpcSystem.OnUpdate`, with an identical `[WorldSystemFilter]` on client and server; an asymmetric setting reintroduces the mismatch.

## Connection state
`Connecting` → `Handshake` → `Approval` (if enabled) → `Connected` → `Disconnected`.

| Component | Role |
|---|---|
| `NetworkStreamConnection` | Transport handle |
| `NetworkStreamInGame` | Ready for snapshots and commands; add manually, else no commands or snapshots and no error |
| `NetworkStreamRequestDisconnect` | Requests disconnect |
| `CommandTarget` | Entity the connection's commands read/write |
| `NetworkId` | Assigned after handshake (and approval) |

- Connection events last one `SimulationSystemGroup` tick: read `ConnectionEventsForTick` inside that group.

## Approval
- `NetworkStreamDriver.RequireConnectionApproval = true` on both sides. Client sends `IApprovalRpcCommand`; server adds `ConnectionApproved`.
- `NetworkId` is withheld until approved; a denied connection is disconnected. Timeout is `HandshakeApprovalTimeoutMS` (default 5000).
