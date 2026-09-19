# Pooling & Performance — the recycle bin, pre-instantiation, caching pools

Source: [OSA 6.0–7.0 Complete Manual](https://forbiddenbyte.com/blog/osa-complete-manual/) (FAQ 13, 15, 16, 28; Tips), [Changelog](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/Changelog.txt).
Covers: SKILL.md §4 — **"Size and persist the recycle pool deliberately rather than accepting the default"**.

By design OSA instantiates the minimum it needs: roughly the visible count
plus one. That is the right default for steady scrolling and the wrong one
at two specific moments — the first fast fling, and a count change that
empties the list — where objects are created or destroyed in a burst.
Everything below trades memory for the absence of those bursts. Measuring
whether a burst actually costs anything is `unity-profiler-diagnostics`'
job, per `performance-and-algorithms.md`'s Verification section.

## `Params.optimization`

| Member | Effect | Use when | Source |
|---|---|---|---|
| `RecycleBinCapacity` | How many recycled views holders are retained rather than destroyed. Raising it worked only from v5.0 onward — it was broken before | Rows are expensive to instantiate and the count changes often | [Manual FAQ 16](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| `KeepItemsPoolOnEmptyList` | Keeps instantiated rows alive across a reset to zero items | The list is emptied and refilled repeatedly (tab switches, filters) | [Manual FAQ 16](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| `KeepItemsPoolOnLayoutRebuild` | Keeps the pool across a layout rebuild | Same, for orientation/viewport changes rather than count changes | [Manual FAQ 16](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| `ResponsiveOnScrollViewSizeChange` | Preserves item positions (ideally velocity) when OSA itself is resized. **Off by default** | The scroll view resizes at runtime *and* uses ContentSizeFitter or dynamic item sizes — the case where the default is not enough | [Manual FAQ 28](https://forbiddenbyte.com/blog/osa-complete-manual/) |

**Critical caveat**: grids ignore `KeepItemsPoolOnLayoutRebuild` when the
rebuild produces a different number of cells per group — a narrower viewport
that fits 3 cells instead of 4 rebuilds the pool regardless of the flag.

## Pre-instantiating rows

Three escalating options, cheapest first.

| Technique | Mechanism | Cost | Source |
|---|---|---|---|
| Enlarge the Viewport | Move the Viewport's edges out by N units on both sides and increase `ContentPadding` by the same N. Items then travel further before leaving the *viewport* (which is what triggers recycling), so more exist than are visible — and the first item still *appears* first | Zero API surface; the count is indirect and set by geometry | [Manual FAQ 15](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| Buffered recycleable items | `CreateBufferredRecycleableItems(count)` + `AddBufferredRecycleableItems(vhs)` — a separate internal list of items that are not destroyed unless promoted to the normal recycle bin | Explicit count, still instantiated at runtime | [Manual FAQ 16](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| Edit-time instances | Supply an existing root instead of a prefab, via `vh.InitWithExistingRoot(root, parent, itemIndex)`. Requires **v5.1.3+** | No runtime `Instantiate` at all; you must decide what happens when OSA asks for more than you pre-made | [Manual FAQ 16](https://forbiddenbyte.com/blog/osa-complete-manual/) |

OSA calls `CreateViewsHolder(int)` with **`-1`** for buffered items. With
several prefab types, pass a distinct negative index per type so the method
can tell which prefab to build.

```csharp
protected override void OnInitialized()
{
    base.OnInitialized();

    var vhs = this.CreateBufferredRecycleableItems(this._PreMadeViews.Count);
    this.AddBufferredRecycleableItems(vhs);

    // Buffered items must survive count changes and rebuilds, or pre-making them is pointless.
    this._Params.optimization.KeepItemsPoolOnEmptyList = true;
    this._Params.optimization.KeepItemsPoolOnLayoutRebuild = true;
}

protected override MyItemViewsHolder CreateViewsHolder(int itemIndex)
{
    MyItemViewsHolder instance = new MyItemViewsHolder();
    if (itemIndex < 0)
    {
        // Called because of CreateBufferredRecycleableItems() above.
        RectTransform preMadeRoot = this._PreMadeViews[this._PreMadeViews.Count - 1];
        this._PreMadeViews.RemoveAt(this._PreMadeViews.Count - 1);
        instance.InitWithExistingRoot(preMadeRoot, this._Params.Content, itemIndex);
    }
    else
    {
        // OSA needs more views than were pre-made: fall back to instantiating, or fail loudly.
        instance.Init(this._Params.ItemPrefab, this._Params.Content, itemIndex);
    }

    return instance;
}
```

Whether the `else` branch instantiates or throws is a real decision, not a
detail: throwing surfaces an under-sized pre-made set during development,
while falling back hides it and reintroduces the runtime allocation the
technique existed to remove.

## Caching pools for downloaded content

`LRUCachingPool` is the pool to use for remotely loaded images — added in
**6.5.4** and better than `FIFOCachingPool` in most cases, because a list
re-scrolled over its recent range hits an LRU cache and misses a FIFO one.

Capacity has to be hard-coded against a device assumption. The vendor's
suggested shape, given an estimate `X` of free RAM in bytes:

```csharp
float safePoolSizeBytes = Mathf.Min(availableRamBytes / 4f, 250 * 1024 * 1024);
float avgBytesPerImage = 4f * averageWidth * averageHeight;
int safePoolCapacity = (int)(safePoolSizeBytes / avgBytesPerImage);
```

A quarter of free RAM, capped at 250 MB, over 4 bytes per pixel. Loading
the images themselves is `unity-addressables`' or the project's download
layer's job — this pool only decides what stays resident.

## Hygiene that is not OSA's

These belong to `ugui` but decide whether a recycling list actually
performs. See [known-issues-and-platform-caveats.md](known-issues-and-platform-caveats.md)
for the version bugs attached to them.

| Practice | Reason | Source |
|---|---|---|
| Nest a `Canvas` around frequently changing UI | Any change rebuilds batch geometry for its whole Canvas; a scrolling list changes constantly, so it must not share a Canvas with static chrome | [Manual — Tips](https://forbiddenbyte.com/blog/osa-complete-manual/), [Unity UI optimization tips](https://create.unity3d.com/Unity-UI-optimization-tips) |
| Prefer `RectMask2D` over `Mask` | Faster for scroll views when shape masking is not needed | [Manual — Tips](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| Keep the views holder a plain C# class, not a MonoBehaviour | Deliberate: the prefab may carry any number of components, and the holder must not add to that per row | [Manual FAQ 2](https://forbiddenbyte.com/blog/osa-complete-manual/) |
