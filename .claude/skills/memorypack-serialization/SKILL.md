---
name: memorypack-serialization
description: "MemoryPack: [MemoryPackable], MemoryPackOrder, MemoryPackUnion, version-tolerant, IL2CPP. Use for compact serialization."
user-invocable: false
---

# MemoryPack

- **Not for:** RPC contract and transport (`magiconion-rpc-networking`).
- **Not for:** generators around the DTOs (`source-generator-authoring`).
- **Not for:** human-readable or designer-authored data (`csvhelper-csv-data`).
- **Not for:** text building (`zstring-zero-allocation-strings`).
- **Not for:** the save header, migration chain and old-save fixtures (`save-data-versioning-migration`).
- **Docs:** https://github.com/Cysharp/MemoryPack
  - **Version caveat:** confirm the version-tolerant mode and attribute names against the README for the installed version.
  - **Core use:** generated code has no `UnityEngine` reference, so it is usable in a Core assembly.
- **Rules:** `csharp.md` Boundaries (validate at real boundaries).
  - **Also:** `csharp-standards` → `coding-principles.md` Correctness boundaries; `performance-and-algorithms.md` Memory discipline.

## Steps
1. **Declare the type `partial` with `[MemoryPackable]`:** the generator emits into the partial; a non-partial type fails to generate.
2. **Decide version tolerance before the type reaches persistent storage:** the layout rules are below.
   - **Permanence:** the choice is effectively permanent once data exists.
   - **Default layout (`GenerateType.Object`):** sequential; members may only be appended; deleting, reordering or retyping one reinterprets existing bytes.
   - **`GenerateType.VersionTolerant`:** also allows deletion at a size cost; choose it deliberately for versioned protocols.
   - **Save files:** follow `save-data-versioning-migration` (one frozen DTO per version, so version tolerance only adds size).
3. **Put `[MemoryPackOrder]` on every member of a persisted or wire type:** required under `GenerateType.VersionTolerant` and `SerializeLayout.Explicit`, ignored otherwise.
   - **Without it:** an insertion shifts all later members and old payloads decode into the wrong fields with no error.
4. **Narrow the surface with `[MemoryPackIgnore]`:** `[MemoryPackInclude]` only for a private member that must round-trip.
   - **Why ignore recomputable values:** they cost bytes forever and add a second source of truth.
5. **Model polymorphism with `[MemoryPackUnion]` and never-reused tags:** a reused retired tag decodes old data as the wrong type and looks valid.
6. **Non-default constructor: `[MemoryPackConstructor]`; post-load fixup: `[MemoryPackOnDeserialized]`:** not a property setter (order-dependent during deserialization).
7. **Serialize into a pooled `IBufferWriter<byte>` and deserialize from `ReadOnlySpan<byte>`:** not an intermediate `byte[]`, in per-frame or per-tick paths.
   - **Overloads:** `Serialize` has no `Span<byte>` overload.
8. **Unity/IL2CPP setup:** Unity 2022.3.12f1 or later, core from NuGet (NuGetForUnity).
   - **`MemoryPack.Unity` package:** optional; adds Unity-type formatters and belongs to Client code only.
   - **Union initializers:** Unity has no `ModuleInitializer`, so call each union's generated `<Name>Initializer.RegisterFormatter()` at startup before the first deserialize.
   - **Custom formatter attributes:** unsupported on Unity.
9. **Validate the payload at the call site that owns the trust decision:** a successful `Deserialize<T>()` proves the bytes parsed, not that values are in range.
   - **Why:** saves can be corrupt and messages hostile.
10. **Keep the type a pure data carrier with no `UnityEngine` type:** `Vector3` breaks the Core boundary even though MemoryPack does not.
    - **Gameplay rules on a DTO:** add a second reason to change to a frozen format.
11. **Changing a shipped type: whether live saves or in-flight messages exist unstated → `Blocked` naming it:** a wrong guess corrupts player data irreversibly.
    - **Live saves or in-flight messages exist:** it is a migration (versioned successor type plus upgrade path), not an edit.

## Never
- **Serializing gameplay classes directly:** e.g. `IAbility` implementations — every refactor becomes a protocol break; use a separate message DTO or `[MemoryPackUnion]` family.
- **Human-readable or hand-editable formats:** using MemoryPack where the format must be human-readable or hand-editable.
- **Untrusted bytes:** deserializing bytes from another player or an unauthenticated client with it — upstream says it is intended for trusted data only.
  - **Saves on the player's own device:** pass the `save-data-versioning-migration` envelope checks first.
  - **Server-received payloads:** `Needs-decision`, `Next: cto` (serializer for untrusted input, `core.md` Security).

## Output
```
## MemoryPack Work — <type>
- Version tolerance: <mode> — target: save file | wire | in-memory only
- Member order: explicit on every member | no (why)
- Serialized surface: <ignored/included, why>
- Polymorphism: [MemoryPackUnion] tags <list> | n/a
- Construction: <[MemoryPackConstructor]/[MemoryPackOnDeserialized] use, if any>
- Boundary validation: <call site> | internal only
- Compatibility impact: none (new type) | breaking — <migration>
```

## Example
- **"Add `[MemoryPackable]` to the `IAbility` implementations so the network can send the one that fired":** declined — couples wire format to rules.
  - **Done instead:** added `AbilityFiredMessage` with `[MemoryPackUnion]` and one DTO per ability.
