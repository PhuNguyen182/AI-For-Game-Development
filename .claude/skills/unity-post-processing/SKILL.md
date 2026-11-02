---
name: unity-post-processing
description: "URP Volume overrides (Bloom, Tonemapping, DoF), FullScreenPassRendererFeature, PPv2. Use for full-screen looks."
user-invocable: false
---

# Unity Post-Processing

- **Not for:** pipeline choice (`render-pipeline-urp-hdrp`).
- **Not for:** HDRP Volumes (`unity-hdrp-rendering`).
- **Not for:** Renderer Features generally and camera anti-aliasing (`unity-urp-rendering`).
- **Not for:** Adaptive Probe Volumes (`unity-lighting`).
- **Not for:** shader content (`shader-authoring`).
- **Not for:** the gameplay rule that triggers an effect (Core, per `csharp-standards`).
- **Docs:** Manual https://docs.unity3d.com/6000.5/Documentation/Manual/post-processing-and-full-screen-effects.html · URP/core API `@17.6` · PPv2 `com.unity.postprocessing@3.5`.
  - **Versions:** swap the version segments for the installed ones.
  - **Render Graph:** it changed pass authoring across majors, so confirm the URP version first.
- **Conflict with `unity:urp-postprocessing`:** if installed, it covers live-Editor URP Volume debugging; this skill wins on conflict.
  - **Example:** reading `VolumeManager.instance.stack` is right inside a renderer feature.

## References
- **[volumes.md](references/volumes.md):** Placing a Volume, or a correct-looking override shows nothing.
- **[effect-catalog.md](references/effect-catalog.md):** Choosing which URP override delivers a look.
- **[pipeline-availability.md](references/pipeline-availability.md):** Promising an effect on a pipeline it was not authored on.
- **[custom-effects.md](references/custom-effects.md):** The catalog cannot express the effect.
- **[postprocessing-v2-legacy.md](references/postprocessing-v2-legacy.md):** The project is on Built-in RP.

## Steps
1. **Confirm the pipeline first:**
   - **Built-in RP:** uses PPv2 only, per [postprocessing-v2-legacy.md](references/postprocessing-v2-legacy.md).
   - **URP:** uses Volumes and is not compatible with PPv2; installing PPv2 adds a stack that never renders.
   - **HDRP:** routes away.
   - **API mixing:** never mix `Volume` and `PostProcessVolume` API in one answer.
2. **Check the two gates before any profile:** the Camera Post Processing checkbox, and HDR on the URP Asset of the target tier.
   - **Asset change:** requested from `unity-performance-engineer`, which owns tier Assets.
   - **Without HDR:** Tonemapping has nothing above 1 and Bloom Threshold misbehaves.
3. **Put the Volume on a layer in the camera's Volume Mask, and keep one Global Volume as the scene floor:** per [volumes.md](references/volumes.md).
4. **From code, write via `Override()`, not `.value`:** the blend skips parameters with `overrideState` false.
   - **`sharedProfile`:** use it for a change that must reach the asset.
   - **`profile`:** instantiates a per-instance copy.
5. **Pick overrides by mechanism:** per [effect-catalog.md](references/effect-catalog.md).
   - **Warmth:** White Balance, not Color Filter.
   - **Focus pull:** Depth of Field, not Vignette.
   - **Bloom Threshold below sky luminance:** blooms the whole sky.
6. **Verify the effect exists on the target pipeline:** per [pipeline-availability.md](references/pipeline-availability.md).
   - **Anti-aliasing and Ambient Occlusion:** not in the URP Volume list; route to `unity-urp-rendering`.
7. **Custom effect: pick the path by whether anything must blend:** then the injection point, per [custom-effects.md](references/custom-effects.md).
   - **Before post-processing:** the effect is tonemapped and graded.
   - **After post-processing:** the effect is not tonemapped or graded.
8. **Mobile: the stack has a fixed cost (tile-memory resolve) plus a per-pass cost for each multi-pass effect:** Bloom, DoF first to drop, per [effect-catalog.md](references/effect-catalog.md).
   - **Per tier:** state whether the look needs post-processing; the tier decision is `unity-performance-engineer`'s.
   - **Claim that removing an effect helped:** needs a Profiler GPU capture (`unity-profiler-diagnostics`).
9. **Keep the trigger rule in Core:** this skill wires only the visual it drives.
10. **Tier and device:** verify on the target tier, and name the tier and device captured; cite the Profiler data behind any performance claim.

## Never
- **Use `RenderPipelineManager.beginCameraRendering` for a reusable effect:** the Manual recommends a Renderer Feature.
  - **Callback is fine:** only for a one-off single-camera pass.
  - **Reusable across cameras, scenes or projects:** use a Renderer Feature.
- **Map PPv2 `ColorGrading` one-to-one onto URP overrides:** it folds Channel Mixer, Color Adjustments, Color Curves, Lift Gamma Gain and tonemapping into one class.

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
```

## Example
- **"Underwater tint works in Editor, not in a build":** a local Volume with no Global Volume (falls back to project defaults outside the blend region), on a layer outside the Volume Mask.
  - **Did instead:** added a Global floor and moved the layer.
