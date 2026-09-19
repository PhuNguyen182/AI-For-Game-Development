---
name: source-generator-authoring
description: >
  C# Incremental Source Generators (`IIncrementalGenerator`) that replace
  mechanically repetitive hand-written code in the Shared Core — snapshot and
  restore codecs for rollback, deterministic equality and hashing, ability or
  effect registries that displace reflection-based discovery — emitted at
  compile time from `partial` declarations and marker attributes, via
  `SyntaxProvider.ForAttributeWithMetadataName`, `context.AddSource`,
  `netstandard2.0` generator assemblies and Unity's `RoslynAnalyzer` asset
  label. Use it once a structurally derivable pattern repeats across types and
  copying it by hand has started to drift. Not for: enforcing a rule or
  reporting a violation (`roslyn-analyzer-codefix`), the formatter MemoryPack
  already generates (`memorypack-serialization`), a one-off with no repetition,
  which YAGNI forbids (`coding-principles.md`).
---

# Source Generator Authoring — Compile-Time Code for the Shared Core

## 1. Objective
Emit boilerplate that would otherwise be copy-pasted across Shared Core types and drift out of sync — without introducing runtime reflection, non-deterministic emission order, or a `UnityEngine` dependency into `Game.Core.*`, and without a pipeline that recomputes on every keystroke and degrades the whole team's IDE.

## 2. Role
Act as the C# meta-programming specialist. You own the generator project itself — its target framework, pipeline design, incremental-caching correctness, and Unity integration — not only the code it happens to emit.

## 3. When to invoke this skill
- A structural pattern repeats across three or more Shared Core types and hand-writing it has drifted or will: snapshot/restore state for rollback-friendly prediction, deterministic equality and hashing for state comparison, a compile-time registry replacing an `Assembly.GetTypes()` scan.
- Reflection-based type discovery is unreliable on the project's IL2CPP or AOT target, where types can be stripped, and it needs to become compile-time.
- Escalated from Tech Lead – C# Unity when a pattern decision resolves to generated code — "Shared Core should expose rollback-friendly state" settled as a generated snapshot contract.
- Negative trigger: flagging a rule violation at compile time — that's `roslyn-analyzer-codefix`, a different Roslyn surface (`DiagnosticAnalyzer`, not `IIncrementalGenerator`).
- Negative trigger: the serialization formatter for a DTO — MemoryPack already generates that from `[MemoryPackable]`, and it belongs to `memorypack-serialization`.
- Negative trigger: one type's boilerplate with no repetition elsewhere — write it by hand; a generator for a single caller is the speculative infrastructure YAGNI forbids in `coding-principles.md`.

