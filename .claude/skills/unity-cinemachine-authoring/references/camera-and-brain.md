# Brain, Priority, and Blends

Base: https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/ — pages `manual/CinemachineBrain.html`, `manual/CinemachineCamera.html`, `manual/CinemachineBlending.html`; API `api/Unity.Cinemachine.<Type>.html`.

The Brain is the only component that touches the real `Camera`; each `CinemachineCamera` supplies a desired pose, the Brain picks, blends and overwrites the transform each frame.

| Piece | Rule |
|---|---|
| Placement | One Brain on the rendering `Camera`. On a `CinemachineCamera` it does nothing; two on one camera fight |
| Update Method | Fixed / Late / Smart. A target moved in `FixedUpdate` needs Fixed |
| Blend Update Method | Evaluates blends separately, so a blend stays frame-rate smooth while the camera updates on the physics clock |
| `ActiveVirtualCamera` / `IsBlending` | Gate gameplay that must wait for a cut to finish |
| Priority | Highest enabled priority is live and blended into. Equal → most recently activated. Deactivating the live camera cuts |
| `Follow` / `LookAt` | Targets the control pair consumes; a control component with no target does nothing and reports nothing |
| Default Blend | Applies to every transition no rule covers; changing it to fix one cut changes all |
| `CinemachineBlenderSettings` | Asset of from→to rules with wildcards; one pair can cut while the rest ease |
| Blend styles | Ease In Out/In/Out, Hard In/Out, Linear, Cut, custom curve. Cut with non-zero time is still a cut |
| During Timeline | Shot-clip overlap drives transitions instead ([timeline-and-channels.md](timeline-and-channels.md)) |
