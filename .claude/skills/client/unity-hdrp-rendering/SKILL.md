---
name: unity-hdrp-rendering
description: >
  Technique for deep High Definition Render Pipeline (HDRP) configuration —
  the HDRP Asset and per-camera Frame Settings, the Volume system (Exposure,
  Fog, Sky, and every other environment/post-process override), Custom Pass
  Volumes, materials and Diffusion Profiles (Lit/StackLit/Decal/Fabric/Hair),
  Adaptive Probe Volumes (APV)/light probes, the Water System, and
  ray/path tracing. Use this once the project is confirmed to be on HDRP and
  the task goes beyond "which pipeline do we target" into actually
  configuring HDRP's own systems. Do not use this for the initial
  pipeline-confirmation/shader-targeting decision between URP and HDRP —
  that's `render-pipeline-urp-hdrp`. Do not use this for URP
  (`unity-urp-rendering`), the shader node-graph/HLSL content itself
  (`shader-authoring`), plain `Camera`/`Transform` scripting
  (`unity-camera-fundamentals`), Cinemachine (`unity-cinemachine-authoring`),
  or particle graph structure (`vfx-particle-authoring`). Do not use this to
  decide how ECS/DOTS entities render through HDRP (`BatchRendererGroup`,
  DOTS Instancing shaders, material overrides) — that's
  `unity-entities-graphics`; this skill still owns the HDRP Asset/Frame
  Settings configuration that entity rendering depends on.
---

# Unity HDRP Rendering — High Definition Render Pipeline Configuration

Sources: see [references/](references/) for the HDRP Manual/Scripting API root links, split by topic — [root-links.md](references/root-links.md), [hdrp-asset-and-frame-settings.md](references/hdrp-asset-and-frame-settings.md), [volumes-and-environment.md](references/volumes-and-environment.md), [custom-pass.md](references/custom-pass.md), [materials-and-diffusion-profiles.md](references/materials-and-diffusion-profiles.md), [probe-volumes-and-lighting.md](references/probe-volumes-and-lighting.md), [water-and-ray-tracing.md](references/water-and-ray-tracing.md).

## 1. Objective
Configure HDRP's own systems correctly and deliberately — the HDRP Asset and Frame Settings, the Volume system, Custom Pass Volumes, materials/Diffusion Profiles, Adaptive Probe Volumes, the Water System, and ray/path tracing — once HDRP is already the project's confirmed pipeline, and keep every PC/console-class-only feature scoped to platforms that actually support it.

## 2. Role
Act as the HDRP configuration specialist: you configure the HDRP Asset and per-camera Frame Settings, author Volume Profiles for every environment/post-process need (not just post-processing — HDRP drives fog, sky, exposure, and more through the same system), build Custom Pass Volumes for effects that need a custom render pass, assign Diffusion Profiles to subsurface-scattering-style materials, set up Adaptive Probe Volumes for baked indirect lighting, and gate high-fidelity features (ray tracing, path tracing, volumetrics, the Water System) to the platform scope the Tech Spec actually authorizes.

