---
name: unity-audio-mixer
description: >
  Technique for Unity's audio system and Audio Mixer: `AudioSource`,
  `AudioListener`, `AudioClip` import/compression/streaming, `AudioMixer`,
  `AudioMixerGroup`, exposed parameters (`SetFloat`/`GetFloat`/`ClearFloat`),
  snapshots (`TransitionTo`), Sends/Receives, Duck Volume, AudioSource
  Filters versus Mixer Effects (Low/High Pass, Echo, Distortion, Reverb,
  Chorus, Flange, Compressor, Pitch Shifter), Audio Random Container,
  ambisonic decoder plugins, the Native Audio Plugin SDK, and the Audio
  Profiler. Use when wiring, routing, or diagnosing sound in a Unity scene.
  Not for: non-audio Profiler modules (`unity-profiler-diagnostics`);
  third-party audio middleware/platform SDKs (`tech-lead-sdk-platform`);
  netcode audio timing (`netcode-engineer`); the gameplay rule triggering a
  sound (`csharp-engineer`); audio-reactive VFX (`technical-artist`).
---

# Unity Audio & Audio Mixer — Playback, Routing, Effects, Diagnostics

## Bundled resources

### References
Read-only context, loaded on demand so SKILL.md itself stays short.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Manual and Scripting API roots, the version pin, and the two documentation gaps in this domain | Starting any task here, or confirming what a page actually states |
| [audio-import-and-clips.md](references/audio-import-and-clips.md) | Source formats, Compression Format, Load Type, streaming overhead, `AudioClip.LoadAudioData`/`UnloadAudioData` | Importing a sound or diagnosing a load stall |
| [audio-source-and-listener.md](references/audio-source-and-listener.md) | Every `AudioSource` property, rolloff modes, `AudioListener`'s one-per-scene rule, playback methods | Placing or scripting an `AudioSource`/`AudioListener` |
| [audio-mixer-core.md](references/audio-mixer-core.md) | Groups, views, Attenuation, Sends/Receives/Duck Volume, exposed parameters, snapshots, the `AudioMixer`/`AudioMixerGroup`/`AudioMixerSnapshot` API | Building or scripting the mixer graph |
| [filters-vs-effects.md](references/filters-vs-effects.md) | The full Filter catalog and Mixer Effect catalog, parameter tables for each | Choosing which DSP component to add, and where |
| [audio-random-container.md](references/audio-random-container.md) | ARC settings, playback modes, pitch-range gotcha vs. plain `AudioClip` | Any repeated SFX that needs clip/volume/pitch variation |
| [native-audio-plugin-sdk.md](references/native-audio-plugin-sdk.md) | The native DSP plugin build/import contract, mandatory `audioplugin` filename prefix | The built-in catalog cannot express the requested DSP |
| [ambisonic-audio.md](references/ambisonic-audio.md) | Ambisonic import/playback path, the no-built-in-decoder gate, decoder authoring contract | 360°/XR soundfield content |
| [audio-profiler-and-settings.md](references/audio-profiler-and-settings.md) | Audio Profiler metrics, the Virtual/voice columns, Project Settings > Audio | A voice-count, CPU, or memory complaint needs a number |

## 1. Objective
Get sound routed, mixed, and audible on the pipeline the project actually
uses, without the class of failure that reports success in the console while
producing silence: an `AudioSource` left on the implicit Output default that
never reaches a mixer's ducking or snapshot, a `SetFloat` call to a typo'd
exposed-parameter name that returns `false` and changes nothing, an
ambisonic clip playing through a project with no decoder plugin installed,
or a voice silently virtualized past `Max Real Voices` with nothing in the
Inspector showing why.

## 2. Role
Act as the audio specialist: import clips correctly, configure
`AudioSource`/`AudioListener`, build the mixer graph (groups, effects,
sends, snapshots), and diagnose playback/performance issues with the Audio
Profiler. You do not decide which gameplay event triggers a sound, you do
not own general (non-audio) Profiler work, and you do not integrate
third-party audio middleware.

## 3. When to invoke this skill
- Importing an audio file and choosing Compression Format/Load Type for its actual length and trigger frequency.
- Setting up or tuning an `AudioSource`'s 2D/3D behaviour, rolloff, or output routing.
- Building the Audio Mixer graph: groups, Sends/Receives, Duck Volume, snapshots, exposed parameters.
- Deciding between an AudioSource Filter and a Mixer Effect for a requested DSP treatment.
- Randomizing repeated SFX (footsteps, impacts, weapon fire) via Audio Random Container.
- Wiring 360°/XR ambisonic audio, or authoring a custom native DSP/decoder plugin.
- A sound is silent, stutters, or a scripted mixer change has no effect, and the cause needs the Audio Profiler.
- Negative trigger: general CPU/GPU/Memory/Rendering Profiler work — that's `unity-profiler-diagnostics`; this skill owns only the Audio module.
- Negative trigger: integrating Wwise/FMOD or a platform-native audio SDK — that's `tech-lead-sdk-platform`.
- Negative trigger: the client-server timing of when a networked sound event fires — that's `netcode-engineer`.
- Negative trigger: the gameplay rule deciding a sound should play (a health threshold, a combat event) — that lives in `Game.Core.*` per `coding-principles.md`; this skill only wires the resulting playback call.
- Negative trigger: an audio-reactive shader or particle system driven by spectrum data — that's `technical-artist`.

