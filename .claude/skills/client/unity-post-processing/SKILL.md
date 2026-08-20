---
name: unity-post-processing
description: >
  Technique for Unity's post-processing/full-screen effects systems — the URP
  Volume system (`UnityEngine.Rendering.Volume`/`VolumeProfile`/
  `VolumeComponent`/`VolumeManager`, Global vs. local Volumes, priority/
  weight/blend distance), URP's built-in Volume Override effect list (Bloom,
  Color Adjustments/Curves/Lookup, Depth of Field, Film Grain, Lens
  Distortion, Lift/Gamma/Gain, Motion Blur, Panini Projection, Screen Space
  Lens Flare, Shadows Midtones Highlights, Split Toning, Tonemapping,
  Vignette, White Balance), authoring a custom post-processing effect in URP
  (the low-code `FullScreenPassRendererFeature` + Fullscreen Shader Graph
  workflow, and the scripted `ScriptableRendererFeature`/`ScriptableRenderPass`
  + `VolumeComponent` workflow), the legacy Post Processing Stack v2 package
  (`com.unity.postprocessing`: `PostProcessLayer`, `PostProcessVolume`,
  `PostProcessProfile`, `PostProcessEffectSettings`) used with the Built-in
  Render Pipeline, and cross-pipeline effect-availability differences (an
  effect present in URP/HDRP but not Built-in RP/PPv2, or vice versa). Use
  this for any task touching a post-processing/full-screen visual effect —
  e.g. "add Bloom and color grading to this URP scene", "set up a Global
  Volume with a blend region for an underwater area", "author a custom
  full-screen distortion effect with Volume-driven intensity", "this
  Built-in-RP project needs a vignette, wire up PPv2", "check whether Panini
  Projection is available outside URP". Do not use this for the initial
  URP-vs-HDRP pipeline decision — that's `render-pipeline-urp-hdrp`. Do not
  use this for HDRP's own post-processing/Volume framework (HDRP has a
  parallel but separate Volume-driven Exposure/Fog/Sky/Custom Pass Volume
  system) — that's `unity-hdrp-rendering`. Do not use this for URP Renderer
  Features/passes in general, rendering path choice (Forward/Forward+/
  Deferred), the 2D Renderer, camera stacking, Rendering Layers, or SRP
  Batcher/quality-tier mapping — that's `unity-urp-rendering`, which also
  gives a one-line mention of Volume-driven post-processing as part of its
  own general URP configuration scope; this skill is the deep-dive
  specialist for the post-processing/Volume content itself, the two skills'
  coverage overlaps by design at that shallow mention. Do not use this for
  Adaptive Probe Volumes (`UnityEngine.Rendering.ProbeVolume`) — an unrelated
  system that happens to share the word "Volume" — that's `unity-lighting`.
  Do not use this to write the actual Shader Graph node content or HLSL of a
  custom post-processing effect's shader — that's `shader-authoring`; this
  skill only covers the Renderer Feature/VolumeComponent authoring workflow
  and API surface around it, not the shader file itself. Do not use this for
  any gameplay decision that merely reads or triggers a post-processing
  state (a "blinded" status effect toggling a vignette, a low-health
  color-grading cue) — that decision belongs in `Game.Core.*` per
  `coding-principles.md`'s Shared Core integrity rule; this skill only
  configures the post-processing system itself.
---

# Unity Post-Processing — Volumes, Effect List, Custom Effects, Legacy PPv2

Sources: see [references/](references/) for the Manual/Scripting API root links, split by topic — [root-links.md](references/root-links.md), [effect-availability-and-effect-list.md](references/effect-availability-and-effect-list.md), [volumes.md](references/volumes.md), [custom-post-processing.md](references/custom-post-processing.md), [postprocessing-v2-legacy.md](references/postprocessing-v2-legacy.md), [scripting-api.md](references/scripting-api.md).

## 1. Objective
Configure Unity's post-processing/full-screen effect systems correctly and deliberately — the URP Volume system and its built-in effect list, custom post-processing effect authoring, and the legacy Post Processing Stack v2 package for Built-in RP projects — matched to the project's actual render pipeline, without drifting into general URP renderer configuration, HDRP's own post-processing framework, Adaptive Probe Volumes, actual shader authoring, or gameplay decisions that merely consume a post-processing effect's state.

## 2. Role
Act as the post-processing specialist: given a scene or feature that needs a visual full-screen effect, you choose and configure the right Volume/Volume Override setup (URP) or `PostProcessVolume`/effect settings setup (Built-in RP), or author a custom effect via the correct URP workflow — you don't decide which pipeline the project targets, you don't build general-purpose Renderer Features unrelated to post-processing, and you don't write the shader code a custom effect ultimately runs, all of which are sibling skills' territory.

