# Serialization — INetworkSerializable, INetworkSerializeByMemcpy, FastBufferWriter/Reader

Sources: [a] manual/advanced-topics/serialization/serialization-arrays.html, [b] manual/advanced-topics/serialization/inetworkserializebymemcpy.html, [c] api/Unity.Netcode.NetworkBehaviourReference.html, [d] manual/advanced-topics/fastbufferwriter-fastbufferreader.html, [e] api/Unity.Netcode.BytePacker.html, [f] manual/advanced-topics/custom-serialization.html.

Resolution order for an Rpc parameter or `NetworkVariable<T>` payload: `UserNetworkVariableSerialization<T>` → built-in codegen → `INetworkSerializable`. `NetworkVariable<T>` itself (permissions, `NetworkVariableBase` subclasses): [state-sync.md](state-sync.md).

## Built-in

| Type | Handling |
|---|---|
| C# primitives incl. `string` (Rpc params only — a `NetworkVariable` needs `FixedString*`); `Color`, `Color32`, `Vector2/3/4`, `Quaternion`, `Ray`, `Ray2D`; enums | Automatic; an enum is sent as its underlying type (`enum E : byte` → 1 byte) |
| Arrays of the above | Automatic, except `string[]` — excluded for allocation cost [a] |
| `NativeArray<T>`, `NativeList<T>` (`T` unmanaged, not nested) | `serializer.SerializeValue(ref x)`; `NativeList<T>` needs a `Collections` assembly reference and define `UNITY_NETCODE_NATIVE_COLLECTION_SUPPORT` [a] |
| Nested native containers (`NativeArray<NativeList<T>>`) | Unsupported — crashes [a] |
| `List<T>`, `Dictionary<K,V>` | Not built in — wrap in an `INetworkSerializable` or send the backing array |
| `unmanaged` struct of the above | Automatic as an Rpc parameter (codegen, field by field) |
| `GameObject`, `NetworkObject`, `NetworkBehaviour` | Not serializable — use `NetworkObjectReference` / `NetworkBehaviourReference` |
| Anything else | Implement `INetworkSerializable` |

## INetworkSerializable vs INetworkSerializeByMemcpy

| Type shape | Use |
|---|---|
| Reference fields, managed type, or per-field logic (e.g. compressing a `Quaternion`) | `INetworkSerializable` |
| Holds a nested `INetworkSerializable`/collection | `INetworkSerializable`; in the reader branch construct the nested value before `SerializeValue`, or it stays null/default |
| Unmanaged POD only — no pointers, no `NativeArray`/`NativeList` | `INetworkSerializeByMemcpy` — whole-struct memcpy, faster but sends padding bytes |
| External unmanaged type you cannot annotate (`System.Guid`) | `ForceNetworkSerializeByMemcpy<T>` (`T : unmanaged, IEquatable<T>`), implicit conversion to/from `T` |

**Caveat:** `INetworkSerializeByMemcpy` is a marker; NGO does not check memcpy-safety. A pointer, or a `NativeList`/`NativeArray` field, corrupts memory or crashes the receiver [b].

```csharp
struct SpawnPoint : INetworkSerializable
{
    public Vector3 Position;
    public Quaternion Rotation;

    public void NetworkSerialize<T>(BufferSerializer<T> serializer) where T : IReaderWriter
    {
        serializer.SerializeValue(ref Position);
        serializer.SerializeValue(ref Rotation);
    }
}

public struct MyStruct : INetworkSerializeByMemcpy { public int A; public float C; public bool D; }

public NetworkVariable<ForceNetworkSerializeByMemcpy<Guid>> GuidVar;
```

## Object references

| Type | Resolve |
|---|---|
| `NetworkObjectReference` | `bool TryGet(out NetworkObject, NetworkManager = null)`; implicit conversion to/from `NetworkObject`/`GameObject` |
| `NetworkBehaviourReference` | `TryGet(out NetworkBehaviour, ...)` or `TryGet<T>(out T, ...) where T : NetworkBehaviour` |

Both send the `NetworkObjectId` (plus component index for a behaviour).

**Caveat:** ids are recycled, so a stale reference can resolve to the *wrong* object rather than fail [c]; `TryGet` also fails once the target despawns. Re-resolve on each use, never cache across frames, and check the `TryGet` result — the implicit conversion returns `null` on failure.

## FastBufferWriter / FastBufferReader / BufferSerializer

