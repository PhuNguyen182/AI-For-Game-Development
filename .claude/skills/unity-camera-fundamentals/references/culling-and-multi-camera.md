# Culling, camera ordering and multi-camera

Source: [Multiple Cameras](https://docs.unity3d.com/Manual/MultipleCameras.html), [Render Textures](https://docs.unity3d.com/Manual/class-RenderTexture.html), [Camera API](https://docs.unity3d.com/ScriptReference/Camera.html).

Every extra camera is another culling and submission pass, so each should see as little as possible. Depth sets sequence; clear flags decide whether a later camera keeps or erases what an earlier one drew.

## Culling
- `cullingMask`: layers rendered at all; excluding VFX and UI from a minimap camera removes the work before submission.
- `layerCullDistances`: per-layer far distance shorter than the camera's; stops small props drawing at range without shortening the far plane.
- `layerCullSpherical`: measures those distances as a sphere so objects do not pop as the camera turns.
- `useOcclusionCulling`: disable on a camera with an unoccluded view; the test itself costs.

## Ordering and composition
- `depth`: higher renders later, on top.
- `clearFlags`: Depth Only preserves the colour beneath and is what a layered composite needs; Skybox or Solid Color on an upper camera erases everything below ("second camera renders but the first disappeared").
- `rect`: normalised viewport for split screen. Effective aspect is the rect's aspect times the screen's, so a half-width viewport halves horizontal coverage at the same FOV; retune framing.
- URP camera stacking (one Base plus Overlays) is cheaper and explicitly ordered; prefer it on URP (`unity-urp-rendering`).

## Render textures
- `targetTexture`: the camera stops rendering to the screen; right for a minimap, a surprise if both were wanted.
- Zero depth bits sorts 3D content wrongly (opaque geometry draws in submission order); a 2D or UI-only target may use zero.
- A minimap does not need screen resolution; texture size is a cost lever independent of the culling mask.
- A `RenderTexture` holds GPU memory until released; allocate once and reuse, never one per call (`csharp-standards` → `performance-and-algorithms.md`, Memory discipline).
