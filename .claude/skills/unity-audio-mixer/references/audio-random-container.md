# Audio Random Container (ARC)

Sources: Manual `AudioRandomContainer`, `AudioRandomContainer-UI`, `Create-randomized-playlist`; API `Audio.AudioResource`, `AudioSource.pitch`.

An `AudioResource` (same base as `AudioClip`) holding a playlist plus play rules. It plays only through an `AudioSource`: assign to `AudioSource.resource`, then use the normal API. Create via `Assets > Create > Audio > Audio Random Container` or `Window > Audio > Audio Random Container`. No runtime-config API; volume/pitch ranges, trigger and loop are asset-authored.

```csharp
this.footstepSource.resource = this.footstepPlaylist;
this.footstepSource.Play();
```

## Settings
- Volume / Pitch (+ Random Range): add to the source's own values; Volume min/max both 0 disables it. Pitch is shared by every source using the container.
- Clips list: each has an Active toggle and its own Volume offset. No per-clip Weight field. List edits apply from the next pick.
- Playback Mode: Sequential (list order; disables triggers and offset); Shuffle (no repeat until the list is exhausted); Random (can repeat immediately).
- Avoid Repeating Last: picks required before a clip may repeat.
- Trigger: Manual (needs `Play()`); Automatic Pulse (fixed interval from each pulse start, e.g. automatic rifle); Automatic Offset (interval after the previous clip finished).
- Loop: Infinite, Clips (individual plays), Cycles (full list passes).
- Unverified: numeric bounds and defaults (volume dB, pitch cents, trigger time, loop count) are not published; read them in the Inspector.

## Pitch range
`AudioClip` allows -3..3. A container allows 0.0001..3.0 (no reverse or pause via pitch); out-of-range logs a warning and clamps. Swapping a source from clip to container silently re-clamps an existing pitch.
