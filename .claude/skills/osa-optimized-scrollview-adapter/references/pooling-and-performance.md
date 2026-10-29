# Pooling & Performance

Sources: M = manual https://forbiddenbyte.com/blog/osa-complete-manual/ (FAQ 2, 13, 15, 16, 28; Tips); C = changelog. OSA instantiates roughly visible count + 1: right for steady scrolling, wrong for the first fast fling and for a count change that empties the list (creation/destruction bursts). Everything here trades memory for no bursts; whether a burst costs anything is measured per `unity-profiler-diagnostics`.

## `Params.optimization`

| Member | Effect | Use when |
|---|---|---|
| `RecycleBinCapacity` | Recycled holders retained instead of destroyed; broken before 5.0 | Expensive rows, frequent count changes |
| `KeepItemsPoolOnEmptyList` | Pool survives a reset to zero | List emptied and refilled (tabs, filters) |
| `KeepItemsPoolOnLayoutRebuild` | Pool survives a layout rebuild (grids ignore it when cells per group change) | Orientation/viewport changes |
| `ResponsiveOnScrollViewSizeChange` | Keeps positions/velocity when OSA is resized; off by default | Runtime resize with ContentSizeFitter or dynamic sizes |

## Pre-instantiating rows (cheapest first)

| Technique | Mechanism | Cost |
|---|---|---|
| Enlarge the Viewport | Move Viewport edges out N units both sides and raise `ContentPadding` by N; items leave the viewport later, so more exist | No API; count set indirectly by geometry |
| Buffered items | `CreateBufferredRecycleableItems(count)` + `AddBufferredRecycleableItems(vhs)`; kept unless promoted to the recycle bin | Explicit count, instantiated at runtime |
| Edit-time instances | `vh.InitWithExistingRoot(root, parent, itemIndex)` (5.1.3+) | No runtime `Instantiate`; you decide what happens when OSA asks for more |

OSA calls `CreateViewsHolder(-1)` for buffered items; with several prefab types use a distinct negative index per type.

```csharp
protected override void OnInitialized()
{
    base.OnInitialized();
    var vhs = CreateBufferredRecycleableItems(_PreMadeViews.Count);
    AddBufferredRecycleableItems(vhs);
    // Buffered items must survive count changes and rebuilds.
    _Params.optimization.KeepItemsPoolOnEmptyList = true;
    _Params.optimization.KeepItemsPoolOnLayoutRebuild = true;
}

protected override MyItemViewsHolder CreateViewsHolder(int itemIndex)
{
    var instance = new MyItemViewsHolder();
    if (itemIndex < 0)
    {
        var root = _PreMadeViews[_PreMadeViews.Count - 1];
        _PreMadeViews.RemoveAt(_PreMadeViews.Count - 1);
        instance.InitWithExistingRoot(root, _Params.Content, itemIndex);
    }
    else
        instance.Init(_Params.ItemPrefab, _Params.Content, itemIndex); // or throw
    return instance;
}
```

Throwing in the `else` surfaces an under-sized pre-made set in development; falling back hides it and brings back the runtime allocation.

## Caching pools for downloaded images

`LRUCachingPool` (6.5.4+) beats `FIFOCachingPool` for lists re-scrolled over their recent range. Capacity is hard-coded against a device assumption (vendor shape, quarter of free RAM capped at 250 MB over 4 bytes per pixel):

```csharp
float safePoolSizeBytes = Mathf.Min(availableRamBytes / 4f, 250 * 1024 * 1024);
int safePoolCapacity = (int)(safePoolSizeBytes / (4f * averageWidth * averageHeight));
```

The pool only decides what stays resident; loading is `unity-addressables` or the download layer.

## uGUI hygiene (owned by `ugui`)

- Nest a `Canvas` around frequently changing UI: any change rebuilds its whole Canvas batch, and a scrolling list changes constantly.
- Prefer `RectMask2D` over `Mask` when shape masking is not needed (bug in [known-issues-and-platform-caveats.md](known-issues-and-platform-caveats.md)).
