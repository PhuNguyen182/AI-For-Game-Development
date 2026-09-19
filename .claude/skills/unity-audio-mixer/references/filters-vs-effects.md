# Audio Filters vs. Mixer Effects — Attachment Point Decides the Choice

Sources: [Audio filters](https://docs.unity3d.com/Manual/audio-filters.html), [Audio effects](https://docs.unity3d.com/Manual/audio-effects.html), [Add an Audio Mixer effect](https://docs.unity3d.com/Manual/class-AudioEffectMixer.html), [AudioGroup Inspector](https://docs.unity3d.com/Manual/AudioMixerInspectors.html), and each component's own manual page linked per row below.
Covers: SKILL.md §4 — **"Pick Filter vs Mixer Effect by attachment point, not by name"**.

Two catalogs answer to similar-sounding names. A **Filter** is a component on
an `AudioSource`/`AudioListener` GameObject; it processes that one source's
signal before it reaches the mixer, and its processing order follows
component order on the GameObject (reorder by moving the component, no
drag-reorder UI). An **Effect** is added inside an `AudioMixerGroup`'s
Inspector; it processes the group's already-mixed signal, and is freely
draggable, bypassable, and removable in that chain. Several pairs below are
the same DSP math at a different attachment point.

## Table of contents
- [AudioSource-level Filters](#audiosource-level-filters)
- [Mixer-Group-level Effects](#mixer-group-level-effects)
- [Mixer-only routing units](#mixer-only-routing-units)

## AudioSource-level Filters

| Filter | Key parameters (range, unit, default) | Use for | Source |
|---|---|---|---|
| Audio Low Pass Filter | Cutoff Frequency 0–22000 Hz (5000); Resonance Q 1–10 (1) | Muffling a source (behind a wall, underwater) | [Low Pass Filter](https://docs.unity3d.com/Manual/class-AudioLowPassFilter.html) |
| Audio High Pass Filter | Cutoff Frequency 10–22000 Hz (5000); Resonance Q 1–10 (1) | Thinning a source (radio, phone) | [High Pass Filter](https://docs.unity3d.com/Manual/class-AudioHighPassFilter.html) |
| Audio Echo Filter | Delay 10–5000 ms (500); Decay Ratio 0–1 (0.5); Wet/Dry Mix 0–1 (1/1) | A per-source echo | [Echo Filter](https://docs.unity3d.com/Manual/class-AudioEchoFilter.html) |
| Audio Distortion Filter | Distortion Level 0–1 (0.5) | Low-quality-radio-style clipping on one source | [Distortion Filter](https://docs.unity3d.com/Manual/class-AudioDistortionFilter.html) |
| Audio Reverb Filter | Dry Level, Room, Room HF/LF (mB); Decay Time 0.1–20 s; Diffusion/Density 0–100%; a Reverb Preset dropdown (editable only when set to User) | Per-source room simulation | [Reverb Filter](https://docs.unity3d.com/Manual/class-AudioReverbFilter.html) |
| Audio Chorus Filter | Dry Mix 0–1 (0.5); Wet Mix 1/2/3 0–1 (0.5 each, 90° phase-offset taps); Delay 0.1–100 ms (40); Rate 0–20 Hz (0.8); Depth 0–1 (0.03); Feedback 0–1 (0) | Thickening a single source | [Chorus Filter](https://docs.unity3d.com/Manual/class-AudioChorusFilter.html) |

**Critical caveat**: low Rate + low Depth on the Chorus Filter produces a
simple dry echo instead of a chorus effect; low feedback plus a short delay
reads as flanging instead.

## Mixer-Group-level Effects

| Effect | Key parameters (range, unit, default) | Distinguishing note | Source |
|---|---|---|---|
| Low Pass / High Pass | Cutoff 10–22000 Hz (5000); Resonance 1–10 (1) | Same math as the Filter, applied to the whole group | [Low Pass Effect](https://docs.unity3d.com/Manual/class-AudioLowPassEffect.html), [High Pass Effect](https://docs.unity3d.com/Manual/class-AudioHighPassEffect.html) |
| Low Pass Simple / High Pass Simple | Cutoff 10–22000 Hz (5000), no resonance control | Cheaper CPU variant — reach for the non-Simple version only when resonance control is actually needed | [Low Pass Simple](https://docs.unity3d.com/Manual/class-AudioLowPassSimpleEffect.html), [High Pass Simple](https://docs.unity3d.com/Manual/class-AudioHighPassSimpleEffect.html) |
| Echo | Delay 10–5000 ms (500); Decay 0–100% (50); Max Channels 0–16 (0); Dry/Wet Mix 0–100% (100/100) | Group-wide echo, e.g. a shared cave ambience bus | [Echo Effect](https://docs.unity3d.com/Manual/class-AudioEchoEffect.html) |
| Flange | Dry/Wet Mix 0–100% (45/55); Depth 0.01–1 (1); Rate 0.1–20 Hz (10) | Not present as an AudioSource Filter — mixer-only | [Flange Effect](https://docs.unity3d.com/Manual/class-AudioFlangeEffect.html) |
| Distortion | Distortion 0–1 (0.5) | Group-wide clipping | [Distortion Effect](https://docs.unity3d.com/Manual/class-AudioDistortionEffect.html) |
| Normalize | Fade In Time 0–20000 ms (5000); Lowest Volume 0–1 (0.10); Maximum Amp 0–100000× (20) | Mixer-only — auto gain-rides a bus toward a target level | [Normalize Effect](https://docs.unity3d.com/Manual/class-AudioNormalizeEffect.html) |
| Parametric EQ | Center Freq 20–22000 Hz (8000); Octave Range 0.2–5 (1); Frequency Gain 0.05–3× (1) | Single-band EQ correction | [Parametric EQ](https://docs.unity3d.com/Manual/class-AudioParamEQEffect.html) |
| Pitch Shifter | Pitch 0.5–2× (1); FFT Size 256–4096 (1024); Overlap 1–32 (4); Max Channels 0–16 (0) | Larger FFT Size and Overlap cost more CPU for fewer artifacts | [Pitch Shifter](https://docs.unity3d.com/Manual/class-AudioPitchShifterEffect.html) |
| Chorus | Same 8-parameter layout as the Chorus Filter | Group-wide chorus | [Chorus Effect](https://docs.unity3d.com/Manual/class-AudioChorusEffect.html) |
| Compressor | Threshold 0 to −60 dB (0); Attack 10–200 ms (50); Release 20–1000 ms (50); Make Up Gain 0–30 dB (0) | Behaves as a limiter with a fixed ∞:1 ratio — no separate Ratio/Knee controls | [Compressor](https://docs.unity3d.com/Manual/class-AudioCompressor.html) |
| SFX Reverb | Wet/Dry Level, Room/Room HF/LF (mB); Decay Time 0.1–20 s; Diffusion/Density 0–100% | The mixer-side equivalent of the Audio Reverb Filter — near-identical parameters, different attachment point | [SFX Reverb](https://docs.unity3d.com/Manual/class-AudioReverbEffect.html) |

## Mixer-only routing units

Attenuation, Send, Receive, and Duck Volume have no AudioSource-level Filter
equivalent — they only exist as Mixer Effects, and are documented separately
on [audio-mixer-core.md](audio-mixer-core.md) rather than on the effects
index pages above.

**Critical caveat**: neither catalog documents a standalone "Audio Reverb
Zone" — that legacy position-triggered reverb component is a distinct,
older system, not linked from either the Filters or Effects index in this
Unity version; do not conflate it with Audio Reverb Filter or SFX Reverb.