## 4. How to use this skill
1. **Decide which layer owns the change before opening a reference** — sound design (import settings, `AudioSource`/`AudioListener` placement, the mixer graph) sits in `Game.Client.*`; the trigger condition for a sound is a gameplay rule that belongs in `Game.Core.*` per `coding-principles.md`'s Shared Core integrity section.
2. **Set the AudioClip import settings by lifetime and length, not by habit** — per [audio-import-and-clips.md](references/audio-import-and-clips.md): short, frequently-triggered SFX default to Decompress On Load with PCM or ADPCM so they play with no per-call decode cost, while long music/dialog stream as Vorbis so they never sit fully decompressed in memory.
3. **Configure `AudioSource` 2D/3D behaviour from `spatialBlend` and rolloff mode, not from Volume alone**, per [audio-source-and-listener.md](references/audio-source-and-listener.md) — a UI cue wants `spatialBlend = 0`, a positional sound wants `1`, and Custom rolloff is the only mode where the curve itself decides falloff shape.
4. **Route every non-trivial AudioSource through an `AudioMixerGroup`, never leave Output on the implicit Audio Listener default** — per [audio-mixer-core.md](references/audio-mixer-core.md), routing is what makes ducking, snapshots, and per-category volume possible later; retrofitting it after dozens of sources exist is the expensive version of the same change.
5. **Pick Filter vs Mixer Effect by attachment point, not by name** — per [filters-vs-effects.md](references/filters-vs-effects.md): a Filter processes one Source before the mix and is reordered only by moving the component itself; an Effect processes a whole Group's already-mixed signal and is freely reorderable in that Group's Inspector.
6. **Drive runtime mixer state through exposed parameters and snapshot transitions, never by fighting the two for the same knob** — per [audio-mixer-core.md](references/audio-mixer-core.md): `AudioMixer.SetFloat` hands a parameter to script control until `ClearFloat` returns it to snapshots, and `AudioMixerSnapshot.TransitionTo`/`AudioMixer.TransitionToSnapshots` blend over time rather than cut.
7. **Reach for Audio Random Container before hand-rolling clip/volume/pitch randomization in script** — per [audio-random-container.md](references/audio-random-container.md), for repeated SFX; write custom randomization only when a container's Playback Mode and Avoid Repeating Last genuinely cannot express the requested rule (YAGNI otherwise).
8. **Escalate to the Native Audio Plugin SDK only once the built-in Filter/Effect catalog cannot express the DSP**, per [native-audio-plugin-sdk.md](references/native-audio-plugin-sdk.md) — it is a per-platform C/C++ build with a mandatory `audioplugin` filename prefix, not a routine authoring path.
9. **Treat Ambisonic playback as a 360°/XR-specific path, and confirm a decoder plugin is installed before promising it works** — per [ambisonic-audio.md](references/ambisonic-audio.md), Unity ships no built-in ambisonic decoder, so the feature is inert until one is installed.
10. **Pool `AudioSource` GameObjects for any sound triggered at high frequency**, per `performance-and-algorithms.md`'s Memory discipline section — `Instantiate`/`Destroy` per gunshot or footstep is exactly the allocation churn that section forbids; reuse a fixed pool instead.
11. **Diagnose a playback or performance complaint from the Audio Profiler module before proposing a fix**, per [audio-profiler-and-settings.md](references/audio-profiler-and-settings.md) — the Virtual column explains "why is this sound silent" against Max Real Voices, and DSP CPU vs Streaming CPU tells whether the cost is mixing or decode.
12. **Keep the gameplay decision in `Game.Core.*` and only the playback call here** — the health threshold that triggers a low-health sting is a game rule per `coding-principles.md`'s Shared Core integrity section; this skill wires the `AudioSource`/mixer call that rule drives.
13. **When a required input is missing — target platform, whether the project has multiplayer audio-sync needs, whether a decoder plugin already exists — ask rather than assume**, and flag the assumption made if the requester wants to proceed anyway.