## 3. When to invoke this skill
- Adding or tuning a **built-in Volume Override effect** in URP (Bloom, Color Adjustments/Curves/Lookup, Depth of Field, Film Grain, Lens Distortion, Lift/Gamma/Gain, Motion Blur, Panini Projection, Screen Space Lens Flare, Shadows Midtones Highlights, Split Toning, Tonemapping, Vignette, White Balance).
- Setting up or troubleshooting the **URP Volume system** itself: Global vs. local Volume, Volume Profile creation/sharing, Volume Override configuration, priority/weight/blend distance blending behavior.
- Authoring a **custom post-processing effect** in URP: the low-code `FullScreenPassRendererFeature` + Fullscreen Shader Graph workflow, or the scripted `ScriptableRendererFeature`/`ScriptableRenderPass` + `VolumeComponent` workflow for a Volume-driven custom effect.
- Wiring up **legacy Post Processing Stack v2** (`PostProcessLayer`/`PostProcessVolume`/`PostProcessProfile`) for a project still on the Built-in Render Pipeline.
- Checking **cross-pipeline effect availability** — confirming whether a specific effect (Auto Exposure, Fog, Screen Space Reflection, Panini Projection, Shadows Midtones Highlights, Split Toning) actually exists on the project's target pipeline before assuming parity across Built-in RP/URP/HDRP.
- Negative trigger: deciding *whether* the project targets URP or HDRP — `render-pipeline-urp-hdrp`.
- Negative trigger: HDRP's own Volume-driven post-processing framework (Exposure, Fog, Sky, Custom Pass Volume, Diffusion Profiles) — `unity-hdrp-rendering`.
- Negative trigger: URP Renderer Features/passes unrelated to post-processing, rendering path choice, the 2D Renderer, camera stacking, Rendering Layers, or SRP Batcher/quality-tier mapping — `unity-urp-rendering`.
- Negative trigger: Adaptive Probe Volumes (`ProbeVolume`/`ProbeAdjustmentVolume`) — a different system that happens to share the word "Volume" — `unity-lighting`.
- Negative trigger: writing the actual Shader Graph nodes or HLSL/blit shader code a custom post-processing effect renders with — `shader-authoring`; this skill only supplies the Renderer Feature/VolumeComponent authoring workflow and API.
- Negative trigger: any gameplay decision that merely reads or triggers a post-processing effect's state (a status-effect vignette, a low-health color grade) — that decision lives in `Game.Core.*` per `coding-principles.md`'s Shared Core integrity rule; this skill only configures the post-processing system itself.

