# VFX Graph: contexts, capacity, events, bounds

Sources: [VFX Graph manual](https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@17.6/manual/index.html), [VisualEffect API](https://docs.unity3d.com/ScriptReference/VFX.VisualEffect.html).

## Contexts (frequency decides placement)
| Context | Runs | Holds |
|---|---|---|
| Spawn | Per spawn decision, CPU | Rate, bursts, gating conditions; the only context deciding whether particles appear |
| Initialize | Once per particle at birth | Start position/velocity/size/color/lifetime; carries **Capacity** |
| Update | Every frame per living particle | Forces, drag, collision, attribute changes; most expensive, so move anything constant into Initialize |
| Output | Every frame per rendered particle | Render type, material, blend, sorting, orientation; where fill-rate is paid |

## Capacity, bounds, space
- **Capacity** (on Initialize) pre-allocates GPU memory for that many particles whether or not they spawn: size it to the real peak.
- **Bounds** drive frustum culling. Default bounds sized to the emitter cull the effect when that point leaves the frustum while particles are still visible (looks like a rendering bug). Recorded bounds capture an authored playthrough; manual bounds are set by hand. Inheriting the default for a travelling world-space effect is a mistake.
- Space is local or world per context, not per asset.

## Driving it from script
- Exposed graph properties are settable from script without editing the asset.
- `SetFloat`/`SetVector3`/`SetTexture`: use the `int` id overloads per frame; string overloads hash the name each call (`csharp-standards` → `performance-and-algorithms.md`).
- `HasFloat`/`HasVector3` before writing: a misspelled name is a silent no-op.
- `SendEvent` fires a named event context (a one-shot burst) instead of toggling the component.
- `Play`/`Stop`/`pause`/`playRate` (slow motion without touching global time). `Reinit()` resets a pooled instance on release. `aliveParticleCount` confirms the budget.

## Composition
- GPU Events: one system spawns another from particle deaths/collisions on the GPU (scalable Sub Emitters).
- Subgraphs: reusable fragments shared as assets.
- Output types: quad, mesh, particle strip, decal, point. Strips (trails, beams) take their particle count per strip, not in total.
- Custom HLSL blocks are the extension point; the kernel is `compute-shader-vfx`'s, the output shader `shader-authoring`'s.
