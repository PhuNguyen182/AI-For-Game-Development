# Root Links — Post-Processing Documentation Roots

Source: the Unity 6000.5 Manual and the package API roots listed below.
Covers: the whole skill — provenance and version anchor for every file in
this folder.

Three separate systems answer to the phrase "post-processing" in Unity, one
per render pipeline, and they do not share an API. Everything this folder
cites resolves under one of the roots below; a page that does not belongs to
a pipeline this skill routes away rather than one it forgot to document.

| Root | Holds | Source |
|---|---|---|
| Manual — general | The pipeline-agnostic overview and the cross-pipeline availability table | [Post-processing and full-screen effects](https://docs.unity3d.com/6000.5/Documentation/Manual/post-processing-and-full-screen-effects.html) |
| Manual — URP | Volumes, the override catalog, custom post-processing, on-tile cost | [Post-processing in URP](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/post-processing-and-full-screen-effects-urp.html) |
| API — core RP | `Volume`, `VolumeProfile`, `VolumeComponent`, `VolumeManager`, parameter types, `Blitter`, `RTHandle` | [core RP 17.6 API](https://docs.unity3d.com/Packages/com.unity.render-pipelines.core@17.6/api/index.html) |
| API — URP | `ScriptableRendererFeature`, `FullScreenPassRendererFeature`, `ScriptableRenderPass` | [URP 17.6 API](https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.6/api/index.html) |
| Package — legacy PPv2 | `PostProcessLayer`, `PostProcessVolume`, `PostProcessProfile`, effect settings classes | [Post Processing 3.5 manual](https://docs.unity3d.com/Packages/com.unity.postprocessing@3.5/manual/index.html) |

## Version pin

Manual pages are pinned to `6000.5`, the SRP packages to `@17.6`, and the
legacy stack to `@3.5`. If the project installs different versions, swap those
segments — page slugs are stable across nearby minors, but the Render Graph
migration changed custom-pass behaviour across majors, so confirm the
installed URP version before relying on any pass-authoring detail here.

## Which system the project is on

| Pipeline | Post-processing system | Source |
|---|---|---|
| Built-in RP | The legacy Post Processing Stack v2 package only — Built-in has no Volume framework of its own | [Introduction to post-processing](https://docs.unity3d.com/6000.5/Documentation/Manual/PostProcessingOverview.html) |
| URP | The integrated Volume system. URP is **not compatible** with the PPv2 package — installing it there produces a stack that never renders | [Post-processing in URP](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/integration-with-post-processing.html) |
| HDRP | Its own Volume-driven framework, parallel to URP's and sharing its vocabulary — routed to `unity-hdrp-rendering` | [Render pipeline feature comparison](https://docs.unity3d.com/6000.5/Documentation/Manual/render-pipelines-feature-comparison.html) |

Two unrelated systems in Unity are called Volumes: this one
(`UnityEngine.Rendering.Volume`) and Adaptive Probe Volumes
(`UnityEngine.Rendering.ProbeVolume`, owned by `unity-lighting`). They share
a word and nothing else.

## Mobile cost

| Page | What it settles | Source |
|---|---|---|
| On-tile post-processing | A tile-based mobile GPU keeps the framebuffer in tile memory; enabling a post-processing stack forces a resolve out to system memory and back. That resolve is paid once the stack exists, largely independent of how many effects it holds | [On-tile post-processing](https://docs.unity3d.com/6000.5/Documentation/Manual/on-tile-post-processing.html) |
