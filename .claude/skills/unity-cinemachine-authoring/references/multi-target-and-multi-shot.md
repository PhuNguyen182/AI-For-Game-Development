# Multi-Target Framing and Automatic Shot Selection

Sources: [Target Groups](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineTargetGroup.html), [State-Driven Camera](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineStateDrivenCamera.html), [ClearShot](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineClearShot.html).
Covers: SKILL.md §4 — **"Add group framing alongside a target group when the shot must actually widen"**, **"Give ClearShot children something to evaluate"**.

Both of these delegate a decision the camera would otherwise need scripting
for — where to point when there are several targets, and which shot to use
when conditions change. Both also have a component they need alongside them
that is easy to omit, and in both cases the omission produces a rig that runs
and looks like it is ignoring its own configuration.

## Target groups

| Piece | What it decides | Source |
|---|---|---|
| `CinemachineTargetGroup` | Supplies a single position and bounding volume derived from its members, usable as a Follow or LookAt target by any camera | [CinemachineTargetGroup](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/api/Unity.Cinemachine.CinemachineTargetGroup.html) |
| Member Weight | How much that member pulls the group position. Weight zero excludes it without removing it, which is the clean way to drop a downed player from the framing | [CinemachineTargetGroup](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineTargetGroup.html) |
| Member Radius | The member's visual size, so the group's bounds account for a large boss rather than treating it as a point | [CinemachineTargetGroup](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineTargetGroup.html) |
| Group framing extension | **The group alone does not widen the shot** — it only recentres it. Adjusting distance or field of view to fit the group's bounds takes a framing extension on the camera, and its absence looks like the framing ignoring a target that has walked away | [CinemachineTargetGroup](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineTargetGroup.html) |
| `AddMember` / `RemoveMember` | Runtime membership. A destroyed member must be removed, not merely disabled, or it keeps contributing a stale position | [CinemachineTargetGroup](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/api/Unity.Cinemachine.CinemachineTargetGroup.html) |

## Automatic selection

| Component | How it chooses, and what it needs | Source |
|---|---|---|
| `CinemachineStateDrivenCamera` | Maps an Animator's states to child cameras. Per-state minimum duration and wait time exist to stop rapid state changes flickering the camera — leaving them at zero makes a twitchy state machine visible in the framing | [State-Driven Camera](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineStateDrivenCamera.html) |
| The Animator behind it | Authored by `unity-animation`. This component consumes states; it does not define them | [State-Driven Camera](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineStateDrivenCamera.html) |
| `CinemachineClearShot` | Picks the child with the best shot quality. **Quality comes from a Deoccluder on each child** — children without one report no quality signal, so ClearShot falls back to priority and appears to ignore obstruction entirely | [ClearShot](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineClearShot.html) |
| Both as parents | Each is a camera that owns children, so its own Priority competes at the Brain level while it resolves internally — two nested layers of selection, not one | [State-Driven Camera](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineStateDrivenCamera.html) |
