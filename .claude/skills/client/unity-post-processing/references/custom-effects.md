# Custom Full-Screen Effects in URP

Sources: [Custom post-processing in URP](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/post-processing/custom-post-processing.html), [Full Screen Pass Renderer Feature reference](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/renderer-features/renderer-feature-full-screen-pass.html), [Injection points reference](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/customize/custom-pass-injection-points.html).
Covers: SKILL.md §4 — **"Choose the custom-effect path by whether the effect needs blendable parameters"**, **"Pick the injection point from what the pass reads and whether its output should be graded"**.

Both documented authoring paths end at the same mechanism: a
`ScriptableRendererFeature` that creates a pass in `Create()` and enqueues it
in `AddRenderPasses()` every frame. What separates them is only whether a
`VolumeComponent` sits in front of that pass supplying blendable parameters —
which is a real cost, and buys nothing for an effect that is either on or off.

## The two paths

| Path | What it costs, what it buys | Source |
|---|---|---|
| Low-code — `FullScreenPassRendererFeature` plus a Fullscreen Shader Graph material | No C# at all. Assign the material, pick an injection point, tick the buffers it needs. No Volume blending, so intensity is baked into the material or set by writing to it directly | [Low-code custom effect](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/post-processing/post-processing-custom-effect-low-code.html) |
| Scripted — custom `ScriptableRendererFeature` and `ScriptableRenderPass` plus a `VolumeComponent` | Two scripts, scaffolded by `Assets > Create > Scripting > URP Post-process Volume Scripts`. The feature reads the resolved `VolumeStack`, pushes values into the material, and the effect blends per-Volume like a built-in override | [Custom effect with Volume support](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/post-processing/custom-post-processing-with-volume.html) |

The decision is whether anything must **blend** — fade in over a region, ramp
with a gameplay value, differ between two overlapping volumes. If the effect
is a constant, the low-code path is finished before the scripted one is
scaffolded.

## Injection point

| Consideration | What it decides | Source |
|---|---|---|
| Before versus after post-processing | An effect injected **before** post-processing is subsequently tonemapped and colour-graded by the rest of the stack; one injected **after** is not. The same shader therefore looks correct in one project and blown out in another | [Injection points reference](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/customize/custom-pass-injection-points.html) |
| What the pass reads | The point must come after whatever the pass samples has been written — a pass reading transparents cannot run before them, and the failure is a stale or empty target rather than an error | [Injection points reference](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/customize/custom-pass-injection-points.html) |
| Available stages | Shadows, prepasses, opaques, skybox, transparents, post-processing — set through `renderPassEvent` on a scripted pass or `injectionPoint` on the Full Screen Pass feature | [Injection points reference](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/customize/custom-pass-injection-points.html) |

## Buffer requirements

| Member | What it decides | Source |
|---|---|---|
| `fetchColorBuffer` | Whether the pass receives the current screen colour. Required for anything that distorts or recolours what is already there, and it forces an intermediate texture — the cost that matters on a tile-based GPU | [Full Screen Pass reference](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/renderer-features/renderer-feature-full-screen-pass.html) |
| `requirements` / `ConfigureInput()` | Declares depth, normals, colour, or motion vectors as inputs. Each one asked for is generated whether or not the shader ends up sampling it | [ScriptableRenderPass API](https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.6/api/UnityEngine.Rendering.Universal.ScriptableRenderPass.html) |
| `requiresIntermediateTexture` | Forces URP off the direct-to-backbuffer path — the same resolve cost, stated explicitly | [ScriptableRenderPass API](https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.6/api/UnityEngine.Rendering.Universal.ScriptableRenderPass.html) |
| `bindDepthStencilAttachment` | Binds depth/stencil for a pass that tests against it rather than only reading colour | [Full Screen Pass reference](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/renderer-features/renderer-feature-full-screen-pass.html) |

## API surface

| Type | What it is for | Source |
|---|---|---|
| `ScriptableRendererFeature` | The injectable unit added to a Renderer asset — `Create()` builds the pass once, `AddRenderPasses()` enqueues it per camera per frame | [ScriptableRendererFeature API](https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.6/api/UnityEngine.Rendering.Universal.ScriptableRendererFeature.html) |
| `FullScreenPassRendererFeature` | The ready-made feature the low-code path uses — `passMaterial`, `injectionPoint`, `requirements`, `fetchColorBuffer` | [FullScreenPassRendererFeature API](https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.6/api/UnityEngine.Rendering.Universal.FullScreenPassRendererFeature.html) |
| `ScriptableRenderPass` | The pass itself — `renderPassEvent`, `RecordRenderGraph()` on the Render Graph path, `ConfigureInput()` | [ScriptableRenderPass API](https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.6/api/UnityEngine.Rendering.Universal.ScriptableRenderPass.html) |
| `Blitter` | The blit utility a pass composites through, rather than a hand-rolled `Graphics.Blit` | [Blitter API](https://docs.unity3d.com/Packages/com.unity.render-pipelines.core@17.6/api/UnityEngine.Rendering.Blitter.html) |
| `RTHandle` | The camera-size-scaling render target wrapper a pass reads and writes | [RTHandle API](https://docs.unity3d.com/Packages/com.unity.render-pipelines.core@17.6/api/UnityEngine.Rendering.RTHandle.html) |

## Not the recommended path

`RenderPipelineManager.beginCameraRendering` can enqueue a pass directly, and
the Manual page documenting it explicitly recommends a Renderer Feature
instead for anything spanning multiple cameras, scenes, or the project — the
callback is a one-off technique, not a way to ship a reusable effect.
Registering the feature on the Renderer asset the target quality tier
actually uses is `unity-urp-rendering`'s concern, and getting it wrong is
silent.
