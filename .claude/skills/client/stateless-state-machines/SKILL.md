---
name: stateless-state-machines
description: >
  Technique for modeling explicit state machines with Stateless-For-Unity —
  `StateMachine<TState,TTrigger>`, `Configure(state).Permit(trigger,
  destination)`/`PermitIf`, `OnEntry`/`OnExit`, substates
  (`SubstateOf`)/hierarchical states, and the fork's optional
  `OnEntryAsync`/`FireAsync` (UniTask-backed, requires the UniTask package).
  Use this whenever a `switch`/bool-flag-driven state machine is emerging by
  hand (an ability's charge/cooldown/active states, a UI flow's
  screen-transition graph, an enemy AI's behavior states) — per Open/Closed
  in `coding-principles.md`, an explicit state machine keeps adding a new
  state/transition additive instead of another branch in a growing
  conditional. The plain synchronous API (`Configure`/`Permit`/`Fire`,
  `OnEntry`/`OnExit`) has no `UnityEngine` dependency and belongs in
  `Game.Core.*` for a state machine that is itself game-rule logic (e.g. an
  ability's state graph the server must also validate); the async
  `*Async`/`FireAsync` surface pulls in the UniTask package, which depends
  on `UnityEngine`, so it is `Game.Client.*`-only — reserve it for
  client-only state machines (a UI flow, a client-side animation-driven
  presentation state) that the server never needs to mirror. Do not use
  this for a continuous value stream — that's `r3-reactive-extensions`. Do
  not use this to write the actual `async` bodies inside `OnEntryAsync`
  callbacks — that's `unitask-async-programming`; this skill only decides
  the state graph and which transitions are async.
---

# Stateless-For-Unity — Explicit State Machines

Source: [github.com/CorundumGames/Stateless-For-Unity](https://github.com/CorundumGames/Stateless-For-Unity) (a fork of [dotnet-state-machine/stateless](https://github.com/dotnet-state-machine/stateless) that swaps `Task` for `UniTask` in its optional async surface).

## 1. Objective
Replace an emerging `switch`/bool-flag state machine with an explicit `StateMachine<TState,TTrigger>` graph — states, triggers, guards, entry/exit actions — without accidentally pulling a `UnityEngine` dependency into a Shared Core state machine that needs to stay server-mirrorable, and without modeling something that isn't actually state-machine-shaped just because the library is available.

## 2. Role
Act as the state-machine-design specialist for the client track: the one who models a system's states and legal transitions explicitly, whether that system belongs in `Game.Core.*` (an ability's state graph) or `Game.Client.*` (a UI flow).

## 3. When to invoke this skill
- A hand-rolled state machine is emerging as a growing `switch` on an enum or a spreading set of interacting bool flags (`isCharging`, `isOnCooldown`, `isActive`) — per Open/Closed in `coding-principles.md`, this is the signal to introduce an explicit `StateMachine<TState,TTrigger>` instead of another branch.
- Modeling a UI screen-flow graph (menu → settings → confirm-dialog → back) where the legal transitions matter and an invalid one should be caught rather than silently allowed.
- Modeling an ability's charge/active/cooldown state graph, or an enemy AI's behavior states, especially when the same graph needs the server to validate the same transitions (per `server-authoritative-engineer`'s "reference Shared Core, never reimplement" rule) — this is exactly why the graph belongs in `Game.Core.*` using the plain synchronous API.
- Using `SubstateOf` to express a hierarchical state relationship (e.g. "Stunned" as a substate of "Active" that inherits its exit behavior) instead of duplicating exit logic across sibling states.
- Negative trigger: a continuous value stream a subscriber composes/observes over time — that's `r3-reactive-extensions`; a state machine models discrete named states and legal transitions between them, not an arbitrary value's evolution.
- Negative trigger: writing the actual async logic inside an `OnEntryAsync` callback — that's `unitask-async-programming`; this skill only decides that a transition's entry action is async and what state graph it belongs to.
- Negative trigger: the states don't actually have meaningfully different legal-transition rules from each other — a state machine over two states with no real guard/transition logic is over-engineering a simple bool (YAGNI).

## 4. How to use this skill
1. **Decide the layer before writing a line of configuration.** If the state graph is game-rule logic the server must also validate (an ability, a match/round flow), it belongs in `Game.Core.*` using only the plain synchronous `Configure`/`Permit`/`Fire`/`OnEntry`/`OnExit` API — never the `*Async` surface, since that pulls in UniTask's `UnityEngine` dependency and would break the Shared Core boundary in `coding-principles.md`. If it's presentation/UI-only and the server never needs to know about it, `Game.Client.*` is fine, and the async surface is available there.
2. **Enumerate states and triggers as named types** (an enum, per `naming-convention.md`'s casing rules), not magic strings/ints — `Configure(State.Charging).Permit(Trigger.Release, State.Active)` reads as a short, explicit narrative of the legal graph.
3. **Use `PermitIf` for guarded transitions** (a trigger that's only legal under a condition, e.g. enough charge accumulated) instead of allowing the transition unconditionally and checking the guard inside the destination state's `OnEntry` — keep the legality check where the library expresses it, not scattered into entry actions.
4. **Put side effects in `OnEntry`/`OnExit`, not in the code that calls `Fire`.** The caller's job is "this trigger happened"; the state machine's job is "here's what happens on entering/leaving a state" — mixing the two back into the call site reintroduces the same tangled logic the state machine was meant to replace.
5. **Use `SubstateOf` for genuine hierarchical behavior sharing** (multiple states that all exit the same way, or share a common superstate's entry logic) instead of duplicating that logic across each sibling state.
6. **Reserve `OnEntryAsync`/`FireAsync` for `Game.Client.*`-only state machines**, and write the async body itself per `unitask-async-programming`'s guidance (cancellation, `.Preserve()` if needed) rather than reinventing async handling inside the state machine's own callback.
7. **Keep the machine single-threaded, by design.** Stateless (and this fork) isn't thread-safe internally — never call `Fire`/`FireAsync` from more than one thread/coroutine context concurrently; funnel all triggers through one owner.

## 5. Specific goals / tasks this skill performs
- Converting a hand-rolled `switch`/bool-flag state machine into an explicit `StateMachine<TState,TTrigger>` graph.
- Deciding whether a given state machine belongs in `Game.Core.*` (sync-only API) or `Game.Client.*` (async surface allowed).
- Modeling guarded transitions (`PermitIf`) and hierarchical states (`SubstateOf`).
- Placing side effects correctly in `OnEntry`/`OnExit` rather than at `Fire` call sites.
- Out of scope: continuous value streams (`r3-reactive-extensions`), the async body behind an `OnEntryAsync` callback (`unitask-async-programming`), a two-state system with no real transition logic (YAGNI — just use a bool).

## 6. Output format
```
## Stateless Work — <system name>
- Layer: Game.Core.* (sync-only API) / Game.Client.* (async surface allowed) — rationale
- States: <enum listing>
- Triggers: <enum listing>
- Transitions: <state -> trigger -> state, guards (PermitIf) noted>
- Substates: <SubstateOf relationships, or "none">
- Side effects: <OnEntry/OnExit actions per state>
- Async usage: <OnEntryAsync/FireAsync — yes/no, and why layer allows it>
- Known limitations: <...>
```

## 7. Examples
**Example 1**
- Input: an ability's behavior is controlled by `isCharging`/`isOnCooldown`/`isActive` bools with growing cross-checks between them, and the server needs to validate the same rules.
- Output: modeled `StateMachine<AbilityState, AbilityTrigger>` in `Game.Core.*` with states `Idle → Charging → Active → Cooldown → Idle`, `PermitIf(Trigger.Release, State.Active, () => chargeAccumulated >= MinCharge)`, cooldown-remaining tracked as `OnEntry` state on the `Cooldown` state; `server-authoritative-engineer` validates ability triggers against the exact same Shared Core graph instead of reimplementing the rules.

**Example 2**
- Input: a settings menu's screen flow (Main → Settings → ConfirmDiscard → Main/Settings) needs an async fade transition on each screen change.
- Output: modeled in `Game.Client.*` since it's UI-only and the server never needs it; used `OnEntryAsync(async () => await FadeInAsync(ct))` with the UniTask package installed, the fade body itself written per `unitask-async-programming`'s cancellation guidance.

## 8. Edge cases & guardrails
- Never use the `*Async`/`FireAsync` surface inside `Game.Core.*` — it pulls in UniTask's `UnityEngine` dependency and breaks the Shared Core boundary in `coding-principles.md`.
- Never call `Fire`/`FireAsync` concurrently from more than one thread/coroutine — the state machine isn't internally thread-safe.
- Never put a transition's side effect at the `Fire` call site instead of in `OnEntry`/`OnExit` — that reintroduces the tangled logic the state machine exists to remove.
- Never model a two-state, no-real-transition-logic case with this library — that's a bool, not a state machine (YAGNI).
- Never let a guard condition live inside a destination state's `OnEntry` when `PermitIf` already expresses "this transition is illegal under condition X" directly.
