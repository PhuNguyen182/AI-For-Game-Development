# Timeline Shots and Cinemachine Channels

Sources: [Timeline integration](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineTimeline.html), [Cinemachine Channels](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineChannels.html).
Covers: SKILL.md §4 — **"Sequence cutscenes with Timeline's Cinemachine shot clips rather than scripted priority changes"**, **"Give each split-screen player its own Channel and matching Brain mask"**.

Both features answer the same underlying question — who decides which camera
is live — by taking that decision away from the Brain's default priority
resolution, in one case temporarily and in the other permanently by partition.

## Timeline

| Piece | What it decides | Source |
|---|---|---|
| Cinemachine track and shot clips | Each clip names a `CinemachineCamera` and a time range. For the clip's duration the track **overrides** the Brain's priority resolution, which is why a script also changing priority during a cutscene produces a fight neither side wins | [Timeline integration](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineTimeline.html) |
| Clip overlap | Blending between shots comes from overlapping clips, not from the Brain's default blend — so cutscene transitions are tuned on the timeline, where they can be scrubbed | [Timeline integration](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineTimeline.html) |
| Handing back | When the last clip ends the Brain resumes priority resolution, so what the game returns to is whatever priority is highest at that moment — worth setting deliberately rather than discovering | [Timeline integration](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineTimeline.html) |
| Timeline itself | Track and clip authoring outside the Cinemachine track has no dedicated skill — route it to `unity-engineer` | [Timeline integration](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineTimeline.html) |

## Channels

| Piece | What it decides | Source |
|---|---|---|
| Channel on a `CinemachineCamera` | Which Brain can consider it. Priority is resolved **within** a channel, so two players' cameras on the same channel compete with each other | [Cinemachine Channels](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineChannels.html) |
| Channel mask on a Brain | Which channels that Brain listens to. Split screen needs one Brain per player camera, each masked to that player's channel | [Cinemachine Channels](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineChannels.html) |
| Impulse channels | A separate, similarly named partition for shake signals — see [impulse-shake.md](impulse-shake.md). Setting one does not set the other | [Cinemachine Channels](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineChannels.html) |

The viewport rects that put each player's camera on part of the screen belong
to `unity-camera-fundamentals`; channels only decide which Cinemachine cameras
each Brain sees.
