---
name: unity-lighting
description: >
  Technique for Unity lighting on the Built-in pipeline and URP: `Light`
  sources and their parameters, baked, realtime and mixed Global Illumination
  through the Progressive Lightmapper, Lighting Modes, lightmap UVs, Light
  Probes, shadow cascades, distance, bias and resolution, Reflection Probes
  and box projection, Adaptive Probe Volume authoring, lighting-side Rendering
  Layers, and the URP lighting HLSL a custom lit shader consults. Use when a
  scene must be lit, baked, or its shadows and reflections tuned. Not for:
  pipeline choice (`render-pipeline-urp-hdrp`); HDRP pipeline settings
  (`unity-hdrp-rendering`); rendering path, Renderer Features and `Light2D`
  (`unity-urp-rendering`); post-process Volumes (`unity-post-processing`);
  shader content (`shader-authoring`).
---

# Unity Lighting — Sources, Global Illumination, Shadows, Reflections, Probe Volumes

## Bundled resources

### References
Read-only context, loaded on demand so SKILL.md itself stays short.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Manual and API roots, the version pin, and where each pipeline keeps its lighting settings | Starting any task here, or a setting appears to have no effect |
| [light-sources.md](references/light-sources.md) | Light types and what each can actually do, intensity units, range, culling, URP light limits | Placing or tuning lights, or lights vanish from some objects |
| [global-illumination.md](references/global-illumination.md) | Light Modes, the three Lighting Modes, lightmapping, lightmap UVs, Light Probes | Anything is being baked, or a bake produced the wrong result |
| [shadows.md](references/shadows.md) | Cascades, distance, bias, resolution tiers, and which asset owns each | Tuning shadow cost or quality, or diagnosing acne and peter-panning |
| [reflections.md](references/reflections.md) | Reflection Probe modes, box projection, blending, refresh cost | A surface must reflect its surroundings rather than only the skybox |
| [probe-volumes.md](references/probe-volumes.md) | Adaptive Probe Volume placement, density, Baking Sets, streaming, leak fixes | Dynamic objects need baked indirect light, or light leaks through walls |
| [rendering-layers.md](references/rendering-layers.md) | Rendering Layers from the light-masking side, and what gates them | One light must affect only some renderers, including across an APV boundary |
| [custom-lighting-api.md](references/custom-lighting-api.md) | URP's lighting HLSL entry points and include files | A custom lit shader needs to read Unity's lights correctly |

## 1. Objective
Light a scene so the result survives a bake, a build, and the target device — the light type chosen for what it can actually do, the Light Mode set before anything is baked around it, geometry flagged and UV'd so the lightmapper has something to write into, shadow cost spent on distance before resolution, and probe data placed so dynamic objects are lit at all. Lighting fails quietly and expensively: a wrong flag costs a re-bake, not a recompile.

## 2. Role
Act as the lighting specialist for Built-in RP and URP, and as the probe and lightmap authoring owner on any SRP — the pipeline skills enable Adaptive Probe Volumes at the Asset level, this skill places, densifies, and bakes them. You do not choose the pipeline, configure Renderer Features, or write the shader that consumes the lighting data you set up.

## 3. When to invoke this skill
- Placing or tuning lights: type, intensity and its unit, range, colour or colour temperature, cookies, spot angles, culling.
- Choosing a lighting strategy — fully baked, fully realtime, or mixed — and configuring the lightmapper, the Lighting Settings Asset, and the bake itself.
- A bake produced nothing, or produced seams, bleeding, or blotches on specific meshes.
- Tuning shadows against a platform budget: cascade count and splits, shadow distance, bias, per-light resolution tiers, soft shadow quality.
- Placing Reflection Probes, deciding baked against realtime, and fitting box projection to a room or corridor.
- Authoring Adaptive Probe Volumes — placement, density, Baking Sets, streaming — and fixing light leaks between spaces that should not influence each other.
- Scoping which lights affect which renderers through Rendering Layers, including across an APV boundary.
- Supplying the URP lighting HLSL surface a custom lit shader must call, without authoring the shader.
- Negative trigger: whether the project targets URP or HDRP — that is `render-pipeline-urp-hdrp`.
- Negative trigger: HDRP pipeline settings — Frame Settings, its Volume framework, Diffusion Profiles, ray and path tracing, and the Asset-level toggle that makes APV available — that is `unity-hdrp-rendering`; the probe authoring it hands off arrives here.
- Negative trigger: rendering path, Renderer Features, camera stacking, or `Light2D` and the 2D Renderer — that is `unity-urp-rendering`, whose rendering-path choice this skill's light limits depend on.
- Negative trigger: post-processing Volumes and their overrides — that is `unity-post-processing`; a `VolumeProfile` and a `ProbeVolume` share a word and nothing else.
- Negative trigger: the Shader Graph or HLSL of a custom lighting model — that is `shader-authoring`; this skill supplies the API surface it calls.
- Negative trigger: a gameplay rule that reads light state — stealth detection, a day-night trigger, a light-based puzzle — that decision lives in `Game.Core.*` per `coding-principles.md`.

