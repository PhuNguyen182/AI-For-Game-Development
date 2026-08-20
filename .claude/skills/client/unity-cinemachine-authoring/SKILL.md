---
name: unity-cinemachine-authoring
description: >
  Technique for authoring camera behavior with the Cinemachine package
  (v3.x) — `CinemachineCamera` position/rotation control pairs, the
  `CinemachineBrain` priority/blend model, `CinemachineConfiner2D/3D`
  bounds, `CinemachineImpulseSource`/`CinemachineImpulseListener` shake,
  `CinemachineTargetGroup` multi-target framing, State-Driven/ClearShot
  camera selection, and Timeline-driven shot sequencing. Use this for any
  task involving a `CinemachineCamera`/`CinemachineVirtualCamera`,
  `CinemachineBrain`, or any `Cinemachine*` component/API. Do not use this
  for plain `Camera`/`Transform`-level scripting with no Cinemachine
  package involved — that's `unity-camera-fundamentals`. Do not use this
  for screen-space shader/post-process VFX (`shader-authoring`/
  `render-pipeline-urp-hdrp`) or UI safe-area handling (UI/UX Programmer's
  scope).
---

# Unity Cinemachine Authoring — Procedural Camera Behavior (v3.x)

Sources: see [references/](references/) for the Cinemachine Manual/Scripting API root links, split by topic — [root-links.md](references/root-links.md), [camera-and-brain.md](references/camera-and-brain.md), [position-and-rotation-control.md](references/position-and-rotation-control.md), [bounds-and-obstruction.md](references/bounds-and-obstruction.md), [impulse-shake.md](references/impulse-shake.md), [multi-target-and-multi-shot.md](references/multi-target-and-multi-shot.md), [timeline-and-channels.md](references/timeline-and-channels.md).

## 1. Objective
Author procedural camera behavior — follow, framing, bounds, obstruction avoidance, shake, multi-shot selection, cutscene sequencing — using Cinemachine's component model instead of hand-rolled `Transform` scripting, and configure the priority/blend system so shot transitions read intentionally rather than by accident.

## 2. Role
Act as the Cinemachine specialist: you compose `CinemachineCamera`s from Position/Rotation Control components, configure the `CinemachineBrain` on the actual render camera, set priorities and blends deliberately, and wire Confiner/Impulse/TargetGroup/State-Driven/ClearShot extensions to match what the Tech Spec's camera behavior actually needs — never a plain `Transform`-scripted substitute once Cinemachine is the project's chosen tool for the camera in question.

## 3. When to invoke this skill
- Setting up a `CinemachineCamera` (follow/look-at targets, Position Control such as `CinemachineFollow`/`CinemachineOrbitalFollow`/`CinemachineSplineDolly`, Rotation Control such as `CinemachineRotationComposer`).
- Configuring the `CinemachineBrain` on the scene's actual `Camera`, or tuning priority/blend behavior between multiple `CinemachineCamera`s.
- Adding bounds via `CinemachineConfiner2D`/`CinemachineConfiner3D`, or obstruction avoidance via `CinemachineDeoccluder`.
- Adding camera shake via `CinemachineImpulseSource` (emit, e.g. on hit/explosion) + `CinemachineImpulseListener` (react, on the live camera).
- Framing multiple moving targets at once via `CinemachineTargetGroup`.
- Multi-shot selection (`CinemachineStateDrivenCamera` off an Animator state, `CinemachineClearShot` picking the least-obstructed view) or cutscene shot sequencing via Timeline's `CinemachineTrack`/`CinemachineShot`.
- Negative trigger: any camera work where the project is **not** using Cinemachine for that camera — plain `Camera`/`Transform` follow, bounds-clamp, or shake scripting is `unity-camera-fundamentals`'s scope; don't introduce the Cinemachine package into a scene that has deliberately stayed off it.
- Negative trigger: screen-space shader distortion, chromatic aberration, or other post-process VFX — `shader-authoring`/`render-pipeline-urp-hdrp`.
- Negative trigger: UI safe-area/notch handling for different aspect ratios — UI/UX Programmer's scope.

