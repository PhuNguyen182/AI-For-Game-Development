---
name: unity-camera-fundamentals
description: >
  Technique for Unity's native `Camera` component and plain `Transform` camera
  scripting: perspective and orthographic projection, vertical field of view
  and aspect behaviour, physical camera and gate fit, clip planes and depth
  precision, culling masks and per-layer cull distances, camera depth and
  clear flags, viewport rects for split screen, `RenderTexture` output, world,
  screen and viewport conversions, `ScreenPointToRay` picking, and hand-rolled
  follow, bounds clamp and shake. Use when a `Camera` must be configured or
  scripted directly. Not for: Cinemachine (`unity-cinemachine-authoring`); URP
  camera stacking and renderer settings (`unity-urp-rendering`); post-process
  effects (`unity-post-processing`); pointer input (`unity-input-system`).
---

# Unity Camera Fundamentals — The Camera Component and Transform-Level Scripting

## Bundled resources

### References
Read-only context, loaded on demand so SKILL.md itself stays short.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Manual and API roots plus the version pin | Starting any task here |
| [projection-and-framing.md](references/projection-and-framing.md) | Projection, vertical FOV and aspect, physical camera, gate fit, clip planes and depth precision | Choosing framing, or framing breaks on a different screen shape |
| [culling-and-multi-camera.md](references/culling-and-multi-camera.md) | Culling mask, per-layer cull distances, depth and clear flags, viewport rect, `RenderTexture` | More than one camera renders, or a camera renders more than it should |
| [coordinates-and-raycasting.md](references/coordinates-and-raycasting.md) | World, screen and viewport conversions, the depth argument, points behind the camera, picking | Converting between spaces, or a conversion returns a plausible wrong answer |
| [follow-and-shake.md](references/follow-and-shake.md) | Update ordering against physics, `SmoothDamp`, bounds from view size, noise-driven shake | Writing camera motion by hand rather than through Cinemachine |

## 1. Objective
Configure and script a `Camera` so its framing holds on every screen the project ships to, and so hand-written camera motion is smooth for the right reason. Most camera bugs are not visual bugs: a conversion that silently returns a point behind the viewer, a follow that judders because it samples a target mid-physics-step, a framing tuned at one aspect ratio that crops the action at another. Each produces a plausible result that is wrong.

## 2. Role
Act as the native camera specialist — the `Camera` component, its adjacent per-pipeline data, and plain `Transform` camera scripts. You do not author Cinemachine rigs, configure the render pipeline behind the camera, or read input devices directly.

## 3. When to invoke this skill
- Setting a camera's projection, field of view or orthographic size, clip planes, clear flags, or culling mask.
- Framing that works on one screen shape and crops or over-reveals on another.
- Converting between world, screen, and viewport space, or picking a world point from a screen position.
- Setting up split screen, a minimap or picture-in-picture through a `RenderTexture`, or ordering several cameras' output.
- Writing follow, bounds clamping, or shake by hand, on a project not using Cinemachine for that camera.
- A hand-written follow judders, lags a frame behind its target, or drifts.
- Negative trigger: any Cinemachine component — `CinemachineCamera`, Brain blending, Confiner, Impulse — that is `unity-cinemachine-authoring`; when the project has Cinemachine and the task is genuinely cinematic, route rather than hand-roll an equivalent.
- Negative trigger: camera stacking, the renderer a camera uses, or anything on the per-pipeline sibling component — that is `unity-urp-rendering` under URP and `unity-hdrp-rendering` under HDRP; this skill owns the `Camera`'s own fields, not the pipeline behind them.
- Negative trigger: the Camera's Post Processing toggle and anything a Volume drives — that is `unity-post-processing`.
- Negative trigger: reading a pointer, stick, or touch position to feed a conversion — that is `unity-input-system`; this skill consumes the screen position it produces.
- Negative trigger: UI safe area and notch handling — that is the UI/UX Programmer's scope.
- Negative trigger: a gameplay decision made from a camera-driven raycast — the camera supplies the world point, `Game.Core.*` decides what it means, per `coding-principles.md`.

