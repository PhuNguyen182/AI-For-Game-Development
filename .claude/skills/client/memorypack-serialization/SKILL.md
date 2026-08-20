---
name: memorypack-serialization
description: >
  Technique for zero-encoding binary serialization with MemoryPack —
  `[MemoryPackable]` partial types, `[MemoryPackOrder]`/`[MemoryPackIgnore]`/
  `[MemoryPackInclude]` member control, `[MemoryPackUnion]` for polymorphic
  types, and `MemoryPackSerializer.Serialize`/`Deserialize` against
  `Span<byte>`/`Stream`. Use this for any Shared Core data that needs to
  cross a boundary as bytes — a save-data snapshot, a network message DTO,
  a rollback/prediction state snapshot. Unlike the rest of this Cysharp
  ecosystem skill set, MemoryPack has no `UnityEngine` dependency — its
  generated code is plain C#, so `[MemoryPackable]` DTOs are one of the few
  things in this stack that are safe to define directly in `Game.Core.*`,
  making it the natural pairing with `source-generator-authoring`'s
  snapshot/codec guidance. Do not use this to design an RPC service/hub
  contract or choose the transport — that's `magiconion-rpc-networking`,
  which consumes MemoryPack as its wire format via the
  `MagicOnion.Serialization.MemoryPack` package but owns the contract shape
  itself. Do not use this for a save-data or network validation boundary
  check (untrusted input at deserialization) — write that check per
  `coding-principles.md`'s Correctness boundaries section at the call site
  that deserializes, not inside the `[MemoryPackable]` type itself. Do not
  use this for hand-rolled JSON/XML serialization needs — MemoryPack is a
  binary-only format; keep human-readable config/save formats on
  `System.Text.Json` or similar where readability matters more than size.
---

# MemoryPack — Zero-Encoding Binary Serialization

