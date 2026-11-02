---
name: unity-urp-rendering
description: "URP: ScriptableRendererFeature, Render Graph, Forward+, URP Asset tiers, SRP Batcher. Use once URP is confirmed."
user-invocable: false
---

# Unity URP Rendering

- **Not for:** which pipeline to use (`render-pipeline-urp-hdrp`).
- **Not for:** HDRP (`unity-hdrp-rendering`).
- **Not for:** shader content (`shader-authoring`).
- **Not for:** Volumes and post-processing (`unity-post-processing`).
- **Not for:** lights, probes and baking (`unity-lighting`).
- **Not for:** `Camera` scripting (`unity-camera-fundamentals`).
- **Not for:** entity rendering (`unity-entities-graphics`), which needs the Forward+ path configured here.
- **Not for:** sprite data 2D lighting reads (`unity-2d-sprite`).
- **Docs:** https://docs.unity3d.com/6000.5/Documentation/Manual/urp/ (manual), https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.3/api/ (API, URP 17.3).
  - **Other URP version:** if the project installs another URP, swap `@17.3`.
  - **Render Graph migration:** it changed behaviour between majors, so confirm the installed version before relying on a pass-authoring detail.
- **Companion:** `unity:validate-urp-render-graph-renderer-feature` (official Unity plugin, if installed) reviews a finished Render Graph feature.

## References
- **[renderer-features-and-passes.md](references/renderer-features-and-passes.md):** Building a custom pass, or one stopped running after an upgrade.
- **[rendering-paths.md](references/rendering-paths.md):** Choosing a path, or lights stop affecting objects past a count.
- **[2d-renderer.md](references/2d-renderer.md):** `Light2D` is expected, or 2D lights do nothing.
- **[camera-stacking-and-asset-settings.md](references/camera-stacking-and-asset-settings.md):** Compositing cameras, per-camera anti-aliasing, URP Asset tiering, Rendering Layers, SRP Batcher.

## Steps
1. **Confirm the URP Asset and Renderer the target quality tier actually uses:** Quality Settings can assign a different asset per level, and a camera can override the Renderer.
   - **Why:** every later step applies to one asset.
   - **Tier a change is for unstated:** step 11.
2. **Write custom passes against Render Graph:** `RecordRenderGraph`, per [renderer-features-and-passes.md](references/renderer-features-and-passes.md).
   - **Unity 6.3:** hides Compatibility Mode behind the `URP_COMPATIBILITY_MODE` define.
   - **Unity 6.4:** removes Compatibility Mode, so an `Execute`-only pass is dead on 6.4+.
   - **Obsolete APIs:** `csharp-standards` → `coding-principles.md` "Obsolete APIs" says new work uses the current API.
3. **Register the feature on the Renderer that tier uses:** a feature on another Renderer asset never runs and logs nothing.
4. **Choose the injection point from what the pass reads, not from how the effect should look:** otherwise the pass samples an empty or stale target.
   - **Colour:** inject after the content the pass samples.
   - **Depth:** inject after depth is written.
5. **Choose the rendering path against measured light counts per tier:** per [rendering-paths.md](references/rendering-paths.md).
   - **Evidence:** a Profiler capture (`csharp-standards` → `performance-and-algorithms.md` "Verification").
6. **Confirm the active Renderer is `Renderer2DData` before relying on `Light2D`:** per [2d-renderer.md](references/2d-renderer.md).
7. **Layer with a Base plus Overlay stack:** `UniversalAdditionalCameraData.cameraStack`, per [camera-stacking-and-asset-settings.md](references/camera-stacking-and-asset-settings.md).
   - **Not independent full-screen cameras:** each is a full render.
   - **Anti-aliasing:** per-camera (FXAA/SMAA/TAA), set on each camera.
   - **Lights and decals:** scope them with Rendering Layers, not shader filtering.
8. **Verify SRP Batcher compatibility:** the toggle is not enough.
   - **Shader side:** `shader-authoring`.
9. **Set tier-sensitive values per tier:** owner `unity-performance-engineer`; `technical-artist` states the look's need.
   - **Values:** render scale, shadow distance, cascades, feature toggles in URP Asset variants per device tier.
   - **Platform branches:** stay behind an interface (`csharp-standards` → `coding-principles.md` "Performance discipline").
   - **Template defaults:** a decision nobody made.
10. **Verify on the real tier:** capture on the quality level and device class that uses the asset.
    - **Why:** a pass on the wrong Renderer and a correct one look identical in code.
11. **Missing input:** the tier a change is for is unstated → dispatched agent `Blocked` or `Needs-decision`; main session `AskUserQuestion`.

## Never
- **Choose Deferred for "lights stop affecting objects":** that is Forward's per-object limit, which Forward+ solves without losing MSAA.

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
```

## Example
- **"Lights stop affecting the crowd, switch to Deferred":** declined unmeasured, the symptom is Forward's per-object limit.
  - **Why:** Forward+ removes the limit and keeps MSAA, which the mobile tier uses.
  - **Did instead:** profiled both on a mid-tier Android under worst-case light count, recommended Forward+ for mobile, left PC unchanged.
