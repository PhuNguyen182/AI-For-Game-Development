# Testing and Debugging

Pages (6.6): `testing/debugging`, logging, PlayMode Tool, Network Profiler, thin clients, gather metrics, source generators. Measurement rules: `csharp-standards` → `performance-and-algorithms.md` Verification.

## PlayMode Tool (Window → Multiplayer → PlayMode Tools)

| Field | Effect |
|---|---|
| PlayMode Type | `Client` / `Server` / `Client & Server`; drives World creation on Play |
| Num Thin Clients | N `ThinClientWorld`s for load |
| RTT Delay / Jitter (ms) | Symmetric delay and variance on client packets |
| Packet Drop (%) / Packet Fuzz (%) | Discard / simulated tampering of serialized data |

- Enabling emulation forces a real UDP socket even same-machine; disabled, client and server use IPC with zero RTT, jitter and loss, so it proves nothing about a real network.
- Use 50 / 150 / 500 ms (server-rewind guidance) to surface [prediction-caveats.md](prediction-caveats.md) cases.
- CLI presets: `--loadNetworkSimulatorJsonFile [path]`, `--createNetworkSimulatorJsonFile [path]` (default `NetworkSimulatorProfile.json`).

## Network Profiler (Window → Analysis → Profiler, or Window → Multiplayer → Network Profiler)
Needs Unity 6.0+ and `com.unity.netcode` 1.12.0+. The Client World and Server World modules are off by default; enable them before recording.

| Tab | Shows |
|---|---|
| Frame Overview | Bandwidth, packet and instance counts |
| Snapshot Overview | Per ghost type: size, % of snapshot, instances, compression efficiency, average size, overhead |
| Prediction and Interpolation | Prediction error (Client World only) |

A newly spawned ghost shows low compression efficiency until a baseline exists; not a steady-state number.

## Thin clients
`World.IsThinClient()` / `ThinClientSimulation`. No rendering, cannot spawn ghosts, minimal logic; for server load tests only. `AutoCommandTarget` does not work by default, so set `CommandTarget` manually.

## Logging
- `NetDebug` singleton levels `Debug` / `Notify` (default) / `Warning` / `Error` / `Exception`; configured via `NetCodeDebugConfig`.
- Packet dumps need an `EnablePacketLogging` component on the connection entity and the `NETCODE_DEBUG` define (`NETCODE_NDEBUG` force-disables). Log files are not auto-cleaned and grow large.

## Metrics API
Add components to the `GhostMetricsMonitor` singleton to opt in, then `SystemAPI.GetSingleton<T>()`: `NetworkMetrics`, `SnapshotMetrics`, `GhostMetrics` (by `GhostNames`), `GhostSerializationMetrics`, `PredictionErrorMetrics` (by `PredictionErrorNames`). Use for overlays or automated tests.

## Source generators
Serialization, RPC and command code is generated at compile time into `Temp/NetCodeGenerated` (cleared on close; never edit or commit). Assets → Multiplayer → Force Code Generation when a new `[GhostField]` or template is not picked up ([ghost-serialization-templates.md](ghost-serialization-templates.md)).