## 3. When to invoke this skill
- Configuring the HD Render Pipeline Asset (global feature toggles) or a camera/Volume's Frame Settings overrides (per-camera feature toggles — can only turn off what the Asset enables, never turn on what it disables).
- Authoring or troubleshooting any Volume-driven system: Exposure, Fog (including Local Volumetric Fog), Sky, or any other environment/post-process Volume Override — HDRP routes nearly everything environmental through Volumes, not just post-processing.
- Building a custom render pass for a visual effect via a **Custom Pass Volume** (`CustomPassVolume` + a `CustomPass`, or a scripted one) — HDRP's equivalent of a URP Renderer Feature, but Volume-based rather than Renderer-based.
- Assigning Diffusion Profiles to materials that need subsurface-scattering-style shading (skin, wax, foliage), or picking between Lit/StackLit/Decal/Fabric/Hair master stacks for a specific material need.
- Setting up or debugging Adaptive Probe Volumes (APV) for baked indirect lighting, instead of manually-placed legacy Light Probes.
- Enabling/configuring the Water System (Pool/River/Ocean-Sea-Lake surface types), or ray tracing/path tracing effects — always confirming platform scope first, since these are PC/console-class-only.
- Negative trigger: deciding *whether* the project should be on HDRP at all, or the shader Graph target/node-graph/HLSL content itself once the pipeline is settled — `render-pipeline-urp-hdrp` for the former, `shader-authoring` for the latter.
- Negative trigger: any URP-specific system (Renderer Features, rendering paths, 2D Renderer, camera stacking, SRP Batcher) — `unity-urp-rendering`.
- Negative trigger: plain `Camera`/`Transform` scripting with no HDRP-specific system involved — `unity-camera-fundamentals`; Cinemachine — `unity-cinemachine-authoring`; particle graph structure — `vfx-particle-authoring`.
- Negative trigger: deciding how ECS/DOTS entities render (`BatchRendererGroup`, DOTS Instancing, material overrides) — that's `unity-entities-graphics`, which depends on this skill's HDRP Asset/Frame Settings configuration as its own prerequisite.

