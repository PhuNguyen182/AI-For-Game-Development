# Hand-Rolled Follow & Shake

Covers SKILL.md steps 7, 9, 11 (follow smoothing, shake, caching `Camera.main`).

## Scripting API
- [`Camera.main`](https://docs.unity3d.com/ScriptReference/Camera-main.html) — cache the result; never call per-frame.
- [`Vector3.SmoothDamp`](https://docs.unity3d.com/ScriptReference/Vector3.SmoothDamp.html) — framerate-independent follow smoothing.
- [`Mathf.PerlinNoise`](https://docs.unity3d.com/ScriptReference/Mathf.PerlinNoise.html) — hand-rolled shake offset source.
