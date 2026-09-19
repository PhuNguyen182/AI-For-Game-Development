# Root Links — Flexalon (unversioned documentation)

Source: the root index pages listed below, as provided for this skill.
Covers: the whole skill — provenance and version anchor for every file in
this folder.

Anchors every link in this folder to flexalon.com's live documentation.
Upstream publishes **no version segment in its URLs**, so no pin is possible:
the site always serves the current release. Version availability is instead
marked inline on the pages themselves — `(v3.0)`, `(v3.2)`, `(v4.0)`,
`(v4.1)`, `(v4.3)` — and every such tag is carried into the sibling files.
Anything not reachable under one of these roots is out of scope for this
skill, not merely undocumented here.

| Root | Holds | Source |
|---|---|---|
| Documentation index | Install, core concepts, every component page, the sidebar that defines this skill's topic set | [Flexalon Docs](https://www.flexalon.com/docs) |
| Scripting API | Every public type and member in the `Flexalon` namespace (`Flexalon.dll`) | [Namespace Flexalon](https://www.flexalon.com/docs/api/Flexalon.html) |
| Product site | Editions, what each layout is for, the free Template Pack | [flexalon.com](https://www.flexalon.com/) |

Every other link in this folder is a specific page under these roots, each
verified to resolve at authoring time. Because nothing is version-pinned,
**re-check any feature tagged `(v4.x)` against the version actually
installed** before depending on it; the live site describes the newest
release, not the one in the project.

## Distribution and install

| Fact | Detail | Source |
|---|---|---|
| Vendor | Virtual Maker Corporation | [flexalon.com](https://www.flexalon.com/) |
| Editions | Paid full asset (Asset Store, "Flexalon Pro: 3D & UI Layouts"), plus a free UI package covering "Flexalon's two most popular layouts" | [flexalon.com](https://www.flexalon.com/) |
| Dependencies | None — "Flexalon won't break your existing workflow, and doesn't have any dependencies" | [flexalon.com](https://www.flexalon.com/) |
| Scope of effect | "Flexalon will only modify objects with Flexalon Layout Components attached" | [flexalon.com](https://www.flexalon.com/) |
| Install | Import the package; `Documentation` and `Samples` directories are optional | [Installation](https://www.flexalon.com/docs) |
| Upgrade | **Delete the existing `Flexalon` directory in the project first** | [Installation](https://www.flexalon.com/docs) |
| Singleton | Add the `Flexalon` component to an empty GameObject, or let it be created automatically on first use of any Flexalon component | [Installation](https://www.flexalon.com/docs) |
| Template Pack | 16 free working example scenes; its install page states Unity 2019.4 or newer | [Template Pack](https://www.flexalon.com/docs/templates) |
| Samples | `Flexalon/Samples/Scenes/UI` (UI), `Samples/Scripts` (a `CustomLayout` example and the drag script the docs reference) | [Flexalon UI](https://www.flexalon.com/docs/ui), [Custom Layout](https://www.flexalon.com/docs/customLayout) |

## Topic → file map

| Topic | File | Source |
|---|---|---|
| Singleton, box model, pipeline steps, `FlexalonNode`, `FlexalonResult`, dirty/update model | [core-concepts-and-pipeline.md](core-concepts-and-pipeline.md) | [Core Concepts](https://www.flexalon.com/docs/coreConcepts), [Pipeline](https://www.flexalon.com/docs/pipeline) |
| `SizeType`, `MinMaxSizeType`, shrinking, margin/padding/offset/rotation/scale, `SkipLayout`, `UseDefaultAdapter` | [flexalon-object-sizing.md](flexalon-object-sizing.md) | [Flexalon Objects](https://www.flexalon.com/docs/flexalonObject) |
| Flexible and Grid layouts, `FlexalonGridCell` | [flexible-and-grid-layouts.md](flexible-and-grid-layouts.md) | [Flexible Layout](https://www.flexalon.com/docs/flexibleLayout), [Grid Layout](https://www.flexalon.com/docs/gridLayout) |
| Circle/Spiral, Curve, Shape, Align, Random layouts | [radial-curve-and-shape-layouts.md](radial-curve-and-shape-layouts.md) | [Circle](https://www.flexalon.com/docs/circleLayout), [Curve](https://www.flexalon.com/docs/curveLayout), [Shape](https://www.flexalon.com/docs/shapeLayout), [Align](https://www.flexalon.com/docs/alignLayout), [Random](https://www.flexalon.com/docs/randomLayout) |
| `FlexalonConstraint`, `FlexalonModifier`, `FlexalonRandomModifier` | [constraints-and-modifiers.md](constraints-and-modifiers.md) | [Constraints](https://www.flexalon.com/docs/constraints), [Random Modifier](https://www.flexalon.com/docs/randomModifier) |
| `FlexalonCloner`, `DataSource`, `DataBinding` | [cloner-and-data-binding.md](cloner-and-data-binding.md) | [Cloner](https://www.flexalon.com/docs/cloner) |
| Curve/Lerp/RigidBody animators, `TransformUpdater`, custom animators | [animators.md](animators.md) | [Animators](https://www.flexalon.com/docs/animators), [Custom Animators](https://www.flexalon.com/docs/customAnimators) |
| `FlexalonInteractable`, `FlexalonDragTarget`, `InputProvider`, XRI/Oculus | [interactions-and-xr.md](interactions-and-xr.md) | [Interactable](https://www.flexalon.com/docs/interactable), [XR](https://www.flexalon.com/docs/xr) |
| Default adapters per component, aspect-ratio/collider adapters, custom `Adapter` | [adapters.md](adapters.md) | [Adapters](https://www.flexalon.com/docs/adapters) |
| Flexalon UI, uGUI mapping, canvas setup, aspect ratio | [ugui-integration.md](ugui-integration.md) | [Flexalon UI](https://www.flexalon.com/docs/ui) |
| `Layout`/`LayoutBase`, `Measure`/`Arrange`, Layout Space | [custom-layouts.md](custom-layouts.md) | [Custom Layout](https://www.flexalon.com/docs/customLayout) |

## Disclosed gaps

| Area | Issue | Source |
|---|---|---|
| Exact current version number | The docs carry no version banner and no changelog page exists; the newest inline tag observed is `(v4.3)`. Read the installed package's own version rather than inferring one from this skill. | [Flexalon Docs](https://www.flexalon.com/docs) |
| Which two layouts the free UI package ships | The product site says "Flexalon's two most popular layouts" without naming them. Confirm against the package before promising a layout is available in the free edition. | [flexalon.com](https://www.flexalon.com/) |
| Default values of inspector properties | The docs describe what each property does, not its default. Confirm a default in the Inspector or the installed source before depending on it. | [Flexalon Objects](https://www.flexalon.com/docs/flexalonObject) |
| Performance characteristics | Upstream publishes no cost model, budget, or complexity statement for any layout. Every performance claim in this folder is derived from the documented update model, not from a vendor benchmark — measure per `performance-and-algorithms.md`. | synthesized |
| Disabled `FlexalonInteractable` features under XR | The XR page states several features are disabled but enumerates them only in an image. | [XR Interactions](https://www.flexalon.com/docs/xr) |
| `Flexalon UI Copilot` | Announced on the docs as "Coming Soon" with no API surface published. Out of scope until it ships. | [Flexalon UI](https://www.flexalon.com/docs/ui) |
