# Optimization and Bandwidth

Pages (6.6): `optimizations` and its children (optimize ghosts, reduce prediction overhead, manage serialization costs, limit snapshot size, off frames, data compression). Measure first with the Network Profiler Snapshot Overview ([testing-and-debugging.md](testing-and-debugging.md)).

## Importance and send priority
Snapshot packets are filled from a priority queue at chunk granularity, highest importance first. Importance is multiplied by ticks since last sent (not since acked), so starved chunks climb.

| Lever | Effect |
|---|---|
| `GhostAuthoringComponent.Importance` | Base per-prefab priority |
| `MaxSendRate` | Caps resend frequency; bypassed for structural changes |
| `GhostDistanceImportance.Scale` + `GhostDistanceData` | Distance scaling via `GhostDistancePartitioningSystem` tiles (adds `GhostDistancePartitionShared`; needs `GhostConnectionPosition`) |
| `GhostImportance.BatchScaleImportanceFunction` | Custom per-chunk/per-connection scaling |

## Relevancy
- `GhostRelevancy` singleton + `GhostRelevancySet`; `GhostRelevancyMode`: `Disabled` (default) / `SetIsRelevant` (whitelist) / `SetIsIrrelevant` (blacklist).
- An irrelevant ghost looks destroyed on the client; add a marker (e.g. `IsDead`) to tell real despawn apart. Group children have no independent relevancy ([ghost-spawning-and-groups.md](ghost-spawning-and-groups.md)).

## Serialization cost
- Default is three-baseline delta compression: cheap bandwidth for predictable data, more encode/decode CPU, continuous resends. `UseSingleBaseline` costs some bandwidth for ~50% less client deserialization CPU and lets unchanged chunks stop resending (`Static` always uses one baseline).
- `UsePreserialization` (adds `PreSerializedGhost`) serializes once per tick for all connections. Worth it only for frequently updated types sent to many clients; otherwise it serializes every tick even when nothing is sent.
- Quantization is the main compression lever and pairs well with NfE's Huffman coding (small deltas); inconsistent quantization breaks resimulation ([prediction-caveats.md](prediction-caveats.md)).

## Resimulation cost

| Lever | Trade-off |
|---|---|
| Physics Step singleton `Multi Threaded = false` | Less scheduling overhead on 20+ resim frames, less parallelism |
| Prediction switching | Fewer predicted ghosts |
| `ClientTickRate.ForcedInputLatencyTicks` | Fewer resim steps, more input latency; input code must read `NetworkTime.InputTargetTick`, not `ServerTick` |
| `RollbackPredictionOnStructuralChanges = false` (per prefab) | Saves CPU; a re-added replicated component resets to default (zero) |

## Snapshot size

| Setting | Scope |
|---|---|
| `NetworkStreamSnapshotTargetSize.Value` | Per-connection byte cap |
| `GhostSendSystemData.DefaultSnapshotPacketSize` | Global cap (non-zero activates) |
| `GhostSendSystemData.MaxSendChunks` / `MaxIterateChunks` | Chunks sent vs iterated per snapshot |
| `GhostSystemConstants.SnapshotHistorySize` | Default 32 (~500 ms at 60 Hz); `NETCODE_SNAPSHOT_HISTORY_SIZE_16` / `_6` defines for 30 Hz or less, or very large projects |

Off frames: on `NetworkTime.IsOffFrame` frames a client-hosted server can spread per-connection send work instead of doing it all on tick frames.
