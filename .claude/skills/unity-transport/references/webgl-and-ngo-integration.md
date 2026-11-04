# WebGL and NGO integration

Sources (`@6.6`): manual `websockets`, `ngo-transports`, `migration`; API `WebSocketNetworkInterface`, `WebSocketParameter`, `Unity.Netcode.NetworkTransport`, `Unity.Netcode.NetworkEvent`, `Unity.Netcode.NetworkDelivery`, `Unity.Netcode.NetworkManager`, `NetcodeInterop.NetworkTransportInterface`.

The NGO types here live in the `Unity.Netcode` namespace inside this package (upstream's placement). NGO's own `NetworkManager`, `NetworkVariable` and spawning are `netcode-for-gameobjects`.

## WebGL

- Browsers expose no UDP sockets, so the default UDP interface cannot be used in a WebGL build. Use `WebSocketNetworkInterface`, Relay, or `IPCNetworkInterface` for same-build hosting.
- UTP supports WebSockets only for WebGL compatibility, not as a general WebSocket library.
- Browsers cannot create listening sockets, so a WebGL build usually cannot `Listen()`. The exceptions are `IPCNetworkInterface` and hosting via Relay.
- A client connects only to a server of the same socket type: a WebSocket client cannot reach a UDP server, or the reverse.
- `NetworkDriver.Create(new WebSocketNetworkInterface(), settings)` is a drop-in for the UDP interface. `LocalEndpoint` is valid only after `Bind()`.
- `settings.WithWebSocketParameters(path: "/some/path")` sets the URL path (not a full URL), default `"/"`. `GetWebSocketParameters` reads it back.
- An HTTPS-served page must connect over WSS, because browsers require every connection from a secure page to be secure.
  - The server needs a CA-signed certificate (e.g. Let's Encrypt); browsers reject self-signed. Set it with `WithSecureServerParameters(certificate, privateKey)`.
  - Clients need only `WithSecureClientParameters(serverName: "your-domain.com")`, no CA certificate.

## INetworkInterface or NetworkTransport

| | `INetworkInterface` | `Unity.Netcode.NetworkTransport` |
|---|---|---|
| Threading | UTP's Job System, off main thread | Main thread |
| Shape | Packet-based | Connection-oriented (client IDs, connect/disconnect/poll events) |
| Types | Burst-compatible, unmanaged | Managed (`MonoBehaviour`) |
| Pick when | Socket-like transport scaling past ~10 concurrent players | Complex connection mechanism (handshake, approval), modest player counts |

Since Unity 6.6 a `NetworkTransport` can be wrapped via `NetworkTransportInterface` and driven directly by `NetworkDriver`.

## NetworkTransport contract

`public abstract class NetworkTransport : MonoBehaviour`, a stripped-down copy of NGO's. Implement the contract and no more; do not reimplement transport lifecycle in Client code.

| Member | Contract |
|---|---|
| `ulong ServerClientId { get; }` | A client's server ID; unused on a server |
| `void Initialize(NetworkManager networkManager = null)` | Unity Transport always passes `null` |
| `bool StartServer()` / `bool StartClient()` | Start listening / connect; true on success |
| `void Shutdown()` | Shut down |
| `void Send(ulong clientId, ArraySegment<byte> payload, NetworkDelivery d)` | Send; UTP only ever passes `Unreliable` |
| `void DisconnectLocalClient()` / `void DisconnectRemoteClient(ulong clientId)` | Disconnect |
| `NetworkEvent PollEvent(out ulong clientId, out ArraySegment<byte> payload, out float receiveTime)` | Next event; `NetworkEvent.Nothing` when none |
| `ulong GetCurrentRtt(ulong clientId)` | RTT in ms; return 0 if unsupported |

Optional members:
- `virtual bool IsSupported`: override for platform restrictions.
- `protected virtual OnEarlyUpdate()`: before UTP processes received packets; read the socket and accept connections here.
- `protected virtual OnPostLateUpdate()`: after processing; flush sends here if `Send` only enqueues.
- Do not override `EarlyUpdate`/`PostLateUpdate`; override the `On...` versions.
- `OnTransportEvent` (`void TransportEventDelegate(NetworkEvent, ulong clientId, ArraySegment<byte>, float receiveTime)`) is an alternative to polling. Raise it with `InvokeOnTransportEvent`, on the main thread only.

`NetworkEvent` values: `Connect`, `Data`, `Disconnect`, `Nothing` (poll only), `TransportFailure` (unrecoverable).

`NetworkDelivery`: only `Unreliable` is used by Unity Transport. `Reliable`, `ReliableSequenced`, `ReliableFragmentedSequenced`, `UnreliableSequenced` exist for other transports. Do not build reliability or ordering for them under UTP: `NetworkPipeline` owns that (`pipelines-reliability-simulation.md`).

## Wiring a custom transport into a driver

`Unity.Networking.Transport.NetcodeInterop.NetworkTransportInterface(NetworkTransport)` is a struct `INetworkInterface` that forwards to the wrapped transport. There is no Inspector assignment in this flow:

```csharp
var go = new GameObject("NetcodeTransport");
GameObject.DontDestroyOnLoad(go);
var transport = go.AddComponent<MyNetcodeTransport>();
var driver = NetworkDriver.Create(new NetworkTransportInterface(transport));
```

Unresolved upstream conflict: the API page says `NetworkTransportInterface` "must be wrapped with `NetworkInterfaceUnmanagedWrapper`" (it holds a managed reference), but the manual sample passes it straight to `Create`. `NetworkInterfaceUnmanagedWrapper` is also `[Obsolete]`. Confirm which `Create` overload is in play (it may wrap internally) before shipping.

`Unity.Netcode.NetworkManager` here is an empty compatibility stub so `Initialize(NetworkManager)` compiles. A real NGO `NetworkManager` is out of scope.

## Migrating from UTP 1.X

2.0+ (including 6.6) needs Unity 2022.3+; 1.X gets bug fixes only on 2021/2022 LTS. The 2.0 wire protocol is incompatible with 1.X in both directions.

| 1.X | Now |
|---|---|
| `DataStreamReader`/`Writer` | Moved to `Unity.Collections` |
| `WriteBytes(byte*, int)` and other raw-pointer methods | `Unsafe` suffix, in `Unity.Collections.LowLevel.Unsafe` (`WriteBytesUnsafe`) |
| `NetworkInterfaceEndPoint` | `NetworkEndpoint` |
| `CreateInterfaceEndPoint`, `GetGenericEndPoint`, `WithDataStreamParameters`, `WithPipelineParameters` | Removed, no replacement listed |
| `NetworkSendInterface`, `NetworkPacketReceiver` | Removed: `ScheduleSend` takes a `PacketsQueue`, `ScheduleReceive` fills one |
| `INetworkInterface` | Must be Burst-compatible, else `WrapToUnmanaged` (now `[Obsolete]`; see `core-driver-lifecycle.md`); `Initialize` gained a packet-padding parameter |
| `NetworkPipelineStageCollection.RegisterPipelineStage` / `.GetStageId` | `NetworkDriver.RegisterPipelineStage` / static `NetworkPipelineStageId.Get` |
| `SimulatorPipelineStageInSend` | Deprecated: `SimulatorPipelineStage` with `ApplyMode` |
| `WithBaselibNetworkInterfaceParameters` | Deprecated: `WithNetworkConfigParameters` |
| Timeout via `WithSecureClientParameters`/`WithSecureServerParameters` | Removed |
| `Disconnect` | The pending `ScheduleUpdate` job must complete before it takes effect |

Collections 1.2 to 2.X can cause compile errors; an Editor restart usually fixes them.
