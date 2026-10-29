# Rendering cost, budget, lifecycle

Sources: [Component reference](https://docs.unity3d.com/Manual/class-ParticleSystem.html), [ParticleSystemRenderer](https://docs.unity3d.com/ScriptReference/ParticleSystemRenderer.html), [ObjectPool](https://docs.unity3d.com/ScriptReference/Pool.ObjectPool_1.html).

## Where the cost is
Transparent particles do not occlude each other, so cost scales with covered pixels × layers, not particle count. Forty large smoke quads can cost more than a thousand sparks; halving count may change nothing measurable.
- Particle size near the camera: one screen-filling particle costs a full screen of shading; clamp with Min/Max Particle Size (viewport units).
- Tile-based mobile GPUs: layered blending is the classic mobile failure and does not show on a desktop test.
- Per-particle shader cost multiplies by every covered pixel (`shader-authoring`).

## Blend and sort
| Choice | Note |
|---|---|
| Additive | Order-independent (addition commutes): no sorting between its own particles. Cheap for sparks, energy, fire; cannot go darker than the background |
| Alpha blend | Order-dependent, needs sorting; smoke and dust cost more than their count suggests |
| Premultiplied alpha | One material can carry additive highlights and alpha body (avoids two systems) |
| Per-particle sorting | Per-frame cost whether or not particles overlap: enable only when overlap is visible and wrong |
| Sorting vs other transparents | Whole-system depth bias (Sorting Fudge), not per particle |
| Soft particles | Fades at geometry intersections; needs the depth texture (`unity-urp-rendering`) |

## Scaling across tiers
- Remove secondary systems: the primary keeps silhouette and timing.
- Thinning every emitter equally makes the effect read as broken: tempting and worse.
- Reduce size before count: cuts overdraw directly and keeps density.
- Distance: distant effects can drop sub-systems and shadows.

## Lifecycle
- Pool anything triggered repeatedly; prefer built-in `ObjectPool<T>` over a hand-rolled pool (`csharp-standards` → `performance-and-algorithms.md`).
- Clear on release, not on take: ParticleSystem `Clear()`, VFX Graph `Reinit()`. Every take is then known-clean.
- Release on liveness (`IsAlive()`), not a hand-kept duration constant that drifts on retuning.
- Cap looping emitters by rate or lifetime; the cap is the release point.
- Measure before claiming a saving: Profiler or Frame Debugger capture (`unity-profiler-diagnostics`).
