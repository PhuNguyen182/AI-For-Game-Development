# VFX Graph vs ParticleSystem

Sources: [Particle Systems](https://docs.unity3d.com/Manual/ParticleSystems.html), [VFX Graph manual](https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@17.6/manual/index.html) (`vfxm`), [ParticleSystem API](https://docs.unity3d.com/ScriptReference/ParticleSystem.html).

## Availability
| Pipeline | ParticleSystem | VFX Graph |
|---|---|---|
| Built-in | Yes | No (SRP only) |
| URP | Yes | Desktop/console yes. Mobile: still preview, no OpenGL ES, needs compute and vertex-stage SSBOs (`SystemInfo.maxComputeBufferInputsVertex > 0`) |
| HDRP | Yes | Yes, fullest output feature set |

Pipeline choice belongs to `render-pipeline-urp-hdrp`; this table is an input to it.

## Differences
| Capability | ParticleSystem | VFX Graph |
|---|---|---|
| Simulation | CPU (main thread or jobs) | GPU compute |
| Practical count | Thousands before CPU dominates | Orders of magnitude more, bounded by fill rate |
| Hard requirement | None | Compute support and an SRP; a device missing either renders nothing |
| Read state from script | `GetParticles` fills a `Particle[]` | Impractical: GPU buffers, readback stalls |
| Collision to gameplay | `OnParticleCollision`, `OnParticleTrigger` | GPU collision only, no script callback |
| Spawn from other particles | Sub Emitters (CPU) | GPU Events (far cheaper at scale) |
| Authoring | Fixed module stack on one component | Node graph of contexts/blocks, custom operators |
| Reuse | Prefab variants | Subgraphs |

## Deciding
| If the effect | Then |
|---|---|
| Must tell gameplay what it touched | ParticleSystem at any scale |
| Ships to a tier without compute | ParticleSystem for that tier (a second authored version, or one tool for both) |
| Is a small one-shot or ambience | ParticleSystem: a graph's setup cost is not repaid by a few dozen particles |
| Is purely visual and dense | VFX Graph |
| Needs a custom simulation step | VFX Graph with a kernel from `compute-shader-vfx` (no built-in equivalent) |
