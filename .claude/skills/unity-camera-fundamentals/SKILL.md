---
name: unity-camera-fundamentals
description: "Native Camera: FOV, orthographicSize, Gate Fit, cullingMask, viewport, ScreenToWorldPoint. Use for non-Cinemachine cam."
user-invocable: false
---

# Unity Camera Fundamentals

- **Not for:** Cinemachine (`unity-cinemachine-authoring`).
  - **Brain:** it overwrites this skill's transform writes every frame.
  - **Project with Cinemachine:** should not get a hand-rolled equivalent.
- **Not for:** camera stacking/renderer/per-pipeline data (`unity-urp-rendering`, `unity-hdrp-rendering`).
- **Not for:** post-process toggle, Volumes and anti-aliasing (`unity-post-processing`).
- **Not for:** pointer input (`unity-input-system`).
- **Not for:** UI safe area (`mobile-safe-area`).
- **Not for:** collider/layer setup and Rigidbody interpolation settings (`unity-3d-physics`, `unity-2d-physics`).
- **Not for:** gameplay meaning of a picked point (Core, per `csharp-standards` → `coding-principles.md`).
- **Docs:** https://docs.unity3d.com/Manual/Cameras.html, https://docs.unity3d.com/ScriptReference/Camera.html — unversioned, current release.
  - **Defaults:** confirm any default against the installed Editor.

## References
- **[projection-and-framing.md](references/projection-and-framing.md):** Choosing framing, or framing breaks on a different screen shape; clip planes and z-fighting.
- **[culling-and-multi-camera.md](references/culling-and-multi-camera.md):** More than one camera renders, or a camera renders more than it should.
- **[coordinates-and-raycasting.md](references/coordinates-and-raycasting.md):** Converting between spaces, picking, or a conversion returns a plausible wrong answer.
- **[follow-and-shake.md](references/follow-and-shake.md):** Writing follow, bounds or shake by hand.

## Steps
1. **Find the owner of the setting:** plain `Camera` fields in Built-in; `UniversalAdditionalCameraData` / `HDAdditionalCameraData` hold renderer, stacking and post-processing toggles on an SRP.
   - **Field missing from the Inspector:** usually on the sibling.
2. **Treat FOV and `orthographicSize` as vertical:** per [projection-and-framing.md](references/projection-and-framing.md).
   - **Aspect:** decides width, so a portrait screen shows less horizontally.
3. **Use the physical camera and Gate Fit for cross-aspect framing:** not aspect branching in script.
4. **Raise the near clip plane before lowering the far:** near dominates perspective depth precision.
5. **Cull with the mask and `layerCullDistances`:** not render-and-discard, per [culling-and-multi-camera.md](references/culling-and-multi-camera.md).
6. **Order cameras by depth and clear flags together:** an upper camera with Skybox/Solid Color clear erases the base, so layers need Depth Only.
7. **Pass a real distance as z to `ScreenToWorldPoint`:** per [coordinates-and-raycasting.md](references/coordinates-and-raycasting.md).
8. **Check z of `WorldToScreenPoint`:** a negative z is behind the camera with a mirrored x/y.
9. **Bound every camera raycast with a mask and max distance:** use the non-allocating overload per frame (`csharp-standards` → `coding-principles.md`).
   - **Screen position:** comes from the input layer.
10. **Follow in `LateUpdate`; check target interpolation before blaming smoothing:** per [follow-and-shake.md](references/follow-and-shake.md).
11. **Smooth with `SmoothDamp` and a persistent velocity field:** not `Lerp` with a constant.
12. **Apply shake as an offset after the follow resolves:** with distinct noise coordinates per axis.
13. **Derive bounds from current view size:** not a fixed padding.
14. **Keep the camera presentational:** it supplies world points and never mutates gameplay state.
15. **`Camera.main` is cached by Unity since 2020.2:** calling it per frame is cheap.
   - **Still cache a camera reference:** when the code must survive the main camera changing tag or being swapped.
16. **Aspect ratios and device classes:** verify on them, and name the ones actually run.

## Never
- **Use the legacy `Input` class to get a pointer position:** see `csharp-standards` → `coding-principles.md`, Obsolete APIs.
- **Tune framing at one aspect ratio:** and ship several.

## Output
```
## Camera — <feature name>
- Pipeline confirmed: <Built-in / URP / HDRP, component holding the settings changed>
- Projection: <orthographic size or vertical FOV> — framing requirement
- Aspect handling: <physical camera and Gate Fit / tuned per tier / single target aspect>
- Clip planes: <near / far> — precision rationale
- Culling: <mask, per-layer cull distances, or "unchanged">
- Multi-camera: <depth, clear flags, viewport rects, render textures, or "single camera">
- Conversions: <APIs used, depth argument and behind-camera handling>
- Motion: <follow / clamp / shake — update phase, smoothing, target interpolation state>
- Layer: <Client code>
```

## Example
- **"Camera follow judders even after raising the smoothing time":** the target's `Rigidbody` had Interpolate off and was sampled between physics steps.
  - **Did instead:** enabled interpolation and restored the smoothing time (raising it had cost responsiveness).
