# Migration and Rx Integration

Sources (under the Docs base): integration-r3, integration-unirx, design-philosophy, faq, migrate-from-dotween, migrate-from-leantween, migrate-from-primetween, migrate-from-v1.

## R3 / UniRx

| Method | Fact |
|---|---|
| `ToObservable()` | `Observable<T>` (R3) / `IObservable<T>` (UniRx) |
| `BindToReactiveProperty(ReactiveProperty<T>)` | Binds into an existing reactive property |

```csharp
Observable.CombineLatest(LMotion.Create(-5f, 5f, 2f).ToObservable(), LMotion.Create(0f, 3f, 2f).ToObservable(),
    (x, y) => new Vector2(x, y)).Subscribe(v => transform.position = v);
```

**Caveat:** Package Manager installs wire this automatically; a `.unitypackage` install needs `LITMOTION_SUPPORT_R3` or `LITMOTION_SUPPORT_UNIRX` in Player Settings, or the methods do not exist.

## No `AppendCallback` / `DelayedCall`

Deliberate: callback delays do not propagate exceptions. Use an `async` method. Last-resort stopgap while porting:

```csharp
LMotion.Create(0f, 1f, delay).WithOnComplete(action).RunWithoutBinding();
```

## Port tables

Whether a module moves from DOTween is a standing decision; see `dotween-tweening` `coexistence-and-migration.md` first.

| Old | LitMotion |
|---|---|
| DOTween `transform.DOMove(end, dur)`; LeanTween `LeanTween.move`; PrimeTween `Tween.Position` | `LMotion.Create(transform.position, end, dur).BindToPosition(transform)` |
| `DOTween.To(getter, setter, end, dur)`; `LeanTween.value`; `Tween.Custom` | `LMotion.Create(v, end, dur).Bind(x => v = x)` |
| `.From(start)` / `.from(start)` | Pass `start` as the first `Create` argument |
| `DOPunch*`/`DOShake*`; `Tween.PunchPosition`/`ShakePosition` | `LMotion.Punch.Create` / `LMotion.Shake.Create` |
| DOTween `SetLoops(n, Yoyo)`; PrimeTween `cycleMode: Yoyo` | `WithLoops(n, LoopType.Yoyo)` |
| LeanTween `setRepeat(n).setLoopPingPong()` | `WithLoops(n, LoopType.Flip)` |
| `Pause()`; `isPaused = true` | `handle.PlaybackSpeed = 0f` |
| `Kill()`; LeanTween `cancel()` | `handle.Cancel()` |
| `Complete()` | `handle.Complete()` |
| DOTween `Sequence().Append/Join/Insert`; PrimeTween `Chain/Group/Insert` | `LSequence.Create().Append/Join/Insert(...).Run()`; no callbacks |
| DOTween `SetUpdate(Fixed)`; PrimeTween `useFixedUpdate: true` | `WithScheduler(MotionScheduler.FixedUpdate)` |
| DOTween `SetLink(go)` | `handle.AddTo(go)` |
| `WaitForCompletion()` / `AsyncWaitForCompletion()` | `handle.ToYieldInstruction()` / `await handle` |
| DOTween Safe Mode | `MotionDispatcher.RegisterUnhandledExceptionHandler(ex => Debug.LogWarning(ex))` |
| PrimeTween `TweenSettings<float>` | `SerializableMotionSettings<float, NoOptions>` |
| `SetSpeedBased`, `DoPath`, `LTSpline`, `Tween.*AtSpeed`, `Tween.Delay`, `DelayedCall` | Unsupported: compute duration from distance; use Unity Splines for paths; async for delays |

## From LitMotion v1

| v1 | v2 |
|---|---|
| `MotionBuilder.Preserve()` | `MotionHandle.Preserve()` |
| `BindToUnityLogger()`/`BindToProgress()` in core namespace | Moved to `LitMotion.Extensions` |
| `BindWithState` | `Bind(state, ...)` overload |
| `ToYieldInteraction()` | `ToYieldInstruction()` |
| `LoopType.Yoyo` (flip back and forth) | `LoopType.Flip`; v2 `Yoyo` differs |
| `LinkBehaviour`, `CancelBehaviour` | `LinkBehavior`, `CancelBehavior` |
| `WithBindOnSchedule()` | `WithImmediateBind()`, default `true` |
| Static `ManualMotionDispatcher.Update` | `ManualMotionDispatcher.Default.Update`; multiple dispatchers possible |
| `MotionTracker` window | LitMotion Debugger |