Source: [github.com/Cysharp/MemoryPack](https://github.com/Cysharp/MemoryPack).

## 1. Objective
Serialize Shared Core data (save snapshots, network DTOs, rollback state) to and from compact binary with source-generated, allocation-minimal code — without breaking determinism across platforms, silently changing wire compatibility via an unordered member, or letting a serialization concern leak into the type's own gameplay logic.

## 2. Role
Act as the binary-serialization specialist for the client track, usable directly inside `Game.Core.*` since MemoryPack's generated code has no `UnityEngine` dependency — the rare tool in this stack C# Software Engineer can reach for without crossing the Shared Core boundary.

## 3. When to invoke this skill
- Defining a save-data snapshot type, a network message DTO, or a rollback/prediction state snapshot that needs to serialize to bytes efficiently.
- A Shared Core type needs polymorphic serialization (an `IAbility`/effect hierarchy that must round-trip through bytes) — model it via `[MemoryPackUnion]` instead of a hand-rolled type tag plus manual branch-decoding.
- A type has fields that shouldn't be serialized (a cached, recomputable value) — use `[MemoryPackIgnore]` rather than restructuring the type or moving the field out.
- Three or more DTOs need the same repetitive shape (a family of network messages, a family of snapshot types) — pair this with `source-generator-authoring`'s guidance for the surrounding boilerplate, while MemoryPack itself handles the per-type serialization code generation.
- Negative trigger: designing the RPC service/hub contract itself — that's `magiconion-rpc-networking`; this skill only defines the DTOs that contract passes over the wire.
- Negative trigger: validating untrusted deserialized data — that's a Correctness-boundary check per `coding-principles.md`, written at the deserialization call site, not baked into the `[MemoryPackable]` type.
- Negative trigger: a human-readable format (JSON config, a debug-inspectable save file) — MemoryPack is binary-only; use a text-based serializer instead when readability is the actual requirement.

## 4. How to use this skill
1. **Mark the type `partial` and `[MemoryPackable]`.** The source generator needs a partial declaration to emit the `IMemoryPackable<T>` implementation into — this is the same mechanical pattern `source-generator-authoring` already establishes for Shared Core generated code.
2. **Set `[MemoryPackOrder]` explicitly on every member once the type ships anywhere persistent** (a save file, a versioned network protocol) — implicit declaration order works until a member is added/reordered later and silently breaks wire/save compatibility with existing data. Treat this the same way a database migration treats column order: deliberate, not incidental.
3. **Use `[MemoryPackIgnore]` for computed/cached fields**, and `[MemoryPackInclude]` only for the rare private member that must round-trip despite not being public — don't serialize more than the type's actual persisted contract needs (YAGNI).
4. **Model polymorphism with `[MemoryPackUnion]`**, not a hand-rolled discriminator field plus manual `switch`-based decoding — this keeps a new subtype addable without touching the base type's serialization code (Open/Closed in `coding-principles.md`).
5. **Serialize against `Span<byte>`/`ReadOnlySpan<byte>` where the call site allows it**, not an intermediate `byte[]` allocation, when the surrounding code is itself allocation-conscious (a per-frame or per-message hot path) — consistent with `performance-and-algorithms.md`'s general allocation discipline.
6. **Treat deserialized data as untrusted at its actual boundary.** A save file can be corrupted or tampered with; a network message can be malformed or hostile. Validate ranges/invariants right after `Deserialize<T>()` returns, at the call site — per Correctness boundaries in `coding-principles.md` — rather than trusting the deserialized shape blindly just because the type-check succeeded.
7. **Keep the `[MemoryPackable]` type a pure data carrier.** No gameplay logic inside it beyond what a DTO should have — that's Single Responsibility; the type's only job is "be an accurate wire/save representation," not "also compute damage."

## 5. Specific goals / tasks this skill performs
- Defining `[MemoryPackable]` DTOs for save data, network messages, or rollback/prediction snapshots inside `Game.Core.*`.
- Setting explicit `[MemoryPackOrder]` for wire/save-compatible member ordering.
- Modeling a polymorphic type family via `[MemoryPackUnion]`.
- Choosing `[MemoryPackIgnore]`/`[MemoryPackInclude]` for a type's actual persisted surface.
- Out of scope: RPC contract/transport design (`magiconion-rpc-networking`), boundary validation logic itself (write per `coding-principles.md` at the call site), human-readable serialization formats.

## 6. Output format
```
## MemoryPack Work — <DTO/type name>
- Type: <name>, partial, [MemoryPackable]
- Member order: explicit [MemoryPackOrder] set — yes/no (why, if no)
- Ignored/included members: <list with rationale>
- Polymorphism: [MemoryPackUnion] — yes/no, subtypes
- Serialization surface: Span<byte> / Stream — call sites
- Boundary validation: <where the deserialized data is validated, or "not a trust boundary — internal use only">
- Layer: Game.Core.* (UnityEngine-free — confirmed)
- Known limitations: <...>
```

## 7. Examples
**Example 1**
- Input: a rollback-friendly snapshot of player state needs to serialize for client-side prediction reconciliation.
- Output: `[MemoryPackable] public partial record struct PlayerStateSnapshot` with explicit `[MemoryPackOrder]` on every field (Position, Health, ActiveAbilityId, CooldownRemaining), no gameplay logic on the type itself, serialized against `Span<byte>` in the reconciliation hot path with no intermediate `byte[]` allocation; confirmed zero `UnityEngine` reference so it stays valid inside `Game.Core.*`.

**Example 2**
- Input: "add MemoryPack serialization directly to the `IAbility` implementations so the network layer can send whichever ability fired."
- Output: modeled `[MemoryPackUnion]` on a base `AbilityFiredMessage` type with one case per ability's DTO instead of hand-rolling a type-tag `switch`; kept the actual `IAbility` gameplay implementations untouched — the wire DTO is a separate, minimal data carrier, not the ability class itself.

## 8. Edge cases & guardrails
- Never leave `[MemoryPackOrder]` implicit on a type that persists to disk or crosses the network — a later member addition/reorder silently breaks compatibility with existing data.
- Never trust deserialized data without a boundary check at the call site — corrupted saves and malformed/hostile network payloads are exactly the case `coding-principles.md`'s Correctness boundaries section calls out.
- Never add gameplay logic to a `[MemoryPackable]` type — it's a data carrier, not a rules implementation (Single Responsibility).
- Never use MemoryPack for a format that needs to stay human-readable/debuggable — it's a binary-only, performance-first serializer.
- Never assume MemoryPack usage alone makes a type Burst-compatible or safe inside a Job — that's an unrelated concern covered by `unity-job-system-and-burst`/`unity-collections` if it ever comes up.
