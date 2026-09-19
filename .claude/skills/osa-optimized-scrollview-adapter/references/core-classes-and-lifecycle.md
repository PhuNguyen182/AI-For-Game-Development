# Core Classes & Lifecycle — the adapter triad and when it initializes

Source: [`Com.ForbiddenByte.OSA.Core` API reference](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/doc/43/html/303f106d-29ab-b975-b0e1-9120154c4aee.htm), [OSA 6.0–7.0 Complete Manual](https://forbiddenbyte.com/blog/osa-complete-manual/) (OSA wizard; Usage; Implementation; FAQ 2, 5, 9, 14), [Changelog](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/Changelog.txt).
Covers: SKILL.md §4 — **"Implement the three types in dependency order — views holder, then params, then adapter"**, **"Let OSA initialize from `Start()` unless you call `Init()` yourself, and never assume a correct viewport size inside `Awake()`"**.

Three classes carry the whole design, and the adapter is generic over the
other two — which is why they get written first. Everything below lives
in `Com.ForbiddenByte.OSA.Core` — the current root, in force since v7.0.
A project still pinned to 6.x carries the pre-rename root instead; see
[root-links.md](root-links.md).

## The triad

| Type | Role | Source |
|---|---|---|
| `AbstractViewsHolder` | References some views and the id of the data those views display. Holds `root` and `ItemIndex` — the identity of "which item is this row currently showing" | [API — Core namespace](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/doc/43/html/303f106d-29ab-b975-b0e1-9120154c4aee.htm) |
| `BaseItemViewsHolder` | The minimal views-holder implementation to subclass for a list. Deliberately **not** a MonoBehaviour, for performance | [API — Core namespace](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/doc/43/html/303f106d-29ab-b975-b0e1-9120154c4aee.htm), [Manual FAQ 2](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| `BaseParams` | Input parameters passed to initialization, exposed as inspector fields — orientation, default item size, padding/spacing, Viewport and Content references, scrollbar, drag/scroll toggles | [API — Core namespace](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/doc/43/html/303f106d-29ab-b975-b0e1-9120154c4aee.htm) |
| `OSA<TParams, TItemViewsHolder>` | The abstract generic MonoBehaviour you extend. Requires at minimum `CreateViewsHolder(int)` and `UpdateViewsHolder(TItemViewsHolder)` | [API — Core namespace](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/doc/43/html/303f106d-29ab-b975-b0e1-9120154c4aee.htm), [Manual — Usage](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| `IOSA` | Non-generic interface exposing the commonly used members, so an adapter can be referenced abstractly — what the DataHelpers bind to | [API — Core namespace](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/doc/43/html/303f106d-29ab-b975-b0e1-9120154c4aee.htm) |

Supporting types in the same namespace: the two params sub-objects, reached
as the lowercase fields `Params.effects` and `Params.optimization` (see
[pooling-and-performance.md](pooling-and-performance.md)), plus
`ItemsDescriptor`, `LayoutInfo`, `OSAConst`, `OSADebugger`, `OSAException`,
`Snapper8` (see [scrolling-navigation-and-snapping.md](scrolling-navigation-and-snapping.md)),
and the enums `ItemCountChangeMode` (`RESET`/`INSERT`/`REMOVE`),
`BaseParams.OrientationEnum` (`VERTICAL`/`HORIZONTAL`) and
`BaseParams.ContentGravity`.

**Critical caveat**: the generated API site flattens nested type names — its
index renders `BaseParams.Effects` as `BaseParamsEffects` and
`FIFOCachingPool.ObjectDestroyer` as `FIFOCachingPoolObjectDestroyer`.
Those flattened spellings do not compile. Always take a nested type's real
name from its own type page's syntax block, never from a listing.

## Implementation order

1. `MyItemViewsHolder : BaseItemViewsHolder`
2. `MyParams : BaseParams` — only if you need extra inspector data
3. `MyScrollViewAdapter : OSA<MyParams, MyItemViewsHolder>`

The order is forced: the adapter's generic arguments are the first two types.

## The two required overrides

| Override | Called | Contract | Source |
|---|---|---|---|
| `protected abstract TItemViewsHolder CreateViewsHolder(int itemIndex)` | The first time an item needs a GameObject, **and** whenever the viewport grows enough to need more rows | `root` is null here — instantiate the prefab, assign it, and call `CollectViews()`; or let `Init(..)` do both. Subscribe listeners here, once | [API](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/doc/43/html/d0db04fa-8987-6216-ef44-21bab452c7b4.htm) |
| `protected abstract void UpdateViewsHolder(TItemViewsHolder newOrRecycled)` | Every time a row is displayed or needs refreshing — i.e. on every recycle | `root` is valid; read `newOrRecycled.ItemIndex` to fetch the model and assign values to already-resolved views. Nothing else | [API](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/doc/43/html/dc74a659-1956-f1e3-0762-80f3e691f0bb.htm) |

`AbstractViewsHolder.Init` has two overloads, both defaulting the last two
arguments: `Init(GameObject rootPrefabGO, RectTransform parent, int itemIndex,
bool activateRootGameObject = true, bool callCollectViews = true)` and the
same taking a `RectTransform rootPrefab`. `root` is a **field**, not a
property, and `ItemIndex` is `public virtual int { get; set; }`.

`CollectViews()` is where child views are resolved once per instantiated
row, so `UpdateViewsHolder` is field assignment rather than a `GetComponent`
per recycle — see [item-interaction-and-decorators.md](item-interaction-and-decorators.md).

```csharp
class MyItemViewsHolder : BaseItemViewsHolder
{
    public Text titleText;
    public Image icon;

    public override void CollectViews()
    {
        base.CollectViews();
        this.titleText = this.root.Find("TitleText").GetComponent<Text>();
        this.icon = this.root.Find("Icon").GetComponent<Image>();
    }
}
```

Other overridable hooks worth knowing: `CollectItemsSizes(..)` (see
[variable-item-sizes.md](variable-item-sizes.md)), `OnInitialized()`,
`OnScrollPositionChanged(double)`, and — on the views holder —
`OnBeforeRecycleOrDisable(int newItemIndex)`, added in **v6.5.4**, which is
where per-row cleanup belongs before the row is handed to a different item.

## Initialization

| Situation | Do this | Source |
|---|---|---|
| Default | Override `Start()`, call `base.Start()`, then `ResetItems(count)` once. OSA initializes itself in `Start()` | [Manual — Implementation](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| Data must be set on the same frame the OSA prefab is instantiated | Call `OSA.Init()` manually first; guard with `OSA.IsInitialized` if it may already have run | [Manual FAQ 14](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| Earlier still | Override `Awake()` and call `Init()` there — OSA detects it and skips auto-init in `Start()`. `Awake()` only runs if the GameObject is active | [Manual FAQ 14](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| Setup that must run once after init | `OnInitialized()` — where pre-instantiated pools are registered | [Manual FAQ 16](https://forbiddenbyte.com/blog/osa-complete-manual/) |

**Critical caveat**: initializing in `Awake()` is the documented cause of a
wrong first layout. On several Unity versions `RectTransform` misreports its
size that early, so the scroll view sees the wrong viewport and a `ScrollTo`
in the same frame lands wrong — grids especially. `Start()` is the general
answer; see [known-issues-and-platform-caveats.md](known-issues-and-platform-caveats.md)
for the narrow workaround when you cannot move.

## What the wizard generates, and what it leaves behind

The OSA wizard (**Tools → OSA**) creates a scroll view from scratch or
retrofits an existing `ScrollRect`, generating an adapter from a List or a
Grid template and wiring a scrollbar.

| Fact | Consequence | Source |
|---|---|---|
| After Initialize, the `ScrollRect` is **disabled** | OSA replaces it. It can safely be removed; a plain uGUI `Scrollbar` bound to it will not work — use `ScrollbarFixer8` | [Manual — OSA wizard](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| The generated script has sections commented out with `/**/` | `OnBeforeRecycleOrDisableCellViewsHolder()`, `GetViews()` and `MarkForRebuild()` are scaffolding — uncomment what you use, delete the rest rather than shipping empty overrides | [Manual — OSA wizard](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| Only example implementations exist initially | `MainExample.cs` and `SimpleExample.cs` are reference material, not production code — read them, don't ship them | [Manual — Usage, FAQ 1](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| OSA ships assembly definitions since v4.3 | Reference `OSA.asmdef` from your own asmdef; from v6.0.1 the OSA folder may also be relocated, tracked by a path-tracker asset | [Manual — Documentation](https://forbiddenbyte.com/blog/osa-complete-manual/), [Changelog 6.0.1](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/Changelog.txt), [Unity assembly definitions](https://docs.unity3d.com/Manual/ScriptCompilationAssemblyDefinitionFiles.html) |

**Critical caveat**: inside an adapter, `Time` and `DeltaTime` are OSA's own
properties, governed by `Params.UseUnscaledTime` (**v5.0+**), and they
deliberately shadow `UnityEngine.Time` so your own animations honour the
same pause behaviour. Write `UnityEngine.Time` explicitly when you really
mean the engine clock.
