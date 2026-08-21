---
name: r3-reactive-extensions
description: >
  R3 — reactive streams for Unity and the UniRx successor: `Observable<T>`,
  `Observer<T>`, `Subject<T>`, `ReactiveProperty<T>`,
  `SerializableReactiveProperty<T>`, operators (`Where`, `Select`,
  `DistinctUntilChanged`, `Throttle`, `CombineLatest`, `Pairwise`,
  `SelectMany`, `Switch`), frame-based `FrameProvider` timing (`IntervalFrame`,
  `DelayFrame`) versus wall-clock `TimeProvider`, the `OnErrorResume` error
  model, and `AddTo`/`DisposableBag`/`ObservableTracker`. Use for a
  continuously observed value or event stream — health changing, an input
  stream, a cooldown ticking, UI data binding. `Game.Client.*` only.
  Not for: one-shot awaits (`unitask-async-programming`), single addressed messages (`messagepipe-event-messaging`), subscription lifetime scoping in DI (`vcontainer-dependency-injection`), formatting the text a sink writes (`zstring-zero-allocation-strings`).
---

# R3 — Reactive Extensions for Continuous Event Streams

## 1. Objective
Model continuously observed state and event streams as composable `Observable<T>` pipelines — without leaking a subscription past its owner's lifetime, multiplying subscriptions through a nested `Subscribe`, or reaching for a stream where a one-shot await or a single routed message was the actual shape of the problem.

## 2. Role
Act as the reactive-programming specialist for the client track — the tool Unity Engineer and UI/UX Programmer reach for when UI or gameplay feedback must react to a changing value rather than poll it every frame, and the one responsible for that pipeline's disposal.

## 3. When to invoke this skill
- Binding UI to a changing gameplay value so it updates only when the value actually changes, satisfying `performance-and-algorithms.md`'s rule against unconditional per-frame UI rebuilds.
- Composing or filtering an input or state stream with operators instead of hand-rolled polling and flag tracking inside `Update()`.
- Timing that should follow Unity's frame cadence rather than wall-clock seconds, or the reverse, where the distinction changes behaviour under a frame-rate drop.
- Auditing an existing pipeline for leaked subscriptions after a scene reload or a long session.
- Negative trigger: a one-shot operation with a definite completion — an animation finishing, an RPC returning — that is `unitask-async-programming`. R3's `SubscribeAwait` and `SelectAwait` consume UniTask internally, so the two compose rather than compete.
- Negative trigger: one discrete addressed message delivered once to decoupled systems — that is `messagepipe-event-messaging`; R3 models a stream a subscriber composes over time.
- Negative trigger: deciding where a subscription's lifetime is scoped in the DI object graph — that is `vcontainer-dependency-injection`; this skill writes and disposes the pipeline once the scope exists.
- Negative trigger: how the sink builds its display string — that is `zstring-zero-allocation-strings`, downstream of the stream decision.
- Negative trigger: any `Game.Core.*` code — the Unity-facing package depends on `UnityEngine`, which `coding-principles.md`'s Shared Core integrity section forbids in Core. Expose Core state as a plain C# event and adapt it to an `Observable<T>` from `Game.Client.*`.

