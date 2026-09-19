# Serialization — INetworkSerializable, INetworkSerializeByMemcpy, FastBufferWriter/Reader

Sources: [Serialization](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/serialization.html), [Serialization overview](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/advanced-topics/serialization/serialization-overview.html), [C# primitives](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/advanced-topics/serialization/cprimitives.html), [Unity primitives](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/advanced-topics/serialization/unity-primitives.html), [Enum types](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/advanced-topics/serialization/enum-types.html), [Arrays and collections](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/advanced-topics/serialization/serialization-arrays.html), [INetworkSerializable](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/advanced-topics/serialization/inetworkserializable.html), [INetworkSerializeByMemcpy](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/advanced-topics/serialization/inetworkserializebymemcpy.html), [NetworkObject serialization](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/advanced-topics/serialization/networkobject-serialization.html), [FastBufferWriter/FastBufferReader](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/advanced-topics/fastbufferwriter-fastbufferreader.html), [BufferSerializer](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/advanced-topics/bufferserializer.html), [Custom serialization](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/advanced-topics/custom-serialization.html), plus the `Unity.Netcode` API pages for `INetworkSerializable`, `INetworkSerializeByMemcpy`, `ForceNetworkSerializeByMemcpy<T>`, `FastBufferWriter`, `FastBufferReader`, `BufferSerializer<T>`, `IReaderWriter`, `BytePacker`, `ByteUnpacker`, `NetworkVariableSerialization<T>`, `UserNetworkVariableSerialization<T>`, `NetworkObjectReference`, `NetworkBehaviourReference`, `GenerateSerializationForTypeAttribute`, `QuaternionCompressor`, and the `DocumentationCodeSamples.Health`/`FastBufferExtensions`/`BufferSerializerExtensions` samples.

Covers: SKILL.md §4 — **"Serialize custom types with INetworkSerializable or INetworkSerializeByMemcpy by actual layout"**.

NGO resolves serialization for any RPC parameter or `NetworkVariable<T>` payload in a fixed order: a registered custom serializer (`UserNetworkVariableSerialization<T>`) first, then built-in codegen for C# primitives/Unity primitives/enums/arrays/`unmanaged` structs of those, then an `INetworkSerializable` implementation. `FastBufferWriter`/`FastBufferReader` are the actual byte-level read/write structs underneath all of this; `BufferSerializer<T>` is a bi-directional wrapper over them so one method body can both read and write.

## Built-in serialization

| Type category | Handling | Source |
|---|---|---|
| C# primitives — `bool`, `char`, `sbyte`, `byte`, `short`, `ushort`, `int`, `uint`, `long`, `ulong`, `float`, `double`, `string` | Automatic, built-in codegen | [C# primitives](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/advanced-topics/serialization/cprimitives.html) |
| Unity primitives — `Color`, `Color32`, `Vector2`, `Vector3`, `Vector4`, `Quaternion`, `Ray`, `Ray2D` | Automatic, built-in codegen | [Unity primitives](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/advanced-topics/serialization/unity-primitives.html) |
| Enums (any underlying integer type, e.g. `enum SmallEnum : byte`) | Automatic — serialized as the enum's underlying integer type | [Enum types](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/advanced-topics/serialization/enum-types.html) |
| Arrays of C# value-type primitives (`int[]`) and Unity primitive types | Automatic | [Arrays](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/advanced-topics/serialization/serialization-arrays.html) |
| `string[]` | **Not** built in (excluded for performance — a string array allocates once per element plus one more) | [Arrays](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/advanced-topics/serialization/serialization-arrays.html) |
| `NativeArray<T>`, `NativeList<T>` (non-nested, `T` unmanaged) | Automatic via `serializer.SerializeValue(ref array)` / `ref list`. `NativeList<T>` needs the assembly to reference `Collections` and `UNITY_NETCODE_NATIVE_COLLECTION_SUPPORT` in Scripting Define Symbols | [Arrays](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/advanced-topics/serialization/serialization-arrays.html) |
| Nested native containers — `NativeArray<NativeList<T>>`, `NativeList<NativeArray<T>>`, etc. | **Unsupported — crashes.** Never nest native collections for network serialization | [Arrays](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/advanced-topics/serialization/serialization-arrays.html) |
| C# generic collections (`List<T>`, `Dictionary<K,V>`, …) | No built-in serialization code — wrap in a container implementing `INetworkSerializable`, or serialize the backing array | [Arrays](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/advanced-topics/serialization/serialization-arrays.html) |
| Any `unmanaged` struct composed only of the above (bool/byte/int/float/enum fields) | Automatic as an RPC parameter — the `unmanaged` generic constraint alone is enough for codegen to serialize it field-by-field | [Serialization overview](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/advanced-topics/serialization/serialization-overview.html) |
| `GameObject`, `NetworkObject`, `NetworkBehaviour` | **Not serializable directly** — wrap in `NetworkObjectReference` / `NetworkBehaviourReference` (see below) | [NetworkObject serialization](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/advanced-topics/serialization/networkobject-serialization.html) |
| Anything else (managed reference types, structs with fields not covered above) | Implement `INetworkSerializable` explicitly | [INetworkSerializable](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/advanced-topics/serialization/inetworkserializable.html) |

```csharp
enum SmallEnum : byte { A, B, C }
enum NormalEnum { X, Y, Z } // default underlying type -> int

[Rpc(SendTo.Server)]
void ConfigServerRpc(SmallEnum smallEnum, NormalEnum normalEnum) { /* ... */ }
```

## Choosing INetworkSerializable vs INetworkSerializeByMemcpy

| Type shape | Interface | Why | Source |
|---|---|---|---|
| Struct with reference fields, or a managed type, or fields needing per-field logic (e.g. compressing a `Quaternion`) | `INetworkSerializable` | Field-by-field control; works with managed types too, though managed types cost more | [INetworkSerializable](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/advanced-topics/serialization/inetworkserializable.html) |
| Struct containing a nested `INetworkSerializable`/collection that must be initialized before reading | `INetworkSerializable`, with the reader branch manually constructing the nested value before `SerializeValue` | Avoids leaving a `null`/default nested value after deserialization | [INetworkSerializable](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/advanced-topics/serialization/inetworkserializable.html) |
| Pure unmanaged POD struct (only primitive/blittable value fields, no pointers, no `NativeArray<T>`/`NativeList<T>`) | `INetworkSerializeByMemcpy` | Whole-struct `memcpy` — faster than per-field serialization, at the cost of sending struct padding bytes (less bandwidth-efficient) | [INetworkSerializeByMemcpy](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/advanced-topics/serialization/inetworkserializebymemcpy.html) |
| An external unmanaged type you can't add an interface to (e.g. `System.Guid`) | Wrap in `ForceNetworkSerializeByMemcpy<T>` (`T : unmanaged, IEquatable<T>`) | Adds `INetworkSerializeByMemcpy` support without modifying the original type; has implicit conversions to/from `T` | [ForceNetworkSerializeByMemcpy API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.ForceNetworkSerializeByMemcpy-1.html) |

**Critical caveat**: `INetworkSerializeByMemcpy` is only a marker interface — NGO does not verify the struct is actually memcpy-safe. A struct containing a pointer, or a type that wraps one (`NativeList<T>`, `NativeArray<T>`), will "likely cause memory corruption or crashes on the receiving side" if marked this way; such types must use `INetworkSerializable` or a `FastBufferReader`/`FastBufferWriter` extension method instead.

```csharp
// INetworkSerializable — field-by-field, works for managed or unmanaged types.
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
```

```csharp
// INetworkSerializeByMemcpy — whole-struct memcpy, unmanaged POD fields only.
public struct MyStruct : INetworkSerializeByMemcpy
{
    public int A;
    public int B;
    public float C;
    public bool D;
}

// Wrapping an external unmanaged type (Guid) you can't annotate directly.
public NetworkVariable<ForceNetworkSerializeByMemcpy<Guid>> GuidVar;
```

## Object references — NetworkObjectReference / NetworkBehaviourReference

`GameObject`/`NetworkObject`/`NetworkBehaviour` cannot be serialized directly, so RPCs/`NetworkVariable`s that need to point at a networked object use these `INetworkSerializable` wrapper structs instead. Both serialize the target's `NetworkObjectId` (plus, for behaviours, the component index) and resolve it back to the live instance on the receiving side.

| Type | Resolution API | Source |
|---|---|---|
| `NetworkObjectReference` | `bool TryGet(out NetworkObject, NetworkManager = null)`; implicit conversions to/from `NetworkObject`/`GameObject` | [NetworkObjectReference API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkObjectReference.html) |
| `NetworkBehaviourReference` | `bool TryGet(out NetworkBehaviour, NetworkManager = null)` and a generic `TryGet<T>(out T, ...) where T : NetworkBehaviour` | [NetworkBehaviourReference API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkBehaviourReference.html) |

```csharp
if (target.TryGet(out NetworkObject targetObject))
{
    // Resolved successfully — safe to use targetObject this frame.
}
else
{
    // Not found: despawned, not yet spawned, or the id was recycled.
}
```

**Critical caveat**: `TryGet` can return `false` even for a reference that resolved a moment ago — the referenced `NetworkObject` may have since despawned, or (per the `NetworkBehaviourReference` API remarks) network ids get recycled by `NetworkManager` over time, so a stale reference can silently resolve to the *wrong* object instead of failing. Never cache the resolved reference across frames without re-resolving; always check the `TryGet` return value instead of trusting the implicit conversion, which returns `null` on failure.

## FastBufferWriter / FastBufferReader / BufferSerializer

| Member | Effect | Use when | Source |
|---|---|---|---|
| `FastBufferWriter(int size, Allocator allocator, int maxSize = -1)` | Struct-based writer, no GC allocation (Native Container allocation scheme) | Constructing a writer for a custom RPC/message body | [FastBufferWriter API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.FastBufferWriter.html) |
| `writer.TryBeginWrite(int bytes)` | Reserves a byte range up front; returns `false` (doesn't throw) if it won't fit | Before a batch of `WriteValue`/`WriteByte` calls, to pay the bounds check once instead of per-call | [FastBufferWriter/Reader](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/advanced-topics/fastbufferwriter-fastbufferreader.html) |
| `writer.WriteValue<T>(in T value)` / `reader.ReadValue<T>(out T value)` | Unsafe, unchecked write/read — fastest path | After a successful `TryBeginWrite`/`TryBeginRead` already covers the bytes | [FastBufferWriter API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.FastBufferWriter.html) |
| `writer.WriteValueSafe<T>(in T value)` / `reader.ReadValueSafe<T>(out T value)` | Bounds-checked write/read; throws `OverflowException` on overrun | One-off writes, or when you don't want to manage `TryBeginWrite` yourself | [FastBufferWriter API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.FastBufferWriter.html) |
| `BufferSerializer<TReaderWriter>` (`ref struct`, `TReaderWriter : IReaderWriter`) | Bi-directional wrapper over `FastBufferWriter`/`FastBufferReader`; one `SerializeValue` call reads or writes depending on `IsReader`/`IsWriter` | Inside `INetworkSerializable.NetworkSerialize<T>` — write the field-copy logic once instead of twice | [BufferSerializer](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/advanced-topics/bufferserializer.html) |
| `serializer.PreCheck(int amount)` + `SerializeValuePreChecked<T>()` | Skips the automatic bounds check `BufferSerializer` normally performs on every `SerializeValue` call | Serializing a large number of values in a loop, where the automatic per-call check adds measurable overhead | [BufferSerializer API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.BufferSerializer-1.html) |
| `serializer.GetFastBufferReader()` / `GetFastBufferWriter()` | Drops down to the raw reader/writer, valid only when `IsReader`/`IsWriter` matches | Needing a `BytePacker`/`ByteUnpacker` call that `BufferSerializer` doesn't expose directly | [BufferSerializer API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.BufferSerializer-1.html) |

**Critical caveat**: bounds violations on the unsafe `WriteValue`/`ReadValue`/`WriteBytes`/`ReadBytes` path only throw `OverflowException` in the Editor/development builds via a debug watermark check. In release/production builds there is no per-operation check — an overrun is undefined behavior (memory corruption), not a caught exception. Use the `Safe` variants, or a validated `TryBeginWrite`/`TryBeginRead`, for anything reading untrusted or variable-length data.

```csharp
// Manual bounds check + unsafe writes, paid once for the whole batch.
using var writer = new FastBufferWriter(256, Allocator.Temp);
if (!writer.TryBeginWrite(sizeof(float) + sizeof(bool) + sizeof(int)))
{
    throw new OverflowException("Not enough space in the buffer");
}

writer.WriteValue(f);
writer.WriteValue(b);
writer.WriteValue(i);
```

## Packed numeric writes — BytePacker / ByteUnpacker

Used inside a custom `NetworkSerialize`/extension method when a field's typical range is much smaller than its declared type, to shrink the wire size below what `WriteValue`/`SerializeValue` would send.

| Member | Encoding | Range / cost | Source |
|---|---|---|---|
| `BytePacker.WriteValuePacked` / `ByteUnpacker.ReadValuePacked` | Varint; supports `int`, `uint`, `long`, `ulong`, `short`, `ushort`, `float`, `double`, `string`, Unity primitives, and `unmanaged Enum` | Any value, but a large value can end up costing **more** than `sizeof(T)` — only use when you're confident values are typically small | [BytePacker API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.BytePacker.html) / [ByteUnpacker API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.ByteUnpacker.html) |
| `BytePacker.WriteValueBitPacked` / `ByteUnpacker.ReadValueBitPacked` | ZigZag-encoded varint, integral types only (`short`/`int`/`long`/`ushort`/`uint`/`ulong`) | Never exceeds `sizeof(T)`, but the usable range shrinks (e.g. `int` effectively loses 3 bits: 29 data bits + sign) | [BytePacker API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.BytePacker.html) |
| `QuaternionCompressor.CompressQuaternion(ref Quaternion) -> uint` / `DecompressQuaternion` | "Smallest three" — omits the largest component (reconstructed via `w = sqrt(1 - (x²+y²+z²))`), packs the rest into a `uint` | 16 bytes → 4 bytes (75% reduction); worked example for how `INetworkSerializable` can compress a field before writing it | [QuaternionCompressor API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.QuaternionCompressor.html) |

## Custom serialization for FastBufferWriter/Reader and NetworkVariable&lt;T&gt;

For a type used only inside a hand-rolled message (not through `INetworkSerializable`), extend `FastBufferWriter`/`FastBufferReader` directly:

```csharp
public struct Health
{
    public int CurrentHealth;
    public uint MaxHealth;
}

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

To let `Health` be used directly as a `NetworkVariable<Health>` payload without implementing `INetworkSerializable` on it, register the same logic with `UserNetworkVariableSerialization<T>` before any serialization happens (e.g. in a static constructor or an early bootstrap method):

```csharp
UserNetworkVariableSerialization<Health>.WriteValue = FastBufferExtensions.WriteValueSafe;
UserNetworkVariableSerialization<Health>.ReadValue = FastBufferExtensions.ReadValueSafe;
UserNetworkVariableSerialization<Health>.DuplicateValue = (in Health value, ref Health duplicatedValue)
    => duplicatedValue = value;
```

**Critical caveat**: `WriteValue`, `ReadValue`, and `DuplicateValue` are three independent delegate fields — all three must be assigned or `NetworkVariable<Health>` fails at runtime; there's no partial/default fallback for the ones you skip. `DuplicateValue` isn't cosmetic — `NetworkVariableSerialization<T>` calls it to snapshot the previous value for dirty-checking, so an incorrect duplicate (e.g. a shallow copy that aliases a reference field) makes the variable's change detection silently wrong.

An equivalent `BufferSerializer<T>` extension method serves `INetworkSerializable` types that embed `Health` as a field, reusing the same two-line body but through the read/write-agnostic `SerializeValue` call instead of separate methods:

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

`WriteDelta`/`ReadDelta` are an optional fourth and fifth pair on `UserNetworkVariableSerialization<T>` — define both together to send only the changed portion of a value instead of the whole thing on every dirty tick; omit both to always send the full value.

For a `NetworkVariable<T>`-like container built from scratch (subclassing `NetworkVariableBase` directly and overriding `WriteField`/`ReadField`/`WriteDelta`/`ReadDelta` yourself, including the generic `MyCustomGenericNetworkVariable<T>` shape), see [state-sync.md](state-sync.md) — that is a `NetworkVariable<T>` design choice, not a serialization-format choice, so it's covered there rather than here.

Two more registration/codegen tools exist for narrower cases: `GenerateSerializationForTypeAttribute(Type)` forces codegen to generate serialization for a specific type in special manual-serialization scenarios (its sibling `GenerateSerializationForGenericParameterAttribute` is the one to reach for on a generic `NetworkVariable`-style class's type parameter); and `NetworkVariableSerialization<T>` itself is the internal dispatcher — it picks codegen, falls back to `UserNetworkVariableSerialization<T>`, and exposes `AreEqual`/`Duplicate` helpers, but application code registers against `UserNetworkVariableSerialization<T>`, not `NetworkVariableSerialization<T>` directly.

## API index

| Type | Source |
|---|---|
| `INetworkSerializable` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.INetworkSerializable.html) |
| `INetworkSerializeByMemcpy` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.INetworkSerializeByMemcpy.html) |
| `ForceNetworkSerializeByMemcpy<T>` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.ForceNetworkSerializeByMemcpy-1.html) |
| `FastBufferWriter` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.FastBufferWriter.html) |
| `FastBufferReader` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.FastBufferReader.html) |
| `BufferSerializer<TReaderWriter>` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.BufferSerializer-1.html) |
| `IReaderWriter` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.IReaderWriter.html) |
| `BytePacker` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.BytePacker.html) |
| `ByteUnpacker` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.ByteUnpacker.html) |
| `NetworkVariableSerialization<T>` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkVariableSerialization-1.html) |
| `UserNetworkVariableSerialization<T>` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.UserNetworkVariableSerialization-1.html) |
| `NetworkObjectReference` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkObjectReference.html) |
| `NetworkBehaviourReference` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkBehaviourReference.html) |
| `GenerateSerializationForTypeAttribute` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.GenerateSerializationForTypeAttribute.html) |
| `QuaternionCompressor` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.QuaternionCompressor.html) |

Related: [state-sync.md](state-sync.md) covers `NetworkVariable<T>`/`NetworkList<T>` themselves (read/write permission, `OnValueChanged`, custom `NetworkVariableBase` subclasses) — this file covers only how a *value* used inside one gets turned into bytes.
