---
name: unity-post-processing
description: >
  Technique for Unity post-processing and full-screen effects: the URP Volume
  system — `Volume`, `VolumeProfile`, `VolumeComponent`, `VolumeManager`,
  global versus local scope, priority, weight, blend distance — the built-in
  Volume Override catalog from Bloom and Tonemapping through Depth of Field,
  Color Adjustments, Motion Blur and Vignette, custom effects through
  `FullScreenPassRendererFeature` or a scripted `ScriptableRendererFeature`
  plus `VolumeComponent`, and legacy Post Processing Stack v2 on the Built-in
  pipeline. Use when a full-screen effect must be added, tuned, or authored.
  Not for: pipeline choice (`render-pipeline-urp-hdrp`); HDRP Volumes
  (`unity-hdrp-rendering`); Renderer Features generally
  (`unity-urp-rendering`); Adaptive Probe Volumes (`unity-lighting`); shader
  content (`shader-authoring`).
---

# Unity Post-Processing — Volumes, Effect Catalog, Custom Effects, Legacy PPv2

## Bundled resources

### References
Read-only context, loaded on demand so SKILL.md itself stays short.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Manual and package roots, the version pin, and which pipeline owns which system | Starting any task here, or confirming what the project actually installs |
| [volumes.md](references/volumes.md) | `Volume`, `VolumeProfile`, `VolumeComponent`, blending order, `overrideState`, scripted access | Placing a Volume, or an override that looks correct produces no visible change |
| [effect-catalog.md](references/effect-catalog.md) | The built-in URP overrides and the property on each that actually decides the look | Choosing which override delivers a requested look |
| [pipeline-availability.md](references/pipeline-availability.md) | Which effects exist on Built-in RP, URP, and HDRP, and where the names diverge | Before promising any effect on a pipeline it was not authored on |
| [custom-effects.md](references/custom-effects.md) | Low-code and scripted authoring paths, injection points, buffer requirements | The built-in catalog cannot express the requested effect |
| [postprocessing-v2-legacy.md](references/postprocessing-v2-legacy.md) | `PostProcessLayer`, `PostProcessVolume`, `PostProcessProfile`, PPv2 effect classes | The project is on the Built-in Render Pipeline |

## 1. Objective
Deliver a full-screen effect that actually reaches the screen on the pipeline the project runs. Post-processing fails silently more than almost any other Unity system: a perfectly authored Volume Profile renders nothing when the Camera's Post Processing checkbox is off, a scripted intensity change does nothing while `overrideState` stays false, an effect requested from the wrong pipeline's catalog does not exist to be added, and a Volume on a layer outside the camera's mask is never evaluated. Every one of those reports success in the console.

## 2. Role
Act as the post-processing specialist: choose the effect, set up the Volume that drives it, and author a custom pass when the catalog cannot express what was asked. You do not choose the render pipeline, you do not build Renderer Features unrelated to post-processing, and you do not write the shader a custom effect runs.

## 3. When to invoke this skill
- Adding or tuning a built-in Volume Override — bloom, colour grading, depth of field, vignette, motion blur — in a URP scene.
- Setting up the Volume system itself: global versus local scope, profile creation and sharing, priority and weight when volumes overlap, blend distance for a region effect.
- A post-processing effect is configured but nothing appears on screen, or a scripted parameter change has no effect.
- Authoring a custom full-screen effect the built-in catalog cannot express, through either the low-code or the Volume-driven scripted path.
- Wiring post-processing on a project still on the Built-in Render Pipeline, through the legacy Post Processing Stack v2 package.
- Confirming whether a specific effect exists at all on the target pipeline before committing to a look.
- Negative trigger: whether the project should be on URP or HDRP — that is `render-pipeline-urp-hdrp`, whose answer this skill needs as input.
- Negative trigger: HDRP's own Volume framework — Exposure, Fog, Sky, Custom Pass Volumes — that is `unity-hdrp-rendering`, a parallel system sharing this one's vocabulary but not its API.
- Negative trigger: Renderer Features, rendering path, the 2D Renderer, or camera stacking — that is `unity-urp-rendering`, which owns Volume placement as pipeline configuration while this skill owns what the Volume drives.
- Negative trigger: Adaptive Probe Volumes and light probes — that is `unity-lighting`; they share the word Volume with this system and nothing else.
- Negative trigger: the Shader Graph nodes or HLSL a custom effect computes — that is `shader-authoring`; this skill delivers the pass and the parameter plumbing around it.
- Negative trigger: the gameplay rule that decides when an effect should appear — a status effect, a low-health cue — that lives in `Game.Core.*` per `coding-principles.md`; this skill only wires the visual to consume it.

