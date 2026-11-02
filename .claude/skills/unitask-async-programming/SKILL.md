---
name: unitask-async-programming
description: "UniTask/UniTaskVoid, PlayerLoop timing, destroy cancellation, Forget. Use for one-shot async in Client code, never Core."
user-invocable: false
---

# UniTask — Allocation-Free Async

- **Not for:** continuous event streams (`r3-reactive-extensions`).
- **Not for:** startup sequencing / `IAsyncStartable` (`vcontainer-dependency-injection`).
- **Not for:** pub/sub dispatch (`messagepipe-event-messaging`).
- **Not for:** transition graphs (`stateless-state-machines`).
  - **This skill writes only:** the `OnEntryAsync`/`FireAsync` bodies.
- **Not for:** RPC contracts (`magiconion-rpc-networking`).
  - **This skill awaits:** the `UnaryResult<T>`.
- **Not for:** Addressables call choice and release (`unity-addressables`).
- **Not for:** DOTween await extension methods (`dotween-tweening`).
  - **This skill supplies:** the cancellation and `PlayerLoopTiming` rules under `UNITASK_DOTWEEN_SUPPORT`.
- **Docs:** https://github.com/Cysharp/UniTask
- **Client only:** the assembly references `UnityEngine`, so never in a Core assembly.
  - **Core-side wait:** express it as a plain interface or callback and let Client code drive it.

## Steps
1. **Replace coroutines for one-shot waits; bridge third-party awaitables with `.AsUniTask()`:**
   - **Return type by who awaits:** `UniTask<T>` for a value, `UniTask` for completion only, `UniTaskVoid` when nothing awaits.
   - **`async void`:** never; exceptions escape to the player loop.
2. **Cancelable methods take a `CancellationToken` as the last parameter:** tied to `this.GetCancellationTokenOnDestroy()` for MonoBehaviour work.
   - **Otherwise:** in-flight work touches a destroyed object.
3. **Pool the `CancellationTokenSource` on repeatable paths:**
   - **Timeouts:** `TimeoutController`.
   - **Linked or manually cancelled source:** cannot be reset on Unity's API level (`TryReset` is .NET 6+), so create it once per lifetime and replace it only after it fires.
   - **New one per call:** never (`performance-and-algorithms.md` → Memory discipline).
4. **Set `PlayerLoopTiming` deliberately when resume order matters (`Update`, `FixedUpdate`, `LastPostLateUpdate`...):**
   - **Default:** invisible, and the bug is timing-dependent.
5. **`UniTask` is single-consumption:** the second await throws at runtime.
   - **Before a second awaiter:** call `.Preserve()` (at the point it is stored, not each await site) or use `UniTask.Lazy`.
   - **Preserved task:** don't reassign it per load.
6. **Bare `.Forget()` swallows exceptions:** pass an exception handler unless the work is truly fire-and-forget.
7. **Pull-based sequence of discrete async values:** `Channel<T>` or async LINQ, not a polling loop.
   - **Reacting to every occurrence:** a reactive stream, `r3-reactive-extensions`.
8. **Dispose every owned `CancellationTokenSource` and `UniTaskCompletionSource`:**
   - **Path:** the same `OnDisable`/`OnDestroy` path as coroutines and subscriptions (`coding-principles.md` → Correctness boundaries).
   - **Restore state in `finally`:** so destruction mid-operation cannot leave it broken (e.g. input disabled).
9. **Cancellation scope or awaiter count unstated:** `Blocked` naming it, before writing.
   - **Why:** they decide steps 2, 3 and 5 and fail only at runtime.
10. **Allocation or timing claim:** report how it was confirmed, or "not applicable".

## Output
```
## UniTask Work — <operation name>
- Return type: <UniTask / UniTask<T> / UniTaskVoid> — why
- Cancellation: <GetCancellationTokenOnDestroy() / pooled TimeoutController / none> — why
- PlayerLoopTiming: <default / explicit> — why, if non-default
- Multi-await: <.Preserve() / UniTask.Lazy / single consumer>
- Fire-and-forget: <.Forget() with handler / not used>
- Disposal: <path for every owned source>
```

## Example
- **"Make the cooldown reactive so UI can bind":** declined — a cooldown observed over time is a stream, not a one-shot; routed to `r3-reactive-extensions` (`ReactiveProperty<float>`).
