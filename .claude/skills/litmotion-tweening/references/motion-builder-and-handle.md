# MotionBuilder and MotionHandle

Sources (under the Docs base): basic-concepts, binding, motion-control; source `Runtime/MotionBuilder.cs`, `MotionHandle.cs`, `MotionHandleExtensions.cs`, `LinkBehavior.cs`.

`LMotion.Create` returns a `MotionBuilder<TValue,TOptions,TAdapter>` struct; nothing is scheduled until `Bind`/`BindTo*`/`RunWithoutBinding`, which returns a `MotionHandle`.

## Create overloads

| Overload | Adapter / options |
|---|---|
| `Create(from, to, float duration)` for `float`, `double`, `int`, `long`, `Vector2/3/4`, `Quaternion`, `Color`, `Rect` | Matching built-in adapter; `int`/`long` use `IntegerOptions`, others `NoOptions` |
| `Create<TValue,TOptions,TAdapter>(in from, in to, duration)` | Custom; see [custom-adapters.md](custom-adapters.md) |
| `Create(MotionSettings<T,TOptions>)` | Stored config; see [motion-settings.md](motion-settings.md) |

## Binding

| Method | Fact that decides |
|---|---|
| `Bind(Action<T>)` | Allocates when the lambda captures |
| `Bind<TState>(state, Action<T,TState>)` (also 2 and 3 state args) | Zero-allocation form |
| `BindTo*` (`LitMotion.Extensions`) | Preferred for supported components; [component-bindings.md](component-bindings.md) |
| `RunWithoutBinding()` | Motion kept only for callbacks, timing or awaiting |

```csharp
LMotion.Create(0f, 10f, 2f).Bind(target, (x, state) => state.Value = x);
```

## MotionHandle

| Member | Fact that decides |
|---|---|
| `IsActive()` / `IsPlaying()` | `IsPlaying()` is `false` after completion even when `Preserve()`d; `IsActive()` is not |
| `Complete()` / `Cancel()` | Throw on an inactive handle; `TryComplete()`/`TryCancel()` return `false` instead |
| `Preserve()` | Not discarded on completion, so replayable by resetting `Time`; must end in `AddTo` or `Cancel()` |
| `PlaybackSpeed` | `0` pauses, negative reverses |
| `Time` | Setting it can complete and discard the motion unless `Preserve()`d |
| `Duration`, `TotalDuration`, `Delay`, `Loops`, `CompletedLoops` | Read-only introspection |
| `AddTo(GameObject or Component, LinkBehavior)` | Ties lifetime to a Unity object |
| `AddTo(CompositeMotionHandle)` | Groups handles under one disposable owner |

| `LinkBehavior` | Effect |
|---|---|
| `CancelOnDestroy` (default) | Cancel when the object is destroyed |
| `CancelOnDisable` | Cancel when disabled |
| `CompleteOnDisable` | Jump to the end value when disabled |

**Caveat:** a finished un-`Preserve()`d motion is auto-discarded, so its handle cannot be reused.
