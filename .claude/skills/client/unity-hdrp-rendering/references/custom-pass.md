# Custom Pass Volumes

Covers SKILL.md step 4 (custom render passes in HDRP).

## Manual
- [Understand custom pass volumes](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/Custom-Pass-Volume-Workflow.html) — Mode (Global/Local/Camera), Priority, Fade Radius; Custom Pass Volumes don't blend like regular Volumes.
- [Create a Custom Pass in a C# script](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.3/manual/Custom-Pass-Scripting.html)

## Scripting API
- [`CustomPassVolume`](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/api/UnityEngine.Rendering.HighDefinition.CustomPassVolume.html) — `isGlobal`, `fadeRadius`, `injectionPoint`, `priority`, `GetActivePassVolumes`.