## 4. How to use this skill
1. **Choose the source by whether new subscribers need the current value**, per the [R3 documentation](https://github.com/Cysharp/R3) — `Subject<T>` for an imperatively pushed event with no retained state, `ReactiveProperty<T>` for a value a late subscriber must receive immediately, and `SerializableReactiveProperty<T>` when the Inspector has to bind it.
2. **Do not stack `DistinctUntilChanged` on a `ReactiveProperty<T>` by reflex** — the property already suppresses equal values through its equality comparer, so the extra operator is a redundant link that reads as though duplicates were expected. Supply an explicit comparer instead when the value type has no meaningful default equality.
3. **Compose with operators rather than manual state tracking** — a chain of `Where`, `Select`, `Pairwise`, and `CombineLatest` reads as one narrative at a single level of abstraction, which is what SLAP in `coding-principles.md` asks for, where an imperative tangle of flags inside a callback does not.
4. **Never call `Subscribe` inside another `Subscribe`** — each outer emission creates a fresh inner subscription that nothing disposes, so both the work and the leak multiply with every event. Flatten with `SelectMany`, or with `Switch` when only the newest inner stream should stay live.
5. **Pick `FrameProvider` or `TimeProvider` from the intended semantics, not from convenience** — `IntervalFrame` and `DelayFrame` track Unity's update cadence and so stretch under a frame-rate drop, which is correct for animation-adjacent and gameplay-tick work; wall-clock `TimeProvider` timing is correct when real elapsed time is the requirement, such as a toast auto-dismiss.
6. **Give every subscription a disposal path tied to a real lifetime** — `.AddTo(this)` for a component-scoped subscription, a `DisposableBag` when one owner holds several. An undisposed subscription keeps its entire capture graph alive, which is the leak `performance-and-algorithms.md`'s Memory discipline section describes and `coding-principles.md`'s Correctness boundaries section requires cleaning up.
7. **Dispose the `ReactiveProperty<T>` itself, not only its subscribers** — it is `IDisposable` and owns its subscriber list, so an undisposed property outliving its scene keeps every subscriber reachable.
8. **Decide `OnErrorResume` behaviour explicitly and state it in the handoff** — R3's error model does not terminate the subscription on an exception the way classic Rx did, so a pipeline that should stop on failure must be made to stop; leaving it default means a broken stream keeps emitting unnoticed.
9. **Do not rebuild pub/sub out of a `Subject<T>`** — if the requirement is notifying decoupled systems once with no ongoing composition, that is a routed message and belongs to `messagepipe-event-messaging`; an ad hoc subject bus reimplements it without the filters, keying, or disposal discipline.
10. **Confirm leaks with `ObservableTracker` rather than by reading the code** — a leaked subscription is invisible in a single frame and only shows as a stale reference after a reload, which is exactly why the library ships tracking.
11. **Ask when the subscription's owning scope is unclear** — a pipeline whose lifetime nobody owns is a leak with a delay, and the scope decision belongs to `vcontainer-dependency-injection`, not to a guess made here.

## 5. Specific goals / tasks this skill performs
- Turn a plain field or C# event into a `ReactiveProperty<T>` or `Observable<T>` pipeline that UI subscribes to directly.
- Compose input and state streams with operators in place of per-frame polling in `Update()`.
- Choose and wire `FrameProvider` versus `TimeProvider` timing to match the intended semantics.
- Flatten nested subscriptions into `SelectMany` or `Switch` so subscriptions cannot multiply.
- Audit disposal — subscriptions, `DisposableBag`s, and the `ReactiveProperty<T>` instances themselves.
- Out of scope: one-shot awaits (`unitask-async-programming`), discrete cross-system dispatch (`messagepipe-event-messaging`), DI-scoped lifetime decisions (`vcontainer-dependency-injection`), sink-side string building (`zstring-zero-allocation-strings`), any use inside `Game.Core.*`.

## 6. Output format
```
## R3 Work — <stream or binding name>
- Source: Subject<T> / ReactiveProperty<T> / SerializableReactiveProperty<T> — <why this one>
- Current-value semantics: late subscriber receives latest / receives nothing
- Operators: <Where/Select/Pairwise/Throttle/CombineLatest/SelectMany/Switch>
- Redundant operators removed: <e.g. DistinctUntilChanged after ReactiveProperty> | none
- Nesting: no Subscribe inside Subscribe — flattened via <SelectMany/Switch> | not applicable
- Timing: FrameProvider (frame cadence) / TimeProvider (wall clock) / none — <why>
- Disposal: AddTo(this) / DisposableBag / Disposable.CreateBuilder — scope: <owner>
- Property disposal: ReactiveProperty<T> disposed by <owner> | not applicable
- Error handling: OnErrorResume decided — recover and continue / terminate
- Leak check: ObservableTracker clean after <scenario> | not run
- Layer: Game.Client.* — never Game.Core.*
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what this pipeline does not handle — error paths, reconnection, ordering>
- Latent concerns: <what holds only while the scene, scope, or emission rate stays as it is>
- Future remediation: <the trigger for each — a reload path, a new subscriber, a rate increase>
```

## 7. Examples
**Example 1**
- Input: the HUD health bar should update only when health changes, and flash briefly when health drops.
- Output: Shared Core's health exposed through a client-side `ReactiveProperty<int>`, subscribed with `.Pairwise().Where(t => t.Current < t.Previous)` so the flash fires only on a decrease. No `DistinctUntilChanged` added — the property already suppresses equal values. `.AddTo(this)` ties the subscription to the HUD component, and the view model disposes the property itself on teardown.

**Example 2**
- Input: "use R3 to broadcast a one-time 'boss defeated' event to the achievement and analytics systems."
- Output: declined. A fire-once notification to decoupled subscribers is `IPublisher<BossDefeated>`/`ISubscriber<BossDefeated>` in `messagepipe-event-messaging`, not an ongoing composition. Building it as a shared `Subject<T>` would recreate a message bus without keying, filters, or a disposal contract, and every subscriber would then need its own disposal path anyway. Routed to that skill instead.

**Example 3**
- Input: after a few scene reloads, an input pipeline fires its handler several times per press and memory grows.
- Output: `ObservableTracker` showed subscription count rising per reload. The cause was a `Subscribe` nested inside another `Subscribe`, so every outer emission created an inner subscription nothing disposed. Flattened with `SelectMany`, and since only the newest inner stream should stay live for this input, `Switch` was used at the second stage. All subscriptions moved into a `DisposableBag` owned by the scene scope; tracker clean across ten reloads.

## 8. Edge cases & guardrails
- Never leave a `Subscribe` without a disposal path tied to a real owner — the capture graph behind it stays alive for the process.
- Never nest `Subscribe` inside `Subscribe`, per §4 — subscriptions and their work multiply per outer emission, and nothing disposes them.
- Never dispose only the subscribers and leave the `ReactiveProperty<T>` alive — the property holds the subscriber list.
- Never let `OnErrorResume` behaviour be accidental — a stream that should stop on error will otherwise keep emitting past a fault.
- Never default to R3 for a single discrete message between systems — that is MessagePipe's job even though both are eventing.
- Never mix frame-cadence and wall-clock timing carelessly — the difference only shows under a frame-rate drop, which is exactly when it matters.
- Never place `R3` or `R3.Unity` types in `Game.Core.*` — expose Core state as a plain event and adapt from the Client layer.
- If the subscription's owning scope is undecided, ask — do not pick a lifetime by default.
