# Prediction Core — the resimulation loop, Simulate tag, partial ticks

Sources: [Introduction to prediction](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/intro-to-prediction.html), [Managing latency with prediction](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/prediction-n4e.html).
Covers: SKILL.md §4 — **"Write predicted-ghost systems against the `Simulate` tag, not a raw tick comparison"**.

Why prediction exists and how a predicted-ghost system should actually be
written. What goes wrong at the edges of this loop —
smoothing, prediction switching, quantization drift, structural-change
races — is [prediction-caveats.md](prediction-caveats.md); physics inside
this same loop is [physics-integration.md](physics-integration.md).

## Why prediction, not client authority

Letting the client simulate and report results invites cheating (teleport,
stat injection) and unresolvable conflicts between two clients' independent
simulations. Client prediction instead lets the client simulate its own
input immediately ("ask forgiveness, not permission") while the server
stays the sole authority; the client rolls back and replays whenever the
server disagrees — invisibly, most of the time.

## The loop, step by step

1. Client simulates its own input locally, ahead of the server by
   `ClientTickRate.TargetCommandSlack` ticks (see
   [time-and-interpolation.md](time-and-interpolation.md)).
2. Client sends input; server queues it.
3. Server simulates at its fixed `SimulationTickRate`.
4. Server sends the result back in the next snapshot; client keeps
   predicting locally in the meantime.
5. Client receives the snapshot, rolls back to that server tick, and
   replays every input since — invisible to the player when the result
   matches what was already predicted.

`PredictedGhost` is added to all predicted ghosts on the client, and to
**every** ghost on the server (the server's "prediction loop" always runs
exactly once per tick and does not touch `TimeData`).

## Query pattern — preferred (`Simulate` tag)

```csharp
foreach (var localTransform in SystemAPI.Query<RefRW<LocalTransform>>()
    .WithAll<PredictedGhost, Simulate>())
{
    // Runs once per tick this ghost actually needs to (re)simulate.
}
```

The `Simulate` tag is disabled for all predicted ghosts at the start of the
loop, enabled per-entity only for the tick(s) that ghost needs, and
guaranteed enabled for every predicted ghost by the loop's end — include it
in every predicted-ghost query, or the system runs on stale/frozen entities
during a partial rollback.

**Legacy pattern** — still functional, do not write new code against it:
```csharp
var serverTick = SystemAPI.GetSingleton<NetworkTime>().ServerTick;
foreach (var (localTransform, predictedGhost) in
    SystemAPI.Query<RefRW<LocalTransform>, RefRW<PredictedGhost>>().WithAll<Simulate>())
{
    if (!predictedGhost.ValueRW.ShouldPredict(serverTick)) return;
    // ...
}
```

For a remote player's predicted-input ghost (owner-predicted elsewhere),
query the replicated `[GhostField]`-marked input directly:
```csharp
foreach (var (localTransform, input, entity) in
    SystemAPI.Query<RefRW<LocalTransform>, RefRO<MyInput>>().WithEntityAccess())
{
    // ...
}
```

## Partial ticks

A client's frame rate rarely lines up with the fixed simulation rate.
**Full ticks** are deterministic, always at `1/SimulationTickRate` deltaTime.
**Partial ticks** run between full ticks at variable deltaTime, rolling back
to the last predicted full tick and simulating one partial step with the
right deltaTime each frame — this is how the client updates visually every
frame while staying deterministic at full-tick boundaries. A partial tick's
deltaTime within **±5%** of a full tick's rounds to the nearest full tick.
`InputEvent` exists specifically to preserve an edge-triggered input (e.g. a
jump press) exactly once across this partial-tick churn.

## Partial snapshots

The server streams a large world's ghosts across multiple ticks rather than
one giant snapshot — so the prediction loop starts from the **oldest** tick
applied to any entity, and some entities may already hold newer data than
others in the same frame. A predicted-ghost system cannot assume every
predicted entity is at the same tick; the `Simulate` tag is what makes this
safe, since it is only enabled for entities actually being (re)simulated
this iteration.

## Batching / catch-up

If real deltaTime exceeds the target (a perf hitch), Netcode batches
multiple ticks into fewer, larger-deltaTime steps to catch up.

**Critical caveat**: batching only happens across ticks that share the same
input — a documented example shows `FOO=1` on ticks 10–12 and `FOO=2` on
ticks 13–15 batching *within* each range but never *across* the 12→13
boundary, since collapsing them would silently change which input applied
when.

## Performance reality

A 300 ms connection can mean roughly **22 frames of resimulation in a
single client frame** — every system in `PredictedSimulationSystemGroup`,
physics included, runs that many times. This is why
[prediction-caveats.md](prediction-caveats.md)'s cost-reduction options and
[optimization-and-bandwidth.md](optimization-and-bandwidth.md) are not
optional polish on a real connection.
