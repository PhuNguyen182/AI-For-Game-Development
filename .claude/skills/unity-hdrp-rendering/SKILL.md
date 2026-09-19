---
name: unity-hdrp-rendering
description: >
  Technique for configuring HDRP's own systems once HDRP is the confirmed
  pipeline: the HD Render Pipeline Asset as the feature ceiling with Frame
  Settings as masks, Volume-driven environment (Exposure, Fog,
  Local Volumetric Fog, Sky), `CustomPassVolume` injection, Diffusion Profiles
  and the Lit, StackLit, Decal, Fabric and Hair master stacks, Adaptive Probe
  Volume enablement, the Water System, and ray and path tracing. Use when HDRP
  must be configured or a feature silently does nothing.
  Not for: which pipeline the project is on (`render-pipeline-urp-hdrp`); URP
  (`unity-urp-rendering`); shader content (`shader-authoring`); post-process
  authoring (`unity-post-processing`); probe baking (`unity-lighting`); plain
  `Camera` scripting (`unity-camera-fundamentals`); entity rendering
  (`unity-entities-graphics`).
---

# Unity HDRP Rendering — High Definition Render Pipeline Configuration

## Bundled resources

### References
Read-only context, loaded on demand so SKILL.md itself stays short.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | HDRP manual and API roots plus the version pin | Starting any task here, or confirming which HDRP version the project installs |
| [hdrp-asset-and-frame-settings.md](references/hdrp-asset-and-frame-settings.md) | The Asset as ceiling, Frame Settings as mask, `HDAdditionalCameraData` | A feature is enabled somewhere and still does nothing |
| [volumes-and-environment.md](references/volumes-and-environment.md) | Volume placement, priority, and the environment overrides HDRP routes through it | Authoring exposure, fog, or sky, or scoping an effect to a region |
| [custom-pass.md](references/custom-pass.md) | `CustomPassVolume`, injection points, fade radius, scripted passes | Custom rendering has to be injected into the HDRP frame |
| [materials-and-diffusion-profiles.md](references/materials-and-diffusion-profiles.md) | Master stacks and the Diffusion Profile registration requirement | Choosing a shading model, or subsurface scattering looks wrong |
| [probe-volumes-and-lighting.md](references/probe-volumes-and-lighting.md) | Adaptive Probe Volumes, what enabling them requires, and where authoring goes | Baked indirect lighting is involved and the Asset side must be right |
| [water-and-ray-tracing.md](references/water-and-ray-tracing.md) | Water System, ray and path tracing, hardware requirements, incompatibilities | A high-fidelity feature is requested, or two of them must coexist |

## 1. Objective
Configure HDRP so a requested feature is actually reachable on the hardware the project ships to, and so the layer that governs it is the one being edited. It prevents HDRP's characteristic failure, which is silence: a Frame Settings toggle that cannot enable what the Asset disabled, a Diffusion Profile assigned to a material but never registered in the project's list, a Custom Pass Volume expected to blend like a regular Volume, a path-traced scene combined with an effect path tracing does not support, and a high-fidelity feature specified for a project whose platform scope excludes the hardware it requires.

## 2. Role
Act as the HDRP configuration specialist for the client track — the tool reached for once `render-pipeline-urp-hdrp` has confirmed HDRP and the work is configuring HDRP's own systems. You own the Asset, Frame Settings, Volumes, Custom Passes, and material shading models; you do not own shader content, post-process effect authoring, or lighting design.

