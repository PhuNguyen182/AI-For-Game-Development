---
name: unity-audio-mixer
description: "Unity audio: AudioSource, AudioListener, clip import (Load Type, compression), AudioMixer groups, snapshots, SetFloat exposed parameters, Duck Volume, Audio Random Container, Max Real Voices, Audio Profiler. Use for audio setup and mixing."
user-invocable: false
---

# Unity Audio & Audio Mixer

Not for: non-audio Profiler modules (`unity-profiler-diagnostics`), Wwise/FMOD or platform audio SDKs (`sdk-platform-engineer`), netcode audio timing (`netcode-engineer`), the gameplay rule that triggers a sound (`csharp-engineer`; it lives in `Game.Core.*`, this skill wires only the playback call), audio-reactive VFX (`technical-artist`).
Docs: https://docs.unity3d.com/Manual/AudioReference.html and Scripting API https://docs.unity3d.com/6000.5/Documentation/ScriptReference/ — pinned to Unity 6000.5; the mixer UI has changed across majors, so confirm UI paths if the project is on another version. The Manual publishes no Duck Volume parameter table and states several Editor slider bounds only by convention; never invent those numbers, read them in the Inspector.

| Reference | Read when |
|---|---|
| [audio-import-and-clips.md](references/audio-import-and-clips.md) | Importing a sound, a load stall, or `LoadAudioData`/`UnloadAudioData` |
| [audio-source-and-listener.md](references/audio-source-and-listener.md) | Placing or scripting an `AudioSource` or `AudioListener` |
| [audio-mixer-core.md](references/audio-mixer-core.md) | Building or scripting groups, Sends, Duck Volume, exposed parameters, snapshots |
| [filters-vs-effects.md](references/filters-vs-effects.md) | Choosing a DSP component and where to attach it |
| [audio-random-container.md](references/audio-random-container.md) | Repeated SFX needing clip/volume/pitch variation |
| [native-audio-plugin-sdk.md](references/native-audio-plugin-sdk.md) | The built-in catalog cannot express the DSP |
| [ambisonic-audio.md](references/ambisonic-audio.md) | 360/XR soundfield content |
| [audio-profiler-and-settings.md](references/audio-profiler-and-settings.md) | A silence, voice-count, CPU or memory complaint needs a number |

## Steps
1. **Set clip import by length and trigger frequency**, per [audio-import-and-clips.md](references/audio-import-and-clips.md) — short frequent SFX: Decompress On Load with PCM/ADPCM; long music/dialog: Streaming with Vorbis.
2. **Drive 2D/3D from `spatialBlend` and rolloff mode, not Volume**, per [audio-source-and-listener.md](references/audio-source-and-listener.md) — UI cue 0, positional sound 1.
3. **Route every non-trivial `AudioSource` through an `AudioMixerGroup`** — the implicit default Output cannot duck or snapshot, and retrofitting routing later is costly. See [audio-mixer-core.md](references/audio-mixer-core.md).
4. **Pick Filter vs Mixer Effect by attachment point** — a Filter processes one Source pre-mix; an Effect processes a whole Group's mix, per [filters-vs-effects.md](references/filters-vs-effects.md).
5. **Use snapshots for mood changes and `SetFloat` for independent knobs** (volume slider); never both on the same parameter. Verify every parameter name string against the Inspector, because a typo returns `false` silently.
6. **Use an Audio Random Container before scripting clip/volume/pitch randomisation**, per [audio-random-container.md](references/audio-random-container.md); script it only if Playback Mode plus Avoid Repeating Last cannot express the rule.
7. **Escalate to the Native Audio Plugin SDK only when the built-in catalog cannot express the DSP** (per-platform native build), per [native-audio-plugin-sdk.md](references/native-audio-plugin-sdk.md).
8. **Ambisonic: confirm a decoder plugin is installed before promising playback** — Unity ships none; see [ambisonic-audio.md](references/ambisonic-audio.md).
9. **Pool `AudioSource` objects for high-frequency sounds** (`csharp-standards` allocation rules); no `Instantiate`/`Destroy` per shot or footstep.
10. **Diagnose silence or cost from the Audio Profiler before proposing a fix**, per [audio-profiler-and-settings.md](references/audio-profiler-and-settings.md).
11. **Target platform, multiplayer audio-sync need or decoder presence unknown** — ask, or state the assumption. A gameplay threshold or condition stays in `Game.Core.*`; ask if the layer is unclear.

## Output
```
## Audio Work — <feature/scene>
- Import settings: <format, load type, rationale per clip>
- Source/Listener: <spatial blend, rolloff, output group>
- Mixer graph: <groups, effects, sends, exposed parameters>
- Runtime control: <SetFloat / TransitionTo usage, or static>
- Randomisation / escalations: <ARC settings, native plugin, decoder, or none>
- Diagnosis: <Audio Profiler evidence behind any perf/silence claim>
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Randomise the footstep clip and volume in `PlayFootstep()`" → declined: an Audio Random Container (Shuffle, Avoid Repeating Last) does it without code; script is `source.resource = playlist; source.Play();`.
