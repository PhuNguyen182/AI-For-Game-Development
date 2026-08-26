---
name: unity-cinemachine-authoring
description: >
  Technique for authoring camera behaviour with Cinemachine 3: the
  `CinemachineBrain` that drives the render camera, `CinemachineCamera`
  composed from a Position Control and Rotation Control pair, priority and
  blend resolution, `CinemachineConfiner2D` and `CinemachineConfiner3D`
  bounds, `CinemachineDeoccluder` obstruction handling, Impulse sources and
  listeners for shake, `CinemachineTargetGroup` with group framing,
  State-Driven and ClearShot selection, Timeline shot clips, and Channels for
  split screen. Use for any `Cinemachine` component or API. Not for: plain
  `Camera` and `Transform` scripting (`unity-camera-fundamentals`); the
  Animator a State-Driven camera reads (`unity-animation`); axis input
  (`unity-input-system`); screen effects (`unity-post-processing`).
---

# Unity Cinemachine Authoring — Procedural Camera Behaviour on Cinemachine 3

## Bundled resources

### References
Read-only context, loaded on demand so SKILL.md itself stays short.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Manual and API roots, the version pin, and the Cinemachine 2 to 3 rename map | Starting any task here, or existing code uses names that no longer exist |
| [camera-and-brain.md](references/camera-and-brain.md) | Brain placement, update methods, priority resolution, blends | Setting up the rig, or a transition cuts when it should blend |
| [position-and-rotation-control.md](references/position-and-rotation-control.md) | The control pairs, damping, dead and soft zones, orbital input, spline dolly | Composing a camera, or its motion feels wrong rather than broken |
| [bounds-and-obstruction.md](references/bounds-and-obstruction.md) | Confiner 2D and 3D, the bake cache, Deoccluder strategies | The camera must stay inside a region or stop clipping through geometry |
| [impulse-shake.md](references/impulse-shake.md) | Impulse sources, listeners, channels, distance falloff | Adding shake, or an impulse fires and nothing moves |
| [multi-target-and-multi-shot.md](references/multi-target-and-multi-shot.md) | Target groups, group framing, State-Driven and ClearShot selection | Several targets must stay framed, or the shot should choose itself |
| [timeline-and-channels.md](references/timeline-and-channels.md) | Timeline shot clips and Cinemachine Channels | Sequencing a cutscene, or two players' cameras interfere |

## 1. Objective
Author camera behaviour through Cinemachine's component model so that shots blend, bounds hold, and shake survives a camera switch — none of which a hand-written equivalent does once more than one camera exists. The failure mode this prevents is a rig that works in isolation and breaks on transition: a hand-clamped position fighting a Confiner, a shake bolted to one camera that stops mid-blend, a priority change bypassed by an active toggle.

## 2. Role
Act as the Cinemachine specialist — the Brain, the cameras, their control pairs, and the extensions around them. You do not configure the underlying `Camera` component's projection or pipeline settings, author the Animator a State-Driven camera reads, or read input devices.

## 3. When to invoke this skill
- Building a `CinemachineCamera`: follow and look-at targets, a Position Control and Rotation Control pair, damping and framing zones.
- Placing and configuring the `CinemachineBrain`, or tuning how one camera hands over to another.
- A camera transition cuts when it should blend, or blends when it should cut.
- Confining the camera to a region, or stopping it clipping through level geometry.
- Adding shake that keeps working across camera switches, through Impulse sources and listeners.
- Framing several moving targets together, or letting shot selection follow an Animator state or the least obstructed view.
- Sequencing cutscene shots through Timeline's Cinemachine track, or separating split-screen players' cameras.
- Negative trigger: camera work on a project deliberately not using Cinemachine for that camera — that is `unity-camera-fundamentals`; do not introduce the package to a scene that has stayed off it.
- Negative trigger: the `Camera` component's own projection, clip planes, culling mask, or viewport rect — that is `unity-camera-fundamentals`; Cinemachine drives the transform, not those fields.
- Negative trigger: authoring the Animator Controller and its states — that is `unity-animation`; a State-Driven camera consumes those states.
- Negative trigger: reading a stick, mouse, or touch to drive an orbit — that is `unity-input-system`, which feeds the axis controller this skill attaches.
- Negative trigger: screen-space effects, vignettes, or colour shifts during a shot — that is `unity-post-processing`.
- Negative trigger: Timeline track and clip authoring beyond the Cinemachine shot track — no skill owns general Timeline; route it to `unity-engineer`.
- Negative trigger: the gameplay rule a camera reacts to — that lives in `Game.Core.*` per `coding-principles.md`; Cinemachine targets are read-only references to already-resolved Client state.

