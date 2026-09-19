---
name: osa-optimized-scrollview-adapter
description: >
  Optimized ScrollView Adapter (OSA) by Forbidden Byte — the recycling
  ListView/GridView/TableView that replaces uGUI's `ScrollRect`:
  `OSA<TParams, TItemViewsHolder>`, `BaseParams`, `BaseItemViewsHolder`,
  `CreateViewsHolder`, `UpdateViewsHolder`, `CollectItemsSizes`,
  `ResetItems`, `InsertItems`, `RemoveItems`, `SimpleDataHelper`,
  `LazyDataHelper`, `GridAdapter`, `CellGroupViewsHolder`, `ScrollTo`,
  `SmoothScrollTo`, `ScheduleComputeVisibilityTwinPass`, `Snapper8`,
  `ScrollbarFixer8`, `OSAContentDecorator`, `Params.optimization`
  pooling, under the current `Com.ForbiddenByte.OSA` namespace root
  (`Com.TheFallenGames.OSA` before the v7.0 rename). Use when a scrolling
  list is too long to instantiate one GameObject per row. Not for:
  Canvas/RectTransform/Layout/`ScrollRect` setup around the adapter
  (`ugui`), UI Toolkit `ListView` virtualization (`ui-toolkit`),
  item-content asset loading (`unity-addressables`), animating items
  (`dotween-tweening`), measuring the result
  (`unity-profiler-diagnostics`), the data model itself
  (`csharp-engineer`).
---

# OSA — Recycling ScrollView Adapter for uGUI

## Bundled resources

### References
Read-only context, loaded on demand so this file stays short.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Version/namespace anchor, vendor rebrand, doc + changelog + migration roots, topic→file map, disclosed gaps | Starting any task here, or an API name doesn't resolve in the installed package |
| [core-classes-and-lifecycle.md](references/core-classes-and-lifecycle.md) | `OSA<TParams, TItemViewsHolder>`, `BaseParams`, `BaseItemViewsHolder`, `AbstractViewsHolder`, wizard flow, `Init`/`Start` ordering, `CreateViewsHolder`/`UpdateViewsHolder` contract | Writing a new adapter, or deciding when initialization must happen |
| [data-and-count-changes.md](references/data-and-count-changes.md) | `ResetItems`/`InsertItems`/`RemoveItems`/`ChangeItemsCount`, `SimpleDataHelper`/`LazyDataHelper`, `keepEndEdgeStationary`, preserving scroll position across a change | Adding, removing, or replacing items, or a list jumps position on update |
| [variable-item-sizes.md](references/variable-item-sizes.md) | `DefaultItemSize`, `CollectItemsSizes`, `BaseParamsWithPrefab`, the ContentSizeFitter twin-pass pattern, `RequestChangeItemSizeAndUpdateLayout`, forced redraw methods | Items are not all the same size, or a size must change at runtime |
| [grid-and-table.md](references/grid-and-table.md) | `GridAdapter`, `GridParams`, `CellGroupViewsHolder`, `CellViewsHolder`, cell-vs-group indexing, `OnCellViewsHolderCreated`, TableView pointer | The layout is a grid or a table rather than a single-column list |
| [scrolling-navigation-and-snapping.md](references/scrolling-navigation-and-snapping.md) | `ScrollTo`/`SmoothScrollTo`, `ScrollbarFixer8`, `Snapper8`, looping, `OnScrollPositionChanged`, `Velocity`, `DragEnabled`/`ScrollEnabled`, cross-axis scrolling | Programmatic scrolling, snapping/paging, scrollbars, or looping is involved |
| [pooling-and-performance.md](references/pooling-and-performance.md) | `Params.optimization` (recycle bin, pool persistence, responsiveness), pre-instantiated items, image caching pools, Canvas/`RectMask2D` hygiene | Instantiation spikes on first scroll, or item count/GC is the concern |
| [item-interaction-and-decorators.md](references/item-interaction-and-decorators.md) | Click/long-click wiring through the views holder, `OSAContentDecorator` headers and inline ads, sticky/overlay items, reusing an existing MonoBehaviour as the views holder | Items need input handling, or non-item chrome must live inside the scroll view |
| [known-issues-and-platform-caveats.md](references/known-issues-and-platform-caveats.md) | `Awake` RectTransform sizing bug, `RectMask2D` clipping bugs, WebGL stripping/`link.xml`, CSF text truncation, Input System, `InputFieldInScrollRectFixerBase` | Behaviour is wrong in a way the code does not explain, before writing a workaround |

