# uGUI Integration

Pages: `/docs/ui`, `/docs/adapters`, `/docs/interactable`. Since v4.0 the same layouts drive uGUI `RectTransform`s. Anchors, Canvas Scaler and EventSystem setup stay with `ugui`.

## Flexalon or Layout Groups
| Situation | Choose |
|---|---|
| Plain 2D screen already on Layout Groups | uGUI (`ugui`); converting buys nothing |
| Third axis, world-space depth, 3D rotation | Flexalon |
| One arrangement logic for world objects and UI | Flexalon |
| Drag between panels, hand reorder, animated moves, data-generated content | Flexalon |
| Long scrolling list | Neither: `osa-optimized-scrollview-adapter` |

Edition: the free UI package has only two layouts (unnamed on the site); confirm before designing a screen around Curve, Shape or Random.

## Mapping (replace, never combine)
| uGUI | Flexalon |
|---|---|
| Layout Element | `FlexalonObject`, `Fixed` or `Fill` |
| Vertical/Horizontal Layout Group | `FlexalonFlexibleLayout` |
| Grid Layout Group | `FlexalonGridLayout` |
| Content Size Fitter | `FlexalonObject` size `Layout` |
| Aspect Ratio Fitter | recipe below |

## Responsive screen
1. Create the Canvas normally (`GameObject > UI > Canvas`).
2. Put Flexalon layouts under it; the root canvas is never resized.
3. Layout `FlexalonObject` width and height `Fill` to track the screen.
4. `Wrap` on a Flexible Layout to reflow when narrow (inert if the direction axis is `Layout`).
5. Sample: `Flexalon/Samples/Scenes/UI`.

## Aspect ratio
- `Image`: Image Type Simple + Preserve Aspect, and a `FlexalonObject` with exactly one axis `Component`, the other `Fixed` or `Fill`.
- Text: one axis `Component`, the other `Fixed` or `Fill`.
- Anything else: `FlexalonAspectRatioAdapter` ([adapters.md](adapters.md)).

## Behaviour to expect
- `TMP_Text` measurement resizes its rect: do not also drive it from a script or Content Size Fitter.
- A `Fill`-width text may re-wrap and change height, forcing re-measure.
- Custom animators must implement `UpdateRectSize` ([animators.md](animators.md)).
- UI interaction needs EventSystem, `GraphicRaycaster` and a raycast-target `Graphic` ([interactions-and-xr.md](interactions-and-xr.md)).
- A layout that re-runs every frame dirties its Canvas geometry: keep static and frequently updating UI on separate Canvases.
