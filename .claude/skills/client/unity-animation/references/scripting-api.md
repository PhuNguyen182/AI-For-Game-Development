# Scripting API Cross-Reference — Unity Animation

Consolidated index of the `UnityEngine`/`UnityEngine.Playables` classes covered across this skill's reference files. Use this as a quick lookup; each row's "Covered in" column has the full member table and usage guidance.

## Runtime playback & control

| Type | Role | Covered in |
|---|---|---|
| `UnityEngine.Animator` | MonoBehaviour driving Animator Controller playback: `Play`/`CrossFade`, `SetFloat`/`SetBool`/`SetInteger`/`SetTrigger` (+ hashed overloads), `GetCurrentAnimatorStateInfo`, `runtimeAnimatorController`, `cullingMode`, `updateMode`, IK members. | [animator-component.md](animator-component.md) |
| `UnityEngine.Animator.StringToHash(string)` | Converts a parameter/state name to a cached `int` id for the hashed Animator overloads. | [animator-component.md](animator-component.md), [performance-and-faq.md](performance-and-faq.md) |
| `UnityEngine.AnimatorStateInfo` | Struct returned by `GetCurrentAnimatorStateInfo`/`GetNextAnimatorStateInfo` — normalized time, state name hash, loop flag. | [animator-component.md](animator-component.md) |
| `UnityEngine.AvatarIKGoal` | Enum identifying an IK target (`LeftFoot`, `RightFoot`, `LeftHand`, `RightHand`) for `SetIKPosition`/`SetIKRotation` calls inside `OnAnimatorIK`. | [avatar-setup.md](avatar-setup.md) |
| `OnAnimatorMove()` / `OnAnimatorIK(int layerIndex)` | MonoBehaviour message callbacks (not `Animator` methods) for scripted root motion / IK. | [animator-component.md](animator-component.md), [avatar-setup.md](avatar-setup.md) |
| `UnityEngine.AnimatorOverrideController` | Runtime clip-swap wrapper around a base `RuntimeAnimatorController`: `this[name]` indexer, `ApplyOverrides`, `GetOverrides`. | [animator-override-controller.md](animator-override-controller.md) |
| `UnityEngine.RuntimeAnimatorController` | Base type for both `AnimatorController` and `AnimatorOverrideController`; the type of `Animator.runtimeAnimatorController`. | [animator-component.md](animator-component.md), [animator-override-controller.md](animator-override-controller.md) |
| `UnityEngine.StateMachineBehaviour` | Script attached to a state/sub-state machine node (not a GameObject): `OnStateEnter`/`OnStateUpdate`/`OnStateExit`/`OnStateMove`/`OnStateIK`/`OnStateMachineEnter`/`OnStateMachineExit`. | [animator-controller.md](animator-controller.md) |

## Clip & event data

| Type | Role | Covered in |
|---|---|---|
| `UnityEngine.AnimationClip` | Asset type holding keyframed curve data; `legacy` flag, `length`, `events`, `SetCurve`. | [mecanim-overview.md](mecanim-overview.md) |
| `UnityEngine.AnimationEvent` | Event payload delivered to a matching-name handler method; exposes `floatParameter`/`intParameter`/`stringParameter`/`objectReferenceParameter`. | [mecanim-overview.md](mecanim-overview.md) |
| `UnityEngine.AnimationCurve` | Underlying curve type for custom clip curves and parameter-driving curves. | [mecanim-overview.md](mecanim-overview.md) |
| `UnityEngine.AvatarMask` | Body-part/transform inclusion mask, authored Humanoid (body diagram) or Transform (bone list); used on Animator layers and at import-time clip masking. | [avatar-setup.md](avatar-setup.md) |
| `UnityEngine.Avatar` | Runtime asset produced by Avatar Configuration; assigned to `Animator.avatar`. | [avatar-setup.md](avatar-setup.md) |
| `UnityEngine.Animation` / legacy `AnimationState` | Legacy (pre-Mecanim) playback component — `Play()`, `CrossFade()`; maintenance-only, do not use for new gameplay code. | [mecanim-overview.md](mecanim-overview.md) |

## Playables API (`UnityEngine.Playables` / `UnityEngine.Animations`)

| Type | Role | Covered in |
|---|---|---|
| `PlayableGraph` | Owns the graph's nodes/outputs; `Create()`, `Connect()`, `Play()`, `Evaluate()`, `SetTimeUpdateMode()`, `Destroy()` (must be called explicitly — not GC'd). | [playables-api.md](playables-api.md) |
| `Playable` / `PlayableExtensions` | Struct handle for a graph node; `SetInputWeight`/`GetInputWeight`, `SetTime`, `Pause`/`Play` via extension methods. | [playables-api.md](playables-api.md) |
| `PlayableOutput` / `PlayableOutputExtensions` | Struct handle for a graph output; `SetSourcePlayable()`. | [playables-api.md](playables-api.md) |
| `AnimationPlayableOutput` | Routes a playable's result into an `Animator`; `Create(graph, name, animator)`. | [playables-api.md](playables-api.md) |
| `AnimationClipPlayable` | Wraps one `AnimationClip` as a node; `Create(graph, clip)`. | [playables-api.md](playables-api.md) |
| `AnimationMixerPlayable` | Weighted N-input blend node; `Create(graph, inputCount)`. | [playables-api.md](playables-api.md) |
| `AnimationLayerMixerPlayable` | Layered N-input blend node with per-input `AvatarMask`/additive support. | [playables-api.md](playables-api.md) |
| `AnimatorControllerPlayable` | Wraps an existing `RuntimeAnimatorController` as a graph node; `Create(graph, controller)`. | [playables-api.md](playables-api.md) |
| `PlayableBehaviour` / `ScriptPlayable<T>` | Base class for fully custom per-frame playable logic (`PrepareFrame`/`ProcessFrame`), wrapped via `ScriptPlayable<T>.Create(graph[, behaviour])`. | [playables-api.md](playables-api.md) |
| `AnimationPlayableUtilities` | Convenience one-liners: `Play(animator, playable, graph)`, `PlayClip(animator, clip, out graph)`. | [playables-api.md](playables-api.md) |
| `AudioClipPlayable` / `AudioPlayableOutput` | Audio-side equivalents, usable on the same graph as an animation output. | [playables-api.md](playables-api.md) |
| `PlayableDirector` | Drives a `PlayableGraph` from a `PlayableAsset` (Timeline's component) — not required for hand-written graphs. | [playables-api.md](playables-api.md) |

## Editor-only (not usable at runtime / in builds)

| Type | Role | Covered in |
|---|---|---|
| `UnityEditor.Animations.AnimatorController` | Editor-only asset-manipulation API for reading/writing an Animator Controller's states/transitions/parameters from an Editor script. | [animator-controller.md](animator-controller.md) (Manual-level coverage only — see that file's note on unreachable Script Reference pages) |

## Practical guidance
- This table is an index, not a substitute for the per-topic reference file — always open the linked file for full member signatures, Inspector field tables, and project-specific guidance before writing code.
- Every hot-path Animator interaction (`Update()`, `FixedUpdate()`, per-tick AI/gameplay code) must use the hashed `int` overloads via a cached `Animator.StringToHash` result — see [animator-component.md](animator-component.md) and [performance-and-faq.md](performance-and-faq.md).
- `PlayableGraph` and its nodes are the one area of this API surface with manual native-resource lifecycle management (`Destroy()` is mandatory) — everything else here follows normal C#/Unity object lifetimes.
