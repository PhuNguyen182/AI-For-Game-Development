---
name: unity-camera-fundamentals
description: >
  Technique for working directly with Unity's native `Camera` component and
  `Transform`-level scripting — projection/FOV/clip-plane/culling-mask
  configuration, viewport rect and split-screen/multi-camera setups, render
  textures, world/screen/viewport coordinate conversions and camera-driven
  raycasting, and hand-rolled follow/bounds/shake behavior via
  `SmoothDamp`/`LateUpdate`. Use this for any task touching the `Camera`
  component or plain-transform camera scripting. Do not use this for
  Cinemachine authoring (`CinemachineCamera`/`CinemachineVirtualCamera`,
  Confiner, Impulse, Brain blending) — that's `unity-cinemachine-authoring`.
  Do not use this for screen-space shader/post-process VFX
  (`shader-authoring`/`render-pipeline-urp-hdrp`) or UI safe-area handling
  (UI/UX Programmer's scope).
---

# Unity Camera Fundamentals — Native Camera Component & Transform Scripting

Sources: see [references/](references/) for the Unity Manual/Scripting API root links, split by topic — [root-links.md](references/root-links.md), [projection-and-clipping.md](references/projection-and-clipping.md), [culling-and-multi-camera.md](references/culling-and-multi-camera.md), [coordinates-and-raycasting.md](references/coordinates-and-raycasting.md), [follow-and-shake.md](references/follow-and-shake.md).

## 1. Objective
Configure and script Unity's built-in `Camera` component correctly — projection, clip planes, culling, viewport, multi-camera rendering, coordinate conversions — and, when a hand-rolled follow/bounds/shake is the right tool (no Cinemachine involved), implement it in a framerate-independent, jitter-free way.

## 2. Role
Act as the native camera specialist: you configure `Camera`/`UniversalAdditionalCameraData`/`HDAdditionalCameraData` fields deliberately per the project's confirmed pipeline, wire multi-camera/render-texture setups, and write plain `Transform`-level camera scripts (follow, clamp, shake) without reaching for a package this skill doesn't own.

## 3. When to invoke this skill
- Configuring a `Camera`'s projection (orthographic vs. perspective), field of view/orthographic size, near/far clip planes, culling mask, or clear flags/background.
- Converting between world, screen, and viewport space, or raycasting from the camera (click-to-move, aim/target picking, cursor-to-world).
- Setting up more than one camera: split-screen (`Camera.rect`), a minimap/PIP camera (`RenderTexture`), or URP Camera Stacking (Base + Overlay).
- Writing a plain follow/track, bounds-clamp, or shake script using `Transform`/`SmoothDamp`/`LateUpdate` — no Cinemachine package involved, or the project deliberately isn't using it for this camera.
- Negative trigger: `CinemachineCamera`/`CinemachineVirtualCamera` authoring, `CinemachineConfiner2D/3D`, `CinemachineImpulseSource/Listener`, or `CinemachineBrain` priority blending — that's `unity-cinemachine-authoring`'s scope; if the project has Cinemachine installed and the task is genuinely cinematic (priority-based shot blending, impulse-composited shake, confiner-quality bounds), route to that skill instead of hand-rolling an equivalent here.
- Negative trigger: screen-space shader distortion, chromatic aberration, or other post-process VFX — `shader-authoring`/`render-pipeline-urp-hdrp`.
- Negative trigger: UI safe-area/notch handling for different aspect ratios — UI/UX Programmer's scope.

## 4. How to use this skill
1. **Confirm the active render pipeline first** (Built-in/URP/HDRP, per `render-pipeline-urp-hdrp`) — it changes which camera-adjacent component actually holds the relevant settings: plain `Camera` fields under Built-in, `UniversalAdditionalCameraData` (renderer, post-processing toggle, camera stacking) under URP, `HDAdditionalCameraData`/Volume-driven settings under HDRP.
2. **Set projection deliberately.** Orthographic for 2D/isometric (`orthographicSize` = half the vertical view height in world units), perspective for 3D (`fieldOfView` in degrees, vertical FOV in Unity). Don't leave either at whatever the template default was — pick the value the design's framing actually needs.
3. **Set clip planes to the real visible range, not defaults left untouched.** A far plane far larger than the scene ever needs wastes depth-buffer precision and invites z-fighting at distance; a near plane too large clips geometry the camera should show up close. Size both to the actual scene scale.
4. **Use the culling mask to exclude irrelevant layers** from a given camera's render (e.g. a minimap camera skipping VFX/UI layers) — this reduces per-camera draw calls, consistent with the rendering-cost discipline in `performance-and-algorithms.md`.
5. **Coordinate conversions**: `Camera.WorldToScreenPoint`/`ScreenToWorldPoint`/`ScreenToViewportPoint` for UI-to-world or input-to-world mapping; `Camera.ScreenPointToRay` for click/tap picking, combined with `Physics.Raycast`/`Physics2D.Raycast`. In a hot path (continuous aim-raycast every frame), use the non-allocating overloads (`Physics.RaycastNonAlloc` with a reused `RaycastHit[]` buffer) instead of the allocating default — per the no-per-frame-allocation rule in `coding-principles.md`.
6. **Multi-camera setups**:
   - Split-screen: one `Camera` per player, each with its own `Camera.rect` (a `Rect` in normalized viewport space, e.g. left half `(0, 0, 0.5, 1)`).
   - Minimap/PIP: a second camera rendering to a `RenderTexture` (culling mask limited to what the minimap needs), displayed on a `RawImage`/UI element — don't render it full-screen redundantly.
   - URP Camera Stacking: a Base camera plus one or more Overlay cameras (`UniversalAdditionalCameraData.cameraStack`) instead of multiple independent full-screen cameras, when compositing layers (e.g. a 3D scene with a separately-rendered UI/effects layer) under URP specifically.
7. **Hand-rolled follow (no Cinemachine)**: update camera position in `LateUpdate`, after gameplay/physics has moved the target in `Update`/`FixedUpdate` — following in `Update` risks a frame of lag/jitter since target movement for that frame may not have happened yet. Use `Vector3.SmoothDamp` (explicit, tunable settle time, framerate-independent) rather than `Vector3.Lerp` with a raw speed constant, which is framerate-dependent.
8. **Hand-rolled bounds clamp**: compute the camera's visible half-extents from `orthographicSize * aspect` (orthographic) or the FOV-derived frustum at the target depth (perspective), then `Mathf.Clamp`/`Rect.Clamp` the camera position against the level's actual bounds — a fixed padding constant that isn't derived from the current view size breaks at a different aspect ratio.
9. **Hand-rolled shake**: offset the camera's position/rotation with decaying Perlin noise (`Mathf.PerlinNoise` sampled over time, amplitude decaying to zero) rather than pure `Random.Range` per frame, which reads as jittery static rather than a shake; always apply the offset on top of the camera's actual follow-resolved position (don't let shake state permanently drift the base position).
10. **Respect the Shared Core boundary.** Camera scripts read the Client layer's already-resolved target position/state (per `coding-principles.md`'s Shared Core integrity rule); they never reach into `Game.Core.*` to decide anything and never mutate gameplay state — a camera is strictly presentational.
11. **Performance**: cache the `Camera` reference once (`Awake`/`Start`, or a serialized field) — never call `Camera.main` inside `Update()`/`FixedUpdate()`/`LateUpdate()`, per `performance-and-algorithms.md`. Cache any frustum/bounds calculation that doesn't change frame-to-frame instead of recomputing it every call.
12. **Verify in Play Mode** across the project's actual target aspect ratios (e.g. ultra-wide PC vs. tall mobile portrait) — orthographic size, clip planes, and bounds clamping that look right at one aspect ratio commonly clip or over-reveal at another.

## 5. Specific goals / tasks this skill performs
- Configuring `Camera` projection, FOV/orthographic size, clip planes, culling mask, and clear flags/background per the project's confirmed pipeline.
- World/screen/viewport coordinate conversions and camera-driven raycasting (click-to-move, aim picking).
- Split-screen (`Camera.rect`), minimap/PIP (`RenderTexture`), and URP Camera Stacking multi-camera setups.
- Hand-rolled follow (`LateUpdate` + `SmoothDamp`), bounds clamping, and Perlin-noise shake scripting for cameras not driven by Cinemachine.
- Out of scope: any Cinemachine component or API (separate skill), shader/post-process screen VFX (`shader-authoring`/`render-pipeline-urp-hdrp`), UI safe-area adaptation.

## 6. Output format
```
## Camera Setup — <feature name>
- Pipeline confirmed: Built-in / URP / HDRP
- Projection: orthographic (size: <n>) / perspective (FOV: <n>°) — rationale
- Clip planes: near <n> / far <n> — sized to actual scene scale
- Culling mask: <layers included/excluded, and why>
- Behavior implemented: follow / bounds clamp / shake / coordinate conversion / multi-camera
- Multi-camera setup (if any): split-screen rects / render-texture minimap / URP stack
- Shared Core boundary: read-only target/state source confirmed — no gameplay mutation from camera code
- Aspect ratios verified: <list>
- Performance check: Camera reference cached outside hot path — yes/no; raycasts non-allocating — yes/no/n-a
- Known limitations: <...>
```

## 7. Examples
**Example 1**
- Input: "Add click-to-move: clicking the ground should raycast from the camera and move the player there."
- Output: cached the main `Camera` reference in `Awake`; on click, `Camera.ScreenPointToRay(Input.mousePosition)` into `Physics.RaycastNonAlloc` with a reused single-element `RaycastHit[]` buffer against a `Ground` layer mask; hit point handed to the Client-layer movement system (which itself calls into Shared Core) — the camera script never decides movement, only supplies the world point.

**Example 2**
- Input: "Add local 2-player split-screen, and a top-down minimap in the corner."
- Output: two `Camera`s each following one player (hand-rolled `LateUpdate`/`SmoothDamp`, no Cinemachine on this project), `Camera.rect` set to left/right halves; a third top-down camera with culling mask excluding UI/VFX layers, rendering to a `RenderTexture` displayed on a corner `RawImage`; verified at 16:9 and an ultra-wide monitor aspect.

## 8. Edge cases & guardrails
- Never leave orthographic size/FOV or clip planes at unexamined defaults — size them to the actual scene/design need.
- Never use an oversized far clip plane "just in case" — it costs depth-buffer precision and invites z-fighting.
- Update hand-rolled camera follow in `LateUpdate`, never `Update` — following in `Update` risks a frame of lag behind the target.
- Never use `Vector3.Lerp` with a raw speed constant for camera smoothing — it's framerate-dependent; use `SmoothDamp`.
- Use non-allocating raycast overloads for any camera-driven raycast that runs every frame or every input event at high frequency.
- Never let camera code read or write `Game.Core.*` state directly, or make a gameplay decision itself — it stays strictly presentational.
- Never call `Camera.main` inside a per-frame method — cache it once.
- Don't hand-roll a Cinemachine-equivalent (confiner-quality bounds, impulse-composited shake, priority blending) when the project has Cinemachine installed and the task is genuinely cinematic — route that to `unity-cinemachine-authoring` instead.
- Never tune bounds/framing against a single assumed aspect ratio when the project ships more than one target device class.
