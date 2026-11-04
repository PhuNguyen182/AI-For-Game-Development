---
name: unity-hdrp-rendering
description: "HDRP: Frame Settings, HDAdditionalCameraData, Volumes, CustomPassVolume, ray tracing. Use once HDRP is confirmed."
user-invocable: false
---

# Unity HDRP Rendering

- **Not for:** which pipeline (`render-pipeline-urp-hdrp`).
- **Not for:** URP (`unity-urp-rendering`).
- **Not for:** shader content (`shader-authoring`).
- **Not for:** post-process authoring (`unity-post-processing`).
- **Not for:** probe placement and baking (`unity-lighting`).
- **Not for:** plain `Camera` scripting (`unity-camera-fundamentals`).
- **Not for:** entity rendering (`unity-entities-graphics`).
- **Docs:** https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/index.html (API: same path, `api/`) — pinned 17.5.
  - **Versions:** limitations change between majors, so confirm the installed version first.

## References
- **[custom-pass.md](references/custom-pass.md):** Rendering must be injected into the HDRP frame, or a pass is not visibly running.
- **[materials-and-diffusion-profiles.md](references/materials-and-diffusion-profiles.md):** Choosing a master stack, or subsurface scattering looks flat.
- **[water-and-ray-tracing.md](references/water-and-ray-tracing.md):** Water, ray tracing or path tracing is requested, or two high-fidelity features must coexist.

## Steps
1. **Identify the HDRP Asset the target quality level uses:** Quality Settings can assign one Asset per level.
   - **Reading only Graphics Settings:** can validate an Asset the target tier never loads.
2. **Diagnose from the Asset downward:** the Asset is the ceiling (features built into the player); Frame Settings only mask it.
   - **Frame Settings sets:** Asset defaults, `HDAdditionalCameraData` per camera, reflection and baked probes as separate sets.
   - **Toggle for a feature the Asset disabled:** shows as on but does nothing, with no warning.
3. **Author exposure, fog and sky as Volume overrides, never per-camera values:** a hardcoded value stops responding to blending.
   - **Local volumes:** need a trigger collider; Priority picks the winner on overlap; Blend Distance 0 pops at the boundary.
   - **Global Volumes:** apply only on layers in the camera's Volume layer mask (`HDAdditionalCameraData`); Visual Environment selects the sky type.
   - **Volumetric fog:** the Fog override's volumetric component and Local Volumetric Fog need Volumetrics enabled in the Asset.
   - **Exposure:** an authored property because HDRP is physically based.
   - **Override catalog:** larger than this skill lists; browse the manual index for an override not named here.
4. **Inject custom rendering through `CustomPassVolume`:** per [custom-pass.md](references/custom-pass.md).
   - **URP equivalent:** `ScriptableRendererFeature`/`ScriptableRenderPass` has no HDRP equivalent.
5. **Pick the master stack per surface and register every Diffusion Profile:** per [materials-and-diffusion-profiles.md](references/materials-and-diffusion-profiles.md).
   - **Unregistered profile:** renders as no profile, which looks like bad tuning.
6. **Enable Adaptive Probe Volumes in the Asset:** then hand off placement and baking to `unity-lighting`.
   - **"APV not working", not enabled in the Asset:** this skill's.
   - **"APV not working", enabled but unbaked, leaking or misplaced:** `unity-lighting`'s.
   - **Unbaked scene:** shows no APV contribution.
7. **Gate ray tracing, path tracing, volumetrics and Water on the Tech Spec's platform scope:** before they enter a spec, per [water-and-ray-tracing.md](references/water-and-ray-tracing.md).
   - **Mobile:** none of these is a mobile feature.
   - **Ray tracing:** also needs capable hardware on the PC/console tier.
   - **Platform scope unstated:** step 10.
8. **Check documented incompatibilities before combining high-fidelity features:** the loser disappears from the frame without an error.
9. **Verify on the Asset and hardware tier that ships:** never from an Editor check on a workstation.
10. **Missing input:** the Tech Spec's platform scope is unstated → dispatched agent `Blocked` or `Needs-decision`; main session `AskUserQuestion`.

## Never
- **Force every surface through Lit:** skin, cloth and hair have dedicated stacks that parameters cannot imitate.

## Output
```
## HDRP Configuration — <feature>
- HDRP Asset: <name> — quality levels referencing it
- Layer edited: <Asset ceiling / Frame Settings mask on camera or probe>
- Environment: <Volume overrides, placement, priority — or "unchanged">
- Custom pass: <mode, injection point, fade radius — or "none">
- Materials: <master stack per surface, Diffusion Profiles confirmed registered>
- APV: <enabled in Asset, authoring handed to unity-lighting / not used>
- High-fidelity features: <which, hardware and platform scope that authorize them, incompatibilities checked>
```

## Example
- **"Enable ray-traced reflections in the camera's Frame Settings, the Asset is fine":** declined.
  - **Did instead:** checked the Asset first, found ray tracing off and the minimum spec below the hardware requirement.
  - **Reported:** a platform decision for `cto`.
