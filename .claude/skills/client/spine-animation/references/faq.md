# FAQ — Import, Visual, Cross-Machine & Performance Symptoms

Source: [spine-unity FAQ](https://esotericsoftware.com/spine-unity-faq).
Covers: SKILL.md §4 — **"Diagnose a Spine-specific symptom against the FAQ before assuming a generic Unity cause"**, **"Ship the binary `.skel.bytes` export and pool skeleton instances"**.

A symptom-to-root-cause index. Read a row before treating a Spine symptom as a
generic Unity rendering or performance bug — most visual faults here trace to
one alpha-workflow or Color Space mismatch rather than to a shader defect.
Shader mechanics are [rendering.md](rendering.md).

## Contents

- [Compatibility and import](#compatibility-and-import)
- [Choosing the alpha workflow](#choosing-the-alpha-workflow)
- [Visual symptoms](#visual-symptoms)
- [Inconsistent behaviour across machines](#inconsistent-behaviour-across-machines)
- [Performance](#performance)

## Compatibility and import

| Symptom | Root cause and fix | Source |
|---|---|---|
| Compile errors naming Unity methods | The Unity version is outside the installed runtime's supported range — check the Compatible Unity Versions table | [Installation](https://esotericsoftware.com/spine-unity-installation#Compatible-Unity-Versions) |
| "Could not automatically set the AtlasAsset for .." | The atlas file must use the `.atlas.txt` extension, not `.atlas`; also check for missing attachments via Find and Replace with "Missing images" enabled | [FAQ](https://esotericsoftware.com/spine-unity-faq) |
| "Failed to read version info at skeleton" | The export selected a lower Spine version than the editor. That export form exists only for importing into a lower-version Spine *Editor* — re-export at the matching version | [FAQ](https://esotericsoftware.com/spine-unity-faq) |
| "Opening scene in read-only package!" | A Unity bug blocking example scenes opened from a git-sourced UPM package — copy the scene files into `Assets` first | [FAQ](https://esotericsoftware.com/spine-unity-faq) |

## Choosing the alpha workflow

| Workflow | Choose when | Source |
|---|---|---|
| Straight alpha | Linear color space (Unity's default), a possible future color-space switch, compatibility with standard non-Spine shaders, or a simpler workflow is wanted | [FAQ](https://esotericsoftware.com/spine-unity-faq) |
| PMA | Gamma color space exclusively, mipmap quality at transparent edges matters, and the team accepts PMA's workflow limits | [FAQ](https://esotericsoftware.com/spine-unity-faq) |

**Critical caveat**: PMA is not supported under Linear color space at all. Any
project on the Unity default has effectively already chosen straight alpha.

## Visual symptoms

| Symptom | Root cause and fix | Source |
|---|---|---|
| Dark borders around transparent areas | Exported PMA but imported or rendered with mismatched settings; straight alpha with mipmaps shows this too when transparent-pixel colour bleed is missing | [FAQ](https://esotericsoftware.com/spine-unity-faq) |
| Washed-out or desaturated colours | Linear color space plus PMA-oriented auto-import settings, which set `sRGB (Color Texture)` wrongly. Switch to Gamma only if PMA is genuinely required | [FAQ](https://esotericsoftware.com/spine-unity-faq) |
| Colourful stripes in transparent areas | Exported straight alpha but imported or rendered as PMA — see the premultiplied-vs-straight import section on the [Assets](https://esotericsoftware.com/spine-unity-assets) page | [FAQ](https://esotericsoftware.com/spine-unity-faq) |
| White borders with Generate Mip Maps on | PMA textures with `sRGB (Color Texture)` left enabled | [FAQ](https://esotericsoftware.com/spine-unity-faq) |
| Wrong colours specifically with Tint Black | `Advanced → Tint Black` is enabled on the shader/material but not on the `SkeletonRenderer`/`SkeletonAnimation` component | [FAQ](https://esotericsoftware.com/spine-unity-faq) |
| A material assigned on the `MeshRenderer` does not stick | Expected — the Materials array is rebuilt every frame; use the custom-materials components, see [rendering.md](rendering.md) | [FAQ](https://esotericsoftware.com/spine-unity-faq) |
| Spine shaders look wrong under URP | The base runtime ships Built-in pipeline shaders only — install the URP Shaders extension package | [FAQ](https://esotericsoftware.com/spine-unity-faq) |
| Outline shader shows only outlines under URP | Either a Built-in outline shader under URP (switch to the URP one), or a single-pass outline-only shader where a combined render is needed — use `RenderExistingMesh` for a second pass | [FAQ](https://esotericsoftware.com/spine-unity-faq) |
| Unwanted inner outlines between parts | Multiple materials produce separately outlined submeshes — reduce to one material by atlas packing or runtime repacking, or use `RenderCombinedMesh` with an outline-only shader | [FAQ](https://esotericsoftware.com/spine-unity-faq) |
| Normal map looks wrong | `Advanced → Solve Tangents` is not enabled on the `SkeletonRenderer` | [FAQ](https://esotericsoftware.com/spine-unity-faq) |
| `SkeletonGraphic` brightens during a `CanvasGroup` fade | Vertex-colour alpha conflicts with premultiplied-alpha shaders — see [main-components.md](main-components.md) | [FAQ](https://esotericsoftware.com/spine-unity-faq) |
| Parts show through each other during a fade | The overlapping-triangle transparency artifact — use the render-texture fade in [utility-components.md](utility-components.md), never a naive alpha reduction | [FAQ](https://esotericsoftware.com/spine-unity-faq) |
| Repacked skin fine in Editor, white polygons in a build | One of the repack preconditions failed — see the failure table in [skeleton-api.md](skeleton-api.md) | [FAQ](https://esotericsoftware.com/spine-unity-faq) |

## Inconsistent behaviour across machines

| Symptom | Root cause and fix | Source |
|---|---|---|
| The project behaves differently per machine with a git UPM URL | A URL ending in `#4.3` resolves to that branch's *latest* commit, so machines pulling at different times get different code — pin a full commit SHA instead | [FAQ](https://esotericsoftware.com/spine-unity-faq) |
| Finding the SHA to pin | Open the branch's [GitHub commits page](https://github.com/EsotericSoftware/spine-runtimes/commits/4.3) and copy the full SHA | [FAQ](https://esotericsoftware.com/spine-unity-faq) |

## Performance

| Symptom | Root cause and fix | Source |
|---|---|---|
| FPS drop or GC allocation when instantiating a skeleton | Export binary `.skel.bytes` rather than `.json`; load at level-load time; pool instead of Instantiate/Destroy, pre-warming ~10 instances; on despawn disable the GameObject and call `AnimationState.ClearTracks()` rather than destroying | [FAQ](https://esotericsoftware.com/spine-unity-faq) |
| Many draw calls, batches, or materials for one skeleton | Multiple atlas pages, or slots alternating blend modes — see [rendering.md](rendering.md), and consider runtime repacking per [skeleton-api.md](skeleton-api.md) | [FAQ](https://esotericsoftware.com/spine-unity-faq) |

| Optimization checklist item | What it targets | Source |
|---|---|---|
| Avoid clipping-attachment polygons where Unity masking would do; minimize their vertex count when unavoidable | Per-frame clipping cost | [FAQ](https://esotericsoftware.com/spine-unity-faq) |
| Minimize mesh-deformation keys, overall vertex count, and unnecessary keyframes | Per-frame skinning and memory cost | [FAQ](https://esotericsoftware.com/spine-unity-faq) |
| Audit the skeleton in the Metrics view | Finding which of the above actually dominates | [Metrics](https://esotericsoftware.com/spine-metrics#Metrics-view) |
| Minimize atlas page textures and order attachments to minimize material switches | Draw-call count | [FAQ](https://esotericsoftware.com/spine-unity-faq) |
| Share one larger atlas across skeletons via the `SkeletonDataAsset` atlas array | Texture memory and batching across instances | [FAQ](https://esotericsoftware.com/spine-unity-faq) |

A Spine license is required to integrate the Spine Runtimes into any application.
