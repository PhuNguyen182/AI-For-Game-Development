---
name: unitask-async-programming
description: >
  Technique for allocation-free async/await in Unity via UniTask
  (`Cysharp.Threading.Tasks`) — `UniTask`/`UniTask<T>`/`UniTaskVoid`,
  `PlayerLoopTiming`-based scheduling, `GetCancellationTokenOnDestroy()` and
  `CancellationTokenSource` pooling, `.Preserve()`/`UniTask.Lazy` for re-await,
  and async LINQ/`Channel<T>` for pull-based streams — replacing
  `Task`/`IEnumerator` coroutines in `Game.Client.*` code. Use this for any
  one-shot asynchronous operation with a definite completion (an animation
  finishing, a network call returning, a delay, an Addressables load). Do not
  use this for a continuous stream of discrete events over time (input,
  health-changed, damage-taken) that callers compose/filter/react to — that's
  `r3-reactive-extensions`; note R3's own `SubscribeAwait`/`SelectAwait`
  operators consume UniTask internally, so the two compose rather than
  compete. Do not use this to decide *how* an async operation should be
  wired into the object graph or app-startup sequence (`IAsyncStartable`,
  scope disposal ordering) — that's `vcontainer-dependency-injection`; this
  skill only covers writing the `async UniTask` method itself. Do not use
  this to design cross-system pub/sub message dispatch — that's
  `messagepipe-event-messaging`, even though its async publishers return
  `UniTask` under the hood. Do not use this to model a state machine's
  transition graph — that's `stateless-state-machines`; this skill only
  covers the `UniTask`-shaped `OnEntryAsync`/`FireAsync` bodies that library
  calls into. Do not use this to await an RPC call's wire format or design
  the service contract — that's `magiconion-rpc-networking`; this skill
  covers awaiting the resulting `UnaryResult<T>` (a UniTask-shaped type), not
  the contract itself. Do not use this to decide which Addressables call to
  make, its content-build-system choice, or its reference-counting/release
  discipline — that's `unity-addressables`; this skill only covers the
  generic await/cancellation mechanics an Addressables `AsyncOperationHandle`
  shares with any other UniTask-awaited operation. Never use this inside `Game.Core.*` — the UniTask
  package assembly references `UnityEngine` for its `PlayerLoop` integration,
  which violates the Shared Core's no-`UnityEngine`-dependency rule in
  `coding-principles.md`; a Core state machine or rule evaluator that needs
  to "wait" expresses that as a plain interface/callback and lets
  `Game.Client.*` drive it with UniTask instead.
---

# UniTask — Allocation-Free Async/Await for Unity