## 4. How to use this skill
1. **Confirm the repetition is real before building anything** — count the types that need it today, not the ones that might. A generator is a permanent build dependency every engineer inherits, so it has to be cheaper than the duplication it removes, which one or two call sites never are.
2. **Target `netstandard2.0` for the generator assembly** — it loads into the compiler host, not into the game, and any other target framework fails to load. That failure is near-silent: the generator emits nothing and the build reports missing types rather than a generator error, so confirm the TFM before debugging the pipeline.
3. **Use `IIncrementalGenerator`, never the obsolete `ISourceGenerator`** — the latter is exactly the kind of deprecated API `coding-principles.md`'s Obsolete APIs rule bans new code against. Confirm the project's Roslyn and Unity versions support it before committing.
4. **Never build a generator that consumes another generator's output** — every generator runs against the original compilation, so one expecting MemoryPack's emitted formatter or another generator's members will find nothing and emit against a type that does not exist yet. Derive everything from the hand-written declaration, or fold both jobs into one generator.
5. **Filter cheapest-first in the pipeline** — a syntax-only predicate before any semantic lookup. Prefer `SyntaxProvider.ForAttributeWithMetadataName(...)` over a hand-rolled `CreateSyntaxProvider` pair when targeting a marker attribute, per the [Roslyn incremental generator cookbook](https://github.com/dotnet/roslyn/blob/main/docs/features/incremental-generators.md); it is already optimized for this case.
6. **Make every value that flows between pipeline stages equatable** — a `readonly record struct` model, never a raw `ISymbol` or `SyntaxNode`. A captured symbol pins the whole compilation and defeats incremental caching, which turns every keystroke in any file into a full regeneration for everyone on the team.
7. **Emit only `partial` additions, fully qualified with `global::`** — a generator must never require a human to edit hand-written code for the build to succeed, and unqualified type names in emitted code collide with whatever `using` directives the consuming file happens to have.
8. **Derive each `AddSource` hint name from the fully-qualified type name** — two marked types sharing a short name across namespaces produce a duplicate hint name, which fails the build with an error that names neither type.
9. **Hold emitted Shared Core code to the same rules as hand-written Shared Core code** — no `UnityEngine` reference in anything landing in `Game.Core.*` per `naming-convention.md`'s namespace boundary, no `UnityEngine.Random` or wall-clock time, and members emitted in source declaration order rather than dictionary or reflection enumeration order, which is the non-determinism `coding-principles.md`'s Shared Core rule exists to prevent.
10. **Keep marker attributes free of logic** — define them in a small attributes assembly both the generator and the consuming code reference; they exist to be found at compile time, nothing more.
11. **Report a diagnostic on malformed input; never throw** — an unhandled exception in a generator kills the whole compilation with an opaque Roslyn internal error that points at no file. Call `context.ReportDiagnostic(...)` at the offending declaration with a message naming what shape was expected.
12. **Confirm the Unity integration path and inspect the real output before claiming it works** — Unity consumes generators as `.dll`s labelled `RoslynAnalyzer` with all platforms unchecked, not as a `<PackageReference>`. Set `<EmitCompilerGeneratedFiles>true</EmitCompilerGeneratedFiles>` to read what was actually emitted on disk, and pin it with `CSharpSourceGeneratorVerifier` snapshot tests rather than eyeballing it once.

## 5. Specific goals / tasks this skill performs
- Snapshot/restore codecs for rollback-friendly state used in prediction and reconciliation.
- Deterministic equality and hashing for state-comparison types.
- Compile-time registries replacing reflection-based type discovery on IL2CPP and AOT targets.
- Generator project setup: `netstandard2.0` target, marker-attribute assembly, Unity `RoslynAnalyzer` packaging.
- Incremental-caching correctness: equatable pipeline models and cheapest-first filtering.
- Out of scope: rule enforcement and diagnostics (`roslyn-analyzer-codefix`), MemoryPack's own formatter generation (`memorypack-serialization`), one-off code with no repetition (`coding-principles.md`).

## 6. Output format
```
## Source Generator — <generator name>
- Repetition justifying it: <types affected today, drift observed>
- Trigger: <marker attribute / syntax shape targeted>
- Pipeline: <predicate → transform → output; inter-stage model type and why it is equatable>
- Generator TFM: netstandard2.0 — confirmed
- Chaining check: <confirmed it consumes no other generator's output>
- Emitted members/types: <summary; hint-name scheme>
- Determinism check: <no UnityEngine reference, emission in source declaration order>
- Unity integration: <RoslynAnalyzer label, platforms unchecked — confirmed how>
- Diagnostics reported: <list, or "none">
- Tests: <snapshot/verifier tests, and the emitted output inspected via EmitCompilerGeneratedFiles>
- Layer: Game.Core.* (emitted) / generator project is Editor-and-build-time only
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <shapes the generator does not handle — omit this line entirely if there are genuinely none>
- Latent concerns: <caching assumptions, type counts not yet reached, toolchain versions relied on>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: "Shared Core inventory and ability-cooldown state both need rollback snapshot/restore, and hand-writing it has already drifted once."
- Output: an `IIncrementalGenerator` keyed on `[Snapshotable]` over `partial struct`s, emitting `Snapshot()`/`Restore(in Snapshot)` in declared-field order with `global::`-qualified types, no `UnityEngine` reference, pipeline models as `readonly record struct`, snapshot tests covering both types.

**Example 2**
- Input: "have the snapshot generator read the members MemoryPack generates, so we don't have to mark them twice."
- Output: declined — generators all run against the original compilation and cannot observe each other's output, so this would emit against members that do not exist at that point. Kept both keyed off the same hand-written `partial` declaration, which is the only shape both can see.

**Example 3**
- Input: after adding a generator, engineers report the IDE getting slower across the whole solution.
- Output: the transform stage was returning `INamedTypeSymbol` directly, so no pipeline value was equatable and every keystroke anywhere invalidated the cache. Replaced it with a `readonly record struct` carrying the fully-qualified name and field list, and moved the attribute match to `ForAttributeWithMetadataName`.

## 8. Edge cases & guardrails
- Never emit code that reads wall-clock time, calls `UnityEngine.Random`, or otherwise reintroduces the non-determinism the Shared Core rule bans — a generator is not exempt because no human typed it.
- Never emit in dictionary or reflection enumeration order — the source is stable but the output would not be, across compilers and platforms.
- Never let a generator throw — the compilation dies with an error naming no file; report a diagnostic instead.
- Never pass an `ISymbol` or `SyntaxNode` between pipeline stages — it defeats incremental caching for everyone on the team, not just its author.
- Never build a generator against another generator's output — it cannot see it.
- Never target anything but `netstandard2.0` for the generator assembly — it fails to load, and it fails quietly.
- Never build a generator for a pattern with one call site — wait until the repetition is real.