## 4. How to use this skill
1. **Confirm the installed Cinemachine major version before writing a single type name** — Cinemachine 3 renamed the namespace to `Unity.Cinemachine` and replaced `CinemachineVirtualCamera` and its Body and Aim model with `CinemachineCamera` plus separate control components. The two generations do not interoperate, and [root-links.md](references/root-links.md) carries the rename map for reading existing code.
2. **Put exactly one `CinemachineBrain` on the rendering `Camera`, never on a `CinemachineCamera`** — and treat it as owning that camera's transform, since it overwrites position and rotation every frame. Any other script writing that transform loses silently, per [camera-and-brain.md](references/camera-and-brain.md).
3. **Match the Brain's Update Method to what the follow target is moved by** — a target moved by physics needs Fixed Update, and leaving the Brain on Late Update against it produces judder that no damping value removes.
4. **Switch cameras by changing Priority, never by toggling GameObjects active** — the Brain resolves the live camera by priority and blends into it; deactivating one produces an unblended cut. Where two cameras share a priority the most recently activated wins, so equal priorities are not a tie, they are an ordering dependency.
5. **Set damping as the seconds of lag the shot should have**, per [position-and-rotation-control.md](references/position-and-rotation-control.md) — it is a time, not a strength, and it is per axis, which is what lets a camera track horizontally tightly while easing vertically.
6. **Frame with the composer's dead and soft zones rather than tighter damping** — the dead zone is where the target moves without moving the camera, and widening it removes the constant micro-motion that damping only slows down.
7. **Attach an input axis controller when an orbital camera must respond to the player** — in Cinemachine 3 the orbit's axes are decoupled from input, so an `CinemachineOrbitalFollow` without one is fully functional and completely unresponsive. The device reading behind it is `unity-input-system`'s.
8. **Use `CinemachineConfiner2D` for what the camera sees and `CinemachineConfiner3D` for where it is**, per [bounds-and-obstruction.md](references/bounds-and-obstruction.md) — the 2D confiner clamps the visible area against a baked shape, so it must be re-baked when the shape or the camera's view size changes, through `InvalidateBoundingShapeCache()`.
9. **Give the Deoccluder a collide-against mask instead of leaving it on Everything**, per [bounds-and-obstruction.md](references/bounds-and-obstruction.md) — otherwise the camera avoids triggers, props, and the player's own collider, which reads as the camera lurching for no reason.
10. **Shake through Impulse, and check the channel before assuming the impulse failed**, per [impulse-shake.md](references/impulse-shake.md) — a source and a listener on mismatched channels produce no motion and no warning, and a listener lives on a specific camera, so a camera without one goes still the moment it becomes live.
11. **Add group framing alongside a target group when the shot must actually widen**, per [multi-target-and-multi-shot.md](references/multi-target-and-multi-shot.md) — a `CinemachineTargetGroup` only supplies a combined position and bounds; nothing zooms out until a framing extension acts on them.
12. **Give ClearShot children something to evaluate** — shot quality comes from a Deoccluder on each child, so a ClearShot whose children have none falls back to priority and appears to ignore obstruction entirely.
13. **Sequence cutscenes with Timeline's Cinemachine shot clips rather than scripted priority changes**, per [timeline-and-channels.md](references/timeline-and-channels.md) — the clip overrides the Brain's resolution for its duration and blends through clip overlap, which is why a scripted sequence and a Timeline both running fight each other.
14. **Give each split-screen player its own Channel and matching Brain mask** — Cinemachine resolves priority per channel, so a shared channel makes one player's camera change decide the other's.
15. **Keep the camera presentational** — follow and look-at targets are read-only references to already-resolved Client state, and the rule that decides when a shot changes lives in `Game.Core.*` per `coding-principles.md`'s Shared Core integrity rule.

## 5. Specific goals / tasks this skill performs
- Brain placement, update method, priority resolution, and default or per-pair blends.
- Composing cameras from Position and Rotation Control pairs, with damping and framing zones tuned to the shot.
- Orbital cameras including their axis controller wiring, and spline dolly shots.
- Bounds through Confiner 2D or 3D, including cache invalidation, and obstruction handling through the Deoccluder.
- Impulse-based shake across camera switches, including channel setup.
- Multi-target framing with target groups plus a framing extension, and automatic shot selection through State-Driven or ClearShot.
- Timeline shot sequencing and per-player Cinemachine Channels.
- Out of scope: the `Camera` component's own fields and plain transform camera scripting (`unity-camera-fundamentals`); Animator authoring (`unity-animation`); input devices (`unity-input-system`); screen effects (`unity-post-processing`); general Timeline authoring (`unity-engineer`); the gameplay rule behind a shot change (`csharp-engineer`).

