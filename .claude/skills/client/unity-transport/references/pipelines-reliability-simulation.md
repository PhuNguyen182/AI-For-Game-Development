# Pipelines, Reliability & Simulation — NetworkPipeline and Its Stages

Sources:
[Using pipelines](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/pipelines-usage.html),
[NetworkPipeline](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkPipeline.html),
[NetworkPipelineContext](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkPipelineContext.html),
[NetworkPipelineStage](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkPipelineStage.html),
[NetworkPipelineStage.InitializeConnectionDelegate](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkPipelineStage.InitializeConnectionDelegate.html),
[NetworkPipelineStage.ReceiveDelegate](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkPipelineStage.ReceiveDelegate.html),
[NetworkPipelineStage.Requests](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkPipelineStage.Requests.html),
[NetworkPipelineStage.SendDelegate](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkPipelineStage.SendDelegate.html),
[NetworkPipelineStageId](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkPipelineStageId.html),
[INetworkPipelineStage](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.INetworkPipelineStage.html),
[FragmentationPipelineStage](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.FragmentationPipelineStage.html),
[ReliableSequencedPipelineStage](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.ReliableSequencedPipelineStage.html),
[UnreliableSequencedPipelineStage](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.UnreliableSequencedPipelineStage.html),
[UnreliableSequencedPipelineStage.SequenceId](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.UnreliableSequencedPipelineStage.SequenceId.html),
[UnreliableSequencedPipelineStage.Statistics](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.UnreliableSequencedPipelineStage.Statistics.html),
[SimulatorPipelineStage](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.SimulatorPipelineStage.html),
[NullPipelineStage](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NullPipelineStage.html),
[PacketProcessor](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.PacketProcessor.html),
[PacketsQueue](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.PacketsQueue.html),
[ReceiveJobArguments](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.ReceiveJobArguments.html),
[SendJobArguments](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.SendJobArguments.html),
[TransportFunctionPointer\<T\>](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.TransportFunctionPointer-1.html),
[NetworkSimulatorParameter](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkSimulatorParameter.html),
[NetworkSimulatorParameterExtensions](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkSimulatorParameterExtensions.html),
[Utilities.ApplyMode](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Utilities.ApplyMode.html),
[Utilities.FragmentationStageParameterExtensions](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Utilities.FragmentationStageParameterExtensions.html),
[Utilities.FragmentationUtility](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Utilities.FragmentationUtility.html),
[Utilities.FragmentationUtility.Parameters](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Utilities.FragmentationUtility.Parameters.html),
[Utilities.ReliableStageParameterExtensions](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Utilities.ReliableStageParameterExtensions.html),
[Utilities.ReliableUtility](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Utilities.ReliableUtility.html),
[Utilities.ReliableUtility.Parameters](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Utilities.ReliableUtility.Parameters.html),
[Utilities.ReliableUtility.RTTInfo](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Utilities.ReliableUtility.RTTInfo.html),
[Utilities.ReliableUtility.SharedContext](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Utilities.ReliableUtility.SharedContext.html),
[Utilities.ReliableUtility.Statistics](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Utilities.ReliableUtility.Statistics.html),
[Utilities.SimulatorStageParameterExtensions](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Utilities.SimulatorStageParameterExtensions.html),
[Utilities.SimulatorUtility](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Utilities.SimulatorUtility.html),
[Utilities.SimulatorUtility.Parameters](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Utilities.SimulatorUtility.Parameters.html).
Covers: SKILL.md §4 — **"Assemble the NetworkPipeline from stages the data actually needs, not by habit"**, **"Gate SimulatorPipelineStage behind an Editor or dev-build check"**.

This file owns `NetworkPipeline` construction, delivery-guarantee and fragmentation stage selection, and network-condition simulation for testing. The `NetworkDriver`/connection lifecycle that actually creates a pipeline (`CreatePipeline`, `Bind`/`Listen`/`Connect`, the per-frame update loop) lives in [core-driver-lifecycle.md](core-driver-lifecycle.md); moving pipeline sends/receives into Burst jobs via the `Concurrent` API lives in [jobs-and-concurrent-api.md](jobs-and-concurrent-api.md).

