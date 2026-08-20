# Root Links

Root/index pages, as given by the user. Follow their own in-page navigation (anchors) for anything not covered by the other files in this folder.

## Given by the user
- [Spine Unity main components](https://esotericsoftware.com/spine-unity-main-components#Main-Components) — `SkeletonRenderer`, `SkeletonAnimation`, `SkeletonGraphic`, `SkeletonMecanim`, the `Skeleton`/`AnimationState`/`TrackEntry` scripting API, skin/attachment/repacking, runtime instantiation. Covered in [main-components.md](main-components.md).
- [Spine Unity utility components](https://esotericsoftware.com/spine-unity-utility-components) — followers, `SkeletonUtility`/`SkeletonUtilityBone`, root motion, render separation, ragdoll/ghost/render-texture helper components. Covered in [utility-components.md](utility-components.md).
- [Spine Unity rendering](https://esotericsoftware.com/spine-unity-rendering) — render pipeline support, materials/atlas/draw calls, sorting, shaders (Built-in/URP/LWRP), PMA vs straight alpha, custom shader requirements. Covered in [rendering.md](rendering.md).
- [Spine Unity Timeline](https://esotericsoftware.com/spine-unity-timeline) — the Timeline extension package's tracks/clips. Covered in [timeline.md](timeline.md).
- [Spine Unity on-demand loading](https://esotericsoftware.com/spine-unity-on-demand-loading) — the on-demand-loading/Addressables extension packages for atlas textures. Covered in [on-demand-loading.md](on-demand-loading.md).
- [Spine Unity FAQ](https://esotericsoftware.com/spine-unity-faq) — import/visual/performance/licensing Q&A. Covered in [faq.md](faq.md).

## Related pages referenced by the above (not independently fetched, but linked from them)
- [Spine Unity installation](https://esotericsoftware.com/spine-unity-installation#Compatible-Unity-Versions) — compatible Unity version table per runtime, referenced by the FAQ's compatibility section.
- [Spine Unity assets](https://esotericsoftware.com/spine-unity-assets) — `SkeletonDataAsset`/`SpineAtlasAsset` import settings, Premultiplied vs. Straight Alpha import, referenced by both rendering.md and faq.md.
- [Spine Metrics](https://esotericsoftware.com/spine-metrics#Metrics-view) — the Metrics view used to audit a skeleton's vertex/deformation/clipping cost, referenced by faq.md's Performance section.

## Licensing
A Spine license is required to integrate the Spine Runtimes into any application — stated on both main-components.md's and on-demand-loading.md's source pages. This is a legal/commercial precondition, not a technical one; flag it if a project pulls in `Spine.Unity.*` without a confirmed license.
