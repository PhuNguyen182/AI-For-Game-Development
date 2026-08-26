# Post Processing Stack v2 — the Built-in Render Pipeline Path

Sources: [Post Processing Stack v2 manual](https://docs.unity3d.com/Packages/com.unity.postprocessing@3.5/manual/index.html), [Quick start](https://docs.unity3d.com/Packages/com.unity.postprocessing@3.5/manual/Quick-start.html), and the package API pages linked per row (`com.unity.postprocessing@3.5`, namespace `UnityEngine.Rendering.PostProcessing`).
Covers: SKILL.md §4 — **"Confirm the active render pipeline before citing a single API"**.

The Built-in Render Pipeline has no post-processing of its own; this package
is the whole of it. The package is in maintenance mode, and URP is **not
compatible** with it — a URP project that installs it gains components that
never render. It remains the correct and only choice on Built-in RP.

## Setup

| Piece | What it does | Source |
|---|---|---|
| `PostProcessLayer` | Goes on the **Camera** and is what actually renders the stack. Its `volumeLayer` mask decides which volumes this camera sees, and `volumeTrigger` decides the transform proximity is measured from — a volume outside the mask is silently ignored, the same failure shape as URP's Volume Mask | [PostProcessLayer](https://docs.unity3d.com/Packages/com.unity.postprocessing@3.5/api/UnityEngine.Rendering.PostProcessing.PostProcessLayer.html) |
| `PostProcessVolume` | The Built-in analogue of URP's `Volume` — `isGlobal`, `weight`, `priority`, `blendDistance`, and the same `sharedProfile` versus instantiated `profile` distinction | [PostProcessVolume](https://docs.unity3d.com/Packages/com.unity.postprocessing@3.5/api/UnityEngine.Rendering.PostProcessing.PostProcessVolume.html) |
| `PostProcessProfile` | The asset holding a list of effect settings — `AddSettings()`, `GetSetting<T>()`, `TryGetSettings<T>()` | [PostProcessProfile](https://docs.unity3d.com/Packages/com.unity.postprocessing@3.5/api/UnityEngine.Rendering.PostProcessing.PostProcessProfile.html) |
| `PostProcessEffectSettings` | Base class every effect's settings derive from — `active`, `enabled`, `IsEnabledAndSupported()` | [PostProcessEffectSettings](https://docs.unity3d.com/Packages/com.unity.postprocessing@3.5/api/UnityEngine.Rendering.PostProcessing.PostProcessEffectSettings.html) |
| `PostProcessEffectRenderer<T>` | Base class for a custom PPv2 effect's renderer, paired to a settings subclass. There is no Renderer Feature equivalent here | [PostProcessEffectRenderer&lt;T&gt;](https://docs.unity3d.com/Packages/com.unity.postprocessing@3.5/api/UnityEngine.Rendering.PostProcessing.PostProcessEffectRenderer-1.html) |

Anti-aliasing lives on `PostProcessLayer` — `antialiasingMode` selecting FXAA,
SMAA, or TAA — not in the effect list, the same placement surprise URP has
with its Camera setting.

## Effects

The one structural difference from URP: **`ColorGrading` is a single class**
covering what URP splits across five overrides. There is no standalone
tonemapper type — `tonemapper` is a field on `ColorGrading`.

| Class | Key members | Source |
|---|---|---|
| `ColorGrading` | `gradingMode` (HDR / LDR / External), `tonemapper`, `lift`/`gamma`/`gain`, `temperature`, `tint`, `saturation`, `hueShift`, `contrast`, `postExposure`, channel mixer, `externalLut`, `ldrLut` | [ColorGrading](https://docs.unity3d.com/Packages/com.unity.postprocessing@3.5/api/UnityEngine.Rendering.PostProcessing.ColorGrading.html) |
| `Bloom` | `intensity`, `threshold`, `softKnee`, `diffusion`, `anamorphicRatio`, `dirtTexture`, `fastMode`, `clamp` | [Bloom](https://docs.unity3d.com/Packages/com.unity.postprocessing@3.5/api/UnityEngine.Rendering.PostProcessing.Bloom.html) |
| `AutoExposure` | `eyeAdaptation` (Progressive / Fixed), `keyValue`, `minLuminance`, `maxLuminance`, `speedUp`, `speedDown` — has no URP counterpart | [AutoExposure](https://docs.unity3d.com/Packages/com.unity.postprocessing@3.5/api/UnityEngine.Rendering.PostProcessing.AutoExposure.html) |
| `AmbientOcclusion` | `intensity`, `radius`, `quality`, `mode`, `ambientOnly`, `directLightingStrength` — an effect here, a Renderer Feature in URP | [AmbientOcclusion](https://docs.unity3d.com/Packages/com.unity.postprocessing@3.5/api/UnityEngine.Rendering.PostProcessing.AmbientOcclusion.html) |
| `DepthOfField` | `aperture`, `focalLength`, `focusDistance`, `kernelSize` — physical camera terms, unlike URP's Bokeh/Gaussian modes | [DepthOfField](https://docs.unity3d.com/Packages/com.unity.postprocessing@3.5/api/UnityEngine.Rendering.PostProcessing.DepthOfField.html) |
| `MotionBlur` | `sampleCount`, `shutterAngle` | [MotionBlur](https://docs.unity3d.com/Packages/com.unity.postprocessing@3.5/api/UnityEngine.Rendering.PostProcessing.MotionBlur.html) |
| `Vignette` | `intensity`, `color`, `mode` (Classic / Masked), `center`, `smoothness`, `rounded`, `opacity` | [Vignette](https://docs.unity3d.com/Packages/com.unity.postprocessing@3.5/api/UnityEngine.Rendering.PostProcessing.Vignette.html) |
| `Grain` | `colored`, `intensity`, `size`, `lumContrib` — named Film Grain in URP | [Grain](https://docs.unity3d.com/Packages/com.unity.postprocessing@3.5/api/UnityEngine.Rendering.PostProcessing.Grain.html) |
| `ChromaticAberration` | `intensity`, `fastMode`, `spectralLut` | [ChromaticAberration](https://docs.unity3d.com/Packages/com.unity.postprocessing@3.5/api/UnityEngine.Rendering.PostProcessing.ChromaticAberration.html) |
| `LensDistortion` | `centerX`, `centerY`, `intensity`, `intensityX`, `intensityY`, `scale` | [LensDistortion](https://docs.unity3d.com/Packages/com.unity.postprocessing@3.5/api/UnityEngine.Rendering.PostProcessing.LensDistortion.html) |

## Documentation gaps

| Gap | Consequence | Source |
|---|---|---|
| The manual's table of contents renders client-side and does not appear in a plain fetch | Sub-page filenames cannot be enumerated from the index; `manual/Effects.html` and a lowercase `manual/quick-start.html` both return 404, so filenames are case-sensitive and must not be guessed | [Manual index](https://docs.unity3d.com/Packages/com.unity.postprocessing@3.5/manual/index.html) |
| The API index page returns chrome only, no class list | Every class above was confirmed by fetching its own page. Effects not listed here — Screen Space Reflections, Dithering, fog integration — exist in the package but were not confirmed, and are omitted rather than assumed | [API index](https://docs.unity3d.com/Packages/com.unity.postprocessing@3.5/api/index.html) |
