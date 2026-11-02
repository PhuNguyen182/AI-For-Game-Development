---
name: osa-optimized-scrollview-adapter
description: "OSA<TParams,TItemViewsHolder>, ResetItems, GridAdapter, ScrollTo, Snapper8. Use for long scroll lists."
user-invocable: false
---

# OSA — Recycling ScrollView Adapter for uGUI

- **Not for:** Canvas/RectTransform/Layout/`ScrollRect` setup (`ugui`).
- **Not for:** UI Toolkit `ListView` (`ui-toolkit`).
- **Not for:** loading item content (`unity-addressables`).
- **Not for:** animating items (`dotween-tweening`).
- **Not for:** measuring the result (`unity-profiler-diagnostics`).
- **Not for:** the data model (`csharp-engineer`).
- **Docs:** manual https://forbiddenbyte.com/blog/osa-complete-manual/ (6.0–7.0), changelog https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/Changelog.txt.
  - **Paid asset with sources in the project:** the vendored `.cs` is the only authority for anything added after 4.3, so confirm signatures and defaults there.
  - **Generated API site:** stops at 4.3 and is silent, not contradicting, about 5.0+.
  - **Params members:** PascalCase here (`RecycleBinCapacity`, `ItemPrefab`); 4.x used lowercase.
- **Namespace:** `Com.ForbiddenByte.OSA.*` since 7.0.0.
  - **6.x and earlier:** use `Com.TheFallenGames.OSA.*`, and so does any sample older than late 2023; the rename is mechanical, nothing else changes.
  - **Root:** read it out of the installed package; if an API named here is missing, the project predates it (version landmarks in [core-classes-and-lifecycle.md](references/core-classes-and-lifecycle.md)).

## References
- **[core-classes-and-lifecycle.md](references/core-classes-and-lifecycle.md):** Writing a new adapter, deciding when `Init()` runs, or a member does not exist in the installed version.
- **[data-and-count-changes.md](references/data-and-count-changes.md):** Adding, removing or replacing items, or the list jumps on update.
- **[variable-item-sizes.md](references/variable-item-sizes.md):** Rows differ in size, a size changes at runtime, or `CollectItemsSizes`/ContentSizeFitter misbehaves.
- **[grid-and-table.md](references/grid-and-table.md):** The layout is a grid (`GridAdapter`) or a table.
- **[scrolling-navigation-and-snapping.md](references/scrolling-navigation-and-snapping.md):** Programmatic scroll, snapping/paging, scrollbar, looping or cross-axis scrolling.
- **[pooling-and-performance.md](references/pooling-and-performance.md):** Instantiation spike on first fling or after emptying the list, pre-made rows, image caching pools.
- **[item-interaction-and-decorators.md](references/item-interaction-and-decorators.md):** Click handling on rows, headers/ads inside the list, sticky items, reusing a MonoBehaviour as view logic.
- **[known-issues-and-platform-caveats.md](references/known-issues-and-platform-caveats.md):** Wrong first layout, clipping, truncated text, WebGL stripping, input conflicts: before writing a workaround.

## Steps
1. **Justify OSA first:** a list that fits a screen or two is cheaper as `ScrollRect` + Layout Group (`ugui`).
   - **Cost:** the adapter/params/views-holder triad is real complexity.
2. **Confirm the inputs that decide the design:**
   - **Installed OSA version:** confirm it.
   - **Scroll orientation:** confirm it.
   - **Expected item count:** confirm it.
   - **Item sizes:** whether they vary.
   - **Why:** each changes the base classes and size strategy and is costly to unwind after the prefab exists.
   - **Unstated:** step 14.
3. **Write the types in order — views holder, params, adapter (the adapter is generic over the other two):**
   - **Child views:** resolve them once in `CollectViews`, per [core-classes-and-lifecycle.md](references/core-classes-and-lifecycle.md).
4. **Initialize from `Start()`:** unless calling `Init()` yourself.
   - **Viewport size in `Awake()`:** never trust it, per [known-issues-and-platform-caveats.md](references/known-issues-and-platform-caveats.md).
5. **Route every dataset change through the count-change API:** never the backing list alone, per [data-and-count-changes.md](references/data-and-count-changes.md).
6. **Pick the size strategy before authoring the prefab (uniform, `CollectItemsSizes`, or ContentSizeFitter twin pass):** per [variable-item-sizes.md](references/variable-item-sizes.md).
   - **Each strategy:** constrains the prefab.
7. **Grid only for a true cell grid:** per [grid-and-table.md](references/grid-and-table.md).
   - **Grid views holder:** a cell group.
   - **Grid indices:** differ.
   - **Grid data change:** supports `ResetItems` only.
8. **Keep `UpdateViewsHolder` a pure data-to-view bind (runs on every recycle):** per [item-interaction-and-decorators.md](references/item-interaction-and-decorators.md).
   - **Listeners:** wire them once in `CreateViewsHolder`.
   - **Item index:** capture the views holder and read `ItemIndex` at invocation.
9. **Scroll only through the adapter (`ScrollTo`/`SmoothScrollTo`):** per [scrolling-navigation-and-snapping.md](references/scrolling-navigation-and-snapping.md).
10. **Non-item chrome hangs off `OSAContentDecorator` under the Viewport:** not Content (its children are the recycled pool).
11. **Size the recycle pool deliberately:** per [pooling-and-performance.md](references/pooling-and-performance.md).
    - **Default:** visible count + 1.
12. **Keep OSA types in Client code:** the adapter reads Core models and decides no rule (`csharp-standards` → `coding-principles.md`).
    - **Serialized params fields:** follow the Inspector camelCase override in `csharp-standards` → `naming-convention.md`.
13. **Verify with the Profiler (instantiated count, GC during a sustained fling, frame time on the lowest target device):** per `unity-profiler-diagnostics`.
    - **Otherwise:** report "not measured".
14. **Missing input:** installed OSA version, scroll orientation, expected item count or whether item sizes vary unstated.
    - **Dispatched agent:** `Blocked` or `Needs-decision`.
    - **Main session:** `AskUserQuestion`.
    - **Otherwise:** proceed on a stated assumption.

## Never
- **Add or remove items inside `UpdateViewsHolder`:** the adapter is mid-layout.
- **Subscribe an event or call `GetComponent` in `UpdateViewsHolder`:** it duplicates per reuse and costs per recycle.
- **Capture an item index in a listener closure:** a recycled row acts on the item it used to show.
- **Parent a header/footer/ad to Content:**
- **Let a Layout Group or `ContentSizeFitter` own an item's size on the scroll axis unless the twin pass cooperates:**
- **Write `Content.localPosition` to scroll:**

## Output
```
## OSA — <list/grid/screen>
- Version & namespace: <installed> — <root>
- Justification: <why recycling at this item count>
- Types: <ViewsHolder / Params base / adapter>, orientation <v|h>
- Init: <Start() | explicit Init() at ...> — why
- Data path: <ResetItems | Insert/RemoveItems | SimpleDataHelper | LazyDataHelper>, position preserved <yes/no>
- Item sizing: <uniform | CollectItemsSizes | twin pass> — prefab constraint
- Grid/Table, scrolling, interaction, pooling: <choices, or n/a>
```

## Example
- **"Rows differ in height, just put a ContentSizeFitter on the prefab":** declined as stated.
  - **Why:** without the twin pass the adapter and the fitter both write the size and the list overlaps.
  - **Did instead:** sizes were knowable per item type, so `CollectItemsSizes` was used.
