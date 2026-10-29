# Load Calls, Awaiting, Release and Reference Counting

Sources (Addressables 4.0): manual `LoadingAddressableAssets.html`, `memory-assets.html`, `memory-assetbundles.html`, `optimization-tools.html`; API `Addressables`, `AssetReference`, `AsyncOperationHandle<T>`. Await/cancel mechanics belong to `unitask-async-programming`.

## Load calls
| Call | Use when |
|---|---|
| `LoadAssetAsync<T>(key)` | One known asset, by address or `AssetReference` |
| `LoadAssetsAsync<T>(keys, callback, mergeMode)` | A label's worth of content, or an intersection of labels |
| `InstantiateAsync(key, position, rotation, parent)` | Spawning a prefab whose instance lifetime drives the count |
| `LoadSceneAsync(key, mode, activateOnLoad)` | A scene addressed by key rather than Build Settings |
| `LoadResourceLocationsAsync(key)` | Check content exists for a key without loading |

## Merge modes
- `Union`: any key matches. A mistyped label contributes nothing and the call still succeeds.
- `Intersection`: every key must match ("enemies that are also bosses"); one non-matching key empties the result.
- `UseFirst`: matches of the first key that resolves; fallback chains where a variant beats a default.

## AssetReference
- Typed subclasses (`AssetReferenceGameObject`, `AssetReferenceSprite`, `AssetReferenceTexture`) reject wrong types at authoring time.
- `RuntimeKey` is what a build resolves against.
- `editorAsset` is Editor-only; code using it works in the Editor and fails in a build.
- `IsValid()` reports a live handle; use it to avoid a double release.
- `OperationHandle` is the handle from this reference's own load, so the release site need not keep one.

## Awaiting and failure
- `AsyncOperationHandle` is directly awaitable when UniTask and Addressables are both installed.
- A failed operation completes, it does not throw at the call site: check `Status` and `OperationException`.
- `WaitForCompletion()` blocks the calling thread; editor-tooling escape hatch only.
- `activateOnLoad: false` leaves the scene loaded but inert until `ActivateAsync()` on the returned scene instance. Converting a scene load to a task and chaining onto it takes activation timing out of your hands.
- `PercentComplete` covers the whole chained operation, not download progress; use `GetDownloadStatus()` for a download bar.

## Reference-counting contract
- Every load increments, every release decrements. An unmatched load produces no warning; the count just never reaches zero.
- Unload happens at zero, not at your release; another holder keeps it alive.
- AssetBundle system: an asset stays resident until its entire bundle reaches zero, so one long-lived reference pins everything packed beside it.
- Loading the same key from several call sites creates several references; track one handle per call site.

## Release APIs
| Call | Effect |
|---|---|
| `Release(handle)` | Decrements a loaded asset; load site kept the handle |
| `ReleaseInstance(gameObject)` | Destroys and decrements together; returns false and does nothing for an object Addressables did not create |
| `AssetReference.ReleaseAsset()` | Releases the load this reference performed |
| `UnloadSceneAsync(sceneInstance)` | Unloads an Addressable scene and releases its content |

## Failure modes
- `Object.Destroy` on an Addressables instance: GameObject goes, reference stays counted all session.
- Release missing on an early return or caught exception: the usual real leak (happy path is correct, failure path ships broken).
- Churn: releasing then reloading the same content, or content sharing its bundle, forces unload/reload cycles; decide lifetime scope (per level, session, app) before writing the release.
- Double release: guard with the reference's validity check, not defensive releasing.

## Diagnosis
- `AsyncOperationHandle.ReferenceCount`: one while in use, zero after release.
- Addressables Profiler module: separates a count that never returns to zero (leak) from one oscillating rapidly (churn).