## 3. When to invoke this skill
- Configuring the HD Render Pipeline Asset's global feature set, or a camera's or reflection probe's Frame Settings overrides.
- Authoring Volume-driven environment: Exposure, Fog and Local Volumetric Fog, Sky and Visual Environment.
- Injecting custom rendering through a `CustomPassVolume`, global or local, or a scripted `CustomPass`.
- Choosing between the Lit, StackLit, Decal, Fabric, and Hair master stacks, and assigning Diffusion Profiles to subsurface-scattering materials.
- Enabling Adaptive Probe Volumes at the Asset level so baked indirect lighting can be authored.
- Setting up the Water System, ray tracing, or path tracing, and confirming the hardware and platform scope they require.
- A reported symptom that reads as HDRP silence: a toggled feature with no visible effect, subsurface materials rendering flat, a custom pass with a hard edge, or an effect that vanishes under path tracing.
- Negative trigger: which pipeline the project runs — that is `render-pipeline-urp-hdrp`, whose answer this skill requires as input.
- Negative trigger: any URP system — Renderer Features, rendering paths, camera stacking, the 2D Renderer — that is `unity-urp-rendering`.
- Negative trigger: the shader's node graph or HLSL — that is `shader-authoring`; this skill picks the master stack and where a pass is injected, not what it computes.
- Negative trigger: authoring a post-process effect or its override component — that is `unity-post-processing`; environment overrides that only HDRP has stay here.
- Negative trigger: probe placement, baking, lightmapping, and light setup as a lighting problem — that is `unity-lighting`; this skill enables APV in the Asset, it does not author the lighting.
- Negative trigger: plain `Camera` or `Transform` scripting with no HDRP system involved — that is `unity-camera-fundamentals`.
- Negative trigger: how ECS entities reach the renderer — that is `unity-entities-graphics`, which depends on this Asset configuration.

## 4. How to use this skill
1. **Confirm the HDRP Asset that the target quality level actually uses** — Quality Settings can assign a different Asset per level, so every step below applies to one specific Asset, and reading only Graphics Settings can validate against one the target tier never loads. [root-links.md](references/root-links.md) pins the HDRP version these settings belong to.
2. **Know whether you are editing the Asset's ceiling or a Frame Settings mask**, per [hdrp-asset-and-frame-settings.md](references/hdrp-asset-and-frame-settings.md) — the Asset decides which features exist in the build at all, and Frame Settings can only turn off what the Asset already enabled. A Frame Settings toggle attempting to enable a disabled feature does nothing and reports nothing, so diagnose from the Asset downward.
3. **Author environment through Volume overrides, not per-camera values**, per [volumes-and-environment.md](references/volumes-and-environment.md) — HDRP routes exposure, fog, and sky through the same Volume system as post-processing, so a hardcoded per-camera value both contradicts the project's own mechanism and stops responding to volume blending.
4. **Inject custom rendering through a `CustomPassVolume`, not a URP-style render pass**, per [custom-pass.md](references/custom-pass.md) — `ScriptableRendererFeature` is URP's model and has no HDRP equivalent. Choose the injection point from what the pass reads, and remember Custom Pass Volumes do not blend like regular Volumes; only Fade Radius softens a local one's edge.
5. **Pick the master stack from the surface type**, per [materials-and-diffusion-profiles.md](references/materials-and-diffusion-profiles.md) — Lit for general PBR, StackLit where a coat or a second specular lobe is genuinely needed, Decal for projection, Fabric and Hair for their shading models. Forcing every surface through Lit is how skin, cloth, and hair end up approximated by parameters that cannot express them.
6. **Register every Diffusion Profile in the project's Diffusion Profile list** — a profile assigned to a material but absent from that list renders as though the material had none, which reads as a badly tuned material rather than a missing registration. The list is bounded, so treat profile slots as a budget shared across the project.
7. **Enable Adaptive Probe Volumes in the Asset and hand placement and baking to the lighting owner**, per [probe-volumes-and-lighting.md](references/probe-volumes-and-lighting.md) — this skill makes APV available; where volumes go, how dense the bricks are, and what the bake produces is `unity-lighting`'s work.
8. **Gate every PC and console class feature on the Tech Spec's platform scope**, per [water-and-ray-tracing.md](references/water-and-ray-tracing.md) — ray tracing, path tracing, volumetrics, and the Water System are not mobile features, and ray tracing additionally needs capable hardware on the PC or console tier itself. Confirm the scope authorizes it before it enters a spec, not after it is built.
9. **Check documented incompatibilities before combining high-fidelity features** — path tracing and Local Volumetric Fog do not compose, and ray tracing has its own gaps against volumetric effects. These are documented per effect, and the failure is an effect quietly missing from the frame rather than an error.
10. **Verify on the Asset and hardware tier that actually ships** — a feature confirmed in the Editor on a workstation says nothing about the console tier, and an Asset-level difference between quality levels is invisible in code.
11. **Ask when the target platform scope is unstated** — HDRP work divides sharply into what every target can run and what only some can, and building the second on an assumption is discovered at certification rather than in review.

