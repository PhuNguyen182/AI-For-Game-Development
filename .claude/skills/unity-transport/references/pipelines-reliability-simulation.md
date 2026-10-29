# Pipelines, reliability, simulation

Sources (`@6.6`): manual `pipelines-usage`; API `NetworkPipeline`, `NetworkPipelineStage`, `FragmentationPipelineStage`, `ReliableSequencedPipelineStage`, `UnreliableSequencedPipelineStage`, `SimulatorPipelineStage`, `Utilities.*Utility.Parameters`, `NetworkSimulatorParameter`, `PacketProcessor`, `PacketsQueue`.

## Building a pipeline

- `driver.CreatePipeline(params Type[])` builds an ordered stage stack. Order is processing order on send and the reverse on receive. Configure identically on client and server or packets are misread.
- `NetworkPipeline.Null` is the built-in no-op pipeline.
- `FragmentationPipelineStage` goes first: no other stage handles packets over the ~1400-byte MTU, and an earlier stage mishandles them silently. Putting it after Reliable makes the reliability header wrap the whole message, not each fragment, wasting bandwidth.
- `SimulatorPipelineStage` goes last, so other stages see the packet before conditions are simulated.
- Set stage parameters on `NetworkSettings` before `NetworkDriver.Create`.

```csharp
var settings = new NetworkSettings();
settings.WithFragmentationStageParameters(payloadCapacity: 10000);
settings.WithReliableStageParameters(windowSize: 64);
#if UNITY_EDITOR || DEVELOPMENT_BUILD
settings.WithSimulatorStageParameters(maxPacketCount: 100, packetDelayMs: 50, packetDropPercentage: 3);
#endif
using var driver = NetworkDriver.Create(settings);
#if UNITY_EDITOR || DEVELOPMENT_BUILD
var pipeline = driver.CreatePipeline(typeof(FragmentationPipelineStage), typeof(ReliableSequencedPipelineStage), typeof(SimulatorPipelineStage));
#else
var pipeline = driver.CreatePipeline(typeof(FragmentationPipelineStage), typeof(ReliableSequencedPipelineStage));
#endif
```

## Stages

| Stage | Use |
|---|---|
| `FragmentationPipelineStage` | A send may exceed the path MTU. It splits and reassembles. |
| `ReliableSequencedPipelineStage` | Delivery plus order (RPCs, one-shot events). Resends like TCP. A lost packet blocks every later packet on that pipeline until delivered. Not for snapshot state a newer packet supersedes. |
| `UnreliableSequencedPipelineStage` | Order without delivery: out-of-order or duplicate packets are culled, never resent. Use for position snapshots. |
| `SimulatorPipelineStage` | Test-only artificial loss, delay, jitter, duplication, bit-fuzzing. |
| `NullPipelineStage` | Passthrough that gives a message group its own pipeline ("channel") at no cost. |

## Reliable and fragmentation parameters

- `WithReliableStageParameters(windowSize: 32, minimumResendTime: 64, maximumResendTime: 200)` (defaults shown, times in ms).
- `WindowSize` caps unacknowledged in-flight packets per connection and pipeline. Default 32, commonly 64, hard max 2040. Above 64 it must be a multiple of 8. Exceeding it returns `NetworkSendQueueFull`.
- `ReliableUtility.SetMinimumResendTime`/`SetMaximumResendTime(int, driver, pipeline, connection)` retunes one live connection.
- `WithFragmentationStageParameters(payloadCapacity: 4096)`: `PayloadCapacity` is the largest splittable message. Beyond the maximum (~20 MB unreliable, ~88 KB with the reliable stage) a send returns `NetworkPacketOverflow`.
- Telemetry types: `ReliableUtility.Statistics`, `ReliableUtility.RTTInfo` (`LastRtt`, `SmoothedRtt`, `SmoothedVariance`, `ResendTimeout`), `UnreliableSequencedPipelineStage.Statistics`.
- Counters: `ReliableUtility.Statistics` has `PacketsSent`, `PacketsReceived`, `PacketsResent`, `PacketsDropped`, `PacketsStale`, `PacketsDuplicated`, `PacketsOutOfOrder`, `AcksReceived`, `AcksSent`. `UnreliableSequencedPipelineStage.Statistics` has `NumPacketsSent`, `NumPacketsReceived`, `NumPacketsCulledOutOfOrder`, `NumPacketsDroppedNeverArrived`.

