# Rendering

Page: rendering. Two independent axes: active pipeline, and the alpha workflow the textures were exported/imported with.

## Pipelines
| Pipeline | Shaders |
|---|---|
| Built-in | ship in the spine-unity runtime package |
| URP | separate extension UPM package (2D and 3D Forward Renderer variants) |
| LWRP | separate legacy extension UPM package |
| Deferred | **no Spine shader supports it** |

Built-in `Spine/Skeleton` under URP, or a URP Spine shader under Built-in, is broken even if it renders something plausible. URP shaders never go on `SkeletonGraphic`.

## Materials
- One material per atlas page, created at import; non-`Normal` slot blend modes add materials (except `Additive` under PMA).
- The Materials array is rebuilt every frame from current attachments, atlas assets and blend modes: **any direct edit is overwritten on the next `LateUpdate()`**.
- Per instance: `SkeletonRendererCustomMaterials`/`SkeletonGraphicCustomMaterials`, or in code:
```csharp
// Full swap breaks batching with other instances on the original material.
// Take the original from SkeletonDataAsset.atlasAssets[0].PrimaryMaterial, never MeshRenderer.material.
skeletonAnimation.CustomMaterialOverride[originalMaterial] = newMaterial;
skeletonAnimation.CustomSlotMaterials[slot] = newMaterial;   // per slot
```
- Project-wide change: edit the Atlas asset.

| Tinting | Batching |
|---|---|
| `Skeleton.R/G/B/A` with PMA Vertex Colors on (works per slot) | preserved — default |
| `MaterialPropertyBlock` via `Renderer.SetPropertyBlock()` | broken unless values match across instances |
| Swapped tinted material instance | broken, and overwritten by the rebuild |

## Draw calls
Material array order follows draw order, one draw call per entry. Attachments spanning atlas pages or blend modes add entries. Levers: fewer atlas pages, attachments organised with draw order in mind.

## Sorting and transparency
- Alpha blending defeats z-sorting; slot draw order guarantees back-to-front within one mesh.
- Between meshes: camera depth → `Material.renderQueue` → shader `Queue` tag → `SortingGroup` → `SortingLayer`/`sortingOrder` → camera distance. Inspector `Sorting Layer`/`Order in Layer` map to `MeshRenderer.sortingLayerID`/`sortingOrder`.
- Multi-page skeleton mis-sorting under an orthographic camera: add a `SortingGroup`, or rotate the camera Y = 0.001.
- Drawing between parts: render separation; fading: render texture (see [utility-components.md](utility-components.md)).

## Shaders
| Shader | Effect |
|---|---|
| `Spine/Skeleton` | Unlit, no z-write; `SkeletonRenderer` default |
| `Spine/Skeleton Graphic` | Unlit, no z-write, single texture; `SkeletonGraphic` default |
| `Spine/Skeleton Lit`, `... Lit ZWrite` | Simple lit |
| `Spine/Skeleton Fill` | Colour overlay (`FillColor`, `FillPhase`) |
| `Spine/Skeleton Tint` | Two-colour tint (`Tint Color`, `Black Point`) |
| `Spine/Skeleton Tint Black`, `... Additive` | Animated per-slot tint black |
| `Spine/SkeletonGraphic Tint Black` | UI variant; Additive with `CanvasGroup` |
| `Spine/Sprite` (Unlit / Vertex Lit / Pixel Lit) | Normal maps, metallic, emission, cel ramps, rim |
| `Spine/Special` (Grayscale, Ghost) | Ghost = `SkeletonGhost` trail |
| `Spine/Blend Modes` (PMA Additive, Multiply, Screen) | Slot blend modes beyond Normal |
| `Spine/Outline`, `Spine/Outline/OutlineOnly-ZWrite` | Outline; ZWrite for combined-mesh rendering |

Extension shaders: URP 2D `Universal Render Pipeline/2D/Spine/{Skeleton, Skeleton Lit, Sprite}`; URP 3D `Universal Render Pipeline/Spine/{Skeleton, Skeleton Lit, Sprite, Outline/Skeleton-OutlineOnly}`; LWRP `Lightweight Render Pipeline/Spine/{Skeleton, Skeleton Lit, Sprite}`.

Feature setup:
- Tint Black: enable `Advanced → Tint Black` on the component; on `SkeletonGraphic` also TexCoord1 and TexCoord2 in the Canvas's Additional Shader Channels. Additive on `SkeletonGraphic`: "CanvasGroup Compatible" on both shader and component.
- Post-processing needing the z-buffer (Depth of Field): shader "Depth Write", or Render Queue Transparent → AlphaTest; some Render Pipeline Assets need both.
- Z-write / non-transparent shader: non-zero `Advanced → Z-Spacing` to avoid Z-fighting (does not fully fix aliasing at semi-transparent edges).

## PMA vs straight alpha
| Workflow | Mechanics |
|---|---|
| Premultiplied | RGB × alpha; `Blend One OneMinusSrcAlpha`; Normal and Additive share one pass via PMA vertex colours. Default until 4.2 |
| Straight | `Blend SrcAlpha OneMinusSrcAlpha` with no Additive slots, or convert in-shader: `#if defined(_STRAIGHT_ALPHA_INPUT) texColor.rgb *= texColor.a; #endif` |

Enable `Advanced → PMA Vertex Colors` whenever the material uses PMA. Mismatch artifacts: [faq.md](faq.md); import-side setting: Assets page.

## Custom Spine shader
- `Cull Off` is mandatory (flipped/negative-scaled skeletons).
- `Advanced → Add Normals` for lighting; `Solve Tangents` for normal maps (no normals/tangents by default).
- Multiply texture by vertex colour for PMA, matching `PMA Vertex Colors`; blend mode matches the workflow.
- `CanvasRenderer`-compatible shaders only on `SkeletonGraphic`; non-UI shaders only on `SkeletonAnimation`/`SkeletonMecanim`.
- `Spine/Skeleton` is the pattern: PMA blend, `ZWrite Off`, `Cull Off`, `return texColor * i.vertexColor`, `ShadowCaster` pass with alpha-threshold clip, optional `#pragma shader_feature _STRAIGHT_ALPHA_INPUT`. No official Shader Graph nodes exist; start from an existing Spine shader. Authoring from scratch is `shader-authoring`.