## 5. Specific goals / tasks this skill performs
- HDRP Asset feature configuration and Frame Settings overrides on cameras and reflection probes.
- Volume-driven environment authoring: Exposure, Fog and Local Volumetric Fog, Sky and Visual Environment.
- `CustomPassVolume` setup, injection point selection, and scripted custom passes.
- Master stack selection and Diffusion Profile assignment plus registration.
- Adaptive Probe Volume enablement at the Asset level.
- Water System, ray tracing, and path tracing configuration, scoped to authorized platforms and hardware.
- Diagnosis of features that are enabled somewhere and still do nothing.
- Out of scope: pipeline targeting (`render-pipeline-urp-hdrp`); URP (`unity-urp-rendering`); shader content (`shader-authoring`); post-process effect authoring (`unity-post-processing`); probe placement, baking, and lighting design (`unity-lighting`); plain camera scripting (`unity-camera-fundamentals`); entity rendering (`unity-entities-graphics`).

## 6. Output format
```
## HDRP Configuration — <feature name>
- HDRP Asset: <name> — and the quality levels that reference it
- Layer edited: <Asset ceiling / Frame Settings mask on camera or probe — which overrides>
- Environment: <Volume overrides authored, placement and priority — or "unchanged">
- Custom pass: <CustomPassVolume mode, injection point, fade radius — or "none">
- Materials: <master stack per surface, Diffusion Profiles assigned and confirmed registered>
- APV: <enabled in Asset — authoring handed to unity-lighting / not used>
- High-fidelity features: <which, hardware requirement confirmed, platform scope that authorizes them>
- Incompatibilities checked: <the combinations verified — or "none combined">
- Verified on: <Asset and hardware tier actually captured>
- Layer: <Game.Client.* pipeline assets and pass code>
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
- Input: "Add volumetric fog to the boss arena for the ultimate's cast" on an HDRP PC and console project.
- Output: confirmed the Asset used by both shipping quality levels has Fog and Volumetrics enabled, since a Frame Settings toggle could not have enabled them otherwise; authored a Local Volumetric Fog through a Volume with a trigger collider scoped to the arena, priority above the global environment volume and a non-zero blend distance so the boundary does not pop; confirmed no ray-traced effect is active on that camera, because ray tracing and volumetric fog do not compose; verified on the console tier's Asset rather than the Editor default.

**Example 2**
- Input: "Turn on ray-traced reflections in the camera's Frame Settings — the Asset is fine, it is a per-camera thing."
- Output: declined the premise. Frame Settings mask downward only: if the Asset does not enable ray tracing, the camera toggle has no effect and logs nothing, which is exactly why this reads as "it did not work." Checked the Asset first, found ray tracing disabled and the project's minimum spec below the hardware requirement, and reported that enabling it would raise the spec — a platform decision for `technical-architect`, not a rendering toggle.

**Example 3**
- Input: a skin material with a Diffusion Profile assigned still renders flat, with no subsurface scattering visible.
- Output: the profile was never added to the project's Diffusion Profile list, so the material referenced a profile the pipeline does not load and rendered as if it had none. Registered it per §4's registration step, and noted that the list is bounded, so the project needs a shared budget for profile slots rather than one per character.

## 8. Edge cases & guardrails
- Never diagnose from Frame Settings alone — the Asset is the ceiling, and a mask cannot enable what was never built in.
- Never assign a Diffusion Profile without registering it — an unregistered profile renders as none, and looks like a tuning problem.
- Never hand-roll a URP-style `ScriptableRenderPass` in HDRP — Custom Pass Volumes are the mechanism, and they do not blend like regular Volumes.
- Never hardcode per-camera exposure, fog, or sky — HDRP drives environment through Volumes, and a hardcoded value stops responding to them.
- Never enable ray tracing, path tracing, volumetrics, or the Water System without confirming both the platform scope and the hardware requirement.
- Never assume high-fidelity features compose — path tracing and Local Volumetric Fog do not, and the loser disappears silently.
- Never force every surface through Lit — skin, cloth, and hair have dedicated stacks for reasons parameters cannot substitute for.
- Never claim completion from an Editor check on a workstation — the shipping hardware tier is the one that matters.
- If the platform scope is unstated, ask before building anything PC or console class — that answer decides whether the work is possible at all.
