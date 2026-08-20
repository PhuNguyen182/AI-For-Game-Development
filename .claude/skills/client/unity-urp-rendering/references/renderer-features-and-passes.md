# Renderer Features & Scriptable Render Passes

Covers SKILL.md step 2 (custom render passes).

## Manual
- [Introduction to Scriptable Render Passes in URP](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/renderer-features/intro-to-scriptable-render-passes.html)
- [Inject a pass using a Scriptable Renderer Feature in URP](https://docs.unity3d.com/6000.1/Documentation/Manual/urp/renderer-features/scriptable-renderer-features/inject-a-pass-using-a-scriptable-renderer-feature.html)
- [Example of a complete Scriptable Renderer Feature in URP](https://docs.unity3d.com/6000.1/Documentation/Manual/urp/renderer-features/create-custom-renderer-feature.html)
- [Custom render pass workflow in URP](https://docs.unity3d.com/Manual/urp/renderer-features/custom-rendering-pass-workflow-in-urp.html)

## Scripting API
- [`ScriptableRendererFeature`](https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.3/api/UnityEngine.Rendering.Universal.ScriptableRendererFeature.html) — the asset you add to a Renderer; override `Create()` and `AddRenderPasses()`.
- [`UnityEngine.Rendering.Universal` namespace index](https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.3/api/UnityEngine.Rendering.Universal.html) — browse from here for `ScriptableRenderPass`, `RenderPassEvent`, and related injection-point types.