## 4. How to use this skill
1. **Confirm the active render pipeline before citing a single API** — the three pipelines' post-processing systems are structurally parallel and mutually incompatible, and URP explicitly does not support the legacy PPv2 package, so installing it there adds a system that never renders. [root-links.md](references/root-links.md) pins the versions every page below is read at, and a Built-in RP project follows [postprocessing-v2-legacy.md](references/postprocessing-v2-legacy.md) from here instead.
2. **Enable Post Processing on the Camera and HDR on the URP Asset before diagnosing anything else** — the camera checkbox gates the entire stack, and with HDR off Tonemapping has no values above one to remap and Bloom's threshold stops behaving as authored. Both are the answer far more often than any profile setting is.
3. **Put the Volume on a layer inside the camera's Volume Mask** — the Volume Manager evaluates only masked layers, so a Volume on an excluded layer is not merely low priority, it is absent from the blend entirely, per [volumes.md](references/volumes.md).
4. **Give the scene one Global Volume as the floor every local Volume blends up from** — a local-only setup falls back to project defaults outside its blend region rather than to the look the scene was authored for, and the scripted-update failure documented in [volumes.md](references/volumes.md) is the same missing-global cause.
5. **Set `overrideState`, not just the parameter value, whenever a Volume parameter is written from code** — the Inspector checkbox beside each property is that flag, and a parameter with it false is skipped by the blend no matter what value it holds. `Override()` sets both, which is why it exists.
6. **Edit `sharedProfile` only when the change is meant to reach the asset on disk** — reading `profile` instantiates a runtime copy, so it is the right call for a per-camera variation and the wrong one for a scene-wide tweak, exactly as `sharedMaterial` is to `material`.
7. **Pick each override from what it decides rather than from what it is called**, per [effect-catalog.md](references/effect-catalog.md) — a warm look is White Balance rather than a tinted Color Filter, a focus pull is Depth of Field rather than a vignette, and Bloom's Threshold set below the scene's own sky luminance makes the whole sky bloom.
8. **Check the effect exists on the target pipeline before designing around it**, per [pipeline-availability.md](references/pipeline-availability.md) — Auto Exposure, Fog, and Screen Space Reflection are absent from URP, Panini Projection and Split Toning are absent from Built-in RP, and post-process anti-aliasing is a Camera setting in URP rather than an override anyone can find in the catalog.
9. **Choose the custom-effect path by whether the effect needs blendable parameters**, per [custom-effects.md](references/custom-effects.md) — `FullScreenPassRendererFeature` plus a Fullscreen Shader Graph needs no C# and gives no Volume blending; the scripted feature plus a `VolumeComponent` costs both and buys per-Volume tuning. Pick the second only when something must actually blend.
10. **Pick the injection point from what the pass reads and whether its output should be graded** — an effect injected before post-processing is subsequently tonemapped and colour-graded, one injected after is not, and the same shader looks correct in one project and blown out in another for exactly this reason.
11. **Treat turning post-processing on as the mobile cost, not the effect count** — a tile-based GPU resolves the framebuffer out of tile memory once the stack is enabled, so the meaningful decision on a low tier is whether that tier carries post-processing at all. Any claim that removing an effect helped ships with a Profiler GPU capture, per `performance-and-algorithms.md`'s Verification section.
12. **Keep the decision in `Game.Core.*` and only the visual here** — the threshold at which a status effect darkens the screen is a game rule per `coding-principles.md`'s Shared Core integrity rule; this skill wires the vignette that rule drives.

## 5. Specific goals / tasks this skill performs
- Volume system setup: global and local scope, profiles, priority, weight, blend distance, layer masking.
- Selecting and tuning built-in Volume Overrides against a described look.
- Diagnosing a post-processing setup that renders nothing, or a scripted parameter that does not take.
- Authoring custom full-screen effects through the low-code or Volume-driven scripted path, including injection point choice.
- Legacy PPv2 setup on Built-in Render Pipeline projects.
- Cross-pipeline effect availability checks before a look is committed to.
- Out of scope: pipeline choice (`render-pipeline-urp-hdrp`); HDRP's Volume framework (`unity-hdrp-rendering`); Renderer Features and rendering path (`unity-urp-rendering`); Adaptive Probe Volumes (`unity-lighting`); shader content (`shader-authoring`); the gameplay rule an effect visualises (`csharp-engineer`).

