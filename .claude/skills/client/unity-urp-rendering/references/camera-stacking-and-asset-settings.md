# Camera Stacking, URP Asset Settings & SRP Batcher

Sources: [Set up a camera stack in URP](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/camera-stacking.html), [Universal Render Pipeline asset reference](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/universalrp-asset.html), [Rendering Layers in URP](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/features/rendering-layers.html).
Covers: SKILL.md §4 — **"Composite with a Base plus Overlay camera stack"**, **"Scope light and decal influence with Rendering Layers rather than filtering in a shader"**, **"Map every tier-sensitive setting deliberately"**, **"Verify SRP Batcher compatibility rather than assuming the toggle is enough"**.

## Contents
- [Camera stacking](#camera-stacking)
- [URP Asset settings](#urp-asset-settings)
- [SRP Batcher](#srp-batcher)

Compositing, per-tier quality, and batching — the three places URP
configuration meets the device it ships on.

## Camera stacking

| Subject | What it decides | Source |
|---|---|---|
| Base camera | Renders the scene and owns the output target; a stack has exactly one | [Camera stacking](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/camera-stacking.html) |
| Overlay camera | Renders on top of the base's result in stack order — the sanctioned way to layer, at far less cost than a second full render | [Camera stacking](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/camera-stacking.html) |
| `UniversalAdditionalCameraData.cameraStack` | The scripting entry point for the stack, plus renderer override and other per-camera URP fields | [UniversalAdditionalCameraData](https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.3/api/UnityEngine.Rendering.Universal.UniversalAdditionalCameraData.html) |
| Renderer override | A camera can use a different Renderer than the asset's default — which is also a way a pass can appear to be missing on one camera | [Universal Additional Camera Data](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/universal-additional-camera-data.html) |

## URP Asset settings

| Setting | What it decides | Source |
|---|---|---|
| Render Scale | Renders at a fraction of screen resolution and upscales — the single most effective mobile fill-rate lever | [URP asset reference](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/universalrp-asset.html) |
| Shadow Distance | How far shadows are drawn; the dominant cost driver in most shadow budgets | [URP asset reference](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/universalrp-asset.html) |
| Shadow Cascades | Trades shadow resolution distribution against per-cascade cost — more cascades is not simply better | [URP asset reference](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/universalrp-asset.html) |
| Per-tier assets | Quality Settings can assign a different URP Asset per level, which is how tier differences are expressed without branching code | [URP asset reference](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/universalrp-asset.html) |
| Rendering Layers | Scope which lights and decals affect which renderers — distinct from physics and culling Layers | [Rendering Layers](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/features/rendering-layers.html) |

## SRP Batcher

| Subject | What it decides | Source |
|---|---|---|
| Enabling it | A toggle on the URP Asset — necessary but not sufficient | [Enable the SRP Batcher](https://docs.unity3d.com/6000.5/Documentation/Manual/SRPBatcher-Enable.html) |
| Shader compatibility | Requires per-material properties in the expected `UnityPerMaterial` constant buffer; a non-conforming shader silently falls out | [Make a URP shader SRP Batcher compatible](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/shaders-in-universalrp-srp-batcher.html) |
| What it batches | Draws sharing a shader variant, by making material data persistent on the GPU — it reduces setup cost, not draw count | [Enable the SRP Batcher](https://docs.unity3d.com/6000.5/Documentation/Manual/SRPBatcher-Enable.html) |

**Critical caveat**: render scale, shadow distance, and cascade count left at
template defaults are the commonest reason a project misses its mobile frame
budget while every individual asset looks reasonable. They are per-tier
decisions, and a default is not one.
