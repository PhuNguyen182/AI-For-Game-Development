---
name: shader-authoring
description: >
  Authoritative technique for building shaders (Shader Graph and hand-written
  HLSL/ShaderLab) for a visual-effect requirement — stylized shading, screen
  distortion, custom lighting models, decals, dissolve/outline effects, and
  similar. Use this before writing or modifying any shader asset, whenever the
  purpose is a visual outcome. Do not use this for a compute-shader-driven
  simulation (GPU particle sim, procedural deformation feeding a VFX) — that's
  `compute-shader-vfx`. Do not use this for particle system authoring itself
  (VFX Graph / Shuriken graph structure) — that's `vfx-particle-authoring`.
  Do not use this when the task is pure performance tuning of an
  already-correct, unchanged shader with no visual delta requested — that
  belongs to Tech Lead – Performance. Do not use this to decide whether a
  shader needs to be DOTS Instancing compatible, or which properties need
  "Hybrid Per Instance" declared for ECS/DOTS entity rendering — that's
  `unity-entities-graphics`; this skill still owns the shader's actual
  node-graph/HLSL content either way.
---

# Shader Authoring

## 1. Objective
Produce shaders that are visually correct, pipeline-appropriate, and performant enough to ship on the project's actual target platforms — without duplicating gameplay decisions inside shader code or silently breaking on a render pipeline the shader was never tested against.

## 2. Role
Act as a senior shader programmer. You choose the right authoring method (Shader Graph vs hand-written HLSL/ShaderLab) for the effect at hand, and you are responsible for the shader compiling and looking correct on every pipeline/platform combination the Tech Spec targets.

## 3. When to invoke this skill
- A Tech Spec or GD request calls for a new or modified shader: stylized surface shading, a screen-space effect (distortion, chromatic aberration, damage vignette), a custom lighting model, a dissolve/outline/hologram effect, a decal shader, a Shader Graph subgraph for reuse across materials.
- Negative trigger: a compute-shader simulation whose output feeds a shader (e.g. GPU particle positions) — build the compute pass under `compute-shader-vfx` first, then use this skill only for the shader that consumes its buffer.
- Negative trigger: authoring the particle system/graph structure itself — use `vfx-particle-authoring`; this skill covers the shader a particle output stage renders with, not the emission/simulation graph.
- Negative trigger: a request to make an existing, visually-unchanged shader faster with no new visual requirement — redirect to Tech Lead – Performance.
- Negative trigger: deciding DOTS Instancing compatibility or "Hybrid Per Instance" property declarations for ECS/DOTS entity rendering — that's `unity-entities-graphics`; this skill still authors the shader's own node-graph/HLSL content once that requirement is known.

## 4. How to use this skill
1. **Confirm the render pipeline target** (Built-in / URP / HDRP) before writing anything — shader structure, includes, and available lighting functions differ per pipeline. If the pipeline-specific setup itself is in question (Renderer Features, Volume-driven effects, master stack target), consult `render-pipeline-urp-hdrp` first.
2. **Choose the authoring method**:
   - Shader Graph by default — easier to hand off, self-documenting node graph, artist-editable.
   - Hand-written HLSL/ShaderLab only when Shader Graph can't express the requirement: a custom lighting model, direct `ComputeBuffer`/`StructuredBuffer` consumption, or a technique needing manual control Shader Graph doesn't expose.
3. **Structure the shader cleanly**: separate vertex and fragment responsibilities, use the correct coordinate space at each stage (don't transform to world space earlier than needed), and put material-tunable values in a `CBUFFER` block so the shader stays SRP Batcher-compatible.
4. **Name things per convention**: shader property reference names follow Unity's own convention (`_BaseColor`, `_NoiseScale` — underscore-prefixed PascalCase), local HLSL variables use camelCase, and any tunable value gets a named property instead of an inlined magic number (per `coding-principles.md`'s "no magic numbers").
5. **Keep keyword/variant count bounded**: use `shader_feature`/`multi_compile` deliberately for real per-material branches, not speculatively. An uncontrolled combinatorial variant count inflates build time and shader memory — state the variant count in the handoff note if it's non-trivial.
6. **Test on every platform the project actually ships**: a shader that only compiles/looks correct on PC but silently fails or renders differently on mobile GLES/Vulkan is not done. Use the Unity MCP tools to capture a scene view on the target quality tier before declaring the effect finished.
7. **Comment the non-obvious math only** — a custom BRDF term, a hand-derived distortion formula, a workaround for a platform quirk — per the shared comment-depth policy; don't restate what the node graph or a straightforward `lerp` already says.

## 5. Specific goals / tasks this skill performs
- Stylized/toon/cel shading, custom lighting models.
- Screen-space effects: distortion, dissolve, outline/rim, hologram, damage/status overlays.
- Decal shaders, material-driven VFX shaders (the render stage a particle/VFX output feeds into).
- Shader Graph subgraphs for reuse across multiple materials.
- Out of scope: compute-shader simulation code (`compute-shader-vfx`), particle graph/emission structure (`vfx-particle-authoring`), and raw non-visual performance tuning (Tech Lead – Performance).

## 6. Output format
```
## Shader Implementation — <effect name>
- Pipeline target: Built-in / URP / HDRP
- Authoring method: Shader Graph / hand-written HLSL
- Files: <paths>
- Properties exposed: <list, with purpose>
- Keywords/variants used: <list, or "none">
- Platforms verified on: <list>
- Known limitations: <...>
```

## 7. Examples
**Example 1**
- Input: "Build a stylized water shader with foam at intersections, from the Tech Spec."
- Output: Shader Graph, URP Lit target, uses scene depth for foam intersection, `_FoamWidth`/`_FoamColor`/`_WaveSpeed` exposed properties, verified on PC and mid-tier Android.

**Example 2**
- Input: "Create a screen distortion shader for the ultimate ability."
- Output: hand-written HLSL full-screen pass (needed for a custom refraction sample not expressible in Shader Graph at the project's pipeline version), single `multi_compile` for an optional chromatic-aberration variant, verified on PC only per Tech Spec scope.

## 8. Edge cases & guardrails
- Shaders are visual-only: never encode a gameplay decision (e.g. "is this a critical hit") directly in shader logic — that decision belongs in `Game.Core.*` and the shader should only receive the already-resolved value (color, intensity) as a property.
- Never drive per-object material variation via `renderer.material.<property> = x` in a hot path — that instantiates a new material and defeats SRP batching; use a `MaterialPropertyBlock` instead, consistent with `performance-and-algorithms.md`.
- Don't claim a shader is finished after testing on only one pipeline/platform when the Tech Spec targets more than one.
- Stay scoped to the requested effect — don't gold-plate with extra parameters or techniques nobody asked for (YAGNI).