## 4. How to use this skill
1. **Confirm which component actually owns the setting on this pipeline** — plain `Camera` fields under the Built-in pipeline, with `UniversalAdditionalCameraData` or `HDAdditionalCameraData` holding the renderer, stacking, and post-processing toggles on an SRP. [root-links.md](references/root-links.md) pins the doc version these fields are read at.
2. **Treat field of view as vertical and let the aspect ratio decide the width**, per [projection-and-framing.md](references/projection-and-framing.md) — Unity's `fieldOfView` and `orthographicSize` both describe the vertical extent, so a taller screen shows *less* horizontally at the same value. Framing tuned once on a landscape monitor is the usual cause of a mobile portrait build cropping the action.
3. **Reach for the physical camera and Gate Fit when framing must survive several screen shapes** — Gate Fit defines what happens when the sensor aspect and the screen aspect disagree, which is the actual control for "keep the composition, change the screen", rather than branching on aspect ratio in script.
4. **Push the near clip plane out before pulling the far plane in** — depth precision is dominated by the near plane, so doubling near recovers far more precision than halving far, and z-fighting at distance is usually a near-plane problem wearing a far-plane costume.
5. **Cull with the mask and per-layer distances rather than rendering and discarding**, per [culling-and-multi-camera.md](references/culling-and-multi-camera.md) — a minimap camera excluding VFX and UI layers, and small props given a short `layerCullDistances` entry, both remove work before it is submitted.
6. **Order multiple cameras with depth and clear flags together, never depth alone** — a higher-depth camera with Skybox or Solid Color clear erases what rendered before it, so a layered composite needs Depth Only on everything above the base.
7. **Pass a real distance as the z component of `ScreenToWorldPoint`**, per [coordinates-and-raycasting.md](references/coordinates-and-raycasting.md) — the input's z is distance from the camera, not a screen coordinate, and leaving it zero returns the camera's own position, which looks like a broken conversion rather than a missing argument.
8. **Check the returned z before trusting `WorldToScreenPoint`** — a point behind the camera returns a mirrored on-screen position with a negative z, so an off-screen indicator built without that check points confidently the wrong way.
9. **Bound and mask every camera-driven raycast, and use the non-allocating overload in a per-frame path** — an unbounded ray against every layer is the default nobody chose, and the allocating overload violates the no-per-frame-allocation rule in `coding-principles.md`.
10. **Follow in `LateUpdate`, and check the target's interpolation before blaming the smoothing**, per [follow-and-shake.md](references/follow-and-shake.md) — a target moved by physics only has a smooth transform if its `Rigidbody` has Interpolate enabled, and no amount of camera smoothing removes judder that is already in the target's position.
11. **Smooth with `SmoothDamp` and a persistent velocity field, never `Lerp` against a raw constant** — `Lerp` with a per-frame constant is framerate-dependent, and a `SmoothDamp` velocity reset each frame silently degrades into the same thing.
12. **Compose shake as an offset applied after the follow resolves, and sample noise at distinct coordinates per axis** — accumulating shake into the camera's own position drifts it permanently, and sampling `PerlinNoise` with the same input on two axes returns the same value, producing a diagonal slide rather than a shake.
13. **Derive bounds clamping from the current view size, not a fixed padding constant** — half-extents come from `orthographicSize` times aspect, or the frustum width at the target depth, so a hard-coded margin breaks on the next aspect ratio.
14. **Keep the camera presentational** — it reads an already-resolved target position and supplies world points; the gameplay meaning of a picked point is decided in `Game.Core.*` per `coding-principles.md`'s Shared Core integrity rule.

## 5. Specific goals / tasks this skill performs
- Projection, field of view or orthographic size, physical camera and Gate Fit, and clip planes sized to the real scene.
- Framing that holds across the project's actual target aspect ratios.
- Culling masks, per-layer cull distances, camera depth and clear-flag ordering.
- Split screen through viewport rects, and minimap or picture-in-picture through a `RenderTexture`.
- World, screen, and viewport conversions, and camera-driven picking.
- Hand-written follow, bounds clamping, and shake for cameras not driven by Cinemachine.
- Out of scope: Cinemachine (`unity-cinemachine-authoring`); camera stacking and per-camera pipeline data (`unity-urp-rendering`, `unity-hdrp-rendering`); post-processing (`unity-post-processing`); reading input devices (`unity-input-system`); UI safe area (`ui-ux-programmer`); gameplay decisions from a picked point (`csharp-engineer`).

