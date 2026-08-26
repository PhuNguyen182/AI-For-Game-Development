# Custom Layouts — implementing `Measure` and `Arrange` in Layout Space

Sources: [Custom Layout](https://www.flexalon.com/docs/customLayout), [Class LayoutBase](https://www.flexalon.com/docs/api/Flexalon.LayoutBase.html), [Interface Layout](https://www.flexalon.com/docs/api/Flexalon.Layout.html), [Interface FlexalonNode](https://www.flexalon.com/docs/api/Flexalon.FlexalonNode.html).
Covers: SKILL.md §4 — **"Extend Flexalon with a custom layout only when no built-in composition reaches the result"**.

A custom layout implements `Flexalon.Layout` — in practice by extending the
`FlexalonLayoutBase` MonoBehaviour (`LayoutBase` in the API), which handles
child management and edit-mode correctness. Two methods to override:
`Measure` and `Arrange`. This is real ongoing cost; nesting built-in layouts
or adding a `FlexalonModifier` ([constraints-and-modifiers.md](constraints-and-modifiers.md)) covers most
arrangements without it.

- [Layout Space — the four assumptions you may rely on](#layout-space--the-four-assumptions-you-may-rely-on)
- [`Measure(FlexalonNode node, Vector3 size, Vector3 min, Vector3 max)`](#measureflexalonnode-node-vector3-size-vector3-min-vector3-max)
- [`Arrange(FlexalonNode node, Vector3 layoutSize)`](#arrangeflexalonnode-node-vector3-layoutsize)
- [The `FlexalonNode` members a layout needs](#the-flexalonnode-members-a-layout-needs)
- [Guardrails for a custom layout](#guardrails-for-a-custom-layout)

## Layout Space — the four assumptions you may rely on

`Measure` and `Arrange` operate in Layout Space, which is neither Unity world
space nor local space.

| Assumption | Consequence | Source |
|---|---|---|
| The layout node's centre is at `(0, 0, 0)` | Positions are computed around the origin, never around the transform | [Custom Layout](https://www.flexalon.com/docs/customLayout) |
| Each child pivots at the centre of its size | No pivot maths, and no `RectTransform` pivot handling | [Custom Layout](https://www.flexalon.com/docs/customLayout) |
| All sizes are axis aligned | Rotation was already folded into the measured box, per [flexalon-object-sizing.md](flexalon-object-sizing.md) | [Custom Layout](https://www.flexalon.com/docs/customLayout) |
| Margin and padding are handled externally | Never add them yourself — they are applied around your result | [Custom Layout](https://www.flexalon.com/docs/customLayout) |

"Essentially, your task is to measure and arrange a set of simple boxes."

## `Measure(FlexalonNode node, Vector3 size, Vector3 min, Vector3 max)`

Returns the `Bounds` of this layout. Two obligations:

| Obligation | How | Source |
|---|---|---|
| Determine the size of any axis set to `SizeType.Layout` | Read `node.GetSizeType(axis)`; the incoming `size` already carries the axes the object fixed itself | [Custom Layout](https://www.flexalon.com/docs/customLayout) |
| Give every `SizeType.Fill` child its share | Call `child.SetShrinkFillSize(...)` on each child in `node.Children` | [Custom Layout](https://www.flexalon.com/docs/customLayout) |

Read child sizes with `child.GetMeasureSize(...)` and their intent with
`child.GetSizeType(...)`. The returned bounds **must fit within `min` and
`max`**.

**Critical caveat**: `Measure` may be called **several times in a single
layout update** with different sizes, because a `Fill` child can change its
own size once it receives one — the documented case is a text object with
width `Fill` and height `Component` that re-wraps and so changes height.
`Measure` must therefore be **pure and idempotent**: no accumulating state,
no instantiation, no side effects on the scene. `Arrange` is called once.

## `Arrange(FlexalonNode node, Vector3 layoutSize)`

Positions and rotates each child. `layoutSize` is the size `Measure`
produced, possibly adjusted by an adapter.

| Call | Purpose | Source |
|---|---|---|
| `child.GetArrangeSize()` | The child's final size for this pass — **not** `GetMeasureSize` | [Custom Layout](https://www.flexalon.com/docs/customLayout) |
| `child.SetPositionResult(Vector3)` | Write the child's position, in Layout Space | [Custom Layout](https://www.flexalon.com/docs/customLayout) |
| `child.SetRotationResult(Quaternion)` | Write the child's rotation | [Custom Layout](https://www.flexalon.com/docs/customLayout) |

```csharp
using UnityEngine;
using Flexalon;

namespace Game.Client.Layout
{
    // Stacks children along Y, each one rotated a fixed step further than the last.
    public class HelixStackLayout : LayoutBase
    {
        [SerializeField] private float step = 1f;
        [SerializeField] private float degreesPerStep = 15f;

        public override Bounds Measure(FlexalonNode node, Vector3 size, Vector3 min, Vector3 max)
        {
            if (node.GetSizeType(Axis.Y) == SizeType.Layout)
            {
                size.y = Mathf.Max(0f, (node.Children.Count - 1) * this.step);
            }

            size = Vector3.Max(min, Vector3.Min(max, size));
            this.SetChildrenFillShrinkSize(node, size, size);
            return new Bounds(Vector3.zero, size);
        }

        public override void Arrange(FlexalonNode node, Vector3 layoutSize)
        {
            float start = -layoutSize.y * 0.5f;

            for (int i = 0; i < node.Children.Count; i++)
            {
                FlexalonNode child = node.GetChild(i);
                child.SetPositionResult(new Vector3(0f, start + (i * this.step), 0f));
                child.SetRotationResult(Quaternion.Euler(0f, i * this.degreesPerStep, 0f));
            }
        }
    }
}
```

`LayoutBase.SetChildrenFillShrinkSize(node, childSize, layoutSize)` is the
provided helper for the fill/shrink obligation — prefer it over calling
`SetShrinkFillSize` per child, per KISS in `coding-principles.md`. The docs
also ship a `CustomLayout` example under `Samples/Scripts`.

## The `FlexalonNode` members a layout needs

| Member | Use | Source |
|---|---|---|
| `Children` (`IReadOnlyList<FlexalonNode>`) / `GetChild(int)` | The children to measure and arrange. Concrete-typed, so `for`/`foreach` over it does not allocate, per `performance-and-algorithms.md` | [Interface FlexalonNode](https://www.flexalon.com/docs/api/Flexalon.FlexalonNode.html) |
| `GetSizeType(Axis)` / `GetSizeType(int)` | Which axes this layout must compute | [Interface FlexalonNode](https://www.flexalon.com/docs/api/Flexalon.FlexalonNode.html) |
| `GetMeasureSize(int, float)` / `GetMeasureSize(Vector3)` | A child's size during measure | [Interface FlexalonNode](https://www.flexalon.com/docs/api/Flexalon.FlexalonNode.html) |
| `GetArrangeSize()` | A child's size during arrange | [Interface FlexalonNode](https://www.flexalon.com/docs/api/Flexalon.FlexalonNode.html) |
| `GetMinSize(int, float)` / `GetMaxSize(int, float)` | A child's bounds **including margin** | [Interface FlexalonNode](https://www.flexalon.com/docs/api/Flexalon.FlexalonNode.html) |
| `CanShrink(int)` | Whether a child is shrinkable on that axis (not filling, min size set) | [Interface FlexalonNode](https://www.flexalon.com/docs/api/Flexalon.FlexalonNode.html) |
| `SetShrinkFillSize(...)` | Allocate a child's fill/shrink space, per axis or by `Vector3` | [Interface FlexalonNode](https://www.flexalon.com/docs/api/Flexalon.FlexalonNode.html) |
| `SkipLayout`, `Index`, `Parent` | Skip opted-out children; read position in the parent | [Interface FlexalonNode](https://www.flexalon.com/docs/api/Flexalon.FlexalonNode.html) |
| `AddChild`, `InsertChild`, `Detach`, `DetachAllChildren` | Node-tree edits — for a layout that owns its children, not for ordinary arrange work | [Interface FlexalonNode](https://www.flexalon.com/docs/api/Flexalon.FlexalonNode.html) |
| `SetMethod(Layout)` | Assigns a layout method to a node from code, without a `LayoutBase` component | [Interface FlexalonNode](https://www.flexalon.com/docs/api/Flexalon.FlexalonNode.html) |

## Guardrails for a custom layout

| Rule | Reason | Source |
|---|---|---|
| No allocation in `Measure`/`Arrange` | They run inside the per-frame update for every dirty node — treat them as hot paths, per `performance-and-algorithms.md` | synthesized |
| No `Instantiate`/`Destroy`, no scene mutation | `Measure` may run several times per update; side effects would multiply | [Custom Layout](https://www.flexalon.com/docs/customLayout) |
| No `UnityEngine.Random`, no wall-clock time | Layout re-runs constantly; use a seed field the way `FlexalonRandomLayout` does | [Random Layout](https://www.flexalon.com/docs/randomLayout) |
| Keep the arrangement rule in `Game.Client.*` | `LayoutBase` is a MonoBehaviour; a game rule that *decides* the arrangement belongs in `Game.Core.*`, per `coding-principles.md`'s Shared Core integrity section | synthesized |
| Prefer nesting built-ins first | A custom layout is permanent maintenance for a one-off shape — YAGNI in `coding-principles.md` | synthesized |
