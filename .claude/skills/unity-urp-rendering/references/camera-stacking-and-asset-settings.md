# Camera Stacking, URP Asset Settings and SRP Batcher

Sources (manual paths under the `Docs:` base): [s] `camera-stacking.html`, [a] `universalrp-asset.html`, [l] `features/rendering-layers.html`, [b] `shaders-in-universalrp-srp-batcher.html`, [u] `universal-additional-camera-data.html`. SRP Batcher enable page: `https://docs.unity3d.com/6000.5/Documentation/Manual/SRPBatcher-Enable.html`.

## Camera stacking

| Subject | Fact that decides |
|---|---|
| Base camera | Renders the scene and owns the output target; exactly one per stack [s] |
| Overlay camera | Renders over the base result in stack order, far cheaper than a second full render [s] |
| `UniversalAdditionalCameraData.cameraStack` | Scripting entry point for the stack and per-camera URP fields |
| Renderer override | A camera can use a Renderer other than the asset's default, which makes a pass appear missing on one camera [u] |
| Anti-aliasing mode | Per-camera FXAA/SMAA/TAA lives on `UniversalAdditionalCameraData`, not in a Volume Override; MSAA is on the URP Asset |

## URP Asset [a]

| Setting | Fact that decides |
|---|---|
| Render Scale | Renders at a fraction of resolution and upscales; the most effective mobile fill-rate lever |
| Shadow Distance | Dominant cost driver in most shadow budgets |
| Shadow Cascades | Trades resolution distribution against per-cascade cost; more is not simply better |
| Per-tier assets | Quality Settings assign a different URP Asset per level: how tier differences are expressed without branching code |
| Rendering Layers | Scope which lights and decals affect which renderers; distinct from physics and culling Layers [l] |

**Caveat:** render scale, shadow distance and cascade count left at template defaults are the commonest reason a project misses its mobile frame budget while every asset looks reasonable.

## SRP Batcher

| Subject | Fact that decides |
|---|---|
| Enabling | Toggle on the URP Asset; necessary, not sufficient |
| Shader compatibility | Per-material properties must sit in the `UnityPerMaterial` constant buffer; a non-conforming shader silently falls out [b] |
| What it batches | Draws sharing a shader variant, by keeping material data persistent on the GPU; it cuts setup cost, not draw count |
