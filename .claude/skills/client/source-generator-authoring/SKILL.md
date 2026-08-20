---
name: source-generator-authoring
description: >
  Technique for building C# Incremental Source Generators (IIncrementalGenerator)
  that eliminate hand-written, mechanically-repetitive boilerplate in the
  Shared Core — snapshot/restore codecs for rollback, deterministic
  equality/hashing, network-message serialization, ability/effect registries
  — generated at compile time from partial classes and marker attributes,
  with zero runtime reflection so the generated code stays deterministic and
  safe for both client prediction and server authority. Use this before
  hand-writing any repetitive, structurally-derivable code across multiple
  Shared Core types. Do not use this for compile-time rule enforcement or
  diagnostics (banning UnityEngine in Game.Core, determinism checks, naming
  violations) — that's `roslyn-analyzer-codefix`. Do not use this for a
  one-off piece of code that isn't actually repeated across types — just
  write it (YAGNI).
---

# Source Generator Authoring

## 1. Objective
Remove hand-written boilerplate that would otherwise be copy-pasted (and drift out of sync) across multiple Shared Core types, by generating it at compile time — without introducing runtime reflection, non-determinism, or a `UnityEngine` dependency into `Game.Core.*`.

## 2. Role
Act as a senior C# meta-programming engineer. You own the generator project itself (its `.csproj`, pipeline design, and incremental-caching correctness), not just the code it happens to emit — a generator that recomputes on every keystroke degrades the whole team's IDE experience, so pipeline design is part of the deliverable.

## 3. When to invoke this skill
- A structural pattern repeats across three or more Shared Core types and hand-writing it risks drift: snapshot/restore state for rollback-friendly prediction, deterministic equality/hashing for state comparison, a serialization codec for a network message DTO, a compile-time registry of ability/effect types replacing reflection-based discovery.
- Escalated from Tech Lead – C# Unity when a pattern decision explicitly calls for generated code (e.g. "Shared Core should expose rollback-friendly state" resolved as a generated snapshot contract).
- Negative trigger: enforcing a coding rule or flagging a violation at compile time — that's `roslyn-analyzer-codefix`, a different Roslyn API surface (`DiagnosticAnalyzer`, not `IIncrementalGenerator`).
- Negative trigger: a single type's boilerplate with no repetition elsewhere in the codebase — write it by hand; a generator for one caller is speculative infrastructure (YAGNI).

## 4. How to use this skill
1. **Use `IIncrementalGenerator`, never the obsolete `ISourceGenerator`.** Confirm the project's actual Unity/.NET SDK version supports it (per the "check the project's language version first" caveat already required by `coding-principles.md`) before committing to it.
2. **Build the pipeline in stages, cheapest filter first**: a fast, syntax-only predicate (e.g. `node is ClassDeclarationSyntax { AttributeLists.Count: > 0 }`) before any semantic-model lookup. Prefer `context.SyntaxProvider.ForAttributeWithMetadataName(...)` over a hand-rolled `CreateSyntaxProvider` predicate/transform pair when targeting a marker attribute — it's already optimized for this exact case.
3. **Keep every pipeline stage incremental-cacheable**: the value flowing between stages must implement value equality (a `readonly record struct` model type, not a raw `ISymbol`/`SyntaxNode`) so Roslyn can skip recomputation when unrelated files change. Capturing a bare `ISymbol` past the transform stage silently defeats incremental caching and degrades IDE responsiveness for the whole team.
4. **Emit only `partial` additions** — a generator must never require editing hand-written code to compile; it only adds members/types the hand-written `partial` declaration opts into.
5. **Marker attributes carry no logic.** Define them in a small shared attributes file/assembly referenced by both the generator and the consuming code; they exist purely as compile-time markers for the generator to find.
6. **Hold generated Shared Core code to the same rules as hand-written Shared Core code**: no `UnityEngine` dependency in anything emitted into `Game.Core.*` (the namespace boundary rule in `naming-convention.md` applies to generated code exactly as much as hand-written code), and no non-deterministic emission — iterate/emit members in stable declaration order (`SyntaxNode` order from the source, never `Dictionary`/reflection enumeration order), since that same instability is exactly what `coding-principles.md`'s Shared Core determinism rule exists to prevent.
7. **Report generator-time problems as diagnostics, don't fail silently or emit broken code.** If a marked type is missing a required member or shape the generator needs, call `context.ReportDiagnostic(...)` with a clear message pointing at the offending declaration — never let the generator throw an unhandled exception (that kills the whole compilation with an opaque Roslyn internal error) or silently skip emission.
8. **Confirm the project's actual Unity integration path** before assuming a generator "just works" — Unity consumes Roslyn generators as `.dll`s imported with the `RoslynAnalyzer` asset label (Unity 2021.2+), not via a `<PackageReference>` the way a plain .NET project would; verify against this project's confirmed Unity version before relying on it.
9. **Test the generator like any other code**: verify emitted output against a known input using `Microsoft.CodeAnalysis.Testing`'s `CSharpSourceGeneratorVerifier` (or an equivalent snapshot test), not just by eyeballing generated output once.

