# Renderer Features, Scriptable Render Passes & Render Graph

Sources: [Introduction to Scriptable Render Passes](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/renderer-features/intro-to-scriptable-render-passes.html), [Inject a pass using a Scriptable Renderer Feature](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/renderer-features/scriptable-renderer-features/inject-a-pass-using-a-scriptable-renderer-feature.html), [Custom render pass workflow in URP](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/renderer-features/custom-rendering-pass-workflow-in-urp.html).
Covers: SKILL.md §4 — **"Write custom passes against the Render Graph API"**, **"Register the feature on the Renderer the target tier actually uses"**, **"Choose the injection point from what the pass must read"**.

How a custom pass gets into the frame, and the two places it silently does not:
the wrong Renderer asset, and the superseded execution path. The shader the
pass runs is `shader-authoring`'s.

## The pieces

| Subject | What it decides | Source |
|---|---|---|
| `ScriptableRendererFeature` | The asset added to a Renderer; `Create()` builds the pass instances and `AddRenderPasses()` enqueues them per camera | [ScriptableRendererFeature](https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.3/api/UnityEngine.Rendering.Universal.ScriptableRendererFeature.html) |
| `ScriptableRenderPass` | The pass itself — what it reads, what it writes, and when it runs | [Intro to Scriptable Render Passes](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/renderer-features/intro-to-scriptable-render-passes.html) |
| Renderer asset scope | A feature belongs to one Renderer asset — a quality tier referencing a different Renderer never runs it, and nothing is logged | [Inject a pass](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/renderer-features/scriptable-renderer-features/inject-a-pass-using-a-scriptable-renderer-feature.html) |
| `RenderPassEvent` | The injection point; it must satisfy the pass's data dependency, not its visual intent | [UnityEngine.Rendering.Universal](https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.3/api/UnityEngine.Rendering.Universal.html) |
| Worked example | A complete feature and pass, end to end | [Create a custom renderer feature](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/renderer-features/create-custom-renderer-feature.html) |

## Render Graph versus Compatibility Mode

| Subject | What it decides | Source |
|---|---|---|
| `RecordRenderGraph` | The current authoring path — the pass declares its resources to the graph, which schedules and culls accordingly | [Custom render pass workflow](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/renderer-features/custom-rendering-pass-workflow-in-urp.html) |
| Resource declaration | A pass must declare what it reads and writes, because the graph can cull a pass whose output nothing consumes | [Custom render pass workflow](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/renderer-features/custom-rendering-pass-workflow-in-urp.html) |
| Compatibility Mode | Keeps the older `Execute`-based path working for migration only — it is not a supported destination for new work | [Custom render pass workflow](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/renderer-features/custom-rendering-pass-workflow-in-urp.html) |

**Critical caveat**: the two ways a pass fails here both produce silence rather
than an error. A feature on the wrong Renderer is never asked to run, and an
`Execute`-only pass stops being invoked once Compatibility Mode is off — in
both cases the console is clean and the effect is simply absent.
