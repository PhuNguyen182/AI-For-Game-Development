# Root Links — Particle and VFX Documentation Roots

Source: the Unity Manual and Scripting API roots below, plus the Visual Effect
Graph package documentation.
Covers: SKILL.md §4 — **"Confirm the render pipeline before choosing the tool"**.

Unity ships two unrelated particle systems. They share no assets, no API, and
no availability: one runs everywhere, the other requires a Scriptable Render
Pipeline and compute shader support. Which one a project can use is settled
before any authoring decision is made.

| Root | Holds | Source |
|---|---|---|
| Manual — Particle Systems | The built-in system, its module stack, and the component reference | [Particle Systems](https://docs.unity3d.com/Manual/ParticleSystems.html) |
| Manual — component reference | Every module's Inspector fields | [Particle System component](https://docs.unity3d.com/Manual/class-ParticleSystem.html) |
| API — `ParticleSystem` | Module structs, playback control, and the particle buffer | [ParticleSystem](https://docs.unity3d.com/ScriptReference/ParticleSystem.html) |
| API — `ParticleSystemRenderer` | Render mode, sorting, materials, alignment | [ParticleSystemRenderer](https://docs.unity3d.com/ScriptReference/ParticleSystemRenderer.html) |
| Package — Visual Effect Graph | Contexts, blocks, operators, capacity, events, output types | [Visual Effect Graph manual](https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@17.6/manual/index.html) |
| API — `VisualEffect` | The runtime component: exposed property setters, `SendEvent`, playback | [VisualEffect](https://docs.unity3d.com/ScriptReference/VFX.VisualEffect.html) |

## Version pin

Manual and Scripting API links are unversioned and resolve to the current
documentation set. The Visual Effect Graph package is pinned to `@17.6`, which
tracks the installed Scriptable Render Pipeline version rather than the Editor
version — swap that segment to match the project's actual SRP packages, since
VFX Graph ships in lockstep with them.

## Availability

| Pipeline | Built-in Particle System | VFX Graph | Source |
|---|---|---|---|
| Built-in Render Pipeline | Supported | **Not supported** — the package targets the Scriptable Render Pipelines | [Visual Effect Graph manual](https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@17.6/manual/index.html) |
| URP | Supported | Supported, subject to compute shader support on the target device | [Visual Effect Graph manual](https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@17.6/manual/index.html) |
| HDRP | Supported | Supported, with the fullest output feature set | [Visual Effect Graph manual](https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@17.6/manual/index.html) |

Which pipeline the project runs is `render-pipeline-urp-hdrp`'s decision, and
this table is one of its inputs rather than a reason to revisit it.

## Adjacent ownership

| Concern | Owner | Source |
|---|---|---|
| The shader an output context or particle renderer uses | `shader-authoring` | [Particle System component](https://docs.unity3d.com/Manual/class-ParticleSystem.html) |
| A custom HLSL or compute simulation step inside a graph | `compute-shader-vfx` | [Visual Effect Graph manual](https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@17.6/manual/index.html) |
| Bloom and colour grading that make an emissive effect glow | `unity-post-processing` — an additive effect in a scene without bloom is a different effect | [Particle Systems](https://docs.unity3d.com/Manual/ParticleSystems.html) |
