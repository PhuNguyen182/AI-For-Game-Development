# Reference Counting — the load and release contract, leaks, and churn

Sources: [Memory management overview](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/MemoryManagement.html), [Managing asset memory](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/memory-assets.html), [AssetBundle memory considerations](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/memory-assetbundles.html), [Addressables API](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/api/UnityEngine.AddressableAssets.Addressables.html).
Covers: SKILL.md §4 — **"Mirror every load with exactly one release, on every code path"**, **"Decide each asset's lifetime scope up front rather than releasing reactively"**.

The contract that decides whether memory is ever reclaimed, and the two ways
it is broken: a release that never happens, and a release that happens too
eagerly. General GC and allocation discipline is
`performance-and-algorithms.md`'s; what is here is the Addressables count.

## The contract

| Rule | Consequence | Source |
|---|---|---|
| Every load increments, every release decrements | An unmatched load is not an error and produces no warning — the count simply never returns to zero | [Managing asset memory](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/memory-assets.html) |
| Unload happens at zero, not at release | Releasing your handle frees nothing while another caller still holds one into the same content | [Managing asset memory](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/memory-assets.html) |
| Bundle-level unload | Under the AssetBundle system an asset stays resident until its entire bundle reaches zero, so one long-lived reference pins everything packed beside it | [AssetBundle memory considerations](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/memory-assetbundles.html) |
| One handle per logical thing loaded | Loading the same key from several call sites creates several references; tracking one handle per call site is what keeps the releases matched | [Managing asset memory](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/memory-assets.html) |

## Release APIs

| Call | Effect | Use when | Source |
|---|---|---|---|
| `Release(handle)` | Decrements the count for a loaded asset | The load site kept the handle | [Addressables API](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/api/UnityEngine.AddressableAssets.Addressables.html) |
| `ReleaseInstance(gameObject)` | Destroys the instance and decrements together; returns false and does nothing when handed an object Addressables did not create | Despawning anything created by `InstantiateAsync` | [Addressables API](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/api/UnityEngine.AddressableAssets.Addressables.html) |
| `AssetReference.ReleaseAsset()` | Releases the load this reference itself performed | The reference owns the handle, so no separate handle field exists | [AssetReference](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/api/UnityEngine.AddressableAssets.AssetReference.html) |
| `UnloadSceneAsync(sceneInstance)` | Unloads an Addressable scene and releases its content | Tearing down an additively loaded scene | [Addressables API](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/api/UnityEngine.AddressableAssets.Addressables.html) |

## Failure modes

| Anti-pattern | What actually happens | Source |
|---|---|---|
| `Object.Destroy` on an Addressables instance | The GameObject leaves the scene and its reference stays counted for the rest of the session — a permanent leak that looks exactly like correct cleanup | [Managing asset memory](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/memory-assets.html) |
| Release missing on an early return or a caught exception | The common shape of a real leak, since the happy path is usually correct and the failure path is what ships broken | [Managing asset memory](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/memory-assets.html) |
| Asset churn | Releasing then reloading the same content, or content sharing its bundle, forces an unload and reload cycle that a decided lifetime scope avoids entirely | [Managing asset memory](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/memory-assets.html) |
| Double release | Decrementing a count already at zero on a handle that has been invalidated; guard with the reference's validity check rather than releasing defensively | [AssetReference](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/api/UnityEngine.AddressableAssets.AssetReference.html) |

## Diagnosis

| Tool | What it settles | Source |
|---|---|---|
| `AsyncOperationHandle.ReferenceCount` | Whether a specific handle's count is what the code intends at a chosen moment — one while in use, zero after release | [AsyncOperationHandle](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/api/UnityEngine.ResourceManagement.AsyncOperations.AsyncOperationHandle-1.html) |
| Addressables Profiler module | Distinguishes a count that never returns to zero from one oscillating rapidly — a leak from churn — across a real play session | [Optimization tools](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/optimization-tools.html) |

**Critical caveat**: choose the lifetime scope — per level, per session, per
app — before writing the release, not after a leak appears. A release placed
by reflex at despawn is the usual origin of churn, and a release omitted from
an exception path is the usual origin of a leak.
