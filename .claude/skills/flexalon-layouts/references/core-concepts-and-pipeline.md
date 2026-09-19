# Core Concepts and Pipeline — the singleton, the node tree, and when layout runs

Sources: [Core Concepts](https://www.flexalon.com/docs/coreConcepts), [Flexalon Pipeline](https://www.flexalon.com/docs/pipeline), [Class Flexalon](https://www.flexalon.com/docs/api/Flexalon.Flexalon.html), [Interface FlexalonNode](https://www.flexalon.com/docs/api/Flexalon.FlexalonNode.html), [Class FlexalonResult](https://www.flexalon.com/docs/api/Flexalon.FlexalonResult.html), [Class FlexalonComponent](https://www.flexalon.com/docs/api/Flexalon.FlexalonComponent.html).
Covers: SKILL.md §4 — **"Settle the update model on the Flexalon singleton before authoring anything"**, **"Measure layout cost in the Profiler before shipping a layout that dirties every frame"**.

Flexalon computes every managed object's position, rotation, and size through
one sequential pipeline over a tree of `FlexalonNode`s. This file holds what
decides *whether and when* that pipeline runs, and what it leaves behind.
The `Measure`/`Arrange` contract a custom layout must satisfy lives in
[custom-layouts.md](custom-layouts.md); per-object sizing inputs live in
[flexalon-object-sizing.md](flexalon-object-sizing.md).

- [The box model](#the-box-model)
- [Pipeline steps — in order](#pipeline-steps--in-order)
- [The `Flexalon` singleton](#the-flexalon-singleton)
- [Dirty tracking — the update model](#dirty-tracking--the-update-model)
- [`FlexalonResult` — what is cached on every laid-out object](#flexalonresult--what-is-cached-on-every-laid-out-object)
- [Cost model — what actually drives per-frame work](#cost-model--what-actually-drives-per-frame-work)

## The box model

| Fact | Consequence | Source |
|---|---|---|
| Every managed gameObject has an invisible layout box | Layout algorithms only ever see boxes, never meshes or glyphs — a visual mismatch is an adapter question, not a layout one | [Flexalon Objects](https://www.flexalon.com/docs/flexalonObject) |
| Box size defaults to the size of the attached Unity components | An object with no `FlexalonObject` still participates, sized by its adapter | [Flexalon Objects](https://www.flexalon.com/docs/flexalonObject) |
| Adding `FlexalonObject` draws the box as a light blue gizmo | The gizmo is the fastest check for "is this object the size I think it is" | [Flexalon Objects](https://www.flexalon.com/docs/flexalonObject) |
| An empty GameObject measures as size 1 | An empty container is never size 0 — set `SizeType.Layout` or `Fixed` if 1 is wrong | [SizeType](https://www.flexalon.com/docs/api/Flexalon.SizeType.html) |

## Pipeline steps — in order

| # | Step | What happens | Extension point | Source |
|---|---|---|---|---|
| 1 | Measure | Adapter's `Measure` runs first to account for external components, then the layout's `Measure` | `Adapter` ([adapters.md](adapters.md)), `LayoutBase` ([custom-layouts.md](custom-layouts.md)) | [Pipeline](https://www.flexalon.com/docs/pipeline) |
| 2 | Arrange | Every node holding a layout positions its children | `LayoutBase` ([custom-layouts.md](custom-layouts.md)) | [Pipeline](https://www.flexalon.com/docs/pipeline) |
| 3 | Constrain | Each node applies its constraint | `Constraint` ([constraints-and-modifiers.md](constraints-and-modifiers.md)) | [Pipeline](https://www.flexalon.com/docs/pipeline) |
| 4 | Compute Transforms | Layout results convert from Layout Space to Unity local space; dependent external components are updated | `Adapter` ([adapters.md](adapters.md)) | [Pipeline](https://www.flexalon.com/docs/pipeline) |
| 5 | Update Transforms | The transform updater or animator moves the transform toward the result | `TransformUpdater` ([animators.md](animators.md)) | [Pipeline](https://www.flexalon.com/docs/pipeline) |

The pipeline runs on each root gameObject Flexalon manages and cascades down
the tree at each step — so a step completes for the whole subtree before the
next begins, which is why `Measure` may be called several times per update
while `Arrange` runs once.

## The `Flexalon` singleton

| Member | What it decides | Source |
|---|---|---|
| `UpdateInEditMode` | Whether property edits recompute layout in the editor. Off ⇒ an **Update button** appears and layout is manual | [Core Concepts](https://www.flexalon.com/docs/coreConcepts) |
| `UpdateInPlayMode` | Whether layout recomputes at runtime at all. Off ⇒ nothing moves unless something calls an update explicitly | [Core Concepts](https://www.flexalon.com/docs/coreConcepts) |
| `SkipInactiveObjects` | Whether inactive gameObjects are excluded from layout — decides whether toggling `SetActive` reflows siblings | [Class Flexalon](https://www.flexalon.com/docs/api/Flexalon.Flexalon.html) |
| `InputProvider` | Replaces the default mouse/touch input for every `FlexalonInteractable` — see [interactions-and-xr.md](interactions-and-xr.md) | [Class Flexalon](https://www.flexalon.com/docs/api/Flexalon.Flexalon.html) |
| `Nodes` | `IReadOnlyCollection<FlexalonNode>` of everything Flexalon tracks — the count to watch when a scene's layout cost grows | [Class Flexalon](https://www.flexalon.com/docs/api/Flexalon.Flexalon.html) |
| `PreUpdate` | `System.Action` invoked before Flexalon updates — the hook for pushing state into layout properties in the right frame order | [Class Flexalon](https://www.flexalon.com/docs/api/Flexalon.Flexalon.html) |
| `ForceUpdate()` | Marks **every** node and component dirty, then updates — a whole-scene recompute, not a targeted one | [Class Flexalon](https://www.flexalon.com/docs/api/Flexalon.Flexalon.html) |
| `UpdateDirtyNodes()` | Updates only what is already dirty — the targeted counterpart to `ForceUpdate()` | [Class Flexalon](https://www.flexalon.com/docs/api/Flexalon.Flexalon.html) |
| `Get()` / `GetOrCreate()` | `Get()` returns null when no singleton exists; `GetOrCreate()` creates one | [Class Flexalon](https://www.flexalon.com/docs/api/Flexalon.Flexalon.html) |
| `GetNode(GameObject)` / `GetOrCreateNode(GameObject)` | Node access — `GetNode` returns null for an unmanaged object, `GetOrCreateNode` brings it under management | [Class Flexalon](https://www.flexalon.com/docs/api/Flexalon.Flexalon.html) |
| `AddComponent<T>(GameObject)` | Adds a component with editor Undo handled correctly — use it over `GameObject.AddComponent` in editor tooling | [Class Flexalon](https://www.flexalon.com/docs/api/Flexalon.Flexalon.html) |

**Critical caveat**: deleting the `Flexalon` singleton in edit mode may require
re-opening Unity, per [Core Concepts](https://www.flexalon.com/docs/coreConcepts) — it is not a safe reset gesture. Use
`ForceUpdate()` for the "Flexalon didn't notice a change" case instead; the
docs name that as the intended escape hatch for edge cases the dirty
tracking misses.

## Dirty tracking — the update model

| Trigger | Effect | Source |
|---|---|---|
| `FlexalonComponent.MarkDirty()` | Marks this component for update; the singleton visits it **in dependency order on `LateUpdate`** | [Class FlexalonComponent](https://www.flexalon.com/docs/api/Flexalon.FlexalonComponent.html) |
| `FlexalonComponent.ForceUpdate()` | Updates this component, its parents, and its children **immediately** — synchronous, not deferred to `LateUpdate` | [Class FlexalonComponent](https://www.flexalon.com/docs/api/Flexalon.FlexalonComponent.html) |
| `FlexalonNode.MarkDirty()` | Marks the node and its parents dirty | [Interface FlexalonNode](https://www.flexalon.com/docs/api/Flexalon.FlexalonNode.html) |
| `FlexalonNode.ForceUpdate()` | Immediate update of the node, its parents, and its children | [Interface FlexalonNode](https://www.flexalon.com/docs/api/Flexalon.FlexalonNode.html) |
| `FlexalonNode.ApplyScaleAndRotation()` | Applies only rotation/scale changes — explicitly "faster than marking it dirty" | [Interface FlexalonNode](https://www.flexalon.com/docs/api/Flexalon.FlexalonNode.html) |
| `FlexalonNode.ResultChanged` | `Action<FlexalonNode>` raised when layout results change — the correct hook for reacting to layout, instead of polling in `Update` | [Interface FlexalonNode](https://www.flexalon.com/docs/api/Flexalon.FlexalonNode.html) |

```csharp
using UnityEngine;
using Flexalon;
using FlexalonSystem = Flexalon.Flexalon;

namespace Game.Client.Layout
{
    // Reacts to layout results instead of polling the transform each frame.
    public class LayoutResultWatcher : MonoBehaviour
    {
        private FlexalonNode _node;

        private void OnEnable()
        {
            this._node = FlexalonSystem.GetOrCreateNode(this.gameObject);
            this._node.ResultChanged += this.OnResultChanged;
        }

        private void OnDisable()
        {
            if (this._node != null)
            {
                this._node.ResultChanged -= this.OnResultChanged;
            }
        }

        private void OnResultChanged(FlexalonNode node)
        {
            this.transform.hasChanged = false;
        }
    }
}
```

**Critical caveat**: the type `Flexalon.Flexalon` shares its name with its own
namespace, so `Flexalon.GetOrCreateNode(...)` written from another namespace
is ambiguous between the two. Alias it (`using FlexalonSystem =
Flexalon.Flexalon;`) as above rather than copying the docs' unqualified form,
which is written from inside the `Flexalon` namespace.

## `FlexalonResult` — what is cached on every laid-out object

A `FlexalonResult` component is added to each object in a layout so results
"can be loaded from a scene/prefab without rerunning layout". It is
generated state, not authored state — do not hand-edit it, and expect it in
scene diffs.

| Field group | Fields | Why it matters | Source |
|---|---|---|---|
| Layout-space results | `LayoutPosition`, `LayoutRotation`, `LayoutBounds`, `AdapterBounds`, `RotatedAndScaledBounds` | The arrange output before conversion to Unity local space | [Class FlexalonResult](https://www.flexalon.com/docs/api/Flexalon.FlexalonResult.html) |
| Allocated size | `FillSize`, `ShrinkSize`, `ComponentScale` | What the parent gave a `Fill` child, and what a min-size child was shrunk to — the first thing to read when a size looks wrong | [Class FlexalonResult](https://www.flexalon.com/docs/api/Flexalon.FlexalonResult.html) |
| Target transform | `TargetPosition`, `TargetRotation`, `TargetScale`, `TargetRectSize` | Where the transform updater is moving the object *to* — differs from the transform mid-animation | [Class FlexalonResult](https://www.flexalon.com/docs/api/Flexalon.FlexalonResult.html) |
| Last written | `TransformPosition`, `TransformRotation`, `TransformScale`, `TransformRectSize` | Used to detect *unexpected* external changes — this is how Flexalon notices another system moved the object | [Class FlexalonResult](https://www.flexalon.com/docs/api/Flexalon.FlexalonResult.html) |
| Hierarchy | `Parent`, `SiblingIndex` | Layout parent and index, independent of the Unity transform ordering at load | [Class FlexalonResult](https://www.flexalon.com/docs/api/Flexalon.FlexalonResult.html) |

## Cost model — what actually drives per-frame work

Upstream publishes no benchmark, so these are the documented mechanics that
determine cost, not measured numbers. Every claim about a specific scene
still needs the Profiler, per `performance-and-algorithms.md`'s Verification
section.

| Mechanic | Cost consequence | Source |
|---|---|---|
| Dirty nodes are visited in dependency order on `LateUpdate` | Work is per-frame only for subtrees that are dirty that frame — a static layout costs nothing after it settles | [Class FlexalonComponent](https://www.flexalon.com/docs/api/Flexalon.FlexalonComponent.html) |
| `Measure` may run several times per update, `Arrange` once | A `Fill`-width text child that re-wraps and changes height forces re-measurement — expensive layouts are usually re-measuring, not re-arranging | [Custom Layout](https://www.flexalon.com/docs/customLayout) |
| A Lerp or Rigid Body animator returns "still animating" every frame | The node keeps updating for the animation's whole duration — see [animators.md](animators.md) | [Interface TransformUpdater](https://www.flexalon.com/docs/api/Flexalon.TransformUpdater.html) |
| `Flexalon.ForceUpdate()` marks every node and component dirty | Whole-scene recompute; never a per-frame call. Prefer `FlexalonComponent.ForceUpdate()` on the affected subtree | [Class Flexalon](https://www.flexalon.com/docs/api/Flexalon.Flexalon.html) |
| `UpdateInPlayMode` can be turned off entirely | For a layout that only needs to settle once (a level built at load), manual updates remove all runtime cost | [Core Concepts](https://www.flexalon.com/docs/coreConcepts) |
| `SkipInactiveObjects` | Deactivated children can be excluded from measurement instead of being measured and hidden | [Class Flexalon](https://www.flexalon.com/docs/api/Flexalon.Flexalon.html) |
