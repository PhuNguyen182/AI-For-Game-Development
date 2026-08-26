# MotionBuilder & MotionHandle — Creation, Binding, Control, Disposal

Sources: [Basic Concepts](https://annulusgames.github.io/LitMotion/articles/en/basic-concepts.html), [Binding](https://annulusgames.github.io/LitMotion/articles/en/binding.html), [Motion Control](https://annulusgames.github.io/LitMotion/articles/en/motion-control.html), verified against [`MotionBuilder.cs`](https://github.com/annulusgames/LitMotion/blob/main/src/LitMotion/Assets/LitMotion/Runtime/MotionBuilder.cs), [`MotionHandle.cs`](https://github.com/annulusgames/LitMotion/blob/main/src/LitMotion/Assets/LitMotion/Runtime/MotionHandle.cs), [`MotionHandleExtensions.cs`](https://github.com/annulusgames/LitMotion/blob/main/src/LitMotion/Assets/LitMotion/Runtime/MotionHandleExtensions.cs).
Covers: SKILL.md §4 — **"Pass captured state into `Bind(TState, Action<TValue,TState>)` instead of a capturing lambda"**, **"Give every `MotionHandle` an explicit disposal path"**.

`MotionBuilder<TValue,TOptions,TAdapter>` is the struct `LMotion.Create()`
returns; every `With-`/`Bind`/`RunWithoutBinding` call consumes and returns it
by chaining. Binding is what actually schedules the motion — nothing runs
before `Bind`/`RunWithoutBinding` is called.

## `LMotion.Create` overloads

| Overload | Value type | Options / Adapter | Source |
|---|---|---|---|
| `Create(float, float, float)` | `float` | `NoOptions` / `FloatMotionAdapter` | [`LMotion.Create.cs`](https://github.com/annulusgames/LitMotion/blob/main/src/LitMotion/Assets/LitMotion/Runtime/LMotion.Create.cs) |
| `Create(double, double, float)` | `double` | `NoOptions` / `DoubleMotionAdapter` | same |
| `Create(int, int, float)` | `int` | `IntegerOptions` / `IntMotionAdapter` | same |
| `Create(long, long, float)` | `long` | `IntegerOptions` / `LongMotionAdapter` | same |
| `Create(Vector2/3/4, ..., float)` | Vector2/3/4 | `NoOptions` / `Vector{2,3,4}MotionAdapter` | same |
| `Create(Quaternion, Quaternion, float)` | `Quaternion` | `NoOptions` / `QuaternionMotionAdapter` | same |
| `Create(Color, Color, float)` | `Color` | `NoOptions` / `ColorMotionAdapter` | same |
| `Create(Rect, Rect, float)` | `Rect` | `NoOptions` / `RectMotionAdapter` | same |
| `Create<TValue,TOptions,TAdapter>(in TValue, in TValue, float)` | any | custom | see [custom-adapters.md](custom-adapters.md) |
| `Create(settings)` where `settings` is `MotionSettings<T,TOptions>` | reuse of stored config | — | see [motion-settings.md](motion-settings.md) |

## Binding — schedules the motion

| Method | Effect | Use when | Source |
|---|---|---|---|
| `Bind(Action<TValue> action)` | Runs `action` every update with the interpolated value | Simple case; note the lambda may capture and allocate | [Binding](https://annulusgames.github.io/LitMotion/articles/en/binding.html) |
| `Bind<TState>(TState state, Action<TValue,TState> action)` | Passes `state` explicitly instead of via closure | The callback needs an outside object/field — the default, zero-allocation form | [Binding](https://annulusgames.github.io/LitMotion/articles/en/binding.html) |
| `Bind<TState0,TState1>(...)` / `Bind<TState0,TState1,TState2>(...)` | Same, with 2–3 state arguments | The callback needs more than one piece of external state | [`MotionBuilder.cs`](https://github.com/annulusgames/LitMotion/blob/main/src/LitMotion/Assets/LitMotion/Runtime/MotionBuilder.cs) |
| `BindTo*` (`LitMotion.Extensions`) | Binds directly to a known Unity component member | Always prefer this over a manual `Bind()` when the target is a supported component — see [component-bindings.md](component-bindings.md) | [Binding](https://annulusgames.github.io/LitMotion/articles/en/binding.html) |
| `RunWithoutBinding()` | Schedules the motion with no value consumer | The motion exists only for its callbacks/timing (e.g. a delay) | [Binding](https://annulusgames.github.io/LitMotion/articles/en/binding.html) |

```csharp
class FooClass { public float Value { get; set; } }
var target = new FooClass();

// Zero-allocation: state passed explicitly instead of captured by a closure
LMotion.Create(0f, 10f, 2f)
    .Bind(target, (x, state) => state.Value = x);
```

**Critical caveat**: `Bind(Action<TValue>)` allocates whenever the lambda captures an outside variable. Prefer the `Bind(TState, ...)` overload whenever the state already exists as an object reference — per `performance-and-algorithms.md`'s Memory discipline section.

## `MotionHandle` — control and lifecycle

All binding methods return a `MotionHandle` struct (`StorageId`/`Index`/`Version`).

| Member | Effect | Source |
|---|---|---|
| `IsValid()` / `IsActive()` | Whether the handle still refers to a live motion | [`MotionHandleExtensions.cs`](https://github.com/annulusgames/LitMotion/blob/main/src/LitMotion/Assets/LitMotion/Runtime/MotionHandleExtensions.cs) |
| `IsPlaying()` | `false` once the motion has completed, even if `Preserve()`d — unlike `IsActive()` | [Motion Control](https://annulusgames.github.io/LitMotion/articles/en/motion-control.html) |
| `Complete()` / `TryComplete()` | Finish immediately; `Try-` returns `false` instead of throwing if inactive | [Motion Control](https://annulusgames.github.io/LitMotion/articles/en/motion-control.html) |
| `Cancel()` / `TryCancel()` | Stop without reaching the end value | [Motion Control](https://annulusgames.github.io/LitMotion/articles/en/motion-control.html) |
| `Preserve()` | Motion is not auto-discarded on completion, so it can be replayed by resetting `Time` | [Motion Control](https://annulusgames.github.io/LitMotion/articles/en/motion-control.html) |
| `PlaybackSpeed` (property) | Scale playback rate; `0` pauses, negative reverses | [Motion Control](https://annulusgames.github.io/LitMotion/articles/en/motion-control.html) |
| `Time` (property) | Manually set elapsed time; also completes/discards unless `Preserve()`d | [Motion Control](https://annulusgames.github.io/LitMotion/articles/en/motion-control.html) |
| `Duration` / `TotalDuration` / `Delay` / `Loops` / `CompletedLoops` (readonly properties) | Introspect the motion's configuration/progress | [Motion Control](https://annulusgames.github.io/LitMotion/articles/en/motion-control.html) |
| `AddTo(GameObject/Component, LinkBehavior = CancelOnDestroy)` | Ties the motion's lifetime to a Unity object | [Motion Control](https://annulusgames.github.io/LitMotion/articles/en/motion-control.html) |
| `AddTo(CompositeMotionHandle)` | Groups several handles under one disposable owner | [Motion Control](https://annulusgames.github.io/LitMotion/articles/en/motion-control.html) |

## `LinkBehavior` (argument to `AddTo`)

| Value | Behavior | Source |
|---|---|---|
| `CancelOnDestroy` (default) | Cancels the motion when the linked object is destroyed | [`LinkBehavior.cs`](https://github.com/annulusgames/LitMotion/blob/main/src/LitMotion/Assets/LitMotion/Runtime/LinkBehavior.cs) |
| `CancelOnDisable` | Cancels when the linked `GameObject`/`Component` is disabled | same |
| `CompleteOnDisable` | Completes (jumps to end value) when disabled, instead of cancelling | same |

**Critical caveat**: a motion is auto-discarded once it finishes, so an un-`Preserve()`d `MotionHandle` cannot be reused — calling `Complete()`/`Cancel()` a second time throws unless guarded with `TryComplete()`/`TryCancel()`. A `Preserve()`d handle runs until `Cancel()` is called explicitly and must always end up in an `AddTo()` scope or an explicit cancel path.
