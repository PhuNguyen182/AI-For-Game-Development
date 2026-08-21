# Root Links — spine-unity Documentation

Source: the root documentation pages listed below, as provided for this skill.
Covers: the whole skill — provenance and page index for every file in this
folder.

Anchors every link in this folder to the official spine-unity documentation
(spine-unity v4.3+). Anything this skill cites resolves under one of these
pages; anything that does not is out of scope for the skill, not merely
undocumented here. **The spine-unity docs are unversioned per URL** — there is
no version segment to pin, so confirm against the runtime version actually
installed before relying on a version-sensitive detail.

## Pages this skill was built from

| Page | Holds | Distilled in | Source |
|---|---|---|---|
| Main Components | `SkeletonRenderer`, `SkeletonAnimation`, `SkeletonGraphic`, `SkeletonMecanim`, the `Skeleton`/`AnimationState`/`TrackEntry` API, skins, repacking, runtime instantiation | [main-components.md](main-components.md), [skeleton-api.md](skeleton-api.md), [animation-state.md](animation-state.md) | [Main Components](https://esotericsoftware.com/spine-unity-main-components#Main-Components) |
| Utility Components | Followers, `SkeletonUtility`/`SkeletonUtilityBone`, root motion, render separation, ragdoll/ghost/render-texture helpers | [utility-components.md](utility-components.md) | [Utility Components](https://esotericsoftware.com/spine-unity-utility-components) |
| Rendering | Pipeline support, materials, atlas and draw calls, sorting, shader catalog, PMA vs. straight alpha, custom shader requirements | [rendering.md](rendering.md) | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |
| Timeline | The Timeline extension package's tracks and clips | [timeline.md](timeline.md) | [Timeline](https://esotericsoftware.com/spine-unity-timeline) |
| On-Demand Loading | The on-demand-loading and Addressables extension packages for atlas textures | [on-demand-loading.md](on-demand-loading.md) | [On-Demand Loading](https://esotericsoftware.com/spine-unity-on-demand-loading) |
| FAQ | Import, visual, cross-machine, performance, and licensing Q&A | [faq.md](faq.md) | [FAQ](https://esotericsoftware.com/spine-unity-faq) |

## Pages linked from the above, not independently distilled

| Page | Holds | Source |
|---|---|---|
| Installation | The Compatible Unity Versions table per runtime version | [Installation](https://esotericsoftware.com/spine-unity-installation#Compatible-Unity-Versions) |
| Assets | `SkeletonDataAsset`/`SpineAtlasAsset` import settings, premultiplied vs. straight alpha import | [Assets](https://esotericsoftware.com/spine-unity-assets) |
| Spine Metrics | The Metrics view for auditing a skeleton's vertex, deformation, and clipping cost | [Metrics](https://esotericsoftware.com/spine-metrics#Metrics-view) |

A Spine license is required to integrate the Spine Runtimes into any
application — stated on both the Main Components and On-Demand Loading pages.
This is a legal precondition rather than a technical one; flag it if a project
pulls in `Spine.Unity.*` without a confirmed license.
