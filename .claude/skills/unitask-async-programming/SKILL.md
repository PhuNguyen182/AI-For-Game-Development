---
name: unitask-async-programming
description: "UniTask allocation-free async on the PlayerLoop: UniTask/UniTaskVoid, timing, cancellation on destroy, Forget, completion sources, async LINQ. Use for one-shot async in Game.Client, never in Game.Core."
user-invocable: false
---

# UniTask — Allocation-Free Async

Not for: continuous event streams (`r3-reactive-extensions`), startup sequencing / `IAsyncStartable` (`vcontainer-dependency-injection`), pub/sub dispatch (`messagepipe-event-messaging`), transition graphs (`stateless-state-machines` — this skill writes only the `OnEntryAsync`/`FireAsync` bodies), RPC contracts (`magiconion-rpc-networking` — this skill awaits the `UnaryResult<T>`), Addressables call choice and release (`unity-addressables`), DOTween await extension methods (`dotween-tweening`; this skill supplies the cancellation and `PlayerLoopTiming` rules under `UNITASK_DOTWEEN_SUPPORT`).
Docs: https://github.com/Cysharp/UniTask
Client only: the assembly references `UnityEngine`, so never in `Game.Core.*`; express a Core-side wait as a plain interface or callback and let `Game.Client.*` drive it.

## Steps
1. **Replace coroutines for one-shot waits; bridge third-party awaitables with `.AsUniTask()`. Return type by who awaits** — `UniTask<T>` for a value, `UniTask` for completion only, `UniTaskVoid` when nothing awaits. Never `async void` (exceptions escape to the player loop).
2. **Cancelable methods take a `CancellationToken` as the last parameter**, tied to `this.GetCancellationTokenOnDestroy()` for MonoBehaviour work — otherwise in-flight work touches a destroyed object.
3. **Pool the `CancellationTokenSource` on repeatable paths** — `TimeoutController`, or a cached source with `.Reset()`; never a new one per call (`performance-and-algorithms.md` → Memory discipline).
4. **Set `PlayerLoopTiming` deliberately when resume order matters** (`Update`, `FixedUpdate`, `LastPostLateUpdate`...) — the default is invisible and the bug timing-dependent.
5. **`UniTask` is single-consumption** — call `.Preserve()` (at the point it is stored, not each await site) or use `UniTask.Lazy` before a second awaiter; the second await throws at runtime. Don't reassign a preserved task per load.
6. **Bare `.Forget()` swallows exceptions** — pass an exception handler unless the work is truly fire-and-forget.
7. **Pull-based sequence of discrete async values → `Channel<T>` or async LINQ**, not a polling loop. Reacting to every occurrence is a reactive stream: `r3-reactive-extensions`.
8. **Dispose every owned `CancellationTokenSource` and `UniTaskCompletionSource`** on the same `OnDisable`/`OnDestroy` path as coroutines and subscriptions (`coding-principles.md` → Correctness boundaries). Restore state in `finally` so destruction mid-operation cannot leave it broken (e.g. input disabled).
9. **Cancellation scope or awaiter count unstated → ask before writing** — they decide steps 2, 3 and 5 and fail only at runtime.

## Output
```
## UniTask Work — <operation name>
- Return type: <UniTask / UniTask<T> / UniTaskVoid> — why
- Cancellation: <GetCancellationTokenOnDestroy() / pooled TimeoutController / none> — why
- PlayerLoopTiming: <default / explicit> — why, if non-default
- Multi-await: <.Preserve() / UniTask.Lazy / single consumer>
- Fire-and-forget: <.Forget() with handler / not used>
- Disposal: <path for every owned source>
- Verification: <how an allocation or timing claim was confirmed, or "not applicable">
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Make the cooldown reactive so UI can bind" → declined: a cooldown observed over time is a stream, not a one-shot; routed to `r3-reactive-extensions` (`ReactiveProperty<float>`).
