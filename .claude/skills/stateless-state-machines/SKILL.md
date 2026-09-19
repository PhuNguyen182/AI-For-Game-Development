---
name: stateless-state-machines
description: >
  Explicit state machines with Stateless-For-Unity:
  `StateMachine<TState,TTrigger>`, `Configure(state)` with
  `Permit`/`PermitIf`/`PermitReentry`/`Ignore`, `OnEntry`/`OnExit`, `SubstateOf`
  hierarchies, `CanFire`/`GetPermittedTriggers`, `OnUnhandledTrigger`, the
  external state-accessor constructor, and the fork's UniTask-backed
  `OnEntryAsync`/`FireAsync`. Use it when a growing `switch` on an enum, or a
  spread of interacting bool flags, has become the real state machine — an
  ability's cooldown graph, a UI screen flow, an enemy's behaviour states. Not for: a continuous value stream a subscriber composes
  over time (`r3-reactive-extensions`), the async body inside an `OnEntryAsync`
  (`unitask-async-programming`), generating a snapshot codec for that state
  (`source-generator-authoring`), a two-state case with no real transition
  rules, which is a bool (`coding-principles.md`).
---

# Stateless-For-Unity — Explicit State Machines

## 1. Objective
Replace an emerging `switch`/bool-flag state machine with a declared `StateMachine<TState,TTrigger>` graph — states, triggers, guards, entry and exit actions — without pulling a `UnityEngine` dependency into a Shared Core machine the server must mirror, without the library's default throw-on-unpermitted-trigger turning ordinary input timing into an exception, and without placing a per-transition-allocating structure on a path that runs for hundreds of entities per tick.

## 2. Role
Act as the state-machine design specialist for the client track: the one who decides which states exist, which transitions are legal, who owns the current state, and which layer the graph belongs to — whether that is `Game.Core.*` for an ability or `Game.Client.*` for a UI flow.

## 3. When to invoke this skill
- A `switch` on a state enum keeps growing a branch per feature, or bools like `isCharging`/`isOnCooldown`/`isActive` have started cross-checking each other — per Open/Closed in `coding-principles.md`, that is the signal to declare the graph instead of branching again.
- Modeling a UI screen flow where illegal transitions should be rejected rather than silently allowed.
- Modeling an ability or match-round graph the server must validate against the same rules, which puts it in `Game.Core.*` per the Shared Core rule.
- Expressing a hierarchical relationship — a "Stunned" substate that inherits "Active"'s exit behaviour — instead of duplicating that behaviour across siblings.
- A symptom: a bug that reduces to "the object was in two states at once", or "this transition should have been impossible".
- Negative trigger: a value evolving continuously that subscribers compose over time — that's `r3-reactive-extensions`; this skill models discrete named states and the legal moves between them.
- Negative trigger: the async work inside an `OnEntryAsync` callback — that's `unitask-async-programming`; this skill only decides which transitions are async.
- Negative trigger: generating snapshot/restore code for the state field — that's `source-generator-authoring`; this skill decides the state is externally held, not how its codec is emitted.
- Negative trigger: two states with no real guard or transition rules — that is a bool, and building a machine for it is the speculative complexity YAGNI forbids in `coding-principles.md`.

## 4. How to use this skill
1. **Settle the layer before writing the first `Configure` call** — a graph that is game-rule logic the server validates belongs in `Game.Core.*` and may use only the synchronous surface, because the `*Async` methods pull in UniTask, which depends on `UnityEngine` and would break the Shared Core boundary in `coding-principles.md`. Presentation-only graphs live in `Game.Client.*`, where the async surface is available.
2. **Decide who owns the current state before configuring transitions** — by default the machine stores it internally, where nothing outside can read or write it. Construct it with the external accessor form, `new StateMachine<TState,TTrigger>(() => this.state, s => this.state = s)`, whenever the state has to be snapshotted, restored, or compared: rollback prediction, server reconciliation, and save data all need the value in a field they can reach. Retrofitting this after the graph ships means touching every consumer.
3. **Declare states and triggers as enums**, per `naming-convention.md`'s casing table — `Configure(AbilityState.Charging).Permit(AbilityTrigger.Release, AbilityState.Active)` reads as the legal graph itself, where magic strings or ints read as nothing.
4. **Decide what an unpermitted trigger does, because the default is to throw** — firing an illegal trigger is a normal event in a game, not a programming error: a player mashes attack during cooldown every single match. Choose deliberately between `Ignore(trigger)` on states where it is explicitly meaningless, an `OnUnhandledTrigger` handler that logs and drops, and a `CanFire` check at the call site. Leaving `InvalidOperationException` as the answer makes ordinary input timing crash.
5. **Express legality with `PermitIf` and keep the guard pure** — a guard belongs where the library evaluates transition legality, not inside the destination's `OnEntry`. It must be free of side effects, because `CanFire` and `GetPermittedTriggers` evaluate it too, and a guard that mutates state runs an unpredictable number of times.
6. **Use `PermitReentry` or `Ignore` for a trigger that targets the current state** — plain `Permit` to the same state throws at configuration time, which surfaces as a startup crash rather than as the design question it actually is: should re-entering re-run `OnEntry`, or should the trigger be dropped?
7. **Put side effects in `OnEntry`/`OnExit` rather than at the `Fire` call site** — the caller's only job is to report that a trigger happened. Note that firing a trigger from inside an `OnEntry` is queued, not recursive: it runs after the current transition finishes, so entry actions that chain transitions complete in an order the call stack does not show.
8. **Use `SubstateOf` only for genuine shared behaviour** — several states that exit the same way, or share a superstate's entry work. A hierarchy introduced for tidiness alone makes the effective transition set harder to read than the duplication it removed.
9. **Keep the machine off a per-entity hot path** — Stateless is dictionary- and delegate-backed and allocates per transition. That cost is irrelevant for one UI flow or one local player's ability, and it is a real per-tick allocation source across hundreds of entities. Per `performance-and-algorithms.md`'s Verification section, measure before scaling one out; at that N a hand-written switch is the cheaper structure and KISS already prefers it.
10. **Reserve `OnEntryAsync`/`FireAsync` for `Game.Client.*` graphs**, writing the body itself per `unitask-async-programming`, including cancelling it when the owning object is destroyed mid-transition.
11. **Funnel every trigger through a single owner** — neither Stateless nor this fork is internally thread-safe, so a `Fire` from a background task or a second coroutine can corrupt the machine's state with no exception to show for it.
12. **Enumerate the illegal transitions first when the graph is unclear** — listing what must never happen produces the state set faster than listing what should, and it is the part a reviewer can actually check. Ask rather than assume when a transition's legality is a design question.

