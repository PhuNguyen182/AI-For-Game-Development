# Odin Serialization

Odin has its own serializer. Use it per field type, not as a replacement for `[SerializeField]`.

## What Unity cannot serialize
| Case | Without Odin |
|---|---|
| `Dictionary<TKey, TValue>` | Shows empty/unserialized |
| `interface`-typed field | Reference lost on reload |
| Polymorphic reference (base field, derived instance) | Only base fields survive |
| `T[,]` (e.g. `[TableMatrix]`, see [attributes-collections-tables.md](attributes-collections-tables.md)) | Not serialized |
| `null` for many reference types | Cannot be represented |

## Opting in
| Approach | Use when |
|---|---|
| Inherit `SerializedMonoBehaviour` | Component has fields needing Odin |
| Inherit `SerializedScriptableObject` | Same, for an asset |
| `[OdinSerialize]` on the member (`Sirenix.Serialization`) | Marks one member for Odin inside a type Odin already serializes (a `Serialized*` base, or `ISerializationCallbackReceiver` wired to Odin's serialization utility). On a plain `MonoBehaviour`/`ScriptableObject` it does nothing: the member silently does not persist |

Both bases implement `ISerializationCallbackReceiver`; overriding the `protected virtual OnBeforeSerialize()`/`OnAfterDeserialize()` must call `base`, which drives Odin's pass.

```csharp
public class AbilityRegistry : SerializedMonoBehaviour
{
    public Dictionary<string, IAbility> abilitiesByName;       // Odin serializes these
    [OdinSerialize] private IAbility fallback;                 // effective only because the base is Odin-serialized
}
```

Formatters, `AnySerializer`, `BinaryDataReader/Writer` in `Sirenix.Serialization` are for custom formats or persistence layers: escalate to `technical-architect`/`sdk-platform-engineer`.

Switching an existing type to `SerializedMonoBehaviour`/`SerializedScriptableObject` changes its serialized format, and existing scene/prefab/asset data is not migrated. Treat it as a breaking change, flag it in the Implementation Note (`csharp-standards` -> `coding-principles.md`, Handoff), and migrate existing assets deliberately. `[OdinSerialize]` on a plain Unity type is not a cheaper alternative (see Opting in).
