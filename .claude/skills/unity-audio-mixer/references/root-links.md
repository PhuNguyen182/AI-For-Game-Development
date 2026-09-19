# Root Links — Unity Audio & Audio Mixer Documentation Roots

Source: the root index pages listed below, as provided for this skill.
Covers: the whole skill — provenance and version anchor for every file in
this folder.

Anchors every link in this folder to Unity **6000.5 (Unity 6.5)**. Anything
this skill cites resolves under one of these roots; anything that does not is
out of scope for the skill, not merely undocumented here.

| Root | Holds | Source |
|---|---|---|
| Manual — Audio | Import, AudioClip/AudioSource/AudioListener, filters, ambisonics, Random Container | [Audio Manual index](https://docs.unity3d.com/Manual/AudioReference.html) |
| Manual — Audio Mixer | Groups, snapshots, sends/receives, ducking, effects, native plugin SDK | [Audio Mixer landing](https://docs.unity3d.com/Manual/audio-mixer-landing.html) |
| Manual — Profiler | The Audio Profiler module | [Profiler modules reference](https://docs.unity3d.com/Manual/ProfilerAudio.html) |
| Scripting API | `AudioSource`, `AudioClip`, `AudioListener`, `AudioMixer`, `AudioMixerGroup`, `AudioMixerSnapshot`, `AudioRandomContainer` | [Scripting API index](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/index.html) |

Every other link in this `references/` folder is a specific page under these
roots, pinned to `6000.5`, each verified to resolve before inclusion — except
where noted inline as unresolved/unconfirmed in the source manual text itself.
Keep the `6000.5` segment when following any link from this skill — the
Render Graph/Audio Mixer UI has changed across majors before, so confirm the
installed Unity version before relying on a UI-path detail here. Consult the
live site for anything not covered below; Unity adds audio features between
releases (Audio Random Container itself shipped in a 2023.2-era release).

## Two documentation gaps to know about before citing anything from here

- The Manual **never publishes a parameter table** for the mixer's **Duck
  Volume** effect (Threshold/Ratio/Attack/Release) — only its mechanism is
  documented. Treat those fields as in-editor-only knowledge; do not invent
  numbers for them.
- Several AudioSource/AudioRandomContainer numeric defaults (exact dB bounds
  on Volume, exact seconds on Automatic Trigger Time, Priority's 0–256 range)
  are Unity Editor slider conventions, not values the Manual text itself
  states — [audio-source-and-listener.md](audio-source-and-listener.md) and
  [audio-random-container.md](audio-random-container.md) flag each one
  individually rather than asserting a false precision.
