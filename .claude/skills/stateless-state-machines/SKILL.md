---
name: stateless-state-machines
description: "Explicit state machines with Stateless: Configure/Permit/PermitIf, entry/exit, substates, guards, parameterized triggers, DOT export. Use when behaviour is states and transitions rather than a formula."
user-invocable: false
---

# Stateless State Machines

Not for: a continuous value stream composed over time (`r3-reactive-extensions`), the async body inside `OnEntryAsync` (`unitask-async-programming`), a snapshot codec for the state (`source-generator-authoring`), an Animator Controller's clip-driving states (`unity-animation`; the logical graph here drives Animator parameters), an enum of kinds rather than states of one thing (`unity-scriptableobject-architecture`), a two-state case with no guards or transition rules, which is a bool (`csharp-standards` → `coding-principles.md` "YAGNI").

## Steps
1. **Use a machine when a `switch` grows a branch per feature, bools like `isCharging`/`isOnCooldown`/`isActive` cross-check each other, or a bug reduces to "in two states at once"** (`csharp-standards` → `coding-principles.md` "SOLID", Open/Closed).
2. **Settle the layer before the first `Configure`** — a graph the server validates belongs in a Core assembly and may use only the synchronous surface: async continuation order is not deterministic, and a UniTask-based Unity fork would also pull `UnityEngine` into Core (`csharp-standards` → `coding-principles.md` "Shared Core integrity"). Presentation-only graphs live in Client code, where async is allowed.
3. **Decide who owns the current state** — by default the machine stores it internally, unreachable. Use the external accessor form `new StateMachine<TState,TTrigger>(() => this.state, s => this.state = s)` whenever the state is snapshotted, restored or compared (rollback, server reconciliation, save data); retrofitting it later touches every consumer.
4. **Declare states and triggers as enums** (casing per `csharp-standards` → `naming-convention.md`): `Configure(AbilityState.Charging).Permit(AbilityTrigger.Release, AbilityState.Active)`.
5. **Decide what an unpermitted trigger does; the default throws `InvalidOperationException`** — an illegal trigger is normal in a game (mashing attack during cooldown). Choose `Ignore(trigger)` where it is meaningless, an `OnUnhandledTrigger` handler that logs and drops, or a `CanFire` check at the call site.
6. **Express legality with `PermitIf`; keep the guard pure** — `CanFire` and `GetPermittedTriggers` evaluate it too, so a guard with side effects runs an unpredictable number of times.
7. **Use `PermitReentry` or `Ignore` for a trigger targeting the current state** — plain `Permit` to the same state throws at configuration time. The design question is whether re-entering re-runs `OnEntry` or the trigger is dropped.
8. **Put side effects in `OnEntry`/`OnExit`, not at the `Fire` call site**, which only reports the trigger. A `Fire` inside an `OnEntry` is queued, not recursive: it runs after the current transition finishes.
9. **Use `SubstateOf` only for genuinely shared behaviour** (common exit, shared superstate entry work); a hierarchy for tidiness hides the effective transition set.
10. **Keep the machine off a per-entity hot path** — Stateless is dictionary- and delegate-backed and allocates per transition. Fine for one UI flow or one local player's ability; a standing allocation source across hundreds of entities per tick, where a hand-written switch is cheaper. Measure before scaling (`csharp-standards` → `performance-and-algorithms.md` "Verification").
11. **Reserve `OnEntryAsync`/`FireAsync` for Client code**, with the body per `unitask-async-programming`, cancelled when the owner is destroyed mid-transition.
12. **Funnel every `Fire` through one owner** — neither Stateless nor its Unity forks are thread-safe; a `Fire` from a background task or second coroutine corrupts state with no exception.
13. **When the graph is unclear, list the illegal transitions first**; that yields the state set faster and is what a reviewer can check. A transition whose legality is a design question → `Needs-decision`, `Next: gd`.

## Output
```
## Stateless Work — <system>
- Layer: Core (synchronous surface only) / Client (async allowed) — rationale
- State ownership: internal / external accessor — rationale
- States: <enum>
- Triggers: <enum>
- Transitions: <state -> trigger -> state; PermitIf guards noted>
- Unpermitted trigger: Ignore / OnUnhandledTrigger / CanFire — which and why
- Reentry: <PermitReentry / Ignore targets, or "none">
- Substates: <SubstateOf relationships, or "none">
- Side effects: <OnEntry/OnExit per state>
- Async usage: <OnEntryAsync/FireAsync and why the layer permits it, or "none">
- Transition frequency: <how often it fires; why allocation is acceptable>
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Put every enemy's AI on a Stateless machine, about 400 re-evaluating every tick" → declined at that scale: per-transition allocation across 400 entities is a standing per-frame source. Used it for the boss's ten-state graph, where transitions are rare, and kept trash mobs on a three-case switch.
