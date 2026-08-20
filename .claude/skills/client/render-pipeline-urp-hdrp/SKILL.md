---
name: render-pipeline-urp-hdrp
description: >
  Technique for targeting and configuring Unity's Scriptable Render
  Pipelines — URP (broad-platform/mobile-first, performance-oriented) and
  HDRP (PC/console, high-fidelity) — so shaders, VFX, custom render passes,
  and lighting/post-processing setups match the project's actual configured
  pipeline. Use this before writing any pipeline-dependent shader or VFX, and
  for the initial "which pipeline, and how do I target it" decision. Do not
  use this for the shader graph node logic itself once the pipeline target is
  already confirmed — that's `shader-authoring`. Do not use this for deep,
  pipeline-specific configuration once the target is confirmed — URP's
  Renderer Features/rendering paths/2D Renderer/camera stacking are
  `unity-urp-rendering`; HDRP's Frame Settings/Volume system/Custom Pass
  Volumes/Diffusion Profiles/APV/ray tracing are `unity-hdrp-rendering`. Do
  not use this for the Built-in Render Pipeline (legacy, no SRP) unless the
  project is explicitly confirmed to still be on it.
---

# Render Pipeline Targeting — URP & HDRP

## 1. Objective
Make sure shader, VFX, and render-feature work actually matches the render pipeline the project runs — since shader master-stack targets, lighting models, and available rendering features differ significantly between URP and HDRP, and code that assumes the wrong one compiles fine but looks wrong or breaks silently.

## 2. Role
Act as the render pipeline configuration specialist: you confirm which SRP is active, structure pipeline-specific work (Renderer Features, Custom Passes, Volumes) correctly for that pipeline, and keep pipeline-specific branching clean rather than scattered.

## 3. When to invoke this skill
- Before writing or modifying any shader/VFX that must integrate with the project's lighting, post-processing, or custom rendering feature set — to confirm which pipeline it must target.
- Deciding *whether* a project should be on URP or HDRP, or resolving which one is actually active before any pipeline-dependent work starts.
- Mapping quality tiers to the right pipeline choice, or keeping pipeline branching clean when one asset must genuinely serve both.
- Negative trigger: once the pipeline target is confirmed, the actual node-graph/HLSL authoring is `shader-authoring`'s job — use this skill only for the pipeline-level setup around it.
- Negative trigger: once the pipeline target is confirmed, deep configuration of that pipeline's own systems (URP Renderer Features/passes, rendering paths, 2D Renderer, camera stacking; HDRP Frame Settings, the Volume system, Custom Pass Volumes, Diffusion Profiles, Adaptive Probe Volumes, Water System, ray/path tracing) belongs to `unity-urp-rendering`/`unity-hdrp-rendering` respectively — use this skill only for the initial targeting decision, not the deep-dive work.
- Negative trigger: don't assume Built-in Render Pipeline; only treat the project as Built-in RP if that's explicitly confirmed — most current Unity projects run URP or HDRP.

