# Audio Random Container — Playlist-Style SFX Randomization

Sources: [Audio Random Container](https://docs.unity3d.com/Manual/AudioRandomContainer.html), [Audio Random Container fundamentals](https://docs.unity3d.com/Manual/AudioRandomContainer-fundamentals.html), [Audio Random Container settings reference](https://docs.unity3d.com/Manual/AudioRandomContainer-UI.html), [Create a randomized playlist](https://docs.unity3d.com/Manual/Create-randomized-playlist.html), [AudioResource scripting API](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/Audio.AudioResource.html), [AudioSource.pitch scripting API](https://docs.unity3d.com/6000.3/Documentation/ScriptReference/AudioSource-pitch.html).
Covers: SKILL.md §4 — **"Reach for Audio Random Container before hand-rolling clip/volume/pitch randomization in script"**.

An Audio Random Container (ARC) is an `AudioResource` asset (the same base
type as `AudioClip`) that stores a playlist plus rules for how it plays —
which clip, at what volume/pitch offset, and on what trigger. It replaces
the common script pattern of picking a random clip from an array and
scaling volume/pitch by hand for repeated SFX (footsteps, impacts, weapon
fire).

## Assigning and playing

| Fact | Detail | Source |
|---|---|---|
| Requires AudioSource | ARC only plays through an `AudioSource` — it is not a standalone playable asset | [Create a randomized playlist](https://docs.unity3d.com/Manual/Create-randomized-playlist.html) |
| Assignment | Assign the ARC asset to `AudioSource.resource` (the field also usable for a plain `AudioClip`) | same |
| Creation | `Assets > Create > Audio > Audio Random Container`, or `Window > Audio > Audio Random Container` | same |
| No dedicated runtime-config API | Volume/pitch ranges, trigger mode, and loop count are asset-authored; runtime interaction goes through the normal `AudioSource` API (`Play`, `Stop`, `isPlaying`) against the assigned resource | [AudioResource](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/Audio.AudioResource.html) |

```csharp
// Swap the resource, then drive it through the ordinary AudioSource API —
// ARC has no separate playback API of its own.
this.footstepSource.resource = this.footstepPlaylist;
this.footstepSource.Play();
```

## Settings

| Field | Effect | Source |
|---|---|---|
| Volume / Volume Random Range | Adds to the AudioSource's own volume; min/max both 0 disables randomization | [Settings reference](https://docs.unity3d.com/Manual/AudioRandomContainer-UI.html) |
| Pitch / Pitch Random Range | Adds to the AudioSource's own pitch; shared across every AudioSource referencing this container | same |
| Audio Clips list | Reorderable clip list; each entry has an Active toggle and its own per-clip Volume offset — **there is no per-clip Weight field**; list edits take effect from the next clip picked, not retroactively | same |
| Playback Mode: Sequential | Plays clips in list order; disables triggers and offset | same |
| Playback Mode: Shuffle | Removes a clip from the pick pool once played, until the whole list has cycled (no repeat until exhausted) | same |
| Playback Mode: Random | Keeps every clip in the pool — a clip can repeat immediately | same |
| Avoid Repeating Last | Number of picks that must occur before a given clip can repeat | same |
| Trigger: Manual | No internal auto-play — requires an explicit `AudioSource.Play()` call | same |
| Trigger: Automatic — Pulse | Fires on a steady interval measured from the start of each pulse (example given: automatic rifle) | same |
| Trigger: Automatic — Offset | Fires an interval after the **previous clip finished**, i.e. a gap between clips | same |
| Loop: Infinite / Clips / Cycles | Infinite never stops; Clips counts individual plays; Cycles counts full list passes (a cycle = one full pass of the Audio Clips list) | same + [Fundamentals](https://docs.unity3d.com/Manual/AudioRandomContainer-fundamentals.html) |

**Critical caveat**: none of the ARC pages publish literal numeric defaults
for Volume dB bounds, pitch cents, Automatic Trigger Time, or Loop Count —
the Manual describes each field qualitatively only. Confirm exact numbers in
the Editor Inspector rather than asserting them from documentation.

## Pitch range differs from a plain AudioClip

| Resource on `AudioSource.resource` | Valid pitch | Reason | Source |
|---|---|---|---|
| `AudioClip` | −3 to 3 | Standard clamp | [AudioSource.pitch](https://docs.unity3d.com/6000.3/Documentation/ScriptReference/AudioSource-pitch.html) |
| `AudioRandomContainer` | 0.0001 to 3.0 | ARC does not support reverse/pause playback from pitch; an out-of-range value logs a console warning and is clamped | same |

**Critical caveat**: switching a source's resource from an `AudioClip` to an
ARC auto-clamps any pitch value already outside `[0.0001, 3.0]` — a pitch
script tuned against the AudioClip range can silently clamp differently
after the swap.
