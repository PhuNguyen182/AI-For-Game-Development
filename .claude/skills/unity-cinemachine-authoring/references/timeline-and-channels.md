# Timeline Shots and Channels

Base: https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/ — pages `CinemachineTimeline.html`, `CinemachineChannels.html`.

| Piece | Rule |
|---|---|
| Cinemachine track / shot clips | Each clip names a camera + time range and **overrides** Brain priority for its duration; a script also changing priority fights it |
| Clip overlap | Blends come from overlapping clips, tuned on the timeline, not the Brain default |
| Handing back | After the last clip the Brain resumes priority; set the highest-priority camera deliberately |
| Channel on a camera | Which Brain may consider it; priority resolves **within** a channel, so a shared channel makes players' cameras compete |
| Channel mask on a Brain | Split screen: one Brain per player camera, each masked to that player's channel |
| Impulse channels | Separate partition ([impulse-shake.md](impulse-shake.md)); setting one does not set the other |

Viewport rects for split screen are `unity-camera-fundamentals`'s.
