---
name: vfx-particle-authoring
description: >
  Technique for particle visual effects in Unity: choosing between VFX Graph
  and the built-in Particle System, VFX Graph's Spawn, Initialize, Update and
  Output contexts with capacity, exposed properties, events and bounds, the
  Particle System's Main, Emission, Shape, Noise, Sub Emitters, Collision,
  Trails and Renderer modules, simulation space, blend and sort mode, overdraw
  budget, per-tier scaling, and pooling. Use for any ability, impact, ambience
  or trail effect built from particles. Not for: the shader an output stage
  renders with (`shader-authoring`); custom simulation kernels
  (`compute-shader-vfx`); pipeline choice (`render-pipeline-urp-hdrp`); the
  bloom that makes an effect glow (`unity-post-processing`).
---

# VFX and Particle Authoring — VFX Graph and the Built-in Particle System

## Bundled resources

### References
Read-only context, loaded on demand so SKILL.md itself stays short.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Manual and package roots, the version pin, and which pipelines each tool runs on | Starting any task here, or confirming a tool is available at all |
| [tool-choice.md](references/tool-choice.md) | What each tool can and cannot do — pipeline support, particle counts, CPU readback, collision callbacks | Deciding between the two, or an effect needs to talk back to gameplay |
| [particle-system-modules.md](references/particle-system-modules.md) | Main, Emission, Shape, Noise, Sub Emitters, Texture Sheet, Collision, Trails, Renderer, and scripting the modules | Building or fixing a built-in Particle System effect |
| [vfx-graph-contexts.md](references/vfx-graph-contexts.md) | Contexts, capacity, attributes, events, GPU events, exposed properties, bounds | Building a VFX Graph, or one disappears at the edge of the screen |
| [rendering-and-budget.md](references/rendering-and-budget.md) | Blend modes, sorting, overdraw, per-tier scaling, pooling, lifecycle | Setting a budget, or the effect looks right and costs too much |

## 1. Objective
Build particle effects that read correctly in motion, stay inside an agreed budget on the weakest target device, and clean up after themselves. The two failures worth designing against are structural rather than artistic: an effect whose cost is overdraw rather than particle count, so reducing the count changes nothing; and an emitter or pooled instance with no defined end, which is the particle-shaped version of the project's unbounded-growth rule.

## 2. Role
Act as the VFX author: pick the tool against the platform and the gameplay contract, build the graph or the module stack, set the budget, and own the effect's lifecycle. You do not write the shader the output stage renders with, the compute kernel behind a custom simulation step, or the post-processing that makes an emissive effect glow.

## 3. When to invoke this skill
- Building an ability cast, impact, muzzle flash, trail, weather, or ambient particle effect.
- Choosing between VFX Graph and the built-in Particle System for a given effect and platform tier.
- An effect is visually finished and too expensive, or behaves differently in a build than in the editor.
- An effect disappears, clips, or sorts incorrectly against other transparents.
- Defining a particle budget and how it scales down across quality tiers.
- Pooling repeatedly triggered effects and getting their stop-and-restart behaviour right.
- Negative trigger: the shader an output context or particle renderer uses — that is `shader-authoring`; build it there and wire it in here.
- Negative trigger: a custom HLSL or compute simulation step inside a graph — that is `compute-shader-vfx`; this skill consumes the kernel it produces.
- Negative trigger: which render pipeline the project targets — that is `render-pipeline-urp-hdrp`, whose answer decides whether VFX Graph is available at all.
- Negative trigger: the bloom or colour grading that makes an emissive effect read as glowing — that is `unity-post-processing`; an additive particle in a scene with no bloom is a different-looking effect.
- Negative trigger: a gameplay rule triggered by particle collision — damage, status application, hit confirmation — that decision lives in `Game.Core.*` per `coding-principles.md`; this skill delivers the collision signal.

## 4. How to use this skill
1. **Confirm the render pipeline before choosing the tool**, per [root-links.md](references/root-links.md) — VFX Graph runs on the Scriptable Render Pipelines and not on the Built-in one, so on a Built-in project the choice has already been made regardless of what the effect needs.
2. **Choose the tool by what the effect must do, not by how big it is**, per [tool-choice.md](references/tool-choice.md) — VFX Graph simulates on the GPU, which is what buys the particle count and what makes reading a particle's state back to gameplay impractical. An effect whose collisions must drive a game rule belongs on the built-in system, whatever its scale.
3. **Verify compute shader support on the weakest target tier before committing to a graph** — VFX Graph requires it, and a tier without it does not render a degraded version of the effect, it renders nothing.
4. **Set Simulation Space deliberately, first**, per [particle-system-modules.md](references/particle-system-modules.md) — Local makes particles follow the emitter, World leaves them behind it, and almost every "the trail moves with the gun" or "the muzzle flash detaches" report is this one setting rather than anything in the emission curve.
5. **Treat Max Particles as a visible cliff, not a safety net** — when the cap is reached, emission simply stops, which reads as the effect cutting out mid-play rather than as a limit being enforced.
6. **Size VFX Graph Capacity to what will exist, not to a comfortable ceiling**, per [vfx-graph-contexts.md](references/vfx-graph-contexts.md) — capacity pre-allocates GPU memory for that many particles whether or not they are ever spawned, so an over-large value is paid in full from the moment the effect loads.
7. **Set the graph's bounds to cover where particles actually travel** — bounds drive culling, so an effect with default bounds and long-lived world-space particles vanishes as soon as its origin leaves the frustum, which reads as a rendering bug.
8. **Budget in overdraw, not in particle count**, per [rendering-and-budget.md](references/rendering-and-budget.md) — a few dozen large transparent quads covering the screen cost more than thousands of small ones, so the number to agree with the Tech Spec is screen coverage and layer count, and reducing particle count alone often changes nothing.
9. **Pick the cheapest blend and sort combination that reads correctly** — additive needs no sorting between its own particles because addition commutes, while alpha blending does, so a smoke effect and a spark effect have genuinely different costs at the same count.
10. **Pool every repeatedly triggered effect, and clear it on release** — per the pooling rule in `performance-and-algorithms.md`, and because a pooled system restarted without clearing replays with the previous instance's particles still alive.
11. **Scale by tier by removing whole sub-effects, not by thinning every emitter** — halving every count everywhere degrades the read of all of them, where dropping secondary sparks and detail smoke keeps the primary effect intact.
12. **Watch the effect play in-engine before calling it done** — a graph that reads correctly in the node editor can still be wrong in motion, at speed, or against the scene's actual background.
13. **Hand the collision signal to gameplay, never the decision** — a particle collision callback reports that something was hit; whether that is damage is a `Game.Core.*` rule per `coding-principles.md`'s Shared Core integrity rule.

