# Build Workflow — Play Mode Scripts, Profiles, layout audits, CI

Sources: [Build Addressable assets](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/Builds.html), [Introduction to building](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/build-intro.html), [Addressables Profiles](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/AddressableAssetsProfiles.html), [Optimization tools](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/optimization-tools.html), [Build with continuous integration](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/ContinuousIntegration.html).
Covers: SKILL.md §4 — **"Drive every build and load path from a Profile"**, **"Verify against a full content build before handing anything off"**.

How content actually gets built and what each Editor shortcut is not
exercising. The runtime call surface is in
[load-calls-and-awaiting.md](load-calls-and-awaiting.md); this file is about
the build that has to exist before those calls resolve to anything.

## Build-script tiers

| Tier | Fidelity to a shipped build | Use when | Source |
|---|---|---|---|
| Play Mode Scripts, Asset Database backed | Lowest — reads assets directly and never resolves a catalog or opens a bundle, so an entire class of failure is unreachable | Day-to-day iteration while the feature is still being written | [Introduction to building](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/build-intro.html) |
| Play Mode Scripts, simulated groups | Medium — models group layout and dependencies without a full build, so duplication and packing problems become visible early | Checking layout consequences of a grouping change without waiting for a build | [Introduction to building](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/build-intro.html) |
| Update a Previous Build | Medium to high — incremental against an existing baseline | Iterating on a build that already exists, without paying full rebuild cost | [Introduction to building](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/build-intro.html) |
| Default Build Script, full content build | Highest — produces the catalog, the content, and the runtime settings that ship | Before any device test, any QA handoff, and every CI run | [Introduction to building](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/build-intro.html) |

**Critical caveat**: a missing dependency, a group excluded from the build, or
a catalog resolution failure cannot reproduce under Asset Database Play Mode
Scripts, because that path never consults the catalog. "It works in the
Editor" is necessary and never sufficient for an Addressables feature.

## Profiles

| Subject | What it decides | Source |
|---|---|---|
| Path variables | Local and remote build and load paths live in the Profile, and both the build scripts and runtime resolution read them from there | [Addressables Profiles](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/AddressableAssetsProfiles.html) |
| One Profile per environment | Development, staging, and production as separate Profiles, so switching is a selection rather than an edit somebody forgets to undo | [Addressables Profiles](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/AddressableAssetsProfiles.html) |
| No path in code | Gameplay code that reconstructs a load path duplicates a value the Profile already owns, and the two drift the first time an environment changes | [Addressables Profiles](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/AddressableAssetsProfiles.html) |

## Audit tools

| Tool | What it settles | Source |
|---|---|---|
| Analyze window | Finds duplicate bundle dependencies — the shared plain asset copied into several bundles — before a build ships with them | [Optimization tools](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/optimization-tools.html) |
| Build Layout Report | Shows which asset landed in which bundle and why, which is the only way to explain a build larger than its contents suggest | [Optimization tools](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/optimization-tools.html) |
| Build profile logs | Where the build step's own time is going, for when the build rather than the runtime is the problem | [Optimization tools](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/optimization-tools.html) |
| Addressables Profiler module | Runtime reference-count behaviour across a session — see [loading-and-reference-counting.md](loading-and-reference-counting.md) | [Optimization tools](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/optimization-tools.html) |

## Continuous integration

| Subject | What it decides | Source |
|---|---|---|
| Scripted content build | Driving the content build from script rather than an Editor button makes it a pipeline step instead of a manual pre-step someone can skip, which is the usual cause of a player shipped against stale content | [Build with continuous integration](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/ContinuousIntegration.html) |
| Ordering | Content build precedes the player build; reversing them produces a player carrying the previous run's catalog | [Build with continuous integration](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/ContinuousIntegration.html) |
| Content state file | Preserve it as a build artifact — a future content update cannot be produced without the state recorded by the build that shipped | [Distribute and update remote content](https://docs.unity3d.com/Packages/com.unity.addressables@4.0/manual/RemoteContentDistribution.html) |
