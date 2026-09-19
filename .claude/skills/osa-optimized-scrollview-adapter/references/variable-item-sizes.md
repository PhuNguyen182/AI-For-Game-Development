# Variable Item Sizes — the three size strategies and runtime resizing

Source: [OSA 6.0–7.0 Complete Manual](https://forbiddenbyte.com/blog/osa-complete-manual/) (Implementation; FAQ 10, 11, 12, 27, 28), [Changelog](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/Changelog.txt).
Covers: SKILL.md §4 — **"Decide the item-size strategy before the item prefab is authored"**.

"Size" always means the extent along the scrolling axis — height for a
vertical scroll view, width for a horizontal one. The adapter must know
every item's size, including items with no GameObject, in order to place
the scrollbar and resolve a `ScrollTo`. The three ways to tell it are not
interchangeable, and the choice constrains the prefab: one of them forbids
a `ContentSizeFitter`, one requires it.

## Choosing the strategy

| Strategy | Mechanism | Choose when | Source |
|---|---|---|---|
| Uniform | `Params.DefaultItemSize` — one size for every item. With a prefab-carrying params class, the prefab's own size sets it | Rows genuinely match. This is the cheapest path and the default; do not leave it for a list whose rows differ | [Manual FAQ 10](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| Precomputed | Override `CollectItemsSizes()` and supply sizes you already know | Sizes are derivable from the model without laying anything out, **and** the set is small enough to precompute. The vendor explicitly warns this is neither the only nor the recommended route on large datasets | [Manual — Implementation](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| Content-driven | A `ContentSizeFitter` on the item prefab plus `ScheduleComputeVisibilityTwinPass()` called from `UpdateViewsHolder` | A row's size is knowable only after its content is bound — wrapped text of unknown length, a variable child count | [Manual FAQ 11](https://forbiddenbyte.com/blog/osa-complete-manual/) |

`CollectItemsSizes()` runs as part of a count change, before
`CreateViewsHolder`/`UpdateViewsHolder` — see
[data-and-count-changes.md](data-and-count-changes.md) for where it sits in
that sequence.

**Critical caveat**: the most common "`CollectItemsSizes` doesn't work"
report is a params class that carries a prefab, because such a class exists
precisely to let the prefab drive `DefaultItemSize` — and it then overrides
what you collected. Either make the prefab smaller than any real item, or
disable that behaviour via `PrefabControlsDefaultItemSize` (**v5.1+**), or
drop to the plain params base and hold the prefab reference yourself for use
in `CreateViewsHolder`.

## The ContentSizeFitter twin pass

`ScheduleComputeVisibilityTwinPass()` is what makes a fitter and the adapter
cooperate instead of fighting: it tells the adapter that this item's size is
not yet final, so it lays the item out, reads the resulting size, and runs a
second visibility pass with the real number. Without it, the adapter and the
fitter both write the size and the list overlaps or mis-scrolls.

Two consequences follow, and both are load-bearing:

| Consequence | Detail | Source |
|---|---|---|
| `UpdateViewsHolder` can no longer be force-called to redraw a row | The twin pass is scheduled from inside it, so calling it manually does not do what it does during a real pass. Use `ForceUpdateViewsHolderIfVisible` (**v5.1+**) instead, which handles the single-item size rebuild too | [Manual FAQ 11](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| Prefab authoring is constrained | Text overflow must be `Overflow`, not `Truncate`, and any child GameObject's edit-time active state must match what the first frame after init sets — see [known-issues-and-platform-caveats.md](known-issues-and-platform-caveats.md) | [Manual — Known issues](https://forbiddenbyte.com/blog/osa-complete-manual/) |

When items are inserted at the end and existing rows should hold their
on-screen position (the chat-log case), pass the keep-end-edge-stationary
flag to `ScheduleComputeVisibilityTwinPass` as well as to the insert itself —
one without the other still shifts the view.

## Redrawing a row whose model changed

`UpdateViewsHolder` normally fires only when a row becomes visible or is
created, so a model edited in place needs an explicit push.

| Situation | Call | Source |
|---|---|---|
| Not using the twin pass | Call `UpdateViewsHolder` directly, or better, put an `UpdateViews` method on the views holder and call that | [Manual FAQ 11](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| Using the twin pass, single row | The views-holder method above, then `ForceRebuildViewsHolderAndUpdateSize` on it | [Manual FAQ 11](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| Any case, v5.1+ | `ForceUpdateViewsHolderIfVisible(itemIndex)` — covers both, including the twin-pass size rebuild | [Manual FAQ 11](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| All visible rows at once, v6.1+ | `ForceUpdateVisibleItems()` | [Changelog 6.1.0](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/Changelog.txt) |
| Direct layout rebuild, v6.0.1+ | `ForceRebuildLayoutNow()` | [Changelog 6.0.1](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/Changelog.txt) |

## Changing one item's size at runtime

`RequestChangeItemSizeAndUpdateLayout(itemIndex, requestedSize)` sets a
single item's size and relays out around it. This is the call behind a
decorator placeholder sized to its content
([item-interaction-and-decorators.md](item-interaction-and-decorators.md))
and behind any non-animated expand/collapse.

For an **animated** expand that also centres the item, two animations must
run at once, and by default they do not:

| Step | Why | Source |
|---|---|---|
| Set `Params.Animation.Cancel.SmoothScroll.OnSizeChanges` to `false` | Otherwise the size change cancels the in-flight `SmoothScrollTo` and the item resizes without ever centring | [Manual FAQ 12](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| Drive the resize through `ExpandCollapseAnimationState` | **Demo code, not shipping API** — it lives in `Com.ForbiddenByte.OSA.Demos.Common`, so copy it into your own code rather than referencing the demo assembly. `MainExample.cs` shows it in use, and the model needs the extra fields that example adds | [Manual FAQ 12](https://forbiddenbyte.com/blog/osa-complete-manual/), [API](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/doc/43/html/3ede4955-73bb-f8bc-4abf-2d0435dc5578.htm) |
| Compute the centring offset from the item's *new* size | Half the leftover viewport space, normalized — see [scrolling-navigation-and-snapping.md](scrolling-navigation-and-snapping.md) | [Manual FAQ 12](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| Use the same duration for both | They are two independent animations; different durations desynchronise visibly | [Manual FAQ 12](https://forbiddenbyte.com/blog/osa-complete-manual/) |

This requires **v5.1 or newer**.

## Resizing the scroll view itself

A viewport size change triggers a full refresh — orientation changes on
mobile, window resizing on standalone. To preserve item positions and
velocity across it, enable `Params.optimization.ResponsiveOnScrollViewSizeChange`;
it is **off by default** because the default handling already suffices
unless items have dynamic sizes, which is exactly the case this file
covers. See [pooling-and-performance.md](pooling-and-performance.md).