## 6. Output format
```
## Camera — <feature name>
- Pipeline confirmed: <Built-in / URP / HDRP — and which component holds the settings changed>
- Projection: <orthographic size or vertical FOV> — and the framing requirement behind it
- Aspect handling: <physical camera and Gate Fit / tuned per tier / single target aspect>
- Clip planes: <near / far> — sized to the scene, with the precision rationale
- Culling: <mask, per-layer cull distances — or "unchanged">
- Multi-camera: <depth and clear flags per camera, viewport rects, render textures — or "single camera">
- Conversions: <APIs used, and how the depth argument and behind-camera case are handled>
- Motion: <follow / clamp / shake — update phase, smoothing method, target interpolation state>
- Verified on: <aspect ratios and device classes actually run>
- Layer: <Game.Client.* camera components and scripts>
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what the delivered camera setup does not cover>
- Latent concerns: <failure modes not yet triggered: assumptions that hold only under current conditions, thresholds not yet reached, trade-offs knowingly deferred>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: "Tapping the ground should move the player there."
- Output: took the screen position from the input layer rather than reading a device here, built a ray with `ScreenPointToRay`, and raycast against a Ground layer mask with an explicit max distance and the non-allocating overload, since this runs per input event in a mobile build. Cached the camera reference in `Awake`. The resulting world point went to the Client movement system, which calls into Shared Core — the camera script decides nothing about movement, it only answers where the tap landed.

**Example 2**
- Input: "The off-screen enemy arrow points the wrong way when enemies are behind the player."
- Output: `WorldToScreenPoint` returns a mirrored position for anything behind the camera, with a negative z as the only signal. Added the z check and flipped the direction for that case before clamping to the screen edge, per §4's behind-camera step. No change to the arrow maths itself — it was correct for everything in front, which is exactly why the bug read as intermittent.

**Example 3**
- Input: "Camera follow judders even after increasing the smoothing time."
- Output: the judder was in the target, not the camera — a `Rigidbody` with Interpolate off, sampled in `LateUpdate` between physics steps. Enabled interpolation on the target and returned the smoothing time to its original value, since raising it had been compensating for the wrong cause and was already costing responsiveness. Confirmed the follow itself ran in `LateUpdate` and that `SmoothDamp` kept its velocity in a field rather than a local.

## 8. Edge cases & guardrails
- Never tune framing at one aspect ratio and ship several — vertical FOV means a taller screen sees less horizontally, and the crop lands on gameplay.
- Never enlarge the far plane "to be safe" — but check the near plane first, since it dominates depth precision.
- Never pass zero as the z of `ScreenToWorldPoint` — that returns the camera's position, not a point on screen.
- Never use `WorldToScreenPoint` without testing z — points behind the camera come back mirrored and plausible.
- Never raycast unbounded against every layer from a camera — set a mask and a max distance, and use the non-allocating overload in a per-frame path.
- Never order layered cameras by depth alone — clear flags decide whether the one above wipes the one below.
- Never follow in `Update` — the target may not have moved yet this frame.
- Never smooth with `Lerp` and a raw constant, and never reset a `SmoothDamp` velocity each frame — both are framerate-dependent in effect.
- Never sample `PerlinNoise` with the same coordinate on two axes — identical values give a diagonal slide, not a shake.
- Never accumulate shake into the camera's own position — apply it as an offset after the follow resolves, or the base position drifts.
- Never call `Camera.main` in a per-frame method — cache it, per `performance-and-algorithms.md`.
- Never reach for the legacy `Input` class to get a pointer position — the input owner supplies it, per the Obsolete APIs rule in `coding-principles.md`.
- Never hand-roll confiner-quality bounds, composited shake, or priority blending on a project that has Cinemachine — route to `unity-cinemachine-authoring`.
- Never let camera code mutate gameplay state — it is presentational, and the picked point's meaning belongs to `Game.Core.*`.
