---
name: shader-authoring
description: >
  Technique for authoring shader content — Shader Graph node graphs and
  hand-written HLSL/ShaderLab: stylized and toon shading, custom lighting
  models, screen distortion, dissolve, outline, rim, hologram, decal and
  material-driven VFX shaders, reusable subgraphs, `UnityPerMaterial` CBUFFER
  layout for SRP Batcher compatibility, `shader_feature` versus
  `multi_compile` variant control, and `half` precision on mobile. Use when a
  shader must be written, fixed, or made to compile.
  Not for: pipeline choice (`render-pipeline-urp-hdrp`); pass injection
  (`unity-urp-rendering`, `unity-hdrp-rendering`); Volume plumbing around a
  full-screen effect (`unity-post-processing`); compute kernels
  (`compute-shader-vfx`); particle graphs (`vfx-particle-authoring`); the
  light rig it reads (`unity-lighting`); DOTS Instancing requirements
  (`unity-entities-graphics`); tuning an unchanged shader
  (`tech-lead-performance`).
---

# Shader Authoring — Shader Graph & HLSL Content

## 1. Objective
Produce shader content that is visually correct, compiles on every pipeline and platform the Tech Spec targets, and stays inside its budget for variants, precision, and batching. It prevents the failures that a working Editor preview hides: a shader that breaks SRP batching because its properties are not in the expected constant-buffer layout, a `multi_compile` that ships every combination into the build whether or not any material uses it, `float` precision applied everywhere on a mobile GPU that pays for it, a gameplay decision encoded in shader logic where the server cannot see it, and an effect verified on exactly one of the platforms it ships to.

## 2. Role
Act as the shader programmer for the client track — the tool reached for whenever a visual requirement resolves to writing or fixing shader content. You own the graph and the HLSL; the pipeline target arrives as an input, and where the resulting shader gets injected into the frame belongs to the pipeline skills.

## 3. When to invoke this skill
- A Tech Spec calls for a new or modified shader: stylized surface shading, a custom lighting model, a screen-space effect, a dissolve, outline, rim, or hologram, a decal shader, or a subgraph meant for reuse.
- Choosing between Shader Graph and hand-written HLSL for a specific effect.
- A shader fails to compile, renders magenta, or looks different between two platforms.
- Bringing a shader into SRP Batcher compatibility, or diagnosing why it is not batching.
- Reducing a shader's variant count, or deciding between `shader_feature` and `multi_compile` for a branch.
- Making an existing shader DOTS Instancing compatible once `unity-entities-graphics` has established that requirement.
- Negative trigger: which pipeline the shader targets, or which master stack — that is `render-pipeline-urp-hdrp`, and this skill needs its answer as an input.
- Negative trigger: where a pass runs in the frame — the Renderer Feature or Custom Pass Volume that injects it is `unity-urp-rendering` or `unity-hdrp-rendering`.
- Negative trigger: the `VolumeComponent` and override plumbing around a full-screen post effect — that is `unity-post-processing`; this skill writes the shader that effect samples.
- Negative trigger: a compute kernel producing simulation data — that is `compute-shader-vfx`; this skill writes the shader that consumes its buffer.
- Negative trigger: particle emission and simulation graph structure — that is `vfx-particle-authoring`; this skill writes the shader its output stage renders with.
- Negative trigger: the lights, probes and limits a lit shader reads — including a shader that receives fewer lights than expected, which is the rendering path's per-object limit rather than the shader — that is `unity-lighting`, which supplies the HLSL entry points this skill calls.
- Negative trigger: deciding that a shader must be DOTS Instancing compatible, or which properties are Hybrid Per Instance — that is `unity-entities-graphics`; authoring the shader itself stays here.
- Negative trigger: making an already-correct shader faster with no visual change requested — that is `tech-lead-performance`.

## 4. How to use this skill
1. **Take the pipeline target and master stack as given, and stop if they are missing** — shader structure, includes, and available lighting functions differ per pipeline, so authoring before `render-pipeline-urp-hdrp` has answered means guessing at the one input that invalidates everything.
2. **Default to Shader Graph and justify hand-written HLSL** — a graph is artist-editable, self-documenting, and generates SRP Batcher-compatible output automatically. Reach for HLSL only when the requirement is genuinely inexpressible in nodes: a custom lighting model, direct `StructuredBuffer` consumption, or control the graph does not surface.
3. **Put every material-tunable property in one `UnityPerMaterial` CBUFFER** — SRP Batcher compatibility depends on that block existing and matching across shaders in the batch, so a property declared outside it silently drops the shader out of batching with no warning anywhere.
4. **Know that a `MaterialPropertyBlock` breaks the SRP batch for that renderer** — `performance-and-algorithms.md` rightly requires it over assigning `renderer.material`, which instantiates and leaks a material; both facts hold, so where per-instance variation is wanted at scale, raise the conflict and let a measurement decide between material variants, GPU instancing, and accepting the lost batch.
5. **Choose `shader_feature` over `multi_compile` unless a variant is selected at runtime** — `shader_feature` strips variants no material in the build references, while `multi_compile` ships every combination unconditionally. Variant count is multiplicative, so state it in the handoff whenever a shader declares more than a couple of keywords.
6. **Use `half` precision by default in fragment work on mobile targets** — tile-based mobile GPUs execute `half` meaningfully faster than `float`, and blanket `float` is a cost paid on every pixel; keep `float` for positions, depth reconstruction, and anywhere banding would show.
7. **Work in the latest coordinate space the effect allows** — transform to world space only where the effect actually needs world coordinates, since an unnecessary per-vertex or per-pixel transform is repeated work no visual requirement asked for.
8. **Name properties per Unity convention and never inline a tunable number** — underscore-prefixed PascalCase reference names (`_BaseColor`, `_FoamWidth`), camelCase HLSL locals, and every tunable exposed as a property rather than a literal, per `coding-principles.md`'s no-magic-numbers rule.
9. **Comment only the non-obvious maths** — a hand-derived BRDF term, a refraction formula, a platform workaround — per `language-and-comments.md`'s Comment depth policy; a `lerp` needs no explanation.
10. **Verify on every platform the Tech Spec targets before calling it done** — capture the effect on each target quality tier; a shader validated only on PC can fail to compile, band, or lose precision on mobile GLES or Vulkan, and none of that shows in the Editor.
11. **Ask when the visual intent is described only by an adjective** — "make it feel weightier" is not a shader specification; get a reference image, a named comparable, or a concrete parameter before authoring, rather than iterating blind.

