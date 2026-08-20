---
name: r3-reactive-extensions
description: >
  Technique for modeling continuous, composable streams of discrete events
  over time in Unity with R3 — `Observable<T>`/`Observer<T>`, `Subject<T>`,
  `ReactiveProperty<T>`/`SerializableReactiveProperty<T>`, `TimeProvider`/
  `FrameProvider`-based operators (`IntervalFrame`, `DelayFrame`), and
  `AddTo`/`DisposableBag`/`CompositeDisposable` disposal composition — the
  successor to UniRx built for modern .NET. Use this for state or events a
  caller needs to filter/combine/transform and subscribe to *continuously*
  (health changed, input stream, cooldown ticking down, UI data binding). Do
  not use this for a one-shot asynchronous operation with a definite
  completion (an animation finishing, a network call returning) — that's
  `unitask-async-programming`; R3's own `SubscribeAwait`/`SelectAwait`
  operators consume `UniTask` internally for the async leg of a pipeline, so
  the two compose rather than compete. Do not use this for a discrete,
  addressed message dispatched once between decoupled systems (an
  "ItemPickedUp" notification, a request/response call) — that's
  `messagepipe-event-messaging`; R3 models a continuous stream a subscriber
  composes over time, MessagePipe models a single routed message. The two
  are frequently used together (a `Subject<T>` feeding both an `Observable`
  pipeline and a `MessagePipe` publish) but solve different problems — don't
  default to R3 just because "it's reactive-sounding." Do not use this to
  decide where a subscription's lifetime is scoped in the DI object graph —
  that's `vcontainer-dependency-injection`; this skill only covers writing
  the observable pipeline and disposing it correctly once scope is decided.
  Never put an `Observable<T>` pipeline in `Game.Core.*` — the Unity-targeted
  R3 package (`R3.Unity`, `SerializableReactiveProperty`, `FrameProvider`)
  depends on `UnityEngine`; a Core state change should be exposed as a plain
  C# event/callback and turned into an `Observable` from `Game.Client.*`.
---

# R3 — Reactive Extensions for Continuous Event Streams

