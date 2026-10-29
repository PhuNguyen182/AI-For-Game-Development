# Core driver lifecycle

Sources (`@6.6`): manual `client-server-simple`; API `NetworkDriver`, `NetworkConnection`, `NetworkEndpoint`, `NetworkSettings`, `NetworkConfigParameter`, `INetworkInterface`, `IPCNetworkInterface`.

## Package

- `com.unity.transport@6.6` needs Unity 2022.3+.
- Samples tab: `SimpleClientServer` is the loop below; `JobifiedClientServer` and `Ping` are the jobified path; `RelayPing` is the Relay path.

## Driver

- `NetworkDriver.Create()` uses `UDPNetworkInterface` and default settings.
- `Create(NetworkSettings)` sets timeouts and queue sizes.
- `Create<N>(N[, settings])` swaps the medium: `IPCNetworkInterface` or a custom `INetworkInterface`. Pass a managed `INetworkInterface` straight in; `WrapToUnmanaged<T>()` and `NetworkInterfaceUnmanagedWrapper<T>` are `[Obsolete]`.
- A plain `NetworkDriver` is not thread-safe. Use it only on the main thread, never from a `Task`/`Thread`. The thread-safe path is `ToConcurrent()` in a job (`jobs-and-concurrent-api.md`).
- `RegisterPipelineStage<T>` (custom stage) must run before the first `Bind()`.

## NetworkSettings

- `new NetworkSettings(Allocator)` defaults to `Temp`; use `Persistent` if it outlives the frame. It owns native memory: `Dispose()` it.
- `WithNetworkConfigParameters(...)` sets the block below. Other `With...Parameters` extensions (Relay, secure, WebSocket, simulator, fragmentation, reliable) are in their own references.
- `AddRawParameterStruct<T>` keeps one block per `T` and throws `ArgumentException` if `T.Validate()` fails (collection checks on).

`NetworkConfigParameter` defaults:

| Field | Default | Meaning |
|---|---|---|
| `connectTimeoutMS` | 1000 | Time between connect attempts |
| `maxConnectAttempts` | 60 | Attempts before a `Disconnect` event for a never-established connection |
| `disconnectTimeoutMS` | 30000 | Inactivity before drop; 0 disables |
| `heartbeatTimeoutMS` | 500 | Idle time before keep-alive; 0 disables |
| `reconnectionTimeoutMS` | 2000 | Window to re-establish after contact loss (e.g. DTLS client IP roaming) |
| `maxFrameTimeMS` / `fixedFrameTimeMS` | 0 / 0 | Cap per-frame timeout advance for debugging / fixed time for deterministic tests |
| `receiveQueueCapacity` / `sendQueueCapacity` | 512 / 512 | Packets, shared across all connections: size for max packets per update |
| `maxMessageSize` | 1400 (MTU) | Largest packet, transport headers included |
| `performPathMtuDiscovery` | false | MTU discovery in the handshake |

## Endpoints

- `AnyIpv4`/`AnyIpv6` is the server bind address; `LoopbackIpv4`/`LoopbackIpv6` is same-machine. `.WithPort(ushort)` returns a copy.
- `Parse` throws on malformed input: trusted hardcoded values only. `TryParse` for user-typed IP/port.
- UTP does not resolve hostnames: `Parse`/`TryParse` take literal IPs. Resolve elsewhere first.
- `NetworkEndpoint.TransferrableData` carries raw address bytes across a job/thread boundary.

## Bind, Listen, Connect

- `Bind` returns 0 on success; a failed bind is otherwise silent. Gate `Listen()` on it: `if (driver.Bind(ep) != 0) return; driver.Listen();`.
- `Accept()` returns one pending connection per call: loop `while ((c = driver.Accept()) != default)`.
- `Connect(NetworkEndpoint)` (or `Connect(FixedString512Bytes, ushort)`) binds implicitly.
- `Disconnect(conn)` closes locally; the peer learns only when a `ScheduleUpdate` ships the notification. `connection.Close` and `connection.Disconnect` are identical.
- `SetAcceptPayload` is sent when the request arrives, not when `Accept()` is called: set it before then.
- Send is two-phase: `BeginSend` returns a writer, `EndSend` enqueues it (hits the wire at the next `ScheduleFlushSend`/`ScheduleUpdate`), `AbortSend` cancels.

## Connection state

- `connection.IsCreated` is true only for a handle from `Accept()`/`Connect()`; a dropped slot is reset to `default`, so check it for connections stored across frames.
- `connection.GetState(driver)` equals `driver.GetConnectionState(conn)`.
- States: `Connecting` (handshake; no sending yet; next event is `Connect` or `Disconnect`), `Connected`, `Disconnected` (no more events ever).
- A client with one connection pumps with `connection.PopEvent(driver, out stream)`; a server uses `driver.PopEventForConnection`.

## Per-frame loop

Each frame: `ScheduleUpdate().Complete()`, then drain events. Skipping it leaves events queued and can miss a timeout or disconnect.

```csharp
void Update()
{
    driver.ScheduleUpdate().Complete();
    for (int i = 0; i < connections.Length; i++)
        if (!connections[i].IsCreated) { connections.RemoveAtSwapBack(i); i--; }

    NetworkConnection c;
    while ((c = driver.Accept()) != default) connections.Add(c);

    for (int i = 0; i < connections.Length; i++)
    {
        NetworkEvent.Type cmd;
        while ((cmd = driver.PopEventForConnection(connections[i], out var stream)) != NetworkEvent.Type.Empty)
        {
            if (cmd == NetworkEvent.Type.Data)
            {
                uint v = stream.ReadUInt();
                driver.BeginSend(NetworkPipeline.Null, connections[i], out var w);
                w.WriteUInt(v);
                driver.EndSend(w);
            }
            else if (cmd == NetworkEvent.Type.Disconnect) { connections[i] = default; break; }
        }
    }
}

void OnDestroy()
{
    if (driver.IsCreated) { driver.Dispose(); connections.Dispose(); }
}
```

Dispose the driver and every `Native*` it owns on shutdown; `IsCreated` stops a double dispose.

## Events

`NetworkEvent.Type`:

- `Empty`: no more events; ends every pop loop.
- `Connect`: handshake done; sending allowed. Servers see new connections via `Accept()` instead.
- `Data`: read the returned `DataStreamReader`.
- `Disconnect`: closed or never established; the reader holds one byte mapping to `DisconnectReason` (`diagnostics-and-testing.md`).

## Interfaces

- `UDPNetworkInterface`: default on standalone; not available on WebGL (`webgl-and-ngo-integration.md`).
- `IPCNetworkInterface`: in-process, instant, loopback addresses only; give each driver in the process a distinct port.
- Custom `INetworkInterface`: `LocalEndpoint`, `Bind`, `Listen`, `Initialize`, `ScheduleReceive`, `ScheduleSend`, `IDisposable`. Its `NetworkEndpoint` uses `NetworkFamily.Custom`.
- `OperationResult` is a struct with an `ErrorCode` (0 = success); errors surface via `NetworkDriver.ReceiveErrorCode`.
- A custom `INetworkParameter` implements `Validate()`.
- Pipeline-stage buffers: `InboundRecvBuffer` (`byte*` + length, `Slice`), `InboundSendBuffer` (payload, plus `bufferWithHeaders` and `headerPadding`).
