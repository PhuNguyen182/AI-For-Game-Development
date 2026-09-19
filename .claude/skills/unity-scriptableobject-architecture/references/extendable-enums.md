# Extendable Enums — Open Sets of "Type" via ScriptableObject

Sources: [ScriptableObject](https://docs.unity3d.com/Manual/class-ScriptableObject.html), [CreateAssetMenuAttribute](https://docs.unity3d.com/ScriptReference/CreateAssetMenuAttribute.html). Pattern synthesized from Ryan Hipple's "Extendable Enum" technique (Unite Austin 2017).
Covers: SKILL.md §4 — **"Replace a growing `switch` on a fixed enum with an Extendable Enum once new cases must be added without editing the switch"**.

A C# `enum` is a closed set — adding a case means recompiling every `switch`
over it. An Extendable Enum replaces the enum with a base SO type
(`DamageTypeSO`) and one asset instance per "case"
(`SO_DamageType_Fire.asset`, `SO_DamageType_Physical.asset`); new cases are
new assets, and equality/lookup use a stable identifier field instead of an
integer.

## Shape

| Member | Effect | Use when | Source |
|---|---|---|---|
| `abstract class DamageTypeSO : ScriptableObject` with `[SerializeField] private string id;` | The base "enum" type | A design-time category needs new members added by content, not by a programmer | synthesized |
| One asset per case (`SO_DamageType_Fire.asset`) | Each "value" of the enum | Designers add a new category without touching code, per `coding-principles.md`'s Open/Closed section | synthesized |
| `Dictionary<DamageTypeSO, float>` (e.g. a resistance table) | Lookup keyed by the SO reference instead of an int | A `switch` on the type would otherwise grow one branch per case | synthesized |

## Code shape

```csharp
public abstract class DamageTypeSO : ScriptableObject
{
    [SerializeField] private string id;

    public string Id => this.id;
}

[CreateAssetMenu(menuName = "Combat/Damage Type", fileName = "SO_DamageType")]
public class DamageType : DamageTypeSO
{
}
```

## Extendable Enum vs Delegate Object

| Concern | Extendable Enum | Delegate Object | Source |
|---|---|---|---|
| What varies | Identity/category (which kind is this) | Behavior/algorithm (what happens) | synthesized |
| Typical member | `Id`/data fields only | An abstract method every subclass implements | synthesized |
| Combine them | A `DamageTypeSO` can hold a [delegate-objects-and-pluggable-behavior.md](delegate-objects-and-pluggable-behavior.md) reference for "what this category does" | | synthesized |

**Critical caveat**: Never compare two Extendable Enum assets by
reference-equality (`==`) once the same logical "case" could plausibly be
loaded twice — a duplicated import, or two Addressables bundles both
containing a copy of the same asset. Compare by the stable `Id` string
instead whenever that risk exists; reference-equality is only safe when every
case is guaranteed to load from exactly one asset.
