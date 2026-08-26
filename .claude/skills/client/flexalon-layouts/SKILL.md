---
name: flexalon-layouts
description: >
  Flexalon (Virtual Maker) — the box-model layout asset that arranges Unity
  GameObjects and uGUI in 3D: the `Flexalon` singleton, `FlexalonObject`
  (`SizeType` Component/Fixed/Fill/Layout, `MinMaxSizeType`, margins,
  padding, offset, `SkipLayout`), `FlexalonFlexibleLayout`,
  `FlexalonGridLayout` with `FlexalonGridCell`, `FlexalonCircleLayout`,
  `FlexalonCurveLayout`, `FlexalonShapeLayout`, `FlexalonAlignLayout`,
  `FlexalonRandomLayout`, `FlexalonConstraint`, `FlexalonRandomModifier`,
  `FlexalonCloner` with `DataSource`/`DataBinding`, `FlexalonInteractable`
  and `FlexalonDragTarget`, Curve/Lerp/RigidBody animators, `Adapter`,
  `TransformUpdater`, `FlexalonNode`, and the Measure→Arrange→Constrain
  pipeline. Use when arranging objects or UI through Flexalon components.
  Not for: uGUI Layout Group and RectTransform authoring (`ugui`), UI
  Toolkit USS flex layout (`ui-toolkit`), tweening engines
  (`dotween-tweening`, `litmotion-tweening`), virtualized scroll lists
  (`osa-optimized-scrollview-adapter`), inspector attributes
  (`odin-inspector`).
---

# Flexalon — 3D and UI Layout for Unity

## Bundled resources

### References
Read-only context, loaded on demand so this file stays short.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Doc roots, edition/version anchor, install steps, topic→file map, disclosed gaps | Starting any task here, or confirming which edition/version is installed |
| [core-concepts-and-pipeline.md](references/core-concepts-and-pipeline.md) | `Flexalon` singleton, box model, the five pipeline steps, `FlexalonNode`, `FlexalonResult`, dirty/update model | Deciding when layout runs, or layout doesn't recompute when expected |
| [flexalon-object-sizing.md](references/flexalon-object-sizing.md) | `SizeType`, `MinMaxSizeType`, shrinking, margins/padding/offset/rotation/scale, `SkipLayout`, `UseDefaultAdapter` | Setting any object's size, or an object sizes differently than intended |
| [flexible-and-grid-layouts.md](references/flexible-and-grid-layouts.md) | `FlexalonFlexibleLayout` (direction, wrap, gap, align), `FlexalonGridLayout` (cells, rows/columns/layers), `FlexalonGridCell` | Building a linear, wrapping, or evenly-spaced arrangement |
| [radial-curve-and-shape-layouts.md](references/radial-curve-and-shape-layouts.md) | Circle/Spiral, Curve, Shape, Align, Random layouts and their enums | The arrangement is radial, along a path, a formation, or randomized |
| [constraints-and-modifiers.md](references/constraints-and-modifiers.md) | `FlexalonConstraint` align/pivot/target, `FlexalonModifier`, `FlexalonRandomModifier` | Positioning across hierarchies, or perturbing a layout's results |
| [cloner-and-data-binding.md](references/cloner-and-data-binding.md) | `FlexalonCloner`, `CloneTypes`, `DataSource`, `DataBinding` | Children must be generated from prefabs or driven by data |
| [animators.md](references/animators.md) | Curve/Lerp/RigidBody animators, `TransformUpdater`, custom animators, animating layout properties | Objects must move between layout results instead of snapping |
| [interactions-and-xr.md](references/interactions-and-xr.md) | `FlexalonInteractable`, `FlexalonDragTarget`, events/state machine, `InputProvider`, XRI and Oculus providers | Adding click/drag, reordering between layouts, or XR grab support |
| [adapters.md](references/adapters.md) | Built-in adapter table per Unity component, `FlexalonAspectRatioAdapter`, `FlexalonColliderAdapter`, custom `Adapter` | An object's Component size or its applied scale is wrong |
| [ugui-integration.md](references/ugui-integration.md) | Flexalon UI, uGUI-component mapping table, canvas setup, aspect-ratio preservation | The surface is a Unity Canvas rather than world-space objects |
| [custom-layouts.md](references/custom-layouts.md) | `Layout`/`LayoutBase`, `Measure`/`Arrange`, Layout Space rules, the `FlexalonNode` API a layout needs | No built-in layout or composition reaches the required arrangement |

