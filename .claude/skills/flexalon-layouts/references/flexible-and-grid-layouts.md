# Flexible and Grid Layouts

Pages: `/docs/flexibleLayout`, `/docs/gridLayout`, API `FlexalonFlexibleLayout`, `FlexalonGridLayout`, `FlexalonGridCell`.

| Need | Layout |
|---|---|
| Differing sizes sitting flush; reflow into lines | `FlexalonFlexibleLayout` (+ `Wrap`) |
| Regular intervals regardless of size; addressable cells; hex board | `FlexalonGridLayout` (`CellType = Hexagonal`; do not offset a rectangle by hand) |

`Align` is `Start`/`Center`/`End`, shared by every layout and `FlexalonConstraint`.

## `FlexalonFlexibleLayout`
| Property | Decides |
|---|---|
| `Direction` | Axis and sign children advance along (`PositiveX`..`NegativeZ`) |
| `Wrap` | New line when the direction axis runs out of space; inert while that axis is `SizeType.Layout` |
| `WrapDirection` | Axis lines advance along; must differ from `Direction` |
| `HorizontalAlign`/`VerticalAlign`/`DepthAlign` | Where the whole layout sits in the parent's box |
| `*InnerAlign` | Along `Direction`: how wrapped lines align to each other; other axes: how objects line up |
| `Gap`/`GapType`, `WrapGap`/`WrapGapType` | Spacing between objects / lines. `GapOptions.Fixed = 0` uses the value; `SpaceBetween = 1` distributes available space |

`SpaceBetween` and `Wrap` need the layout's own `FlexalonObject` direction axis set to `Fixed` or `Fill`, otherwise both silently do nothing.

## `FlexalonGridLayout`
Children fill in column-row-layer order. Layers and per-axis cell sizing arrived in v3.0.

| Property | Decides |
|---|---|
| `CellType` | `Rectangle = 0`, `Hexagonal = 1` |
| `Columns`, `Rows`, `Layers` | Cell counts (`Layers` makes it 3D) |
| `ColumnDirection`, `RowDirection`, `LayerDirection` | Axis/sign per grid axis; puts a grid on the XZ floor |
| `ColumnSizeType`/`RowSizeType`/`LayerSizeType` | `CellSizeTypes.Fill = 0` divides layout size by count (needs a `Fixed`/`Fill` layout axis); `Fixed = 1` |
| `ColumnSize`, `RowSize`, `LayerSizeSize` | Fixed extent per axis (the layer property really is `LayerSizeSize`) |
| `ColumnSpacing`, `RowSpacing`, `LayerSpacing` | Space between cells |
| `HorizontalAlign`/`VerticalAlign`/`DepthAlign` | Child alignment within its own cell |
| `GetChildAt(c, r, l = 0)`, `GetChildrenAt(...)` | First / all `Transform`s in a cell |

## `FlexalonGridCell`
`Cell` (`Vector3Int`) or `Column`/`Row`/`Layer` pins a child to a cell. Such a child is skipped by automatic ordering, so adding one shifts every later sibling by one cell. It is the only way to put several children in one cell (pieces on a board square).
