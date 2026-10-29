# Prediction Caveats

Pages (6.6): prediction smoothing, prediction switching, `prediction-details` (edge cases), server-side rewind.

## Smoothing a correction
- `GhostPredictionSmoothingSystem` reconciles prediction error. Register via `GhostPredictionSmoothing.RegisterSmoothingAction` with a `PortableFunctionPointer<GhostPredictionSmoothing.SmoothingActionDelegate>`: `void SmoothingAction(IntPtr currentData, IntPtr previousData, IntPtr userData)`.
- It fires only when reconciling against a new snapshot, not every render frame; it is stateless, so keep logic out of it; it stops working after a structural change on the entity (chunk-relative state).

## Switching predicted and interpolated at runtime
- `GhostPredictionSwitchingQueues` (`ConvertToPredictedQueue`, `ConvertToInterpolatedQueue`), processed by `GhostPredictionSwitchingSystem`. Use for the player's controller and what it collides or interacts with; leave the rest interpolated.

```csharp
ref var queues = ref SystemAPI.GetSingletonRW<GhostPredictionSwitchingQueues>().ValueRW;
queues.ConvertToPredictedQueue.Enqueue(new ConvertPredictionEntry
    { TargetEntity = e, TransitionDurationSeconds = 1f }); // 0 = instant
```

- An invalid entry is ignored with a log. Valid only if `SupportedGhostMode` is `All`, the ghost is not `OwnerPredicted`, the target mode differs, and it is not mid-switch.
- Predicted runs ~1 ping ahead and interpolated ~1 ping behind, so a switch can teleport the ghost by more than 2x ping. `SwitchPredictionSmoothing` interpolates position/rotation over `TransitionDurationSeconds`; fast, direction-changing objects can still artifact.

## Known edge cases

| Case | Cause | Mitigation |
|---|---|---|
| Two predicted ghosts interact wrongly after a partial snapshot | Only ghosts in that snapshot roll back; others stay frozen at an old tick | Client anticipation; mutate the other ghost's state instead of waiting; `GhostGroup` for critical pairs; prioritize send order; filter with `Simulate` |
| Rollback goes further back than expected | Clamped to the input queue size, const 64 ticks | None |
| A predicted-spawned ghost mispredicts against just-rolled-back ghosts | No snapshot yet, so it never rolls back itself | Enable "allow predicted spawned ghost to rollback to spawn tick" |
| Client and server values drift over ticks | Resimulation does not quantize between ticks; client derives from a quantized value, server from full precision | Raise or disable quantization, or quantize both sides identically at tick end |
| Component resets to default after remove/re-add on a predicted ghost | Full-tick backups lack a component absent at backup time; re-adding triggers no rollback | Avoid it; else do it before `GhostUpdateSystem` runs that tick |

- Manual quote: "Netcode does not guarantee determinism if you use unquantized values either. Fundamentally, Netcode is not a deterministic package." Do not present it to design as bit-exact; client/server agreement is the Core's determinism discipline (`csharp-standards` → `coding-principles.md` Shared Core integrity).

## Server-side rewind (lag compensation)
- `PhysicsWorldHistorySingleton` keeps 250-500 ms of server physics history. `GetCollisionWorldFromTick(predictingTick, delay, ...)` rewinds to the state the client saw, using `CommandDataInterpolationDelay`, to validate a hit.
- Gate on `NetworkTime.IsFirstTimeFullyPredictingTick` to run once per real tick.
- Only physics is backed up. Other validity state (invincibility frames, shield buffs) needs its own per-tick history, or disable rewind for it.
- Config: `LagCompensationConfig` singleton for the history; physics docs also name `NetCodePhysicsConfig.EnableLagCompensation` (see [physics-integration.md](physics-integration.md)).