## 5. Specific goals / tasks this skill performs
- Stylized, toon, and custom-lighting-model surface shaders.
- Screen-space effect shaders: distortion, dissolve, outline, rim, hologram, status overlays.
- Decal shaders and the material shaders a particle or VFX output stage renders with.
- Reusable Shader Graph subgraphs.
- SRP Batcher compatibility work and diagnosis of a shader that is not batching.
- Variant-count control through deliberate `shader_feature`/`multi_compile` choice.
- Precision and platform-compatibility work across the project's shipping targets.
- Out of scope: pipeline targeting (`render-pipeline-urp-hdrp`); pass injection (`unity-urp-rendering`, `unity-hdrp-rendering`); Volume plumbing for post effects (`unity-post-processing`); compute kernels (`compute-shader-vfx`); particle graphs (`vfx-particle-authoring`); the light rig a lit shader reads (`unity-lighting`); DOTS Instancing requirements (`unity-entities-graphics`); pure performance tuning (`tech-lead-performance`).

## 6. Output format
```
## Shader Implementation — <effect name>
- Pipeline target: <URP / HDRP> and master stack — source: render-pipeline-urp-hdrp
- Authoring method: <Shader Graph / hand-written HLSL> — what made HLSL necessary, if used
- Files: <paths>
- Properties exposed: <name and purpose each>
- SRP Batcher: <compatible — UnityPerMaterial layout confirmed / not compatible and why>
- Keywords: <each, shader_feature or multi_compile, and the resulting variant count>
- Precision: <half/float choices in fragment work, and the target that drove them>
- Platforms verified: <each target actually captured, not assumed>
- Layer: <Game.Client.* shader assets — values received as properties, never decided here>
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what the delivered shader does not cover>
- Latent concerns: <failure modes not yet triggered: assumptions that hold only under current conditions, thresholds not yet reached, trade-offs knowingly deferred>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: "Build a stylized water shader with foam where it meets geometry", on a URP project shipping PC and mid-tier Android.
- Output: Shader Graph on the Universal Lit target, foam derived from scene depth difference; `_FoamWidth`, `_FoamColor`, and `_WaveSpeed` exposed as properties with no inlined constants; graph output confirmed SRP Batcher compatible; one `shader_feature` for an optional refraction variant so it strips from the build unless a material enables it; fragment maths kept in `half` except the depth reconstruction; captured on both PC and a mid-tier Android tier before hand-off.

**Example 2**
- Input: "Make the shader flash red when the hit is a critical, it already knows the damage number."
- Output: declined that shape — a shader must not decide what counts as critical, because that rule lives in `Game.Core.*` where the server evaluates the same logic, per `coding-principles.md`'s Shared Core integrity section. Exposed `_HitFlashColor` and `_HitFlashIntensity` instead and let the already-resolved outcome drive them from the client layer, which also makes the effect reusable for any hit category without touching the shader.

**Example 3**
- Input: a material with per-instance tint colour set through a `MaterialPropertyBlock` shows far more draw calls than expected after an SRP Batcher audit.
- Output: confirmed the cause rather than the symptom — the block is doing its job of avoiding a material instantiation, but a renderer using one leaves the SRP Batcher path, so the two goals genuinely conflict here. Reported both, and put the choice to a measurement per §4: material variants for a small fixed palette, GPU instancing for many instances of one mesh, or keeping the block and accepting the batch loss where the instance count is low.

## 8. Edge cases & guardrails
- Never author before the pipeline target and master stack are confirmed — that single input determines structure, includes, and whether the graph compiles at all.
- Never encode a gameplay decision in shader logic — the shader receives already-resolved values, because the rule lives in `Game.Core.*` where the server can evaluate it too.
- Never assign `renderer.material` in a hot path — it instantiates a material per renderer and leaks it, which is worse than the batching cost of the alternative.
- Never declare a material property outside `UnityPerMaterial` and assume batching survives — it drops silently, with no warning to notice.
- Never reach for `multi_compile` where `shader_feature` fits — the build ships every variant either way only in the first case, and variant counts multiply.
- Never use blanket `float` precision on a mobile target — it is a per-pixel cost with no visual return outside the cases that genuinely need the range.
- Never claim completion after verifying one platform when the Tech Spec names more — Editor-correct and device-correct are different claims.
- Never add parameters or techniques nobody asked for — an extra exposed property is another thing to tune, document, and keep working (YAGNI).
- If the visual intent is only an adjective, ask for a reference before authoring — iterating on a guess costs more than the question.
