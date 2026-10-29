# Renderer Features, Scriptable Render Passes and Render Graph

Sources (manual paths under the `Docs:` base): [p] `renderer-features/intro-to-scriptable-render-passes.html`, [i] `renderer-features/scriptable-renderer-features/inject-a-pass-using-a-scriptable-renderer-feature.html`, [w] `renderer-features/custom-rendering-pass-workflow-in-urp.html`, [e] `renderer-features/create-custom-renderer-feature.html` (worked example).

| Subject | Fact that decides |
|---|---|
| `ScriptableRendererFeature` | Added to a Renderer asset; `Create()` builds the pass instances, `AddRenderPasses()` enqueues them per camera |
| `ScriptableRenderPass` | What the pass reads, writes and when it runs [p] |
| Renderer asset scope | A feature belongs to one Renderer asset; a tier or camera referencing another Renderer never runs it, nothing logged [i] |
| `RenderPassEvent` | The injection point; it must satisfy the pass's data dependency, not its visual intent |
| `RecordRenderGraph` | Current authoring path: the pass declares its resources and the graph schedules and culls [w] |
| Resource declaration | Declare everything read and written; the graph can cull a pass whose output nothing consumes [w] |
| Compatibility Mode | Keeps the old `Execute` path for migration only, not a destination for new work [w] |

**Caveat:** both failures are silent. A feature on the wrong Renderer is never asked to run, and an `Execute`-only pass stops being invoked once Compatibility Mode is off; the console is clean and the effect is absent.