## 4. How to use this skill
1. **Confirm HDRP is actually active** (HDRP Asset assigned in Graphics settings) before doing any work here — if the project is on URP or Built-in RP, this skill doesn't apply; route to `unity-urp-rendering` or flag the mismatch.
2. **HDRP Asset vs. Frame Settings — know which one you're editing.** The HDRP Asset sets the *global ceiling* of what features exist in the build (per quality tier, if using multiple Assets); Frame Settings (on a Camera, Reflection Probe, or the Asset's own defaults) can only toggle features *within* what the Asset already enables — a Frame Settings toggle that tries to turn on something the Asset disabled has no effect. Diagnose "a feature isn't showing up" by checking the Asset first, not just the camera's Frame Settings.
3. **Everything environmental goes through Volumes, not per-camera settings.** Exposure, Fog, Sky, and most other environment/post-process behavior is authored as a Volume Profile with the relevant Overrides, placed on a Global Volume or a local Volume with a defined blend region/priority — don't hardcode per-camera exposure/fog values when the project already drives this through Volumes.
4. **Custom rendering work goes through Custom Pass Volumes, not a hand-rolled `ScriptableRenderPass`** (that's URP's model, not HDRP's). Set the Custom Pass Volume's Mode (Global vs. local, with Fade Radius for a local volume) and inject at the correct point in the render loop for what the pass needs to read/write; note Custom Pass Volumes don't blend the way regular Volumes do — only Fade Radius softens a local volume's edge.
5. **Diffusion Profiles drive subsurface-scattering-style materials** (skin, wax, foliage) — assign the correct Diffusion Profile asset rather than approximating the look via a Lit shader's base parameters alone; for StackLit specifically, set Dual Specular Lobe Parametrization to "From Diffusion Profile" when the profile should drive the specular lobes too.
6. **Pick the master stack per material need**: Lit for general PBR surfaces, StackLit for materials needing multiple specular lobes/coat layers, Decal for projected decals, Fabric/Hair for their respective specialized shading models — don't force every material through Lit when the surface type has a dedicated stack.
7. **Adaptive Probe Volumes (APV) over manually-placed Light Probes** for baked indirect lighting in most new work — APV auto-places probe "bricks" based on scene geometry density; only reach for manual Light Probe placement when APV's automatic placement genuinely doesn't fit the scene's needs.
8. **Gate PC/console-only features explicitly.** Ray tracing, path tracing, volumetric fog/clouds, and the Water System are high-fidelity features that are PC/console-class only (and require ray-tracing-capable hardware for the ray/path-tracing subset specifically) — never enable one of these if the project also ships a mobile build, unless the Tech Spec explicitly scopes it as PC/console-only with a defined fallback for other platforms. Confirm hardware requirements before assuming ray tracing is viable at all on the target PC/console tier.
9. **Path tracing and regular ray tracing have real feature gaps** (e.g. Local Volumetric Fog isn't supported under path tracing, and general ray tracing isn't compatible with volumetric fog either) — check the specific effect's documented limitations before combining it with ray/path tracing rather than assuming everything composes.
10. **Verify on the actually-configured Asset/platform tier before calling it done.** A Frame Settings toggle that silently does nothing because the Asset disabled that feature, or a high-fidelity effect that doesn't run on the actual target hardware class, isn't caught by "it compiled" — capture a scene view or request a build check on the real target tier.

## 5. Specific goals / tasks this skill performs
- HDRP Asset global feature configuration and per-camera/per-probe Frame Settings overrides.
- Volume Profile/Override authoring for Exposure, Fog (incl. Local Volumetric Fog), Sky, and other environment-driven effects.
- Custom Pass Volume authoring for effects needing a custom render pass.
- Material/Diffusion Profile assignment across Lit/StackLit/Decal/Fabric/Hair master stacks.
- Adaptive Probe Volume setup for baked indirect lighting.
- Water System setup and ray/path tracing configuration, always platform-scoped per the Tech Spec.
- Out of scope: the URP-vs-HDRP targeting decision (`render-pipeline-urp-hdrp`), shader node-graph/HLSL content (`shader-authoring`), URP systems (`unity-urp-rendering`).

## 6. Output format
```
## HDRP Setup — <feature name>
- HDRP confirmed active: yes (HDRP Asset: <name>)
- Layer edited: HDRP Asset (global) / Frame Settings (camera or probe, override list: <...>)
- Approach: Volume Profile/Override / Custom Pass Volume / Material+Diffusion Profile / APV / Water System / Ray-Path Tracing
- Files: <paths>
- Platform scope: PC/console-only feature(s) flagged — <yes/no, which ones> ; hardware requirement confirmed — <yes/no/n-a>
- Known limitations/incompatibilities: <e.g. path tracing + Local Volumetric Fog not supported>
- Verified on: <Asset/platform tier actually tested>
```

## 7. Examples
**Example 1**
- Input: "Add volumetric fog for the boss arena's ability" on an HDRP PC-only project.
- Output: confirmed HDRP Asset has Fog and Volumetrics enabled; authored a Local Volumetric Fog via a Volume Profile with a Fog Override scoped to the arena's Volume trigger region; flagged as PC/console-only per the project's platform scope (no mobile fallback needed since the project doesn't ship one); confirmed no ray-tracing effects are active on that camera that would conflict with volumetric fog.

**Example 2**
- Input: "Give the boss a skin-like material that reads correctly under the arena's lighting."
- Output: built the material on the Lit master stack with Subsurface Scattering enabled, assigned a dedicated Diffusion Profile tuned for skin rather than approximating via base color/smoothness alone; verified under the arena's actual baked Adaptive Probe Volume lighting rather than only in an isolated test scene.

## 8. Edge cases & guardrails
- Never assume a Frame Settings toggle alone controls a feature — check whether the HDRP Asset itself has that feature enabled first; the Asset is the ceiling, Frame Settings can only work within it.
- Never hardcode per-camera exposure/fog/sky values when the project drives environment behavior through the Volume system elsewhere — stay consistent with Volume Profiles/Overrides.
- Never hand-roll a `ScriptableRenderPass`-style custom pass for HDRP — use Custom Pass Volumes, HDRP's actual mechanism for injected render passes.
- Never approximate a subsurface-scattering-style material (skin, wax, foliage) purely through Lit base parameters when a Diffusion Profile is the correct tool.
- Never enable ray tracing, path tracing, volumetric fog/clouds, or the Water System on a project that also ships mobile without explicit Tech Spec sign-off and a defined non-PC/console fallback.
- Never assume ray-traced and volumetric effects compose freely — check the specific documented incompatibilities (e.g. path tracing vs. Local Volumetric Fog) before combining them.
- Never claim a pipeline-dependent HDRP effect is finished without verifying it on the actually-configured HDRP Asset and target platform tier.
