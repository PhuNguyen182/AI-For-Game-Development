# Hand-Rolled Follow, Bounds, and Shake

Sources: [Vector3.SmoothDamp](https://docs.unity3d.com/ScriptReference/Vector3.SmoothDamp.html), [Mathf.PerlinNoise](https://docs.unity3d.com/ScriptReference/Mathf.PerlinNoise.html), [Camera.main](https://docs.unity3d.com/ScriptReference/Camera-main.html), [Order of execution for event functions](https://docs.unity3d.com/Manual/ExecutionOrder.html).
Covers: SKILL.md §4 — **"Follow in `LateUpdate`, and check the target's interpolation before blaming the smoothing"**, **"Smooth with `SmoothDamp` and a persistent velocity field, never `Lerp` against a raw constant"**, **"Compose shake as an offset applied after the follow resolves, and sample noise at distinct coordinates per axis"**, **"Derive bounds clamping from the current view size, not a fixed padding constant"**.

Hand-written camera motion goes wrong in three places, and none of them is
the smoothing curve: **when** the target is sampled, **how** the smoothing is
integrated across variable frame times, and **where** the shake offset is
stored. Reaching for a longer smoothing time is the usual response to all
three, and it fixes none of them while costing responsiveness.

## When to sample the target

| Phase | What has already happened | Source |
|---|---|---|
| `Update` | Gameplay for this frame may not have moved the target yet — following here can read last frame's position, producing a consistent one-frame lag | [Order of execution](https://docs.unity3d.com/Manual/ExecutionOrder.html) |
| `LateUpdate` | All `Update` calls are done, so a transform-driven target is final. The correct phase for a camera follow | [Order of execution](https://docs.unity3d.com/Manual/ExecutionOrder.html) |
| A physics-driven target | Moves in `FixedUpdate`, which does not align with frame boundaries. Its transform is only smooth between steps when its `Rigidbody` has **Interpolate** enabled — without that, the judder is in the target's position before the camera ever reads it, and no camera-side smoothing removes it | [Order of execution](https://docs.unity3d.com/Manual/ExecutionOrder.html) |

Rigidbody interpolation settings themselves belong to `unity-3d-physics` and
`unity-2d-physics`; this file only names the dependency, because a follow bug
is where it usually surfaces.

## Smoothing

| Approach | Behaviour across frame times | Source |
|---|---|---|
| `Vector3.SmoothDamp` | Critically damped, parameterised by an approximate time to reach the target, and framerate-independent. Requires a **persistent** velocity field passed by `ref` — declaring it as a local each frame resets the damping and degrades it into a jerky lerp | [Vector3.SmoothDamp](https://docs.unity3d.com/ScriptReference/Vector3.SmoothDamp.html) |
| `Vector3.Lerp(a, b, k)` with a constant `k` | Framerate-dependent: the same `k` moves further per second at a higher frame rate, so the camera feels different on different hardware | [Vector3.Lerp](https://docs.unity3d.com/ScriptReference/Vector3.Lerp.html) |
| `Lerp` with an exponential factor | `1 - Mathf.Pow(1 - k, Time.deltaTime)` is the framerate-independent correction if `Lerp` must be kept — but `SmoothDamp` expresses the same intent with a tunable that means something | [Vector3.Lerp](https://docs.unity3d.com/ScriptReference/Vector3.Lerp.html) |
| `maxSpeed` on `SmoothDamp` | Caps catch-up speed — the difference between a camera that snaps to a teleporting target and one that races across the level | [Vector3.SmoothDamp](https://docs.unity3d.com/ScriptReference/Vector3.SmoothDamp.html) |

## Bounds clamping

| Quantity | How to derive it | Source |
|---|---|---|
| Orthographic half-extents | Half-height is `orthographicSize`; half-width is `orthographicSize * camera.aspect`. Both change with the screen, which is why a fixed padding constant fails on the next device | [Camera.orthographicSize](https://docs.unity3d.com/ScriptReference/Camera-orthographicSize.html) |
| Perspective half-extents at a depth | Half-height is `distance * Mathf.Tan(fieldOfView * 0.5f * Mathf.Deg2Rad)`; half-width multiplies by `aspect`. Depends on the follow distance, so it must be recomputed when that changes | [Camera.fieldOfView](https://docs.unity3d.com/ScriptReference/Camera-fieldOfView.html) |
| Clamp target | Clamp the **resolved follow position** before the shake offset is added, so the shake can still push slightly past the bound without fighting the clamp every frame | [Camera API](https://docs.unity3d.com/ScriptReference/Camera.html) |

## Shake

| Rule | Why | Source |
|---|---|---|
| Sample `PerlinNoise` at distinct coordinates per axis | `Mathf.PerlinNoise(t, t)` walks the diagonal of the noise field and returns correlated values, so x and y move together and the result reads as a slide. Offset one axis — `(t, 0)` and `(0, t)` — to decorrelate them | [Mathf.PerlinNoise](https://docs.unity3d.com/ScriptReference/Mathf.PerlinNoise.html) |
| Prefer noise over per-frame `Random` | Independent random values every frame produce static rather than motion, because there is no continuity between samples | [Mathf.PerlinNoise](https://docs.unity3d.com/ScriptReference/Mathf.PerlinNoise.html) |
| Recentre the noise | `PerlinNoise` returns roughly 0–1 and tends to 0.5 at integer coordinates — subtract 0.5 before scaling or the shake carries a constant bias | [Mathf.PerlinNoise](https://docs.unity3d.com/ScriptReference/Mathf.PerlinNoise.html) |
| Store the offset separately | Add shake to the resolved follow position each frame rather than into the transform's own state; accumulating it drifts the camera permanently and there is nothing to drift back to | [Camera API](https://docs.unity3d.com/ScriptReference/Camera.html) |
| Decay the amplitude | A shake with no envelope either never ends or ends abruptly — decay amplitude to zero over the effect's duration | [Mathf.PerlinNoise](https://docs.unity3d.com/ScriptReference/Mathf.PerlinNoise.html) |

Composited, priority-blended, or source-and-listener shake belongs to
`unity-cinemachine-authoring`; this file covers the hand-rolled case on a
project not using it for that camera.

| Reference | Rule | Source |
|---|---|---|
| `Camera.main` | Performs a tagged lookup rather than reading a field — cache it in `Awake` and never call it per frame, per `performance-and-algorithms.md` | [Camera.main](https://docs.unity3d.com/ScriptReference/Camera-main.html) |
