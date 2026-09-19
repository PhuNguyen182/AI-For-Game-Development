# Transport and Connection — drivers, Relay, protocol checks, connection lifecycle

Sources: [Netcode for Entities multi-driver architecture](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/networking-network-drivers.html), [Use Unity Relay with Netcode for Entities](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/networking-using-relay.html), [Network protocol checks](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/network-protocol-checks.html), [Connecting server and clients](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/network-connection.html).
Covers: SKILL.md §4 — **"Configure the transport and connection lifecycle explicitly, rather than assuming a connection is ready for gameplay"**.

Which transport a World actually uses, how a connection entity moves through
its states, and how a version mismatch is caught before gameplay code ever
sees bad data. Ghost/RPC/command traffic that flows over an established
connection is [ghost-authoring.md](ghost-authoring.md) and
[rpcs-and-commands.md](rpcs-and-commands.md).

## Drivers

`NetworkDriverStore` holds up to **three** `NetworkDriver`s per World, each on
a different `INetworkInterface`; `NetworkStreamReceiveSystem` configures it
automatically at World creation from `NetworkStreamReceiveSystem.DriverConstructor`
(an `INetworkStreamDriverConstructor`), set before World creation to customize.

| Interface | Use when | Source |
|---|---|---|
| `IPCNetworkInterface` | Client and server share a process (self-hosting, in-Editor Client&Server) | [Multi-driver architecture](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/networking-network-drivers.html) |
| `UDPNetworkInterface` | External connections, non-web standalone platforms | [Multi-driver architecture](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/networking-network-drivers.html) |
| `WebSocketNetworkInterface` | External connections on WebGL | [Multi-driver architecture](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/networking-network-drivers.html) |

`DefaultDriverBuilder` exposes `RegisterClientUdpDriver`/`RegisterClientWebSocketDriver`/
`RegisterServerUdpDriver`/`RegisterServerWebSocketDriver`/`RegisterServerIpcDriver`.
`NetworkStreamDriver.ResetDriverStore(...)` reconfigures drivers on an
already-created World — only valid while **no live `NetworkStreamConnection`
exists** — the mechanism Relay setup below relies on.

## Unity Relay integration

NfE's default driver setup is **not** Relay-aware out of the box — either
implement `INetworkStreamDriverConstructor` (set before World creation) or
call `NetworkStreamDriver.ResetDriverStore` after it, both using
`settings.WithRelayParameters(ref relayServerData)` from a `RelayServerData`
obtained through the Relay service SDK. Recommended pattern: server registers
an IPC driver first (for local client-hosted play) then a second Relay driver
on the same port for external clients; client falls back to IPC only when
Relay data is invalid **and** the topology is `ClientAndServer`. See
[host-migration.md](host-migration.md) for the Lobby+Relay flow this same
mechanism supports across a host change.

## Protocol version checks

| Concept | Effect | Source |
|---|---|---|
| `NetworkProtocolVersion` | Exchanged at connect time — RPC hash + ghost-component hash + netcode version | [Network protocol checks](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/network-protocol-checks.html) |
| Mismatch | Both peers self-disconnect with `NetworkStreamDisconnectReason.BadProtocolVersion` | [Network protocol checks](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/network-protocol-checks.html) |
| `RpcCollection.DynamicAssemblyList = true` | Disables strict upfront hash checking | [Network protocol checks](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/network-protocol-checks.html) |

**Critical caveat**: setting `DynamicAssemblyList = true` trades an upfront,
clean disconnect for a **mid-game runtime error** on an unknown type hash,
and adds 6 bytes to every RPC sent (full hash instead of a `ushort` index).
Must be configured in `InitializationSystemGroup`, after `RpcSystem.OnCreate`
but before `RpcSystem.OnUpdate`, with an identical `[WorldSystemFilter]` on
both client and server — an asymmetric setting reintroduces the mismatch it
was meant to avoid.

## Connection components

| Component | Role | Source |
|---|---|---|
| `NetworkStreamConnection` | The Transport handle on the connection entity | [Connecting server and clients](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/network-connection.html) |
| `NetworkStreamInGame` | Marks a connection ready for snapshots/commands — **must be added manually** | [Connecting server and clients](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/network-connection.html) |
| `NetworkStreamRequestDisconnect` | Requests a disconnect | [Connecting server and clients](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/network-connection.html) |
| `CommandTarget` | The entity a connection's commands read/write | [Connecting server and clients](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/network-connection.html) |
| `NetworkId` | Assigned only after handshake (and approval, if enabled) succeeds | [Connecting server and clients](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/network-connection.html) |

## Connection state machine

`Connecting` → `Handshake` (protocol version exchange) → `Approval`
(only if enabled) → `Connected` → `Disconnected`. Before
`NetworkStreamInGame` is added, the client sends no commands and the server
sends no snapshots — a connection that never gets this tag looks "stuck"
with no error. Connection events are only visible for **one**
`SimulationSystemGroup` tick — read `ConnectionEventsForTick` inside that
group's own systems, not after the fact.

## Connection approval

Enable with `NetworkStreamDriver.RequireConnectionApproval = true` on
**both** client and server. Client sends `IApprovalRpcCommand` RPCs during
Handshake/Approval; server adds a `ConnectionApproved` component to accept.
`NetworkId` is withheld until approval succeeds; a denied connection is
disconnected automatically. Timeout is `ClientServerTickRate.HandshakeApprovalTimeoutMS`
(default 5000 ms, per [setup-and-worlds.md](setup-and-worlds.md)).
