# Diagnostics & Testing — Statistics, Logging, Disconnect Reasons, FAQ

Source: [Frequently Asked Questions](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/faq.html), [BandwidthStatistics](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Analytics.BandwidthStatistics.html), [ConnectionStatistics](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Analytics.ConnectionStatistics.html), [ConnectionStatistics.LatencyStatistics](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Analytics.ConnectionStatistics.LatencyStatistics.html), [DriverStatistics](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Analytics.DriverStatistics.html), [PacketSizeStatistics](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Analytics.PacketSizeStatistics.html), [DisconnectReason](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Error.DisconnectReason.html), [StatusCode](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Error.StatusCode.html), [LoggingParameter](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Logging.LoggingParameter.html), [LoggingParameterExtensions](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Logging.LoggingParameterExtensions.html).
Covers: SKILL.md §4 — **"Verify with a real multi-client connect, send, and disconnect run before claiming the feature works"**.

This file is the destination for diagnosing an already-running connection — why a client disconnected, what a driver's statistics show, and how to turn on logging — and for the package's own FAQ/troubleshooting content. It does not cover the driver setup that precedes any of this (creating the driver, binding, connecting, running the update loop), which lives in [core-driver-lifecycle.md](core-driver-lifecycle.md). Per SKILL.md §4's verification directive, this file supports diagnosing a run, but a real multi-client connect/send/disconnect run is what actually proves a feature works — reading statistics after the fact isn't a substitute for that test.

