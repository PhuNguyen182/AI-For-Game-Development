# Variable Item Sizes

Sources: M = manual https://forbiddenbyte.com/blog/osa-complete-manual/ (Implementation, FAQ 10, 11, 12, 27, 28); C = changelog. "Size" is the extent along the scroll axis. The adapter needs every item's size, including items with no GameObject.

## Strategies

| Strategy | Mechanism | Choose when |
|---|---|---|
| Uniform | `Params.DefaultItemSize`; with a prefab-carrying params class the prefab's size sets it | Rows match. Cheapest and default |
| Precomputed | Override `CollectItemsSizes()` | Sizes derive from the model without layout **and** the set is small; the vendor does not recommend it on large datasets |
| Content-driven | `ContentSizeFitter` on the prefab plus `ScheduleComputeVisibilityTwinPass()` from `UpdateViewsHolder` | Size is known only after content is bound (wrapped text, variable child count) |

`CollectItemsSizes()` runs during a count change, before `CreateViewsHolder`.

"`CollectItemsSizes` doesn't work" is usually a prefab-carrying params class overriding the collected sizes. Make the prefab smaller than any real item, disable it via `PrefabControlsDefaultItemSize` (5.1+), or use the plain params base and hold the prefab yourself.

## ContentSizeFitter twin pass

`ScheduleComputeVisibilityTwinPass()` tells the adapter the item size is not final: it lays the item out, reads the size, runs a second visibility pass. Without it the adapter and fitter both write the size and the list overlaps or mis-scrolls.

- `UpdateViewsHolder` can no longer be force-called to redraw a row (the twin pass is scheduled from inside it). Use `ForceUpdateViewsHolderIfVisible(itemIndex)` (5.1+).
- Prefab authoring: Text overflow must be `Overflow` not `Truncate`, and child edit-time active state must match the first frame after init (see [known-issues-and-platform-caveats.md](known-issues-and-platform-caveats.md)).
- Inserting at the end while holding position (chat log): pass the keep-end-edge-stationary flag to the twin pass as well as to the insert.

## Redrawing a row whose model changed

| Situation | Call |
|---|---|
| No twin pass | `UpdateViewsHolder` directly, or an `UpdateViews` method on the views holder |
| Twin pass, single row | That method, then `ForceRebuildViewsHolderAndUpdateSize` |
| Any case, 5.1+ | `ForceUpdateViewsHolderIfVisible(itemIndex)` |
| All visible, 6.1+ | `ForceUpdateVisibleItems()` |
| Direct layout rebuild, 6.0.1+ | `ForceRebuildLayoutNow()` |

## Changing one item's size at runtime

`RequestChangeItemSizeAndUpdateLayout(itemIndex, requestedSize)` sets one size and relays out; behind decorator placeholders ([item-interaction-and-decorators.md](item-interaction-and-decorators.md)) and non-animated expand/collapse.

Animated expand that also centres (5.1+):
1. Set `Params.Animation.Cancel.SmoothScroll.OnSizeChanges` to `false`, or the size change cancels the in-flight `SmoothScrollTo`.
2. Drive the resize through `ExpandCollapseAnimationState`: **demo code** in `Com.ForbiddenByte.OSA.Demos.Common`; copy it, do not reference the demo assembly. `MainExample.cs` shows use; the model needs the example's extra fields.
3. Compute the centring offset from the item's *new* size (see [scrolling-navigation-and-snapping.md](scrolling-navigation-and-snapping.md)).
4. Use the same duration for both animations.

## Resizing the scroll view

A viewport size change triggers a full refresh. To keep positions/velocity enable `Params.optimization.ResponsiveOnScrollViewSizeChange` (off by default; needed with dynamic item sizes).
