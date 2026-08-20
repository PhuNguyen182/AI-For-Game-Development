---
name: unity-urp-rendering
description: >
  Technique for deep Universal Render Pipeline (URP) configuration — Renderer
  Features (`ScriptableRendererFeature`/`ScriptableRenderPass`), the
  Forward/Forward+/Deferred/Deferred+ rendering paths, the URP Asset's
  quality/shadow/SRP Batcher settings, Volume-driven post-processing, the 2D
  Renderer (Light2D, 2D shadows), camera stacking
  (`UniversalAdditionalCameraData`), and Rendering Layers. Use this once the
  project is confirmed to be on URP and the task goes beyond "which pipeline
  do we target" into actually configuring URP's own systems. Do not use this
  for the initial pipeline-confirmation/shader-targeting decision between URP
  and HDRP — that's `render-pipeline-urp-hdrp`. Do not use this for HDRP
  (`unity-hdrp-rendering`), the shader node-graph/HLSL content itself
  (`shader-authoring`), plain `Camera`/`Transform` scripting
  (`unity-camera-fundamentals`), Cinemachine (`unity-cinemachine-authoring`),
  or particle graph structure (`vfx-particle-authoring`). Do not use this to
  decide how ECS/DOTS entities render through URP (`BatchRendererGroup`,
  DOTS Instancing shaders, material overrides) — that's
  `unity-entities-graphics`; this skill still owns the URP Asset/Renderer
  configuration (notably the Forward+ path, which Entities Graphics
  specifically requires) that entity rendering depends on.
---

# Unity URP Rendering — Universal Render Pipeline Configuration

Sources: see [references/](references/) for the URP Manual/Scripting API root links, split by topic — [root-links.md](references/root-links.md), [renderer-features-and-passes.md](references/renderer-features-and-passes.md), [rendering-paths.md](references/rendering-paths.md), [volumes-and-post-processing.md](references/volumes-and-post-processing.md), [2d-renderer.md](references/2d-renderer.md), [camera-stacking-and-asset-settings.md](references/camera-stacking-and-asset-settings.md).

## 1. Objective
Configure URP's own systems correctly and deliberately — Renderer Features/passes, rendering path choice, the URP Asset's quality/shadow/batching settings, Volume-driven post-processing, the 2D Renderer, and camera stacking — once URP is already the project's confirmed pipeline.

## 2. Role
Act as the URP configuration specialist: you build `ScriptableRendererFeature`/`ScriptableRenderPass` custom render passes, pick and justify a rendering path per platform tier, author Volume Profiles for post-processing, configure the 2D Renderer and Light2D setups, wire camera stacking, and map URP Asset quality settings to the project's actual target devices.

## 3. When to invoke this skill
- Building a custom render pass for a visual effect: outline pass, screen distortion, custom compositing, decals-in-URP — via `ScriptableRendererFeature` + `ScriptableRenderPass`.
- Choosing or changing the rendering path (Forward, Forward+, Deferred, Deferred+) for a quality tier, or diagnosing a per-object light-count budget problem tied to the active path.
- Authoring or troubleshooting Volume-driven post-processing (Volume Profiles, Volume Overrides, Global vs. local Volumes).
- Configuring the 2D Renderer: `Light2D` setup, 2D shadows, `Renderer2DData`, Sprite/Tilemap/Sprite Shape lighting integration.
- Setting up URP Camera Stacking (Base + Overlay cameras via `UniversalAdditionalCameraData`), or reading/writing `UniversalAdditionalCameraData` fields.
- Mapping URP Asset settings (shadow distance/cascades, render scale, SRP Batcher, Rendering Layers) to the project's actual platform quality tiers.
- Negative trigger: deciding *whether* the project should be on URP at all, or the shader Graph target/node-graph/HLSL content itself once the pipeline is settled — `render-pipeline-urp-hdrp` for the former, `shader-authoring` for the latter.
- Negative trigger: any HDRP-specific system (Frame Settings, HDRP Volumes-for-everything, Custom Pass Volume, Diffusion Profiles, Probe Volumes, ray/path tracing) — `unity-hdrp-rendering`.
- Negative trigger: plain `Camera`/`Transform` scripting with no URP-specific system involved — `unity-camera-fundamentals`; Cinemachine — `unity-cinemachine-authoring`; particle graph structure — `vfx-particle-authoring`.
- Negative trigger: deciding how ECS/DOTS entities render (`BatchRendererGroup`, DOTS Instancing, material overrides) — that's `unity-entities-graphics`, which depends on this skill's URP Asset/Renderer configuration (specifically, the Forward+ path) as its own prerequisite.