## 1. Objective
Arrange GameObjects or uGUI content through Flexalon's box-model pipeline so
positions, rotations, and sizes are computed by declared intent rather than
hand-placed transforms — without two systems fighting over the same
transform (a uGUI Layout Group and a Flexalon layout on one RectTransform, a
Rigidbody and a layout result, a tween and a layout result), without a
layout silently never recomputing because nothing marked it dirty, without a
`SizeType.Fill` child inside a `SizeType.Layout` parent producing a
circular sizing dependency, and without Flexalon types reaching
`Game.Core.*`.

## 2. Role
Act as the Flexalon layout specialist for the client track — the tool
reached for whenever a scene arrangement, a formation, a 3D/XR interface, or
a Canvas screen should be expressed as declared layout intent that adapts to
content and available space, rather than as fixed transform values.

## 3. When to invoke this skill
- Arranging children through any `Flexalon*Layout` component, or sizing an object through `FlexalonObject`.
- A layout must adapt to content size, screen size, or a changing child count (wrapping rows, a grid, a carousel, a formation).
- Positioning one object relative to another across hierarchy boundaries via `FlexalonConstraint`.
- Generating children from prefabs or a data source with `FlexalonCloner`, `DataSource`, and `DataBinding`.
- Click-and-drag insertion, removal, or reordering between layouts via `FlexalonInteractable` and `FlexalonDragTarget`, including XRI/Oculus grab.
- Animating objects between layout results with the Curve, Lerp, or Rigid Body animator, or a custom `TransformUpdater`.
- A symptom report shaped like "objects don't reposition after I change X", "the object is the wrong size", or "physics and the layout fight over the same object".
- Extending the pipeline with a custom `Layout`, `Adapter`, or `TransformUpdater`.
- Negative trigger: uGUI Layout Groups, Content Size Fitter, RectTransform anchoring, or Canvas/EventSystem construction that does not involve Flexalon — that's `ugui`; this skill only covers Flexalon's own uGUI surface and where the two must not overlap.
- Negative trigger: UI Toolkit / UXML / USS flexbox layout — that's `ui-toolkit`; Flexalon does not participate in it.
- Negative trigger: interpolating a value over time as an animation in its own right — that's `dotween-tweening`/`litmotion-tweening`; Flexalon animators only carry an object to its computed layout result.
- Negative trigger: a virtualized/recycling scroll list over a large dataset — that's `osa-optimized-scrollview-adapter`; `FlexalonCloner` instantiates one object per data item with no recycling.
- Negative trigger: inspector attributes, custom drawers, or editor-window tooling — that's `odin-inspector`.
- Negative trigger: any `Game.Core.*` code — Flexalon is `UnityEngine`-dependent, which `coding-principles.md`'s Shared Core integrity section forbids in Core.

