---
name: flexalon-layouts
description: "Flexalon 3D/uGUI layouts: FlexalonObject SizeType, Flexible/Grid/Circle/Curve layouts, FlexalonConstraint, Cloner/DataSource, animators, Interactable/DragTarget, adapters, MarkDirty. Use when a layout needs Flexalon, not uGUI Layout Groups."
user-invocable: false
---

# Flexalon

Not for: uGUI Layout Group/RectTransform authoring (`ugui`), UI Toolkit USS layout (`ui-toolkit`), general tweening (`dotween-tweening`, `litmotion-tweening`), recycling scroll lists (`osa-optimized-scrollview-adapter`), Inspector attributes (`odin-inspector`), any Core code.
Docs: https://www.flexalon.com/docs (API: https://www.flexalon.com/docs/api/Flexalon.html) — unversioned, serves the newest release; features carry inline `(v3.x/v4.x)` tags, so check any tagged feature against the installed package version. Docs give no default values and no version banner: read both from the Inspector or the installed package. Pages are cited below by URL slug (`/docs/<slug>`).

| Reference | Read when |
|---|---|
| [core-concepts-and-pipeline.md](references/core-concepts-and-pipeline.md) | Layout does not recompute, `MarkDirty`/`ForceUpdate`, singleton settings, per-frame cost |
| [flexalon-object-sizing.md](references/flexalon-object-sizing.md) | Setting any size, `Fill`/`Layout`/`Component`, min/max, margin/padding/offset, an object sized wrongly |
| [flexible-and-grid-layouts.md](references/flexible-and-grid-layouts.md) | Linear, wrapping or fixed-cell arrangement, a board, `FlexalonGridCell` |
| [radial-curve-and-shape-layouts.md](references/radial-curve-and-shape-layouts.md) | Ring, spiral, path, formation, align-only or random arrangement |
| [constraints-and-modifiers.md](references/constraints-and-modifiers.md) | Positioning relative to an object in another hierarchy, or perturbing a layout's result |
| [cloner-and-data-binding.md](references/cloner-and-data-binding.md) | Children generated from prefabs or a data source |
| [animators.md](references/animators.md) | Objects must move to layout results instead of snapping, or a Rigidbody is involved |
| [interactions-and-xr.md](references/interactions-and-xr.md) | Click, drag, reorder between layouts, custom input, XR grab |
| [adapters.md](references/adapters.md) | `SizeType.Component` measures wrong or `localScale` is overwritten |
| [ugui-integration.md](references/ugui-integration.md) | The surface is a Canvas, or Flexalon vs Layout Groups is undecided |
| [custom-layouts.md](references/custom-layouts.md) | No built-in layout or nesting reaches the arrangement |

## Steps
1. **Confirm the edition and version installed** before adding a component: the free UI package ships only two layouts (the site does not name them), and a tagged feature may be missing. Unstated → ask.
2. **Surface decides the seam.** Canvas: replace Layout Groups, never layer them, per [ugui-integration.md](references/ugui-integration.md).
3. **Set update model and per-axis size types first**, per [core-concepts-and-pipeline.md](references/core-concepts-and-pipeline.md) and [flexalon-object-sizing.md](references/flexalon-object-sizing.md). Runtime changes outside a Flexalon component need `MarkDirty()`.
4. **Pick the layout from the arrangement's shape**: linear/wrapping/cells → [flexible-and-grid-layouts.md](references/flexible-and-grid-layouts.md); radial/path/formation/align/random → [radial-curve-and-shape-layouts.md](references/radial-curve-and-shape-layouts.md). Nest layouts before writing a custom one.
5. **`FlexalonConstraint` only across hierarchies** (parent-child is already a layout), per [constraints-and-modifiers.md](references/constraints-and-modifiers.md).
6. **Generate repeated children with `FlexalonCloner`**, per [cloner-and-data-binding.md](references/cloner-and-data-binding.md); hand-instantiated children are outside its lifecycle.
7. **Choose the animator by how often the result changes** (Curve rare, Lerp continuous, Rigid Body when a Rigidbody exists), per [animators.md](references/animators.md).
8. **Interaction**: confirm the input path (collider for world, raycast-target `Graphic` + EventSystem + GraphicRaycaster for UI, SDK provider for XR), per [interactions-and-xr.md](references/interactions-and-xr.md).
9. **Wrong size or overwritten scale**: find the adapter first, per [adapters.md](references/adapters.md).
10. **Custom `Layout`/`Adapter`/`TransformUpdater` only when composition cannot reach the result**, per [custom-layouts.md](references/custom-layouts.md).
11. **Never claim layout performance without Profiler numbers; measure any layout that dirties every frame** (Lerp animator, per-frame property writes, animated `StartAt`) in the Profiler and report frame time and allocations; the docs publish no cost model (`unity-profiler-diagnostics`).

## Never
- Leave a uGUI Layout Group, Content Size Fitter or Aspect Ratio Fitter on an object a Flexalon layout also drives: both write the same values and execution order picks the winner.
- Let a `Rigidbody`/`Rigidbody2D` and the pipeline write one transform without `FlexalonRigidBodyAnimator`: the object jitters.
- Set a child axis to `Fill` under a parent axis of `Layout`: the parent sizes itself from its children, so there is nothing to take a fraction of.
- Delete the `Flexalon` singleton in edit mode to reset layout (Unity may need reopening): use `ForceUpdate()`.
- Put Flexalon types in a Core assembly: the package depends on `UnityEngine`; layout intent lives in Client code and reads Core state, never the reverse.
- Upgrade without the user's explicit confirmation in this conversation: it requires deleting the project's existing `Flexalon` directory before importing the new package.

## Output
```
## Flexalon — <layout/feature>
- Edition & version: <confirmed, not assumed>
- Surface: <world objects / uGUI Canvas>; conflicting uGUI layout components removed: <yes / n/a>
- Sizing: <per-axis SizeType + min/max> — <reason>
- Layout: <component, key properties> — <why this one>
- Constraint / modifier / data / animation / interaction: <choice and input path, or n/a>
- Update model: <settings, MarkDirty/ForceUpdate call sites>
- Verified: <Profiler numbers vs budget, or "not run">
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Add a Vertical Layout Group next to the Flexalon Flexible Layout, it centres faster" → declined: two drivers on one `RectTransform`; set `HorizontalAlign`/`VerticalAlign` (and inner align) on the Flexalon layout and removed the Layout Group.