## 6. Output format
```
## Post-Processing — <scene or feature name>
- Pipeline confirmed: <Built-in RP with PPv2 / URP version / HDRP routed away>
- Camera and asset gates: <Post Processing enabled, HDR state, Volume Mask layers>
- Volume setup: <global or local, profile asset, priority, weight, blend distance>
- Overrides used: <effect list — the property tuned on each and why>
- Availability checked: <effects confirmed present on this pipeline, any refused>
- Custom effect: <low-code or scripted, injection point and what it reads — or "none">
- Scripted access: <sharedProfile or profile, and overrideState handling — or "none">
- Mobile: <whether the tier carries post-processing at all, and the rationale>
- Verified on: <device or quality tier captured, Profiler data behind any perf claim>
- Layer: <Game.Client.* profiles, renderer assets, and pass code>
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what the delivered configuration does not cover>
- Latent concerns: <failure modes not yet triggered: assumptions that hold only under current conditions, thresholds not yet reached, trade-offs knowingly deferred>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: "Give this URP scene a warm filmic daytime look — bloom on the bright surfaces, graded, slight vignette."
- Output: confirmed URP and that HDR was enabled on the asset the target tier uses, since Tonemapping without it produces a flat result that reads as a bad grade rather than a missing setting. One Global Volume with a new profile: Tonemapping in ACES, Color Adjustments for exposure and saturation, White Balance for the warmth rather than tinting through Color Filter, Bloom with Threshold set above the scene's actual sky luminance so it fires on the intended surfaces only, and a low-intensity Vignette. Left Depth of Field and Motion Blur out — neither was asked for, and both are expensive on the mobile tier.

**Example 2**
- Input: "The underwater volume works in the editor but the tint never appears in a build."
- Output: the Volume was local with no Global Volume in the scene, so outside its blend region the stack fell back to project defaults, and the local volume's own layer sat outside the camera's Volume Mask — it was never evaluated on either side. Added a Global Volume as the scene floor and moved the local Volume onto a masked layer, per §4's masking and global-fallback steps. The build-only symptom was the editor holding a previously resolved stack that a fresh load did not reproduce.

**Example 3**
- Input: "Fade the screen to grayscale as the player's health drops. Write it as a custom effect."
- Output: scripted path, since the fade has to blend — a `ScriptableRendererFeature` plus a `VolumeComponent` exposing a `ClampedFloatParameter`, injected after post-processing so the desaturation is not itself re-graded by Tonemapping. Wrote through `Override()` rather than assigning `.value`, which is what makes a scripted parameter take. The grayscale shader went to `shader-authoring`; the health threshold driving the parameter went to `Game.Core.*` — this skill delivered the pass and the parameter path between them.

## 8. Edge cases & guardrails
- Never debug a profile before checking the Camera's Post Processing toggle and the URP Asset's HDR setting — both silently disable work that is otherwise correct.
- Never assume an effect exists across pipelines — URP has no Auto Exposure, Fog, or Screen Space Reflection, and Built-in RP has no Panini Projection, Shadows Midtones Highlights, or Split Toning.
- Never look for anti-aliasing in URP's override catalog — it is a Camera setting, and time lost searching the Volume list is the usual outcome.
- Never assign a Volume parameter's `.value` from code and stop there — without `overrideState` the blend ignores it, and nothing reports the omission.
- Never read `volume.profile` for a scene-wide change — it instantiates a copy, so the edit reaches one instance and never the asset.
- Never map PPv2's `ColorGrading` onto URP's separate overrides one to one — PPv2 folds Channel Mixer, Color Adjustments, Color Curves, Lift Gamma Gain, and tonemapping into that single class, and there is no standalone PPv2 tonemapper type.
- Never mix `Volume` and `PostProcessVolume` API in one recommendation — they are parallel systems, and the project is on exactly one.
- Never confuse this Volume system with Adaptive Probe Volumes — shared word, unrelated system, and `unity-lighting` owns the other.
- Never reach for `RenderPipelineManager.beginCameraRendering` to inject a reusable effect — the Manual recommends the Renderer Feature pattern, and the callback is a one-off technique.
- Never carry a PC effect stack onto a mobile tier unchanged — the off-tile resolve is paid the moment the stack is enabled, before any effect runs.
- Never let post-processing code decide a gameplay outcome — it visualises a decision `Game.Core.*` already made.