## 4. How to use this skill
1. **Confirm Flexalon is the right layout system for this surface, and which edition is installed, before adding any component** — the free UI package ships only a subset of layouts, and a Canvas already driven by uGUI Layout Groups must be converted, not layered on, per [root-links.md](references/root-links.md) and [ugui-integration.md](references/ugui-integration.md).
2. **Settle the update model on the Flexalon singleton before authoring anything** — `UpdateInEditMode`, `UpdateInPlayMode`, and `SkipInactiveObjects` decide whether layout runs at all, and runtime property changes made outside a Flexalon component need `MarkDirty()`, per [core-concepts-and-pipeline.md](references/core-concepts-and-pipeline.md).
3. **Set every axis's size type on Flexalon Object before choosing a layout** — `Component`, `Fixed`, `Fill`, and `Layout` decide what the layout has left to distribute, and `Fill` inside a `Layout`-sized parent axis is the recurring authoring error, per [flexalon-object-sizing.md](references/flexalon-object-sizing.md).
4. **Pick the layout component from the arrangement's actual shape** — linear/wrapping or fixed-interval cells go to [flexible-and-grid-layouts.md](references/flexible-and-grid-layouts.md); radial, path-following, formation, alignment-only, or randomized arrangements go to [radial-curve-and-shape-layouts.md](references/radial-curve-and-shape-layouts.md). Nest layouts rather than reaching for a custom one.
5. **Reach for Flexalon Constraint only when the relationship crosses hierarchies** — a parent-child relationship is already a layout; `FlexalonConstraint` exists for the case where the target is elsewhere in the scene, and it redefines "available space" to the target's size, per [constraints-and-modifiers.md](references/constraints-and-modifiers.md).
6. **Generate repeated children with Flexalon Cloner bound to a data source** — hand-instantiating into a layout duplicates the cloner's child management and loses the `DataBinding` hookup, per [cloner-and-data-binding.md](references/cloner-and-data-binding.md).
7. **Choose the animator by how often the layout result changes** — Curve for results that change rarely (it restarts on every change), Lerp for results that change continuously, Rigid Body whenever a `Rigidbody`/`Rigidbody2D` would otherwise fight the pipeline for the transform, per [animators.md](references/animators.md).
8. **Wire click and drag through Flexalon Interactable plus Flexalon Drag Target, and confirm the input path** — world objects need a `Collider`, UI objects need a raycast-target `Graphic` plus an EventSystem and GraphicRaycaster, and XR routes movement through the SDK's own provider, per [interactions-and-xr.md](references/interactions-and-xr.md).
9. **Confirm which adapter measures an object before fighting its size** — `SizeType.Component` is resolved by the adapter for `MeshRenderer`, `SpriteRenderer`, `TMP_Text`, `RectTransform`, `Image`, or a collider, and the same adapter decides what happens to `localScale`, per [adapters.md](references/adapters.md).
10. **Extend Flexalon with a custom layout only when no built-in composition reaches the result** — a custom `Layout` owes correct `Measure`/`Arrange` behaviour under repeated `Measure` calls and Layout Space rules, which is real cost YAGNI does not pay for speculatively, per [custom-layouts.md](references/custom-layouts.md) and KISS in `coding-principles.md`.
11. **Keep every Flexalon type out of Shared Core** — the package depends on `UnityEngine`, so layout intent lives in `Game.Client.*` and reads Core state, never the reverse, per `coding-principles.md`'s Shared Core integrity section.
12. **Measure layout cost in the Profiler before shipping a layout that dirties every frame** — Flexalon recomputes dirty nodes in `LateUpdate` and a Lerp animator or a per-frame-changed property keeps the subtree dirty continuously; state the frame-time and allocation numbers, per `performance-and-algorithms.md`'s Verification section and [core-concepts-and-pipeline.md](references/core-concepts-and-pipeline.md).
13. **Ask when the edition, the platform's input path, or the animator's timing requirement is unstated** — each changes which components are even available, and all three are expensive to unwind after a scene is authored against the wrong assumption.

## 5. Specific goals / tasks this skill performs
- Authoring a Flexalon layout hierarchy with deliberate per-axis size types, min/max, margins, and padding.
- Selecting and configuring the layout component (flexible, grid, circle/spiral, curve, shape, align, random) that matches the required arrangement.
- Positioning objects across hierarchies with `FlexalonConstraint`, and perturbing results with `FlexalonRandomModifier`.
- Driving children from prefabs or data with `FlexalonCloner`, `DataSource`, and `DataBinding`.
- Adding motion between layout results with the Curve, Lerp, or Rigid Body animator, or a custom `TransformUpdater`.
- Building drag-and-drop between layouts with `FlexalonInteractable`/`FlexalonDragTarget`, including a custom `InputProvider` or an XR provider.
- Diagnosing wrong size, wrong scale, or a layout that never recomputes, against the pipeline and adapter rules.
- Implementing a custom `Layout`, `Adapter`, or `TransformUpdater` when the built-ins genuinely cannot compose to the result.
- Out of scope: uGUI Layout Group/RectTransform authoring (`ugui`), UI Toolkit layout (`ui-toolkit`), general tweening (`dotween-tweening`/`litmotion-tweening`), virtualized scrolling (`osa-optimized-scrollview-adapter`), inspector tooling (`odin-inspector`), shader/VFX work (`technical-artist`), any `Game.Core.*` usage.

## 6. Output format
```
## Flexalon Work — <layout/feature name>
- Edition & version: <Flexalon Pro / free UI package, version> — confirmed, not assumed
- Surface: <world objects / uGUI Canvas> — conflicting uGUI layout components removed: <yes/n/a>
- Sizing: <per-axis SizeType + min/max per object> — rationale
- Layout: <component chosen> — <key properties set, and why this over the alternative>
- Constraint / modifier: <FlexalonConstraint target + align/pivot, modifiers — or "n/a">
- Data: <FlexalonCloner + DataSource/DataBinding — or "static children">
- Animation: <Curve / Lerp / RigidBody / none> — chosen by result-change frequency
- Interaction: <Interactable + DragTarget config, input path confirmed — or "n/a">
- Update model: <UpdateInEditMode/UpdateInPlayMode/manual>, <MarkDirty/ForceUpdate call sites>
- Verification: <Profiler frame-time and allocation numbers vs budget, or how confirmed>
- Layer: Game.Client.* — never Game.Core.*
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces
the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what this layout does not cover>
- Latent concerns: <assumptions holding only at the current child count, screen size, or edition>
- Future remediation: <the concrete fix for each, and its trigger condition>
```

