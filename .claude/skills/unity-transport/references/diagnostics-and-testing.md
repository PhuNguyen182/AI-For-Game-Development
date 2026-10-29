# Diagnostics and testing

Sources (`@6.6`): manual `faq`; API `Error.DisconnectReason`, `Error.StatusCode`, `Analytics.DriverStatistics`, `Analytics.ConnectionStatistics`, `Logging.LoggingParameter`.

Statistics explain a run; they do not replace a real multi-client connect, send and disconnect run.

## FAQ

- **Which endpoint to bind?** Clients do not call `Bind`; the ephemeral auto-bind on `Connect` is right ~99% of the time. Servers bind `AnyIpv4.WithPort(port)`, or `LoopbackIpv4` to block external connections in local dev. With Relay, even the server binds an ephemeral port via `AnyIpv4`.
- **`Bind` returns an error?** The endpoint does not exist locally (e.g. a public IP behind a router), the port is in use (`netstat -a -p UDP`), the port is below 1024 and needs elevation, or the OS user may not create sockets.
- **Client will not connect?** Confirm the server bound. Test with the firewall off; if that fixes it, add a proper exception instead of leaving it off. Check reachability with `ping`, `traceroute` or Wireshark.
- **Change timeouts?** `connectTimeoutMS`, `maxConnectAttempts`, `disconnectTimeoutMS` via `WithNetworkConfigParameters`. Defaults: ~1 minute to establish, 30 s of inactivity (`core-driver-lifecycle.md`).
- **Peer not told of a disconnect?** `Disconnect()` only queues the message; it ships on the next `ScheduleUpdate`. `Disconnect()` then `Dispose()` in one frame drops it. Schedule and complete one more update between them; `ScheduleFlushSend` alone is not enough.
- **Largest message?** `NetworkParameterConstants.MaxMessageSize - driver.MaxHeaderSize(pipeline)`, or `BeginSend`, read `writer.Capacity`, then `AbortSend`. Larger needs `FragmentationPipelineStage`.
- **Large messages lost?** Usually IP fragmentation. Lower `maxMessageSize` (default 1400) only if the default is the cause.
- **`NetworkSendQueueFull`?** From `BeginSend`: raise `sendQueueCapacity` and `receiveQueueCapacity` together (default 512, ~1500 bytes of memory per unit). From `EndSend`: only with `ReliableSequencedPipelineStage`, when the in-flight window is full. The FAQ states 32; `windowSize` is configurable (`pipelines-reliability-simulation.md`).

## DisconnectReason

Read one byte from the `DataStreamReader` of a `Disconnect` event.

| Value | Meaning |
|---|---|
| `Default` | Internal; seeing it usually means the byte was read at the wrong offset |
| `ClosedByRemote` | Peer closed it |
| `Timeout` | Inactivity (`disconnectTimeoutMS`) |
| `MaxConnectionAttempts` | Server unreachable within `maxConnectAttempts` |
| `HostNotFound` | Hostname `Connect` could not resolve |
| `ProtocolError` | Unrecoverable protocol failure (socket error, malformed TCP payload); not normal operation |
| `AuthenticationFailure` | DTLS/TLS authentication failed |

## StatusCode

Returned by `BeginSend`, `EndSend`, `Connect` and others.

| Value | Meaning |
|---|---|
| `Success` | OK |
| `NetworkDriverParallelForErr` | One connection processed in two jobs |
| `NetworkIdMismatch` | Invalid connection handle |
| `NetworkPacketOverflow` | Packet too large |
| `NetworkReceiveQueueFull` | Only via `NetworkDriver.ReceiveErrorCode` |
| `NetworkSendHandleInvalid` | Invalid `DataStreamWriter` from `BeginSend` |
| `NetworkSendQueueFull` | See FAQ |
| `NetworkSocketError` | Low-level socket error |
| `NetworkStateMismatch` | Send on a connecting or closed connection |
| `NetworkVersionMismatch` | Stale handle: a closed connection was reused |

## Statistics

`driver.GetStatistics()` returns `DriverStatistics`, cumulative since creation across all connections:
- `RxBandwidth`/`TxBandwidth` (`BandwidthStatistics`, kbit/s):
  - `Current` is the last full second; `Mean` is lifetime.
  - `Minimum`/`Maximum` are over any complete 1 s window and read 0 until one second of data exists.
  - `MaximumBurst` is the peak within one driver update.
- `RxTotalBytes`/`TxTotalBytes`, `RxTotalPackets`/`TxTotalPackets`.
- `RxPacketSizes`/`TxPacketSizes` (`PacketSizeStatistics`): buckets `SmallerThan128Bytes`, `Between128And255Bytes`, `Between256And511Bytes`, `Between512And1023Bytes`, `LargerThan1023Bytes`, plus `Minimum`/`Maximum`/`Mean`/`StandardDeviation`.
- `RxMeanQueueUsage`/`TxMeanQueueUsage` and `RxMaximumQueueUsage`/`TxMaximumQueueUsage`, in packets. A peak near the capacity explains `NetworkSendQueueFull`.

Packet sizes include IP and UDP/TCP headers but exclude link-layer headers and padding, so they will not match a capture byte-for-byte. For WebSocket the TCP header is assumed to be 32 bytes. Only a custom `INetworkInterface` reports exact sizes.

`driver.GetConnectionStatistics(conn)` returns `ConnectionStatistics`, valid only in `Connected`, cumulative per connection:
- `Latency` (RTT in ms): `Current`, `SmoothedCurrent`, `Mean`, `Minimum`, `Maximum`, `StandardDeviation`.
- `PacketLossPercent`, `PacketDuplicationPercent`, `PacketOutOfOrderPercent`.
- `Reliable` (`ReliableUtility.Statistics`) and `UnreliableSequenced` (`UnreliableSequencedPipelineStage.Statistics`).

`Latency` and `PacketDuplicationPercent` come only from `ReliableSequencedPipelineStage` pipelines. Loss and out-of-order come from reliable and unreliable-sequenced pipelines. A connection that sends only on a plain unreliable pipeline reports zero or meaningless latency, which does not mean zero latency.

## Logging

`WithLoggingParameters(driverName)` sets a `FixedString32Bytes` label, but the type is documented "Currently unused" in 6.6. It does not enable extra log output.
