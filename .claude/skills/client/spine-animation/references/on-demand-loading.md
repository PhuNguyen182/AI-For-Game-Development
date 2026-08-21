# On-Demand Loading — Deferred Atlas Textures & the Addressables Extension

Source: [spine-unity On-Demand Loading](https://esotericsoftware.com/spine-unity-on-demand-loading).
Covers: SKILL.md §4 — **"Reach for on-demand loading only once a measured build-size or memory problem justifies it"**.

By default every atlas texture is indirectly referenced by the
`SkeletonDataAsset` and loads with the skeleton, including pages a given
instance will never show. This extension defers the high-resolution load until
the matching skin is assigned, trading a small per-load delay for a smaller
download and memory footprint. It builds on Addressables rather than replacing
it — the general loading and reference-counting contract stays with
`unity-addressables`.

## The two extension packages

| Package | Holds | Use when | Source |
|---|---|---|---|
| `com.esotericsoftware.spine.on-demand-loading` | Generic infrastructure for a custom loading strategy | A bespoke strategy is genuinely required | [On-Demand Loading](https://esotericsoftware.com/spine-unity-on-demand-loading) |
| `com.esotericsoftware.spine.addressables` | Ready-to-use Addressables implementation; depends on the package above, so install that first | The standard case — no custom code needed | [On-Demand Loading](https://esotericsoftware.com/spine-unity-on-demand-loading) |

## Setting up the Addressables extension

| Step | Action | Source |
|---|---|---|
| 1 | Mark the relevant textures Addressable as usual | [On-Demand Loading](https://esotericsoftware.com/spine-unity-on-demand-loading) |
| 2 | Right-click the `SpineAtlasAsset` Inspector heading → "Add Addressables Loader", creating an `AddressableTextureLoader` asset | [On-Demand Loading](https://esotericsoftware.com/spine-unity-on-demand-loading) |
| 3 | Build Addressables content normally | [On-Demand Loading](https://esotericsoftware.com/spine-unity-on-demand-loading) |
| Automatic | A pre-build step swaps build-output textures for low-resolution placeholders; a post-build step restores the originals into the project | [On-Demand Loading](https://esotericsoftware.com/spine-unity-on-demand-loading) |

**Critical caveat**: placeholders only take effect in an actual build — the
Editor always shows full resolution. The `AddressableTextureLoader`'s
"Testing → Assign Placeholders" menu previews the behaviour, but manually
assigning placeholders is never a substitute for building; the pre/post-build
swap already handles the real build.

## Custom implementation

| Base class | Use when | Source |
|---|---|---|
| `GenericOnDemandTextureLoader` | Most custom cases — implement its abstract methods, following `AddressablesTextureLoader` as the reference | [On-Demand Loading](https://esotericsoftware.com/spine-unity-on-demand-loading) |
| `OnDemandTextureLoader` | A fully custom loading strategy that shares nothing with the generic template | [On-Demand Loading](https://esotericsoftware.com/spine-unity-on-demand-loading) |

| Source location | Holds | Source |
|---|---|---|
| `spine-unity/Assets/Spine/Runtime/spine-unity/Asset Types/OnDemandTextureLoader.cs` | Core infrastructure | [On-Demand Loading](https://esotericsoftware.com/spine-unity-on-demand-loading) |
| `com.esotericsoftware.spine.on-demand-loading/Runtime/GenericOnDemandTextureLoader.cs` | The generic template to subclass | [On-Demand Loading](https://esotericsoftware.com/spine-unity-on-demand-loading) |
| `com.esotericsoftware.spine.addressables/Runtime/AddressablesTextureLoader.cs` | The Addressables reference implementation | [On-Demand Loading](https://esotericsoftware.com/spine-unity-on-demand-loading) |

## When it is justified

| Condition | Verdict | Source |
|---|---|---|
| Many skins or atlas pages per skeleton, with a measured size or memory problem | Adopt it | synthesized |
| A small, fixed skin set | Do not adopt — the complexity buys nothing | synthesized |
| No measurement taken yet | Measure first, per `performance-and-algorithms.md`'s Verification section | synthesized |

A Spine license is required to integrate the Spine Runtimes into an application.