## 4. How to use this skill
1. **Confirm the pipeline and then confirm which asset actually owns the setting being changed** — Built-in RP reads Quality Settings, URP reads its own Asset, and editing the wrong one changes nothing while looking correct. [root-links.md](references/root-links.md) pins the doc version and maps each setting to its owner.
2. **Choose the light type by what it can do, not by how it looks in the viewport**, per [light-sources.md](references/light-sources.md) — an Area light contributes only through a bake and is inert at runtime, a Directional light ignores its position entirely and uses only rotation, and a Point or Spot light's Range is a hard cutoff rather than a falloff, so a light that stops short is a range problem that raising intensity only blows out.
3. **Set each light's Mode before anything is authored around it** — Realtime, Baked, or Mixed is a bake-time property, so changing it later invalidates the bake rather than taking effect, and the scene's single Lighting Mode applies to every Mixed light at once, per [global-illumination.md](references/global-illumination.md). One light cannot be Shadowmask while another is Baked Indirect.
4. **Flag the geometry and give it lightmap UVs before blaming the lightmapper** — a mesh without Contribute GI is never lightmapped and a mesh with overlapping or missing lightmap UVs bakes bleeding and seams, and both report success, per [global-illumination.md](references/global-illumination.md).
5. **Spend shadow budget on distance before resolution**, per [shadows.md](references/shadows.md) — shadow distance is the dominant cost lever, and cascades subdivide that distance rather than extending it, so adding a cascade redistributes resolution instead of making shadows reach further.
6. **Fix shadow acne with normal bias before depth bias** — depth bias pushes the whole comparison along the light ray and detaches contact shadows from their casters, which reads as objects floating, while normal bias offsets along the surface normal and costs far less of that artifact.
7. **Choose Reflection Probe mode by whether the reflected content actually changes**, per [reflections.md](references/reflections.md) — Baked is nearly free at runtime, a Realtime probe re-renders six faces and needs a deliberate refresh mode and time slicing, and box projection needs its box fitted to the real room or reflections slide as the camera moves.
8. **Author Adaptive Probe Volumes for dynamic objects instead of a legacy Light Probe Group**, per [probe-volumes.md](references/probe-volumes.md) — confirm APV is enabled on the pipeline Asset first, since without that the volumes bake and render nothing — on URP that toggle is part of this setup, on HDRP `unity-hdrp-rendering` owns it and hands the authoring here — then size and densify to the traversable space rather than the whole level.
9. **Treat an APV light leak as a placement problem before reaching for bias** — a probe sitting inside a wall carries outdoor light into the room next to it, and a Probe Adjustment Volume or a rendering layer mask removes the cause, where raising leak-reduction bias only trades it for a different artifact.
10. **Scope lights with Rendering Layers rather than culling masks under an SRP**, per [rendering-layers.md](references/rendering-layers.md) — the mask must be enabled on the pipeline Asset before it does anything, and it is what filters the shadow pass, so an object excluded from a light by culling mask alone can still appear in that light's shadows.
11. **Supply the lighting API and hand the shader off**, per [custom-lighting-api.md](references/custom-lighting-api.md) — `GetMainLight`, the `GetAdditionalLightsCount` loop, the attenuation and indirect helpers, and the include files they live in; the Shader Graph or HLSL that uses them is `shader-authoring`'s work.
12. **Attach a measurement to any lighting performance claim**, per `performance-and-algorithms.md`'s Verification section — bake time, frame time, or memory, captured on the tier being claimed for, not inferred from the optimization guide.
13. **Keep the gameplay decision in `Game.Core.*`** — a stealth threshold that reads light level is a game rule per `coding-principles.md`'s Shared Core integrity rule; this skill configures the light it reads from.

## 5. Specific goals / tasks this skill performs
- Light placement and parameter setup across Directional, Point, Spot, and Area, including intensity units and URP light limits.
- Lighting strategy: Baked, Realtime, or Mixed, the scene's Lighting Mode, lightmapper configuration, and the bake itself.
- Diagnosing failed or wrong bakes — unflagged geometry, lightmap UV problems, seams, bleeding.
- Shadow tuning against a platform budget: cascades, distance, bias, resolution tiers, soft shadow quality.
- Reflection Probe placement, mode choice, box projection fitting, and blending.
- Adaptive Probe Volume authoring on any SRP: placement, density, Baking Sets, streaming, leak removal.
- Lighting-side Rendering Layer masks, including across APV boundaries.
- Supplying URP's lighting HLSL surface to a custom shader author.
- Out of scope: pipeline choice (`render-pipeline-urp-hdrp`); HDRP pipeline settings and the APV enablement toggle (`unity-hdrp-rendering`); rendering path, Renderer Features, `Light2D` (`unity-urp-rendering`); post-process Volumes (`unity-post-processing`); shader content (`shader-authoring`); gameplay rules reading light state (`csharp-engineer`).

