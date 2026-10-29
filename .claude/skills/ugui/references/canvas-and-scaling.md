# Canvas, Canvas Scaler, Canvas Group

Every UI element lives under a `Canvas` (the GameObject menu creates one). Children draw in Hierarchy order, first child first; reorder with `SetAsFirstSibling`/`SetAsLastSibling`/`SetSiblingIndex`.

## Render modes
| Mode | Behaviour | Fits |
|---|---|---|
| Screen Space – Overlay | On top of everything, auto-resizes, no camera | Standard HUD/menu |
| Screen Space – Camera | In front of a Camera; its perspective/FOV affects the UI | UI needing post-processing/perspective, or occluded by 3D |
| World Space | Ordinary scene object sized by its `RectTransform` | Diegetic UI, nameplates, VR (sizing in [profiling-performance-and-howtos.md](profiling-performance-and-howtos.md)) |

- Overlay canvases are unlit, so Normal/Tangent shader channels do nothing there. Enable them (and TexCoord1–3) only for lit/normal-mapped UI on a Camera/World Space canvas; each channel is per-vertex memory on every element.
- "Vertex Color Always in Gamma Color Space" matters only in a Linear project (keeps dark-tone precision by deferring sRGB conversion to the shader).

## CanvasScaler (on the root Canvas)
| Mode | Key properties | Use |
|---|---|---|
| Constant Pixel Size (default) | Scale Factor, Reference Pixels Per Unit | Does not adapt to resolution |
| Scale With Screen Size | Reference Resolution, Screen Match Mode, Match 0–1, Reference Pixels Per Unit | Standard for responsive PC + mobile |
| Constant Physical Size | Physical Unit, Fallback Screen DPI, Default Sprite DPI | Print-like or accessibility UI |

- **Match pitfall**: at 0 (Width), a screen much wider than the reference scales everything up. Use 0.5 for portrait + landscape or several aspect ratios.
- Screen Match Mode Expand grows the canvas (never crops); Shrink crops. Choose by whether edge loss or spare space is acceptable.
- Responsive = anchors (where) + `CanvasScaler` (how big); neither alone suffices.

## CanvasGroup (whole subtree at once)
| Property | Effect |
|---|---|
| `Alpha` | Multiplies child Graphic opacity; the way to fade a panel |
| `Interactable` | False: every `Selectable` below ignores input |
| `Blocks Raycasts` | False: pointer events pass through the group |
| `Ignore Parent Groups` | Nested group opts out of the parent's alpha/interactable/raycast state |

Prefer it over per-child `interactable` flags or `SetActive`. It forces a batch break for everything under it (UI Profiler example: a dropdown list), so budget that before adding one purely to fade a large subtree.
