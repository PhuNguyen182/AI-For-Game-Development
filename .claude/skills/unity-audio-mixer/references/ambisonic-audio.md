# Ambisonic Audio

Sources: Manual `audio-ambisonic`, `AmbisonicAudio`, `AudioDevelopAmbisonicDecoder`, `class-AudioManager`.

Soundfield format for 360 video, XR and audio skyboxes; rotates with listener orientation and decodes to the project's speaker layout.

**Unity ships no built-in ambisonic decoder.** Install one (vendor VR SDK) or author one with the [Native Audio Plugin SDK](native-audio-plugin-sdk.md) before any ambisonic clip decodes. Do not scope a feature around a custom decoder without that escalation.

- Select it at `Edit > Project Settings > Audio` > Ambisonic Decoder Plugin; the dropdown lists only decoders already in the project.
- First-order only (no second-order); outputs binaural stereo and quad, plugin-dependent.
- Source file: multi-channel B-format, ACN ordering, SN3D normalisation.
- Enable Ambisonic on the clip importer. On the `AudioSource`, disable Spatialize; the decoder decodes and spatialises together.
- Reverb Zones are disabled for ambisonic clips.
