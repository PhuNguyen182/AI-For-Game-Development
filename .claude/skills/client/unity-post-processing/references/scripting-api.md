# Scripting API Index — Post-Processing

Consolidated index of every class/API surface referenced by this skill's other reference files, organized by system. See the linked topic file for member details and usage context on each entry.

## URP Volume system (`com.unity.render-pipelines.core`)
Full detail: [volumes.md](volumes.md)
- `UnityEngine.Rendering.Volume` — the scene component (`isGlobal`, `priority`, `weight`, `blendDistance`, `sharedProfile`, `profile`).
- `UnityEngine.Rendering.VolumeProfile` — the asset holding a set of `VolumeComponent`s (`Add<T>()`, `Remove<T>()`, `Has<T>()`, `TryGet<T>()`).
- `UnityEngine.Rendering.VolumeComponent` — base class for one effect's parameter set (`active`, `parameters`, `Override()`).
- `UnityEngine.Rendering.VolumeManager` — resolves/blends all active Volumes each frame (`Update()`, `GetVolumes()`, `stack`).
- `UnityEngine.Rendering.VolumeParameter` / `VolumeParameter<T>` — base parameter wrapper types (`overrideState`, `value`, `Interp()`).
- `UnityEngine.Rendering.FloatParameter`, `ClampedFloatParameter`, `BoolParameter` — concrete parameter types used inside a custom `VolumeComponent`.

## URP built-in post-processing effects (Volume Overrides)
Full detail: [effect-availability-and-effect-list.md](effect-availability-and-effect-list.md)
- 18 built-in Volume Override effects (Bloom, Channel Mixer, Chromatic Aberration, Color Adjustments, Color Curves, Color Lookup, Depth of Field, Film Grain, Lens Distortion, Lift/Gamma/Gain, Motion Blur, Panini Projection, Screen Space Lens Flare, Shadows Midtones Highlights, Split Toning, Tonemapping, Vignette, White Balance) — each is a `VolumeComponent` subclass configured through the Inspector, not typically constructed directly in code.

## URP custom post-processing (`com.unity.render-pipelines.universal` / `.core`)
Full detail: [custom-post-processing.md](custom-post-processing.md)
- `UnityEngine.Rendering.Universal.ScriptableRendererFeature` — base class for injecting a custom pass into the URP Renderer (`Create()`, `AddRenderPasses()`).
- `UnityEngine.Rendering.Universal.FullScreenPassRendererFeature` — ready-made Renderer Feature for a no-code, Shader-Graph-driven full-screen effect (`passMaterial`, `injectionPoint`, `requirements`, `fetchColorBuffer`).
- `UnityEngine.Rendering.Universal.ScriptableRenderPass` — the actual pass a Renderer Feature enqueues (`renderPassEvent`, `RecordRenderGraph()`, `ConfigureInput()`).
- `UnityEngine.Rendering.Blitter` — static blit/copy utility for reading/writing render targets inside a custom pass.
- `UnityEngine.Rendering.RTHandle` — camera-size-scaling `RenderTexture` wrapper used as a custom pass's color/depth source/destination.

## Legacy Post Processing Stack v2 (`com.unity.postprocessing`, Built-in Render Pipeline)
Full detail: [postprocessing-v2-legacy.md](postprocessing-v2-legacy.md)
- `UnityEngine.Rendering.PostProcessing.PostProcessLayer` — camera component that renders the stack (`antialiasingMode`, `volumeLayer`, `volumeTrigger`, `Render()`).
- `UnityEngine.Rendering.PostProcessing.PostProcessVolume` — the Built-in RP equivalent of URP's `Volume` (`isGlobal`, `weight`, `priority`, `blendDistance`, `sharedProfile`).
- `UnityEngine.Rendering.PostProcessing.PostProcessProfile` — the Built-in RP equivalent of `VolumeProfile` (`settings`, `AddSettings()`, `GetSetting<T>()`).
- `UnityEngine.Rendering.PostProcessing.PostProcessEffectSettings` — base class for a PPv2 effect's settings (`active`, `enabled`, `IsEnabledAndSupported()`).
- `UnityEngine.Rendering.PostProcessing.PostProcessEffectRenderer<T>` — base class for a custom PPv2 effect's renderer.
- Built-in PPv2 effect settings classes: `Bloom`, `ColorGrading`, `Vignette`, `DepthOfField`, `MotionBlur`, `ChromaticAberration`, `Grain`, `AmbientOcclusion`, `AutoExposure`, `LensDistortion`.

## Cross-reference note
The URP Volume system (`Volume`/`VolumeProfile`/`VolumeComponent`) and the legacy PPv2 system (`PostProcessVolume`/`PostProcessProfile`/`PostProcessEffectSettings`) are structurally parallel but **not** interchangeable or compatible with each other — a project is on exactly one of the two, matching its render pipeline (URP → Volume system; Built-in RP → PPv2). Never mix API from the two systems in the same recommendation without first confirming which pipeline the project targets.
