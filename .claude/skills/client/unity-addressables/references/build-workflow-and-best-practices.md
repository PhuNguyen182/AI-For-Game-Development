# Build Workflow & Standard-Process Best Practices

Covers SKILL.md's "standard workflow" guidance — how Addressables content actually gets built, verified, and shipped, as distinct from the runtime loading API covered in `loading-and-reference-counting.md`.

## The build-script spectrum — pick the right one for the moment

Addressables separates "how the Editor resolves your content right now" from "the actual shippable build," via three tiers:

| Tier | Speed | Fidelity to shipped behavior | When to use |
|---|---|---|---|
| Play Mode Scripts | Fastest | Lowest — reads assets straight from the Asset Database, not from built bundles/content directories | Day-to-day iteration in the Editor while actively developing |
| Update a Previous Build | Medium | Medium — incremental, rebuilds only what changed | Iterative verification once a baseline build exists, without paying full-rebuild cost every time |
| Default Build Script (full content build) | Slowest | Highest — produces the actual catalog, bundles/content directory, and runtime settings that will ship | Before any real-device test, before handing a build to QA/Playtest, and always in CI |

The practical implication: a bug that only reproduces after a full content build (a missing dependency, a group misconfiguration, a catalog resolution failure) will not show up under Play Mode Scripts, because Play Mode Scripts bypass the actual bundle/catalog resolution path entirely. Treat "it works in Play Mode" as necessary but not sufficient — a feature that touches Addressables is not considered verified until it has been checked against at least one real content build, per `qa-automation-engineer`'s and `playtest-tester`'s usual verification standard.

## Profiles — never hardcode an environment

Profiles hold the Local/Remote Build Path and Local/Remote Load Path variables that build scripts and runtime resolution both consume. Practical rules:
- Maintain a separate Profile per environment (Development/Staging/Production) rather than editing path values in place before each build — switching environments should be a Profile selection, not a hand-edited path.
- Never hardcode a CDN URL, bucket path, or local build path directly in gameplay code — if code ever needs to know a load path, it should be reading it through Addressables' own resolution, not duplicating a Profile's value independently.
- Coordinate Profile setup with whoever owns the actual hosting/CDN vendor decision (`tech-lead-sdk-platform`) — this skill covers wiring the Profile variable correctly once a host exists, not choosing the host.

## Content update workflow (AssetBundle system only)

For a live game shipping content post-launch:
1. A content update build produces only the changed content plus an updated catalog, rather than a full rebuild of everything.
2. At runtime, `Addressables.CheckForCatalogUpdates(...)` checks whether a newer catalog is available, and `Addressables.UpdateCatalogs(...)` applies it.
3. Treat a catalog update as a deliberate, user-visible step (a "new content available" prompt, a download step before entering the affected area) rather than a silent swap underneath a session already in progress — an asset a running session already resolved against the old catalog can behave unexpectedly if the underlying content changes out from under it without a clear transition point.
4. This workflow only applies to the AssetBundle content build system — the Content Directory system is local-only and has no equivalent remote catalog-update path per the current manual.

## Optimization tools — treat as a pre-ship gate, not optional tooling

- **Analyze window** — evaluates the Addressables layout for structural problems (most importantly, duplicate bundle dependencies from the non-Addressable-dependency pattern described in `architecture-and-concepts.md`). Run it whenever group structure changes meaningfully, not only when something is already visibly wrong.
- **Build Layout Report** — inspect actual build output (which assets landed in which bundle/directory, and why) when a build's size or memory footprint doesn't match expectations, instead of guessing from group configuration alone.
- **Build Profile Logs** — Chromium-viewable build performance data, useful when the build step itself (not the runtime result) is the bottleneck being investigated.
- **Addressables Profiler module** — the runtime counterpart; use it to verify reference-counting behavior and catch asset churn per `loading-and-reference-counting.md`'s guidance, and to confirm a change actually improved load behavior rather than just appearing to in casual testing.

Fold an Analyze pass and a Build Layout Report check into the same "feature-complete, ready for Code Review" gate that `coding-principles.md`'s Handoff section already requires — a duplicate-dependency finding caught here is far cheaper than one found after a live content update ships with bloated bundles.

## CI

For automated builds, drive the Addressables content build through `AddressableAssetSettings.BuildPlayerContent()`-based scripting rather than relying on manual Editor button clicks before every CI run — this keeps the content build reproducible and makes it a first-class step in the same pipeline as the player build itself, not a manual pre-step someone can forget.
