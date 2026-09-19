# Root Links — OSA (Optimized ScrollView Adapter) 6.0–7.0

Source: the root pages listed below, plus the vendor-supplied OSA 6.0–7.0
manual (a licensed Google Doc shipped with the asset, not a public URL).
Covers: the whole skill — provenance and version anchor for every file in
this folder.

Anchors every link and every namespace in this folder to OSA **6.0–7.0**.
OSA is a paid Unity Asset Store asset, so its source sits in the project
rather than on a package registry, and the installed version is a fact to
read out of that source.

## The namespace root — `Com.ForbiddenByte.OSA.*`

**Every namespace this skill names is written against `Com.ForbiddenByte.OSA.*`,
the current root.** It has been in force since v7.0.0 (2023-10-10), when the
vendor's rebrand from **The Fallen Games** to **Forbidden Byte** was carried
into the code.

| Version | Namespace root | Source |
|---|---|---|
| 7.0.0 and later — **the default** | `Com.ForbiddenByte.OSA.*` | [Changelog](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/Changelog.txt) |
| 6.x and earlier — legacy | `Com.TheFallenGames.OSA.*` | [Changelog](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/Changelog.txt) (7.0.0 entry: "Namespaces changed from Com.TheFallenGames to Com.ForbiddenByte") |

The rename is mechanical: swapping the root is the whole difference, and the
folder structure moved with it while the obsolete `IInitializable8` and
`Singleton8` types were dropped. Every class and member documented in this
folder is the same on both sides, so a 6.x project needs the legacy root
substituted and nothing else changed.

Two consequences worth holding onto: any sample, tutorial or forum answer
published before late 2023 carries the legacy root and will not compile as
pasted, and `thefallengames.com` still serves the same documentation tree as
`forbiddenbyte.com` — prefer the `forbiddenbyte.com` form and treat a
`thefallengames.com` link found elsewhere as the same page.

## Roots

