# Core Driver Lifecycle — NetworkDriver, Connections, Endpoints, Settings

Source: [Install Unity Transport](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/install.html), [Package samples](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/samples-usage.html), [Simple client and server](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/client-server-simple.html), [NetworkDriver](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkDriver.html), [NetworkConnection](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkConnection.html), [NetworkConnection.State](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkConnection.State.html), [NetworkEndpoint](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkEndpoint.html), [NetworkEndpoint.TransferrableData](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkEndpoint.TransferrableData.html), [NetworkEvent](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkEvent.html), [NetworkEvent.Type](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkEvent.Type.html), [NetworkFamily](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkFamily.html), [NetworkSettings](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkSettings.html), [NetworkConfigParameter](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkConfigParameter.html), [NetworkParameterConstants](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkParameterConstants.html), [CommonNetworkParametersExtensions](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.CommonNetworkParametersExtensions.html), [INetworkInterface](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.INetworkInterface.html), [INetworkParameter](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.INetworkParameter.html), [IPCNetworkInterface](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.IPCNetworkInterface.html), [UDPNetworkInterface](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.UDPNetworkInterface.html), [InboundRecvBuffer](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.InboundRecvBuffer.html), [InboundSendBuffer](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.InboundSendBuffer.html), [ManagedNetworkInterfaceExtensions](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.ManagedNetworkInterfaceExtensions.html), [NetworkInterfaceUnmanagedWrapper\<T\>](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkInterfaceUnmanagedWrapper-1.html), [OperationResult](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.OperationResult.html).
Covers: SKILL.md §4 — **"Decide whether this is a standalone NetworkDriver integration or the NGO UnityTransport component before writing any code"**, **"Create and Bind/Listen the NetworkDriver, then drive it every frame via ScheduleUpdate/Complete/PopEvent without skipping a frame"**.

This file is the entry point for the **standalone (non-NGO) integration path**: creating a `NetworkDriver` by hand, opening connections, and running the per-frame update loop. The NGO integration path — implementing `Unity.Netcode.NetworkTransport` so a custom transport plugs into Netcode for GameObjects — lives in [webgl-and-ngo-integration.md](webgl-and-ngo-integration.md). `NetworkPipeline` stages, reliability, and packet-loss/latency simulation live in [pipelines-reliability-simulation.md](pipelines-reliability-simulation.md). Moving this same driver update onto `NetworkDriver.Concurrent`/`MultiNetworkDriver` inside Burst jobs lives in [jobs-and-concurrent-api.md](jobs-and-concurrent-api.md). Nothing here covers TLS, Relay, or connection diagnostics — those are `security-and-encryption.md`, `relay-and-cross-play.md`, and `diagnostics-and-testing.md` respectively.

