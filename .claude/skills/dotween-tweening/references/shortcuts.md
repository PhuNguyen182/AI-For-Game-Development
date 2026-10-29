# Creating tweens — generic, shortcuts, uGUI/TMP

## Generic
```csharp
DOTween.To(() => myFloat, x => myFloat = x, 52, 1);   // getter, setter, end, duration
```
`DOTween.To` works only for the types listed in getting-started.md (Tweenable types) plus custom plugins.
For a private/static value or a type no shortcut covers; allocates the closures.

Variants: `DOTween.Punch`/`Shake` (Vector3 without a Transform), `ToAlpha` (Color alpha), `ToArray` (Vector3 through several end values), `ToAxis` (one axis).
Virtual tween: `DOTween.To(x => prop = x, 0, 12, 0.5f)` has no backing target, only a callback with the interpolated value. Use only when no real field or property exists to bind to.

## Shortcuts
Extension methods that know their target: `transform.DOMove(v, 1)`, `material.DOColor(c, 1)`.

| Component | Shortcuts |
|---|---|
| `Transform` | `DOMove`/`DOLocalMove`, `DORotate`/`DOLocalRotate`, `DOScale`, `DOPunch*`, `DOShake*`, `DOPath`/`DOLocalPath` |
| `Material` | `DOColor`, `DOFade`, float/color by shader property name |
| `Camera`, `Light` | FOV, ortho size, background colour; intensity, colour |
| `LineRenderer`, `TrailRenderer` | colour, width |
| `Rigidbody`/`Rigidbody2D` | `DOMove`/`DORotate` via physics, `DOPath` (Physics modules) |
| `SpriteRenderer` | `DOColor`, `DOFade` |
| `AudioSource`/`AudioMixer` | volume, pitch, exposed parameter |

Unverified: signatures beyond Transform/Material were not individually checked; confirm against the live docs.

## uGUI (needs `DOTweenModuleUI`; component setup is `ugui`'s)
| Component | Shortcuts / note |
|---|---|
| `CanvasGroup` | `DOFade` |
| `Graphic`, `Image` | `DOColor`, `DOFade`, `DOBlendableColor` (lets two colour tweens coexist); `Image`: `DOFillAmount`, `DOGradientColor` |
| `Outline` | `DOColor`, `DOFade` |
| `LayoutElement` | `DOFlexibleSize`, `DOMinSize`, `DOPreferredSize` — conflicts with Layout Groups |
| `RectTransform` | `DOAnchorPos(3D)`, `DOAnchorMax/Min`, `DOSizeDelta`, `DOPunchAnchorPos`, `DOShakeAnchorPos`, `DOJumpAnchorPos` (returns a `Sequence`); `DOScale` also applies |
| `ScrollRect` | `DOHorizontalNormalizedPos`, `DOVerticalNormalizedPos` |
| `Slider` | `DOValue` — fires `OnValueChanged` like a player drag |
| legacy `Text` | `DOText(to, dur, richTextEnabled, scrambleMode)`, `DOColor`, `DOFade` |

A Layout Group or Content Size Fitter recalculating a size while `DOSizeDelta`/`DOFlexibleSize` drives it produces a visible fight. `CanvasGroup` breaks UI batching whichever library drives the fade. UI Toolkit `VisualElement` shortcuts exist but belong to `ui-toolkit`.

## TextMeshPro (Pro only)
`TMP_Text`: `DOText(to, dur, richTextEnabled, scrambleMode, scrambleChars)`, `DOColor`, `DOFade`, `DOFontSize`.

`DOTweenTMPAnimator` wraps a `TMP_Text` for per-character tweens by index: `DOFadeChar`, `DOColorChar`, `DOOffsetChar`, `DORotateChar`, `DOScaleChar`, `DOPunchChar*`, `DOShakeChar*`. It caches character geometry: re-initialise it after any change to `text`.
