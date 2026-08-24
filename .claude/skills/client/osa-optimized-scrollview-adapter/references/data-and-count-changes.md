# Data & Count Changes — keeping the adapter and the dataset in agreement

Source: [OSA 6.0–7.0 Complete Manual](https://forbiddenbyte.com/blog/osa-complete-manual/) (Usage; Implementation; FAQ 5, 6, 23, 27), [Changelog](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/Changelog.txt).
Covers: SKILL.md §4 — **"Route every dataset change through the adapter's count-change API, never through the backing list alone"**.

The adapter deliberately knows nothing about your collection — only how
many items exist and, optionally, how big each one is. That is what lets it
display billions of items and lazily built models, and it is also why a
`List<T>.Add` alone changes nothing on screen: the count, the cached sizes
and the content size all still describe the old dataset. Every change is
therefore two things — the data, and the notification — or one DataHelper
call that does both.

## The count-change API

| Call | Effect | Use when | Source |
|---|---|---|---|
| `ResetItems(int itemsCount, bool contentPanelEndEdgeStationary = false, bool keepVelocity = false)` | Full refresh at the new count. Runs `CollectItemsSizes(..)`, then `CreateViewsHolder(int)` for each view that must exist, then `UpdateViewsHolder(vh)` per visible item | First population, and any wholesale replacement. **The only data path grids support** | [API](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/doc/43/html/2784edbc-f199-ce51-30a4-ff44e078ee44.htm) |
| `InsertItems(int index, int itemsCount, bool contentPanelEndEdgeStationary = false, bool keepVelocity = false)` | Incremental insert, preserving what is already built | Lists, whenever items are appended or spliced in — this is what keeps the view stable | [API](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/doc/43/html/1b7616c0-e4ec-2069-be09-f77fb68a6d19.htm) |
| `RemoveItems(int index, int itemsCount, bool contentPanelEndEdgeStationary = false, bool keepVelocity = false)` | Incremental removal | Lists, same reasoning | [API](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/doc/43/html/efbd3ee3-c745-b6ee-d0ea-094fa3e8522b.htm) |
| `ChangeItemsCount(ItemCountChangeMode changeMode, int itemsCount, int indexIfInsertingOrRemoving = -1, ...)` | The general form the three above delegate to; `ItemCountChangeMode` is `RESET`/`INSERT`/`REMOVE` | Driving a change whose mode is decided at runtime | [API](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/doc/43/html/bcd95e5c-107b-c47a-1601-1c25516d1288.htm) |
| `GetItemsCount()` | The count the adapter currently believes. **On a grid this returns cells, not groups** | Guarding any index-based work, including inside `OnScrollPositionChanged` before the first data set | [API](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/doc/43/html/961a900f-4a1b-2bba-ffc4-b4514ac511a3.htm) |

**Critical caveat**: `ResetItems()` also runs by itself whenever the
viewport's size changes — a mobile orientation change, a standalone window
resize. Anything you do in the reset path therefore happens at times you did
not schedule, so it must be idempotent and must not, for example, re-fetch
from the network.

Grids are the constraint to design around: they can only use `ResetItems`
for data manipulation, so a grid that must not lose its scroll position on
update needs the manual position-restore sequence below. See
[grid-and-table.md](grid-and-table.md).

## Keeping the end edge stationary

Insert and remove take a flag that decides which edge stays put. It is the
whole mechanism behind a chat log: new messages arrive at the bottom and
push older content up, rather than the viewport jumping.

| Case | What to pass | Source |
|---|---|---|
| Appending at the bottom of a reversed list | `contentPanelEndEdgeStationary: true` on the insert | [Manual FAQ 27](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| The same, with ContentSizeFitter items | Also pass it to `ScheduleComputeVisibilityTwinPass` — one without the other still shifts | [Manual FAQ 27](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| Unsure which edge should hold on a resize | `GuessShouldKeepEndStationaryOnResize(..)` (**v6.5.4+**) | [Changelog 6.5.4](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/Changelog.txt) |

**A reversed list is your list, reversed.** There is no adapter flag for
"first item at the bottom" — the vendor's position is that reversing the
backing collection is simpler than another layer of adapter complexity, and
that the flag above covers the insertion behaviour that actually matters.

## DataHelpers — when you don't need the two-step

`SimpleDataHelper<T>` and `LazyDataHelper<T>` wrap the collection and the
notification together, so `helper.Insert(...)` both mutates and tells the
adapter. They work through the adapter's abstract interface, so the same
helper serves a list or a grid.

| Helper | For | Source |
|---|---|---|
| `SimpleDataHelper<T>` | Models that already exist in memory | [Changelog](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/Changelog.txt) |
| `LazyDataHelper<T>` | Models built on demand — the large-dataset and download-as-needed case | [Changelog](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/Changelog.txt) |

Use the raw two-step only when you need what the separation buys: showing
an item whose model has **not been fully retrieved yet** — downloading one
at a time, or only when first shown. That is the reason the API is split at
all, so reaching for the helpers is the default and the split is the
exception. Loading the content itself belongs to `unity-addressables` or the
project's download layer.

**Critical caveat**: never add or remove items from inside
`UpdateViewsHolder`. It binds data to views and has no business deciding
what the dataset contains; the adapter is mid-layout when it runs.

## Preserving the scroll position across a change

Neither insert nor reset promises the same rows stay under the user's eye.
The supported shape is to record where the first visible item sits, change
the data, then scroll back to it.

```csharp
int countBefore = this.GetItemsCount();

// Index 0 here is the first VISIBLE item, not data index 0.
MyItemViewsHolder vh = this.GetItemViewsHolder(0);
int indexToScrollTo = vh.ItemIndex;
// Note the asymmetry: the "Real" form takes a RectTransform and returns float,
// while GetItemVirtualInsetFromParentStart(int) returns double.
float inset = this.GetItemRealInsetFromParentStart(vh.root);
double insetNorm = inset / this.GetViewportSize();

this.AddItemsToDataset();

// Items added at the START shift every existing index down by the number added.
int numberOfAdditionalItems = this.GetItemsCount() - countBefore;
if (this.AddedAtStart)
    indexToScrollTo += numberOfAdditionalItems;

this.ScrollTo(indexToScrollTo, (float)insetNorm, 0f);
```

`GetItemViewsHolder(0)` indexes the **visible** list, while
`vh.ItemIndex` is the data index — conflating the two is the usual bug
here. Grids need the extra step of converting between cell and group
indices; see [grid-and-table.md](grid-and-table.md).