| Root | Holds | Source |
|---|---|---|
| Generated API reference — **v4.3 only**, see the caveat below | Declaration syntax for everything that existed in 4.3, under the current namespace root | [OSA API docs](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/doc/43/html/303f106d-29ab-b975-b0e1-9120154c4aee.htm) (`Com.ForbiddenByte.OSA.Core` namespace index) |
| **The vendored `.cs` sources in the project** | The only authority for anything added after 4.3 — which is much of this skill's surface | Ships with the asset; the vendor's [doc index](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/doc/) states for 5.0 and up: "Code reference not needed because the code itself is documented and all of its sources are included" |
| Manual 6.0–7.0 | Usage/implementation flow, wizard, grid/table pointers, known issues, FAQ | [OSA 6.0–7.0 Complete Manual](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| Demos manual | The demo scenes each technique is exemplified in, plus grid and TableView documentation | [OSA Demos manual](https://docs.google.com/document/d/1FeIaLsvhHCRFQg8BaSBxyoOEYgzZjMoYkevv1l1eJ-0/edit), [OSA 5.0–7.0 Demo Scenes Introduction](https://forbiddenbyte.com/blog/osa-demo-scenes/) |
| Changelog | Which version introduced or renamed a member — the tiebreaker when an API is missing | [Changelog.txt](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/Changelog.txt) |
| Migration guides | Incremental upgrade steps; they must be applied one version at a time, never skipped | [5.x → 6.0](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/Migration%20guide%20from%205.x%20to%206.0.txt), [5.0 → 5.1](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/Migration%20guide%20from%205.0%20to%205.1.txt), [4.3 → 5.0](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/Migration%20guide%20from%204.3%20to%205.0.txt) |
| Asset Store listing | Distribution, current published version, Editor compatibility | [Optimized ScrollView Adapter](https://assetstore.unity.com/packages/tools/gui/optimized-scrollview-adapter-68436) |
| Quick start | The wizard walkthrough, as video | [OSA Quick Start Tutorial](https://forbiddenbyte.com/blog/osa-quick-start-tutorial/) |

## Version landmarks inside the 6.0–7.0 range

Reach for these when an API named in this folder does not exist in the
installed package — the answer is usually that the project predates it.

| Version | Landmark | Source |
|---|---|---|
| 6.0.1 | New Input System support; `ForceRebuildLayoutNow()`; OSA folder relocatable via a path-tracker asset | [Changelog](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/Changelog.txt) |
| 6.1.0 | `OSA.ForceUpdateVisibleItems()` added alongside `ForceUpdateViewsHolderIfVisible()` | [Changelog](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/Changelog.txt) |
| 6.4.0 | Looping `SmoothScrollTo` takes the shortest path; `ForceUpdateCellViewsHolderIfVisible` added to `GridAdapter` | [Changelog](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/Changelog.txt) |
| 6.5.4 | `LRUCachingPool` added (preferred over `FIFOCachingPool`); `OnBeforeRecycleOrDisable(int newItemIndex)` on the views holder | [Changelog](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/Changelog.txt) |
| 7.0.0 | Namespace + folder rebrand; `IInitializable8` and `Singleton8` removed | [Changelog](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/Changelog.txt) |

## Topic → file map

| Topic | File | Source |
|---|---|---|
| Core triad, views-holder contract, `Init`/`Start` ordering, wizard | [core-classes-and-lifecycle.md](core-classes-and-lifecycle.md) | [API docs](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/doc/43/html/303f106d-29ab-b975-b0e1-9120154c4aee.htm), [Manual](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| Count changes, DataHelpers, position preservation | [data-and-count-changes.md](data-and-count-changes.md) | [API docs](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/doc/43/html/303f106d-29ab-b975-b0e1-9120154c4aee.htm), [Manual](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| Item sizing, ContentSizeFitter twin-pass, runtime resize | [variable-item-sizes.md](variable-item-sizes.md) | [Manual](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| Grid and TableView adapters | [grid-and-table.md](grid-and-table.md) | [Demos manual](https://docs.google.com/document/d/1FeIaLsvhHCRFQg8BaSBxyoOEYgzZjMoYkevv1l1eJ-0/edit) |
| Scrolling, snapping, scrollbars, looping | [scrolling-navigation-and-snapping.md](scrolling-navigation-and-snapping.md) | [Manual](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| Pooling, `Params.optimization`, caching pools | [pooling-and-performance.md](pooling-and-performance.md) | [Manual](https://forbiddenbyte.com/blog/osa-complete-manual/), [Changelog](https://forbiddenbyte.com/unityassetstore/optimizedscrollviewadapter/Changelog.txt) |
| Item input, decorators, sticky overlays | [item-interaction-and-decorators.md](item-interaction-and-decorators.md) | [Manual](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| Engine/version bugs and platform caveats | [known-issues-and-platform-caveats.md](known-issues-and-platform-caveats.md) | [Manual](https://forbiddenbyte.com/blog/osa-complete-manual/) |

## Disclosed gaps

| Area | Issue |
|---|---|
| **The generated API reference stops at v4.3** | `/doc/43/` is the OSA **4.3** build, not a doc revision number — its own `C.OSA_VERSION_STRING` reads `"4.3"`, and the vendor's version selector offers builds only up to 4.3 (`/doc/50/`, `/doc/70/` and friends return 404). Its pages *were* updated to the current `Com.ForbiddenByte` root, which makes it look current when it is not. Treat it as: authoritative declaration syntax for anything that existed in 4.3, and **silent — not contradicting — about everything added in 5.0+**. Roughly a third of the surface this skill covers falls in that gap: the twin-pass forced-update family, buffered recycleable items, `Time`/`DeltaTime`, `UseUnscaledTime`, the `Animation` config chain, the pool-persistence flags, `InitWithExistingRoot`, `OSAContentDecorator`, `LRUCachingPool`, `OSASnapperFocusedItemInfo`, and all of TableView. |
| **Casing changed at 5.0 for some params members** | Several fields went lowercase → PascalCase after 4.3: the API site shows `recycleBinCapacity` and `itemPrefab`, while the 6.0–7.0 manual uses `RecycleBinCapacity` and `ItemPrefab`. This skill writes the **6.0–7.0 (PascalCase) forms** throughout. On a 4.x project, expect the lowercase spelling instead. |
| Verifying a 5.0+ member | Read the vendored `.cs` in the project — the asset ships full sources. Changelog and manual name these members but never publish a declaration, so a signature taken from prose alone is a guess. |
| Exact parameter defaults | Optional-parameter defaults (`contentPanelEndEdgeStationary`, `keepVelocity`, `ScrollTo`'s normalized offsets) are stated at the level the API pages and manual give them; confirm an exact default against the installed package's IntelliSense before relying on it silently. |
| Grid and TableView depth | The manual delegates both to the Demos manual rather than documenting them itself, so [grid-and-table.md](grid-and-table.md) is deliberately a routing layer over the grid demo scene rather than a full API distillation. |
| Playmaker support | OSA ships Playmaker actions under its own plugin-support folder. Out of scope for this skill — it targets C# implementations, per [SKILL.md](../SKILL.md)'s §1. |
| Version pinning | Unlike a UPM package, OSA has no version in its documentation URLs, so these roots always serve the newest published version. When the project sits on an older 6.x, the changelog table above is what reconciles the two. |
