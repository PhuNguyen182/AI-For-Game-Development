# Build Workflow

Sources (Addressables 4.0 manual): `Builds.html`, `build-intro.html`, `AddressableAssetsProfiles.html`, `optimization-tools.html`, `ContinuousIntegration.html`, `RemoteContentDistribution.html`. The CI command line is `unity-batchmode-cli`'s.

## Build-script tiers
| Tier | Fidelity | Use when |
|---|---|---|
| Play Mode Scripts, Asset Database | Lowest: never resolves a catalog or opens a bundle | Day-to-day iteration |
| Play Mode Scripts, simulated groups | Medium: models layout and dependencies, shows duplication early | Checking a grouping change without a build |
| Update a Previous Build | Medium-high: incremental against a baseline | Iterating on an existing build |
| Default Build Script, full content build | Highest: produces catalog, content, runtime settings | Before any device test, QA handoff, and every CI run |

A missing dependency, a group excluded from the build, or a catalog failure cannot reproduce under Asset Database mode. "Works in the Editor" is never sufficient.

## Profiles
- Local and remote build/load paths live in the Profile; build scripts and runtime read them from there.
- One Profile per environment (development, staging, production); switching is a selection.
- Code that rebuilds a load path duplicates a Profile value and drifts when the environment changes.

## Audit tools
- Analyze window: duplicate bundle dependencies, before shipping.
- Build Layout Report: which asset landed in which bundle and why; the way to explain an oversized build.
- Build profile logs: where build time goes.
- Addressables Profiler module: runtime reference counts (see [load-and-release.md](load-and-release.md)).

## CI
- Script the content build so it is a pipeline step, not a skippable manual pre-step (the usual cause of a player shipped against stale content).
- Content build precedes the player build; reversed, the player carries the previous run's catalog.
- Keep the content state file as a build artifact; a future content update cannot be built without it.
