---
name: unity-addressables
description: "Addressables 4.0: AssetReference, LoadAssetAsync/InstantiateAsync/LoadSceneAsync, Release/ReleaseInstance ref counting, groups/labels, remote catalogs, content updates, Content Directory vs AssetBundle. Use for runtime asset delivery or asset leaks."
user-invocable: false
---

# Unity Addressables

Not for: await/cancellation mechanics (`unitask-async-programming`), pool design (`unity-performance-engineer`), import/compression settings (`unity-2d-sprite`, `unity-audio-mixer`, else `unity-performance-engineer`), remote-config cadence (`live-ops-content-pipeline`), CDN vendor choice (`sdk-platform-engineer`), the CI command that runs the content build (`unity-batchmode-cli`). Addressables calls stay in `Game.Client.*`; `Game.Core.*` takes resolved data (`csharp-standards`).
Docs: https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/index.html (API: same root, `/api/index.html`). Keep `@4.0`; earlier versions have no Content Directory system. Read the installed version from `Packages/manifest.json` and swap the segment if it differs.

| Reference | Read when |
|---|---|
| [architecture-and-concepts.md](references/architecture-and-concepts.md) | Choosing the build system or packing mode, or build size/duplication is the question |
| [load-and-release.md](references/load-and-release.md) | Writing a load call, or deciding where a release goes, or an asset will not unload |
| [remote-content-and-catalogs.md](references/remote-content-and-catalogs.md) | Content ships or updates remotely |
| [build-workflow-and-best-practices.md](references/build-workflow-and-best-practices.md) | Preparing a build, switching environments, or auditing layout before handoff |

## Steps
1. **Pick the content build system once per project** — Content Directory is simpler and dedupes shared plain assets but is local-only; AssetBundle is required for remote delivery and content updates. Mixing both builds shared dependencies twice.
2. **Address Inspector-wired assets via `AssetReference`; use string keys only for runtime-resolved content** — GUID survives rename, typed subclasses reject wrong assets.
3. **Await the handle; never `WaitForCompletion()` in gameplay code** (`await handle.Task` works without extra packages; UniTask's `ToUniTask()` is preferred in Client code). Check `Status`: a failed load completes rather than throwing.
4. **Load scenes with `activateOnLoad` false and call `ActivateAsync()`** when the scene should go live, so a loading screen is not cut short.
5. **Mirror every load with exactly one release on every path** (early return and exception included); `ReleaseInstance`, never `Object.Destroy`, for instances.
6. **Decide each asset's lifetime scope first** (level, session, app) — releasing then reloading a bundle costs more than holding.
7. **Size remote content before committing the player** with `GetDownloadSizeAsync` (zero = skip the prompt); pre-download ahead of the transition.
8. **Group by what loads together, then choose the packing mode**, per [architecture-and-concepts.md](references/architecture-and-concepts.md).
9. **Make a plain asset Addressable once a second Addressable references it**, and run the Analyze window before shipping.
10. **Drive paths from a Profile per environment**; no URL or path in code.
11. **Treat a catalog update as a visible step**: check, apply, then let the player through.
12. **Verify on a full content build before handoff**; Play Mode Scripts never resolve a catalog or bundle. Hand to `qa-automation-engineer` and `playtest-tester` only after that build exists.

## Never
- Read `AssetReference.editorAsset` at runtime: it works in the Editor and returns nothing in a build.
- Ship a content update without the previous build's content state file: it cannot be produced; the only path left is a full player release.
- Expect one release to free an asset under the AssetBundle system: nothing unloads until the whole bundle's count is zero.

## Output
```
## Addressables Work — <asset, scene, or system>
- Content build system: <Content Directory / AssetBundle> — why
- Addressing: <AssetReference / string key / label> — merge mode if several keys
- Load call: <...>
- Scene activation: <activateOnLoad false + ActivateAsync — or n/a>
- Release path: <Release / ReleaseInstance> — confirmed on every path
- Lifetime scope: <level / session / app> — release trigger
- Remote: <size check, pre-download point, catalog handling — or local only>
- Group and packing: <principle and mode — or n/a under Content Directory>
- Shared-dependency check: <Analyze result — or n/a>
- Verified against: <full content build / Play Mode Scripts only (not sufficient for handoff)>
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Just `Object.Destroy` the Addressables prop on despawn, it is simpler" → declined: the reference stays counted and the bundle never unloads, silently. Used `ReleaseInstance` and checked its return value (false when handed an object Addressables did not create).
