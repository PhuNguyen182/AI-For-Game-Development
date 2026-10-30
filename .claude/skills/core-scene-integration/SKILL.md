---
name: core-scene-integration
description: "Core to scene wiring: one tick owner (VContainer IFixedTickable or one MonoBehaviour), injected tick time, per-tick input command, physics results as plain data, read-only views, render-only interpolation. Use when hooking Core into a scene."
user-invocable: false
---

# Core Scene Integration

Not for: the Core rule itself (`csharp-engineer`), auditing Core for `UnityEngine` or wall-clock leaks (`shared-core-boundary-audit`), float agreement and replay hashing (`core-determinism`), Core tests without a scene (`core-tests-without-unity`), the netcode tick, prediction and remote-entity snapshot interpolation (`netcode-engineer`, `netcode-for-gameobjects`, `netcode-for-entities`), action maps, bindings and Update Mode (`unity-input-system`), Rigidbody and collider setup (`unity-3d-physics`, `unity-2d-physics`), container registration (`vcontainer-dependency-injection`), fanning Core state changes out as events or streams (`messagepipe-event-messaging`, `r3-reactive-extensions`), UI binding (`ui-engineer`).
Docs: https://docs.unity.com/en-us/engine/current/ (Manual `manual/...`, API `script-reference/unityengine/...`; old docs.unity3d.com links redirect here) — unversioned, tracks the current release: re-check in the project's Editor. VContainer entry points: https://vcontainer.hadashikick.jp/integrations/entrypoint (unversioned).

| Reference | Read when |
|---|---|
| [tick-and-interpolation.md](references/tick-and-interpolation.md) | Choosing or wiring the tick owner, ordering a tick against the physics step, or a view jitters, lags or slides between ticks |
| [input-and-physics-into-core.md](references/input-and-physics-into-core.md) | A press is missed or doubled, or a Core rule needs a raycast, overlap or contact result |

## Steps
1. **Name the one tick owner** — multiplayer on (`CLAUDE.md`): the netcode stack owns the tick and `netcode-engineer` wires it, this skill covers only the input and view side. Otherwise VContainer in `Packages/manifest.json` → one `IFixedTickable` registered with `RegisterEntryPoint<T>()`; no VContainer → one driver MonoBehaviour. Per [tick-and-interpolation.md](references/tick-and-interpolation.md). Done when exactly one call site advances each Core simulation; per-object `FixedUpdate` calls into Core are folded into the owner.
2. **Inject time into Core as a value** — the owner passes the tick index and the fixed step; Core never reads `Time.*` (rule `csharp.md` Boundaries). The Core API takes no time parameter → `Blocked`, `Next: csharp-engineer`. Done when the Core call signature has no `UnityEngine` type.
3. **Sample input into one per-tick command struct** — latch in the frame loop, consume and clear in the tick, per [input-and-physics-into-core.md](references/input-and-physics-into-core.md). Done when a press in a frame with zero fixed steps reaches the next tick exactly once, and a frame with two fixed steps does not deliver it twice.
4. **Decide per quantity who owns it** — Core-owned (Core output drives a kinematic body) or physics-owned (a simulated body's result fed back as data); one owner each, per [input-and-physics-into-core.md](references/input-and-physics-into-core.md). Spec silent on a quantity both could own → `Needs-decision`, `Next: technical-architect`.
5. **Resolve physics on the client, pass plain data** — raycasts, overlaps and contacts become Core structs with Core entity ids; Core never sees `Collider`, `GameObject` or `Vector3`. Same reference. Done when every physics input in the tick signature is a Core type.
6. **Order the tick** — command + physics queries + physics-owned reads → Core tick → apply Core output to bodies → physics step → buffer contacts for the next tick, per [tick-and-interpolation.md](references/tick-and-interpolation.md). Done when each contact is consumed by exactly one tick.
7. **Views read Core state, never write it** — a view depends on a read-only interface or snapshot published after the tick; a view that wants a change sends it through the command struct or asks the owner. A view doing outcome arithmetic is a restated rule → `shared-core-boundary-audit`.
8. **Interpolate for rendering only** — lerp between the previous and current snapshot by the render alpha; never feed the interpolated value back to Core or physics, per [tick-and-interpolation.md](references/tick-and-interpolation.md). A Rigidbody-driven view uses `Rigidbody.interpolation` instead, never both. Done when Core state is identical with interpolation on and off.
9. **Verify frame-rate independence** — the same command sequence at two render rates (e.g. `Time.captureDeltaTime` 1/30 and 1/144) reaches the same Core state at the same tick, and the view shows no stutter at the low rate. A Play Mode test (`unity-test-framework`) or a playtest (`playtest-scenario-execution`); neither run → `Verified: not run`.

## Never
- Mutate Core state from an async continuation, event callback or physics callback outside the tick — it lands at an arbitrary PlayerLoop point between ticks; queue it into the next tick's input.
- Advance Core from `Update` with `Time.deltaTime` for smoothness — outcomes then depend on frame rate and diverge from server and replay; smoothness is step 8's job.

## Output
```
## Core Scene Integration — <feature / scene>
- Tick owner: <IFixedTickable type / driver MonoBehaviour / netcode stack> — <rate Hz>
- Time into Core: <tick index + fixed step, how passed>
- Input: <command struct; latch point; consume point>
- Ownership: <quantity — Core-owned / physics-owned>
- Physics → Core: <query/contact → Core struct; buffer cleared when>
- Views: <read-only interface or snapshot consumed; no writes>
- Interpolation: <snapshot pair + alpha source / Rigidbody interpolation / none>
- Verified: <frame-rate test or playtest, or "not run">
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Put `health -= damage` in the enemy's `OnCollisionEnter`, it's one line" → declined: a rule in a view, run mid physics step. The contact is buffered as a `HitData` and the Core damage rule applies it on the next tick.
