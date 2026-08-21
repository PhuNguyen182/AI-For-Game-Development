# Volumes — Placement, Priority & Blending

Sources: [Understand volumes in URP](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/Volumes.html), [Set up a volume in URP](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/set-up-a-volume.html).
Covers: SKILL.md §4 — **"Place Volumes as pipeline configuration and hand the effects to their owner"**.

Volume *placement* — global versus local, priority, blend distance, and the
camera's volume mask. Which overrides go inside a profile, and how a custom
post-process effect is authored, belong to `unity-post-processing`; this file
deliberately stops at the boundary.

| Subject | What it decides | Source |
|---|---|---|
| Global Volume | Applies everywhere its layer is visible to the camera — the project-wide baseline | [Understand volumes](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/Volumes.html) |
| Local Volume | Requires a Collider set to trigger; applies only inside it, which is what scopes an effect to a room or region | [Set up a volume](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/set-up-a-volume.html) |
| Priority | Higher priority wins where volumes overlap — the mechanism for a local override beating the global baseline | [Understand volumes](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/Volumes.html) |
| Blend Distance | The fade band outside a local volume; zero produces a hard pop at the boundary | [Understand volumes](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/Volumes.html) |
| Volume Mask on the camera | The layer mask deciding which volumes a camera sees at all — a volume on an unmasked layer is simply ignored | [Understand volumes](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/Volumes.html) |
| Volume Profile | The asset holding the overrides; sharing one profile across volumes means editing it edits every user | [Set up a volume](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/set-up-a-volume.html) |
| Post-processing toggle | Post-processing must also be enabled on the camera, or profiles apply to nothing | [Add post-processing in URP](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/add-post-processing.html) |

**Critical caveat**: a volume that appears to do nothing usually is not
misconfigured internally — it is on a layer the camera's volume mask excludes,
outside a trigger collider, or losing to a higher-priority volume. Check
placement before opening the profile.
