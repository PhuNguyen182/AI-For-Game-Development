# Culling & Multi-Camera Setups

Covers SKILL.md steps 4 and 6 (culling mask, split-screen, minimap/PIP, URP Camera Stacking).

## Manual
- [Camera Stacking (URP)](https://docs.unity3d.com/Manual/urp/camera-stacking.html) — Base + Overlay camera compositing under URP.
- [Multiple Cameras](https://docs.unity3d.com/Manual/MultipleCameras.html) — split-screen / secondary-viewport setups.
- [Render Textures](https://docs.unity3d.com/Manual/class-RenderTexture.html) — rendering a camera's output to a texture (minimap/PIP).

## Scripting API
- [`Camera.cullingMask`](https://docs.unity3d.com/ScriptReference/Camera-cullingMask.html)
- [`Camera.rect`](https://docs.unity3d.com/ScriptReference/Camera-rect.html) — normalized viewport rect, used for split-screen.
- [`Camera.targetTexture`](https://docs.unity3d.com/ScriptReference/Camera-targetTexture.html) — render-to-`RenderTexture` (minimap/PIP).
