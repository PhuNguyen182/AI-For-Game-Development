# Audio Mixer — Groups, Snapshots, Sends/Receives, Ducking, Exposed Parameters

Sources: [Audio Mixer landing](https://docs.unity3d.com/Manual/audio-mixer-landing.html), [Introduction to Audio Mixer](https://docs.unity3d.com/Manual/AudioMixerOverview.html), [Audio Mixer window](https://docs.unity3d.com/Manual/AudioMixer.html), [Audio Mixer window specifics](https://docs.unity3d.com/Manual/AudioMixerSpecifics.html), [AudioGroup Inspector](https://docs.unity3d.com/Manual/AudioMixerInspectors.html), [Audio Mixer usage and API overview](https://docs.unity3d.com/Manual/AudioMixerUsage.html), [AudioMixer scripting API](https://docs.unity3d.com/ScriptReference/Audio.AudioMixer.html), [AudioMixerGroup scripting API](https://docs.unity3d.com/ScriptReference/Audio.AudioMixerGroup.html), [AudioMixerSnapshot scripting API](https://docs.unity3d.com/ScriptReference/Audio.AudioMixerSnapshot.html).
Covers: SKILL.md §4 — **"Route every non-trivial AudioSource through an `AudioMixerGroup`, never leave Output on the implicit Audio Listener default"**, **"Drive runtime mixer state through exposed parameters and snapshot transitions, never by fighting the two for the same knob"**.

The Audio Mixer is a tree-based asset of `AudioMixerGroup`s (buses), each
group accepting multiple inputs and producing one output. Signal flow is
**Audio Source → Audio Mixer → Audio Listener** — 3D spatialization and
distance attenuation happen at the Source, before the signal ever reaches
the mixer. The group hierarchy is independent of the scene's GameObject
hierarchy.

## Table of contents
- [Groups, views, and the effect chain](#groups-views-and-the-effect-chain)
- [Sends, Receives, and Duck Volume](#sends-receives-and-duck-volume)
- [Exposed parameters and snapshots](#exposed-parameters-and-snapshots)
- [Scripting API](#scripting-api)

## Groups, views, and the effect chain

| Concept | Mechanism | Source |
|---|---|---|
| Group | Mixes its inputs into exactly one output (except Sends). Every mixer has a Master group | [Introduction to Audio Mixer](https://docs.unity3d.com/Manual/AudioMixerOverview.html) |
| View | An organizational filter — toggles which groups are visible in the Mixer window. Purely visual, does not change audio behavior | [Audio Mixer window specifics](https://docs.unity3d.com/Manual/AudioMixerSpecifics.html) |
| Solo | On a group, mutes everything except that group's own subtree | same |
| Mute | Excludes the group from the audible mix | same |
| Bypass | Disables all effect units on the group without removing them | same |
| Attenuation | The one effect unit every group has by default and cannot remove, though it can be reordered. Range **−80 dB to +20 dB**. Its VU meter reads the level immediately after attenuation is applied | [AudioGroup Inspector](https://docs.unity3d.com/Manual/AudioMixerInspectors.html) |
| Multi-mixer routing | A group's output can route into a group on a **different** Audio Mixer asset, chaining mixers together | [Audio Mixer window](https://docs.unity3d.com/Manual/AudioMixer.html) |
| Effect ordering | Effect units on a group are freely reorderable by dragging, or via right-click Move Up/Move Down — see [filters-vs-effects.md](filters-vs-effects.md) for how this differs from AudioSource-level Filters | [AudioGroup Inspector](https://docs.unity3d.com/Manual/AudioMixerInspectors.html) |

**Critical caveat**: WebGL only partially supports the Audio Mixer — confirm
target platform before designing a build around it.

## Sends, Receives, and Duck Volume

| Unit | Mechanism | Source |
|---|---|---|
| Send | Diverts a copy of the group's signal to a chosen destination Effect Unit elsewhere in the graph, at a configurable Send Level; destination is **unassigned by default** and must be picked from a dropdown | [AudioGroup Inspector](https://docs.unity3d.com/Manual/AudioMixerInspectors.html) |
| Receive | Mixes in whatever a Send routes to it; carries no parameters of its own | same |
| Duck Volume | Side-chain compression driven by a Send's signal — must receive from at least one Send to have any effect | same |

**Critical caveat**: soloing a **Receive** unit silences playback — this is
documented as intentional, not a bug. The Manual publishes no parameter
table for Duck Volume (Threshold/Ratio/Attack/Release) — those fields exist
only in the editor UI itself; do not assert numeric defaults for them.

## Exposed parameters and snapshots

| Concept | Mechanism | Source |
|---|---|---|
| Exposed parameter | Any group parameter (Pitch, Volume, Send Level, Wet Level, an effect's own parameter) can be right-clicked → **Expose 'X' to script**, making it settable by name from code. Renaming it (right-click → Rename) changes the string key every calling script must use | [AudioGroup Inspector](https://docs.unity3d.com/Manual/AudioMixerInspectors.html) |
| Snapshot | Captures every parameter's current value across the whole mixer. Created via **+** in the Snapshots panel; one snapshot can be marked **Set as Start Snapshot** | [Audio Mixer window specifics](https://docs.unity3d.com/Manual/AudioMixerSpecifics.html) |
| Snapshots as sub-assets | Snapshots appear as sub-assets of the Audio Mixer asset, browsable in the Project window | same |

## Scripting API

```csharp
// Hand a parameter to script control; it stays script-controlled until ClearFloat.
// Call from Start() or later — never from Awake/OnEnable/AfterSceneLoad.
this.mixer.SetFloat("MusicVolume", -6f);

// Blend to a mood snapshot over 2 seconds instead of cutting instantly.
AudioMixerSnapshot combatSnapshot = this.mixer.FindSnapshot("Combat");
combatSnapshot.TransitionTo(2f);
```

| Member | Signature | Behavior | Source |
|---|---|---|---|
| `AudioMixer.SetFloat` | `bool SetFloat(string name, float value)` | Sets an exposed parameter; that parameter is then script-controlled until `ClearFloat`. Returns `false` silently on a name that doesn't match — never throws | [SetFloat](https://docs.unity3d.com/ScriptReference/Audio.AudioMixer.SetFloat.html) |
| `AudioMixer.GetFloat` | `bool GetFloat(string name, out float value)` | Reads an exposed parameter's current value (snapshot-driven or script-driven) | [GetFloat](https://docs.unity3d.com/ScriptReference/Audio.AudioMixer.GetFloat.html) |
| `AudioMixer.ClearFloat` | `bool ClearFloat(string name)` | Returns a parameter from script control back to snapshot/transition control | [ClearFloat](https://docs.unity3d.com/ScriptReference/Audio.AudioMixer.ClearFloat.html) |
| `AudioMixer.FindSnapshot` | `AudioMixerSnapshot FindSnapshot(string name)` | Exact, case-sensitive name match; no fuzzy lookup | [FindSnapshot](https://docs.unity3d.com/ScriptReference/Audio.AudioMixer.FindSnapshot.html) |
| `AudioMixerSnapshot.TransitionTo` | `void TransitionTo(float timeToReach)` | Interpolates every captured parameter toward this snapshot's stored values over `timeToReach` seconds | [TransitionTo](https://docs.unity3d.com/ScriptReference/Audio.AudioMixerSnapshot.TransitionTo.html) |
| `AudioMixer.TransitionToSnapshots` | `void TransitionToSnapshots(AudioMixerSnapshot[] snapshots, float[] weights, float timeToReach)` | Blends **multiple** snapshots by weight — for a continuum game state (health, map position) rather than a binary switch | [TransitionToSnapshots](https://docs.unity3d.com/ScriptReference/Audio.AudioMixer.TransitionToSnapshots.html) |
| `AudioSource.outputAudioMixerGroup` | `AudioMixerGroup outputAudioMixerGroup` | The sole hook that routes a source into the mixer graph, settable from the Inspector or from code | [AudioSource-outputAudioMixerGroup](https://docs.unity3d.com/ScriptReference/AudioSource-outputAudioMixerGroup.html) |

**Critical caveat**: `SetFloat`/`GetFloat`/`ClearFloat` never throw on a
typo'd parameter name — they return `false`. A silently-ignored `SetFloat`
call is the most common "the mixer isn't responding to my script" bug in
this system, and nothing in the console reports it.
