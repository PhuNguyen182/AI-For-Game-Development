---
name: unity-urp-rendering
description: "URP configuration: ScriptableRendererFeature/RenderPass (Render Graph), Forward/Forward+/Deferred, URP Asset tiers, shadows, SRP Batcher, MSAA, 2D Renderer, camera stacking. Use once URP is the confirmed pipeline."
user-invocable: false
---

# Unity URP Rendering

Not for: which pipeline to use (`render-pipeline-urp-hdrp`), HDRP (`unity-hdrp-rendering`), shader content (`shader-authoring`), Volumes and post-processing (`unity-post-processing`), lights, probes and baking (`unity-lighting`), `Camera` scripting (`unity-camera-fundamentals`), entity rendering (`unity-entities-graphics`, needs the Forward+ path configured here), sprite data 2D lighting reads (`unity-2d-sprite`).
Docs: https://docs.unity3d.com/6000.5/Documentation/Manual/urp/ (manual), https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.3/api/ (API, URP 17.3) — if the project installs another URP, swap `@17.3`; the Render Graph migration changed behaviour between majors, so confirm the installed version before relying on a pass-authoring detail.
Companion: `unity:validate-urp-render-graph-renderer-feature` (official Unity plugin, if installed) reviews a finished Render Graph feature.

| Reference | Read when |
|---|---|
| [renderer-features-and-passes.md](references/renderer-features-and-passes.md) | Building a custom pass, or one stopped running after an upgrade |
| [rendering-paths.md](references/rendering-paths.md) | Choosing a path, or lights stop affecting objects past a count |
| [2d-renderer.md](references/2d-renderer.md) | `Light2D` is expected, or 2D lights do nothing |
| [camera-stacking-and-asset-settings.md](references/camera-stacking-and-asset-settings.md) | Compositing cameras, per-camera anti-aliasing, URP Asset tiering, Rendering Layers, SRP Batcher |

## Steps
1. **Confirm the URP Asset and Renderer the target quality tier actually uses** — Quality Settings can assign a different asset per level, and a camera can override the Renderer; every later step applies to one asset. Ask which tier a change is for when unstated.
2. **Write custom passes against Render Graph** (`RecordRenderGraph`), per [renderer-features-and-passes.md](references/renderer-features-and-passes.md); the `Execute` path survives only behind Compatibility Mode, and `csharp-standards` → `coding-principles.md` "Obsolete APIs" says new work uses the current API.
3. **Register the feature on the Renderer that tier uses** — a feature on another Renderer asset never runs and logs nothing.
4. **Choose the injection point from what the pass reads** (colour after the content it samples, depth after depth is written), not from how the effect should look, or it samples an empty or stale target.
5. **Choose the rendering path against measured light counts per tier**, per [rendering-paths.md](references/rendering-paths.md), backed by a Profiler capture (`csharp-standards` → `performance-and-algorithms.md` "Verification").
6. **Confirm the active Renderer is `Renderer2DData` before relying on `Light2D`**, per [2d-renderer.md](references/2d-renderer.md).
7. **Layer with a Base plus Overlay stack** (`UniversalAdditionalCameraData.cameraStack`), not independent full-screen cameras (a full render each), per [camera-stacking-and-asset-settings.md](references/camera-stacking-and-asset-settings.md). Per-camera anti-aliasing (FXAA/SMAA/TAA) is set on each camera. Scope lights and decals with Rendering Layers, not shader filtering.
8. **Verify SRP Batcher compatibility**; the toggle is not enough. Shader side with `shader-authoring`.
9. **Set tier-sensitive values per tier** — render scale, shadow distance, cascades, feature toggles in URP Asset variants per device tier; platform branches stay behind an interface (`csharp-standards` → `coding-principles.md` "Performance discipline"). Template defaults are a decision nobody made.
10. **Verify on the real tier** — capture on the quality level and device class that uses the asset; a pass on the wrong Renderer and a correct one look identical in code.

## Never
- Choose Deferred for "lights stop affecting objects": that is Forward's per-object limit, which Forward+ solves without losing MSAA.

## Output
```
## URP Configuration — <feature>
- URP Asset: <name> — tiers that reference it
- Renderer asset targeted: <name> — confirmed used by <tiers>
- Pass: <feature/pass names, Render Graph or Compatibility Mode, injection point and its data dependency>
- Rendering path: <path> — measurement that decided it
- 2D Renderer: <Renderer2DData and Light2D setup, or "not a 2D project">
- Camera stack: <base and overlays, or "single camera">
- Rendering Layers: <what they scope, or "unused">
- SRP Batcher: <enabled; how shader compatibility was confirmed>
- Tier mapping: <render scale, shadow distance, cascades per tier, or "unchanged, and why">
- Verified on: <quality tier and device class captured>
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Lights stop affecting the crowd, switch to Deferred" → declined unmeasured: the symptom is Forward's per-object limit; Forward+ removes it and keeps MSAA, which the mobile tier uses. Profiled both on a mid-tier Android under worst-case light count, recommended Forward+ for mobile, left PC unchanged.
