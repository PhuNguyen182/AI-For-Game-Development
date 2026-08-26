# Data Containers & Variable SOs — Shared Constants Without Duplication

Sources: [ScriptableObject](https://docs.unity3d.com/Manual/class-ScriptableObject.html), [CreateAssetMenuAttribute](https://docs.unity3d.com/ScriptReference/CreateAssetMenuAttribute.html). Pattern synthesized from the "Data" and "Reference/Variable" building blocks of Ryan Hipple's ScriptableObject architecture (Unite Austin 2017).
Covers: SKILL.md §4 — **"Use a Data Container/Variable SO to remove duplicated constants across prefabs or scenes"**.

The simplest ScriptableObject use: one asset holds a value (or a related group
of values) that would otherwise be copy-pasted across many prefabs or
`[SerializeField]` fields, edited once instead of N times. Three shapes cover
almost every case.

## Shape

| Shape | Structure | Use when | Source |
|---|---|---|---|
| Data Container SO | One `[CreateAssetMenu]` asset holding several related read-only config fields (e.g. `SO_EnemyStats` with `maxHealth`, `moveSpeed`) | Several related constants belong to one concept and are shared by many prefabs of the same kind | [ScriptableObject](https://docs.unity3d.com/Manual/class-ScriptableObject.html) |
| Variable SO | A single-value asset wrapping one primitive (`FloatVariable`, `IntVariable`, `BoolVariable`) exposing a `Value` property | One named quantity (master volume, current difficulty multiplier) must be read or written from many unrelated scripts without a static field or singleton | [ScriptableObject](https://docs.unity3d.com/Manual/class-ScriptableObject.html) |
| Reference wrapper struct | A `[Serializable]` struct (`FloatReference`) holding a `useConstant` bool, a local `constantValue`, and a `Variable` SO reference, plus an implicit `operator float` | A field should let a designer pick, per-instance, between "use this shared Variable" and "use this one-off local value" | synthesized |

## Code shape

```csharp
[CreateAssetMenu(menuName = "Data/Float Variable", fileName = "SO_FloatVariable")]
public class FloatVariable : ScriptableObject
{
    [SerializeField] private float value;

    public float Value
    {
        get => this.value;
        set => this.value = value;
    }
}

[Serializable]
public struct FloatReference
{
    [SerializeField] private bool useConstant;
    [SerializeField] private float constantValue;
    [SerializeField] private FloatVariable variable;

    public float Value => this.useConstant ? this.constantValue : this.variable.Value;

    public static implicit operator float(FloatReference reference)
    {
        return reference.Value;
    }
}
```

The implicit conversion lets a consumer read `this.moveSpeedReference` anywhere
a `float` is expected, so the "shared asset or local override" choice never
leaks past the declaration site.

## Data Container vs Variable

| Concern | Data Container | Variable | Source |
|---|---|---|---|
| Shape | Several fields, one concept | One named primitive | synthesized |
| Typical mutability | Read-only for its whole lifetime | Read at design time, often written at runtime | synthesized |
| Runtime write discipline | None needed — never mutated | Needs [dual-serialization.md](dual-serialization.md) if written at runtime | synthesized |

**Critical caveat**: A Variable SO's `Value` is one shared asset field, not
per-instance state — writing to it from one object changes what every other
reference reads next. Use it only for values genuinely global to the system
(settings, a shared multiplier); never for per-instance runtime state like one
enemy's current health, which belongs on that enemy's own component or in
`Game.Core.*`. Any runtime write to a Variable SO must be paired with
[dual-serialization.md](dual-serialization.md) so the mutated value does not
leak into the serialized asset between Play sessions.