| Member | Fact |
|---|---|
| `FastBufferWriter(int size, Allocator, int maxSize = -1)` | Struct, no GC allocation; dispose it |
| `TryBeginWrite(int bytes)` / `TryBeginRead` | Reserves a range once; returns `false`, never throws |
| `WriteValue<T>` / `ReadValue<T>` | Unchecked; only inside a successful `TryBegin*` range |
| `WriteValueSafe<T>` / `ReadValueSafe<T>` | Bounds-checked; throws `OverflowException` |
| `BufferSerializer<TReaderWriter>` (`ref struct`) | One `SerializeValue` reads or writes per `IsReader`/`IsWriter` |
| `serializer.PreCheck(int)` + `SerializeValuePreChecked<T>` | Skips the per-call bounds check — for large loops |
| `serializer.GetFastBufferReader()` / `GetFastBufferWriter()` | Raw access (e.g. for `BytePacker`); valid only on the matching side |

**Caveat:** the unchecked path (`WriteValue`/`ReadValue`/`WriteBytes`/`ReadBytes`) throws `OverflowException` only in Editor/development builds; in release an overrun is silent memory corruption [d]. Use `*Safe` or a validated `TryBegin*` for untrusted or variable-length data.

```csharp
using var writer = new FastBufferWriter(256, Allocator.Temp);
if (!writer.TryBeginWrite(sizeof(float) + sizeof(bool) + sizeof(int)))
    throw new OverflowException("Not enough space in the buffer");
writer.WriteValue(f);
writer.WriteValue(b);
writer.WriteValue(i);
```

## Packed writes

| Member | Fact |
|---|---|
| `BytePacker.WriteValuePacked` / `ByteUnpacker.ReadValuePacked` | Varint; integral, `float`, `double`, `string`, Unity primitives, unmanaged enums. A large value can cost **more** than `sizeof(T)` — use only when values are typically small [e] |
| `WriteValueBitPacked` / `ReadValueBitPacked` | ZigZag varint, integral only; never exceeds `sizeof(T)` but range shrinks (`int` → 29 data bits + sign) [e] |
| `QuaternionCompressor.CompressQuaternion(ref Quaternion) → uint` / `DecompressQuaternion` | Smallest-three, 16 → 4 bytes |

## Custom serializer for a type you do not own

`FastBufferWriter`/`FastBufferReader` extension methods, for hand-rolled messages:

```csharp
public struct Health { public int CurrentHealth; public uint MaxHealth; }

public static class FastBufferExtensions
{
    public static void WriteValueSafe(this FastBufferWriter writer, in Health health)
    {
        writer.WriteValueSafe(health.MaxHealth);
        writer.WriteValueSafe(health.CurrentHealth);
    }

    public static void ReadValueSafe(this FastBufferReader reader, out Health health)
    {
        reader.ReadValueSafe(out uint max);
        reader.ReadValueSafe(out int current);
        health = new Health { MaxHealth = max, CurrentHealth = current };
    }
}
```

For `NetworkVariable<Health>`, register before any serialization (static constructor or early bootstrap):

```csharp
UserNetworkVariableSerialization<Health>.WriteValue = FastBufferExtensions.WriteValueSafe;
UserNetworkVariableSerialization<Health>.ReadValue = FastBufferExtensions.ReadValueSafe;
UserNetworkVariableSerialization<Health>.DuplicateValue = (in Health value, ref Health duplicatedValue)
    => duplicatedValue = value;
```

**Caveat:** all three delegates are required; a missing one fails at runtime, with no default. `DuplicateValue` snapshots the previous value for dirty-checking, so a shallow copy that aliases a reference field silently breaks change detection [f]. Optional `WriteDelta`/`ReadDelta` must be set together (send only the changed part); omit both to send the full value.

For an `INetworkSerializable` that embeds `Health`, a `BufferSerializer` extension:

```csharp
public static class BufferSerializerExtensions
{
    public static void SerializeValue<TReaderWriter>(
        this BufferSerializer<TReaderWriter> serializer,
        ref Health health) where TReaderWriter : IReaderWriter
    {
        serializer.SerializeValue(ref health.MaxHealth);
        serializer.SerializeValue(ref health.CurrentHealth);
    }
}
```

| Member | Fact |
|---|---|
| `GenerateSerializationForTypeAttribute(Type)` | Forces codegen for a type used only in manual serialization |
| `GenerateSerializationForGenericParameterAttribute` | Same, for a generic `NetworkVariable`-style class's type parameter |
| `NetworkVariableSerialization<T>` | Internal dispatcher (`AreEqual`, `Duplicate`); register against `UserNetworkVariableSerialization<T>`, not this |
