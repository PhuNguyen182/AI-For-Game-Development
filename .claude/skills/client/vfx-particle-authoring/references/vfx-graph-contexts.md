# VFX Graph — Contexts, Capacity, Events, and Bounds

Sources: [Visual Effect Graph manual](https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@17.6/manual/index.html), [VisualEffect API](https://docs.unity3d.com/ScriptReference/VFX.VisualEffect.html), [VisualEffectAsset](https://docs.unity3d.com/ScriptReference/VFX.VisualEffectAsset.html).
Covers: SKILL.md §4 — **"Size VFX Graph Capacity to what will exist, not to a comfortable ceiling"**, **"Set the graph's bounds to cover where particles actually travel"**.

A graph is a chain of contexts, each running at a different frequency: Spawn
once per spawn decision, Initialize once per particle at birth, Update every
frame per particle, Output every frame per rendered particle. Putting work in
the wrong context is not a style question — it is the difference between
evaluating something once and evaluating it a million times a frame.

## Contexts

| Context | Runs when, and what belongs in it | Source |
|---|---|---|
| Spawn | Per spawn decision, on the CPU. Rate, bursts, and the conditions that gate them. Cheap, and the only context that decides *whether* particles appear | [VFX Graph manual](https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@17.6/manual/index.html) |
| Initialize | Once per particle at birth. Starting position, velocity, size, colour, lifetime — anything constant for that particle's life. Carries the system's **Capacity** | [VFX Graph manual](https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@17.6/manual/index.html) |
| Update | Every frame, per living particle. Forces, drag, collision, attribute changes over life. The most expensive context by construction, so work that could sit in Initialize should | [VFX Graph manual](https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@17.6/manual/index.html) |
| Output | Every frame, per rendered particle. Render type, material, blend, sorting, orientation — and where fill-rate cost is actually paid | [VFX Graph manual](https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@17.6/manual/index.html) |

## Capacity and bounds

| Setting | What it decides | Source |
|---|---|---|
| Capacity | The maximum living particles for that system, set on Initialize. It **pre-allocates GPU memory for that count** regardless of how many ever spawn, so a generous value is paid in full from load. Size it to the peak the effect actually reaches | [VFX Graph manual](https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@17.6/manual/index.html) |
| Bounds | The volume used for frustum culling. Default bounds sized to the emitter cull the effect as soon as that point leaves the frustum, even while its particles are still on screen — which reads as a rendering bug rather than a culling setting | [VFX Graph manual](https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@17.6/manual/index.html) |
| Bounds mode | Recorded bounds capture what an authored playthrough actually used; manual bounds are set by hand. Either is a decision — inheriting the default for a world-space effect that travels is not | [VFX Graph manual](https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@17.6/manual/index.html) |
| Space | Each system is local or world space, chosen per context rather than for the whole asset — the same distinction the built-in system makes once, made repeatedly here | [VFX Graph manual](https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@17.6/manual/index.html) |

## Communicating with the effect

| Member | What it is for | Source |
|---|---|---|
| Exposed properties | Graph properties marked exposed become settable from script — the supported way to drive an effect from gameplay without editing the asset | [VisualEffect](https://docs.unity3d.com/ScriptReference/VFX.VisualEffect.html) |
| `SetFloat`, `SetVector3`, `SetTexture` | Write those properties. Overloads taking an `int` id are the per-frame form; the string overloads hash the name on every call, exactly as with Animator parameters, per `performance-and-algorithms.md` | [VisualEffect](https://docs.unity3d.com/ScriptReference/VFX.VisualEffect.html) |
| `HasFloat`, `HasVector3` | Check a property exists before writing it — a misspelled name is otherwise a silent no-op | [VisualEffect](https://docs.unity3d.com/ScriptReference/VFX.VisualEffect.html) |
| `SendEvent` | Triggers a named event context, which is how a one-shot burst is fired rather than by toggling the component | [VisualEffect](https://docs.unity3d.com/ScriptReference/VFX.VisualEffect.html) |
| `Play` / `Stop` / `pause` / `playRate` | Playback control, including slow motion through `playRate` without touching global time | [VisualEffect](https://docs.unity3d.com/ScriptReference/VFX.VisualEffect.html) |
| `Reinit()` | Resets the effect to its initial state — the clean-slate call a pooled instance needs on release, equivalent to clearing a built-in system | [VisualEffect](https://docs.unity3d.com/ScriptReference/VFX.VisualEffect.html) |
| `aliveParticleCount` | The live count, for confirming an effect stays inside its budget rather than assuming it does | [VisualEffect](https://docs.unity3d.com/ScriptReference/VFX.VisualEffect.html) |

## Composition

| Feature | What it enables | Source |
|---|---|---|
| GPU Events | One system spawns another from its own particles' deaths or collisions, entirely on the GPU. The scalable counterpart of Sub Emitters, with no CPU involvement per particle | [VFX Graph manual](https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@17.6/manual/index.html) |
| Subgraphs | Reusable graph fragments shared across effects as assets — the unit of reuse, in place of duplicating systems | [VFX Graph manual](https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@17.6/manual/index.html) |
| Output types | Quad, mesh, particle strip, decal, and point. Strips are what trails and beams are built from and need their particle count expressed per strip, not in total | [VFX Graph manual](https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@17.6/manual/index.html) |
| Custom HLSL blocks | The extension point for behaviour the built-in blocks cannot express — the kernel itself belongs to `compute-shader-vfx`, and the shader an output renders with to `shader-authoring` | [VFX Graph manual](https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@17.6/manual/index.html) |
