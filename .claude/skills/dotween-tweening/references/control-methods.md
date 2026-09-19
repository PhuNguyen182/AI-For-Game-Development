# Control Methods — Instance and Filtered Static Control

Source: [DOTween Documentation](https://dotween.demigiant.com/documentation.php).
Covers: SKILL.md §4 — "Filter static control by Id/Target deliberately, never `DOTween.KillAll()` as a reflex".

## Instance methods (Tweener and Sequence alike)

| Method | Effect |
|---|---|
| `Play()` | Resume from paused, or start if stopped |
| `Pause()` | Pause without losing progress |
| `TogglePause()` | Flips between playing and paused |
| `Rewind()` | Jumps back to the start, still respecting callbacks along the way |
| `Restart()` | Restarts from the beginning as if newly created |
| `Complete()` | Jumps immediately to the end and fires completion |
| `Kill()` | Destroys the tween (or recycles it, if recyclable — see [safe-mode-recycling-and-performance.md](safe-mode-recycling-and-performance.md)) |
| `Flip()` | Reverses the play direction |
| `Goto(time)` | Jumps to an explicit time position |
| `SmoothRewind()` | Animates back to the start smoothly rather than snapping |
| `PlayForward()` / `PlayBackwards()` | Explicitly plays in a given direction rather than toggling |

## Static, filtered control

Every instance method above has a `DOTween.*All` static equivalent
(`PlayAll`, `PauseAll`, `RestartAll`, `RewindAll`, `CompleteAll`,
`KillAll`, and so on) that operates on a set of tweens filtered by:

- **Id** (via `SetId(object)`) — the usual choice for "all tweens belonging
  to this logical group," e.g. every tween tagged with a specific UI
  panel's id.
- **Target** (via `SetTarget(object)`, or a Shortcut's implicit target) —
  "every tween currently animating this specific object."
- **No filter (all tweens globally)** — reserve this for something
  genuinely global (a scene teardown, an app-wide pause), never as a
  reflexive way to "clean up" without knowing what's actually running;
  killing every tween in the project on a narrow trigger is the tween
  equivalent of a top-level exception handler that swallows everything.

Prefer tagging tweens with `SetId`/`SetTarget` and filtering deliberately
over `DOTween.KillAll()`/`DOTween.CompleteAll()` with no filter — the
unfiltered form affects tweens the calling code has no knowledge of and no
business touching.
