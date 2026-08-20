# Multi-Target Framing & Multi-Shot Selection

Covers SKILL.md steps 9–10 (target groups, state-driven/clear-shot selection).

## Manual
- [Target Groups](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineTargetGroup.html) — `CinemachineTargetGroup`, framing multiple weighted targets at once.
- [State-Driven Camera](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineStateDrivenCamera.html) — switches active child camera off an Animator's state.
- [ClearShot](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineClearShot.html) — auto-picks the child camera with the least obstructed view.

## Scripting API
- [`CinemachineTargetGroup`](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/api/Unity.Cinemachine.CinemachineTargetGroup.html) — `AddMember`/`RemoveMember`, per-member weight/radius.
- [`CinemachineStateDrivenCamera`](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/api/Unity.Cinemachine.CinemachineStateDrivenCamera.html) / [`CinemachineClearShot`](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/api/Unity.Cinemachine.CinemachineClearShot.html)
