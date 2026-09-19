# Unity UI (uGUI) and TextMeshPro Shortcuts

Source: [DOTween Documentation](https://dotween.demigiant.com/documentation.php).
Covers: SKILL.md §4 — "Tween uGUI through `DOTweenModuleUI` shortcuts, never a hand-rolled `Update()` lerp", "Confirm Pro before promising a TMP shortcut".
Cross-reference: this is this skill's primary interop surface with the
**`ugui`** skill — every component below is one `ugui` already documents
the non-tweening side of (Inspector fields, layout, event wiring); this
file is only the DOTween-authored *animation* of those same components.

## Requires `DOTweenModuleUI`

All shortcuts below need the `DOTweenModuleUI` module enabled (per
[getting-started.md](getting-started.md)'s Modules table) and, for a
project targeting Unity 2019.1+, work against the same `Canvas`/
`RectTransform` components [ugui](../../ugui/SKILL.md) documents in its own
[canvas-and-scaling.md](../../ugui/references/canvas-and-scaling.md),
[visual-components.md](../../ugui/references/visual-components.md), and
[interaction-components.md](../../ugui/references/interaction-components.md).

| Component | Shortcut | Effect | `ugui` reference |
|---|---|---|---|
| `CanvasGroup` | `DOFade(to, dur)` | Fades the group's `alpha` | [canvas-and-scaling.md](../../ugui/references/canvas-and-scaling.md) |
| `Graphic` (base) | `DOColor(to, dur)`, `DOFade(to, dur)`, `DOBlendableColor(to, dur)` | Color/alpha of any Graphic; the Blendable variant lets more than one color tween run on the same Graphic without one overwriting the other | [visual-components.md](../../ugui/references/visual-components.md) |
| `Image` | `DOColor`/`DOFade`/`DOBlendableColor` (inherited from `Graphic`), `DOFillAmount(to, dur)`, `DOGradientColor(gradient, dur)` | `DOFillAmount` is the direct DOTween equivalent of hand-animating an `Image.Filled` cooldown/progress indicator | [visual-components.md](../../ugui/references/visual-components.md) |
| `Outline` | `DOColor(to, dur)`, `DOFade(to, dur)` | Tweens the UI Effects Outline component's color/alpha | [visual-components.md](../../ugui/references/visual-components.md) |
| `LayoutElement` | `DOFlexibleSize`, `DOMinSize`, `DOPreferredSize` (`Vector2 to, float dur, bool snapping`) | Animates the width/height overrides a Layout Group reads — coordinate with [rect-transform-and-layout.md](../../ugui/references/rect-transform-and-layout.md)'s layout-controller-ownership rule so a tween and a Content Size Fitter don't fight over the same size | [rect-transform-and-layout.md](../../ugui/references/rect-transform-and-layout.md) |
| `RectTransform` | `DOAnchorPos`/`DOAnchorPos3D`, `DOAnchorMax`/`DOAnchorMin`, `DOSizeDelta`, `DOPunchAnchorPos`, `DOShakeAnchorPos`, `DOJumpAnchorPos` (returns a `Sequence`, not a `Tweener`) | The standard way to slide/punch/shake/jump a panel; `DOScale` also applies since `RectTransform` is a `Transform` | [rect-transform-and-layout.md](../../ugui/references/rect-transform-and-layout.md) |
| `ScrollRect` | `DOHorizontalNormalizedPos(to, dur)`, `DOVerticalNormalizedPos(to, dur)` | Programmatically scrolls to a position — e.g. "scroll to selected item" | [interaction-components.md](../../ugui/references/interaction-components.md) |
| `Slider` | `DOValue(to, dur, snapping = false)` | Animates the slider's value — note this fires the same `OnValueChanged` a player drag would, so a listener that reacts to player input specifically must distinguish the two if that matters | [interaction-components.md](../../ugui/references/interaction-components.md) |
| `Text` (legacy) | `DOText(to, dur, richTextEnabled = true, scrambleMode)`, `DOColor`, `DOFade`, `DOBlendableColor` | `DOText`'s `scrambleMode` drives the "decrypting text" reveal effect; legacy `Text` only — see TMP row below for `TMP_Text` | [visual-components.md](../../ugui/references/visual-components.md), [legacy-text-and-rich-text.md](../../ugui/references/legacy-text-and-rich-text.md) |
| UI Toolkit `VisualElement` | Listed alongside the uGUI shortcuts in DOTween's docs | Out of scope for this cross-reference — UI Toolkit is `ui-toolkit`'s surface, not `ugui`'s; confirm the screen is genuinely uGUI before reaching for these shortcuts at all, per `ugui`'s own system-choice guardrail | — |

## TextMeshPro shortcuts — **Pro only**

Confirm DOTween Pro (not just free DOTween) is actually installed before
promising any of these — see [getting-started.md](getting-started.md)'s
Free vs Pro table.

| Target | Shortcut | `ugui` reference |
|---|---|---|
| `TMP_Text` / `TextMeshProUGUI` | `DOText(to, dur, richTextEnabled, scrambleMode, scrambleChars)`, `DOColor`, `DOFade`, `DOFontSize(to, dur)` | [textmeshpro-core-and-rich-text.md](../../ugui/references/textmeshpro-core-and-rich-text.md) |

### `DOTweenTMPAnimator` — per-character animation

A wrapper object built around a `TMP_Text`, exposing per-character tweens
by character index — the DOTween-authored equivalent of what `ugui`'s
[textmeshpro-core-and-rich-text.md](../../ugui/references/textmeshpro-core-and-rich-text.md)
documents as TMP's own `<rotate>`/`<voffset>` rich text tags, but animated
over time rather than statically tagged:

| Method | Effect |
|---|---|
| `DOFadeChar(charIndex, to, dur)` | Fades one character's alpha |
| `DOColorChar(charIndex, to, dur)` | Colors one character |
| `DOOffsetChar(charIndex, to, dur)` | Offsets one character's position |
| `DORotateChar(charIndex, to, dur, mode)` | Rotates one character |
| `DOScaleChar(charIndex, to, dur)` | Scales one character |
| `DOPunchCharOffset`/`Rotation`/`Scale` | Punch variants, per character |
| `DOShakeCharOffset`/`Rotation`/`Scale` | Shake variants, per character |

`DOTweenTMPAnimator` must be told to refresh whenever the source string
changes (it caches per-character geometry) — re-initialize it after any
edit to the `TMP_Text`'s `text` property rather than assuming stale
character indices still line up.

## Practical guidance

- **Default to a Shortcut over hand-computing a Lerp inside `Update()`** —
  same reasoning as `ugui`'s own performance guardrail against unconditional
  per-frame updates, and `performance-and-algorithms.md`'s general
  hot-path rules: a `DOFade`/`DOColor`/`DOAnchorPos` call already handles
  timing, easing, and completion in one line.
- **Don't let a DOTween tween and a `ugui` Layout Group/Content Size
  Fitter fight over the same `RectTransform` property** — per
  [rect-transform-and-layout.md](../../ugui/references/rect-transform-and-layout.md)'s
  layout-controller-ownership rule, a Layout Group recalculating a size
  every frame while a `DOSizeDelta`/`DOFlexibleSize` tween also drives it
  produces a visibly fighting result; pick one owner for that property.
- **A `CanvasGroup.DOFade` and a `ugui` batch-break note interact** — per
  `ugui`'s [profiling-performance-and-howtos.md](../../ugui/references/profiling-performance-and-howtos.md),
  a `CanvasGroup` is a documented UI batch-break trigger regardless of
  whether its alpha changes via DOTween or any other mechanism; that cost
  exists independent of which tweening library drives the fade.
