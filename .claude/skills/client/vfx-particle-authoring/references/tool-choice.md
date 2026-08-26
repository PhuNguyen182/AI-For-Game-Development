# Choosing Between VFX Graph and the Built-in Particle System

Sources: [Particle Systems](https://docs.unity3d.com/Manual/ParticleSystems.html), [Visual Effect Graph manual](https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@17.6/manual/index.html), [ParticleSystem API](https://docs.unity3d.com/ScriptReference/ParticleSystem.html).
Covers: SKILL.md §4 — **"Choose the tool by what the effect must do, not by how big it is"**, **"Verify compute shader support on the weakest target tier before committing to a graph"**.

The two systems differ in where simulation happens, and every other
difference follows from that. GPU simulation is what gives VFX Graph its
particle counts, and it is the same fact that makes a particle's state
expensive for the CPU to read — so the deciding question is usually not "how
many particles" but "does anything outside the effect need to know what a
particle did".

| Capability | Built-in Particle System | VFX Graph | Source |
|---|---|---|---|
| Where simulation runs | CPU, on the main thread or jobs | GPU, in compute shaders | [Visual Effect Graph manual](https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@17.6/manual/index.html) |
| Practical particle count | Thousands before CPU cost dominates | Orders of magnitude more, bounded by fill rate rather than simulation | [Visual Effect Graph manual](https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@17.6/manual/index.html) |
| Hard requirement | None — runs on every platform Unity targets | Compute shader support **and** a Scriptable Render Pipeline. A device missing either renders nothing, not a simplified version | [Visual Effect Graph manual](https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@17.6/manual/index.html) |
| Reading particle state from script | `GetParticles` fills a `Particle[]` the CPU can inspect and write back | Impractical — the data lives in GPU buffers, and pulling it back stalls the pipeline | [ParticleSystem.GetParticles](https://docs.unity3d.com/ScriptReference/ParticleSystem.GetParticles.html) |
| Collision reported to gameplay | `OnParticleCollision` and `OnParticleTrigger` deliver callbacks to a `MonoBehaviour` | Collision is simulated on the GPU with no script callback — the effect can react, gameplay cannot | [ParticleSystem API](https://docs.unity3d.com/ScriptReference/ParticleSystem.html) |
| Spawning from another effect's particles | Sub Emitters, evaluated on the CPU | GPU Events, entirely on the GPU and far cheaper at scale | [Visual Effect Graph manual](https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@17.6/manual/index.html) |
| Authoring model | A fixed stack of toggleable modules on one component | A node graph of contexts and blocks, extensible with custom operators | [Visual Effect Graph manual](https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@17.6/manual/index.html) |
| Reuse of authored behaviour | Prefab variants and duplicated systems | Subgraphs, shared across effects as assets | [Visual Effect Graph manual](https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@17.6/manual/index.html) |

## Deciding

| If the effect | Then | Source |
|---|---|---|
| Must tell gameplay what it touched | Built-in system, at any scale — the callback does not exist on the other side | [ParticleSystem API](https://docs.unity3d.com/ScriptReference/ParticleSystem.html) |
| Ships to a tier without compute support | Built-in system for that tier, which means either a second authored version or one tool for both | [Visual Effect Graph manual](https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@17.6/manual/index.html) |
| Is a small, one-shot impact or ambience | Built-in system — a graph's fixed setup cost is not repaid by a few dozen particles | [Particle Systems](https://docs.unity3d.com/Manual/ParticleSystems.html) |
| Is purely visual and genuinely dense | VFX Graph, where the count is affordable and the authoring model scales | [Visual Effect Graph manual](https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@17.6/manual/index.html) |
| Needs a custom simulation step | VFX Graph with a custom kernel from `compute-shader-vfx` — the built-in system has no equivalent extension point | [Visual Effect Graph manual](https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@17.6/manual/index.html) |

Authoring the same effect twice for two tiers is a real cost and a legitimate
outcome; deciding it up front is cheaper than discovering it when the low-tier
build ships with nothing on screen.
