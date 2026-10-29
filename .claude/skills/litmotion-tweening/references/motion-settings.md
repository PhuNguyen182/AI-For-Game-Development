# Motion Configuration

Sources (under the Docs base): motion-configuration, motion-settings; source `Runtime/MotionBuilderExtensions.cs`, `LoopType.cs`, `DelayType.cs`.

All `With-` methods return the builder, may be chained in any order, and must precede `Bind`/`RunWithoutBinding`.

## Core `With-` methods

| Method | Fact that decides | Default |
|---|---|---|
| `WithEase(Ease)` | Easing curve | `Linear` |
| `WithEase(AnimationCurve)` | Sets `Ease.CustomAnimationCurve`; do not also pass an `Ease` | none |
| `WithDelay(float, DelayType, bool skipValuesDuringDelay)` | `skipValuesDuringDelay` skips `Bind` calls during the delay | `FirstLoop`, `true` |
| `WithLoops(int, LoopType)` | `-1` loops forever | 1, `Restart` |
| `WithOnComplete` / `WithOnCancel` | Final completion / on `Cancel()` | none |
| `WithOnLoopComplete(Action<int>)` | After each loop; fires before `OnComplete` on the last loop | none |
| `WithScheduler(IMotionScheduler)` | Update timing source (below) | `MotionScheduler.Update` |
| `WithCancelOnError(bool)` | Cancel when `Bind`/`WithOnComplete` throws | `false` |
| `WithImmediateBind(bool)` | Run `Bind` once at scheduling | `true` |
| `WithDebugName(string)` | Name in the LitMotion Debugger | auto |
| `ToMotionSettings()` | Capture the chain as reusable `MotionSettings<T,TOptions>` | none |

| `LoopType` | Behaviour |
|---|---|
| `Restart` | Reset to start each loop |
| `Flip` | Back and forth; this is the v1 meaning of "Yoyo" |
| `Incremental` | Each loop's end value is added as an offset to the next |
| `Yoyo` | Forward to end, then backward to start, per loop; changed in v2 |

`DelayType`: `FirstLoop` (default) delays only before the first loop; `EveryLoop` before each.

## Schedulers

Each base scheduler has an `-IgnoreTimeScale` variant (`Time.unscaledDeltaTime`) and a `-Realtime` variant (`Time.realtimeSinceStartup`).

| Scheduler | Runs at |
|---|---|
| `Initialization`, `EarlyUpdate`, `PreUpdate`, `Update` (default), `PreLateUpdate`, `PostLateUpdate`, `TimeUpdate` | The same-named PlayerLoop stage |
| `FixedUpdate` | PlayerLoop `FixedUpdate`; needed to match physics state |
| `Manual` | `ManualMotionDispatcher.Default.Update(dt)`; see [async-lifecycle-and-debugging.md](async-lifecycle-and-debugging.md) |
| `EditorMotionScheduler.Update` (`LitMotion.Editor`) | `EditorApplication.update` |

**Caveat:** every scheduler except `-IgnoreTimeScale`/`-Realtime` follows `Time.timeScale`; a pause-menu tween on the default scheduler freezes with gameplay.

## Type-restricted methods

| Method | Applies to | Fact |
|---|---|---|
| `WithRoundingMode` | `int`/`long` | `ToEven` (default), `AwayFromZero`, `ToZero`, `ToPositiveInfinity`, `ToNegativeInfinity` |
| `WithFrequency(int)` | Punch/Shake | Oscillations until settling; default `10` |
| `WithDampingRatio(float)` | Punch/Shake | `1` fully damped (default), `0` never damps |
| `WithRandomSeed(uint)` | Shake, string motions | Deterministic randomness |
| `WithScrambleChars(ScrambleMode or FixedString64Bytes)`, `WithRichText(bool = true)` | String motions | See [text-and-tmp-animation.md](text-and-tmp-animation.md) |

## Reusable settings

```csharp
var settings = LMotion.Create(0f, 10f, 2f).WithEase(Ease.OutQuad).ToMotionSettings();
LMotion.Create(settings).Bind(x => { });
var faster = settings with { Duration = 1f }; // record copy
```

`MotionSettings<T,TOptions>` is for plain C#; `SerializableMotionSettings<T,TOptions>` is the `[SerializeField]` Inspector form.
