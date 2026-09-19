# uGUI Integration — Flexalon UI on a Unity Canvas

Sources: [Flexalon UI](https://www.flexalon.com/docs/ui), [Adapters](https://www.flexalon.com/docs/adapters), [Interactable](https://www.flexalon.com/docs/interactable), [flexalon.com](https://www.flexalon.com/).
Covers: SKILL.md §4 — **"Confirm Flexalon is the right layout system for this surface, and which edition is installed, before adding any component"**.

Since v4.0 the same layout components drive uGUI `RectTransform`s. This file
holds the decision of whether a Canvas should be laid out by Flexalon at all,
and the mapping to use if it is. Everything about uGUI itself — anchors,
Canvas Scaler, EventSystem configuration, component construction — stays with
the `ugui` skill; this file only covers the seam.

## Deciding: Flexalon or uGUI layout groups

| Situation | Choose | Why | Source |
|---|---|---|---|
| The screen is plain 2D UI already built on Layout Groups | uGUI (`ugui`) | Converting a working screen buys nothing and risks the double-driver conflict below | synthesized |
| The layout needs a third axis, world-space depth, or 3D rotation | Flexalon | uGUI layout groups are 2D only | [Flexalon UI](https://www.flexalon.com/docs/ui) |
| The same arrangement logic must serve both world objects and UI | Flexalon | One component set, one mental model, for both | [Flexalon UI](https://www.flexalon.com/docs/ui) |
| Items must be dragged between panels, or reordered by hand | Flexalon | `FlexalonInteractable` + `FlexalonDragTarget` — see [interactions-and-xr.md](interactions-and-xr.md) | [Flexalon UI](https://www.flexalon.com/docs/ui) |
| Elements must animate between layout positions | Flexalon | Lerp/Curve animators operate on layout results — see [animators.md](animators.md) | [Flexalon UI](https://www.flexalon.com/docs/ui) |
| Panel content is generated from data | Flexalon | `FlexalonCloner` + `DataSource` — see [cloner-and-data-binding.md](cloner-and-data-binding.md) | [Flexalon UI](https://www.flexalon.com/docs/ui) |
| A long, scrolling list over many rows | Neither — `osa-optimized-scrollview-adapter` | Flexalon instantiates one object per item with no recycling | synthesized |

The project's licensed edition constrains this: the product site describes a
**free UI package covering "Flexalon's two most popular layouts"**, with the
full layout set in the paid asset. Confirm what is installed before designing
a screen around Curve, Shape, or Random layouts, per [root-links.md](root-links.md).

## Mapping from uGUI

| uGUI component | Flexalon equivalent | Source |
|---|---|---|
| Layout Element | `FlexalonObject` with size `Fixed` or `Fill` | [Flexalon UI](https://www.flexalon.com/docs/ui) |
| Vertical / Horizontal Layout Group | `FlexalonFlexibleLayout` | [Flexalon UI](https://www.flexalon.com/docs/ui) |
| Grid Layout Group | `FlexalonGridLayout` | [Flexalon UI](https://www.flexalon.com/docs/ui) |
| Content Size Fitter | `FlexalonObject` with size `Layout` | [Flexalon UI](https://www.flexalon.com/docs/ui) |
| Aspect Ratio Fitter | The aspect-ratio recipe below | [Flexalon UI](https://www.flexalon.com/docs/ui) |

**Critical caveat**: these are replacements, not companions. Leaving a Layout
Group, Content Size Fitter, or Aspect Ratio Fitter on an object a Flexalon
layout also drives means two systems writing the same `RectTransform` values,
and which one wins depends on execution order — a silent,
frame-order-dependent conflict rather than an error. Remove the uGUI
component when adopting the Flexalon one.

## Building a responsive screen

| Step | What to do | Source |
|---|---|---|
| 1 | Create the Canvas the normal Unity way (`GameObject > UI > Canvas`) | [Flexalon UI](https://www.flexalon.com/docs/ui) |
| 2 | Add Flexalon layout objects **under** the Canvas — the root canvas itself is never resized by Flexalon | [Flexalon UI](https://www.flexalon.com/docs/ui), [Adapters](https://www.flexalon.com/docs/adapters) |
| 3 | Set the layout's `FlexalonObject` width and height to `SizeType.Fill` so it tracks the screen | [Flexalon UI](https://www.flexalon.com/docs/ui) |
| 4 | Check `Wrap` on a Flexible Layout so content reflows as the screen narrows | [Flexalon UI](https://www.flexalon.com/docs/ui) |
| 5 | Study `Flexalon/Samples/Scenes/UI` for the other layouts, animators, interactables, and scroll views | [Flexalon UI](https://www.flexalon.com/docs/ui) |

Steps 3 and 4 are one decision: wrapping is inert while the direction axis is
`SizeType.Layout`, because a shrink-wrapping layout never runs out of space,
per [flexible-and-grid-layouts.md](flexible-and-grid-layouts.md).

## Preserving aspect ratio

| Content | Recipe | Source |
|---|---|---|
| `Image` | Set Image Type to **Simple** and check **Preserve Aspect**; add a `FlexalonObject` with **one** axis `Component` and the other `Fixed` or `Fill` | [Flexalon UI](https://www.flexalon.com/docs/ui) |
| Text | Add a `FlexalonObject` with one axis `Component` and the other `Fixed` or `Fill` | [Flexalon UI](https://www.flexalon.com/docs/ui) |
| Anything else | `FlexalonAspectRatioAdapter` with an explicit ratio — see [adapters.md](adapters.md) | [Class FlexalonAspectRatioAdapter](https://www.flexalon.com/docs/api/Flexalon.FlexalonAspectRatioAdapter.html) |

The one-axis rule is the `Image` adapter's actual condition: it derives the
size from the sprite's aspect ratio **only when exactly one axis** is
`Component`. Two `Component` axes and the image sizes from the sprite in both
directions instead of preserving a ratio against an allocated width.

## uGUI-specific behaviour to expect

| Behaviour | Consequence | Source |
|---|---|---|
| `TMP_Text` measurement resizes the `RectTransform` to fit the text | Do not also drive that rect from another script or a Content Size Fitter | [Adapters](https://www.flexalon.com/docs/adapters) |
| A `Fill`-width text object may re-wrap and change its own height | The parent layout re-measures — this is the documented reason `Measure` runs more than once per update, per [core-concepts-and-pipeline.md](core-concepts-and-pipeline.md) | [Custom Layout](https://www.flexalon.com/docs/customLayout) |
| Root canvas sizes are never modified | Put the first Flexalon layout on a child of the Canvas, never on the Canvas object itself | [Adapters](https://www.flexalon.com/docs/adapters) |
| Non-root and World Space canvases are adapted as `RectTransform`s | A nested canvas participates in layout normally | [Adapters](https://www.flexalon.com/docs/adapters) |
| Rect sizing flows through `TransformUpdater.UpdateRectSize` | A custom animator that ignores that method leaves UI elements unsized while animating — see [animators.md](animators.md) | [Interface TransformUpdater](https://www.flexalon.com/docs/api/Flexalon.TransformUpdater.html) |
| UI interaction needs an EventSystem, a GraphicsRaycaster, and a raycast-target `Graphic` | Missing any of the three fails silently — see [interactions-and-xr.md](interactions-and-xr.md) | [Interactable](https://www.flexalon.com/docs/interactable) |

Splitting static and frequently-updating UI across separate `Canvas`
components still applies here, per `performance-and-algorithms.md`'s
Rendering & draw calls section — a Flexalon layout that re-runs every frame
also dirties the canvas geometry it sits on.
