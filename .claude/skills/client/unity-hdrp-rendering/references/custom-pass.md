# Custom Pass Volumes

Sources: [Understand custom pass volumes](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/Custom-Pass-Volume-Workflow.html), [Create a Custom Pass in a C# script](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/Custom-Pass-Scripting.html).
Covers: SKILL.md §4 — **"Inject custom rendering through a `CustomPassVolume`, not a URP-style render pass"**.

HDRP's mechanism for injected rendering. It is volume-based rather than
renderer-based, which is the structural difference from URP's
`ScriptableRendererFeature` — and it behaves unlike a regular Volume in one
important way.

| Subject | What it decides | Source |
|---|---|---|
| `CustomPassVolume` | The component holding one or more passes; volume-scoped rather than attached to a renderer asset | [CustomPassVolume](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/api/UnityEngine.Rendering.HighDefinition.CustomPassVolume.html) |
| Mode — Global, Local, Camera | Global runs everywhere, Local inside its collider, Camera binds the pass to one camera | [Custom pass volume workflow](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/Custom-Pass-Volume-Workflow.html) |
| Injection point | Where in the HDRP frame the pass executes — chosen from what it needs to read and write | [Custom pass volume workflow](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/Custom-Pass-Volume-Workflow.html) |
| Priority | Orders several custom pass volumes affecting the same camera | [CustomPassVolume](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/api/UnityEngine.Rendering.HighDefinition.CustomPassVolume.html) |
| Fade Radius | The **only** softening a local custom pass volume has — these volumes do not blend the way regular Volumes do | [Custom pass volume workflow](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/Custom-Pass-Volume-Workflow.html) |
| Scripted `CustomPass` | Subclassing for passes beyond what the built-in types express | [Custom Pass scripting](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/Custom-Pass-Scripting.html) |
| `GetActivePassVolumes` | Queries which volumes are currently affecting rendering — the diagnostic when a pass is not visibly running | [CustomPassVolume](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/api/UnityEngine.Rendering.HighDefinition.CustomPassVolume.html) |

**Critical caveat**: expecting Volume-style blending is the usual surprise
here. A local custom pass volume switches on and off at its boundary, softened
only by Fade Radius, so an effect authored to "blend in" needs that radius set
deliberately rather than inherited from a regular Volume's mental model.
