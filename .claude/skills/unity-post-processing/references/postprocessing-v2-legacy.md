# Post Processing Stack v2 (Built-in RP)

Source: `com.unity.postprocessing@3.5` manual and API, namespace `UnityEngine.Rendering.PostProcessing`. Maintenance mode, but the only option on Built-in RP; URP is not compatible.

## Setup
- `PostProcessLayer` on the **Camera** renders the stack. `volumeLayer` is the mask (a volume outside it is silently ignored); `volumeTrigger` is the proximity transform. Anti-aliasing is `antialiasingMode` (FXAA/SMAA/TAA) here, not in the effect list.
- `PostProcessVolume`: `isGlobal`, `weight`, `priority`, `blendDistance`; same `sharedProfile` vs `profile` distinction as URP.
- `PostProcessProfile`: `AddSettings()`, `GetSetting<T>()`, `TryGetSettings<T>()`.
- `PostProcessEffectSettings` base: `active`, `enabled`, `IsEnabledAndSupported()`.
- Custom effect: `PostProcessEffectRenderer<T>` paired to a settings subclass; no Renderer Feature equivalent.

## Effects (key members)
| Class | Members |
|---|---|
| `ColorGrading` | One class for what URP splits across five overrides: `gradingMode` (HDR/LDR/External), `tonemapper`, `lift`/`gamma`/`gain`, `temperature`, `tint`, `saturation`, `hueShift`, `contrast`, `postExposure`, channel mixer, `externalLut`, `ldrLut` |
| `Bloom` | `intensity`, `threshold`, `softKnee`, `diffusion`, `anamorphicRatio`, `dirtTexture`, `fastMode`, `clamp` |
| `AutoExposure` | `eyeAdaptation`, `keyValue`, `minLuminance`, `maxLuminance`, `speedUp`, `speedDown` (no URP counterpart) |
| `AmbientOcclusion` | `intensity`, `radius`, `quality`, `mode`, `ambientOnly`, `directLightingStrength` |
| `DepthOfField` | `aperture`, `focalLength`, `focusDistance`, `kernelSize` (physical terms) |
| `MotionBlur` | `sampleCount`, `shutterAngle` |
| `Vignette` | `intensity`, `color`, `mode`, `center`, `smoothness`, `rounded`, `opacity` |
| `Grain` | `colored`, `intensity`, `size`, `lumContrib` |
| `ChromaticAberration` | `intensity`, `fastMode`, `spectralLut` |
| `LensDistortion` | `centerX`, `centerY`, `intensity`, `intensityX`, `intensityY`, `scale` |

Unverified: Screen Space Reflections, Dithering and fog integration exist in the package but were not confirmed. The manual's sub-page filenames are case-sensitive and not enumerable from the index; do not guess URLs.
