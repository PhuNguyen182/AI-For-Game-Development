# Native Audio Plugin SDK — Custom DSP Effects & Spatializers

Sources: [Native audio plug-in SDK](https://docs.unity3d.com/Manual/AudioMixerNativeAudioPlugin.html), [Developing an audio DSP plug-in](https://docs.unity3d.com/Manual/AudioNativeDSPPlugin.html), [Building a custom GUI for a native plug-in](https://docs.unity3d.com/Manual/AudioNativeCustomGUI.html), [Importing a native audio plug-in](https://docs.unity3d.com/Manual/AudioNativePluginImport.html), [Native audio plug-in examples](https://docs.unity3d.com/Manual/AudioNativePluginExamples.html), [Audio Spatializer SDK](https://docs.unity3d.com/Manual/AudioSpatializerSDK.html), [NativeAudioPlugins repository](https://github.com/Unity-Technologies/NativeAudioPlugins).
Covers: SKILL.md §4 — **"Escalate to the Native Audio Plugin SDK only once the built-in Filter/Effect catalog cannot express the DSP"**.

The Native Audio Plugin SDK lets a per-platform C/C++ DSP implementation
appear in Unity as an addable Mixer Effect (optionally with a custom managed
GUI), or as a Spatializer/Ambisonic decoder plugin. It is a build-and-ship
commitment, not a routine authoring path — reach for it only after
confirming [filters-vs-effects.md](filters-vs-effects.md)'s catalog genuinely
cannot express the requested DSP.

## What it takes to ship one

| Step | Requirement | Source |
|---|---|---|
| Author the DSP | Implement `CreateCallback`, `ReleaseCallback`, and `ProcessCallback` against `AudioPluginInterface.h`; register each parameter's name, unit, min/max/default, and display curve via `RegisterParameter` | [Developing an audio DSP plug-in](https://docs.unity3d.com/Manual/AudioNativeDSPPlugin.html) |
| Optional custom GUI | A managed (C#) GUI layer can replace the default auto-generated parameter sliders | [Building a custom GUI](https://docs.unity3d.com/Manual/AudioNativeCustomGUI.html) |
| Compile per platform | No cross-platform binary — build separately for each target platform | [Native audio plug-in SDK](https://docs.unity3d.com/Manual/AudioMixerNativeAudioPlugin.html) |
| Name with the mandatory prefix | The compiled library **must** be named with an `audioplugin` prefix (case-insensitive), e.g. `audioplugin-myeffect.dll` — Unity needs to discover audio plugins before it builds any mixer asset that might reference one | [Importing a native audio plug-in](https://docs.unity3d.com/Manual/AudioNativePluginImport.html) |
| Import | Drop the compiled library into the project's `Assets` folder; Unity auto-installs it; use the plugin importer Inspector to assign target platforms | same |
| Ambisonic decoder variant | A decoder additionally sets `UnityAudioEffectDefinitionFlags_IsAmbisonicDecoder` and implements `UnityAudioAmbisonicData` (including `ambisonicOutChannels`, populated from the project's speaker configuration) — see [ambisonic-audio.md](ambisonic-audio.md) | [Native audio plug-in SDK](https://docs.unity3d.com/Manual/AudioMixerNativeAudioPlugin.html) |

**Critical caveat**: the mandatory `audioplugin` filename prefix means a
correctly-built native library with an ordinary plugin name is silently
never discovered as a Mixer effect — there is no error, it simply never
appears in the Add Effect list.

## Reference implementations

| Category | Examples | Source |
|---|---|---|
| No custom GUI | NoiseBox, Ring Modulator, StereoWidener, Lofinator | [NativeAudioPlugins repository](https://github.com/Unity-Technologies/NativeAudioPlugins) |
| With custom GUI | Equalizer, multiband compressor, CorrelationMeter, Loudness Monitor, TeeBee/TeeDee synths | same |

The repository is public-domain and intended as a starting template rather
than production-ready code as-is.

## When this is the wrong tool

- The requested DSP already exists as a built-in Filter or Mixer Effect —
  check [filters-vs-effects.md](filters-vs-effects.md) first.
- The requirement is spatial audio behavior only (HRTF, binaural rendering)
  rather than a new DSP effect — that is the narrower **Audio Spatializer
  SDK** variant of this same plugin architecture, per [Audio Spatializer
  SDK](https://docs.unity3d.com/Manual/AudioSpatializerSDK.html), not a
  general-purpose effect plugin.
- The team has no per-platform native build pipeline already in place —
  this is `tech-lead-sdk-platform`/`tech-lead-performance` escalation
  territory, not a routine Unity Engineer task.
