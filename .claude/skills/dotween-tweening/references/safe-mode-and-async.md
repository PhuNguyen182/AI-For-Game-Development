# Safe Mode, recycling, allocation, awaiting

## Safe Mode
`useSafeMode` (default `true`) lets DOTween handle a target destroyed mid-tween at a small speed cost. Leave it on.
iOS: Safe Mode works correctly only with "Strip Assemblies" stripping level or "Slow and Safe" Script Call Optimization; check the project's iOS settings.

## Recycling
`SetRecyclable(true)` or `recycleAllByDefault` pools a killed tween. The C# reference is then reused by an unrelated future tween, so a reference held past the kill is a use-after-recycle bug. Null it in `OnKill`:
```csharp
myTween = transform.DOMoveX(4, 1).SetRecyclable(true);
myTween.OnKill(() => myTween = null);
```
Enable `recycleAllByDefault` only once every held tween reference follows this.

## Allocation
- `DOTween.To(getter, setter, ...)` allocates the closures per call; a shortcut still allocates the `Tweener` unless recycled.
- LitMotion's struct `MotionHandle` allocates nothing per motion with no recycling scheme.
- Hundreds of simultaneous tweens on a hot path is a reason to prefer LitMotion for that system, once profiled ([coexistence-and-migration.md](coexistence-and-migration.md)).

## Awaiting completion
| Situation | Use |
|---|---|
| UniTask in project (`unitask-async-programming`) | `await tween` / `tween.WithCancellation(token)` (`GetCancellationTokenOnDestroy()`) |
| No UniTask, plain `async` | `await tween.AsyncWaitForCompletion()` — reported to freeze WebGL builds; verify there |
| Legacy coroutine | `yield return tween.WaitForCompletion()`; also `WaitForKill`, `WaitForRewind`, `WaitForElapsedLoops(n)`, `WaitForPosition(t)`, `WaitForStart` |
| `SetAutoKill(false)` tween, specific state | `AwaitForComplete`, `AwaitForPause`, `AwaitForPlay`, `AwaitForRewind`, `AwaitForStepComplete` |

UniTask integration needs the `UNITASK_DOTWEEN_SUPPORT` scripting define, set after importing DOTween:
```csharp
await UniTask.WhenAll(
    transform.DOMoveX(10, 3).WithCancellation(ct),
    transform.DOScale(10, 3).WithCancellation(ct));
```
Default `await`/`WithCancellation` covers a normal finish and `Kill()`/`Complete()`. Unverified: the full list of UniTask cancel-behaviour options; check UniTask's source before naming an enum member. Token lifetime, `PlayerLoopTiming` and `.Preserve()` belong to `unitask-async-programming`.
