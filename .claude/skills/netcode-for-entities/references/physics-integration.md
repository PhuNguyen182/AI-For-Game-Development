# Physics Integration — predicted physics, multi-world proxies

Sources: [Physics](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/physics.html).
Covers: SKILL.md §4 — **"Route a predicted ghost's physics through `PredictedFixedStepSimulationSystemGroup`, never a bespoke physics loop"**.

How Unity Physics runs inside a ghost's prediction/interpolation, and how to
give a client-only effect (debris, VFX) its own physics world without it
silently trying to interact with predicted gameplay. Rollback mechanics
this physics loop is subject to are in [prediction-core.md](prediction-core.md).

## Hard requirement

Physics does not run at all unless **at least one predicted ghost exists**
in the scene — a physics-only project with no predicted ghosts will see
`PhysicsSystemGroup` simply not update.

## Interpolated vs. predicted ghost physics

| Ghost mode | Behavior | Source |
|---|---|---|
| Interpolated | Physics simulates on the **server only**; client receives position/rotation from snapshots. `Simulate` is disabled client-side at frame start, so `PhysicsVelocity` is ignored and the body is effectively kinematic on non-authoritative clients | [Physics](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/physics.html) |
| Predicted | During initialization, Netcode moves `PhysicsSystemGroup` and every `FixedStepSimulationSystemGroup` system into `PredictedFixedStepSimulationSystemGroup` | [Physics](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/physics.html) |

`PredictedFixedStepSimulationSystemGroup` runs once per rollback tick, so it
can run many times in a single frame — the same cost profile described in
[prediction-core.md](prediction-core.md)'s Performance reality section.

## Batching (CPU cost mitigation)

| Setting | Side | Effect | Source |
|---|---|---|---|
| `ClientServerTickRate.MaxSimulationStepBatchSize` / `MaxSimulationStepsPerFrame` | Server | Caps steps simulated per frame | [Physics](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/physics.html) |
| `ClientTickRate.MaxPredictionStepBatchSizeFirstTimeTick` / `MaxPredictionStepBatchSizeRepeatedTick` | Client | Caps prediction resimulation batch size | [Physics](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/physics.html) |

**Critical caveat**: batching trades CPU for accuracy — it raises the
probability of a visible misprediction. Default quantization for transform
and velocity fields is **1000**; raising it reduces visible
correction/jitter at a bandwidth cost.

## Lag compensation

`NetCodePhysicsConfig.EnableLagCompensation` turns on rewound collision-world
queries via `PhysicsWorldHistorySingleton` — see
[prediction-caveats.md](prediction-caveats.md)'s Server-side rewind section
for the query API and its 250–500 ms history-window limit.

## When predicted physics actually runs this frame

All of: `NetworkStreamInGame` singleton present, at least one predicted
ghost exists, fixed-tick execution only (no partial-tick physics unless
`SimulationTickRate` is configured faster), and either a kinematic entity
(`PhysicsVelocity`) exists or lag compensation is enabled. Tune via two
enums:

| `PredictionLoopUpdateMode` | `PhysicGroupRunMode` | Net requirement | Source |
|---|---|---|---|
| `RequirePredictedGhost` (default) | `LagCompensationEnabledOrKinematicGhosts` | Predicted ghosts **and** (kinematic ghosts or lag compensation) | [Physics](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/physics.html) |
| `RequirePredictedGhost` | `AlwaysRun` | Predicted ghosts only | [Physics](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/physics.html) |
| `AlwaysRun` | `AlwaysRun` | Fixed tick only, no ghost/collider requirement | [Physics](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/physics.html) |

## A second, client-only physics world

For effects that must never interact with predicted gameplay (loose
debris, purely visual particles): add `NetcodePhysicsConfig` to the
sub-scene with "Client Non Ghost World" set, tag client-only physics
GameObjects with `PhysicsWorldIndex` matching that value, and declare a
custom group:

```csharp
[WorldSystemFilter(WorldSystemFilterFlags.ClientSimulation)]
[UpdateInGroup(typeof(FixedStepSimulationSystemGroup))]
public partial class VisualizationPhysicsSystemGroup : CustomPhysicsSystemGroup
{
    public VisualizationPhysicsSystemGroup() : base(1, true) {} // world index, shared static colliders
}
```

The two simulations run at independent fixed steps and cannot interact
directly — they are separate islands. To let a predicted ghost still affect
the client-only world (e.g. spawn debris on impact), add
`CustomPhysicsProxyAuthoring` to the ghost: baking creates a kinematic proxy
entity with a copy of the ghost's collider, and `SyncCustomPhysicsProxySystem`
keeps it positioned to match the real ghost — drive mode defaults to
kinematic velocity, configurable via `GenerateGhostPhysicsProxy.DriveMode`
(authoring) or `PhysicsProxyGhostDriver.driveMode` (runtime).

**Critical caveat**: the default `PhysicsSystemGroup` must update at least
once before any `CustomPhysicsSystemGroup` can run — `SimulationSingleton.Type`
has to leave `SimulationType.NoPhysics` first. `Unity.Physics` debug
visualization only draws the default physics world; a second world's
colliders are invisible to it. Physics also ignores partial ticks entirely
— use physics-specific interpolation if a predicted body needs smoother
visuals than the fixed physics tick provides.
