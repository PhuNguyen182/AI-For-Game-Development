# Item Interaction & Decorators — input on recycled rows, and non-item chrome

Source: [OSA 6.0–7.0 Complete Manual](https://forbiddenbyte.com/blog/osa-complete-manual/) (FAQ 2, 3, 5, 18, 22), [OSA API docs](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/doc/43/html/303f106d-29ab-b975-b0e1-9120154c4aee.htm).
Covers: SKILL.md §4 — **"Keep `UpdateViewsHolder` a pure data-to-view bind"**, **"Hang anything that is not an item off `OSAContentDecorator` under the Viewport, not as a child of Content"**.

Two problems that both come from the same fact: a views holder outlives the
item it displays. Input wired to a row must resolve *which* item at
invocation time, and anything that is not an item must not live among the
recycled children of Content at all. Building the Canvas hierarchy these
sit in belongs to `ugui`; tweening a decorator belongs to
`dotween-tweening`/`litmotion-tweening`.

- [Wiring input to a recycled row](#wiring-input-to-a-recycled-row)
- [Reusing an existing MonoBehaviour as the row's view logic](#reusing-an-existing-monobehaviour-as-the-rows-view-logic)
- [`OSAContentDecorator` — headers, footers, inline ads](#osacontentdecorator--headers-footers-inline-ads)
- [Sticky item that never leaves the screen](#sticky-item-that-never-leaves-the-screen)

## Wiring input to a recycled row

The rule is one handler shared by every row, taking the views holder — never
the item index — and reading `ItemIndex` when the event actually fires.

| Where | What belongs there | Source |
|---|---|---|
| `CreateViewsHolder` | Subscribe listeners, once per instantiated row, capturing the views holder | [Manual FAQ 3](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| `UpdateViewsHolder` | Assign values to already-resolved views. Nothing else — no subscription, no `GetComponent`, no item add/remove | [Manual FAQ 3, 5](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| The handler body | `vh.ItemIndex` → look the model up in your dataset | [Manual FAQ 3](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| `GridAdapter.OnCellViewsHolderCreated` | The grid equivalent — cells are created for you, so this is the hook that runs right after a cell exists | [Manual FAQ 3](https://forbiddenbyte.com/blog/osa-complete-manual/) |

```csharp
protected override MyItemViewsHolder CreateViewsHolder(int itemIndex)
{
    MyItemViewsHolder vh = new MyItemViewsHolder();
    vh.Init(this._Params.ItemPrefab, this._Params.Content, itemIndex);

    // Capture the views holder, never itemIndex: this row will show a
    // different item after the first recycle.
    vh.button.onClick.AddListener(() => this.OnItemClicked(vh));
    return vh;
}

void OnItemClicked(MyItemViewsHolder vh)
{
    MyItemModel model = this._Params.Data[vh.ItemIndex];
    this.OpenDetails(model);
}
```

Long-click follows the same shape; OSA ships a utility for it, exercised by
the `SelectionExample` script and its scene.

**Critical caveat**: `UpdateViewsHolder` must never add or remove items. It
binds data and nothing more — the adapter is mid-layout when it runs, and
the vendor states outright that whatever you want there is achievable
without a count change from inside it.

## Reusing an existing MonoBehaviour as the row's view logic

The views holder deliberately is **not** a MonoBehaviour — the prefab may
carry any number of components, and keeping the holder a plain C# object
avoids paying for that. If view-binding logic already lives in a
MonoBehaviour, resolve it once in `CollectViews` and call it from
`UpdateViewsHolder`.

```csharp
class MyVH : BaseItemViewsHolder
{
    public MyExistingBehaviour behaviour;

    public override void CollectViews()
    {
        base.CollectViews();
        this.behaviour = this.root.GetComponent<MyExistingBehaviour>();
    }
}
```

`CollectViews` runs once per instantiated row, so this is the only place a
`GetComponent` belongs — `performance-and-algorithms.md`'s Scripting & GC
section forbids it in the per-recycle path.

## `OSAContentDecorator` — headers, footers, inline ads

Content's children are the recycle pool. A decorator lives under the
**Viewport** instead and is positioned by inset, so the adapter never owns
or recycles it.

| Case | Setup | Source |
|---|---|---|
| Header that scrolls with the content | Add the element as a child of Viewport (not Content) and attach `OSAContentDecorator`. Defaults suffice | [Manual FAQ 18A](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| Element at a specific position in the list (e.g. an ad) | Insert an **empty placeholder model** at that index so the list reserves the space, then drive the decorator's inset from the placeholder's virtual position | [Manual FAQ 18B](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| Manual OSA initialization | Call the decorator's own `Init()` before `OSA.Init()` — it must initialize first | [Manual FAQ 18](https://forbiddenbyte.com/blog/osa-complete-manual/) |

For the positioned case, four things happen together: the placeholder is
inserted into the dataset before the first refresh, the placeholder item is
resized once to the decorator's actual size, the decorator's inset is
re-synced on every scroll, and `UpdateViewsHolder` skips the placeholder
index entirely (there is nothing to bind, and any size logic for real items
would be wrong for it).

```csharp
protected override void OnScrollPositionChanged(double normPos)
{
    base.OnScrollPositionChanged(normPos);

    // Items not set yet, or too few to include the ad.
    if (this.GetItemsCount() <= this._AdIndex)
        return;

    float adInset = (float)this.GetItemVirtualInsetFromParentStart(this._AdIndex);
    this._Decorator.SetInset(adInset);
}
```

The one-time resize uses
`RequestChangeItemSizeAndUpdateLayout(adIndex, adSize)` with `adSize` read
off the decorator's own `RectTransform` (`rect.height` vertically,
`rect.width` horizontally) — see [variable-item-sizes.md](variable-item-sizes.md).
Keep the decorator's GameObject inactive at edit time and activate it in
code before the first data set, or it sits visible in an empty scroll view.
If the decorator does not cover its placeholder completely, disable the
placeholder's children for that index rather than the item itself — OSA
owns the item's active state.

**Critical caveat**: `OSAContentDecorator.SetInset()` was added after
v5.1.2. If it is missing, the package is older than this skill's 6.0–7.0
anchor, per [root-links.md](root-links.md).

## Sticky item that never leaves the screen

There is no built-in sticky mode. The supported shape is a second views
holder you instantiate and position yourself, parented to the Viewport with
item index `-1` so the adapter never manages it, kept in a field and updated
like any other holder.

Each frame: ask whether the real item is currently visible, read its inset
from Content, clamp that inset to the viewport, and apply it to the overlay
holder.

```csharp
void UpdateStickyOverlay(int targetItemIndex)
{
    MyItemViewsHolder realVH = this.GetItemViewsHolderIfVisible(targetItemIndex);
    if (realVH == null)
        return;

    float realInset = realVH.root.GetInsetFromParentTopEdge(this._Params.Content);
    float size = this._OverlayVH.root.rect.height;
    float maxInset = (float)this.GetViewportSize() - size;
    float targetInset = Mathf.Clamp(realInset, 0f, maxInset);

    this._OverlayVH.root.SetInsetAndSizeFromParentTopEdgeWithCurrentAnchors(targetInset, size);
}
```

`GetInsetFromParentTopEdge` and
`SetInsetAndSizeFromParentTopEdgeWithCurrentAnchors` are OSA-provided
`RectTransform` extensions and work on any `RectTransform`, not only views
holders.
