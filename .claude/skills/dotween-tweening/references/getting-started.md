# Getting Started — Install, Init, Modules, Free vs Pro

Source: [DOTween Documentation](https://dotween.demigiant.com/documentation.php), [Downloads](https://dotween.demigiant.com/download.php), [Get Started](https://dotween.demigiant.com/getstarted.php).
Covers: SKILL.md §4 — "Confirm the Modules panel matches what the feature actually touches before assuming a shortcut exists", "Set `DOTween.Init` deliberately, not on its defaults".

## Nomenclature

| Term | Meaning |
|---|---|
| **Tweener** | Controls the animation of a single value/property |
| **Sequence** | Controls a group of Tweeners and/or nested Sequences as one unit |
| **Tween** | The generic term covering both Tweener and Sequence |
| **Nested tween** | A Tweener or Sequence placed inside a Sequence |

Method name prefixes: **`DO`** creates a tween (`DOMove`, `DOFade`), **`Set`**
configures an existing tween (`SetEase`, `SetLoops`), **`On`** attaches a
callback (`OnComplete`, `OnKill`).

## Install and setup

Canonical distribution is the Unity Asset Store package "DOTween (HOTween
v2)" (free) plus, optionally, the separately purchased **DOTween Pro**
layered on top — see [root-links.md](root-links.md) for the UPM-mirror
caveat. After importing or updating the package, run **Tools > Demigiant >
DOTween Utility Panel > Setup DOTween...** once — this step generates/
refreshes the per-module wrapper scripts (the actual `DO*` shortcut
extension methods) from whichever Modules are enabled. Skipping it, or
enabling a module afterward without re-running it, is the usual reason a
shortcut method "doesn't exist" on an otherwise-correctly-imported project.

### Modules

The Utility Panel toggles which shortcut modules are compiled in:

| Module | Enables shortcuts for |
|---|---|
| `DOTweenModuleUI` | Unity UI (uGUI) components — see [ugui-and-tmp-shortcuts.md](ugui-and-tmp-shortcuts.md) |
| `DOTweenModulePhysics` | `Rigidbody` |
| `DOTweenModulePhysics2D` | `Rigidbody2D` |
| `DOTweenModuleAudio` | `AudioSource`, `AudioMixer` |
| `DOTweenModuleSprite` | `SpriteRenderer` |

Disabling a module removes its shortcuts entirely — calling one anyway is a
compile error, not a runtime one. Confirm the enabled module set matches
what the current feature actually needs (a UI-only feature doesn't need
Physics2D enabled, etc.) rather than assuming every module is on.

## `DOTween.Init`

```csharp
DOTween.Init(bool recycleAllByDefault = false, bool useSafeMode = true,
             LogBehaviour logBehaviour = LogBehaviour.ErrorsOnly);
```

| Parameter | Effect |
|---|---|
| `recycleAllByDefault` | When `true`, every new tween defaults to recyclable (pooled on kill instead of discarded) — see [safe-mode-recycling-and-performance.md](safe-mode-recycling-and-performance.md) before enabling this project-wide. |
| `useSafeMode` | When `true` (the default), DOTween runs slightly slower but automatically handles a target being destroyed mid-tween. Disabling it trades that safety for raw speed. |
| `logBehaviour` | `ErrorsOnly` (default), `Default` (errors + warnings), or `Verbose`. |

Call `DOTween.Init(...)` once, early (e.g. from a bootstrap/composition-root
script), before creating any tween — never rely on its implicit
first-tween auto-init with unexamined defaults for a feature that actually
depends on Safe Mode or recycling behavior.

## Free vs Pro

| | Free DOTween | DOTween Pro |
|---|---|---|
| Core tweening, Shortcuts, Sequences, Path tweens | Included | Included (same engine) |
| Visual Sequence editor (GUI timeline) | — | Included |
| TextMeshPro shortcuts (`DOText`/`DOColor`/`DOFade`/`DOFontSize`, `DOTweenTMPAnimator`) | — | Included |
| Path gizmo visual editor | — | Included |

A Tech Spec that calls for TMP tweening or a visually-authored Sequence
needs Pro; confirm which one the project has before promising either
surface, per [ugui-and-tmp-shortcuts.md](ugui-and-tmp-shortcuts.md).

## Supported value types

`float`, `double`, `int`, `uint`, `long`, `ulong`, `Vector2`, `Vector3`,
`Vector4`, `Quaternion`, `Rect`, `RectOffset`, `Color`, `string` — plus any
additional type a custom DOTween plugin adds. This is the type set both
`DOTween.To()` (generic) and every Shortcut ultimately tween, per
[tweeners-shortcuts-and-generic.md](tweeners-shortcuts-and-generic.md).
