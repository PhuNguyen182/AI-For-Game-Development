---
name: unity-lighting
description: >
  Technique for Unity's lighting system — light sources (`UnityEngine.Light`:
  Directional/Point/Spot/Area, `LightType`, `LightShadows`, `LightRenderMode`,
  cookies, culling mask), direct vs. indirect lighting and Global
  Illumination (Baked GI/Progressive Lightmapper, Realtime GI/Enlighten,
  Mixed Lighting Modes — Baked Indirect/Shadowmask/Subtractive, the Lighting
  window, Light Probes, lightmap UVs), shadows (shadow cascades, shadow
  distance/bias/resolution, both the Built-in Render Pipeline's general
  shadow model and URP's shadow settings/screen space shadows), reflections
  (Reflection Probes — baked/realtime/custom, box projection, blending, both
  general and URP-specific), and URP's own lighting-adjacent systems: the
  URP lighting landing page, Adaptive Probe Volumes (APV —
  `UnityEngine.Rendering.ProbeVolume`/`ProbeAdjustmentVolume`), Rendering
  Layers used from the lighting side (`Light.renderingLayerMask`,
  `RenderingLayerMask`, preventing APV light leaks), and the URP lighting
  HLSL API a custom lit shader consults (`GetMainLight`,
  `GetAdditionalLight`/`GetAdditionalLightsCount`, `LightingLambert`/
  `LightingSpecular`, `DistanceAttenuation`/`AngleAttenuation`,
  `GlossyEnvironmentReflection`/`EvaluateAdaptiveProbeVolume`/`SampleSH`).
  Use this for any task touching a `Light` component, GI/lightmap baking
  configuration, shadow cascade/distance/resolution tuning, Reflection Probe
  placement, Adaptive Probe Volume setup, or lighting-side Rendering Layer
  masks — e.g. "set up baked lighting for this static level", "the mobile
  build's shadows are too expensive, tune cascades and distance", "place
  reflection probes for this reflective corridor", "bake Adaptive Probe
  Volumes for dynamic object lighting in this URP scene", "a custom shader
  needs to read the additional lights list in URP". Do not use this for the
  initial URP-vs-HDRP pipeline/shader-targeting decision — that's
  `render-pipeline-urp-hdrp`. Do not use this for HDRP lighting (HDRP Frame
  Settings, HDRP's own Volume-driven Exposure/Fog/Sky overrides, Diffusion
  Profiles, HDRP's Adaptive Probe Volume/light probe workflow, ray/path
  tracing) — that's `unity-hdrp-rendering`; this skill's Manual references
  are Built-in Render Pipeline and URP only. Do not use this for URP Renderer
  Features/passes, rendering path choice (Forward/Forward+/Deferred),
  post-processing Volume Profiles/Overrides (Bloom, Tonemapping — an
  unrelated "Volume" concept from Adaptive Probe Volumes), the 2D Renderer
  (`Light2D`), or camera stacking — that's `unity-urp-rendering`, which also
  documents Rendering Layers from its own renderer-feature/Decal-targeting
  angle; the two skills' Rendering Layers coverage overlaps by design, this
  skill covers it specifically from the light-to-object-masking side. Do not
  use this to write the actual shader code for a custom lighting model
  (Shader Graph nodes, HLSL/ShaderLab authoring) — that's
  `shader-authoring`; this skill only covers the URP lighting API/concepts a
  custom shader consults, not the shader file itself. Do not use this for
  Cinemachine camera lighting-adjacent behavior, particle/VFX light-driven
  effects, or any gameplay decision that merely reads a light's state
  (stealth detection, day/night gameplay triggers) — the decision itself
  belongs in `Game.Core.*` per `coding-principles.md`'s Shared Core
  integrity rule; this skill only configures the light/GI/shadow/reflection
  system itself.
---

# Unity Lighting — Light Sources, Global Illumination, Shadows, Reflections, URP Lighting Systems

Sources: see [references/](references/) for the Manual/Scripting API root links, split by topic — [root-links.md](references/root-links.md), [light-sources-and-parameters.md](references/light-sources-and-parameters.md), [direct-indirect-and-gi.md](references/direct-indirect-and-gi.md), [shadows.md](references/shadows.md), [reflections.md](references/reflections.md), [urp-lighting-landing.md](references/urp-lighting-landing.md), [probe-volumes.md](references/probe-volumes.md), [rendering-layers.md](references/rendering-layers.md), [custom-lighting.md](references/custom-lighting.md), [scripting-api.md](references/scripting-api.md).

## 1. Objective
Configure Unity's lighting system correctly and deliberately — light sources and their parameters, the GI mode per light (Realtime/Baked/Mixed), shadow cascades/distance/resolution, Reflection Probe placement, and (in URP) Adaptive Probe Volumes and lighting-side Rendering Layer masks — matched to the project's actual render pipeline (Built-in RP or URP) and target platform tier, without drifting into pipeline choice, Renderer Features, post-processing Volumes, HDRP systems, actual shader authoring, or gameplay decisions that merely consume a light's state.

## 2. Role
Act as the lighting specialist: given a scene or feature that needs light sources, baked/realtime GI, shadows, or reflections, you choose and configure the right `UnityEngine.Light`/GI/shadow/Reflection Probe/Adaptive Probe Volume setup for the confirmed render pipeline — you don't decide which pipeline the project targets, you don't build Renderer Features or post-processing Volumes, and you don't write the custom shader code that consumes lighting data, all of which are sibling skills' territory.

## 3. When to invoke this skill
- Setting up or tuning **light sources**: choosing Directional/Point/Spot/Area, configuring range/intensity/color/color temperature/cookie/culling mask/spot angle, or diagnosing per-pixel vs. per-vertex rendering (`LightRenderMode`).
- Choosing and configuring **Global Illumination**: Baked GI (Progressive Lightmapper) vs. Realtime GI (Enlighten) vs. Mixed Lighting (Baked Indirect/Shadowmask/Subtractive), setting a light's `Mode` (`Realtime`/`Mixed`/`Baked`), configuring the Lighting window/Lighting Settings Asset, Light Probes placement, or lightmap UV generation.
- Configuring or troubleshooting **shadows**: shadow cascade count/splits, shadow distance, shadow resolution/bias, hard vs. soft shadows, shadow acne/peter-panning artifacts, or URP-specific shadow resolution tiers and screen space shadows.
- Placing or tuning **Reflection Probes**: baked vs. realtime vs. custom mode, box projection, blending, resolution/refresh mode/time-slicing, or URP's reflection probe resolution/blending behavior.
- Configuring **URP's own lighting-adjacent systems**: the URP lighting landing page's light-limit/Forward+ light handling, **Adaptive Probe Volumes** (placement, density, baking sets, streaming, runtime lighting changes), or **Rendering Layers used to mask which Lights affect which Renderers** (including preventing APV light leaks).
- Consulting URP's **lighting HLSL API** (`GetMainLight`, `GetAdditionalLight`/`GetAdditionalLightsCount`, indirect lighting sampling, light falloff functions) to inform — but not author — a custom lit shader.
- Negative trigger: deciding *whether* the project targets URP or HDRP — `render-pipeline-urp-hdrp`.
- Negative trigger: any HDRP-specific lighting system (Frame Settings, HDRP's Volume-driven Exposure/Fog/Sky, Diffusion Profiles, HDRP's own APV/light probe workflow, ray/path tracing) — `unity-hdrp-rendering`.
- Negative trigger: URP Renderer Features/passes, rendering path choice (Forward/Forward+/Deferred/Deferred+), post-processing Volume Profiles/Overrides, the 2D Renderer (`Light2D`), or camera stacking — `unity-urp-rendering`.
- Negative trigger: writing the actual Shader Graph nodes or HLSL/ShaderLab code for a custom lighting model — `shader-authoring`; this skill only supplies the lighting API/concepts that shader consults.
- Negative trigger: any gameplay decision that merely reads a light's/shadow's state (stealth detection thresholds, day/night gameplay triggers, a light-based puzzle's win condition) — that decision lives in `Game.Core.*` per `coding-principles.md`'s Shared Core integrity rule; this skill only configures the lighting system itself.

## 4. How to use this skill
1. **Confirm the active render pipeline first** (Built-in RP, URP, or HDRP — check Graphics settings/the assigned pipeline asset) before citing any Manual page. Built-in RP and URP diverge in page location and in some behavior (e.g. shadow resolution tiers, Adaptive Probe Volumes are URP/HDRP-only). If the project is on HDRP, route to `unity-hdrp-rendering` instead.
2. **Choose light types and parameters deliberately**, per [light-sources-and-parameters.md](references/light-sources-and-parameters.md): Directional for a scene's dominant sun/moon, Point/Spot/Area for local sources, and set `LightType`/intensity/color/cookie/culling mask/`LightRenderMode` to match the actual visual and performance requirement — don't leave lights at Editor defaults.
3. **Decide the GI mode per light deliberately**, per [direct-indirect-and-gi.md](references/direct-indirect-and-gi.md): `Baked` for fully static geometry (cheapest at runtime, via the Progressive Lightmapper), `Realtime` for lights that must react to runtime changes, `Mixed` (Shadowmask/Baked Indirect/Subtractive) as the deliberate middle ground for lights on static geometry that also need dynamic shadow casters. Use Light Probes so dynamic (non-lightmapped) objects still receive baked indirect lighting.
4. **Configure shadows to the actual quality tier**, per [shadows.md](references/shadows.md): pick cascade count/splits and shadow distance based on scene scale and the target platform (mobile vs. PC), tune bias to avoid acne/peter-panning rather than over-correcting blindly, and — on URP — set per-tier shadow resolution and consider screen space shadows only where the extra pass is justified.
5. **Place and configure Reflection Probes deliberately**, per [reflections.md](references/reflections.md): Baked for static reflective surfaces (cheapest), Realtime only where the reflected content genuinely changes at runtime (with a deliberate `refreshMode`/time-slicing choice, since realtime probes are expensive), box projection when a probe's reflection must respect room/corridor bounds rather than assuming an infinitely distant environment.
6. **In URP, treat the URP lighting landing page as the map** ([urp-lighting-landing.md](references/urp-lighting-landing.md)) to the Forward+ per-object light limit, `UniversalAdditionalLightData` (URP's per-light extension component), and where Adaptive Probe Volumes/Rendering Layers fit in.
7. **Configure Adaptive Probe Volumes for dynamic-object indirect lighting in URP** ([probe-volumes.md](references/probe-volumes.md)) instead of the legacy baked Light Probe Group workflow when the project's URP version supports APV — size/density Probe Volumes to the scene's actual geometry, use Baking Sets for multi-scene bakes, and use rendering layer masks to prevent light leaks between rooms/volumes that shouldn't influence each other.
8. **Use Rendering Layers from the lighting side deliberately** ([rendering-layers.md](references/rendering-layers.md)): set `Light.renderingLayerMask`/`Renderer.renderingLayerMask` to scope which Lights affect which Renderers when a scene genuinely needs per-light exclusion (e.g. an indoor light that shouldn't leak onto an adjacent APV cell) — don't reach for this as a routine default when a simpler culling mask or scene layout change would do.
9. **When a custom lit shader needs lighting data, supply the API, hand off the authoring**: point to the confirmed HLSL entry points in [custom-lighting.md](references/custom-lighting.md) (`GetMainLight`, `GetAdditionalLight`/`GetAdditionalLightsCount`, `LightingLambert`/`LightingSpecular`, `DistanceAttenuation`/`AngleAttenuation`, `GlossyEnvironmentReflection`/`EvaluateAdaptiveProbeVolume`/`SampleSH`), then route the actual Shader Graph/HLSL authoring to `shader-authoring`.
10. **Validate any performance claim with a measurement** (Unity Profiler frame time, memory, or bake time), not asserted from the optimization guide alone, per `performance-and-algorithms.md`'s Verification section — this applies to shadow cascade/distance changes, reflection probe count/resolution, and Adaptive Probe Volume density.
11. **Respect the Shared Core boundary.** A light/shadow/reflection setup is purely a Client-layer visual/rendering concern; any gameplay rule that happens to consume a light's state (stealth detection, a light-triggered puzzle) is decided in `Game.Core.*` per `coding-principles.md`'s Shared Core integrity rule — this skill only configures the lighting system, it never decides the gameplay outcome.

## 5. Specific goals / tasks this skill performs
- Configuring light sources and parameters (`LightType`, intensity/color/color temperature, cookies, culling mask, `LightRenderMode`).
- Choosing and configuring GI mode per light (Baked/Realtime/Mixed), Progressive Lightmapper settings, Light Probes, lightmap UVs.
- Tuning shadow cascades, distance, resolution, and bias — for both the Built-in Render Pipeline and URP (including URP screen space shadows).
- Placing and configuring Reflection Probes (baked/realtime/custom, box projection, blending, resolution/refresh mode).
- Configuring URP's Adaptive Probe Volumes (placement, density, Baking Sets, streaming, runtime lighting changes).
- Using Rendering Layers from the lighting-masking side (`Light.renderingLayerMask`, preventing APV light leaks).
- Supplying the URP lighting HLSL API surface a custom shader needs to consume (without authoring the shader itself).
- Out of scope: URP/HDRP pipeline choice (`render-pipeline-urp-hdrp`); HDRP-specific lighting systems (`unity-hdrp-rendering`); URP Renderer Features/rendering path/post-processing Volumes/2D Renderer/camera stacking (`unity-urp-rendering`); actual shader code authoring (`shader-authoring`); gameplay decisions consuming light state (`csharp-engineer`'s Shared Core).

## 6. Output format
```
## Lighting Work — <scene/feature name>
- Render pipeline confirmed: Built-in RP / URP (version) — HDRP routed to unity-hdrp-rendering if applicable
- Light sources: type(s) used, key parameter choices, rationale
- GI mode per light: Baked / Realtime / Mixed <Shadowmask/Baked Indirect/Subtractive> — rationale
- Light Probes / Adaptive Probe Volumes: placement/density summary, or "not used" + why
- Shadows: cascade count/splits, distance, resolution tier, bias — rationale + platform tier targeted
- Reflection Probes: mode(s), placement, box projection, blend distance — rationale
- Rendering Layers (if used): masks defined, lighting-side purpose
- Custom lighting API consulted (if applicable): functions referenced, hand-off to shader-authoring confirmed
- Verified on: <device/quality tier actually tested, bake time if relevant>
- Shared Core boundary: confirmed no gameplay decision made in lighting-layer config/code
- Known limitations: <...>
```

## 7. Examples
**Example 1**
- Input: "Set up lighting for an outdoor daytime URP level: static architecture, a moving player character, and a few reflective glass corridors."
- Output: confirmed URP active; one Directional Light as the sun set to `Mixed` (Shadowmask) so static geometry gets baked indirect lighting while the moving player still casts a real-time shadow; baked GI via the Progressive GPU Lightmapper for static architecture; Adaptive Probe Volumes placed and densified around the player's traversable area so the moving character receives correct indirect lighting without a legacy Light Probe Group; four shadow cascades with distance tuned to the level's actual draw distance; Baked Reflection Probes with box projection placed in each glass corridor sized to the corridor bounds; verified bake time and runtime frame cost on the target mid-tier device via Profiler.
- Hand-off: none needed for this task — entirely within scope.

**Example 2**
- Input: "A custom toon-shaded material needs to correctly react to the main light and up to 4 additional lights under URP's Forward+ path."
- Output: confirmed the project is on URP with Forward+ active (cross-checked with `unity-urp-rendering`'s rendering-path configuration, which owns that choice); supplied the shader author with the confirmed HLSL entry points from [custom-lighting.md](references/custom-lighting.md) — `GetMainLight()` for the sun, `GetAdditionalLightsCount()`/`GetAdditionalLight()` inside a `LIGHT_LOOP_BEGIN`/`LIGHT_LOOP_END` loop for the additional lights, and `DistanceAttenuation()`/`AngleAttenuation()` for falloff; confirmed the material's affecting lights are scoped correctly via `Light.renderingLayerMask`.
- Hand-off: the actual Shader Graph/HLSL implementation of the toon ramp itself is `shader-authoring`'s task — this skill's contribution stopped at supplying the correct lighting API surface and confirming the light-count/rendering-layer setup it depends on.

## 8. Edge cases & guardrails
- Never cite a Built-in Render Pipeline Manual page (e.g. `Manual/Shadows.html`, `Manual/ReflectionProbes.html`) as authoritative for a URP project, or vice versa — confirm the active pipeline first; the two diverge in page location and in real behavior (shadow resolution tiers, Adaptive Probe Volumes availability).
- Adaptive Probe Volumes and post-processing Volumes (Bloom/Tonemapping, owned by `unity-urp-rendering`) share the word "Volume" but are unrelated systems — never conflate `UnityEngine.Rendering.ProbeVolume` with a `VolumeProfile`/`VolumeComponent`.
- `LightShape` is obsolete — use `LightType.Spot`/`Pyramid`/`Box` instead; don't recommend it for new work.
- `LightProbeProxyVolume` is deprecated alongside the Built-in Render Pipeline's deprecation — don't recommend it for new URP/HDRP work; use Adaptive Probe Volumes instead.
- The Manual slug `GlobalIllumination.html` now redirects to `lighting-window.html` — if a stale bookmark/reference uses the old slug, treat the redirect target as current.
- Never leave shadow cascades/distance, Reflection Probe count/resolution, or Adaptive Probe Volume density at Editor defaults for a shipping platform tier — map them deliberately to the project's actual target devices, per `performance-and-algorithms.md`.
- Never assert a lighting-related performance improvement (a cascade change, a probe density reduction, a bake-time optimization) without a Profiler/bake-time measurement backing it, per `performance-and-algorithms.md`'s Verification section.
- Realtime Reflection Probes and Realtime GI (Enlighten) are both meaningfully more expensive than their baked counterparts — never default to `Realtime` mode without a concrete runtime-change requirement justifying the cost.
- Rendering Layers has overlapping coverage with `unity-urp-rendering` (which documents it from the Renderer Feature/Decal-targeting angle) — this skill's angle is strictly the lighting/light-masking side; don't use this skill's guidance to author a Decal-targeting or general renderer-feature Rendering Layer setup unrelated to lighting.
- Never write the actual shader code for a custom lighting model here — this skill supplies the URP lighting HLSL API surface (`GetMainLight`, `GetAdditionalLight`, falloff/indirect functions) for `shader-authoring` to consume; authoring the shader itself is out of scope.
- Never let lighting-layer code/config make a gameplay decision (a stealth-detection threshold based on light level, a day/night gameplay trigger) — that decision belongs in `Game.Core.*` per `coding-principles.md`'s Shared Core integrity rule; this skill only configures the light/shadow/reflection/probe system that the decision might read from.
