# Position and Rotation Control

Sources: [Position Control](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachinePositionControl.html), [Rotation Control](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineRotationControl.html), [CinemachinePositionComposer](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachinePositionComposer.html).
Covers: SKILL.md §4 — **"Set damping as the seconds of lag the shot should have"**, **"Frame with the composer's dead and soft zones rather than tighter damping"**, **"Attach an input axis controller when an orbital camera must respond to the player"**.

A `CinemachineCamera` has no behaviour of its own — it is a target holder plus
whatever Position Control and Rotation Control components are added to it.
Picking the pair is picking the shot, and the two most common tuning mistakes
are treating damping as a strength rather than a duration, and reaching for it
where a framing zone is the actual control.

## Position Control

| Component | The shot it produces | Source |
|---|---|---|
| `CinemachineFollow` | Holds a fixed offset from the target, optionally in the target's local space. The straightforward third-person or chase rig | [CinemachineFollow](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/api/Unity.Cinemachine.CinemachineFollow.html) |
| `CinemachineOrbitalFollow` | Orbits the target on a horizontal and vertical axis, with a three-ring profile giving different radii at top, middle, and bottom. The generation-3 replacement for FreeLook | [CinemachineOrbitalFollow](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/api/Unity.Cinemachine.CinemachineOrbitalFollow.html) |
| `CinemachinePositionComposer` | Moves to keep the target at a chosen screen position, with dead and soft zones. The workhorse for 2D and any shot framed in screen space rather than world space | [CinemachinePositionComposer](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachinePositionComposer.html) |
| `CinemachineHardLockToTarget` | Exactly the target's position, no smoothing at all — a first-person head mount, not a camera rig | [Position Control](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachinePositionControl.html) |
| `CinemachineSplineDolly` | Constrains the camera to a spline. Automatic Dolly mode tracks the target's nearest point on it, which is how a rail follows a free-moving character | [CinemachineSplineDolly](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/api/Unity.Cinemachine.CinemachineSplineDolly.html) |

## Rotation Control

| Component | The shot it produces | Source |
|---|---|---|
| `CinemachineRotationComposer` | Rotates to keep the look-at target inside a screen-space dead zone, easing through a soft zone beyond it. The counterpart of the position composer for aim | [Rotation Control](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineRotationControl.html) |
| `CinemachineHardLookAt` | Points straight at the target with no smoothing or framing tolerance | [Rotation Control](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineRotationControl.html) |
| `CinemachineSameAsFollowTarget` | Takes the target's own rotation — the pairing for a camera mounted on a vehicle or a head bone | [Rotation Control](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineRotationControl.html) |
| `CinemachinePanTilt` | Player-driven look, decoupled from the follow target — a first-person or free-look aim, driven by the same axis controller as orbital follow | [Rotation Control](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineRotationControl.html) |

## Damping and framing zones

| Control | What it decides | Source |
|---|---|---|
| Damping | **Approximate seconds** for the camera to close the gap, specified per axis. Not a strength value — raising it lengthens the lag rather than tightening the follow, and per-axis is what lets a platformer track horizontally tightly while easing vertically over jumps | [CinemachinePositionComposer](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachinePositionComposer.html) |
| Dead zone | The screen region in which the target moves and the camera does not. Widening it is the correct fix for constant micro-motion; damping only slows that motion down | [CinemachinePositionComposer](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachinePositionComposer.html) |
| Soft zone | Beyond the dead zone, the camera catches up at a rate set by damping. Its edge is a hard limit the target cannot pass | [CinemachinePositionComposer](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachinePositionComposer.html) |
| Screen X / Screen Y | Where in frame the target sits — the difference between a centred shot and one that leads the character's direction of travel | [CinemachinePositionComposer](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachinePositionComposer.html) |
| Lookahead | Predicts target motion and offsets the framing ahead of it. Effective on a consistently moving target, unstable on one that reverses often | [CinemachinePositionComposer](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachinePositionComposer.html) |

## Input

Cinemachine 3 separates the axes from the device that drives them: an orbital
follow or pan-tilt exposes axes, and an **input axis controller** component
supplies their values. Without it the camera is completely configured and
completely unresponsive — no error, no warning, no motion. Reading the device
itself belongs to `unity-input-system`.
