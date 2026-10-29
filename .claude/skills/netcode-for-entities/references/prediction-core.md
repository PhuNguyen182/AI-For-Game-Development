# Prediction, Time and Interpolation

Pages (6.6): `prediction-n4e`, `time-synchronization`, `interpolation`.

## The loop
1. Client simulates its own input ahead of the server by `TargetCommandSlack` ticks and sends it.
2. Server simulates at fixed `SimulationTickRate` and returns the result in a snapshot.
3. Client rolls back to that server tick and replays every input since; invisible when the result matches.
- `PredictedGhost` is on predicted ghosts on the client and on every ghost on the server (server loop runs once per tick, no `TimeData` change).
- Cost: a 300 ms connection can mean ~22 resimulation frames in one client frame, for every system in `PredictedSimulationSystemGroup`, physics included.

## Query pattern

```csharp
foreach (var lt in SystemAPI.Query<RefRW<LocalTransform>>().WithAll<PredictedGhost, Simulate>()) { }
```

- `Simulate` is disabled for all predicted ghosts at loop start, enabled per entity for the ticks it needs, and enabled for all by loop end. Omit it and the system runs on frozen entities during partial rollback.
- Legacy: `predictedGhost.ValueRW.ShouldPredict(serverTick)` still works; do not write new code with it.
- A remote player's input ghost: query the replicated `[GhostField]` input directly.

## Partial ticks and snapshots
- Full ticks are deterministic at `1/SimulationTickRate`. Partial ticks roll back to the last full predicted tick and simulate one step at variable deltaTime each frame. A delta within ±5% of a full tick rounds to it. `InputEvent` keeps an edge-triggered input exactly-once through this.
- Partial snapshots stream a large world over several ticks, so entities may sit at different ticks; the loop starts from the oldest. `Simulate` makes that safe.
- Catch-up batches ticks that share the same input, never across an input change (e.g. input 1 on ticks 10-12 and 2 on 13-15 batch within each range only).

## `NetworkTime` (client and server)

| Field | Meaning |
|---|---|
| `ServerTick` | Tick being simulated/predicted |
| `InterpolationTick` / `InterpolationTickFraction` | Interpolated render tick and blend toward the next |
| `IsFirstPredictionTick` / `IsFinalPredictionTick` | First since last snapshot / last this frame |
| `IsFirstTimeFullyPredictingTick` | First time a full tick is predicted; the guard for one-off spawn/VFX/SFX |
| `IsPartialTick` | Resimulating a partial tick |
| `IsOffFrame` | Client frame where the fixed tick does not advance |

- `NetworkTimeSystem` nudges the client clock toward the server in small steps by scaling `Time.DeltaTime`/`ElapsedTime` in `SimulationSystemGroup`; `UnscaledClientTime` gives unscaled time.

## Tick-rate settings

| Singleton.field | Effect |
|---|---|
| `ClientServerTickRate.SimulationTickRate` | Server rate, default 60 |
| `ClientServerTickRate.NetworkTickRate` | Snapshot rate; less than and a common factor of `SimulationTickRate` |
| `ClientTickRate.TargetCommandSlack` | Ticks the client runs ahead, default 2 |
| `ClientTickRate.MaxPredictAheadTimeMS` | Clamp on the RTT used for the predicted tick |
| `ClientTickRate.InterpolationTimeNetTicks` / `InterpolationTimeMS` | Interpolation buffer |
| `ClientTickRate.MaxExtrapolationTimeSimTicks` | Extrapolation cap, default 20 ticks (~333 ms at 60 Hz) |

## Interpolation
Non-predicted ghosts render by linear interpolation between snapshots inside a deliberately delayed buffer; the interpolated timeline trails the server by RTT/2 + `InterpolationTimeNetTicks`. If render rate equals tick rate there is nothing to blend, so check `InterpolationTickFraction` before relying on smoothing.
