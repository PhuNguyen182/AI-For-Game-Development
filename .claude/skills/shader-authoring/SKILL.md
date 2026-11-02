---
name: shader-authoring
description: "Shader Graph and HLSL/ShaderLab: toon, outline, dissolve, keywords, SRP Batcher. Use for any shader work."
user-invocable: false
---

# Shader Authoring

- **Not for:** pipeline choice (`render-pipeline-urp-hdrp`).
- **Not for:** pass injection (`unity-urp-rendering`, `unity-hdrp-rendering`).
- **Not for:** Volume plumbing for a full-screen effect (`unity-post-processing`).
- **Not for:** compute kernels (`compute-shader-vfx`).
- **Not for:** particle graphs (`vfx-particle-authoring`).
- **Not for:** the light rig or per-object light limits (`unity-lighting`).
- **Not for:** deciding DOTS Instancing requirements (`unity-entities-graphics`).
  - **Stays here:** authoring the DOTS-Instancing-compatible shader.
- **Not for:** tuning an unchanged shader (`gameplay-engineer`).
- **Companion:** if the Unity plugin is installed, `unity:shader-graph-create-custom-node` turns existing HLSL into a Shader Graph custom node.

## Steps
1. **Take the pipeline target and master stack as given; stop if missing:** see `render-pipeline-urp-hdrp`; includes and lighting functions differ per pipeline.
2. **Default to Shader Graph; justify hand-written HLSL:** graphs are artist-editable and SRP Batcher compatible.
   - **HLSL only for what nodes cannot express:** a custom lighting model, direct `StructuredBuffer` use.
3. **Put every material-tunable property in one `UnityPerMaterial` CBUFFER:** a property outside it drops the shader out of SRP batching with no console warning.
   - **Check:** the shader Inspector's SRP Batcher row reads compatible.
4. **`MaterialPropertyBlock` breaks the SRP batch for that renderer:** `csharp-standards` → `performance-and-algorithms.md` still requires it over `renderer.material`.
   - **`renderer.material`:** it instantiates and leaks a material.
   - **Both hold:** where per-instance variation is wanted at scale, report the conflict and let a measurement choose between these options:
     - **Material variants:** a small fixed palette.
     - **GPU instancing:** many instances of one mesh.
     - **Keeping the block:** low count.
5. **`shader_feature` unless a variant is selected at runtime:** `multi_compile` ships every combination; `shader_feature` strips unreferenced ones.
   - **More than a couple of keywords:** state the variant count (multiplicative).
6. **`half` by default in mobile fragment work:** `float` for positions, depth reconstruction and where banding shows.
7. **World space:** transform only where the effect needs it.
8. **Expose every tunable as a property, never a literal:** names `_PascalCase`, HLSL locals camelCase (`coding-principles.md`).
   - **Comments:** only non-obvious maths (`coding-principles.md` → Comments).
9. **Verify on every platform the Tech Spec targets:** a PC-only check misses compile failures, banding and precision loss on mobile GLES/Vulkan.
10. **Missing input:** visual intent given only as an adjective → dispatched agent `Blocked` or `Needs-decision`; main session `AskUserQuestion`.
    - **Needed before authoring:** a reference image, a named comparable or a concrete parameter.

## Never
- **Encode a gameplay decision in shader logic:** the rule lives in a Core assembly where the server evaluates it.
  - **Instead:** pass resolved values as properties (e.g. `_HitFlashColor`, `_HitFlashIntensity`).
- **`renderer.material` in a hot path:** never assign it.
- **Unrequested parameters and techniques:** never add parameters or techniques nobody asked for.

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
```

## Example
- **"Flash red when the hit is a critical, the shader already knows the damage":** declined, criticality is a Core rule.
  - **Did instead:** exposed `_HitFlashColor`/`_HitFlashIntensity`, driven from the client layer.
