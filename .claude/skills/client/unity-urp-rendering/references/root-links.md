# Root Links — URP 17.3 / Unity 6000.5 Manual

Source: the root index pages listed below, as provided for this skill.
Covers: the whole skill — provenance and version anchor for every file in
this folder.

Anchors every link in this folder to the Unity 6000.5 manual's URP section and
the Universal Render Pipeline package API, version 17.3. Anything this skill
cites resolves under one of these roots; anything that does not is out of
scope for the skill, not merely undocumented here.

| Root | Holds | Source |
|---|---|---|
| Manual — URP | Renderer Features, rendering paths, Volumes, 2D Renderer, camera stacking, asset settings | [Introduction to the Universal Render Pipeline](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/urp-introduction.html) |
| Scripting API | `ScriptableRendererFeature`, `ScriptableRenderPass`, `RenderPassEvent`, `UniversalAdditionalCameraData` | [URP Scripting API](https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.3/api/index.html) |

Every other link in this folder is a specific page under these two roots,
pinned to `6000.5` for manual pages and `@17.3` for API pages. If the project
installs a different URP version, swap the `@17.3` segment — page slugs are
stable across nearby minor versions, but the Render Graph migration in
particular changed behaviour between major versions, so confirm the installed
version before relying on a pass-authoring detail.
