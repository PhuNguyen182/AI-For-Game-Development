# Interaction Components

## Selectable (base of all below; pairs with a visual `Image` to render)
- **Interactable**: one flag disables input and sets the Disabled state. Prefer it or a parent `CanvasGroup` over gating each handler.
- **Transition**: None / Color Tint / Sprite Swap / Animation, over Normal/Highlighted/Pressed/Selected/Disabled.
- **Navigation**: None / Horizontal / Vertical / Automatic / Explicit; the Inspector Visualize button shows the graph. Use Explicit when Automatic picks the wrong neighbour.

### Animation transition
- Needs an `Animator` on the same GameObject. "Auto Generate Animation" creates the `Animator` and a controller; save the controller asset for it to take effect.
- **Incompatible with the legacy `Animation` component**; re-target any legacy clips onto an `Animator Controller`.
- Four clip slots: Normal (usually empty, since Inspector values already represent it), Highlighted, Pressed, Disabled. Each is a single keyframe that may change any number of properties. Edit in Window > Animation: Record, change Inspector values, exit Record.
- Use only when tint/sprite swap cannot express the feedback; it costs a controller asset per element.

## Components
- **Button**: `OnClick` `UnityEvent`.
- **Toggle / Toggle Group**: `Is On` + `OnValueChanged`. One `Toggle Group` assigned on each Toggle gives radio behaviour; do not hand-wire exclusivity.
- **Slider**: min/max, `OnValueChanged`. Read the value from the event/property, never the handle transform.
- **Scrollbar**: 0–1 value, `Size` = handle proportion; pair with `ScrollRect` and a mask.
- **Dropdown / InputField**: prefer `TMP_Dropdown` / `TMP_InputField`. InputField has separate content-changed and end-edit events, Content Type validation and a character limit. The new Input System does not deliver character entry into either field (`unity-input-system` limitation).

## ScrollRect
| Property | Effect |
|---|---|
| `Content` | RectTransform scrolled |
| `Movement Type` | Unrestricted / Elastic (bounces by `Elasticity`) / Clamped |
| `Inertia` / `Deceleration Rate` | 0 = instant stop, 1 = never stops |
| `Scroll Sensitivity` | Wheel/trackpad response |
| `Viewport` | Visible window; put `RectMask2D` on it ([visual-components.md](visual-components.md)) |
| `Horizontal`/`Vertical Scrollbar` | Optional, each with a Visibility mode (e.g. auto-hide) |

Fires `OnValueChanged` with the normalized position. Drive `Content` size with a Vertical/Grid Layout Group plus Content Size Fitter ([rect-transform-and-layout.md](rect-transform-and-layout.md)), not by hand.
