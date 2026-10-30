# Tick and Interpolation

Sources (below the SKILL.md `Docs:` base unless a full URL): [eo] `manual/scripting/managing-update-order/execution-order`, [fu] `script-reference/unityengine/monobehaviour/fixedupdate`, [ft] `script-reference/unityengine/time/fixedtime`, [md] `script-reference/unityengine/time/maximumdeltatime`, [sim] `script-reference/unityengine/physics/simulate`, [cd] `script-reference/unityengine/time/capturedeltatime`, [vc] https://vcontainer.hadashikick.jp/integrations/entrypoint.

## Tick owner

| Owner | Fact that decides |
|---|---|
| VContainer `IFixedTickable.FixedTick()` | Runs "nearly `MonoBehaviour.FixedUpdate()`" [vc]; plain C# class registered with `builder.RegisterEntryPoint<T>()`, Core injected by constructor. Full entry-point order: `vcontainer-dependency-injection` step 8 |
| One driver MonoBehaviour `FixedUpdate` | Fallback without VContainer; put `[DefaultExecutionOrder]` on it so it runs before any script that moves bodies in `FixedUpdate` |
| Script-stepped physics | `Physics.simulationMode = SimulationMode.Script`, owner calls `Physics.Simulate(step)` [sim]. Use when the tick must own the physics step (rollback, replay, own accumulator). `Simulate` fires contact, trigger and joint callbacks but never calls `FixedUpdate` [sim] |
| Netcode stack | NGO `NetworkManager.NetworkTickSystem.Tick`, tick rate equal to the fixed rate when physics is involved (`netcode-for-gameobjects` → `transform-latency.md`); NfE prediction group (`netcode-for-entities`). Wired by `netcode-engineer` |

## Fixed-step facts

| Subject | Fact that decides |
|---|---|
| Calls per frame | `FixedUpdate` runs zero, one or several times per frame [fu]: never assume one tick per frame |
| Catch-up cap | `Time.maximumDeltaTime` bounds fixed steps per frame to `maximumDeltaTime / fixedDeltaTime` [md]; past it the game runs slow instead of spiralling |
| Physics position in the loop | With `SimulationMode.FixedUpdate` the physics step runs directly after `FixedUpdate`, then trigger, collision and joint callbacks; `WaitForFixedUpdate` resumes at the end of the fixed step [eo]. Order between trigger and collision callbacks is not documented [eo] |
| Script step size | Pass a constant step; above 0.03 s is likely inaccurate, a frame-rate-dependent step is non-deterministic [sim] |
| Step source | One config value sets both `Time.fixedDeltaTime` (once at startup) and the Core step: a mismatch drifts Core time from physics time |
| Core time | Core derives time as tick index × step; never a float accumulator, which drifts |
| Timestamps | Prefer `Time.fixedTimeAsDouble` over `Time.fixedTime` [ft] |
| Render-rate test | `Time.captureDeltaTime` advances `Time.time` by a fixed amount per frame regardless of real time [cd] |

```csharp
using _Project.Scripts.Match.Core;
using _Project.Scripts.Match.DataModels;
using VContainer.Unity;

namespace _Project.Scripts.Match.DataControllers
{
    // The only call site that advances MatchSimulation (_Project.Scripts.Match.Core).
    public sealed class MatchTickDriver : IFixedTickable
    {
        private readonly MatchSimulation _simulation;
        private readonly CommandSampler _sampler;
        private readonly ContactBuffer _contacts;
        private readonly BodyApplier _bodies;
        private readonly MatchSnapshots _snapshots;
        private readonly float _stepSeconds;
        private int _tick;

        public MatchTickDriver(
            MatchSimulation simulation,
            CommandSampler sampler,
            ContactBuffer contacts,
            BodyApplier bodies,
            MatchSnapshots snapshots,
            TickSettings settings)
        {
            this._simulation = simulation;
            this._sampler = sampler;
            this._contacts = contacts;
            this._bodies = bodies;
            this._snapshots = snapshots;
            this._stepSeconds = settings.StepSeconds;
        }

        public void FixedTick()
        {
            PlayerCommand command = this._sampler.Consume();
            this._snapshots.ShiftCurrentToPrevious();
            this._simulation.Tick(this._tick, this._stepSeconds, command, this._contacts.Pending);
            this._contacts.Clear();
            // Core-owned quantities reach kinematic bodies before the physics step that follows.
            this._bodies.Apply(this._simulation.State);
            this._snapshots.CaptureCurrent(this._simulation.State);
            this._tick++;
        }
    }
}
```

Core seam: `public void Tick(int tick, float stepSeconds, PlayerCommand command, ReadOnlySpan<HitData> contacts)` on `MatchSimulation`; `ContactBuffer.Pending` is a `ReadOnlySpan<HitData>` over a preallocated array, valid until `Clear()`.

## Render-only interpolation

| Subject | Fact that decides |
|---|---|
| Snapshot pair | Owner copies view-relevant state to `previous` before the tick and `current` after; views read only these |
| Alpha (auto physics) | In `Update`/`LateUpdate`: `(Time.timeAsDouble - Time.fixedTimeAsDouble) / Time.fixedDeltaTime`, clamped to 0..1 (derived from the `fixedTime` definition [ft]) |
| Alpha (script physics) | Owner's accumulator remainder ÷ step |
| Lag | The view trails the newest tick by up to one step; extrapolating instead overshoots on direction changes |
| Teleport, respawn | A per-entity snap flag skips the lerp for that tick, else the view slides across the map |
| Rigidbody-driven view | `Rigidbody.interpolation` (`unity-3d-physics`), never a second hand-written lerp on the same Transform |
| Networked remote entities | Snapshot interpolation belongs to the stack (`NetworkTransform`, NfE interpolated ghosts), not to this pair |

Unverified: order of VContainer `FixedTick` relative to `MonoBehaviour.FixedUpdate` in the same step (VContainer says only "nearly"); whether fixed steps follow `Time.captureDeltaTime` game time exactly (the page does not mention `FixedUpdate`).