## 7. Examples
**Example 1**
- Input: a 3D inventory shelf must lay items out in rows that wrap, stay centred, and re-flow when the shelf mesh is resized.
- Output: `FlexalonFlexibleLayout` with `Direction.PositiveX`, `Wrap` on and `WrapDirection.NegativeY`; the layout's own `FlexalonObject` width/height set to `SizeType.Fill` so it takes the shelf's space (wrap is inert while the direction axis is `SizeType.Layout`, per [flexible-and-grid-layouts.md](references/flexible-and-grid-layouts.md)); items left at `SizeType.Component` so the `MeshRenderer` adapter measures them, with `MarginRight`/`MarginBottom` for spacing instead of a fixed cell size.

**Example 2**
- Input: "just add a Vertical Layout Group next to the Flexalon Flexible Layout on that panel, it'll centre the children faster."
- Output: declined — both components would drive the same `RectTransform` children and the visible result depends on execution order, which is a silent conflict rather than a Flexalon bug. Set `HorizontalAlign`/`VerticalAlign` (and `HorizontalInnerAlign`/`VerticalInnerAlign`) on the Flexalon layout instead and removed the Layout Group, per [ugui-integration.md](references/ugui-integration.md).

**Example 3**
- Input: chess pieces sit in a grid layout, and a physics object knocks them over; they should push themselves back into place.
- Output: `FlexalonGridLayout` retained; added `FlexalonRigidBodyAnimator` to each piece so the pipeline applies `PositionForce`/`RotationForce` to the `Rigidbody` instead of writing the transform directly — a Lerp or Curve animator would still be fighting the physics system for the same transform, per [animators.md](references/animators.md).

**Example 4**
- Input: a search-results strip is populated at runtime from a web response, and nothing appears until the scene is touched in the editor.
- Output: root-caused to the update model, not the layout — the results were instantiated directly rather than through `FlexalonCloner`, so no node was marked dirty. Moved generation to a `FlexalonCloner` with a component implementing `DataSource` (raising `DataChanged`) and a `DataBinding` on the item prefab, per [cloner-and-data-binding.md](references/cloner-and-data-binding.md) and [core-concepts-and-pipeline.md](references/core-concepts-and-pipeline.md).

## 8. Edge cases & guardrails
- Never leave a uGUI Layout Group, Content Size Fitter, or Aspect Ratio Fitter on an object a Flexalon layout also drives — both write the same values and the winner depends on execution order.
- Never let a `Rigidbody`/`Rigidbody2D` and the pipeline drive the same transform without `FlexalonRigidBodyAnimator` — the object will jitter between physics and layout results every frame.
- Never set a child's axis to `SizeType.Fill` when the parent layout's same axis is `SizeType.Layout` — the parent is sizing itself from its children, so there is no space to take a fraction of.
- Never assume the docs' word "Parent" means a distinct size option — older doc prose says "Parent" where the current enum member is `SizeType.Fill`.
- Never delete the `Flexalon` singleton GameObject in edit mode to "reset" layout — the docs state Unity may need reopening; use `ForceUpdate()` instead.
- Never change a layout property through a non-Flexalon path at runtime without calling `MarkDirty()` — the node stays clean and the layout silently never recomputes.
- Never claim a Flexalon layout is performant without Profiler evidence, per `performance-and-algorithms.md`'s Verification section — a continuously dirty subtree re-runs Measure/Arrange in `LateUpdate` every frame.
- Never place Flexalon types in `Game.Core.*`, per `coding-principles.md`'s Shared Core integrity section.
- If the installed edition, the input system in use, or which layouts the project is licensed for is unstated, ask rather than authoring against an assumption.
- Upgrading Flexalon requires deleting the project's existing `Flexalon` directory before importing the new package, per [root-links.md](references/root-links.md) — that deletion is destructive and requires explicit user confirmation in the current conversation, never inferred from context.
