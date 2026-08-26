# Scrolling, Snapping & Scrollbars — moving the viewport through the adapter

Source: [OSA 6.0–7.0 Complete Manual](https://forbiddenbyte.com/blog/osa-complete-manual/) (FAQ 4, 8, 12, 17, 19, 21, 26), [Changelog](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/Changelog.txt), [OSA API docs](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/doc/43/html/303f106d-29ab-b975-b0e1-9120154c4aee.htm).
Covers: SKILL.md §4 — **"Move the viewport only through the adapter's own scroll API"**.

The adapter owns a virtual position for every item, including ones that
have no GameObject right now. Every scroll operation is expressed against
an **item index**, not a pixel offset, because only the adapter can resolve
one into the other. Writing `Content.localPosition` yourself bypasses the
visibility pass that decides which rows exist.

## Scrolling to an item

| Member | Effect | Use when | Source |
|---|---|---|---|
| `ScrollTo(itemIndex, normalizedOffsetFromViewportStart, normalizedPositionOfItemPivotToUse)` | Jumps immediately | Restoring a position, or any non-animated jump | [Manual FAQ 23](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| `SmoothScrollTo(itemIndex, duration, normalizedOffsetFromViewportStart, normalizedPositionOfItemPivotToUse, onProgress, onDone, overrideCurrentScrollingAnimation)` | Animates over `duration`, with optional progress/completion callbacks | Any user-visible navigation; also the workaround for the `Awake` sizing bug, called with duration 0 | [Manual FAQ 12, 19](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| `OnScrollPositionChanged(double normPos)` | Overridable hook fired as the normalized position changes | Keeping something outside the list in sync with scroll — a decorator inset, a progress indicator | [Manual FAQ 18B](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| `Velocity` | Current scrolling velocity | Gating interaction while the content is still moving | [Manual FAQ 21](https://forbiddenbyte.com/blog/osa-complete-manual/) |

The two normalized parameters are what centre an item rather than merely
bringing it into view: the first says where in the viewport the anchor
lands, the second which point of the item is anchored. To centre an item of
a known size, compute the offset from the leftover viewport space.

```csharp
void ScrollItemIntoCentre(int itemIndex, float itemSize, float duration)
{
    float viewportSize = (float)this.GetViewportSize();
    float normalizedOffsetFromViewportStart = ((viewportSize - itemSize) / viewportSize) / 2f;

    this.SmoothScrollTo(itemIndex, duration, normalizedOffsetFromViewportStart, 0f, null, null, true);
}
```

**Critical caveat**: a `SmoothScrollTo` in progress is cancelled by a size
change by default. To resize an item *and* scroll to it simultaneously — the
expand-and-centre gesture — set
`Params.Animation.Cancel.SmoothScroll.OnSizeChanges` to `false` first, or
one animation kills the other. Drive the resize itself through
`ExpandCollapseAnimationState`, per [variable-item-sizes.md](variable-item-sizes.md).

## Scrollbars

`ScrollbarFixer8` is the scrollbar solution for OSA — a plain uGUI
`Scrollbar` bound to the disabled `ScrollRect` does nothing, because OSA
replaced it. The OSA wizard generates and links one automatically, and
detects an existing scrollbar if one is present.

**It only works in the main scrolling direction.** There is no built-in
cross-axis scrollbar; see the cross-axis section below.

## Snapping and paging

`Snapper8` is a component added to the OSA GameObject. With it there is
always a snapped ("focused") item — the gallery/page-view pattern.

| Member | Effect | Source |
|---|---|---|
| `Snapper8.GetMiddleVH(out float)` | The currently snapped views holder, or `null` when there are no items | [Manual FAQ 19](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| `Snapper8.viewportSnapPivot01`, `Snapper8.itemSnapPivot01` | The configured snap pivots — pass these through to `SmoothScrollTo` so programmatic navigation lands where the snapper would have | [Manual FAQ 19](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| `Params.Snapper.SnappingStarted`, `Params.Snapper.SnappingEndedOrCancelled` | Events around a snap animation | [Manual FAQ 26](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| `OSASnapperFocusedItemInfo` | Utility script exposing the focused item, added in 5.1 — small enough to copy into an adapter instead | [Manual FAQ 17](https://forbiddenbyte.com/blog/osa-complete-manual/) |

Programmatic next/previous page is `GetMiddleVH` → `ItemIndex + 1` →
`SmoothScrollTo` with the snapper's own pivots, guarding both the "no items"
and "past the end" cases.

**A PageView deliberately allows skipping a page on a fast swipe.** That is
a UX choice, not a bug — swipe momentum compounds the way a regular
`ScrollRect`'s does. To disable it, turn off dragging and scrolling for the
duration of the snap:

```csharp
void OnSnappingStarted()
{
    this._Params.DragEnabled = this._Params.ScrollEnabled = false;
}

void OnSnappingEndedOrCancelled()
{
    this._Params.DragEnabled = this._Params.ScrollEnabled = true;
}
```

This requires **v6.2.3 or newer** — an earlier version has a bug that breaks it.

## Looping

Looping needs more items than the viewport can show at once, or there is
nothing to wrap around to.

| Approach | What it costs | Source |
|---|---|---|
| Duplicate the models until the count exceeds the minimum shown | Memory, and index arithmetic against the real dataset. Roughly `(minItemSize + spacing) / viewportSize + 1` items are needed at minimum | [Manual FAQ 4](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| Enable/disable looping on count change, by content-to-viewport ratio | A threshold to choose — pick one that always keeps at least one item out of view (e.g. disable looping below 1.3×). The ratio comes from the extensions in `IScrollRectProxy` | [Manual FAQ 4](https://forbiddenbyte.com/blog/osa-complete-manual/) |

Since **6.4.0**, `SmoothScrollTo` takes the shortest path when looping is
enabled, instead of scrolling the long way round.

## Scrolling in both directions

Not supported out of the box. In rough order of increasing fidelity:

| Approach | Shape | Source |
|---|---|---|
| Manual increments | Adjust Content's `localPosition.x` yourself from two arrow buttons | [Manual FAQ 8](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| Parent `ScrollRect` for the cross axis | Wrap OSA in a classic horizontal `ScrollRect` whose content *is* OSA, with OSA's width fixed at edit time, a normal `Scrollbar`, `ForwardDragToParents` enabled, and no Viewport between the two | [Manual FAQ 8](https://forbiddenbyte.com/blog/osa-complete-manual/), [Unity ScrollRect](https://docs.unity3d.com/Manual/script-ScrollRect.html) |
| Draggable edge | Model on the `EdgeDragger` script from the ContentSizeFitter and horizontal-async demo scenes — demo-quality code, but close to a real solution | [Manual FAQ 8](https://forbiddenbyte.com/blog/osa-complete-manual/) |

The parent-`ScrollRect` approach is the only one that keeps a real scrollbar
on the cross axis; the trade is that OSA's own width stops being responsive.
