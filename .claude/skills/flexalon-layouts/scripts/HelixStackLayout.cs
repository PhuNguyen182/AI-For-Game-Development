// A custom Flexalon layout: LayoutBase subclass whose Measure sizes Y from the child count and Arrange stacks the children in a rotating helix.
// Adapt into: Assets/_Project/Scripts/<Feature>/Views/HelixStackLayout.cs (Client code)
// Unverified: not compiled or run (no Unity project in this repo).
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