## 4. How to use this skill
1. **Confirm the active render pipeline first** (Built-in RP, URP, or HDRP — check Graphics settings/the assigned pipeline asset) before citing any Manual page or API. The three pipelines' post-processing systems are structurally parallel but not interchangeable: URP uses the Volume system, Built-in RP uses the legacy PPv2 package, HDRP has its own Volume-driven framework. If the project is on HDRP, route to `unity-hdrp-rendering` instead.
2. **On URP, set up the Volume system first**, per [volumes.md](references/volumes.md): add a Global Volume for scene-wide effects or a local Volume (with a collider and `blendDistance`) for a region-triggered effect, assign a `VolumeProfile`, and set `priority`/`weight` deliberately when multiple Volumes can overlap — don't leave blending behavior to accident.
3. **Add and tune built-in Volume Override effects deliberately**, per [effect-availability-and-effect-list.md](references/effect-availability-and-effect-list.md): pick only the effects the scene's actual look calls for, tune their key properties instead of leaving Editor defaults, and confirm cross-pipeline availability before assuming an effect exists everywhere (e.g. Auto Exposure/Fog/Screen Space Reflection are HDRP+PPv2 only, not in URP; Panini Projection/Shadows Midtones Highlights/Split Toning are URP+HDRP only, not in Built-in RP/PPv2).
4. **On Built-in RP, use legacy PPv2 instead of assuming URP's Volume system applies**, per [postprocessing-v2-legacy.md](references/postprocessing-v2-legacy.md): add a `PostProcessLayer` to the camera, create a `PostProcessVolume` with a `PostProcessProfile`, and add effect settings (`Bloom`, `ColorGrading`, `Vignette`, etc.) — note PPv2 groups several URP-separate effects (Channel Mixer, Color Adjustments, Color Curves, Lift/Gamma/Gain, Tonemapping) under the single `ColorGrading` class rather than exposing them individually.
5. **Author a custom post-processing effect only when the built-in effect list genuinely doesn't cover the need**, per [custom-post-processing.md](references/custom-post-processing.md): choose the low-code `FullScreenPassRendererFeature` + Fullscreen Shader Graph path when no C# is needed, or the scripted `ScriptableRendererFeature`/`ScriptableRenderPass` + `VolumeComponent` path when the effect needs Volume-driven, blendable parameters — then hand off the actual Shader Graph/HLSL content to `shader-authoring`.
6. **Pick the injection point deliberately** for any custom pass — before/after transparents, after post-processing, etc. — per the injection-points reference in [custom-post-processing.md](references/custom-post-processing.md); an effect injected at the wrong point silently reads/writes the wrong buffer state.
7. **Mind mobile/tile-based GPU cost.** Full-screen post-processing effects resolve off-tile on tile-based mobile GPUs, which is meaningfully more expensive than on-tile rendering — check [root-links.md](references/root-links.md)'s on-tile post-processing note before defaulting to a heavy effect stack on a mobile quality tier.
8. **Validate any performance claim with a measurement** (Unity Profiler GPU frame time), not asserted from the optimization guide alone, per `performance-and-algorithms.md`'s Verification section — this applies to effect count/quality settings and custom pass cost alike.
9. **Never conflate the two pipelines' parallel-but-incompatible systems.** `Volume`/`VolumeProfile`/`VolumeComponent` (URP) and `PostProcessVolume`/`PostProcessProfile`/`PostProcessEffectSettings` (Built-in RP/PPv2) are structurally analogous but not the same API — confirm which pipeline before citing either.
10. **Respect the Shared Core boundary.** A post-processing effect setup is purely a Client-layer visual concern; any gameplay rule that happens to trigger or read a post-processing effect's state (a status-effect vignette, a damage color flash) is decided in `Game.Core.*` per `coding-principles.md`'s Shared Core integrity rule — this skill only configures the effect, it never decides the gameplay outcome.

## 5. Specific goals / tasks this skill performs
- Setting up and troubleshooting the URP Volume system (Global/local Volumes, Volume Profiles, priority/weight/blend distance).
- Adding and tuning built-in URP Volume Override effects (the full 18-effect list).
- Authoring custom post-processing effects in URP via the low-code Renderer Feature workflow or the scripted Renderer-Feature-plus-`VolumeComponent` workflow.
- Wiring up legacy Post Processing Stack v2 (`PostProcessLayer`/`PostProcessVolume`/`PostProcessProfile`/effect settings) for Built-in RP projects.
- Checking and explaining cross-pipeline effect-availability differences.
- Out of scope: URP/HDRP pipeline choice (`render-pipeline-urp-hdrp`); HDRP's own post-processing/Volume framework (`unity-hdrp-rendering`); general URP Renderer Features/rendering path/2D Renderer/camera stacking/Rendering Layers (`unity-urp-rendering`); Adaptive Probe Volumes (`unity-lighting`); actual shader code authoring (`shader-authoring`); gameplay decisions consuming post-processing state (`csharp-engineer`'s Shared Core).

## 6. Output format
```
## Post-Processing Work — <scene/feature name>
- Render pipeline confirmed: Built-in RP (legacy PPv2) / URP (version) — HDRP routed to unity-hdrp-rendering if applicable
- Volume setup (URP) / PostProcessVolume setup (Built-in RP): Global/local, profile, priority/weight/blend distance
- Effects used: <effect list> — key property choices, rationale
- Cross-pipeline availability checked: yes/no — any effect confirmed unavailable on the target pipeline
- Custom effect (if applicable): low-code Renderer Feature / scripted Renderer-Feature-plus-VolumeComponent — injection point, hand-off to shader-authoring confirmed
- Mobile/tile-based GPU cost considered: yes/no + rationale
- Verified on: <device/quality tier actually tested, Profiler data if a perf claim is made>
- Shared Core boundary: confirmed no gameplay decision made in post-processing config/code
- Known limitations: <...>
```

