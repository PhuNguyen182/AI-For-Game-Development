# CinemachineCamera & Brain

Covers SKILL.md steps 2, 4–5 (Brain placement, priority selection, blends).

## Manual
- [CinemachineCamera](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineCamera.html) — the CM3 camera-source GameObject (replaces the CM2 Virtual Camera), composed of a Procedural Position/Rotation Control pair.
- [CinemachineBrain](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineBrain.html) — lives on the actual `Camera` GameObject; resolves which `CinemachineCamera` is live by priority and drives the blend.
- [Blends](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineBlending.html) — default blend and per-pair custom blend curves via `CinemachineBlenderSettings`.

## Scripting API
- [`CinemachineBrain`](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/api/Unity.Cinemachine.CinemachineBrain.html) — `ActiveVirtualCamera`, `IsBlending`, default blend settings.
- [`CinemachineCamera`](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/api/Unity.Cinemachine.CinemachineCamera.html) — `Priority`, `Follow`, `LookAt`, `Target`.
- [`CinemachineVirtualCameraBase.Priority`](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/api/Unity.Cinemachine.CinemachineVirtualCameraBase.html) — the priority field driving which camera the Brain selects as live.
- [`CinemachineBlenderSettings`](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/api/Unity.Cinemachine.CinemachineBlenderSettings.html) — custom blend curve per camera pair.
