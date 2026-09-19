# Delegate Objects & Pluggable Behavior — Strategy via ScriptableObject

Sources: [ScriptableObject](https://docs.unity3d.com/Manual/class-ScriptableObject.html), [CreateAssetMenuAttribute](https://docs.unity3d.com/ScriptReference/CreateAssetMenuAttribute.html). Pattern synthesized from Ryan Hipple's "Delegate/Strategy" ScriptableObject technique (Unite Austin 2017) and the classic Strategy design pattern.
Covers: SKILL.md §4 — **"Use a Delegate Object SO for pluggable/strategy behavior swapped without new code"**.

An abstract SO with one behavior-defining method, implemented by several
concrete SO subclasses, lets a MonoBehaviour or a caller swap the algorithm by
swapping which asset is assigned in the Inspector — no code edit, no growing
`switch` on a "behavior type" enum. This is the Strategy pattern expressed as
an asset instead of a `new`-ed class, which is what makes it
Inspector-configurable per prefab without a programmer.

## Shape

| Member | Effect | Use when | Source |
|---|---|---|---|
| `abstract class AbilityTargetingSO : ScriptableObject` with `public abstract IReadOnlyList<Vector3> GetTargetPoints(...)` | Declares the contract every strategy implements | A behavior varies by design-time choice, not by a runtime condition a single method could branch on | synthesized |
| Concrete subclasses (`ConeTargetingSO`, `SingleTargetTargetingSO`) | Each ships one algorithm as its own asset | Adding a new variant should never touch existing callers, per `coding-principles.md`'s Open/Closed section | synthesized |
| `[SerializeField] private AbilityTargetingSO targeting;` on the consuming prefab | The swap point — reassign the asset reference, nothing else | A designer must be able to change behavior without a programmer | synthesized |

## Code shape

```csharp
public abstract class AbilityTargetingSO : ScriptableObject
{
    public abstract IReadOnlyList<Vector3> GetTargetPoints(Vector3 origin, Vector3 direction);
}

[CreateAssetMenu(menuName = "Abilities/Targeting/Cone", fileName = "SO_ConeTargeting")]
public class ConeTargetingSO : AbilityTargetingSO
{
    [SerializeField] private float coneAngle = 45f;
    [SerializeField] private int rayCount = 5;

    public override IReadOnlyList<Vector3> GetTargetPoints(Vector3 origin, Vector3 direction)
    {
        // Fan `rayCount` points across `coneAngle` around `direction`, returning candidate points only.
        return this.BuildConePoints(origin, direction, this.coneAngle, this.rayCount);
    }
}
```

## When to reach for this over an Extendable Enum

| Concern | Delegate Object | Extendable Enum | Source |
|---|---|---|---|
| What varies | Behavior/algorithm (what happens) | Identity/category (which kind is this) | synthesized |
| Typical member | An abstract method every subclass implements | An `Id`/data field only | synthesized |
| Combine them | A [extendable-enums.md](extendable-enums.md) category SO can hold a Delegate Object reference for "what this category does" | | synthesized |

**Critical caveat**: `GetTargetPoints` may resolve *which points to check* — a
presentation/spatial concern using `UnityEngine.Vector3` — but the decision of
*what those points mean* (damage dealt, a hit resolved, a cooldown consumed)
stays in `Game.Core.*`; pass the resolved points in as already-computed data,
per `coding-principles.md`'s Shared Core integrity section. A Delegate Object
that also computes damage is reimplementing a rule outside Core, not
delegating to it.
