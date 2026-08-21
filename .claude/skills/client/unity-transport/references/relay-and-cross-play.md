# Relay & Cross-Play — NAT Traversal via Unity Relay

Sources: [Cross-play support](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/cross-play.html), [NetworkDriverRelayExtensions](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Relay.NetworkDriverRelayExtensions.html), [RelayAllocationId](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Relay.RelayAllocationId.html), [RelayConnectionData](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Relay.RelayConnectionData.html), [RelayConnectionStatus](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Relay.RelayConnectionStatus.html), [RelayHMACKey](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Relay.RelayHMACKey.html), [RelayNetworkParameter](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Relay.RelayNetworkParameter.html), [RelayParameterExtensions](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Relay.RelayParameterExtensions.html), [RelayServerData](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Relay.RelayServerData.html).
Covers: SKILL.md §4 — **"Route through Unity Relay's RelayServerData when the topology needs NAT traversal without a public server IP"**.

This file owns Relay's UTP-side integration — turning an already-fetched Relay
allocation into a `RelayServerData` the driver can consume — plus cross-play
networking considerations. Transport-level encryption (TLS/DTLS certificates,
`SecureNetworkProtocolParameter`) is a separate, orthogonal concern owned by
[security-and-encryption.md](security-and-encryption.md). Fetching or joining
the Relay allocation itself (`RelayService.Instance.CreateAllocationAsync`,
`JoinAllocationAsync`, `GetJoinCodeAsync`, `AllocationUtils.ToRelayServerData`)
is the Unity Gaming Services Relay SDK's job — a separate product with its own
docs, outside `com.unity.transport`. Nothing under this package's manual or
API roots documents that side; this file covers only what UTP does with the
allocation data once the UGS SDK hands it over.

