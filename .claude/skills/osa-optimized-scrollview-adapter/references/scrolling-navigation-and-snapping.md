# Scrolling, Snapping & Scrollbars

Sources: M = manual https://forbiddenbyte.com/blog/osa-complete-manual/ (FAQ 4, 8, 12, 17, 19, 21, 26); C = changelog. Every scroll operation is against an item index, because only the adapter can resolve it to a position; writing `Content.localPosition` bypasses the visibility pass.

## Scrolling to an item

| Member | Use when |
|---|---|
| `ScrollTo(itemIndex, normalizedOffsetFromViewportStart, normalizedPositionOfItemPivotToUse)` | Immediate jump, restoring a position |
| `SmoothScrollTo(itemIndex, duration, normalizedOffsetFromViewportStart, normalizedPositionOfItemPivotToUse, onProgress, onDone, overrideCurrentScrollingAnimation)` | User-visible navigation; with duration 0 also the `ScrollTo` workaround for the `Awake` sizing bug |
| `OnScrollPositionChanged(double normPos)` | Keep something outside the list in sync (decorator inset, progress) |
| `Velocity` | Gate interaction while content moves |

The first normalized parameter says where in the viewport the anchor lands, the second which point of the item is anchored. Centring an item of known size:

```csharp
float viewportSize = (float)GetViewportSize();
float offset = ((viewportSize - itemSize) / viewportSize) / 2f;
SmoothScrollTo(itemIndex, duration, offset, 0f, null, null, true);
```

A size change cancels an in-progress `SmoothScrollTo` by default. For resize-and-scroll set `Params.Animation.Cancel.SmoothScroll.OnSizeChanges = false` ([variable-item-sizes.md](variable-item-sizes.md)).

## Scrollbars

`ScrollbarFixer8` is the OSA scrollbar (wizard links one). Main scrolling direction only; there is no cross-axis scrollbar.

## Snapping and paging

`Snapper8` on the OSA GameObject: there is always a snapped item.

| Member | Effect |
|---|---|
| `Snapper8.GetMiddleVH(out float)` | Snapped views holder, `null` when no items |
| `Snapper8.viewportSnapPivot01`, `itemSnapPivot01` | Pass to `SmoothScrollTo` so programmatic moves land where the snapper would |
| `Params.Snapper.SnappingStarted`, `SnappingEndedOrCancelled` | Events around a snap |
| `OSASnapperFocusedItemInfo` (5.1+) | Exposes the focused item; small enough to copy |

Next/previous page: `GetMiddleVH` then `ItemIndex + 1` then `SmoothScrollTo` with the snapper's pivots; guard "no items" and "past the end".

A PageView deliberately lets a fast swipe skip a page. To prevent it, disable input during the snap (needs **6.2.3+**; earlier versions have a bug):

```csharp
void OnSnappingStarted() { _Params.DragEnabled = _Params.ScrollEnabled = false; }
void OnSnappingEndedOrCancelled() { _Params.DragEnabled = _Params.ScrollEnabled = true; }
```

## Looping

Needs more items than the viewport shows. Minimum about `(minItemSize + spacing) / viewportSize + 1`.

| Approach | Cost |
|---|---|
| Duplicate models until the count exceeds the minimum | Memory and index arithmetic against the real dataset |
| Toggle looping on count change by content-to-viewport ratio (from `IScrollRectProxy` extensions) | Pick a threshold that always keeps one item out of view (e.g. off below 1.3x) |

Since 6.4.0, looping `SmoothScrollTo` takes the shortest path.

## Both directions (not supported out of the box)

| Approach | Shape |
|---|---|
| Manual increments | Adjust Content `localPosition.x` from two buttons |
| Parent `ScrollRect` for the cross axis | Classic horizontal `ScrollRect` whose content is OSA, OSA width fixed at edit time, normal `Scrollbar`, `ForwardDragToParents` on, no Viewport between. Only option with a real cross-axis scrollbar; OSA width stops being responsive |
| Draggable edge | Model on `EdgeDragger` from the ContentSizeFitter and horizontal-async demos (demo quality) |
