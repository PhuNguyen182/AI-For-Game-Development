# Load Calls and Awaiting — call shapes, merge modes, AssetReference, failure surfacing

Sources: [Load Addressable assets](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/LoadingAddressableAssets.html), [Addressables API](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/api/UnityEngine.AddressableAssets.Addressables.html), [AssetReference](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/api/UnityEngine.AddressableAssets.AssetReference.html), [AsyncOperationHandle](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/api/UnityEngine.ResourceManagement.AsyncOperations.AsyncOperationHandle-1.html).
Covers: SKILL.md §4 — **"Address Inspector-wired assets through `AssetReference` and reserve string keys for runtime-resolved content"**, **"Await the handle directly rather than blocking on `WaitForCompletion()`"**, **"Control scene activation explicitly rather than letting the load perform it"**.

Which call to make, what its arguments actually change, and how a load reports
that it failed. Cancellation, timing, and multi-await mechanics around the
await itself belong to `unitask-async-programming`; what is here is
Addressables-specific. Where the matching release goes is in
[loading-and-reference-counting.md](loading-and-reference-counting.md).

## Load calls

| Call | Effect | Use when | Source |
|---|---|---|---|
| `LoadAssetAsync<T>(key)` | Resolves one key and loads one asset | A single known asset, by address or `AssetReference` | [Load Addressable assets](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/LoadingAddressableAssets.html) |
| `LoadAssetsAsync<T>(keys, callback, mergeMode)` | Resolves several keys or labels into a list, with the merge mode deciding which matches survive | Loading a whole label's worth of content, or an intersection of two labels | [Load Addressable assets](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/LoadingAddressableAssets.html) |
| `InstantiateAsync(key, position, rotation, parent)` | Loads and instantiates in one operation, with Addressables tracking the instance | Spawning a prefab whose instance lifetime should drive the reference count | [Addressables API](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/api/UnityEngine.AddressableAssets.Addressables.html) |
| `LoadSceneAsync(key, mode, activateOnLoad)` | Streams an Addressable scene, additively or replacing | A scene addressed by key rather than listed in Build Settings | [Load Addressable assets](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/LoadingAddressableAssets.html) |
| `LoadResourceLocationsAsync(key)` | Resolves a key to locations without loading anything | Checking whether content exists for a key before committing to a load or a download | [Addressables API](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/api/UnityEngine.AddressableAssets.Addressables.html) |

## Merge modes

| Mode | Result set | Consequence | Source |
|---|---|---|---|
| `Union` | Everything matching any key | A mistyped label contributes nothing and the call still succeeds, so the shortfall shows up as missing content rather than an error | [Load Addressable assets](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/LoadingAddressableAssets.html) |
| `Intersection` | Only assets matching every key | The usual choice for "enemies that are also bosses"; one non-matching key empties the result entirely | [Load Addressable assets](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/LoadingAddressableAssets.html) |
| `UseFirst` | Matches of the first key that resolves to anything | Fallback chains, where a variant should win over a default if it exists | [Load Addressable assets](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/LoadingAddressableAssets.html) |

## AssetReference

| Member | Effect | Source |
|---|---|---|
| Typed subclasses | `AssetReferenceGameObject`, `AssetReferenceSprite`, `AssetReferenceTexture` and the generic base restrict what the Inspector will accept, catching a wrong-type assignment at authoring time instead of at load | [AssetReference](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/api/UnityEngine.AddressableAssets.AssetReference.html) |
| `RuntimeKey` | The identifier actually used at runtime — this is what a build resolves against | [AssetReference](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/api/UnityEngine.AddressableAssets.AssetReference.html) |
| `editorAsset` | Editor-only convenience that returns the asset without loading it; it has no runtime equivalent, so code depending on it works in the Editor and fails in the build | [AssetReference](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/api/UnityEngine.AddressableAssets.AssetReference.html) |
| `IsValid()` | Reports whether the reference currently holds a live operation handle, which is how a double-release is avoided | [AssetReference](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/api/UnityEngine.AddressableAssets.AssetReference.html) |
| `OperationHandle` | The handle from this reference's own load, so the release site does not need to have kept one separately | [AssetReference](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/api/UnityEngine.AddressableAssets.AssetReference.html) |

## Awaiting and failure

| Subject | What it decides | Source |
|---|---|---|
| Direct await | `AsyncOperationHandle` and its generic form are awaitable once UniTask and Addressables are both installed, so no conversion call is needed | [AsyncOperationHandle](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/api/UnityEngine.ResourceManagement.AsyncOperations.AsyncOperationHandle-1.html) |
| `Status` and `OperationException` | A failed operation completes rather than throwing at the call site, so a key that resolves to nothing reads as a load returning nothing until the status is checked | [AsyncOperationHandle](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/api/UnityEngine.ResourceManagement.AsyncOperations.AsyncOperationHandle-1.html) |
| `WaitForCompletion()` | Blocks the calling thread until the operation finishes — it removes the async benefit entirely and is an editor-tooling escape hatch, not a runtime pattern | [AsyncOperationHandle](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/api/UnityEngine.ResourceManagement.AsyncOperations.AsyncOperationHandle-1.html) |
| `activateOnLoad: false` | Leaves the streamed scene loaded but inert until `ActivateAsync()` on the returned scene instance, which is what lets a loading screen finish on its own terms | [Load Addressable assets](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/LoadingAddressableAssets.html) |
| `PercentComplete` | Progress across the whole chained operation, not download progress; a download bar driven from it moves in ways the download does not | [AsyncOperationHandle](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/api/UnityEngine.ResourceManagement.AsyncOperations.AsyncOperationHandle-1.html) |

**Critical caveat**: converting a scene load into a task and chaining onto it
puts activation timing outside your control. Await the handle with
`activateOnLoad` false and call `ActivateAsync()` at the chosen moment instead.
