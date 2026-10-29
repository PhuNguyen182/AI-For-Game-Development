# Audio Profiler & Project Settings

Sources: Manual `ProfilerAudio`, `class-AudioManager`. Settings at `Edit > Project Settings > Audio`.

## Profiler metrics

| Metric | Reads as |
|---|---|
| Playing / Paused / Total Audio Sources | Rising Playing count points to leaked or unstopped looping sources |
| Audio Voices | Nearing Max Real Voices starts virtualising |
| DSP CPU | Mixing plus effects; too many or too costly Mixer Effects |
| Streaming CPU | Decode of many concurrent Streaming clips |
| Total Audio CPU | Whole engine |
| Total Audio Memory | Pooled; growth toward saturation is not a leak |
| Sample Sound Memory | Decompressed Decompress-On-Load clips ([audio-import-and-clips.md](audio-import-and-clips.md)) |

Per-voice columns: **Virtual = YES** means demoted by exceeding Max Real Voices, the answer to "why is this sound silent"; Audibility is post-attenuation level; 3D shows whether distance attenuation applies. DSP Buffer Size is not shown live; correlate by hand (smaller buffer = lower latency, more callback CPU).

## Settings

| Setting | Note |
|---|---|
| Volume Rolloff Scale | Multiplies logarithmic rolloff; 1 = real world |
| Doppler Factor | 0 disables |
| Default Speaker Mode | Default Stereo |
| DSP Buffer Size | Presets Default / Best Latency / Good Latency / Best Performance; sample counts unpublished |
| Max Virtual Voices / Max Real Voices | Real = simultaneously audible; loudest stay real |
| Spatializer Plugin / Ambisonic Decoder Plugin | None built-in ([native-audio-plugin-sdk.md](native-audio-plugin-sdk.md), [ambisonic-audio.md](ambisonic-audio.md)) |
| Disable Unity Audio | Standalone builds only; the Editor still previews |
| Virtualize Effect | Disables effects and spatializers on virtual sources to save CPU |

Raising Max Real Voices without measuring DSP/Streaming CPU swaps a virtualisation symptom for a CPU one; measure it (`unity-profiler-diagnostics`).
