# Animator Controller

Pages: `AnimationStateMachines`, `class-State`, `class-Transition`, `StateMachineTransitions`, `AnimationParameters`, `animation-blend-trees`, `AnimationLayers`, `NestedStateMachines`, `StateMachineBehaviours`.

## Transitions
| Field | Decides |
|---|---|
| Has Exit Time | Waits for a normalised point in the source clip; on an interrupt it makes the interrupt refuse to fire |
| Transition Duration / Fixed Duration | Blend length: seconds when fixed, else fraction of source clip; seconds outlives a shorter override clip ([animator-override-controller.md](animator-override-controller.md)) |
| Transition Offset | Start point in the destination clip (a blend into a run picks up mid-stride) |
| Interruption Source | Whether an in-progress transition can be cut short; none = input ignored until the blend ends |
| Can Transition To Self | On Any State, whether it retriggers the playing state (restarts from the top) |
| Conditions | All must hold; no condition and no exit time = takes immediately |

Any State defaults are wrong for an interrupt twice over: exit time stops it interrupting, self-transition restarts a correct state.

## States and parameters
- State speed/multiplier can be driven by a float parameter (one clip, several speeds).
- Write Defaults: resets properties the state does not animate; inconsistent settings across states leave values stuck after a transition.
- Triggers are consumed by the transition using them, else stay armed.
- Sub-state machines: Entry/Exit nodes; an Exit with nowhere to go returns to the parent's default. Use for readability once the graph stops fitting on screen.
- `StateMachineBehaviour`: enter/update/exit callbacks; exit does not run if the component is disabled or destroyed while the state is active.
- Solo/Mute are Editor-time isolation; left on they change runtime behaviour and look like a bug.

## Blend Trees
| Form | Driven by | Use when |
|---|---|---|
| 1D | one float | single axis (speed); thresholds can be computed from each clip's root-motion speed |
| 2D Simple Directional | two floats | one clip per distinct direction |
| 2D Freeform Directional | two floats | several clips share a direction at different magnitudes (walk + run forward) |
| 2D Freeform Cartesian | two floats | axes are not direction/magnitude (speed vs turn angle) |
| Direct | one parameter per child | independent weights, e.g. additive facial/damage layers |

## Layers
- Weight: a non-base layer starts at 0 and does nothing until raised.
- Blending: Override replaces layers below within the mask; Additive adds on top — wrong choice gives a dead layer or doubled pose.
- Mask restricts to a body region (upper-body aim over lower-body run).
- Sync (optionally Timing) reuses another layer's state machine.
- IK Pass enables `OnAnimatorIK` for the layer ([avatar-setup.md](avatar-setup.md)).
