---
name: memorypack-serialization
description: >
  MemoryPack — zero-encoding binary serialization for C#: `[MemoryPackable]`
  partial types, `[MemoryPackOrder]`, `[MemoryPackIgnore]`,
  `[MemoryPackInclude]`, `[MemoryPackConstructor]`, `[MemoryPackOnDeserialized]`
  callbacks, `[MemoryPackUnion]` polymorphism, and
  `MemoryPackSerializer.Serialize`/`Deserialize` over `Span<byte>` or `Stream`.
  No `UnityEngine` dependency, so DTOs are safe inside `Game.Core.*`. Use when
  defining or changing a type that persists to disk or crosses the network —
  a save snapshot, a message DTO, a rollback/prediction state — especially when
  it must stay compatible with data already written.
  Not for: RPC contract and transport design (`magiconion-rpc-networking`), generators around the DTOs (`source-generator-authoring`), human-readable or designer-authored data (`csvhelper-csv-data`), text building (`zstring-zero-allocation-strings`).
---

# MemoryPack — Zero-Encoding Binary Serialization

## 1. Objective
Serialize save snapshots, network DTOs, and rollback state to compact binary through source-generated code — without silently breaking compatibility with data already on disk or in flight, without trusting a deserialized payload that may be corrupt or hostile, and without letting serialization concerns grow into the type's gameplay responsibilities.

## 2. Role
Act as the binary-serialization specialist for the client track, and the rare one usable directly inside `Game.Core.*`: MemoryPack's generated code is plain C# with no `UnityEngine` reference, so C# Software Engineer can reach for it without crossing the Shared Core boundary that `coding-principles.md`'s Shared Core integrity section draws.

## 3. When to invoke this skill
- Defining a save-data snapshot, a network message DTO, or a rollback/prediction state type that must serialize to bytes efficiently.
- Adding, removing, or reordering a member on a type that has already shipped — the case where the format's compatibility rules actually decide the answer.
- A Shared Core type needs polymorphic round-tripping (an effect or ability hierarchy) and would otherwise grow a hand-rolled type tag plus manual decode branch.
- A type carries fields that must not persist — a cached, recomputable value — and needs its serialized surface narrowed rather than its shape restructured.
- Negative trigger: designing the RPC service or hub contract, choosing the transport, or configuring `MagicOnion.Serialization.MemoryPack` — that is `magiconion-rpc-networking`; this skill defines only the DTOs that contract carries.
- Negative trigger: generating the boilerplate *around* a family of DTOs — that is `source-generator-authoring`; MemoryPack already generates the per-type serialization code itself.
- Negative trigger: a format that must stay human-readable or hand-editable, such as a designer-authored balance table — that is `csvhelper-csv-data`; MemoryPack is binary-only.
- Negative trigger: building strings or text output — that is `zstring-zero-allocation-strings`; MemoryPack is not a formatting tool.

