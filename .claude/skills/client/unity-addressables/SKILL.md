---
name: unity-addressables
description: >
  Technique for runtime asset/scene loading and content delivery via Unity's
  Addressables package (`UnityEngine.AddressableAssets`/
  `UnityEngine.ResourceManagement`) — `Addressables.LoadAssetAsync`/
  `LoadAssetsAsync`/`InstantiateAsync`/`LoadSceneAsync`, reference-counted
  `Release`/`ReleaseInstance` discipline, `GetDownloadSizeAsync`/
  `DownloadDependenciesAsync` pre-downloading, `AssetReference` fields,
  groups/labels, and remote content catalogs/updates — awaited via UniTask's
  built-in `AsyncOperationHandle`/`AsyncOperationHandle<T>` support
  (`Cysharp.Threading.Tasks.Addressables`, auto-enabled once both packages
  are installed). Use this for loading/instantiating any asset or scene that
  should be addressed by key/label/`AssetReference` instead of a hard scene
  reference or a `Resources` folder, and for pre-downloading or updating
  remote content. Do not use this for the generic mechanics of awaiting,
  cancelling, or `.Preserve()`-ing an async operation — that's
  `unitask-async-programming`; this skill only covers which Addressables
  call to make and its Addressables-specific release timing. Do not use
  this to design the pooling strategy layered on top of instantiated
  GameObjects — that's `performance-and-algorithms.md`'s pooling guidance;
  this skill covers acquiring/releasing the Addressable handle behind a
  pooled object, not the pool itself. Do not use this for texture/audio
  import compression settings — that's `performance-and-algorithms.md`'s
  Assets & memory footprint section / Technical Artist; this skill assumes
  the asset's import settings are already correct and only covers how it's
  addressed and loaded at runtime. Do not use this to decide the
  infrastructure behind remote-config/economy/event content cadence
  (Firebase Remote Config, PlayFab Title Data) — that's
  `live-ops-content-pipeline`, a tunable-data concern entirely separate from
  Addressables' binary asset/AssetBundle delivery. Do not use this to
  select or contract a specific CDN/cloud hosting vendor for remote content
  — that vendor decision belongs to `tech-lead-sdk-platform`; this skill
  covers the Addressables-side catalog/download API once a host is chosen.
  Never use Addressables APIs inside `Game.Core.*` — the package depends on
  `UnityEngine`; Shared Core receives already-resolved data/references from
  `Game.Client.*`, it never calls into Addressables itself.
---

# Unity Addressables — Runtime Asset & Scene Loading

Sources: [Addressables Manual](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/index.html), [Addressables API reference](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/api/index.html).

## 1. Objective
Load, instantiate, and release addressable assets/scenes correctly — right content-build-system choice, right reference-counting discipline, right pre-download strategy for remote content — awaited through UniTask instead of a raw callback or a blocking `WaitForCompletion()`, without leaking a handle, double-releasing one, or bypassing the reference count with a raw `Destroy()`.

## 2. Role
Act as the asset-streaming specialist for the client track — the tool Unity Engineer reaches for whenever a prefab, scene, or other asset should be loaded by address/label instead of a hard reference, a `Resources` folder call, or a raw `AssetBundle` API.

## 3. When to invoke this skill
- Replacing a `Resources.Load`/hard scene reference/direct prefab reference with an addressed load (`AssetReference` field, or a string key/label) so the asset can be reorganized, moved to remote delivery, or updated post-launch without a code change.
- Instantiating a prefab via `Addressables.InstantiateAsync` instead of `Object.Instantiate` on an already-loaded reference, so Addressables' own reference counting tracks the instance's underlying asset correctly.
- Loading/unloading an Addressable scene via `Addressables.LoadSceneAsync`/`UnloadSceneAsync` (additive or single, with `activateOnLoad` control) instead of `SceneManager.LoadScene` for a scene that's addressed rather than build-index-referenced.
- Pre-downloading content before it's needed — `GetDownloadSizeAsync` to size a progress bar, `DownloadDependenciesAsync` to actually fetch it — ahead of a level transition or before showing a "download required" prompt.
- Deciding between the two content build systems Addressables 4.0 offers: the newer **Content Directory** system (local-only content, simpler workflow, requires Unity 6.6+) vs. the classic **AssetBundle**-based system (required for remote content distribution, content updates post-launch, and pre-6.6 Unity) — this choice is made once per project and should not be mixed within the same project.
- Checking/applying a remote content catalog update (`CheckForCatalogUpdates`/`UpdateCatalogs`) for a live game shipping content post-launch, when the project uses the AssetBundle content build system.
- Negative trigger: writing the generic cancellation/`.Preserve()`/`PlayerLoopTiming` mechanics around the await itself — that's `unitask-async-programming`.
- Negative trigger: designing an object pool for the instantiated GameObjects — that's `performance-and-algorithms.md`'s pooling guidance; this skill only governs acquiring and releasing the underlying Addressable handle.
- Negative trigger: texture/audio compression or import settings — that's `performance-and-algorithms.md`'s Assets & memory footprint section / Technical Artist.
- Negative trigger: choosing remote-config/economy-tuning infrastructure — that's `live-ops-content-pipeline`, a different concern from binary asset delivery.
- Negative trigger: contracting a specific CDN/cloud hosting vendor for remote content — that's `tech-lead-sdk-platform`'s call.
- Negative trigger: any `Game.Core.*` code — Addressables depends on `UnityEngine`; Shared Core only ever receives the already-resolved object/data from `Game.Client.*`.

