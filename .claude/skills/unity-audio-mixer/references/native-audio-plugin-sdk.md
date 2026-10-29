# Native Audio Plugin SDK

Sources: Manual `AudioMixerNativeAudioPlugin`, `AudioNativeDSPPlugin`, `AudioNativeCustomGUI`, `AudioNativePluginImport`, `AudioSpatializerSDK`; examples https://github.com/Unity-Technologies/NativeAudioPlugins (public domain, a template rather than production code).

A per-platform C/C++ DSP appears as an addable Mixer Effect (optional managed GUI), Spatializer, or Ambisonic decoder. Use it only after [filters-vs-effects.md](filters-vs-effects.md) is exhausted. Wrong tool when:
- the DSP exists built-in;
- the need is only spatial audio (HRTF, binaural), which is the narrower Audio Spatializer SDK variant;
- no per-platform native build pipeline exists (escalate to `sdk-platform-engineer`).

## Shipping one
1. Implement `CreateCallback`, `ReleaseCallback`, `ProcessCallback` against `AudioPluginInterface.h`; `RegisterParameter` per parameter (name, unit, min/max/default, curve).
2. Optional managed C# GUI replaces the auto-generated sliders.
3. Compile separately per platform; no cross-platform binary.
4. Name the library with an `audioplugin` prefix (case-insensitive), e.g. `audioplugin-myeffect.dll`. Otherwise it is silently never discovered and never appears in Add Effect.
5. Drop it in `Assets`; use the plugin importer Inspector to set target platforms.
6. A decoder also sets `UnityAudioEffectDefinitionFlags_IsAmbisonicDecoder` and implements `UnityAudioAmbisonicData` (`ambisonicOutChannels` is filled from the speaker configuration); see [ambisonic-audio.md](ambisonic-audio.md).