## Table of contents
- [Building a pipeline](#building-a-pipeline)
- [Built-in pipeline stages](#built-in-pipeline-stages)
- [Reliable delivery and fragmentation](#reliable-delivery-and-fragmentation)
- [Simulating network conditions for testing](#simulating-network-conditions-for-testing)
- [Packet-level plumbing](#packet-level-plumbing)
- [Authoring a custom pipeline stage (low-level API)](#authoring-a-custom-pipeline-stage-low-level-api)

## Building a pipeline

A `NetworkPipeline` is a named, ordered stack of stages layered on top of UTP's raw unreliable datagrams. `NetworkDriver.CreatePipeline(params Type[])` (owned by [core-driver-lifecycle.md](core-driver-lifecycle.md)) builds one from a `Type[]` list — that list's order is the processing order on send, and the *reverse* order on receive, so every stage sees output only from the stages before it. Pipelines must be configured identically on client and server, since a mismatched stage list on either side desyncs how packets get interpreted.

| Subject | What it decides | Source |
|---|---|---|
| `NetworkPipeline` | The identifier returned by `CreatePipeline`; `NetworkPipeline.Null` is the built-in default pipeline and acts as a no-op passthrough — pass it to skip every stage. | [NetworkPipeline](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkPipeline.html) |
| Stage order in `CreatePipeline` | `FragmentationPipelineStage` should normally be **first** in the chain, since no other stage supports packets larger than the ~1400-byte MTU. `SimulatorPipelineStage` should normally be **last**, so every other stage has already processed a packet before conditions get simulated on it. Reversing Fragmentation and Reliable order means the reliability header only wraps the whole unfragmented message instead of each fragment, wasting bandwidth. | [Using pipelines](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/pipelines-usage.html) |

```csharp
// Fragmentation must run first so no later stage ever sees an over-MTU
// packet; the dev-only Simulator stage must run last so every other stage
// has already processed the packet before it gets delayed or dropped.
var settings = new NetworkSettings();
settings.WithFragmentationStageParameters(payloadCapacity: 10000);
settings.WithReliableStageParameters(windowSize: 64);

#if UNITY_EDITOR || DEVELOPMENT_BUILD
settings.WithSimulatorStageParameters(
    maxPacketCount: 100,
    packetDelayMs: 50,
    packetDropPercentage: 3);
#endif

using var driver = NetworkDriver.Create(settings);

#if UNITY_EDITOR || DEVELOPMENT_BUILD
var pipeline = driver.CreatePipeline(
    typeof(FragmentationPipelineStage),
    typeof(ReliableSequencedPipelineStage),
    typeof(SimulatorPipelineStage));
#else
var pipeline = driver.CreatePipeline(
    typeof(FragmentationPipelineStage),
    typeof(ReliableSequencedPipelineStage));
#endif
```

**Critical caveat**: stage order in `CreatePipeline` is not a style preference — swapping `FragmentationPipelineStage` to after `ReliableSequencedPipelineStage` changes what the reliability header wraps, and any stage placed before Fragmentation that doesn't understand over-MTU packets will mishandle them silently rather than raise an error.

## Built-in pipeline stages

Pick stages by what the payload actually needs — order and delivery guarantee, per SKILL.md §4 — never default every send to the reliable pipeline.

| Subject | What it decides | Source |
|---|---|---|
| `FragmentationPipelineStage` | Splits a payload larger than the ~1400-byte MTU into multiple packets and reassembles them on receive. Add it whenever a single send may exceed the path MTU; size limits are configured through `FragmentationUtility.Parameters` below. | [FragmentationPipelineStage](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.FragmentationPipelineStage.html) |
| `ReliableSequencedPipelineStage` | Guarantees delivery and in-order arrival, resending unacknowledged packets like TCP. Head-of-line blocking applies: a lost packet blocks every later packet on that pipeline until it is resent and delivered. Use only for traffic that genuinely needs order and delivery (RPCs, one-shot events) — not for snapshot-style state that a newer packet will supersede anyway. | [ReliableSequencedPipelineStage](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.ReliableSequencedPipelineStage.html) |
| `UnreliableSequencedPipelineStage` | Enforces ordering without delivery guarantees — an out-of-order or duplicate packet is silently culled, never resent. Pick this over Reliable when a newer update should simply supersede a dropped one (position snapshots) instead of blocking on retransmission. | [UnreliableSequencedPipelineStage](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.UnreliableSequencedPipelineStage.html) |
| `SimulatorPipelineStage` | Injects artificial packet loss, delay, jitter, duplication, and bit-fuzzing into the traffic passing through it, for testing under conditions closer to a real network. Configured via `SimulatorUtility.Parameters` (see below) — test-only, never production. | [SimulatorPipelineStage](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.SimulatorPipelineStage.html) |
| `NullPipelineStage` | Does nothing — a passthrough placeholder used only to give one group of message types its own distinct pipeline/"channel", separate from other traffic on the same connection, without adding any processing overhead. | [NullPipelineStage](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NullPipelineStage.html) |

| Type | Source |
|---|---|
| `UnreliableSequencedPipelineStage.SequenceId` | [UnreliableSequencedPipelineStage.SequenceId](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.UnreliableSequencedPipelineStage.SequenceId.html) |
| `UnreliableSequencedPipelineStage.Statistics` — `NumPacketsCulledOutOfOrder`, `NumPacketsDroppedNeverArrived`, `NumPacketsReceived`, `NumPacketsSent` | [UnreliableSequencedPipelineStage.Statistics](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.UnreliableSequencedPipelineStage.Statistics.html) |

## Reliable delivery and fragmentation

| Subject | What it decides | Source |
|---|---|---|
| `ReliableUtility.Parameters.WindowSize` | Caps in-flight unacknowledged packets per connection+pipeline; default 32, commonly raised to 64, with a hard technical ceiling of 2040 — any value above 64 must be a multiple of 8. Exceeding the window returns `NetworkSendQueueFull`. | [Utilities.ReliableUtility.Parameters](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Utilities.ReliableUtility.Parameters.html), [ReliableSequencedPipelineStage](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.ReliableSequencedPipelineStage.html) |
| `ReliableUtility.Parameters.MinimumResendTime` | Minimum time to wait before resending an unacknowledged reliable packet; default 64 ms. | [Utilities.ReliableUtility.Parameters](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Utilities.ReliableUtility.Parameters.html) |
| `ReliableUtility.Parameters.MaximumResendTime` | Maximum time to wait before resending an unacknowledged reliable packet; default 200 ms. | [Utilities.ReliableUtility.Parameters](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Utilities.ReliableUtility.Parameters.html) |
| `ReliableStageParameterExtensions.WithReliableStageParameters` | `NetworkSettings` extension that sets `ReliableUtility.Parameters`: `WithReliableStageParameters(windowSize: 32, minimumResendTime: 64, maximumResendTime: 200)`. Call before `NetworkDriver.Create` so the stage picks the values up at `StaticInitialize`. | [Utilities.ReliableStageParameterExtensions](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Utilities.ReliableStageParameterExtensions.html) |
| `ReliableUtility` (static) | Exposes `DefaultMinimumResendTime` = 64 ms / `DefaultMaximumResendTime` = 200 ms constants, plus `SetMinimumResendTime`/`SetMaximumResendTime(int, NetworkDriver, NetworkPipeline, NetworkConnection)` to retune resend timing on one live connection without recreating the driver. | [Utilities.ReliableUtility](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Utilities.ReliableUtility.html) |
| `FragmentationUtility.Parameters` | `PayloadCapacity` is the largest message `FragmentationPipelineStage` can split (extension default 4096 bytes). Sending beyond the maximum (~20 MB unreliable, ~88 KB when combined with the reliable stage) returns `NetworkPacketOverflow` instead of fragmenting further. | [Utilities.FragmentationUtility.Parameters](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Utilities.FragmentationUtility.Parameters.html) |
| `FragmentationStageParameterExtensions.WithFragmentationStageParameters` | `NetworkSettings` extension that sets `FragmentationUtility.Parameters`: `WithFragmentationStageParameters(payloadCapacity: 4096)`. | [Utilities.FragmentationStageParameterExtensions](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Utilities.FragmentationStageParameterExtensions.html) |
| `FragmentationUtility` (static) | Namespace container for the fragmentation stage's types — the fetched page lists no members of its own beyond the nested `Parameters` struct above; a thin stub page. | [Utilities.FragmentationUtility](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Utilities.FragmentationUtility.html) |

Internal telemetry the reliable stage maintains but that doesn't itself settle a configuration choice:

| Type | Source |
|---|---|
| `ReliableUtility.Statistics` — `PacketsResent`, `PacketsDropped`, `PacketsSent`, `PacketsReceived`, `PacketsStale`, `PacketsDuplicated`, `PacketsOutOfOrder`, `AcksReceived`, `AcksSent` | [Utilities.ReliableUtility.Statistics](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Utilities.ReliableUtility.Statistics.html) |
| `ReliableUtility.RTTInfo` — `LastRtt`, `SmoothedRtt`, `SmoothedVariance`, `ResendTimeout` (all ms) | [Utilities.ReliableUtility.RTTInfo](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Utilities.ReliableUtility.RTTInfo.html) |
| `ReliableUtility.SharedContext` — effective `WindowSize`/`MinimumResendTime`/`MaximumResendTime`, `RttInfo`, `stats` shared between the stage's send and receive direction | [Utilities.ReliableUtility.SharedContext](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Utilities.ReliableUtility.SharedContext.html) |

## Simulating network conditions for testing

UTP has **two independent** ways to inject artificial packet loss/delay/jitter, and they don't compose through the same knob — pick one deliberately rather than assuming they're the same mechanism:

| Subject | What it decides | Source |
|---|---|---|
| `SimulatorUtility.Parameters.MaxPacketCount` | Maximum number of packets the simulator stage tracks at once; no default — a required argument to `WithSimulatorStageParameters`. Part of the per-pipeline mechanism: requires explicitly adding `SimulatorPipelineStage` to a pipeline's `CreatePipeline` stage list. | [Utilities.SimulatorUtility.Parameters](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Utilities.SimulatorUtility.Parameters.html) |
| `SimulatorUtility.Parameters.MaxPacketSize` | Packets larger than this bypass the simulator entirely instead of being delayed/dropped; default 1472 bytes. | [Utilities.SimulatorUtility.Parameters](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Utilities.SimulatorUtility.Parameters.html) |
| `SimulatorUtility.Parameters.PacketDelayMs` | Fixed delay applied to every packet that passes through; default 0 ms. Manual guidance: ~20 ms for good broadband, up to ~200 ms for poor mobile. | [Utilities.SimulatorUtility.Parameters](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Utilities.SimulatorUtility.Parameters.html), [Using pipelines](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/pipelines-usage.html) |
| `SimulatorUtility.Parameters.PacketJitterMs` | Random variance added on top of `PacketDelayMs`; default 0 ms. Manual guidance: roughly half the delay value or less. | [Utilities.SimulatorUtility.Parameters](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Utilities.SimulatorUtility.Parameters.html), [Using pipelines](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/pipelines-usage.html) |
| `SimulatorUtility.Parameters.PacketDropInterval` | Drops every Nth packet on a fixed interval instead of at random; default 0 (disabled). | [Utilities.SimulatorUtility.Parameters](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Utilities.SimulatorUtility.Parameters.html) |
| `SimulatorUtility.Parameters.PacketDropPercentage` | Percentage (0–100) of packets dropped at random; default 0. Manual guidance: rarely above 3% even for poor mobile. | [Utilities.SimulatorUtility.Parameters](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Utilities.SimulatorUtility.Parameters.html), [Using pipelines](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/pipelines-usage.html) |
| `SimulatorUtility.Parameters.PacketDuplicationPercentage` | Percentage (0–100) of packets duplicated; default 0. | [Utilities.SimulatorUtility.Parameters](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Utilities.SimulatorUtility.Parameters.html) |
| `SimulatorUtility.Parameters.FuzzFactor` / `FuzzOffset` | `FuzzFactor` is the percentage (0–100) of packets fuzzed and the per-bit flip probability; `FuzzOffset` is the byte offset inside the packet where fuzzing starts. Both default 0. | [Utilities.SimulatorUtility.Parameters](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Utilities.SimulatorUtility.Parameters.html) |
| `SimulatorUtility.Parameters.RandomSeed` | Seeds the simulator's random number generator, for reproducible test runs. | [Utilities.SimulatorUtility.Parameters](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Utilities.SimulatorUtility.Parameters.html) |
| `SimulatorStageParameterExtensions.WithSimulatorStageParameters` | `NetworkSettings` extension: `WithSimulatorStageParameters(maxPacketCount, maxPacketSize = 1472, mode = ApplyMode.AllPackets, packetDelayMs = 0, packetJitterMs = 0, packetDropInterval = 0, packetDropPercentage = 0, packetDuplicationPercentage = 0, fuzzFactor = 0, fuzzOffset = 0, randomSeed = 0)`. | [Utilities.SimulatorStageParameterExtensions](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Utilities.SimulatorStageParameterExtensions.html) |
| `SimulatorStageParameterExtensions.ModifySimulatorStageParameters` | Retunes a live driver's simulator stage parameters at runtime; `maxPacketCount`/`maxPacketSize` cannot change and must be passed back unmodified. | [Utilities.SimulatorStageParameterExtensions](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Utilities.SimulatorStageParameterExtensions.html) |
| `Utilities.ApplyMode` | Picks simulation direction: `AllPackets`, `SentPacketsOnly`, `ReceivedPacketsOnly`, or `Off` (used for toggling the simulator on/off at runtime without removing the stage). | [Utilities.ApplyMode](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Utilities.ApplyMode.html) |
| `SimulatorUtility` (static) | Namespace container for the simulator stage's types — the fetched page lists no members of its own beyond the nested `Parameters` struct above; a thin stub page, same as `FragmentationUtility`. | [Utilities.SimulatorUtility](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.Utilities.SimulatorUtility.html) |
| `NetworkSimulatorParameter.ReceivePacketLossPercent` / `.SendPacketLossPercent` | Percentage (0–100) of received/sent packets to drop, applied **globally to the driver — no pipeline stage needed**; both default 0 via the extension. | [NetworkSimulatorParameter](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkSimulatorParameter.html) |
| `NetworkSimulatorParameter.SendDelayMS` / `.SendJitterMS` | Fixed delay and delay variance the global simulator applies to every packet the driver sends; both default 0. | [NetworkSimulatorParameter](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkSimulatorParameter.html) |
| `NetworkSimulatorParameter.SendDuplicatePercent` | Percentage (0–100) of sent packets the global simulator duplicates; default 0. | [NetworkSimulatorParameter](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkSimulatorParameter.html) |
| `NetworkSimulatorParameter.ReceiveMtu` | Maximum packet length the global simulator processes on receive; default 0 via the extension. | [NetworkSimulatorParameter](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkSimulatorParameter.html) |
| `NetworkSimulatorParameterExtensions` | `WithNetworkSimulatorParameters(...)` sets `NetworkSimulatorParameter` in `NetworkSettings` before `NetworkDriver.Create`; `ModifyNetworkSimulatorParameters(NetworkDriver, NetworkSimulatorParameter)` retunes the global simulator live. | [NetworkSimulatorParameterExtensions](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkSimulatorParameterExtensions.html) |

**Critical caveat**: both mechanisms are test-only. Whether it's `SimulatorPipelineStage` in a pipeline's stage list or `NetworkSimulatorParameter` applied to the driver, gate it behind `UNITY_EDITOR`/`DEVELOPMENT_BUILD` (or an equivalent dev-only flag), per SKILL.md §4. Either one left wired into a release build injects artificial packet loss, delay, and jitter into every real player's connection.

## Packet-level plumbing

`PacketProcessor` and `PacketsQueue` are the low-level API a custom `NetworkInterface` or pipeline stage uses to read and mutate packet bytes directly — most feature work never touches these, since the driver and built-in stages already use them internally.

| Subject | What it decides | Source |
|---|---|---|
| `PacketProcessor.Length` / `.Capacity` / `.Offset` | Slice geometry: `Length` is the packet's current data size, `Capacity` the buffer size backing it, `Offset` where the packet's first byte sits inside that buffer. | [PacketProcessor](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.PacketProcessor.html) |
| `PacketProcessor.BytesAvailableAtStart` / `.BytesAvailableAtEnd` | Free space before/after the packet's current data inside its buffer — how much a `Prepend`/`Append` call can add before the buffer is full. | [PacketProcessor](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.PacketProcessor.html) |
| `PacketProcessor.EndpointRef` | The packet's remote endpoint — the sender for a packet in the receive queue, the destination for a packet in the send queue. | [PacketProcessor](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.PacketProcessor.html) |
| `PacketProcessor.IsCreated` | Whether this `PacketProcessor` was actually obtained from a valid `PacketsQueue`, as opposed to a default/uninitialized value. | [PacketProcessor](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.PacketProcessor.html) |
| `PacketProcessor.AppendToPayload` / `.PrependToPayload<T>` | Grow the packet by copying bytes or a value onto the end or the start of its payload. | [PacketProcessor](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.PacketProcessor.html) |
| `PacketProcessor.GetPayloadDataRef<T>` / `.GetUnsafePayloadPtr` | Read or write the packet's payload in place, reinterpreted as `T` or accessed as a raw pointer. | [PacketProcessor](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.PacketProcessor.html) |
| `PacketProcessor.CopyPayload` | Fills the caller's buffer with the data at the start of the payload, leaving that data in the packet — use this to peek at a header without consuming it. | [PacketProcessor](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.PacketProcessor.html) |
| `PacketProcessor.RemoveFromPayloadStart` | Copies out **and removes** bytes from the front of the payload — e.g. stripping a header before handing the rest on. Use this instead of `CopyPayload` when the consumed bytes should not remain in the packet. | [PacketProcessor](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.PacketProcessor.html) |
| `PacketProcessor.Drop()` | Discards the packet by setting its length to 0, without removing its slot from the queue. | [PacketProcessor](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.PacketProcessor.html) |
| `PacketsQueue.Count` / `.Capacity` / `.IsCreated` | How many packets are currently queued, how many the queue can hold, and whether the queue instance is valid. | [PacketsQueue](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.PacketsQueue.html) |
| `PacketsQueue.this[int]` | Indexes into the queue, returning the `PacketProcessor` for the packet at that position. | [PacketsQueue](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.PacketsQueue.html) |
| `PacketsQueue.EnqueuePacket(out PacketProcessor)` | Claims one buffer from the queue's preallocated pool; returns `false` once the pool is exhausted instead of growing it. | [PacketsQueue](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.PacketsQueue.html) |
| `PacketsQueue.EnqueuePackets(ref PacketsQueue)` | Bulk-copies packets from another queue into this one; does not raise an error if not all packets fit. | [PacketsQueue](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.PacketsQueue.html) |
| `PacketsQueue.Clear()` / `.Dispose()` | Release all queued packets, or release the queue instance itself (`IDisposable`). | [PacketsQueue](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.PacketsQueue.html) |

| Type | Source |
|---|---|
| `ReceiveJobArguments` — `ReceiveQueue` (`PacketsQueue`), `ReceiveResult` (`OperationResult`), `Time` (ms) passed into a custom `NetworkInterface`'s receive job | [ReceiveJobArguments](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.ReceiveJobArguments.html) |
| `SendJobArguments` — `SendQueue` (`PacketsQueue`), `Time` (ms) passed into a custom `NetworkInterface`'s send job | [SendJobArguments](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.SendJobArguments.html) |

## Authoring a custom pipeline stage (low-level API)

Reach for this only once none of the five built-in stages above cover the need — it's the contract Unity itself uses to implement them. Implement `INetworkPipelineStage`; its `StaticSize` property reports how much shared "static" storage the stage needs (shared by every instance of that stage type), and its `StaticInitialize(byte* staticInstanceBuffer, int staticInstanceBufferLength, NetworkSettings settings)` runs once per stage type and must return a populated `NetworkPipelineStage` struct — built via the constructor `NetworkPipelineStage(TransportFunctionPointer<ReceiveDelegate>, TransportFunctionPointer<SendDelegate>, TransportFunctionPointer<InitializeConnectionDelegate>, int, int, int, int, int)`, carrying the `ReceiveCapacity`/`SendCapacity`/`HeaderCapacity`/`SharedStateCapacity`/`PayloadCapacity` sizing fields plus the `Receive`/`Send`/`InitializeConnection` function pointers the pipeline runtime calls at send/receive time.

Each `Receive`/`Send` call gets a `ref NetworkPipelineContext` exposing the stage's buffers (`internalProcessBuffer`, `internalSharedProcessBuffer`, `staticInstanceBuffer` and their lengths), a writable `header` (`DataStreamWriter`), the connection's `maxMessageSize` (path MTU), and the current `timestamp`; each call returns/updates a `NetworkPipelineStage.Requests` flag — `None`, `Resume` (run again immediately), `Update` (run receive on next update), `SendUpdate` (run send on next update), or `Error` — to tell the pipeline runtime what to do next. `NetworkPipelineStageId.Get<T>()` identifies a stage type for runtime lookup, and `TransportFunctionPointer<T>` (constructed from a delegate via `TransportFunctionPointer(T executeDelegate)`, exposing the wrapped pointer through its `Ptr` field) is the Burst-compatible wrapper every one of those function pointers uses.

| Type | Source |
|---|---|
| `INetworkPipelineStage` | [INetworkPipelineStage](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.INetworkPipelineStage.html) |
| `NetworkPipelineStage` | [NetworkPipelineStage](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkPipelineStage.html) |
| `NetworkPipelineContext` | [NetworkPipelineContext](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkPipelineContext.html) |
| `NetworkPipelineStage.Requests` | [NetworkPipelineStage.Requests](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkPipelineStage.Requests.html) |
| `NetworkPipelineStage.InitializeConnectionDelegate` | [NetworkPipelineStage.InitializeConnectionDelegate](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkPipelineStage.InitializeConnectionDelegate.html) |
| `NetworkPipelineStage.ReceiveDelegate` | [NetworkPipelineStage.ReceiveDelegate](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkPipelineStage.ReceiveDelegate.html) |
| `NetworkPipelineStage.SendDelegate` | [NetworkPipelineStage.SendDelegate](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkPipelineStage.SendDelegate.html) |
| `NetworkPipelineStageId` | [NetworkPipelineStageId](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkPipelineStageId.html) |
| `TransportFunctionPointer\<T\>` | [TransportFunctionPointer\<T\>](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.TransportFunctionPointer-1.html) |
