---
name: vfx-particle-authoring
description: "Particle effects: VFX Graph vs ParticleSystem, contexts, Capacity, bounds, SendEvent, GPU Events, Simulation Space, Max Particles, sub-emitters, blend/sorting, overdraw, pooling. Use for particle visuals and their budget."
user-invocable: false
---

# VFX and Particle Authoring

Not for: the shader an output renders with (`shader-authoring`), custom simulation kernels (`compute-shader-vfx`), pipeline choice (`render-pipeline-urp-hdrp`), the bloom that makes an effect glow (`unity-post-processing`), gameplay rules triggered by a collision (`Game.Core.*`; this skill delivers the signal only).
Docs: https://docs.unity3d.com/Manual/ParticleSystems.html (unversioned); Visual Effect Graph `com.unity.visualeffectgraph@17.6` tracks the installed SRP version, so swap the segment to the project's SRP packages.

| Reference | Read when |
|---|---|
| [tool-choice.md](references/tool-choice.md) | Choosing VFX Graph vs ParticleSystem, or the effect must report back to gameplay |
| [particle-system-modules.md](references/particle-system-modules.md) | Building or fixing a built-in ParticleSystem effect |
| [vfx-graph-contexts.md](references/vfx-graph-contexts.md) | Building a VFX Graph, or it vanishes at the screen edge |
| [rendering-and-budget.md](references/rendering-and-budget.md) | Setting a budget, an effect costs too much, or pooling/tier scaling |

## Steps
1. **Confirm the render pipeline first** — VFX Graph needs a Scriptable Render Pipeline (URP, HDRP) and compute shaders; the Built-in pipeline has only ParticleSystem ([tool-choice.md](references/tool-choice.md)).
2. **Choose the tool by what the effect must do** — GPU simulation buys count but makes reading particle state back impractical, so an effect whose collisions drive a game rule uses ParticleSystem at any scale.
3. **Check compute support on the weakest target tier before committing to a graph** — a tier without it renders nothing, not a degraded effect. A second authored version for that tier is a legitimate outcome: decide it up front.
4. **ParticleSystem: set Simulation Space first** — Local follows the emitter, World stays behind; most attached/detached complaints are this setting ([particle-system-modules.md](references/particle-system-modules.md)).
5. **Treat Max Particles as a visible cliff** — at the cap emission stops, which reads as the effect cutting out.
6. **VFX Graph: size Capacity to the real peak** (it pre-allocates GPU memory) and **set bounds to cover where particles travel** (default bounds cull the effect when its origin leaves the frustum) ([vfx-graph-contexts.md](references/vfx-graph-contexts.md)).
7. **Budget in overdraw** (screen coverage × layers), not particle count; pick the cheapest blend/sort that reads correctly ([rendering-and-budget.md](references/rendering-and-budget.md)).
8. **Pool every repeatedly triggered effect and clear it on release** (`csharp-standards` → `performance-and-algorithms.md`); never `Instantiate`/`Destroy` per use; cap every looping emitter.
9. **Scale by tier by removing whole sub-effects**, not by thinning every emitter.
10. **Watch it play in-engine** on the target tier against the real background, and measure before claiming a saving (`unity-profiler-diagnostics`).
11. **Hand gameplay the collision signal, never the decision.**

## Never
- Assume an additive effect glows: that is bloom (`unity-post-processing`).
- Enable per-particle sorting by default: additive does not need it and it is paid every frame.

## Output
```
## VFX — <effect>
- Pipeline: <Built-in / URP / HDRP> — VFX Graph available?
- Tool: <VFX Graph / ParticleSystem> — deciding constraint
- Structure: <contexts or module stack>
- Simulation space: <Local / World> — why
- Capacity / Max Particles: <value> — behavior at the cap
- Bounds (VFX Graph): <how set, travel covered>
- Blend and sort: <mode, sorting on/off> — why
- Overdraw budget: <coverage and layers, agreed with whom>
- Tier scaling: <what is removed per tier>
- Pooling: <source, stop-and-clear on release>
- Gameplay signal: <collision/event handed to Client layer, or "purely visual">
- Verified: <in-engine capture: tier, background — or "not run">
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Flamethrower that sets enemies on fire where flames touch them" → ParticleSystem despite the count: it must report contact. World space, collision messages on, callback handed to the Client layer, which asks `Game.Core.*` whether it is a burn; collision quality set deliberately (High tests every particle against real colliders).
