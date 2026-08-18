---
name: render-pipeline-urp-hdrp
description: >
  Technique for targeting and configuring Unity's Scriptable Render
  Pipelines — URP (broad-platform/mobile-first, performance-oriented) and
  HDRP (PC/console, high-fidelity) — so shaders, VFX, custom render passes,
  and lighting/post-processing setups match the project's actual configured
  pipeline. Use this before writing any pipeline-dependent shader or VFX, and
  whenever asked to build a custom render feature/pass (URP Renderer Feature,
  HDRP Custom Pass) for a visual effect. Do not use this for the shader graph
  node logic itself once the pipeline target is already confirmed — that's
  `shader-authoring`. Do not use this for the Built-in Render Pipeline (legacy,
  no SRP) unless the project is explicitly confirmed to still be on it.
---

# Render Pipeline Targeting — URP & HDRP

## 1. Objective
Make sure shader, VFX, and render-feature work actually matches the render pipeline the project runs — since shader master-stack targets, lighting models, and available rendering features differ significantly between URP and HDRP, and code that assumes the wrong one compiles fine but looks wrong or breaks silently.

## 2. Role
Act as the render pipeline configuration specialist: you confirm which SRP is active, structure pipeline-specific work (Renderer Features, Custom Passes, Volumes) correctly for that pipeline, and keep pipeline-specific branching clean rather than scattered.

## 3. When to invoke this skill
- Before writing or modifying any shader/VFX that must integrate with the project's lighting, post-processing, or custom rendering feature set.
- Whenever asked to build a custom render pass for a visual effect: a URP `ScriptableRendererFeature`/`ScriptableRenderPass` (outline pass, screen distortion, custom compositing, decals-in-URP), or an HDRP Custom Pass Volume.
- Whenever a Volume-driven effect (HDRP) or Renderer Feature-driven effect (URP) is requested rather than a plain material shader.
- Negative trigger: once the pipeline target is confirmed, the actual node-graph/HLSL authoring is `shader-authoring`'s job — use this skill only for the pipeline-level setup around it.
- Negative trigger: don't assume Built-in Render Pipeline; only treat the project as Built-in RP if that's explicitly confirmed — most current Unity projects run URP or HDRP.

## 4. How to use this skill
1. **Confirm the active pipeline asset first** — check the project's Graphics/Quality settings for the assigned Render Pipeline Asset (URP Asset vs HDRP Asset), or the Tech Spec if it states the target. Never assume.
2. **URP specifics**:
   - Shader Graph target: "Universal" (Lit/Unlit/Sprite-Lit master stacks).
   - Custom render passes: implement a `ScriptableRendererFeature` + `ScriptableRenderPass`, and register it on the URP Renderer asset actually used by the target quality tier.
   - Rendering path matters: Forward, Forward+, and Deferred have different per-object light count budgets — confirm which path the project uses before assuming a light count is affordable.
   - URP is the mobile-first/broad-platform default — keep shader instruction count and overdraw within a mobile-appropriate budget even when also targeting PC through the same pipeline.
3. **HDRP specifics**:
   - Shader Graph target: "HDRP" (Lit/Unlit/Decal/Fabric/Hair/StackLit master stacks depending on material need).
   - Post-processing and environment settings live in the **Volume system** (Volume Profiles + Volume components with a blend region/priority) — not per-camera settings; author a Volume Profile for the effect rather than hardcoding per-camera post-process values.
   - Custom rendering work goes through **Custom Pass Volumes**, not a hand-rolled `ScriptableRenderPass` (that's URP's model, not HDRP's).
   - Diffusion Profiles drive subsurface-scattering-style materials (skin, wax, foliage) — assign the correct profile rather than approximating it in a Lit shader's base parameters.
   - High-fidelity HDRP-only features (ray tracing, path tracing, volumetric fog/clouds) are PC/console-class only — never assume they're available if the project also ships a mobile build; confirm against the Tech Spec's platform scope before using one.
4. **Keep pipeline branching clean.** When one asset must genuinely serve both pipelines, prefer a per-pipeline Shader Graph target pair (a URP-target graph and an HDRP-target graph sharing subgraphs) over a single hand-written HLSL file riddled with `#if UNIVERSAL_PIPELINE`/`#if HDRP` branches — this mirrors the "clean abstraction, not scattered `#if`" platform rule in `performance-and-algorithms.md`, applied to pipeline instead of platform.
5. **Map quality tiers deliberately.** URP render scale/shadow distance/shadow cascade settings, or HDRP Quality/Frame Settings overrides, should be assigned per the project's actual platform tiers — not left at whatever the template default was.
6. **Verify on the real pipeline before calling it done.** Capture a scene view (or request a build check) on the actual configured pipeline — a shader/effect validated only against Built-in RP assumptions can silently render incorrectly, or not at all, under URP/HDRP.

## 5. Specific goals / tasks this skill performs
- Confirming and targeting the project's actual SRP (URP or HDRP) for any pipeline-dependent shader/VFX work.
- Authoring URP Renderer Features / HDRP Custom Pass Volumes for effects that need a custom render pass.
- Authoring HDRP Volume Profiles for post-process or environment-driven visual effects.
- Mapping render pipeline quality settings to the project's platform tiers.
- Out of scope: the shader node-graph/HLSL content itself once the pipeline target is settled (`shader-authoring`), and particle graph structure (`vfx-particle-authoring`).

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
- Output: confirmed URP Forward+ renderer, built as a `ScriptableRendererFeature` injecting a full-screen distortion pass, Shader Graph Universal Unlit target for the distortion sample, verified on both PC and a mid-tier Android device since the project ships both.

**Example 2**
- Input: "Add volumetric fog for the boss arena's ability" on an HDRP PC-only project.
- Output: confirmed HDRP, authored via a Volume Profile with a Fog override scoped to the arena's Volume trigger region, flagged as PC/console-only per the project's platform scope (no mobile fallback needed since the project doesn't ship one).

## 8. Edge cases & guardrails
- Never assume Built-in Render Pipeline defaults — confirm URP or HDRP explicitly.
- Never claim a pipeline-dependent effect is finished without verifying it on the actually-configured pipeline.
- Never use an HDRP-only high-fidelity feature (ray tracing, volumetrics) on a project that also targets mobile without explicit Tech Spec sign-off.
- Keep pipeline-specific branches behind clean per-pipeline authoring (separate Shader Graph targets/passes), not scattered `#if` directives through shared code.
