---
name: unity-addressables
description: >
  Technique for runtime asset and scene delivery through Unity's Addressables
  package — `Addressables.LoadAssetAsync`, `LoadAssetsAsync`,
  `InstantiateAsync`, `LoadSceneAsync`, `Release` and `ReleaseInstance`
  reference counting, `AsyncOperationHandle`, `AssetReference` fields, groups,
  labels, Profiles, catalogs, `GetDownloadSizeAsync`,
  `DownloadDependenciesAsync`, `CheckForCatalogUpdates`, `UpdateCatalogs`, and
  the Content Directory versus AssetBundle content build systems. Use when an
  asset or scene should be addressed by key, label or reference instead of
  hard-referenced, or when content ships or updates remotely. Not for: generic
  await and cancellation mechanics (`unitask-async-programming`); pool design
  (`unity-engineer`); import and compression settings (`technical-artist`);
  remote-config cadence (`live-ops-content-pipeline`); CDN vendor choice
  (`tech-lead-sdk-platform`).
---

# Unity Addressables — Addressing, Loading, Reference Counting, Remote Content

## Bundled resources

### References
Read-only context, loaded on demand so SKILL.md itself stays short.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Manual and API roots, the package version pin, and which file answers which question | Starting any task here, or confirming the installed package version |
| [architecture-and-concepts.md](references/architecture-and-concepts.md) | Content build systems compared, addressing model, groups, packing modes, the dependency-duplication mechanism | Before the first load call is written, or when build size or duplication is the question |
| [load-calls-and-awaiting.md](references/load-calls-and-awaiting.md) | Call shapes for asset, multi-key, instance and scene loads, merge modes, `AssetReference`, awaiting, failure surfacing | Choosing or writing a specific load call |
| [loading-and-reference-counting.md](references/loading-and-reference-counting.md) | The reference-counting contract, bundle-level unload, release APIs, leak and churn diagnosis | Deciding where a release goes, or an asset will not unload |
| [remote-content-and-catalogs.md](references/remote-content-and-catalogs.md) | Download sizing, pre-download, caching, catalog update flow and its build-time prerequisite | Content ships or updates remotely |
| [build-workflow-and-best-practices.md](references/build-workflow-and-best-practices.md) | Play Mode Scripts versus full builds, Profiles, Analyze window, Build Layout Report, CI | Preparing a build, switching environments, or auditing layout before handoff |

## 1. Objective
Deliver content that loads when it should, unloads when it should, and behaves in a shipped build the way it behaved in the Editor. Addressables fails quietly in both directions: a missing release leaks a bundle for the rest of the session while everything appears to work, and an `Object.Destroy` on an Addressables instance leaks the same way while looking like correct cleanup. A key that resolves to nothing surfaces on the handle rather than at the call site, and a feature verified only under Play Mode Scripts has never once exercised the catalog the build will actually use.

## 2. Role
Act as the asset-streaming specialist for the client track — the tool reached for whenever an asset, prefab, or scene should be addressed by key, label, or `AssetReference` rather than hard-referenced, loaded from a `Resources` folder, or driven through raw `AssetBundle` calls.

## 3. When to invoke this skill
- Replacing a `Resources.Load`, a hard prefab reference, or a build-index scene load with an addressed load so the content can move, grow, or go remote without a code change.
- Instantiating and despawning prefabs through Addressables so the reference count tracks the instances.
- Loading and unloading Addressable scenes, with control over when the loaded scene actually activates.
- Pre-downloading remote content ahead of the moment it is needed, and sizing that download for a progress bar or a prompt.
- Choosing between the Content Directory and AssetBundle content build systems, or auditing a project that has mixed them.
- Shipping or applying a content update to a live game, including the catalog check and the build-time state file it depends on.
- Organizing groups and packing modes, or investigating a build that is larger than the assets in it should produce.
- An asset will not unload, memory grows across level transitions, or a load throws for a key that visibly exists in the Groups window.
- Negative trigger: the mechanics of awaiting, cancelling, or preserving an async operation in general — that is `unitask-async-programming`; this skill owns which Addressables call to make and when its handle is released.
- Negative trigger: designing the pool that reuses instantiated objects — that is `unity-engineer` under `performance-and-algorithms.md`; this skill owns acquiring and releasing the handle behind a pooled object, not the pool.
- Negative trigger: texture, audio, or mesh import and compression settings — that is `technical-artist`; this skill assumes the import settings are already right and covers only how the asset is addressed and loaded.
- Negative trigger: remote-config, economy tuning, or event cadence infrastructure — that is `live-ops-content-pipeline`, tunable data rather than binary asset delivery.
- Negative trigger: choosing a CDN or hosting vendor for remote content — that is `tech-lead-sdk-platform`; this skill wires the catalog and download API once a host exists.
- Negative trigger: any Addressables call inside `Game.Core.*` — the package depends on `UnityEngine`, so Shared Core receives already-resolved data from `Game.Client.*`, per `coding-principles.md`'s Shared Core integrity rule.

