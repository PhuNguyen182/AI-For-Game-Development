# The Built-in Particle System — Modules That Decide the Result

Sources: [Particle System component reference](https://docs.unity3d.com/Manual/class-ParticleSystem.html), [ParticleSystem API](https://docs.unity3d.com/ScriptReference/ParticleSystem.html), [ParticleSystemRenderer API](https://docs.unity3d.com/ScriptReference/ParticleSystemRenderer.html).
Covers: SKILL.md §4 — **"Set Simulation Space deliberately, first"**, **"Treat Max Particles as a visible cliff, not a safety net"**.

The module stack is long and most of it is curve authoring. The entries below
are the ones that change what the effect *is* rather than how it looks, plus
the ones whose failure mode is silent.

## Contents

- [Main module](#main-module)
- [Emission and shape](#emission-and-shape)
- [Behaviour modules](#behaviour-modules)
- [Renderer](#renderer)
- [Scripting](#scripting)

## Main module

| Property | What it decides | Source |
|---|---|---|
| Simulation Space | **Local** carries particles with the emitter, **World** leaves them where they were born, **Custom** ties them to another transform. This single setting separates a muzzle flash that stays on the barrel from a smoke trail that stays in the air, and it is the cause of most attached-or-detached motion complaints | [Particle System component](https://docs.unity3d.com/Manual/class-ParticleSystem.html) |
| Max Particles | A hard ceiling. On reaching it the system **stops emitting** until particles die, which looks like the effect cutting out rather than a cap being applied | [Particle System component](https://docs.unity3d.com/Manual/class-ParticleSystem.html) |
| Start Lifetime | Together with emission rate, the actual determinant of how many particles exist at once — the pair that has to be reasoned about, not either alone | [Particle System component](https://docs.unity3d.com/Manual/class-ParticleSystem.html) |
| Scaling Mode | Local, Hierarchy, or Shape — why a particle effect on a scaled prefab sometimes ignores that scale entirely | [Particle System component](https://docs.unity3d.com/Manual/class-ParticleSystem.html) |
| Simulation Speed / Delta Time | Delta Time set to Unscaled is what keeps an effect running while the game is paused, for a pause-menu or hit-stop effect | [Particle System component](https://docs.unity3d.com/Manual/class-ParticleSystem.html) |
| Play On Awake | Fine for ambience, wrong for a pooled one-shot — a pooled instance should be started by whoever took it from the pool | [Particle System component](https://docs.unity3d.com/Manual/class-ParticleSystem.html) |
| Stop Action | What happens when the system finishes — Disable, Destroy, or Callback. Destroy and pooling are mutually exclusive | [Particle System component](https://docs.unity3d.com/Manual/class-ParticleSystem.html) |

## Emission and shape

| Property | What it decides | Source |
|---|---|---|
| Rate over Time | Particles per second — correct for continuous ambience | [Particle System component](https://docs.unity3d.com/Manual/class-ParticleSystem.html) |
| Rate over Distance | Particles per unit travelled, so a trail has the same density whether the emitter crawls or sprints. The correct choice for anything attached to a moving object | [Particle System component](https://docs.unity3d.com/Manual/class-ParticleSystem.html) |
| Bursts | Count, cycles, interval, and probability — a one-shot impact is bursts with the rate at zero, not a rate briefly raised | [Particle System component](https://docs.unity3d.com/Manual/class-ParticleSystem.html) |
| Shape | The emission volume and the initial direction derived from it. Changing the shape changes velocity direction, which is why swapping a Cone for a Sphere alters far more than the spawn positions | [Particle System component](https://docs.unity3d.com/Manual/class-ParticleSystem.html) |
| Arc mode | Random, Loop, Ping-Pong, or Burst Spread around the shape — the difference between scattered emission and a sweeping one | [Particle System component](https://docs.unity3d.com/Manual/class-ParticleSystem.html) |

## Behaviour modules

| Module | What it decides, and what it costs | Source |
|---|---|---|
| Noise | The most effective single module for making motion look organic, and one of the most expensive. Its Quality setting selects one-, two-, or three-dimensional noise — a real cost difference, not a polish slider | [Particle System component](https://docs.unity3d.com/Manual/class-ParticleSystem.html) |
| Sub Emitters | Spawns another system on Birth, Collision, Death, or Trigger. Each sub emitter is a full particle system with its own cost, so a three-deep chain multiplies rather than adds | [Particle System component](https://docs.unity3d.com/Manual/class-ParticleSystem.html) |
| Texture Sheet Animation | Flipbook detail from one texture — the cheap way to add per-particle motion without more particles or geometry | [Particle System component](https://docs.unity3d.com/Manual/class-ParticleSystem.html) |
| Collision | World or Planes. **Planes is dramatically cheaper** and enough for a ground plane. World quality High tests against real colliders per particle; the lower settings use an approximation, and the gap between them is the module's whole cost story | [Particle System component](https://docs.unity3d.com/Manual/class-ParticleSystem.html) |
| Send Collision Messages | Required for `OnParticleCollision` to fire at all — collision can be simulating correctly and reporting nothing | [ParticleSystem API](https://docs.unity3d.com/ScriptReference/ParticleSystem.html) |
| Triggers | Reports particles entering, exiting, or inside a collider without simulating a bounce — the right tool when only the event matters | [Particle System component](https://docs.unity3d.com/Manual/class-ParticleSystem.html) |
| Trails | Ribbons attached to particles. Needs a **second material** on the renderer; leaving it empty is the usual cause of magenta trails on an otherwise correct effect | [Particle System component](https://docs.unity3d.com/Manual/class-ParticleSystem.html) |
| Lights | Attaches real lights to particles, at real per-light cost. The ratio control exists because one light per particle is almost never affordable | [Particle System component](https://docs.unity3d.com/Manual/class-ParticleSystem.html) |

## Renderer

| Property | What it decides | Source |
|---|---|---|
| Render Mode | Billboard, Stretched Billboard for speed-aligned sparks, Horizontal or Vertical Billboard, Mesh, or None for a simulation-only system feeding trails | [ParticleSystemRenderer](https://docs.unity3d.com/ScriptReference/ParticleSystemRenderer.html) |
| Sort Mode and Sorting Fudge | Order within the system, and a bias on the whole system's depth against other transparents. Fudge is the lever for "the effect draws behind the character it should be in front of" | [ParticleSystemRenderer](https://docs.unity3d.com/ScriptReference/ParticleSystemRenderer.html) |
| Min / Max Particle Size | Clamps in **viewport** fraction, not world units — the control that stops one particle covering the screen when the camera gets close, which is an overdraw problem as much as a visual one | [ParticleSystemRenderer](https://docs.unity3d.com/ScriptReference/ParticleSystemRenderer.html) |
| Mask Interaction | How particles respond to a `SpriteMask`, for 2D effects — the sprite side belongs to `unity-2d-sprite` | [ParticleSystemRenderer](https://docs.unity3d.com/ScriptReference/ParticleSystemRenderer.html) |

## Scripting

| Point | What it means in practice | Source |
|---|---|---|
| Modules are structs | `ps.main.startLifetime = 2f;` does not compile — the module must be assigned to a local first, and writing through that local does affect the system | [ParticleSystem API](https://docs.unity3d.com/ScriptReference/ParticleSystem.html) |
| `Stop(withChildren, stopBehavior)` | Stop Emitting lets existing particles finish; Stop Emitting And Clear removes them immediately. The choice between a natural end and an instant one | [ParticleSystem.Stop](https://docs.unity3d.com/ScriptReference/ParticleSystem.Stop.html) |
| `Clear()` before `Play()` | A pooled system restarted without clearing replays with the previous use's particles still alive — denser and mistimed | [ParticleSystem.Clear](https://docs.unity3d.com/ScriptReference/ParticleSystem.Clear.html) |
| `GetParticles` / `SetParticles` | Reads the live particle buffer into an array the CPU can modify. Allocate that array once and reuse it, per `performance-and-algorithms.md` | [ParticleSystem.GetParticles](https://docs.unity3d.com/ScriptReference/ParticleSystem.GetParticles.html) |
| `IsAlive()` | The correct release condition for a pooled one-shot — not a fixed timer that has to be kept in step with the effect's duration | [ParticleSystem.IsAlive](https://docs.unity3d.com/ScriptReference/ParticleSystem.IsAlive.html) |
