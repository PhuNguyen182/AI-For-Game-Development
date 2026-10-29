# Audio Import & AudioClip

Sources: Manual `AudioFiles-*`, `class-AudioClip`; API `AudioClip`. Formats: .mp3 .aiff/.aif .wav .ogg .flac, tracker .mod .xm .it .s3m (no waveform preview; use Compressed In Memory). Up to 8 channels.

## Compression Format

| Format | Cost | Best for |
|---|---|---|
| PCM | No decode CPU, largest | Short, frequent SFX |
| ADPCM | ~3.5x smaller, slight CPU, artifacts on smooth signals | Footsteps, impacts |
| Vorbis/MP3 | Highest CPU, best ratio (Quality slider) | Music, dialog |

Decompressed size exceeds the file size: Vorbis ~10x, ADPCM ~3.5x, paid per simultaneous voice for Compressed In Memory.

## Load Type (per platform)

| Load Type | Use when |
|---|---|
| Decompress On Load | Short clips needing instant, glitch-free play |
| Compressed In Memory | Medium clips; memory matters more than decode cost |
| Streaming | Long music/dialog; ~200 KB overhead even with nothing loaded |

WebGL forces Decompress On Load whatever is configured.

## Importer settings
Force To Mono (Normalize only applies with it), Load In Background (async load at start, default off), Ambisonic (see [ambisonic-audio.md](ambisonic-audio.md)), Sample Rate Setting (Preserve default / Optimize / Override), Quality (default High), Preload Audio Data (default on).

## Scripting
- `AudioClip.LoadAudioData()` loads ahead of play so `Play()` does not stall. Returns `true` at once if already loaded; synchronous unless `loadInBackground`; poll `loadState`.
- `AudioClip.UnloadAudioData()` works only for file-backed clips, not procedural ones; call `LoadAudioData()` again to reuse.
- `length`, `channels`, `frequency`, `samples` are readable before the data loads.
- Unverified: exact `AudioDataLoadState` member names; read them from IDE autocomplete.
