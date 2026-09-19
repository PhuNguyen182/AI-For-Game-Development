# Rx Integration & Migration — R3/UniRx, DOTween/LeanTween/PrimeTween/v1

Sources: [R3](https://annulusgames.github.io/LitMotion/articles/en/integration-r3.html), [UniRx](https://annulusgames.github.io/LitMotion/articles/en/integration-unirx.html), [Design Philosophy](https://annulusgames.github.io/LitMotion/articles/en/design-philosophy.html), [FAQ](https://annulusgames.github.io/LitMotion/articles/en/faq.html), [Migrate from DOTween](https://annulusgames.github.io/LitMotion/articles/en/migrate-from-dotween.html), [Migrate from LeanTween](https://annulusgames.github.io/LitMotion/articles/en/migrate-from-leantween.html), [Migrate from PrimeTween](https://annulusgames.github.io/LitMotion/articles/en/migrate-from-primetween.html), [Migrate from LitMotion v1](https://annulusgames.github.io/LitMotion/articles/en/migrate-from-v1.html).
Covers: SKILL.md §4 — **"Reach for `LSequence` only for structural composition"**, **"If the async ecosystem (UniTask/R3/UniRx availability), target Unity/C# version, or hot-path volume is unstated, ask before committing to an async mechanism or a scripting define"**.

## Table of contents
- [R3 / UniRx](#r3--unirx)
- [Design decision: no `AppendCallback`/`DelayedCall`](#design-decision-no-appendcallbackdelayedcall)
- [Migrating from DOTween](#migrating-from-dotween)
- [Migrating from LeanTween](#migrating-from-leantween)
- [Migrating from PrimeTween](#migrating-from-primetween)
- [Migrating from LitMotion v1](#migrating-from-litmotion-v1)

## R3 / UniRx

Both add the same two extension methods; pick whichever reactive library the
project already uses (see `r3-reactive-extensions` for composing the
resulting stream further — this skill only produces it).

| Method | Effect | Requires | Source |
|---|---|---|---|
| `ToObservable()` | Converts the motion to `Observable<T>` (R3) / `IObservable<T>` (UniRx) | `LITMOTION_SUPPORT_R3` / `LITMOTION_SUPPORT_UNIRX` scripting define if installed via `.unitypackage` instead of Package Manager | [R3](https://annulusgames.github.io/LitMotion/articles/en/integration-r3.html), [UniRx](https://annulusgames.github.io/LitMotion/articles/en/integration-unirx.html) |
| `BindToReactiveProperty(ReactiveProperty<T>)` | Binds the motion's value directly into an existing reactive property | same | same |

```csharp
var x = LMotion.Create(-5f, 5f, 2f).ToObservable();
var y = LMotion.Create(0f, 3f, 2f).ToObservable();
Observable.CombineLatest(x, y, (x, y) => new Vector2(x, y))
    .Subscribe(v => transform.position = v);
```

**Critical caveat**: installing via Package Manager wires this automatically; installing via `.unitypackage` requires manually adding the matching `LITMOTION_SUPPORT_*` define to Player Settings, or the extension methods simply don't exist.

## Design decision: no `AppendCallback`/`DelayedCall`

Per [Design Philosophy](https://annulusgames.github.io/LitMotion/articles/en/design-philosophy.html) and the [FAQ](https://annulusgames.github.io/LitMotion/articles/en/faq.html): LitMotion deliberately omits DOTween-style `DelayedCall()` and `Sequence.AppendCallback()`. Callback-based delays don't propagate exceptions to the caller; `async`/`await` (via UniTask) is the recommended replacement for both, and `LSequence` stays scoped to pure motion composition. If porting code that relies on either, replace it with an `async` method, or (as a last resort during migration) a throwaway motion:

```csharp
LMotion.Create(0f, 1f, delay).WithOnComplete(action).RunWithoutBinding();
```

## Migrating from DOTween

This table assumes the porting direction has already been decided. It
hasn't been decided for you by default — whether DOTween or LitMotion
governs a given module is a standing project/module choice, not this
skill's to assume; see `dotween-tweening`'s own
[coexistence-and-migration.md](../../dotween-tweening/references/coexistence-and-migration.md)
for that checklist and for the DOTween-side vocabulary (its uGUI/TextMeshPro
shortcuts, its `UNITASK_DOTWEEN_SUPPORT` async integration) before treating
every existing DOTween call site as something to port.

| DOTween | LitMotion | Source |
|---|---|---|
| `transform.DOMove(end, dur)` | `LMotion.Create(transform.position, end, dur).BindToPosition(transform)` | [Migrate from DOTween](https://annulusgames.github.io/LitMotion/articles/en/migrate-from-dotween.html) |
| `DOTween.To(() => v, x => v = x, end, dur)` | `LMotion.Create(v, end, dur).Bind(x => v = x)` | same |
| `.From(start)` | Pass `start` as `LMotion.Create`'s first argument directly | same |
| `.DOPunchPosition(...)` / `.DOShakePosition(...)` | `LMotion.Punch.Create(...)` / `LMotion.Shake.Create(...)` | same |
| `tween.SetLoops(n, LoopType.Yoyo).SetEase(e)` | `builder.WithLoops(n, LoopType.Yoyo).WithEase(e)` | same |
| `tween.Pause()` / `.Complete()` / `.Kill()` | `handle.PlaybackSpeed = 0f` / `.Complete()` / `.Cancel()` | same |
| `DOTween.Sequence().Append/Join/Insert(...)` | `LSequence.Create().Append/Join/Insert(...).Run()` — no callback support, see above | same |
| `tween.SetUpdate(UpdateType.Fixed)` | `builder.WithScheduler(MotionScheduler.FixedUpdate)` | same |
| `tween.SetLink(gameObject)` | `handle.AddTo(gameObject)` | same |
| `yield return tween.WaitForCompletion()` / `await tween.AsyncWaitForCompletion()` | `yield return handle.ToYieldInstruction()` / `await handle` | same |
| Safe Mode (log exceptions as warnings) | `MotionDispatcher.RegisterUnhandledExceptionHandler(ex => Debug.LogWarning(ex))` | same |
| `SetSpeedBased()`, `DoPath()` | Not supported — compute duration from distance; combine with Unity Splines for paths | same |

## Migrating from LeanTween

| LeanTween | LitMotion | Source |
|---|---|---|
| `LeanTween.move(go, end, dur)` | `LMotion.Create(transform.position, end, dur).BindToPosition(transform)` | [Migrate from LeanTween](https://annulusgames.github.io/LitMotion/articles/en/migrate-from-leantween.html) |
| `LeanTween.value(go, x => v = x, v, end, dur)` | `LMotion.Create(v, end, dur).Bind(x => v = x)` | same |
| `.from(start)` | Pass `start` as `LMotion.Create`'s first argument | same |
| `descr.setRepeat(n).setLoopPingPong().setEase(t)` | `builder.WithLoops(n, LoopType.Flip).WithEase(e)` | same |
| `descr.pause()` / `.cancel()` | `handle.PlaybackSpeed = 0f` / `handle.Cancel()` | same |
| `LeanTween.DelayedCall()`, `LTSpline` | Not supported — see the design-decision note above; combine with Unity Splines for paths | same |

## Migrating from PrimeTween

| PrimeTween | LitMotion | Source |
|---|---|---|
| `Tween.Position(transform, end, dur)` | `LMotion.Create(transform.position, end, dur).BindToPosition(transform)` | [Migrate from PrimeTween](https://annulusgames.github.io/LitMotion/articles/en/migrate-from-primetween.html) |
| `Tween.Custom(v, end, dur, x => value = x)` | `LMotion.Create(v, end, dur).Bind(x => value = x)` | same |
| `Tween.ShakePosition/PunchPosition(...)` | `LMotion.Shake.Create(...)` / `LMotion.Punch.Create(...)` | same |
| `cycle: n, cycleMode: CycleMode.Yoyo` | `.WithLoops(n, LoopType.Yoyo)` | same |
| `tween.isPaused = true` / `.Complete()` / `.Kill()` | `handle.PlaybackSpeed = 0f` / `.Complete()` / `.Cancel()` | same |
| `Sequence.Create().Chain/Group/Insert(...)` | `LSequence.Create().Append/Join/Insert(...).Run()` | same |
| `new TweenSettings(dur, useFixedUpdate: true)` | `.WithScheduler(MotionScheduler.FixedUpdate)` | same |
| `[SerializeField] TweenSettings<float>` | `[SerializeField] SerializableMotionSettings<float, NoOptions>` | same |
| `Tween.Delay()`, `Tween.*AtSpeed()` | Not supported — see design-decision note; compute duration from distance | same |

## Migrating from LitMotion v1

| v1 | v2 | Source |
|---|---|---|
| `MotionBuilder.Preserve()` | `MotionHandle.Preserve()` (moved to the handle) | [Migrate from v1](https://annulusgames.github.io/LitMotion/articles/en/migrate-from-v1.html) |
| `BindToUnityLogger()`/`BindToProgress()` in core namespace | Moved to `LitMotion.Extensions` — reference that asmdef | same |
| `BindWithState(state, (x, state) => ...)` | `Bind(state, (x, state) => ...)` — now an overload of `Bind` | same |
| `ToYieldInteraction()` | Renamed `ToYieldInstruction()` (typo fix) | same |
| `LoopType.Yoyo` (old meaning: flip back and forth) | That behavior is now `LoopType.Flip`; `LoopType.Yoyo` means something different in v2 — see [motion-settings.md](motion-settings.md) | same |
| `LinkBehaviour`, `CancelBehaviour` | Renamed `LinkBehavior`, `CancelBehavior` (American spelling) | same |
| `WithBindOnSchedule()` | Renamed `WithImmediateBind()`; default changed to `true` | same |
| `ManualMotionDispatcher.Update(...)` (static) | `ManualMotionDispatcher.Default.Update(...)` (instance-based; multiple dispatchers now possible) | same |
| `MotionTracker` window | Replaced by the [LitMotion Debugger](async-lifecycle-and-debugging.md) | same |
