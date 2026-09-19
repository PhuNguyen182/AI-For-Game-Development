# Architecture and Concepts — build systems, addressing, groups, dependencies

Sources: [Choose a content build system](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/content-build-systems.html), [Addressables introduction](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/AddressableAssetsOverview.html), [Organizing Addressable assets](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/organize-addressable-assets.html), [Packing groups into AssetBundles](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/PackingGroupsAsBundles.html), [Asset dependencies](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/AssetDependencies.html).
Covers: SKILL.md §4 — **"Pick the content build system once, per project"**, **"Organize groups by what loads together, then pick the packing mode from that"**, **"Make a plain asset Addressable the moment a second Addressable references it"**.

What has to be settled before the first load call exists: which build system
the project uses, how content is grouped, and how a shared plain asset becomes
five copies without anything reporting it. Where the content is hosted is not
decided here — that is `tech-lead-sdk-platform`.

## Content build system

| Axis | Content Directory | AssetBundle | Source |
|---|---|---|---|
| Dependency tracking | Per asset, with shared plain assets deduplicated automatically | Per bundle, so a shared plain asset is copied into each referencing bundle | [Choose a content build system](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/content-build-systems.html) |
| Unload granularity | An asset frees once its own direct dependencies are freed | An asset stays resident until its whole bundle's count reaches zero | [Choose a content build system](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/content-build-systems.html) |
| Remote delivery | Local only — there is no remote path and no catalog update flow | Local and remote, and the only system that supports post-launch content updates | [Choose a content build system](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/content-build-systems.html) |
| Group to output | Groups build into one directory; grouping is organizational | Each group maps to bundles, so grouping has direct runtime consequences | [Choose a content build system](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/content-build-systems.html) |
| Editor requirement | Requires a recent Editor; unavailable on older versions | Available across every version this package supports | [Choose a content build system](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/content-build-systems.html) |

**Critical caveat**: the two systems are a project-wide choice, not a per-group
one. A project carrying both builds its shared dependencies twice, inflating
the shipped size while the Groups window still looks correct.

## Addressing model

| Term | What it decides | Source |
|---|---|---|
| Address | A stable name assigned to an asset, so code stops depending on where the file sits in the project | [Addressables introduction](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/AddressableAssetsOverview.html) |
| Label | A tag several assets share; loading by label pulls every match, which makes a mistyped label return nothing rather than fail | [Addressables introduction](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/AddressableAssetsOverview.html) |
| `AssetReference` | A serialized GUID, so renaming or moving the asset keeps the reference intact where a string address would break | [AssetReference](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/api/UnityEngine.AddressableAssets.AssetReference.html) |
| Catalog | The key-to-location map produced at content-build time; a key missing from the catalog fails at resolution, before any provider is involved | [Addressables introduction](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/AddressableAssetsOverview.html) |
| Group | The unit every Addressable belongs to, carrying the schema that decides packing and whether the group is built at all | [Organizing Addressable assets](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/organize-addressable-assets.html) |

## Grouping strategy

| Principle | Use when | Source |
|---|---|---|
| Concurrent usage | Assets are needed at the same moment — everything one level loads — so one load brings in exactly what the transition needs | [Organizing Addressable assets](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/organize-addressable-assets.html) |
| Logical entity | A self-contained thing owns its model, textures, animations and audio, so its lifetime is managed as one unit | [Organizing Addressable assets](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/organize-addressable-assets.html) |
| Type based | Content does not cluster by level or entity — all music, all UI atlases — and the alternative is arbitrary groups | [Organizing Addressable assets](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/organize-addressable-assets.html) |

## Packing modes (AssetBundle system)

| Mode | Effect | Trade-off | Source |
|---|---|---|---|
| Pack Together | The whole group becomes one bundle | Loading one asset brings the entire bundle into memory, and nothing in it unloads until every reference is gone | [Packing groups into AssetBundles](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/PackingGroupsAsBundles.html) |
| Pack Separately | Each asset becomes its own bundle | Finest unload granularity and resumable downloads, at the cost of per-bundle catalog overhead and many more requests | [Packing groups into AssetBundles](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/PackingGroupsAsBundles.html) |
| Pack Together by Label | Assets sharing a label set become one bundle each | A middle ground that only works if labels already describe how content is used | [Packing groups into AssetBundles](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/PackingGroupsAsBundles.html) |

## Dependency duplication

| Case | Consequence | Source |
|---|---|---|
| Addressable references another Addressable | Packed by the referenced asset's own group settings, and shared cleanly however the two are grouped | [Asset dependencies](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/AssetDependencies.html) |
| One Addressable references a plain asset | The plain asset rides along in that bundle, which is correct and costs nothing extra | [Asset dependencies](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/AssetDependencies.html) |
| Two or more Addressables reference the same plain asset | Under the AssetBundle system it is copied into every referencing bundle — several runtime instances of one project asset, visible only as unexplained build size | [Asset dependencies](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/AssetDependencies.html) |
| The fix | Make the shared asset Addressable in its own right so it becomes one explicit shared dependency; the Analyze window reports the duplicates before a build ships | [Optimization tools](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/optimization-tools.html) |
