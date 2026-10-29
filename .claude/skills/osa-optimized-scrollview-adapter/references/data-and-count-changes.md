# Data & Count Changes

Sources: M = manual https://forbiddenbyte.com/blog/osa-complete-manual/ (Usage, Implementation, FAQ 5, 6, 23, 27); C = changelog.

The adapter knows only the item count (and optionally sizes), so a `List<T>.Add` alone changes nothing on screen: count, cached sizes and content size still describe the old dataset. Every change is data plus notification, or one DataHelper call doing both.

| Call | Effect | Use when |
|---|---|---|
| `ResetItems(int itemsCount, bool contentPanelEndEdgeStationary = false, bool keepVelocity = false)` | Full refresh: `CollectItemsSizes`, then `CreateViewsHolder` per needed view, then `UpdateViewsHolder` per visible item | First population, wholesale replacement. **Only path grids support** |
| `InsertItems(int index, int itemsCount, bool contentPanelEndEdgeStationary = false, bool keepVelocity = false)` | Incremental, preserves built rows | Lists: append/splice, keeps the view stable |
| `RemoveItems(int index, int itemsCount, ...same flags)` | Incremental removal | Lists |
| `ChangeItemsCount(ItemCountChangeMode, int itemsCount, int indexIfInsertingOrRemoving = -1, ...)` | General form of the three | Mode decided at runtime |
| `GetItemsCount()` | Count the adapter believes; on a grid it returns **cells**, not groups | Guard index work, including `OnScrollPositionChanged` before the first data set |

`ResetItems()` also runs by itself when the viewport size changes (mobile rotation, window resize), so reset-path code must be idempotent and must not, for example, re-fetch from the network.

## Keeping the end edge stationary

| Case | Pass |
|---|---|
| Appending at the bottom of a reversed list (chat log) | `contentPanelEndEdgeStationary: true` on the insert (M FAQ 27) |
| Same, with ContentSizeFitter items | Also pass it to `ScheduleComputeVisibilityTwinPass`; one without the other still shifts |
| Unsure which edge holds on resize | `GuessShouldKeepEndStationaryOnResize(..)` (6.5.4+) |

There is no "first item at the bottom" flag: reverse the backing collection yourself.

## DataHelpers

`SimpleDataHelper<T>` (models in memory) and `LazyDataHelper<T>` (models built on demand) wrap collection and notification, so `helper.Insert(...)` does both; they work through `IOSA`, so the same helper serves list or grid. Use the raw two-step only to show an item whose model is not fully retrieved yet. Content loading belongs to `unity-addressables` or the download layer.

## Preserving scroll position across a change

Neither insert nor reset keeps the same rows under the user's eye. Record the first visible item, change data, scroll back:

```csharp
int countBefore = GetItemsCount();
// Index 0 is the first VISIBLE item, not data index 0.
MyItemViewsHolder vh = GetItemViewsHolder(0);
int indexToScrollTo = vh.ItemIndex;
// "Real" form takes a RectTransform and returns float; the "Virtual" form takes int and returns double.
float inset = GetItemRealInsetFromParentStart(vh.root);
double insetNorm = inset / GetViewportSize();

AddItemsToDataset();

// Items added at the START shift every existing index by the number added.
if (AddedAtStart) indexToScrollTo += GetItemsCount() - countBefore;
ScrollTo(indexToScrollTo, (float)insetNorm, 0f);
```

`GetItemViewsHolder(0)` indexes the visible list; `vh.ItemIndex` is the data index. Grids add a cell/group conversion: see [grid-and-table.md](grid-and-table.md).
