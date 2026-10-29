---
name: shader-authoring
description: "Author Shader Graph and HLSL/ShaderLab: toon, custom lighting, dissolve, outline, distortion, keywords and variants, SRP Batcher compatibility, mobile precision. Use for any shader work."
user-invocable: false
---

# Shader Authoring

Not for: pipeline choice (`render-pipeline-urp-hdrp`), pass injection (`unity-urp-rendering`, `unity-hdrp-rendering`), Volume plumbing for a full-screen effect (`unity-post-processing`), compute kernels (`compute-shader-vfx`), particle graphs (`vfx-particle-authoring`), the light rig or per-object light limits (`unity-lighting`), deciding DOTS Instancing requirements (`unity-entities-graphics`; authoring the DOTS-Instancing-compatible shader stays here), tuning an unchanged shader (`gameplay-engineer`).
Companion, if the Unity plugin is installed: `unity:shader-graph-create-custom-node` turns existing HLSL into a Shader Graph custom node.

## Steps
1. **Take the pipeline target and master stack as given; stop if missing** (`render-pipeline-urp-hdrp`) — includes and lighting functions differ per pipeline.
2. **Default to Shader Graph; justify hand-written HLSL** — graphs are artist-editable and SRP Batcher compatible. HLSL only for what nodes cannot express: a custom lighting model, direct `StructuredBuffer` use.
3. **Put every material-tunable property in one `UnityPerMaterial` CBUFFER** — a property outside it silently drops the shader out of SRP batching, with no warning.
4. **`MaterialPropertyBlock` breaks the SRP batch for that renderer**, while `csharp-standards` → `performance-and-algorithms.md` requires it over `renderer.material` (which instantiates and leaks a material). Both hold: where per-instance variation is wanted at scale, report the conflict and let a measurement choose between material variants (small fixed palette), GPU instancing (many instances of one mesh), or keeping the block (low count).
5. **`shader_feature` unless a variant is selected at runtime** — `multi_compile` ships every combination; `shader_feature` strips unreferenced ones. State the variant count (multiplicative) when more than a couple of keywords exist.
6. **`half` by default in mobile fragment work**; `float` for positions, depth reconstruction and where banding shows.
7. **Transform to world space only where the effect needs it.**
8. **Expose every tunable as a property**, never a literal; names `_PascalCase`, HLSL locals camelCase (`coding-principles.md`). Comment only non-obvious maths (`coding-principles.md` → Comments).
9. **Verify on every platform the Tech Spec targets** — a PC-only check misses compile failures, banding and precision loss on mobile GLES/Vulkan.
10. **Visual intent given only as an adjective** — ask for a reference image, a named comparable or a concrete parameter before authoring.

## Never
- Encode a gameplay decision in shader logic — the rule lives in `Game.Core.*` where the server evaluates it; pass resolved values as properties (e.g. `_HitFlashColor`, `_HitFlashIntensity`).
- Assign `renderer.material` in a hot path.
- Add parameters or techniques nobody asked for.

## Output
```
## Shader Implementation — <effect name>
- Pipeline target: <URP / HDRP> and master stack — from render-pipeline-urp-hdrp
- Authoring method: <Shader Graph / HLSL> — why HLSL, if used
- Files: <paths>
- Properties exposed: <name and purpose each>
- SRP Batcher: <compatible — UnityPerMaterial layout confirmed / not, and why>
- Keywords: <each, shader_feature or multi_compile, resulting variant count>
- Precision: <half/float choices and the target that drove them>
- Platforms verified: <each target actually captured>
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Flash red when the hit is a critical, the shader already knows the damage" → declined: criticality is a `Game.Core.*` rule; exposed `_HitFlashColor`/`_HitFlashIntensity` driven from the client layer.
