# WebGL & NGO Integration — WebSocketNetworkInterface, NetworkTransport Contract

Source: [Using WebSockets](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/websockets.html), [Using Netcode for GameObjects transports](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/ngo-transports.html), [Migrating from 1.X](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/migration.html), [Unity.Netcode.NetworkDelivery](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Netcode.NetworkDelivery.html), [Unity.Netcode.NetworkEvent](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Netcode.NetworkEvent.html), [Unity.Netcode.NetworkManager](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Netcode.NetworkManager.html), [Unity.Netcode.NetworkTransport](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Netcode.NetworkTransport.html), [Unity.Netcode.NetworkTransport.TransportEventDelegate](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Netcode.NetworkTransport.TransportEventDelegate.html), [Unity.Networking.Transport.WebSocketNetworkInterface](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.WebSocketNetworkInterface.html), [Unity.Networking.Transport.WebSocketParameter](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.WebSocketParameter.html), [Unity.Networking.Transport.WebSocketParameterExtensions](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.WebSocketParameterExtensions.html), [Unity.Networking.Transport.NetcodeInterop.NetworkTransportInterface](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetcodeInterop.NetworkTransportInterface.html).
Covers: SKILL.md §4 — **"Decide whether this is a standalone NetworkDriver integration or the NGO UnityTransport component before writing any code"**, **"Treat the Unity.Netcode NetworkTransport contract as NGO's integration boundary, never reimplement transport lifecycle in Game.Client code"**.

This file owns two decisions: (a) which network interface a WebGL target must use, since WebGL cannot open raw UDP sockets, and (b) the `Unity.Netcode.NetworkTransport` abstract contract any custom transport — including `UnityTransport` itself — implements to plug into Netcode for GameObjects (NGO). It does not cover NGO's own `NetworkVariable`/Rpc/`NetworkObject`/spawning API — that is the separate `netcode-for-gameobjects` skill's territory (it may or may not be present in a given project). The plain standalone driver lifecycle (Bind/Listen/Connect, ScheduleUpdate) lives in [core-driver-lifecycle.md](core-driver-lifecycle.md). Note: this Transport package's own docs bundle these NGO integration types under the `Unity.Netcode` namespace, not `Unity.Networking.Transport` — that placement is upstream's, not a miscategorization in this file.