## 4. How to use this skill
1. **Confirm the installed Cinemachine major version first.** The v3.x API (`CinemachineCamera`, `CinemachineBrain` on the render camera, separate Position/Rotation Control components) replaced v2's `CinemachineVirtualCamera`/Composer-as-one-component model — the two are not interchangeable. Check the manifest/Package Manager before writing code; this skill and `reference.md` target 3.1.
2. **Put exactly one `CinemachineBrain` on the actual rendering `Camera`** (never on the `CinemachineCamera`s themselves) — it's the component that resolves which `CinemachineCamera` is live by priority and drives the blend between them.
3. **Compose each `CinemachineCamera` from a Position Control + Rotation Control pair** matched to the actual shot need: `CinemachineFollow` (offset-follow) or `CinemachineOrbitalFollow` (orbit around target) for position; `CinemachineRotationComposer` (dead-zone/soft-zone framing) or `CinemachineHardLookAt` for rotation. Don't default to one pairing everywhere — pick per shot.
4. **Drive camera selection with `Priority`, not manual enable/disable toggling.** Set `CinemachineCamera.Priority` (or `CinemachineVirtualCameraBase.Priority`) so the Brain picks the intended camera; toggling `GameObject.SetActive` to force a switch bypasses the priority system and produces a hard cut where a blend was likely intended.
5. **Set blend behavior deliberately** — either the Brain's default blend, or a `CinemachineBlenderSettings` asset for a specific from/to camera pair that needs a different curve/duration (e.g. a snappy cut into an aim camera vs. a slow ease into a cutscene shot). Don't leave every transition on whatever the default happened to be if the design calls for a specific feel.
6. **Bounds**: `CinemachineConfiner2D` (2D collider-defined bounding shape, cached via `InvalidateBoundingShapeCache()` if the shape changes at runtime) or `CinemachineConfiner3D` (3D bounding volume) — don't hand-roll a `Mathf.Clamp`-based bounds script for a camera Cinemachine already drives; that duplicates behavior the Confiner does correctly, including camera-frustum-aware edge handling.
7. **Obstruction avoidance**: `CinemachineDeoccluder` when geometry can occlude the follow target (e.g. a wall between camera and player in 3D) — configure it to pull the camera in front of the obstruction rather than ignoring the occlusion.
8. **Shake via Impulse, not a hand-rolled Perlin offset on a Cinemachine-driven camera.** Fire `CinemachineImpulseSource.GenerateImpulse(...)` at the event source (explosion, hit, footstep) and let `CinemachineImpulseListener` on the live camera pick it up — this decouples "what caused the shake" from "which camera is currently live," so shake keeps working correctly across blends and camera switches, which a hand-rolled offset applied to one specific camera does not.
9. **Multi-target framing**: `CinemachineTargetGroup` with per-member weight/radius when more than one target must stay in frame together (e.g. two co-op players, or a player plus a boss) — weight controls how much a member pulls the framing, radius accounts for the member's visual size.
10. **Multi-shot logic**: `CinemachineStateDrivenCamera` when shot selection should follow an Animator's current state (e.g. combat-stance vs. exploration camera); `CinemachineClearShot` when it should follow whichever child camera currently has the least obstructed view. Don't hand-write a priority-juggling script to reimplement either — that's exactly what these components exist for.
11. **Cutscenes**: sequence shots via Timeline's `CinemachineTrack`/`CinemachineShot` rather than scripting priority changes on a timer — Timeline gives scrubbing, exact timing, and designer-editable cuts that a script-driven priority sequence doesn't.
12. **Split-screen with Cinemachine**: give each player's Brain/camera group its own Cinemachine Channel so one player's `CinemachineCamera` priority changes don't affect the other player's Brain.
13. **Respect the Shared Core boundary.** `CinemachineCamera` follow/look-at targets are Client-layer `Transform` references to already-resolved state; Cinemachine components never read from or drive `Game.Core.*` — same boundary `unity-camera-fundamentals` enforces for plain `Camera` scripting.
14. **Verify in Play Mode**: confirm priority-driven transitions blend as intended, Impulse propagates through a camera switch mid-shake, and Confiner bounds hold at the project's actual target aspect ratios.

