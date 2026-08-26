---
name: unitask-async-programming
description: >
  UniTask (`Cysharp.Threading.Tasks`) — allocation-free async/await on Unity's
  `PlayerLoop`: `UniTask`/`UniTask<T>`/`UniTaskVoid`, `PlayerLoopTiming`,
  `GetCancellationTokenOnDestroy()`, pooled `CancellationTokenSource` and
  `TimeoutController`, `.Preserve()`/`UniTask.Lazy` for re-await, `.Forget()`,
  `UniTaskCompletionSource`, `.AsUniTask()`, and `Channel<T>`/async LINQ for
  pull-based streams. Use for any one-shot operation with a definite
  completion — an animation finishing, an RPC returning, a delay, an
  Addressables load — replacing `Task` and `IEnumerator` coroutines in
  `Game.Client.*`. Never inside `Game.Core.*`: the assembly references
  `UnityEngine`. Not for: continuous event streams (`r3-reactive-extensions`),
  startup sequencing (`vcontainer-dependency-injection`), pub/sub dispatch
  (`messagepipe-event-messaging`), transition graphs
  (`stateless-state-machines`), RPC contracts (`magiconion-rpc-networking`),
  Addressables load and release discipline (`unity-addressables`).
---

# UniTask — Allocation-Free Async/Await for Unity

## 1. Objective
Replace `Task`-based async and `IEnumerator` coroutines in `Game.Client.*` with a struct-based, zero- or near-zero-allocation `UniTask`/`UniTask<T>` running on Unity's `PlayerLoop` rather than the thread pool — without leaking a `CancellationTokenSource`, double-awaiting a `UniTask`, or reintroducing the per-call allocation the library exists to remove.

## 2. Role
Act as the async/await specialist for the client track — the tool C# Software Engineer and Unity Engineer reach for whenever `Game.Client.*` code must wait on something (an animation, a network round-trip, a frame delay, an Addressables handle) without blocking the main thread or allocating a `Task` and closure per call.

## 3. When to invoke this skill
- Converting a `MonoBehaviour` coroutine (`IEnumerator` + `StartCoroutine`) to `async UniTask`/`async UniTaskVoid` for a one-shot operation: a delay, an animation-then-callback sequence, a load-then-activate flow.
- Awaiting a genuinely asynchronous result with a definite endpoint — an Addressables load, an HTTP call, a `UnityWebRequest`, or a `UnaryResult<T>` returned by a MagicOnion service call.
- Wiring cancellation to a GameObject's lifetime via `GetCancellationTokenOnDestroy()`, or replacing a per-call `new CancellationTokenSource()` with a `TimeoutController` or cached source.
- A `UniTask` must be awaited from more than one place (a shared "loaded" signal) — applying `.Preserve()` or `UniTask.Lazy` deliberately, since a bare `UniTask` is single-consumption.
- Draining a pull-based stream of discrete async values one at a time via `Channel<T>` or async LINQ.
- Wiring the cancellation-token/`PlayerLoopTiming` discipline behind awaiting a DOTween tween through `UNITASK_DOTWEEN_SUPPORT` — the DOTween-specific extension methods (`.ToUniTask()`-style await, `AwaitForComplete`/`AwaitForPause`/etc.) themselves are `dotween-tweening`'s to document; this skill supplies the cancellation-token lifetime and timing rules underneath.
- Negative trigger: a continuous stream of discrete events callers compose, filter, and react to over time — that's `r3-reactive-extensions`. R3's own `SubscribeAwait`/`SelectAwait` consume UniTask internally, so the two compose rather than compete.
- Negative trigger: deciding where in the DI object graph or startup sequence an async operation runs (`IAsyncStartable`, scope disposal ordering) — that's `vcontainer-dependency-injection`; this skill writes the `async UniTask` method itself.
- Negative trigger: designing cross-system pub/sub message dispatch — that's `messagepipe-event-messaging`, even though its async publishers return `UniTask` underneath.
- Negative trigger: modeling a state machine's transition graph — that's `stateless-state-machines`; this skill supplies only the `OnEntryAsync`/`FireAsync` bodies it calls into.
- Negative trigger: designing an RPC service or hub contract — that's `magiconion-rpc-networking`; this skill awaits the resulting `UnaryResult<T>`, not the contract.
- Negative trigger: choosing which Addressables call to make, its content-build system, or its reference-counting and release discipline — that's `unity-addressables`; this skill covers only the generic await and cancellation mechanics an `AsyncOperationHandle` shares with any awaited operation.
- Negative trigger: any `Game.Core.*` code — the UniTask assembly references `UnityEngine` for `PlayerLoop` integration, which `coding-principles.md`'s Shared Core integrity section forbids in Core.

