---
name: r3-reactive-extensions
description: "R3 reactive streams: Observable, Subject, ReactiveProperty, operators, Unity frame providers, AddTo disposal, UI binding. Use for continuous event streams; one-shot async is UniTask."
user-invocable: false
---

# R3 — Continuous Event Streams

Not for: one-shot awaits (`unitask-async-programming`; R3's `SubscribeAwait`/`SelectAwait` take a `Func<T, CancellationToken, ValueTask>`; await a UniTask inside that lambda), single addressed messages (`messagepipe-event-messaging`), where a subscription's lifetime is scoped in DI (`vcontainer-dependency-injection`), building the sink's text (`zstring-zero-allocation-strings`), named states with legal transitions (`stateless-state-machines` — a `ReactiveProperty<GameState>` enforces nothing about transitions).
Docs: https://github.com/Cysharp/R3
Client only, by project policy: core R3 is plain .NET (only `R3.Unity` needs `UnityEngine`), but a reactive dependency in Core couples rule code to a push library and its scheduling, so never in a Core assembly; expose Core state as a plain C# event and adapt to `Observable<T>` in Client code.

## Steps
1. **Choose the source by whether late subscribers need the current value** — `Subject<T>` for a pushed event with no state, `ReactiveProperty<T>` when they must get the latest, `SerializableReactiveProperty<T>` to bind in the Inspector.
2. **No reflexive `DistinctUntilChanged` on a `ReactiveProperty<T>`** — it already suppresses equal values; pass a comparer when the type lacks meaningful equality.
3. **Compose with `Where`/`Select`/`Pairwise`/`CombineLatest`** instead of flags and polling in `Update()` (SLAP, `coding-principles.md`).
4. **Never `Subscribe` inside `Subscribe`** — every outer emission leaks an undisposed inner subscription. Flatten with `SelectMany`, or `Switch` when only the newest inner stream should live.
5. **`FrameProvider` vs `TimeProvider` by semantics** — `IntervalFrame`/`DelayFrame` follow update cadence and stretch under a frame-rate drop (gameplay ticks, animation-adjacent); wall-clock `TimeProvider` when real elapsed time matters (toast auto-dismiss).
6. **Every subscription gets a disposal path tied to a real owner** — `.AddTo(this)` for a component, `DisposableBag` for several. An undisposed subscription keeps its whole capture graph alive.
7. **Dispose the `ReactiveProperty<T>` itself** — it owns the subscriber list; one outliving its scene keeps all subscribers reachable.
8. **Decide `OnErrorResume` behaviour explicitly and state it in the handoff** — R3 does not terminate on an exception as classic Rx did; a pipeline that must stop on failure has to be made to.
9. **Confirm leaks with `ObservableTracker`** after a scene reload; reading code won't show them.
10. **Owning scope unclear → `Needs-decision`, `Next: technical-architect`** (scope decision is `vcontainer-dependency-injection`'s); never pick a lifetime by default.

## Never
- Rebuild pub/sub from a shared `Subject<T>` — a fire-once notification to decoupled systems is `messagepipe-event-messaging`; the subject bus lacks keying, filters and disposal discipline.

## Output
```
## R3 Work — <stream or binding name>
- Source: <Subject / ReactiveProperty / SerializableReactiveProperty> — why
- Operators: <list>; redundant ones removed: <...> | none
- Nesting: flattened via <SelectMany/Switch> | not applicable
- Timing: <FrameProvider / TimeProvider / none> — why
- Disposal: <AddTo / DisposableBag> — owner; ReactiveProperty disposed by <owner>
- Error handling: OnErrorResume — <recover and continue / terminate>
- Leak check: ObservableTracker <clean after scenario | not run>
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Broadcast a one-time 'boss defeated' to achievements and analytics with R3" → declined: `IPublisher<BossDefeated>` in `messagepipe-event-messaging`.