## 4. How to use this skill
1. **Declare the type `partial` and attribute it `[MemoryPackable]`**, per the [MemoryPack documentation](https://github.com/Cysharp/MemoryPack) — the source generator emits the `IMemoryPackable<T>` implementation into that partial declaration, so a non-partial type fails to generate rather than failing at runtime.
2. **Decide version tolerance before the type ships anywhere persistent, not after** — the default generated layout is positional, so adding or reordering a member later reinterprets existing bytes. Confirm the version-tolerant generation mode against the upstream README and choose it deliberately for save files and versioned protocols; the choice is effectively permanent once real data exists.
3. **Set `[MemoryPackOrder]` explicitly on every member of a persisted type** — implicit declaration order works until someone inserts a field in the middle, at which point every previously written payload decodes into the wrong members with no error raised. Treat member order the way a schema migration treats columns.
4. **Narrow the serialized surface with `[MemoryPackIgnore]`, and reach for `[MemoryPackInclude]` only for a private member that genuinely must round-trip** — a cached or recomputable value written into every payload costs bytes forever and adds a second source of truth (YAGNI).
5. **Model polymorphism with `[MemoryPackUnion]` and stable, never-reused tag values** — a hand-rolled discriminator plus `switch` decoding must be edited for every new subtype, which is exactly the modification Open/Closed in `coding-principles.md` forbids. Reusing a retired tag silently decodes old data as the wrong type.
6. **Give a type with a non-default constructor an explicit `[MemoryPackConstructor]`**, and put any post-load fixup in `[MemoryPackOnDeserialized]` rather than in a property setter — a setter that runs during deserialization produces order-dependent behaviour that is very hard to reproduce.
7. **Serialize against `Span<byte>` or `ReadOnlySpan<byte>` rather than an intermediate `byte[]` wherever the call site allows** — per `performance-and-algorithms.md`'s Memory discipline section, an allocation per message in a per-frame or per-tick path is the cost this library exists to avoid.
8. **Validate every deserialized payload at the call site that produced it, not inside the type** — a save file can be corrupt or tampered with and a network message can be hostile, which is precisely the case `coding-principles.md`'s Correctness boundaries section names. A successful `Deserialize<T>()` proves the bytes parsed, never that the values are in range.
9. **Keep the `[MemoryPackable]` type a pure data carrier** — its one job is to be an accurate wire or save representation, per Single Responsibility; gameplay rules on a DTO put a second reason to change into a type whose format is meant to stay frozen.
10. **Confirm the type compiles with no `UnityEngine` reference before placing it in `Game.Core.*`** — the Core assembly must stay engine-free, and a DTO that pulls in `Vector3` fails that boundary even though MemoryPack itself does not.
11. **Ask before changing a shipped type's shape when it is unclear whether live data exists** — if saves or in-flight messages are already out there, the change is a migration, not an edit, and guessing wrong corrupts player data irreversibly.

## 5. Specific goals / tasks this skill performs
- Define `[MemoryPackable]` DTOs for save data, network messages, or rollback snapshots inside `Game.Core.*`.
- Fix explicit `[MemoryPackOrder]` and the version-tolerance mode before a type reaches persistent storage.
- Model a polymorphic type family through `[MemoryPackUnion]` with stable tags.
- Narrow a type's persisted surface with `[MemoryPackIgnore]`/`[MemoryPackInclude]`.
- Place the boundary validation for deserialized data at the call site that owns the trust decision.
- Out of scope: RPC contract and transport design (`magiconion-rpc-networking`), surrounding boilerplate generation (`source-generator-authoring`), the validation rules themselves (written per `coding-principles.md` at the call site), designer-authored and human-readable data (`csvhelper-csv-data`).

## 6. Output format
```
## MemoryPack Work — <type name>
- Type: <name> — partial, [MemoryPackable]
- Version tolerance: <mode chosen> — persisted target: save file / wire protocol / in-memory only
- Member order: explicit [MemoryPackOrder] on every member — yes/no (why, if no)
- Serialized surface: <members ignored/included, with rationale>
- Polymorphism: [MemoryPackUnion] with tags <list> | not applicable
- Construction: [MemoryPackConstructor] / [MemoryPackOnDeserialized] — <what runs, if any>
- Serialization surface: Span<byte> / Stream — <call sites>
- Boundary validation: <call site validating the payload> | not a trust boundary — internal only
- Compatibility impact: none (new type) | breaking — <migration needed for existing data>
- Layer: Game.Core.* — confirmed free of UnityEngine references
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what this type's format does not cover>
- Latent concerns: <compatibility assumptions holding only while no live data exists, tags not yet reused>
- Future remediation: <the migration path for each, and the event that forces it>
```

## 7. Examples
**Example 1**
- Input: a rollback-friendly player state snapshot must serialize for client-side prediction reconciliation, many times per second.
- Output: `[MemoryPackable] public partial record struct PlayerStateSnapshot` with explicit `[MemoryPackOrder]` on Position, Health, ActiveAbilityId, and CooldownRemaining. Serialized into a pooled `Span<byte>` in the reconciliation path with no intermediate `byte[]`. No gameplay logic on the type. Version tolerance left off deliberately and recorded as such, since the snapshot never persists beyond a single session — with the re-open trigger stated as "the moment this shape is written to disk or replayed across builds".

**Example 2**
- Input: "add `[MemoryPackable]` to the `IAbility` implementations so the network layer can send whichever ability fired."
- Output: declined. Serializing the gameplay classes couples the wire format to the rules implementation, so every ability refactor becomes a protocol break, and it puts a second reason to change into types the format needs frozen. Modeled a separate `AbilityFiredMessage` base with `[MemoryPackUnion]` and one minimal DTO per ability instead; the `IAbility` implementations were left untouched.

**Example 3**
- Input: a shipped save type needs a new `UnlockedSkins` field added.
- Output: treated as a migration rather than an edit. The existing type was positional with no version tolerance, so appending a member would have made every existing save decode short. Confirmed live saves exist, then introduced a versioned successor type with the version-tolerant mode enabled and an explicit upgrade path from the old shape, rather than mutating the shipped one in place.

## 8. Edge cases & guardrails
- Never add, remove, or reorder a member on a shipped persisted type without confirming whether live data exists — the failure is silent misdecoding, not an exception.
- Never leave `[MemoryPackOrder]` implicit on anything that reaches disk or the network, per §4 — a later insertion shifts every subsequent member.
- Never reuse a retired `[MemoryPackUnion]` tag — old payloads will decode into the wrong type and look valid.
- Never treat a successful `Deserialize<T>()` as validation — it proves the bytes parsed, not that the values are sane.
- Never put gameplay logic on a `[MemoryPackable]` type — a DTO whose format must stay frozen cannot also carry rules that need to change.
- Never let a `UnityEngine` type into a DTO destined for `Game.Core.*` — that breaks the Shared Core boundary regardless of MemoryPack's own independence.
- Never use MemoryPack where the format must stay human-readable — it is binary-first and not hand-inspectable.
