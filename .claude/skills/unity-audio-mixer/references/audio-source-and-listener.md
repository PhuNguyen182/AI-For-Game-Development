# AudioSource & AudioListener

Sources: Manual `class-AudioSource`, `AudioSource-reference`, `class-AudioListener`; API `AudioSource`, `AudioListener`.

## AudioSource properties

| Property | Note |
|---|---|
| `outputAudioMixerGroup` | Only hook into the mixer graph; default none = straight to Listener ([audio-mixer-core.md](audio-mixer-core.md)) |
| `resource` / `clip` | `AudioClip` or [Audio Random Container](audio-random-container.md) |
| `spatialBlend` | 0 = 2D, 1 = 3D |
| `panStereo` | -1..1, 2D sounds |
| `rolloffMode` | Logarithmic / Linear / Custom; only Custom lets the curve decide shape. `maxDistance` is the zero point in Linear mode |
| `minDistance` | Volume stays at max inside it |
| `spread` | 0-360 degrees |
| `dopplerLevel` | 0 = none |
| `velocityUpdateMode` | Fixed vs Dynamic update; sets when Doppler velocity is calculated |
| `priority` | 0 highest .. 256 lowest (Editor convention, not a Manual bound) |
| `reverbZoneMix` | 0-1.1 |
| `bypassEffects` / `bypassListenerEffects` / `bypassReverbZones` | Skip Filters / Listener effects / Reverb Zones |
| `ignoreListenerVolume` / `ignoreListenerPause` | Opt out of `AudioListener.volume` / `.pause` |
| `pitch` | Editor slider -3..3 (not a Manual bound); an Audio Random Container narrows it |

## Playback
- `PlayOneShot(clip, volumeScale)` fires without touching `clip` or loop state.
- `PlayScheduled(double dspTime)` is sample-accurate (music loops); `PlayDelayed(seconds)`.
- `Play`, `Stop`, `Pause`, `UnPause`.
- Use an Audio Random Container instead of random-clip `PlayOneShot` when variation is the goal.

## AudioListener
- Exactly one active per scene; ships on Main Camera, moving it to the player is valid. The Manual does not publish the console warning text for zero or multiple listeners; do not quote one.
- Static `AudioListener.volume` (0-1) is master volume; `AudioListener.pause` pauses all audio.
- Reverb Zones and Listener effect components apply to all sound while the Listener is inside the zone or on that GameObject.