## 4. How to use this skill
1. **Pick the content build system deliberately, once, per project.** Content Directory for local-only content on Unity 6.6+ (simpler workflow, per-asset dependency tracking, assets release as soon as their direct dependencies are freed); the AssetBundle-based system whenever the project needs remote content distribution, post-launch content updates, or supports pre-6.6 Unity. Never mix both content build systems in the same project — Addressables will build shared dependencies twice, inflating build size and risking asset duplication.
2. **Address assets through `AssetReference` fields for anything wired in the Inspector**, and through string keys/labels only for runtime-determined content (a key built from data, or "load everything with label X") — an `AssetReference` gives compile-time-ish safety (`AssetReferenceGameObject`, `AssetReferenceSprite`, etc.) that a bare string key doesn't.
3. **Await through UniTask's native support, not a blocking call.** Both `AsyncOperationHandle` and `AsyncOperationHandle<T>` are directly awaitable once the Addressables and UniTask packages are both installed (`Cysharp.Threading.Tasks.Addressables` auto-enables) — `var asset = await Addressables.LoadAssetAsync<GameObject>(reference);` reads cleanly and follows `unitask-async-programming`'s cancellation/`.Preserve()` guidance for anything beyond the simplest single-await case. Never call `handle.WaitForCompletion()` on a hot path or the main thread's steady-state code — it blocks synchronously and defeats the entire point of an async load.
4. **Do not chain `Addressables.LoadSceneAsync(...).ToUniTask()` uncritically.** UniTask's own documentation flags scene-loading timing as a special case; prefer awaiting the handle directly (`await Addressables.LoadSceneAsync(key, LoadSceneMode.Additive, activateOnLoad: false)`) and controlling activation explicitly via the returned `SceneInstance`'s `ActivateAsync()` at the exact point the scene should actually go live, rather than trusting an implicit `.ToUniTask()` chain to time activation correctly.
5. **Track every handle you get back and release it exactly once, on every code path.** `Addressables.Release(handle)` for a loaded asset, `Addressables.ReleaseInstance(gameObject)` (or the returned handle) for something created via `InstantiateAsync` — never call `Object.Destroy()` on an Addressables-instantiated GameObject directly; that bypasses the reference count entirely and leaks the underlying asset/bundle for the rest of the session. This is the Addressables-specific instance of `coding-principles.md`'s Correctness boundaries rule about cleaning up on every `OnDisable`/`OnDestroy` path, including an early return or an exception.
6. **Pre-download before a hard requirement, not during it.** Use `GetDownloadSizeAsync(key)` to know how much needs fetching (drive a progress bar, or skip the download UI entirely if it returns 0), then `DownloadDependenciesAsync(key)` ahead of the actual level/content transition — don't let a player discover a multi-hundred-MB download only once they've already hit "Play."
7. **Use merge modes (`Union`/`Intersection`/`Difference`) deliberately when loading by multiple labels/keys** — state which merge semantics the load actually needs rather than accepting the default and being surprised by which assets came back.
8. **Treat a remote catalog update as a deliberate, user-visible step**, not a silent background swap — `CheckForCatalogUpdates` then `UpdateCatalogs` only for content build systems that support remote catalogs (the AssetBundle system), and surface the download/update state to the player rather than silently invalidating already-loaded content underneath a running session.
9. **Verify with the Profiler / Addressables' own event viewer** when a memory or reference-count issue is suspected, rather than assuming a `Release` call alone fixed it — an asset with a still-outstanding reference elsewhere in the project won't actually unload just because one caller released its handle.