## 4. How to use this skill
1. **Pick the return type from who awaits the result**, per the [UniTask documentation](https://github.com/Cysharp/UniTask) — `UniTask<T>` when it produces a value, `UniTask` when a caller awaits completion only, `UniTaskVoid` when nothing will ever await it. Never `async void`: it cannot be awaited, and its exceptions escape to the Unity player loop instead of the caller.
2. **Thread a `CancellationToken` through as the last parameter of every cancelable async method**, tied to `this.GetCancellationTokenOnDestroy()` for MonoBehaviour-scoped work. Without it, in-flight work outlives the destroyed object and touches a dead reference — the async equivalent of the leaked-coroutine failure `coding-principles.md`'s Correctness boundaries section already forbids.
3. **Pool the `CancellationTokenSource` on any repeatable path** — a fresh source per invocation of a retriggerable ability is exactly the per-call allocation `performance-and-algorithms.md`'s Memory discipline section names. Reuse a `TimeoutController`, or a cached source with `.Reset()`.
4. **Choose `PlayerLoopTiming` deliberately whenever resume order matters** — `Update`, `FixedUpdate`, `LastPostLateUpdate`, and the rest decide *where in the frame* the continuation runs. This is load-bearing for anything reading or writing `transform` state near another system's update, and invisible when left at the default.
5. **Call `.Preserve()`, or wrap in `UniTask.Lazy`, before handing a `UniTask` to a second awaiter** — a `UniTask` is a single-consumption struct, and the second await throws at runtime rather than compile time. Decide "will this be awaited more than once" up front, not after the exception.
6. **Pass an explicit exception handler whenever `.Forget()` covers work that can fail** — bare `.Forget()` drops the result and swallows the exception, which is correct for genuinely fire-and-forget work and a silent failure everywhere else.
7. **Prefer `Channel<T>` or async LINQ over a hand-rolled polling loop** for a pull-based sequence of discrete async values. If the real need is reacting to every occurrence as it happens, that is a reactive stream and belongs to `r3-reactive-extensions` instead.
8. **Dispose every `CancellationTokenSource` and `UniTaskCompletionSource` this code owns** on the same `OnDisable`/`OnDestroy` path `coding-principles.md` already requires for coroutines and event subscriptions.
9. **If the operation's cancellation scope or its awaiter count is unstated, ask before writing** — scope decides steps 2–3 and awaiter count decides step 5. Both compile either way, and both fail only at runtime, on a path a test may never reach.

## 5. Specific goals / tasks this skill performs
- Converting coroutine-based flows (`IEnumerator`/`StartCoroutine`) to `async UniTask`/`UniTaskVoid`.
- Wiring `GetCancellationTokenOnDestroy()` and pooled `CancellationTokenSource`s to remove per-call allocation and stop work on destroyed objects.
- Awaiting third-party async surfaces — Addressables, `UnityWebRequest`, a MagicOnion `UnaryResult<T>` — via `.AsUniTask()` or native UniTask support.
- Diagnosing a "cannot await twice" runtime error and resolving it with `.Preserve()` or `UniTask.Lazy`.
- Draining a pull-based async sequence with `Channel<T>` or async LINQ.
- Out of scope: reactive event streams (`r3-reactive-extensions`); DI startup sequencing (`vcontainer-dependency-injection`); cross-system message dispatch (`messagepipe-event-messaging`); state machine transition design (`stateless-state-machines`); RPC contract design (`magiconion-rpc-networking`); Addressables load/release discipline (`unity-addressables`); any use inside `Game.Core.*`.

## 6. Output format
```
## UniTask Work — <operation name>
- Return type: <UniTask / UniTask<T> / UniTaskVoid> — rationale
- Cancellation: <GetCancellationTokenOnDestroy() / pooled TimeoutController / none> — why
- PlayerLoopTiming: <default / explicit timing> — why, if non-default
- Multi-await handling: <.Preserve() / UniTask.Lazy / not needed — single consumer>
- Fire-and-forget: <.Forget() with handler / not used>
- Rule compliance: <disposal path for every owned source, per Correctness boundaries>
- Verification: <how the allocation or timing claim was confirmed, or "not applicable">
- Layer: Game.Client.* — never Game.Core.*, which cannot reference UnityEngine
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what the delivered solution does not cover>
- Latent concerns: <failure modes not yet triggered: assumptions holding only under current conditions, thresholds not yet reached>
- Future remediation: <the concrete fix for each concern, each with its trigger condition>
```

## 7. Examples
**Example 1**
- Input: a `MonoBehaviour` coroutine plays a hit-reaction animation, waits for it to finish, then re-enables player input.
- Output: rewritten as `async UniTaskVoid PlayHitReactionAsync(CancellationToken cancellationToken)` with the token from `this.GetCancellationTokenOnDestroy()`, awaiting `UniTask.WaitUntil(...)`; input re-enabled in a `finally` block so destruction mid-animation cannot leave input permanently disabled.

**Example 2**
- Input: "make the ability cooldown system reactive so UI can bind to it directly."
- Output: declined — a cooldown counting down and observed continuously is a stream of state changes over time, not a one-shot completion. Routed to `r3-reactive-extensions` and a `ReactiveProperty<float>`; a `UniTask` would complete once and never report the intermediate values the UI actually binds to.

**Example 3**
- Input: a level loader awaits one `UniTask` from three separate systems that each need to know when loading finished.
- Output: the second await was throwing at runtime, since a bare `UniTask` is single-consumption. Applied `.Preserve()` at the point the task is stored rather than at each await site, so all three consumers share one completion, and documented that the preserved task must not be reassigned per load.

## 8. Edge cases & guardrails
- Never write `async void` — use `async UniTaskVoid`, or `UniTask`/`UniTask<T>` when a caller awaits; `async void` exceptions escape the caller entirely.
- Never allocate a fresh `CancellationTokenSource` per call on a repeatable path — pool or reuse it.
- Never await a `UniTask` from more than one place without `.Preserve()` or `UniTask.Lazy` — the second await throws at runtime, not compile time.
- Never let a bare `.Forget()` cover work that can fail — pass an explicit exception handler, or the failure disappears entirely.
- Never use UniTask inside `Game.Core.*` — its assembly references `UnityEngine`. Express a Core-side wait as a plain interface or callback and let `Game.Client.*` drive it.
- Never reach for `Channel<T>` or async LINQ when the need is reacting continuously to every occurrence — that's a reactive stream, not a pull-based sequence.
- Never leave `PlayerLoopTiming` at the default in code whose correctness depends on frame ordering — the default resumes wherever it resumes, and the resulting bug is timing-dependent.
- If the cancellation scope or the number of awaiters is unstated, ask — both decide a §6 field and both fail only at runtime.
