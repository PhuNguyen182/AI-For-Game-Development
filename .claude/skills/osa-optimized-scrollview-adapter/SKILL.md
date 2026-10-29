---
name: osa-optimized-scrollview-adapter
description: "OSA recycling list/grid/table views replacing ScrollRect: OSA<TParams,TItemViewsHolder>, ResetItems/InsertItems, GridAdapter, ScrollTo, Snapper8, ContentSizeFitter twin pass. Use when a scrolling list is too long for one GameObject per row."
user-invocable: false
---

# OSA — Recycling ScrollView Adapter for uGUI

Not for: Canvas/RectTransform/Layout/`ScrollRect` setup (`ugui`), UI Toolkit `ListView` (`ui-toolkit`), loading item content (`unity-addressables`), animating items (`dotween-tweening`), measuring the result (`unity-profiler-diagnostics`), the data model (`csharp-engineer`).
Docs: manual https://forbiddenbyte.com/blog/osa-complete-manual/ (6.0–7.0), changelog https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/Changelog.txt. Paid asset with sources in the project: the vendored `.cs` is the only authority for anything added after 4.3 (the generated API site stops at 4.3 and is silent, not contradicting, about 5.0+), so confirm signatures and defaults there. Params members are PascalCase here (`RecycleBinCapacity`, `ItemPrefab`); 4.x used lowercase.
Namespace: `Com.ForbiddenByte.OSA.*` since 7.0.0. 6.x and earlier use `Com.TheFallenGames.OSA.*`, and so does any sample older than late 2023; the rename is mechanical, nothing else changes. Read the root out of the installed package; if an API named here is missing, the project predates it (version landmarks in [core-classes-and-lifecycle.md](references/core-classes-and-lifecycle.md)).

| Reference | Read when |
|---|---|
| [core-classes-and-lifecycle.md](references/core-classes-and-lifecycle.md) | Writing a new adapter, deciding when `Init()` runs, or a member does not exist in the installed version |
| [data-and-count-changes.md](references/data-and-count-changes.md) | Adding, removing or replacing items, or the list jumps on update |
| [variable-item-sizes.md](references/variable-item-sizes.md) | Rows differ in size, a size changes at runtime, or `CollectItemsSizes`/ContentSizeFitter misbehaves |
| [grid-and-table.md](references/grid-and-table.md) | The layout is a grid (`GridAdapter`) or a table |
| [scrolling-navigation-and-snapping.md](references/scrolling-navigation-and-snapping.md) | Programmatic scroll, snapping/paging, scrollbar, looping or cross-axis scrolling |
| [pooling-and-performance.md](references/pooling-and-performance.md) | Instantiation spike on first fling or after emptying the list, pre-made rows, image caching pools |
| [item-interaction-and-decorators.md](references/item-interaction-and-decorators.md) | Click handling on rows, headers/ads inside the list, sticky items, reusing a MonoBehaviour as view logic |
| [known-issues-and-platform-caveats.md](references/known-issues-and-platform-caveats.md) | Wrong first layout, clipping, truncated text, WebGL stripping, input conflicts: before writing a workaround |

## Steps
1. **Justify OSA first** — a list that fits a screen or two is cheaper as `ScrollRect` + Layout Group (`ugui`); the adapter/params/views-holder triad is real complexity.
2. **Ask if unstated**: installed OSA version, scroll orientation, expected item count, whether item sizes vary. Each changes the base classes and size strategy and is costly to unwind after the prefab exists.
3. **Write the types in order — views holder, params, adapter** (the adapter is generic over the other two); resolve child views once in `CollectViews`, per [core-classes-and-lifecycle.md](references/core-classes-and-lifecycle.md).
4. **Initialize from `Start()`** unless calling `Init()` yourself; never trust the viewport size in `Awake()`, per [known-issues-and-platform-caveats.md](references/known-issues-and-platform-caveats.md).
5. **Route every dataset change through the count-change API**, never the backing list alone, per [data-and-count-changes.md](references/data-and-count-changes.md).
6. **Pick the size strategy before authoring the prefab** (uniform, `CollectItemsSizes`, or ContentSizeFitter twin pass); each constrains the prefab, per [variable-item-sizes.md](references/variable-item-sizes.md).
7. **Grid only for a true cell grid**: its views holder is a cell group, indices differ, and it supports `ResetItems` only, per [grid-and-table.md](references/grid-and-table.md).
8. **Keep `UpdateViewsHolder` a pure data-to-view bind** (runs on every recycle): wire listeners once in `CreateViewsHolder`, capture the views holder and read `ItemIndex` at invocation, per [item-interaction-and-decorators.md](references/item-interaction-and-decorators.md).
9. **Scroll only through the adapter** (`ScrollTo`/`SmoothScrollTo`), per [scrolling-navigation-and-snapping.md](references/scrolling-navigation-and-snapping.md).
10. **Non-item chrome hangs off `OSAContentDecorator` under the Viewport**, not Content (its children are the recycled pool).
11. **Size the recycle pool deliberately**, per [pooling-and-performance.md](references/pooling-and-performance.md); default is visible count + 1.
12. **Keep OSA types in `Game.Client.*`**; the adapter reads Core models and decides no rule (`csharp-standards` → `coding-principles.md`). Serialized params fields follow the Inspector camelCase override in `csharp-standards` → `naming-convention.md`.
13. **Verify with the Profiler** (instantiated count, GC during a sustained fling, frame time on the lowest target device) per `unity-profiler-diagnostics`; otherwise report "not measured".

## Never
- Add or remove items inside `UpdateViewsHolder`: the adapter is mid-layout.
- Subscribe an event or call `GetComponent` in `UpdateViewsHolder`: it duplicates per reuse and costs per recycle.
- Capture an item index in a listener closure: a recycled row acts on the item it used to show.
- Parent a header/footer/ad to Content.
- Let a Layout Group or `ContentSizeFitter` own an item's size on the scroll axis unless the twin pass cooperates.
- Write `Content.localPosition` to scroll.

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
- Verified: <Profiler evidence, or "not measured">
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Rows differ in height, just put a ContentSizeFitter on the prefab" → declined as stated: without the twin pass the adapter and the fitter both write the size and the list overlaps. Sizes were knowable per item type, so `CollectItemsSizes` was used.
