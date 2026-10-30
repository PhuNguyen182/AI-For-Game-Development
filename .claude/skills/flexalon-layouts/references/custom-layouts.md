# Custom Layouts

Pages: `/docs/customLayout`, API `LayoutBase`, `Layout`, `FlexalonNode`. Sample: `Flexalon/Samples/Scripts` (`CustomLayout`).

Extend `LayoutBase` (a MonoBehaviour that handles child management and edit-mode correctness) and override `Measure` and `Arrange`. This is permanent maintenance; nesting built-ins or a `FlexalonModifier` covers most shapes.

## Layout Space
Neither world nor local space. You may rely on: node centre at `(0,0,0)`; each child pivots at the centre of its size; all sizes axis-aligned (rotation already folded in); margin and padding applied externally (never add them). The task is measuring and arranging simple boxes.

## `Measure(node, size, min, max)` returns `Bounds`
- Compute any axis where `node.GetSizeType(axis) == SizeType.Layout`; incoming `size` already holds the axes the object fixed.
- Give every `Fill` child its share: `child.SetShrinkFillSize(...)`, or the helper `SetChildrenFillShrinkSize(node, childSize, layoutSize)`.
- Result must fit within `min`/`max`.
- May be called several times per update (a `Fill` child can change size, e.g. re-wrapping text), so keep it pure and idempotent: no accumulated state, no `Instantiate`/`Destroy`, no scene mutation.

## `Arrange(node, layoutSize)` (once per update)
- `child.GetArrangeSize()` (not `GetMeasureSize`), then `SetPositionResult(Vector3)` and `SetRotationResult(Quaternion)` in Layout Space.

```csharp
public class HelixStackLayout : LayoutBase
{
    [SerializeField] float step = 1f, degrees = 15f;
    public override Bounds Measure(FlexalonNode node, Vector3 size, Vector3 min, Vector3 max)
    {
        if (node.GetSizeType(Axis.Y) == SizeType.Layout) size.y = Mathf.Max(0f, (node.Children.Count - 1) * step);
        size = Vector3.Max(min, Vector3.Min(max, size));
        SetChildrenFillShrinkSize(node, size, size);
        return new Bounds(Vector3.zero, size);
    }
    public override void Arrange(FlexalonNode node, Vector3 layoutSize)
    {
        for (int i = 0; i < node.Children.Count; i++)
        {
            var c = node.GetChild(i);
            c.SetPositionResult(new Vector3(0f, -layoutSize.y * 0.5f + i * step, 0f));
            c.SetRotationResult(Quaternion.Euler(0f, i * degrees, 0f));
        }
    }
}
```

## `FlexalonNode` members
| Member | Use |
|---|---|
| `Children` (`IReadOnlyList`), `GetChild(i)` | Iterate with `for`; no allocation |
| `GetSizeType(Axis/int)` | Axes to compute |
| `GetMeasureSize`, `GetArrangeSize` | Child size per phase |
| `GetMinSize`, `GetMaxSize` | Child bounds including margin |
| `CanShrink(int)` | Shrinkable on that axis |
| `SetShrinkFillSize` | Allocate fill/shrink space |
| `SkipLayout`, `Index`, `Parent` | Skip opted-out children; position in parent |
| `AddChild`, `InsertChild`, `Detach`, `DetachAllChildren` | Tree edits for a layout that owns its children |
| `SetMethod(Layout)` | Assign a layout from code without a component |

## Rules
- No allocation in `Measure`/`Arrange`: hot path for every dirty node.
- No `UnityEngine.Random` or wall-clock time; use a seed field as `FlexalonRandomLayout` does.
- A game rule that decides the arrangement belongs in a Core assembly; the `LayoutBase` stays in Client code.