## 1. Objective
Build and maintain a recycling scroll view through OSA that displays an
arbitrarily large dataset with a bounded number of instantiated
GameObjects — without pinning the wrong namespace root for the installed
version, mutating the backing list without telling the adapter (which
leaves item count, content size and cached sizes silently disagreeing),
allocating or re-resolving components inside `UpdateViewsHolder` on every
recycle, letting a `ContentSizeFitter` and the adapter fight over the same
item size, or leaking listeners onto views holders that are reused for a
different item a frame later.

## 2. Role
Act as the OSA specialist for the client track — the tool reached for
whenever a uGUI list, grid or table is long enough that one GameObject per
row is untenable, and its items must be recycled while the underlying
dataset is added to, removed from, resized, scrolled to, or snapped.

## 3. When to invoke this skill
- Implementing a new list/grid/table screen whose item count is large, unbounded, or streamed in.
- Subclassing `OSA<TParams, TItemViewsHolder>` and writing `CreateViewsHolder`/`UpdateViewsHolder`, or extending `BaseParams`/`BaseItemViewsHolder`.
- A reported symptom of recycling gone wrong: stale data on a row after scrolling, listeners firing for the wrong item, the list jumping when items are inserted, or items overlapping when their sizes differ.
- Changing an existing OSA dataset — `ResetItems`, `InsertItems`, `RemoveItems`, or the `SimpleDataHelper`/`LazyDataHelper` equivalents.
- Adding snapping/paging (`Snapper8`), a working scrollbar (`ScrollbarFixer8`), looping, or programmatic `ScrollTo`/`SmoothScrollTo`.
- Migrating an OSA project across the v7.0 namespace rename, or importing OSA into a project for the first time.
- Negative trigger: Canvas render mode, `CanvasScaler`, `RectTransform` anchoring, Layout Groups, `Mask`/`RectMask2D`, or the plain `ScrollRect` the adapter replaces — that's `ugui`; this skill only consumes the hierarchy `ugui` sets up.
- Negative trigger: virtualization through UI Toolkit's own `ListView`/`UIDocument` — that's `ui-toolkit`; OSA is uGUI-only.
- Negative trigger: loading the sprites, prefabs or data an item displays — that's `unity-addressables`; this skill only decides when a row asks for them.
- Negative trigger: animating an item's transform/colour, or the expand-collapse tween itself — that's `dotween-tweening`/`litmotion-tweening`.
- Negative trigger: producing the frame-time or GC number that judges the result — that's `unity-profiler-diagnostics`, and `performance-qa-engineer` owns the verdict against a budget.
- Negative trigger: the game rules, economy or state machine behind the displayed models — that's `csharp-engineer` in `Game.Core.*`.

