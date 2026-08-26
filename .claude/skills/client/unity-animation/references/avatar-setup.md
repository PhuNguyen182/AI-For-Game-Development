# Avatar Setup — mapping, pose, retargeting, masks, root motion, IK

Sources: [Configuring the Avatar](https://docs.unity3d.com/Manual/ConfiguringtheAvatar.html), [Avatar Mapping tab](https://docs.unity3d.com/Manual/class-Avatar.html), [Muscle and Settings tab](https://docs.unity3d.com/Manual/MuscleDefinitions.html), [Human Template](https://docs.unity3d.com/Manual/class-HumanTemplate.html), [Avatar Mask](https://docs.unity3d.com/Manual/class-AvatarMask.html), [Retargeting humanoid animation](https://docs.unity3d.com/Manual/Retargeting.html), [How root motion works](https://docs.unity3d.com/Manual/RootMotion.html), [Scripting root motion](https://docs.unity3d.com/Manual/ScriptingRootMotion.html), [Inverse kinematics](https://docs.unity3d.com/Manual/InverseKinematics.html).
Covers: SKILL.md §4 — **"Verify the Avatar's pose before investigating a retargeting problem"**, **"Decide where root motion comes from at import time"**.

Everything that only exists once a rig is Humanoid, plus the two motion
questions that produce the most confusing symptoms. Constraint-based rigs are
the Animation Rigging package and are not covered here or anywhere in this
project — see [root-links.md](root-links.md).

## Avatar configuration

| Element | What it decides | Source |
|---|---|---|
| Mapping tab | Which bone in the model fills each required humanoid slot; required bones missing means no valid Avatar and therefore no retargeting at all | [Avatar Mapping tab](https://docs.unity3d.com/Manual/class-Avatar.html) |
| Pose | The model must be in the reference pose for the mapping to mean anything; a pose warning is about the pose and will not be fixed by remapping bones | [Configuring the Avatar](https://docs.unity3d.com/Manual/ConfiguringtheAvatar.html) |
| Muscles and Settings | Per-joint rotation limits the retargeting solver respects, which is how a rig with unusual proportions stops producing impossible poses | [Muscle and Settings tab](https://docs.unity3d.com/Manual/MuscleDefinitions.html) |
| Human Template | Saves a mapping for reuse across models built the same way, so a whole character set is configured once | [Human Template](https://docs.unity3d.com/Manual/class-HumanTemplate.html) |
| Avatar Mask | Restricts which body parts or transforms an animation writes; applied on a layer or on an imported clip, and the two are separate settings | [Avatar Mask](https://docs.unity3d.com/Manual/class-AvatarMask.html) |

**Critical caveat**: retargeting requires both source and target to be
Humanoid with a valid, correctly posed Avatar. One Generic rig anywhere in
the chain means the clip simply does not transfer, with no error to explain it.

## Root motion

| Choice | Effect | Source |
|---|---|---|
| Baked into pose at import | The movement stays inside the animation and the object does not travel — correct for an in-place locomotion clip driven by code | [How root motion works](https://docs.unity3d.com/Manual/RootMotion.html) |
| Applied by the component | The component moves the transform from the clip's root curves — correct when the animation itself is the movement | [How root motion works](https://docs.unity3d.com/Manual/RootMotion.html) |
| Taken over by the movement callback | Implementing the callback stops the component applying motion automatically and hands the delta to your code, so the object stops moving entirely if the callback does not apply it | [Scripting root motion](https://docs.unity3d.com/Manual/ScriptingRootMotion.html) |
| Root Transform settings | Which axes the root actually contributes, and against what reference — a character that slides sideways is usually a bake setting rather than a clip fault | [How root motion works](https://docs.unity3d.com/Manual/RootMotion.html) |

| Symptom | Where to look | Source |
|---|---|---|
| Character animates but never moves | Motion baked into the pose, or the movement callback implemented without applying the delta | [Scripting root motion](https://docs.unity3d.com/Manual/ScriptingRootMotion.html) |
| Character drifts or fights the controller | Both root motion and a script writing the transform, with the last writer winning per frame | [How root motion works](https://docs.unity3d.com/Manual/RootMotion.html) |

## Inverse kinematics

| Subject | What it decides | Source |
|---|---|---|
| The IK pass | The callback is invoked only on layers with the IK pass enabled; without it the callback exists, compiles, and never runs | [Inverse kinematics](https://docs.unity3d.com/Manual/InverseKinematics.html) |
| Humanoid only | Goal-based IK is part of the humanoid system; a Generic rig has no goals to set | [Inverse kinematics](https://docs.unity3d.com/Manual/InverseKinematics.html) |
| Goal weights | Position and rotation weights are set every frame the callback runs, so a weight left from a previous frame keeps the limb pinned | [Inverse kinematics](https://docs.unity3d.com/Manual/InverseKinematics.html) |
| Look-at | A separate weighted target with its own body, head and eye contribution, distinct from the limb goals | [Inverse kinematics](https://docs.unity3d.com/Manual/InverseKinematics.html) |
| Scope boundary | Constraint chains beyond these goals are the Animation Rigging package, which no skill in this project owns | [Inverse kinematics](https://docs.unity3d.com/Manual/InverseKinematics.html) |