## 4. How to use this skill
1. **Pick the content build system once, per project** — Content Directory is the simpler workflow with automatic deduplication of shared plain assets, and it is local-only; the AssetBundle system is required for remote delivery, post-launch content updates, and older Editor versions, per [architecture-and-concepts.md](references/architecture-and-concepts.md) and the version pin in [root-links.md](references/root-links.md). Mixing both builds shared dependencies twice, so this is settled before the first group is created, not per group.
2. **Address Inspector-wired assets through `AssetReference` and reserve string keys for runtime-resolved content** — an `AssetReference` stores a GUID, so renaming or moving the asset does not break it, and its typed subclasses reject the wrong asset type at authoring time, per [load-calls-and-awaiting.md](references/load-calls-and-awaiting.md). A string key built from data is right only where the target genuinely is not known until runtime.
3. **Await the handle directly rather than blocking on `WaitForCompletion()`** — both handle types are awaitable once UniTask and Addressables are installed together, and the blocking call stalls the calling thread until the load finishes, which is the entire cost the async API exists to avoid. Cancellation and multi-await handling follow `unitask-async-programming`; failure surfacing does not, and is covered in [load-calls-and-awaiting.md](references/load-calls-and-awaiting.md).
4. **Control scene activation explicitly rather than letting the load perform it** — load with `activateOnLoad` set to false and call `ActivateAsync()` at the point the scene should go live, so a loading screen is not cut short by the scene appearing the instant it finishes streaming.
5. **Mirror every load with exactly one release, on every code path** — including early returns and caught exceptions, per [loading-and-reference-counting.md](references/loading-and-reference-counting.md) and `coding-principles.md`'s Correctness boundaries section. `Object.Destroy` on an Addressables-created instance removes the GameObject and leaves its reference counted for the rest of the session.
6. **Decide each asset's lifetime scope up front rather than releasing reactively** — per level, per session, or per app. Releasing something that is needed again moments later forces an unload and reload of its whole bundle, and that churn costs more than holding the asset would have.
7. **Size the download before the player is committed to it** — `GetDownloadSizeAsync` reports what is still missing after the cache, so zero means the prompt can be skipped entirely, per [remote-content-and-catalogs.md](references/remote-content-and-catalogs.md). Fetch ahead of the transition, not at the moment the content is first requested.
8. **Organize groups by what loads together, then pick the packing mode from that** — grouping decides bundle boundaries under the AssetBundle system, so a group whose assets load at different times forces a load of all of them, per [architecture-and-concepts.md](references/architecture-and-concepts.md).
9. **Make a plain asset Addressable the moment a second Addressable references it** — under the AssetBundle system an unaddressed shared asset is copied into every bundle that references it, which shows up as build bloat with no duplicate in the project. Run the Analyze window before shipping rather than reading group settings and assuming.
10. **Drive every build and load path from a Profile** — one Profile per environment, so changing environment is a selection rather than an edit, per [build-workflow-and-best-practices.md](references/build-workflow-and-best-practices.md). A hardcoded URL in gameplay code is the failure that ships a development build pointing at a staging bucket.
11. **Treat a catalog update as a step the player sees** — check, then apply, then let the player through, per [remote-content-and-catalogs.md](references/remote-content-and-catalogs.md). Swapping content underneath a session that has already resolved against the old catalog produces failures with no clear cause.
12. **Verify against a full content build before handing anything off** — Play Mode Scripts read from the Asset Database and never exercise catalog or bundle resolution, so the class of bug that only exists in a build is exactly the class they cannot show. Route the result to `qa-automation-engineer` and `playtest-tester` only after that build exists.
13. **Keep every Addressables call inside `Game.Client.*`** — the package depends on `UnityEngine`, and Shared Core takes the already-resolved object or data, per `coding-principles.md`'s Shared Core integrity rule.

## 5. Specific goals / tasks this skill performs
- Converting hard-referenced or `Resources`-loaded assets and scenes to addressed loads.
- Writing load, instantiate, scene, and release calls with correct reference-count pairing on every path.
- Choosing the content build system and organizing groups, labels, and packing modes.
- Pre-download flows, download sizing, and remote catalog checks and updates.
- Auditing for leaks, churn, and non-Addressable dependency duplication.
- Setting up Profiles per environment and selecting the right build-script tier for the moment.
- Diagnosing loads that fail for keys that exist, and assets that will not unload.
- Out of scope: async and cancellation mechanics (`unitask-async-programming`); pool design (`unity-engineer`); import and compression settings (`technical-artist`); remote-config and economy cadence (`live-ops-content-pipeline`); CDN vendor choice (`tech-lead-sdk-platform`); any `Game.Core.*` usage (`csharp-engineer`).

