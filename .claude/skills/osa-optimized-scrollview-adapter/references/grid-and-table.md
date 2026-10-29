# Grid & Table

Sources: M = manual https://forbiddenbyte.com/blog/osa-complete-manual/ (FAQ 3, 16, 23); D = Demos manual https://docs.google.com/document/d/1FeIaLsvhHCRFQg8BaSBxyoOEYgzZjMoYkevv1l1eJ-0/edit (grid and TableView are documented there, built on the "Grid, horizontal layout, async items download" demo); A = API site (4.3). Namespace `Com.ForbiddenByte.OSA.CustomAdapters.GridView`.

A grid's views holder is a **group** (one row for vertical, one column for horizontal): the adapter recycles groups, not cells.

## Design consequences

| Subject | Fact |
|---|---|
| Override | Implement `protected abstract void UpdateCellViewsHolder(TCellVH)`, not `UpdateViewsHolder`; renaming a list adapter leaves the wrong method overridden |
| Data path | `ResetItems` only; `InsertItems`/`RemoveItems` are "not currently implemented for GridAdapters". To add items keeping position use the record-and-restore sequence in [data-and-count-changes.md](data-and-count-changes.md), or reconsider a list |
| Views holder | `GetItemViewsHolder(0)` returns `CellGroupViewsHolder<TCellVH>`, not a cell |
| Cell creation | Cells are created for you. `CellViewsHolder.Init` **throws `InvalidOperationException` by design**; use `InitWithExistingRootPrefab`. Post-creation hook: `protected virtual void OnCellViewsHolderCreated(TCellVH cellVH, CellGroupViewsHolder<TCellVH> cellGroup)` (wire listeners here) |
| Cells per group | Follows viewport size and changes on resize: read `CurrentUsedNumCellsPerGroup` on `GridParams` itself, not the nested `grid` config |
| Layout config | Lowercase `Params.grid`: `cellPrefab`, `MaxCellsPerGroup`, `spacingInGroup`, `alignmentOfCellsInGroup`, `groupPadding` (vendor casing) |
| Pool | `KeepItemsPoolOnLayoutRebuild` is ignored when the rebuild changes cells per group (M FAQ 16) |
| Cell cleanup | `OnBeforeRecycleOrDisableCellViewsHolder(TCellVH, int newItemIndex)` |

Types: `GridAdapter<TParams, TCellVH> : OSA<TParams, CellGroupViewsHolder<TCellVH>>` (`TParams : GridParams`, `TCellVH : CellViewsHolder, new()`), `GridParams : BaseParams`, `CellGroupViewsHolder<TCellVH> : BaseItemViewsHolder`, `CellViewsHolder : AbstractViewsHolder`, `GridParams.GridConfig`.

## Index translation

| Kind | Used by |
|---|---|
| **Group** index | `ScrollToGroup(int groupIndex, float normalizedOffsetFromViewportStart = 0f, float normalizedPositionOfItemPivotToUse = 0f)`, `SmoothScrollToGroup`, the holder from `GetItemViewsHolder` |
| **Cell** index | `ScrollTo`, `SmoothScrollTo` (both `override sealed` on `GridAdapter`), `GetItemsCount()`, every model lookup |

Group to cell is `groupIndex * CurrentUsedNumCellsPerGroup`, read live. Items added at the **start** add the new cell count on top; at the **end** scroll to the recorded group with `ScrollToGroup`:

```csharp
int cellIndexToScrollTo = groupIndexToScrollTo * _Params.CurrentUsedNumCellsPerGroup + numberOfAdditionalCells;
ScrollTo(cellIndexToScrollTo, (float)insetNorm, 0f);
```

`ForceUpdateCellViewsHolderIfVisible` (6.4.0+) redraws one cell; no published signature, confirm in the vendored source. Before 6.4.0 a cell refresh needs a full `ResetItems`.

## TableView

`TableAdapter` (5.0+) for genuinely tabular data (typed columns, headers, sorting). It has **no API page anywhere** and blog type names predate the rebrand. Read the `table_view` demo scene and scripts in the project; they are the specification. Demo scene inventory: https://forbiddenbyte.com/blog/osa-demo-scenes/