## 6. Output format
```
## Lighting — <scene or feature name>
- Pipeline confirmed: <Built-in RP / URP version / HDRP — and which asset owns the settings changed>
- Lights: <type, intensity and unit, range, colour or temperature — and why each>
- Light Modes: <per light> — scene Lighting Mode: <Baked Indirect / Shadowmask / Subtractive>
- Bake: <lightmapper, resolution, Contribute GI coverage, lightmap UV source, bake time>
- Dynamic-object lighting: <Adaptive Probe Volumes with density and Baking Set / Light Probes / none>
- Shadows: <distance, cascade count and splits, bias values, resolution tier — and the budget behind them>
- Reflections: <probe modes, placement, box projection fit, blend distance — or "skybox only">
- Rendering Layers: <what they scope, and confirmation the Asset enables them — or "unused">
- Custom shader API supplied: <entry points handed to shader-authoring — or "none">
- Verified on: <device or tier captured, bake time and frame time behind any perf claim>
- Layer: <Game.Client.* scene lighting, lighting assets, probe data>
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what the delivered lighting does not cover>
- Latent concerns: <failure modes not yet triggered: assumptions that hold only under current conditions, thresholds not yet reached, trade-offs knowingly deferred>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: "Light this URP outdoor level — static architecture, a player character that moves through it, glass corridors that should reflect."
- Output: one Directional sun set to Mixed with the scene's Lighting Mode on Shadowmask, so static geometry keeps baked shadows past the shadow distance while the player still casts a realtime one inside it. Verified every static mesh carried Contribute GI and had generated lightmap UVs before the first bake rather than after a wasted one. Adaptive Probe Volumes sized to the traversable space, not the whole level, so the player picks up indirect light without paying for probes in unreachable geometry. Shadow distance set from the level's real sightlines first, then four cascades within it. Baked Reflection Probes per corridor with box projection fitted to the corridor bounds, since an unfitted box slides the reflection as the camera moves. Bake time and mid-tier frame time both captured.

**Example 2**
- Input: "Some objects stop being lit when the player walks into the crowded market area."
- Output: not a lighting bug — Forward's per-object additional-light limit, which drops the lowest-priority lights per renderer while the scene as a whole still looks lit. Confirmed the light count in that area against the limit, and routed the rendering-path decision to `unity-urp-rendering`, since Forward+ removes exactly that limit and the choice belongs to it. On the lighting side, reduced overlapping decorative point lights whose ranges covered the same stalls, which lowered the count under the existing path regardless of how that decision lands.

**Example 3**
- Input: "Indoor rooms are picking up the outdoor sky colour after the APV bake."
- Output: a leak — probes falling inside the wall volume carry exterior lighting into the interior cell. Fixed at the cause with a Probe Adjustment Volume over the affected rooms plus rendering layer masks separating interior from exterior lights, per §4's leak step, after confirming Rendering Layers were actually enabled on the URP Asset. Left the leak-reduction bias at default deliberately: raising it would have hidden this leak while softening contact lighting everywhere else in the level.

## 8. Edge cases & guardrails
- Never assume a Built-in RP page applies to URP — shadow distance, cascades, and resolution live on the URP Asset, and the Quality Settings fields for them do not drive a URP project.
- Never expect an Area light to do anything at runtime — it contributes through the bake only, and a realtime one is silently inert.
- Never move a Directional light to change its lighting — only its rotation is read.
- Never raise intensity to make a Point or Spot light reach further — Range is a hard cutoff, and the result is a blown-out near field with the same reach.
- Never treat Light Mode as a runtime switch — it is baked into the result, and changing it invalidates the bake.
- Never set two Mixed lights to different Lighting Modes — the mode is a scene-wide setting, and the Inspector will not warn.
- Never bake before confirming Contribute GI and lightmap UVs — the most common bad bake is geometry the lightmapper was never given.
- Never add cascades to make shadows reach further — cascades subdivide the shadow distance, they do not extend it.
- Never fix acne by raising depth bias alone — it detaches shadows from their casters, which is a worse artifact than the one being fixed.
- Never leave a Realtime Reflection Probe on every-frame refresh without time slicing — it re-renders six faces, and the cost is not visible in the Inspector.
- Never author Adaptive Probe Volumes without confirming the pipeline Asset enables them — they bake and render nothing, with no error.
- Never treat an APV light leak as a bias problem first — the probe placement is the cause, and bias trades the artifact rather than removing it.
- Never rely on a light's culling mask to keep an object out of its shadows under an SRP — the shadow pass filters on rendering layer mask.
- `LightShape` is obsolete — use `LightType.Spot`, `Pyramid`, or `Box`. `LightProbeProxyVolume` belongs to the Built-in pipeline; new SRP work uses Adaptive Probe Volumes.
- Never assert a lighting performance win without a capture — bake time, frame time, or memory, on the tier claimed for.
- Never let lighting configuration decide a gameplay outcome — `Game.Core.*` owns the rule that reads it.
