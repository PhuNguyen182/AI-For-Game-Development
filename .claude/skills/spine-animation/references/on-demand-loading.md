# On-Demand Loading

Page: on-demand-loading. By default every atlas texture loads with the `SkeletonDataAsset`, including pages an instance never shows. This defers the high-resolution load until the matching skin is assigned (small per-load delay, smaller download and memory). It builds on Addressables; the general contract is `unity-addressables`.

Adopt for many skins/atlas pages per skeleton with a measured size or memory problem. Not for a small fixed skin set; measure first.

| Package | Holds |
|---|---|
| `com.esotericsoftware.spine.on-demand-loading` | generic infrastructure for a custom strategy |
| `com.esotericsoftware.spine.addressables` | ready Addressables implementation; depends on the one above (install it first) |

## Addressables setup
1. Mark the textures Addressable as usual.
2. Right-click the `SpineAtlasAsset` Inspector heading → "Add Addressables Loader" (creates an `AddressableTextureLoader` asset).
3. Build Addressables content normally. A pre-build step swaps build-output textures for low-res placeholders; a post-build step restores originals.

Placeholders apply only in a real build; the Editor shows full resolution. `Testing → Assign Placeholders` previews them, but manual assignment never substitutes for building.

## Custom loader
- `GenericOnDemandTextureLoader` (`com.esotericsoftware.spine.on-demand-loading/Runtime/`): subclass for most cases; `AddressablesTextureLoader` (`com.esotericsoftware.spine.addressables/Runtime/`) is the reference.
- `OnDemandTextureLoader` (`spine-unity/Assets/Spine/Runtime/spine-unity/Asset Types/`): fully custom strategy.