## 6. Output format
```
## Addressables Work — <asset, scene, or system name>
- Content build system: <Content Directory / AssetBundle> — rationale
- Addressing: <AssetReference field / string key / label> — merge mode if more than one key
- Load call: <LoadAssetAsync / LoadAssetsAsync / InstantiateAsync / LoadSceneAsync>
- Awaited how: <direct await, cancellation per unitask-async-programming — or "not applicable">
- Scene activation: <activateOnLoad false plus explicit ActivateAsync — or "not a scene load">
- Release path: <Release / ReleaseInstance> — confirmed on every path including early return and exception
- Lifetime scope: <per level / per session / per app> — and what triggers the release
- Remote: <download size check, pre-download trigger point, catalog update handling — or "local only">
- Group and packing: <grouping principle and packing mode — or "not applicable under Content Directory">
- Shared-dependency check: <Analyze window result — or "not applicable">
- Verified against: <full content build / Play Mode Scripts only, which is not sufficient for handoff>
- Layer: Game.Client.* — no Addressables call in Game.Core.*
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what the delivered setup does not cover>
- Latent concerns: <failure modes not yet triggered: assumptions that hold only at current content size, thresholds not yet reached, trade-offs knowingly deferred>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: an enemy prefab is a hard `[SerializeField] GameObject` reference and should become addressable so it can move to remote content later.
- Output: replaced the field with an `AssetReferenceGameObject`, instantiated through it, and tracked one handle per spawned instance. The despawn path releases through Addressables rather than destroying, so the count actually drops. Lifetime scope is per level, so the handles release at level teardown rather than at each despawn, which would have reloaded the bundle on the next wave. Group is per-level concurrent usage, packed together.

**Example 2**
- Input: "Just call `Object.Destroy` on the Addressables-instantiated prop when it despawns, it is simpler."
- Output: declined — `Destroy` removes the GameObject while the reference stays counted, so the bundle behind it never unloads for the rest of the session and nothing reports the leak. Used `ReleaseInstance`, which destroys the object and decrements the count together. Checked its return value as well, since it reports false and does nothing at all when handed an object Addressables did not create.

**Example 3**
- Input: "The feature works in the Editor, so the Addressables work is done."
- Output: flagged that the Editor session was running under Play Mode Scripts, which read straight from the Asset Database and never touch the catalog or the bundles. Ran a full content build and retested; a group left out of the build resolved to nothing at runtime, which the Editor path could not have surfaced. Only then handed off to `qa-automation-engineer`.

**Example 4**
- Input: the build report shows a shared UI font duplicated across five panel bundles.
- Output: the font was a plain asset referenced by five Addressables, so the AssetBundle system copied it into each. Made it Addressable in its own group and reran the Analyze window to confirm the five copies collapsed into one shared dependency, per [architecture-and-concepts.md](references/architecture-and-concepts.md)'s dependency model.

## 8. Edge cases & guardrails
- Never call `Object.Destroy` on an Addressables-created instance — the GameObject goes, the reference count does not, and the leak is silent for the session.
- Never leave a load handle unreleased on any path — early return and caught exception included, per `coding-principles.md`'s Correctness boundaries section.
- Never call `WaitForCompletion()` in gameplay code — it blocks the calling thread; reserve it, if ever, for editor tooling.
- Never mix the Content Directory and AssetBundle systems in one project — shared dependencies build twice.
- Never assume one release frees the asset — under the AssetBundle system nothing unloads until the whole bundle's count reaches zero.
- Never read an `AssetReference`'s editor-only asset accessor at runtime — it resolves in the Editor and returns nothing in a build, which is a bug that cannot reproduce where it is being debugged.
- Never trust that a load succeeded because the await returned — a key that resolves to nothing completes the operation in a failed state rather than throwing at the call site.
- Never ship a content update without the previous build's content state file — without it the update cannot be produced at all, and the only remaining path is a full player release.
- Never hardcode a build path or CDN URL in code — drive it from a Profile, one per environment.
- Never treat "works under Play Mode Scripts" as verification — that path never resolves a catalog or a bundle.
- Never release an asset that is about to be needed again — the reload of its whole bundle costs more than holding it would have.
- Never call Addressables from `Game.Core.*` — it depends on `UnityEngine`, and Core takes resolved data instead.
