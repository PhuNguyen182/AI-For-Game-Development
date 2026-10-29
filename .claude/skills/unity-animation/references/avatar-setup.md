# Avatar Setup

Pages: `ConfiguringtheAvatar`, `class-Avatar`, `MuscleDefinitions`, `class-HumanTemplate`, `class-AvatarMask`, `Retargeting`, `RootMotion`, `ScriptingRootMotion`, `InverseKinematics`.

## Avatar
- Mapping tab: which bone fills each required humanoid slot; missing required bones = no valid Avatar = no retargeting.
- Pose: the model must be in the reference pose (T-pose) for mapping to mean anything; the pose warning is not fixed by remapping.
- Muscles and Settings: per-joint limits the solver respects (unusual proportions).
- Human Template: saves a mapping for models built the same way.
- Avatar Mask: limits body parts/transforms an animation writes; set on a layer or on an imported clip (separate settings).
- Retargeting needs source and target both Humanoid with valid, correctly posed Avatars. One Generic rig in the chain: the clip silently does not transfer.

## Root motion
| Choice | Effect |
|---|---|
| Baked into pose | Object does not travel — right for in-place locomotion driven by code |
| Applied by component | Transform moves from the clip's root curves — right when the animation is the movement |
| Movement callback (`OnAnimatorMove`) implemented | Component stops applying motion and hands the delta to your code; the object does not move unless the callback applies it |

Root Transform settings choose which axes the root contributes and the reference; sideways sliding is usually a bake setting, not a clip fault.
- Animates but never moves: motion baked into pose, or callback without applying the delta.
- Drifts or fights the controller: root motion plus a script writing the transform; last writer wins per frame.

## Inverse kinematics
- `OnAnimatorIK` runs only on layers with **IK Pass** enabled; otherwise it compiles and never runs.
- Humanoid only (Generic has no goals).
- Set position/rotation weights every frame the callback runs; a stale weight keeps the limb pinned.
- Look-at is a separate weighted target (body, head, eyes) distinct from limb goals.
- Constraint chains beyond these goals are Animation Rigging: no owning skill.
