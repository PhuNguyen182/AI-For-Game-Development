# Mecanim Overview — Animation Types, clip import, events

Sources: [Mecanim animation system](https://docs.unity3d.com/Manual/animation-mecanim.html), [Rig tab](https://docs.unity3d.com/Manual/FBXImporter-Rig.html), [Introduction to animation clips](https://docs.unity3d.com/Manual/AnimationClips.html), [Animation from external sources](https://docs.unity3d.com/Manual/AnimationsImport.html), [Animation window guide](https://docs.unity3d.com/Manual/AnimationEditorGuide.html), [Loop optimization](https://docs.unity3d.com/Manual/LoopingAnimationClips.html), [Animation Events on imported clips](https://docs.unity3d.com/Manual/AnimationEventsOnImportedClips.html), [Generic animations](https://docs.unity3d.com/Manual/GenericAnimations.html), [Legacy animation](https://docs.unity3d.com/Manual/animation-legacy.html).
Covers: SKILL.md §4 — **"Set the Animation Type before anything else is imported"**, **"Author clip content in the Animation window and flow in the Animator window"**.

The decision made once per model, and what a clip carries. Configuring the
Avatar that a Humanoid type creates is next door in
[avatar-setup.md](avatar-setup.md); the art itself belongs to
`unity-2d-sprite` or the modelling pipeline.

## Animation Type

| Type | What it buys | What it costs | Source |
|---|---|---|---|
| Humanoid | Clips retarget across any other Humanoid rig, and the muscle system normalises the pose | A per-frame retargeting pass every Generic rig avoids, plus the Avatar configuration step | [Rig tab](https://docs.unity3d.com/Manual/FBXImporter-Rig.html) |
| Generic | No retargeting cost and no Avatar to configure; the right default for creatures, props, vehicles and sprite swaps | Clips are bound to their own rig and cannot be shared with a differently built one | [Generic animations](https://docs.unity3d.com/Manual/GenericAnimations.html) |
| Legacy | Nothing new; it exists for content that already depends on the pre-Mecanim component | No state machine, no blend trees, no retargeting — never the choice for new work | [Legacy animation](https://docs.unity3d.com/Manual/animation-legacy.html) |

**Critical caveat**: changing the type after clips and controllers exist
invalidates the bindings built against it. Settle it at import, not once the
graph is half built.

## Clip import settings

| Setting | What it decides | Source |
|---|---|---|
| Loop Time and Loop Pose | Whether the clip repeats, and whether the ends are matched so the seam disappears; the match quality indicator is what tells you the seam will show | [Loop optimization](https://docs.unity3d.com/Manual/LoopingAnimationClips.html) |
| Root Transform position and rotation bake | Whether motion stays in the animation or becomes root motion the component applies — the source of both a character that drifts and one that never moves | [Animation from external sources](https://docs.unity3d.com/Manual/AnimationsImport.html) |
| Clip splitting | Cutting one long imported take into named clips by frame range, which is how a single exported animation becomes a usable set | [Splitting animations](https://docs.unity3d.com/Manual/Splittinganimations.html) |
| Curves | Extra float curves authored alongside the clip and readable as Animator parameters, for driving something the pose cannot express | [Curves on imported clips](https://docs.unity3d.com/Manual/AnimationCurvesOnImportedClips.html) |
| Mask on an imported clip | Restricts which parts of the rig the clip writes, which is a different mask from the one a layer applies | [Mask animation clips](https://docs.unity3d.com/Manual/AnimationMaskOnImportedClips.html) |
| Euler curve resampling | Whether rotation curves are resampled to quaternions on import; disabling it preserves authored Euler interpolation that resampling would round off | [Euler curve import](https://docs.unity3d.com/Manual/AnimationEulerCurveImport.html) |

## The two windows

| Window | Owns | Source |
|---|---|---|
| Animation window | The contents of one clip — keys, curves, and Animation Events | [Animation window guide](https://docs.unity3d.com/Manual/AnimationEditorGuide.html) |
| Animator window | The graph between clips — states, transitions, parameters, layers | [Animator window](https://docs.unity3d.com/Manual/AnimatorWindow.html) |

An event belongs to a clip, never to a state. A state that plays two clips
through a blend therefore has no single event timeline, which is why an event
appears to fire at the wrong moment when the blend weight shifts.

## Animation Events

| Rule | Consequence | Source |
|---|---|---|
| Handler location | The method must be on a component of the same GameObject as the `Animator`; one on a child is never found and nothing reports it | [Animation Events](https://docs.unity3d.com/Manual/script-AnimationWindowEvent.html) |
| Parameter count | At most one parameter, of a small set of supported types — a handler with two is not called | [Animation Events](https://docs.unity3d.com/Manual/script-AnimationWindowEvent.html) |
| Final-frame placement | An event on the very last frame of a non-looping clip is unreliable; place it slightly earlier | [Animation Events on imported clips](https://docs.unity3d.com/Manual/AnimationEventsOnImportedClips.html) |
| Imported clips | Events on an imported clip are added in the import settings, not in the Animation window, since the clip asset is read-only | [Animation Events on imported clips](https://docs.unity3d.com/Manual/AnimationEventsOnImportedClips.html) |
| Scope | An event signals that a moment was reached; deciding what that means is `Game.Core.*`'s, per `coding-principles.md` | [Animation Events](https://docs.unity3d.com/Manual/script-AnimationWindowEvent.html) |
