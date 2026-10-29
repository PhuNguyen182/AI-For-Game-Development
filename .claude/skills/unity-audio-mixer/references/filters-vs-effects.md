# Filters vs Mixer Effects

Sources: Manual `audio-filters`, `audio-effects`, `class-Audio*Filter`, `class-Audio*Effect`. Values are range (default).

A Filter is a component on a Source/Listener GameObject; it processes that source pre-mix, ordered by component order (move the component to reorder). An Effect lives in an `AudioMixerGroup`'s Inspector, processes the group's mixed signal, and is freely reorderable, bypassable and removable. Attenuation, Send, Receive and Duck Volume exist only as Mixer units ([audio-mixer-core.md](audio-mixer-core.md)).

## Filters (per source)

| Filter | Parameters |
|---|---|
| Low Pass | Cutoff 0-22000 Hz (5000); Resonance Q 1-10 (1) |
| High Pass | Cutoff 10-22000 Hz (5000); Resonance Q 1-10 (1) |
| Echo | Delay 10-5000 ms (500); Decay 0-1 (0.5); Wet/Dry 0-1 (1/1) |
| Distortion | Level 0-1 (0.5) |
| Reverb | Dry, Room, Room HF/LF (mB); Decay 0.1-20 s; Diffusion/Density 0-100%; Preset editable only as User |
| Chorus | Dry 0-1 (0.5); Wet 1-3 0-1 (0.5); Delay 0.1-100 ms (40); Rate 0-20 Hz (0.8); Depth 0-1 (0.03); Feedback 0-1 (0) |

Chorus with low Rate and Depth gives a plain dry echo; low feedback with short delay reads as flanging.

## Effects (per group)

| Effect | Parameters / note |
|---|---|
| Low/High Pass | Cutoff 10-22000 Hz (5000); Resonance 1-10 (1) |
| Low/High Pass Simple | Cutoff only; cheaper, use unless resonance is needed |
| Echo | Delay 10-5000 ms (500); Decay 0-100% (50); Max Channels 0-16; Dry/Wet 0-100% |
| Flange (mixer only) | Dry/Wet 0-100% (45/55); Depth 0.01-1 (1); Rate 0.1-20 Hz (10) |
| Distortion | 0-1 (0.5) |
| Normalize (mixer only) | Fade In 0-20000 ms (5000); Lowest Volume 0-1 (0.10); Max Amp 0-100000x (20) |
| Parametric EQ | Center 20-22000 Hz (8000); Octave Range 0.2-5 (1); Gain 0.05-3x (1) |
| Pitch Shifter | Pitch 0.5-2x; Max Channels 0-16 (0); FFT 256-4096 (1024); Overlap 1-32 (4); larger FFT/Overlap = more CPU, fewer artifacts |
| Chorus | Same 8 parameters as the Filter |
| Compressor | Threshold 0 to -60 dB; Attack 10-200 ms (50); Release 20-1000 ms (50); Make Up 0-30 dB; limiter with fixed infinity:1 ratio, no Ratio/Knee |
| SFX Reverb | Near-identical to Reverb Filter |

The legacy Audio Reverb Zone is a separate older system; do not conflate it with either reverb.
