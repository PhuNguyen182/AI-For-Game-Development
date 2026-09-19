# Async Completion, Exceptions, Manual Dispatch, Editor Playback, Debugging

Sources: [Await Motion in Coroutine](https://annulusgames.github.io/LitMotion/articles/en/await-motion-in-coroutine.html), [Await Motion in async/await](https://annulusgames.github.io/LitMotion/articles/en/await-motion-in-async-await.html), [Convert to IDisposable](https://annulusgames.github.io/LitMotion/articles/en/convert-to-disposable.html), [Exception Handling](https://annulusgames.github.io/LitMotion/articles/en/exception-handling.html), [ManualMotionDispatcher](https://annulusgames.github.io/LitMotion/articles/en/manual-motion-dispatcher.html), [Play Motion in Editor](https://annulusgames.github.io/LitMotion/articles/en/play-motion-in-editor.html), [Avoid Dynamic Memory Allocation](https://annulusgames.github.io/LitMotion/articles/en/avoid-dynamic-memory-allocation.html), [LitMotion Debugger](https://annulusgames.github.io/LitMotion/articles/en/litmotion-debugger.html).
Covers: SKILL.md §4 — **"Await completion with the mechanism matching the call site"**, **"Verify the zero-allocation and Burst claims with the Profiler before shipping a hot-path or high-volume motion"**.

## Table of contents
- [Awaiting a `MotionHandle`](#awaiting-a-motionhandle)
- [`CancelBehavior`](#cancelbehavior)
- [`ToDisposable`](#todisposable)
- [Exception handling](#exception-handling)
- [`ManualMotionDispatcher`](#manualmotiondispatcher)
- [Editor playback](#editor-playback)
- [Avoiding dynamic allocation](#avoiding-dynamic-allocation)
- [LitMotion Debugger](#litmotion-debugger)

## Awaiting a `MotionHandle`

| Mechanism | Use when | Source |
|---|---|---|
| `await handle` (`GetAwaiter()`) | Simplest case, no cancellation token needed | [Await in async/await](https://annulusgames.github.io/LitMotion/articles/en/await-motion-in-async-await.html) |
| `handle.ToUniTask(CancellationToken)` | UniTask is installed — preferred for real projects (best performance, per Design Philosophy) | [UniTask integration](https://annulusgames.github.io/LitMotion/articles/en/integration-unitask.html) |
| `handle.ToValueTask(CancellationToken)` | UniTask unavailable; accepts the `ValueTask`-in-Unity overhead noted upstream | [Await in async/await](https://annulusgames.github.io/LitMotion/articles/en/await-motion-in-async-await.html) |
| `handle.ToAwaitable(CancellationToken)` | Unity 2023.1+, no UniTask dependency wanted | same |
| `handle.ToYieldInstruction()` | Inside a legacy `IEnumerator` coroutine only — coroutines can't return values or await in parallel | [Await in Coroutine](https://annulusgames.github.io/LitMotion/articles/en/await-motion-in-coroutine.html) |

```csharp
async ValueTask ExampleAsync(CancellationToken cancellationToken)
{
    await LMotion.Create(0f, 10f, 1f)
        .RunWithoutBinding()
        .ToAwaitable(CancelBehavior.Complete, true, cancellationToken);
}
```

The 3-argument `ToValueTask`/`ToAwaitable` overload takes `(CancelBehavior, bool cancelAwaitOnMotionCanceled, CancellationToken)`.

## `CancelBehavior`

Controls what happens to the motion when the awaiting async method itself is cancelled via its token.

| Value | Effect | Source |
|---|---|---|
| `None` | Motion is left running | [`CancelBehavior.cs`](https://github.com/annulusgames/LitMotion/blob/main/src/LitMotion/Assets/LitMotion/Runtime/CancelBehavior.cs) |
| `Cancel` | Motion is cancelled | same |
| `Complete` | Motion is completed (jumps to end value) | same |

`cancelAwaitOnMotionCanceled = true` additionally makes the **await itself**
throw/cancel if the `MotionHandle` is cancelled from elsewhere.

## `ToDisposable`

```csharp
var disposable = handle.ToDisposable(DisposeBehavior.Complete); // default is DisposeBehavior.Cancel
disposable.Dispose(); // calls handle.Complete()
```

Use when a motion needs to participate in an existing `IDisposable` scope
(a `CompositeDisposable`, a DI-scoped disposal bag) rather than LitMotion's
own `AddTo`/`CompositeMotionHandle` — source: [Convert to IDisposable](https://annulusgames.github.io/LitMotion/articles/en/convert-to-disposable.html).

## Exception handling

`MotionDispatcher.RegisterUnhandledExceptionHandler(Action<Exception>)`
replaces the default handler (`Debug.LogException`) for uncaught exceptions
inside `Bind`/`WithOnComplete`. `MotionDispatcher.GetUnhandledExceptionHandler()`
retrieves the current one. Combine with `WithCancelOnError(true)` (per
[motion-settings.md](motion-settings.md)) to also stop the motion on error —
source: [Exception Handling](https://annulusgames.github.io/LitMotion/articles/en/exception-handling.html).

## `ManualMotionDispatcher`

Drives motions without a PlayerLoop tick — useful for custom simulation
loops or deterministic testing.

```csharp
var dispatcher = new ManualMotionDispatcher();
LMotion.Create(0f, 10f, 2f).WithScheduler(dispatcher.Scheduler).BindToUnityLogger();
dispatcher.Update(0.1); // advance by 0.1s
```

`ManualMotionDispatcher.Default` is a globally available instance; `MotionScheduler.Manual` is an alias for `ManualMotionDispatcher.Default.Scheduler`. **Critical caveat**: with Domain Reload disabled, `ManualMotionDispatcher.Default`'s state survives play sessions unexpectedly — call `ManualMotionDispatcher.Default.Reset()` explicitly in `Awake()` to avoid stale motions. Source: [ManualMotionDispatcher](https://annulusgames.github.io/LitMotion/articles/en/manual-motion-dispatcher.html).

## Editor playback

Motions created while `!Application.isPlaying` (Edit Mode) auto-schedule on
`EditorApplication.update`; `EditorMotionScheduler.Update` (`LitMotion.Editor`
namespace) can be set explicitly via `WithScheduler` for the same effect —
source: [Play Motion in Editor](https://annulusgames.github.io/LitMotion/articles/en/play-motion-in-editor.html).

## Avoiding dynamic allocation

`MotionDispatcher.EnsureStorageCapacity<TValue,TOptions,TAdapter>(int capacity)`
pre-grows the internal per-type-combination storage array so it never resizes
at runtime. Storage is keyed by the exact `(TValue, TOptions, TAdapter)`
triple, so call it once per combination expected at high volume, typically at
startup:

```csharp
MotionDispatcher.EnsureStorageCapacity<float, NoOptions, FloatMotionAdapter>(500);
MotionDispatcher.EnsureStorageCapacity<Vector3, NoOptions, Vector3MotionAdapter>(1000);
```

Source: [Avoid Dynamic Memory Allocation](https://annulusgames.github.io/LitMotion/articles/en/avoid-dynamic-memory-allocation.html).

## LitMotion Debugger

`Window > LitMotion Debugger`, click **Enable** to activate; **Stack Trace**
additionally records where each motion was created. `WithDebugName(string)`
sets a searchable name (default: `` MotionHandle`{StorageId}({Index}:{Version}) ``);
`handle.GetDebugName()` reads it back. Debug names are stripped from Release
builds unless `LITMOTION_DEBUG` is added to Scripting Define Symbols.

**Critical caveat**: the debugger window has a real, documented performance cost while enabled — keep it off outside active debugging sessions. Source: [LitMotion Debugger](https://annulusgames.github.io/LitMotion/articles/en/litmotion-debugger.html).
