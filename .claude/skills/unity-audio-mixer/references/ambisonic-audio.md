# Ambisonic Audio — 360°/XR Soundfields

Sources: [Ambisonic audio](https://docs.unity3d.com/Manual/audio-ambisonic.html), [Ambisonic audio (concept)](https://docs.unity3d.com/Manual/AmbisonicAudio.html), [Developing an ambisonic decoder](https://docs.unity3d.com/Manual/AudioDevelopAmbisonicDecoder.html), [Audio Manager settings](https://docs.unity3d.com/Manual/class-AudioManager.html).
Covers: SKILL.md §4 — **"Treat Ambisonic playback as a 360°/XR-specific path, and confirm a decoder plugin is installed before promising it works"**.

Ambisonics represent a full soundfield surrounding the listener — a
recording/authoring format, not a fixed speaker-channel mapping — used for
360° video, XR, and audio skyboxes (distant ambient beds). It rotates with
listener orientation (e.g. VR head tracking) and decodes to whatever speaker
layout the project targets.

## The one fact that gates everything else

**Critical caveat**: Unity ships **no built-in ambisonic decoder**. A
project must install or author one via the [Native Audio Plugin
SDK](native-audio-plugin-sdk.md) before any ambisonic clip produces sound
through the expected decode path — this is not a missing setting to toggle,
it is a plugin that must exist in the project first.

| Fact | Detail | Source |
|---|---|---|
| Decoder selection | `Edit > Project Settings > Audio` → **Ambisonic Decoder Plugin** dropdown, populated only by decoder plugins already present in the project | [Ambisonic audio](https://docs.unity3d.com/Manual/AmbisonicAudio.html), [Audio Manager](https://docs.unity3d.com/Manual/class-AudioManager.html) |
| Decoder source | Write a custom decoder against the Native Audio Plugin SDK, or obtain one from a VR hardware/SDK vendor | [Ambisonic audio](https://docs.unity3d.com/Manual/AmbisonicAudio.html) |
| Supported order | First-order ambisonics only — no second-order support | [Developing an ambisonic decoder](https://docs.unity3d.com/Manual/AudioDevelopAmbisonicDecoder.html) |
| Output formats | Binaural stereo and quad (plugin-dependent) | same |

## Import and playback

| Step | Requirement | Source |
|---|---|---|
| Source file format | Multi-channel B-format, **ACN** component ordering, **SN3D** normalization | [Ambisonic audio](https://docs.unity3d.com/Manual/AmbisonicAudio.html) |
| Import setting | Enable the **Ambisonic** checkbox on the AudioClip importer | same |
| Playback | Assign the ambisonic clip as the `AudioSource`'s clip; disable **Spatialize** on that source — the selected decoder plugin performs decoding and spatialization together, converting from ambisonic format to the project's speaker format | same |

**Critical caveat**: **Reverb Zones are disabled for ambisonic audio
clips** — a scene that relies on Reverb Zones for its usual room ambience
will not apply them to an ambisonic-driven soundscape.

## Writing a decoder (escalation only)

| Requirement | Detail | Source |
|---|---|---|
| Effect definition flag | Must set `UnityAudioEffectDefinitionFlags_IsAmbisonicDecoder` during plugin scanning | [Developing an ambisonic decoder](https://docs.unity3d.com/Manual/AudioDevelopAmbisonicDecoder.html) |
| Data struct | Must implement `UnityAudioAmbisonicData`, including `ambisonicOutChannels` — auto-populated from the project's configured speaker layout | same |
| Packaging | Build via the Native Audio Plugin SDK, compile per target platform, package as a platform library, drop into the project's `Assets` folder — it then appears under the Ambisonic Decoder Plugin dropdown automatically | same |

Writing a decoder is [native-audio-plugin-sdk.md](native-audio-plugin-sdk.md)
territory — do not scope a feature around a custom decoder without routing
through that escalation path first.
