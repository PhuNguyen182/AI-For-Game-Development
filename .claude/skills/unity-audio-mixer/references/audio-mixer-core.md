# Audio Mixer: Groups, Sends, Exposed Parameters, Snapshots

Sources: Manual `AudioMixerOverview`, `AudioMixerSpecifics`, `AudioMixerInspectors`; API `Audio.AudioMixer`, `AudioMixerSnapshot`.

Signal flow is Source -> Mixer -> Listener; 3D spatialisation and distance attenuation happen at the Source, before the mixer. The group tree is independent of the GameObject hierarchy. WebGL supports the mixer only partially.

## Groups
- Each group mixes its inputs into one output; every mixer has Master. A group can output into a group in a different mixer asset.
- Attenuation: the always-present, non-removable but reorderable unit; -80 to +20 dB.
- Solo mutes everything outside the group's subtree; Mute removes it from the mix; Bypass disables its effect units without removing them. Views are visual only.
- Effects on a group are drag-reorderable.

## Send, Receive, Duck Volume
- Send copies the group's signal to a destination Effect Unit at a Send Level; destination is unassigned by default, so pick it.
- Receive mixes in what Sends route to it; no parameters of its own.
- Duck Volume is side-chain compression and does nothing without at least one Send feeding it. Its parameters are Editor-only.
- Ducking recipe: the Send sits on the triggering group (e.g. Dialogue); its destination is the Duck Volume unit on the group to be ducked (e.g. Footsteps).
- Soloing a Receive silences playback; documented as intentional.

## Exposed parameters and snapshots
- Right-click a parameter -> Expose to script; Rename changes the string key every caller must use.
- A snapshot captures every parameter of the mixer; one can be marked "Set as Start Snapshot"; stored as sub-assets of the mixer asset.

## API

| Member | Behavior |
|---|---|
| `bool SetFloat(name, value)` | Hands the parameter to script control until `ClearFloat`. Returns `false`, never throws, on an unknown name. Call from `Start()` or later, not `Awake`/`OnEnable`/`AfterSceneLoad` |
| `bool GetFloat(name, out value)` | Current value, snapshot- or script-driven |
| `bool ClearFloat(name)` | Returns the parameter to snapshot control |
| `FindSnapshot(name)` | Exact, case-sensitive |
| `AudioMixerSnapshot.TransitionTo(seconds)` | Blends all captured parameters over time |
| `AudioMixer.TransitionToSnapshots(snapshots[], weights[], seconds)` | Weighted blend for continuum state (health, map position) |
| `AudioSource.outputAudioMixerGroup` | Routes a source into the graph |

`SetFloat` and a snapshot fighting over one parameter gives visibly wrong blends.
