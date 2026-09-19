# Root Links — Camera Documentation Roots

Source: the Unity Manual and Scripting API roots listed below.
Covers: SKILL.md §4 — **"Confirm which component actually owns the setting on this pipeline"**.

The `Camera` component is shared across every render pipeline, but each SRP
adds a sibling component holding the settings that pipeline introduced. A
field missing from the Inspector is usually on the sibling, not absent.

| Root | Holds | Source |
|---|---|---|
| Manual — Cameras | Camera concepts, the Inspector reference, physical cameras, multiple cameras, render textures | [Cameras](https://docs.unity3d.com/Manual/Cameras.html) |
| API — `Camera` | Every camera field and the conversion and raycast helpers | [Camera](https://docs.unity3d.com/ScriptReference/Camera.html) |
| Per-pipeline sibling | `UniversalAdditionalCameraData` under URP, `HDAdditionalCameraData` under HDRP — renderer choice, stacking, post-processing toggle, anti-aliasing | [Camera component reference for URP](https://docs.unity3d.com/Manual/urp/camera-component-reference.html) |

## Version pin

Manual and Scripting API links here are unversioned and resolve to the current
documentation set rather than a pinned Editor version. Any default value
quoted in this folder was read at the time of writing — confirm a specific
number against the installed Editor before relying on it.

## Ownership boundaries

| Concern | Owner | Source |
|---|---|---|
| Camera stacking, the renderer a camera uses, per-camera pipeline settings | `unity-urp-rendering` — this skill sets the `Camera` fields, not the pipeline | [Camera component reference for URP](https://docs.unity3d.com/Manual/urp/camera-component-reference.html) |
| Post Processing toggle and everything a Volume drives | `unity-post-processing` | [Camera component reference for URP](https://docs.unity3d.com/Manual/urp/camera-component-reference.html) |
| Anti-aliasing mode | A Camera setting rather than an effect, but tuned as part of post-processing — `unity-post-processing` | [Camera component reference for URP](https://docs.unity3d.com/Manual/urp/camera-component-reference.html) |
| Cinemachine driving a camera's transform | `unity-cinemachine-authoring` — a Brain overwrites this skill's transform writes every frame | [Cameras](https://docs.unity3d.com/Manual/Cameras.html) |
