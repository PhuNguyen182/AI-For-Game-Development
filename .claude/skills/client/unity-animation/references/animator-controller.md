# Animator Controller

Sources: `https://docs.unity3d.com/Manual/animation-animator-controller.html`, `https://docs.unity3d.com/Manual/AnimationStateMachines.html`, and sub-pages (see [root-links.md](root-links.md)).

## Overview
An Animator Controller (`.controller` asset) "arranges and maintains a set of Animation Clips and associated Animation Transitions for a character or an animated GameObject," organized as one or more layered **Animation State Machines**, driven by **Animation Parameters**. It's created via **Assets > Create > Animator Controller**, and assigned by dragging it onto an `Animator` component's `Controller` field (see [animator-component.md](animator-component.md)).

The **Animator window** is the editor for this asset: **Parameters** panel (add via the `+` icon, delete via `Delete` key), **Layers** panel (create/reorder/configure layers), and the graph **Controller view** (right-click empty space to add a state; Alt-drag / Option-drag to pan; breadcrumb trail shows nesting when inside a sub-state machine or Blend Tree).

## State machine building blocks
A state machine is a flowchart of nodes (states) and connecting lines (transitions); only one state is active at a time per layer, and transitions fire when their conditions are satisfied.

| Node type | Description |
|---|---|
| **State** | Contains a `Motion` — either a single `AnimationClip` or a Blend Tree. |
| **Entry** | Fixed node every state machine has; branches to the default state, or to another state based on conditions if additional Entry transitions are configured. |
| **Exit** | Signals the state machine (or sub-state machine) should terminate/hand control back up — used for clean state-machine-to-state-machine flow. |
| **Any State** | A pseudo-state whose outgoing transitions can fire from *any* currently active state, without needing a direct transition drawn from each one — useful for global interrupts (e.g. a "Hit" or "Death" transition reachable from every state). |
| **Default state** | Shown in a distinct color (typically orange/brown); the state entered automatically when the layer/state machine activates. Set via right-click → **Set As Default**. |

## Animation State — Inspector fields

| Field | Description |
|---|---|
| `Motion` | The `AnimationClip` or Blend Tree this state plays. |
| `Speed` | Playback speed multiplier; can be driven by a parameter (`Speed Multiplier` toggle + parameter picker). |
| `Motion Time` | Optional parameter-driven override of normalized playback time. |
| `Mirror` | Humanoid-only; mirrors the animation left/right; can be parameter-driven. |
| `Cycle Offset` | Offset added to the state's start time within the motion. |
| `Foot IK` | Humanoid-only; whether the state respects foot IK. |
| `Write Defaults` | Whether unanimated properties reset to their default values on this state, or are left as whatever the previous state left them. |
| `Transitions` | List of outgoing transitions from this state. |
| `Solo` / `Mute` | Preview-only toggles (see Solo/Mute below); don't affect a shipped build's logic. |

## Transitions — Inspector fields

| Field | Description |
|---|---|
| `Has Exit Time` | If enabled, the transition can fire based on the source state's normalized playback time alone (no parameter needed). |
| `Exit Time` | Normalized-time threshold at which the exit-time condition becomes true, e.g. `0.75` = true on the first frame where 75% of the animation has played. |
| `Fixed Duration` | Whether `Transition Duration`/`Exit Time` are interpreted in seconds (checked) or as a normalized fraction of the state's length (unchecked). |
| `Transition Duration` | Length of the crossfade blend, in seconds or normalized time per `Fixed Duration`. |
| `Transition Offset` | Normalized start time within the destination state, e.g. `0.5` starts the destination state playing from 50% in. |
| `Interruption Source` | Which other transitions may interrupt this one mid-blend: `None`, `Current State`, `Next State`, `Current State then Next State`, `Next State then Current State`. |
| `Ordered Interruption` | Whether interruption eligibility respects the transition's ordering, independent of `Interruption Source`. |
| `Conditions` | List of `(Parameter, Comparator, Value)` triples that must all be true (for Float/Int: `Greater`/`Less`/`Equals`/`NotEqual`; for Bool: `true`/`false`; Trigger: just presence) for the transition to fire. |

**State Machine Transitions** (Entry/Exit-node transitions) sit at a higher abstraction level than regular state-to-state transitions: every state machine has a default Entry→default-state transition, and you can add more Entry transitions with conditions to make the state machine start in different states depending on parameter values at entry time. Transitions can mix freely — state-to-state, state-to-state-machine, and state-machine-to-state-machine.

