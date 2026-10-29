# Sequences, configuration, callbacks, control, paths

## Sequence
```csharp
Sequence seq = DOTween.Sequence();
seq.Append(transform.DOMoveX(45, 1));
seq.Insert(0, transform.DOScale(3f, seq.Duration()));
seq.PrependInterval(1);
```
| Method | Effect |
|---|---|
| `Append` / `Prepend` | After everything / before the current start |
| `Join` | Same start time as the last added tween |
| `Insert(at, tween)` | Explicit time offset |
| `AppendInterval` / `PrependInterval` | Pure time gap |
| `AppendCallback` / `InsertCallback` | Callback at a point or offset |

Nest reusable sub-sequences instead of flattening. `AppendCallback` suits fire-and-forget effects (sound, particle). Branching logic, awaiting inside the callback, or exception propagation: `async`/`await` around the Sequence ([safe-mode-and-async.md](safe-mode-and-async.md)); exceptions in a plain callback do not propagate like an `async` method's.

## `Set*` options (Tweener and Sequence)
| Method | Effect |
|---|---|
| `SetEase(Ease)` | Easing curve |
| `SetLoops(int, LoopType)` | `Restart`, `Yoyo`, `Incremental` (additive per loop) |
| `SetId` / `SetTarget` | Filter keys for static control |
| `SetAutoKill(bool)` | Default `true`; `false` keeps it for `Restart()`/`Play()` |
| `SetRecyclable(bool)` | Per-tween pooling, overrides the `Init` default |
| `SetRelative(bool)` | End value added to start |
| `SetUpdate(UpdateType, bool ignoreTimeScale)` | `Normal`, `Late`, `Fixed`, `Manual`; the default follows `Time.timeScale`, wrong for a pause-menu animation. Decide per tween |

## Callbacks
`OnStart` (once), `OnPlay` (every start/resume), `OnPause`, `OnUpdate` (per frame), `OnStepComplete` (each loop), `OnWaypointChange` (path waypoint reached), `OnRewind`, `OnComplete` (all loops done), `OnKill` (the place to null a held reference).

Use a named method, not a lambda, when the callback touches state outliving the call, so it does not leak a stale closure.

## Global settings
- `DOTween.timeScale`: global multiplier independent of `Time.timeScale`.
- `DOTween.SetTweensCapacity(tweeners, sequences)`: pre-size pools at startup if the project exceeds the default.
- `DOTween.showUnityEditorReport`: Editor-only max-capacity report that slows the Editor; switch on temporarily.

## Control
Instance: `Play`, `Pause`, `TogglePause`, `Rewind`, `Restart`, `Complete` (jump to end, fires completion), `Kill` (recycles if recyclable), `Flip`, `Goto(time)`, `SmoothRewind`, `PlayForward`/`PlayBackwards`.

Each has a static `DOTween.*All` form (`PlayAll`, `PauseAll`, `KillAll`, ...) filtered by Id or Target. The unfiltered form is for genuinely global moments (scene teardown, app-wide pause), never reflexive cleanup.

## `DOPath` / `DOLocalPath`
```csharp
transform.DOPath(waypoints, duration, pathType, pathMode, resolution, gizmoColor);
```
- `pathType`: `Linear` (patrol, mechanical), `CatmullRom` (smooth through every waypoint), `CubicBezier` (explicit control points, waypoints in groups of three: waypoint, in-control, out-control; the first waypoint is taken from the current position).
- `pathMode`: `Ignore`, `3D`, `Sidescroller2D`, `TopDown2D` (automatic facing).
- `resolution`: default 10; raise only for visible faceting, cost scales with length and waypoint count.
- `SetOptions(...)`: closed loop and related flags. `SetLookAt(...)`: facing independent of `pathMode`.
- `Rigidbody2D` has its own `DOPath` over `Vector2[]` (needs `DOTweenModulePhysics2D`).
- Use `OnWaypointChange` for per-waypoint logic instead of polling position.