## 5. Specific goals / tasks this skill performs
- Tool selection between VFX Graph and the built-in Particle System against pipeline, platform tier, and gameplay contract.
- VFX Graph authoring: context structure, capacity, attributes, exposed properties, events and GPU events, bounds.
- Built-in Particle System authoring: module stack, simulation space, emission shaping, noise, sub emitters, trails, collision.
- Blend and sort mode selection, and overdraw-based budgeting with per-tier scaling.
- Pooling and lifecycle for repeatedly triggered effects.
- Out of scope: the output shader (`shader-authoring`); custom simulation kernels (`compute-shader-vfx`); pipeline choice (`render-pipeline-urp-hdrp`); the bloom an emissive effect relies on (`unity-post-processing`); the gameplay rule behind a collision (`csharp-engineer`).

## 6. Output format
```
## VFX — <effect name>
- Pipeline confirmed: <Built-in / URP / HDRP> — and whether VFX Graph is available at all
- Tool: <VFX Graph / built-in Particle System> — and the constraint that decided it
- Structure: <contexts, or the module stack — one line each>
- Simulation space: <Local / World> — and why
- Capacity or Max Particles: <value> — and what happens when it is reached
- Bounds: <how set, and the travel they cover> — VFX Graph only
- Blend and sort: <mode, sorting on or off> — and the read it serves
- Overdraw budget: <screen coverage and layer count agreed, and with whom>
- Tier scaling: <what is removed at each tier, rather than what is thinned>
- Pooling: <pool source, and the stop-and-clear behaviour on release>
- Gameplay signal: <collision or event handed to the Client layer — or "purely visual">
- Verified: <in-engine capture, on which tier and against which background>
- Layer: <Game.Client.* assets and prefabs>
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what the delivered effect does not cover>
- Latent concerns: <failure modes not yet triggered: assumptions that hold only under current conditions, thresholds not yet reached, trade-offs knowingly deferred>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: "Big explosion for the ultimate ability — make it feel enormous."
- Output: VFX Graph on the PC tier, since the project's URP setup supports it and the effect is purely visual with no gameplay readback. Capacity set to the burst's actual peak rather than a round number, because capacity is allocated up front. Bounds set manually to cover the debris travel, which default bounds would have clipped the moment the camera turned. Additive output with sorting off, since additive composites order-independently and the sort would have been pure cost. The scale came from screen coverage and a bright emissive core relying on the scene's existing bloom — which belongs to `unity-post-processing`, and was confirmed present rather than assumed, since without it the effect reads as flat white.

**Example 2**
- Input: "Flamethrower that sets enemies on fire where the flames touch them."
- Output: built-in Particle System despite the count, because the effect has to tell gameplay what it hit and GPU-simulated particles cannot report that back affordably. World simulation space so flames trail behind a turning player, World collision with collision messages enabled, and the callback handed to the Client layer — which asks `Game.Core.*` whether that constitutes a burn, rather than applying one. Collision quality set deliberately rather than left at the default, since the high setting tests every particle against real colliders and was the dominant cost here.

**Example 3**
- Input: "The hit effect plays wrong the second time an enemy is hit."
- Output: a pooled system restarted without clearing — the previous instance's particles were still alive, so the second play looked denser and mistimed. Fixed on release rather than on spawn, so a pooled instance is always returned clean, and confirmed the emitter's own stop behaviour distinguished stopping emission from clearing what was already emitted.

## 8. Edge cases & guardrails
- Never plan a VFX Graph effect before confirming the pipeline and the weakest tier's compute support — the failure is total, not degraded.
- Never choose VFX Graph for an effect gameplay must read particle state from — GPU simulation makes that readback impractical.
- Never leave Simulation Space unexamined — it is the cause of most attached-or-detached motion complaints.
- Never treat Max Particles as a safety cap — reaching it stops emission visibly.
- Never set VFX Graph Capacity generously — it allocates GPU memory whether the particles exist or not.
- Never ship a VFX Graph with default bounds and long-travelling particles — it will cull itself out of frame.
- Never budget in particle count alone — overdraw is what costs, and count is a poor proxy for it.
- Never enable per-particle sorting by default — additive does not need it, and it is paid every frame it is on.
- Never `Instantiate` and `Destroy` a triggered effect per use — pool it, and clear it on release.
- Never scale a tier down by thinning every emitter equally — remove secondary effects and keep the primary read intact.
- Never leave a looping emitter without a lifetime or rate cap.
- Never assume an additive effect will glow — that is bloom, and it belongs to `unity-post-processing`.
- Never let a particle collision callback decide a gameplay outcome — it reports the contact, `Game.Core.*` rules on it.
