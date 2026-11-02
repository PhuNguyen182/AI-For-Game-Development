---
name: unity-audio-mixer
description: "AudioSource, AudioMixer groups, snapshots, SetFloat, clip import, Duck Volume. Use for audio setup and mixing."
user-invocable: false
---

# Unity Audio & Audio Mixer

- **Not for:** non-audio Profiler modules (`unity-profiler-diagnostics`).
- **Not for:** Wwise/FMOD or platform audio SDKs (`sdk-platform-engineer`).
- **Not for:** netcode audio timing (`netcode-engineer`).
- **Not for:** the gameplay rule that triggers a sound (`csharp-engineer`; it lives in Core, this skill wires only the playback call).
- **Not for:** audio-reactive VFX (`technical-artist`).
- **Docs:** https://docs.unity3d.com/Manual/AudioReference.html and Scripting API https://docs.unity3d.com/6000.5/Documentation/ScriptReference/ — pinned to Unity 6000.5.
  - **Mixer UI:** it has changed across majors, so confirm UI paths if the project is on another version.
  - **Duck Volume:** the Manual publishes no parameter table for it.
  - **Editor slider bounds:** the Manual states several only by convention.
  - **Duck Volume parameters and slider bounds:** never invent those numbers; read them in the Inspector.

## References
- **[audio-import-and-clips.md](references/audio-import-and-clips.md):** Importing a sound, a load stall, or `LoadAudioData`/`UnloadAudioData`.
- **[audio-source-and-listener.md](references/audio-source-and-listener.md):** Placing or scripting an `AudioSource` or `AudioListener`.
- **[audio-mixer-core.md](references/audio-mixer-core.md):** Building or scripting groups, Sends, Duck Volume, exposed parameters, snapshots.
- **[filters-vs-effects.md](references/filters-vs-effects.md):** Choosing a DSP component and where to attach it.
- **[audio-random-container.md](references/audio-random-container.md):** Repeated SFX needing clip/volume/pitch variation.
- **[native-audio-plugin-sdk.md](references/native-audio-plugin-sdk.md):** The built-in catalog cannot express the DSP.
- **[ambisonic-audio.md](references/ambisonic-audio.md):** 360/XR soundfield content.
- **[audio-profiler-and-settings.md](references/audio-profiler-and-settings.md):** A silence, voice-count, CPU or memory complaint needs a number.

## Steps
1. **Set clip import by length and trigger frequency:** per [audio-import-and-clips.md](references/audio-import-and-clips.md).
   - **Short frequent SFX:** Decompress On Load with PCM/ADPCM.
   - **Long music/dialog:** Streaming with Vorbis.
2. **Drive 2D/3D from `spatialBlend` and rolloff mode, not Volume:** per [audio-source-and-listener.md](references/audio-source-and-listener.md).
   - **UI cue:** 0.
   - **Positional sound:** 1.
3. **Route every non-trivial `AudioSource` through an `AudioMixerGroup`:** the implicit default Output cannot duck or snapshot, and retrofitting routing later is costly. See [audio-mixer-core.md](references/audio-mixer-core.md).
4. **Pick Filter vs Mixer Effect by attachment point:** per [filters-vs-effects.md](references/filters-vs-effects.md).
   - **Filter:** processes one Source pre-mix.
   - **Effect:** processes a whole Group's mix.
5. **Use snapshots for mood changes and `SetFloat` for independent knobs:** a volume slider is a knob; never both on the same parameter.
   - **Parameter names:** verify every name string against the Inspector, because a typo returns `false` silently.
6. **Use an Audio Random Container before scripting clip/volume/pitch randomisation:** per [audio-random-container.md](references/audio-random-container.md).
   - **Script it:** only if Playback Mode plus Avoid Repeating Last cannot express the rule.
7. **Escalate to the Native Audio Plugin SDK only when the built-in catalog cannot express the DSP:** it is a per-platform native build, per [native-audio-plugin-sdk.md](references/native-audio-plugin-sdk.md).
8. **Ambisonic:** confirm a decoder plugin is installed before promising playback.
   - **Decoder:** Unity ships none; see [ambisonic-audio.md](references/ambisonic-audio.md).
9. **Pool `AudioSource` objects for high-frequency sounds:** per `csharp-standards` allocation rules.
   - **Per shot or footstep:** no `Instantiate`/`Destroy`.
10. **Diagnose silence or cost from the Audio Profiler before proposing a fix:** per [audio-profiler-and-settings.md](references/audio-profiler-and-settings.md).
11. **Target platform, multiplayer audio-sync need or decoder presence unknown:** state the assumption under `Assumptions:`, or `Blocked` when it changes the mixer design.
   - **Gameplay threshold or condition:** stays in Core.
   - **Layer unclear:** `Needs-decision`, `Next: technical-architect`.

## Output
```
## Audio Work — <feature/scene>
- Import settings: <format, load type, rationale per clip>
- Source/Listener: <spatial blend, rolloff, output group>
- Mixer graph: <groups, effects, sends, exposed parameters>
- Runtime control: <SetFloat / TransitionTo usage, or static>
- Randomisation / escalations: <ARC settings, native plugin, decoder, or none>
- Diagnosis: <Audio Profiler evidence behind any perf/silence claim>
```

## Example
- **"Randomise the footstep clip and volume in `PlayFootstep()`":** declined.
  - **Why:** an Audio Random Container (Shuffle, Avoid Repeating Last) does it without code.
  - **Did instead:** script is `source.resource = playlist; source.Play();`.