## 4. How to use this skill
1. **Confirm a recycling adapter is warranted before reaching for OSA at all** — a bounded list that fits a screen or two is cheaper as a plain `ScrollRect` with a Layout Group (`ugui`), and OSA's adapter/params/views-holder triad is real complexity that KISS in `coding-principles.md` only justifies once instantiating every row is genuinely untenable.
2. **Write every `using` against `Com.ForbiddenByte.OSA.*`, the current namespace root** — v7.0 renamed the whole tree from `Com.TheFallenGames.OSA.*`, so tutorials and samples predating 2023 carry a root that no longer compiles; reach for the legacy root only after confirming the project is actually pinned to 6.x, per [root-links.md](references/root-links.md).
3. **Implement the three types in dependency order — views holder, then params, then adapter** — the adapter is generic over the other two, and `CollectViews` on the views holder is what makes `UpdateViewsHolder` a field assignment rather than a `GetComponent` call per recycle, per [core-classes-and-lifecycle.md](references/core-classes-and-lifecycle.md).
4. **Let OSA initialize from `Start()` unless you call `Init()` yourself, and never assume a correct viewport size inside `Awake()`** — several Unity versions misreport `RectTransform` size that early, which surfaces as a wrong first layout rather than an error, per [core-classes-and-lifecycle.md](references/core-classes-and-lifecycle.md) and [known-issues-and-platform-caveats.md](references/known-issues-and-platform-caveats.md).
5. **Route every dataset change through the adapter's count-change API, never through the backing list alone** — the adapter caches item count, per-item sizes and content size, and a list mutated behind its back leaves all three disagreeing with what is drawn; use the DataHelpers when you don't need the raw two-step control, per [data-and-count-changes.md](references/data-and-count-changes.md).
6. **Decide the item-size strategy before the item prefab is authored** — uniform `DefaultItemSize` when rows genuinely match, `CollectItemsSizes` when sizes are known up front and the set is small enough to precompute, and the ContentSizeFitter twin-pass only when a row's size is knowable solely after its content is bound; each choice constrains the prefab's layout components, per [variable-item-sizes.md](references/variable-item-sizes.md) and the ContentSizeFitter prefab traps in [known-issues-and-platform-caveats.md](references/known-issues-and-platform-caveats.md).
7. **Reach for `GridAdapter` only when the layout is genuinely a cell grid, and accept its data-path constraint up front** — a grid's views holder is a *group* of cells, its indices are not your model indices, and it does not offer the list's incremental insert/remove, per [grid-and-table.md](references/grid-and-table.md).
8. **Keep `UpdateViewsHolder` a pure data-to-view bind** — it is called on every recycle, so it must not add or remove items, allocate, re-resolve components, or subscribe an event; wire listeners once at creation and read `ItemIndex` inside the handler so a recycled row acts on the item it currently shows, per [item-interaction-and-decorators.md](references/item-interaction-and-decorators.md) and `performance-and-algorithms.md`'s Update loop & callback overhead section.
9. **Move the viewport only through the adapter's own scroll API** — `ScrollTo`/`SmoothScrollTo` resolve an item index against virtual positions the adapter owns, whereas writing `Content.localPosition` desynchronises it from the visibility pass, per [scrolling-navigation-and-snapping.md](references/scrolling-navigation-and-snapping.md).
10. **Hang anything that is not an item off `OSAContentDecorator` under the Viewport, not as a child of Content** — Content's children are the recycled pool, so a header parented there is destroyed, recycled or repositioned without warning, per [item-interaction-and-decorators.md](references/item-interaction-and-decorators.md).
11. **Size and persist the recycle pool deliberately rather than accepting the default** — OSA creates only the minimum visible count plus one, which is correct for steady scrolling but produces an instantiation spike on the first fast fling and on every count change that empties the list, per [pooling-and-performance.md](references/pooling-and-performance.md).
12. **Keep every OSA type in `Game.Client.*`** — OSA is a `UnityEngine`/uGUI component set, which `coding-principles.md`'s Shared Core integrity section forbids in `Game.Core.*`; the adapter reads Core models and never decides a rule itself, and its serialized params fields follow the Inspector camelCase override in `naming-convention.md`.
13. **Verify the recycling win and any pooling change with the Profiler before claiming it** — instantiated-object count, GC allocation during a sustained fling, and frame time on the lowest target device, per `performance-and-algorithms.md`'s Verification section; an untested "OSA made it faster" is an assertion, not a result.
14. **If the installed OSA version, the scroll orientation, the expected item count, or whether item sizes vary is unstated, ask before writing the adapter** — each one changes which base classes and which size strategy are correct, and all four are expensive to unwind once the prefab and params are built.

## 5. Specific goals / tasks this skill performs
- Implementing a views holder, params class and `OSA<TParams, TItemViewsHolder>` subclass for a new list, and wiring the prefab and scroll view they need.
- Binding a dataset to an adapter and keeping it in sync across insert, remove, reset and full-refresh, including position-preserving updates.
- Choosing and implementing a fixed, precomputed, or content-driven item-size strategy, and changing a single item's size at runtime.
- Implementing a grid or table variant, including correct cell-versus-group index handling.
- Adding programmatic scrolling, snapping/paging, a functioning scrollbar, or looping.
- Wiring per-item input so a recycled row never acts on a stale item index.
- Tuning the recycle pool, pre-instantiating items, and adding headers/overlays via decorators.
- Migrating an existing OSA integration across the v7.0 namespace rename.
- Out of scope: Canvas/layout/`ScrollRect` construction (`ugui`), UI Toolkit virtualization (`ui-toolkit`), asset loading for item content (`unity-addressables`), item animation (`dotween-tweening`/`litmotion-tweening`), the performance verdict against a budget (`performance-qa-engineer`), and the models and rules being displayed (`csharp-engineer`).

