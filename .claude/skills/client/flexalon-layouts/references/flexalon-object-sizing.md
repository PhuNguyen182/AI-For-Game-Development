# Flexalon Object Sizing — size types, min/max, spacing, and transform order

Sources: [Flexalon Objects](https://www.flexalon.com/docs/flexalonObject), [Class FlexalonObject](https://www.flexalon.com/docs/api/Flexalon.FlexalonObject.html), [Enum SizeType](https://www.flexalon.com/docs/api/Flexalon.SizeType.html), [Enum MinMaxSizeType](https://www.flexalon.com/docs/api/Flexalon.MinMaxSizeType.html), [Struct Directions](https://www.flexalon.com/docs/api/Flexalon.Directions.html).

Covers: SKILL.md §4 — **"Set every axis's size type on Flexalon Object before choosing a layout"**.

`FlexalonObject` is the only place an object states its own size intent, and
every layout algorithm reads that intent before it can distribute anything.
Getting the three axes right first is what makes the layout choice
mechanical. How `SizeType.Component` is actually resolved per Unity
component lives in [adapters.md](adapters.md).

- [Size types — one per axis](#size-types--one-per-axis)
- [Min / max — `MinMaxSizeType` (v4.1)](#min--max--minmaxsizetype-v41)
- [Scripting surface — the naming pattern](#scripting-surface--the-naming-pattern)
- [Spacing — margin vs padding](#spacing--margin-vs-padding)
- [Offset, rotation, and scale — the ordering that surprises people](#offset-rotation-and-scale--the-ordering-that-surprises-people)
- [Opt-outs](#opt-outs)

## Size types — one per axis

| `SizeType` | Meaning | Choose when | Source |
|---|---|---|---|
| `Component` | Size comes from the adapter and the attached Unity components (`MeshRenderer`, `SpriteRenderer`, `TMP_Text`, `RectTransform`, colliders). An empty GameObject measures **1** | The object's own content should decide its size | [Enum SizeType](https://www.flexalon.com/docs/api/Flexalon.SizeType.html) |
| `Fixed` | An explicit value. Spherical editor handles appear for dragging it | The size is a design constant, not derived from content or space | [Flexalon Objects](https://www.flexalon.com/docs/flexalonObject) |
| `Fill` | A **factor** of the space the parent layout allocated — `0.5` is half, `1` is all | The object should consume available space, not dictate it | [Enum SizeType](https://www.flexalon.com/docs/api/Flexalon.SizeType.html) |
| `Layout` | The size the object's own layout algorithm computes from its children | A container should shrink-wrap its contents | [Enum SizeType](https://www.flexalon.com/docs/api/Flexalon.SizeType.html) |

**Critical caveat**: `Fill` on a child axis and `Layout` on the parent's same
axis is circular — the parent is sizing itself from its children while the
child is asking the parent for a fraction of a size that does not exist yet.
The Flexible Layout's wrapping has the same dependency and simply does not
wrap while its direction axis is `SizeType.Layout`, per
[flexible-and-grid-layouts.md](flexible-and-grid-layouts.md).

**Critical caveat**: several documentation pages say to set a size to
**"Parent"** (the Flexible Layout hint, Constraints, Random Layout). No such
member exists — the current enum member is `SizeType.Fill`. Read "Parent" in
older doc prose as `Fill`.

## Min / max — `MinMaxSizeType` (v4.1)

| `MinMaxSizeType` | Meaning | Source |
|---|---|---|
| `Fixed` | An explicit minimum or maximum value | [Enum MinMaxSizeType](https://www.flexalon.com/docs/api/Flexalon.MinMaxSizeType.html) |
| `Fill` | A factor of the parent layout's size — `0.5` is half the parent | [Enum MinMaxSizeType](https://www.flexalon.com/docs/api/Flexalon.MinMaxSizeType.html) |
| `None` | Unbounded: for min, "the object cannot shrink"; for max, infinity | [Enum MinMaxSizeType](https://www.flexalon.com/docs/api/Flexalon.MinMaxSizeType.html) |

**Shrinking (v4.1)**: an object whose min type is anything other than `None`
"may be shrunk to fit into the parent layout" — so a min other than `None`
does not only raise a floor, it also *opts the object into being shrunk
below its `Fixed` size*. The docs' own example: a 2×2 grid cell with a
child of width 3 and min width 0 shrinks the child to 2. The amount actually
applied is readable as `FlexalonResult.ShrinkSize`, per
[core-concepts-and-pipeline.md](core-concepts-and-pipeline.md).

## Scripting surface — the naming pattern

Each axis carries a type, a fixed value, and a relative factor, and each of
the three exists for size, min, and max. Learn the pattern once rather than
the 30+ property names.

| Pattern | Members | Source |
|---|---|---|
| Per-axis type | `WidthType`, `HeightType`, `DepthType` (`SizeType`) | [Class FlexalonObject](https://www.flexalon.com/docs/api/Flexalon.FlexalonObject.html) |
| Per-axis fixed value | `Width`, `Height`, `Depth` (`float`); `Size` (`Vector3`) sets all three | [Class FlexalonObject](https://www.flexalon.com/docs/api/Flexalon.FlexalonObject.html) |
| Per-axis fill factor | `WidthOfParent`, `HeightOfParent`, `DepthOfParent`; `SizeOfParent` (`Vector3`) | [Class FlexalonObject](https://www.flexalon.com/docs/api/Flexalon.FlexalonObject.html) |
| Min | `MinWidthType`/`MinWidth`/`MinWidthOfParent` (+ Height/Depth), `MinSize`, `MinSizeOfParent` | [Class FlexalonObject](https://www.flexalon.com/docs/api/Flexalon.FlexalonObject.html) |
| Max | `MaxWidthType`/`MaxWidth`/`MaxWidthOfParent` (+ Height/Depth), `MaxSize`, `MaxSizeOfParent` | [Class FlexalonObject](https://www.flexalon.com/docs/api/Flexalon.FlexalonObject.html) |
| Spacing | `Margin`/`Padding` (`Directions`) and the six-way `MarginLeft`…`MarginFront`, `PaddingLeft`…`PaddingFront` | [Class FlexalonObject](https://www.flexalon.com/docs/api/Flexalon.FlexalonObject.html) |
| Transform intent | `Offset` (`Vector3`), `Rotation` (`Quaternion`), `Scale` (`Vector3`) | [Class FlexalonObject](https://www.flexalon.com/docs/api/Flexalon.FlexalonObject.html) |
| Opt-outs | `SkipLayout` (v4.1), `UseDefaultAdapter` (v4.3) | [Class FlexalonObject](https://www.flexalon.com/docs/api/Flexalon.FlexalonObject.html) |

```csharp
using UnityEngine;
using Flexalon;

namespace Game.Client.Layout
{
    // Half the parent's width, natural height from the attached component,
    // never narrower than 200 units.
    public class PanelSizer : MonoBehaviour
    {
        [SerializeField] private FlexalonObject panel;

        public void ApplyResponsiveWidth()
        {
            this.panel.WidthType = SizeType.Fill;
            this.panel.WidthOfParent = 0.5f;
            this.panel.HeightType = SizeType.Component;
            this.panel.MinWidthType = MinMaxSizeType.Fixed;
            this.panel.MinWidth = 200f;
        }
    }
}
```

## Spacing — margin vs padding

| Property | Where the space goes | Who reads it | Source |
|---|---|---|---|
| `Margin` | **Around** the object | The **parent's** layout — it spaces siblings apart | [Flexalon Objects](https://www.flexalon.com/docs/flexalonObject) |
| `Padding` | **Inside** the object | The object's **own** layout — it reduces the space available to children | [Flexalon Objects](https://www.flexalon.com/docs/flexalonObject) |

Both are a `Directions` struct: six floats named `Right`, `Left`, `Top`,
`Bottom`, `Back`, `Front`, with `Size`/`Center` helpers, `Directions.zero`,
and indexers by `int` or `Direction`. Prefer per-item margins over a
layout-wide gap when spacing must differ per child; prefer a gap when it does
not, per [flexible-and-grid-layouts.md](flexible-and-grid-layouts.md).

## Offset, rotation, and scale — the ordering that surprises people

| Property | When it applies | What it does to the box | Source |
|---|---|---|---|
| `Rotation` | **Before** layout | Generates a new size that encapsulates the rotated object — a rotated child therefore occupies a larger axis-aligned box | [Flexalon Objects](https://www.flexalon.com/docs/flexalonObject) |
| `Scale` | **Before** layout | Generates a new size that encapsulates the scaled object — layout sees the scaled size | [Flexalon Objects](https://www.flexalon.com/docs/flexalonObject) |
| `Offset` | **After** layout completes | Adjusts the final position only; the layout never sees it, so siblings do not move out of the way | [Flexalon Objects](https://www.flexalon.com/docs/flexalonObject) |

That asymmetry is the whole rule: use `Rotation`/`Scale` when the layout
should account for the change, and `Offset` when it deliberately should not
(a nudge, a hover lift, a decorative overlap). Rotation and scale changes
alone can be applied through `FlexalonNode.ApplyScaleAndRotation()`, which
the API documents as faster than marking the node dirty.

## Opt-outs

| Property | Effect | Use when | Source |
|---|---|---|---|
| `SkipLayout` (v4.1) | The parent layout skips this child entirely; its position and rotation are not modified | A decorative or manually placed child sits inside a laid-out parent | [Flexalon Objects](https://www.flexalon.com/docs/flexalonObject) |
| `UseDefaultAdapter` (v4.3) | When unchecked, the object is measured as if it were an empty GameObject, ignoring its Unity components | The renderer/collider bounds are the wrong sizing authority — see [adapters.md](adapters.md) | [Class FlexalonObject](https://www.flexalon.com/docs/api/Flexalon.FlexalonObject.html) |
