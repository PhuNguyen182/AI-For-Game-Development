# Time and Interpolation — NetworkTime, tick rates, interpolation/extrapolation buffer

Sources: [Time synchronization](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/time-synchronization.html), [Interpolation](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/interpolation.html).
Covers: SKILL.md §4 — **"Write predicted-ghost systems against the `Simulate` tag, not a raw tick comparison"**.

The clock every ghost-mode decision in [ghost-authoring.md](ghost-authoring.md)
and every query in [prediction-core.md](prediction-core.md) is built on:
what tick a predicted ghost is being simulated at, and how far behind an
interpolated ghost's rendered position sits.

## `NetworkTime` singleton

`SystemAPI.GetSingleton<NetworkTime>()`, valid on both client and server.

| Field | Meaning | Source |
|---|---|---|
| `ServerTick` | The tick currently being simulated/predicted | [Time synchronization](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/time-synchronization.html) |
| `InterpolationTick` / `InterpolationTickFraction` | Current interpolated-rendering tick, and the blend fraction toward the next one | [Interpolation](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/interpolation.html) |
| `IsFirstPredictionTick` | True on the first tick predicted since the last snapshot | [Time synchronization](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/time-synchronization.html) |
| `IsFinalPredictionTick` | True on the last tick this frame will predict | [Time synchronization](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/time-synchronization.html) |
| `IsFirstTimeFullyPredictingTick` | True only the first time a **full** (non-partial) tick is predicted — the correct guard for one-off spawn/VFX/SFX logic | [Time synchronization](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/time-synchronization.html) |
| `IsPartialTick` | True while resimulating a partial (sub-frame) tick | [Prediction in Netcode for Entities](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/prediction-n4e.html) |

`NetworkTimeSystem` nudges the client clock toward the server's estimated
time in small increments rather than jumping — implemented by scaling
`Time.DeltaTime`/`Time.ElapsedTime` inside `SimulationSystemGroup`;
`UnscaledClientTime` is the escape hatch for code that needs real,
unscaled time even there.

## Tick rate configuration

| Singleton | Field | Effect | Source |
|---|---|---|---|
| `ClientServerTickRate` | `SimulationTickRate` | Server fixed rate, default 60/s | [setup-and-worlds.md](setup-and-worlds.md) |
| `ClientServerTickRate` | `NetworkTickRate` | Snapshot send rate — must be less than, and a common factor of, `SimulationTickRate` | [Introduction to prediction](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/intro-to-prediction.html) |
| `ClientTickRate` | `TargetCommandSlack` | Ticks the client runs ahead so its input reaches the server in time — default 2 | [Introduction to prediction](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/intro-to-prediction.html) |
| `ClientTickRate` | `MaxPredictAheadTimeMS` | Clamp on RTT used to compute the client's predicted server tick | [Time synchronization](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/time-synchronization.html) |
| `ClientTickRate` | `InterpolationTimeNetTicks` / `InterpolationTimeMS` | Interpolation buffer size, in ticks or milliseconds | [Interpolation](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/interpolation.html) |
| `ClientTickRate` | `MaxExtrapolationTimeSimTicks` | Cap on extrapolation when new data is missing — **default 20 ticks** (≈333 ms at 60 Hz) | [Interpolation](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/interpolation.html) |

Worked example (60 tick/s, 200 ms RTT, server on tick 10): the client
simulates roughly tick 18 so its input lands in time — command slack absorbs
a small amount of jitter without the client needing to run further ahead.

## Interpolation and extrapolation

Non-predicted ghosts render via **waypoint pathing** (linear interpolation
between successive snapshot values) held in a **buffered** delay — a
deliberately delayed render window that trades latency for smoothness
against jitter and loss. The client's interpolated timeline runs behind the
server by `RTT/2 + InterpolationTimeNetTicks`.

**Critical caveat**: if the render frame rate exactly matches the
simulation tick rate, "interpolation" degrades to just buffered-delay
display of raw snapshot values — there is nothing to blend between. Do not
assume every frame is actually interpolating; check `InterpolationTickFraction`
before relying on smoothing behavior in that edge case.