## 5. Specific goals / tasks this skill performs
- Converting a `Resources.Load`/hard-referenced asset or scene to an addressed `AssetReference`/key-based load.
- Loading, instantiating, and correctly releasing assets and Addressable scenes with UniTask-awaited calls.
- Pre-download flows via `GetDownloadSizeAsync`/`DownloadDependenciesAsync` ahead of a content-gated transition.
- Choosing the content build system (Content Directory vs. AssetBundle) for a project's actual remote-content needs.
- Checking and applying remote catalog updates for live content post-launch.
- Auditing reference-counting correctness — no `Object.Destroy()` on an Addressables instance, no missing `Release`/`ReleaseInstance` on any code path.
- Out of scope: generic async/cancellation mechanics (`unitask-async-programming`), object pooling design (`performance-and-algorithms.md`), import/compression settings (`performance-and-algorithms.md`/Technical Artist), remote-config/economy infrastructure (`live-ops-content-pipeline`), CDN vendor selection (`tech-lead-sdk-platform`), any `Game.Core.*` usage.

## 6. Output format
```
## Addressables Work — <asset/scene/system name>
- Content build system: Content Directory / AssetBundle — rationale
- Addressing: AssetReference field / string key / label(s) — merge mode if multiple
- Load call: LoadAssetAsync / LoadAssetsAsync / InstantiateAsync / LoadSceneAsync
- Awaited via: UniTask native AsyncOperationHandle support — cancellation/.Preserve() per unitask-async-programming
- Pre-download: GetDownloadSizeAsync + DownloadDependenciesAsync — yes/no, trigger point
- Release path: Release / ReleaseInstance — confirmed on every code path (including early return/exception)
- Remote catalog handling: CheckForCatalogUpdates/UpdateCatalogs — applicable/not applicable
- Layer: Game.Client.* (never Game.Core.*)
- Known limitations: <...>
```

## 7. Examples
**Example 1**
- Input: an enemy prefab is currently a hard `[SerializeField] GameObject` reference that should instead be addressable so it can move to remote content later.
- Output: replaced the field with `[SerializeField] AssetReferenceGameObject enemyPrefab`, instantiated via `await enemyPrefab.InstantiateAsync(spawnPoint.position, spawnPoint.rotation)`, tracked the returned handle per spawned instance, released each via `Addressables.ReleaseInstance(handle)` in the pooling system's despawn path instead of `Object.Destroy()`.

**Example 2**
- Input: a level transition currently just calls `SceneManager.LoadScene`, but the target scene's assets are large enough that players on mobile networks should see a download progress bar first.
- Output: computed `await Addressables.GetDownloadSizeAsync(sceneKey)`; if greater than zero, showed a progress UI driven by `Addressables.DownloadDependenciesAsync(sceneKey)`'s `GetDownloadStatus()` polled via `unitask-async-programming`'s timing guidance; only then called `await Addressables.LoadSceneAsync(sceneKey, LoadSceneMode.Single)`.

**Example 3**
- Input: "just call `Object.Destroy()` on the Addressables-instantiated prop when it despawns, it's simpler."
- Output: declined — `Object.Destroy()` bypasses Addressables' reference count entirely, leaking the underlying asset/bundle reference for the rest of the session; used `Addressables.ReleaseInstance(...)` instead, which both destroys the GameObject and correctly decrements the reference count.

## 8. Edge cases & guardrails
- Never call `Object.Destroy()` directly on a GameObject created via `Addressables.InstantiateAsync` — always `Addressables.ReleaseInstance(...)`, or the reference count leaks.
- Never leave a `LoadAssetAsync`/`LoadAssetsAsync` handle un-released on any code path — including an early return or a caught exception — per the same discipline `coding-principles.md` already requires for coroutines and event subscriptions.
- Never call `handle.WaitForCompletion()` in steady-state/hot-path code — it blocks the main thread synchronously; reserve it, if ever, for a narrow editor/tooling context, not runtime gameplay code.
- Never mix the Content Directory and AssetBundle content build systems in the same project — shared dependencies build twice, inflating build size and risking duplication.
- Never chain `LoadSceneAsync(...).ToUniTask()` without checking scene-activation timing — prefer awaiting the handle directly with `activateOnLoad: false` and an explicit `ActivateAsync()` call at the right moment.
- Never silently swap a remote catalog under a running session — surface the update/download state to the player deliberately.
- Never assume a single `Release` call frees the underlying asset if another caller still holds an outstanding reference to it — reference counting is per-handle, not per-asset-name.
