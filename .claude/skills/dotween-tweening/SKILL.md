---
name: dotween-tweening
description: "DOTween (Demigiant): DOTween.To, DOMove/DOFade shortcuts, Sequence Append/Join/Insert, SetEase/SetLoops/SetUpdate, OnKill, KillAll, Safe Mode, SetRecyclable, DOPath, DOTweenTMPAnimator. Use for code tweens in a module on DOTween."
user-invocable: false
---

# DOTween

Not for: LitMotion (`litmotion-tweening`), async orchestration beyond awaiting a tween (`unitask-async-programming`), uGUI setup and wiring (`ugui`), reactive streams (`r3-reactive-extensions`), shader/particle VFX (`vfx-particle-authoring`), force/collision movement with no tween (`unity-3d-physics`, `unity-2d-physics`).
Docs: `https://dotween.demigiant.com/documentation.php` (single page, no version pin; Asset Store distribution, DOTween Pro is a separate paid layer) — check an exact default against the installed version's source.

| Reference | Read when |
|---|---|
| [getting-started.md](references/getting-started.md) | Adding DOTween, a shortcut "does not exist", `DOTween.Init` choices, Free vs Pro |
| [shortcuts.md](references/shortcuts.md) | Creating a tween: shortcut vs `DOTween.To`, uGUI/TMP shortcuts, punch/shake/virtual tweens |
| [sequences-config-control.md](references/sequences-config-control.md) | Sequences, `Set*` options, callbacks, pausing/killing, `DOPath` |
| [safe-mode-and-async.md](references/safe-mode-and-async.md) | Safe Mode, recycling, capacity, awaiting a tween |
| [coexistence-and-migration.md](references/coexistence-and-migration.md) | No established tween engine for the touched module, or a DOTween/LitMotion port |

## Steps
1. **Confirm DOTween governs this module** — existing module convention, then project-wide choice, then `Needs-decision`, `Next: technical-architect`. Never default to it because this skill was invoked ([coexistence-and-migration.md](references/coexistence-and-migration.md)).
2. **Confirm Modules and tier cover the feature** — uGUI needs `DOTweenModuleUI`; TMP shortcuts and the visual Sequence editor need Pro ([getting-started.md](references/getting-started.md)).
3. **Prefer a shortcut over `DOTween.To()`**; generic only for a private/static/uncovered value ([shortcuts.md](references/shortcuts.md)).
4. **For a uGUI component, pick one owner per `RectTransform` property** — a `DOSizeDelta`/`DOFlexibleSize` tween against a Layout Group or Content Size Fitter fights silently ([shortcuts.md](references/shortcuts.md)).
5. **Compose with a `Sequence`**; use `async`/`await` instead of `AppendCallback` once mid-animation logic branches, awaits or must propagate exceptions ([sequences-config-control.md](references/sequences-config-control.md)).
6. **Set `SetUpdate(..., ignoreTimeScale: true)` for anything that animates while paused** (pause menu, Game Over fade); the default follows `Time.timeScale`.
7. **Tag with `SetId`/`SetTarget` and filter static control** — an unfiltered `KillAll()` hits tweens the caller does not own.
8. **Leave Safe Mode on**, and null a held reference to a recyclable tween in its `OnKill` ([safe-mode-and-async.md](references/safe-mode-and-async.md)).
9. **Await via UniTask `UNITASK_DOTWEEN_SUPPORT` when `unitask-async-programming` governs the project**, with `GetCancellationTokenOnDestroy()`; `AsyncWaitForCompletion()` only without UniTask and after the WebGL caveat check.
10. **Use `DOPath` only for real multi-waypoint motion**, choosing `PathType`/`resolution` deliberately.
11. **Claim an allocation advantage for either engine only after a Profiler measurement** (`unity-profiler-diagnostics`).
12. **Engine convention, async ecosystem or WebGL target unstated → `Blocked` naming it.**

## Never
- Put DOTween in a Core assembly — it depends on `UnityEngine`; drive Core state from Client code.

## Output
```
## DOTween Work — <animation>
- Engine: DOTween confirmed — <convention | decided | asked>
- Creation: <shortcut or DOTween.To + reason>, modules, Free/Pro
- Composition / configuration: <Sequence shape; Ease, Loops, Id/Target, AutoKill, Recyclable, Update>
- Completion: <UniTask await | AsyncWaitForCompletion | WaitFor*>
- Safe Mode / recycling: <on | exception>; <OnKill nulling if recyclable>
- Verified: <evidence, or "not run">
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Just use DOTween for the new inventory grid, it's simpler" → the module has no tween code and no stated convention; asked which engine governs it instead of defaulting.
