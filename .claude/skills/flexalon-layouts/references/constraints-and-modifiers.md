# Constraints and Modifiers — cross-hierarchy positioning and post-arrange perturbation

Sources: [Constraints](https://www.flexalon.com/docs/constraints), [Random Modifier](https://www.flexalon.com/docs/randomModifier), [Class FlexalonConstraint](https://www.flexalon.com/docs/api/Flexalon.FlexalonConstraint.html), [Interface Constraint](https://www.flexalon.com/docs/api/Flexalon.Constraint.html), [Interface FlexalonModifier](https://www.flexalon.com/docs/api/Flexalon.FlexalonModifier.html), [Class FlexalonRandomModifier](https://www.flexalon.com/docs/api/Flexalon.FlexalonRandomModifier.html).
Covers: SKILL.md §4 — **"Reach for Flexalon Constraint only when the relationship crosses hierarchies"**.

Two extension points that sit either side of `Arrange`: a constraint runs in
the pipeline's Constrain stage to place an object relative to a target
anywhere in the scene, and a modifier runs after arrange to alter results a
layout already produced. Both are documented in [core-concepts-and-pipeline.md](core-concepts-and-pipeline.md)'s step table.

## `FlexalonConstraint` — when the target is not the parent

| Property | What it decides | Source |
|---|---|---|
| `Target` (`GameObject`) | The object to constrain to — **any** gameObject, in any hierarchy. Position follows Align/Pivot, rotation is set to match the target's, and the **available space becomes the target's size** | [Constraints](https://www.flexalon.com/docs/constraints) |
| `HorizontalAlign`, `VerticalAlign`, `DepthAlign` (`Align`) | How each axis aligns to the **target's** box | [Class FlexalonConstraint](https://www.flexalon.com/docs/api/Flexalon.FlexalonConstraint.html) |
| `HorizontalPivot`, `VerticalPivot`, `DepthPivot` (`Align`) | How each axis aligns to **this object's** box | [Class FlexalonConstraint](https://www.flexalon.com/docs/api/Flexalon.FlexalonConstraint.html) |
| `Constrain(FlexalonNode)` | The `Constraint` interface method the pipeline calls in its Constrain stage | [Interface Constraint](https://www.flexalon.com/docs/api/Flexalon.Constraint.html) |
| `FlexalonNode.SetConstraint(Constraint, FlexalonNode)` | Assigns a constraint and its target node from code, for a custom `Constraint` implementation | [Interface FlexalonNode](https://www.flexalon.com/docs/api/Flexalon.FlexalonNode.html) |

**The align/pivot pair is the whole mechanism**: align picks the point on the
*target's* box, pivot picks the point on *this* object's box, and the two are
made to coincide. `Align.Center`/`Align.Center` centres one on the other;
`Align.End` on the target with `Align.Start` on self stacks this object
immediately after the target on that axis.

**Critical caveat**: constraining redefines "available space" to the
**target's** size, not the transform parent's. A constrained object whose
axis is `SizeType.Fill` therefore takes a fraction of the *target* — the
docs' worked example sets a circle layout to fill 120% of the target's width
so the ring grows to surround whatever was clicked. Set size types with the
target in mind, per [flexalon-object-sizing.md](flexalon-object-sizing.md).

```csharp
using UnityEngine;
using Flexalon;

namespace Game.Client.Layout
{
    // Retargets a highlight ring to whichever object was selected.
    public class SelectionRing : MonoBehaviour
    {
        [SerializeField] private FlexalonConstraint ring;

        public void Focus(GameObject target)
        {
            this.ring.Target = target;
            this.ring.MarkDirty();
        }
    }
}
```

### Constraint or layout?

| Situation | Use | Why | Source |
|---|---|---|---|
| Objects are children of the thing arranging them | A layout component | That is what a layout is; a constraint would duplicate it | [Core Concepts](https://www.flexalon.com/docs/coreConcepts) |
| The target sits in an unrelated part of the hierarchy | `FlexalonConstraint` | "The two gameObjects don't have to be in the same hierarchy" | [Constraints](https://www.flexalon.com/docs/constraints) |
| The target changes at runtime (selection, focus, attach point) | `FlexalonConstraint` | `Target` is a settable property; the docs' example swaps it on click | [Constraints](https://www.flexalon.com/docs/constraints) |
| A chain where each object follows the one below it | `FlexalonConstraint` per link, plus a Lerp animator | The docs' stacked-blocks example — each block constrains to the one beneath, and the chain propagates | [Animators](https://www.flexalon.com/docs/animators) |
| Two layouts must combine (a ring sized by a mesh, a panel sized by a socket) | `FlexalonConstraint` on the layout itself | Both the constrained object and the target may carry layouts — that composition is the documented reason the component exists | [Constraints](https://www.flexalon.com/docs/constraints) |

A constrained object that must track a continuously moving target needs a
Lerp animator rather than a Curve animator, per [animators.md](animators.md) — a curve restarts
on every result change and would never complete.

## `FlexalonModifier` — altering results after arrange

| Member | Contract | Source |
|---|---|---|
| `PostArrange(FlexalonNode)` | Called after the node's children are arranged; the implementation adjusts the results already computed | [Interface FlexalonModifier](https://www.flexalon.com/docs/api/Flexalon.FlexalonModifier.html) |
| `FlexalonNode.Modifiers` | `IReadOnlyList<FlexalonModifier>` applying to this node | [Interface FlexalonNode](https://www.flexalon.com/docs/api/Flexalon.FlexalonNode.html) |
| `FlexalonNode.AddModifier` / `RemoveModifier` | Registers or removes a modifier from code | [Interface FlexalonNode](https://www.flexalon.com/docs/api/Flexalon.FlexalonNode.html) |

Because a modifier runs *after* arrange, it cannot change sizes or influence
how space was distributed — it only moves and rotates what the layout already
decided. Anything that must affect measurement belongs in a layout, per
[custom-layouts.md](custom-layouts.md).

## `FlexalonRandomModifier`

Add it to **any** layout to perturb that layout's results.

| Property group | Members | Source |
|---|---|---|
| Seed | `RandomSeed` (`int`) — keeps results stable across the repeated recomputes layout performs | [Random Modifier](https://www.flexalon.com/docs/randomModifier) |
| Position | `RandomizePositionX/Y/Z`, `PositionMin`/`PositionMax` (`Vector3`) and the per-axis `PositionMinX`…`PositionMaxZ` | [Class FlexalonRandomModifier](https://www.flexalon.com/docs/api/Flexalon.FlexalonRandomModifier.html) |
| Rotation | `RandomizeRotationX/Y/Z` and the per-axis `RotationMinX`…`RotationMaxZ` | [Class FlexalonRandomModifier](https://www.flexalon.com/docs/api/Flexalon.FlexalonRandomModifier.html) |

It randomizes **position and rotation only** — no size, unlike
`FlexalonRandomLayout`, which randomizes available size as well but replaces
the arrangement entirely. Use the modifier when the base arrangement still
carries meaning (a grid of tiles that should look hand-placed) and the layout
when it does not, per [radial-curve-and-shape-layouts.md](radial-curve-and-shape-layouts.md).
