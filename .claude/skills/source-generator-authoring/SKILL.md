---
name: source-generator-authoring
description: "C# IIncrementalGenerator replacing repetitive Shared Core code: snapshot codecs, equality/hashing, registries; netstandard2.0, Unity RoslynAnalyzer packaging, caching. Use when the same boilerplate repeats across 3+ types."
user-invocable: false
---

# Source Generator Authoring

Not for: enforcing a rule or reporting a violation (`roslyn-analyzer-codefix`), the formatter MemoryPack already generates (`memorypack-serialization`), a one-off with no repetition (write it by hand).
Docs: https://github.com/dotnet/roslyn/blob/main/docs/features/incremental-generators.md — confirm the project's Roslyn and Unity versions support `IIncrementalGenerator`.

## Steps
1. **Count the types that need it today, not the ones that might** — a generator is a permanent build dependency; one or two call sites never justify it.
2. **Target `netstandard2.0` for the generator assembly** — it loads into the compiler host; any other TFM fails quietly (nothing emitted, build reports missing types, no generator error). Check the TFM before debugging the pipeline.
3. **Use `IIncrementalGenerator`, never obsolete `ISourceGenerator`** (`csharp-standards` → `coding-principles.md` Obsolete APIs).
4. **Never consume another generator's output** — all generators run against the original compilation. Derive from the hand-written declaration, or fold both jobs into one generator.
5. **Filter cheapest-first** — syntax predicate before semantic lookup; for a marker attribute use `SyntaxProvider.ForAttributeWithMetadataName(...)`.
6. **Make every inter-stage value equatable** — `readonly record struct`, never `ISymbol` or `SyntaxNode`; a captured symbol pins the compilation, defeats caching and regenerates on every keystroke for the whole team.
7. **Emit only `partial` additions with `global::`-qualified names** — the build must never need a hand edit, and unqualified names collide with the consumer's `using`s.
8. **Derive each `AddSource` hint name from the fully-qualified type name** — same short name in two namespaces gives a duplicate-hint build error naming neither type.
9. **Hold emitted Core code to Core rules** — no `UnityEngine` reference, no `UnityEngine.Random` or wall-clock time, members in source declaration order (not dictionary/reflection order). See `csharp-standards` → `coding-principles.md` Shared Core integrity.
10. **Keep marker attributes logic-free**, in a small attributes assembly both generator and consumers reference.
11. **Report a diagnostic on malformed input** with `context.ReportDiagnostic(...)` at the declaration, naming the expected shape.
12. **Verify Unity integration and real output** — Unity consumes generators as `.dll`s labelled `RoslynAnalyzer` with all platforms unchecked, not as `<PackageReference>`. Set `<EmitCompilerGeneratedFiles>true</EmitCompilerGeneratedFiles>` to read the emitted files; pin with `CSharpSourceGeneratorVerifier` snapshot tests.

## Never
- Let a generator throw — the compilation dies with an opaque error naming no file.
- Emit anything non-deterministic because "no human typed it".

## Output
```
## Source Generator — <name>
- Repetition justifying it: <types today, drift observed>
- Trigger: <marker attribute / syntax shape>
- Pipeline: <predicate → transform → output; model type, why equatable>
- Generator TFM: netstandard2.0 — confirmed
- Chaining check: consumes no other generator's output — confirmed
- Emitted: <members/types; hint-name scheme>
- Determinism: <no UnityEngine, declaration order>
- Layer: emitted into Core; generator is Editor/build-time only
- Unity integration: <RoslynAnalyzer label, platforms unchecked — how confirmed>
- Diagnostics: <list | none>
- Tests: <snapshot tests; emitted output inspected>
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Have the snapshot generator read the members MemoryPack generates, so we mark once" → declined: generators cannot see each other's output; both key off the same hand-written `partial` declaration.
- IDE slows solution-wide after adding a generator → transform returned `INamedTypeSymbol`; replaced with a `readonly record struct` (fully-qualified name + field list) and `ForAttributeWithMetadataName`.
