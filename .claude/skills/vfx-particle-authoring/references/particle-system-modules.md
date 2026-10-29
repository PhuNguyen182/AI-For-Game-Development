# Built-in ParticleSystem modules

Sources: [Component reference](https://docs.unity3d.com/Manual/class-ParticleSystem.html), [ParticleSystem API](https://docs.unity3d.com/ScriptReference/ParticleSystem.html), [ParticleSystemRenderer API](https://docs.unity3d.com/ScriptReference/ParticleSystemRenderer.html).

## Main
- **Simulation Space**: Local carries particles with the emitter, World leaves them where born, Custom ties them to another transform.
- **Max Particles**: at the ceiling the system stops emitting until particles die.
- **Start Lifetime** × emission rate determine how many exist at once: reason about the pair.
- **Scaling Mode** (Local/Hierarchy/Shape): why an effect on a scaled prefab can ignore the scale.
- **Delta Time = Unscaled** keeps an effect running while paused (pause menu, hit-stop).
- **Play On Awake**: fine for ambience, wrong for a pooled one-shot (whoever takes it from the pool starts it).
- **Stop Action** (Disable/Destroy/Callback): Destroy excludes pooling.

## Emission and shape
- Rate over Time for continuous ambience; Rate over Distance for anything on a moving object (constant trail density).
- Bursts (count, cycles, interval, probability): a one-shot is bursts with rate 0, not a briefly raised rate.
- Shape sets the volume and the initial direction: swapping Cone for Sphere changes velocity direction, not only spawn positions. Arc mode: Random, Loop, Ping-Pong, Burst Spread.

## Behavior modules
| Module | Note |
|---|---|
| Noise | Best single module for organic motion, also among the most expensive; Quality selects 1D/2D/3D noise |
| Sub Emitters | Birth/Collision/Death/Trigger; each is a full system, so a three-deep chain multiplies cost |
| Texture Sheet Animation | Cheap per-particle flipbook motion |
| Collision | **Planes is far cheaper** than World and enough for a ground. World High tests real colliders per particle |
| Send Collision Messages | Required for `OnParticleCollision`; without it collision simulates but reports nothing |
| Triggers | Enter/exit/inside a collider without bounce: use when only the event matters |
| Trails | Needs a **second material** on the renderer; empty = magenta trails |
| Lights | Real per-light cost; use the ratio control, one light per particle is rarely affordable |

## Renderer
- Render Mode: Billboard, Stretched Billboard (speed-aligned sparks), Horizontal/Vertical Billboard, Mesh, None (simulation-only feeding trails).
- Sort Mode orders within the system; Sorting Fudge biases the whole system's depth against other transparents ("draws behind the character it should cover").
- Min/Max Particle Size clamps in viewport fraction, stopping one particle covering the screen near the camera (overdraw).
- Mask Interaction responds to `SpriteMask` for 2D (sprite side: `unity-2d-sprite`).

## Scripting
- Modules are structs: `ps.main.startLifetime = 2f;` does not compile; assign `var main = ps.main;` first, then write through it.
- `Stop(withChildren, stopBehavior)`: StopEmitting lets live particles finish; StopEmittingAndClear removes them now.
- `Clear()` before `Play()` on a pooled system, or it replays with the previous use's particles alive.
- `GetParticles`/`SetParticles`: allocate the array once and reuse (`csharp-standards` → `performance-and-algorithms.md`).
- `IsAlive()` is the release condition for a pooled one-shot, not a fixed timer.
