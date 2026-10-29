# Animator Component

Pages: `class-Animator`, `ScriptReference/Animator`, `MecanimPeformanceandOptimization`.

## Fields
- Controller: replacing it at runtime resets the state machine (use an override for variants).
- Avatar: required on Humanoid, else nothing retargets.
- Apply Root Motion: moves the transform from root curves; overridden entirely once `OnAnimatorMove` is implemented.

## Culling Mode
| Mode | Off screen | Choose when |
|---|---|---|
| Always Animate (default) | Full evaluation | Off-screen state must advance exactly (synchronised crowd) |
| Cull Update Transforms | State machine and events run; transform/IK writes skipped | Common choice |
| Cull Completely | Evaluation stops, resumes where left; pose can jump on return | Nothing depends on hidden advancement and the jump is acceptable |

Culling follows renderer visibility, not distance or logic: a renderer still in frame is not culled.

## Update Mode
| Mode | Clock | Choose when |
|---|---|---|
| Normal | Scaled frame time | Ordinary gameplay |
| Animate Physics | Fixed step | Animation drives a kinematic body |
| Unscaled Time | Ignores time scale | Menus/UI animating during pause |

## Scripting
- Parameter setters by name hash the string every call; use the integer overloads with `Animator.StringToHash` cached in a static readonly field.
- `Play` jumps with no blend; `CrossFade` blends over a duration, bypassing authored transitions and conditions.
- `ResetTrigger` clears an unconsumed trigger (the fix for a state change firing long after the input).
- `GetCurrentAnimatorStateInfo` / next-state info: state, normalised time (keeps counting past 1 on a loop), whether a transition is running.
- `SetLayerWeight` fades a layer in rather than snapping.
- `deltaPosition` / `deltaRotation`: this frame's root-motion delta, valid inside `OnAnimatorMove`.
