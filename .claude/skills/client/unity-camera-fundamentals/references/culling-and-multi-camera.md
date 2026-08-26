# Culling, Camera Ordering, and Multi-Camera Setups

Sources: [Multiple Cameras](https://docs.unity3d.com/Manual/MultipleCameras.html), [Render Textures](https://docs.unity3d.com/Manual/class-RenderTexture.html), [Camera API](https://docs.unity3d.com/ScriptReference/Camera.html).
Covers: SKILL.md §4 — **"Cull with the mask and per-layer distances rather than rendering and discarding"**, **"Order multiple cameras with depth and clear flags together, never depth alone"**.

Every additional camera is another full culling and submission pass over
whatever it can see, so the cheapest multi-camera setup is the one where each
camera sees as little as possible. Ordering is where the surprises live:
depth alone decides *sequence*, and clear flags decide whether the later
camera preserves or erases what the earlier one drew.

## Culling

| Property | What it decides | Source |
|---|---|---|
| `cullingMask` | Which layers this camera renders at all. Excluding VFX and UI from a minimap camera removes that work before submission rather than after | [Camera.cullingMask](https://docs.unity3d.com/ScriptReference/Camera-cullingMask.html) |
| `layerCullDistances` | A per-layer far distance, shorter than the camera's own. The standard way to stop drawing small props at range without shortening the far plane for everything | [Camera.layerCullDistances](https://docs.unity3d.com/ScriptReference/Camera-layerCullDistances.html) |
| `layerCullSpherical` | Measures those distances as a sphere rather than against the far plane, so objects do not pop in and out as the camera turns | [Camera.layerCullSpherical](https://docs.unity3d.com/ScriptReference/Camera-layerCullSpherical.html) |
| `useOcclusionCulling` | Per-camera opt-out from baked occlusion data — worth disabling on a camera whose view is unoccluded, since the test itself costs | [Camera.useOcclusionCulling](https://docs.unity3d.com/ScriptReference/Camera-useOcclusionCulling.html) |

## Ordering and composition

| Property | What it decides | Source |
|---|---|---|
| `depth` | Render order among cameras — higher renders later, on top | [Camera.depth](https://docs.unity3d.com/ScriptReference/Camera-depth.html) |
| `clearFlags` | Whether the later camera keeps what is already there. **Depth Only** preserves the colour beneath and is what a layered composite needs; Skybox or Solid Color on an upper camera erases everything below it, which is the usual cause of "my second camera renders but the first disappeared" | [Camera.clearFlags](https://docs.unity3d.com/ScriptReference/Camera-clearFlags.html) |
| `rect` | Normalised viewport rect for split screen. **Each camera's effective aspect is its rect's aspect times the screen's**, so a half-width viewport halves horizontal coverage at the same FOV — the framing must be retuned, not inherited | [Camera.rect](https://docs.unity3d.com/ScriptReference/Camera-rect.html) |
| URP camera stacking | Replaces several independent full-screen cameras with one Base plus Overlays, which is cheaper and ordered explicitly. Owned by `unity-urp-rendering`, and preferred over this file's depth-and-clear-flags approach on a URP project | [Multiple Cameras](https://docs.unity3d.com/Manual/MultipleCameras.html) |

## Render textures

| Property | What it decides | Source |
|---|---|---|
| `targetTexture` | Redirects the camera's output into a `RenderTexture`. Setting it means the camera **stops rendering to the screen**, which is correct for a minimap and a surprise if it was meant to do both | [Camera.targetTexture](https://docs.unity3d.com/ScriptReference/Camera-targetTexture.html) |
| Depth buffer bits | A `RenderTexture` created with zero depth bits sorts 3D content incorrectly — opaque geometry draws in submission order. A 2D or UI-only target can leave it at zero | [Render Textures](https://docs.unity3d.com/Manual/class-RenderTexture.html) |
| Resolution | A minimap does not need screen resolution; the texture's size is an independent cost lever from the camera's culling mask | [Render Textures](https://docs.unity3d.com/Manual/class-RenderTexture.html) |
| Release | A `RenderTexture` holds GPU memory until released, and one created per call is a leak — allocate once and reuse, per the Memory discipline section of `performance-and-algorithms.md` | [Render Textures](https://docs.unity3d.com/Manual/class-RenderTexture.html) |
