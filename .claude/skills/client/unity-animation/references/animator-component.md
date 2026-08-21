# Animator Component — fields, culling, update timing, scripting

Sources: [Animator component](https://docs.unity3d.com/Manual/class-Animator.html), [Animator scripting API](https://docs.unity3d.com/ScriptReference/Animator.html), [Mecanim performance and optimization](https://docs.unity3d.com/Manual/MecanimPeformanceandOptimization.html).
Covers: SKILL.md §4 — **"Set Culling Mode and Update Mode deliberately rather than leaving the defaults"**, **"Drive parameters through cached hashes rather than strings"**.

The component that runs a finished graph, and the two fields on it that
decide cost and correctness. The graph itself is
[animator-controller.md](animator-controller.md); budgeting the rig behind it
is [performance-and-faq.md](performance-and-faq.md).

## Fields

| Field | What it decides | Source |
|---|---|---|
| Controller | The graph this component runs; replacing it at runtime resets the state machine, which is why a variant swap uses an override instead | [Animator component](https://docs.unity3d.com/Manual/class-Animator.html) |
| Avatar | The humanoid rig definition; absent on a Humanoid setup, nothing retargets and the character does not move correctly | [Animator component](https://docs.unity3d.com/Manual/class-Animator.html) |
| Apply Root Motion | Whether the component moves the transform from the clip's root curves — overridden entirely once the movement callback is implemented | [Animator component](https://docs.unity3d.com/Manual/class-Animator.html) |
| Culling Mode | How much evaluation is skipped when no renderer is visible | [Animator component](https://docs.unity3d.com/Manual/class-Animator.html) |
| Update Mode | Which clock drives evaluation | [Animator component](https://docs.unity3d.com/Manual/class-Animator.html) |

## Culling Mode

| Mode | Behaviour off screen | Choose when | Source |
|---|---|---|---|
| Always Animate | Full evaluation regardless of visibility — the default, and a cost paid for every character nobody can see | Something off screen must keep advancing exactly, such as a synchronised crowd | [Animator component](https://docs.unity3d.com/Manual/class-Animator.html) |
| Cull Update Transforms | The state machine and events keep running; transform and IK writes are skipped | The common choice — state stays correct and the expensive part stops | [Animator component](https://docs.unity3d.com/Manual/class-Animator.html) |
| Cull Completely | Evaluation stops entirely and resumes where it left off, so the pose can visibly jump when the character returns | Nothing depends on the state advancing while hidden, and the jump is acceptable | [Animator component](https://docs.unity3d.com/Manual/class-Animator.html) |

**Critical caveat**: culling depends on renderer visibility, not on distance
or logic. A character with a renderer still technically in frame is not
culled, however far away it is.

## Update Mode

| Mode | Clock | Choose when | Source |
|---|---|---|---|
| Normal | Scaled frame time | Ordinary gameplay animation | [Animator component](https://docs.unity3d.com/Manual/class-Animator.html) |
| Animate Physics | The fixed step | The animation drives a kinematic body, so animation and physics stay in step instead of visibly disagreeing | [Animator component](https://docs.unity3d.com/Manual/class-Animator.html) |
| Unscaled Time | Frame time ignoring the time scale | Menus and UI that must keep animating while the game is paused | [Animator component](https://docs.unity3d.com/Manual/class-Animator.html) |

## Scripting

| Member | Effect | Source |
|---|---|---|
| Parameter setters by name | Hash the string on every call, which is the per-frame cost `performance-and-algorithms.md` names — the integer overloads exist to avoid it | [Animator scripting API](https://docs.unity3d.com/ScriptReference/Animator.html) |
| String-to-hash | Converts a parameter or state name once; store the result in a static readonly field rather than recomputing it | [Animator scripting API](https://docs.unity3d.com/ScriptReference/Animator.html) |
| Play | Jumps straight to a state with no blend, which is right for a hard cut and wrong for anything that should ease | [Animator scripting API](https://docs.unity3d.com/ScriptReference/Animator.html) |
| Cross-fade | Blends into a state over a given duration, bypassing the authored transition and its conditions | [Animator scripting API](https://docs.unity3d.com/ScriptReference/Animator.html) |
| Reset trigger | Clears a trigger nothing consumed, which is the fix for a state change firing much later than the input that set it | [Animator scripting API](https://docs.unity3d.com/ScriptReference/Animator.html) |
| Current and next state info | Reports the state, its normalised time and whether a transition is in progress; normalised time keeps counting past one on a looping clip | [Animator scripting API](https://docs.unity3d.com/ScriptReference/Animator.html) |
| Layer weight | Read and set at runtime, which is how an upper-body layer fades in rather than snapping | [Animator scripting API](https://docs.unity3d.com/ScriptReference/Animator.html) |
| Delta position and rotation | The root-motion delta for this frame, valid inside the movement callback | [Animator scripting API](https://docs.unity3d.com/ScriptReference/Animator.html) |
