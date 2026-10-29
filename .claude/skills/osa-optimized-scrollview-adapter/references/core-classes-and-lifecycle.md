# Core Classes & Lifecycle

Sources: M = manual https://forbiddenbyte.com/blog/osa-complete-manual/ (wizard, Usage, Implementation, FAQ); C = changelog; A = API site (4.3 only). Namespace `Com.ForbiddenByte.OSA.Core` (see SKILL.md for 6.x).

## The triad

| Type | Role |
|---|---|
| `AbstractViewsHolder` | Holds `root` (a field) and `ItemIndex` (virtual get/set): which item the row currently shows |
| `BaseItemViewsHolder` | Subclass for a list. Deliberately **not** a MonoBehaviour (the prefab may carry any number of components) |
| `BaseParams` | Inspector params: orientation, default item size, padding/spacing, Viewport/Content, scrollbar, drag/scroll toggles. Sub-objects are lowercase fields `Params.effects`, `Params.optimization` |
| `OSA<TParams, TItemViewsHolder>` | Abstract generic MonoBehaviour to extend |
| `IOSA` | Non-generic interface; what the DataHelpers bind to |

Enums: `ItemCountChangeMode` (`RESET`/`INSERT`/`REMOVE`), `BaseParams.OrientationEnum`, `BaseParams.ContentGravity`.

Order is forced: `MyItemViewsHolder : BaseItemViewsHolder`, then `MyParams : BaseParams` (only for extra inspector data), then `MyAdapter : OSA<MyParams, MyItemViewsHolder>`.

The API site flattens nested type names (`BaseParamsEffects`, `FIFOCachingPoolObjectDestroyer`); those spellings do not compile. Take nested names from the type page's syntax block.

## Required overrides

| Override | Called | Contract |
|---|---|---|
| `TItemViewsHolder CreateViewsHolder(int itemIndex)` | First time an item needs a GameObject, and when the viewport grows | `root` is null: instantiate and assign it and call `CollectViews()`, or let `Init(..)` do both. Subscribe listeners here, once |
| `void UpdateViewsHolder(TItemViewsHolder vh)` | Every display/refresh, i.e. every recycle | `root` valid; read `vh.ItemIndex`, assign to already-resolved views. Nothing else |

`AbstractViewsHolder.Init(GameObject rootPrefabGO, RectTransform parent, int itemIndex, bool activateRootGameObject = true, bool callCollectViews = true)`, plus a `RectTransform rootPrefab` overload.

```csharp
class MyItemViewsHolder : BaseItemViewsHolder
{
    public Text titleText;
    public override void CollectViews()
    {
        base.CollectViews();
        titleText = root.Find("TitleText").GetComponent<Text>();
    }
}
```

`CollectViews` runs once per instantiated row: the only place for `GetComponent`, including resolving an existing MonoBehaviour on the prefab. Other hooks: `CollectItemsSizes(..)`, `OnInitialized()`, `OnScrollPositionChanged(double)`, and on the views holder `OnBeforeRecycleOrDisable(int newItemIndex)` (6.5.4+), the place for per-row cleanup before reuse.

## Initialization

| Situation | Do |
|---|---|
| Default | Override `Start()`, call `base.Start()`, then `ResetItems(count)` once; OSA initializes itself in `Start()` |
| Data needed the frame the OSA prefab is instantiated | Call `Init()` manually; guard with `IsInitialized` (M FAQ 14) |
| Earlier still | Call `Init()` in `Awake()` (only runs on an active GameObject); OSA then skips auto-init (M FAQ 14) |
| Once-after-init setup | `OnInitialized()`, where pre-made pools are registered |

`Awake()` init is the documented cause of a wrong first layout (see [known-issues-and-platform-caveats.md](known-issues-and-platform-caveats.md)).

## Wizard (Tools > OSA)

- After Initialize the `ScrollRect` is **disabled**; it can be removed. A plain uGUI `Scrollbar` bound to it will not work: use `ScrollbarFixer8`.
- Generated scripts have `/**/` sections (`OnBeforeRecycleOrDisableCellViewsHolder()`, `GetViews()`, `MarkForRebuild()`): uncomment what is used, delete the rest.
- `MainExample.cs` and `SimpleExample.cs` are reference material, not production code.
- List and Grid templates generate different code and example prefabs; generate the right one.
- `OSA.asmdef` exists since 4.3: reference it from your asmdef. From 6.0.1 the OSA folder may be relocated (path-tracker asset).
- Inside an adapter `Time`/`DeltaTime` are OSA's own (5.0+, governed by `Params.UseUnscaledTime`) and shadow `UnityEngine.Time`; `'float' does not contain a definition for 'time'` means `Time.time` was written there: use `UnityEngine.Time`.

## Version landmarks (C)

| Version | Landmark |
|---|---|
| 5.1 | `ForceUpdateViewsHolderIfVisible`, `PrefabControlsDefaultItemSize`, `OSASnapperFocusedItemInfo` |
| 6.0.1 | New Input System support; `ForceRebuildLayoutNow()` |
| 6.1.0 | `ForceUpdateVisibleItems()` |
| 6.2.3 | Needed for the page-skip workaround in [scrolling-navigation-and-snapping.md](scrolling-navigation-and-snapping.md) |
| 6.4.0 | Looping `SmoothScrollTo` takes the shortest path; `GridAdapter.ForceUpdateCellViewsHolderIfVisible` |
| 6.5.4 | `LRUCachingPool` (over `FIFOCachingPool`); `OnBeforeRecycleOrDisable`; `GuessShouldKeepEndStationaryOnResize` |
| 7.0.0 | Namespace/folder rebrand; `IInitializable8` and `Singleton8` removed |

Migration guides apply one version at a time, never skipped: https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/ (`Migration guide from 4.3 to 5.0.txt`, `5.0 to 5.1`, `5.x to 6.0`).
