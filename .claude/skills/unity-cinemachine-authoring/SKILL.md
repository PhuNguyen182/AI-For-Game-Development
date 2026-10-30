---
name: unity-cinemachine-authoring
description: "Cinemachine 3 (Unity.Cinemachine): CinemachineBrain, CinemachineCamera, Follow/OrbitalFollow/PositionComposer, Confiner2D/3D, Deoccluder, Impulse, TargetGroup, StateDriven/ClearShot, Channels. Use for authored camera behaviour."
user-invocable: false
---

# Unity Cinemachine Authoring

Not for: plain `Camera`/Transform scripting or Camera fields (`unity-camera-fundamentals`), the Animator a State-Driven camera reads (`unity-animation`), axis input devices (`unity-input-system`), screen effects (`unity-post-processing`), general Timeline authoring (no owning skill: flag the gap), a camera deliberately not on Cinemachine: do not introduce the package (`unity-camera-fundamentals`).
Docs: https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/index.html (API: `.../api/index.html`) — pinned 3.1; swap the segment for another 3.x. Cinemachine 2 is a different component model: read its code with the rename list below, never port by search-and-replace.

| Reference | Read when |
|---|---|
| [camera-and-brain.md](references/camera-and-brain.md) | Setting up the rig, or a transition cuts when it should blend |
| [position-and-rotation-control.md](references/position-and-rotation-control.md) | Choosing a control pair, or motion feels wrong rather than broken |
| [bounds-and-obstruction.md](references/bounds-and-obstruction.md) | Camera must stay in a region or clips through geometry |
| [impulse-shake.md](references/impulse-shake.md) | Adding shake, or an impulse fires and nothing moves |
| [multi-target-and-multi-shot.md](references/multi-target-and-multi-shot.md) | Several targets must stay framed, or the shot should choose itself |
| [timeline-and-channels.md](references/timeline-and-channels.md) | Cutscene shots, or split-screen cameras interfere |

Cinemachine 2 → 3: namespace `Cinemachine` → `Unity.Cinemachine` (mismatch shows as a missing type) · `CinemachineVirtualCamera` Body/Aim → `CinemachineCamera` + separate Position/Rotation Control components · Transposer → `CinemachineFollow` · Framing Transposer → `CinemachinePositionComposer` · Composer → `CinemachineRotationComposer` · Collider extension → `CinemachineDeoccluder` · FreeLook → `CinemachineOrbitalFollow` (three-ring orbit) · input inside the camera → separate input axis controller.

## Steps
1. **Confirm the installed Cinemachine major version before writing a type name** — 2 and 3 do not interoperate; never mix their names.
2. **One `CinemachineBrain` on the rendering `Camera`**, never on a `CinemachineCamera` or twice — it overwrites that transform every frame, so another script writing it silently loses ([camera-and-brain.md](references/camera-and-brain.md)).
3. **Leave Brain Update Method on Smart Update (Unity's recommended setting) and interpolate physics targets** — a Rigidbody target without interpolation judders under Late Update; Fixed Update only when interpolation must stay off.
4. **Switch shots by Priority, never `SetActive`** — deactivating cuts instead of blending. Equal priorities resolve by most recently activated: a hidden ordering dependency, not a tie.
5. **Pick the control pair; set damping in seconds** (per axis, not strength), per [position-and-rotation-control.md](references/position-and-rotation-control.md). Remove jitter by widening the dead zone, not tightening damping.
6. **An orbital or pan-tilt camera needs an input axis controller** — without it the camera is fully configured and unresponsive, no warning.
7. **Bounds**: Confiner2D bounds what the camera sees (shape changed: `InvalidateBoundingShapeCache()`, the expensive re-bake; orthographic size, FOV or aspect changed: `InvalidateLensCache()`); Confiner3D bounds where it is. Give the Deoccluder a Collide Against mask, never Everything ([bounds-and-obstruction.md](references/bounds-and-obstruction.md)).
8. **Shake via Impulse**; check channel match and that the live camera has a listener before assuming failure ([impulse-shake.md](references/impulse-shake.md)).
9. **Multi-target**: `CinemachineTargetGroup` only recentres; add a group framing extension to widen. ClearShot children need a Deoccluder each or it falls back to priority ([multi-target-and-multi-shot.md](references/multi-target-and-multi-shot.md)).
10. **Cutscenes via Timeline shot clips; split-screen via Channels** with one Brain mask per player ([timeline-and-channels.md](references/timeline-and-channels.md)). Never also script priority during a Timeline.
11. **Keep the camera presentational** — targets are read-only Client references; the rule that triggers a shot change lives in Core (`csharp-standards`), and Cinemachine never reads or drives it.
12. **Verify in Play Mode**: transitions, impulse across a camera switch, bounds at each target aspect ratio.

## Never
- Hand-roll a clamp or Perlin shake on a Cinemachine-driven camera — both break at the first blend.

## Output
```
## Cinemachine — <feature>
- Version confirmed: <package version; existing code generation 2 or 3>
- Brain / blends: <Camera, Update Method and why, default and per-pair blends>
- Cameras: <name — Position/Rotation Control — damping and zones>
- Priority model: <values, what changes them, deliberate equal-priority ordering>
- Bounds / obstruction: <Confiner type + bake invalidation / Deoccluder strategy + mask — or "none">
- Shake / Channels: <source, listener, channel / per-player assignment — or "none">
- Multi-target / Timeline: <choices — or "none">
- Verified in Play Mode: <what ran, or "not run">
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Impulse fires but the camera never moves" → source and listener on different channels (no warning), or the live camera has no listener; matched the channel and put a listener on the camera live at that moment.