## 5. Specific goals / tasks this skill performs
- Converting a `switch`/bool-flag state machine into a declared `StateMachine<TState,TTrigger>` graph.
- Choosing the layer (`Game.Core.*`, synchronous surface only, or `Game.Client.*`) and justifying it.
- Choosing internal versus external state ownership against snapshot, rollback, and save requirements.
- Defining unpermitted-trigger behaviour via `Ignore`/`OnUnhandledTrigger`/`CanFire` instead of accepting the default throw.
- Modeling guarded transitions (`PermitIf`), reentry (`PermitReentry`), and hierarchies (`SubstateOf`).
- Out of scope: continuous value streams (`r3-reactive-extensions`), the async body behind `OnEntryAsync` (`unitask-async-programming`), snapshot codec generation (`source-generator-authoring`), a two-state case that is a bool (`coding-principles.md`).

## 6. Output format
```
## Stateless Work — <system name>
- Layer: Game.Core.* (synchronous surface only) / Game.Client.* (async allowed) — rationale
- State ownership: internal / external accessor — rationale (snapshot, rollback, save)
- States: <enum listing>
- Triggers: <enum listing>
- Transitions: <state -> trigger -> state; PermitIf guards noted>
- Unpermitted trigger: Ignore / OnUnhandledTrigger / CanFire at call site — which and why
- Reentry: PermitReentry / Ignore targets, or "none"
- Substates: <SubstateOf relationships, or "none">
- Side effects: <OnEntry/OnExit per state>
- Async usage: <OnEntryAsync/FireAsync, and why the layer permits it — or "none">
- Transition frequency: <how often it fires; allocation acceptable because ...>
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what the graph does not model — omit this line entirely if there are genuinely none>
- Latent concerns: <transitions never exercised, guards assumed pure, entity counts not yet reached>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: an ability is driven by `isCharging`/`isOnCooldown`/`isActive` with growing cross-checks, and the server must validate the same rules.
- Output: `StateMachine<AbilityState, AbilityTrigger>` in `Game.Core.*` over `Idle → Charging → Active → Cooldown → Idle`, with `PermitIf(AbilityTrigger.Release, AbilityState.Active, () => this.charge >= MinCharge)`. Built with the external accessor form so reconciliation can restore the state directly, and `Ignore(AbilityTrigger.Press)` on `Cooldown` so mashing input during cooldown is a no-op instead of an exception. `server-authoritative-engineer` validates against this graph rather than reimplementing it.

**Example 2**
- Input: "put every enemy's AI on a Stateless machine — there are about 400 of them and they re-evaluate every tick."
- Output: declined at that scale. Stateless allocates per transition, so 400 entities transitioning per tick is a standing per-frame allocation source `performance-and-algorithms.md` rules out. Used it for the boss's ten-state graph, where transitions are rare and the clarity pays, and kept the trash mobs on a three-case switch.

**Example 3**
- Input: a settings flow (Main → Settings → ConfirmDiscard → back) needs an async fade on each screen change.
- Output: modeled in `Game.Client.*` since the server never sees it, using `OnEntryAsync` for the fade with the body written per `unitask-async-programming` and cancelled on destroy. Internal state ownership was fine here — nothing snapshots a menu.

## 8. Edge cases & guardrails
- Never use `OnEntryAsync`/`FireAsync` inside `Game.Core.*` — it pulls UniTask's `UnityEngine` dependency across the Shared Core boundary.
- Never leave the default throw in place for an unpermitted trigger in gameplay code — ordinary input timing will hit it, and it crashes rather than declines.
- Never write a guard with side effects — `CanFire` and `GetPermittedTriggers` evaluate guards too, an unpredictable number of times per fire.
- Never call `Fire`/`FireAsync` from more than one thread or coroutine context — the machine is not internally thread-safe and corrupts silently.
- Never put a transition's side effect at the `Fire` call site — that rebuilds the tangled logic the machine was introduced to remove.
- Never choose internal state ownership for a graph that rollback, reconciliation, or save data must read — retrofitting the accessor form later touches every consumer.
- Never scale a Stateless machine across hundreds of per-tick entities without measuring — per-transition allocation is the cost, and a switch is cheaper at that N.
