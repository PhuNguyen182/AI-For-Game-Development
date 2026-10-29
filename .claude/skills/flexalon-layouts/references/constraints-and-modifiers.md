# Constraints and Modifiers

Pages: `/docs/constraints`, `/docs/randomModifier`, API `FlexalonConstraint`, `Constraint`, `FlexalonModifier`, `FlexalonRandomModifier`.

## `FlexalonConstraint`
Runs in the Constrain stage; places an object relative to a target in any hierarchy.

| Property | Decides |
|---|---|
| `Target` (`GameObject`) | Settable at runtime (e.g. on click). Rotation is set to match the target's |
| `HorizontalAlign`/`VerticalAlign`/`DepthAlign` | Point on the target's box |
| `HorizontalPivot`/`VerticalPivot`/`DepthPivot` | Point on this object's box |

The align/pivot pair is the whole mechanism: the two points are made to coincide. Center/Center centres one on the other; target `End` with self `Start` stacks this object after the target.

Constraining redefines available space as the target's size, not the transform parent's. A `Fill` axis takes a fraction of the target (docs example: a circle layout at 120% of the clicked target's width). Set size types with the target in mind.

Use a constraint when the target is outside the parent chain, changes at runtime, forms a follow chain (one per link plus a Lerp animator), or when a layout itself must be sized by another object. Retarget from code with `Target = x; MarkDirty()`. A constrained object tracking a moving target needs a Lerp animator; a Curve animator restarts on every change and never completes ([animators.md](animators.md)).

Custom constraint: implement `Constraint.Constrain(FlexalonNode)`; assign with `FlexalonNode.SetConstraint(Constraint, FlexalonNode)`.

## `FlexalonModifier`
`PostArrange(FlexalonNode)` runs after children are arranged and adjusts computed results. It can move and rotate only; it cannot affect measurement or space distribution (that belongs in a layout, [custom-layouts.md](custom-layouts.md)). Registered with `FlexalonNode.AddModifier`/`RemoveModifier`; read `FlexalonNode.Modifiers`.

## `FlexalonRandomModifier`
Add to any layout to perturb its result. Position and rotation only (no size): `RandomSeed`, `RandomizePositionX/Y/Z` with `PositionMin`/`PositionMax`, `RandomizeRotationX/Y/Z` with `RotationMin*`/`RotationMax*`. Use it when the base order still matters; `FlexalonRandomLayout` when it does not.
