# Flexible and Grid Layouts — linear, wrapping, and fixed-interval arrangements

Sources: [Flexible Layout](https://www.flexalon.com/docs/flexibleLayout), [Grid Layout](https://www.flexalon.com/docs/gridLayout), [Class FlexalonFlexibleLayout](https://www.flexalon.com/docs/api/Flexalon.FlexalonFlexibleLayout.html), [Class FlexalonGridLayout](https://www.flexalon.com/docs/api/Flexalon.FlexalonGridLayout.html), [Class FlexalonGridCell](https://www.flexalon.com/docs/api/Flexalon.FlexalonGridCell.html).
Covers: SKILL.md §4 — **"Pick the layout component from the arrangement's actual shape"**.

The two layouts that cover most work: Flexible packs children one after
another and accounts for their individual sizes; Grid places them at fixed
intervals regardless of size. Radial, path, formation, and randomized
arrangements live in [radial-curve-and-shape-layouts.md](radial-curve-and-shape-layouts.md).

## Choosing between them

| Requirement | Layout | Why | Source |
|---|---|---|---|
| Children have differing sizes and should sit flush against each other | `FlexalonFlexibleLayout` | It measures each child and spaces accordingly | [Flexible Layout](https://www.flexalon.com/docs/flexibleLayout) |
| Content must reflow into new lines when it runs out of room | `FlexalonFlexibleLayout` with `Wrap` | Grid has no wrapping concept — its line breaks are fixed by `Columns` | [Flexible Layout](https://www.flexalon.com/docs/flexibleLayout) |
| Every child must land on a regular interval regardless of its size | `FlexalonGridLayout` | Cells are positional, not content-derived | [Grid Layout](https://www.flexalon.com/docs/gridLayout) |
| A specific child must occupy a specific cell | `FlexalonGridLayout` + `FlexalonGridCell` | Only the grid has addressable cells | [Grid Layout](https://www.flexalon.com/docs/gridLayout) |
| The arrangement is a hex board | `FlexalonGridLayout` with `CellTypes.Hexagonal` | Built in; do not hand-offset a rectangular grid | [Grid Layout](https://www.flexalon.com/docs/gridLayout) |

## `FlexalonFlexibleLayout`

| Property | What it decides | Source |
|---|---|---|
| `Direction` (`Direction`) | The axis and sign children advance along: `PositiveX`…`NegativeZ` | [Class FlexalonFlexibleLayout](https://www.flexalon.com/docs/api/Flexalon.FlexalonFlexibleLayout.html) |
| `Wrap` (`bool`) | Start a new line when the direction axis runs out of space — **inert while that axis is `SizeType.Layout`**, because the layout is then sizing itself from its children | [Flexible Layout](https://www.flexalon.com/docs/flexibleLayout) |
| `WrapDirection` (`Direction`) | The axis new lines advance along — must differ from `Direction` to be meaningful | [Class FlexalonFlexibleLayout](https://www.flexalon.com/docs/api/Flexalon.FlexalonFlexibleLayout.html) |
| `HorizontalAlign`, `VerticalAlign`, `DepthAlign` (`Align`) | Where the **whole layout** sits inside the parent's box | [Class FlexalonFlexibleLayout](https://www.flexalon.com/docs/api/Flexalon.FlexalonFlexibleLayout.html) |
| `HorizontalInnerAlign`, `VerticalInnerAlign`, `DepthInnerAlign` (`Align`) | Along the `Direction` axis: how wrapped **lines** align with each other. Along the other two axes: how each **object** lines up with the others | [Flexible Layout](https://www.flexalon.com/docs/flexibleLayout) |
| `Gap` (`float`) / `GapType` (`GapOptions`) | Space between objects on the `Direction` axis | [Class FlexalonFlexibleLayout](https://www.flexalon.com/docs/api/Flexalon.FlexalonFlexibleLayout.html) |
| `WrapGap` (`float`) / `WrapGapType` (`GapOptions`) | Space between lines on the `WrapDirection` axis | [Class FlexalonFlexibleLayout](https://www.flexalon.com/docs/api/Flexalon.FlexalonFlexibleLayout.html) |

| `GapOptions` | Effect | Choose when | Source |
|---|---|---|---|
| `Fixed = 0` | The `Gap`/`WrapGap` value is the spacing | Spacing is a constant the design specifies | [Enum GapOptions](https://www.flexalon.com/docs/api/Flexalon.FlexalonFlexibleLayout.GapOptions.html) |
| `SpaceBetween = 1` | Space is added between children to fill the available space | The layout has a known size (`Fixed`/`Fill`) and children should distribute across it | [Enum GapOptions](https://www.flexalon.com/docs/api/Flexalon.FlexalonFlexibleLayout.GapOptions.html) |

`Align` has exactly three members — `Start`, `Center`, `End` — and is shared by
every layout and by `FlexalonConstraint`.

**Critical caveat**: `SpaceBetween` and `Wrap` both need a bounded direction
axis. If the layout's own `FlexalonObject` leaves that axis at
`SizeType.Layout`, both silently do nothing — the layout has no space to
distribute or overflow. Set the axis to `Fixed` or `Fill` first, per
[flexalon-object-sizing.md](flexalon-object-sizing.md).

```csharp
using UnityEngine;
using Flexalon;

namespace Game.Client.Layout
{
    // A wrapping row that fills its parent and spreads items across each line.
    public class WrappingRow : MonoBehaviour
    {
        [SerializeField] private FlexalonObject bounds;
        [SerializeField] private FlexalonFlexibleLayout row;

        private void Awake()
        {
            this.bounds.WidthType = SizeType.Fill;
            this.bounds.WidthOfParent = 1f;
            this.bounds.HeightType = SizeType.Layout;

            this.row.Direction = Direction.PositiveX;
            this.row.Wrap = true;
            this.row.WrapDirection = Direction.NegativeY;
            this.row.GapType = FlexalonFlexibleLayout.GapOptions.SpaceBetween;
            this.row.WrapGapType = FlexalonFlexibleLayout.GapOptions.Fixed;
            this.row.WrapGap = 8f;
            this.row.HorizontalInnerAlign = Align.Start;
            this.row.VerticalInnerAlign = Align.Center;
        }
    }
}
```

## `FlexalonGridLayout`

Children are placed **in column-row-layer order**. Layers, per-axis cell
sizing, and layer spacing arrived in v3.0.

| Property | What it decides | Source |
|---|---|---|
| `CellType` (`CellTypes`) | `Rectangle = 0` or `Hexagonal = 1` cells on the column-row axes | [Enum CellTypes](https://www.flexalon.com/docs/api/Flexalon.FlexalonGridLayout.CellTypes.html) |
| `Columns`, `Rows`, `Layers` (`uint`) | Cell counts on each axis — `Layers` (v3.0) makes the grid 3D | [Class FlexalonGridLayout](https://www.flexalon.com/docs/api/Flexalon.FlexalonGridLayout.html) |
| `ColumnDirection`, `RowDirection`, `LayerDirection` (`Direction`) | Which axis and sign each grid axis maps to — this is what puts a grid on the XZ floor plane instead of XY | [Class FlexalonGridLayout](https://www.flexalon.com/docs/api/Flexalon.FlexalonGridLayout.html) |
| `ColumnSizeType`, `RowSizeType`, `LayerSizeType` (`CellSizeTypes`) | `Fill = 0` divides the layout's size by the cell count; `Fixed = 1` uses the explicit size | [Enum CellSizeTypes](https://www.flexalon.com/docs/api/Flexalon.FlexalonGridLayout.CellSizeTypes.html) |
| `ColumnSize`, `RowSize`, `LayerSizeSize` (`float`) | The fixed cell extent per axis when that axis is `Fixed`. The layer property really is spelled `LayerSizeSize` in the API | [Class FlexalonGridLayout](https://www.flexalon.com/docs/api/Flexalon.FlexalonGridLayout.html) |
| `ColumnSpacing`, `RowSpacing`, `LayerSpacing` (`float`) | Empty space **between** cells, on top of cell size | [Grid Layout](https://www.flexalon.com/docs/gridLayout) |
| `HorizontalAlign`, `VerticalAlign`, `DepthAlign` (`Align`) | How each child aligns **within its own cell** — not how the grid aligns in its parent | [Class FlexalonGridLayout](https://www.flexalon.com/docs/api/Flexalon.FlexalonGridLayout.html) |
| `GetChildAt(column, row, layer = 0)` | The first `Transform` in a cell — the read path for "what is on this square" | [Class FlexalonGridLayout](https://www.flexalon.com/docs/api/Flexalon.FlexalonGridLayout.html) |
| `GetChildrenAt(column, row, layer = 0)` | All `Transform`s in a cell, since a cell can hold several | [Class FlexalonGridLayout](https://www.flexalon.com/docs/api/Flexalon.FlexalonGridLayout.html) |

`CellSizeTypes.Fill` divides the layout's own size by the cell count, so it
requires that axis to be sized `Fixed` or `Fill` on the grid's
`FlexalonObject` — the same bounded-axis precondition as wrapping above.

## `FlexalonGridCell` — addressing a specific cell

| Member | Effect | Source |
|---|---|---|
| `Cell` (`Vector3Int`) | The cell to occupy, as column/row/layer | [Class FlexalonGridCell](https://www.flexalon.com/docs/api/Flexalon.FlexalonGridCell.html) |
| `Column`, `Row`, `Layer` (`int`) | The same address, one axis at a time | [Class FlexalonGridCell](https://www.flexalon.com/docs/api/Flexalon.FlexalonGridCell.html) |

A child carrying `FlexalonGridCell` is **skipped by the automatic
column-row ordering**, so adding one shifts every later sibling's cell by one
position. It is also the only way to put more than one child in the same
cell — which is what makes a piece-on-a-square board work.
