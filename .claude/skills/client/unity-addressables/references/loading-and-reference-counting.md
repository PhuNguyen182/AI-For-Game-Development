# Loading, Instantiating, and Reference-Counting Discipline

Covers SKILL.md's "optimal calling" guidance — how to call the load/instantiate/scene APIs and how the reference-counting contract actually works underneath them.

## The reference-counting contract

- Every successful load (`LoadAssetAsync`, `LoadAssetsAsync`, `InstantiateAsync`, `LoadSceneAsync`, or an `AssetReference`'s own load methods) **increments a reference count** on the resolved location/bundle. Every matching release (`Addressables.Release(handle)`, `Addressables.ReleaseInstance(...)`, `AssetReference.ReleaseAsset()`/`ReleaseInstance()`) **decrements it**.
- An asset only actually unloads once its reference count reaches zero — and for the AssetBundle system, an individual asset inside a bundle doesn't unload until the **entire bundle's** reference count reaches zero, even if that one asset's own local count is already zero. Releasing "your" handle doesn't guarantee the underlying memory is freed if something else still holds a reference into the same bundle.
- The governing rule, stated directly by the manual: **mirror every call to a load method with a call to a release method** — release using either the returned instance (`ReleaseInstance(gameObject)`) or the operation handle it came from (`Release(handle)`), whichever is on hand at the release site.

## Anti-patterns to avoid

- **Asset churn**: releasing an asset and then immediately reloading it (or another asset sharing its bundle) triggers an avoidable unload/reload cycle. If something will plausibly be needed again shortly, keep it loaded rather than releasing eagerly and reloading a moment later — decide the actual lifetime scope up front (per-level, per-session, per-app-lifetime) instead of releasing reactively.
- **`Object.Destroy()` on an Addressables-instantiated GameObject**: this bypasses the reference count entirely. The GameObject disappears from the scene, but the underlying asset/bundle reference it held stays counted as "in use" for the rest of the session — a permanent, silent leak. Always use `Addressables.ReleaseInstance(...)` (or the `AssetReference`'s own `ReleaseInstance()`) instead.
- **Loading the same key repeatedly without tracking the handle** — every load is a new reference; if nothing ever releases the earlier ones, the reference count only grows. Track exactly one handle per logical "thing I loaded," not one per call site that happens to need the same asset.
- **Releasing before a dependent bundle asset is actually done being used** — because bundle-level unload only happens at zero references, a premature release usually doesn't cause a visible bug, but it does mean the *next* load of anything in that bundle pays a reload cost that careful lifetime scoping would have avoided.

## Diagnosing leaks and churn

- `AsyncOperationHandle.ReferenceCount` — inspect at runtime to confirm a specific handle's count is what's expected (e.g. exactly 1 while something is actively using it, 0 right after the matching release).
- The **Addressables Profiler module** — the primary tool for spotting a reference count that never reaches zero (a leak) or one that oscillates rapidly (churn) over a play session, rather than guessing from code inspection alone.

## Loading and instantiating — call shape

- `Addressables.LoadAssetAsync<T>(key)` for a single asset by key/`AssetReference`; `LoadAssetsAsync<T>(...)` for multiple keys/labels at once, with an explicit merge mode (`Union`/`Intersection`/`Difference`) when combining more than one label/key — state which merge semantics the call actually needs rather than accepting a default and being surprised by what came back.
- `Addressables.InstantiateAsync(key, position, rotation, parent)` (or the `AssetReference` equivalent) for a GameObject that needs Addressables to track the resulting instance's reference — never load the prefab separately and call `Object.Instantiate` on it if the loaded reference itself isn't going to be tracked and released correctly.
- Scenes: `Addressables.LoadSceneAsync(key, LoadSceneMode.Additive/Single, activateOnLoad)` / `UnloadSceneAsync(...)`. Use `activateOnLoad: false` when the moment of activation needs to be controlled precisely (e.g. behind a loading screen), then call the returned `SceneInstance`'s `ActivateAsync()` at the right point.

## Awaiting with UniTask

- Both `AsyncOperationHandle` and `AsyncOperationHandle<T>` are natively awaitable once UniTask and Addressables are both installed (`Cysharp.Threading.Tasks.Addressables` auto-enables) — `var asset = await Addressables.LoadAssetAsync<GameObject>(key);` needs no extra conversion call.
- Do not chain `Addressables.LoadSceneAsync(...).ToUniTask()` without checking scene-activation timing — UniTask's own guidance flags this combination as a special case where the `.ToUniTask()` conversion's completion timing doesn't line up cleanly with when the scene is actually ready to activate. Prefer awaiting the handle directly with `activateOnLoad: false` and an explicit `ActivateAsync()` call instead.
- Cancellation, `.Preserve()` for multi-await cases, and `PlayerLoopTiming` all follow `unitask-async-programming`'s general guidance directly — Addressables doesn't need special-cased handling for these beyond the scene-loading caveat above.
- Never call `handle.WaitForCompletion()` in steady-state/hot-path code — it blocks the calling thread synchronously until the operation finishes, defeating the point of an async load. If a truly synchronous load is unavoidable, treat it as an explicit, narrow exception (e.g. an editor tool), not a runtime gameplay pattern.

## Pre-downloading remote content

- `await Addressables.GetDownloadSizeAsync(key)` first — if it returns `0`, nothing needs downloading and the download UI can be skipped entirely.
- `await Addressables.DownloadDependenciesAsync(key)` to actually fetch content ahead of the point it's required — trigger this ahead of a level transition or behind an explicit "Download" prompt, not lazily at the moment the content is first requested.
- Drive a progress bar off `handle.GetDownloadStatus()` rather than the general `PercentComplete` (which reflects overall operation progress across chained operations, not download-specific progress). When reporting progress through UniTask, prefer `Cysharp.Threading.Tasks.Progress.Create<float>(...)` over a bare `System.Progress<T>` to avoid its per-report allocation, consistent with `performance-and-algorithms.md`'s general allocation discipline.
