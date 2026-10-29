# Custom Full-Screen Effects in URP

Sources: Manual `urp/post-processing/custom-post-processing.html`, `urp/renderer-features/renderer-feature-full-screen-pass.html`, `urp/customize/custom-pass-injection-points.html`; URP 17.6 API.

Both paths end in a `ScriptableRendererFeature` (`Create()` builds the pass once, `AddRenderPasses()` enqueues per camera per frame). The difference is whether a `VolumeComponent` supplies blendable parameters.

| Path | Cost / benefit |
|---|---|
| Low-code: `FullScreenPassRendererFeature` + Fullscreen Shader Graph material | No C#. Assign material, injection point, buffers. No Volume blending; intensity is baked in or written to the material |
| Scripted: `ScriptableRendererFeature` + `ScriptableRenderPass` + `VolumeComponent` | Scaffold with `Assets > Create > Scripting > URP Post-process Volume Scripts`. Feature reads the resolved `VolumeStack`, pushes values to the material; blends per Volume |

Choose scripted only when something must blend (fade over a region, ramp with a gameplay value, differ between overlapping volumes).

## Injection point (`renderPassEvent` / `injectionPoint`)
- Before post-processing: the effect is tonemapped and graded. After: it is not. The same shader looks right in one project and blown out in another.
- The point must follow whatever the pass samples; a pass reading transparents cannot run before them, and the failure is a stale or empty target, not an error.
- Stages: shadows, prepasses, opaques, skybox, transparents, post-processing.

## Buffers
- `fetchColorBuffer`: current screen colour; required to distort/recolour; forces an intermediate texture (the tile-GPU cost).
- `requirements` / `ConfigureInput()`: depth, normals, colour, motion vectors; each is generated whether or not the shader samples it.
- `requiresIntermediateTexture`: forces off the direct-to-backbuffer path.
- `bindDepthStencilAttachment`: for a pass that tests depth/stencil.
- Composite through `Blitter` (not hand-rolled `Graphics.Blit`); targets are `RTHandle`; on the Render Graph path override `RecordRenderGraph()`.

Register the feature on the Renderer asset the target quality tier uses (`unity-urp-rendering`); a wrong asset fails silently.
