# Prediction Caveats — smoothing, switching, known edge cases, lag compensation

Sources: [Prediction smoothing](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/prediction-smoothing.html), [Prediction switching](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/prediction-switching.html), [Prediction edge cases and known issues](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/prediction-details.html), [Server-side rewind](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/server-rewind.html).
Covers: SKILL.md §4 — **"Treat every prediction correction as something to minimize, not eliminate"**.

What to do about a visible correction, when to stop predicting a ghost at
all, and the specific ways this loop ([prediction-core.md](prediction-core.md))
diverges between client and server. Read this before treating a visible
snap or jitter as a bug rather than a known, budgetable cost.

## Smoothing a correction

`GhostPredictionSmoothingSystem` reconciles prediction error from client/
server logic differences, packet loss, or quantization. Register a
correction via `GhostPredictionSmoothing.RegisterSmoothingAction`, a
`PortableFunctionPointer<GhostPredictionSmoothing.SmoothingActionDelegate>`
with signature `void SmoothingAction(IntPtr currentData, IntPtr previousData, IntPtr userData)`.

**Critical caveat**: the callback fires only when the client reconciles
against a new predicted-ghost snapshot — not every render frame — and it is
a stateless function pointer with no context, so complex logic does not
belong inside it. It also stops working the instant the entity undergoes a
structural change, since the smoothing state is chunk-relative.

## Switching predicted ↔ interpolated at runtime

`GhostPredictionSwitchingQueues` singleton (`ConvertToPredictedQueue`,
`ConvertToInterpolatedQueue`), processed by `GhostPredictionSwitchingSystem`.
Use for: the player's own character controller, objects it's currently
colliding with, and items it's actively interacting with — not for the rest
of the world, which should simply stay interpolated.

```csharp
ref var queues = ref SystemAPI.GetSingletonRW<GhostPredictionSwitchingQueues>().ValueRW;
queues.ConvertToPredictedQueue.Enqueue(new ConvertPredictionEntry
{
    TargetEntity = entityA,
    TransitionDurationSeconds = 1f, // 0f = instant
});
```

Rules (an invalid entry is silently ignored, with a log): the ghost's
`SupportedGhostMode` must be `All`; `CurrentGhostMode` cannot already be
`OwnerPredicted`; the target mode must differ from the current one; the
ghost cannot already be mid-switch.

**Critical caveat**: predicted and interpolated ghosts live on different
relative timelines (predicted runs ~1 ping ahead, interpolated ~1 ping
behind), so a switch can visibly teleport the ghost by more than **2×
ping**. `SwitchPredictionSmoothing` linearly interpolates position/rotation
over `TransitionDurationSeconds` to hide this, but fast, frequently
direction-changing objects can still show artifacts — this is a mitigation,
not a fix.

## Known edge cases

| Case | Root cause | Mitigation | Source |
|---|---|---|---|
| Two predicted ghosts interact wrongly after a partial snapshot | Only the ghosts included in that partial snapshot roll back; others stay frozen at their old tick, so the interaction uses stale data for one side | Client anticipation instead of full self-prediction; mutate the *other* ghost's state rather than waiting on it; `GhostGroup` critical pairs; prioritize send order; filter with `Simulate` | [Prediction edge cases](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/prediction-details.html) |
| Rollback goes further back than expected | Rollback is clamped to the input queue size — a **const 64** ticks | — | [Prediction edge cases](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/prediction-details.html) |
| A predicted-spawned ghost mispredicts against ghosts that just rolled back | A fresh predicted spawn has no snapshot yet, so it never rolls back on its own — but other ghosts around it do | Enable "allow predicted spawned ghost to rollback to spawn tick" so it resimulates in step with everything else | [Prediction edge cases](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/prediction-details.html) |
| Client and server values drift over several ticks | **Netcode does not quantize values between ticks during resimulation** — the client re-derives from an already-quantized value while the server derives from the full-precision one | Raise quantization precision, disable it, or manually quantize both sides identically at tick end | [Prediction edge cases](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/prediction-details.html) |
| A component's value resets to default after remove/re-add on a predicted ghost | Full-tick state backups don't capture a component that didn't exist at backup time; re-adding does not itself trigger a rollback | Avoid remove/re-add of replicated components on predicted ghosts; if unavoidable, do it before `GhostUpdateSystem` runs that tick | [Prediction edge cases](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/prediction-details.html) |

**Critical caveat**: per NfE's own documentation, *"Netcode does not
guarantee determinism if you use unquantized values either. Fundamentally,
Netcode is not a deterministic package."* — this is a materially different
guarantee than a lockstep/rollback framework provides; do not sell it to
design as bit-exact determinism, and keep the Shared Core's own determinism
discipline (`coding-principles.md`'s Shared Core integrity section) as the
actual source of client/server agreement, not an assumption about NfE.

## Server-side rewind (lag compensation)

`PhysicsWorldHistorySingleton` retains **250–500 ms** of server physics
history; `GetCollisionWorldFromTick(predictingTick, delay, ...)` rewinds a
collision-world snapshot to validate a client's claimed hit (e.g. a hitscan)
against the state the client actually saw, using
`CommandDataInterpolationDelay` to compute how far back to rewind. Gate the
check on `NetworkTime.IsFirstTimeFullyPredictingTick` to run it once per
real tick, not once per resimulation.

**Critical caveat**: only **physics** state is backed up. Any other
gameplay state that affects the validity of an action — invincibility
frames, a shield buff — needs its own per-tick history tracked separately,
or selectively disable rewind for those states/scenarios instead.
