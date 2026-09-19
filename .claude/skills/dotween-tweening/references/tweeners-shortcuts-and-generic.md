# Creating Tweeners — Generic Way, Shortcuts, Punch/Shake/Virtual

Source: [DOTween Documentation](https://dotween.demigiant.com/documentation.php).
Covers: SKILL.md §4 — "Reach for a Shortcut before a generic `DOTween.To()`", "Use a virtual tween only when there is genuinely no target object".

## A. Generic way — `DOTween.To()`

```csharp
DOTween.To(() => myFloat, x => myFloat = x, 52, 1);
// getter          setter              to  duration
```

Takes a getter lambda, a setter lambda, an end value, and a duration.
This is the escape hatch for a **private or static** property, or any
value no Shortcut already covers — it works for exactly the type set in
[getting-started.md](getting-started.md), and for nothing else without a
custom plugin. Every generic call allocates the getter/setter closures;
see [safe-mode-recycling-and-performance.md](safe-mode-recycling-and-performance.md)
for when that allocation actually matters.

## B. Shortcuts way

A Shortcut is an extension method on a known Unity component that already
knows its own target — no getter/setter needed:

```csharp
transform.DOMove(new Vector3(2, 3, 4), 1);
material.DOColor(Color.green, 1);
```

Reach for a Shortcut whenever one exists for the value being animated —
it is both less code and, unlike the generic `DOTween.To()` path, doesn't
require hand-writing a getter/setter pair. Fall back to the generic way
only once the target genuinely has no matching Shortcut (a private field,
a computed value, a type DOTween's Shortcuts don't cover).

### Non-UI component shortcuts (by Module)

| Component | Representative shortcuts |
|---|---|
| `Transform` | `DOMove`/`DOLocalMove`, `DORotate`/`DOLocalRotate`, `DOScale`, `DOPunchPosition`/`Rotation`/`Scale`, `DOShakePosition`/`Rotation`/`Scale`, `DOPath`/`DOLocalPath` (see [path-tweens.md](path-tweens.md)) |
| `Material` | `DOColor`, `DOFade`, property-specific float/color tweens by shader property name |
| `Camera` | Field of view, orthographic size, background color tweens |
| `Light` | Intensity, color tweens |
| `LineRenderer` / `TrailRenderer` | Color/width tweens |
| `Rigidbody` (`DOTweenModulePhysics`) | `DOMove`/`DORotate` variants that move via physics rather than `transform` directly, plus `DOPath` |
| `Rigidbody2D` (`DOTweenModulePhysics2D`) | Same idea in 2D, including a 2D `DOPath` |
| `SpriteRenderer` (`DOTweenModuleSprite`) | `DOColor`, `DOFade` |
| `AudioSource` / `AudioMixer` (`DOTweenModuleAudio`) | Volume, pitch, exposed mixer parameter tweens |

uGUI/UI Toolkit and TextMeshPro shortcuts are large enough to warrant their
own file — see [ugui-and-tmp-shortcuts.md](ugui-and-tmp-shortcuts.md),
which is also where this skill's uGUI cross-reference lives.

## C. Additional generic ways

| Method | Purpose |
|---|---|
| `DOTween.Punch(...)` | Punches a `Vector3` toward a direction and back, as if on elastic — the generic version of `DOPunchPosition`/etc. for a value with no Transform-style Shortcut |
| `DOTween.Shake(...)` | Shakes a `Vector3` with configurable strength/vibrato/randomness — generic counterpart to `DOShakePosition`/etc. |
| `DOTween.ToAlpha(...)` | Tweens specifically a `Color`'s alpha channel |
| `DOTween.ToArray(...)` | Tweens a `Vector3` through multiple end values in sequence, with easing applied between each segment |
| `DOTween.ToAxis(...)` | Tweens a single axis of a `Vector3` in isolation |
| **Virtual tweens** | `DOTween.To(x => someProperty = x, 0, 12, 0.5f)` — a tween with no real backing target object, just a callback receiving the interpolated value over time; the right shape for driving something that isn't a field at all (e.g. feeding a shader property block, or a value read by another system each frame) |

Prefer a genuine Shortcut/generic-with-real-target over a virtual tween
whenever an actual field or property exists to bind to — a virtual tween
is meant for values that live outside any object's serialized state, not
as a shortcut around writing a one-line setter.
