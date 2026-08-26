# Remote Content and Catalogs — sizing, pre-download, caching, content updates

Sources: [Distribute and update remote content](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/RemoteContentDistribution.html), [Addressables API](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/api/UnityEngine.AddressableAssets.Addressables.html), [Addressables Profiles](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/AddressableAssetsProfiles.html).
Covers: SKILL.md §4 — **"Size the download before the player is committed to it"**, **"Treat a catalog update as a step the player sees"**.

Everything that only exists under the AssetBundle content build system: remote
delivery, the download cache, and the post-launch content update flow. Where
the content is hosted is `tech-lead-sdk-platform`'s decision, and what tunable
data ships alongside it is `live-ops-content-pipeline`'s.

## Pre-download

| Call | Effect | Use when | Source |
|---|---|---|---|
| `GetDownloadSizeAsync(key)` | Returns the bytes still missing after the local cache, so zero means the whole download prompt can be skipped | Before showing any download UI, and before deciding whether a prompt is needed at all | [Distribute and update remote content](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/RemoteContentDistribution.html) |
| `DownloadDependenciesAsync(key)` | Fetches the content backing a key or label into the cache without loading it | Ahead of a transition the content gates, not at the moment it is first requested | [Distribute and update remote content](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/RemoteContentDistribution.html) |
| `handle.GetDownloadStatus()` | Download-specific bytes and percentage, which is what a progress bar needs; the handle's overall completion figure covers the chained operation instead | Driving any user-visible download progress | [AsyncOperationHandle](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/api/UnityEngine.ResourceManagement.AsyncOperations.AsyncOperationHandle-1.html) |
| `ClearDependencyCacheAsync(key)` | Drops cached bundles for a key so the next load refetches them | Forcing a redownload after a corrupt cache, or freeing device storage deliberately | [Distribute and update remote content](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/RemoteContentDistribution.html) |

## Caching behaviour

| Subject | What it decides | Source |
|---|---|---|
| Cache persists across sessions | A second launch downloads nothing, so a size check that returned a large number once returns zero afterwards — test the first-run path deliberately rather than on a device that has already cached | [Distribute and update remote content](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/RemoteContentDistribution.html) |
| Bundle granularity | A failed download restarts its bundle rather than resuming mid-file, so one very large bundle on a poor connection can fail indefinitely | [AssetBundle memory considerations](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/memory-assetbundles.html) |
| Device storage | Cached bundles occupy user storage until cleared; content that will never be needed again is worth clearing explicitly rather than accumulating | [Distribute and update remote content](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/RemoteContentDistribution.html) |

## Content update flow

| Step | What it decides | Source |
|---|---|---|
| Content state file from the shipped build | The update build is produced by diffing against the previous build's recorded state; without that file no content update can be built at all and the only path left is a full player release | [Distribute and update remote content](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/RemoteContentDistribution.html) |
| Update build | Produces only the changed content plus a new catalog, rather than rebuilding everything | [Distribute and update remote content](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/RemoteContentDistribution.html) |
| `CheckForCatalogUpdates()` | Reports which catalogs have a newer version available, without changing anything yet | [Addressables API](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/api/UnityEngine.AddressableAssets.Addressables.html) |
| `UpdateCatalogs(catalogs)` | Applies the newer catalogs, after which keys resolve to the new content | [Addressables API](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/api/UnityEngine.AddressableAssets.Addressables.html) |
| Remote load path | Comes from the active Profile rather than from code, so pointing a build at staging or production is a Profile selection | [Addressables Profiles](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/AddressableAssetsProfiles.html) |

**Critical caveat**: apply a catalog update at a boundary the player crosses
deliberately — a prompt, a restart, a return to the menu. Swapping catalogs
underneath a session that has already resolved content against the old one
produces failures whose cause is invisible from the symptom.

Nothing in this file applies to the Content Directory build system, which is
local-only and has no remote catalog path at all.
