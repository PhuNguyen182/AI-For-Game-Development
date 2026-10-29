# Position and Rotation Control

Base: https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/ — pages `CinemachinePositionControl.html`, `CinemachineRotationControl.html`, `CinemachinePositionComposer.html`.

A `CinemachineCamera` has no behaviour of its own: the Position + Rotation Control pair is the shot.

| Position Control | Shot |
|---|---|
| `CinemachineFollow` | Fixed offset from target, optionally target-local; chase/third-person |
| `CinemachineOrbitalFollow` | Orbit on horizontal/vertical axes, three-ring radii (top/middle/bottom); replaces FreeLook |
| `CinemachinePositionComposer` | Keeps target at a screen position with dead/soft zones; 2D and screen-space framing |
| `CinemachineHardLockToTarget` | Exact target position, no smoothing; first-person head mount |
| `CinemachineSplineDolly` | Constrained to a spline; Automatic Dolly tracks the target's nearest point |

| Rotation Control | Shot |
|---|---|
| `CinemachineRotationComposer` | Keeps look-at target in a screen dead zone, easing through a soft zone |
| `CinemachineHardLookAt` | Points straight at target, no tolerance |
| `CinemachineSameAsFollowTarget` | Copies target rotation; vehicle or head bone |
| `CinemachinePanTilt` | Player-driven look decoupled from target; same axis controller as orbital |

| Framing control (`CinemachinePositionComposer`) | Rule |
|---|---|
| Damping | Approximate seconds to close the gap, per axis; raising it lengthens lag. Per-axis lets a platformer track X tightly and ease Y over jumps |
| Dead zone | Target moves, camera does not. Widen it to stop micro-motion; damping only slows it |
| Soft zone | Camera catches up at the damping rate; its edge is a hard limit the target cannot pass |
| Screen X/Y | Where the target sits in frame (centred vs leading its travel) |
| Lookahead | Good on steadily moving targets, unstable on ones that reverse often |

## Input
Orbital follow and pan-tilt expose axes; an **input axis controller** component supplies the values. Missing → no error, no motion. Device reading is `unity-input-system`'s.