## 4. How to use this skill
1. **Confirm the active pipeline asset first** — check the project's Graphics/Quality settings for the assigned Render Pipeline Asset (URP Asset vs HDRP Asset), or the Tech Spec if it states the target. Never assume.
2. **URP at a glance**: Shader Graph target "Universal" (Lit/Unlit/Sprite-Lit master stacks); mobile-first/broad-platform default — keep shader instruction count and overdraw within a mobile-appropriate budget even when also targeting PC through the same pipeline. Once the target is confirmed as URP, hand off Renderer Features/passes, rendering-path choice, 2D Renderer, camera stacking, and quality-tier asset settings to `unity-urp-rendering` — this skill doesn't own that configuration depth.
3. **HDRP at a glance**: Shader Graph target "HDRP" (Lit/Unlit/Decal/Fabric/Hair/StackLit master stacks depending on material need); high-fidelity HDRP-only features (ray tracing, path tracing, volumetric fog/clouds, the Water System) are PC/console-class only — never assume they're available if the project also ships a mobile build; confirm against the Tech Spec's platform scope before using one. Once the target is confirmed as HDRP, hand off Frame Settings, the Volume system, Custom Pass Volumes, Diffusion Profiles, Adaptive Probe Volumes, and ray/path tracing/Water System configuration to `unity-hdrp-rendering` — this skill doesn't own that configuration depth.
4. **Keep pipeline branching clean.** When one asset must genuinely serve both pipelines, prefer a per-pipeline Shader Graph target pair (a URP-target graph and an HDRP-target graph sharing subgraphs) over a single hand-written HLSL file riddled with `#if UNIVERSAL_PIPELINE`/`#if HDRP` branches — this mirrors the "clean abstraction, not scattered `#if`" platform rule in `performance-and-algorithms.md`, applied to pipeline instead of platform.
5. **Map quality tiers deliberately at the targeting level.** Confirm which quality tiers map to which pipeline (or pipeline asset variant) — the actual per-setting tuning (URP render scale/shadow cascades, HDRP Frame Settings overrides) happens in the pipeline-specific skill, not here.
6. **Verify on the real pipeline before calling it done.** Capture a scene view (or request a build check) on the actual configured pipeline — a shader/effect validated only against Built-in RP assumptions can silently render incorrectly, or not at all, under URP/HDRP.

## 5. Specific goals / tasks this skill performs
- Confirming and targeting the project's actual SRP (URP or HDRP) for any pipeline-dependent shader/VFX work.
- Keeping pipeline branching clean when a single asset must serve both URP and HDRP.
- Mapping quality tiers to the right pipeline/asset variant at a targeting level.
- Out of scope: the shader node-graph/HLSL content itself once the pipeline target is settled (`shader-authoring`); particle graph structure (`vfx-particle-authoring`); deep URP configuration — Renderer Features/passes, rendering paths, 2D Renderer, camera stacking (`unity-urp-rendering`); deep HDRP configuration — Frame Settings, Volume system, Custom Pass Volumes, Diffusion Profiles, Adaptive Probe Volumes, Water System, ray/path tracing (`unity-hdrp-rendering`).

## 6. Output format
```
## Pipeline Setup — <effect/feature name>
- Confirmed active pipeline: URP / HDRP (source of confirmation: <settings asset / Tech Spec>)
- Approach: Shader Graph target / Renderer Feature / Custom Pass Volume / Volume Profile
- Files: <paths>
- Quality tier mapping: <summary, or "unchanged from project default" with rationale>
- Platform scope: <PC/console/mobile — and any HDRP-only feature flagged as PC/console-only>
- Verified on: <pipeline + platform combination actually tested>
- Known limitations: <...>
```

## 7. Examples
**Example 1**
- Input: "Create a shader graph effect for the ultimate ability's screen distortion" on a URP mobile+PC project.
- Output: confirmed the URP Asset is active and the project's actual Renderer/quality tiers, set the Shader Graph target to Universal Unlit for the distortion sample, and handed off the full-screen injection (which Renderer, which `RenderPassEvent`) to `unity-urp-rendering` for the `ScriptableRendererFeature` build-out.

**Example 2**
- Input: "Add volumetric fog for the boss arena's ability" on an HDRP PC-only project.
- Output: confirmed HDRP is active and the project's platform scope is PC/console-only (no mobile fallback needed), flagged volumetric fog as a PC/console-class feature per that scope, and handed off the actual Volume Profile/Fog Override authoring to `unity-hdrp-rendering`.

## 8. Edge cases & guardrails
- Never assume Built-in Render Pipeline defaults — confirm URP or HDRP explicitly.
- Never claim a pipeline-dependent effect is finished without verifying it on the actually-configured pipeline.
- Never use an HDRP-only high-fidelity feature (ray tracing, volumetrics, Water System) on a project that also targets mobile without explicit Tech Spec sign-off.
- Keep pipeline-specific branches behind clean per-pipeline authoring (separate Shader Graph targets/passes), not scattered `#if` directives through shared code.
- Don't do the deep pipeline-specific configuration work here — confirm the target and platform scope, then hand off to `unity-urp-rendering` or `unity-hdrp-rendering` for the actual Renderer Feature/Custom Pass Volume/Volume Profile/etc. build-out.