## 6. Output format
```
## OSA Work — <list/grid/screen name>
- Version & namespace: <installed version> — Com.ForbiddenByte.OSA.* (legacy Com.TheFallenGames.OSA.* only if pinned to 6.x)
- Justification: <why recycling over a plain ScrollRect + Layout Group at this item count>
- Types: <ViewsHolder / Params base chosen / adapter class>, orientation <vertical|horizontal>
- Initialization: <Start() default | explicit Init() at ...> — and why
- Data path: <ResetItems | Insert/RemoveItems | SimpleDataHelper | LazyDataHelper>, position preserved: <yes/no>
- Item sizing: <uniform DefaultItemSize | CollectItemsSizes | ContentSizeFitter twin-pass> — and what it constrains in the prefab
- Grid/Table: <GridAdapter with cell-index handling, or "n/a — list">
- Scrolling: <ScrollTo/SmoothScrollTo | Snapper8 | ScrollbarFixer8 | looping | none>
- Interaction: <listener wiring point, and how stale ItemIndex is avoided>
- Pooling: <recycle bin capacity / pool persistence / pre-instantiation, or "defaults, unchanged">
- Verification: <Profiler evidence: instantiated count, GC during fling, device/frame time — or "not measured">
- Layer: Game.Client.* — never Game.Core.*
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces
the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what this adapter does not cover today>
- Latent concerns: <assumptions holding only at the current item count, orientation, device tier or OSA version>
- Future remediation: <the concrete fix for each, and the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: an inventory screen must show up to ~2,000 items in a vertical uGUI list; every row is the same height and the models are already loaded in memory.
- Output: `MyItemViewsHolder : BaseItemViewsHolder` caching its child views in `CollectViews`; params derived from the prefab-carrying base so the prefab drives `DefaultItemSize` (uniform sizing, so no `CollectItemsSizes` and no ContentSizeFitter); adapter subclass with `UpdateViewsHolder` doing nothing but assigning fields from the model at `ItemIndex`; the row's Button listener added once in `CreateViewsHolder` and reading `vh.ItemIndex` at click time. Data driven through a `SimpleDataHelper`. Kept in `Game.Client.UI`; the item models stay in `Game.Core.*`.

**Example 2**
- Input: "the row heights are all different, so just put a ContentSizeFitter on the prefab and let it work itself out."
- Output: declined as stated — a ContentSizeFitter on an OSA item is only correct alongside the twin-pass the adapter schedules from `UpdateViewsHolder`; dropped in without it, the adapter and the fitter both write the item's size and the list overlaps or mis-scrolls. Checked first whether the sizes are actually knowable before binding — they were (fixed per item type), so `CollectItemsSizes` was used instead, which is cheaper and needs no twin pass, per [variable-item-sizes.md](references/variable-item-sizes.md).

**Example 3**
- Input: a chat log where new messages arrive continuously and must appear at the bottom without yanking the user away from what they are reading.
- Output: incremental insert (not `ResetItems`) with the end edge kept stationary, so existing rows hold their on-screen position while the content grows; the reversal itself done in the backing list rather than expecting an adapter flag, per [data-and-count-changes.md](references/data-and-count-changes.md). Flagged that this is a list-only path — the same requirement on a grid would need the manual position-restore sequence instead.

**Example 4**
- Input: a project on OSA 6.5 is upgrading to 7.0 and the build breaks with unresolved `Com.TheFallenGames.OSA.Core` references.
- Output: identified as the v7.0 vendor rebrand rather than a missing package — every `Com.TheFallenGames.OSA.*` namespace became `Com.ForbiddenByte.OSA.*` in 7.0.0, so the fix is a namespace-root rename across the project's `using` directives and any asmdef reference, applied through the vendor's incremental migration guides rather than a version jump, per [root-links.md](references/root-links.md).

## 8. Edge cases & guardrails
- Never mutate the backing collection without a matching count-change call — the adapter's cached count, sizes and content size silently diverge from what is drawn, and the symptom appears later as a wrong row or a dead scroll region.
- Never add or remove items from inside `UpdateViewsHolder` — it binds data and nothing else; the adapter is mid-layout and the result is undefined.
- Never subscribe an event or call `GetComponent` inside `UpdateViewsHolder` — it runs on every recycle, so the subscription duplicates per reuse and the lookup is a per-recycle cost, per `performance-and-algorithms.md`'s Scripting & GC section.
- Never capture an item index in a listener closure — capture the views holder and read its current `ItemIndex` at invocation, or a recycled row acts on the item it used to show.
- Never parent a header, footer, ad or sticky element to Content — Content's children are the recycled pool; use a Viewport-level decorator instead.
- Never let a Layout Group or `ContentSizeFitter` own an item's size along the scrolling axis unless the adapter's twin-pass explicitly cooperates with it, per `ugui`'s ownership of those components.
- Never place OSA types in `Game.Core.*` — the package depends on `UnityEngine` and uGUI, which `coding-principles.md`'s Shared Core integrity section forbids there.
- Never write a workaround for odd clipping, WebGL stripping errors, early-`Awake` sizing, or truncated text before checking [known-issues-and-platform-caveats.md](references/known-issues-and-platform-caveats.md) — several are known engine or version bugs with a documented fix, and a hand-rolled workaround for one hides it.
- Never claim a recycling or pooling improvement without a Profiler measurement, per `performance-and-algorithms.md`'s Verification section.
- Never infer the namespace root from a code sample found online — most predate the v7.0 rename; read it out of the installed package, defaulting to `Com.ForbiddenByte.OSA.*`.
- Never treat the vendor's generated API site as current — it stops at v4.3, so anything added in 5.0+ is absent rather than contradicted, and some params members were re-cased at 5.0. For those, the vendored `.cs` in the project is the only authority, per [root-links.md](references/root-links.md).
- If the scroll orientation, expected item count, or size variability is unknown, ask rather than assume — each one changes which base classes and size strategy are correct.
