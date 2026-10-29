# Core Concepts and Pipeline

Pages: `/docs/coreConcepts`, `/docs/pipeline`, API `Flexalon.Flexalon`, `FlexalonNode`, `FlexalonResult`, `FlexalonComponent`, `TransformUpdater`.

## Box model
- Layout algorithms see invisible boxes, never meshes: a visual mismatch is an adapter question ([adapters.md](adapters.md)).
- Box size defaults to the attached components' size; an object without `FlexalonObject` still participates.
- `FlexalonObject` draws the box as a light blue gizmo: fastest size check.
- An empty GameObject measures 1, never 0.

## Pipeline (per root, each step completes for the whole subtree)
1. Measure: adapter then layout; may run several times per update.
2. Arrange: layouts position children; runs once.
3. Constrain: constraints apply.
4. Compute Transforms: Layout Space to Unity local space.
5. Update Transforms: transform updater/animator moves toward the result.

## `Flexalon` singleton
Added to an empty GameObject, or auto-created on first use.

| Member | Decides |
|---|---|
| `UpdateInEditMode` | Off: an Update button appears, layout is manual in the editor |
| `UpdateInPlayMode` | Off: nothing moves at runtime unless updated explicitly; fits a layout that settles once at load |
| `SkipInactiveObjects` | Whether `SetActive(false)` children are excluded and siblings reflow |
| `InputProvider` | Global input source, see [interactions-and-xr.md](interactions-and-xr.md) |
| `PreUpdate` (`Action`) | Hook to push state into layout properties before the update |
| `ForceUpdate()` | Marks every node dirty then updates: whole-scene, never per-frame |
| `UpdateDirtyNodes()` | Updates only what is already dirty |
| `Get()` / `GetOrCreate()` | `Get()` returns null without a singleton |
| `GetNode(go)` / `GetOrCreateNode(go)` | `GetNode` returns null for an unmanaged object |
| `Nodes` | Tracked nodes; the count to watch as cost grows |

Alias the type: `Flexalon.Flexalon` shares its namespace's name, so `Flexalon.GetOrCreateNode(...)` is ambiguous outside the namespace (`using FlexalonSystem = Flexalon.Flexalon;`).

## Dirty tracking
| Call | Effect |
|---|---|
| `FlexalonComponent.MarkDirty()` | Visited in dependency order on `LateUpdate` |
| `FlexalonComponent.ForceUpdate()` | Immediate: this component, parents and children |
| `FlexalonNode.MarkDirty()` / `ForceUpdate()` | Same, at node level (MarkDirty also dirties parents) |
| `FlexalonNode.ApplyScaleAndRotation()` | Rotation/scale only; faster than marking dirty |
| `FlexalonNode.ResultChanged` | `Action<FlexalonNode>` when results change: use instead of polling |

`FlexalonCloner.MarkDirty()` is a different operation (regenerates clones).

## `FlexalonResult`
Generated per laid-out object so results load from scene/prefab without re-running layout; do not hand-edit, expect it in scene diffs. Diagnostics fields:
- `FillSize`, `ShrinkSize`, `ComponentScale`: what the parent gave a `Fill` child or shrank to; first read for a wrong size.
- `AdapterBounds` vs `LayoutBounds`: adapter vs layout origin of a size.
- `TargetPosition/Rotation/Scale/RectSize`: where the updater is heading (differs mid-animation).
- `Transform*` fields: last written values; how Flexalon notices another system moved the object.

## Cost
The docs publish no benchmark; these are mechanics, so profile real scenes.
- A static layout costs nothing after it settles; work is per dirty subtree per frame.
- A `Fill`-width text that re-wraps and changes height forces re-measure.
- A Lerp or Rigid Body animator reports "still animating" every frame ([animators.md](animators.md)).
- Prefer `FlexalonComponent.ForceUpdate()` on the affected subtree over the singleton's.
