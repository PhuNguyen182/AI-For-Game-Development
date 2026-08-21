# Impulse — Shake That Survives a Camera Switch

Sources: [Impulse](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineImpulse.html), [CinemachineImpulseSource](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/api/Unity.Cinemachine.CinemachineImpulseSource.html), [CinemachineImpulseListener](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/api/Unity.Cinemachine.CinemachineImpulseListener.html).
Covers: SKILL.md §4 — **"Shake through Impulse, and check the channel before assuming the impulse failed"**.

Impulse separates the event from the reaction. A source emits a signal at a
world position; every listener within range reacts, scaled by distance. That
separation is the whole point: a hand-written shake is attached to one
camera and stops existing the moment the rig blends to another, while an
impulse is a property of the world that whichever camera is live responds to.

| Piece | What it decides | Source |
|---|---|---|
| `CinemachineImpulseSource` | Sits on the thing that shakes the world — the explosion, the landing, the hit. `GenerateImpulse()` emits at its own position, and overloads take a velocity or force so one source can express different magnitudes | [CinemachineImpulseSource](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/api/Unity.Cinemachine.CinemachineImpulseSource.html) |
| Raw signal asset | The waveform — a noise profile or a fixed 6-degrees-of-freedom curve. Swapping the signal changes the character of every shake from that source without touching the emitting code | [Impulse](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineImpulse.html) |
| Impact shape and dissipation | How the signal falls off with distance and over time — what makes a distant explosion a rumble and a near one a jolt, from the same source | [Impulse](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineImpulse.html) |
| `CinemachineImpulseListener` | An extension on a `CinemachineCamera`. It is **per camera**, so a rig whose other cameras have no listener goes still the moment one of them becomes live | [CinemachineImpulseListener](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/api/Unity.Cinemachine.CinemachineImpulseListener.html) |
| Channel mask | Sources emit on a channel, listeners subscribe to a mask. **A mismatch produces no motion and no warning** — the first thing to check when an impulse appears not to fire | [Impulse](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineImpulse.html) |
| Gain | Per-listener scaling, so one camera can react more strongly than another to the same event without duplicating sources | [CinemachineImpulseListener](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/api/Unity.Cinemachine.CinemachineImpulseListener.html) |
| Use 2D Distance | Measures falloff in the plane rather than in 3D — for a side-on or top-down game where the camera's depth offset would otherwise dominate the distance | [CinemachineImpulseListener](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/api/Unity.Cinemachine.CinemachineImpulseListener.html) |

Firing the impulse belongs to the Client-layer handler that already knows the
event happened. The rule deciding that it happened — the hit landing, the
damage applying — lives in `Game.Core.*` per `coding-principles.md`.
