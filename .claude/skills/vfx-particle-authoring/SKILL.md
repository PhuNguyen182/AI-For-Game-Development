---
name: vfx-particle-authoring
description: "VFX Graph vs ParticleSystem, Capacity, bounds, SendEvent, sub-emitters, overdraw. Use for particle visuals and budget."
user-invocable: false
---

# VFX and Particle Authoring

- **Not for:** the shader an output renders with (`shader-authoring`).
- **Not for:** custom simulation kernels (`compute-shader-vfx`).
- **Not for:** pipeline choice (`render-pipeline-urp-hdrp`).
- **Not for:** the bloom that makes an effect glow (`unity-post-processing`).
- **Not for:** gameplay rules triggered by a collision (Core).
  - **This skill delivers:** the signal only.
- **Docs:** https://docs.unity3d.com/Manual/ParticleSystems.html (unversioned).
  - **Visual Effect Graph:** `com.unity.visualeffectgraph@17.6` tracks the installed SRP version, so swap the segment to the project's SRP packages.

## References
- **[tool-choice.md](references/tool-choice.md):** Choosing VFX Graph vs ParticleSystem, or the effect must report back to gameplay.
- **[particle-system-modules.md](references/particle-system-modules.md):** Building or fixing a built-in ParticleSystem effect.
- **[vfx-graph-contexts.md](references/vfx-graph-contexts.md):** Building a VFX Graph, or it vanishes at the screen edge.
- **[rendering-and-budget.md](references/rendering-and-budget.md):** Setting a budget, an effect costs too much, or pooling/tier scaling.

## Steps
1. **Confirm the render pipeline first:** VFX Graph needs a Scriptable Render Pipeline (URP, HDRP) and compute shaders ([tool-choice.md](references/tool-choice.md)).
   - **Built-in pipeline:** has only ParticleSystem.
2. **Choose the tool by what the effect must do:** GPU simulation buys count but makes reading particle state back impractical.
   - **Collisions drive a game rule:** the effect uses ParticleSystem at any scale.
3. **Check VFX Graph support on the weakest target tier before committing to a graph:**
   - **On mobile:** VFX Graph is preview, excludes OpenGL ES and needs compute plus `SystemInfo.maxComputeBufferInputsVertex > 0`.
   - **Tier without support:** renders nothing, not a degraded effect.
   - **Broad Android:** defaults to ParticleSystem.
   - **Second authored version for a tier without support:** a legitimate outcome; decide it up front.
4. **ParticleSystem: set Simulation Space first:** Local follows the emitter, World stays behind ([particle-system-modules.md](references/particle-system-modules.md)).
   - **Complaints:** most attached/detached complaints are this setting.
5. **Treat Max Particles as a visible cliff:** at the cap emission stops, which reads as the effect cutting out.
6. **VFX Graph Capacity and bounds:** per [vfx-graph-contexts.md](references/vfx-graph-contexts.md).
   - **Capacity:** size it to the real peak, because it pre-allocates GPU memory.
   - **Bounds:** set them to cover where particles travel, because default bounds cull the effect when its origin leaves the frustum.
7. **Budget in overdraw (screen coverage × layers), not particle count:** pick the cheapest blend/sort that reads correctly ([rendering-and-budget.md](references/rendering-and-budget.md)).
8. **Pool every repeatedly triggered effect and clear it on release:** per `csharp-standards` → `performance-and-algorithms.md`.
   - **Per use:** never `Instantiate`/`Destroy`.
   - **Looping emitters:** cap every one.
9. **Scale by tier by removing whole sub-effects:** not by thinning every emitter.
10. **Watch it play in-engine on the target tier against the real background:** measure before claiming a saving (`unity-profiler-diagnostics`).
11. **Gameplay hand-off:** hand gameplay the collision signal, never the decision.

## Never
- **Assume an additive effect glows:** that is bloom (`unity-post-processing`).
- **Enable per-particle sorting by default:** additive does not need it and it is paid every frame.

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
```

## Example
- **"Flamethrower that sets enemies on fire where flames touch them":** ParticleSystem despite the count, because it must report contact.
  - **Setup:** World space, collision messages on.
  - **Callback:** handed to the Client layer, which asks Core whether it is a burn.
  - **Collision quality:** set deliberately (High tests every particle against real colliders).