## 6. Output format
```
## Cinemachine — <feature name>
- Version confirmed: <package version, and whether existing code is generation 2 or 3>
- Brain: <on which Camera, Update Method and why, default blend>
- Cameras: <name — Position Control / Rotation Control — damping and zone choices>
- Priority model: <values, what changes them, and any deliberate equal-priority ordering>
- Blends: <default, or per-pair settings and the feel each targets>
- Bounds / obstruction: <Confiner type, bake invalidation plan / Deoccluder strategy and mask>
- Shake: <sources, listeners, channel, what fires it>
- Multi-target / multi-shot: <target group and framing extension / State-Driven / ClearShot — or "single camera">
- Timeline: <shot track and clips — or "none">
- Channels: <per-player assignment — or "single channel">
- Verified in Play Mode: <transitions, impulse across a switch, bounds at each target aspect ratio>
- Layer: <Game.Client.* camera GameObjects and assets>
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what the delivered rig does not cover>
- Latent concerns: <failure modes not yet triggered: assumptions that hold only under current conditions, thresholds not yet reached, trade-offs knowingly deferred>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: "Third-person follow camera that doesn't clip through walls and shakes when the player is hit."
- Output: one `CinemachineCamera` with `CinemachineOrbitalFollow` and `CinemachineRotationComposer`, plus the axis controller — without it the orbit would have been inert against player input, which reads as a broken camera rather than a missing component. `CinemachineDeoccluder` with a collide-against mask limited to level geometry, since Everything would have made it avoid the player's own collider. Impulse listener on the camera and a source on the hit handler, on a named channel rather than the default, so later ambient shakes can be kept separate. Brain set to Fixed Update because the player is a `Rigidbody`.

**Example 2**
- Input: "Boss camera should frame the player and the boss together, and cut to an intro shot when the fight starts."
- Output: `CinemachineTargetGroup` with both as weighted members, and a group framing extension on the combat camera — the group alone would have re-centred the shot without ever widening it, which looks like the framing ignoring one target. Intro shot sequenced as a Timeline Cinemachine shot clip rather than a scripted priority change, so the cut timing is designer-editable and the two systems do not both drive the Brain. Blend back to the combat camera tuned as a per-pair setting rather than moving the project default, which every other transition also uses.

**Example 3**
- Input: "Impulse fires on explosion but the camera never moves."
- Output: the source and the listener were on different Impulse channels, which produces no motion and no warning — the same silent shape as a mismatched rendering layer. Matched the channel and confirmed the listener sits on the camera that is actually live during the explosion, since a listener is per camera and the rig switches to a scripted shot at that moment.

## 8. Edge cases & guardrails
- Never mix generation 2 and generation 3 type names — the namespace and the component model both changed, and old code compiles against neither by accident.
- Never place a Brain on a `CinemachineCamera`, or more than one on a render camera.
- Never write a camera's transform from another script while a Brain drives it — the Brain overwrites it every frame and the other script simply loses.
- Never leave the Brain's Update Method unexamined when the follow target is physics-driven — the judder is timing, not damping.
- Never force a shot change with `SetActive` — priority is what the Brain blends on.
- Never treat equal priorities as neutral — the most recently activated wins, which makes activation order a hidden dependency.
- Never tighten damping to remove framing jitter — widen the dead zone; damping only slows the same motion down.
- Never ship an orbital camera without its axis controller — it is fully configured and completely unresponsive.
- Never let a Confiner 2D shape or the camera's view size change without invalidating the bake cache.
- Never leave a Deoccluder colliding against Everything — it will avoid triggers and the player.
- Never assume an Impulse works because it fires — check the channel, and check the live camera has a listener.
- Never expect a target group alone to widen the shot — it supplies bounds; a framing extension acts on them.
- Never build a ClearShot without Deoccluders on its children — it has no quality signal and silently falls back to priority.
- Never drive a cutscene from both a Timeline shot track and a script changing priority — they resolve the same thing and fight.
- Never share one Channel across split-screen players — priority resolves per channel.
- Never hand-roll a clamp or a Perlin shake on a Cinemachine-driven camera — both break at the first blend; that work belongs to `unity-camera-fundamentals` only on cameras Cinemachine does not drive.
- Never let a Cinemachine component read or drive `Game.Core.*` — targets are read-only Client references.