## Contents
- [Installing the package and using the samples](#installing-the-package-and-using-the-samples)
- [Creating the NetworkDriver](#creating-the-networkdriver)
- [NetworkSettings and NetworkConfigParameter](#networksettings-and-networkconfigparameter)
- [NetworkEndpoint](#networkendpoint)
- [Bind, Listen, Connect, Accept, Disconnect](#bind-listen-connect-accept-disconnect)
- [NetworkConnection and connection state](#networkconnection-and-connection-state)
- [The per-frame update loop](#the-per-frame-update-loop)
- [NetworkEvent and NetworkEvent.Type](#networkevent-and-networkeventtype)
- [Network interfaces](#network-interfaces)
- [Buffer and wrapper plumbing](#buffer-and-wrapper-plumbing)
- [API index](#api-index)

## Installing the package and using the samples

| Subject | What it decides | Source |
|---|---|---|
| Minimum Unity version | `com.unity.transport@6.6` requires Unity Editor 2022.3 or later — confirm before assuming any syntax in this skill compiles on an older project. | [Install](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/install.html) |
| Install path | Package Manager → Add → "Add package by name" → `com.unity.transport`. | [Install](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/install.html) |
| `SimpleClientServer` sample | Importable from the package's Samples tab; it is the exact code this file's [update loop](#the-per-frame-update-loop) section distills — pull it in directly instead of retyping the walkthrough by hand. | [Package samples](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/samples-usage.html) |
| `JobifiedClientServer` sample | Same walkthrough moved onto `NetworkDriver.Concurrent`/Burst — owned by `jobs-and-concurrent-api.md`, not this file. | [Package samples](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/samples-usage.html) |
| `Ping` / `RelayPing` samples | Burst-jobified ping/pong, and a Relay-integrated variant — owned by `jobs-and-concurrent-api.md` and `relay-and-cross-play.md`. | [Package samples](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/samples-usage.html) |

## Creating the NetworkDriver

| Overload | What it decides | Source |
|---|---|---|
| `NetworkDriver.Create()` | Default `UDPNetworkInterface` and default `NetworkSettings` — the common case for a standalone client or server. | [NetworkDriver](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkDriver.html) |
| `NetworkDriver.Create(NetworkSettings)` | Custom timeouts/queue sizes with the default interface — build the `NetworkSettings` first (below), then pass it here. | [NetworkDriver](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkDriver.html) |
| `NetworkDriver.Create<N>(N)` / `Create<N>(ref N)` | Swap the transport medium itself — `IPCNetworkInterface` for in-process testing, or a custom `INetworkInterface`. | [NetworkDriver](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkDriver.html) |
| `NetworkDriver.Create<N>(N, NetworkSettings)` / `Create<N>(ref N, NetworkSettings)` | Custom interface and custom settings together. | [NetworkDriver](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkDriver.html) |
| `driver.IsCreated` | Guards every shutdown path — check before `Dispose()` so a driver that failed to initialize (or was already disposed) is never disposed twice. | [NetworkDriver](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkDriver.html) |

**Critical caveat**: a plain `NetworkDriver` value (not obtained via `ToConcurrent()`) is **not** thread-safe. Calling it from anywhere other than the main thread — including a hand-rolled `Task`/`Thread` — is a correctness bug, not just a style issue; the thread-safe path is `NetworkDriver.Concurrent` inside a Burst job, covered in `jobs-and-concurrent-api.md`.

## NetworkSettings and NetworkConfigParameter

`NetworkSettings` is a struct of typed parameter blocks; build one, call its extension methods to fill in the blocks you need, then pass it to `NetworkDriver.Create`.

| Member | What it decides | Source |
|---|---|---|
| `NetworkSettings(Allocator)` | Allocator for the settings' internal storage; defaults to `Allocator.Temp` if omitted — use `Allocator.Persistent` if the settings object outlives the current frame. | [NetworkSettings](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkSettings.html) |
| `AddRawParameterStruct<T>(ref T)` | Stores a custom `INetworkParameter` block; only one instance per `T` is kept, and it throws `ArgumentException` (with collection checks on) if `T.Validate()` fails. | [NetworkSettings](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkSettings.html) |
| `TryGet<T>(out T)` / `AsReadOnly()` | Read back a stored parameter block, or get a read-only view to pass into a job. | [NetworkSettings](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkSettings.html) |
| `Dispose()` | Must be called once the settings object is no longer needed — it owns native memory the same way `NetworkDriver` does. | [NetworkSettings](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkSettings.html) |
| `WithNetworkConfigParameters(...)` / `GetNetworkConfigParameters()` | Fluent setter/getter for the `NetworkConfigParameter` block below — chain it onto the `NetworkSettings` before creating the driver. | [CommonNetworkParametersExtensions](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.CommonNetworkParametersExtensions.html) |
| Relay / TLS / WebSocket / simulator extensions | `WithRelayParameters`, `WithSecureClientParameters`/`WithSecureServerParameters`, `WithWebSocketParameters`, `WithNetworkSimulatorParameters` also live on `NetworkSettings` but are owned by `relay-and-cross-play.md`, `security-and-encryption.md`, `webgl-and-ngo-integration.md`, and `pipelines-reliability-simulation.md` respectively — not detailed here. | [NetworkSettings](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkSettings.html) |

`NetworkConfigParameter` fields, with the default `CommonNetworkParametersExtensions.WithNetworkConfigParameters()` assigns when a value isn't specified:

| Field | Default | Meaning | Source |
|---|---|---|---|
| `connectTimeoutMS` | 1000 (`NetworkParameterConstants.ConnectTimeoutMS`) | Time between connection attempts. | [NetworkConfigParameter](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkConfigParameter.html) |
| `maxConnectAttempts` | 60 | Attempts before a `Disconnect` event fires for a connection that never established. | [NetworkConfigParameter](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkConfigParameter.html) |
| `disconnectTimeoutMS` | 30000 | Inactivity period after which a live connection is dropped; `0` disables the timeout entirely. | [NetworkConfigParameter](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkConfigParameter.html) |
| `heartbeatTimeoutMS` | 500 | Idle time before a heartbeat keep-alive is sent to the peer; `0` disables heartbeats. | [NetworkConfigParameter](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkConfigParameter.html) |
| `reconnectionTimeoutMS` | 2000 | Window to silently re-establish a connection after peer contact is lost (e.g. client IP roaming under DTLS). | [NetworkConfigParameter](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkConfigParameter.html) |
| `maxFrameTimeMS` / `fixedFrameTimeMS` | 0 / 0 | Caps per-frame timeout advancement for debugging, or replaces real elapsed time with a fixed value for deterministic tests. | [NetworkConfigParameter](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkConfigParameter.html) |
| `receiveQueueCapacity` / `sendQueueCapacity` | 512 / 512 | Queue capacity in packets, shared across connections — size for the actual max packets per update, not per connection. | [NetworkConfigParameter](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkConfigParameter.html) |
| `maxMessageSize` | 1400 (`NetworkParameterConstants.MTU`) | Largest packet the transport will send, including transport headers but excluding the OS network stack's own headers. | [NetworkConfigParameter](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkConfigParameter.html) |
| `performPathMtuDiscovery` | `false` | Enables MTU discovery during the handshake to fit messages to the actual path. | [NetworkConfigParameter](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkConfigParameter.html) |

## NetworkEndpoint

| Member | What it decides | Source |
|---|---|---|
| `NetworkEndpoint.AnyIpv4` / `AnyIpv6` | Wildcard bind address (`0.0.0.0` / `::`) — what a server binds to. | [NetworkEndpoint](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkEndpoint.html) |
| `NetworkEndpoint.LoopbackIpv4` / `LoopbackIpv6` | Loopback address (`127.0.0.1` / `::1`) — same-machine testing and the only address `IPCNetworkInterface` accepts. | [NetworkEndpoint](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkEndpoint.html) |
| `.WithPort(ushort)` | Returns a copy of an existing endpoint with a different port — the usual way to turn `AnyIpv4` into a bindable address. | [NetworkEndpoint](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkEndpoint.html) |
| `NetworkEndpoint.Parse(...)` | Throws/asserts on a malformed address — use only for trusted, hardcoded input. | [NetworkEndpoint](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkEndpoint.html) |
| `NetworkEndpoint.TryParse(..., out NetworkEndpoint)` | Fails safely instead of throwing — the correct choice for a user-typed IP/port. | [NetworkEndpoint](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkEndpoint.html) |
| `.IsValid` / `.IsLoopback` / `.IsAny` | Query an endpoint's shape without branching on `.Family` by hand. | [NetworkEndpoint](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkEndpoint.html) |
| `NetworkEndpoint.TransferrableData` | Opaque container for the raw address bytes, with no public members — pass it across a job/thread boundary instead of the `NetworkEndpoint` itself where the API asks for it. | [NetworkEndpoint.TransferrableData](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkEndpoint.TransferrableData.html) |

**Critical caveat**: UTP does not resolve domain names. `NetworkEndpoint.Parse`/`TryParse` accept only literal IP addresses — resolve a hostname to an IP through some other API before building the endpoint.

## Bind, Listen, Connect, Accept, Disconnect

| Method | What it decides | Source |
|---|---|---|
| `driver.Bind(NetworkEndpoint)` | Returns `0` on success, non-zero on failure — check the return value; a failed bind is silent otherwise. | [NetworkDriver](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkDriver.html) |
| `driver.Listen()` | Puts the driver in the `Listening` state so it can `Accept()` — only meaningful after a successful `Bind`. | [NetworkDriver](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkDriver.html) |
| `driver.Accept()` / `Accept(out NativeArray<byte>)` | Pulls one pending inbound connection per call — loop it (`while ((c = driver.Accept()) != default)`) to drain every connection queued since the last update. | [NetworkDriver](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkDriver.html) |
| `driver.Connect(NetworkEndpoint)` | Client-side connect; implicitly binds the driver first if it wasn't already bound. | [NetworkDriver](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkDriver.html) |
| `driver.Connect(FixedString512Bytes, ushort)` | String-address overload — same implicit-bind behavior. | [NetworkDriver](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkDriver.html) |
| `driver.Disconnect(NetworkConnection)` | Closes a connection locally; the peer only learns of it once a `ScheduleUpdate` actually ships the disconnect notification. | [NetworkDriver](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkDriver.html) |
| `driver.SetAcceptPayload(NativeArray<byte>)` | Server-side accept payload sent immediately when the connection request arrives, not when `Accept()` is later called — set it before that timing matters. | [NetworkDriver](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkDriver.html) |
| `driver.RegisterPipelineStage<T>(T)` | Must be called before the first `Bind()` — registering a custom pipeline stage after connections exist is unsupported. | [NetworkDriver](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkDriver.html) |
| `driver.BeginSend(...)` / `EndSend(DataStreamWriter)` / `AbortSend(DataStreamWriter)` | Two-phase send: `BeginSend` gets a writer, `EndSend` enqueues it (data doesn't hit the wire until the next `ScheduleFlushSend`/`ScheduleUpdate`), `AbortSend` cancels a write in progress. | [NetworkDriver](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkDriver.html) |

**Critical caveat**: `Listen()` only puts the driver in the `Listening` state if the preceding `Bind()` actually succeeded — always gate `Listen()` on `Bind()`'s return value, per the pattern in [Simple client and server](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/client-server-simple.html): `if (m_Driver.Bind(endpoint) != 0) return; m_Driver.Listen();`.

## NetworkConnection and connection state

| Member | What it decides | Source |
|---|---|---|
| `connection.IsCreated` | `true` only if the handle came from `Accept()` or `Connect()` — check it before using a connection stored across frames, since a disconnected slot is typically reset to `default`. | [NetworkConnection](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkConnection.html) |
| `connection.GetState(NetworkDriver)` | Query the connection's current lifecycle state on demand, versus reacting only to events. | [NetworkConnection](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkConnection.html) |
| `connection.Close(NetworkDriver)` / `Disconnect(NetworkDriver)` | Documented as identical — both close an active connection; either returns `0` on success. | [NetworkConnection](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkConnection.html) |
| `connection.PopEvent(NetworkDriver, out DataStreamReader)` | Single-connection event pump — used by a client with exactly one `NetworkConnection` instead of the driver-wide `PopEventForConnection`. | [NetworkConnection](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkConnection.html) |
| `driver.GetConnectionState(NetworkConnection)` | Same query, called on the driver instead of the connection — equivalent to `connection.GetState(driver)`. | [NetworkDriver](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkDriver.html) |

`NetworkConnection.State` values:

| Value | Meaning | Source |
|---|---|---|
| `Connecting` | Handshake in progress; sending data is not allowed yet. The next event is `Connect` (success) or `Disconnect` (failure). | [NetworkConnection.State](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkConnection.State.html) |
| `Connected` | Open; safe to send and receive. | [NetworkConnection.State](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkConnection.State.html) |
| `Disconnected` | Closed; no further events will ever arrive for this connection. | [NetworkConnection.State](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkConnection.State.html) |

## The per-frame update loop

Every driver — server or client — is driven the same way each frame: schedule the update job, complete it synchronously, then drain events before doing anything else. Skipping a frame's `ScheduleUpdate`/`Complete` call leaves incoming events queued and can cause a state transition (timeout, disconnect) to be missed entirely, per `coding-principles.md`'s Correctness boundaries section on cleaning up state at defined lifecycle boundaries.

```csharp
public class EchoServer : MonoBehaviour
{
    private NetworkDriver driver;
    private NativeList<NetworkConnection> connections;

    private void Start()
    {
        this.driver = NetworkDriver.Create();
        this.connections = new NativeList<NetworkConnection>(16, Allocator.Persistent);

        NetworkEndpoint endpoint = NetworkEndpoint.AnyIpv4.WithPort(7777);
        if (this.driver.Bind(endpoint) != 0)
        {
            return;
        }

        this.driver.Listen();
    }

    private void Update()
    {
        this.driver.ScheduleUpdate().Complete();

        for (int i = 0; i < this.connections.Length; i++)
        {
            if (!this.connections[i].IsCreated)
            {
                this.connections.RemoveAtSwapBack(i);
                i--;
            }
        }

        NetworkConnection incoming;
        while ((incoming = this.driver.Accept()) != default)
        {
            this.connections.Add(incoming);
        }

        for (int i = 0; i < this.connections.Length; i++)
        {
            DataStreamReader stream;
            NetworkEvent.Type cmd;
            while ((cmd = this.driver.PopEventForConnection(this.connections[i], out stream)) != NetworkEvent.Type.Empty)
            {
                if (cmd == NetworkEvent.Type.Data)
                {
                    uint value = stream.ReadUInt();
                    this.driver.BeginSend(NetworkPipeline.Null, this.connections[i], out DataStreamWriter writer);
                    writer.WriteUInt(value);
                    this.driver.EndSend(writer);
                }
                else if (cmd == NetworkEvent.Type.Disconnect)
                {
                    this.connections[i] = default;
                    break;
                }
            }
        }
    }

    private void OnDestroy()
    {
        if (this.driver.IsCreated)
        {
            this.driver.Dispose();
            this.connections.Dispose();
        }
    }
}
```

**Critical caveat**: `NetworkDriver.Dispose()` and every `NativeList`/`NativeArray` the driver's owner allocated (the connections list above) must be disposed on shutdown — guard the call with `driver.IsCreated` so a driver that failed to initialize, or was already disposed, is never disposed twice. On the client side, replace `Accept`/`PopEventForConnection` with a single stored `NetworkConnection` and `connection.PopEvent(driver, out stream)`, per [Simple client and server](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/client-server-simple.html).

## NetworkEvent and NetworkEvent.Type

`NetworkEvent` itself is documented as internal-use-only; the type applications actually branch on is the nested `NetworkEvent.Type` enum returned by `PopEvent`/`PopEventForConnection`.

| Value | Meaning | Source |
|---|---|---|
| `Empty` | No more events pending — the loop-termination condition for every `PopEvent` `while` loop. | [NetworkEvent.Type](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkEvent.Type.html) |
| `Connect` | Handshake succeeded; sending is now allowed. Servers observe new connections through `Accept()` instead of this event. | [NetworkEvent.Type](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkEvent.Type.html) |
| `Data` | A message arrived; read it from the `DataStreamReader` the pop call returned. | [NetworkEvent.Type](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkEvent.Type.html) |
| `Disconnect` | Connection closed or failed to establish; the `DataStreamReader` holds one byte mapping to a `DisconnectReason` (see `diagnostics-and-testing.md`). | [NetworkEvent.Type](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkEvent.Type.html) |

## Network interfaces

| Type | What it decides | Source |
|---|---|---|
| `INetworkInterface` | Contract a custom transport medium implements: `LocalEndpoint`, `Bind`, `Listen`, `Initialize`, `ScheduleReceive`, `ScheduleSend`, plus `IDisposable`. Pass an instance to `NetworkDriver.Create<N>`. | [INetworkInterface](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.INetworkInterface.html) |
| `UDPNetworkInterface` | The default interface on every standalone platform. **Not available on WebGL** — WebGL needs `WebSocketNetworkInterface`, covered in `webgl-and-ngo-integration.md`. | [UDPNetworkInterface](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.UDPNetworkInterface.html) |
| `IPCNetworkInterface` | In-memory, same-process transport for tests and single-player-as-local-host modes; sends are instantaneous but confined to drivers in the same process. | [IPCNetworkInterface](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.IPCNetworkInterface.html) |
| `NetworkFamily.Invalid` / `Ipv4` / `Ipv6` / `Custom` | `Custom` is what a hand-rolled `INetworkInterface` uses when its `NetworkEndpoint` is neither IPv4 nor IPv6. | [NetworkFamily](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkFamily.html) |

**Critical caveat**: `IPCNetworkInterface` only accepts loopback addresses (`NetworkEndpoint.LoopbackIpv4`) for `Bind`/`Connect` — give each driver sharing the process a distinct port, since the addresses themselves cannot distinguish them.

## Buffer and wrapper plumbing

Custom `INetworkInterface`/`INetworkPipelineStage` implementations exchange data through these low-level buffer and parameter types.

| Type | What it decides | Source |
|---|---|---|
| `InboundRecvBuffer` | Buffer passed into a pipeline stage's `Receive` — a raw `byte*` plus `bufferLength`, with a `Slice(int)` helper for sub-ranges. | [InboundRecvBuffer](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.InboundRecvBuffer.html) |
| `InboundSendBuffer` | Buffer passed into a pipeline stage's `Send` — exposes both the payload alone (`buffer`/`bufferLength`) and the payload with prior stages' headers (`bufferWithHeaders`/`bufferWithHeadersLength`/`headerPadding`). | [InboundSendBuffer](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.InboundSendBuffer.html) |
| `INetworkParameter` | Contract for a custom settings block: implement `Validate()`, which `NetworkSettings.AddRawParameterStruct<T>` calls automatically when the block is added. | [INetworkParameter](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.INetworkParameter.html) |
| `OperationResult` | Struct (not an enum) carrying an `ErrorCode` — `0` is success, anything else is an error surfaced through `NetworkDriver.ReceiveErrorCode`. | [OperationResult](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.OperationResult.html) |
| `ManagedNetworkInterfaceExtensions.WrapToUnmanaged<T>()` | **`[Obsolete]`** — do not call it in new code. Managed `INetworkInterface` implementations now pass directly to `NetworkDriver.Create<N>`. | [ManagedNetworkInterfaceExtensions](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.ManagedNetworkInterfaceExtensions.html) |
| `NetworkInterfaceUnmanagedWrapper<T>` | **`[Obsolete]`** — the wrapper `WrapToUnmanaged<T>()` used to produce; superseded the same way. | [NetworkInterfaceUnmanagedWrapper\<T\>](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkInterfaceUnmanagedWrapper-1.html) |

**Critical caveat**: both `ManagedNetworkInterfaceExtensions.WrapToUnmanaged<T>()` and `NetworkInterfaceUnmanagedWrapper<T>` are marked `[Obsolete]` on this page. Per `coding-principles.md`'s Obsolete APIs section, never declare or consume either in new code — pass a managed `INetworkInterface` straight to `NetworkDriver.Create<N>(N)` instead.

## API index

| Type | Source |
|---|---|
| `NetworkDriver` | [NetworkDriver](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkDriver.html) |
| `NetworkConnection` | [NetworkConnection](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkConnection.html) |
| `NetworkConnection.State` | [NetworkConnection.State](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkConnection.State.html) |
| `NetworkEndpoint` | [NetworkEndpoint](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkEndpoint.html) |
| `NetworkEndpoint.TransferrableData` | [NetworkEndpoint.TransferrableData](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkEndpoint.TransferrableData.html) |
| `NetworkEvent` | [NetworkEvent](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkEvent.html) |
| `NetworkEvent.Type` | [NetworkEvent.Type](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkEvent.Type.html) |
| `NetworkFamily` | [NetworkFamily](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkFamily.html) |
| `NetworkSettings` | [NetworkSettings](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkSettings.html) |
| `NetworkConfigParameter` | [NetworkConfigParameter](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkConfigParameter.html) |
| `NetworkParameterConstants` | [NetworkParameterConstants](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkParameterConstants.html) |
| `CommonNetworkParametersExtensions` | [CommonNetworkParametersExtensions](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.CommonNetworkParametersExtensions.html) |
| `INetworkInterface` | [INetworkInterface](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.INetworkInterface.html) |
| `INetworkParameter` | [INetworkParameter](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.INetworkParameter.html) |
| `IPCNetworkInterface` | [IPCNetworkInterface](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.IPCNetworkInterface.html) |
| `UDPNetworkInterface` | [UDPNetworkInterface](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.UDPNetworkInterface.html) |
| `InboundRecvBuffer` | [InboundRecvBuffer](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.InboundRecvBuffer.html) |
| `InboundSendBuffer` | [InboundSendBuffer](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.InboundSendBuffer.html) |
| `ManagedNetworkInterfaceExtensions` | [ManagedNetworkInterfaceExtensions](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.ManagedNetworkInterfaceExtensions.html) |
| `NetworkInterfaceUnmanagedWrapper<T>` | [NetworkInterfaceUnmanagedWrapper\<T\>](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkInterfaceUnmanagedWrapper-1.html) |
| `OperationResult` | [OperationResult](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.OperationResult.html) |
