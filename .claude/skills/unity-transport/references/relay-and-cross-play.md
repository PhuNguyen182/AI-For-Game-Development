# Relay and cross-play

Sources (`@6.6`): manual `cross-play`; API `Relay.RelayServerData`, `Relay.RelayParameterExtensions`, `Relay.RelayNetworkParameter`, `Relay.NetworkDriverRelayExtensions`, `Relay.RelayConnectionStatus`, `Relay.RelayAllocationId`, `Relay.RelayConnectionData`, `Relay.RelayHMACKey`.

Scope: turning a Relay allocation into `RelayServerData` the driver consumes. Fetching or joining the allocation (`RelayService`, `AllocationUtils`) belongs to the UGS Relay SDK, a separate product that this package's docs do not cover. TLS/DTLS certificates are in `security-and-encryption.md`.

## RelayServerData

Constructors:
- `(string host, ushort port, byte[] allocationId, byte[] connectionData, byte[] hostConnectionData, byte[] key, bool isSecure[, bool isWebSocket])` is the high-level entry from the SDK's raw arrays. A hostname `host` triggers a DNS resolution that may block 20-120 ms: build once, never in `Update`.
- `(ref NetworkEndpoint, ushort nonce, ref RelayAllocationId, ref RelayConnectionData, ref RelayConnectionData hostConnectionData, ref RelayHMACKey, bool isSecure[, bool isWebSocket])` takes a pre-resolved endpoint and parsed types, so no DNS.

Parsed types (each built with `FromByteArray(byte[])` or `FromBytePointer(byte*, int)`):
- `RelayAllocationId`: 16 bytes.
- `RelayConnectionData`: 255 bytes.
- `RelayHMACKey`: 64 bytes.

Fields:
- `Endpoint`: the Relay server every packet goes to, never the peer.
- `AllocationId`, `ConnectionData`, `HMACKey`: this peer's own.
- `HostConnectionData`: the host's, set on the host and every client so Relay routes to the right host.
- `Nonce`: advance with `IncrementNonce()`, which recomputes the HMAC; do not mutate it by hand.
- `IsSecure`: nonzero enables DTLS/WSS on top of Relay (encryption, separate from routing).
- `IsWebSocket`: not auto-detected. Set `true` (or protocol `"wss"`) only with `NetworkDriver.Create(new WebSocketNetworkInterface(), settings)`; leave `false` for `"dtls"`/`"udp"` on the default interface. A mismatch fails the handshake silently.

Protocol strings are `"dtls"`, `"wss"`, `"udp"`.

## Wiring

- `settings.WithRelayParameters(ref serverData, relayConnectionTimeMS = 3000)` attaches it; `Validate()` runs automatically. `GetRelayParameters` reads back.
- `RelayConnectionTimeMS` is the keep-alive ping interval. Keep it under 10 s, since the Relay server severs an idle connection after that.
- `driver.Connect()` (extension, no endpoint) uses the endpoint in `RelayServerData`; it returns a default `NetworkConnection` on failure. The Relay connection starts automatically on `Connect()` or `Bind()`.
- Poll `driver.GetRelayConnectionStatus()`; do not infer a dead allocation from send failures:
  - `NotUsingRelay`: no `RelayServerData` attached.
  - `NotEstablished`: not connected yet.
  - `Established`: up until the driver is disposed or an error invalidates the allocation.
  - `AllocationInvalid`: invalid or timed out from inactivity. Retrying `Connect()` does not recover it. Request a fresh allocation and build a new `RelayServerData` and `NetworkDriver`.

```csharp
// Host over DTLS; client joins the same session over WebSocket.
var serverData = AllocationUtils.ToRelayServerData(allocation, "dtls");   // UGS SDK
var settings = new NetworkSettings();
settings.WithRelayParameters(ref serverData);
var driver = NetworkDriver.Create(settings);
driver.Bind(NetworkEndpoint.AnyIpv4);
driver.Listen();

var clientData = AllocationUtils.ToRelayServerData(joined, "wss");        // UGS SDK
var clientSettings = new NetworkSettings();
clientSettings.WithRelayParameters(ref clientData);
var clientDriver = NetworkDriver.Create(new WebSocketNetworkInterface(), clientSettings);
clientDriver.Connect();
```

Relay makes cross-play trivial: a DTLS host and a browser WebSocket client reach each other through the same server with no bridging code.

## Cross-play without Relay

One `NetworkDriver` accepts a single connection type. UDP, WebSocket or IPv4/IPv6 clients together need `MultiNetworkDriver` (limits in `jobs-and-concurrent-api.md`): each driver must already be `Listening`, have accepted no connections, and define the same number of pipelines (stages may differ); at most 4 drivers.

```csharp
var udp = NetworkDriver.Create(new UDPNetworkInterface());
udp.Bind(NetworkEndpoint.AnyIpv4.WithPort(7777)); udp.Listen();
var ws = NetworkDriver.Create(new WebSocketNetworkInterface());
ws.Bind(NetworkEndpoint.AnyIpv4.WithPort(7778)); ws.Listen();
var multi = MultiNetworkDriver.Create();
multi.AddDriver(udp);
multi.AddDriver(ws);
```

- It also pairs IPv4 with IPv6, or a reliable pipeline with a `NullPipelineStage` one.
- A client-side `MultiNetworkDriver` calls `Connect(driverId, endpoint)`.
- It solves protocol diversity, not a missing public server IP: use Relay when NAT traversal is also needed.
