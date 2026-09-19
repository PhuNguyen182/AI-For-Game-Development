# Rendering Cost, Budget, and Lifecycle

Sources: [Particle System component reference](https://docs.unity3d.com/Manual/class-ParticleSystem.html), [ParticleSystemRenderer](https://docs.unity3d.com/ScriptReference/ParticleSystemRenderer.html), [ObjectPool](https://docs.unity3d.com/ScriptReference/Pool.ObjectPool_1.html).
Covers: SKILL.md §4 — **"Budget in overdraw, not in particle count"**, **"Pick the cheapest blend and sort combination that reads correctly"**, **"Pool every repeatedly triggered effect, and clear it on release"**, **"Scale by tier by removing whole sub-effects, not by thinning every emitter"**.

Particle cost is overwhelmingly fill rate. Every particle is a transparent
surface the GPU shades once per covered pixel, and transparent surfaces do not
occlude each other, so cost scales with **covered pixels times layers**, not
with particle count. That is why a smoke puff of forty large quads can cost
more than a thousand sparks, and why halving a particle count sometimes
changes nothing measurable.

## Where the cost is

| Factor | Why it dominates | Source |
|---|---|---|
| Overdraw | Transparent particles are all drawn, all shaded, none culled by each other. Screen coverage multiplied by layer depth is the real budget number | [Particle System component](https://docs.unity3d.com/Manual/class-ParticleSystem.html) |
| Particle size near the camera | One particle filling the screen costs a full screen of shading. Min and Max Particle Size clamp this in viewport terms, which is the only unit that makes the cost bounded | [ParticleSystemRenderer](https://docs.unity3d.com/ScriptReference/ParticleSystemRenderer.html) |
| Tile-based mobile GPUs | Blending reads and writes tile memory repeatedly; heavy layered transparency is the classic mobile particle failure, and it does not appear on a desktop test | [Particle System component](https://docs.unity3d.com/Manual/class-ParticleSystem.html) |
| Shader complexity per particle | Multiplied by every covered pixel, so a slightly heavier particle shader is a large change — the shader itself belongs to `shader-authoring` | [ParticleSystemRenderer](https://docs.unity3d.com/ScriptReference/ParticleSystemRenderer.html) |

## Blend and sort

| Choice | What it buys and costs | Source |
|---|---|---|
| Additive | Order-independent, because addition commutes — so **no sorting is needed between its own particles**. The cheap choice for sparks, energy, and fire, and it cannot render anything darker than its background | [Particle System component](https://docs.unity3d.com/Manual/class-ParticleSystem.html) |
| Alpha blend | Order-dependent, so overlapping particles need sorting to composite correctly. The choice for smoke and dust, and the reason those effects cost more than their count suggests | [Particle System component](https://docs.unity3d.com/Manual/class-ParticleSystem.html) |
| Premultiplied alpha | Lets one material carry both additive highlights and alpha-blended body, which avoids running two systems for one visual | [Particle System component](https://docs.unity3d.com/Manual/class-ParticleSystem.html) |
| Per-particle sorting | Real per-frame cost, paid whether or not any particles actually overlap. Enable it when overlap is visible and wrong, not preemptively | [ParticleSystemRenderer](https://docs.unity3d.com/ScriptReference/ParticleSystemRenderer.html) |
| Sorting against other transparents | A whole-system depth bias, not a per-particle concern — the lever for an effect drawing behind something it should cover | [ParticleSystemRenderer](https://docs.unity3d.com/ScriptReference/ParticleSystemRenderer.html) |
| Soft particles | Fade where particles intersect geometry, removing hard intersection lines. Requires the depth texture, which is a pipeline setting owned by `unity-urp-rendering` | [Particle System component](https://docs.unity3d.com/Manual/class-ParticleSystem.html) |

## Scaling across tiers

| Approach | Result | Source |
|---|---|---|
| Remove secondary systems | The primary effect keeps its silhouette and timing; the tier loses detail it was never reading closely | [Particle Systems](https://docs.unity3d.com/Manual/ParticleSystems.html) |
| Thin every emitter equally | Every part of the effect degrades at once, so the effect reads as broken rather than simplified — the more tempting option and the worse one | [Particle Systems](https://docs.unity3d.com/Manual/ParticleSystems.html) |
| Reduce size before count | Directly cuts overdraw, which is where the cost is, and preserves the effect's density | [ParticleSystemRenderer](https://docs.unity3d.com/ScriptReference/ParticleSystemRenderer.html) |
| Distance-based simplification | Distant effects can drop sub-systems and shadows entirely, since detail there is not resolvable | [Particle Systems](https://docs.unity3d.com/Manual/ParticleSystems.html) |

## Lifecycle

| Rule | Why | Source |
|---|---|---|
| Pool anything triggered repeatedly | Instantiate and Destroy per hit, per shot, or per footstep is the exact case `performance-and-algorithms.md` requires pooling for. `ObjectPool<T>` is the built-in implementation to prefer over a hand-rolled one | [ObjectPool](https://docs.unity3d.com/ScriptReference/Pool.ObjectPool_1.html) |
| Clear on release, not on take | A pooled effect released dirty replays with the previous use's particles alive. Cleaning on release means every take is known-clean | [ParticleSystem.Clear](https://docs.unity3d.com/ScriptReference/ParticleSystem.Clear.html) |
| Release on liveness, not on a timer | A duration constant kept in step with the effect by hand drifts the moment the effect is retuned | [ParticleSystem.IsAlive](https://docs.unity3d.com/ScriptReference/ParticleSystem.IsAlive.html) |
| Cap looping emitters | A loop with no rate or lifetime bound is unbounded growth in the sense `performance-and-algorithms.md` names — the cap is the release point | [Particle System component](https://docs.unity3d.com/Manual/class-ParticleSystem.html) |
| Measure before claiming a saving | A particle optimisation claim needs a Profiler or frame-debugger capture, per that file's Verification section — especially here, where the intuitive lever is often the wrong one | [Particle Systems](https://docs.unity3d.com/Manual/ParticleSystems.html) |
