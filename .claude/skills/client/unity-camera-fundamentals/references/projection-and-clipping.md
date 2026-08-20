# Projection & Clipping

Covers SKILL.md steps 2–3 (projection, clip planes).

## Manual
- [Camera component reference](https://docs.unity3d.com/Manual/class-Camera.html) — Inspector field reference (Clear Flags, Projection, FOV/Size, Clipping Planes, Culling Mask, Viewport Rect, Depth, Rendering Path).
- [Physical Camera properties](https://docs.unity3d.com/Manual/PhysicalCameras.html) — focal length/sensor-size-driven FOV for realistic lens behavior.

## Scripting API
- [`Camera.orthographic`](https://docs.unity3d.com/ScriptReference/Camera-orthographic.html), [`Camera.orthographicSize`](https://docs.unity3d.com/ScriptReference/Camera-orthographicSize.html), [`Camera.fieldOfView`](https://docs.unity3d.com/ScriptReference/Camera-fieldOfView.html)
- [`Camera.nearClipPlane`](https://docs.unity3d.com/ScriptReference/Camera-nearClipPlane.html), [`Camera.farClipPlane`](https://docs.unity3d.com/ScriptReference/Camera-farClipPlane.html)
