# Animator Controller — states, transitions, parameters, Blend Trees, layers

Sources: [Animation state machines](https://docs.unity3d.com/Manual/AnimationStateMachines.html), [State machine basics](https://docs.unity3d.com/Manual/StateMachineBasics.html), [Animation state](https://docs.unity3d.com/Manual/class-State.html), [Animation transition](https://docs.unity3d.com/Manual/class-Transition.html), [State machine transitions](https://docs.unity3d.com/Manual/StateMachineTransitions.html), [Animation parameters](https://docs.unity3d.com/Manual/AnimationParameters.html), [Blend trees](https://docs.unity3d.com/Manual/animation-blend-trees.html), [1D blending](https://docs.unity3d.com/Manual/BlendTree-1DBlending.html), [2D blending](https://docs.unity3d.com/Manual/BlendTree-2DBlending.html), [Direct blending](https://docs.unity3d.com/Manual/BlendTree-DirectBlending.html), [Animation layers](https://docs.unity3d.com/Manual/AnimationLayers.html), [Nested state machines](https://docs.unity3d.com/Manual/NestedStateMachines.html), [StateMachineBehaviours](https://docs.unity3d.com/Manual/StateMachineBehaviours.html).
Covers: SKILL.md §4 — **"Build the graph from explicit transitions and reserve Any State for genuine interrupts"**, **"Pick the Blend Tree form from the shape of the parameter driving it"**.

The graph itself and the fields on it that behave differently from how they
read. What the component does with the finished graph is in
[animator-component.md](animator-component.md).

## Transitions

| Field | What it decides | Source |
|---|---|---|
| Has Exit Time | The transition waits until the source clip reaches a normalised point before it can take — enabled on an interrupt, it makes the interrupt refuse to fire | [Animation transition](https://docs.unity3d.com/Manual/class-Transition.html) |
| Transition Duration and Fixed Duration | The blend length, in seconds when fixed and as a fraction of the source clip otherwise; the seconds form outlives a shorter override clip — see [animator-override-controller.md](animator-override-controller.md) | [Animation transition](https://docs.unity3d.com/Manual/class-Transition.html) |
| Transition Offset | Where in the destination clip playback begins, which is how a blend into a run picks up mid-stride instead of restarting it | [Animation transition](https://docs.unity3d.com/Manual/class-Transition.html) |
| Interruption Source | Whether an in-progress transition can be cut short at all; left at none, later input is ignored until the blend finishes | [Animation transition](https://docs.unity3d.com/Manual/class-Transition.html) |
| Can Transition To Self | On an Any State transition, whether it retriggers the state already playing — enabled, a repeated trigger restarts the animation from the top | [State machine transitions](https://docs.unity3d.com/Manual/StateMachineTransitions.html) |
| Conditions | Parameter tests that must all hold; a transition with no condition and no exit time takes immediately | [Animation transition](https://docs.unity3d.com/Manual/class-Transition.html) |

**Critical caveat**: Any State is for genuine global interrupts. Its defaults
are wrong for that job in two ways at once — exit time stops it interrupting,
and self-transition restarts a state that was already correct.

## States and parameters

| Subject | What it decides | Source |
|---|---|---|
| State speed and multiplier | Playback rate, optionally driven by a float parameter, which is how one clip serves several movement speeds | [Animation state](https://docs.unity3d.com/Manual/class-State.html) |
| Write Defaults | Whether properties not animated by the state are reset to their defaults; inconsistent settings across states are a classic source of a value that sticks after a transition | [Animation state](https://docs.unity3d.com/Manual/class-State.html) |
| Trigger parameters | Consumed by the transition that uses them, and otherwise stay armed — a trigger set when nothing can take it fires later, at a moment no code explains | [Animation parameters](https://docs.unity3d.com/Manual/AnimationParameters.html) |
| Entry and Exit nodes | Where a sub-state machine hands control in and back out; an Exit with nowhere to go returns to the parent's default | [Nested state machines](https://docs.unity3d.com/Manual/NestedStateMachines.html) |
| `StateMachineBehaviour` | A script attached to a state, receiving enter, update and exit callbacks; the exit callback does not run if the component is disabled or destroyed while the state is active | [StateMachineBehaviours](https://docs.unity3d.com/Manual/StateMachineBehaviours.html) |
| Solo and Mute | Editor-time isolation of one branch for debugging; left on, it changes runtime behaviour and looks like a bug | [Solo and mute](https://docs.unity3d.com/Manual/AnimationSoloMute.html) |

## Blend Trees

| Form | Driven by | Use when | Source |
|---|---|---|---|
| 1D | One float | The blend is a single axis such as speed; thresholds can be computed from each clip's own root-motion speed rather than guessed | [1D blending](https://docs.unity3d.com/Manual/BlendTree-1DBlending.html) |
| 2D Simple Directional | Two floats, one clip per direction | Movement clips point in distinct directions with no two the same way | [2D blending](https://docs.unity3d.com/Manual/BlendTree-2DBlending.html) |
| 2D Freeform Directional | Two floats | Several clips share a direction at different magnitudes — walk and run forward together | [2D blending](https://docs.unity3d.com/Manual/BlendTree-2DBlending.html) |
| 2D Freeform Cartesian | Two floats | The axes are not direction and magnitude at all, such as speed against turn angle | [2D blending](https://docs.unity3d.com/Manual/BlendTree-2DBlending.html) |
| Direct | One parameter per child | Each clip's weight is controlled independently, for additive facial or damage-reaction layers | [Direct blending](https://docs.unity3d.com/Manual/BlendTree-DirectBlending.html) |

## Layers

| Subject | What it decides | Source |
|---|---|---|
| Weight | A layer above the base starts at zero and contributes nothing until raised — the usual reason a newly added layer appears to do nothing | [Animation layers](https://docs.unity3d.com/Manual/AnimationLayers.html) |
| Blending mode | Override replaces the layers below within the mask, additive adds on top of them; choosing the wrong one produces either a dead layer or a doubled pose | [Animation layers](https://docs.unity3d.com/Manual/AnimationLayers.html) |
| Mask | Restricts the layer to a body region, which is what makes an upper-body aim pose coexist with a lower-body run | [Animation layers](https://docs.unity3d.com/Manual/AnimationLayers.html) |
| Sync and Timing | Reuses another layer's state machine, optionally taking its timing, so a variant set stays structurally identical without being rebuilt | [Animation layers](https://docs.unity3d.com/Manual/AnimationLayers.html) |
| IK Pass | Enables the IK callback for this layer — see [avatar-setup.md](avatar-setup.md); off, the callback never runs | [Animation layers](https://docs.unity3d.com/Manual/AnimationLayers.html) |
