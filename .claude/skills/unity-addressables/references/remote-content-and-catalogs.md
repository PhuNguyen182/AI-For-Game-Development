# Remote Content and Catalogs

Sources (Addressables 4.0): manual `RemoteContentDistribution.html`, `AddressableAssetsProfiles.html`, `memory-assetbundles.html`; API `Addressables`, `AsyncOperationHandle<T>`. AssetBundle system only: Content Directory is local-only with no remote catalog path. Hosting choice is `sdk-platform-engineer`'s; tunable data is `live-ops-content-pipeline`'s.

## Pre-download
| Call | Use when |
|---|---|
| `GetDownloadSizeAsync(key)` | Before any download UI; bytes still missing after cache, zero means skip the prompt |
| `DownloadDependenciesAsync(key)` | Ahead of a transition the content gates, not at first request |
| `handle.GetDownloadStatus()` | Download bytes and percentage for a progress bar |
| `ClearDependencyCacheAsync(key)` | Force a redownload after a corrupt cache, or free storage deliberately |

## Caching
- The cache persists across sessions: a size check returning a large number once returns zero later. Test the first-run path on a device that has not cached.
- A failed download restarts its bundle rather than resuming, so one very large bundle on a poor connection can fail indefinitely.
- Cached bundles occupy user storage until cleared.

## Content update flow
1. Preserve the content state file from the shipped build. Without it no content update can be built; the only path left is a full player release.
2. Update build produces only changed content plus a new catalog.
3. `CheckForCatalogUpdates()` reports newer catalogs without changing anything.
4. `UpdateCatalogs(catalogs)` applies them; keys then resolve to new content.
5. The remote load path comes from the active Profile, not code.

Apply a catalog update at a boundary the player crosses deliberately (prompt, restart, return to menu). Swapping catalogs under a session that resolved against the old one fails with no visible cause.
