# Root Links — Cinemachine 3.1 Documentation Roots

Source: the Cinemachine 3.1 package manual and API, linked below.
Covers: SKILL.md §4 — **"Confirm the installed Cinemachine major version before writing a single type name"**.

| Root | Holds | Source |
|---|---|---|
| Manual | Every component page, the blending model, Impulse, Timeline integration, Channels | [Cinemachine 3.1 manual](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/index.html) |
| Scripting API | `Unity.Cinemachine` types and members | [Cinemachine 3.1 API](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/api/index.html) |

## Version pin

Every link in this folder is pinned to `@3.1`. Swap the segment if the project
installs a different 3.x version; page slugs are stable across nearby minors.
A project on Cinemachine 2 is a different product for authoring purposes — the
rename table below is for reading its code, not for porting by search and
replace, because the component model changed underneath the names.

## Generation 2 to generation 3 renames

| Cinemachine 2 | Cinemachine 3 | Source |
|---|---|---|
| Namespace `Cinemachine` | Namespace `Unity.Cinemachine` — the reason a version mismatch shows up as a missing type rather than a changed signature | [Cinemachine 3.1 API](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/api/index.html) |
| `CinemachineVirtualCamera` with Body and Aim slots | `CinemachineCamera` with separate Position Control and Rotation Control components added to the GameObject | [CinemachineCamera](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineCamera.html) |
| Transposer | `CinemachineFollow` | [Position Control](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachinePositionControl.html) |
| Framing Transposer | `CinemachinePositionComposer` | [CinemachinePositionComposer](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachinePositionComposer.html) |
| Composer | `CinemachineRotationComposer` | [Rotation Control](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineRotationControl.html) |
| Collider extension | `CinemachineDeoccluder` | [CinemachineDeoccluder](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineDeoccluder.html) |
| FreeLook camera | A `CinemachineCamera` with `CinemachineOrbitalFollow` and its three-ring orbit | [Position Control](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachinePositionControl.html) |
| Input read inside the camera | A separate input axis controller component — see [position-and-rotation-control.md](position-and-rotation-control.md) | [Position Control](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachinePositionControl.html) |

## What this package does not own

| Concern | Owner | Source |
|---|---|---|
| Projection, field of view, clip planes, culling mask, viewport rect | `unity-camera-fundamentals` — Cinemachine drives the transform and can drive lens values, but those fields live on the `Camera` | [CinemachineBrain](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineBrain.html) |
| The Animator states a State-Driven camera reacts to | `unity-animation` | [State-Driven Camera](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineStateDrivenCamera.html) |
| Reading the device behind an orbit axis | `unity-input-system` | [Position Control](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachinePositionControl.html) |
| Timeline itself, outside the Cinemachine shot track | No dedicated skill — route to `unity-engineer` | [Timeline integration](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineTimeline.html) |
