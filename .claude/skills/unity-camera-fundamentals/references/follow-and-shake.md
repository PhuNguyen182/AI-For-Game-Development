# Hand-rolled follow, bounds and shake

Source: [Vector3.SmoothDamp](https://docs.unity3d.com/ScriptReference/Vector3.SmoothDamp.html), [Mathf.PerlinNoise](https://docs.unity3d.com/ScriptReference/Mathf.PerlinNoise.html), [Order of execution](https://docs.unity3d.com/Manual/ExecutionOrder.html).

Bugs come from when the target is sampled, how smoothing integrates over variable frame times, and where the shake offset lives. A longer smoothing time fixes none of them and costs responsiveness. Composited or priority-blended shake belongs to `unity-cinemachine-authoring`.

## When to sample
- `Update`: the target may not have moved yet, giving a consistent one-frame lag.
- `LateUpdate`: all `Update` calls are done; the correct phase for a follow.
- Physics-driven target: moves in `FixedUpdate`; smooth between steps only if its `Rigidbody` has Interpolate enabled. Otherwise the judder is in the target and no camera smoothing removes it.

## Smoothing
- `Vector3.SmoothDamp`: critically damped, framerate-independent. Needs a persistent velocity field passed by `ref`; a per-frame local resets damping into a jerky lerp.
- `Vector3.Lerp(a, b, k)` with constant `k`: framerate-dependent, so the camera feels different on different hardware.
- If `Lerp` must stay, use the factor `1 - Mathf.Pow(1 - k, Time.deltaTime)`.
- `maxSpeed` on `SmoothDamp` caps catch-up: the difference between snapping to a teleporting target and racing across the level.

## Bounds clamping
- Orthographic half-extents: half-height `orthographicSize`, half-width `orthographicSize * camera.aspect`.
- Perspective at a depth: half-height `distance * Mathf.Tan(fieldOfView * 0.5f * Mathf.Deg2Rad)`, half-width times `aspect`; recompute when the follow distance changes.
- Clamp the resolved follow position before adding shake, so shake can pass the bound slightly without fighting the clamp.

## Shake
- Sample `PerlinNoise` at distinct coordinates per axis (`(t, 0)` and `(0, t)`); `PerlinNoise(t, t)` walks the diagonal, so x and y correlate into a slide.
- Prefer noise to per-frame `Random`: independent values give static, not motion.
- Subtract 0.5 before scaling; the noise is about 0-1 and would bias the shake.
- Store the offset separately and add it to the resolved follow each frame; accumulating into the transform drifts the camera permanently.
- Decay amplitude to zero over the duration, or the shake never ends or ends abruptly.
