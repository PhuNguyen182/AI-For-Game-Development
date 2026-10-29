# Getting started — install, Init, Modules, Free vs Pro

## Terms
Tweener = one value; Sequence = group of tweens; Tween = either. Prefixes: `DO` creates (`DOMove`), `Set` configures (`SetEase`), `On` attaches a callback (`OnComplete`).

## Install
- Asset Store "DOTween (HOTween v2)" (free) plus optional DOTween Pro. No official UPM distribution; community mirrors are not canonical, so confirm the layout in use.
- After importing or updating, run **Tools > Demigiant > DOTween Utility Panel > Setup DOTween...** once. It generates the per-module `DO*` extension methods. A missing shortcut is usually this step skipped, or a module enabled afterwards without re-running it.

## Modules
| Module | Shortcuts for |
|---|---|
| `DOTweenModuleUI` | uGUI |
| `DOTweenModulePhysics` | `Rigidbody` |
| `DOTweenModulePhysics2D` | `Rigidbody2D` |
| `DOTweenModuleAudio` | `AudioSource`, `AudioMixer` |
| `DOTweenModuleSprite` | `SpriteRenderer` |

A disabled module's shortcuts are a compile error.

## `DOTween.Init`
```csharp
DOTween.Init(bool recycleAllByDefault = false, bool useSafeMode = true,
             LogBehaviour logBehaviour = LogBehaviour.ErrorsOnly);
```
- `recycleAllByDefault`: pool every killed tween; see [safe-mode-and-async.md](safe-mode-and-async.md) before enabling project-wide.
- `useSafeMode`: slower but handles a target destroyed mid-tween.
- `logBehaviour`: `ErrorsOnly`, `Default` (errors and warnings), `Verbose`.

Call once, early (bootstrap), before any tween. The implicit first-tween auto-init uses these defaults.

## Free vs Pro
Pro only: visual Sequence editor, TextMeshPro shortcuts (`DOText`/`DOColor`/`DOFade`/`DOFontSize`, `DOTweenTMPAnimator`), path gizmo editor. Anything not listed is assumed free (not cross-checked against a Pro changelog).

## Tweenable types
`float`, `double`, `int`, `uint`, `long`, `ulong`, `Vector2/3/4`, `Quaternion`, `Rect`, `RectOffset`, `Color`, `string`, plus custom-plugin types.
