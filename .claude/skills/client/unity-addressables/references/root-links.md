# Root Links

Root/index pages, as given by the user, plus the specific sub-pages this skill was built from underneath them. Follow their own in-page navigation for anything not covered by the other files in this folder.

## Given by the user
- [Addressables Manual — index](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/index.html)
- [Addressables API reference — index](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/api/index.html)

## Manual — concepts & architecture
- [Addressables introduction](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/AddressableAssetsOverview.html) — addresses, keys, labels, catalogs, local-vs-remote resolution.
- [Choose a content build system](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/content-build-systems.html) — Content Directory vs. AssetBundle, when each applies, Unity 6.6+ requirement for Content Directory.
- [Create and organize Addressable assets](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/AddressableAssetsDevelopmentCycle.html)
  - [Introduction to organizing Addressable assets](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/organize-addressable-assets.html) — grouping strategies (concurrent-usage, logical-entity, type-based).
  - [Define how to pack groups into AssetBundles](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/PackingGroupsAsBundles.html) — Pack Together / Pack Separately / Pack Together by Label trade-offs.
  - [Addressable asset dependencies](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/AssetDependencies.html) — explicit vs. implicit dependencies, duplication risk.
  - [Addressables Profiles](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/AddressableAssetsProfiles.html) — Local/Remote Build/Load Path variables, per-environment switching.

## Manual — loading, memory, releasing
- [Load Addressable assets](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/LoadingAddressableAssets.html) — the API surface hub for load/instantiate/scene calls.
- [Memory management overview](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/MemoryManagement.html)
  - [Managing asset memory](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/memory-assets.html) — reference counting mechanics, load/release pairing, asset-churn anti-pattern.
  - [Addressable AssetBundle memory considerations](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/memory-assetbundles.html) — bundle-level unload semantics, fewer-larger vs. many-smaller bundle trade-offs.

## Manual — build workflow
- [Build Addressable assets](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/Builds.html)
  - [Introduction to building Addressable assets](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/build-intro.html) — Play Mode Scripts vs. Default Build Script vs. Update-a-Previous-Build.
  - [Build with continuous integration](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/ContinuousIntegration.html)

## Manual — remote content & optimization
- [Distribute and update remote content](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/RemoteContentDistribution.html) — remote profiles, AssetBundle caching, CCD integration, content update workflow (`CheckForCatalogUpdates`/`UpdateCatalogs`).
- [Optimization tools](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/optimization-tools.html) — Build Reports, Analyze window, Build Layout Report, Addressables Profiler module.

## API reference — types this skill's guidance is built from
- [`Addressables`](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/api/UnityEngine.AddressableAssets.Addressables.html) — the static entry-point API (`LoadAssetAsync`, `InstantiateAsync`, `LoadSceneAsync`, `Release`/`ReleaseInstance`, `GetDownloadSizeAsync`/`DownloadDependenciesAsync`, `CheckForCatalogUpdates`/`UpdateCatalogs`).
- [`AsyncOperationHandle<T>`](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/api/UnityEngine.ResourceManagement.AsyncOperations.AsyncOperationHandle-1.html) — `Result`/`Status`/`IsDone`/`PercentComplete`/`OperationException`, native `GetAwaiter()`, `ReferenceCount` (diagnostics).
- [`AssetReference`](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/api/UnityEngine.AddressableAssets.AssetReference.html) — `LoadAssetAsync`/`InstantiateAsync`/`ReleaseAsset`/`ReleaseInstance`, `OperationHandle`, `IsValid()`, `editorAsset` vs. `RuntimeKey`; typed subclasses (`AssetReferenceGameObject`, `AssetReferenceTexture`, `AssetReferenceSprite`, etc.) via `AssetReferenceT<TObject>`.
- [`ResourceManager`](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/api/UnityEngine.ResourceManagement.ResourceManager.html) — the engine `Addressables` delegates to; rarely touched directly, but explains why `IResourceLocation`/`IResourceProvider` exist underneath the static API.
- [`IResourceLocation`](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/api/UnityEngine.ResourceManagement.ResourceLocations.IResourceLocation.html) — what a resolved key/label/`AssetReference` becomes internally before a provider loads it.

Note: some guessed page slugs from older Addressables versions (e.g. a dedicated `AnalyzeRules.html`) return 404 on the 4.0 docs — the Analyze tool's rule list is covered instead from [optimization-tools.html](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/optimization-tools.html)'s own content; check that page's current in-page navigation if a rule-by-rule breakdown is needed.