## Simulating network conditions

Two independent mechanisms, configured differently. Pick one deliberately.

Per-pipeline: add `SimulatorPipelineStage` to `CreatePipeline`, set with `WithSimulatorStageParameters(maxPacketCount, maxPacketSize = 1472, mode = ApplyMode.AllPackets, packetDelayMs, packetJitterMs, packetDropInterval, packetDropPercentage, packetDuplicationPercentage, fuzzFactor, fuzzOffset, randomSeed)`. All except `maxPacketCount` (required) default to 0.

- Packets over `maxPacketSize` bypass the simulator.
- `packetDropInterval` drops every Nth packet; `packetDropPercentage` is random.
- `fuzzFactor` is the percentage of packets fuzzed and the per-bit flip probability; `fuzzOffset` is the start byte.
- `randomSeed` makes runs reproducible.
- `ApplyMode`: `AllPackets`, `SentPacketsOnly`, `ReceivedPacketsOnly`, `Off` (toggle at runtime without removing the stage).
- `ModifySimulatorStageParameters` retunes live; `maxPacketCount` and `maxPacketSize` cannot change.
- Manual guidance: delay ~20 ms for good broadband up to ~200 ms for poor mobile; jitter at most about half the delay; drop rarely above 3%.

Driver-global (no pipeline stage): `WithNetworkSimulatorParameters(...)` before `Create`, `ModifyNetworkSimulatorParameters(driver, p)` live. Fields: `ReceivePacketLossPercent`, `SendPacketLossPercent`, `SendDelayMS`, `SendJitterMS`, `SendDuplicatePercent`, `ReceiveMtu`. All default 0.

Either mechanism left in a release build degrades every real player's connection: gate with `UNITY_EDITOR`/`DEVELOPMENT_BUILD` or an equivalent dev flag.

## Custom stage (low-level)

Only when no built-in stage fits.

- Implement `INetworkPipelineStage`: `StaticSize` (storage shared by all instances of the type) and `StaticInitialize(byte*, int, NetworkSettings)`, which returns a populated `NetworkPipelineStage`.
- Build it with capacities (`ReceiveCapacity`, `SendCapacity`, `HeaderCapacity`, `SharedStateCapacity`, `PayloadCapacity`) plus `Receive`, `Send`, `InitializeConnection` function pointers. Wrap each with `TransportFunctionPointer<T>` (Burst-compatible).
- Each call gets `ref NetworkPipelineContext`: stage buffers, a writable `header`, `maxMessageSize` (path MTU), `timestamp`.
- It returns a `NetworkPipelineStage.Requests` flag: `None`, `Resume` (run again now), `Update` (receive next update), `SendUpdate` (send next update), `Error`.
- `NetworkPipelineStageId.Get<T>()` identifies a stage type. Register with `driver.RegisterPipelineStage<T>` before `Bind()`.
- Packet access uses `PacketProcessor`:
  - Geometry: `Length`, `Capacity`, `Offset`, `BytesAvailableAtStart`/`BytesAvailableAtEnd`, `EndpointRef` (sender on receive, destination on send).
  - `AppendToPayload`/`PrependToPayload<T>` grow it.
  - `GetPayloadDataRef<T>`/`GetUnsafePayloadPtr` access in place.
  - `CopyPayload` peeks at the front and leaves the data.
  - `RemoveFromPayloadStart` copies out and removes, e.g. to strip a header.
  - `Drop()` sets length 0 but keeps the queue slot.
- `PacketsQueue` indexes by `this[int]`.
  - `EnqueuePacket(out PacketProcessor)` returns false when the preallocated pool is exhausted.
  - `EnqueuePackets(ref PacketsQueue)` silently drops what does not fit.
  - `Clear()`, `Dispose()`.
- A custom network interface's receive/send jobs get `ReceiveJobArguments` (`ReceiveQueue`, `ReceiveResult`, `Time`) and `SendJobArguments` (`SendQueue`, `Time`).
