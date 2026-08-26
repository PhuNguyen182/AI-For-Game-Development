# Grid & Table — cell groups, index translation, and the ResetItems constraint

Source: [OSA 6.0–7.0 Complete Manual](https://forbiddenbyte.com/blog/osa-complete-manual/) (Grid; Table; Usage; FAQ 3, 16, 23), [OSA Demos manual](https://docs.google.com/document/d/1FeIaLsvhHCRFQg8BaSBxyoOEYgzZjMoYkevv1l1eJ-0/edit#bookmark=id.w12qnswihdje), [Changelog](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/Changelog.txt).
Covers: SKILL.md §4 — **"Reach for `GridAdapter` only when the layout is genuinely a cell grid, and accept its data-path constraint up front"**.

A grid is not a list with more columns. Its views holder is a **group** — one
row (vertical scroll view) or one column (horizontal) of cells — so the
adapter recycles groups, not cells, and every index you hand it needs to be
the right kind. This file routes to the authoritative material and carries
the facts that decide a design; the vendor documents grids in the Demos
manual rather than the main one, built around the "Grid, horizontal layout,
async items download" demo, and that demo is where the fuller answers live.

## What a grid changes about the design

| Subject | What it decides | Source |
|---|---|---|
| **The override you implement is a different method** | Not `UpdateViewsHolder` — grids require `protected abstract void UpdateCellViewsHolder(TCellVH viewsHolder)`, documented as "the only important callback for inheritors". Porting a list adapter by renaming the class silently leaves the wrong method overridden | [API — GridAdapter](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/doc/43/html/6cb1a917-baf6-6e3e-0f9e-a93b273dfea6.htm) |
| `ResetItems` is the only data path | **Grids cannot insert or remove incrementally** — `InsertItems` and `RemoveItems` are documented "not currently implemented for GridAdapters". If the screen must add items without losing the scroll position, budget for the manual record-and-restore sequence in [data-and-count-changes.md](data-and-count-changes.md) — or reconsider whether a list would serve | [API — GridAdapter](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/doc/43/html/efc5ae65-bb64-617e-7590-7eff0bbda92a.htm) |
| The views holder is a cell **group** | `GetItemViewsHolder(0)` returns a `CellGroupViewsHolder\<TCellVH\>` — a row or column of cells, not one cell. Anything written against a list's views holder needs rethinking, not porting | [Manual FAQ 23](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| Cells are created for you | You do not instantiate cells in `CreateViewsHolder`. `CellViewsHolder.Init` **throws `InvalidOperationException` by design** — the documented replacement is `InitWithExistingRootPrefab`. To run code right after a cell exists, override `protected virtual void OnCellViewsHolderCreated(TCellVH cellVH, CellGroupViewsHolder\<TCellVH\> cellGroup)` | [API — CellViewsHolder](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/doc/43/html/c2a4fbba-f5b9-524c-abd5-00bfb3c98eeb.htm), [API — OnCellViewsHolderCreated](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/doc/43/html/69ebb0ec-295a-85b4-0ec7-ed1275f7991f.htm) |
| Cells per group is dynamic | It follows the viewport width/height, so it changes on resize. Read `CurrentUsedNumCellsPerGroup` off the params rather than assuming your authored column count holds — note it lives on `GridParams` itself, not on the nested `grid` config | [API — CurrentUsedNumCellsPerGroup](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/doc/43/html/fe7b7263-1f54-ac8b-9c71-944a159d0ab9.htm) |
| Cell layout is configured on `Params.grid` | The nested config field (lowercase `grid`) carries `cellPrefab`, `MaxCellsPerGroup`, `spacingInGroup`, `alignmentOfCellsInGroup` and `groupPadding` — mixed casing is the vendor's, not a typo here | [API — GridParams](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/doc/43/html/4155448f-2d78-4a25-9c3f-0d1b43a4bffc.htm) |
| Pool persistence is weaker | Grids ignore `KeepItemsPoolOnLayoutRebuild` when the rebuild produces a different number of cells per group | [Manual FAQ 16](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| The wizard has a separate template | List and Grid templates generate different code, and their example item prefabs differ — generate the right one rather than adapting a list prefab | [Manual — OSA wizard](https://forbiddenbyte.com/blog/osa-complete-manual/) |

## Index translation

Two index spaces coexist, and mixing them is the recurring grid bug.

| Index kind | Used by | Source |
|---|---|---|
| **Group** index — which row/column | `ScrollToGroup`, `SmoothScrollToGroup`, and the views holder returned by `GetItemViewsHolder` | [API — ScrollToGroup](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/doc/43/html/c1002148-ab7e-5ecd-c1e4-5389d873f299.htm) |
| **Cell** index — which item in the dataset | `ScrollTo`, `SmoothScrollTo`, `GetItemsCount()` (which returns *cells*, not groups), and every model lookup | [API — ScrollTo](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/doc/43/html/115432be-fcc2-17d1-2c0a-ac50836e500f.htm) |

`GridAdapter` presents a **cell-indexed façade over a group-indexed base**:
`ScrollTo` and `SmoothScrollTo` are `override sealed` on it — you cannot
re-override them — and `ChangeItemsCount` converts a cell count to a group
count before delegating. So every public number you pass is a cell number,
and only the `…Group` variants speak in groups.

Converting group → cell is `groupIndex * CurrentUsedNumCellsPerGroup`, read
live rather than as a constant. When items are added at the **start**, the
number of new cells is added on top of that before scrolling back:

```csharp
int cellIndexToScrollTo = (groupIndexToScrollTo * this._Params.CurrentUsedNumCellsPerGroup)
                          + numberOfAdditionalCells;

this.ScrollTo(cellIndexToScrollTo, (float)insetNorm, 0f);
```

When items are added at the **end**, no shift is needed — scroll to the
recorded group directly with `ScrollToGroup`.

## Redrawing a single cell

`ForceUpdateCellViewsHolderIfVisible` was added to `GridAdapter` in
**v6.4.0** — the grid counterpart of the list's
`ForceUpdateViewsHolderIfVisible` covered in
[variable-item-sizes.md](variable-item-sizes.md). On an older 6.x, a cell's
refresh has to go through a full `ResetItems`.

## TableView

A separate custom adapter layered on the same core, shipped in **v5.0** —
the changelog calls `TableAdapter` "the biggest sub-component of the OSA
package". Choose it when the requirement is genuinely tabular — typed
columns, headers, sorting — rather than a grid of uniform cells.

**Critical caveat**: TableView has **no generated API page anywhere**,
because it shipped one release after the last doc build (see
[root-links.md](root-links.md)). Type names quoted in blog articles predate
the rebrand and use the old `Com.TheFallenGames.OSA` root. This skill
therefore distils none of its API on purpose: read the `table_view` demo
scene and its scripts in the project, which are the actual specification.

## Where to read further

| Need | Go to | Source |
|---|---|---|
| Implementing a grid end to end | The "Grid, horizontal layout, async items download" demo and its write-up — it carries most grid questions, including the common ones | [Demos manual](https://docs.google.com/document/d/1FeIaLsvhHCRFQg8BaSBxyoOEYgzZjMoYkevv1l1eJ-0/edit#bookmark=id.w12qnswihdje) |
| TableView basics | The TableView section of the same manual | [Demos manual](https://docs.google.com/document/d/1FeIaLsvhHCRFQg8BaSBxyoOEYgzZjMoYkevv1l1eJ-0/edit#bookmark=id.w12qnswihdje) |
| The full demo-scene inventory | Demo scenes introduction | [OSA 5.0–7.0 Demo Scenes Introduction](https://forbiddenbyte.com/blog/osa-demo-scenes/) |

## API index

The five types in `Com.ForbiddenByte.OSA.CustomAdapters.GridView` — that is
the whole namespace.

| Declaration | Source |
|---|---|
| `public abstract class GridAdapter\<TParams, TCellVH\> : OSA\<TParams, CellGroupViewsHolder\<TCellVH\>\>` where `TParams : GridParams` and `TCellVH : CellViewsHolder, new()` | [API](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/doc/43/html/efc5ae65-bb64-617e-7590-7eff0bbda92a.htm) |
| `public class GridParams : BaseParams` — carries the `grid` config field and `CurrentUsedNumCellsPerGroup` | [API](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/doc/43/html/4155448f-2d78-4a25-9c3f-0d1b43a4bffc.htm) |
| `public class CellGroupViewsHolder\<TCellVH\> : BaseItemViewsHolder` | [API](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/doc/43/html/d4a4ffc3-32c9-e568-b9f7-a601e229273d.htm) |
| `public abstract class CellViewsHolder : AbstractViewsHolder` | [API](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/doc/43/html/c2a4fbba-f5b9-524c-abd5-00bfb3c98eeb.htm) |
| `GridParams.GridConfig` — the nested cell-layout config | [API](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/doc/43/html/31400f25-92ff-b543-1b48-113302306c4b.htm) |
| `protected abstract void UpdateCellViewsHolder(TCellVH viewsHolder)` | [API](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/doc/43/html/6cb1a917-baf6-6e3e-0f9e-a93b273dfea6.htm) |
| `protected virtual void OnCellViewsHolderCreated(TCellVH cellVH, CellGroupViewsHolder\<TCellVH\> cellGroup)` | [API](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/doc/43/html/69ebb0ec-295a-85b4-0ec7-ed1275f7991f.htm) |
| `protected virtual void OnBeforeRecycleOrDisableCellViewsHolder(TCellVH viewsHolder, int newItemIndex)` | [API](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/doc/43/html/1c9c10ae-f810-b279-724d-cc1eae1e12d1.htm) |
| `public virtual void ScrollToGroup(int groupIndex, float normalizedOffsetFromViewportStart = 0f, float normalizedPositionOfItemPivotToUse = 0f)`, plus `SmoothScrollToGroup` | [API](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/doc/43/html/c1002148-ab7e-5ecd-c1e4-5389d873f299.htm) |
| `ForceUpdateCellViewsHolderIfVisible` — **v6.4.0+, no published signature**; confirm against the vendored source | [Changelog](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/Changelog.txt) |
