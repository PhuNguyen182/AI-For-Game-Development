# Interaction Components — Selectable, Button, Toggle, Slider, Scrollbar, Dropdown, InputField, ScrollRect

Source: [Interaction Components](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/UIInteractionComponents.html), [Selectable](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/script-Selectable.html), [Scroll Rect](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/script-ScrollRect.html).
Covers: SKILL.md §4 — "Compose from Selectable rather than hand-rolling pointer handling", "Configure ScrollRect's Movement Type deliberately".

## Selectable — the shared base

Every interaction component below is built on `Selectable`, which supplies:

- **Interactable** — a single flag that disables input handling and moves
  the visual state to Disabled; prefer this (or a parent `CanvasGroup`,
  per [canvas-and-scaling.md](canvas-and-scaling.md)) over manually gating
  each event handler.
- **Transition** (None / Color Tint / Sprite Swap / Animation) — the visual
  feedback strategy for Normal/Highlighted/Pressed/Disabled (and Selected)
  states. See [animation-and-transitions.md](animation-and-transitions.md)
  for the Animation mode specifically.
- **Navigation** (None / Horizontal / Vertical / Automatic / Explicit) —
  keyboard/controller focus movement between selectables, with a Visualize
  button in the Inspector to see the computed navigation graph. Explicit
  mode is the escape hatch when Automatic's spatial guess picks the wrong
  neighbor.

Selectable components are invisible on their own — each pairs with a
Visual Component (usually an `Image`) to actually render.

## Button

An `OnClick` `UnityEvent` fired on a completed click. The simplest
interaction component — no additional state beyond `Selectable`'s own.

## Toggle / Toggle Group

`Toggle` carries an `Is On` boolean and an `OnValueChanged` `UnityEvent`,
with a checkmark Graphic shown/hidden by its state. `Toggle Group` makes a
set of Toggles mutually exclusive (radio-button behavior) — add the group
component once and assign it on each Toggle, rather than wiring exclusivity
by hand in each `OnValueChanged` handler.

## Slider

A draggable value between a min and max, horizontal or vertical, firing
`OnValueChanged`. Read the current value from the event/property; never
recompute it from the handle's transform.

## Scrollbar

A 0–1 value with a `Size` property controlling handle-to-track proportion.
Almost always paired with a `ScrollRect` and a `Mask`/`RectMask2D` rather
than used standalone.

## Dropdown

Presents a list of text/image options, firing `OnValueChanged` on
selection. Prefer `TMP_Dropdown` (TextMeshPro's variant, see
[textmeshpro-core-and-rich-text.md](textmeshpro-core-and-rich-text.md)) for
new work over the legacy `Dropdown`.

## Input Field

Editable text entry with separate `UnityEvent`s for "content changed" and
"editing ended," a Content Type (for validation — integer, decimal,
alphanumeric, password, etc.), and a character limit. Prefer
`TMP_InputField` for new work, same reasoning as Dropdown above. Recall
from `unity-input-system`'s documented limitation: the new Input System
package does not itself deliver character text entry into either
`InputField` or `TMP_InputField` — that path still runs through the legacy
input backend regardless of which Input Module drives navigation/clicks.

## Scroll Rect

Displays a large **Content** rect through a smaller viewport:

| Property | Effect |
|---|---|
| `Content` | The RectTransform being scrolled (e.g. a large image or a Layout-Group-driven item list) |
| `Horizontal` / `Vertical` | Enable scrolling per axis |
| `Movement Type` | **Unrestricted** (scrolls freely, no bounds), **Elastic** (bounces back past content edges by `Elasticity`), **Clamped** (hard-stops at content edges) |
| `Inertia` / `Deceleration Rate` | Whether content keeps moving after release, and how fast it decelerates (`0` = instant stop, `1` = never stops) |
| `Scroll Sensitivity` | Responsiveness to scroll-wheel/trackpad input |
| `Viewport` | The parent RectTransform that defines the visible window — pair with `RectMask2D` on the same object, per [visual-components.md](visual-components.md) |
| `Horizontal`/`Vertical Scrollbar` | Optional `Scrollbar` references, each with its own Visibility mode (e.g. auto-hide when content fits) |

Fires `OnValueChanged` with the current normalized scroll position. For a
long or dynamically-sized item list, pair `Content` with a `Vertical`/`Grid`
Layout Group plus a `Content Size Fitter` (per
[rect-transform-and-layout.md](rect-transform-and-layout.md)) rather than
sizing `Content` by hand — see also
[HOWTO-UIFitContentSize](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/HOWTO-UIFitContentSize.html)
(not independently fetched for this skill; confirm details on the live
page before citing them precisely).
