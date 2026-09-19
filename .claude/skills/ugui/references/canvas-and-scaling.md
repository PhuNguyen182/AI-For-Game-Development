# Canvas, Canvas Scaler, Canvas Group

Source: [Canvas](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/UICanvas.html), [Canvas Scaler](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/script-CanvasScaler.html), [Canvas Group](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/script-CanvasGroup.html).
Covers: SKILL.md §4 — "Pick the Canvas render mode from where the UI lives, not by default", "Drive multi-resolution scaling through `CanvasScaler`, never a fixed pixel layout".

## Canvas — the root every uGUI element needs

Every UI element is a GameObject that must live under a `Canvas`. Creating a
UI element through the GameObject menu auto-creates one if none exists.
Canvas content is drawn in the same order it appears in the Hierarchy — the
first child draws first, later siblings draw on top. Reorder with
`SetAsFirstSibling`/`SetAsLastSibling`/`SetSiblingIndex`, not by hand-editing
draw order elsewhere.

### Render Modes

| Mode | Behavior | Fits |
|---|---|---|
| **Screen Space – Overlay** | Renders on top of everything, auto-resizes to the screen; no camera reference needed | Standard HUD/menu — the default choice |
| **Screen Space – Camera** | Placed a set distance in front of a specified Camera; that camera's perspective/FOV affects UI appearance; auto-scales with screen size or camera frustum changes | A HUD that must be affected by camera post-processing/perspective, or must render behind 3D geometry that occludes it |
| **World Space** | Behaves like any other scene object — sized via its own `RectTransform`, positioned/rotated freely, rendered by any camera pointed at it | Diegetic UI: a nameplate, an in-world screen, VR panels — see [profiling-performance-and-howtos.md](profiling-performance-and-howtos.md) for the sizing walkthrough |

Screen Space – Overlay canvases are unaffected by scene lighting, so the
Normal/Tangent additional shader channels have no visible effect there —
only add them (along with TexCoord1–3) when a Camera/World Space canvas
genuinely needs lit or normal-mapped UI shaders; each additional channel
is per-vertex memory cost paid by every element on that canvas.

In a linear color space project, "Vertex Color Always in Gamma Color Space"
defers sRGB conversion to the shader instead of the vertex stream — it
preserves precision in darker tones/gradients but only matters under
Linear color space.

### Canvas Scaler — three UI Scale Modes

Add `CanvasScaler` to the root `Canvas` to make a layout resolution-independent.

| Mode | Key properties | Behavior |
|---|---|---|
| **Constant Pixel Size** (default) | Scale Factor, Reference Pixels Per Unit | UI elements keep the same pixel size regardless of screen size — simplest, but does not adapt to different device resolutions |
| **Scale With Screen Size** | Reference Resolution, Screen Match Mode (Match Width Or Height / Expand / Shrink), Match (0–1 slider), Reference Pixels Per Unit | Scales the whole canvas relative to a Reference Resolution — the standard choice for a responsive PC + mobile HUD, per `coding-principles.md`'s responsive-UI expectation |
| **Constant Physical Size** | Physical Unit (mm/points/picas), Fallback Screen DPI, Default Sprite DPI, Reference Pixels Per Unit | UI elements keep the same real-world size across devices/resolutions — rare outside print-like or accessibility-driven UI |

**Match slider pitfall**: at `Match = 0` (Width), a landscape resolution
notably wider than the reference resolution scales the whole canvas up
disproportionately, oversizing every element. `Match = 0.5` (Width and
Height balanced) is the documented fix for a UI that must support both
portrait and landscape or several aspect ratios — never leave Match at its
default 0 for a genuinely multi-aspect-ratio target without checking this.

**Screen Match Mode Expand/Shrink**: Expand grows the canvas area (never
crops content) on a mismatched aspect ratio; Shrink crops it instead —
pick per whether losing content at the edges or leaving unused space is
the acceptable trade-off for that screen.

### Canvas Group

`CanvasGroup` controls a whole subtree at once without touching each
child's own components:

| Property | Effect |
|---|---|
| `Alpha` | Multiplies the rendered opacity of every child Graphic — the standard way to fade a whole panel in/out |
| `Interactable` | When false, every `Selectable` under the group stops accepting input, without disabling each one individually |
| `Blocks Raycasts` | When false, pointer events pass through the whole group to whatever is behind it |
| `Ignore Parent Groups` | Lets a nested CanvasGroup opt out of inheriting a parent CanvasGroup's alpha/interactable/raycast state |

Use `CanvasGroup` rather than toggling many individual `Selectable.interactable`
flags or a `GameObject.SetActive` per child when the intent is "disable/fade
this whole panel" — it is also the standard vehicle for a fade-in/fade-out
tween (see `litmotion-tweening`'s `BindToAlpha` on `CanvasGroup`).

Note also from the UI Profiler ([profiling-performance-and-howtos.md](profiling-performance-and-howtos.md)):
a `CanvasGroup` forces a batch break for everything under it — a dropdown
list is the documented example. Budget that when a `CanvasGroup` is added
purely for a fade effect on a large subtree.
