# Async, Exceptions, Manual Dispatch, Editor Playback, Debugging

Sources (under the Docs base): await-motion-in-coroutine, await-motion-in-async-await, integration-unitask, convert-to-disposable, exception-handling, manual-motion-dispatcher, play-motion-in-editor, avoid-dynamic-memory-allocation, litmotion-debugger; source `Runtime/CancelBehavior.cs`.

## Awaiting a handle

| Mechanism | Use when |
|---|---|
| `await handle` | Simplest; no cancellation token |
| `handle.ToUniTask(CancellationToken)` | UniTask installed; preferred (best performance per Design Philosophy) |
| `handle.ToValueTask(...)` | No UniTask; accepts `ValueTask`-in-Unity overhead |
| `handle.ToAwaitable(...)` | Unity 2023.1+, no UniTask |
| `handle.ToYieldInstruction()` | Legacy coroutine only |

```csharp
await LMotion.Create(0f, 10f, 1f).RunWithoutBinding()
    .ToAwaitable(CancelBehavior.Complete, true, cancellationToken);
```

The 3-argument `ToValueTask`/`ToAwaitable` takes `(CancelBehavior, bool cancelAwaitOnMotionCanceled, CancellationToken)`.

| `CancelBehavior` (when the awaiting token is cancelled) | Effect |
|---|---|
| `None` | Motion keeps running |
| `Cancel` | Motion cancelled |
| `Complete` | Motion jumps to its end value |

`cancelAwaitOnMotionCanceled = true` also cancels the await when the handle is cancelled elsewhere.

## Other lifecycle

| Topic | Fact |
|---|---|
| `handle.ToDisposable(DisposeBehavior)` | Default `DisposeBehavior.Cancel`; `Complete` makes `Dispose()` call `Complete()`. For an existing `IDisposable` scope |
| Exceptions | `MotionDispatcher.RegisterUnhandledExceptionHandler(Action<Exception>)` replaces the default `Debug.LogException` for `Bind`/`WithOnComplete` throws; `GetUnhandledExceptionHandler()` reads it. Add `WithCancelOnError(true)` to also stop the motion |
| `ManualMotionDispatcher` | `new ManualMotionDispatcher()` then `WithScheduler(d.Scheduler)` and `d.Update(dt)`; `.Default` is global and `MotionScheduler.Manual` aliases `Default.Scheduler` |
| Editor playback | A motion created while `!Application.isPlaying` auto-schedules on `EditorApplication.update`; or `WithScheduler(EditorMotionScheduler.Update)` |
| `MotionDispatcher.EnsureStorageCapacity<TValue,TOptions,TAdapter>(int)` | Pre-sizes storage per exact type triple so it never resizes; call at startup per high-volume combination |
| LitMotion Debugger | `Window > LitMotion Debugger`, **Enable**; **Stack Trace** records creation site. `WithDebugName`/`GetDebugName()`; names are stripped from Release unless `LITMOTION_DEBUG` is defined |

```csharp
MotionDispatcher.EnsureStorageCapacity<float, NoOptions, FloatMotionAdapter>(500);
MotionDispatcher.EnsureStorageCapacity<Vector3, NoOptions, Vector3MotionAdapter>(1000);
```

**Caveat:** with Domain Reload disabled, `ManualMotionDispatcher.Default` keeps state across play sessions; call `ManualMotionDispatcher.Default.Reset()` in `Awake()`.

**Caveat:** the Debugger has a documented performance cost while enabled.