## 4. How to use this skill
1. **Confirm URP is actually active** (URP Asset assigned in Graphics settings) before doing any work here — if the project is on HDRP or Built-in RP, this skill doesn't apply; route to `unity-hdrp-rendering` or flag the mismatch.
2. **Custom render passes**: implement a `ScriptableRendererFeature` that creates and enqueues one or more `ScriptableRenderPass` instances via `AddRenderPasses`, register the feature on the URP Renderer asset actually used by the target quality tier (not just whichever renderer happens to be default), and pick the correct injection point (`RenderPassEvent`) for what the pass needs to read/write.
3. **Pick the rendering path deliberately, per platform tier.** Forward has a hard per-object light limit; Forward+ removes that limit via screen-space light tiling at a higher cost; Deferred/Deferred+ front-load a G-buffer pass and light everything at once, trading bandwidth for light-count scalability. Don't leave the path at whatever the template default was — choose per the project's actual light count and target hardware, and verify with the Profiler per `performance-and-algorithms.md`, not from Big-O/folklore alone.
4. **Post-processing goes through Volumes.** Add a Volume (Global or a local trigger-region Volume), assign a Volume Profile, add the needed Overrides (Bloom, Tonemapping, etc.) — don't hardcode post-process values per-camera when the project already uses the Volume system for everything else.
5. **2D Renderer work**: use `Light2D` for 2D-optimized lighting (Sprite/Tilemap/Sprite Shape targets), and confirm the active Renderer asset is actually the 2D Renderer (`Renderer2DData`) before assuming 2D lighting features are available — a project on the 3D Universal Renderer won't have them.
6. **Camera stacking**: prefer a Base + Overlay camera stack (`UniversalAdditionalCameraData.cameraStack`) over multiple independent full-screen cameras when compositing rendering layers (e.g. 3D scene + separately-rendered effects/UI layer) under URP — this is URP's dedicated mechanism for that, not a generic multi-camera workaround.
7. **Rendering Layers** (not to be confused with Unity's built-in physics/culling Layers) scope which Lights/Decals affect which GameObjects — use them instead of manually filtering light influence in a shader or script.
8. **SRP Batcher**: confirm it's enabled on the URP Asset (it usually should be, for a real perf win on projects with many materials sharing a shader variant), and confirm shaders are actually SRP-Batcher-compatible (per-material properties in the compatible `CBUFFER` layout) rather than assuming compatibility.
9. **Map quality tiers deliberately.** Render scale, shadow distance, shadow cascade count, and per-tier Renderer Feature toggles should be assigned per the project's actual platform tiers (mobile vs. PC) — not left at whatever the template default was, per the platform-abstraction rule in `performance-and-algorithms.md` (don't scatter `#if UNITY_ANDROID` through gameplay code; keep tier differences in URP Asset variants/quality levels instead).
10. **Verify on the actually-configured Renderer/pipeline before calling it done.** A Renderer Feature registered on the wrong Renderer asset, or a rendering-path assumption that doesn't match the target quality tier's actual asset, silently doesn't run — capture a scene view or profiler check on the real target tier.

## 5. Specific goals / tasks this skill performs
- Authoring `ScriptableRendererFeature`/`ScriptableRenderPass` custom render passes and registering them on the correct URP Renderer asset.
- Choosing and justifying Forward/Forward+/Deferred/Deferred+ per platform tier, backed by a measurement.
- Volume Profile/Override post-processing setup (Global and local trigger-region Volumes).
- 2D Renderer configuration: `Light2D`, 2D shadows, `Renderer2DData`.
- Camera stacking via `UniversalAdditionalCameraData` (Base + Overlay).
- Rendering Layers, SRP Batcher compatibility, and URP Asset quality-tier mapping (shadow distance/cascades, render scale).
- Out of scope: the URP-vs-HDRP targeting decision (`render-pipeline-urp-hdrp`), shader node-graph/HLSL content (`shader-authoring`), HDRP systems (`unity-hdrp-rendering`).

## 6. Output format
```
## URP Setup — <feature name>
- URP confirmed active: yes (URP Asset: <name>)
- Renderer asset targeted: <name> — used by quality tier: <tier(s)>
- Rendering path: Forward / Forward+ / Deferred / Deferred+ — rationale + measurement
- Approach: Renderer Feature/Pass / Volume Profile / 2D Renderer config / Camera Stack / Asset quality settings
- Files: <paths>
- Quality tier mapping: <summary, or "unchanged from project default" with rationale>
- SRP Batcher: enabled — yes/no; shaders confirmed compatible — yes/no/n-a
- Verified on: <quality tier / device class actually tested>
- Known limitations: <...>
```

## 7. Examples
**Example 1**
- Input: "Add a full-screen outline pass for selected units."
- Output: confirmed URP active with a Forward+ Universal Renderer on all quality tiers; built a `ScriptableRendererFeature` enqueuing a `ScriptableRenderPass` at `AfterRenderingTransparents`, registered on the actual Renderer asset used by both the PC and mobile quality levels; verified the pass renders on both tiers in Play Mode.

**Example 2**
- Input: "The mobile build is light-count-limited in a crowded arena scene — evaluate switching rendering paths."
- Output: profiled the existing Forward path under a worst-case light count on a mid-tier Android device, compared against a Forward+ test build using the Unity Profiler frame-time data (per `performance-and-algorithms.md`'s verification rule), recommended Forward+ for that tier with the measured frame-time delta included, left PC tier on its existing path since it wasn't light-count-bound.

## 8. Edge cases & guardrails
- Never register a Renderer Feature on a Renderer asset other than the one the target quality tier actually uses — it silently won't run for that tier.
- Never change the rendering path on folklore/Big-O reasoning alone — back it with a Profiler measurement per `performance-and-algorithms.md`.
- Never hardcode post-process values per-camera when the project uses the Volume system elsewhere — stay consistent with Volume Profiles/Overrides.
- Never assume 2D Renderer features (`Light2D`, 2D shadows) are available without confirming the active Renderer asset is actually the 2D Renderer.
- Never use multiple independent full-screen cameras to composite layers when URP Camera Stacking (`UniversalAdditionalCameraData.cameraStack`) already covers the case.
- Never assume SRP Batcher compatibility — verify the shader's actual `CBUFFER` layout, don't just assume the toggle alone is sufficient.
- Never leave quality-tier-sensitive settings (shadow distance/cascades, render scale) at template defaults — map them deliberately to the project's actual platform tiers.
