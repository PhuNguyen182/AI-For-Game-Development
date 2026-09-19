# Brain, Priority, and Blends

Sources: [CinemachineBrain](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineBrain.html), [CinemachineCamera](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineCamera.html), [Blending](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineBlending.html).
Covers: SKILL.md §4 — **"Put exactly one `CinemachineBrain` on the rendering `Camera`, never on a `CinemachineCamera`"**, **"Match the Brain's Update Method to what the follow target is moved by"**, **"Switch cameras by changing Priority, never by toggling GameObjects active"**.

The Brain is the only component here that touches the real `Camera`. Every
`CinemachineCamera` is a source of a desired position and rotation; the Brain
picks between them, blends, and writes the result to the transform each
frame. That last part is the fact most worth carrying: the Brain **overwrites**
the camera transform, so any other script writing it is not conflicting, it is
being discarded.

| Piece | What it decides | Source |
|---|---|---|
| Brain placement | On the rendering `Camera` GameObject, exactly one. A Brain on a `CinemachineCamera` does nothing, and two Brains on one camera fight | [CinemachineBrain](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineBrain.html) |
| Update Method | Fixed, Late, or Smart Update. A follow target moved in `FixedUpdate` needs Fixed here, or the camera samples it between physics steps and judders — the same failure `unity-camera-fundamentals` describes for hand-written follows | [CinemachineBrain](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineBrain.html) |
| Blend Update Method | Separately controls when blends are evaluated, so a blend can stay frame-rate smooth while the camera itself updates on the physics clock | [CinemachineBrain](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineBrain.html) |
| `ActiveVirtualCamera` / `IsBlending` | What is live and whether a transition is in progress — the correct gate for gameplay that must wait for a cut to finish | [CinemachineBrain API](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/api/Unity.Cinemachine.CinemachineBrain.html) |

## Priority

| Behaviour | Consequence | Source |
|---|---|---|
| Highest priority among enabled cameras is live | Changing `Priority` is the supported way to switch shots, and the Brain blends into the new one | [CinemachineVirtualCameraBase](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/api/Unity.Cinemachine.CinemachineVirtualCameraBase.html) |
| Equal priorities resolve by most recently activated | Two cameras at the same value are not a stable tie — activation order decides, which makes it a dependency that is invisible in the Inspector | [CinemachineCamera](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineCamera.html) |
| Deactivating the live camera | Removes it from consideration rather than blending away from it, producing a cut | [CinemachineBrain](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineBrain.html) |
| `Follow` / `LookAt` | The targets a control pair consumes. A control component with no target does nothing and reports nothing | [CinemachineCamera API](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/api/Unity.Cinemachine.CinemachineCamera.html) |

## Blends

| Piece | What it decides | Source |
|---|---|---|
| Default Blend on the Brain | Applies to every transition that no specific rule covers — style and duration for the whole project, which is why changing it to fix one cut changes all of them | [Blending](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineBlending.html) |
| `CinemachineBlenderSettings` | An asset of from-to rules with wildcard entries, so one pair can cut while the rest ease | [CinemachineBlenderSettings](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/api/Unity.Cinemachine.CinemachineBlenderSettings.html) |
| Blend styles | Ease In Out, Ease In, Ease Out, Hard In, Hard Out, Linear, Cut, or a custom curve — Cut with a non-zero time is still a cut | [Blending](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineBlending.html) |
| Blends during a Timeline shot | The shot track drives transitions through clip overlap instead, overriding the Brain for its duration — see [timeline-and-channels.md](timeline-and-channels.md) | [Timeline integration](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineTimeline.html) |
