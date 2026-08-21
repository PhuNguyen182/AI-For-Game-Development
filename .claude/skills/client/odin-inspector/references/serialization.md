# Odin Serialization — SerializedMonoBehaviour, SerializedScriptableObject, [OdinSerialize]

Sources: [SerializedMonoBehaviour](https://odininspector.com/documentation/sirenix.odininspector.serializedmonobehaviour), [SerializedScriptableObject](https://odininspector.com/documentation/sirenix.odininspector.serializedscriptableobject), [OdinSerializeAttribute](https://odininspector.com/documentation/sirenix.serialization.odinserializeattribute), [Sirenix.Serialization namespace](https://odininspector.com/documentation/sirenix.serialization).
Covers: SKILL.md §4 — **"When the field's type can't survive Unity's own serializer"**.

Odin ships its own serializer, independent of Unity's. Use it only when a
specific field's *type* genuinely needs it — it is not a blanket replacement
for `[SerializeField]`, and switching a type to it is not free (see the
critical caveat below).

## Table of contents
- [When Unity's serializer is insufficient](#when-unitys-serializer-is-insufficient)
- [Opting a type in](#opting-a-type-in)
- [Base classes](#base-classes)
- [What the serializer covers](#what-the-serializer-covers)

## When Unity's serializer is insufficient

Unity's built-in serializer cannot represent, among others:

| Case | Symptom without Odin serialization |
|---|---|
| `Dictionary<TKey, TValue>` | Field silently shows as empty/unserialized in the Inspector |
| An `interface`-typed field | Not serialized; reference is lost on reload |
| Polymorphic reference fields (a base-class field holding a derived instance) | Only the base type's own fields survive; derived fields are lost |
| Multi-dimensional arrays (`T[,]`, as used by `[TableMatrix]` in [attributes-collections-tables.md](attributes-collections-tables.md)) | Not serialized by Unity at all |
| `null` reference-type values in general contexts | Unity's serializer cannot represent `null` for many types; Odin's can |

## Opting a type in

| Approach | When to use | Source |
|---|---|---|
| Inherit `SerializedMonoBehaviour` instead of `MonoBehaviour` | The whole component has one or more fields needing Odin serialization | [SerializedMonoBehaviour](https://odininspector.com/documentation/sirenix.odininspector.serializedmonobehaviour) |
| Inherit `SerializedScriptableObject` instead of `ScriptableObject` | Same, for a ScriptableObject asset | [SerializedScriptableObject](https://odininspector.com/documentation/sirenix.odininspector.serializedscriptableobject) |
| Mark just the member `[OdinSerialize]` (from `Sirenix.Serialization`) | The containing type already serializes fine with Unity, and only one or two members need Odin's serializer — avoids opting the whole type in | [OdinSerializeAttribute](https://odininspector.com/documentation/sirenix.serialization.odinserializeattribute) |

Both base classes implement `ISerializationCallbackReceiver` and expose
`protected virtual OnBeforeSerialize()` / `OnAfterDeserialize()` hooks if a
derived type needs to react to (de)serialization — call the base
implementation when overriding, since that is what drives Odin's actual
serialize/deserialize pass.

## Base classes

```csharp
// The whole component needs Odin serialization (e.g. a polymorphic list).
public class AbilityRegistry : SerializedMonoBehaviour
{
    // Interfaces and Dictionary<K,V> now serialize correctly.
    [SerializeField] private Dictionary<string, IAbility> abilitiesByName;
}

// Only one field needs it; the rest of the type stays on Unity's serializer.
public class EnemyConfig : ScriptableObject
{
    public string enemyName;          // Unity serializes this fine.

    [OdinSerialize]
    private IEnemyBehaviorStrategy strategy;   // Interface — needs Odin.
}
```

## What the serializer covers

The `Sirenix.Serialization` namespace itself (formatters, `AnySerializer`,
`BinaryDataReader`/`Writer`, per-type formatters like `DictionaryFormatter`,
`ArrayFormatter<T>`) is internal machinery — reach for it directly only when
building a custom serialization format or a completely custom persistence
layer, which is `tech-lead-csharp-unity`/`tech-lead-sdk-platform` escalation
territory, not routine Inspector work.

**Critical caveat**: switching an existing type to `SerializedMonoBehaviour`/
`SerializedScriptableObject` changes its underlying serialized data format.
Existing scene/prefab/asset data serialized under Unity's own format is not
automatically migrated — treat this as a breaking change to existing assets
of that type, flag it in the Implementation Note per `coding-principles.md`'s
Handoff section, and prefer the narrower `[OdinSerialize]`-on-one-member
approach when the rest of the type does not need it.
