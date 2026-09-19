# Root Links — Addressables 4.0

Source: the root index pages listed below, as provided for this skill.
Covers: the whole skill — provenance and version anchor for every file in
this folder.

Anchors every link in this folder to Addressables 4.0. Anything this skill
cites resolves under one of these roots; anything that does not is out of
scope for the skill rather than merely undocumented here. The async mechanics
around a handle belong to `unitask-async-programming`, and asset import
settings to `technical-artist` — neither is under these roots.

## Roots

| Root | Holds | Source |
|---|---|---|
| Manual | Concepts, workflows, build and remote-content procedure | [Addressables Manual index](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/index.html) |
| API reference | `Addressables`, handles, `AssetReference`, `ResourceManager` | [Addressables API index](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/api/index.html) |

## Which file answers which question

| Question | File | Source |
|---|---|---|
| Which content build system, and how do groups map to output | [architecture-and-concepts.md](architecture-and-concepts.md) | [Choose a content build system](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/content-build-systems.html) |
| Which call, with what arguments, and how does it report failure | [load-calls-and-awaiting.md](load-calls-and-awaiting.md) | [Load Addressable assets](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/LoadingAddressableAssets.html) |
| Where does the release go, and why has this not unloaded | [loading-and-reference-counting.md](loading-and-reference-counting.md) | [Managing asset memory](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/memory-assets.html) |
| How does remote content download and update | [remote-content-and-catalogs.md](remote-content-and-catalogs.md) | [Distribute and update remote content](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/RemoteContentDistribution.html) |
| How is content built, verified, and switched between environments | [build-workflow-and-best-practices.md](build-workflow-and-best-practices.md) | [Build Addressable assets](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/Builds.html) |

## Core API types

| Type | Source |
|---|---|
| `Addressables` | [Addressables](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/api/UnityEngine.AddressableAssets.Addressables.html) |
| `AsyncOperationHandle\<T\>` | [AsyncOperationHandle](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/api/UnityEngine.ResourceManagement.AsyncOperations.AsyncOperationHandle-1.html) |
| `AssetReference` | [AssetReference](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/api/UnityEngine.AddressableAssets.AssetReference.html) |
| `ResourceManager` | [ResourceManager](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/api/UnityEngine.ResourceManagement.ResourceManager.html) |
| `IResourceLocation` | [IResourceLocation](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/api/UnityEngine.ResourceManagement.ResourceLocations.IResourceLocation.html) |

Keep the `@4.0` segment when following any link from this skill — earlier
Addressables versions have no Content Directory build system at all, and some
page slugs from those versions no longer resolve. Read the installed version
from `Packages/manifest.json` and substitute the segment if it differs, rather
than assuming the pages match.
