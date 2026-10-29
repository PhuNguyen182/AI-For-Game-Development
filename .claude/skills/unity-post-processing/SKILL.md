---
name: unity-post-processing
description: "URP Volume/VolumeProfile/VolumeComponent overrides (Bloom, Tonemapping, DoF), overrideState, Volume Mask, FullScreenPassRendererFeature custom passes, PPv2 on Built-in RP, mobile cost. Use for full-screen looks."
user-invocable: false
---

# Unity Post-Processing

Not for: pipeline choice (`render-pipeline-urp-hdrp`), HDRP Volumes (`unity-hdrp-rendering`), Renderer Features generally and camera anti-aliasing (`unity-urp-rendering`), Adaptive Probe Volumes (`unity-lighting`), shader content (`shader-authoring`), the gameplay rule that triggers an effect (`Game.Core.*`, per `csharp-standards`).
Docs: Manual https://docs.unity3d.com/6000.5/Documentation/Manual/post-processing-and-full-screen-effects.html · URP/core API `@17.6` · PPv2 `com.unity.postprocessing@3.5`. Swap the version segments for the installed ones; Render Graph changed pass authoring across majors, so confirm the URP version first. If `unity:urp-postprocessing` is installed it covers live-Editor URP Volume debugging; this skill wins on conflict (reading `VolumeManager.instance.stack` is right inside a renderer feature).

| Reference | Read when |
|---|---|
| [volumes.md](references/volumes.md) | Placing a Volume, or a correct-looking override shows nothing |
| [effect-catalog.md](references/effect-catalog.md) | Choosing which URP override delivers a look |
| [pipeline-availability.md](references/pipeline-availability.md) | Promising an effect on a pipeline it was not authored on |
| [custom-effects.md](references/custom-effects.md) | The catalog cannot express the effect |
| [postprocessing-v2-legacy.md](references/postprocessing-v2-legacy.md) | The project is on Built-in RP |

## Steps
1. **Confirm the pipeline first.** Built-in RP uses PPv2 only; URP uses Volumes and is not compatible with PPv2 (installing it adds a stack that never renders); HDRP routes away. Built-in follows [postprocessing-v2-legacy.md](references/postprocessing-v2-legacy.md). Never mix `Volume` and `PostProcessVolume` API in one answer.
2. **Check the two gates before any profile:** Camera Post Processing checkbox, and HDR on the URP Asset of the target tier (without HDR, Tonemapping has nothing above 1 and Bloom Threshold misbehaves).
3. **Put the Volume on a layer in the camera's Volume Mask, and keep one Global Volume as the scene floor**, per [volumes.md](references/volumes.md).
4. **From code, write via `Override()`, not `.value`**: the blend skips parameters with `overrideState` false. Use `sharedProfile` for a change that must reach the asset; `profile` instantiates a per-instance copy.
5. **Pick overrides by mechanism** ([effect-catalog.md](references/effect-catalog.md)): warmth is White Balance, not Color Filter; focus pull is Depth of Field, not Vignette; Bloom Threshold below sky luminance blooms the whole sky.
6. **Verify the effect exists on the target pipeline** ([pipeline-availability.md](references/pipeline-availability.md)). Anti-aliasing and Ambient Occlusion are not in the URP Volume list: route to `unity-urp-rendering`.
7. **Custom effect: pick the path by whether anything must blend**, then the injection point (before post-processing = tonemapped and graded; after = not), per [custom-effects.md](references/custom-effects.md).
8. **Mobile: the cost is having a stack at all** (tile-memory resolve), not the effect count. Decide per tier whether it carries post-processing; a claim that removing an effect helped needs a Profiler GPU capture (`unity-profiler-diagnostics`).
9. **Keep the trigger rule in `Game.Core.*`**; this skill wires only the visual it drives.

## Never
- Use `RenderPipelineManager.beginCameraRendering` for a reusable effect: the Manual recommends a Renderer Feature. The callback is fine only for a one-off single-camera pass; anything reusable across cameras, scenes or projects is a Renderer Feature.
- Map PPv2 `ColorGrading` one-to-one onto URP overrides: it folds Channel Mixer, Color Adjustments, Color Curves, Lift Gamma Gain and tonemapping into one class.

## Output
```
## Post-Processing — <scene or feature>
- Pipeline: <Built-in + PPv2 / URP version / HDRP routed>
- Gates: <Post Processing, HDR, Volume Mask layers>
- Volumes: <scope, profile, priority, weight, blend distance>
- Overrides: <effect — property tuned and why>
- Custom effect: <path, injection point, buffers read — or none>
- Scripted access: <sharedProfile/profile, overrideState handling — or none>
- Mobile: <does the tier carry post-processing>
- Verified: <tier/device captured; Profiler data behind any perf claim, or "not run">
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Underwater tint works in Editor, not in a build" → local Volume with no Global Volume (falls back to project defaults outside the blend region) and on a layer outside the Volume Mask; added a Global floor and moved the layer.
