# On-Demand Loading — Deferred Atlas Texture Loading & the Addressables Extension

Source: [spine-unity-on-demand-loading](https://esotericsoftware.com/spine-unity-on-demand-loading).

## Why
By default, all atlas textures are indirectly referenced by the `SkeletonDataAsset` and load whenever the skeleton itself loads — even skins/atlas pages that won't be visible for a given instance. On-demand loading lets a project (typically one with many skins/atlas pages per skeleton) defer high-resolution atlas texture loads until the corresponding skin is actually assigned, trading a small per-load runtime delay for a smaller initial download/memory footprint. This is Spine's own extension on top of the underlying loading mechanism — see `unity-addressables` for Addressables' general loading/reference-counting contract, which this extension builds on but doesn't replace.

## Two extension UPM packages
1. **`com.esotericsoftware.spine.on-demand-loading`** — generic infrastructure for a custom loading strategy.
2. **`com.esotericsoftware.spine.addressables`** — a ready-to-use implementation built on Unity Addressables; depends on the On-Demand Loading package, so install that one first.

## Setting up the Addressables extension
1. Mark the relevant textures Addressable in the project as usual.
2. Right-click the `SpineAtlasAsset`'s Inspector heading → "Add Addressables Loader." This creates an `AddressableTextureLoader` asset with its configuration parameters.
3. Build Addressables content normally.

No custom code is required for the standard case. A pre-build step automatically swaps the build output's textures for low-resolution placeholders; a post-build step restores the original high-resolution textures back into the project.

## Editor preview caveat
Low-resolution placeholders only take effect in an actual build — the Editor always shows the full-resolution texture. To preview the placeholder behavior without building, select the `AddressableTextureLoader` asset and use its "Testing" menu → "Assign Placeholders." This is preview-only and has no effect on a built executable — **never manually assign placeholders as a substitute for actually building**, since the automated pre/post-build swap already handles the real build correctly.

## Custom implementation
- For most custom cases, derive from `GenericOnDemandTextureLoader` and implement its abstract methods — use `AddressablesTextureLoader` as the reference implementation to follow.
- For a fully custom loading strategy, derive from `OnDemandTextureLoader` directly instead.

**Relevant source locations**:
- `spine-unity/Assets/Spine/Runtime/spine-unity/Asset Types/OnDemandTextureLoader.cs` — core infrastructure.
- `com.esotericsoftware.spine.on-demand-loading/Runtime/GenericOnDemandTextureLoader.cs` — the generic template to subclass.
- `com.esotericsoftware.spine.addressables/Runtime/AddressablesTextureLoader.cs` — the Addressables reference implementation.

## When to reach for this
Only once a real, measured build-size or memory problem justifies the added complexity (per `performance-and-algorithms.md`'s "measured, practical performance" principle) — most skeletons with a small, fixed skin set don't need this at all. Don't adopt it speculatively for a skeleton that only ever uses one or two skins.

## Licensing
A Spine license is required to integrate the Spine Runtimes into an application.
