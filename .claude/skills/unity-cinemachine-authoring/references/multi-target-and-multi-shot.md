# Multi-Target Framing and Shot Selection

Base: https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/ — pages `CinemachineTargetGroup.html`, `CinemachineStateDrivenCamera.html`, `CinemachineClearShot.html`.

## Target groups
| Piece | Rule |
|---|---|
| `CinemachineTargetGroup` | One position + bounds from its members; usable as Follow/LookAt |
| Member Weight | Pull on group position; 0 excludes without removing (drop a downed player) |
| Member Radius | Member's visual size so a large boss is not a point |
| Group framing extension | The group alone only recentres; fitting distance/FOV needs a framing extension on the camera. Absent → looks like a target is ignored |
| `AddMember` / `RemoveMember` | A destroyed member must be removed, not just disabled, or it contributes a stale position |

## Automatic selection
| Component | Rule |
|---|---|
| `CinemachineStateDrivenCamera` | Maps Animator states to child cameras. Per-state min duration / wait time stop flicker; zero exposes a twitchy state machine. States are authored in `unity-animation` |
| `CinemachineClearShot` | Picks best shot quality, which comes from a Deoccluder on each child; none → falls back to priority and seems to ignore obstruction |
| As parents | Their own Priority competes at the Brain while they select internally: two layers of selection |