Source: [github.com/Cysharp/UniTask](https://github.com/Cysharp/UniTask).

## 1. Objective
Replace `Task`-based async and `IEnumerator` coroutines in `Game.Client.*` with a struct-based, zero (or near-zero) allocation `UniTask`/`UniTask<T>` that runs on Unity's `PlayerLoop` instead of the thread pool — without leaking a `CancellationTokenSource`, double-awaiting a `UniTask`, or accidentally reintroducing an allocation the library exists to avoid.

## 2. Role
Act as the async/await specialist for the client track — the tool C# Software Engineer and Unity Engineer reach for whenever `Game.Client.*` code needs to wait on something (an animation, a network round-trip, a frame delay, an Addressables handle) without blocking the main thread or allocating a `Task`/closure per call.

## 3. When to invoke this skill
- Converting a `MonoBehaviour` coroutine (`IEnumerator` + `StartCoroutine`) to `async UniTaskVoid`/`async UniTask` for a one-shot operation: a delay, an animation-then-callback sequence, a load-then-activate flow.
- Awaiting a genuinely asynchronous result with a definite endpoint: an Addressables load, an HTTP/RPC call, a `UnityWebRequest`, or a `UnaryResult<T>` returned by a `magiconion-rpc-networking` service call.
- Wiring cancellation to a GameObject's lifetime via `GetCancellationTokenOnDestroy()`, or pooling a reusable `CancellationTokenSource` via `TimeoutController`/a cached source instead of `new CancellationTokenSource()` per call.
- A `UniTask` needs to be awaited from more than one place (e.g. a shared "loaded" signal) — apply `.Preserve()` or `UniTask.Lazy` deliberately, since a bare `UniTask` can only be awaited once.
- Negative trigger: a continuous stream of discrete events a caller composes/filters/reacts to over time — that's `r3-reactive-extensions`.
- Negative trigger: deciding where in the DI-managed object graph or app-startup sequence an async operation runs — that's `vcontainer-dependency-injection`'s `IAsyncStartable`.
- Negative trigger: designing a cross-system pub/sub message — that's `messagepipe-event-messaging`.
- Negative trigger: modeling a state machine's transition graph — that's `stateless-state-machines`; this skill only supplies the async method bodies it calls into.
- Negative trigger: designing an RPC service/hub contract — that's `magiconion-rpc-networking`; this skill only awaits the resulting `UnaryResult<T>`.
- Negative trigger: any `Game.Core.*` code. UniTask's assembly depends on `UnityEngine` — using it in Shared Core breaks `coding-principles.md`'s Shared Core integrity rule. Express a Core-side "wait" as a plain interface/callback/`IEnumerator`-free state transition and drive it from `Game.Client.*`.

## 4. How to use this skill
1. **Pick the right return type.** `UniTask` for a fire-and-forget-but-awaitable void operation; `UniTask<T>` for one that produces a value; `UniTaskVoid` only for genuinely fire-and-forget work nothing will ever await (an `async void` replacement) — never use `async void` itself.
2. **Never call `.Forget()` silently on something that can throw without a plan.** `.Forget()` drops the result and swallows exceptions unless you pass an exception handler — use it deliberately for truly fire-and-forget work, not as a way to avoid handling a `try`/`catch`.
3. **Thread cancellation through explicitly.** Accept a `CancellationToken` as the last parameter of any cancelable async method; tie it to `this.GetCancellationTokenOnDestroy()` for a `MonoBehaviour`-scoped operation so a destroyed GameObject's in-flight async work stops instead of touching a dead object.
4. **Pool `CancellationTokenSource` instances for repeated calls.** A fresh `CancellationTokenSource` per invocation on a hot path (e.g. a repeatedly-retriggered ability) is exactly the kind of per-call allocation `performance-and-algorithms.md`'s Memory discipline section warns about — reuse a `TimeoutController` or a cached source with `.Reset()` instead.
5. **Choose the `PlayerLoopTiming` deliberately** when an operation must resume at a specific point in the frame (`Update`, `FixedUpdate`, `LastPostLateUpdate`, etc.) instead of accepting whatever the default resumes at — this matters for anything that reads/writes `transform` state near other systems' updates.
6. **Mark a `UniTask` `.Preserve()` (or wrap it in `UniTask.Lazy`) before handing it to more than one awaiter.** A `UniTask` is a single-consumption struct; awaiting it twice without `.Preserve()` throws at runtime, not compile time — treat "will this be awaited more than once" as a design question up front.
7. **Prefer async LINQ / `Channel<T>` over a hand-rolled polling loop** for a pull-based stream of discrete async values (e.g. draining a queue of incoming events one at a time) — but if the actual need is "react to every occurrence as it happens," that's `r3-reactive-extensions`'s territory instead.
8. **Dispose what needs disposing.** A `CancellationTokenSource` you own, an `UniTaskCompletionSource` you created — clean it up on the same `OnDisable`/`OnDestroy` path `coding-principles.md`'s Correctness boundaries section already requires for coroutines and event subscriptions.

## 5. Specific goals / tasks this skill performs
- Converting coroutine-based async flows (`IEnumerator`/`StartCoroutine`) to `async UniTask`/`UniTaskVoid`.
- Wiring `GetCancellationTokenOnDestroy()` and pooled `CancellationTokenSource`s to avoid per-call allocation and dangling operations on destroyed objects.
- Awaiting third-party async surfaces (Addressables, `UnityWebRequest`, a `UnaryResult<T>` from MagicOnion) via `.AsUniTask()`/native `UniTask` support.
- Diagnosing a "cannot await twice" runtime error via `.Preserve()`/`UniTask.Lazy`.
- Out of scope: reactive event streams (`r3-reactive-extensions`), DI-managed startup sequencing (`vcontainer-dependency-injection`), cross-system message dispatch (`messagepipe-event-messaging`), state machine transition design (`stateless-state-machines`), RPC contract design (`magiconion-rpc-networking`), any use inside `Game.Core.*`.

## 6. Output format
```
## UniTask Work — <operation name>
- Return type: UniTask / UniTask<T> / UniTaskVoid — rationale
- Cancellation: <GetCancellationTokenOnDestroy() / pooled TimeoutController / none — why>
- PlayerLoopTiming: <default / explicit timing — why, if non-default>
- Multi-await handling: <.Preserve() / UniTask.Lazy / not needed — single consumer>
- Disposal: <CancellationTokenSource / UniTaskCompletionSource cleanup path>
- Layer: Game.Client.* (never Game.Core.* — UnityEngine dependency)
- Known limitations: <...>
```

## 7. Examples
**Example 1**
- Input: a `MonoBehaviour` coroutine plays a hit-reaction animation, waits for it to finish, then re-enables player input.
- Output: rewritten as `async UniTaskVoid PlayHitReactionAsync(CancellationToken ct)`, cancellation sourced from `this.GetCancellationTokenOnDestroy()`, awaiting `UniTask.WaitUntil(() => animator.IsAnimationDone, cancellationToken: ct)`, input re-enabled in a `finally` block so a mid-animation object destruction doesn't leave input permanently disabled.

**Example 2**
- Input: a request came in to "make the ability cooldown system reactive so UI can bind to it directly."
- Output: declined — a cooldown counting down and being observed continuously by UI is a stream of state changes over time, which is `r3-reactive-extensions`'s territory (a `ReactiveProperty<float>`), not a one-shot `UniTask` await; recommended that skill instead.

## 8. Edge cases & guardrails
- Never write `async void` — always `async UniTaskVoid` (or `UniTask`/`UniTask<T>` when the caller awaits it).
- Never allocate a fresh `CancellationTokenSource` per call on a hot/repeatable path — pool or reuse it.
- Never await a non-`.Preserve()`d `UniTask` from more than one location — it throws at runtime on the second await.
- Never use UniTask inside `Game.Core.*` — its assembly depends on `UnityEngine`; this belongs to `Game.Client.*` only, per the Shared Core rule in `coding-principles.md`.
- Never let `.Forget()` silently swallow an exception that matters — pass an explicit exception handler when the fire-and-forget work can actually fail.
- Don't reach for async LINQ/`Channel<T>` when the actual need is "react continuously to every occurrence" — that's a reactive stream (`r3-reactive-extensions`), not a pull-based async sequence.
