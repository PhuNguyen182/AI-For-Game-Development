# Rendering — Pipelines, Shaders, Materials, Draw Calls & Alpha Workflow

Source: [spine-unity Rendering](https://esotericsoftware.com/spine-unity-rendering).
Covers: SKILL.md §4 — **"Match the shader family to the render pipeline and never mix them"**, **"Never assign a Materials array entry or `MeshRenderer.material` directly"**.

Two independent axes decide everything here: which pipeline is active, and
which alpha workflow the textures were exported and imported with. Getting
either wrong renders *something*, which is why the symptom index in
[faq.md](faq.md) matters more than eye inspection. The components these
materials sit on are [main-components.md](main-components.md); the effect
components are [utility-components.md](utility-components.md).

## Contents

- [Pipeline support](#pipeline-support)
- [Materials and the rebuild rule](#materials-and-the-rebuild-rule)
- [Draw calls and material switching](#draw-calls-and-material-switching)
- [Transparency and draw order](#transparency-and-draw-order)
- [Shader catalog](#shader-catalog)
- [PMA vs. straight alpha](#pma-vs-straight-alpha)
- [Writing a custom Spine shader](#writing-a-custom-spine-shader)

## Pipeline support

| Pipeline | Shader source | Source |
|---|---|---|
| Built-in Render Pipeline | Default shaders ship in the spine-unity runtime package | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |
| Universal Render Pipeline | A separate extension UPM package, with 2D and 3D Forward Renderer variants | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |
| Lightweight Render Pipeline | A separate legacy extension UPM package | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |
| Deferred Shading | **Not supported** by any Spine shader, Built-in or URP | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |

**Critical caveat**: a Built-in `Spine/Skeleton` shader under URP, or a URP
Spine shader under Built-in, is broken even where it renders something
plausible. Never mix families across a pipeline boundary.

## Materials and the rebuild rule

| Fact | What it decides | Source |
|---|---|---|
| One material per atlas page | Created automatically at import | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |
| Non-`Normal` slot blend modes add materials | Except `Additive` under PMA, which reuses the normal material | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |
| The Materials array is rebuilt every frame | From current attachments, their atlas assets, and slot blend modes — **any direct edit is overwritten on the next `LateUpdate()`** | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |
| Per-instance override | `SkeletonRendererCustomMaterials`/`SkeletonGraphicCustomMaterials`, or `CustomMaterialOverride`/`CustomSlotMaterials` in code | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |
| Project-wide change | Edit the Atlas asset itself, not the instance | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |

```csharp
// Full swap — breaks batching with other instances on the original material.
// Take the original from SkeletonDataAsset.atlasAssets[0].PrimaryMaterial,
// never from MeshRenderer.material.
this.skeletonAnimation.CustomMaterialOverride[originalMaterial] = newMaterial;

// Per-slot override.
this.skeletonAnimation.CustomSlotMaterials[slot] = newMaterial;
```

| Tinting approach | Batching consequence | Source |
|---|---|---|
| `Skeleton.R`/`G`/`B`/`A` with PMA Vertex Colors enabled | Preserves batching; works per-slot too — the correct default | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |
| `MaterialPropertyBlock` via `Renderer.SetPropertyBlock()` | Differing values per instance still break batching; batching survives only when values match | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |
| Swapping in a tinted material instance | Breaks batching and is overwritten by the next rebuild | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |

## Draw calls and material switching

| Fact | What it decides | Source |
|---|---|---|
| Material array order follows draw order | Each entry is one draw call | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |
| Attachments spanning atlas pages or blend modes add entries | The array is populated in the order draw order needs them | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |
| The lever is packing and ordering | Pack across fewer atlas pages and organize attachments with draw order in mind, not by visual grouping | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |

## Transparency and draw order

| Fact | What it decides | Source |
|---|---|---|
| Alpha blending defeats z-buffer sorting | Triangles must render back-to-front; slot draw order guarantees this within one mesh | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |
| Between meshes, order resolves by priority | Camera depth → `Material.renderQueue` → shader `Queue` tag → `SortingGroup` → `SortingLayer`/`sortingOrder` → distance from camera | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |
| Inspector sorting properties | `Sorting Layer`/`Order in Layer` back onto `MeshRenderer.sortingLayerID`/`sortingOrder` | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |
| Multi-page skeletons under an orthographic camera can mis-sort | Add a `SortingGroup` to the skeleton GameObject, or rotate the camera negligibly (Y = 0.001) to break the degenerate case | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |
| Drawing between skeleton parts | Requires render separation, see [utility-components.md](utility-components.md) | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |
| Fading a skeleton | Render to a `RenderTexture` at full opacity, then draw that at the target opacity — lowering alpha directly shows attachments through each other | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |

## Shader catalog

| Built-in shader | Effect | Source |
|---|---|---|
| `Spine/Skeleton` | Unlit, no z-write — the default for `SkeletonRenderer` | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |
| `Spine/Skeleton Graphic` | Unlit, no z-write, single texture — the default for `SkeletonGraphic` | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |
| `Spine/Skeleton Lit`, `Spine/Skeleton Lit ZWrite` | Simple lit, without and with z-write | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |
| `Spine/Skeleton Fill` | Unlit with a colour overlay (`FillColor`, `FillPhase`) | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |
| `Spine/Skeleton Tint` | Unlit two-colour tint — light via `Tint Color`, dark via `Black Point` | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |
| `Spine/Skeleton Tint Black`, `... Additive` | Animated per-slot tint-black, and its additive variant | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |
| `Spine/SkeletonGraphic Tint Black` | The `SkeletonGraphic` variant; supports Additive with `CanvasGroup` | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |
| `Spine/Sprite` (Unlit / Vertex Lit / Pixel Lit) | Configurable — normal maps, metallic, emission, cel ramps, rim lighting | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |
| `Spine/Special` (Grayscale, Ghost) | Ghost is the trail variant used by `SkeletonGhost` | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |
| `Spine/Blend Modes` (PMA Additive, Multiply, Screen) | Slot blend modes beyond Normal | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |
| `Spine/Outline`, `Spine/Outline/OutlineOnly-ZWrite` | Outline variants; the ZWrite one is for combined-mesh rendering | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |

| Extension shaders | Names | Source |
|---|---|---|
| URP 2D Renderer | `Universal Render Pipeline/2D/Spine/Skeleton`, `.../Skeleton Lit`, `.../Sprite` | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |
| URP 3D Forward Renderer | `Universal Render Pipeline/Spine/Skeleton`, `.../Skeleton Lit`, `.../Sprite`, `.../Outline/Skeleton-OutlineOnly` | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |
| LWRP (legacy) | `Lightweight Render Pipeline/Spine/Skeleton`, `.../Skeleton Lit`, `.../Sprite` | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |

| Feature setup | Requirement | Source |
|---|---|---|
| Tint Black | Enable `Advanced → Tint Black` on the component; on `SkeletonGraphic` also enable TexCoord1 and TexCoord2 in the Canvas's Additional Shader Channels | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |
| Tint Black Additive on `SkeletonGraphic` | Enable "CanvasGroup Compatible" on both the shader and the component | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |
| Post-processing needing the z-buffer, e.g. Depth of Field | Enable the shader's "Depth Write", or move the material's Render Queue from Transparent to AlphaTest — some Render Pipeline Assets need both | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |
| Z-write or a non-transparent shader | Set `Advanced → Z-Spacing` non-zero to avoid Z-fighting; it does not fully solve aliasing at semi-transparent edges | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |

**Critical caveat**: URP Spine shaders must never go on `SkeletonGraphic` or
the Deferred path. Only `Spine/SkeletonGraphic*` materials belong on
`SkeletonGraphic` — the single most common Spine rendering mistake.

## PMA vs. straight alpha

| Workflow | Mechanics | Source |
|---|---|---|
| Premultiplied Alpha | RGB pre-multiplied by alpha; `Blend One OneMinusSrcAlpha`; lets Normal and Additive slot blend modes share one single-pass shader via PMA vertex colours. Was the default until spine-unity 4.2 | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |
| Straight Alpha | RGB not pre-multiplied; either standard `Blend SrcAlpha OneMinusSrcAlpha` with no Additive slots, or a shader-level conversion `#if defined(_STRAIGHT_ALPHA_INPUT) texColor.rgb *= texColor.a; #endif` | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |
| Component setting | Enable `Advanced → PMA Vertex Colors` whenever the material uses PMA | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |

Which artifact each mismatch produces is indexed in [faq.md](faq.md); the
import-side setting lives on the Assets page linked from
[root-links.md](root-links.md).

## Writing a custom Spine shader

| Requirement | Why | Source |
|---|---|---|
| `Cull Off` is mandatory | Flipped or negatively scaled skeletons need both faces rendered | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |
| Enable `Advanced → Add Normals` for lighting | Meshes carry no normals by default | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |
| Enable `Advanced → Solve Tangents` for normal maps | Meshes carry no tangents by default | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |
| Multiply texture by vertex colour for PMA | Must match `Advanced → PMA Vertex Colors` on the component | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |
| Blend mode must match the alpha workflow | `Blend One OneMinusSrcAlpha` for PMA, `Blend SrcAlpha OneMinusSrcAlpha` for straight | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |
| Keep the UI/non-UI split strict | `CanvasRenderer`-compatible shaders only on `SkeletonGraphic`; non-UI shaders only on `SkeletonAnimation`/`SkeletonMecanim` | [Rendering](https://esotericsoftware.com/spine-unity-rendering) |

`Spine/Skeleton` itself demonstrates the pattern: PMA blend, `ZWrite Off`,
`Cull Off`, `return (texColor * i.vertexColor)`, a `"ShadowCaster"` pass with
an alpha-threshold clip, and an optional `#pragma shader_feature
_STRAIGHT_ALPHA_INPUT`. No official Shader Graph nodes exist for Spine;
straight-alpha textures work with ordinary non-Spine shaders, and starting from
an existing Spine shader is the fastest path to a working custom one.
Authoring one from scratch is `shader-authoring`'s territory, not this skill's.