## 5. Specific goals / tasks this skill performs
- AudioClip import configuration: format, compression, load type, streaming.
- AudioSource/AudioListener setup: 2D/3D blend, rolloff, output routing, playback API.
- Audio Mixer graph authoring: groups, effect chains, Sends/Receives, Duck Volume, exposed parameters, snapshots.
- Filter vs Mixer Effect selection and parameter tuning.
- Audio Random Container setup for varied repeated SFX.
- Ambisonic audio wiring and native audio plugin escalation for custom DSP/decoders.
- Diagnosing silent, stuttering, or unresponsive audio via the Audio Profiler and Project Settings > Audio.
- Out of scope: general Profiler modules (`unity-profiler-diagnostics`); third-party audio middleware/platform SDKs (`tech-lead-sdk-platform`); netcode audio timing (`netcode-engineer`); the gameplay rule a sound visualises (`csharp-engineer`); audio-reactive VFX (`technical-artist`).

## 6. Output format
```
## Audio Work — <feature/scene name>
- Import settings: <compression format, load type, per-clip rationale — or "not applicable">
- AudioSource/Listener setup: <spatial blend, rolloff mode, output group — or "not applicable">
- Mixer graph: <groups, effects added, sends/receives/duck volume, exposed parameters — or "none">
- Snapshot/runtime control: <SetFloat/TransitionTo usage, or "static, no runtime mixer control">
- Randomization: <Audio Random Container settings, or "not applicable">
- Escalations: <native plugin / ambisonic decoder used, or "none">
- Diagnosis: <Audio Profiler evidence behind any perf/silence claim, or "not applicable">
- Layer: <Game.Client.* components/assets; the gameplay trigger stays in Game.Core.*>
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what the delivered audio setup does not cover>
- Latent concerns: <failure modes not yet triggered: assumptions holding only under current conditions, thresholds not yet reached, deferred trade-offs>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: "Add footstep sounds that don't get repetitive, routed through a footsteps bus that ducks when dialogue plays."
- Output: created an Audio Random Container with 5–6 footstep clips, Playback Mode Shuffle, Avoid Repeating Last set above 1, no per-clip Weight field available so variation came from per-clip Volume trims instead. Assigned it to an `AudioSource.resource` on the player. Routed that source's Output to a new "Footsteps" `AudioMixerGroup`. Added a Send on Footsteps into a Duck Volume unit on the "Dialogue" group's chain, so dialogue playback compresses footsteps automatically — no script-side ducking logic needed.

**Example 2**
- Input: "Just randomize the footstep clip and volume in the PlayFootstep() script, it's simpler than setting up an asset."
- Output: declined as the default — per §4's Audio Random Container step, hand-rolled `Random.Range` clip-picking with manual volume jitter duplicates what Playback Mode + Volume Random Range already do, and loses Avoid Repeating Last's anti-repetition guarantee for free. Built the ARC asset instead; scripting is limited to `source.resource = playlist; source.Play();`.

**Example 3**
- Input: "Combat music should swell when the player takes damage, then fade back to explore music after a few seconds."
- Output: two snapshots ("Explore", "Combat") capturing the music group's Volume and a Low Pass Effect's cutoff. On damage, called `mixer.FindSnapshot("Combat").TransitionTo(0.5f)`; after the cooldown, transitioned back to "Explore" over 3 seconds. Did not use `SetFloat` for the swell itself, since two discrete states blending over time is exactly what snapshots are for — `SetFloat` was reserved for the master volume slider, an independent exposed parameter.

## 8. Edge cases & guardrails
- Never leave a Mixer parameter change on `SetFloat` alone when the design calls for a mood change — check whether a snapshot transition is the correct tool first; `SetFloat` and snapshots fighting over the same parameter produces visibly wrong blends.
- Never assume `SetFloat`/`GetFloat`/`ClearFloat` failed loudly — a typo'd exposed-parameter name returns `false` silently; verify the exact string against the Inspector's exposed-parameter name.
- Never promise ambisonic playback works without first confirming a decoder plugin is installed — Unity ships none built-in, and the feature is otherwise inert.
- Never reach for the Native Audio Plugin SDK before exhausting the built-in Filter/Effect catalog — it is a per-platform native build commitment, not a routine authoring step (YAGNI).
- Never `Instantiate`/`Destroy` an `AudioSource` GameObject per one-shot sound in a hot path — pool it, per `performance-and-algorithms.md`'s Memory discipline section.
- Never assert a numeric default this skill's references flag as unconfirmed (Duck Volume parameters, some AudioSource/ARC slider bounds) — confirm in the Editor Inspector instead of inventing a number.
- If the target Unity version differs from the `6000.5` pin in [root-links.md](references/root-links.md), confirm UI paths before relying on any step here — the Audio Mixer UI has changed shape across majors before.
- If it is unclear which layer a change belongs in — a gameplay rule vs. a sound-design detail — ask rather than assume; do not let a threshold or condition drift into `Game.Client.*` code.