## Contents
- [Frequently asked questions (troubleshooting)](#frequently-asked-questions-troubleshooting)
- [Disconnect reasons — Error.DisconnectReason](#disconnect-reasons--errordisconnectreason)
- [Status codes — Error.StatusCode](#status-codes--errorstatuscode)
- [Driver-wide statistics — DriverStatistics, BandwidthStatistics, PacketSizeStatistics](#driver-wide-statistics--driverstatistics-bandwidthstatistics-packetsizestatistics)
- [Per-connection statistics — ConnectionStatistics, LatencyStatistics](#per-connection-statistics--connectionstatistics-latencystatistics)
- [Driver logging — LoggingParameter](#driver-logging--loggingparameter)
- [API index](#api-index)

## Frequently asked questions (troubleshooting)

| Question | Key fact | Source |
|---|---|---|
| Which endpoint should I bind to? | Clients should not call `Bind` — the default ephemeral-port auto-bind on `Connect` is correct 99% of the time. Servers bind `NetworkEndpoint.AnyIpv4.WithPort(port)` (or `NetworkEndpoint.LoopbackIpv4` to block external connections during local dev). With Unity Relay, even the server should bind an ephemeral port via `AnyIpv4` | [FAQ](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/faq.html#which-endpoint-should-i-bind-to) |
| Why is `Bind` returning an error? | The endpoint doesn't exist locally (e.g. a public IP behind a router), the port is already used by another service (check with `netstat -a -p UDP`), the port is below 1024 and needs elevated privileges, or the OS user lacks socket-creation permission | [FAQ](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/faq.html#why-is-bind-returning-an-error) |
| Why isn't my client connecting? | Confirm the server bound correctly (see above), then try disabling the firewall — if that fixes it, add a proper exception instead of leaving it off. Confirm reachability with `ping`, `traceroute`, or Wireshark | [FAQ](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/faq.html#why-isnt-my-client-connecting) |
| How do I change the connection/disconnection timeouts? | Set `connectTimeoutMS`, `maxConnectAttempts`, `disconnectTimeoutMS` via `NetworkSettings.WithNetworkConfigParameters`. Defaults are 1 minute to establish a connection, 30 seconds of inactivity before disconnecting | [FAQ](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/faq.html#how-can-i-modify-the-connectiondisconnection-timeouts) |
| Why was my connection closed? | Read the single byte off the `DataStreamReader` that `PopEvent` returns when the popped event is `NetworkEvent.Type.Disconnect`; the value maps to `Error.DisconnectReason` (see below) | [FAQ](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/faq.html#why-was-my-connection-closed) |
| Why isn't the other end immediately notified of a disconnection? | `Disconnect()` only queues the disconnect message — it is not actually sent until the next `ScheduleUpdate`. Wait a frame (schedule and complete one more update) before `Dispose`-ing the driver; `ScheduleFlushSend` alone is not sufficient | [FAQ](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/faq.html#why-isnt-the-other-end-immediately-notified-of-a-disconnection) |
| What's the largest message I can send? | Compute `NetworkParameterConstants.MaxMessageSize - driver.MaxHeaderSize(pipeline)`, or open a `BeginSend` and read `writer.Capacity` then `AbortSend` it. Use `FragmentationPipelineStage` for payloads larger than that | [FAQ](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/faq.html#whats-the-largest-message-i-can-send) |
| Why are large messages getting lost? | Usually IP fragmentation at the network layer. If it persists, lower `maxMessageSize` (default 1400) via `NetworkSettings.WithNetworkConfigParameters` — only recommended if the default is actually causing the problem | [FAQ](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/faq.html#why-are-large-messages-getting-lost) |
| What does error `NetworkSendQueueFull` mean? | From `BeginSend`: the send/receive queue is undersized — raise `sendQueueCapacity`/`receiveQueueCapacity` together via `NetworkSettings.WithNetworkConfigParameters` (default 512; ~1500 bytes of memory per capacity unit). From `EndSend`: only possible with `ReliableSequencedPipelineStage` — 32 reliable packets are already in flight, which is the maximum | [FAQ](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/faq.html#what-does-error-networksendqueuefull-mean) |

**Critical caveat**: the FAQ's disconnect-notification note is the single most common cause of a "the other client never sees the disconnect" bug report — calling `Disconnect()` and immediately `Dispose()`-ing the driver in the same frame drops the outgoing disconnect packet on the floor. Always schedule and complete one more update between the two calls.

## Disconnect reasons — Error.DisconnectReason

`byte`-backed enum. Obtained by reading one byte off the `DataStreamReader` from `PopEvent` when the event is `NetworkEvent.Type.Disconnect`.

| Value | Meaning | Source |
|---|---|---|
| `Default` | Internal placeholder value; not a real disconnect cause | [DisconnectReason](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Error.DisconnectReason.html#Unity_Networking_Transport_Error_DisconnectReason_Default) |
| `ClosedByRemote` | The remote peer manually closed the connection | [DisconnectReason](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Error.DisconnectReason.html#Unity_Networking_Transport_Error_DisconnectReason_ClosedByRemote) |
| `Timeout` | Connection timed out due to inactivity (see `disconnectTimeoutMS` above) | [DisconnectReason](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Error.DisconnectReason.html#Unity_Networking_Transport_Error_DisconnectReason_Timeout) |
| `MaxConnectionAttempts` | Connect handshake failed — the server could not be reached within `maxConnectAttempts` | [DisconnectReason](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Error.DisconnectReason.html#Unity_Networking_Transport_Error_DisconnectReason_MaxConnectionAttempts) |
| `HostNotFound` | Hostname-based `Connect` could not resolve the host | [DisconnectReason](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Error.DisconnectReason.html#Unity_Networking_Transport_Error_DisconnectReason_HostNotFound) |
| `ProtocolError` | Unrecoverable low-level protocol failure (unexpected socket error, malformed TCP payload) | [DisconnectReason](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Error.DisconnectReason.html#Unity_Networking_Transport_Error_DisconnectReason_ProtocolError) |
| `AuthenticationFailure` | Remote peer failed authentication; only possible when using DTLS or TLS (WebSockets) | [DisconnectReason](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Error.DisconnectReason.html#Unity_Networking_Transport_Error_DisconnectReason_AuthenticationFailure) |

**Critical caveat**: `Default` is documented as "internal value, do not use" and `ProtocolError` is documented as something that "should not be returned under normal operating circumstances." Seeing either in a real disconnect event is itself a bug signal — `Default` usually means the byte was misread from the wrong stream offset, and `ProtocolError` means an unexpected socket/stream failure occurred, not a normal disconnect path. Neither should be treated as an ordinary "connection ended" case.

## Status codes — Error.StatusCode

Returned by many driver/pipeline methods (`BeginSend`, `EndSend`, `Connect`, etc.) to report why an operation failed.

| Value | Meaning | Source |
|---|---|---|
| `Success` | Operation completed successfully | [StatusCode](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Error.StatusCode.html#Unity_Networking_Transport_Error_StatusCode_Success) |
| `NetworkDriverParallelForErr` | The same connection was processed in two different jobs | [StatusCode](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Error.StatusCode.html#Unity_Networking_Transport_Error_StatusCode_NetworkDriverParallelForErr) |
| `NetworkIdMismatch` | Connection handle is invalid | [StatusCode](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Error.StatusCode.html#Unity_Networking_Transport_Error_StatusCode_NetworkIdMismatch) |
| `NetworkPacketOverflow` | Packet is too large for the supported capacity | [StatusCode](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Error.StatusCode.html#Unity_Networking_Transport_Error_StatusCode_NetworkPacketOverflow) |
| `NetworkReceiveQueueFull` | Receive queue is full; only ever returned through `NetworkDriver.ReceiveErrorCode` | [StatusCode](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Error.StatusCode.html#Unity_Networking_Transport_Error_StatusCode_NetworkReceiveQueueFull) |
| `NetworkSendHandleInvalid` | The `DataStreamWriter` handle from `BeginSend` is invalid | [StatusCode](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Error.StatusCode.html#Unity_Networking_Transport_Error_StatusCode_NetworkSendHandleInvalid) |
| `NetworkSendQueueFull` | Send queue is full — see the FAQ row above for the fix | [StatusCode](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Error.StatusCode.html#Unity_Networking_Transport_Error_StatusCode_NetworkSendQueueFull) |
| `NetworkSocketError` | Underlying low-level socket reported an error | [StatusCode](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Error.StatusCode.html#Unity_Networking_Transport_Error_StatusCode_NetworkSocketError) |
| `NetworkStateMismatch` | Connection state doesn't allow the requested operation — usually a send attempted on a connecting or closed connection | [StatusCode](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Error.StatusCode.html#Unity_Networking_Transport_Error_StatusCode_NetworkStateMismatch) |
| `NetworkVersionMismatch` | Connection handle is stale — usually caused by reusing a connection that was already closed | [StatusCode](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Error.StatusCode.html#Unity_Networking_Transport_Error_StatusCode_NetworkVersionMismatch) |

## Driver-wide statistics — DriverStatistics, BandwidthStatistics, PacketSizeStatistics

`NetworkDriver.GetStatistics()` returns a `DriverStatistics` struct, cumulative since the driver was created and aggregated across every connection it has ever handled.

| Fields | Type | What it shows | Source |
|---|---|---|---|
| `RxBandwidth` / `TxBandwidth` | `BandwidthStatistics` | Incoming/outgoing bandwidth usage — see the table below | [DriverStatistics](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Analytics.DriverStatistics.html) |
| `RxTotalBytes` / `TxTotalBytes` | `ulong` | Cumulative bytes received/transmitted by the driver | [DriverStatistics](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Analytics.DriverStatistics.html#Unity_Networking_Transport_Analytics_DriverStatistics_RxTotalBytes) |
| `RxTotalPackets` / `TxTotalPackets` | `ulong` | Cumulative packets received/transmitted by the driver | [DriverStatistics](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Analytics.DriverStatistics.html#Unity_Networking_Transport_Analytics_DriverStatistics_RxTotalPackets) |
| `RxPacketSizes` / `TxPacketSizes` | `PacketSizeStatistics` | Size-distribution buckets for received/transmitted packets — see the table below | [DriverStatistics](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Analytics.DriverStatistics.html) |
| `RxMeanQueueUsage` / `TxMeanQueueUsage` | `float` | Average receive/send queue usage, in packets, over the driver's lifetime — compare against `receiveQueueCapacity`/`sendQueueCapacity` | [DriverStatistics](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Analytics.DriverStatistics.html#Unity_Networking_Transport_Analytics_DriverStatistics_RxMeanQueueUsage) |
| `RxMaximumQueueUsage` / `TxMaximumQueueUsage` | `uint` | Peak receive/send queue usage, in packets — a value approaching the configured capacity explains a `NetworkSendQueueFull` status seen in the FAQ above | [DriverStatistics](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Analytics.DriverStatistics.html#Unity_Networking_Transport_Analytics_DriverStatistics_RxMaximumQueueUsage) |

`BandwidthStatistics` — all values in kbit/s:

| Field | What it shows | Source |
|---|---|---|
| `Current` | Bandwidth usage over the last full second | [BandwidthStatistics](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Analytics.BandwidthStatistics.html#Unity_Networking_Transport_Analytics_BandwidthStatistics_Current) |
| `Mean` | Average bandwidth over the driver's entire lifetime | [BandwidthStatistics](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Analytics.BandwidthStatistics.html#Unity_Networking_Transport_Analytics_BandwidthStatistics_Mean) |
| `Minimum` / `Maximum` | Lowest/highest bandwidth seen over any complete 1-second window; both read `0` until at least 1 second of data has been collected | [BandwidthStatistics](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Analytics.BandwidthStatistics.html#Unity_Networking_Transport_Analytics_BandwidthStatistics_Maximum) |
| `MaximumBurst` | Highest bandwidth seen within a single driver update — a finer-grained spike than `Maximum` | [BandwidthStatistics](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Analytics.BandwidthStatistics.html#Unity_Networking_Transport_Analytics_BandwidthStatistics_MaximumBurst) |

`PacketSizeStatistics` — size-distribution buckets and summary stats, in bytes:

| Field | What it shows | Source |
|---|---|---|
| `SmallerThan128Bytes`, `Between128And255Bytes`, `Between256And511Bytes`, `Between512And1023Bytes`, `LargerThan1023Bytes` | Packet counts falling into each size bucket | [PacketSizeStatistics](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Analytics.PacketSizeStatistics.html) |
| `Minimum` / `Maximum` / `Mean` / `StandardDeviation` | Distribution stats across all recorded packet sizes | [PacketSizeStatistics](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Analytics.PacketSizeStatistics.html) |

**Critical caveat**: `PacketSizeStatistics` sizes include IP and UDP/TCP headers but exclude link-layer headers (Ethernet, Wi-Fi) and any padding the link layer adds — so these numbers will not match a raw packet capture byte-for-byte. For WebSocket connections the TCP header is assumed to be 32 bytes, an approximation, not a measurement. Only a custom `INetworkInterface` reports exact sizes with no OS header assumptions.

## Per-connection statistics — ConnectionStatistics, LatencyStatistics

`NetworkDriver.GetConnectionStatistics(connection)` returns a `ConnectionStatistics` struct, valid only while the connection is in the `Connected` state, cumulative for that connection's lifetime.

| Member | Type | What it shows | Source |
|---|---|---|---|
| `Latency` | `ConnectionStatistics.LatencyStatistics` | Round-trip time statistics — see the table below | [ConnectionStatistics](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Analytics.ConnectionStatistics.html#Unity_Networking_Transport_Analytics_ConnectionStatistics_Latency) |
| `PacketLossPercent` | `float` | Percentage of packets lost on this connection | [ConnectionStatistics](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Analytics.ConnectionStatistics.html#Unity_Networking_Transport_Analytics_ConnectionStatistics_PacketLossPercent) |
| `PacketDuplicationPercent` | `float` | Percentage of packets duplicated on this connection | [ConnectionStatistics](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Analytics.ConnectionStatistics.html#Unity_Networking_Transport_Analytics_ConnectionStatistics_PacketDuplicationPercent) |
| `PacketOutOfOrderPercent` | `float` | Percentage of packets received out of order on this connection | [ConnectionStatistics](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Analytics.ConnectionStatistics.html#Unity_Networking_Transport_Analytics_ConnectionStatistics_PacketOutOfOrderPercent) |
| `Reliable` | `ReliableUtility.Statistics` | Cumulative counters for pipelines on this connection using `ReliableSequencedPipelineStage` | [ConnectionStatistics](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Analytics.ConnectionStatistics.html#Unity_Networking_Transport_Analytics_ConnectionStatistics_Reliable) |
| `UnreliableSequenced` | `UnreliableSequencedPipelineStage.Statistics` | Cumulative counters for pipelines on this connection using `UnreliableSequencedPipelineStage` | [ConnectionStatistics](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Analytics.ConnectionStatistics.html#Unity_Networking_Transport_Analytics_ConnectionStatistics_UnreliableSequenced) |

`ConnectionStatistics.LatencyStatistics` — all values are RTT ("ping") in milliseconds:

| Field | What it shows | Source |
|---|---|---|
| `Current` | Most recent RTT sample | [LatencyStatistics](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Analytics.ConnectionStatistics.LatencyStatistics.html#Unity_Networking_Transport_Analytics_ConnectionStatistics_LatencyStatistics_Current) |
| `SmoothedCurrent` | Weighted average of the last few RTT samples | [LatencyStatistics](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Analytics.ConnectionStatistics.LatencyStatistics.html#Unity_Networking_Transport_Analytics_ConnectionStatistics_LatencyStatistics_SmoothedCurrent) |
| `Mean` | Average RTT over the connection's lifetime | [LatencyStatistics](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Analytics.ConnectionStatistics.LatencyStatistics.html#Unity_Networking_Transport_Analytics_ConnectionStatistics_LatencyStatistics_Mean) |
| `Minimum` / `Maximum` | Lowest/highest RTT seen over the connection's lifetime | [LatencyStatistics](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Analytics.ConnectionStatistics.LatencyStatistics.html#Unity_Networking_Transport_Analytics_ConnectionStatistics_LatencyStatistics_Maximum) |
| `StandardDeviation` | Standard deviation of RTT around `Mean` | [LatencyStatistics](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Analytics.ConnectionStatistics.LatencyStatistics.html#Unity_Networking_Transport_Analytics_ConnectionStatistics_LatencyStatistics_StandardDeviation) |

**Critical caveat**: `Latency` and `PacketDuplicationPercent` are drawn entirely from pipelines carrying a `ReliableSequencedPipelineStage`, and their quality depends on how much traffic actually flows over that pipeline. `PacketLossPercent` and `PacketOutOfOrderPercent` draw from both reliable and unreliable-sequenced pipelines. A connection that only ever sends on a plain unreliable pipeline will report zero/meaningless latency and duplication figures — this is not the same as "connection has zero latency."

## Driver logging — LoggingParameter

| Member | Signature | What it does | Source |
|---|---|---|---|
| `LoggingParameter.DriverName` | field, `FixedString32Bytes` | Label to use for this driver in the logs | [LoggingParameter](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Logging.LoggingParameter.html#Unity_Networking_Transport_Logging_LoggingParameter_DriverName) |
| `LoggingParameter.Validate()` | method → `bool` | Runs automatically when the parameter is added to `NetworkSettings`; returns `false` on invalid field data | [LoggingParameter](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Logging.LoggingParameter.html#Unity_Networking_Transport_Logging_LoggingParameter_Validate) |
| `NetworkSettings.WithLoggingParameters(driverName)` | extension method → `ref NetworkSettings` | Attaches a `LoggingParameter` carrying `driverName` to the settings | [LoggingParameterExtensions](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Logging.LoggingParameterExtensions.html) |

**Critical caveat**: the `LoggingParameter` type's own summary states it is "Currently unused." Calling `WithLoggingParameters` in 6.6 records a driver name on `NetworkSettings` but does not by itself turn on any additional diagnostic log output — do not treat setting this parameter as equivalent to enabling verbose/debug logging, and do not spend time debugging a "logging didn't turn on" report by way of this API alone.

## API index

| Type | Source |
|---|---|
| `BandwidthStatistics` | [API](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Analytics.BandwidthStatistics.html) |
| `ConnectionStatistics` | [API](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Analytics.ConnectionStatistics.html) |
| `ConnectionStatistics.LatencyStatistics` | [API](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Analytics.ConnectionStatistics.LatencyStatistics.html) |
| `DriverStatistics` | [API](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Analytics.DriverStatistics.html) |
| `PacketSizeStatistics` | [API](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Analytics.PacketSizeStatistics.html) |
| `Error.DisconnectReason` | [API](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Error.DisconnectReason.html) |
| `Error.StatusCode` | [API](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Error.StatusCode.html) |
| `Logging.LoggingParameter` | [API](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Logging.LoggingParameter.html) |
| `Logging.LoggingParameterExtensions` | [API](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Logging.LoggingParameterExtensions.html) |
