# Item Interaction & Decorators

Sources: M = manual https://forbiddenbyte.com/blog/osa-complete-manual/ (FAQ 2, 3, 5, 18, 22). A views holder outlives the item it displays: input must resolve *which* item at invocation time, and non-item elements must not live among Content's recycled children.

## Wiring input to a recycled row

One handler shared by every row, taking the views holder, reading `ItemIndex` when the event fires.

| Where | What belongs there |
|---|---|
| `CreateViewsHolder` | Subscribe listeners once per row, capturing the views holder |
| `UpdateViewsHolder` | Assign values to resolved views only: no subscription, no `GetComponent`, no add/remove items |
| Handler body | `vh.ItemIndex` then model lookup |
| `GridAdapter.OnCellViewsHolderCreated` | Grid equivalent |

```csharp
protected override MyItemViewsHolder CreateViewsHolder(int itemIndex)
{
    var vh = new MyItemViewsHolder();
    vh.Init(_Params.ItemPrefab, _Params.Content, itemIndex);
    // Capture vh, never itemIndex: this row shows another item after the first recycle.
    vh.button.onClick.AddListener(() => OnItemClicked(vh));
    return vh;
}
void OnItemClicked(MyItemViewsHolder vh) => OpenDetails(_Params.Data[vh.ItemIndex]);
```

Long-click: OSA ships a utility, exercised by `SelectionExample`. Existing MonoBehaviour view logic: resolve it in `CollectViews`, call it from `UpdateViewsHolder` (see [core-classes-and-lifecycle.md](core-classes-and-lifecycle.md)).

## `OSAContentDecorator` — headers, footers, inline ads

Lives under the **Viewport**, positioned by inset, never owned or recycled by the adapter.

| Case | Setup |
|---|---|
| Header scrolling with content | Child of Viewport (not Content) with `OSAContentDecorator`; defaults suffice |
| Element at a list position (ad) | Insert an **empty placeholder model** at that index, drive the decorator's inset from the placeholder's virtual position |
| Manual OSA init | Call the decorator's `Init()` **before** `OSA.Init()` |

Positioned case, all together: placeholder inserted before the first refresh; placeholder resized once to the decorator's size; inset re-synced on every scroll; `UpdateViewsHolder` skips the placeholder index.

```csharp
protected override void OnScrollPositionChanged(double normPos)
{
    base.OnScrollPositionChanged(normPos);
    if (GetItemsCount() <= _AdIndex) return; // items not set yet, or too few
    _Decorator.SetInset((float)GetItemVirtualInsetFromParentStart(_AdIndex));
}
```

Resize once with `RequestChangeItemSizeAndUpdateLayout(adIndex, adSize)`, size from the decorator's `RectTransform` (`rect.height` vertical, `rect.width` horizontal). Keep the decorator GameObject inactive at edit time and activate it in code before the first data set. If it does not fully cover the placeholder, disable the placeholder's children, not the item (OSA owns the item's active state). `SetInset()` exists after 5.1.2; if missing the package is older than 6.0.

## Sticky item

No built-in mode. Instantiate a second views holder yourself, parent it to the Viewport with item index `-1` so the adapter never manages it, and each frame clamp the real item's inset:

```csharp
void UpdateStickyOverlay(int targetItemIndex)
{
    var realVH = GetItemViewsHolderIfVisible(targetItemIndex);
    if (realVH == null) return;
    float size = _OverlayVH.root.rect.height;
    float inset = Mathf.Clamp(realVH.root.GetInsetFromParentTopEdge(_Params.Content), 0f, (float)GetViewportSize() - size);
    _OverlayVH.root.SetInsetAndSizeFromParentTopEdgeWithCurrentAnchors(inset, size);
}
```

`GetInsetFromParentTopEdge` and `SetInsetAndSizeFromParentTopEdgeWithCurrentAnchors` are OSA `RectTransform` extensions usable on any `RectTransform`.
