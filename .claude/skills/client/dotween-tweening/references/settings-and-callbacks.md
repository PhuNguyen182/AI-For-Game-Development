# Tweener/Sequence Settings and Callbacks

Source: [DOTween Documentation](https://dotween.demigiant.com/documentation.php).
Covers: SKILL.md §4 — "Configure via `Set*` chain methods deliberately, especially `SetUpdate`", "Attach callbacks by name, never rely on `AppendCallback` for anything that must propagate an exception".

## `Set*` options (chainable on both Tweener and Sequence)

| Method | Effect |
|---|---|
| `SetEase(Ease)` | Applies an easing curve (`Ease.InOutQuad`, `Ease.Linear`, etc.) |
| `SetLoops(int, LoopType)` | Repeats the tween — `LoopType.Restart` (jump back to start each loop), `LoopType.Yoyo` (play forward then backward), `LoopType.Incremental` (each loop continues from where the last ended, additively) |
| `SetId(object)` | Tags the tween with an identifier usable as a filter for the static `DOTween.*All` control methods (see [control-methods.md](control-methods.md)) |
| `SetTarget(object)` | Sets/overrides what the tween is considered to target, for the same filtering purpose |
| `SetAutoKill(bool)` | `true` (default): the tween is destroyed on completion. `false`: it persists after completing, replayable via `Restart()`/`Play()` without recreating it |
| `SetRecyclable(bool)` | Marks this specific tween for pooling on kill, independent of the `DOTween.Init` project-wide default — see [safe-mode-recycling-and-performance.md](safe-mode-recycling-and-performance.md) |
| `SetRelative(bool)` | Treats the tween's end value as relative to the start (`startValue + endValue`) rather than absolute |
| `SetUpdate(UpdateType, bool ignoreTimeScale)` | Chooses which loop drives the tween — `Normal` (`Update`), `Late` (`LateUpdate`), `Fixed` (`FixedUpdate`), `Manual` — and whether it ignores `Time.timeScale`. Leaving this at its default silently ties every tween to `Update()` with time-scale applied, which is wrong for e.g. a pause-menu fade that must play while gameplay time is frozen |

**`SetUpdate` is the setting most often left unexamined and most likely to
cause a real bug** — a UI element meant to animate during a paused game
(a pause menu itself, a "Game Over" fade) needs `ignoreTimeScale: true`;
a gameplay-synced tween usually doesn't. Decide this deliberately per
tween rather than accepting whatever the default happens to be.

## Chained callbacks

| Callback | Fires |
|---|---|
| `OnStart` | Once, when the tween begins playing |
| `OnPlay` | Every time playback starts/resumes (including after a pause) |
| `OnPause` | When transitioning from playing to paused |
| `OnUpdate` | Every frame while playing |
| `OnStepComplete` | Each time one loop cycle completes (relevant with `SetLoops`) |
| `OnWaypointChange` | Each time a path tween (see [path-tweens.md](path-tweens.md)) reaches a waypoint |
| `OnRewind` | When the tween rewinds back to its start |
| `OnComplete` | When the tween finishes entirely (after all loops) |
| `OnKill` | When the tween is destroyed — the place to null out a held reference to a non-autokilled tween, per [safe-mode-recycling-and-performance.md](safe-mode-recycling-and-performance.md) |

```csharp
transform.DOMoveX(4, 1).OnComplete(MyCallback);
```

Prefer a named method over an inline lambda when the callback references
state that could outlive a single call (a MonoBehaviour field, a captured
object) — per `coding-principles.md`'s Event handlers rule, so the
callback can actually be reasoned about and, if needed, unregistered by
replacing the tween rather than leaking a stale closure.

## Global settings (via `DOTween` statics, not per-tween)

| Setting | Effect |
|---|---|
| `DOTween.timeScale` | A time-scale multiplier applied to every DOTween tween globally, independent of `Time.timeScale` |
| `DOTween.showUnityEditorReport` | Editor-only diagnostic report of max capacity reached — useful while tuning capacity, but "will slightly slow down your performance while inside Unity Editor," so it's an Editor-only debugging aid, not something to leave on |
| Capacity (`DOTween.SetTweensCapacity(tweenersCapacity, sequencesCapacity)`) | Pre-allocates internal tween/sequence pool capacity — set this once at startup if the project routinely exceeds the default and DOTween is having to grow its internal arrays at runtime |
