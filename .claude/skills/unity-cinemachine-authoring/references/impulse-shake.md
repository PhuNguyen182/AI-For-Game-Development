# Impulse

Base: https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineImpulse.html (API: `CinemachineImpulseSource`, `CinemachineImpulseListener`).

A source emits at a world position; listeners react scaled by distance. Unlike a hand-written shake it survives blending to another camera.

| Piece | Rule |
|---|---|
| `CinemachineImpulseSource` | On the explosion/landing/hit. `GenerateImpulse()` emits at its position; overloads take velocity or force for varied magnitude |
| Raw signal asset | Waveform (noise profile or fixed 6-DOF curve); swap it to change every shake's character |
| Impact shape / dissipation | Falloff over distance and time (distant rumble vs near jolt) |
| `CinemachineImpulseListener` | Extension **per camera**: a camera without one goes still the moment it is live |
| Channel mask | Source channel vs listener mask; a mismatch gives no motion and no warning, so check it first |
| Gain | Per-listener scaling |
| Use 2D Distance | Falloff in-plane, for side-on/top-down where depth offset dominates |

Fire it from the Client handler that knows the event happened; the rule that decides it happened is `Game.Core.*`.
