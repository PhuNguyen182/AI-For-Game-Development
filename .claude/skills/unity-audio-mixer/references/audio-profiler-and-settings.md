# Audio Profiler & Project Settings — Diagnosing Voices, CPU, Memory

Sources: [Profiler: Audio module](https://docs.unity3d.com/Manual/ProfilerAudio.html), [Audio Manager settings](https://docs.unity3d.com/Manual/class-AudioManager.html).
Covers: SKILL.md §4 — **"Diagnose a playback or performance complaint from the Audio Profiler module before proposing a fix"**.

The Audio Profiler module reports live voice/CPU/memory numbers; the Audio
Manager (`Edit > Project Settings > Audio`) holds the settings those numbers
are measured against. Read them together — a Profiler number rarely means
anything without the setting it is bounded by. General non-audio Profiler
modules (CPU/GPU/Memory/Rendering) stay with `unity-profiler-diagnostics`;
this file covers the Audio module specifically.

## Audio Profiler metrics

| Metric | Meaning | What a spike means | Source |
|---|---|---|---|
| Playing / Paused / Total Audio Sources | Source counts this frame | Playing count rising unexpectedly points at leaked or unstopped looping sources | [Profiler: Audio](https://docs.unity3d.com/Manual/ProfilerAudio.html) |
| Audio Voices | Active channels in use | Approaching **Max Real Voices** starts virtualizing sources | same |
| Total Audio CPU | Overall audio engine CPU cost | High cost from too many simultaneous effects/streams/decompression | same |
| DSP CPU | Cost of mixing + effect processing | The direct signal for "too many, or too expensive, Mixer Effects" | same |
| Streaming CPU | Cost of decoding streamed clips | High with many simultaneously-playing Streaming-load-type clips | same |
| Total Audio Memory | RAM used by the audio engine | Unity pools this memory — growth alone does not prove a leak, it grows toward saturation | same |
| Sample Sound Memory | Decompressed data for Decompress-On-Load clips | Large uncompressed clips inflate this quickly — cross-check against [audio-import-and-clips.md](audio-import-and-clips.md)'s Load Type table | same |

## Per-voice diagnostic columns

| Column | What it tells you | Source |
|---|---|---|
| Virtual | `YES` means this voice was demoted to virtual because **Max Real Voices** was exceeded — the direct answer to "why is this sound silent" | [Profiler: Audio](https://docs.unity3d.com/Manual/ProfilerAudio.html) |
| Audibility | Post-attenuation actual level | same |
| 3D | Whether distance attenuation is active on this voice | same |

**Critical caveat**: the Profiler does not display DSP Buffer Size directly
— that is a Project Settings value, not a live metric. Correlate it
manually: a smaller buffer lowers latency but raises per-callback CPU
overhead.

## Project Settings > Audio (`AudioManager`)

| Setting | Effect | Default | Source |
|---|---|---|---|
| Volume Rolloff Scale | Multiplier on logarithmic-rolloff attenuation speed; 1 "simulates the real world" | 1 | [Audio Manager](https://docs.unity3d.com/Manual/class-AudioManager.html) |
| Doppler Factor | 0 disables Doppler entirely; 1 makes it audible for fast-moving sources | — | same |
| Default Speaker Mode | Output channel layout | 2 (Stereo) | same |
| DSP Buffer Size | Named presets: Default / Best Latency / Good Latency / Best Performance — exact sample counts are not published in the Manual for this version | Default | same |
| Max Virtual Voices | Ceiling on virtual (non-audible-processed) voices tracked | — | same |
| Max Real Voices | Ceiling on simultaneously **audible** voices; the system keeps the loudest voices real when exceeded | — | same |
| Spatializer Plugin | Native plugin used for 3D spatialized filtering | None built-in | same; see [native-audio-plugin-sdk.md](native-audio-plugin-sdk.md) |
| Ambisonic Decoder Plugin | Native plugin used for ambisonic decode | None built-in | same; see [ambisonic-audio.md](ambisonic-audio.md) |
| Disable Unity Audio | Deactivates audio in standalone **builds only**; the Editor still previews | Disabled | same |
| Virtualize Effect | Dynamically disables effects/spatializers on culled (virtual) sources to save CPU | — | same |

**Critical caveat**: raising **Max Real Voices** without measuring DSP/
Streaming CPU first trades a virtualization symptom for a CPU one — treat
this as a trade-off to measure, per `performance-and-algorithms.md`'s
Verification section, not a free fix.