Source: [github.com/Cysharp/R3](https://github.com/Cysharp/R3).

## 1. Objective
Model continuous, composable streams of state/events (health, input, cooldowns, UI bindings) as `Observable<T>` pipelines that compose cleanly with LINQ-style operators — without leaking a subscription, double-disposing a `DisposableBag`, or reaching for R3 when a one-shot async await or a single routed message would do.

## 2. Role
Act as the reactive-programming specialist for the client track — the tool Unity Engineer and UI/UX Programmer reach for whenever UI or gameplay feedback needs to react continuously to a changing value rather than poll it every frame or handle a single fire-once notification.

## 3. When to invoke this skill
- Binding UI directly to a changing gameplay value (health bar to `ReactiveProperty<int> Health`, cooldown ring to a ticking value) so the UI updates only when the value actually changes, per `performance-and-algorithms.md`'s "only update UI when the value changed" rule.
- Composing/filtering an input or event stream with LINQ-style operators (`Where`, `Select`, `Throttle`, `DistinctUntilChanged`) instead of hand-rolled per-frame polling in `Update()`.
- Using `IntervalFrame`/`DelayFrame` (Unity's frame-count-based timing) instead of wall-clock `TimeProvider` operators, when the semantics should be "every N frames" rather than "every N seconds."
- Negative trigger: a one-shot async operation with a definite completion — that's `unitask-async-programming`, though R3's `SubscribeAwait`/`SelectAwait` will call into it for the async leg of a pipeline.
- Negative trigger: a discrete, addressed message dispatched once between decoupled systems, or a request/response call — that's `messagepipe-event-messaging`.
- Negative trigger: deciding a subscription's lifetime scope inside the DI object graph — that's `vcontainer-dependency-injection`; this skill only writes/disposes the pipeline once that scope exists.
- Negative trigger: any `Game.Core.*` code — the Unity-facing R3 package depends on `UnityEngine`; expose a Core state change as a plain C# event and adapt it to `Observable<T>` from `Game.Client.*`.

## 4. How to use this skill
1. **Model the source correctly.** `Subject<T>` for an imperatively-pushed event; `ReactiveProperty<T>` (or `SerializableReactiveProperty<T>` for an Inspector-bindable field) for a value with current state that new subscribers should immediately receive.
2. **Compose with operators, not manual state tracking.** `Where`/`Select`/`DistinctUntilChanged`/`Throttle`/`CombineLatest` read as a short narrative of the transformation — per SLAP in `coding-principles.md` — instead of an imperative chain of `if`s inside a hand-written callback.
3. **Pick `TimeProvider` vs `FrameProvider` deliberately.** Frame-based timing (`IntervalFrame`, `DelayFrame`) for anything that should track Unity's actual update cadence (animation-adjacent, gameplay-tick-adjacent); wall-clock `TimeProvider` timing only when real elapsed time (not frame count) is the actual semantic, e.g. a UI toast auto-dismiss.
4. **Dispose deliberately, every time.** Use `.AddTo(ref disposableBag)`/`.AddTo(this)` (for a `MonoBehaviour`/`Component` target) or `Disposable.CreateBuilder()` for a fixed, known set of static subscriptions — an undisposed subscription keeps its whole capture graph alive, exactly the concern `performance-and-algorithms.md`'s Memory discipline section raises for event handlers generally.
5. **Treat `OnErrorResume` as deliberate control flow, not an afterthought.** R3's redesigned error model means an exception doesn't silently terminate the subscription the way classic Rx.NET does — decide explicitly whether a pipeline should recover and keep observing or shut down, and say so in the handoff.
6. **Don't reimplement MessagePipe with a `Subject<T>`.** If the actual requirement is "notify decoupled system B that event X happened once, with no ongoing composition," that's a single routed message — hand it to `messagepipe-event-messaging` instead of building an ad hoc `Subject<T>` bus.
7. **Verify with `ObservableTracker`** (or equivalent) when subscription leaks are suspected, rather than guessing from code inspection alone — R3 ships tracking support specifically because long-lived game sessions make a leaked subscription's effect (a stale reference kept alive) hard to spot from a single frame's behavior.

## 5. Specific goals / tasks this skill performs
- Turning a plain field or event into a `ReactiveProperty<T>`/`Observable<T>` pipeline UI can subscribe to directly.
- Composing input/state streams with LINQ-style operators instead of per-frame polling logic in `Update()`.
- Choosing and wiring `FrameProvider`- vs `TimeProvider`-based timing operators correctly.
- Auditing subscription disposal (`AddTo`/`DisposableBag`) for leaks tied to a `MonoBehaviour`'s lifetime.
- Out of scope: one-shot async awaits (`unitask-async-programming`), discrete cross-system message dispatch (`messagepipe-event-messaging`), DI-scoped subscription lifetime decisions (`vcontainer-dependency-injection`), any use inside `Game.Core.*`.

## 6. Output format
```
## R3 Work — <stream/binding name>
- Source: Subject<T> / ReactiveProperty<T> / SerializableReactiveProperty<T> — rationale
- Operators applied: <Where/Select/Throttle/DistinctUntilChanged/CombineLatest/...>
- Timing: FrameProvider (frame-based) / TimeProvider (wall-clock) / none — rationale
- Disposal: AddTo(this) / DisposableBag / Disposable.CreateBuilder() — scope
- Error handling: OnErrorResume behavior decided — <recover and continue / terminate>
- Layer: Game.Client.* (never Game.Core.*)
- Known limitations: <...>
```

## 7. Examples
**Example 1**
- Input: the HUD health bar should update only when health actually changes, and should animate a brief flash on decrease.
- Output: exposed Shared Core's health value through a `ReactiveProperty<int>` on the client-side view model, subscribed with `.Pairwise().Where(t => t.Current < t.Previous)` to trigger the flash only on a decrease, `.AddTo(this)` tying the subscription to the HUD component's lifetime; verified no unconditional per-frame text rebuild remained.

**Example 2**
- Input: "use R3 to broadcast a one-time 'boss defeated' event to the achievement system and the analytics system."
- Output: declined — a single fire-once notification to decoupled subscribers is `messagepipe-event-messaging`'s `IPublisher<BossDefeated>`/`ISubscriber<BossDefeated>`, not an ongoing `Observable` composition; recommended that skill instead.

## 8. Edge cases & guardrails
- Never leave a subscription without a disposal path — every `.Subscribe(...)` needs an `.AddTo(...)` or equivalent, tied to a real lifetime scope.
- Never default to R3 for a single, discrete, addressed message between systems — that's MessagePipe's job even though both are "eventing."
- Never put `R3`/`R3.Unity` types in `Game.Core.*` — it's a `UnityEngine`-dependent package; expose Core state as a plain event and adapt from Client.
- Don't mix `TimeProvider` (wall-clock) and `FrameProvider` (frame-count) semantics carelessly — pick the one that matches the actual game-design intent (real elapsed time vs. frame cadence).
- Don't let `OnErrorResume` behavior be accidental — decide and document whether a pipeline recovers or terminates on error.
