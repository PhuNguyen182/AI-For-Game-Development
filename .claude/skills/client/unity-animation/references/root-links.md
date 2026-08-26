# Root Links — Unity Mecanim animation

Source: the root index pages listed below, as provided for this skill.
Covers: the whole skill — provenance and version anchor for every file in
this folder.

Anchors every link in this folder. Unity's animation Manual pages are
published unversioned and resolve to the current documentation, so there is
no version segment to keep. Everything under these roots is Mecanim; the
systems listed at the end sit beside it and are deliberately excluded.

## Roots

| Root | Holds | Source |
|---|---|---|
| Animation system | The whole system, and which part owns which asset | [Animation system overview](https://docs.unity3d.com/Manual/AnimationOverview.html) |
| Mecanim | The current animation system this skill covers | [Mecanim animation system](https://docs.unity3d.com/Manual/animation-mecanim.html) |
| Animation clips | Clip authoring, import, events, curves | [Animation clips](https://docs.unity3d.com/Manual/animation-clips-landing.html) |
| Avatar | Humanoid rig configuration and retargeting | [Avatar creation and setup](https://docs.unity3d.com/Manual/AvatarCreationandSetup.html) |
| Animator Controller | The state machine asset and its editor | [Animator Controller](https://docs.unity3d.com/Manual/animation-animator-controller.html) |
| Playables | The low-level graph the Animator itself runs on | [Playables API](https://docs.unity3d.com/Manual/Playables.html) |
| Performance | Rig cost and optimisation guidance | [Mecanim performance and optimization](https://docs.unity3d.com/Manual/MecanimPeformanceandOptimization.html) |

## Which file answers which question

| Question | File | Source |
|---|---|---|
| Which Animation Type, and how does the clip import | [mecanim-overview.md](mecanim-overview.md) | [Rig tab](https://docs.unity3d.com/Manual/FBXImporter-Rig.html) |
| Why does the retarget or the root motion misbehave | [avatar-setup.md](avatar-setup.md) | [Configuring the Avatar](https://docs.unity3d.com/Manual/ConfiguringtheAvatar.html) |
| Why does this transition or blend not do what it looks like | [animator-controller.md](animator-controller.md) | [Animation state machines](https://docs.unity3d.com/Manual/AnimationStateMachines.html) |
| Which component field or scripting call do I need | [animator-component.md](animator-component.md) | [Animator component](https://docs.unity3d.com/Manual/class-Animator.html) |
| How do variants share one graph | [animator-override-controller.md](animator-override-controller.md) | [Animator Override Controller](https://docs.unity3d.com/Manual/AnimatorOverrideController.html) |
| How do I compose a blend at runtime | [playables-api.md](playables-api.md) | [Playables graph](https://docs.unity3d.com/Manual/Playables-Graph.html) |
| What does this rig actually cost | [performance-and-faq.md](performance-and-faq.md) | [Modeling optimized characters](https://docs.unity3d.com/Manual/ModelingOptimizedCharacters.html) |

## Core type index

| Type | Source |
|---|---|
| `Animator` | [Animator](https://docs.unity3d.com/ScriptReference/Animator.html) |
| `AnimationClip`, `AnimationEvent`, `AnimationCurve` | [AnimationClip](https://docs.unity3d.com/ScriptReference/AnimationClip.html) |
| `Avatar`, `AvatarMask`, `AvatarIKGoal` | [Avatar Mask](https://docs.unity3d.com/Manual/class-AvatarMask.html) |
| `StateMachineBehaviour` | [StateMachineBehaviour](https://docs.unity3d.com/ScriptReference/StateMachineBehaviour.html) |
| `AnimatorOverrideController` | [AnimatorOverrideController](https://docs.unity3d.com/ScriptReference/AnimatorOverrideController.html) |
| `PlayableGraph` and the animation playable family | [Playables graph](https://docs.unity3d.com/Manual/Playables-Graph.html) |
| `Animation`, the pre-Mecanim component | [Legacy animation](https://docs.unity3d.com/Manual/animation-legacy.html) |

## Adjacent, and deliberately outside

| System | Why it is not here | Source |
|---|---|---|
| Timeline | Sequences tracks and clips on top of Playables; the authoring workflow is separate and no skill here owns it | [Timeline package](https://docs.unity3d.com/Packages/com.unity.timeline@latest) |
| Animation Rigging | Constraint-based runtime rigs, a separate installable package distinct from the goal-based IK pass covered in [avatar-setup.md](avatar-setup.md) | [Animation Rigging package](https://docs.unity3d.com/Packages/com.unity.animation.rigging@latest) |
| Cinemachine | Cameras that read Animator state — owned by `unity-cinemachine-authoring` | [Cinemachine package](https://docs.unity3d.com/Packages/com.unity.cinemachine@latest) |
| 2D Animation | Skeletal sprite rigging, distinct from driving a sprite swap through a Generic controller, which this skill does cover | [2D Animation package](https://docs.unity3d.com/Packages/com.unity.2d.animation@latest) |