## Table of contents
- [WebGL: why UDP is out and what replaces it](#webgl-why-udp-is-out-and-what-replaces-it)
- [WebSocketNetworkInterface configuration surface](#websocketnetworkinterface-configuration-surface)
- [TLS/WSS requirements for WebGL WebSocket transports](#tlswss-requirements-for-webgl-websocket-transports)
- [Choosing between INetworkInterface and NetworkTransport](#choosing-between-inetworkinterface-and-networktransport)
- [The Unity.Netcode.NetworkTransport contract](#the-unitynetcodenetworktransport-contract)
- [Minimal custom NetworkTransport skeleton](#minimal-custom-networktransport-skeleton)
- [NetworkTransportInterface — the NGO↔UTP bridge](#networktransportinterface--the-ngoutp-bridge)
- [NetworkManager and transport assignment](#networkmanager-and-transport-assignment)
- [Migrating from UTP 1.X](#migrating-from-utp-1x)
- [API index](#api-index)

## WebGL: why UDP is out and what replaces it

| Subject | What it decides | Source |
|---|---|---|
| Raw UDP on WebGL | Web browsers don't expose direct UDP socket access to page scripts, so the default UDP `NetworkInterface` cannot be used at all in a WebGL build — this is a platform restriction, not a configuration choice. | [Using WebSockets](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/websockets.html) |
| `WebSocketNetworkInterface` scope | UTP supports the WebSocket protocol specifically to enable WebGL compatibility; the docs explicitly warn it is "not intended as a general-purpose WebSocket library" — don't reach for it outside the WebGL-compatibility use case. | [Using WebSockets](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/websockets.html) |
| Server on WebGL | Browsers do not allow creating listening sockets, so a WebGL build usually cannot `Listen()` even with `WebSocketNetworkInterface`. The two exceptions: `IPCNetworkInterface` for an in-memory server within the same WebGL build, and hosting via Unity Relay. | [Using WebSockets](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/websockets.html) |
| Socket type matching | A client can only directly connect to a server using the same underlying socket type — a WebSocket client cannot connect to a plain UDP server, and vice versa. | [Using WebSockets](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/websockets.html) |

**Critical caveat**: WebGL's inability to open raw UDP sockets is a hard browser restriction, not a performance trade-off to weigh — every WebGL target must use `WebSocketNetworkInterface` (or Relay, or `IPCNetworkInterface` for same-build hosting) in place of the default UDP interface, with no middle ground.

## WebSocketNetworkInterface configuration surface

| Member | Kind | What it decides | Source |
|---|---|---|---|
| `WebSocketNetworkInterface` | struct, implements `INetworkInterface` + `IDisposable` | Instantiate explicitly — `NetworkDriver.Create(new WebSocketNetworkInterface())` — instead of the default UDP interface; drops into the same `NetworkDriver.Create` call. | [WebSocketNetworkInterface](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.WebSocketNetworkInterface.html) |
| `LocalEndpoint` | property (`NetworkEndpoint`) | Only valid after `Bind()` has been called. | [WebSocketNetworkInterface](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.WebSocketNetworkInterface.html) |
| `Bind`, `Listen`, `ScheduleReceive`, `ScheduleSend`, `Dispose` | methods | Same `INetworkInterface` surface as the UDP interface — no special-cased driver code needed once the interface is swapped in. | [WebSocketNetworkInterface](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.WebSocketNetworkInterface.html) |
| `WebSocketParameter.Path` | field (`FixedString128Bytes`) | The URL path segment only — for clients, the path to connect to; for servers, the path to accept on (e.g. `"/some/path"`, not a full URL). Defaults to `"/"`. | [WebSocketParameter](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.WebSocketParameter.html) |
| `WebSocketParameter.Validate()` | method (`bool`) | Runs automatically when the parameter is added to `NetworkSettings` — no manual call needed. | [WebSocketParameter](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.WebSocketParameter.html) |
| `settings.WithWebSocketParameters(path)` | extension method | Sets the path before driver creation: `settings.WithWebSocketParameters(path: "/some/path")`. | [WebSocketParameterExtensions](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.WebSocketParameterExtensions.html) |
| `settings.GetWebSocketParameters()` | extension method | Reads back the `WebSocketParameter` already stored on a `NetworkSettings` instance. | [WebSocketParameterExtensions](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.WebSocketParameterExtensions.html) |

```csharp
var settings = new NetworkSettings();
settings.WithWebSocketParameters(path: "/some/path");
var driver = NetworkDriver.Create(new WebSocketNetworkInterface(), settings);
```

## TLS/WSS requirements for WebGL WebSocket transports

| Subject | What it decides | Source |
|---|---|---|
| HTTPS page → WSS required | If the WebGL build is served over HTTPS, it **must** connect via WSS — browsers enforce that once the page load is secure, every connection it opens must also be secure. | [Using WebSockets](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/websockets.html) |
| Server certificate | The server needs an official CA-signed certificate (e.g. Let's Encrypt); a self-signed certificate is rejected by browsers for WSS. Configure via `settings.WithSecureServerParameters(certificate, privateKey)`. | [Using WebSockets](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/websockets.html) |
| Client configuration | Clients only need `serverName` — `settings.WithSecureClientParameters(serverName: "your-domain.com")` — no CA certificate is required client-side. | [Using WebSockets](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/websockets.html) |

## Choosing between INetworkInterface and NetworkTransport

Two ways exist to plug a custom transport into UTP; the choice is a design trade-off, not a preference.

| Axis | `INetworkInterface` | `Unity.Netcode.NetworkTransport` | Source |
|---|---|---|---|
| Threading | Runs inside UTP's Job System, off the main thread. | Runs on the main thread. | [Using Netcode for GameObjects transports](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/ngo-transports.html) |
| API shape | Packet-based (send/receive raw packets). | Connection-oriented (client IDs, connect/disconnect/poll events). | [Using Netcode for GameObjects transports](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/ngo-transports.html) |
| Type constraints | Must be Burst-compatible, unmanaged. | Uses ordinary managed types (it's a `MonoBehaviour`). | [Using Netcode for GameObjects transports](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/ngo-transports.html) |
| Pick when | The transport is socket-like and the session scales past roughly 10 concurrent players. | The transport needs a complex connection mechanism (handshake, connection approval) and player counts stay modest. | [Using Netcode for GameObjects transports](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/ngo-transports.html) |

Starting with Unity 6.6, an `Unity.Netcode.NetworkTransport` implementation (the same abstract contract NGO custom transports already use) can be wrapped and driven directly by UTP's own `NetworkDriver` via `NetworkTransportInterface` — see below.

## The Unity.Netcode.NetworkTransport contract

`Unity.Netcode.NetworkTransport` (`Unity.Netcode` namespace, `Unity.Networking.Transport.NetcodeInterop.dll`) is described as "a stripped-down abstract class copied from Netcode for GameObjects" — `public abstract class NetworkTransport : MonoBehaviour`. Every abstract member below must be overridden; there is no default behavior to fall back on.

| Member | Kind | Signature | Contract | Source |
|---|---|---|---|---|
| `ServerClientId` | abstract property (`ulong`, get-only) | — | For clients, the server's client ID; unused for servers. | [NetworkTransport](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Netcode.NetworkTransport.html) |
| `Initialize` | abstract method | `void Initialize(NetworkManager networkManager = null)` | Initialize the transport. With Unity Transport, `networkManager` is always `null`. | [NetworkTransport](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Netcode.NetworkTransport.html) |
| `StartServer` | abstract method | `bool StartServer()` | Start listening for incoming connections; return `true` on success. | [NetworkTransport](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Netcode.NetworkTransport.html) |
| `StartClient` | abstract method | `bool StartClient()` | Connect a client to the server; return `true` on success. | [NetworkTransport](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Netcode.NetworkTransport.html) |
| `Shutdown` | abstract method | `void Shutdown()` | Shut down the transport. | [NetworkTransport](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Netcode.NetworkTransport.html) |
| `Send` | abstract method | `void Send(ulong clientId, ArraySegment<byte> payload, NetworkDelivery networkDelivery)` | Send `payload` to `clientId` with the given delivery guarantee. | [NetworkTransport](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Netcode.NetworkTransport.html) |
| `DisconnectLocalClient` | abstract method | `void DisconnectLocalClient()` | Disconnect the local client from the server. | [NetworkTransport](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Netcode.NetworkTransport.html) |
| `DisconnectRemoteClient` | abstract method | `void DisconnectRemoteClient(ulong clientId)` | Disconnect the given client. | [NetworkTransport](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Netcode.NetworkTransport.html) |
| `PollEvent` | abstract method | `NetworkEvent PollEvent(out ulong clientId, out ArraySegment<byte> payload, out float receiveTime)` | Poll for the next incoming event; returns `NetworkEvent.Nothing` when none is pending. | [NetworkTransport](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Netcode.NetworkTransport.html) |
| `GetCurrentRtt` | abstract method | `ulong GetCurrentRtt(ulong clientId)` | Round-trip time in milliseconds; optional — return `0` if unsupported. | [NetworkTransport](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Netcode.NetworkTransport.html) |
| `IsSupported` | virtual property (`bool`, get-only) | — | Whether this transport is supported on the current platform; override only when the transport has platform restrictions. | [NetworkTransport](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Netcode.NetworkTransport.html) |
| `OnEarlyUpdate` | protected virtual method | `void OnEarlyUpdate()` | Invoked before UTP processes received packets — the usual place to read from a socket and accept new connections. | [NetworkTransport](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Netcode.NetworkTransport.html) |
| `OnPostLateUpdate` | protected virtual method | `void OnPostLateUpdate()` | Invoked after packets/events are processed and enqueued — the usual place to actually flush sends if `Send` only enqueues them. | [NetworkTransport](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Netcode.NetworkTransport.html) |
| `OnTransportEvent` | event (`NetworkTransport.TransportEventDelegate`) | — | Fires when the transport has a new event — an alternative to poll-based consumption. Must be invoked on the main thread. | [NetworkTransport](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Netcode.NetworkTransport.html) |
| `EarlyUpdate`, `PostLateUpdate`, `InvokeOnTransportEvent` | non-virtual methods | — | Framework-invoked plumbing — call `InvokeOnTransportEvent` from your own code to raise `OnTransportEvent`; do not override `EarlyUpdate`/`PostLateUpdate` themselves, override `OnEarlyUpdate`/`OnPostLateUpdate` instead. | [NetworkTransport](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Netcode.NetworkTransport.html) |

| Delegate/enum | Values | Source |
|---|---|---|
| `NetworkTransport.TransportEventDelegate` | `void TransportEventDelegate(NetworkEvent eventType, ulong clientId, ArraySegment<byte> payload, float receiveTime)` | [TransportEventDelegate](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Netcode.NetworkTransport.TransportEventDelegate.html) |
| `NetworkEvent` | `Connect` (a client connected), `Data` (data received), `Disconnect` (a remote client disconnected), `Nothing` (no event — only relevant while polling), `TransportFailure` (unrecoverable failure) | [NetworkEvent](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Netcode.NetworkEvent.html) |
| `NetworkDelivery` | `Unreliable` (no order/delivery guarantee); `Reliable`, `ReliableSequenced`, `ReliableFragmentedSequenced`, `UnreliableSequenced` all documented as "unused by Unity Transport" — kept for compatibility with other NGO transports only | [NetworkDelivery](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Netcode.NetworkDelivery.html) |

**Critical caveat**: a UTP-driven `NetworkTransport.Send` is only ever called with `NetworkDelivery.Unreliable` — the other four enum values exist purely for source compatibility with other NGO transports. Building reliability/ordering handling for those values inside a transport meant to run under Unity Transport is wasted work; UTP's own `NetworkPipeline` already owns that concern (see [pipelines-reliability-simulation.md](pipelines-reliability-simulation.md)).

## Minimal custom NetworkTransport skeleton

Shows the shape only — every abstract member from the table above, with the minimum body needed to compile. Real send/receive/connection-state logic replaces the placeholder bodies.

```csharp
using System;
using Unity.Netcode;

namespace Game.Client.Networking;

public sealed class MyNetcodeTransport : NetworkTransport
{
    public override ulong ServerClientId => 0;

    public override void Initialize(NetworkManager networkManager = null)
    {
        // Unity Transport always passes null here; no NetworkManager to read from.
    }

    public override bool StartServer()
    {
        return true;
    }

    public override bool StartClient()
    {
        return true;
    }

    public override void Shutdown()
    {
    }

    public override void Send(ulong clientId, ArraySegment<byte> payload, NetworkDelivery networkDelivery)
    {
        // Unity Transport only ever calls this with NetworkDelivery.Unreliable.
    }

    public override void DisconnectLocalClient()
    {
    }

    public override void DisconnectRemoteClient(ulong clientId)
    {
    }

    public override NetworkEvent PollEvent(out ulong clientId, out ArraySegment<byte> payload, out float receiveTime)
    {
        clientId = 0;
        payload = default;
        receiveTime = 0f;
        return NetworkEvent.Nothing;
    }

    public override ulong GetCurrentRtt(ulong clientId)
    {
        return 0;
    }
}
```

## NetworkTransportInterface — the NGO↔UTP bridge

`Unity.Networking.Transport.NetcodeInterop.NetworkTransportInterface` wraps an `Unity.Netcode.NetworkTransport` so it can act as UTP's `INetworkInterface`, letting `NetworkDriver` drive a Netcode-style transport directly.

| Member | Kind | Description | Source |
|---|---|---|---|
| `NetworkTransportInterface` | struct, implements `INetworkInterface` + `IDisposable` | Wraps a `NetworkTransport` so `NetworkDriver.Create()` can consume it. | [NetworkTransportInterface](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetcodeInterop.NetworkTransportInterface.html) |
| `NetworkTransportInterface(NetworkTransport transport)` | constructor | Takes the `NetworkTransport` component instance to wrap. | [NetworkTransportInterface](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetcodeInterop.NetworkTransportInterface.html) |
| `LocalEndpoint`, `Bind`, `Dispose`, `Initialize`, `Listen`, `ScheduleReceive`, `ScheduleSend` | members | Standard `INetworkInterface` surface, forwarded to the wrapped transport. | [NetworkTransportInterface](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetcodeInterop.NetworkTransportInterface.html) |

```csharp
var go = new GameObject("NetcodeTransport");
GameObject.DontDestroyOnLoad(go);
var transport = go.AddComponent<MyNetcodeTransport>();
var netif = new NetworkTransportInterface(transport);
var driver = NetworkDriver.Create(netif);
```

**Critical caveat**: the `NetworkTransportInterface` API page states it "must be wrapped with `NetworkInterfaceUnmanagedWrapper` before it can be used", since it holds a managed `NetworkTransport` reference internally — yet the manual's own minimal sample above passes `netif` straight into `NetworkDriver.Create(netif)` with no visible wrapping call. Treat that as unresolved rather than assuming either path is safe by default: confirm which `NetworkDriver.Create` overload is actually in play (it may wrap internally) before shipping this pattern.

## NetworkManager and transport assignment

| Subject | What it decides | Source |
|---|---|---|
| `Unity.Netcode.NetworkManager` in this package | Documented as "an empty shell only present for compatibility with existing transports (which take an optional `NetworkManager` parameter in their `Initialize` method)" — it carries no members beyond the ones every `object` has. | [NetworkManager](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Netcode.NetworkManager.html) |
| How UTP calls `Initialize` | Unity Transport "will always pass null to `Initialize(NetworkManager)`" — there is no assignment/discovery step through this stub type. | [NetworkManager](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Netcode.NetworkManager.html) |
| Actual assignment path (this package's context) | A custom transport is wired manually: instantiate it as a component, wrap it in `NetworkTransportInterface`, and hand that to `NetworkDriver.Create()` — see the code sample above. There is no Inspector-field-based assignment in this flow. | [Using Netcode for GameObjects transports](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/ngo-transports.html) |

A real, standalone NGO project's own `NetworkManager` component (its Inspector-assigned transport reference, connection approval, spawning, scene management) is out of scope here — that is `netcode-for-gameobjects` territory. This `Unity.Netcode.NetworkManager` stub exists only so a `NetworkTransport.Initialize(NetworkManager)` signature compiles when driven by UTP directly.

## Migrating from UTP 1.X

The migration page documents the 1.X → 2.0 API break; it is still the current migration reference under the 6.6 docs because no further breaking rename has landed since. UTP 2.0+ (including 6.6) requires Unity Editor 2022.3 or later; 1.X remains on 2021/2022 LTS receiving bug fixes only. The 2.0 wire protocol is backward-incompatible with 1.X — a 2.0+ client cannot connect to a 1.X server or vice versa.

| 1.X API | Current API | Note | Source |
|---|---|---|---|
| `DataStreamReader`/`DataStreamWriter` (UTP) | Same types, moved to `Unity.Collections` | Add `using Unity.Collections;`. | [Migrating from 1.X](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/migration.html) |
| `WriteBytes(byte*, int)` | `WriteBytesUnsafe(byte*, int)` in `Unity.Collections.LowLevel.Unsafe` | All raw-pointer methods gained the `Unsafe` suffix and moved namespace. | [Migrating from 1.X](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/migration.html) |
| `NetworkInterfaceEndPoint` | `NetworkEndpoint` | Type renamed. | [Migrating from 1.X](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/migration.html) |
| `CreateInterfaceEndPoint`, `GetGenericEndPoint` | removed | No replacement listed. | [Migrating from 1.X](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/migration.html) |
| `NetworkSendInterface` | removed — `ScheduleSend` now receives a `PacketsQueue` | Custom `INetworkInterface` implementations must update their send path. | [Migrating from 1.X](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/migration.html) |
| `NetworkPacketReceiver`-based receive | `ScheduleReceive` fills a `PacketsQueue` directly | Custom `INetworkInterface` implementations must update their receive path. | [Migrating from 1.X](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/migration.html) |
| Any `INetworkInterface` | must be Burst-compatible; use `WrapToUnmanaged` if it isn't | New constraint in 2.0+. | [Migrating from 1.X](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/migration.html) |
| driver construction | static `NetworkDriver.Create()` | Replaces older construction paths. | [Migrating from 1.X](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/migration.html) |
| `INetworkInterface.Initialize` | gained a packet-padding parameter | Signature change. | [Migrating from 1.X](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/migration.html) |
| `NetworkPipelineStageCollection.RegisterPipelineStage` | `NetworkDriver.RegisterPipelineStage` | Registration moved onto the driver instance. | [Migrating from 1.X](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/migration.html) |
| `NetworkPipelineStageCollection.GetStageId` | static `NetworkPipelineStageId.Get` | Lookup moved to a static call. | [Migrating from 1.X](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/migration.html) |
| `SimulatorPipelineStageInSend` | deprecated — use `SimulatorPipelineStage` with an `ApplyMode` parameter | Single stage now covers both directions. | [Migrating from 1.X](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/migration.html) |
| `WithBaselibNetworkInterfaceParameters` | deprecated — use `WithNetworkConfigParameters` | Rename/consolidation. | [Migrating from 1.X](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/migration.html) |
| `WithDataStreamParameters`, `WithPipelineParameters` | removed | No replacement listed. | [Migrating from 1.X](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/migration.html) |
| manual timeout config via `WithSecureClientParameters`/`WithSecureServerParameters` | removed | Timeout is no longer configured through the secure-parameters call. | [Migrating from 1.X](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/migration.html) |
| `NetworkDriver.ScheduleUpdate` after `Disconnect` | job completion is now required | A pending `Disconnect` needs its `ScheduleUpdate` job completed before the disconnect takes effect. | [Migrating from 1.X](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/migration.html) |
| Collections package 1.2 → 2.X upgrade | may cause compile errors | Known issue; an Editor restart typically resolves it. | [Migrating from 1.X](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/migration.html) |

## API index

| Type | Source |
|---|---|
| `Unity.Networking.Transport.WebSocketNetworkInterface` | [WebSocketNetworkInterface](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.WebSocketNetworkInterface.html) |
| `Unity.Networking.Transport.WebSocketParameter` | [WebSocketParameter](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.WebSocketParameter.html) |
| `Unity.Networking.Transport.WebSocketParameterExtensions` | [WebSocketParameterExtensions](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.WebSocketParameterExtensions.html) |
| `Unity.Networking.Transport.NetcodeInterop.NetworkTransportInterface` | [NetworkTransportInterface](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetcodeInterop.NetworkTransportInterface.html) |
| `Unity.Netcode.NetworkTransport` | [NetworkTransport](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Netcode.NetworkTransport.html) |
| `Unity.Netcode.NetworkTransport.TransportEventDelegate` | [TransportEventDelegate](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Netcode.NetworkTransport.TransportEventDelegate.html) |
| `Unity.Netcode.NetworkEvent` | [NetworkEvent](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Netcode.NetworkEvent.html) |
| `Unity.Netcode.NetworkDelivery` | [NetworkDelivery](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Netcode.NetworkDelivery.html) |
| `Unity.Netcode.NetworkManager` (this package's compatibility stub) | [NetworkManager](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Netcode.NetworkManager.html) |
