---
name: vfx-particle-authoring
description: >
  Technique for building particle-based visual effects with Unity's VFX
  Graph (GPU, high particle counts, complex per-particle behavior) and the
  built-in Particle System / Shuriken (CPU, simpler effects, universal
  platform support) — including which tool to choose per case, budget
  discipline, and pooling. Use this for ability casts, impacts, environmental
  ambience, trails, and any particle-driven effect. Do not use this for the
  shader a particle output stage renders with — that's `shader-authoring`. Do
  not use this for the compute kernel behind a VFX Graph's custom simulation
  step — that's `compute-shader-vfx`.
---

# VFX & Particle System Authoring

## 1. Objective
Build particle effects that read correctly to the player, stay inside an agreed performance budget on every target platform, and don't leak GameObjects or run unbounded — rather than a visually-correct effect that quietly tanks framerate or spawns without limit.

## 2. Role
Act as a VFX/particle engineer choosing the right tool (VFX Graph vs Shuriken) per effect, and owning the graph structure, budget, and lifecycle of the particle systems you build.

## 3. When to invoke this skill
- Any ability-cast, impact, environmental (weather, ambience), or trail effect built from particles.
- Deciding between VFX Graph and the legacy Particle System (Shuriken) for a given effect.
- Negative trigger: the shader a particle Output context renders with — build that under `shader-authoring`, then wire it in here.
- Negative trigger: a custom GPU simulation kernel behind a VFX Graph "Custom HLSL"/compute step — build that under `compute-shader-vfx` first.

## 4. How to use this skill
1. **Choose the tool deliberately, don't default blindly**:
   - **VFX Graph** — GPU-simulated, for high particle counts (thousands+) and complex per-particle behavior (forces, collision, GPU events). Requires compute shader support — verify the project's actual minimum-spec platform supports it before committing; if it doesn't (some low-end/older mobile hardware), fall back to Shuriken for that platform tier.
   - **Particle System (Shuriken)** — CPU-simulated, lower particle-count ceiling, but universally supported. Correct default for simpler effects and for any platform where compute shader support is a blocker.
2. **Structure a VFX Graph by context, one job per context**: Spawn (rate/burst timing) → Initialize (birth properties: position, velocity, size, color) → Update (per-frame forces/behavior) → Output (render as quad/mesh/particle strip). Don't cram Update-stage logic into Initialize or vice versa — same single-responsibility reasoning applied to graph contexts.
3. **Choose blend/sort mode deliberately, not by default**: Additive for glow/energy/magic, Alpha Blend for smoke/dust, Premultiplied Alpha for correctly composited soft edges. Enable per-particle sorting only when actual visual overlap requires it — sorting has a real per-particle cost every frame it's on.
4. **Set an explicit particle/system budget** with the Tech Spec or GD: max simultaneous particles, max concurrently active systems, and how that scales down on lower quality tiers. An emitter with no cap is the VFX-specific case of the project's "no unbounded growth" memory rule — cap spawn rate/lifetime, don't let it run away.
5. **Pool triggered VFX.** Any `ParticleSystem`/`VisualEffect` GameObject spawned repeatedly (hit effects, projectile trails, muzzle flashes) must come from a pool, not `Instantiate`/`Destroy` per trigger, per the project's pooling rule.
6. **Scale by platform/quality tier**: reduce particle count, disable secondary/detail sub-systems, or drop to a cheaper Shuriken variant at lower quality settings or at distance, rather than shipping one fixed-density effect across every target.
7. **Use texture sheet animation (flipbooks)** for per-particle visual detail instead of adding extra geometry or sub-emitters where a flipbook achieves the same read.
8. **Verify in-engine** — capture a scene view of the effect actually playing (via the Unity MCP scene-capture tools) before declaring it done; a graph that looks right in the node editor can still read wrong in motion.

## 5. Specific goals / tasks this skill performs
- Ability cast/impact VFX, environmental ambience, weather, trails, muzzle flashes, status-effect particles.
- GPU vs CPU particle tool selection per platform constraint.
- Particle budget definition and quality-tier scaling.
- Out of scope: the render shader for a particle output stage (`shader-authoring`) and any custom compute kernel behind the simulation (`compute-shader-vfx`).

## 6. Output format
```
## VFX Implementation — <effect name>
- Tool: VFX Graph / Particle System (Shuriken) — rationale: <...>
- Contexts/modules: <summary of graph structure>
- Blend/sort mode: <mode> — rationale: <...>
- Budget: <max particles>, <max concurrent systems>, scaling plan across quality tiers
- Pooling: <pool source/mechanism, or "one-shot, not pooled" with rationale>
- Platforms verified on: <list>
- Known limitations: <...>
```

## 7. Examples
**Example 1**
- Input: "Implement a compute-shader-driven particle VFX for the new ability" (ultimate-ability explosion).
- Output: VFX Graph, GPU particles, budget of 5,000 particles per cast capped by a burst-count node, Additive blend, verified PC-only per Tech Spec (project's mobile tier doesn't guarantee compute support for this ability).

**Example 2**
- Input: "GD wants a torch flame effect for the mobile build."
- Output: Particle System (Shuriken) chosen specifically for mobile compatibility, ~30 particle cap, Alpha Blend, pooled per torch prefab instance, texture sheet flipbook for flame detail instead of extra sub-emitters.

## 8. Edge cases & guardrails
- Never assume VFX Graph is available on every target platform — confirm compute shader support against the project's actual minimum spec before choosing it.
- Never ship a looping emitter without a spawn-rate or lifetime cap.
- Never `Instantiate`/`Destroy` a triggered VFX GameObject per use — pool it.
- Don't enable sorting or a heavier blend mode by default "just in case" — pick the cheapest mode that reads correctly for the effect.
