---
name: memorypack-serialization
description: "MemoryPack binary serialization: [MemoryPackable] partial types, [MemoryPackOrder], version-tolerant mode, [MemoryPackUnion], formatters, IL2CPP setup. Use for saves, snapshots or network messages needing fast compact serialization."
user-invocable: false
---

# MemoryPack

Not for: RPC contract and transport (`magiconion-rpc-networking`), generators around the DTOs (`source-generator-authoring`), human-readable or designer-authored data (`csvhelper-csv-data`), text building (`zstring-zero-allocation-strings`).
Docs: https://github.com/Cysharp/MemoryPack — confirm the version-tolerant mode and attribute names against the README for the installed version. Generated code has no `UnityEngine` reference, so it is usable in `Game.Core.*`.
Rules: csharp.md Boundaries (validate at real boundaries); csharp-standards → coding-principles.md Correctness boundaries; performance-and-algorithms.md Memory discipline.

## Steps
1. **Declare the type `partial` with `[MemoryPackable]`** — the generator emits into the partial; a non-partial type fails to generate.
2. **Decide version tolerance before the type reaches persistent storage** — the default layout is positional, so a later add or reorder reinterprets existing bytes. Choose it deliberately for save files and versioned protocols; effectively permanent once data exists.
3. **Put `[MemoryPackOrder]` on every member of a persisted or wire type** — an insertion otherwise shifts all later members and old payloads decode into the wrong fields with no error.
4. **Narrow the surface with `[MemoryPackIgnore]`**; `[MemoryPackInclude]` only for a private member that must round-trip. Recomputable values cost bytes forever and add a second source of truth.
5. **Model polymorphism with `[MemoryPackUnion]` and never-reused tags** — a reused retired tag decodes old data as the wrong type and looks valid.
6. **Non-default constructor: `[MemoryPackConstructor]`; post-load fixup: `[MemoryPackOnDeserialized]`**, not a property setter (order-dependent during deserialization).
7. **Serialize to `Span<byte>`/`ReadOnlySpan<byte>`, not an intermediate `byte[]`**, in per-frame or per-tick paths.
8. **Validate the payload at the call site that owns the trust decision** — a successful `Deserialize<T>()` proves the bytes parsed, not that values are in range; saves can be corrupt and messages hostile.
9. **Keep the type a pure data carrier with no `UnityEngine` type** (`Vector3` breaks the Core boundary even though MemoryPack does not). Gameplay rules on a DTO add a second reason to change to a frozen format.
10. **Changing a shipped type: ask whether live saves or in-flight messages exist** — if so it is a migration (versioned successor type plus upgrade path), not an edit; a wrong guess corrupts player data irreversibly.

## Never
- Serialize gameplay classes (e.g. `IAbility` implementations) directly — every refactor becomes a protocol break; use a separate message DTO or `[MemoryPackUnion]` family.
- Use MemoryPack where the format must be human-readable or hand-editable.

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
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Add `[MemoryPackable]` to the `IAbility` implementations so the network can send the one that fired" → declined: couples wire format to rules; added `AbilityFiredMessage` with `[MemoryPackUnion]` and one DTO per ability.