## 5. Specific goals / tasks this skill performs
- Snapshot/restore codecs for rollback-friendly state (client prediction + reconciliation).
- Deterministic equality/hashing for state-comparison types used in reconciliation.
- Serialization codecs for network message DTOs (when the backend track is active).
- Compile-time ability/effect/state registries that replace reflection-based type discovery — reflection has both a startup cost and, on IL2CPP/AOT platforms, can be unreliable or stripped entirely.
- Out of scope: diagnostic/analyzer enforcement of coding rules (`roslyn-analyzer-codefix`), and any one-off code with no cross-type repetition (write it by hand).

## 6. Output format
```
## Source Generator — <generator name>
- Trigger: <marker attribute / syntax shape the generator targets>
- Pipeline stages: <syntax filter → transform → output, with caching notes>
- Emitted members/types: <summary>
- Determinism check: <confirms no UnityEngine dependency, stable emission order>
- Unity integration: <RoslynAnalyzer asset label / other confirmed mechanism>
- Diagnostics reported: <list, or "none">
- Tests: <snapshot/verifier tests added>
- Known limitations: <...>
```

## 7. Examples
**Example 1**
- Input: "The Shared Core inventory and ability-cooldown state both need rollback-friendly snapshot/restore, and hand-writing it for every new state type has already drifted once."
- Output: an `IIncrementalGenerator` triggered by a `[Snapshotable]` marker attribute on a `partial struct`, emitting a `Snapshot()`/`Restore(in Snapshot)` pair in declared-field order, no `UnityEngine` reference, verified with a source-generator snapshot test covering both state types.

**Example 2**
- Input: "New ability types need to be discoverable by the ability system without runtime reflection, since reflection-based discovery isn't reliable on the project's IL2CPP mobile target."
- Output: a generator that scans `partial` types implementing `IAbility` marked `[RegisterAbility]` and emits a single static registry class listing them in source order, replacing a prior `Assembly.GetTypes()` scan.

## 8. Edge cases & guardrails
- Never emit code that calls `UnityEngine.Random`, reads wall-clock time, or otherwise reintroduces the exact non-determinism `coding-principles.md`'s Shared Core rule bans — a generator is not exempt from that rule just because a human didn't type the code by hand.
- Never emit members/types in reflection or dictionary-enumeration order — that reintroduces non-determinism across compiler/platform runs even though the source is stable.
- Never let the generator throw on malformed input; report a diagnostic at the offending syntax node instead.
- Don't build a generator for a pattern that appears in only one place — that's premature infrastructure; wait until the repetition is real (YAGNI, per `coding-principles.md`).
- Don't reach for a generator to enforce a coding rule — that's a `DiagnosticAnalyzer`'s job (`roslyn-analyzer-codefix`), not a source generator's.