## 7. Examples
**Example 1**
- Input: "Set up outdoor daytime post-processing for this URP scene: bloom on bright surfaces, filmic color grading, and a subtle vignette."
- Output: confirmed URP active; added one Global Volume with a new Volume Profile; added Bloom (Threshold/Intensity/Scatter tuned to the scene's actual bright-surface count), Tonemapping (ACES mode) plus Color Adjustments (Post Exposure/Contrast/Saturation) for the filmic grade, and Vignette (low Intensity, Smoothness tuned) — left Depth of Field and Motion Blur out since the brief didn't call for them; verified GPU frame time on the target mid-tier device via Profiler before calling the effect count final.
- Hand-off: none needed — entirely within scope.

**Example 2**
- Input: "Author a custom 'screen static' effect that intensifies as a status effect progresses, blendable like a built-in Volume Override."
- Output: confirmed URP active; used the scripted `Assets > Create > Scripting > URP Post-process Volume Scripts` template to scaffold a custom `ScriptableRendererFeature`/`ScriptableRenderPass` pair and a `VolumeComponent` exposing a `ClampedFloatParameter` for static intensity; wired the pass's `AddRenderPasses()` to read the active `VolumeComponent`'s overridden value from the `VolumeStack` and push it to the effect Material via `SetFloat`; injection point set to "After Rendering Post Processing".
- Hand-off: the Fullscreen Shader Graph/HLSL implementing the actual static noise pattern is `shader-authoring`'s task — this skill's contribution stopped at the Renderer Feature/VolumeComponent scaffold and confirming how the Volume-driven intensity value reaches the shader. The status-effect progression logic that sets the intensity value at runtime is a `Game.Core.*` gameplay rule per the Shared Core boundary — this skill only wired the visual effect to consume it.

## 8. Edge cases & guardrails
- Never assume an effect exists on every pipeline — check [effect-availability-and-effect-list.md](references/effect-availability-and-effect-list.md) first; Auto Exposure/Fog/Screen Space Reflection are HDRP+PPv2 only (not URP), Panini Projection/Shadows Midtones Highlights/Split Toning are URP+HDRP only (not Built-in RP/PPv2).
- Never cite PPv2's `ColorGrading` class properties as if they map 1:1 to URP's separate Channel Mixer/Color Adjustments/Color Curves/Lift-Gamma-Gain/Tonemapping overrides — PPv2 groups them into one class; there is no standalone PPv2 `Tonemapper` class, tonemapping is a field on `ColorGrading`.
- `Volume`/`VolumeProfile`/`VolumeComponent` (URP) and `PostProcessVolume`/`PostProcessProfile`/`PostProcessEffectSettings` (Built-in RP/PPv2) are structurally parallel but not compatible or interchangeable — never mix API from the two in the same recommendation without first confirming the active pipeline.
- Adaptive Probe Volumes (`unity-lighting`) and the post-processing Volume system share the word "Volume" but are unrelated — never conflate `UnityEngine.Rendering.ProbeVolume` with `UnityEngine.Rendering.Volume`.
- Never leave a scene with zero Global Volume when any Volume Override is expected to apply — a Volume Override on a local-only Volume with no overlapping Global fallback silently has no effect outside its blend region.
- Prefer the low-code `FullScreenPassRendererFeature` + Shader Graph workflow when no runtime-tunable parameter is needed; reach for the scripted Renderer-Feature-plus-`VolumeComponent` workflow only when the effect genuinely needs Volume-driven blending/parameters — don't default to the more complex scripted path out of habit.
- Never use `RenderPipelineManager.beginCameraRendering` callbacks to inject a reusable custom post-processing pass — the Manual explicitly recommends the Renderer Feature pattern instead; the callback approach is a narrower, one-off technique.
- Full-screen post-processing effects are meaningfully more expensive on tile-based mobile GPUs (off-tile resolve) — never assume a PC-tuned effect stack is free to reuse unchanged on a mobile quality tier; check the on-tile post-processing guidance and verify with Profiler.
- Never assert a post-processing performance improvement (an effect removed, a quality setting lowered) without a Profiler measurement backing it, per `performance-and-algorithms.md`'s Verification section.
- This skill's coverage of "Volume-driven post-processing" overlaps by design with `unity-urp-rendering`'s own shallow one-line mention of the same topic — this skill is the deep-dive specialist; route general Renderer Feature/rendering-path/2D-Renderer/camera-stacking/Rendering-Layer work to `unity-urp-rendering` instead.
- Never write the actual shader code for a custom post-processing effect here — this skill supplies the Renderer Feature/VolumeComponent authoring workflow and API for `shader-authoring` to consume; authoring the Shader Graph/HLSL itself is out of scope.
- Never let post-processing-layer code/config make a gameplay decision (a status-effect threshold driving a vignette, a low-health color-grade trigger) — that decision belongs in `Game.Core.*` per `coding-principles.md`'s Shared Core integrity rule; this skill only configures the post-processing system that the decision might drive.
