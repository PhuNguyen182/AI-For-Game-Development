# Dual Serialization — Resetting Runtime State on an SO Asset

Sources: [ISerializationCallbackReceiver](https://docs.unity3d.com/ScriptReference/ISerializationCallbackReceiver.html), [Script Serialization](https://docs.unity3d.com/Manual/script-Serialization.html), [Domain Reloading](https://docs.unity3d.com/Manual/DomainReloading.html). Pattern synthesized from the common ScriptableObject "reset on domain reload" technique used across Variable/Runtime Set implementations.
Covers: SKILL.md §4 — **"Apply Dual Serialization to every SO asset carrying runtime-mutable state"**.

A ScriptableObject asset is one shared instance living for the whole Editor
session — mutating its serialized field at runtime (a Runtime Set's list, a
Variable's current value) changes the asset in memory, and with Domain
Reloading disabled (an Enter Play Mode Option), that mutated value survives
past Stop into the next Play session instead of resetting. Dual Serialization
keeps two fields — a serialized default and a runtime-only working value —
and resets the working value from the default via
`ISerializationCallbackReceiver.OnAfterDeserialize`, which Unity calls on
every domain reload and on entering Play Mode.

## Shape

| Member | Effect | Use when | Source |
|---|---|---|---|
| `[SerializeField] private float initialValue;` | The designer-authored default, saved to the asset | Every mutable SO field this pattern applies to | [Script Serialization](https://docs.unity3d.com/Manual/script-Serialization.html) |
| `private float runtimeValue;` (not the serialized field) | The actual value read/written during Play | Consumers read/write only this one | synthesized |
| `void OnAfterDeserialize()` | Copies `initialValue` into `runtimeValue` | Called by Unity on every domain reload and on entering Play Mode — the reset hook | [ISerializationCallbackReceiver](https://docs.unity3d.com/ScriptReference/ISerializationCallbackReceiver.html) |
| `void OnBeforeSerialize()` | Left as a deliberate no-op here | The runtime value must never write back into `initialValue`, unless a design intentionally wants Play Mode edits to persist — a rare, explicit choice | [ISerializationCallbackReceiver](https://docs.unity3d.com/ScriptReference/ISerializationCallbackReceiver.html) |

## Code shape

```csharp
[CreateAssetMenu(menuName = "Data/Float Variable", fileName = "SO_FloatVariable")]
public class FloatVariable : ScriptableObject, ISerializationCallbackReceiver
{
    [SerializeField] private float initialValue;

    private float runtimeValue;

    public float Value
    {
        get => this.runtimeValue;
        set => this.runtimeValue = value;
    }

    public void OnAfterDeserialize()
    {
        this.runtimeValue = this.initialValue;
    }

    public void OnBeforeSerialize()
    {
        // Deliberately empty: a Play Mode mutation must never write back into the saved asset.
    }
}
```

## When this is mandatory vs skippable

| Asset carries | Dual serialization needed | Why | Source |
|---|---|---|---|
| A Variable SO's current value | Yes | Every reader elsewhere shares the same asset instance; without the reset, one Play session's value bleeds into the next | synthesized |
| A Runtime Set's `List<T>` | Yes | Left populated across a domain-reload-disabled Play boundary, it reports instances that no longer exist | synthesized |
| A Delegate Object's pure strategy method, no field mutated at runtime | No | Nothing about it changes at runtime — there is no working value to reset | synthesized |
| A pure Data Container, never written at runtime | No | Read-only for its whole lifetime | synthesized |

**Critical caveat**: This pattern only protects against the in-memory asset
instance carrying stale state between Play sessions inside one Editor run —
it does not, by itself, prevent `OnBeforeSerialize` from ever accidentally
writing the runtime value back if that method is filled in later. Keep
`OnBeforeSerialize` empty (or state explicitly why it isn't) for every field
this pattern governs.