## 5. Specific goals / tasks this skill performs
- Composing `CinemachineCamera`s from Position/Rotation Control components and configuring the `CinemachineBrain`.
- Priority and blend configuration between multiple `CinemachineCamera`s, including per-pair `CinemachineBlenderSettings`.
- Bounds (`CinemachineConfiner2D`/`3D`) and obstruction avoidance (`CinemachineDeoccluder`).
- Impulse-based camera shake (`CinemachineImpulseSource`/`CinemachineImpulseListener`).
- Multi-target framing (`CinemachineTargetGroup`) and multi-shot selection (`CinemachineStateDrivenCamera`/`CinemachineClearShot`).
- Timeline-driven cutscene shot sequencing (`CinemachineTrack`/`CinemachineShot`) and per-player Cinemachine Channels for split-screen.
- Out of scope: plain `Camera`/`Transform` scripting with no Cinemachine involved (`unity-camera-fundamentals`), shader/post-process screen VFX (`shader-authoring`/`render-pipeline-urp-hdrp`), UI safe-area adaptation.

## 6. Output format
```
## Cinemachine Setup — <feature name>
- Cinemachine version confirmed: <e.g. 3.1>
- Brain location: <on the actual render Camera — confirmed>
- Cameras: <CinemachineCamera name(s)> — Position Control: <...> / Rotation Control: <...>
- Priority/blend model: <priority values and rationale, default blend or CinemachineBlenderSettings pair(s)>
- Bounds/obstruction: Confiner2D/3D — <yes/no, config> ; Deoccluder — <yes/no, config>
- Shake: Impulse source(s)/listener — <event(s) that trigger it>
- Multi-target/multi-shot: TargetGroup / StateDrivenCamera / ClearShot — <config, or n/a>
- Split-screen channels: <n/a, or per-player channel assignment>
- Shared Core boundary: follow/look-at targets are Client-layer read-only references — confirmed
- Aspect ratios verified: <list>
- Known limitations: <...>
```

## 7. Examples
**Example 1**
- Input: "Set up a third-person follow camera for the player that avoids clipping through walls and shakes on hit."
- Output: one `CinemachineCamera` with `CinemachineOrbitalFollow` (position) + `CinemachineRotationComposer` (rotation), `CinemachineDeoccluder` added to pull the camera in front of blocking geometry, a `CinemachineImpulseSource` fired from the Client-layer hit-reaction handler on damage-taken and a `CinemachineImpulseListener` on the camera; `CinemachineBrain` confirmed on the scene's main `Camera`; verified the Deoccluder holds up against the level's actual wall geometry in Play Mode.

**Example 2**
- Input: "Add a boss-fight camera that frames both the player and the boss, and cuts to a scripted intro shot when the fight starts."
- Output: `CinemachineTargetGroup` with the player and boss as weighted members feeding a combat `CinemachineCamera`'s framing; a separate intro `CinemachineCamera` sequenced via a `CinemachineTrack`/`CinemachineShot` in a Timeline asset that plays on fight-start, with `Priority` on the combat camera set higher so the Brain blends back to it once the intro shot's Timeline clip ends; blend curve for the intro→combat cut set via a dedicated `CinemachineBlenderSettings` entry for a slower, more deliberate ease.

## 8. Edge cases & guardrails
- Never introduce Cinemachine into a scene/camera that's deliberately staying on plain `Camera`/`Transform` scripting — route that work to `unity-camera-fundamentals` instead.
- Never mix v2 (`CinemachineVirtualCamera`) and v3 (`CinemachineCamera`) authoring patterns in the same project without confirming which major version is actually installed — their APIs are not interchangeable.
- Never put more than one active `CinemachineBrain` driving the same render camera, and never put a `CinemachineBrain` on a `CinemachineCamera` itself.
- Never force a camera switch via `GameObject.SetActive`/manual enable-disable when a `Priority` change would let the Brain blend correctly — bypassing priority produces an unintended hard cut.
- Never hand-roll a `Mathf.Clamp` bounds script or a Perlin-noise shake offset on a camera Cinemachine already drives — use `CinemachineConfiner2D/3D` and Impulse respectively; a hand-rolled equivalent breaks the moment that camera blends with another one.
- Never let `CinemachineCamera` follow/look-at targets be anything other than a read-only reference to already-resolved Client-layer state — Cinemachine components never read from or drive `Game.Core.*`.
- Never script a priority-juggling shot sequence for a cutscene when Timeline's `CinemachineTrack`/`CinemachineShot` already covers it.
- Never share one Cinemachine Channel across split-screen players — each player's Brain needs its own channel or their camera priorities interfere with each other.
- Never tune Confiner bounds or framing against a single assumed aspect ratio when the project ships more than one target device class.