## Parameters
Four types, created/edited in the Animator window's **Parameters** panel:

| Type | Description |
|---|---|
| `Float` | Fractional value; set via `Animator.SetFloat`. |
| `Int` | Whole number; set via `Animator.SetInteger`. |
| `Bool` | True/false; set via `Animator.SetBool`. |
| `Trigger` | One-shot bool that auto-resets after being consumed by a transition; set via `Animator.SetTrigger`, manually cleared via `Animator.ResetTrigger`. |

Communication is bidirectional: scripts write parameters to drive the state machine (locomotion speed, action triggers), and animation curves baked into a clip can also write back to a parameter for script consumption (e.g. driving audio pitch from a curve — see [mecanim-overview.md](mecanim-overview.md)'s Curves section).

## Blend Trees
A Blend Tree is a `Motion` type that smoothly blends multiple child clips based on parameter value(s), configured via the **Blend Type** dropdown in the Blend Tree Inspector.

| Blend Type | Parameters | Use case | Setup |
|---|---|---|---|
| `1D` | 1 float | Single-axis blend, e.g. walk/run speed. | Each child clip gets a `Threshold` (the parameter value at which it has full weight, 1.0). Enable `Automate Thresholds` to distribute thresholds evenly across the range, or use the `Compute Thresholds` dropdown (e.g. `Speed`) to derive thresholds from each clip's own root-motion speed. |
| `2D Simple Directional` | 2 floats | Distinct-direction motions (forward/back/left/right walk), optionally with one neutral clip at `(0,0)` (e.g. idle). Avoid multiple clips in the same direction. | Each child clip gets `Pos X`/`Pos Y`. |
| `2D Freeform Directional` | 2 floats | Like Simple Directional but allows multiple clips in the same direction (e.g. both "walk forward" and "run forward"). Must include exactly one clip at `(0,0)`. | `Pos X`/`Pos Y` per clip. |
| `2D Freeform Cartesian` | 2 floats | Non-directional parameter pairs, e.g. angular speed × linear speed ("walk forward no turn" vs "run forward turn right"). | `Pos X`/`Pos Y` per clip. |
| `Direct` | 1 float parameter per child, mapped 1:1 | Bypasses the directional/cartesian algorithms entirely — each Animator parameter directly drives one child's blend weight. Used for facial blend-shape mixing, additive layering, or any case needing exact parameter-to-weight control. | Assign one Animator parameter per child motion. |

2D modes offer a `Compute Positions` dropdown to auto-derive `Pos X`/`Pos Y` from a clip's root-motion data (velocity components, speed, or angular speed) instead of hand-entering them.

**Common Blend Tree options** (Inspector, all blend types):
- `Time Scale` per clip (clock icon) — speed-scales an individual child clip.
- `Adjust Time Scale > Homogeneous Speed` — proportionally rescales all child clip speeds together while preserving their relative speed ratios. Only works when all children are plain `AnimationClip`s, not nested Blend Trees.
- `Mirror` — reflects a humanoid clip left/right at no extra memory cost; Unity auto-applies positional offsets to keep foot-contact timing synced across the mirrored/unmirrored pair.

Blend Trees can be nested (a Blend Tree as a child motion of another Blend Tree), navigable via the Animator window's breadcrumb trail.

## Sub-State Machines
Right-click empty graph space → **Create Sub-State Machine** to collapse a group of related states (e.g. a multi-step "Trickshot": crouch → aim → shoot → stand) into a single hexagon-shaped node, keeping the top-level graph readable as more complex actions are added. Double-click to enter/edit; the breadcrumb trail shows current nesting depth. When transitioning *into* a sub-state machine from outside, you must specify which internal state receives the transition. The special `_Up` pseudo-state, used from within a sub-state machine, represents "the enclosing state machine" for transitioning back out to the parent level.

## Layers
Configured in the Animator window's **Layers** panel; each layer has its own state machine, useful for splitting animation by body region (e.g. base full-body locomotion layer + an upper-body action layer stacked above it). Click the cog icon on a layer for settings.

| Setting | Description |
|---|---|
| `Weight` | Blend weight of this layer against layers below it (0–1). Also settable at runtime via `Animator.SetLayerWeight`/read via `GetLayerWeight`. A weight-`0` layer is skipped entirely by Unity — see [performance-and-faq.md](performance-and-faq.md). |
| `Blending` — `Override` | This layer's animation replaces the animation from layers below it (for the affected body parts). |
| `Blending` — `Additive` | This layer's animation is added on top of the animation from layers below it. |
| `Mask` | An `AvatarMask` restricting which body parts this layer's animation affects (see [avatar-setup.md](avatar-setup.md)). Indicated by an "M" icon on the layer row. |
| `Sync` | A synced layer reuses another layer's state machine structure (same states/transitions) but can assign different motions per state. Indicated by an "S" icon; a `Timing` checkbox rescales each synced state's duration based on relative weight across the synced layers. |
| `IK Pass` | Per-layer toggle enabling the `OnAnimatorIK` callback during that layer's evaluation (see [animator-component.md](animator-component.md)). |

## StateMachineBehaviour
`StateMachineBehaviour` is a script type attached to an individual **state** (or sub-state machine) inside the Animator Controller graph — not to a GameObject like a `MonoBehaviour`. Attach via: select a state in the Animator window → Inspector → **Add Behaviour** → pick/create a `StateMachineBehaviour` script.

| Method | Fires |
|---|---|
| `OnStateEnter` | First update frame the state machine evaluates this state. |
| `OnStateUpdate` | Every update frame except the first and last. |
| `OnStateExit` | Last update frame this state is evaluated. |
| `OnStateMove` | During root-motion application for this state. |
| `OnStateIK` | During the Animator's IK pass, for this state. |
| `OnStateMachineEnter` | Entering a sub-state machine. |
| `OnStateMachineExit` | Last update frame when taking a transition out of a (sub-)state machine. |

These fire based on state-machine evaluation context, not GameObject activation — a `StateMachineBehaviour`'s lifecycle is entirely independent of `MonoBehaviour.OnEnable`/`OnDisable`/`OnDestroy`. Common uses: state-scoped audio triggers, conditional per-state checks (e.g. ground detection only while in a jump state), state-scoped VFX activation.

## Solo / Mute (transition preview tool)
Editor-only preview aid on transitions: `Mute` disables a transition, `Solo` plays only that transition (enabling Solo on one automatically mutes others; if both are set, Mute wins). Green arrows in the graph = solo'd; red = muted. Configurable from either the Transition Inspector or the source State's Inspector (which lists all its outgoing transitions). Note: the graph's visual solo/mute state can drift from the underlying engine state in some cases — don't rely on the graph coloring alone to confirm behavior; verify by playing.

## Practical guidance
- Prefer **Any State** transitions only for genuinely global interrupts (hit reactions, death, stun) — overusing Any State for routine flow defeats the readability benefit of an explicit state graph and can create hard-to-trace transition priority bugs, since Any State transitions are evaluated across every active state.
- A growing `switch` on an "action type"/"ability type" enum driving which state to play is exactly the Open/Closed violation flagged in `coding-principles.md` — model it as parameter-driven transitions/sub-state machines instead, or as one `IAbility` implementation per type feeding a shared parameter set.
- Use `Has Exit Time` for transitions that should only occur after a clip naturally finishes (e.g. attack recovery → idle); disable it for anything that should react immediately to a parameter/trigger (e.g. locomotion direction changes, hit reactions).
- Choose `1D` for single-axis blends (speed), `2D Simple Directional` when clips map to distinct compass directions with no overlap, `2D Freeform Directional` when multiple clips share a direction (walk vs. run forward), `2D Freeform Cartesian` when the two parameters aren't spatial directions at all (e.g. turn-rate × speed), and `Direct` when you need exact one-parameter-per-clip control (facial blend shapes) rather than an interpolation algorithm.
- Keep `StateMachineBehaviour` scripts thin/visual (audio cues, VFX triggers, animation-driven flags) — actual gameplay-rule decisions (what a "Hit" state *means* for damage/state, cooldowns, etc.) still belong in `Game.Core.*` per this project's Shared Core integrity rule; a `StateMachineBehaviour` may read from or signal into a Client-layer adapter, but must not itself implement game rules.
- Use **Sync layers** for genuine visual variants of one shared state machine (e.g. different weapon-hold animations reusing the same locomotion graph) rather than duplicating the whole layer — same principle as `AnimatorOverrideController` (see [animator-override-controller.md](animator-override-controller.md)), applied at the layer level instead of clip level.