## Table of contents
- [Turning an allocation into RelayServerData](#turning-an-allocation-into-relayserverdata)
- [Fixed-length Relay byte-blob types](#fixed-length-relay-byte-blob-types)
- [RelayServerData fields](#relayserverdata-fields)
- [Attaching RelayServerData to NetworkSettings](#attaching-relayserverdata-to-networksettings)
- [Connecting through Relay and reading status](#connecting-through-relay-and-reading-status)
- [Cross-play without Relay — MultiNetworkDriver](#cross-play-without-relay--multinetworkdriver)
- [API index](#api-index)

## Turning an allocation into RelayServerData

| Constructor overload | What it decides | Source |
|---|---|---|
| `RelayServerData(string host, ushort port, byte[] allocationId, byte[] connectionData, byte[] hostConnectionData, byte[] key, bool isSecure)` | High-level entry point for a DTLS/UDP relay connection built from the UGS SDK's raw byte arrays. If `host` is a hostname (not an IP literal) this constructor performs a DNS resolution that "may block for 20-120 milliseconds" — build it once outside a per-frame path, never inside `Update`. | [RelayServerData](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Relay.RelayServerData.html) |
| `RelayServerData(string host, ushort port, byte[] allocationId, byte[] connectionData, byte[] hostConnectionData, byte[] key, bool isSecure, bool isWebSocket)` | Same as above, plus the `isWebSocket` flag — set `true` only when the driver will use `WebSocketNetworkInterface` (the `"wss"` protocol). | [RelayServerData](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Relay.RelayServerData.html) |
| `RelayServerData(ref NetworkEndpoint endpoint, ushort nonce, ref RelayAllocationId allocationId, ref RelayConnectionData connectionData, ref RelayConnectionData hostConnectionData, ref RelayHMACKey key, bool isSecure)` | Low-level overload for a pre-resolved `NetworkEndpoint` and already-parsed Relay types — skips the DNS resolution cost of the string-host overloads. | [RelayServerData](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Relay.RelayServerData.html) |
| `RelayServerData(ref NetworkEndpoint endpoint, ushort nonce, ref RelayAllocationId allocationId, ref RelayConnectionData connectionData, ref RelayConnectionData hostConnectionData, ref RelayHMACKey key, bool isSecure, bool isWebSocket)` | Same low-level overload, plus `isWebSocket` for a pre-resolved WebSocket relay connection. | [RelayServerData](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Relay.RelayServerData.html) |

The manual's cross-play example builds `RelayServerData` from a UGS Relay SDK
allocation and shows why Relay makes cross-play trivial: a DTLS host on
desktop/mobile and a WebSocket client from a browser reach each other through
the same Relay server without any transport-specific bridging code. The
`RelayService`/`AllocationUtils` calls below belong to the UGS Relay SDK, not
this package — they are shown only for the allocation-to-`RelayServerData`
handoff this file owns.

```csharp
// Host — connects over DTLS. RelayService/AllocationUtils are UGS Relay SDK
// calls, not part of com.unity.transport; shown only for context.
var allocation = await RelayService.Instance.CreateAllocationAsync(10);
var serverData = AllocationUtils.ToRelayServerData(allocation, "dtls");
var settings = new NetworkSettings();
settings.WithRelayParameters(ref serverData);
var driver = NetworkDriver.Create(settings);
driver.Bind(NetworkEndpoint.AnyIpv4);
driver.Listen();

// Client — connects over WebSocket ("wss"), joining the same Relay session.
var joinedAllocation = await RelayService.Instance.JoinAllocationAsync(joinCode);
var clientServerData = AllocationUtils.ToRelayServerData(joinedAllocation, "wss");
var clientSettings = new NetworkSettings();
clientSettings.WithRelayParameters(ref clientServerData);
var clientDriver = NetworkDriver.Create(new WebSocketNetworkInterface(), clientSettings);
clientDriver.Connect();
```

Supported Relay protocol strings are `"dtls"`, `"wss"`, and `"udp"`.

## Fixed-length Relay byte-blob types

| Type | Fixed length | What it holds | Source |
|---|---|---|---|
| `RelayAllocationId` | 16 bytes (`k_Length`) | "Unique identifier for a connected client/host to a Relay server." Implements `IEquatable<RelayAllocationId>` and `IComparable<RelayAllocationId>`, plus `==`/`!=` operators. Build with `FromByteArray(byte[])` or `FromBytePointer(byte*, int)`. | [RelayAllocationId](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Relay.RelayAllocationId.html) |
| `RelayConnectionData` | 255 bytes (`k_Length`) | "Encrypted data that the Relay server uses to describe a connection." Build with `FromByteArray(byte[])` or `FromBytePointer(byte*, int)`. | [RelayConnectionData](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Relay.RelayConnectionData.html) |
| `RelayHMACKey` | 64 bytes (`k_Length`) | "HMAC key that the Relay server uses to authentify a connection." Build with `FromByteArray(byte[])` or `FromBytePointer(byte*, int)`. | [RelayHMACKey](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Relay.RelayHMACKey.html) |

These three types are the parsed form of the raw byte arrays a UGS Relay
allocation returns (`AllocationId`, `ConnectionData`, `Key`) — the
string/byte-array `RelayServerData` constructors build them internally, and
the low-level constructors expect them pre-built via `FromByteArray`.

## RelayServerData fields

| Field | Type | What it decides | Source |
|---|---|---|---|
| `Endpoint` | `NetworkEndpoint` | The Relay server's IP address and port every packet is actually sent to — never the peer's own address. | [RelayServerData](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Relay.RelayServerData.html) |
| `AllocationId` | `RelayAllocationId` | This peer's own allocation identifier on the Relay server. | [RelayServerData](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Relay.RelayServerData.html) |
| `ConnectionData` | `RelayConnectionData` | This peer's own connection parameters, as issued by the Relay allocation. | [RelayServerData](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Relay.RelayServerData.html) |
| `HostConnectionData` | `RelayConnectionData` | Connection parameters for the session's host peer — set on both the host's and every client's `RelayServerData` so the Relay server can route to the right host. | [RelayServerData](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Relay.RelayServerData.html) |
| `HMACKey` | `RelayHMACKey` | Signs the handshake so the Relay server can authenticate this peer. | [RelayServerData](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Relay.RelayServerData.html) |
| `Nonce` | `ushort` | Handshake nonce; call `IncrementNonce()` to advance it and recompute the associated HMAC rather than mutating it by hand. | [RelayServerData](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Relay.RelayServerData.html) |
| `IsSecure` | `byte` | Nonzero enables DTLS/WSS on top of the Relay connection — the encryption switch, distinct from the Relay routing itself. | [RelayServerData](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Relay.RelayServerData.html) |
| `IsWebSocket` | `byte` | Must agree with the driver's actual `NetworkInterface` — see the critical caveat below. | [RelayServerData](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Relay.RelayServerData.html) |

**Critical caveat**: `RelayServerData.IsWebSocket` is not auto-detected — it
must match the `NetworkInterface` the driver was actually created with. Build
`RelayServerData` with `isWebSocket: true` (or the `"wss"` protocol string)
only when calling `NetworkDriver.Create(new WebSocketNetworkInterface(), settings)`;
a `"dtls"`/`"udp"` driver using the default interface must leave it `false`.
Mismatching the flag against the interface fails the Relay handshake silently
rather than throwing a compile- or setup-time error.

## Attaching RelayServerData to NetworkSettings

| Member | Effect | Source |
|---|---|---|
| `RelayParameterExtensions.WithRelayParameters(this ref NetworkSettings settings, ref RelayServerData serverData, int relayConnectionTimeMS = 3000)` | Attaches the built `RelayServerData` to `NetworkSettings` so `NetworkDriver.Create(settings)` routes through Relay. `Validate()` runs automatically at this point. | [RelayParameterExtensions](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Relay.RelayParameterExtensions.html) |
| `RelayParameterExtensions.GetRelayParameters(this ref NetworkSettings settings)` | Reads back the `RelayNetworkParameter` already stored on `NetworkSettings` — for inspecting configuration after the fact, not for building it. | [RelayParameterExtensions](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Relay.RelayParameterExtensions.html) |
| `RelayNetworkParameter.RelayConnectionTimeMS` (`int`, milliseconds) | Ping frequency that keeps the Relay connection alive. Default is 3000 ms; "should be set to less than 10 seconds since that's the time after which the relay server will sever the connection if there is no activity." | [RelayNetworkParameter](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Relay.RelayNetworkParameter.html) |
| `RelayNetworkParameter.ServerData` (`RelayServerData`) | The connection data described in the fields table above. | [RelayNetworkParameter](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Relay.RelayNetworkParameter.html) |
| `RelayNetworkParameter.Validate()` | Checks every field is valid; called automatically when the parameter is added to `NetworkSettings` — no need to call it directly. | [RelayNetworkParameter](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Relay.RelayNetworkParameter.html) |

## Connecting through Relay and reading status

| Member | Effect | Source |
|---|---|---|
| `NetworkDriverRelayExtensions.Connect(this NetworkDriver driver)` | Connects to the Relay server without an endpoint parameter — the endpoint already lives in the driver's `RelayServerData`. Returns a default `NetworkConnection` if the attempt fails. | [NetworkDriverRelayExtensions](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Relay.NetworkDriverRelayExtensions.html) |
| `NetworkDriverRelayExtensions.GetRelayConnectionStatus(this NetworkDriver driver)` | Returns the driver's current `RelayConnectionStatus` — poll this to detect a dead allocation instead of inferring it from send/receive failures. | [NetworkDriverRelayExtensions](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Relay.NetworkDriverRelayExtensions.html) |

| `RelayConnectionStatus` value | Meaning | Source |
|---|---|---|
| `NotUsingRelay` | "The NetworkDriver is not configured to use Unity Relay" — no `RelayServerData` was attached via `WithRelayParameters`. | [RelayConnectionStatus](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Relay.RelayConnectionStatus.html) |
| `NotEstablished` | Connection to the Relay server has not been made yet; it starts automatically on `Connect()` or `Bind()`. | [RelayConnectionStatus](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Relay.RelayConnectionStatus.html) |
| `Established` | Connection to the Relay server is up, and stays that way "until the NetworkDriver is disposed or an error invalidates the relay service allocation." | [RelayConnectionStatus](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Relay.RelayConnectionStatus.html) |
| `AllocationInvalid` | The allocation was invalid, or "timed out from inactivity" — see the critical caveat below. | [RelayConnectionStatus](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Relay.RelayConnectionStatus.html) |

**Critical caveat**: `AllocationInvalid` is not recoverable by retrying
`Connect()` on the same driver. A Relay allocation and HMAC key expire from
inactivity (bounded by `RelayConnectionTimeMS`, capped under 10 seconds
server-side); once `GetRelayConnectionStatus()` reports `AllocationInvalid`,
the fix is to request a fresh allocation from the UGS Relay SDK and build a
new `RelayServerData`/`NetworkDriver` from it — the existing driver cannot be
reused in place.

## Cross-play without Relay — MultiNetworkDriver

When Relay is not in the topology, a single `NetworkDriver` "can only accept
connections on a single connection type," so cross-play across UDP, WebSocket,
or IPv4/IPv6 clients requires `MultiNetworkDriver` — a container that manages
several `NetworkDriver` instances behind one API.

| Requirement to add a driver | Detail | Source |
|---|---|---|
| Listening state | The driver must already be `Listening` before it is added. | [Cross-play support](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/cross-play.html) |
| No prior connections | The driver must not have accepted any connections yet. | [Cross-play support](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/cross-play.html) |
| Matching pipeline count | Every driver added to the same `MultiNetworkDriver` must define the same number of pipelines (per-driver pipeline stages may still differ). | [Cross-play support](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/cross-play.html) |
| 4-driver cap | A `MultiNetworkDriver` accepts at most 4 drivers. | [Cross-play support](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/cross-play.html) |

```csharp
var udpDriver = NetworkDriver.Create(new UDPNetworkInterface());
udpDriver.Bind(NetworkEndpoint.AnyIpv4.WithPort(7777));
udpDriver.Listen();

var wsDriver = NetworkDriver.Create(new WebSocketNetworkInterface());
wsDriver.Bind(NetworkEndpoint.AnyIpv4.WithPort(7778));
wsDriver.Listen();

var multiDriver = MultiNetworkDriver.Create();
multiDriver.AddDriver(udpDriver);
multiDriver.AddDriver(wsDriver);
```

The same pattern combines an IPv4 and an IPv6 driver for dual-stack support,
or a driver with a `ReliableSequencedPipelineStage` alongside one using
`NullPipelineStage` when the two connection types need different pipeline
configurations. A client-side `MultiNetworkDriver` is valid too — it lets
client code call `Connect(driverId, endpoint)` through the same shared API
used on the server. Prefer routing through Relay (above) over hand-rolling
`MultiNetworkDriver` when NAT traversal is also required — `MultiNetworkDriver`
solves protocol diversity, not the lack of a public server IP.

## API index

| Type | Source |
|---|---|
| `NetworkDriverRelayExtensions` | [NetworkDriverRelayExtensions](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Relay.NetworkDriverRelayExtensions.html) |
| `RelayAllocationId` | [RelayAllocationId](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Relay.RelayAllocationId.html) |
| `RelayConnectionData` | [RelayConnectionData](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Relay.RelayConnectionData.html) |
| `RelayConnectionStatus` | [RelayConnectionStatus](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Relay.RelayConnectionStatus.html) |
| `RelayHMACKey` | [RelayHMACKey](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Relay.RelayHMACKey.html) |
| `RelayNetworkParameter` | [RelayNetworkParameter](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Relay.RelayNetworkParameter.html) |
| `RelayParameterExtensions` | [RelayParameterExtensions](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Relay.RelayParameterExtensions.html) |
| `RelayServerData` | [RelayServerData](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Relay.RelayServerData.html) |

Every page above was fetched and confirmed to resolve at `@6.6`; none 404'd
or came back as a stub. What none of them document — allocation creation,
join codes, or the `RelayService`/`AllocationUtils` UGS SDK surface used in
the code sample above — is intentionally out of scope for this package's own
docs, and therefore out of scope for this file.
