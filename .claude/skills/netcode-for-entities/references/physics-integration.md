# Physics Integration

Page (6.6): `physics`.

- Physics does not run unless at least one predicted ghost exists in the scene.
- Interpolated ghost: physics runs on the server only; `Simulate` is disabled client-side, so `PhysicsVelocity` is ignored and the body is effectively kinematic there.
- Predicted ghost: Netcode moves `PhysicsSystemGroup` and every `FixedStepSimulationSystemGroup` system into `PredictedFixedStepSimulationSystemGroup`, which runs once per rollback tick (many times per frame).
- `NetCodePhysicsConfig.EnableLagCompensation` enables rewound queries (API in [prediction-caveats.md](prediction-caveats.md)).

## Batching (trades accuracy for CPU; raises misprediction odds)
- Server: `ClientServerTickRate.MaxSimulationStepBatchSize`, `MaxSimulationStepsPerFrame`.
- Client: `ClientTickRate.MaxPredictionStepBatchSizeFirstTimeTick`, `MaxPredictionStepBatchSizeRepeatedTick`.
- Default quantization for transform and velocity fields is 1000; raising it reduces visible jitter at a bandwidth cost.

## When predicted physics runs
Needs `NetworkStreamInGame`, a predicted ghost, fixed ticks only (no partial-tick physics unless `SimulationTickRate` is faster), and a kinematic entity (`PhysicsVelocity`) or lag compensation. Tune with:

| `PredictionLoopUpdateMode` | `PhysicGroupRunMode` | Runs when |
|---|---|---|
| `RequirePredictedGhost` (default) | `LagCompensationEnabledOrKinematicGhosts` (default) | Predicted ghosts and (kinematic ghosts or lag compensation) |
| `RequirePredictedGhost` | `AlwaysRun` | Predicted ghosts |
| `AlwaysRun` | `AlwaysRun` | Every fixed tick |

`PredictedPhysicsNonGhostWorld` declares which physics world a predicted group uses.

## Client-only physics world (debris, visual particles)
- Add `NetcodePhysicsConfig` to the subscene with "Client Non Ghost World" set; tag the GameObjects with a matching `PhysicsWorldIndex`; declare a group:

```csharp
[WorldSystemFilter(WorldSystemFilterFlags.ClientSimulation)]
[UpdateInGroup(typeof(FixedStepSimulationSystemGroup))]
public partial class VisualizationPhysicsSystemGroup : CustomPhysicsSystemGroup
{ public VisualizationPhysicsSystemGroup() : base(1, true) {} } // world index, share static colliders
```

- The two worlds run independent fixed steps and cannot interact. To let a ghost affect the client-only world, add `CustomPhysicsProxyAuthoring`: baking makes a kinematic proxy with a collider copy, kept in sync by `SyncCustomPhysicsProxySystem` (`GenerateGhostPhysicsProxy.DriveMode` at authoring, `PhysicsProxyGhostDriver.driveMode` at runtime; default kinematic velocity).
- The default `PhysicsSystemGroup` must update once before any `CustomPhysicsSystemGroup` (`SimulationSingleton.Type` must leave `NoPhysics`).
- Unity.Physics debug drawing shows only the default world.
- Physics ignores partial ticks; use physics-specific interpolation for smoother visuals.
