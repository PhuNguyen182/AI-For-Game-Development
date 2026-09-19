# AudioSource & AudioListener — 2D/3D Playback, Rolloff, Routing

Sources: [AudioSource](https://docs.unity3d.com/Manual/class-AudioSource.html), [AudioSource reference](https://docs.unity3d.com/Manual/AudioSource-reference.html), [AudioSource overview](https://docs.unity3d.com/Manual/AudioSource-overview.html), [Creating an AudioSource](https://docs.unity3d.com/Manual/AudioSource-create.html), [AudioListener](https://docs.unity3d.com/Manual/class-AudioListener.html), [AudioSource scripting API](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AudioSource.html), [AudioListener scripting API](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AudioListener.html).
Covers: SKILL.md §4 — **"Configure `AudioSource` 2D/3D behaviour from `spatialBlend` and rolloff mode, not from Volume alone"**.

`AudioSource` plays an Audio Generator (an `AudioClip` or an [Audio Random
Container](audio-random-container.md)); `AudioListener` is the one-per-scene
receiver every audible source mixes into. Spatial behavior — not Volume — is
what decides whether a sound reads as 2D (UI, music) or 3D (positional world
sound).

## AudioSource — key inspector/scripting properties

| Property | Effect | Range/Default | Source |
|---|---|---|---|
| `clip` / Audio Generator | The `AudioClip` or Audio Random Container this source plays | — | [AudioSource reference](https://docs.unity3d.com/Manual/AudioSource-reference.html) |
| `outputAudioMixerGroup` / Output | Routes the source's signal into an `AudioMixerGroup` for shared processing | Default: no group (Audio Listener direct) | same; see [audio-mixer-core.md](audio-mixer-core.md) |
| `volume` | Loudness at 1 world unit distance | 0–1 | same |
| `pitch` | Playback speed/pitch multiplier, 1 = normal | commonly −3 to 3 in the Editor slider (not stated as a hard bound in the Manual) | same |
| `spatialBlend` | Blend between 2D (0) and full 3D (1) | 0–1 | same |
| `panStereo` | Stereo position for 2D sounds | −1 to 1 | same |
| `rolloffMode` | `Logarithmic` / `Linear` / `Custom` distance attenuation | — | [AudioRolloffMode](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AudioRolloffMode.html) |
| `minDistance` / `maxDistance` | Inside `minDistance` volume stays at max; in Linear mode `maxDistance` is where volume reaches zero | — | [AudioSource reference](https://docs.unity3d.com/Manual/AudioSource-reference.html) |
| `dopplerLevel` | Amount of Doppler effect applied to this source | 0 = none | same |
| `spread` | Spread angle of a 3D stereo/multichannel sound in speaker space | 0–360° | same |
| `priority` | Priority among all sources competing for a real voice | 0 (highest) – 256 (lowest), Editor convention — not stated as a literal bound in the Manual text | same |
| `reverbZoneMix` | Amount of signal routed into scene Reverb Zones | 0–1.1 | same |
| `bypassEffects` / `bypassListenerEffects` / `bypassReverbZones` | Skip Filter components / global Listener effects / Reverb Zones respectively | Disabled | same |
| `playOnAwake` / `loop` / `mute` | Standard playback flags | Disabled / Disabled / Disabled | same |
| `ignoreListenerVolume` | Excludes this source from `AudioListener.volume` scaling | Disabled | [AudioSource scripting API](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AudioSource.html) |
| `ignoreListenerPause` | Lets this source keep playing while `AudioListener.pause` is true | Disabled | same |
| `velocityUpdateMode` | Fixed vs dynamic update, affects Doppler calculation timing | — | same |

## AudioSource — playback API

| Method | Effect | Source |
|---|---|---|
| `Play()` | Plays the assigned clip/generator | [AudioSource](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AudioSource.html) |
| `PlayOneShot(AudioClip, float volumeScale = 1)` | Fires a clip once, scaled by `volumeScale`, without disturbing the source's main `clip` slot | same |
| `PlayScheduled(double time)` | Schedules playback at an absolute DSP time — use for sample-accurate sequencing (e.g. music loops) | same |
| `PlayDelayed(float delay)` | Plays after a delay in seconds | same |
| `Stop()` / `Pause()` / `UnPause()` | Standard transport controls | same |

```csharp
// Fire a one-shot without touching this source's assigned clip or its loop state.
this.impactSource.PlayOneShot(this.impactClips[Random.Range(0, this.impactClips.Length)]);
```

Reach for [Audio Random Container](audio-random-container.md) instead of this
pattern once the requirement is "pick a random clip and vary volume/pitch" —
it is the built-in tool for exactly that case.

## AudioListener

| Fact | Detail | Source |
|---|---|---|
| Role | "A microphone-like device" — receives every audible source in the scene and outputs to speakers | [AudioListener](https://docs.unity3d.com/Manual/class-AudioListener.html) |
| One per scene | Only one `AudioListener` may be active per scene for correct behavior | same |
| Default placement | Ships on Main Camera by default; moving it to the player GameObject is a common, valid alternative | same |
| `AudioListener.volume` (static) | Master game sound volume, 0–1 | [AudioListener scripting API](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AudioListener.html) |
| `AudioListener.pause` (static) | Pauses the whole audio system; sources with `ignoreListenerPause` keep playing | same |
| Reverb Zones / Listener effects | Apply to all audible sound while the Listener is inside a Reverb Zone's bounds, or via effect components on the Listener's own GameObject | [AudioListener](https://docs.unity3d.com/Manual/class-AudioListener.html) |

**Critical caveat**: the exact console warning text for zero or multiple
active listeners is not published in the Manual — the rule itself ("exactly
one Audio Listener per scene") is confirmed, but do not quote a specific
warning string as verbatim Unity output without checking the Console
directly.
