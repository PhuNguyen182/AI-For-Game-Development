# Coroutines, Native Async, and UniTask Integration

Source: [DOTween Documentation](https://dotween.demigiant.com/documentation.php), [UniTask](https://github.com/Cysharp/UniTask).
Covers: SKILL.md §4 — "Await a tween through UniTask's native DOTween support once UniTask is in the project, not `AsyncWaitForCompletion()`".
Cross-reference: this is this skill's primary interop surface with the
**`unitask-async-programming`** skill.

## DOTween's own coroutine waits

A tween exposes `IEnumerator`-returning wait methods for use inside a
legacy `StartCoroutine` flow: `WaitForCompletion()`, `WaitForKill()`,
`WaitForRewind()`, `WaitForElapsedLoops(count)`, `WaitForPosition(time)`,
`WaitForStart()`.

```csharp
IEnumerator PlayThenContinue()
{
    yield return transform.DOMoveX(4, 1).WaitForCompletion();
    // runs after the tween completes
}
```

## Native `AsyncWaitForCompletion()`

DOTween also exposes a `Task`-returning `AsyncWaitForCompletion()` for
plain `async`/`await` without any other package:

```csharp
await transform.DOMoveX(4, 1).AsyncWaitForCompletion();
```

**Documented caveat**: this path has reported issues freezing WebGL
builds. Treat it as usable on non-WebGL targets, but confirm on the
project's actual WebGL build before depending on it there — prefer
UniTask's native integration below wherever UniTask is already a project
dependency, since it doesn't carry this caveat.

## UniTask's native DOTween support — the preferred path

Once `unitask-async-programming` is in the project, enable DOTween
integration with the `UNITASK_DOTWEEN_SUPPORT` scripting define (set after
importing DOTween, per UniTask's own setup instructions). This makes a
`Tween`/`Tweener`/`Sequence` directly awaitable and cancelable:

```csharp
await transform.DOMoveX(2, 10);
await transform.DOMoveZ(5, 20);

// with cancellation, composed with UniTask.WhenAll
await UniTask.WhenAll(
    transform.DOMoveX(10, 3).WithCancellation(cancellationToken),
    transform.DOScale(10, 3).WithCancellation(cancellationToken));
```

The default `await`/`WithCancellation()` behavior waits for the tween's
completion (covering both a normal finish and a `Kill()`/`Complete()`
outcome). For a reusable tween created with `SetAutoKill(false)` (per
[settings-and-callbacks.md](settings-and-callbacks.md)), additional
extension methods target a specific state transition instead of overall
completion: `AwaitForComplete`, `AwaitForPause`, `AwaitForPlay`,
`AwaitForRewind`, `AwaitForStepComplete`.

### Which mechanism to reach for

| Situation | Use |
|---|---|
| UniTask is a project dependency (the common case per `unitask-async-programming`) | `await tween` / `tween.WithCancellation(token)` — ties into `GetCancellationTokenOnDestroy()` the same way any other UniTask-awaited operation does |
| UniTask is unavailable, and a plain `Task`/`async` method is acceptable | `AsyncWaitForCompletion()` — confirm the WebGL caveat above doesn't apply to this project's targets |
| A legacy `IEnumerator` coroutine, not an `async` method | `yield return tween.WaitForCompletion()` (or the other `WaitFor*` variants for a different state) |
| A reusable (`SetAutoKill(false)`) tween needs to be awaited for a *specific* state transition, not full completion | `AwaitForPause`/`AwaitForPlay`/`AwaitForRewind`/`AwaitForStepComplete` |

**Default to the UniTask path whenever `unitask-async-programming` already
governs the project's async style** — it's the option that composes with
`GetCancellationTokenOnDestroy()`, `UniTask.WhenAll`/`WhenAny`, and the
rest of that skill's cancellation discipline, rather than introducing a
second, separately-managed cancellation story alongside it. Route to
`unitask-async-programming` for anything beyond the DOTween-specific
extension methods themselves — the cancellation-token lifetime rules,
`PlayerLoopTiming`, and multi-awaiter (`.Preserve()`) concerns are that
skill's, not this one's.
