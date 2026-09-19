# Audio Import & AudioClip — Formats, Compression, Load Type, Streaming

Sources: [Audio Files](https://docs.unity3d.com/Manual/AudioFiles.html), [Audio clip compatibility](https://docs.unity3d.com/Manual/AudioFiles-compatibility.html), [Audio clip compression](https://docs.unity3d.com/Manual/AudioFiles-compression.html), [Importing audio files](https://docs.unity3d.com/Manual/AudioFiles-import.html), [Introduction to audio files](https://docs.unity3d.com/Manual/AudioFiles-introduction.html), [AudioClip](https://docs.unity3d.com/Manual/class-AudioClip.html), [AudioClip scripting API](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AudioClip.html).
Covers: SKILL.md §4 — **"Set the AudioClip import settings by lifetime and length, not by habit"**.

Every imported audio file becomes an `AudioClip` asset with a separate Load
Type and Compression Format per build target. The wrong pairing for a given
clip's length and trigger frequency either stalls playback on first use or
wastes memory holding fully-decompressed audio no one asked for.

## Supported source formats

| Format | Extension | Note | Source |
|---|---|---|---|
| MPEG Layer 3 | `.mp3` | | [Compatibility](https://docs.unity3d.com/Manual/AudioFiles-compatibility.html) |
| Audio Interchange File Format | `.aiff` / `.aif` | | same |
| Microsoft Wave | `.wav` | | same |
| Ogg Vorbis | `.ogg` | | same |
| Free Lossless Audio Codec | `.flac` | | same |
| Tracker modules | `.mod`, `.xm`, `.it`, `.s3m` | No waveform preview in the importer; use Compressed In Memory for a low footprint | same |

Unity supports mono, stereo, and multichannel clips up to **8 channels**.

## Compression Format — pick by CPU vs memory budget

| Format | Mechanism | Cost | Best for | Source |
|---|---|---|---|---|
| PCM | Uncompressed | Minimal CPU (no decode), largest file/memory size | Short, frequently-triggered SFX where CPU matters more than memory | [Compression](https://docs.unity3d.com/Manual/AudioFiles-compression.html) |
| ADPCM | Fixed ~3.5x compression | Slightly more CPU than PCM; noticeable artifacts on smooth signals (music, ambience) | Short/medium SFX (footsteps, impacts) as a memory/CPU middle ground | same |
| Vorbis/MP3 | Variable compression via Quality slider | Highest CPU (decode cost); best compression ratio of the three | Long files — background music, dialog | same |

**Critical caveat**: decompressing at runtime costs memory the compressed
source size does not show — Vorbis decompresses to roughly **10x** its
compressed size, ADPCM to roughly **3.5x**. A "Compressed In Memory" clip pays
that expansion on every simultaneous voice, not once.

## Load Type — per platform, on the AudioClip importer

| Load Type | Behavior | Use when | Source |
|---|---|---|---|
| Decompress On Load | Fully decompressed into memory at load time | Short clips where instant, glitch-free playback matters more than memory | [AudioClip](https://docs.unity3d.com/Manual/class-AudioClip.html) |
| Compressed In Memory | Stays compressed in RAM, decoded per-play | Medium clips where memory matters more than the small decode cost | same |
| Streaming | Read from disk/storage as it plays | Long music/dialog that should never be fully resident | same |

**Critical caveat**: a Streaming clip carries an overhead of **~200 KB even
with no audio data loaded** — it is not free just because it is not resident.
WebGL browsers force **Decompress On Load** regardless of the configured
setting, due to memory bugs in the other load types on that target.

## AudioClip importer settings

| Setting | Effect | Default | Source |
|---|---|---|---|
| Force To Mono | Mixes multi-channel audio to mono before packing | Off | [AudioClip](https://docs.unity3d.com/Manual/class-AudioClip.html) |
| Normalize | Normalizes audio during the Force To Mono mixdown (only relevant with Force To Mono on) | Off | same |
| Load In Background | Loads the clip asynchronously when the game starts, instead of blocking | Off | same |
| Ambisonic | Marks the clip as ambisonic-encoded — see [ambisonic-audio.md](ambisonic-audio.md) | Off | same |
| Sample Rate Setting | Preserve / Optimize / Override Sample Rate, per platform | Preserve Sample Rate | same |
| Quality | Compression amount for a compressed clip | High | same |
| Preload Audio Data | Preloads the clip once its scene finishes loading | Enabled | same |

## Scripting — explicit load/unload

```csharp
// Force an explicit load ahead of playback instead of letting AudioSource.Play()
// trigger an implicit, potentially stalling, dynamic load.
if (!this.footstepClip.LoadAudioData())
{
    Debug.LogWarning("Footstep clip failed to begin loading.");
}
```

| Member | Effect | Caveat | Source |
|---|---|---|---|
| `AudioClip.LoadAudioData()` | Loads the clip's data into memory ahead of playback | Returns `true` immediately for an already-loaded clip; loads synchronously unless `loadInBackground` is set; poll `AudioClip.loadState` for progress | [LoadAudioData](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AudioClip.LoadAudioData.html) |
| `AudioClip.UnloadAudioData()` | Releases the clip's audio data from memory | Only works for clips backed by an actual sound file asset, not a procedurally-generated `AudioClip`; must call `LoadAudioData()` again to reuse | [UnloadAudioData](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AudioClip.UnloadAudioData.html) |
| `AudioClip.length` / `.channels` / `.frequency` / `.samples` | Read-only metadata, queryable **before** the clip's full audio data is loaded | Use this to schedule playback without forcing a full load up front | [AudioClip](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/AudioClip.html) |

The exact `AudioClip.AudioDataLoadState` enum member names were not
resolvable from a primary source in this pass — confirm in the Editor/IDE
autocomplete rather than asserting exact names from this file.
