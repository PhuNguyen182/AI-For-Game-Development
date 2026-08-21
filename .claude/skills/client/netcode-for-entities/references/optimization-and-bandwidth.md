# Optimization and Bandwidth — importance, relevancy, preserialization, compression

Sources: [Optimize ghosts](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/optimization/optimize-ghosts.html), [Reduce prediction overhead](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/optimization/reduce-prediction-overhead.html), [Manage serialization costs](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/optimization/manage-serialization-costs.html), [Limit snapshot size](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/optimization/limit-snapshot-size.html), [Execute expensive operations during off frames](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/optimization/off-frame.html), [Data compression](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/optimization/compression.html).
Covers: SKILL.md §4 — **"Tune bandwidth and CPU deliberately, before assuming the transport itself is the bottleneck"**.

Every lever here trades bandwidth for CPU, or accuracy for both — measure
with [testing-and-debugging.md](testing-and-debugging.md)'s Network
Profiler Snapshot Overview tab before and after, per
`performance-and-algorithms.md`'s Verification section.

## Importance and send priority

Server fills each fixed-size snapshot packet from a priority queue, highest
importance first, at chunk granularity — importance is multiplied by
**ticks since last sent** (not ticks since acked), so a starved chunk's
priority climbs over time.

| Lever | Effect | Source |
|---|---|---|
| `GhostAuthoringComponent.Importance` | Base per-prefab-type priority | [Optimize ghosts](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/optimization/optimize-ghosts.html) |
| `GhostAuthoringComponent.MaxSendRate` | Caps resend frequency for this prefab's chunks — bypassed for structural changes | [Optimize ghosts](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/optimization/optimize-ghosts.html) |
| `GhostDistanceImportance.Scale` + `GhostDistanceData` | Built-in distance-based scaling via `GhostDistancePartitioningSystem` spatial tiles | [Optimize ghosts](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/optimization/optimize-ghosts.html) |
| `GhostImportance.BatchScaleImportanceFunction` | Custom per-chunk/per-connection scaling function | [Optimize ghosts](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/optimization/optimize-ghosts.html) |

## Relevancy — don't replicate what a client can't act on

`GhostRelevancy` singleton + `GhostRelevancySet`, mode
`GhostRelevancyMode.Disabled` (default) / `SetIsRelevant` (whitelist) /
`SetIsIrrelevant` (blacklist). An irrelevant ghost looks **destroyed** on
the client — use a separate marker (e.g. `IsDead`) if real despawn needs to
be distinguishable from "just went out of relevancy." Ghost group children
don't support relevancy independently — see
[ghost-spawning-and-groups.md](ghost-spawning-and-groups.md).

## Preserialization

`GhostAuthoringComponent.UsePreserialization` serializes a ghost's state
**once per tick** and reuses it across every connection, instead of once
per connection. Worth it only for a ghost type that is both frequently
updated and sent to many clients — otherwise it serializes every tick
regardless of whether that tick is actually sent to anyone, which can cost
more than it saves.

## Reducing prediction resimulation cost

| Lever | Trade-off | Source |
|---|---|---|
| Physics Step singleton, `Multi Threaded = false` | Less scheduling overhead when resimulating 20+ frames at high ping, at the cost of parallelism | [Reduce prediction overhead](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/optimization/reduce-prediction-overhead.html) |
| Prediction switching | Fewer ghosts predicted at all — see [prediction-caveats.md](prediction-caveats.md) | [Reduce prediction overhead](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/optimization/reduce-prediction-overhead.html) |
| `ClientTickRate.ForcedInputLatencyTicks` | Fewer resimulation steps per frame, at the cost of added input latency; requires reading `NetworkTime.InputTargetTick` instead of `ServerTick` in input code | [Reduce prediction overhead](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/optimization/reduce-prediction-overhead.html) |
| `RollbackPredictionOnStructuralChanges = false` (per-prefab) | Saves CPU, but a removed-then-re-added replicated component resets to **default (zero)** instead of the server value — see [prediction-caveats.md](prediction-caveats.md) | [Reduce prediction overhead](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/optimization/reduce-prediction-overhead.html) |

## Serialization cost

Default **three-baseline delta compression** predicts against the last
three acknowledged snapshots — cheap on bandwidth for predictable data
(timers, linear motion) but costs CPU to encode/decode and requires
continuous resends even when nothing changed. `GhostAuthoringComponent.UseSingleBaseline`
trades some of that bandwidth efficiency for roughly **50% less client-side
deserialization CPU**, and lets unchanged chunks stop resending after a
period. `GhostOptimizationMode.Static` (per
[ghost-authoring.md](ghost-authoring.md)) always uses a single baseline
regardless of this setting.

## Snapshot size limits

| Setting | Scope | Source |
|---|---|---|
| `NetworkStreamSnapshotTargetSize.Value` | Per-connection byte cap | [Limit snapshot size](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/optimization/limit-snapshot-size.html) |
| `GhostSendSystemData.DefaultSnapshotPacketSize` | Global cap (non-zero activates it) | [Limit snapshot size](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/optimization/limit-snapshot-size.html) |
| `GhostSendSystemData.MaxSendChunks` / `MaxIterateChunks` | Chunks sent vs. chunks iterated per snapshot | [Limit snapshot size](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/optimization/limit-snapshot-size.html) |
| `GhostSystemConstants.SnapshotHistorySize` | Default **32** (~500 ms at 60 Hz); `NETCODE_SNAPSHOT_HISTORY_SIZE_16`/`_6` scripting defines for ≤30 Hz or very large projects | [Limit snapshot size](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/optimization/limit-snapshot-size.html) |

## Off-frame work and compression

`NetworkTime.IsOffFrame` is true on a client frame where the fixed
simulation tick doesn't advance (frame rate above tick rate) — a
client-hosted server can spread per-connection sending work across these
frames instead of doing it all on tick frames. Quantization
(`[GhostField(Quantization=...)]`) is the main compression lever;
delta-compresses well against Netcode's Huffman coding specifically because
quantized values tend to produce small deltas — see
[ghost-authoring.md](ghost-authoring.md) for the parameter itself and
[prediction-caveats.md](prediction-caveats.md) for why quantization
interacts badly with resimulation if applied inconsistently.
