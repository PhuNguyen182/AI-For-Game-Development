# Selectable Animation Integration

Source: [Animation Integration](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/UIAnimationIntegration.html).
Covers: SKILL.md §4 — "Wire the Animation transition through an Animator Controller, never the legacy animation system".

## The Animation transition mode

`Selectable.Transition` (per
[interaction-components.md](interaction-components.md)) has four modes;
**Animation** is the most capable — it drives an `Animator` through state
changes instead of a plain color/sprite swap.

**Setup requires an `Animator` component on the same GameObject.** Unity's
"Auto Generate Animation" button in the Inspector creates both the
`Animator` and a pre-populated `Animator Controller` asset, which then must
be saved to the project before it takes effect.

### The four states

The generated controller exposes four Animation Clip slots, each
corresponding to a `Selectable` state:

| State | When it plays | Typical content |
|---|---|---|
| Normal | Default/idle | Usually left empty — the element's own Inspector-set values already represent this state |
| Highlighted | Pointer/keyboard focus enters | A single keyframe at the start of the timeline changing whatever properties should visually differ |
| Pressed | Actively pressed/clicked | Same one-keyframe pattern |
| Disabled | `Interactable` is false | Same one-keyframe pattern |

Any number of properties can be set within that single keyframe — color,
scale, a child element's active state, etc. Edit clips through
**Window > Animation**: select Record, change the relevant Inspector
values, then exit Record mode.

**Hard constraint: the Animation transition mode is not compatible with
Unity's legacy Animation system** — it requires the `Animator` component
specifically, never a legacy `Animation` component. Do not attempt to
reuse an existing legacy-animation-driven UI element's clips directly here
without re-targeting them onto an `Animator Controller`.

Reach for Animation mode only when Color Tint or Sprite Swap genuinely
can't express the needed feedback (e.g. a multi-property or staged
transition) — per KISS in `coding-principles.md`, the simpler transition
modes cover the large majority of buttons/toggles without the overhead of
an `Animator Controller` asset per interactive element.
