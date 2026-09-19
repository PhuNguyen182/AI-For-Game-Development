# Motion Configuration — `With-` Methods, Scheduler, MotionSettings

Sources: [Motion Configuration](https://annulusgames.github.io/LitMotion/articles/en/motion-configuration.html), [MotionSettings](https://annulusgames.github.io/LitMotion/articles/en/motion-settings.html), verified against [`MotionBuilderExtensions.cs`](https://github.com/annulusgames/LitMotion/blob/main/src/LitMotion/Assets/LitMotion/Runtime/MotionBuilderExtensions.cs), [`LoopType.cs`](https://github.com/annulusgames/LitMotion/blob/main/src/LitMotion/Assets/LitMotion/Runtime/LoopType.cs), [`DelayType.cs`](https://github.com/annulusgames/LitMotion/blob/main/src/LitMotion/Assets/LitMotion/Runtime/DelayType.cs).
Covers: SKILL.md §4 — **"Configure via the `With-` chain rather than re-deriving the same behavior by hand"**.

Every `With-` method returns the same `MotionBuilder`, so multiple settings
chain freely; order among `With-` calls does not matter, but they must be
called before `Bind`/`RunWithoutBinding`.

## Table of contents
- [Core `With-` methods](#core-with--methods)
- [`LoopType`](#looptype)
- [`DelayType`](#delaytype)
- [`MotionScheduler`](#motionscheduler-timing)
- [Type-restricted `With-` methods](#type-restricted-with--methods)
- [`MotionSettings<T,TOptions>` and `SerializableMotionSettings`](#motionsettingsttoptions-and-serializablemotionsettings)

## Core `With-` methods

| Method | Effect | Default | Source |
|---|---|---|---|
| `WithEase(Ease)` | Applies an easing curve (see enum below) | `Ease.Linear` | [Motion Configuration](https://annulusgames.github.io/LitMotion/articles/en/motion-configuration.html) |
| `WithEase(AnimationCurve)` | Custom curve; sets `Ease.CustomAnimationCurve` — do not also pass `Ease` | — | same |
| `WithDelay(float, DelayType, bool skipValuesDuringDelay)` | Delays start; `skipValuesDuringDelay` skips `Bind` calls during the delay | `skipValuesDuringDelay = true` | same |
| `WithLoops(int, LoopType)` | Repeat count; `-1` loops forever until stopped | `1` loop, `LoopType.Restart` | same |
| `WithOnComplete(Action)` | Callback at final completion | — | same |
| `WithOnCancel(Action)` | Callback when `Cancel()`'d | — | same |
| `WithOnLoopComplete(Action<int>)` | Callback after each loop; fires before `OnComplete` on the final loop | — | same |
| `WithScheduler(IMotionScheduler)` | Update timing source (table below) | `MotionScheduler.Update` | same |
| `WithCancelOnError(bool)` | Cancels the motion if `Bind`/`WithOnComplete` throws uncaught | `false` | same |
| `WithImmediateBind(bool)` | Runs `Bind` once immediately at scheduling time | `true` | same |
| `WithDebugName(string)` | Custom name shown in the LitMotion Debugger | auto-generated | same |
| `ToMotionSettings()` | Captures the current chain into a reusable `MotionSettings<T,TOptions>` | — | [MotionSettings](https://annulusgames.github.io/LitMotion/articles/en/motion-settings.html) |

## `LoopType`

| Value | Behavior | Source |
|---|---|---|
| `Restart` (default) | Resets to the start value at the end of each loop | [`LoopType.cs`](https://github.com/annulusgames/LitMotion/blob/main/src/LitMotion/Assets/LitMotion/Runtime/LoopType.cs) |
| `Flip` | Cycles back and forth between end and start (this is what "yoyo" meant in LitMotion v1) | same |
| `Incremental` | Each loop's end value becomes the next loop's added offset | same |
| `Yoyo` | Plays forward to the end value, then backward to the start, per loop | same |

**Critical caveat**: `LoopType.Yoyo`'s behavior changed in v2 — the v1 meaning is now `LoopType.Flip`. See [migration-and-rx-integration.md](migration-and-rx-integration.md) if porting v1 code.

## `DelayType`

| Value | Behavior | Source |
|---|---|---|
| `FirstLoop` (default) | Delay applies only before the first loop | [`DelayType.cs`](https://github.com/annulusgames/LitMotion/blob/main/src/LitMotion/Assets/LitMotion/Runtime/DelayType.cs) |
| `EveryLoop` | Delay applies before every loop | same |

## `MotionScheduler` timing

Every scheduler has an `-IgnoreTimeScale` variant (uses `Time.unscaledDeltaTime`) and a `-Realtime` variant (`Time.realtimeSinceStartup`), for each PlayerLoop stage below.

| Base scheduler | Runs at | Source |
|---|---|---|
| `Initialization` | PlayerLoop `Initialization` | [Motion Configuration](https://annulusgames.github.io/LitMotion/articles/en/motion-configuration.html) |
| `EarlyUpdate` | PlayerLoop `EarlyUpdate` | same |
| `FixedUpdate` | PlayerLoop `FixedUpdate` — required to match physics-driven state | same |
| `PreUpdate` | PlayerLoop `PreUpdate` | same |
| `Update` (default) | PlayerLoop `Update` | same |
| `PreLateUpdate` | PlayerLoop `PreLateUpdate` | same |
| `PostLateUpdate` | PlayerLoop `PostLateUpdate` | same |
| `TimeUpdate` | PlayerLoop `TimeUpdate` | same |
| `Manual` | `ManualMotionDispatcher.Default.Update(deltaTime)` — see [async-lifecycle-and-debugging.md](async-lifecycle-and-debugging.md) | same |
| `EditorMotionScheduler.Update` (`LitMotion.Editor`, editor-only) | `EditorApplication.update` | [Play Motion in Editor](https://annulusgames.github.io/LitMotion/articles/en/play-motion-in-editor.html) |

**Critical caveat**: pick the scheduler deliberately — `Time.timeScale` applies to every non-`IgnoreTimeScale`/non-`Realtime` variant, so a pause-menu tween built on the default `Update` scheduler will freeze along with gameplay unless that is the intended behavior.

## Type-restricted `With-` methods

| Method | Applies to | Effect | Source |
|---|---|---|---|
| `WithRoundingMode(RoundingMode)` | `int`/`long` motions (`IntegerOptions`) | `ToEven` (default), `AwayFromZero`, `ToZero`, `ToPositiveInfinity`, `ToNegativeInfinity` | [Motion Configuration](https://annulusgames.github.io/LitMotion/articles/en/motion-configuration.html) |
| `WithFrequency(int)` | Punch/Shake (`PunchOptions`/`ShakeOptions`) | Oscillation count until settling; default `10` | see [sequence-and-vibration.md](sequence-and-vibration.md) |
| `WithDampingRatio(float)` | Punch/Shake | `1` = fully damped, `0` = never damps; default `1` | same |
| `WithRandomSeed(uint)` | Shake and string motions (`ShakeOptions`/`StringOptions`) | Deterministic random seed | same, and [text-and-tmp-animation.md](text-and-tmp-animation.md) |
| `WithScrambleChars(ScrambleMode)` / `WithScrambleChars(FixedString64Bytes)` | String motions | Fills not-yet-revealed characters — see [text-and-tmp-animation.md](text-and-tmp-animation.md) | [`MotionBuilderExtensions.cs`](https://github.com/annulusgames/LitMotion/blob/main/src/LitMotion/Assets/LitMotion/Runtime/MotionBuilderExtensions.cs) |
| `WithRichText(bool = true)` | String motions | Advances characters correctly around rich-text tags | same |

**Critical caveat**: the upstream Motion Configuration page names this method `WithScrambleMode`, but the shipped API (`MotionBuilderExtensions.cs`) calls it `WithScrambleChars` — use the source-verified name.

## `MotionSettings<T,TOptions>` and `SerializableMotionSettings`

```csharp
// Object initializer
var settings = new MotionSettings<float, NoOptions>
{
    StartValue = 0f, EndValue = 10f, Duration = 2f, Ease = Ease.OutQuad
};

// Or captured from a builder
var settings = LMotion.Create(0f, 10f, 2f).WithEase(Ease.OutQuad).ToMotionSettings();

// Reused
LMotion.Create(settings).Bind(x => { });

// MotionSettings<T,TOptions> is a record — `with` copies and overrides
var faster = settings with { Duration = 1f };
```

| Type | Use when | Source |
|---|---|---|
| `MotionSettings<T,TOptions>` | Reusing/storing a configuration in plain C# | [MotionSettings](https://annulusgames.github.io/LitMotion/articles/en/motion-settings.html) |
| `SerializableMotionSettings<T,TOptions>` | The same, but exposed as an editable `[SerializeField]` in the Inspector | same |
